# Asteroid Defence - 2D game in Python with Pygame
# Menu: 1-9 = asteroid size, SPACE = Start. Game: Arrow/A/D = rotate, SPACE = shoot

import os
import sys
import asyncio
import pygame
import random
import math

# === Settings ===
WIDTH = 600
HEIGHT = 800
BARREL_WIDTH = 24
BARREL_LENGTH = 56
CANNON_BASE_WIDTH = 70
CANNON_BASE_HEIGHT = 22
ROTATE_SPEED = 3
MENU_ASTEROID_ROTATE_SPEED = 3.0
BULLET_SPEED = 12
ASTEROID_RADIUS_MIN = 10
ASTEROID_RADIUS_MAX = 120
ASTEROID_START_SPEED = 2
ASTEROID_SPEED_INCREASE = 0.15
ASTEROID_SPAWN_INTERVAL = 90
POINTS_PER_HIT = 10
GROUND_OFFSET = 20
MAX_PARTICLES = 120

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 60, 60)
GRAY = (120, 120, 120)
GREEN = (60, 200, 80)
CANNON_METAL = (70, 75, 90)
CANNON_GLOW = (60, 140, 220)
CANNON_DARK = (50, 55, 68)
CANNON_HIGHLIGHT = (95, 100, 115)
AIM_COLOR = (100, 200, 255)
ASTEROID_FILL = (80, 75, 70)
ASTEROID_EDGE = (100, 95, 90)
ASTEROID_CRATER = (50, 48, 45)
ASTEROID_HIGHLIGHT = (105, 100, 95)
UFO_WIDTH = WIDTH
UFO_HEIGHT = 85
BULLET_GLOW = (80, 140, 255)
STAR_COLORS = [(200, 210, 255), (220, 220, 255), (180, 190, 255), (255, 255, 255)]
EXPLOSION_COLORS = [(255, 200, 80), (255, 150, 40), (255, 100, 30), (255, 80, 20), (255, 220, 100)]
MUZZLE_COLORS = [(255, 255, 220), (255, 240, 140), (255, 200, 60)]
CITY_COLOR = (12, 15, 22)
CITY_WINDOW = (200, 190, 100)
CITY_OUTLINE = (20, 25, 35)
MOUNTAIN_COLOR = (15, 18, 25)
NEBULA_COLORS = [(25, 12, 40), (12, 18, 35), (30, 10, 25), (10, 25, 30)]


def size_to_radius(size):
    """Asteroid size 1-9 to pixel radius. Linear: 1 -> MIN, 9 -> MAX."""
    size = max(1, min(9, size))
    return int(round(ASTEROID_RADIUS_MIN + (ASTEROID_RADIUS_MAX - ASTEROID_RADIUS_MIN) * (size - 1) / 8.0))


def make_asteroid_vertices(radius, num_points=None):
    if num_points is None:
        num_points = max(8, min(14, radius // 8))
    verts = []
    for i in range(num_points):
        angle = (i / num_points) * 2 * math.pi + random.uniform(0, 0.3)
        r = radius * random.uniform(0.75, 1.2)
        verts.append((r * math.cos(angle), r * math.sin(angle)))
    return verts


def make_asteroid_craters(radius):
    craters = []
    n = max(2, min(6, radius // 15))
    for _ in range(n):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0.1, 0.6) * radius
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        cr = random.uniform(0.08, 0.22) * radius
        craters.append((dx, dy, max(2, cr)))
    return craters


def get_assets_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def make_background():
    """Generate all static background elements with fixed seeds."""
    rng = random.Random(42)
    stars = []
    for _ in range(70):
        phase = rng.uniform(0, 2 * math.pi)
        speed = rng.uniform(0.02, 0.08)
        stars.append((rng.randint(0, WIDTH - 1), rng.randint(0, HEIGHT - 1),
                       rng.choice([1, 1, 2]), rng.randint(0, len(STAR_COLORS) - 1),
                       phase, speed))
    planets = []
    for _ in range(2):
        x = rng.randint(80, WIDTH - 80)
        y = rng.randint(80, HEIGHT - 200)
        r = rng.randint(20, 40)
        c = rng.choice([(80, 60, 90), (60, 70, 100), (90, 55, 70), (50, 80, 90)])
        has_ring = rng.random() < 0.4
        planets.append((x, y, r, c, has_ring))
    nebulae = []
    for _ in range(3):
        nebulae.append((rng.randint(0, WIDTH), rng.randint(0, HEIGHT - 150),
                         rng.randint(50, 110), rng.choice(NEBULA_COLORS)))
    # Mountains
    mrng = random.Random(456)
    mountain_ridge = [(0, 700)]
    mx = 0
    while mx <= WIDTH:
        mountain_ridge.append((mx, mrng.randint(580, 690)))
        mx += mrng.randint(40, 90)
    mountain_ridge.append((WIDTH, 700))
    mountains = mountain_ridge + [(WIDTH, HEIGHT), (0, HEIGHT)]
    # City
    crng = random.Random(123)
    buildings = []
    bx = 0
    while bx < WIDTH:
        bw = crng.randint(18, 50)
        bh = crng.randint(12, 65)
        buildings.append((bx, bw, bh))
        bx += bw + crng.randint(2, 8)
    windows = []
    for bbx, bw, bh in buildings:
        top = HEIGHT - GROUND_OFFSET - bh
        cols = max(1, bw // 12)
        rows = max(1, bh // 14)
        for row in range(rows):
            for col in range(cols):
                wx = bbx + 4 + col * max(1, (bw - 8) // max(cols, 1))
                wy = top + 4 + row * 14
                if wx < bbx + bw - 4 and wy < HEIGHT - GROUND_OFFSET - 4 and crng.random() < 0.5:
                    windows.append((wx, wy))
    return {
        "stars": stars, "planets": planets, "nebulae": nebulae,
        "mountains": mountains, "mountain_ridge": mountain_ridge,
        "buildings": buildings, "windows": windows,
    }


def create_explosion(x, y, count=15):
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 6)
        size = random.uniform(2, 7)
        lifetime = random.randint(15, 40)
        color = random.choice(EXPLOSION_COLORS)
        particles.append({
            "x": x, "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed - 1.5,
            "size": size, "color": color,
            "life": lifetime, "max_life": lifetime,
        })
    return particles


def load_space_music(assets_dir, log):
    for name in ("space_music.ogg", "space_music.mp3", "space_music.wav", "music.ogg", "music.mp3", "music.wav"):
        path = os.path.join(assets_dir, name)
        if os.path.isfile(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(loops=-1)
                if log:
                    print("  Music: playing (" + name + ")")
                return True
            except Exception as e:
                if log:
                    print("  Music: error loading", name, "-", e)
    if log:
        print("  Music: not found")
    return False


def load_shoot_sound(assets_dir, log):
    for name in ("shoot.ogg", "shoot.wav"):
        path = os.path.join(assets_dir, name)
        if os.path.isfile(path):
            try:
                snd = pygame.mixer.Sound(path)
                if log:
                    print("  Shoot sound: loaded (" + name + ")")
                return snd
            except Exception as e:
                if log:
                    print("  Shoot sound: error -", e)
    if log:
        print("  Shoot sound: not found")
    return None


async def main():
    pygame.init()
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    except Exception as e:
        print("Mixer init failed:", e)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
    pygame.display.set_caption("Asteroid Defence")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)
    font_large = pygame.font.Font(None, 72)
    font_small = pygame.font.Font(None, 36)

    assets_dir = get_assets_dir()
    print("Assets folder:", os.path.abspath(assets_dir))
    if not os.path.isdir(assets_dir):
        print("  -> Folder missing! Create 'assets' next to main.py and add files.")
    shoot_sound = load_shoot_sound(assets_dir, log=True) if os.path.isdir(assets_dir) else None
    music_loaded = False
    if os.path.isdir(assets_dir):
        music_loaded = load_space_music(assets_dir, log=True)
    bg = make_background()

    def new_game(asteroid_size):
        return {
            "angle": 0,
            "bullets": [],
            "asteroids": [],
            "score": 0,
            "asteroid_speed": ASTEROID_START_SPEED,
            "frame": 0,
            "game_over": False,
            "ground_y": HEIGHT - GROUND_OFFSET,
            "asteroid_size": asteroid_size,
            "asteroid_radius": size_to_radius(asteroid_size),
            "particles": [],
            "shake": 0,
            "score_popups": [],
            "muzzle_flash": 0,
            "shooting_stars": [],
        }

    _init_r = min(size_to_radius(5), 80)
    state = {
        "menu": True, "asteroid_size": 5, "menu_asteroid_angle": 0, "music_on": False,
        "menu_asteroid_verts": make_asteroid_vertices(_init_r),
        "menu_asteroid_craters": make_asteroid_craters(_init_r),
        "menu_asteroid_cached_size": 5,
    }
    if music_loaded:
        pygame.mixer.music.set_volume(0)

    tick = 0
    running = True
    while running:
        tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state.get("menu"):
                        running = False
                    else:
                        _sz = state.get("asteroid_size", 5)
                        _r = min(size_to_radius(_sz), 80)
                        state = {"menu": True, "asteroid_size": _sz,
                                 "menu_asteroid_angle": state.get("menu_asteroid_angle", 0),
                                 "music_on": state.get("music_on", False),
                                 "menu_asteroid_verts": make_asteroid_vertices(_r),
                                 "menu_asteroid_craters": make_asteroid_craters(_r),
                                 "menu_asteroid_cached_size": _sz}
                        continue
                if state.get("menu"):
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        state["asteroid_size"] = event.key - pygame.K_0
                        _r = min(size_to_radius(state["asteroid_size"]), 80)
                        state["menu_asteroid_verts"] = make_asteroid_vertices(_r)
                        state["menu_asteroid_craters"] = make_asteroid_craters(_r)
                        state["menu_asteroid_cached_size"] = state["asteroid_size"]
                    elif event.key == pygame.K_0:
                        state["music_on"] = not state.get("music_on", False)
                        if music_loaded:
                            if state["music_on"]:
                                pygame.mixer.music.set_volume(0.6)
                                pygame.mixer.music.play(loops=-1)
                            else:
                                pygame.mixer.music.set_volume(0)
                    elif event.key == pygame.K_SPACE:
                        saved_music = state.get("music_on", False)
                        saved_angle = state.get("menu_asteroid_angle", 0)
                        state = new_game(state["asteroid_size"])
                        state["music_on"] = saved_music
                        state["menu_asteroid_angle"] = saved_angle
                    continue
                if state.get("game_over") and event.key == pygame.K_SPACE:
                    _sz = state["asteroid_size"]
                    _r = min(size_to_radius(_sz), 80)
                    state = {"menu": True, "asteroid_size": _sz,
                             "menu_asteroid_angle": state.get("menu_asteroid_angle", 0),
                             "music_on": state.get("music_on", False),
                             "menu_asteroid_verts": make_asteroid_vertices(_r),
                             "menu_asteroid_craters": make_asteroid_craters(_r),
                             "menu_asteroid_cached_size": _sz}
                    continue
                if not state.get("game_over") and event.key in (pygame.K_SPACE, pygame.K_LCTRL, pygame.K_RCTRL):
                    rad = math.radians(state["angle"])
                    cx = WIDTH // 2
                    pivot_y = HEIGHT - GROUND_OFFSET - CANNON_BASE_HEIGHT
                    tip_x = cx + math.sin(rad) * BARREL_LENGTH
                    tip_y = pivot_y - math.cos(rad) * BARREL_LENGTH
                    vx = BULLET_SPEED * math.sin(rad)
                    vy = -BULLET_SPEED * math.cos(rad)
                    state["bullets"].append({"x": tip_x, "y": tip_y, "vx": vx, "vy": vy,
                                              "trail": [(tip_x, tip_y)]})
                    state["score"] = max(0, state["score"] - 1)
                    state["muzzle_flash"] = 6
                    state["shake"] = max(state.get("shake", 0), 2)
                    if shoot_sound is not None:
                        shoot_sound.play()

        # --- Game logic ---
        if not state.get("menu") and not state.get("game_over"):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                state["angle"] -= ROTATE_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                state["angle"] += ROTATE_SPEED
            state["angle"] = max(-80, min(80, state["angle"]))

            state["frame"] += 1
            r = state["asteroid_radius"]
            if state["frame"] % ASTEROID_SPAWN_INTERVAL == 0:
                x = random.randint(r, WIDTH - r)
                verts = make_asteroid_vertices(r)
                craters = make_asteroid_craters(r)
                state["asteroids"].append({
                    "x": x, "y": -r * 2, "verts": verts, "craters": craters,
                    "angle": random.uniform(0, 360), "rot_speed": random.uniform(0.5, 2.5)
                })

            for b in state["bullets"][:]:
                b["x"] += b["vx"]
                b["y"] += b["vy"]
                if "trail" not in b:
                    b["trail"] = [(b["x"], b["y"])]
                b["trail"].append((b["x"], b["y"]))
                if len(b["trail"]) > 6:
                    b["trail"] = b["trail"][-6:]
                if b["y"] < -20 or b["x"] < -20 or b["x"] > WIDTH + 20:
                    state["bullets"].remove(b)

            state["ground_y"] = HEIGHT - GROUND_OFFSET
            for a in state["asteroids"][:]:
                a["y"] += state["asteroid_speed"]
                a["angle"] = a.get("angle", 0) + a.get("rot_speed", 1)
                if a["y"] + state["asteroid_radius"] >= state["ground_y"]:
                    state["game_over"] = True
                    state["shake"] = 15
                    break
                state["asteroid_speed"] += 0.001

            for b in state["bullets"][:]:
                for a in state["asteroids"][:]:
                    dist = math.sqrt((b["x"] - a["x"]) ** 2 + (b["y"] - a["y"]) ** 2)
                    if dist < state["asteroid_radius"] + 5:
                        if b in state["bullets"]:
                            state["bullets"].remove(b)
                        if a in state["asteroids"]:
                            state["asteroids"].remove(a)
                        state["score"] += POINTS_PER_HIT
                        state["asteroid_speed"] += ASTEROID_SPEED_INCREASE * 0.5
                        state["shake"] = max(state.get("shake", 0), 4)
                        if len(state["particles"]) < MAX_PARTICLES:
                            state["particles"].extend(create_explosion(a["x"], a["y"]))
                        state["score_popups"].append({
                            "x": a["x"], "y": a["y"],
                            "text": f"+{POINTS_PER_HIT}",
                            "life": 40,
                        })
                        break

            # Particles
            for p in state["particles"][:]:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.1
                p["life"] -= 1
                if p["life"] <= 0:
                    state["particles"].remove(p)

            # Score popups
            for sp in state["score_popups"][:]:
                sp["y"] -= 1.2
                sp["life"] -= 1
                if sp["life"] <= 0:
                    state["score_popups"].remove(sp)

            # Muzzle flash decay
            if state.get("muzzle_flash", 0) > 0:
                state["muzzle_flash"] -= 1

            # Shooting stars
            if random.random() < 0.006:
                state["shooting_stars"].append({
                    "x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT // 3),
                    "vx": random.uniform(3, 7) * random.choice([-1, 1]),
                    "vy": random.uniform(2, 5),
                    "life": random.randint(10, 25), "max_life": 25,
                })
            for ss in state["shooting_stars"][:]:
                ss["x"] += ss["vx"]
                ss["y"] += ss["vy"]
                ss["life"] -= 1
                if ss["life"] <= 0 or ss["x"] < -20 or ss["x"] > WIDTH + 20 or ss["y"] > HEIGHT:
                    state["shooting_stars"].remove(ss)

        # === Drawing ===
        screen.fill(BLACK)

        # Nebulae
        for nx, ny, nr, nc in bg["nebulae"]:
            pygame.draw.circle(screen, nc, (nx, ny), nr, 0)
            inner = (min(255, nc[0] + 6), min(255, nc[1] + 6), min(255, nc[2] + 6))
            pygame.draw.circle(screen, inner, (nx, ny), nr * 2 // 3, 0)

        # Twinkling stars
        for sx, sy, sz, ci, phase, spd in bg["stars"]:
            base = STAR_COLORS[ci % len(STAR_COLORS)]
            brightness = 0.5 + 0.5 * math.sin(tick * spd + phase)
            c = (max(0, min(255, int(base[0] * brightness))),
                 max(0, min(255, int(base[1] * brightness))),
                 max(0, min(255, int(base[2] * brightness))))
            pygame.draw.circle(screen, c, (sx, sy), sz, 0)

        # Planets with shading and optional rings
        for px, py, pr, pc, has_ring in bg["planets"]:
            pygame.draw.circle(screen, pc, (px, py), pr, 0)
            hi = (min(255, pc[0] + 30), min(255, pc[1] + 30), min(255, pc[2] + 30))
            pygame.draw.circle(screen, hi, (px - pr // 4, py - pr // 4), pr // 3, 0)
            pygame.draw.circle(screen, hi, (px, py), pr, 1)
            if has_ring:
                ring_rect = pygame.Rect(px - int(pr * 1.5), py - pr // 4, pr * 3, pr // 2)
                pygame.draw.ellipse(screen, hi, ring_rect, 1)

        # Shooting stars
        for ss in state.get("shooting_stars", []):
            alpha = ss["life"] / ss["max_life"]
            sc = (int(255 * alpha), int(255 * alpha), int(200 * alpha))
            tail_x = ss["x"] - ss["vx"] * 3
            tail_y = ss["y"] - ss["vy"] * 3
            pygame.draw.line(screen, sc, (int(ss["x"]), int(ss["y"])), (int(tail_x), int(tail_y)), 1)

        # Mountain silhouette
        if len(bg["mountains"]) > 2:
            pygame.draw.polygon(screen, MOUNTAIN_COLOR, bg["mountains"], 0)
            if len(bg["mountain_ridge"]) > 1:
                pygame.draw.lines(screen, (22, 28, 38), False, bg["mountain_ridge"], 1)

        # --- Menu ---
        if state.get("menu"):
            state["menu_asteroid_angle"] = state.get("menu_asteroid_angle", 0) + MENU_ASTEROID_ROTATE_SPEED
            g = state["asteroid_size"]
            title = font_large.render("Asteroid Defence", True, WHITE)
            size_text = font.render(f"Asteroid size: {g}", True, GREEN)
            music_text = font.render("0 = Music " + ("On" if state.get("music_on", False) else "Off"), True, GRAY)
            hint = font.render("1-9 = size  |  SPACE = Start", True, GRAY)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
            screen.blit(size_text, (WIDTH // 2 - size_text.get_width() // 2, 220))
            screen.blit(music_text, (WIDTH // 2 - music_text.get_width() // 2, 280))
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 320))
            cached_verts = state.get("menu_asteroid_verts")
            cached_craters = state.get("menu_asteroid_craters")
            if cached_verts is None or state.get("menu_asteroid_cached_size") != g:
                _r = min(size_to_radius(g), 80)
                cached_verts = make_asteroid_vertices(_r)
                cached_craters = make_asteroid_craters(_r)
                state["menu_asteroid_verts"] = cached_verts
                state["menu_asteroid_craters"] = cached_craters
                state["menu_asteroid_cached_size"] = g
            center = (WIDTH // 2, 560)
            angle_rad = math.radians(state["menu_asteroid_angle"])
            cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
            pts = [(center[0] + dx * cos_a - dy * sin_a, center[1] + dx * sin_a + dy * cos_a)
                    for dx, dy in cached_verts]
            pygame.draw.polygon(screen, ASTEROID_FILL, pts, 0)
            for dx, dy, cr in cached_craters:
                rdx = dx * cos_a - dy * sin_a
                rdy = dx * sin_a + dy * cos_a
                pygame.draw.circle(screen, ASTEROID_CRATER, (int(center[0] + rdx), int(center[1] + rdy)), int(cr), 0)
            pygame.draw.polygon(screen, ASTEROID_EDGE, pts, 2)

        # --- Gameplay ---
        elif not state.get("game_over"):
            cx = WIDTH // 2
            ground_y = state.get("ground_y", HEIGHT - GROUND_OFFSET)
            w = math.radians(state["angle"])
            cos_w, sin_w = math.cos(w), math.sin(w)
            pivot_y = ground_y - CANNON_BASE_HEIGHT

            # City silhouette (behind UFO)
            for bbx, bw, bh in bg["buildings"]:
                rect = pygame.Rect(bbx, ground_y - bh, bw, bh + GROUND_OFFSET)
                pygame.draw.rect(screen, CITY_COLOR, rect, 0)
                pygame.draw.rect(screen, CITY_OUTLINE, rect, 1)
            for i, (wx, wy) in enumerate(bg["windows"]):
                if (tick + i * 7) % 150 != 0:
                    pygame.draw.rect(screen, CITY_WINDOW, (wx, wy, 4, 4), 0)

            # Ground gradient
            for gi in range(8):
                gy = ground_y + gi * 2
                gv = max(0, 40 - gi * 5)
                pygame.draw.line(screen, (gv, int(gv * 1.1), gv), (0, gy), (WIDTH, gy), 2)
            # --- Cannon ---
            # Trapezoid base
            top_w = CANNON_BASE_WIDTH * 0.65
            base_pts = [
                (cx - CANNON_BASE_WIDTH // 2, ground_y),
                (cx + CANNON_BASE_WIDTH // 2, ground_y),
                (cx + top_w / 2, ground_y - CANNON_BASE_HEIGHT),
                (cx - top_w / 2, ground_y - CANNON_BASE_HEIGHT),
            ]
            pygame.draw.polygon(screen, CANNON_METAL, base_pts, 0)
            for rx in (cx - 14, cx, cx + 14):
                pygame.draw.circle(screen, CANNON_DARK, (rx, int(pivot_y + CANNON_BASE_HEIGHT // 2)), 3, 0)
                pygame.draw.circle(screen, CANNON_HIGHLIGHT, (rx, int(pivot_y + CANNON_BASE_HEIGHT // 2)), 3, 1)
            pygame.draw.polygon(screen, CANNON_GLOW, base_pts, 2)
            # Tapered barrel
            bw_base = BARREL_WIDTH // 2
            bw_tip = BARREL_WIDTH // 3
            bl = BARREL_LENGTH
            barrel_shape = [(-bw_base, 0), (bw_base, 0), (bw_tip, -bl), (-bw_tip, -bl)]
            barrel = [(cx + px * cos_w - py * sin_w, pivot_y + px * sin_w + py * cos_w)
                       for px, py in barrel_shape]
            pygame.draw.polygon(screen, CANNON_METAL, barrel, 0)
            for seg in (0.33, 0.66):
                ly = -bl * seg
                lw = bw_base + (bw_tip - bw_base) * seg
                ln_x1 = cx + (-lw) * cos_w - ly * sin_w
                ln_y1 = pivot_y + (-lw) * sin_w + ly * cos_w
                ln_x2 = cx + lw * cos_w - ly * sin_w
                ln_y2 = pivot_y + lw * sin_w + ly * cos_w
                pygame.draw.line(screen, CANNON_DARK, (ln_x1, ln_y1), (ln_x2, ln_y2), 2)
            pygame.draw.polygon(screen, CANNON_GLOW, barrel, 2)
            # Muzzle flash
            if state.get("muzzle_flash", 0) > 0:
                flash_t = state["muzzle_flash"] / 6.0
                tip_x = cx + math.sin(w) * bl
                tip_y = pivot_y - math.cos(w) * bl
                for fi, fc in enumerate(MUZZLE_COLORS):
                    fr = int((14 - fi * 4) * flash_t)
                    fb = max(0.1, flash_t * (1 - fi * 0.3))
                    mc = (int(fc[0] * fb), int(fc[1] * fb), int(fc[2] * fb))
                    pygame.draw.circle(screen, mc, (int(tip_x), int(tip_y)), max(1, fr), 0)

            # Bullets
            for b in state["bullets"]:
                trail = b.get("trail", [(b["x"], b["y"])])
                for i, (tx, ty) in enumerate(trail[:-1]):
                    alpha = (i + 1) / max(len(trail), 1)
                    tc = (int(BULLET_GLOW[0] * alpha), int(BULLET_GLOW[1] * alpha),
                          int(BULLET_GLOW[2] * alpha))
                    pygame.draw.line(screen, tc, (int(tx), int(ty)),
                                      (int(trail[i + 1][0]), int(trail[i + 1][1])), 2)
                pygame.draw.circle(screen, BULLET_GLOW, (int(b["x"]), int(b["y"])), 10, 0)
                pygame.draw.circle(screen, (150, 200, 255), (int(b["x"]), int(b["y"])), 5, 0)
                pygame.draw.circle(screen, WHITE, (int(b["x"]), int(b["y"])), 2, 0)

            # Asteroids
            rad = state["asteroid_radius"]
            for a in state["asteroids"]:
                ang = math.radians(a.get("angle", 0))
                cos_a, sin_a = math.cos(ang), math.sin(ang)
                pts = [(a["x"] + dx * cos_a - dy * sin_a, a["y"] + dx * sin_a + dy * cos_a)
                        for dx, dy in a["verts"]]
                # Main body
                pygame.draw.polygon(screen, ASTEROID_FILL, pts, 0)
                # Craters
                for dx, dy, cr in a.get("craters", []):
                    rdx = dx * cos_a - dy * sin_a
                    rdy = dx * sin_a + dy * cos_a
                    pygame.draw.circle(screen, ASTEROID_CRATER,
                                        (int(a["x"] + rdx), int(a["y"] + rdy)), int(cr), 0)
                pygame.draw.polygon(screen, ASTEROID_EDGE, pts, 2)

            # Explosion particles
            for p in state.get("particles", []):
                alpha = p["life"] / p["max_life"]
                sz = max(1, int(p["size"] * alpha))
                pc = (int(p["color"][0] * alpha), int(p["color"][1] * alpha),
                      int(p["color"][2] * alpha))
                pygame.draw.circle(screen, pc, (int(p["x"]), int(p["y"])), sz, 0)

            # HUD: score with background
            score_surf = font.render(f"Score: {state['score']}", True, WHITE)
            bg_rect = pygame.Rect(14, 14, score_surf.get_width() + 16, score_surf.get_height() + 8)
            pygame.draw.rect(screen, (10, 12, 20), bg_rect, 0)
            pygame.draw.rect(screen, (40, 50, 70), bg_rect, 1)
            screen.blit(score_surf, (22, 18))

            # Score popups
            for sp in state.get("score_popups", []):
                sp_alpha = max(0.0, sp["life"] / 40.0)
                pc = (int(255 * sp_alpha), int(220 * sp_alpha), int(80 * sp_alpha))
                popup = font_small.render(sp["text"], True, pc)
                screen.blit(popup, (int(sp["x"]) - popup.get_width() // 2, int(sp["y"])))

        # --- Game Over ---
        else:
            text_over = font_large.render("Game Over!", True, RED)
            text_score = font.render(f"Score: {state['score']}", True, WHITE)
            text_restart = font.render("SPACE = Back to menu", True, WHITE)
            screen.blit(text_over, (WIDTH // 2 - text_over.get_width() // 2, HEIGHT // 2 - 80))
            screen.blit(text_score, (WIDTH // 2 - text_score.get_width() // 2, HEIGHT // 2 - 20))
            screen.blit(text_restart, (WIDTH // 2 - text_restart.get_width() // 2, HEIGHT // 2 + 40))

        # Screen shake
        shake_val = state.get("shake", 0) if not state.get("menu") else 0
        if shake_val > 0:
            si = max(1, int(shake_val))
            ox = random.randint(-si, si)
            oy = random.randint(-si, si)
            temp = screen.copy()
            screen.fill(BLACK)
            screen.blit(temp, (ox, oy))
            state["shake"] = max(0, shake_val - 0.5)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.mixer.music.stop()
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
