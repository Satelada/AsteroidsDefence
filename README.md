# Asteroid Defence

A 2D space defence game built with Python and Pygame. Rotate a cannon at the bottom of the screen and shoot asteroids before they hit the ground. The more you hit, the more points — and asteroids speed up over time.

## Play online

Play in the browser via GitHub Pages (no install needed):

**https://satelada.github.io/AsteroidsDefence/**

## Run locally

### 1. Install Python

- Download from [python.org](https://www.python.org/downloads/)
- During setup, check **"Add Python to PATH"**

### 2. Install Pygame

Open a terminal in the project folder and run:

```text
python -m pip install -r requirements.txt
```

### 3. Start the game

```text
python main.py
```

Or double-click `Start_Falling_Asteroids.bat` on Windows.

## Controls

| Key | Action |
|-----|--------|
| **1** (menu) | Easy difficulty |
| **2** (menu) | Normal difficulty |
| **3** (menu) | Difficult difficulty |
| **ENTER** (menu) | Start game |
| **Left** / **A** | Rotate cannon left |
| **Right** / **D** | Rotate cannon right |
| **SPACE** (in game) | Shoot |
| **ENTER** (game over) | Back to menu / Enter name |
| **Escape** | Quit / Back to menu |

## Difficulty

| Level | Asteroid size | Description |
|-------|--------------|-------------|
| 1 = Easy | Large | Big targets, easy to hit |
| 2 = Normal | Medium | Balanced challenge |
| 3 = Difficult | Small | Tiny targets, hard to hit |

## Highscores

- **10 entries per difficulty level**, shown on the menu screen
- After game over, enter your name if you made the top 10
- Press ENTER to confirm or ESC to skip
- **Desktop:** saved in `highscores.json`
- **Browser:** saved in localStorage (persists across sessions)

## Optional: images

Place files in the `assets/` folder next to `main.py`:

- **Cannon:** `cannon.png` — custom cannon graphic
- **Spaceship:** `spaceship.png` — custom ship under the cannon
