"""Episode 002 — "I found the developer command in my Roblox town... Part 2" (sets + animation)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pipeline"))
from lib import *

LIGHTS["frozen"] = ("6f7f99", "c9d2de", "b8c4d6", 0.8, 2.6, "e4ecff", DAYROT)
LIGHTS["alarm"] = ("2a0606", "8a1a1a", "ff7a6a", 0.75, 2.2, "ff5a40", (math.radians(70), 0, math.radians(200)))

SHOT_LIGHT = {"empty": "frozen", "mansion": "interior", "room": "room", "tiny": "dusk", "return": "day", "clones": "day",
              "crown": "day", "crowd": "day", "mine": "cave", "dad": "cave", "alarm": "alarm"}
SHOT_FSTOP = {"empty": 2.8, "mansion": 1.8, "room": 1.4, "tiny": 1.6, "return": 2.8, "clones": 2.2, "crown": 1.6, "crowd": 2.0,
              "mine": 1.6, "dad": 1.4, "alarm": 1.8}
VIS_EXTRA = {"empty": {"town"}, "return": {"town", "people"}, "clones": {"town", "people"}, "crown": {"town", "people"},
             "crowd": {"town", "people"}, "dad": {"mine"}, "alarm": {"town", "people", "mine"}}
setup_shots(SHOT_LIGHT, SHOT_FSTOP)
HERO_LOOK = dict(shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
CLONE = dict(shirt="8f8f8f", pants="5a4a3a", patched=True)

_sm0 = set_mouth
def set_mouth(a, kind):
    _sm0(a, kind)
    if kind == "open": a["mouth_open"].scale = (0.36, 0.08, 0.26)

def pt_light(name, loc, energy, color, kind="POINT", size=None, rot=None):
    l = bpy.data.lights.new(name, kind); l.energy = energy; l.color = color
    if size: l.size = size
    o = bpy.data.objects.new(name, l); col(CUR[0]).objects.link(o); o.location = loc
    if rot: o.rotation_euler = rot
    return o

def sit_pose(a, k=1.0):
    pose(a, legs=(-1.5, -1.5), arms=(-0.35, -0.35), knees=(1.5, 1.5), lean=0.0)

# ================================================================== SETS
# ---------- town (base for empty/return/clones/crown/crowd/alarm)
X = at("town", 0)
baseplate(X, 60, 500)
box((X, 60, 0.02), (14, 220, 0.06), "8c8c8c")
for i in range(9):
    box((X, -30 + i * 22, 0.06), (0.8, 6, 0.04), "f2f2f2")
cols = [("f4d7a8", "c0392b"), ("dfe6ff", "2d6cdf"), ("d8f0d0", "e67e22"), ("fff1b8", "8e44ad"), ("ffd9d9", "16a085"), ("e8e8e8", "d35400")]
random.seed(4)
for i in range(8):
    for sx in (-1, 1):
        wc, rc = cols[(i * 2 + (sx > 0)) % 6]
        house((X + 16 * sx, -10 + i * 18, 0), math.pi / 2 * -sx, wc, rc, h=6 + random.random() * 4)
        if i % 2 == 0: tree((X + 9.5 * sx, -1 + i * 18, 0), 0.8)
spawnpad((X - 3, -16, 0))
MANSION = empty((X + 4, 70, 0))
box((0, 0, 9), (30, 14, 18), "fff6e0", MANSION); wedge((0, 0, 20.5), (32, 16, 5), "2c3e50", MANSION, rot=(0, 0, math.pi / 2))
for i in range(6): box((-12.5 + i * 5, -7.1, 9), (1.3, 0.3, 18), "ffffff", MANSION)
box((0, -7.2, 3), (4, 0.3, 6), "8b5a2b", MANSION)
for (x, y, z, s) in ((X - 40, 160, 60, 2), (X + 50, 200, 70, 2.5), (X + 10, 260, 80, 3)):
    cloud((x, y, z), s)
random.seed(21)
for i in range(7):
    for sx in (-1, 1):
        lamp((X + 7.8 * sx, -2 + i * 18 + 9, 0))
        bush((X + 11.5 * sx, -5 + i * 18 + 12, 0), 0.9)

# ---------- empty: hero alone + frozen leftovers hanging in the air
CUR[0] = "empty"
HERO_E = avatar((X, -14, 0), fdir(0, 1), name="hero_e", **HERO_LOOK)
def hero_e_y(t): return -14 + min(t, 14.5) * 1.9
YB = hero_e_y(W(2, "l")) + 7
FROZEN_B = []
for i, (txt, x, dy, z) in enumerate((("L", -3, 0, 8.5), ("L", 2.5, 1.5, 9.5), ("LOL", 0.5, 3, 11.5), ("L", -1.5, 4.5, 13.0), ("L", 3.5, 5.5, 12.0), ("gg", -4, 6.5, 10.5))):
    FROZEN_B.append(bubble(txt, (X + x, YB + dy, z)))
random.seed(9)
for i in range(12):
    box((X + 4 + random.uniform(-6, 6), 56 + random.uniform(-4, 4), random.uniform(3, 20)), (1.2, 2.4, 0.7), "ffc83d", rot=(random.random() * 3, random.random() * 3, 0), metal=1, rough=0.25)
CAP = empty((X - 4.5, YB + 9, 7.5), rot=(0.4, 0.3, 0.8))
box((0, 0, 0), (1.42, 1.35, 0.36), "e84a4a", CAP, r=0.14); box((0, -0.86, -0.12), (1.0, 0.65, 0.1), "e84a4a", CAP, r=0.04)

# ---------- people: everyone back, all in the hero's patched outfit
CUR[0] = "people"
HERO_P = avatar((X, -4, 0), fdir(0, 1), name="hero_p", **HERO_LOOK)
SPEC = [  # (x, y, hair, hat, shades, scale)
    (-2.2, 8, "f1c40f", "crown", True, 1.0),     # 0 crown kid (richest)
    (1.6, 11, "bdc3c7", "tophat", False, 1.0),   # 1 mayor
    (4.0, 36, "7a4a24", None, False, 4.0),       # 2 giant kid
    (3.8, 7, "1a1a1a", "cap", False, 1.0),       # 3 flyer
    (-4.8, 12, "f1c40f", None, True, 1.0),       # 4 speeder
    (-0.4, 14, "4a2c17", None, False, 1.0),
    (4.6, 15, "1a1a1a", None, False, 1.0),
    (-3.6, 17, "7a4a24", "cap", False, 1.0),
    (1.2, 18.5, "f1c40f", None, False, 1.0),
    (-5.8, 20, "1a1a1a", None, True, 1.0),
    (5.2, 21, "4a2c17", "hardhat", False, 1.0),
    (-1.6, 22.5, "bdc3c7", None, False, 1.0),
    (2.8, 24.5, "1a1a1a", "cap", False, 1.0),
    (-4.2, 26, "f1c40f", None, False, 1.0),
]
PEOPLE = [avatar((X + x, y, 0), fdir(0, -1), hair=h, hat=hat, shades=sh, scale=sc, **CLONE) for (x, y, h, hat, sh, sc) in SPEC]
PFLASH = [cyl((X, 0, 0), (1, 1, 1), "fff6a0", emit=6.0) for _ in PEOPLE]
CROWN, MAYOR, GIANT = PEOPLE[0], PEOPLE[1], PEOPLE[2]
BROKE_B = bubble("why do i look broke??", (X - 2.2, 8, 7.6), w=9.5)
MILLION = empty((X - 2.2, 8, 9.6))
text("1,000,000 R$", (0, 0, 0), 1.5, "2ecc71", MILLION, emit=2.5)

# ---------- alarm props in town
CUR[0] = "alarmtown"
VIS_EXTRA["alarm"].add("alarmtown")
BILL = empty((X, 46, 25)); BILL.scale = (1.35, 1.35, 1.35)
box((0, 0, 0), (26, 0.8, 9), "1a0505", BILL)
box((0, -0.45, 0), (25, 0.1, 8), "ff1a1a", BILL, emit=5.0)
text("SERVER SHUTDOWN", (0, -0.6, 1.5), 2.4, "ffffff", BILL, emit=3.0)
text("WARNING", (0, -0.6, -2.0), 2.0, "ffe0e0", BILL, emit=2.0)
for sx in (-1, 1):
    box((X + 9 * sx, 40, 7), (0.5, 6, 4), "ff2020", emit=4.0, rot=(0, 0, 0))
pt_light("alrt", (X, 40, 18), 30000, (1, 0.2, 0.15))

# ---------- mansion interior
X = at("mansion", 300)
box((X, 10, -0.5), (40, 50, 1), "efe6d2", rough=0.2)
box((X, 8, 0.03), (4, 30, 0.06), "b0182a")
box((X, 32, 10), (40, 1, 20), "fff3d6"); box((X, -15, 10), (40, 1, 20), "fff3d6")
for sx in (-1, 1): box((X + 19 * sx, 8, 10), (1, 50, 20), "f7ead0")
box((X, 8, 20.5), (40, 50, 1), "e8dcc0")
for y in (-4, 4, 12, 20):
    for sx in (-1, 1):
        cyl((X + 7 * sx, y, 9.5), (1.4, 1.4, 19), "ffc83d", metal=1, rough=0.25)
box((X, 24, 0.6), (11, 7, 1.2), "c9a227", metal=0.7, rough=0.3)
THRONE = empty((X, 24.5, 1.2))
box((0, 0, 1.0), (3.6, 3.2, 2.0), "ffc83d", THRONE, metal=1, rough=0.22)
box((0, -0.1, 2.15), (3.2, 2.8, 0.3), "c0392b", THRONE, rough=0.7)
box((0, 1.5, 4.8), (3.8, 0.6, 7.5), "ffc83d", THRONE, metal=1, rough=0.22)
box((0, 1.15, 4.6), (2.8, 0.2, 5.0), "c0392b", THRONE, rough=0.7)
for sx in (-1, 1):
    box((1.95 * sx, -0.1, 2.8), (0.5, 3.0, 0.5), "ffc83d", THRONE, metal=1, rough=0.22)
    sph((1.6 * sx, 1.5, 8.8), (0.6, 0.6, 0.6), "e84a4a", THRONE, emit=0.5, rough=0.1)
cyl((0, 1.5, 8.9), (1.6, 1.6, 0.5), "ffc83d", THRONE, metal=1, rough=0.22)
random.seed(5)
for i in range(40):
    sx = random.choice((-1, 1))
    box((X + sx * random.uniform(4, 10), 24 + random.uniform(-4, 4), 1.2 + random.uniform(0, 2.5) * random.random()), (1.2, 2.4, 0.7), "ffc83d",
        rot=(0, 0, random.random() * 3), metal=1, rough=0.25)
box((X, 31.4, 13), (10, 0.3, 4), "2c3e50"); text("RICH ONLY", (X, 31.2, 13), 1.6, "ffd34d", emit=2.0)
for y in (0, 14):
    sph((X, y, 17.5), (2.0, 2.0, 1.2), "fff2c0", emit=5.0)
pt_light("mnl", (X, 8, 19), 4000, (1, 0.9, 0.75), "AREA", 20, (0, 0, 0))
pt_light("mnl2", (X, 20, 12), 2500, (1, 0.85, 0.6))
HERO_MN = avatar((X, 0, 0), fdir(0, 1), name="hero_mn", **HERO_LOOK)

# ---------- room (computer)
X = at("room", 600)
box((X, 0, -0.5), (30, 30, 1), "1e1e2a"); box((X, 10, 8), (30, 1, 16), "2a2a3a")
for sx in (-1, 1): box((X + 12 * sx, 0, 8), (1, 30, 16), "23232f")
box((X, 6, 2.2), (10, 4, 0.4), "3d3d4f"); box((X - 4, 6, 1), (0.5, 3.5, 2), "3d3d4f"); box((X + 4, 6, 1), (0.5, 3.5, 2), "3d3d4f")
box((X, 7.4, 5.2), (8, 0.5, 5), "111111")
box((X, 7.1, 5.2), (7.4, 0.1, 4.4), "0a2a66", emit=0.45)
pt_light("scr", (X, 5.5, 5.2), 400, (0.35, 0.55, 1.0), "AREA", 7, (math.radians(90), 0, 0))
pt_light("ramb", (X - 6, -6, 12), 300, (0.7, 0.6, 1.0))
SCR1 = [text("DEVELOPER CONSOLE", (X, 6.95, 6.6), 0.5, "ffffff", emit=1.0), text("UNLOCKED", (X, 6.95, 5.8), 0.75, "2ecc71", emit=1.6),
        text("> type any command_", (X, 6.95, 4.9), 0.42, "ffe066", emit=1.2)]
SCR2 = [text("FREE TRIAL", (X, 6.93, 4.0), 0.6, "ff5252", emit=1.6), text("3 commands left", (X, 6.95, 3.35), 0.38, "ffffff", emit=1.0)]
HERO_R = avatar((X, 1, 0), fdir(0, 1), name="hero_r", **HERO_LOOK)
box((X, 0, 1.2), (1, 1, 2.4), "3d3d4f")

# ---------- tiny house at the spawn pad (hero's "home")
X = at("tiny", 900)
baseplate(X, 30, 400, "4a9f45")
spawnpad((X, 0, 0), 1.2)
BED = empty((X - 1, 0.5, 0.4))
box((0, 0, 0.6), (3.2, 6, 1.2), "8b5a2b", BED); box((0, 0.2, 1.3), (3, 5.2, 0.5), "dfe6ff", BED); box((0, 2.3, 1.7), (2.4, 1.2, 0.5), "ffffff", BED)
box((0, -0.8, 1.6), (3.05, 3.2, 0.3), "c0392b", BED)
box((X - 8, 4, 0.8), (3, 2, 1.6), "a0522d"); cyl((X - 8, 4, 2.3), (1.0, 1.0, 1.4), "7f8c8d")
tree((X - 14, 20, 0), 1.0); tree((X + 15, 26, 0), 1.2); tree((X + 18, 6, 0), 0.9)
fence((X - 12, 10, 0), (X + 12, 10, 0), "a87443")
random.seed(3)
for k in range(5): bush((X + random.uniform(-14, 14), random.uniform(6, 18), 0), 0.8)
lamp((X - 7, -3, 0))
for (x, y, s) in ((X - 30, 140, 2), (X + 40, 180, 2.5)):
    cloud((x, y, 50), s)
TINY = house((X + 6.5, -6.0, 0), 0.75 * math.pi, "f4d7a8", "c0392b")
TINY.scale = (0.15, 0.15, 0.15)
TFLASH = cyl((X + 6.5, -6.0, 0.5), (1, 1, 1), "fff6a0", emit=6.0)
HERO_TY = avatar((X + 6.5, -2.5, 0), fdir(0, -1), name="hero_ty", **HERO_LOOK)

# ---------- mine (dad's secret computer)
X = at("mine", 1200)
box((X, 10, -0.5), (80, 80, 1), "5d4037")
random.seed(7)
for i in range(14):
    a = i / 14 * math.pi
    box((X + 18 * math.cos(a), 10 + 18 * math.sin(a) * 0.6 + 6, 6 + random.random() * 6), (6, 6, 14 + random.random() * 6), random.choice(["6d4c41", "5d4037", "795548"]), rot=(0, 0, random.random()))
box((X, 30, 20), (60, 4, 30), "4e342e")
ROCK = empty((X - 4, 6, 0))
box((0, 0, 2), (5, 4, 4), "7f8c8d", ROCK, rot=(0, 0, 0.3)); box((0.6, -0.6, 3.6), (3, 3, 2.5), "95a5a6", ROCK, rot=(0.2, 0, -0.2))
for (x, z) in ((-1.2, 2.6), (1.5, 1.4), (0.3, 4.4)):
    cyl((x, -2.1, z), (0.9, 0.9, 0.25), "2ecc71", ROCK, rot=(math.pi / 2, 0, 0))
PICK = empty((X - 4.5, 3.4, 4.6), rot=(0.5, 0.2, 0.3))
box((0, 0, 0), (0.25, 0.25, 3.2), "8b5a2b", PICK); box((0, -0.2, 1.6), (0.3, 2.6, 0.35), "95a5a6", PICK, rot=(0.25, 0, 0))
# rock pile hiding the secret desk
for (x, y, sx_, sz) in ((8.5, 7.5, 3.5, 4.5), (11.5, 7.8, 3.2, 3.6), (10, 6.8, 2.6, 2.4)):
    box((X + x, y, sz / 2), (sx_, 2.6, sz), "6d4c41", rot=(0, 0, 0.15))
DX, DY = X + 10, 12.6
box((DX, DY + 2.2, 2.7), (5.4, 2.4, 0.3), "3d3d4f")
for sx in (-1, 1): box((DX + 2.4 * sx, DY + 2.2, 1.3), (0.35, 2.0, 2.6), "3d3d4f")
box((DX, DY + 3.0, 4.6), (4.6, 0.35, 3.0), "111111")
SCR_B = box((DX, DY + 2.8, 4.6), (4.2, 0.08, 2.6), "0b3d91", emit=1.4)
SCR_R = box((DX, DY + 2.79, 4.6), (4.2, 0.08, 2.6), "b01010", emit=2.0)
SCR_L = pt_light("dsl", (DX, DY + 1.2, 4.6), 500, (0.35, 0.55, 1.0), "AREA", 4, (math.radians(90), 0, 0))
DEVT = [text("DEVELOPER", (DX, DY + 2.72, 5.2), 0.55, "ffffff", emit=2.5), text("LOGGED IN", (DX, DY + 2.72, 4.3), 0.5, "2ecc71", emit=3.5)]
SHUT = [text("SHUTDOWN", (DX, DY + 2.7, 4.8), 0.6, "ffffff", emit=3.0)]
CHAIR = empty((DX, DY, 0))
box((0, 0, 1.75), (2.3, 2.3, 0.4), "2d3436", CHAIR); cyl((0, 0, 0.8), (0.4, 0.4, 1.6), "636e72", CHAIR, metal=0.6)
box((0, -1.1, 3.4), (2.3, 0.35, 3.0), "2d3436", CHAIR)
DAD = avatar((DX, DY, 0.0), fdir(0, 1), shirt="7f8c8d", pants="2c3e50", hair="4a2c17", hat="hardhat", scale=1.1, name="dad")
DEVTAG = empty((0, 0, 1.95), DAD["head"])
box((0, 0, 0.25), (2.6, 0.15, 0.8), "2ecc71", DEVTAG, emit=1.5); text("DEV", (0, -0.1, 0.25), 0.55, "0b2e13", DEVTAG)
SKIN_PARTS = [o for o in DAD["head"].children if o.type == "MESH" and o.material_slots[0].material == mat(SKIN)]
for (x, y) in ((-10, 16), (12, 18), (-14, 8)):
    box((X + x, y, 5), (0.5, 0.5, 0.9), "ffd27a", emit=12.0)
    pt_light("lan", (X + x, y - 1, 5), 2500, (1, 0.7, 0.35))
for k in range(8):
    sph((X + random.uniform(-14, 14), random.uniform(12, 20), random.uniform(2, 9)), (0.5, 0.3, 0.5), "2ecc71", emit=3.0)
HERO_M = avatar((X, -8, 0), fdir(0, -1), name="hero_m", **HERO_LOOK)
pt_light("runl", (X - 4, -12, 9), 2500, (1, 0.8, 0.55))
pt_light("runl2", (X + 4, -2, 8), 1500, (1, 0.8, 0.55))
ALARM_L = pt_light("mal", (DX - 2, DY - 6, 9), 0, (1, 0.15, 0.1))

# ================================================================== ANIMATION
def update(t):
    CAMTIME[0] = t
    shot, u = shot_at(t)
    apply_shot(shot, VIS_EXTRA)
    if shot == "empty": do_empty(t, u)
    elif shot == "mansion": do_mansion(t, u)
    elif shot == "room": do_room(t, u)
    elif shot == "tiny": do_tiny(t, u)
    elif shot in ("return", "clones", "crown", "crowd"): do_people(t, u, shot)
    elif shot == "mine": do_mine(t, u)
    elif shot == "dad": do_dad(t, u)
    elif shot == "alarm": do_alarm(t, u)
    return shot

def do_empty(t, u):
    X = SETX["town"]; H = HERO_E
    y = hero_e_y(t)
    stop = t > 14.5
    H["root"].location = (X, y, 0)
    if t < 13.3: walk(H, t, 8, 0.6)
    else: idle(H, t); pose(H, head=(0.15, 0, 0.0))
    set_mouth(H, "flat" if t < 11 else "sad"); blink(H, t)
    hp = Vector((X, y, 0))
    behind = S(2) <= t < S(3)
    for b in FROZEN_B: b.rotation_euler = (0, 0, 0 if behind else math.pi)
    if t < S(2):        # front close-up, empty street behind him
        k = ease(t / S(2))
        cam(hp + Vector((lerp(2.5, 1.5, k), lerp(9, 8, k), 4.8)), hp + Vector((0, 0, 4.2)), 30)
    elif t < W(2, "nobody") - 0.1:
        cam(hp + Vector((-6, -11, 7)), hp + Vector((0, 6, 3)), 24)
    elif t < W(2, "spams") - 0.4:   # wide high: nobody anywhere
        v = t - (W(2, "nobody") - 0.1)
        cam(vl((X + 10, y - 24, 22), (X + 8, y - 26, 26), ease(v / 2.5)), (X, y + 14, 3), 24)
    elif t < S(3):      # frozen L bubbles hanging in the air
        v = t - (W(2, "spams") - 0.4)
        cam(vl((X + 2.5, YB - 7, 7.0), (X + 2, YB - 5.5, 7.8), ease(v / 2)), (X, YB + 3, 10.8), 26)
    elif t < W(3, "gray") - 0.1:
        cam(hp + Vector((3.5, 7.5, 5.0)), hp + Vector((0, 0, 4.0)), 30)
    else:               # pull up and away: just me
        v = t - (W(3, "gray") - 0.1)
        k = ease(v / 2.6)
        cam(vl(hp + Vector((2, 10, 6)), hp + Vector((6, 30, 30)), k), hp + Vector((0, 0, 2.5)), 26)

def do_mansion(t, u):
    X = SETX["mansion"]; H = HERO_MN
    TS = W(4, "sat")
    if t < TS - 0.4:
        k = ease((t - shot_start("mansion")) / (TS - 0.4 - shot_start("mansion")))
        H["root"].location = (X, lerp(2, 21.5, k), 0)
        H["root"].rotation_euler = (0, 0, fdir(0, 1))
        walk(H, t, 9, 0.6)
        set_mouth(H, "open"); blink(H, t)
        cam(vl((X + 2.5, -9, 5.5), (X + 2, 4, 6.5), k), (X, 24, 4.5), 26)
        return
    v = t - (TS - 0.4)
    H["root"].rotation_euler = (0, 0, fdir(0, -1))
    k = ease(v / 0.5)
    H["root"].location = (X, lerp(22.5, 24.7, k), lerp(1.2, 1.95, k) + 4 * k * (1 - k) * 1.5)
    if k < 1: jump_pose(H, 0.6)
    else:
        sit_pose(H)
        pose(H, legs=(-1.5, -1.5), knees=(1.5, 1.5), arms=(-0.5, -0.5), arms_out=(0.35, 0.35), head=(0.0, 0, math.sin(t * 0.8) * 0.1))
    blink(H, t)
    bored = t >= W(5, "being") - 0.2
    set_mouth(H, "smile" if not bored else "flat")
    if bored:
        pose(H, legs=(-1.5, -1.5), knees=(1.5, 1.5), arms=(-0.4, -0.9), arms_out=(0.1, 0.1), head=(0.35, 0, 0.25), lean=0.15)
    if t < S(5):
        cam(vl((X + 7, 10, 6), (X + 6, 12, 7), ease(v / 2)), (X, 24, 5.5), 26)
    elif t < W(5, "being") - 0.2:
        w = t - S(5)
        cam(vl((X + 2, 16.5, 7.0), (X + 1.4, 17.6, 6.8), ease(w / 3)), (X, 24.6, 6.6), 32)
    else:   # alone in a huge empty room
        w = t - (W(5, "being") - 0.2)
        cam(vl((X - 3.5, 2, 12), (X - 3.5, -4, 15), ease(w / 3.5)), (X, 22, 4), 24)

def do_room(t, u):
    X = SETX["room"]; H = HERO_R
    idle(H, t); set_mouth(H, "open" if W(6, "developer") - 0.2 < t < S(7) else ("flat" if t >= W(7, "free") else "smile"))
    T1 = W(6, "developer") - 0.3
    for i, o in enumerate(SCR1): o.hide_render = t < T1 + i * 0.6
    for i, o in enumerate(SCR2): o.hide_render = t < W(7, "free") - 0.15 + i * 0.6
    if t < W(6, "it") - 0.2:
        cam(vl((X + 5, -10, 7.5), (X + 3, -7, 7), ease(u / 2)), (X, 6, 5), 26)
    elif t < S(7):
        v = t - (W(6, "it") - 0.2)
        cam(vl((X + 2.6, -0.5, 6.6), (X + 2.0, 1.4, 6.0), ease(v / 4)), (X, 7, 5.6), 30)
    elif t < W(7, "free") - 0.2:   # hero face reaction
        cam((X + 1.2, 5.5, 5.0), (X, 1, 4.6), 30)
    else:
        v = t - (W(7, "free") - 0.2)
        cam(vl((X + 1.8, 2.0, 5.0), (X + 1.4, 2.8, 4.6), ease(v / 3)), (X, 7, 3.9), 32)

def do_tiny(t, u):
    X = SETX["tiny"]; H = HERO_TY
    TSP = W(9, "spawned") - 0.05
    hx, hy = X + 6.5, -2.4
    H["root"].location = (hx, hy, 0)
    H["root"].rotation_euler = (0, 0, fdir(0, -1))
    idle(H, t)
    set_mouth(H, "smile" if t < TSP else "open")
    if t < TSP:
        TINY.scale = (0.0001,) * 3
    else:
        v = t - TSP
        s = 0.15 * min(1.0, v / 0.18) * (1 + 0.25 * math.sin(min(1, v / 0.35) * math.pi))
        TINY.scale = (s, s, s)
        set_mouth(H, "open" if t < S(10) else "flat")
    TFLASH.hide_render = not (TSP <= t < TSP + 0.3)
    fs = 0.5 + (t - TSP) * 14
    TFLASH.scale = (fs, fs, 0.15)
    if S(10) <= t:
        v = t - S(10)
        k = ease((v - 0.2) / 0.7)
        H["root"].location = (hx, hy - 1.2 * k, 0)
        pose(H, legs=(0, -1.0 * k), knees=(0.05, 0.5 * k), arms=(-0.3 * k, -0.6 * k), arms_out=(0.5 * k, 0.5 * k), head=(0.45 * k, 0, 0), lean=-0.12 * k)
        set_mouth(H, "flat")
    if t < W(8, "because") - 0.1:
        cam(vl((hx + 5.5, -12, 5.5), (hx + 4.5, -10.5, 5.2), ease(u / 2.5)), (hx, hy, 4.3), 28)
    elif t < TSP - 0.1:   # the spawn pad bed = home
        v = t - (W(8, "because") - 0.1)
        cam(vl((X - 6, -13, 7), (X - 4, -12, 6), ease(v / 3)), (X, 0.5, 1.5), 26)
    elif t < S(10) - 0.05:   # ground-level: tiny house, hero towering behind
        v = t - (TSP - 0.1)
        cam(vl((hx + 4.5, -10.5, 0.8), (hx + 4.0, -9.8, 0.9), ease(v / 3)), (hx, -4.5, 2.6), 24)
    else:                    # side view: one foot in
        v = t - S(10)
        cam(vl((hx + 8.5, -5.5, 2.2), (hx + 7.5, -5.0, 2.6), ease(v / 2.5)), (hx, -4.4, 1.8), 30)

T_DROP = W(12, "worked") - 0.1
ROWS = [(0, 3), (1, 4), (5, 6), (7, 8), (9, 10), (11, 12), (13, 2)]
def drop_time(i):
    order = [j for r in ROWS for j in r]
    return T_DROP + order.index(i) * 0.17

def place_people(t, shot):
    X = SETX["town"]
    for i, (a, (x, y, h, hat, sh, sc)) in enumerate(zip(PEOPLE, SPEC)):
        base = Vector((X + x, y, 0))
        a["root"].rotation_euler = (0, 0, fdir(0, -1))
        ts = drop_time(i)
        fl = PFLASH[i]
        fl.hide_render = True
        if shot == "return" or shot == "alarm" and False:
            if t < ts:
                hide(a["root"]); continue
            hide(a["root"], False)
            v = t - ts
            z = max(0.0, 12 * sc - 40 * v * v)
            a["root"].location = base + Vector((0, 0, z))
            if z > 0: jump_pose(a)
            else: idle(a, t, i); set_mouth(a, "open")
            if v < 0.28:
                fl.hide_render = False; fl.location = base + Vector((0, 0, 0.3)); s_ = (1.5 + v * 14) * sc; fl.scale = (s_, s_, 0.15)
            continue
        hide(a["root"], False)
        a["root"].location = base
        idle(a, t, i * 1.3)
        set_mouth(a, "flat" if i % 3 else "sad")

def do_people(t, u, shot):
    X = SETX["town"]; H = HERO_P
    BROKE_B.hide_render = True; hide(BROKE_B, True); hide(MILLION, True)
    H["root"].location = (X, -4, 0); H["root"].rotation_euler = (0, 0, fdir(0, 1))
    idle(H, t); set_mouth(H, "flat")
    place_people(t, shot)
    hp = Vector((X, -4, 0))
    if shot == "return":
        set_mouth(H, "smile" if t >= T_DROP + 0.4 else "flat")
        if t < S(12) - 0.1:
            cam(vl(hp + Vector((2.6, 8, 4.6)), hp + Vector((2.0, 7, 4.8)), ease(u / 3.5)), hp + Vector((0, 0, 4.4)), 30)
        else:
            v = t - (S(12) - 0.1)
            cam(vl((X + 6, -16, 9), (X + 5, -18, 12), ease(v / 3.5)), (X, 14, 3.5), 24)
        return
    if shot == "clones":
        TM = W(13, "mine") - 0.1
        if t < TM:
            v = t - shot_start("clones")
            cam(vl((X + 3, -6, 5.5), (X + 2, -3, 5.0), ease(v / 3)), (X - 0.5, 12, 3.8), 26)
        elif t < S(14):
            cam(hp + Vector((1.0, -5.5, 4.8)), hp + Vector((0, 0, 4.4)), 30)  # hero from front? he faces +Y
            cam(hp + Vector((1.8, 6.0, 4.9)), hp + Vector((0, 0, 4.5)), 30)
            set_mouth(H, "flat")
        elif t < W(14, "even") - 0.15:   # slow pan across the patched crowd
            v = t - S(14)
            cam(vl((X - 6, 2, 4.2), (X + 4, 2, 4.4), ease(v / 3.5)), vl((X - 4, 14, 3.4), (X + 3, 14, 3.4), ease(v / 3.5)), 28)
        elif t < W(14, "even", 1) - 0.15:  # the mayor
            m = Vector(MAYOR["root"].location)
            set_mouth(MAYOR, "sad")
            cam(m + Vector((-0.5, -5.5, 5.6)), m + Vector((0, 0, 5.0)), 30)
        else:                              # the giant kid, low angle
            g = Vector(GIANT["root"].location)
            set_mouth(GIANT, "open")
            v = t - (W(14, "even", 1) - 0.15)
            cam(vl(g + Vector((2, -22, 7)), g + Vector((2, -21, 7.5)), ease(v / 2)), g + Vector((0, 0, 13)), 22)
        return
    if shot == "crown":
        c = Vector(CROWN["root"].location)
        A = CROWN
        if t < W(15, "why") - 0.1:
            pose(A, arms=(0.3, 0.3), arms_out=(0.5, 0.5), head=(0.35, 0, 0), lean=0.1)
            set_mouth(A, "flat")
        elif t < S(16):
            pose(A, arms=(-0.4, -0.4), arms_out=(0.0, 0.0), elbows=(-1.3, -1.3), head=(-0.05, 0, 0.1))
            set_mouth(A, "open")
            hide(BROKE_B, False); BROKE_B.location = c + Vector((0, -0.4, 7.6))
        else:
            pose(A, arms=(-1.5, 0), arms_out=(0.0, 0.1), head=(0, 0, 0))
            set_mouth(A, "smile")
            if t >= W(16, "one") - 0.1:
                hide(MILLION, False); k = min(1, (t - W(16, "one") + 0.1) / 0.25)
                MILLION.location = c + Vector((-0.5, -1.2, 8.0)); MILLION.scale = (k, k, k)
        if t < W(15, "said") - 0.2:
            v = t - shot_start("crown")
            cam(vl(c + Vector((1.4, -5.0, 3.0)), c + Vector((1.1, -4.4, 3.2)), ease(v / 3)), c + Vector((0, 0, 4.4)), 30)
        elif t < S(16):
            cam(c + Vector((1.4, -7.5, 5.6)), c + Vector((0, 0, 5.8)), 28)
        elif t < W(16, "my") - 0.1:
            v = t - S(16)
            cam(vl(c + Vector((3.0, -11, 6.5)), c + Vector((2.5, -10, 7.0)), ease(v / 3)), c + Vector((0, 0, 6.5)), 28)
        else:   # hero reaction: my dad makes that in 2000 years
            set_mouth(H, "sad")
            cam(hp + Vector((1.8, 6.0, 4.9)), hp + Vector((0, 0, 4.5)), 30)
        return
    if shot == "crowd":
        T19 = S(19)
        for i, a in enumerate(PEOPLE):
            x, y = a["root"].location.x, a["root"].location.y
            face_me = fdir(H["root"].location.x - x, H["root"].location.y - y)
            away = face_me + math.pi
            k = ease((t - T19 - 0.6 - i * 0.05) / 2.2)
            a["root"].rotation_euler = (0, 0, lerp(away, face_me + 2 * math.pi, k))
            set_mouth(a, "flat")
            for br in a["brows"]: br.rotation_euler = (0, (-0.3 if br.location.x < 0 else 0.3) * k, 0)
        if t < T19:
            set_mouth(H, "smile" if t < S(18) else "sad")
            cam(hp + Vector((1.8, 6.0, 4.9)), hp + Vector((0, 0, 4.5)), 30)
        else:   # over-the-shoulder: the whole town turns around
            v = t - T19
            pose(H, head=(0.0, 0, 0)); set_mouth(H, "open")
            cam(vl(hp + Vector((2.6, -5.5, 6.2)), hp + Vector((2.0, -3.0, 5.8)), ease(v / 3.4)), (X - 0.5, 12, 4.0), 26)

def do_mine(t, u):
    X = SETX["mine"]; H = HERO_M
    for o in DEVT + SHUT: o.hide_render = True
    hide(DEVTAG, True); SCR_R.hide_render = True
    DAD["root"].location = (DX, DY, 0.2); DAD["root"].rotation_euler = (0, 0, fdir(0, 1)); CHAIR.rotation_euler = (0, 0, 0)
    sit_pose(DAD); pose(DAD, legs=(-1.5, -1.5), knees=(1.5, 1.5), arms=(-1.2 + math.sin(t * 9) * 0.1, -1.2 + math.cos(t * 9) * 0.1), head=(0.1, 0, 0))
    T21 = S(21)
    if t < T21:
        k = (t - shot_start("mine")) / (T21 - shot_start("mine"))
        p = Vector((X + lerp(-12, 2, k), lerp(-16, -2, k), 0))
        H["root"].location = p; H["root"].rotation_euler = (0, 0, fdir(1, 1))
        walk(H, t, 15, 1.0); set_mouth(H, "sad")
        cam(p + Vector((7.0, 7.0, 4.6)), p + Vector((0, 0, 3.8)), 28)
    else:
        v = t - T21
        p = Vector((X + 2, -2, 0))
        H["root"].location = p; H["root"].rotation_euler = (0, 0, fdir(0.5, 1)); idle(H, t); set_mouth(H, "open")
        if t < W(21, "he") - 0.1:   # empty spot, pickaxe left in the ore
            cam(vl((X - 9, -6, 5), (X - 8, -4, 5.2), ease(v / 1.5)), (X - 4, 5, 3.4), 28)
        else:                       # crane over the rock pile: dad at a secret computer
            w = t - (W(21, "he") - 0.1)
            k = ease(w / 2.8)
            cam(vl((X + 7, 1.5, 6.5), (X + 8, 4.2, 10.5), k), vl((X + 9, 9, 4.5), (DX, DY + 1.5, 4.0), k), 28)

def do_dad(t, u):
    X = SETX["mine"]; H = HERO_M; D = DAD
    for o in SKIN_PARTS: o.material_slots[0].material = mat(SKIN)
    ALARM_L.data.energy = 0; SCR_L.data.color = (0.35, 0.55, 1.0)
    SCR_R.hide_render = True
    for o in SHUT: o.hide_render = True
    for i, o in enumerate(DEVT): o.hide_render = t < W(22, "developer") - 0.1 + i * 0.5
    hp = Vector((DX + 3.6, DY - 2.0, 0))
    H["root"].location = hp; H["root"].rotation_euler = (0, 0, fdir(-1, -0.25)); idle(H, t)
    set_mouth(H, "open" if t >= W(23, "made") else "flat")
    TT = S(23) - 0.2
    k = ease((t - TT) / 0.8)
    rz = lerp(fdir(0, 1), fdir(0.25, -1) + 2 * math.pi, k) if t >= TT else fdir(0, 1)
    D["root"].location = (DX, DY, 0.2); D["root"].rotation_euler = (0, 0, rz); CHAIR.rotation_euler = (0, 0, rz - fdir(0, 1))
    blink(D, t)
    if t < TT:
        pose(D, legs=(-1.5, -1.5), knees=(1.5, 1.5), arms=(-1.2 + math.sin(t * 9) * 0.1, -1.2 + math.cos(t * 9) * 0.1), head=(0.1, 0, 0))
        set_mouth(D, "flat")
    else:
        talk = S(24) <= t < S(25)
        pose(D, legs=(-1.5, -1.5), knees=(1.5, 1.5), arms=(-0.4, -0.9 if talk else -0.4), arms_out=(0.2, 0.3), head=(0.0, 0, 0.2 if t >= S(24) else 0))
        set_mouth(D, ("open" if int(t * 7) % 2 else "smile") if talk else "smile")
    hide(DEVTAG, t < W(23, "made") - 0.1)
    dh = Vector((DX, DY, 0))
    if t < TT:      # over dad's shoulder onto the screen
        v = t - shot_start("dad")
        cam(vl((DX + 3.4, DY - 2.6, 5.9), (DX + 3.0, DY - 1.8, 5.7), ease(v / 3)), (DX + 0.2, DY + 2.8, 4.8), 30)
    elif t < S(24):  # dad turns: he made the whole game
        v = t - TT
        cam(vl(dh + Vector((1.2, -6.5, 5.4)), dh + Vector((0.9, -5.6, 5.3)), ease(v / 3)), dh + Vector((0, 0, 5.1)), 30)
    elif t < S(25):  # two-shot
        v = t - S(24)
        cam(vl(dh + Vector((2.2, -10.5, 6.6)), dh + Vector((2.0, -9.5, 6.4)), ease(v / 5)), dh + Vector((1.8, 0, 4.4)), 28)
    else:            # hero: about to ask
        v = t - S(25)
        set_mouth(H, "open" if int(t * 6) % 2 and t < W(25, "game") + 0.3 else "flat")
        cam(vl(hp + Vector((-1.5, -5.8, 4.9)), hp + Vector((-1.2, -5.2, 4.8)), ease(v / 4)), hp + Vector((0, 0, 4.4)), 30)

def do_alarm(t, u):
    X = SETX["town"]
    # town part
    HERO_P["root"].location = (X, -4, 0); HERO_P["root"].rotation_euler = (0, 0, fdir(0, 1)); idle(HERO_P, t)
    hide(BROKE_B, True); hide(MILLION, True)
    place_people(t, "alarm")
    for i, a in enumerate(PEOPLE):
        pose(a, head=(-0.45, 0, 0), arms=(0.1, 0.1), arms_out=(0.2, 0.2)); set_mouth(a, "open")
        a["root"].rotation_euler = (0, 0, fdir(0, 1))
    pose(HERO_P, head=(-0.45, 0, 0)); set_mouth(HERO_P, "open")
    BILL.location = (X, 46, 25 + math.sin(t * 2) * 0.3)
    # mine part
    D = DAD; H = HERO_M
    SCR_R.hide_render = False
    for o in DEVT: o.hide_render = True
    for o in SHUT: o.hide_render = int(t * 3) % 2 == 0
    SCR_L.data.color = (1, 0.15, 0.1)
    ALARM_L.data.energy = 900 * (0.6 + 0.4 * abs(math.sin(t * 4)))
    hp = Vector((DX + 3.6, DY - 2.0, 0))
    H["root"].location = hp; H["root"].rotation_euler = (0, 0, fdir(-1, -0.25)); idle(H, t); set_mouth(H, "sad")
    rz = fdir(0.25, -1)
    D["root"].location = (DX, DY, 0.2); D["root"].rotation_euler = (0, 0, rz); CHAIR.rotation_euler = (0, 0, rz - fdir(0, 1))
    pose(D, legs=(-1.5, -1.5), knees=(1.5, 1.5), arms=(-0.3, -0.3), arms_out=(0.1, 0.1), head=(0, 0, 0.15))
    blink(D, t)
    hide(DEVTAG, False)
    white = t >= W(27, "white") - 0.1
    for o in SKIN_PARTS: o.material_slots[0].material = mat("f4f4f0") if white else mat(SKIN)
    set_mouth(D, "open" if t >= W(27, "white") - 0.1 else "flat")
    if S(27) - 0.1 <= t < S(28) and t >= W(27, "son") - 0.05:
        set_mouth(D, "open" if int(t * 7) % 2 else "flat")
    dh = Vector((DX, DY, 0))
    if t < S(27) - 0.1:   # town: everyone looks up at the red sky screen
        v = t - shot_start("alarm")
        cam(vl((X + 3, -11, 3.5), (X + 2.5, -13, 4.0), ease(v / 4)), vl((X, 20, 8), (X, 46, 22), ease(v / 3)), 22)
    elif t < S(28) - 0.1:   # dad close-up, face goes white
        v = t - (S(27) - 0.1)
        cam(vl(dh + Vector((1.0, -5.8, 5.3)), dh + Vector((0.8, -5.0, 5.2)), ease(v / 3)), dh + Vector((0, 0, 5.1)), 32)
    else:                   # two-shot, push in
        v = t - (S(28) - 0.1)
        cam(vl(dh + Vector((2.2, -11, 5.8)), dh + Vector((2.0, -8.5, 5.4)), ease(v / 4)), dh + Vector((1.8, 0, 4.3)), 28)


if __name__ == "__main__":
    run(update, VIS_EXTRA)
