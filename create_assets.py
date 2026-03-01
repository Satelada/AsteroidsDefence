"""
Creates default assets for Asteroid Defence and saves them into the assets/ folder:
- cannon.png   (space cannon, barrel pointing up)
- spaceship.png (ship hull to place under cannon)
- space_music.wav (varied C64-style music loop)
Run once: python create_assets.py
"""
import os
import sys
import math
import wave
import struct

# Try pygame for images
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
UFO_WIDTH = 600
UFO_HEIGHT = 85


def create_assets_dir():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    print("Assets folder:", ASSETS_DIR)


def create_cannon_png():
    if not HAS_PYGAME:
        print("  cannon.png: skip (pygame not installed)")
        return
    # Pivot = top of base (where barrel meets base). Image height so pivot is at vertical center for correct rotation.
    barrel_h, base_h = 88, 22
    pivot_y = barrel_h  # top of base in drawn cannon
    img_h = pivot_y * 2  # so pivot is at img_h/2
    w, h = 80, img_h
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    cx = w // 2
    # Base (dark metal) – drawn so its top is at pivot_y
    base_rect = pygame.Rect(cx - 28, pivot_y, 56, base_h)
    pygame.draw.rect(s, (55, 60, 72), base_rect, 0)
    pygame.draw.rect(s, (75, 85, 100), base_rect, 2)
    # Barrel (pointing up from pivot_y)
    barrel = [(cx - 12, pivot_y), (cx + 12, pivot_y), (cx + 10, pivot_y - barrel_h + 10), (cx - 10, pivot_y - barrel_h + 10)]
    pygame.draw.polygon(s, (60, 65, 78), barrel, 0)
    pygame.draw.polygon(s, (90, 100, 120), barrel, 2)
    for y_ in (pivot_y - 25, pivot_y - 50):
        pygame.draw.line(s, (45, 50, 58), (cx - 11, y_), (cx + 11, y_), 2)
    path = os.path.join(ASSETS_DIR, "cannon.png")
    pygame.image.save(s, path)
    print("  cannon.png: created (transparent, pivot at base)")


def create_spaceship_png():
    """UFO (flying saucer) spanning full game width."""
    if not HAS_PYGAME:
        print("  spaceship.png: skip (pygame not installed)")
        return
    w, h = UFO_WIDTH, UFO_HEIGHT
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    cx = w // 2
    # Main saucer: two overlapping ellipses (top dome + bottom)
    pygame.draw.ellipse(s, (50, 55, 70), (0, 0, w, h), 0)
    pygame.draw.ellipse(s, (70, 78, 95), (0, 0, w, h), 2)
    # Upper dome (cockpit band)
    pygame.draw.ellipse(s, (45, 52, 68), (w // 6, 8, 2 * w // 3, 50), 0)
    pygame.draw.ellipse(s, (65, 75, 92), (w // 6, 8, 2 * w // 3, 50), 2)
    pygame.draw.ellipse(s, (80, 95, 120), (w // 4, 22, w // 2, 22), 0)  # inner glow
    # Lights along the edge (full width)
    for lx in range(40, w - 40, 55):
        pygame.draw.circle(s, (100, 120, 180), (lx, 18), 4, 0)
        pygame.draw.circle(s, (70, 85, 110), (lx, h - 20), 5, 0)
    path = os.path.join(ASSETS_DIR, "spaceship.png")
    pygame.image.save(s, path)
    print("  spaceship.png: created (UFO, full width)")


def _square(phase):
    return 1.0 if (phase % 1.0) < 0.5 else -1.0


def _triangle(phase):
    p = phase % 1.0
    return 4.0 * p - 1.0 if p < 0.5 else 3.0 - 4.0 * p


def _noise(seed_val):
    """Deterministic pseudo-noise for drum sounds."""
    x = (seed_val * 1103515245 + 12345) & 0x7FFFFFFF
    return (x / 0x7FFFFFFF) * 2.0 - 1.0


def create_space_music_wav():
    """Rich C64-style track: 32 bars, 6 sections, bass + arp + melody + drums."""
    path = os.path.join(ASSETS_DIR, "space_music.wav")
    sample_rate = 44100
    bpm = 108
    beat_sec = 60.0 / bpm
    bars = 32
    beats_total = bars * 4
    duration_sec = beats_total * beat_sec
    n_frames = int(sample_rate * duration_sec)

    # Note frequencies (C2-C6 range)
    def note_freq(midi):
        return 440.0 * (2.0 ** ((midi - 69) / 12.0))

    # Section definitions (bar ranges -> chord + melody data)
    # Sections: Intro(0-3), A(4-11), B(12-19), C(20-23), A'(24-27), Outro(28-31)
    sections = {
        "intro":  {"bars": range(0, 4),   "bass": [33, 33, 36, 33],  "arp": [57, 60, 64, 67], "melody": [76, 79, 81, 84, 81, 79, 76, 72], "vol": 0.5},
        "a":      {"bars": range(4, 12),  "bass": [33, 40, 36, 38],  "arp": [57, 60, 64, 67], "melody": [69, 72, 76, 79, 81, 79, 76, 72], "vol": 1.0},
        "b":      {"bars": range(12, 20), "bass": [31, 36, 33, 38],  "arp": [55, 59, 62, 67], "melody": [67, 71, 74, 79, 74, 71, 67, 62], "vol": 1.0},
        "c":      {"bars": range(20, 24), "bass": [36, 38, 40, 43],  "arp": [60, 64, 67, 72], "melody": [72, 76, 79, 84, 88, 84, 79, 76], "vol": 0.9},
        "a_rep":  {"bars": range(24, 28), "bass": [33, 40, 36, 38],  "arp": [57, 60, 64, 67], "melody": [69, 72, 76, 79, 81, 79, 76, 72], "vol": 1.0},
        "outro":  {"bars": range(28, 32), "bass": [33, 33, 36, 33],  "arp": [57, 60, 64, 67], "melody": [76, 72, 69, 64, 60, 57, 52, 48], "vol": 0.4},
    }

    def get_section(bar):
        for sec in sections.values():
            if bar in sec["bars"]:
                return sec
        return sections["intro"]

    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        out = []
        for i in range(n_frames):
            t = i / sample_rate
            beat = t / beat_sec
            bar = int(beat // 4) % bars
            beat_in_bar = beat % 4
            sec = get_section(bar)
            vol = sec["vol"]

            # Bass: square wave, one note per beat
            bi = int(beat_in_bar) % len(sec["bass"])
            bass_freq = note_freq(sec["bass"][bi])
            bass = 0.18 * vol * _square(t * bass_freq)

            # Arpeggio: triangle wave, 8th notes cycling through chord
            ai = int(beat * 2) % len(sec["arp"])
            arp_freq = note_freq(sec["arp"][ai])
            env_arp = 1.0 - 0.5 * ((beat * 2) % 1.0)
            arp = 0.12 * vol * env_arp * _triangle(t * arp_freq)

            # Melody: triangle wave, 8th notes with decay envelope
            mi = int(beat * 2) % len(sec["melody"])
            mel_freq = note_freq(sec["melody"][mi])
            env_mel = max(0, 1.0 - 0.7 * ((beat * 2) % 1.0))
            melody = 0.10 * vol * env_mel * _triangle(t * mel_freq)

            # Drums: kick on beats 0,2; snare on 1,3; hi-hat on 8ths
            drum = 0.0
            beat_frac = beat_in_bar % 1.0
            if bar >= 4 and bar < 28:
                # Kick (low sine burst)
                if int(beat_in_bar) % 2 == 0 and beat_frac < 0.15:
                    kick_env = 1.0 - beat_frac / 0.15
                    drum += 0.20 * vol * kick_env * math.sin(2 * math.pi * 60 * (1.0 - beat_frac * 3) * t)
                # Snare (noise burst)
                if int(beat_in_bar) % 2 == 1 and beat_frac < 0.08:
                    snare_env = 1.0 - beat_frac / 0.08
                    drum += 0.10 * vol * snare_env * _noise(i)
                # Hi-hat (short noise on every 8th)
                hh_frac = (beat * 2) % 1.0
                if hh_frac < 0.03:
                    hh_env = 1.0 - hh_frac / 0.03
                    drum += 0.05 * vol * hh_env * _noise(i * 3)

            v = bass + arp + melody + drum
            v = max(-1.0, min(1.0, v))
            out.append(struct.pack("<h", int(v * 18000)))
        wav.writeframes(b"".join(out))
    print("  space_music.wav: created (32-bar varied track)")


def create_shoot_sound_wav():
    """Short laser/shoot sound."""
    path = os.path.join(ASSETS_DIR, "shoot.wav")
    sample_rate = 22050
    duration_sec = 0.12
    n_frames = int(sample_rate * duration_sec)
    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        out = []
        for i in range(n_frames):
            t = i / sample_rate
            # Short descending "pew" (sine with envelope)
            env = 1.0 - (t / duration_sec) ** 0.5
            freq = 800 - 400 * (t / duration_sec)
            v = 0.35 * env * math.sin(2 * math.pi * freq * t)
            v = max(-1, min(1, v))
            out.append(struct.pack("<h", int(v * 20000)))
        wav.writeframes(b"".join(out))
    print("  shoot.wav: created")


def main():
    print("Creating assets...")
    create_assets_dir()
    # cannon.png and spaceship.png: use the generated graphics in assets/ (not overwritten here)
    if HAS_PYGAME:
        pass  # create_cannon_png() / create_spaceship_png() available but not run by default
    create_space_music_wav()
    create_shoot_sound_wav()
    print("Done.")


if __name__ == "__main__":
    main()
