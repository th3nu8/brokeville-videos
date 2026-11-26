"""E001 explainer effects: tracked labels (from labels/fNNNNN.json written by scene.py), halving graphic, calm music."""
import os, json, math
from PIL import ImageDraw
from timing import *

HEADER = ("HOW A NUCLEAR BUNKER", "IS BUILT")
HOT = {"nuclear", "radiation", "half", "thousandth", "rebar", "concrete", "fifty", "blast", "door", "hatch", "hepa", "carbon",
       "pressure", "pushed", "earth", "fallout", "month"}

# (anchor, text, start, end)
LABELS = [
    ("pit", "DIRT = RADIATION SHIELD", W(2, "every"), S(4) - 0.2),
    ("wall", "~50 cm REINFORCED CONCRETE", W(5, "walls") - 0.1, S(6) - 0.1),
    ("door", "BLAST DOOR", W(6, "blast"), S(7) - 0.1),
    ("hatch", "ESCAPE HATCH", W(7, "emergency") - 0.1, S(8) - 0.1),
    ("pre", "1  PRE-FILTER", W(8, "pre") - 0.1, S(9) - 0.1),
    ("hepa", "2  HEPA FILTER", W(8, "hepa") - 0.1, S(9) - 0.1),
    ("carbon", "3  ACTIVATED CARBON", W(8, "activated") - 0.1, S(9) - 0.1),
    ("room", "HIGHER PRESSURE INSIDE", W(9, "higher") - 0.1, S(10) - 0.1),
    ("bunks", "BUNKS", W(10, "bunks") - 0.05, S(11) - 0.1),
    ("water", "WATER", W(10, "water") - 0.05, S(11) - 0.1),
    ("food", "FOOD", W(10, "food") - 0.05, S(11) - 0.1),
    ("power", "POWER", W(10, "power") - 0.05, S(11) - 0.1),
    ("radio", "RADIO", W(10, "radio") - 0.05, S(11) - 0.1),
    ("earth", "TONS OF EARTH", W(11, "buried"), S(12) - 0.1),
]
LBL_DIR = os.path.join(EP, "labels")

def punches():
    return [(W(6, "blast"), 0.05), (W(7, "emergency"), 0.04), (W(11, "buried"), 0.05)]

def _label(img, ui, x, y, txt, k):
    d = ImageDraw.Draw(img)
    f = ui.font(40, "ExtraBold")
    w = f.getlength(txt)
    # place the pill above-left or above-right of the anchor, keep on screen and above captions
    bx = min(max(40, x - w / 2 - 22), ui.W - w - 84)
    by = max(470, min(y - 190, 1000))
    a = int(255 * k)
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
    # halving graphic
    th = W(3, "stack")
    if W(2, "half") - 0.1 <= t < th:
        ui.center_text(img, "RADIATION  ÷ 2", 300, 92, (255, 222, 33), 0.85 + 0.15 * min(1, (t - W(2, "half")) / 0.15))
    if th <= t < S(4) - 0.1:
        n = min(10, 1 + int((t - th) / 0.22))
        ui.center_text(img, "÷2 " * min(n, 5) + ("…" if n > 5 else ""), 260, 70, (255, 255, 255))
        if n >= 10:
            ui.center_text(img, "≈ 1/1000 GETS THROUGH", 360, 76, (255, 222, 33))

def moods():
    return [(0.0, "mystery"), (S(12), "eerie")]

def sfx(cue):
    cue("rumble", W(2, "dig"), 0.8); cue("rumble", W(2, "dig") + 2.0, 0.6)
    for k in range(6): cue("thud", S(4) + 0.3 + k * 0.3, 0.35)
    cue("sizzle", W(5, "concrete"), 0.6)
    cue("bonk", W(6, "shock") + 0.1, 0.6)
    cue("pop", W(7, "emergency"))
    for w in ("pre", "hepa", "activated"): cue("blip", W(8, w))
    for w in ("bunks", "water", "food", "power", "radio"): cue("pop", W(10, w), 0.6)
    cue("rumble", W(11, "buried"), 0.9)
