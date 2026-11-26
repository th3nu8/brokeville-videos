"""E002 effects: tracked labels, title, calm music."""
import os, json
from PIL import ImageDraw
from timing import *

HEADER = ("HOW A NUCLEAR PLANT WORKS", "BUILT FROM BLOCKS")
HOT = {"uranium", "pellet", "coal", "core", "neutrons", "heat", "control", "pressure", "boil", "steam", "turbine",
       "generator", "electricity", "vapor", "smoke"}
LABELS = [
    ("pellet", "URANIUM PELLET", W(2, "uranium"), S(4) - 0.1),
    ("coal", "≈ 1 TON OF COAL", W(3, "coal"), S(4) - 0.1),
    ("core", "REACTOR CORE", W(4, "core"), S(5) - 0.1),
    ("neutron", "NEUTRON", S(5), W(5, "split") + 0.2),
    ("rods", "CONTROL RODS", W(6, "control"), S(7) - 0.1),
    ("loop", "PRESSURIZED WATER", W(7, "water"), S(8) - 0.1),
    ("sg", "STEAM GENERATOR", W(8, "second"), S(9) - 0.1),
    ("turbine", "TURBINE", W(9, "turbine"), W(9, "generator")),
    ("generator", "GENERATOR", W(9, "generator"), S(10) - 0.1),
    ("houses", "ELECTRICITY", W(9, "electricity"), S(10) - 0.1),
    ("condenser", "CONDENSER", W(10, "cooled") - 0.1, S(11) - 0.1),
    ("vapor", "WATER VAPOR", W(11, "vapor") - 0.1, S(12) - 0.1),
]
LBL_DIR = os.path.join(EP, "labels")

def punches():
    return [(W(3, "coal"), 0.06), (W(5, "splits"), 0.05), (W(9, "electricity"), 0.05), (W(11, "smoke"), 0.05)]

def _label(img, ui, x, y, txt, k):
    d = ImageDraw.Draw(img); f = ui.font(40, "ExtraBold"); w = f.getlength(txt)
    bx = min(max(40, x - w / 2 - 22), ui.W - w - 84); by = max(470, min(y - 190, 1000))
    d.line([(x, y), (bx + w / 2 + 22, by + 64)], fill=(255, 255, 255), width=5)
    r = 11 + 4 * (1 - k)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 210, 40), outline=(20, 20, 20), width=3)
    d.rounded_rectangle([bx, by, bx + w + 44, by + 64], radius=18, fill=(255, 255, 255), outline=(20, 20, 20), width=3)
    d.text((bx + 22, by + 8), txt, font=f, fill=(20, 22, 28))

def overlays(img, t, ui):
    p = os.path.join(LBL_DIR, f"f{int(round(t * 24)):05d}.json")
    anch = json.load(open(p)) if os.path.exists(p) else {}
    for name, txt, a, b in LABELS:
        if a <= t < b and name in anch:
            x, y, z = anch[name]
            if z > 0 and 0.03 < x < 0.97 and 0.05 < y < 0.95:
                _label(img, ui, x * ui.W, y * ui.H, txt, min(1, (t - a) / 0.2))
    if W(3, "coal") <= t < S(4) - 0.1:
        ui.center_text(img, "1 PELLET  =  1 TON OF COAL", 300, 70, (255, 222, 33))

def moods():
    return [(0.0, "mystery"), (S(9), "happy"), (S(11), "mystery")]

def sfx(cue):
    cue("pop", W(2, "uranium"), 0.6)
    for k in range(5): cue("thud", W(3, "coal") + k * 0.12, 0.3)
    for k in range(3): cue("blip", W(4, "core") - 0.6 + k * 0.3)
    cue("pop", W(5, "splits"), 0.7); cue("pop", W(5, "more", 1) if False else W(5, "split"), 0.6)
    cue("thud", W(6, "steady"), 0.5)
    cue("sizzle", W(8, "steam"), 0.6)
    cue("rumble", W(9, "turbine"), 0.8)
    cue("coin", W(9, "electricity"), 0.7)
    cue("whoosh", W(11, "vapor"))
