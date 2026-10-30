import pygame
import sys
import math
import os

# ==========================================================
# ARENA DE BATALHA - 2 JOGADORES
# Jogador 1: WASD move | F ataque perto | G tiro
# Jogador 2: Setas movem | ENTER ataque perto | CTRL DIR tiro
# ESC: sair | R: reiniciar rodada/partida
# ==========================================================

pygame.init()
pygame.display.set_caption("arena_batalha_4")
WIDTH, HEIGHT = 1000, 680
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Sprites do jogo (pasta assets, ao lado deste arquivo).
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

def load_sprite(filename):
    path = os.path.join(ASSETS_DIR, filename)
    try:
        return pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError):
        return None

SPRITE_PLAYER1 = load_sprite("jogador1.png")
SPRITE_ROBOT = load_sprite("robo.png")
SPRITE_AI = load_sprite("inimigo_ia.png")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("consolas", 21)
SMALL = pygame.font.SysFont("consolas", 16)
BIG = pygame.font.SysFont("consolas", 40, bold=True)

WHITE = (245, 245, 245)
DARK = (14, 18, 28)
BLUE = (65, 155, 255)
RED = (240, 85, 90)
GOLD = (255, 205, 75)
ARENA = pygame.Rect(35, 115, WIDTH - 70, HEIGHT - 180)
FPS = 60


def draw_text(text, x, y, color=WHITE, font=FONT, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    rect.center = (x, y) if center else rect.center
    if not center:
        rect.topleft = (x, y)
    screen.blit(surf, rect)


def clamp(value, low, high):
    return max(low, min(high, value))


class Projectile:
    def __init__(self, x, y, direction, owner, color):
        self.x = float(x)
        self.y = float(y)
        self.dx, self.dy = direction
        self.owner = owner
        self.color = color
        self.speed = 8
        self.radius = 9
        self.damage = 12
        self.life = 85

    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.life -= 1
        return (
            self.life > 0
            and ARENA.left < self.x < ARENA.right
            and ARENA.top < self.y < ARENA.bottom
        )

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius + 3)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        # Pequeno brilho na parte de tras do projétil.
        pygame.draw.circle(
            screen, (255, 245, 180),
            (int(self.x - self.dx * 5), int(self.y - self.dy * 5)), 3
        )


class Fighter:
    def __init__(self, name, x, y, color, controls, facing, shape):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.controls = controls
        self.facing = facing
        self.shape = shape  # jogador 1: triangulo; jogador 2: robo quadrado
        self.sprite = SPRITE_PLAYER1 if shape == "triangle" else SPRITE_ROBOT
        self.radius = 23
        self.speed = 4.1
        self.hp = 100
        self.max_hp = 100
        self.melee_cooldown = 0
        self.ranged_cooldown = 0
        self.melee_flash = 0
        self.invulnerable = 0
        self.wins = 0
        self.alive = True

    def update(self, keys):
        if not self.alive:
            return

        dx = int(keys[self.controls["right"]]) - int(keys[self.controls["left"]])
        dy = int(keys[self.controls["down"]]) - int(keys[self.controls["up"]])

        if dx or dy:
            length = math.hypot(dx, dy)
            dx, dy = dx / length, dy / length
            self.x += dx * self.speed
            self.y += dy * self.speed
            if abs(dx) > abs(dy):
                self.facing = (1 if dx > 0 else -1, 0)
            else:
                self.facing = (0, 1 if dy > 0 else -1)

        self.x = clamp(self.x, ARENA.left + self.radius, ARENA.right - self.radius)
        self.y = clamp(self.y, ARENA.top + self.radius, ARENA.bottom - self.radius)

        self.melee_cooldown = max(0, self.melee_cooldown - 1)
        self.ranged_cooldown = max(0, self.ranged_cooldown - 1)
        self.melee_flash = max(0, self.melee_flash - 1)
        self.invulnerable = max(0, self.invulnerable - 1)

    def melee_attack(self, opponent):
        if not self.alive or self.melee_cooldown:
            return "Ataque de perto recarregando!"
        self.melee_cooldown = 28
        self.melee_flash = 9

        vx, vy = opponent.x - self.x, opponent.y - self.y
        distance = math.hypot(vx, vy) or 1
        dot = (vx / distance) * self.facing[0] + (vy / distance) * self.facing[1]

        if distance <= 88 and dot > 0.1:
            if opponent.invulnerable == 0:
                opponent.take_damage(18)
                return f"{self.name} acertou um golpe de perto! -18 HP"
            return f"{opponent.name} esta protegido por alguns instantes!"
        return f"{self.name} errou o ataque de perto!"

    def ranged_attack(self, projectiles):
        if not self.alive or self.ranged_cooldown:
            return "Ataque de longe recarregando!"
        self.ranged_cooldown = 48
        fx, fy = self.facing
        projectiles.append(
            Projectile(self.x + fx * 30, self.y + fy * 30,
                       self.facing, self, self.color)
        )
        return f"{self.name} lancou um projetil!"

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.invulnerable = 18
        if self.hp <= 0:
            self.alive = False

    def draw(self):
        x, y = int(self.x), int(self.y)
        # Pisca quando recebe dano.
        if self.invulnerable and (self.invulnerable // 3) % 2 == 1:
            return

        pygame.draw.ellipse(screen, (8, 10, 16), (x - 25, y + 17, 50, 13))

        if self.sprite is not None:
            # Desenha o sprite recortado da folha de imagens.
            sprite_h = 86
            sprite_w = 62
            sprite = pygame.transform.smoothscale(self.sprite, (sprite_w, sprite_h))
            screen.blit(sprite, (x - sprite_w // 2, y - sprite_h // 2))
        elif self.shape == "triangle":
            points = [(x, y - 27), (x - 25, y + 21), (x + 25, y + 21)]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, WHITE, points, 3)
            pygame.draw.circle(screen, WHITE, (x, y - 3), 5)
            pygame.draw.circle(screen, DARK, (x, y - 3), 2)
        else:
            body = pygame.Rect(x - 22, y - 22, 44, 44)
            pygame.draw.rect(screen, self.color, body, border_radius=7)
            pygame.draw.rect(screen, WHITE, body, 3, border_radius=7)
            pygame.draw.line(screen, WHITE, (x, y - 22), (x, y - 32), 3)
            pygame.draw.circle(screen, GOLD, (x, y - 34), 5)
            pygame.draw.circle(screen, DARK, (x - 8, y - 4), 4)
            pygame.draw.circle(screen, DARK, (x + 8, y - 4), 4)
            pygame.draw.line(screen, DARK, (x - 8, y + 10), (x + 8, y + 10), 3)

        # Indicador da direcao atual.
        fx, fy = self.facing
        pygame.draw.circle(screen, GOLD, (x + fx * 15, y + fy * 15), 4)

        # Efeito visual do golpe corpo a corpo.
        if self.melee_flash:
            end_x = x + fx * 65 - fy * 24
            end_y = y + fy * 65 + fx * 24
            pygame.draw.line(screen, GOLD, (x + fx * 20, y + fy * 20),
                             (int(end_x), int(end_y)), 10)
            pygame.draw.circle(screen, WHITE, (int(end_x), int(end_y)), 5)


def draw_health(x, y, width, player, color, label):
    draw_text(label, x, y - 26, color, SMALL)
    pygame.draw.rect(screen, (65, 68, 80), (x, y, width, 18), border_radius=8)
    fill = int(width * player.hp / player.max_hp)
    if fill:
        pygame.draw.rect(screen, color, (x, y, fill, 18), border_radius=8)
    pygame.draw.rect(screen, WHITE, (x, y, width, 18), 2, border_radius=8)
    draw_text(f"{player.hp}/100", x + width + 10, y, WHITE, SMALL)


def create_players():
    p1_controls = {
        "up": pygame.K_w, "down": pygame.K_s,
        "left": pygame.K_a, "right": pygame.K_d
    }
    p2_controls = {
        "up": pygame.K_UP, "down": pygame.K_DOWN,
        "left": pygame.K_LEFT, "right": pygame.K_RIGHT
    }
    p1 = Fighter("JOGADOR 1", ARENA.left + 170, ARENA.centery,
                 BLUE, p1_controls, (1, 0), "triangle")
    p2 = Fighter("JOGADOR 2", ARENA.right - 170, ARENA.centery,
                 RED, p2_controls, (-1, 0), "robot")
    return p1, p2


def reset_round(p1, p2):
    p1.x, p1.y = ARENA.left + 170, ARENA.centery
    p2.x, p2.y = ARENA.right - 170, ARENA.centery
    for p in (p1, p2):
        p.hp = p.max_hp
        p.alive = True
        p.melee_cooldown = p.ranged_cooldown = 0
        p.melee_flash = p.invulnerable = 0
    p1.facing, p2.facing = (1, 0), (-1, 0)



def draw_button(rect, title, subtitle, mouse_pos, accent):
    hovered = rect.collidepoint(mouse_pos)
    fill = (54, 67, 88) if not hovered else (72, 91, 119)
    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, accent if hovered else (110, 125, 145), rect, 3, border_radius=14)
    draw_text(title, rect.centerx, rect.centery - 12, WHITE, FONT, center=True)
    draw_text(subtitle, rect.centerx, rect.centery + 18, accent, SMALL, center=True)


def draw_lobby(mouse_pos, selected_mode=None):
    screen.fill((14, 18, 28))
    # Decorative arena rings.
    pygame.draw.circle(screen, (24, 35, 50), (WIDTH // 2, 210), 160, 3)
    pygame.draw.circle(screen, (24, 35, 50), (WIDTH // 2, 210), 120, 3)
    draw_text("ARENA BATALHA 4", WIDTH // 2, 80, GOLD, BIG, center=True)
    draw_text("Escolha como quer jogar", WIDTH // 2, 135, WHITE, FONT, center=True)
    coop_rect = pygame.Rect(125, 310, 330, 130)
    solo_rect = pygame.Rect(545, 310, 330, 130)
    draw_button(coop_rect, "COOPERATIVO", "2 jogadores no mesmo teclado", mouse_pos, BLUE)
    draw_button(solo_rect, "MODO SOLO", "Jogue contra a inteligência artificial", mouse_pos, RED)
    draw_text("Use o mouse para selecionar", WIDTH // 2, 490, (180, 190, 205), SMALL, center=True)
    draw_text("ESC: sair", WIDTH // 2, 525, (130, 145, 165), SMALL, center=True)
    pygame.display.flip()
    return coop_rect, solo_rect


def draw_pause_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    screen.blit(overlay, (0, 0))
    draw_text("PAUSA", WIDTH // 2, HEIGHT // 2 - 25, GOLD, BIG, center=True)
    draw_text("Pressione ESC para voltar ao menu", WIDTH // 2, HEIGHT // 2 + 25, WHITE, FONT, center=True)


def ai_choose_action(ai, player, projectiles):
    """Simple enemy AI: chase the player, face them, and attack when ready."""
    if not ai.alive or not player.alive:
        return "A IA esta fora de combate."
    dx, dy = player.x - ai.x, player.y - ai.y
    distance = math.hypot(dx, dy) or 1
    ai.facing = (dx / distance, dy / distance)
    # Move toward the player, stopping at a useful firing distance.
    if distance > 175:
        ai.x += (dx / distance) * ai.speed * 0.78
        ai.y += (dy / distance) * ai.speed * 0.78
    ai.x = clamp(ai.x, ARENA.left + ai.radius, ARENA.right - ai.radius)
    ai.y = clamp(ai.y, ARENA.top + ai.radius, ARENA.bottom - ai.radius)
    ai.melee_cooldown = max(0, ai.melee_cooldown - 1)
    ai.ranged_cooldown = max(0, ai.ranged_cooldown - 1)
    ai.melee_flash = max(0, ai.melee_flash - 1)
    ai.invulnerable = max(0, ai.invulnerable - 1)
    if distance <= 82 and ai.melee_cooldown == 0:
        ai.melee_cooldown = 35
        ai.melee_flash = 8
        if player.invulnerable == 0:
            player.take_damage(14)
    elif distance > 82 and distance < 430 and ai.ranged_cooldown == 0:
        ai.ranged_cooldown = 58
        projectiles.append(
            Projectile(ai.x + ai.facing[0] * 30, ai.y + ai.facing[1] * 30,
                       ai.facing, ai, ai.color)
        )


def main():
    p1, p2 = create_players()
    projectiles = []
    message = "Escolha um modo de jogo."
    round_over = False
    match_over = False
    winning_score = 3
    running = True
    game_state = "lobby"
    game_mode = "coop"
    paused = False

    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == "game":
                        game_state = "lobby"
                        paused = False
                        projectiles.clear()
                        p1, p2 = create_players()
                        p1.wins = p2.wins = 0
                        round_over = match_over = False
                        message = "Escolha um modo de jogo."
                    else:
                        running = False

                if game_state == "game" and not paused:
                    if not round_over:
                        if event.key == pygame.K_f:
                            message = p1.melee_attack(p2)
                        elif event.key == pygame.K_g:
                            message = p1.ranged_attack(projectiles)
                        elif game_mode == "coop" and event.key == pygame.K_RETURN:
                            message = p2.melee_attack(p1)
                        elif game_mode == "coop" and event.key == pygame.K_RCTRL:
                            message = p2.ranged_attack(projectiles)

                if game_state == "game" and event.key == pygame.K_p:
                    paused = not paused

                if game_state == "game" and event.key == pygame.K_r and round_over:
                    if match_over:
                        p1.wins = p2.wins = 0
                        match_over = False
                    reset_round(p1, p2)
                    projectiles.clear()
                    round_over = False
                    message = "Nova rodada! Boa batalha!"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "lobby":
                    coop_rect = pygame.Rect(125, 310, 330, 130)
                    solo_rect = pygame.Rect(545, 310, 330, 130)
                    if coop_rect.collidepoint(event.pos):
                        game_mode = "coop"
                        p1, p2 = create_players()
                        p1.wins = p2.wins = 0
                        projectiles.clear()
                        round_over = match_over = False
                        message = "Cooperativo: derrote o outro jogador!"
                        game_state = "game"
                    elif solo_rect.collidepoint(event.pos):
                        game_mode = "solo"
                        p1, p2 = create_players()
                        p1.name = "VOCE"
                        p2.name = "IA INIMIGA"
                        p2.sprite = SPRITE_AI or SPRITE_ROBOT
                        p2.speed = 3.35
                        p1.wins = p2.wins = 0
                        projectiles.clear()
                        round_over = match_over = False
                        message = "Modo solo: derrote a inteligencia artificial!"
                        game_state = "game"

        if game_state == "lobby":
            draw_lobby(mouse_pos)
            continue

        if paused:
            # Draw the arena behind the pause overlay, but do not update the match.
            pass
        elif not round_over:
            keys = pygame.key.get_pressed()
            p1.update(keys)
            if game_mode == "coop":
                p2.update(keys)
            else:
                ai_choose_action(p2, p1, projectiles)

            for shot in projectiles[:]:
                if not shot.update():
                    projectiles.remove(shot)
                    continue
                target = p2 if shot.owner is p1 else p1
                if target.alive:
                    distance = math.hypot(target.x - shot.x, target.y - shot.y)
                    if distance <= target.radius + shot.radius:
                        if target.invulnerable == 0:
                            target.take_damage(12)
                            message = f"Projetil acertou {target.name}! -12 HP"
                        else:
                            message = f"{target.name} desviou do projetil!"
                        projectiles.remove(shot)

            if not p1.alive or not p2.alive:
                round_over = True
                projectiles.clear()
                if game_mode == "solo":
                    if p1.alive:
                        p1.wins += 1
                        message = "Voce venceu a rodada!"
                    else:
                        p2.wins += 1
                        message = "A IA venceu a rodada!"
                elif not p1.alive:
                    p2.wins += 1
                    message = "JOGADOR 2 venceu a rodada!"
                else:
                    p1.wins += 1
                    message = "JOGADOR 1 venceu a rodada!"
                if p1.wins >= winning_score or p2.wins >= winning_score:
                    match_over = True

        # Draw arena.
        screen.fill((24, 29, 42))
        pygame.draw.rect(screen, (43, 65, 67), ARENA, border_radius=18)
        pygame.draw.rect(screen, (125, 155, 140), ARENA, 4, border_radius=18)
        for x in range(ARENA.left + 30, ARENA.right, 70):
            for y in range(ARENA.top + 30, ARENA.bottom, 70):
                pygame.draw.circle(screen, (54, 79, 77), (x, y), 2)

        draw_text("ARENA BATALHA 4", WIDTH // 2, 24, GOLD, BIG, center=True)
        left_label = "VOCE" if game_mode == "solo" else "JOGADOR 1 | TRIANGULO"
        right_label = "IA INIMIGA | ROBO" if game_mode == "solo" else "JOGADOR 2 | ROBO"
        draw_health(45, 78, 285, p1, BLUE, left_label)
        draw_health(WIDTH - 330, 78, 285, p2, RED, right_label)
        draw_text(f"{p1.wins} x {p2.wins}", WIDTH // 2, 84, GOLD, FONT, center=True)

        for shot in projectiles:
            shot.draw()
        p1.draw()
        p2.draw()

        pygame.draw.rect(screen, DARK, (0, HEIGHT - 65, WIDTH, 65))
        if game_mode == "solo":
            draw_text("VOCE: WASD mover | F ataque perto | G tiro", 22, HEIGHT - 52, BLUE, SMALL)
            draw_text("P: pausa | R: proxima rodada | ESC: menu", 540, HEIGHT - 52, WHITE, SMALL)
        else:
            draw_text("P1: WASD mover | F perto | G tiro", 22, HEIGHT - 52, BLUE, SMALL)
            draw_text("P2: SETAS mover | ENTER perto | CTRL DIR tiro", 390, HEIGHT - 52, RED, SMALL)
        draw_text(message[:90], WIDTH // 2, HEIGHT - 25, WHITE, SMALL, center=True)

        if round_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 165))
            screen.blit(overlay, (0, 0))
            if match_over:
                if game_mode == "solo":
                    champion = "VOCE" if p1.wins >= winning_score else "IA INIMIGA"
                else:
                    champion = "JOGADOR 1" if p1.wins >= winning_score else "JOGADOR 2"
                title = f"{champion} VENCEU A PARTIDA!"
            else:
                title = "FIM DA RODADA!"
            draw_text(title, WIDTH // 2, HEIGHT // 2 - 45, GOLD, BIG, center=True)
            draw_text(message, WIDTH // 2, HEIGHT // 2 + 5, WHITE, FONT, center=True)
            draw_text("Pressione R para continuar | ESC para menu",
                      WIDTH // 2, HEIGHT // 2 + 48, WHITE, FONT, center=True)

        if paused:
            draw_pause_overlay()
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
