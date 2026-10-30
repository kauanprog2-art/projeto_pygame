# 🎮 Arena Batalha 4 — Projeto Pygame

Um jogo de batalha desenvolvido em **Python com Pygame**, com modo cooperativo para dois jogadores e modo solo contra uma inteligência artificial (IA).

## 📌 Sobre o projeto

O **Arena Batalha 4** é um jogo de combate em uma arena, onde os jogadores podem se movimentar, atacar de perto e disparar projéteis para derrotar seus adversários.

O projeto utiliza Python e a biblioteca Pygame para criar a janela do jogo, desenhar os personagens, controlar os movimentos e gerenciar os combates.

## ✨ Funcionalidades

- 👥 Modo cooperativo para dois jogadores no mesmo teclado.
- 🤖 Modo solo contra um inimigo controlado pelo computador.
- ⚔️ Ataques corpo a corpo.
- 💥 Ataques à distância com projéteis.
- ❤️ Barras de vida dos personagens.
- 🏆 Sistema de rodadas e vitórias.
- 🎨 Recursos gráficos e sprites para os personagens.
- ⏸️ Sistema de pausa.

## 🕹️ Controles

### Jogador 1 / Modo Solo

| Tecla | Ação |
|---|---|
| `W` | Mover para cima |
| `A` | Mover para a esquerda |
| `S` | Mover para baixo |
| `D` | Mover para a direita |
| `F` | Ataque corpo a corpo |
| `G` | Ataque à distância |

### Jogador 2 — Modo Cooperativo

| Tecla | Ação |
|---|---|
| `↑` | Mover para cima |
| `↓` | Mover para baixo |
| `←` | Mover para a esquerda |
| `→` | Mover para a direita |
| `Enter` | Ataque corpo a corpo |
| `Ctrl direito` | Ataque à distância |

### Controles gerais

- **Mouse:** selecionar o modo de jogo no menu.
- **P:** pausar ou retomar a partida.
- **R:** continuar após o fim de uma rodada.
- **Esc:** voltar ao menu ou sair do jogo.

## 🛠️ Tecnologias utilizadas

- [Python](https://www.python.org/)
- [Pygame](https://www.pygame.org/)

## 📥 Como instalar e executar

### 1. Instale o Python

### 2. Instale o Pygame

Abra o terminal e execute:

```bash
pip install pygame
```

### 3. Baixe o projeto

Clone este repositório:

```bash
git clone https://github.com/SEU-USUARIO/projeto_pygame.git
```

Entre na pasta:

```bash
cd projeto_pygame
```

### 4. Execute o jogo

Se o arquivo principal estiver na raiz do projeto, execute:

```bash
python arena_batalha_4.py
```

Se estiver utilizando o arquivo de inicialização compartilhável, execute:

```bash
python arena_batalha_4_compartilhar.py
```

> **Importante:** mantenha a pasta `assets` junto do arquivo Python principal quando utilizar a versão que carrega as imagens externamente.

## 📁 Estrutura do projeto

```text
projeto_pygame/
├── arena_batalha_4.py
├── arena_batalha_4_compartilhar.py
├── assets/
│   ├── spritesheet.png
│   ├── spritesheet_menu_ataques.png
│   ├── jogador1.png
│   ├── robo.png
│   ├── inimigo_ia.png
│   └── ...
└── README.md
```

A estrutura acima é uma sugestão. Os arquivos e as imagens presentes no repositório podem variar conforme a versão adicionada.

## 🚀 Melhorias futuras

- [ ] Animações completas para os personagens.
- [ ] Efeitos visuais para os ataques.
- [ ] Música de fundo e efeitos sonoros.
- [ ] Novos personagens e habilidades.
- [ ] Novas arenas e cenários.
- [ ] Melhorias na inteligência artificial.
- [ ] Sistema de seleção de personagens.

## 🎯 Objetivo

Este projeto tem como objetivo praticar programação em Python, desenvolvimento de jogos, lógica de combate, movimentação de personagens e criação de interfaces com Pygame.

