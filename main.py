# Asteroid Defence - 2D game in Python with Pygame
# Menu: 1-3 = difficulty, ENTER = Start. Game: Arrows = rotate, SPACE = shoot

import os
import sys
import asyncio
import pygame
import random
import math
import json

# === Settings (defaults; overwritten by config.json if present) ===
def _load_config():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    defaults = {
        "UI_SCALE": 1.0,
        "WIDTH": 600, "HEIGHT": 800,
        "BARREL_WIDTH": 24, "BARREL_LENGTH": 56,
        "CANNON_BASE_WIDTH": 70, "CANNON_BASE_HEIGHT": 22,
        "ROTATE_SPEED": 3.3, "MENU_ASTEROID_ROTATE_SPEED": 3.0,
        "BULLET_SPEED": 12,
        "ASTEROID_RADIUS_MIN": 10, "ASTEROID_RADIUS_MAX": 120,
        "ASTEROID_SIZE_VARIANCE": 0.15,
        "ASTEROID_START_SPEED": 2,
        "ASTEROID_SPEED_INCREASE_PER_HIT": 0.075,
        "ASTEROID_SPEED_INCREASE_PER_FRAME": 0.0005,
        "ASTEROID_SPAWN_INTERVAL": 90,
        "ASTEROID_SPAWN_INTERVAL_MIN": 40,
        "ASTEROID_SPAWN_INTERVAL_DECREASE_EVERY_FRAMES": 500,
        "ASTEROID_SPAWN_INTERVAL_DECREASE_STEP": 5,
        "POINTS_PER_HIT": 5, "POINTS_PER_LEVEL": 100, "SHOT_COST": 2,
        "GOLDEN_ASTEROID_CHANCE": 0.05, "GOLDEN_ASTEROID_MULTIPLIER": 2,
        "GROUND_OFFSET": 20,
        "MAX_PARTICLES": 120, "MAX_HIGHSCORES": 10,
        "POWERUP_RADIUS": 20, "POWERUP_MAX_ON_SCREEN": 3,
        "POWERUP_SPAWN_CHANCE_PER_FRAME": 0.002,
        "POWERUP_EASY_SIZE_MULTIPLIER": 2.0,
        "POWERUP_NORMAL_SIZE_MULTIPLIER": 1.25,
        "MAX_EXTRA_SHOTS": 5,
        "START_LIVES": 3, "MAX_LIVES": 10,
        "SHIELD_DURATION_SEC": 10, "SHIELD_ARC_RADIUS": 320, "SHIELD_ARC_TOP_OFFSET": 180,
        "LASER_DURATION_SEC": 5, "TRIPLE_SHOT_COUNT": 10,
        "TOUCH_DRAG_SENSITIVITY": 4.0,
        "TOUCH_TAP_THRESHOLD": 0.02,
        "CONTROLLER_DEADZONE": 0.15,
        "CONTROLLER_ROTATE_SPEED_FACTOR": 1.0,
        "power_ups": {
            "triple_shot": {"min_level": 2, "spawn_weight": 1, "label": "T"},
            "shield": {"min_level": 1, "spawn_weight": 1, "label": "S"},
            "bomb": {"min_level": 1, "spawn_weight": 1, "label": "B"},
            "laser": {"min_level": 1, "spawn_weight": 0.7, "label": "L"},
            "slow": {"min_level": 1, "spawn_weight": 0.8, "label": "W"},
            "extra_shot": {"min_level": 1, "spawn_weight": 0.6, "label": "+"},
            "life": {"min_level": 0, "spawn_weight": 0.4, "label": "♥"},
        },
    }
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in data.items():
                if k == "power_ups" and isinstance(v, dict):
                    for pk, pv in v.items():
                        if isinstance(pv, dict):
                            if pk in defaults["power_ups"]:
                                defaults["power_ups"][pk].update(pv)
                            else:
                                defaults["power_ups"][pk] = pv
                elif k in defaults and k != "power_ups":
                    defaults[k] = v
        except Exception as e:
            print("Config load failed, using defaults:", e)
    return defaults

_cfg = _load_config()
UI_SCALE = _cfg.get("UI_SCALE", 1.0)
def S(v):
    """Scale a pixel value by UI_SCALE."""
    return int(round(v * UI_SCALE))

WIDTH = S(_cfg["WIDTH"])
HEIGHT = S(_cfg["HEIGHT"])
BARREL_WIDTH = S(_cfg["BARREL_WIDTH"])
BARREL_LENGTH = S(_cfg["BARREL_LENGTH"])
CANNON_BASE_WIDTH = S(_cfg["CANNON_BASE_WIDTH"])
CANNON_BASE_HEIGHT = S(_cfg["CANNON_BASE_HEIGHT"])
ROTATE_SPEED = _cfg["ROTATE_SPEED"]
MENU_ASTEROID_ROTATE_SPEED = _cfg["MENU_ASTEROID_ROTATE_SPEED"]
BULLET_SPEED = _cfg["BULLET_SPEED"] * UI_SCALE
ASTEROID_RADIUS_MIN = S(_cfg["ASTEROID_RADIUS_MIN"])
ASTEROID_RADIUS_MAX = S(_cfg["ASTEROID_RADIUS_MAX"])
ASTEROID_SIZE_VARIANCE = _cfg.get("ASTEROID_SIZE_VARIANCE", 0.15)
ASTEROID_START_SPEED = _cfg["ASTEROID_START_SPEED"] * UI_SCALE
ASTEROID_SPEED_INCREASE_PER_HIT = _cfg["ASTEROID_SPEED_INCREASE_PER_HIT"] * UI_SCALE
ASTEROID_SPEED_INCREASE_PER_FRAME = _cfg["ASTEROID_SPEED_INCREASE_PER_FRAME"] * UI_SCALE
ASTEROID_SPAWN_INTERVAL = _cfg["ASTEROID_SPAWN_INTERVAL"]
ASTEROID_SPAWN_INTERVAL_MIN = _cfg["ASTEROID_SPAWN_INTERVAL_MIN"]
ASTEROID_SPAWN_INTERVAL_DECREASE_EVERY_FRAMES = _cfg["ASTEROID_SPAWN_INTERVAL_DECREASE_EVERY_FRAMES"]
ASTEROID_SPAWN_INTERVAL_DECREASE_STEP = _cfg["ASTEROID_SPAWN_INTERVAL_DECREASE_STEP"]
POINTS_PER_HIT = _cfg["POINTS_PER_HIT"]
POINTS_PER_LEVEL = _cfg.get("POINTS_PER_LEVEL", 100)
SHOT_COST = _cfg.get("SHOT_COST", 2)
GOLDEN_ASTEROID_CHANCE = _cfg.get("GOLDEN_ASTEROID_CHANCE", 0.05)
GOLDEN_ASTEROID_MULTIPLIER = _cfg.get("GOLDEN_ASTEROID_MULTIPLIER", 2)
GROUND_OFFSET = S(_cfg["GROUND_OFFSET"])
MAX_PARTICLES = _cfg["MAX_PARTICLES"]
MAX_HIGHSCORES = _cfg["MAX_HIGHSCORES"]
POWERUP_RADIUS = S(_cfg.get("POWERUP_RADIUS", 20))
POWERUP_MAX_ON_SCREEN = _cfg.get("POWERUP_MAX_ON_SCREEN", 3)
POWERUP_EASY_SIZE_MULTIPLIER = _cfg.get("POWERUP_EASY_SIZE_MULTIPLIER", 2.0)
POWERUP_NORMAL_SIZE_MULTIPLIER = _cfg.get("POWERUP_NORMAL_SIZE_MULTIPLIER", 1.25)
MAX_EXTRA_SHOTS = _cfg.get("MAX_EXTRA_SHOTS", 5)
START_LIVES = _cfg.get("START_LIVES", 3)
MAX_LIVES = _cfg.get("MAX_LIVES", 10)
SHIELD_DURATION_SEC = _cfg.get("SHIELD_DURATION_SEC", 10)
SHIELD_ARC_RADIUS = S(_cfg.get("SHIELD_ARC_RADIUS", 320))
SHIELD_ARC_TOP_OFFSET = S(_cfg.get("SHIELD_ARC_TOP_OFFSET", 180))
LASER_DURATION_SEC = _cfg.get("LASER_DURATION_SEC", 5)
TRIPLE_SHOT_COUNT = _cfg.get("TRIPLE_SHOT_COUNT", 10)
POWERUP_SPAWN_CHANCE_PER_FRAME = _cfg.get("POWERUP_SPAWN_CHANCE_PER_FRAME", 0.002)
TOUCH_DRAG_SENSITIVITY = _cfg.get("TOUCH_DRAG_SENSITIVITY", 4.0)
TOUCH_TAP_THRESHOLD = _cfg.get("TOUCH_TAP_THRESHOLD", 0.02)
CONTROLLER_DEADZONE = _cfg.get("CONTROLLER_DEADZONE", 0.15)
CONTROLLER_ROTATE_SPEED_FACTOR = _cfg.get("CONTROLLER_ROTATE_SPEED_FACTOR", 1.0)
POWERUP_TYPES = _cfg.get("power_ups", {
    "triple_shot": {"min_level": 2, "spawn_weight": 1},
    "shield": {"min_level": 1, "spawn_weight": 1},
    "bomb": {"min_level": 1, "spawn_weight": 1},
    "laser": {"min_level": 1, "spawn_weight": 0.7, "label": "L"},
    "slow": {"min_level": 1, "spawn_weight": 0.8, "label": "W"},
    "extra_shot": {"min_level": 1, "spawn_weight": 0.6, "label": "+"},
    "life": {"min_level": 0, "spawn_weight": 0.4, "label": "♥"},
})

DIFFICULTIES = {
    1: {"name": "Easy", "size": 9, "key": "easy"},
    2: {"name": "Normal", "size": 6, "key": "normal"},
    3: {"name": "Difficult", "size": 3, "key": "difficult"},
}
TEST_MODE_POWERUP_SPAWN_CHANCE = 0.08
TEST_MODE_POWERUP_MAX_ON_SCREEN = 8

POWERUP_COLORS = {
    "triple_shot": (100, 200, 255), "shield": (80, 220, 120), "bomb": (255, 120, 60),
    "laser": (255, 80, 200), "slow": (180, 140, 255), "extra_shot": (255, 220, 50),
    "life": (220, 40, 60),
}
POWERUP_LABELS = {k: v.get("label", k[0].upper()) for k, v in POWERUP_TYPES.items()}
GOLDEN_FILL = (200, 170, 40)
GOLDEN_EDGE = (255, 220, 80)
GOLDEN_CRATER = (140, 120, 30)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 60, 60)
GRAY = (120, 120, 120)
GREEN = (60, 200, 80)
YELLOW = (255, 220, 80)
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
UFO_HEIGHT = S(85)
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


def _segment_point_dist_sq(ax, ay, bx, by, px, py):
    """Squared distance from segment (ax,ay)-(bx,by) to point (px,py)."""
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    c1 = wx * vx + wy * vy
    c2 = vx * vx + vy * vy
    if c2 <= 0:
        return wx * wx + wy * wy
    if c1 <= 0:
        return wx * wx + wy * wy
    if c1 >= c2:
        return (px - bx) ** 2 + (py - by) ** 2
    b = c1 / c2
    pbx, pby = ax + b * vx, ay + b * vy
    return (px - pbx) ** 2 + (py - pby) ** 2


def _asteroid_hits_shield_arc(ax, ay, ar, ground_y):
    """Return True if asteroid circle touches the active shield upper arc."""
    cx_s = WIDTH // 2
    cy_s = ground_y - SHIELD_ARC_TOP_OFFSET
    rx = SHIELD_ARC_RADIUS
    ry = max(1, int(rx * 0.45))
    ex = max(1, rx + ar)
    ey = max(1, ry + ar)
    dx = (ax - cx_s) / ex
    dy = (ay - cy_s) / ey
    return (dx * dx + dy * dy <= 1.0) and (ay <= cy_s + ar)


def draw_heart(screen, cx, cy, size, color):
    """Draw a heart shape at (cx, cy)."""
    s = size
    pts = []
    for deg in range(0, 360, 5):
        t = math.radians(deg)
        x = s * 0.5 * (16 * math.sin(t) ** 3)
        y = -s * 0.5 * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        pts.append((cx + x / 16, cy + y / 16))
    if len(pts) >= 3:
        pygame.draw.polygon(screen, color, pts, 0)


def draw_power_up(screen, x, y, color, label, font, scale=1.0, tick=0, pu_type=None):
    """Draw power-up with glow, pulsing outline, and centered label."""
    r = int(POWERUP_RADIUS * scale)
    pulse = 0.7 + 0.3 * math.sin(tick * 0.12)
    glow_r = int(r * 1.5)
    glow_col = (max(0, min(255, int(color[0] * 0.3 * pulse))),
                max(0, min(255, int(color[1] * 0.3 * pulse))),
                max(0, min(255, int(color[2] * 0.3 * pulse))))
    pygame.draw.circle(screen, glow_col, (x, y), glow_r, 0)
    if pu_type == "life":
        draw_heart(screen, x, y, r * 1.1, color)
        hi = (min(255, color[0] + 80), min(255, color[1] + 40), min(255, color[2] + 40))
        draw_heart(screen, x - 1, y - 1, r * 0.7, hi)
    else:
        pts = [(x, y - r), (x + r, y), (x, y + r), (x - r, y)]
        pygame.draw.polygon(screen, color, pts, 0)
        hi = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60))
        hi_pts = [(x, y - r + 4), (x - r + 6, y), (x, y - 2)]
        if len(hi_pts) >= 3:
            pygame.draw.polygon(screen, hi, hi_pts, 0)
        outline_w = 2 if pulse < 0.85 else 3
        bright = (min(255, int(color[0] + 100 * pulse)), min(255, int(color[1] + 100 * pulse)), min(255, int(color[2] + 100 * pulse)))
        pygame.draw.polygon(screen, bright, pts, outline_w)
        txt = font.render(label, True, WHITE)
        tr = txt.get_rect(center=(x, y + 1))
        screen.blit(txt, tr)


def get_assets_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def _keep_largest_opaque_component(img, alpha_min=8):
    """Keep only the largest connected opaque component (removes speckles)."""
    w, h = img.get_size()
    visited = [[False for _ in range(w)] for _ in range(h)]
    largest = []
    largest_size = 0
    for y in range(h):
        for x in range(w):
            if visited[y][x]:
                continue
            visited[y][x] = True
            if img.get_at((x, y))[3] <= alpha_min:
                continue
            stack = [(x, y)]
            comp = []
            while stack:
                cx, cy = stack.pop()
                comp.append((cx, cy))
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                        visited[ny][nx] = True
                        if img.get_at((nx, ny))[3] > alpha_min:
                            stack.append((nx, ny))
            if len(comp) > largest_size:
                largest = comp
                largest_size = len(comp)
    if largest_size <= 0:
        return
    keep = set(largest)
    for y in range(h):
        for x in range(w):
            r, g, b, a = img.get_at((x, y))
            if a > alpha_min and (x, y) not in keep:
                img.set_at((x, y), (r, g, b, 0))


def _crop_to_opaque_bounds(img, alpha_min=8):
    """Crop image to bounding box of opaque pixels."""
    w, h = img.get_size()
    min_x, min_y = w, h
    max_x, max_y = -1, -1
    for y in range(h):
        for x in range(w):
            if img.get_at((x, y))[3] > alpha_min:
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y
    if max_x < min_x or max_y < min_y:
        return img
    rect = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    return img.subsurface(rect).copy()


def _find_sprite_pivot(img, alpha_min=8):
    """Estimate cannon pivot from lowest opaque row."""
    w, h = img.get_size()
    for y in range(h - 1, -1, -1):
        xs = [x for x in range(w) if img.get_at((x, y))[3] > alpha_min]
        if xs:
            px = int(sum(xs) / len(xs))
            py = y + 1
            # Pull pivot slightly upward for more natural turret rotation.
            py = max(1, int(py - max(1, h * 0.08)))
            return px, py
    return w // 2, h


def load_cannon_sprite(assets_dir):
    """Load cannon sprite and prepare style/rotation fit for the scene."""
    for name in ("cannon_laser_ohne_fluegel.png", "cannon.png"):
        path = os.path.join(assets_dir, name)
        if not os.path.isfile(path):
            continue
        try:
            img = pygame.image.load(path)
            img = img.convert_alpha()
            iw, ih = img.get_width(), img.get_height()
            if iw <= 0 or ih <= 0:
                continue
            # Fast path: scale first, then run one cleanup pass on the small image.
            target_h = int((BARREL_LENGTH + CANNON_BASE_HEIGHT) * 1.28)
            scale = target_h / ih
            nw = max(1, int(iw * scale))
            nh = max(1, int(ih * scale))
            img = pygame.transform.scale(img, (nw, nh))

            # Remove white background after scaling (captures interpolation artifacts too).
            post_thresh = 200
            for y in range(nh):
                for x in range(nw):
                    r, g, b, a = img.get_at((x, y))
                    if r >= post_thresh and g >= post_thresh and b >= post_thresh:
                        img.set_at((x, y), (r, g, b, 0))
            # Keep only the main sprite body to remove tiny leftovers.
            _keep_largest_opaque_component(img, alpha_min=8)
            img = _crop_to_opaque_bounds(img, alpha_min=8)
            nw, nh = img.get_width(), img.get_height()
            if nw <= 0 or nh <= 0:
                continue

            # 5) Slight cool tint so sprite blends into the night palette.
            tint = pygame.Surface((nw, nh), pygame.SRCALPHA)
            tint.fill((185, 195, 220, 255))
            img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            pivot_x, pivot_y_img = _find_sprite_pivot(img, alpha_min=8)
            pad = max(nw, nh) + S(20)
            surf = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))
            surf.blit(img, (pad - pivot_x, pad - pivot_y_img))
            if not _is_web():
                print("  Cannon sprite:", name)
            return surf
        except Exception as e:
            if not _is_web():
                print("  Cannon sprite failed:", name, e)
    return None


def _is_web():
    return sys.platform == "emscripten"


def _web_prompt_name():
    """Show a browser prompt dialog for name entry (mobile-friendly)."""
    try:
        import platform as plat
        name = plat.window.prompt("New Highscore! Enter your name:", "")
        if name is None:
            return ""
        return str(name).strip()[:15]
    except Exception:
        return ""


def _request_fullscreen():
    """Request fullscreen on web (requires user gesture context)."""
    if not _is_web():
        return
    try:
        import platform as plat
        el = plat.window.document.documentElement
        if hasattr(el, "requestFullscreen"):
            el.requestFullscreen()
        elif hasattr(el, "webkitRequestFullscreen"):
            el.webkitRequestFullscreen()
    except Exception:
        pass


def get_highscore_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")


def load_highscores():
    default = {"easy": [], "normal": [], "difficult": []}
    if _is_web():
        try:
            import platform
            raw = platform.window.localStorage.getItem("asteroid_defence_highscores")
            if raw:
                data = json.loads(raw)
                for key in default:
                    if key not in data:
                        data[key] = []
                return data
        except Exception:
            pass
        return default
    path = get_highscore_path()
    if not os.path.isfile(path):
        return default
    try:
        with open(path, "r") as f:
            data = json.load(f)
        for key in default:
            if key not in data:
                data[key] = []
        return data
    except Exception:
        return default


def save_highscores(data):
    if _is_web():
        try:
            import platform
            platform.window.localStorage.setItem(
                "asteroid_defence_highscores", json.dumps(data))
        except Exception as e:
            print("Could not save highscores to localStorage:", e)
        return
    try:
        with open(get_highscore_path(), "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print("Could not save highscores:", e)


def is_highscore(data, difficulty, score):
    if score <= 0:
        return False
    key = DIFFICULTIES[difficulty]["key"]
    entries = data.get(key, [])
    if len(entries) < MAX_HIGHSCORES:
        return True
    return score > entries[-1]["score"]


def add_highscore(data, difficulty, name, score):
    key = DIFFICULTIES[difficulty]["key"]
    entries = data.get(key, [])
    entries.append({"name": name if name else "-", "score": score})
    entries.sort(key=lambda e: e["score"], reverse=True)
    data[key] = entries[:MAX_HIGHSCORES]
    return data


def make_background():
    """Generate random background elements (different every start)."""
    rng = random.Random()
    stars = []
    for _ in range(70):
        phase = rng.uniform(0, 2 * math.pi)
        speed = rng.uniform(0.02, 0.08)
        stars.append((rng.randint(0, WIDTH - 1), rng.randint(0, HEIGHT - 1),
                       rng.choice([1, 1, 2]), rng.randint(0, len(STAR_COLORS) - 1),
                       phase, speed))
    planets = []
    for _ in range(2):
        x = rng.randint(S(80), WIDTH - S(80))
        y = rng.randint(S(80), HEIGHT - S(200))
        r = rng.randint(S(20), S(40))
        c = rng.choice([(80, 60, 90), (60, 70, 100), (90, 55, 70), (50, 80, 90)])
        has_ring = rng.random() < 0.4
        planets.append((x, y, r, c, has_ring))
    nebulae = []
    for _ in range(3):
        nebulae.append((rng.randint(0, WIDTH), rng.randint(0, HEIGHT - S(150)),
                         rng.randint(S(50), S(110)), rng.choice(NEBULA_COLORS)))
    mrng = random.Random()
    mountain_ridge = [(0, S(700))]
    mx = 0
    while mx <= WIDTH:
        mountain_ridge.append((mx, mrng.randint(S(580), S(690))))
        mx += mrng.randint(S(40), S(90))
    mountain_ridge.append((WIDTH, S(700)))
    mountains = mountain_ridge + [(WIDTH, HEIGHT), (0, HEIGHT)]
    crng = random.Random()
    buildings = []
    bx = 0
    while bx < WIDTH:
        bw = crng.randint(S(18), S(50))
        bh = crng.randint(S(12), S(65))
        buildings.append((bx, bw, bh))
        bx += bw + crng.randint(S(2), S(8))
    windows = []
    for bbx, bw, bh in buildings:
        top = HEIGHT - GROUND_OFFSET - bh
        cols = max(1, bw // S(12))
        rows = max(1, bh // S(14))
        for row in range(rows):
            for col in range(cols):
                wx = bbx + S(4) + col * max(1, (bw - S(8)) // max(cols, 1))
                wy = top + S(4) + row * S(14)
                if wx < bbx + bw - S(4) and wy < HEIGHT - GROUND_OFFSET - S(4) and crng.random() < 0.5:
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
        speed = random.uniform(1.5 * UI_SCALE, 6 * UI_SCALE)
        size = random.uniform(2 * UI_SCALE, 7 * UI_SCALE)
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


def make_menu_state(difficulty, angle=0, test_mode=False):
    _r = min(size_to_radius(DIFFICULTIES[difficulty]["size"]), S(80))
    return {
        "menu": True, "difficulty": difficulty,
        "menu_asteroid_angle": angle,
        "menu_asteroid_verts": make_asteroid_vertices(_r),
        "menu_asteroid_craters": make_asteroid_craters(_r),
        "menu_asteroid_cached_diff": difficulty,
        "test_mode": test_mode,
    }


async def main():
    pygame.init()
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
    except Exception as e:
        print("Mixer init failed:", e)
    _flags = pygame.DOUBLEBUF
    if not _is_web():
        _flags |= pygame.HWSURFACE
    screen = pygame.display.set_mode((WIDTH, HEIGHT), _flags)
    pygame.display.set_caption("Asteroid Defence")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, S(48))
    font_large = pygame.font.Font(None, S(72))
    font_small = pygame.font.Font(None, S(36))
    font_tiny = pygame.font.Font(None, S(28))

    pygame.joystick.init()
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Controller: {joystick.get_name()}")

    touch_state = {"active": False, "start_x": 0.0, "start_y": 0.0, "moved": 0.0, "start_tick": 0}

    assets_dir = get_assets_dir()
    print("Assets folder:", os.path.abspath(assets_dir))
    if not os.path.isdir(assets_dir):
        print("  -> Folder missing! Create 'assets' next to main.py and add files.")
    cannon_sprite = load_cannon_sprite(assets_dir) if os.path.isdir(assets_dir) else None
    cannon_tip_len = int(BARREL_LENGTH * (1.22 if cannon_sprite is not None else 1.0))
    shoot_sound = load_shoot_sound(assets_dir, log=True) if os.path.isdir(assets_dir) else None
    bg = make_background()
    highscores = load_highscores()

    def new_game(difficulty, test_mode=False):
        asteroid_size = DIFFICULTIES[difficulty]["size"]
        return {
            "angle": 0,
            "bullets": [],
            "asteroids": [],
            "power_ups": [],
            "score": 0,
            "asteroid_speed": ASTEROID_START_SPEED,
            "frame": 0,
            "next_spawn_frame": ASTEROID_SPAWN_INTERVAL,
            "game_over": False,
            "ground_y": HEIGHT - GROUND_OFFSET,
            "asteroid_size": asteroid_size,
            "asteroid_radius": size_to_radius(asteroid_size),
            "particles": [],
            "shake": 0,
            "score_popups": [],
            "muzzle_flash": 0,
            "shooting_stars": [],
            "difficulty": difficulty,
            "triple_shot_remaining": 0,
            "shield_remaining_frames": 0,
            "laser_remaining_frames": 0,
            "extra_shots": 0,
            "slow_flash": 0,
            "lives": START_LIVES,
            "test_mode": test_mode,
            "test_seen_powerups": set(),
        }

    def fire_cannon(st):
        """Fire the cannon. Returns True if fired."""
        if st.get("menu") or st.get("game_over") or st.get("paused"):
            return False
        if st.get("laser_remaining_frames", 0) > 0:
            return False
        rad = math.radians(st["angle"])
        cx = WIDTH // 2
        pivot_y = HEIGHT - GROUND_OFFSET - CANNON_BASE_HEIGHT
        base_bullets = 1 + st.get("extra_shots", 0)
        num_bullets = 3 if st.get("triple_shot_remaining", 0) > 0 else base_bullets
        if st.get("triple_shot_remaining", 0) > 0:
            st["triple_shot_remaining"] -= 1
        spread_deg = 8
        for i in range(num_bullets):
            angle_off = (i - (num_bullets - 1) / 2) * spread_deg
            r = math.radians(st["angle"] + angle_off)
            vx = BULLET_SPEED * math.sin(r)
            vy = -BULLET_SPEED * math.cos(r)
            tx = cx + math.sin(r) * cannon_tip_len
            ty = pivot_y - math.cos(r) * cannon_tip_len
            st["bullets"].append({"x": tx, "y": ty, "vx": vx, "vy": vy,
                                  "trail": [(tx, ty)], "age": 0})
        st["score"] = max(0, st["score"] - SHOT_COST)
        st["muzzle_flash"] = 6
        st["shake"] = max(st.get("shake", 0), 2)
        if shoot_sound is not None:
            shoot_sound.play()
        return True

    state = make_menu_state(2)

    tick = 0
    running = True
    while running:
        tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                # --- Name entry mode ---
                if state.get("entering_name"):
                    if event.key == pygame.K_RETURN:
                        name = state.get("player_name", "").strip()
                        highscores = add_highscore(highscores, state["difficulty"], name, state["final_score"])
                        save_highscores(highscores)
                        state = make_menu_state(
                            state["difficulty"],
                            state.get("menu_asteroid_angle", 0),
                            state.get("test_mode", False),
                        )
                    elif event.key == pygame.K_BACKSPACE:
                        state["player_name"] = state.get("player_name", "")[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        highscores = add_highscore(highscores, state["difficulty"], "", state["final_score"])
                        save_highscores(highscores)
                        state = make_menu_state(
                            state["difficulty"],
                            state.get("menu_asteroid_angle", 0),
                            state.get("test_mode", False),
                        )
                    elif event.unicode and len(state.get("player_name", "")) < 15:
                        if event.unicode.isprintable() and event.unicode not in ('\r', '\n', '\t'):
                            state["player_name"] = state.get("player_name", "") + event.unicode
                    continue

                if event.key == pygame.K_ESCAPE:
                    if state.get("menu"):
                        running = False
                    elif state.get("paused"):
                        state = make_menu_state(
                            state.get("difficulty", 2),
                            state.get("menu_asteroid_angle", 0),
                            state.get("test_mode", False),
                        )
                    else:
                        state = make_menu_state(
                            state.get("difficulty", 2),
                            state.get("menu_asteroid_angle", 0),
                            state.get("test_mode", False),
                        )
                        continue

                if not state.get("menu") and not state.get("game_over") and not state.get("entering_name") and event.key == pygame.K_RETURN:
                    state["paused"] = not state.get("paused", False)
                    continue

                if state.get("menu"):
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        state["difficulty"] = 1
                        state["test_mode"] = False
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        state["difficulty"] = 2
                        state["test_mode"] = False
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        state["difficulty"] = 3
                        state["test_mode"] = False
                    elif event.key in (pygame.K_5, pygame.K_KP5):
                        # Hidden test mode (not shown in menu options).
                        state["test_mode"] = True
                    elif event.key == pygame.K_RETURN:
                        saved_angle = state.get("menu_asteroid_angle", 0)
                        diff = state["difficulty"]
                        _request_fullscreen()
                        state = new_game(diff, state.get("test_mode", False))
                        state["menu_asteroid_angle"] = saved_angle
                    diff = state.get("difficulty", 2)
                    if state.get("menu") and state.get("menu_asteroid_cached_diff") != diff:
                        _r = min(size_to_radius(DIFFICULTIES[diff]["size"]), S(80))
                        state["menu_asteroid_verts"] = make_asteroid_vertices(_r)
                        state["menu_asteroid_craters"] = make_asteroid_craters(_r)
                        state["menu_asteroid_cached_diff"] = diff
                    continue

                if state.get("game_over") and event.key == pygame.K_RETURN:
                    score = state.get("score", 0)
                    diff = state.get("difficulty", 2)
                    if is_highscore(highscores, diff, score):
                        if _is_web():
                            name = _web_prompt_name()
                            highscores = add_highscore(highscores, diff, name, score)
                            save_highscores(highscores)
                            state = make_menu_state(diff, state.get("menu_asteroid_angle", 0), state.get("test_mode", False))
                        else:
                            state["entering_name"] = True
                            state["player_name"] = ""
                            state["final_score"] = score
                    else:
                        state = make_menu_state(
                            diff,
                            state.get("menu_asteroid_angle", 0),
                            state.get("test_mode", False),
                        )
                    continue

                if not state.get("game_over") and not state.get("paused") and event.key in (pygame.K_SPACE, pygame.K_LCTRL, pygame.K_RCTRL):
                    fire_cannon(state)

            # --- Controller events ---
            if event.type == pygame.JOYDEVICEADDED:
                if joystick is None:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joystick.init()
                    print(f"Controller connected: {joystick.get_name()}")
            if event.type == pygame.JOYDEVICEREMOVED:
                joystick = None
                print("Controller disconnected")

            if event.type == pygame.JOYBUTTONDOWN and joystick is not None:
                if state.get("entering_name"):
                    if event.button == 0:
                        name = state.get("player_name", "").strip()
                        highscores = add_highscore(highscores, state["difficulty"], name, state["final_score"])
                        save_highscores(highscores)
                        state = make_menu_state(state["difficulty"], state.get("menu_asteroid_angle", 0), state.get("test_mode", False))
                elif state.get("menu"):
                    if event.button in (0, 7):
                        saved_angle = state.get("menu_asteroid_angle", 0)
                        diff = state["difficulty"]
                        _request_fullscreen()
                        state = new_game(diff, state.get("test_mode", False))
                        state["menu_asteroid_angle"] = saved_angle
                elif state.get("game_over"):
                    if event.button in (0, 7):
                        score = state.get("score", 0)
                        diff = state.get("difficulty", 2)
                        if is_highscore(highscores, diff, score):
                            if _is_web():
                                name = _web_prompt_name()
                                highscores = add_highscore(highscores, diff, name, score)
                                save_highscores(highscores)
                                state = make_menu_state(diff, state.get("menu_asteroid_angle", 0), state.get("test_mode", False))
                            else:
                                state["entering_name"] = True
                                state["player_name"] = ""
                                state["final_score"] = score
                        else:
                            state = make_menu_state(diff, state.get("menu_asteroid_angle", 0), state.get("test_mode", False))
                else:
                    if event.button == 0:
                        fire_cannon(state)
                    elif event.button == 1:
                        state["paused"] = not state.get("paused", False)
                    elif event.button == 7:
                        state["paused"] = not state.get("paused", False)

            if event.type == pygame.JOYHATMOTION and joystick is not None:
                if state.get("menu"):
                    hx, hy = event.value
                    if hx < 0:
                        state["difficulty"] = max(1, state.get("difficulty", 2) - 1)
                        state["test_mode"] = False
                    elif hx > 0:
                        state["difficulty"] = min(3, state.get("difficulty", 2) + 1)
                        state["test_mode"] = False
                    diff = state.get("difficulty", 2)
                    if state.get("menu_asteroid_cached_diff") != diff:
                        _r = min(size_to_radius(DIFFICULTIES[diff]["size"]), S(80))
                        state["menu_asteroid_verts"] = make_asteroid_vertices(_r)
                        state["menu_asteroid_craters"] = make_asteroid_craters(_r)
                        state["menu_asteroid_cached_diff"] = diff

            # --- Touch events ---
            if event.type == pygame.FINGERDOWN:
                touch_state["active"] = True
                touch_state["start_x"] = event.x
                touch_state["start_y"] = event.y
                touch_state["moved"] = 0.0
                touch_state["start_tick"] = tick

            if event.type == pygame.FINGERMOTION and touch_state["active"]:
                touch_state["moved"] += abs(event.dx) + abs(event.dy)
                if not state.get("menu") and not state.get("game_over") and not state.get("paused") and not state.get("entering_name"):
                    state["angle"] += event.dx * TOUCH_DRAG_SENSITIVITY * ROTATE_SPEED * 20
                    state["angle"] = max(-80, min(80, state["angle"]))

            if event.type == pygame.FINGERUP:
                if touch_state["active"]:
                    was_tap = touch_state["moved"] < TOUCH_TAP_THRESHOLD
                    touch_x = event.x * WIDTH
                    touch_y = event.y * HEIGHT
                    if state.get("entering_name"):
                        if was_tap:
                            btn_y = HEIGHT // 2 + S(100)
                            btn_h = S(40)
                            btn_w = S(120)
                            gap = S(20)
                            confirm_x = WIDTH // 2 - btn_w - gap // 2
                            skip_x = WIDTH // 2 + gap // 2
                            if btn_y <= touch_y <= btn_y + btn_h:
                                if confirm_x <= touch_x <= confirm_x + btn_w:
                                    name = state.get("player_name", "").strip()
                                    highscores = add_highscore(highscores, state["difficulty"], name, state["final_score"])
                                    save_highscores(highscores)
                                    state = make_menu_state(state["difficulty"], state.get("menu_asteroid_angle", 0), state.get("test_mode", False))
                                elif skip_x <= touch_x <= skip_x + btn_w:
                                    highscores = add_highscore(highscores, state["difficulty"], "", state["final_score"])
                                    save_highscores(highscores)
                                    state = make_menu_state(state["difficulty"], state.get("menu_asteroid_angle", 0), state.get("test_mode", False))
                    elif state.get("menu"):
                        if was_tap:
                            y_diff_top = S(122)
                            y_diff_bot = S(162)
                            if y_diff_top <= touch_y <= y_diff_bot:
                                for d_num in DIFFICULTIES:
                                    cx_d = WIDTH // 2 + (d_num - 2) * S(160)
                                    if abs(touch_x - cx_d) < S(80):
                                        state["difficulty"] = d_num
                                        state["test_mode"] = False
                                        diff = d_num
                                        if state.get("menu_asteroid_cached_diff") != diff:
                                            _r = min(size_to_radius(DIFFICULTIES[diff]["size"]), S(80))
                                            state["menu_asteroid_verts"] = make_asteroid_vertices(_r)
                                            state["menu_asteroid_craters"] = make_asteroid_craters(_r)
                                            state["menu_asteroid_cached_diff"] = diff
                                        break
                            elif S(198) <= touch_y <= S(248):
                                saved_angle = state.get("menu_asteroid_angle", 0)
                                diff = state["difficulty"]
                                _request_fullscreen()
                                state = new_game(diff, state.get("test_mode", False))
                                state["menu_asteroid_angle"] = saved_angle
                    elif state.get("game_over"):
                        if was_tap:
                            score = state.get("score", 0)
                            diff = state.get("difficulty", 2)
                            if is_highscore(highscores, diff, score):
                                if _is_web():
                                    name = _web_prompt_name()
                                    highscores = add_highscore(highscores, diff, name, score)
                                    save_highscores(highscores)
                                    state = make_menu_state(diff, state.get("menu_asteroid_angle", 0), state.get("test_mode", False))
                                else:
                                    state["entering_name"] = True
                                    state["player_name"] = ""
                                    state["final_score"] = score
                            else:
                                state = make_menu_state(diff, state.get("menu_asteroid_angle", 0), state.get("test_mode", False))
                    elif state.get("paused"):
                        if was_tap:
                            btn_w = S(180)
                            btn_h = S(40)
                            btn_x = WIDTH // 2 - btn_w // 2
                            resume_y = HEIGHT // 2 + S(10)
                            menu_y = HEIGHT // 2 + S(60)
                            if resume_y <= touch_y <= resume_y + btn_h and btn_x <= touch_x <= btn_x + btn_w:
                                state["paused"] = False
                            elif menu_y <= touch_y <= menu_y + btn_h and btn_x <= touch_x <= btn_x + btn_w:
                                state = make_menu_state(state.get("difficulty", 2), state.get("menu_asteroid_angle", 0), state.get("test_mode", False))
                    else:
                        if was_tap:
                            fire_cannon(state)
                    touch_state["active"] = False

        # --- Controller analog stick (continuous, polled every frame) ---
        if joystick is not None and not state.get("menu") and not state.get("game_over") and not state.get("paused"):
            try:
                axis_x = joystick.get_axis(0)
                if abs(axis_x) > CONTROLLER_DEADZONE:
                    state["angle"] += axis_x * ROTATE_SPEED * CONTROLLER_ROTATE_SPEED_FACTOR
                    state["angle"] = max(-80, min(80, state["angle"]))
            except Exception:
                pass

        # --- Game logic ---
        if not state.get("menu") and not state.get("game_over") and not state.get("paused"):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                state["angle"] -= ROTATE_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                state["angle"] += ROTATE_SPEED
            state["angle"] = max(-80, min(80, state["angle"]))

            diff = state.get("difficulty", 2)
            if diff == 1:
                pu_size_mult = POWERUP_EASY_SIZE_MULTIPLIER
            elif diff == 2:
                pu_size_mult = POWERUP_NORMAL_SIZE_MULTIPLIER
            else:
                pu_size_mult = 1.0
            pu_radius_eff = POWERUP_RADIUS * pu_size_mult
            state["frame"] += 1
            r = state["asteroid_radius"]
            # Spawn interval decreases over time (more asteroids = harder)
            steps = state["frame"] // ASTEROID_SPAWN_INTERVAL_DECREASE_EVERY_FRAMES
            current_interval = max(
                ASTEROID_SPAWN_INTERVAL_MIN,
                ASTEROID_SPAWN_INTERVAL - steps * ASTEROID_SPAWN_INTERVAL_DECREASE_STEP,
            )
            if state["frame"] >= state.get("next_spawn_frame", current_interval):
                state["next_spawn_frame"] = state["frame"] + current_interval
                var = ASTEROID_SIZE_VARIANCE
                actual_r = max(8, int(r * random.uniform(1 - var, 1 + var)))
                x = random.randint(actual_r, WIDTH - actual_r)
                verts = make_asteroid_vertices(actual_r)
                craters = make_asteroid_craters(actual_r)
                is_golden = random.random() < GOLDEN_ASTEROID_CHANCE
                state["asteroids"].append({
                    "x": x, "y": -actual_r * 2, "verts": verts, "craters": craters,
                    "angle": random.uniform(0, 360), "rot_speed": random.uniform(0.5, 2.5),
                    "r": actual_r, "golden": is_golden,
                })

            level = state["score"] // POINTS_PER_LEVEL
            # Power-up spawn: weighted random by config (min_level, spawn_weight), max on screen from config
            test_mode = state.get("test_mode", False)
            max_powerups_on_screen = TEST_MODE_POWERUP_MAX_ON_SCREEN if test_mode else POWERUP_MAX_ON_SCREEN
            spawn_chance = TEST_MODE_POWERUP_SPAWN_CHANCE if test_mode else POWERUP_SPAWN_CHANCE_PER_FRAME
            if len(state.get("power_ups", [])) < max_powerups_on_screen:
                if random.random() < spawn_chance:
                    if test_mode:
                        # In test mode all upgrades are available from level 0 and appear very frequently.
                        all_types = list(POWERUP_TYPES.keys())
                        seen = state.setdefault("test_seen_powerups", set())
                        unseen = [t for t in all_types if t not in seen]
                        pu_type = random.choice(unseen if unseen else all_types)
                        seen.add(pu_type)
                    else:
                        allowed = [(t, info) for t, info in POWERUP_TYPES.items() if info.get("min_level", 1) <= level]
                        if not allowed:
                            pu_type = None
                        else:
                            types = [x[0] for x in allowed]
                            weights = [POWERUP_TYPES[t].get("spawn_weight", 1) for t in types]
                            pu_type = random.choices(types, weights=weights, k=1)[0]
                    if pu_type is not None:
                        spawn_r = int(pu_radius_eff) + 5
                        state.setdefault("power_ups", []).append({
                            "x": random.randint(spawn_r, WIDTH - spawn_r),
                            "y": -spawn_r * 2,
                            "type": pu_type,
                        })

            for b in state["bullets"][:]:
                b["x"] += b["vx"]
                b["y"] += b["vy"]
                b["age"] = b.get("age", 0) + 1
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
                ar = a.get("r", state["asteroid_radius"])
                if state.get("shield_remaining_frames", 0) > 0 and _asteroid_hits_shield_arc(a["x"], a["y"], ar, state["ground_y"]):
                    if a in state["asteroids"]:
                        state["asteroids"].remove(a)
                    if len(state["particles"]) < MAX_PARTICLES:
                        state["particles"].extend(create_explosion(a["x"], a["y"], count=10))
                    state["shake"] = max(state.get("shake", 0), 6)
                    continue
                if a["y"] + ar >= state["ground_y"]:
                    if state.get("shield_remaining_frames", 0) > 0:
                        if a in state["asteroids"]:
                            state["asteroids"].remove(a)
                        if len(state["particles"]) < MAX_PARTICLES:
                            state["particles"].extend(create_explosion(a["x"], state["ground_y"]))
                        state["shake"] = max(state.get("shake", 0), 6)
                    else:
                        state["lives"] = state.get("lives", 0) - 1
                        if a in state["asteroids"]:
                            state["asteroids"].remove(a)
                        if len(state["particles"]) < MAX_PARTICLES:
                            state["particles"].extend(create_explosion(a["x"], state["ground_y"]))
                        state["shake"] = max(state.get("shake", 0), 10)
                        if state["lives"] <= 0:
                            state["game_over"] = True
                            state["shake"] = 15
                    break
                state["asteroid_speed"] += ASTEROID_SPEED_INCREASE_PER_FRAME

            for pu in state.get("power_ups", [])[:]:
                pu["y"] += state["asteroid_speed"]
                if pu["y"] - pu_radius_eff > state["ground_y"]:
                    state["power_ups"].remove(pu)

            # Laser: continuous beam destroys asteroids and power-ups in line of fire
            if state.get("laser_remaining_frames", 0) > 0:
                rad = math.radians(state["angle"])
                cx = WIDTH // 2
                pivot_y = HEIGHT - GROUND_OFFSET - CANNON_BASE_HEIGHT
                tip_x = cx + math.sin(rad) * cannon_tip_len
                tip_y = pivot_y - math.cos(rad) * cannon_tip_len
                dy = -math.cos(rad)
                if abs(dy) < 0.01:
                    end_x, end_y = tip_x + (1 if math.sin(rad) >= 0 else -1) * WIDTH, tip_y
                else:
                    t = (0 - tip_y) / dy
                    t = max(0, min(t, HEIGHT * 2))
                    end_x = tip_x + math.sin(rad) * t
                    end_y = tip_y + dy * t
                for a in state["asteroids"][:]:
                    ar = a.get("r", state["asteroid_radius"])
                    if _segment_point_dist_sq(tip_x, tip_y, end_x, end_y, a["x"], a["y"]) <= ar * ar:
                        if a in state["asteroids"]:
                            state["asteroids"].remove(a)
                        pts_mult = GOLDEN_ASTEROID_MULTIPLIER if a.get("golden") else 1
                        state["score"] += POINTS_PER_HIT * pts_mult
                        state["asteroid_speed"] += ASTEROID_SPEED_INCREASE_PER_HIT
                        if len(state["particles"]) < MAX_PARTICLES:
                            state["particles"].extend(create_explosion(a["x"], a["y"]))
                for pu in state.get("power_ups", [])[:]:
                    if _segment_point_dist_sq(tip_x, tip_y, end_x, end_y, pu["x"], pu["y"]) <= pu_radius_eff * pu_radius_eff:
                        if pu in state["power_ups"]:
                            state["power_ups"].remove(pu)
                        ptype = pu["type"]
                        info = POWERUP_TYPES.get(ptype, {})
                        if ptype == "triple_shot":
                            state["triple_shot_remaining"] = TRIPLE_SHOT_COUNT
                        elif ptype == "shield":
                            state["shield_remaining_frames"] = max(state.get("shield_remaining_frames", 0), int(SHIELD_DURATION_SEC * 60))
                        elif ptype == "laser":
                            state["laser_remaining_frames"] = max(state.get("laser_remaining_frames", 0), int(LASER_DURATION_SEC * 60))
                        elif ptype == "slow":
                            state["asteroid_speed"] = max(0.5, state["asteroid_speed"] * 0.9)
                            state["slow_flash"] = 30
                        elif ptype == "extra_shot":
                            state["extra_shots"] = min(MAX_EXTRA_SHOTS - 1, state.get("extra_shots", 0) + 1)
                        elif ptype == "life":
                            state["lives"] = min(MAX_LIVES, state.get("lives", 0) + 1)
                        elif ptype == "bomb":
                            for a in state["asteroids"][:]:
                                if len(state["particles"]) < MAX_PARTICLES:
                                    state["particles"].extend(create_explosion(a["x"], a["y"], count=12))
                                pts_mult = GOLDEN_ASTEROID_MULTIPLIER if a.get("golden") else 1
                                state["score"] += POINTS_PER_HIT * pts_mult
                                state["asteroid_speed"] += ASTEROID_SPEED_INCREASE_PER_HIT
                            state["asteroids"] = []
                            state["shake"] = max(state.get("shake", 0), 8)
                state["laser_remaining_frames"] = state["laser_remaining_frames"] - 1

            for b in state["bullets"][:]:
                for pu in state.get("power_ups", [])[:]:
                    dist = math.sqrt((b["x"] - pu["x"]) ** 2 + (b["y"] - pu["y"]) ** 2)
                    if dist < pu_radius_eff + 5:
                        if b in state["bullets"]:
                            state["bullets"].remove(b)
                        if pu in state["power_ups"]:
                            state["power_ups"].remove(pu)
                        ptype = pu["type"]
                        popup_text = ""
                        if ptype == "triple_shot":
                            state["triple_shot_remaining"] = TRIPLE_SHOT_COUNT
                            popup_text = "3x Shot!"
                        elif ptype == "shield":
                            state["shield_remaining_frames"] = max(state.get("shield_remaining_frames", 0), int(SHIELD_DURATION_SEC * 60))
                            popup_text = "Shield!"
                        elif ptype == "life":
                            state["lives"] = min(MAX_LIVES, state.get("lives", 0) + 1)
                            popup_text = "+1 Life!"
                        elif ptype == "laser":
                            state["laser_remaining_frames"] = int(LASER_DURATION_SEC * 60)
                            popup_text = "Laser!"
                        elif ptype == "slow":
                            state["asteroid_speed"] = max(0.5, state["asteroid_speed"] * 0.9)
                            state["slow_flash"] = 30
                            popup_text = "Slow!"
                        elif ptype == "extra_shot":
                            state["extra_shots"] = min(MAX_EXTRA_SHOTS - 1, state.get("extra_shots", 0) + 1)
                            popup_text = f"+1 Shot! ({1 + state['extra_shots']})"
                        elif ptype == "bomb":
                            for a in state["asteroids"][:]:
                                if len(state["particles"]) < MAX_PARTICLES:
                                    state["particles"].extend(create_explosion(a["x"], a["y"], count=12))
                                pts_mult = GOLDEN_ASTEROID_MULTIPLIER if a.get("golden") else 1
                                state["score"] += POINTS_PER_HIT * pts_mult
                                state["asteroid_speed"] += ASTEROID_SPEED_INCREASE_PER_HIT
                            state["asteroids"] = []
                            state["shake"] = max(state.get("shake", 0), 8)
                            popup_text = "Bomb!"
                        if popup_text:
                            state["score_popups"].append({
                                "x": pu["x"], "y": pu["y"],
                                "text": popup_text,
                                "life": 40,
                            })
                        break

            for b in state["bullets"][:]:
                for a in state["asteroids"][:]:
                    ar = a.get("r", state["asteroid_radius"])
                    dist = math.sqrt((b["x"] - a["x"]) ** 2 + (b["y"] - a["y"]) ** 2)
                    if dist < ar + 5:
                        if b in state["bullets"]:
                            state["bullets"].remove(b)
                        if a in state["asteroids"]:
                            state["asteroids"].remove(a)
                        pts_mult = GOLDEN_ASTEROID_MULTIPLIER if a.get("golden") else 1
                        pts = POINTS_PER_HIT * pts_mult
                        state["score"] += pts
                        state["asteroid_speed"] += ASTEROID_SPEED_INCREASE_PER_HIT
                        state["shake"] = max(state.get("shake", 0), 4)
                        if len(state["particles"]) < MAX_PARTICLES:
                            state["particles"].extend(create_explosion(a["x"], a["y"]))
                        state["score_popups"].append({
                            "x": a["x"], "y": a["y"],
                            "text": f"+{pts}",
                            "life": 40,
                        })
                        break

            for p in state["particles"][:]:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.1
                p["life"] -= 1
                if p["life"] <= 0:
                    state["particles"].remove(p)

            for sp in state["score_popups"][:]:
                sp["y"] -= 1.2
                sp["life"] -= 1
                if sp["life"] <= 0:
                    state["score_popups"].remove(sp)

            if state.get("muzzle_flash", 0) > 0:
                state["muzzle_flash"] -= 1

            if state.get("slow_flash", 0) > 0:
                state["slow_flash"] -= 1

            if state.get("shield_remaining_frames", 0) > 0:
                state["shield_remaining_frames"] -= 1

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
                pygame.draw.lines(screen, (30, 38, 50), False, bg["mountain_ridge"], 2)

        # --- Menu ---
        if state.get("menu"):
            state["menu_asteroid_angle"] = state.get("menu_asteroid_angle", 0) + MENU_ASTEROID_ROTATE_SPEED
            diff = state.get("difficulty", 2)
            diff_info = DIFFICULTIES[diff]

            title = font_large.render("Asteroid Defence", True, WHITE)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, S(50)))

            # Difficulty selection
            y_diff = S(125)
            diff_btn_h = S(34)
            for d_num, d_info in DIFFICULTIES.items():
                is_sel = d_num == diff
                color = GREEN if is_sel else GRAY
                txt = font_small.render(d_info['name'], True, color)
                diff_btn_w = txt.get_width() + S(24)
                diff_btn_x = WIDTH // 2 + (d_num - 2) * S(160) - diff_btn_w // 2
                if is_sel:
                    pygame.draw.rect(screen, (15, 40, 15), (diff_btn_x, y_diff, diff_btn_w, diff_btn_h), 0, border_radius=int(S(4)))
                pygame.draw.rect(screen, color, (diff_btn_x, y_diff, diff_btn_w, diff_btn_h), 2, border_radius=int(S(4)))
                screen.blit(txt, (diff_btn_x + (diff_btn_w - txt.get_width()) // 2, y_diff + (diff_btn_h - txt.get_height()) // 2))

            # Controls
            ctrl1 = font_tiny.render("Arrows / Drag = Rotate  |  SPACE / Tap = Shoot", True, GRAY)
            screen.blit(ctrl1, (WIDTH // 2 - ctrl1.get_width() // 2, S(175)))
            start_surf = font_small.render("Start", True, GREEN)
            start_w = max(start_surf.get_width() + S(40), S(160))
            start_h = start_surf.get_height() + S(16)
            start_x = WIDTH // 2 - start_w // 2
            start_y = S(202)
            pygame.draw.rect(screen, (15, 40, 15), (start_x, start_y, start_w, start_h), 0, border_radius=int(S(6)))
            pygame.draw.rect(screen, GREEN, (start_x, start_y, start_w, start_h), 2, border_radius=int(S(6)))
            screen.blit(start_surf, (WIDTH // 2 - start_surf.get_width() // 2, start_y + (start_h - start_surf.get_height()) // 2))

            # Spinning asteroid preview
            cached_verts = state.get("menu_asteroid_verts")
            cached_craters = state.get("menu_asteroid_craters")
            if cached_verts is None or state.get("menu_asteroid_cached_diff") != diff:
                _r = min(size_to_radius(diff_info["size"]), S(80))
                cached_verts = make_asteroid_vertices(_r)
                cached_craters = make_asteroid_craters(_r)
                state["menu_asteroid_verts"] = cached_verts
                state["menu_asteroid_craters"] = cached_craters
                state["menu_asteroid_cached_diff"] = diff
            center = (WIDTH // 2, S(370))
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

            # Highscores
            hs_key = diff_info["key"]
            hs_entries = highscores.get(hs_key, [])
            hs_title = font_small.render(f"Highscores - {diff_info['name']}", True, YELLOW)
            hs_box_w = S(320)
            hs_box_x = WIDTH // 2 - hs_box_w // 2
            hs_y0 = S(475)
            hs_line_h = S(24)
            n_entries = len(hs_entries[:MAX_HIGHSCORES]) if hs_entries else 1
            hs_box_h = S(38) + n_entries * hs_line_h + S(8)
            pygame.draw.rect(screen, (8, 10, 18), (hs_box_x - S(10), hs_y0 - S(4), hs_box_w + S(20), hs_box_h), 0)
            pygame.draw.rect(screen, (40, 50, 70), (hs_box_x - S(10), hs_y0 - S(4), hs_box_w + S(20), hs_box_h), 1)
            screen.blit(hs_title, (WIDTH // 2 - hs_title.get_width() // 2, hs_y0))
            hs_content_y = hs_y0 + S(32)
            if hs_entries:
                for i, entry in enumerate(hs_entries[:MAX_HIGHSCORES]):
                    name_str = entry.get("name", "-") or "-"
                    score_str = str(entry["score"])
                    rank_str = f"{i+1:>2}. {name_str}"
                    rank_surf = font_tiny.render(rank_str, True, WHITE)
                    score_surf = font_tiny.render(score_str, True, WHITE)
                    row_y = hs_content_y + i * hs_line_h
                    screen.blit(rank_surf, (hs_box_x, row_y))
                    screen.blit(score_surf, (hs_box_x + hs_box_w - score_surf.get_width(), row_y))
            else:
                no_hs = font_tiny.render("No scores yet", True, GRAY)
                screen.blit(no_hs, (WIDTH // 2 - no_hs.get_width() // 2, hs_content_y))

        # --- Gameplay ---
        elif not state.get("game_over"):
            cx = WIDTH // 2
            ground_y = state.get("ground_y", HEIGHT - GROUND_OFFSET)
            w = math.radians(state["angle"])
            cos_w, sin_w = math.cos(w), math.sin(w)
            pivot_y = ground_y - CANNON_BASE_HEIGHT

            for bbx, bw, bh in bg["buildings"]:
                top = ground_y - bh
                rect = pygame.Rect(bbx, top, bw, bh + GROUND_OFFSET)
                pygame.draw.rect(screen, CITY_COLOR, rect, 0)
                pygame.draw.rect(screen, CITY_OUTLINE, rect, 1)
                # Rooftop accent
                pygame.draw.line(screen, (30, 40, 55), (bbx, top), (bbx + bw, top), 2)
                if bw > S(25):
                    pygame.draw.rect(screen, (18, 22, 32), (bbx + bw // 3, top - S(4), bw // 3, S(4)), 0)
            for i, (wx, wy) in enumerate(bg["windows"]):
                if (tick + i * 7) % 150 != 0:
                    wc = CITY_WINDOW if (tick + i * 13) % 300 > 20 else (230, 220, 130)
                    pygame.draw.rect(screen, wc, (wx, wy, S(4), S(4)), 0)

            for gi in range(8):
                gy = ground_y + gi * S(2)
                gv = max(0, 40 - gi * 5)
                pygame.draw.line(screen, (gv, int(gv * 1.1), gv), (0, gy), (WIDTH, gy), 2)

            shield_frames = state.get("shield_remaining_frames", 0)
            if shield_frames > 0:
                cx_s = WIDTH // 2
                cy_s = ground_y - SHIELD_ARC_TOP_OFFSET
                total = int(SHIELD_DURATION_SEC * 60)
                frac = min(1.0, shield_frames / total)
                pulse = 0.7 + 0.3 * math.sin(tick * 0.15)
                rx = SHIELD_ARC_RADIUS
                ry = int(rx * 0.45)
                for w_line in range(3):
                    rx_i = rx - w_line * S(5)
                    ry_i = ry - w_line * S(3)
                    if rx_i < S(10) or ry_i < S(5):
                        break
                    rect_s = pygame.Rect(cx_s - rx_i, cy_s - ry_i, rx_i * 2, ry_i * 2)
                    alpha_f = frac * pulse * (1.0 - w_line * 0.25)
                    c_draw = (int(80 * alpha_f), int(220 * alpha_f), int(255 * alpha_f))
                    try:
                        pygame.draw.arc(screen, c_draw, rect_s, 0, math.pi, 3)
                    except TypeError:
                        pygame.draw.arc(screen, c_draw, rect_s, 0, math.pi)

            bl = cannon_tip_len
            if cannon_sprite is not None:
                # Soft ground shadow helps the sprite sit naturally in the scene.
                sh_w = S(110)
                sh_h = S(24)
                shadow = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow, (0, 0, 0, 95), (0, 0, sh_w, sh_h), 0)
                screen.blit(shadow, (cx - sh_w // 2, ground_y - sh_h // 2))
                rot = pygame.transform.rotate(cannon_sprite, -state["angle"])
                rrect = rot.get_rect(center=(cx, pivot_y))
                screen.blit(rot, rrect.topleft)
            else:
                top_w = CANNON_BASE_WIDTH * 0.65
                base_pts = [
                    (cx - CANNON_BASE_WIDTH // 2, ground_y),
                    (cx + CANNON_BASE_WIDTH // 2, ground_y),
                    (cx + top_w / 2, ground_y - CANNON_BASE_HEIGHT),
                    (cx - top_w / 2, ground_y - CANNON_BASE_HEIGHT),
                ]
                pygame.draw.polygon(screen, CANNON_METAL, base_pts, 0)
                for rx in (cx - S(14), cx, cx + S(14)):
                    pygame.draw.circle(screen, CANNON_DARK, (rx, int(pivot_y + CANNON_BASE_HEIGHT // 2)), S(3), 0)
                    pygame.draw.circle(screen, CANNON_HIGHLIGHT, (rx, int(pivot_y + CANNON_BASE_HEIGHT // 2)), S(3), 1)
                pygame.draw.polygon(screen, CANNON_GLOW, base_pts, 2)
                bw_base = BARREL_WIDTH // 2
                bw_tip = BARREL_WIDTH // 3
                barrel_shape = [(-bw_base, 0), (bw_base, 0), (bw_tip, -bl), (-bw_tip, -bl)]
                barrel = [(cx + bpx * cos_w - bpy * sin_w, pivot_y + bpx * sin_w + bpy * cos_w)
                           for bpx, bpy in barrel_shape]
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

            if state.get("muzzle_flash", 0) > 0:
                flash_t = state["muzzle_flash"] / 6.0
                tip_x = cx + math.sin(w) * bl
                tip_y = pivot_y - math.cos(w) * bl
                for fi, fc in enumerate(MUZZLE_COLORS):
                    fr = int((S(14) - fi * S(4)) * flash_t)
                    fb = max(0.1, flash_t * (1 - fi * 0.3))
                    mc = (int(fc[0] * fb), int(fc[1] * fb), int(fc[2] * fb))
                    pygame.draw.circle(screen, mc, (int(tip_x), int(tip_y)), max(1, fr), 0)

            for b in state["bullets"]:
                trail = b.get("trail", [(b["x"], b["y"])])
                for i, (tx, ty) in enumerate(trail[:-1]):
                    alpha = (i + 1) / max(len(trail), 1)
                    tc = (int(BULLET_GLOW[0] * alpha), int(BULLET_GLOW[1] * alpha),
                          int(BULLET_GLOW[2] * alpha))
                    pygame.draw.line(screen, tc, (int(tx), int(ty)),
                                      (int(trail[i + 1][0]), int(trail[i + 1][1])), 2)
                vx, vy = b.get("vx", 0), b.get("vy", 0)
                age = b.get("age", 0)
                if age < 6 and (vx != 0 or vy != 0):
                    speed = math.sqrt(vx * vx + vy * vy) or 1
                    nx, ny = -vx / speed, -vy / speed
                    for tail_i in range(3):
                        dist = (3 - tail_i) * S(6)
                        bx = b["x"] + nx * dist
                        by = b["y"] + ny * dist
                        fade = (4 - tail_i) / 5.0 * (1.0 - age / 6.0)
                        tc = (int(BULLET_GLOW[0] * fade), int(BULLET_GLOW[1] * fade),
                             int(BULLET_GLOW[2] * fade))
                        r = max(1, S(4) - tail_i - age // 2)
                        pygame.draw.circle(screen, tc, (int(bx), int(by)), r, 0)
                pygame.draw.circle(screen, BULLET_GLOW, (int(b["x"]), int(b["y"])), S(10), 0)
                pygame.draw.circle(screen, (150, 200, 255), (int(b["x"]), int(b["y"])), S(5), 0)
                pygame.draw.circle(screen, WHITE, (int(b["x"]), int(b["y"])), S(2), 0)

            if state.get("laser_remaining_frames", 0) > 0:
                rad = math.radians(state["angle"])
                tip_x = cx + math.sin(rad) * cannon_tip_len
                tip_y = pivot_y - math.cos(rad) * cannon_tip_len
                dy = -math.cos(rad)
                if abs(dy) < 0.01:
                    end_x, end_y = tip_x + (1 if math.sin(rad) >= 0 else -1) * WIDTH, tip_y
                else:
                    t = (0 - tip_y) / dy
                    t = max(0, min(t, HEIGHT * 2))
                    end_x = tip_x + math.sin(rad) * t
                    end_y = tip_y + dy * t
                pulse = 0.7 + 0.3 * math.sin(tick * 0.4)
                ix, iy, ex, ey = int(tip_x), int(tip_y), int(end_x), int(end_y)
                glow_outer = (int(80 * pulse), int(20 * pulse), int(60 * pulse))
                pygame.draw.line(screen, glow_outer, (ix, iy), (ex, ey), S(20))
                glow_mid = (int(180 * pulse), int(50 * pulse), int(140 * pulse))
                pygame.draw.line(screen, glow_mid, (ix, iy), (ex, ey), S(12))
                core = (int(255 * pulse), int(100 * pulse), int(220 * pulse))
                pygame.draw.line(screen, core, (ix, iy), (ex, ey), S(6))
                pygame.draw.line(screen, (255, 220, 255), (ix, iy), (ex, ey), S(2))

            if state.get("slow_flash", 0) > 0:
                sf = state["slow_flash"] / 30.0
                slow_col = (int(100 * sf), int(80 * sf), int(200 * sf))
                for edge_w in range(4):
                    pygame.draw.rect(screen, slow_col, (edge_w, edge_w, WIDTH - edge_w * 2, HEIGHT - edge_w * 2), 1)

            pu_scale = pu_size_mult
            for pu in state.get("power_ups", []):
                pc = POWERUP_COLORS.get(pu["type"], YELLOW)
                label = POWERUP_LABELS.get(pu["type"], "?")
                draw_power_up(screen, int(pu["x"]), int(pu["y"]), pc, label, font_tiny, scale=pu_scale, tick=tick, pu_type=pu["type"])

            rad = state["asteroid_radius"]
            for a in state["asteroids"]:
                ang = math.radians(a.get("angle", 0))
                cos_a, sin_a = math.cos(ang), math.sin(ang)
                pts = [(a["x"] + dx * cos_a - dy * sin_a, a["y"] + dx * sin_a + dy * cos_a)
                        for dx, dy in a["verts"]]
                if a.get("golden"):
                    pygame.draw.polygon(screen, GOLDEN_FILL, pts, 0)
                    for dx, dy, cr in a.get("craters", []):
                        rdx = dx * cos_a - dy * sin_a
                        rdy = dx * sin_a + dy * cos_a
                        pygame.draw.circle(screen, GOLDEN_CRATER,
                                            (int(a["x"] + rdx), int(a["y"] + rdy)), int(cr), 0)
                    pygame.draw.polygon(screen, GOLDEN_EDGE, pts, 2)
                else:
                    pygame.draw.polygon(screen, ASTEROID_FILL, pts, 0)
                    for dx, dy, cr in a.get("craters", []):
                        rdx = dx * cos_a - dy * sin_a
                        rdy = dx * sin_a + dy * cos_a
                        pygame.draw.circle(screen, ASTEROID_CRATER,
                                            (int(a["x"] + rdx), int(a["y"] + rdy)), int(cr), 0)
                    pygame.draw.polygon(screen, ASTEROID_EDGE, pts, 2)

            for p in state.get("particles", []):
                alpha = p["life"] / p["max_life"]
                sz = max(1, int(p["size"] * alpha))
                pc = (int(p["color"][0] * alpha), int(p["color"][1] * alpha),
                      int(p["color"][2] * alpha))
                pygame.draw.circle(screen, pc, (int(p["x"]), int(p["y"])), sz, 0)

            level = state["score"] // POINTS_PER_LEVEL
            score_surf = font.render(f"Score: {state['score']}", True, WHITE)
            bg_rect = pygame.Rect(S(14), S(14), score_surf.get_width() + S(16), score_surf.get_height() + S(8))
            pygame.draw.rect(screen, (10, 12, 20), bg_rect, 0)
            pygame.draw.rect(screen, (40, 50, 70), bg_rect, 1)
            screen.blit(score_surf, (S(22), S(18)))
            lvl_surf = font.render(f"Level {level}", True, YELLOW)
            lvl_x = WIDTH // 2 - lvl_surf.get_width() // 2
            lvl_bg = pygame.Rect(lvl_x - S(8), S(14), lvl_surf.get_width() + S(16), lvl_surf.get_height() + S(8))
            pygame.draw.rect(screen, (10, 12, 20), lvl_bg, 0)
            pygame.draw.rect(screen, (40, 50, 70), lvl_bg, 1)
            screen.blit(lvl_surf, (lvl_x, S(18)))
            lives = state.get("lives", 0)
            for hi in range(lives):
                hx = WIDTH - S(22) - hi * S(22)
                draw_heart(screen, hx, S(28), S(14), (220, 40, 60))
                draw_heart(screen, hx - 1, S(27), S(10), (255, 80, 100))
            y_extra = S(52)
            if state.get("triple_shot_remaining", 0) > 0:
                ts_surf = font_tiny.render(f"3x Shot: {state['triple_shot_remaining']}", True, (100, 200, 255))
                screen.blit(ts_surf, (S(22), y_extra))
                y_extra += S(20)
            if state.get("extra_shots", 0) > 0:
                es_surf = font_tiny.render(f"Shots: {1 + state['extra_shots']}", True, (255, 220, 50))
                screen.blit(es_surf, (S(22), y_extra))

            for sp in state.get("score_popups", []):
                sp_alpha = max(0.0, sp["life"] / 40.0)
                pc = (int(255 * sp_alpha), int(220 * sp_alpha), int(80 * sp_alpha))
                popup = font_small.render(sp["text"], True, pc)
                screen.blit(popup, (int(sp["x"]) - popup.get_width() // 2, int(sp["y"])))

            if state.get("paused"):
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                screen.blit(overlay, (0, 0))
                pause_text = font_large.render("PAUSED", True, WHITE)
                screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - S(60)))
                p_btn_w = S(180)
                p_btn_h = S(40)
                p_btn_x = WIDTH // 2 - p_btn_w // 2
                p_resume_y = HEIGHT // 2 + S(10)
                p_menu_y = HEIGHT // 2 + S(60)
                resume_surf = font_small.render("Resume", True, GREEN)
                pygame.draw.rect(screen, (15, 40, 15), (p_btn_x, p_resume_y, p_btn_w, p_btn_h), 0, border_radius=int(S(6)))
                pygame.draw.rect(screen, GREEN, (p_btn_x, p_resume_y, p_btn_w, p_btn_h), 2, border_radius=int(S(6)))
                screen.blit(resume_surf, (WIDTH // 2 - resume_surf.get_width() // 2, p_resume_y + (p_btn_h - resume_surf.get_height()) // 2))
                menu_surf = font_small.render("Menu", True, GRAY)
                pygame.draw.rect(screen, (30, 20, 20), (p_btn_x, p_menu_y, p_btn_w, p_btn_h), 0, border_radius=int(S(6)))
                pygame.draw.rect(screen, GRAY, (p_btn_x, p_menu_y, p_btn_w, p_btn_h), 2, border_radius=int(S(6)))
                screen.blit(menu_surf, (WIDTH // 2 - menu_surf.get_width() // 2, p_menu_y + (p_btn_h - menu_surf.get_height()) // 2))

        # --- Game Over / Name Entry ---
        else:
            if state.get("entering_name"):
                text_over = font_large.render("New Highscore!", True, YELLOW)
                text_score = font.render(f"Score: {state.get('final_score', state.get('score', 0))}", True, WHITE)
                prompt = font_small.render("Enter your name:", True, WHITE)
                name_str = state.get("player_name", "")
                cursor_char = "_" if (tick // 30) % 2 == 0 else " "
                name_display = font.render(name_str + cursor_char, True, GREEN)
                screen.blit(text_over, (WIDTH // 2 - text_over.get_width() // 2, HEIGHT // 2 - S(120)))
                screen.blit(text_score, (WIDTH // 2 - text_score.get_width() // 2, HEIGHT // 2 - S(50)))
                screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + S(10)))
                screen.blit(name_display, (WIDTH // 2 - name_display.get_width() // 2, HEIGHT // 2 + S(50)))
                ne_btn_y = HEIGHT // 2 + S(100)
                ne_btn_h = S(40)
                ne_btn_w = S(120)
                ne_gap = S(20)
                ne_confirm_x = WIDTH // 2 - ne_btn_w - ne_gap // 2
                ne_skip_x = WIDTH // 2 + ne_gap // 2
                confirm_surf = font_small.render("Confirm", True, GREEN)
                pygame.draw.rect(screen, (15, 40, 15), (ne_confirm_x, ne_btn_y, ne_btn_w, ne_btn_h), 0, border_radius=int(S(6)))
                pygame.draw.rect(screen, GREEN, (ne_confirm_x, ne_btn_y, ne_btn_w, ne_btn_h), 2, border_radius=int(S(6)))
                screen.blit(confirm_surf, (ne_confirm_x + (ne_btn_w - confirm_surf.get_width()) // 2, ne_btn_y + (ne_btn_h - confirm_surf.get_height()) // 2))
                skip_surf = font_small.render("Skip", True, GRAY)
                pygame.draw.rect(screen, (30, 20, 20), (ne_skip_x, ne_btn_y, ne_btn_w, ne_btn_h), 0, border_radius=int(S(6)))
                pygame.draw.rect(screen, GRAY, (ne_skip_x, ne_btn_y, ne_btn_w, ne_btn_h), 2, border_radius=int(S(6)))
                screen.blit(skip_surf, (ne_skip_x + (ne_btn_w - skip_surf.get_width()) // 2, ne_btn_y + (ne_btn_h - skip_surf.get_height()) // 2))
            else:
                text_over = font_large.render("Game Over!", True, RED)
                text_score = font.render(f"Score: {state['score']}", True, WHITE)
                screen.blit(text_over, (WIDTH // 2 - text_over.get_width() // 2, HEIGHT // 2 - S(80)))
                screen.blit(text_score, (WIDTH // 2 - text_score.get_width() // 2, HEIGHT // 2 - S(20)))
                go_btn_w = S(220)
                go_btn_h = S(40)
                go_btn_x = WIDTH // 2 - go_btn_w // 2
                go_btn_y = HEIGHT // 2 + S(35)
                continue_surf = font_small.render("Continue", True, WHITE)
                pygame.draw.rect(screen, (25, 25, 35), (go_btn_x, go_btn_y, go_btn_w, go_btn_h), 0, border_radius=int(S(6)))
                pygame.draw.rect(screen, WHITE, (go_btn_x, go_btn_y, go_btn_w, go_btn_h), 2, border_radius=int(S(6)))
                screen.blit(continue_surf, (WIDTH // 2 - continue_surf.get_width() // 2, go_btn_y + (go_btn_h - continue_surf.get_height()) // 2))

        if state.get("test_mode"):
            test_surf = font_small.render("TESTMODUS", True, (255, 90, 130))
            test_w = test_surf.get_width() + S(24)
            test_h = test_surf.get_height() + S(10)
            test_x = WIDTH // 2 - test_w // 2
            test_y = S(8)
            pygame.draw.rect(screen, (35, 8, 18), (test_x, test_y, test_w, test_h), 0, border_radius=int(S(6)))
            pygame.draw.rect(screen, (255, 90, 130), (test_x, test_y, test_w, test_h), 2, border_radius=int(S(6)))
            screen.blit(test_surf, (WIDTH // 2 - test_surf.get_width() // 2, test_y + (test_h - test_surf.get_height()) // 2))

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

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
