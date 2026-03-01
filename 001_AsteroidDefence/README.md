# Falling Asteroids

A 2D game: you rotate a space cannon at the bottom and shoot at asteroids falling from above. If an asteroid hits the ground, game over. The more you hit, the more points—and asteroids speed up over time.

## How to run

### 1. Install Python (if needed)

- Go to [python.org](https://www.python.org/downloads/) and download the latest Python.
- During setup, check **"Add Python to PATH"**, then run "Install Now".

### 2. Install Pygame

Open a command prompt or PowerShell and go to this folder:

```text
cd "001_Fallende_Steine"
```

Then run:

```text
python -m pip install -r requirements.txt
```

### 3. Start the game

**Important:** Start the game from the project folder so that music and images (from the `assets` folder) work:

```text
cd "c:\Users\marker_d\Documents\99_programmieren\Sateda\001_Fallende_Steine"
python main.py
```

Do not just double-click `main.py` or run it from another directory – otherwise the game cannot find the `assets` folder.

A window opens and the game runs.

## Controls

| Key | Action |
|-----|--------|
| **1–9** (in menu) | Asteroid size (difficulty) |
| **SPACE** (in menu) | Start game |
| **Left** / **A** | Rotate cannon left |
| **Right** / **D** | Rotate cannon right |
| **SPACE** (in game) | Shoot |
| **SPACE** (game over) | Back to menu |
| **Escape** | Quit |

## Rules

- The **cannon** at the bottom is fixed; **rotate** it to aim.
- **Asteroids** (irregular rocks) fall from the top. Shoot them with the white bullets.
- Each hit gives **10 points**. Asteroids get **faster** over time.
- If an asteroid touches the **green ground line**, it’s **Game Over**—press SPACE to return to the menu.

## Optional: music and images

The game looks for files in the **`assets`** folder (next to `main.py`). You must run the game from the project folder (see step 3 above), otherwise these files are not found.

- **Music:** Put `space_music.ogg` or `space_music.mp3` in `assets/` – the game will loop it.
- **Cannon:** Put `cannon.png` in `assets/` for a custom cannon graphic (barrel pointing up).
- **Spaceship:** Put `spaceship.png` (or `ship.png`) in `assets/` for a custom ship under the cannon.

See `assets/README.txt` for a short guide (in German).

Enjoy!

