# Asteroid Defence

A 2D space defence game built with Python and Pygame. Rotate a cannon at the bottom of the screen and shoot asteroids before they hit the city. Collect power-ups, earn points, level up, and survive as long as you can.

## Play online

Play in the browser via GitHub Pages (no install needed):

**https://satelada.github.io/AsteroidsDefence/**

## Run locally

### 1. Install Python

- Download from [python.org](https://www.python.org/downloads/)
- During setup, check **"Add Python to PATH"**

### 2. Install Pygame

```text
python -m pip install -r requirements.txt
```

### 3. Start the game

```text
python main.py
```

Or double-click `Start_Falling_Asteroids.bat` on Windows.

## Controls

### Keyboard

| Key | Action |
|-----|--------|
| **1 / 2 / 3** (menu) | Select difficulty (Easy / Normal / Difficult) |
| **ENTER** (menu) | Start game |
| **Arrow Left / Right** | Rotate cannon |
| **SPACE** | Shoot |
| **ENTER** (in game) | Pause / Resume |
| **ENTER** (game over) | Back to menu / Enter name |
| **Escape** | Quit / Back to menu |

### Controller (Xbox / PS4 / PS5 / generic)

| Input | Action |
|-------|--------|
| **Left Stick / D-Pad** | Rotate cannon / Switch difficulty |
| **A / Cross** | Shoot / Confirm |
| **B / Circle** | Pause |
| **Start** | Confirm / Pause |

### Touchscreen

| Gesture | Action |
|---------|--------|
| **Drag left/right** | Rotate cannon |
| **Tap** | Shoot / Confirm / Select |

## Features

- **3 difficulty levels** — Easy (large asteroids), Normal, Difficult (small asteroids)
- **Level system** — Level up every 100 points
- **Lives** — Start with 3 lives, earn more through power-ups (max 10)
- **Golden asteroids** — Rare golden asteroids worth double points
- **Shot cost** — Each shot costs 2 points
- **UI scaling** — Set `UI_SCALE` in config.json to scale the entire game proportionally

## Power-ups

Power-ups fall from the sky and can be shot or hit by the laser to activate them.

| Power-up | Label | Effect |
|----------|-------|--------|
| **Triple Shot** | T | Next 10 shots fire 3 bullets |
| **Shield** | S | Absorbs all asteroid impacts for 10 seconds |
| **Bomb** | B | Destroys all asteroids on screen (awards points) |
| **Laser** | L | Continuous laser beam for 5 seconds |
| **Slow** | W | Slows asteroid speed by 10% |
| **Extra Shot** | + | Permanently adds +1 bullet per shot (max 5) |
| **Life** | ♥ | +1 life (max 10) |

## Configuration

All game parameters are configurable in `config.json`. The file includes inline descriptions for every parameter. See the `_desc_*` keys next to each value.

## Highscores

- **10 entries per difficulty level**, shown on the menu screen
- After game over, enter your name if you made the top 10
- **Desktop:** saved in `highscores.json`
- **Browser:** saved in localStorage

## Optional assets

Place files in the `assets/` folder next to `main.py`:

- `cannon.png` — custom cannon graphic
- `spaceship.png` — ship under the cannon
- `shoot.wav` / `shoot.ogg` — shoot sound effect
- `space_music.ogg` / `space_music.mp3` — background music
