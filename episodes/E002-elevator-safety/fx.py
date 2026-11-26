"""E002 explainer effects: tracked labels (from labels/fNNNNN.json written by scene.py), number callouts, calm music."""
import os, json, math
from PIL import ImageDraw
from timing import *

HEADER = ("WHY ELEVATORS", "ALMOST NEVER FALL")
HOT = {"falls", "rails", "ropes", "one", "motor", "counterweight", "forty", "brake", "governor", "fast", "grabs", "wedges",
       "buffers", "otis", "cut", "fall", "snapped"}

# (anchor, text, start, end)
LABELS = [
    ("rails", "GUIDE RAILS", W(2, "guide"), S(3) - 0.1),
    ("car", "CAR", W(3, "car"), S(4) - 0.1),
    ("ropes", "STEEL ROPES", W(4, "steel"), W(4, "one") - 0.05),
    ("onerope", "ONE ROPE CAN HOLD IT", W(4, "one"), S(5) - 0.1),
    ("sheave", "MOTOR + GROOVED WHEEL", W(5, "motor"), S(6) - 0.1),
    ("cw", "COUNTERWEIGHT", W(6, "counterweight"), S(7) - 0.1),
    ("brake", "SPRING BRAKE", W(7, "springs"), S(8) - 0.1),
    ("govrope", "GOVERNOR ROPE", W(8, "own"), S(9) - 0.1),
    ("governor", "GOVERNOR", S(9), S(10) - 0.1),
    ("wedges", "SAFETY WEDGES", W(10, "wedges"), S(11) - 0.1),
    ("buffer", "BUFFERS", W(11, "buffers"), S(12) - 0.1),
]
LBL_DIR = os.path.join(EP, "labels")

def punches():
    return [(W(7, "clamp"), 0.04), (W(9, "grabs"), 0.05), (W(10, "tight"), 0.06), (W(12, "cut"), 0.05)]

def _label(img, ui, x, y, txt, k):
    d = ImageDraw.Draw(img)
    f = ui.font(40, "ExtraBold")
    w = f.getlength(txt)
    bx = min(max(40, x - w / 2 - 22), ui.W - w - 84)
    by = max(470, min(y - 190, 1000))
    d.line([(x, y), (bx + w / 2 + 22, by + 64)], fill=(255, 255, 255), width=5)
    r = 11 + 4 * (1 - k)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 210, 40), outline=(20, 20, 20), width=3)
    d.rounded_rectangle([bx, by, bx + w + 44, by + 64], radius=18, fill=(255, 255, 255), outline=(20, 20, 20), width=3)
    d.text((bx + 22, by + 8), txt, font=f, fill=(20, 22, 28))

def overlays(img, t, ui):
    fi = int(round(t * 24))
    p = os.path.join(LBL_DIR, f"f{fi:05d}.json")
    anch = json.load(open(p)) if os.path.exists(p) else {}
    for name, txt, a, b in LABELS:
        if a <= t < b and name in anch:
            x, y, z = anch[name]
            if z > 0 and 0.03 < x < 0.97 and 0.05 < y < 0.95:
                _label(img, ui, x * ui.W, y * ui.H, txt, min(1, (t - a) / 0.2))
    def pop(a):
        return 0.85 + 0.15 * min(1, (t - a) / 0.15)
    a = W(4, "several")
    if a <= t < W(4, "one") - 0.05:
        ui.center_text(img, "OFTEN 4 TO 8 ROPES", 300, 76, (255, 222, 33), pop(a))
    a = W(6, "forty")
    if a <= t < S(7) - 0.1:
        ui.center_text(img, "≈ CAR + 40% LOAD", 300, 80, (255, 222, 33), pop(a))
    a = W(7, "power")
    if a <= t < W(7, "springs"):
        ui.center_text(img, "POWER OFF", 300, 86, (255, 80, 60), pop(a))
    a = W(9, "fast")
    if a <= t < T_GRAB_END():
        ui.center_text(img, "TOO FAST!", 300, 96, (255, 80, 60), pop(a))
    a = W(12, "eighteen")
    if a <= t < S(13) - 0.1:
        ui.center_text(img, "1854", 300, 150, (255, 222, 33), pop(a))

def T_GRAB_END():
    return S(10) - 0.1

def moods():
    return [(0.0, "mystery"), (S(12), "happy")]

def sfx(cue):
    cue("rumble", W(2, "first"), 0.5)
    cue("thud", W(3, "rails") + 0.2, 0.6)
    for i in range(6): cue("blip", W(4, "several") + i * 0.12, 0.5)
    cue("pop", W(4, "one"))
    cue("pop", W(5, "motor"), 0.7)
    cue("thud", W(6, "balances"), 0.5)
    cue("tapestop", W(7, "power") + 0.2, 0.7)
    cue("bonk", W(7, "clamp") + 0.1, 0.7)
    cue("pop", W(8, "governor"), 0.6)
    cue("whoosh", W(9, "fast"), 1.0)
    cue("bonk", W(9, "grabs"), 0.6)
    cue("sizzle", W(10, "tight") - 0.2, 0.7)
    cue("thud", W(10, "tight"), 0.8)
    cue("pop", W(11, "buffers"), 0.6)
    cue("glitch", W(12, "cut"), 0.6)
    cue("coin", W(13, "didn't"), 0.8)
