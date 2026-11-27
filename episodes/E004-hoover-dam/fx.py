"""E004 explainer effects: tracked labels (labels/fNNNNN.json from scene.py), cooling-time graphic, calm music."""
import os, json
from PIL import ImageDraw
from timing import *

HEADER = ("HOW THE HOOVER DAM", "WAS BUILT")
HOT = {"hoover", "dam", "lake", "four", "tunnels", "river", "dry", "grout", "concrete", "blocks", "five", "hundred", "twenty",
       "years", "cold", "pipe", "mead", "sixty", "pressure", "depth", "weight", "arch", "seventeen", "turbines", "electricity",
       "spillways", "floods", "trust"}

# (anchor, text, start, end)
LABELS = [
    ("front", "1 OF 4 DIVERSION TUNNELS", W(2, "four") - 0.1, S(3) - 0.1),
    ("tflow", "RIVER → TUNNEL", W(3, "pushed"), W(3, "leaving")),
    ("coffer", "COFFERDAM", W(3, "leaving"), S(4) - 0.1),
    ("dry", "DRY RIVERBED", W(3, "dry") - 0.2, S(4) - 0.1),
    ("bedrock", "BEDROCK", W(4, "bedrock") - 0.1, W(4, "filled") - 0.1),
    ("grout", "GROUT CURTAIN", W(4, "grout") - 0.1, S(5) - 0.1),
    ("blocks", "~215 BLOCKS", W(5, "two") - 0.1, W(5, "five") - 0.1),
    ("blocks", "5 FEET AT A TIME", W(5, "five") - 0.1, S(6) - 0.1),
    ("pipes", "580+ MILES OF PIPE", W(7, "hundreds") - 0.1, S(8) - 0.1),
    ("gate", "TUNNEL GATE CLOSES", W(8, "tunnels") - 0.1, W(8, "lake") - 0.1),
    ("lake", "LAKE MEAD", W(8, "lake") - 0.1, S(9) - 0.1),
    ("base", "660 FT THICK", W(9, "six") - 0.1, W(9, "because") - 0.1),
    ("press", "MORE PRESSURE DEEPER", W(9, "water") + 0.2, S(10) - 0.1),
    ("weight", "WEIGHT", W(10, "weight") - 0.1, S(11) - 0.1),
    ("arch", "ARCH SHAPE", W(10, "arch") - 0.1, S(11) - 0.1),
    ("tower", "INTAKE TOWER", W(11, "towers") - 0.1, W(11, "seventeen") - 0.1),
    ("turbines", "17 TURBINES", W(11, "seventeen") - 0.1, S(12) - 0.1),
    ("spill", "SPILLWAY", W(12, "spillways") - 0.1, S(13) - 0.1),
    ("outlet", "FLOODWATER OUT", W(12, "escape") - 0.1, S(13) - 0.1),
]
LBL_DIR = os.path.join(EP, "labels")

def punches():
    return [(W(2, "dug"), 0.04), (W(5, "concrete"), 0.04), (W(8, "closed"), 0.05), (W(10, "arch"), 0.04)]

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
    # cooling time graphic
    a = W(6, "hundred") - 0.1
    if a <= t < S(7) - 0.05:
        ui.center_text(img, "≈ 125 YEARS", 300, 96, (255, 160, 60), 0.85 + 0.15 * min(1, (t - a) / 0.15))
        ui.center_text(img, "TO COOL ON ITS OWN", 400, 60, (255, 255, 255))

def moods():
    return [(0.0, "mystery"), (S(8), "happy"), (S(13), "mystery")]

def sfx(cue):
    cue("rumble", W(2, "dug"), 0.8); cue("rumble", W(2, "dug") + 1.8, 0.6)
    cue("whoosh", W(3, "pushed"), 1.0)
    cue("rumble", S(4), 0.5)
    for w in ("drilled", "filled"): cue("blip", W(4, w))
    for k in range(6): cue("thud", S(5) + 0.4 + k * 0.55, 0.35)
    cue("sizzle", W(6, "poured"), 0.6)
    cue("whoosh", W(7, "cold"), 0.8)
    cue("bonk", W(8, "closed"), 0.6)
    cue("whoosh", W(8, "lake"), 1.0)
    cue("pop", W(9, "six"), 0.6)
    cue("thud", W(10, "weight"), 0.8)
    cue("pop", W(11, "seventeen"), 0.6)
    cue("coin", W(11, "electricity"), 0.6)
    cue("whoosh", W(12, "spillways"), 0.9)
