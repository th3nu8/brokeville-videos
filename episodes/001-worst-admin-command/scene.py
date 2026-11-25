"""Episode 001 — "Everyone in my Roblox town gets admin commands... I got /jump" (sets + animation)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pipeline"))
from lib import *

SHOT_LIGHT = {"town": "day", "freeze": "day", "spawn": "dusk", "shop": "interior", "laugh": "day", "school": "day", "mine": "cave",
              "mayor": "day", "line": "day", "fails": "day", "climb": "high", "clouds": "high", "top": "sunset", "room": "room"}
SHOT_FSTOP = {"town": 2.8, "freeze": 2.8, "spawn": 1.6, "shop": 1.6, "laugh": 1.8, "school": 1.8, "mine": 1.4, "mayor": 2.8,
              "line": 1.8, "fails": 2.8, "climb": 2.8, "clouds": 3.5, "top": 2.2, "room": 1.4}
VIS_EXTRA = {"line": {"mayor"}, "fails": {"mayor", "line"}, "freeze": {"town"}, "clouds": {"climb"}, "top": {"topclouds"}}
setup_shots(SHOT_LIGHT, SHOT_FSTOP)

# ================================================================== SETS
# ---------- town (also used for freeze)
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
spawnpad((X - 3, -12, 0))
# mansion for money kid
MANSION = empty((X + 4, 70, 0))
box((0, 0, 9), (30, 14, 18), "fff6e0", MANSION); wedge((0, 0, 20.5), (32, 16, 5), "2c3e50", MANSION, rot=(0, 0, math.pi / 2))
for i in range(6): box((-12.5 + i * 5, -7.1, 9), (1.3, 0.3, 18), "ffffff", MANSION)
text("SOLD", (0, -7.4, 13), 3.5, "e84a4a", MANSION)
FLYER = avatar((X, 0, 0), shirt="e84a4a", pants="1f1f1f", hair="1a1a1a", hat="cap")
SPEEDER = avatar((X, 0, 0), shirt="2fb3ff", pants="ffffff", hair="f1c40f", shades=True)
SPEED_LINES = [box((X, 0, 0), (0.15, 6, 0.15), "ffffff") for _ in range(6)]
GIANT = avatar((X + 25, 40, 0), shirt="2ecc71", pants="27ae60", hair="7a4a24", scale=4.0)
RICH = avatar((X, 64, 0), fdir(0, -1), shirt="111111", pants="111111", hair="f1c40f", hat="crown", shades=True)
GOLD = [box((X, 60, 30), (1.2, 2.4, 0.7), "ffc83d", metal=1, rough=0.25) for _ in range(16)]
TOWN_KIDS = [avatar((X - 4 + (i % 4) * 2.6, 4 + (i // 4) * 6, 0), fdir(0, -1), shirt=c, hair=h) for i, (c, h) in enumerate(
    [("9b59b6", "1a1a1a"), ("e67e22", "4a2c17"), ("1abc9c", "f1c40f"), ("e84393", "1a1a1a"), ("34495e", "7a4a24"), ("f1c40f", "1a1a1a"), ("16a085", "4a2c17"), ("d35400", "1a1a1a")])]
HERO_T = avatar((X - 3, -12, 0.4), fdir(0, -1), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True, name="hero_town")
for (x, y, z, s) in ((X - 40, 160, 60, 2), (X + 50, 200, 70, 2.5), (X + 10, 260, 80, 3)):
    cloud((x, y, z), s)

# ---------- spawn (where hero lives)
X = at("spawn", 300)
baseplate(X, 30, 400, "4a9f45")
spawnpad((X, 0, 0), 1.2)
BED = empty((X, 0.5, 0.4))
box((0, 0, 0.6), (3.2, 6, 1.2), "8b5a2b", BED); box((0, 0.2, 1.3), (3, 5.2, 0.5), "dfe6ff", BED); box((0, 2.3, 1.7), (2.4, 1.2, 0.5), "ffffff", BED)
box((0, -0.8, 1.6), (3.05, 3.2, 0.3), "c0392b", BED)
HERO_S = avatar((X + 0.0, 1.0, 1.45), fdir(0, -1), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
box((X + 6, 3, 1), (2, 2, 2), "b98b4e"); text("HOME", (X + 6, 1.9, 1.3), 0.45, "3a2410")
box((X - 7, 4, 0.8), (3, 2, 1.6), "a0522d"); cyl((X - 7, 4, 2.3), (1.0, 1.0, 1.4), "7f8c8d")
NEWB = [avatar((X, 0, 0), fdir(0, -1), shirt=c, pants="2b3a55", hair=h) for c, h in (("e84a4a", "1a1a1a"), ("2fb3ff", "f1c40f"), ("2ecc71", "4a2c17"), ("f39c12", "1a1a1a"))]
SPAWN_FLASH = [cyl((X, 0, 0), (1, 1, 1), "fff6a0", emit=6.0) for _ in range(4)]
for (x, y, s) in ((X - 30, 140, 2), (X + 40, 180, 2.5)):
    cloud((x, y, 50), s)
tree((X - 14, 20, 0), 1.0); tree((X + 15, 26, 0), 1.2)

# ---------- shop
X = at("shop", 600)
baseplate(X, 30, 300, "3e8e3b")
box((X, 6, 0.05), (26, 20, 0.1), "d9c4a0")
box((X, 16, 8), (26, 1, 16), "34495e")
for sx in (-1, 1): box((X + 13 * sx, 6, 8), (1, 20, 16), "2c3e50")
box((X, 16, 17), (28, 22, 1), "2c3e50")
box((X, 15.3, 13), (16, 0.4, 3), "111111"); text("ADMIN COMMANDS", (X, 15.0, 13), 1.6, "ffd34d", emit=3.0)
_sh_l = bpy.data.lights.new("shopl", "AREA"); _sh_l.energy = 2500; _sh_l.size = 14; _sh_l.color = (1, 0.92, 0.8)
_shl = bpy.data.objects.new("shopl", _sh_l); col(CUR[0]).objects.link(_shl); _shl.location = (X, 4, 16.2)
CARDS = []
for i, (c, p, col_) in enumerate((("/fly", "9,999 R$", "e84a4a"), ("/speed", "7,500 R$", "2fb3ff"), ("/giant", "8,000 R$", "2ecc71"), ("/money", "50,000 R$", "ffc83d"))):
    x = X - 8.4 + i * 5.6
    box((x, 15.2, 7.5), (4.6, 0.3, 5.2), col_)
    text(c, (x, 14.9, 8.4), 1.15, "ffffff"); text(p, (x, 14.9, 6.6), 0.75, "111111")
    box((x - 1.6, 14.95, 9.75), (1.5, 0.1, 0.6), "c0392b", rot=(0, 0.15, 0)); text("SOLD OUT", (x - 1.6, 14.85, 9.75), 0.25, "ffffff", rot=(math.radians(90), 0.15, 0))
box((X, 7, 1.8), (16, 3, 3.6), "8b5a2b"); box((X, 7, 3.65), (16.4, 3.4, 0.3), "a87443")
KEEPER = avatar((X + 2, 9.5, 0), fdir(0, -1), shirt="8e44ad", pants="2c3e50", hair="bdc3c7", shades=True)
HERO_SH = avatar((X - 2, 2.2, 0), fdir(0, 1), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
JCARD = empty((X, 7, 4.2))
box((0, 0, 0), (3.6, 0.25, 2.4), "bdc3c7", JCARD)
text("/jump", (0, -0.15, 0.35), 0.95, "2d3436", JCARD); text("FREE", (0, -0.15, -0.65), 0.5, "e84a4a", JCARD)
box((0.9, -0.15, -0.55), (1.3, 0.05, 0.08), "636e72", JCARD, rot=(0, -0.25, 0))

# ---------- laugh
X = at("laugh", 900)
baseplate(X, 30, 300)
box((X, 20, 0.02), (14, 120, 0.06), "8c8c8c")
house((X - 14, 22, 0), -math.pi / 2, "dfe6ff", "2d6cdf"); house((X + 14, 26, 0), math.pi / 2, "fff1b8", "8e44ad")
HERO_L = avatar((X, 6, 0), fdir(0, -1), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
LAUGHERS = []
for i, (x, y, c, h, hat) in enumerate(((X - 5, 3, "e84a4a", "1a1a1a", "cap"), (X + 5, 2.5, "2fb3ff", "f1c40f", None), (X - 7, 9, "2ecc71", "4a2c17", None), (X + 6.5, 9.5, "111111", "f1c40f", "crown"), (X - 2.5, 12, "e67e22", "1a1a1a", None), (X + 2.5, 12.5, "9b59b6", "7a4a24", None))):
    LAUGHERS.append(avatar((x, y, 0), fdir(X - x, 6 - y), shirt=c, hair=h, hat=hat, shades=(i == 3)))
BUBS = []
for i, (txt, x, y, z) in enumerate((("LOL", X - 5, 3, 8.2), ("/jump?? LMAO", X + 5, 2.5, 8.2), ("L", X - 7, 9, 8.6), ("L", X + 6.5, 9.5, 10.0), ("L", X - 2.5, 12, 8.6), ("L", X + 2.5, 12.5, 8.6),
                                   ("L", X - 7, 9, 10.0), ("L", X - 2.5, 12, 10.0), ("L", X + 2.5, 12.5, 10.0), ("L", X - 7, 9, 11.4), ("L", X + 6.5, 9.5, 11.4), ("L", X - 2.5, 12, 11.4))):
    BUBS.append(bubble(txt, (x, y - 0.6, z)))

# ---------- school
X = at("school", 1200)
baseplate(X, 30, 300)
box((X, 26, 9), (40, 12, 18), "c0392b"); box((X, 19.9, 15), (18, 0.4, 3), "ffffff"); text("SCHOOL", (X, 19.6, 15), 2.2, "c0392b")
for i in range(5):
    box((X - 14 + i * 7, 19.9, 7), (3, 0.3, 3), "9fd8ff")
box((X + 6, 12, 1.8), (10, 3, 3.6), "bdc3c7"); box((X + 6, 12, 3.7), (10.4, 3.4, 0.25), "ecf0f1")
LADY = avatar((X + 6, 15, 0), fdir(0, -1), shirt="ffffff", pants="7f8c8d", hair="bdc3c7")
cyl((X + 6, 15, 5.4), (1.3, 1.3, 0.6), "ffffff")
LINE_KIDS = [avatar((X + 6 - 0 - i * 0.0, 7 - i * 3.0, 0), fdir(0, 1), shirt=c, hair=h) for i, (c, h) in enumerate((("1abc9c", "1a1a1a"), ("f39c12", "4a2c17"), ("e84393", "1a1a1a")))]
HERO_SC = avatar((X + 6, -3, 0), fdir(0, 1), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
SC_FLYERS = [avatar((X, 0, 0), shirt=c, pants="111111", hair="1a1a1a", hat=h, shades=s) for c, h, s in (("e84a4a", "cap", False), ("111111", "crown", True))]
PIZZA = empty((X, 0, 0))
obj(M_WEDGE, (0, 0, 0), (1.6, 0.02, 1.6), "f5b041", PIZZA, rot=(0, 0, 0))
sph((0.2, -0.02, -0.2), (0.35, 0.02, 0.35), "c0392b", PIZZA); sph((-0.25, -0.02, -0.35), (0.3, 0.02, 0.3), "c0392b", PIZZA)
PIZZA_LBL = text("decal.png", (X, 0, 0), 0.35, "ffffff")
tree((X - 22, 10, 0), 1.1); tree((X + 24, 8, 0), 1.0)

# ---------- mine
X = at("mine", 1500)
box((X, 10, -0.5), (80, 80, 1), "5d4037")
for i in range(14):
    a = i / 14 * math.pi
    box((X + 18 * math.cos(a), 10 + 18 * math.sin(a) * 0.6 + 6, 6 + random.random() * 6), (6, 6, 14 + random.random() * 6), random.choice(["6d4c41", "5d4037", "795548"]), rot=(0, 0, random.random()))
box((X, 30, 20), (60, 4, 30), "4e342e")
ROCK = empty((X + 4, 10, 0))
box((0, 0, 2), (5, 4, 4), "7f8c8d", ROCK, rot=(0, 0, 0.3)); box((0.6, -0.6, 3.6), (3, 3, 2.5), "95a5a6", ROCK, rot=(0.2, 0, -0.2))
for (x, z) in ((-1.2, 2.6), (1.5, 1.4), (0.3, 4.4)):
    cyl((x, -2.1, z), (0.9, 0.9, 0.25), "2ecc71", ROCK, rot=(math.pi / 2, 0, 0))
DAD = avatar((X + 0, 6.5, 0), fdir(1, 0.6), shirt="7f8c8d", pants="2c3e50", hair="4a2c17", hat="hardhat", scale=1.2)
PICK = empty((0, 0, -0.85), DAD["elbows"][1])
box((0, 0, -0.6), (0.25, 0.25, 3.2), "8b5a2b", PICK); box((0, -0.2, -2.2), (0.3, 2.6, 0.35), "95a5a6", PICK, rot=(0.25, 0, 0))
HERO_M = avatar((X - 5, 4, 0), fdir(1, 0.2), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
COIN = empty((X + 4, 7.5, 3))
cyl((0, 0, 0), (1.1, 1.1, 0.25), "2ecc71", COIN, rot=(math.pi / 2, 0, 0), emit=2.0); text("+1 R$", (0, -0.25, 1.3), 0.7, "ffffff", COIN, emit=1.5)
for (x, y) in ((-10, 16), (12, 18), (-14, 8)):
    box((X + x, y, 5), (0.5, 0.5, 0.9), "ffd27a", emit=12.0)
    _pl = bpy.data.lights.new("lan", "POINT"); _pl.energy = 2500; _pl.color = (1, 0.7, 0.35)
    _po = bpy.data.objects.new("lan", _pl); col(CUR[0]).objects.link(_po); _po.location = (X + x, y - 1, 5)

# ---------- mayor + tower (shared base area at x=1800); tower stages go up
X = at("mayor", 1800)
baseplate(X, 60, 600)
box((X, 0, 1), (16, 8, 2), "8e44ad"); box((X, 0, 2.05), (16.2, 8.2, 0.1), "f1c40f")
box((X, -2, 3.5), (2.4, 1.6, 3), "6b3f22")
MAYOR = avatar((X, 0, 2), fdir(0, -1), shirt="2c3e50", pants="2c3e50", hair="bdc3c7", hat="tophat")
CROWD = [avatar((X - 10 + (i % 6) * 4 + random.uniform(-0.6, 0.6), -10 - (i // 6) * 4, 0), fdir(0, 1), shirt=random.choice(["e84a4a", "2fb3ff", "2ecc71", "f39c12", "9b59b6", "1abc9c"]), hair=random.choice(["1a1a1a", "4a2c17", "f1c40f"])) for i in range(12)]
HERO_MY = avatar((X + 2, -6, 0), fdir(0, 1), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
TOWER = empty((X, 110, 0))
cols_t = ["e74c3c", "e67e22", "f1c40f", "2ecc71", "3498db", "9b59b6"]
for i in range(40):
    box((0, 0, i * 9 + 4.5), (24 - i * 0.2, 24 - i * 0.2, 9), cols_t[i % 6], TOWER)
    box((0, -12.2 + i * 0.1, i * 9 + 4.5), (6, 0.4, 5), "111111", TOWER)
box((0, -12.4, 30), (30, 0.6, 6), "111111", TOWER); text("TOWER OF DOOM", (0, -12.8, 30), 3.6, "ff3b30", TOWER, emit=4.0)
PRIZE = empty((X, -2, 14))
text("1,000,000 R$", (0, 0, 0), 2.6, "2ecc71", PRIZE, emit=2.0)
for (x, s) in ((X - 60, 2.5), (X + 70, 3)):
    cloud((x, 220, 70), s)

# ---------- tower base: line + fails (same world as mayor, near tower foot, different collection so mayor props hidden)
X = at("line", 1800)
box((X, 82, 0.06), (24, 0.8, 0.12), "ffffff")
LINEUP = [avatar((X - 7.5 + i * 5, 84, 0), fdir(0, 1) + math.pi, shirt=c, pants=p, hair=h, hat=hat, shades=s, scale=sc)
          for i, (c, p, h, hat, s, sc) in enumerate((("e84a4a", "1f1f1f", "1a1a1a", "cap", False, 1), ("2fb3ff", "ffffff", "f1c40f", None, True, 1), ("2ecc71", "27ae60", "7a4a24", None, False, 2.2), ("8f8f8f", "5a4a3a", "4a2c17", None, False, 1)))]
# fails share
CUR[0] = "fails"
# stage 1 obstacles in front of tower door
LASERS = [box((X, 96, 9 + i * 2.2), (24, 0.4, 0.4), "ff2d2d", emit=8.0) for i in range(4)]
for sx in (-1, 1): box((X + 12.5 * sx, 96, 9), (1, 1, 18), "2d3436")
box((X, 93, 0.04), (24, 6, 0.08), "ff6b1a", emit=5.0)
_lava_l = bpy.data.lights.new("lava", "AREA"); _lava_l.energy = 3000; _lava_l.color = (1, 0.45, 0.12); _lava_l.size = 20
_ll = bpy.data.objects.new("lava", _lava_l); col(CUR[0]).objects.link(_ll); _ll.location = (X, 93, 0.6)
box((X, 93, 0.1), (24.4, 6.4, 0.05), "c0392b")
DOOR_W = empty((X + 6, 98.6, 0))
box((-2.2, 0, 4), (1.4, 1.2, 8), "2d3436", DOOR_W); box((2.2, 0, 4), (1.4, 1.2, 8), "2d3436", DOOR_W); box((0, 0, 8.6), (5.8, 1.2, 1.2), "2d3436", DOOR_W)
F_FLY = [avatar((X - 6 + i * 3, 86, 0), fdir(0, 1), shirt=c, pants="1f1f1f", hair="1a1a1a", hat="cap") for i, c in enumerate(("e84a4a", "c0392b"))]
F_SPD = [avatar((X - 1 + i * 3, 86, 0), fdir(0, 1), shirt=c, pants="ffffff", hair="f1c40f", shades=True) for i, c in enumerate(("2fb3ff", "0984e3"))]
F_GNT = avatar((X + 6, 86, 0), fdir(0, 1), shirt="2ecc71", pants="27ae60", hair="7a4a24", scale=2.6)
STAR_B = [text("BONK", (X, 95, 14), 2.2, "ffffff") for _ in range(1)]
OOF = [text("OOF", (X, 93, 4), 1.8, "ffffff") for _ in range(2)]

# ---------- climb + clouds + top (tower exterior obby)
X = at("climb", 2400)
TWR2 = empty((X, 0, 0))
for i in range(60):
    box((0, 0, i * 10 + 5), (14, 14, 10), cols_t[i % 6], TWR2)
# spiral platforms path
PLAT = []
for i in range(80):
    a = i * 0.62
    r = 12.5
    z = 2 + i * 2.2 + (i ** 1.6) * 0.18
    p = (X + r * math.cos(a), r * math.sin(a), z)
    PLAT.append(p)
    box(p, (3.2, 3.2, 0.8), cols_t[(i + 2) % 6])
    if i % 5 == 3:
        box((p[0], p[1], p[2] + 0.5), (3.2, 0.5, 0.25), "ff2d2d")
HERO_C = avatar((X, 0, 0), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
JUMPTXT = text("/jump", (0, 0, 0), 1.0, "ffffff")
CUR[0] = "clouds"
CLOUDS = [cloud((X + random.uniform(-60, 60), random.uniform(-60, 60), 260 + random.uniform(-25, 25)), random.uniform(1.6, 3.0)) for _ in range(16)]
PLANE = empty((X, 0, 0))
box((0, 0, 0), (2.4, 12, 2.4), "ecf0f1", PLANE); box((0, 0, 0), (16, 3, 0.4), "bdc3c7", PLANE); box((0, 5, 1.6), (0.4, 2.5, 3), "e74c3c", PLANE)
box((0, 5, 0.3), (6, 2, 0.3), "bdc3c7", PLANE); box((0, -5.6, 0.6), (1.6, 1.4, 1), "2d3436", PLANE)
PILOT_B = bubble("what", (0, -5.6, 3.2), PLANE)
CUR[0] = "top"
TOPZ = 640
box((X, 0, TOPZ - 5), (30, 30, 10), "2d3436")
OWNDOOR = empty((X, 6, TOPZ))
box((0, 0, 4.5), (8, 2, 9), "111111", OWNDOOR); box((0, -1.05, 3.6), (4, 0.2, 7.2), "6c5ce7", OWNDOOR)
box((0, -1.2, 8.4), (6.4, 0.2, 1.4), "ffffff", OWNDOOR); text("OWNER ONLY", (0, -1.35, 8.4), 0.95, "111111", OWNDOOR)
HERO_TOP = avatar((X, -8, TOPZ), fdir(0, 1), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
CUR[0] = "topclouds"
for _ in range(10):
    cloud((X + random.uniform(-80, 80), random.uniform(-80, 80), TOPZ - 30 + random.uniform(-15, 5)), random.uniform(2, 3.5))

# ---------- room
X = at("room", 2800)
box((X, 0, -0.5), (30, 30, 1), "1e1e2a"); box((X, 10, 8), (30, 1, 16), "2a2a3a")
for sx in (-1, 1): box((X + 12 * sx, 0, 8), (1, 30, 16), "23232f")
box((X, 6, 2.2), (10, 4, 0.4), "3d3d4f"); box((X - 4, 6, 1), (0.5, 3.5, 2), "3d3d4f"); box((X + 4, 6, 1), (0.5, 3.5, 2), "3d3d4f")
box((X, 7.4, 5.2), (8, 0.5, 5), "111111")
SCREEN = box((X, 7.1, 5.2), (7.4, 0.1, 4.4), "1b6ef3", emit=3.5)
_scr_l = bpy.data.lights.new("scr", "AREA"); _scr_l.energy = 400; _scr_l.color = (0.35, 0.55, 1.0); _scr_l.size = 7
_sl = bpy.data.objects.new("scr", _scr_l); col(CUR[0]).objects.link(_sl); _sl.location = (X, 5.5, 5.2); _sl.rotation_euler = (math.radians(90), 0, 0)
_amb_l = bpy.data.lights.new("ramb", "POINT"); _amb_l.energy = 300; _amb_l.color = (0.7, 0.6, 1.0)
_al = bpy.data.objects.new("ramb", _amb_l); col(CUR[0]).objects.link(_al); _al.location = (X - 6, -6, 12)
SCR1 = [text("PLAYER:", (X, 6.95, 6.5), 0.55, "ffffff", font=FONTB, emit=2.0), text("BrokeKid_2014", (X, 6.95, 5.6), 0.8, "ffe066", font=FONTB, emit=2.5)]
SCR2 = [text("CONGRATS.", (X, 6.95, 4.4), 0.55, "ffffff", emit=2.0), text("You found the", (X, 6.95, 3.75), 0.45, "ffffff", emit=2.0), text("/dev", (X, 6.93, 3.0), 0.85, "2ecc71", emit=4.0)]
HERO_R = avatar((X, 1, 0), fdir(0, 1), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
box((X, 0, 1.2), (1, 1, 2.4), "3d3d4f")


# ================================================================== extra map detail
random.seed(21)
CUR[0] = "town"
for i in range(7):
    for sx in (-1, 1):
        lamp((SETX["town"] + 7.8 * sx, -2 + i * 18 + 9, 0))
        bush((SETX["town"] + 11.5 * sx, -5 + i * 18 + 12, 0), 0.9)
box((SETX["town"] - 8.5, 20, 0.6), (0.5, 3.6, 0.15), "8b5a2b", r=0.04)
CUR[0] = "spawn"
fence((SETX["spawn"] - 12, 10, 0), (SETX["spawn"] + 12, 10, 0), "a87443")
for k in range(5): bush((SETX["spawn"] + random.uniform(-14, 14), random.uniform(6, 18), 0), 0.8)
lamp((SETX["spawn"] - 7, -3, 0))
CUR[0] = "laugh"
for k in range(4): lamp((SETX["laugh"] + (-8 if k % 2 else 8), -4 + k * 9, 0))
for k in range(6): bush((SETX["laugh"] + random.choice([-11, 11]) + random.uniform(-1, 1), random.uniform(-6, 18), 0), 0.9)
CUR[0] = "school"
fence((SETX["school"] - 20, 19, 0), (SETX["school"] - 4, 19, 0), "ecf0f1")
for k in range(6): bush((SETX["school"] + random.uniform(-22, 22), random.uniform(14, 18), 0), 0.9)
box((SETX["school"] - 12, 6, 1.0), (6, 2.5, 0.3), "8b5a2b", r=0.08); box((SETX["school"] - 12, 6, 0.5), (0.4, 2.0, 1.0), "8b5a2b")
CUR[0] = "mayor"
for k in range(10): bush((SETX["mayor"] + random.uniform(-30, 30), random.uniform(-25, 70), 0), random.uniform(0.8, 1.3))
for k in range(8): lamp((SETX["mayor"] + (-14 if k % 2 else 14), -20 + k * 12, 0))
for k in range(6): tree((SETX["mayor"] + random.choice([-40, 40]) + random.uniform(-8, 8), random.uniform(-10, 120), 0), random.uniform(1.0, 1.6))
CUR[0] = "mine"
for k in range(5):
    box((SETX["mine"] + random.uniform(-12, 12), random.uniform(-4, 14), 0.9), (1.8, 1.8, 1.8), "8b5a2b", rot=(0, 0, random.random()), r=0.08)
for k in range(8):
    sph((SETX["mine"] + random.uniform(-14, 14), random.uniform(12, 20), random.uniform(2, 9)), (0.5, 0.3, 0.5), "2ecc71", emit=3.0)

def update(t):
    CAMTIME[0] = t
    shot, u = shot_at(t)
    apply_shot(shot, VIS_EXTRA)
    # reset common visibility
    if shot in ("town", "freeze"):
        do_town(t, u, shot)
    elif shot == "spawn": do_spawn(t, u)
    elif shot == "shop": do_shop(t, u)
    elif shot == "laugh": do_laugh(t, u)
    elif shot == "school": do_school(t, u)
    elif shot == "mine": do_mine(t, u)
    elif shot == "mayor": do_mayor(t, u)
    elif shot == "line": do_line(t, u)
    elif shot == "fails": do_fails(t, u)
    elif shot in ("climb", "clouds"): do_climb(t, u, shot)
    elif shot == "top": do_top(t, u)
    elif shot == "room": do_room(t, u)
    return shot

TF, TS, TG, TM = W(2, "fly"), W(2, "speed"), W(2, "giant"), W(3, "money")
def do_town(t, u, shot):
    X = SETX["town"]
    frozen = shot == "freeze"
    t_anim = t
    T_FROZE = W(26, "froze") if frozen else 1e9
    T_GONE = W(26, "disappeared") if frozen else 1e9
    if frozen:
        t_anim = min(t, T_FROZE)
    # flyer loops over street
    a = t_anim * 0.7
    FLYER["root"].location = (X + 6 * math.sin(a), 10 + 14 * math.cos(a * 0.8), 9 + 2 * math.sin(a * 1.3))
    FLYER["root"].rotation_euler = (-1.2, 0, fdir(math.cos(a), -math.sin(a * 0.8)))
    fly_pose(FLYER, t)
    # speeder dashes back and forth along street
    sp = ((t_anim * 0.9) % 2.0) / 2.0
    sy = lerp(-20, 60, sp)
    if TS - 0.1 <= t < TG - 0.1:
        sy = lerp(-14, 30, (t - (TS - 0.1)) / max(0.3, TG - TS))
    SPEEDER["root"].location = (X + 3.5, sy, 0)
    SPEEDER["root"].rotation_euler = (0.25, 0, fdir(0, 1))
    walk(SPEEDER, t_anim, 30, 1.0)
    for i, l in enumerate(SPEED_LINES):
        l.location = (X + 3.5 + (i - 2.5) * 0.5, sy - 4 - (i % 3) * 1.5, 1 + (i % 4) * 1.1)
    # giant walks slowly
    GIANT["root"].location = (X + 26, 30 + math.sin(t_anim * 0.25) * 8, 0)
    GIANT["root"].rotation_euler = (0, 0, fdir(0, math.cos(t_anim * 0.25)))
    walk(GIANT, t_anim, 3, 0.4)
    # rich money kid + gold rain
    RICH["root"].location = (X + 4, 56, 0)
    pose(RICH, arms=(-2.8, -2.8), arms_out=(0.4, 0.4))
    random.seed(9)
    for i, g in enumerate(GOLD):
        x0 = X + 4 + random.uniform(-6, 6); y0 = 56 + random.uniform(-4, 4); ph = random.random()
        z = 22 - ((t_anim * 0.6 + ph) % 1.0) * 22
        g.location = (x0, y0, max(0.4, z)); g.rotation_euler = (t_anim * 2 + i, t_anim + i, 0)
    for i, k in enumerate(TOWN_KIDS):
        k["root"].location.z = 0
        if i % 2 == 0: walk(k, t_anim + i, 8, 0.5); k["root"].location.y = 4 + (i // 4) * 6 + math.sin(t_anim * 0.5 + i) * 2
        else: idle(k, t_anim, i)
        set_mouth(k, "smile")
    H = HERO_T
    H["root"].location = (X - 3, -12, 0.4)
    idle(H, t_anim)
    set_mouth(H, "flat")
    for o in (FLYER, SPEEDER, GIANT, RICH, *TOWN_KIDS):
        hide(o["root"], t >= T_GONE)
    for g in GOLD + SPEED_LINES:
        g.hide_render = t >= T_GONE
    if frozen:
        k = ease((u) / 2.0)
        cam(vl((X - 1, -24, 4), (X - 2, -20, 3.5), k), (X - 3, -12, 3.5), 26)
        if t >= T_GONE:
            v = t - T_GONE
            cam(vl((X - 3, -21, 3.8), (X - 3, -32, 12), ease(v / 3.5)), (X - 3, -10, 3), 26)
        return
    if t < TF - 0.15:
        k = ease(t / (TF - 0.15))
        cam(vl((X + 2, -28, 3), (X - 1, -30, 8), k), vl((X, 10, 5), (X, 20, 8), k), 24)
    elif t < TS - 0.1:
        p = FLYER["root"].location
        cam(Vector(p) + Vector((9, -13, -1)), p, 28)
    elif t < TG - 0.1:
        p = SPEEDER["root"].location
        cam((X + 9, p.y - 7, 3), (p.x, p.y + 1, 2.4), 28)
    elif t < TM - 0.6:
        p = GIANT["root"].location
        cam((X + 4, p.y - 34, 10), (p.x, p.y, 10), 26)
    else:
        v = t - (TM - 0.6)
        cam(vl((X - 6, 30, 5), (X - 2, 36, 6), ease(v / 3)), (X + 4, 58, 9), 26)

def do_spawn(t, u):
    X = SETX["spawn"]
    H = HERO_S
    H["root"].location = (X, 0.6, 1.45)
    pose(H, legs=(-1.5, -1.5), arms=(-0.3, -0.3), head=(0.25, 0, 0), knees=(0.15, 0.1), lean=0.15)
    H["root"].location.z = 0.25
    blink(H, t)
    set_mouth(H, "sad")
    s5 = S(5) - shot_start("spawn")
    for i, (n, fl) in enumerate(zip(NEWB, SPAWN_FLASH)):
        ts = s5 + 0.5 + i * 0.9
        if u < ts:
            hide(n["root"]); fl.hide_render = True; continue
        hide(n["root"], False)
        v = u - ts
        z = max(1.95, 9 - 30 * v * v)
        landed = z <= 1.96
        n["root"].location = (X + (i - 1.5) * 0.6, 0.4 + (i % 2) * 0.5, z + (i * 0.0))
        if landed:
            n["root"].location.z = 1.95
            pose(n, arms=(-0.4, 0.3), legs=(0, 0))
            set_mouth(n, "open")
        else:
            jump_pose(n)
        fl.hide_render = v > 0.25
        fl.location = (X + (i - 1.5) * 0.6, 0.4, 3)
        s = 2 + v * 20
        fl.scale = (s, s, 0.2)
        if v > 0.2:
            set_mouth(H, "open")
    if u < s5:
        k = ease(u / s5)
        cam(vl((X + 9, -20, 9), (X + 4, -12, 5), k), (X, 1, 2), 28)
    else:
        v = u - s5
        cam(vl((X + 5, -11, 4), (X + 3, -9, 4.5), ease(v / 4)), (X, 0.8, 2.6), 30)

def do_shop(t, u):
    X = SETX["shop"]
    T7 = S(7) - 0.15
    H = HERO_SH
    if t < S(6) + 1.2:
        k = ease((t - shot_start("shop")) / 1.4)
        H["root"].location = (X - 2, lerp(-2, 2.2, k), 0)
        walk(H, t, 9, 0.6 * (1 - k))
    else:
        H["root"].location = (X - 2, 2.2, 0); idle(H, t)
    set_mouth(H, "smile" if t < T7 else "flat")
    idle(KEEPER, t, 1)
    pose(KEEPER, arms=(-1.4 if t > T7 - 0.4 else 0, 0), head=(0, 0, 0))
    if t < T7:
        JCARD.location = (X + 2, 7.6, 4.0); JCARD.scale = (0.001,) * 3
    else:
        v = t - T7
        k = ease(v / 0.5)
        JCARD.location = (X + lerp(2, -0.5, k), lerp(7.6, 3.6, k), lerp(4.0, 6.2, k) + math.sin(v * 3) * 0.15)
        JCARD.scale = (lerp(0.3, 1.0, k),) * 3
        JCARD.rotation_euler = (0, 0, (1 - k) * 6.28 + math.sin(v * 2) * 0.1)
    if t < T7 - 0.1:
        k = ease(u / max(0.5, T7 - shot_start("shop")))
        cam(vl((X - 9, -14, 9), (X - 6, -10, 7), k), vl((X, 14, 8), (X, 10, 6), k), 26)
    else:
        v = t - T7
        cam(vl((X - 2.5, -3.5, 6.6), (X - 1.6, -2.2, 6.4), ease(v / 1.5)), (X - 0.5, 3.6, 6.1), 32)

def do_laugh(t, u):
    X = SETX["laugh"]
    H = HERO_L
    idle(H, t); pose(H, head=(0.3, 0, 0)); set_mouth(H, "sad")
    for i, a in enumerate(LAUGHERS):
        laugh(a, t, i * 1.1)
    TL_ = W(8, "l") - shot_start("laugh")
    for i, b in enumerate(BUBS):
        ts = 0.4 + i * 0.45 if i < 2 else TL_ + (i - 2) * 0.12
        hide(b, u < ts)
        if u >= ts:
            k = min(1.0, (u - ts) / 0.12) * 1.6; b.scale = (k, k, k)
    k = ease(u / 5.0)
    cam(vl((X + 1.5, -8, 6), (X + 0.5, -5.5, 7), k), (X, 7, 6.5), 26)

def do_school(t, u):
    X = SETX["school"]
    T_STUD = W(9, "stud")
    T_USED = W(9, "used")
    s10 = S(10)
    for i, k in enumerate(LINE_KIDS): idle(k, t, i)
    idle(LADY, t, 2)
    H = HERO_SC
    H["root"].location = (X + 6, -3, 0)
    # flyers arc over the line
    for i, f in enumerate(SC_FLYERS):
        ts = shot_start("school") + 1.0 + i * 0.8
        v = max(0, t - ts) / 2.4
        y = lerp(-14, 22, min(1, v))
        f["root"].location = (X + 6 + (i - 0.5) * 2, y, 3 + 9 * math.sin(min(1, v) * math.pi))
        f["root"].rotation_euler = (-1.1, 0, fdir(0, 1))
        fly_pose(f, t)
        hide(f["root"], t < ts or v >= 1)
    if t >= T_USED - 0.1:
        v = t - (T_USED - 0.1)
        z = 0.5 * 4 * min(1, v / 0.5) * (1 - min(1, v / 0.5)) if v < 0.5 else 0
        H["root"].location.z = z
        if v < 0.5: jump_pose(H)
        else: idle(H, t)
    else:
        idle(H, t)
    set_mouth(H, "flat")
    hide(PIZZA, t < s10)
    for k_ in LINE_KIDS: hide(k_["root"], t >= s10)
    PIZZA_LBL.hide_render = t < W(10, "decal") - 0.1
    if t < s10:
        k = ease(u / 3.5)
        cam(vl((X - 14, -18, 5), (X - 12, -16, 10), k), (X + 6, 4, 5), 24)
        if t > T_USED - 0.4:
            cam((X - 3, -1.5, 2.8), (X + 6, -3, 2.2), 30)
    else:
        v = t - s10
        H["root"].location = (X + 6, 9.5, 0)
        H["root"].rotation_euler = (0, 0, fdir(0.3, 1))
        pose(H, arms=(-1.4, 0), head=(0.15, 0, 0))
        hp = Vector((X + 5.2, 8.0, 3.3))
        PIZZA.location = hp + Vector((0, 0, 0.9))
        PIZZA.rotation_euler = (0, 0, 0.1)
        PIZZA_LBL.location = hp + Vector((0, -0.3, -0.1))
        PIZZA_LBL.rotation_euler = (math.radians(90), 0, 0)
        cam(vl((X + 3.5, 2.5, 5.5), (X + 4.2, 4.0, 5.0), ease(v / 3)), (X + 5.4, 8.6, 4.1), 32)

def do_mine(t, u):
    X = SETX["mine"]
    s12 = S(12)
    H = HERO_M
    idle(H, t); set_mouth(H, "flat")
    D = DAD
    if t < s12:
        D["root"].rotation_euler = (0, 0, fdir(-1, -0.3))
        idle(D, t, 0.5)
        pose(D, arms=(-0.5 + math.sin(t * 3) * 0.2, 0), head=(0, 0, 0))
        set_mouth(D, "smile")
        COIN.scale = (0.001,) * 3
        k = ease(u / 4)
        cam(vl((X - 9, -6, 4.5), (X - 7, -4, 4.2), k), (X - 2.2, 5.2, 4.5), 26)
    else:
        v = t - s12
        D["root"].rotation_euler = (0, 0, fdir(1, 0.6))
        sw = (v * 1.6) % 1.0
        ang = -2.9 + 2.2 * (sw ** 0.5 if sw < 0.7 else 1 - (sw - 0.7) / 0.3)
        pose(D, arms=(-0.3, ang), head=(0.1, 0, 0))
        set_mouth(D, "flat")
        T1 = W(12, "earned")
        if t >= T1:
            w = t - T1
            COIN.scale = (min(1, w / 0.2),) * 3
            COIN.location = (X + 4, 7.0, 3 + w * 1.2)
            COIN.rotation_euler = (0, 0, w * 3)
        else:
            COIN.scale = (0.001,) * 3
        cam(vl((X - 6, -6, 5), (X - 4, -3, 6), ease(v / 4.5)), (X + 3, 8, 3.5), 26)

def do_mayor(t, u):
    X = SETX["mayor"]
    idle(MAYOR, t)
    pose(MAYOR, arms=(-2.2 + math.sin(t * 4) * 0.3, 0), arms_out=(0.3, 0))
    set_mouth(MAYOR, "open" if int(t * 6) % 2 else "smile")
    for i, c in enumerate(CROWD): idle(c, t, i)
    idle(HERO_MY, t)
    s14 = S(14)
    if t < W(13, "doom") - 0.3:
        k = ease(u / 2.4)
        cam(vl((X + 8, -26, 5), (X + 6, -22, 5), k), (X, 0, 5.5), 28)
    elif t < s14:
        v = t - (W(13, "doom") - 0.3)
        cam(vl((X + 10, -40, 4), (X + 4, -46, 6), ease(v / 3.5)), vl((X, 110, 40), (X, 110, 140), ease(v / 3.5)), 24)
    else:
        v = t - s14
        PRIZE.scale = (min(1, v / 0.25),) * 3
        cam((X + 1, -16, 8), (X, 0, 10), 26)
    hide(PRIZE, t < s14)

def do_line(t, u):
    X = SETX["mayor"]
    for i, a in enumerate(LINEUP):
        idle(a, t, i)
        a["root"].rotation_euler = (0, 0, fdir(0, 1))
    set_mouth(LINEUP[3], "flat")
    tw = [W(15, "fly"), W(15, "speed"), W(15, "giant"), W(15, "and")]
    idx = sum(1 for x in tw if t >= x - 0.1) - 1
    if idx < 0:
        k = ease(u / 2.2)
        cam(vl((X + 5, 97, 10), (X + 3, 96, 9), k), (X, 84, 4), 24)
    else:
        a = LINEUP[idx]
        p = Vector(a["root"].location)
        hgt = 4.5 * (2.2 if idx == 2 else 1)
        off = Vector((5.0, 11.0, hgt * 0.55)) if idx == 2 else Vector((2.0, 7.0, hgt * 0.75))
        cam(p + off, p + Vector((0, 0, hgt * 0.85)), 30 if idx != 2 else 24)

def do_fails(t, u):
    X = SETX["mayor"]
    TB = W(16, "bonk")
    TLV = W(17, "lava")
    TG_ = W(17, "giant")
    TD = W(17, "door")
    # flyers rise into lasers then fall
    for i, f in enumerate(F_FLY):
        ts = shot_start("fails") + 0.6 + i * 0.25
        v = max(0, t - ts)
        if t < TB - 0.05:
            z = min(9.5, v * 5); y = 86 + min(9.5, v * 4)
            f["root"].location = (X - 6 + i * 3, y, z)
            f["root"].rotation_euler = (-0.9, 0, fdir(0, 1)); fly_pose(f, t)
        else:
            w = t - (TB - 0.05)
            f["root"].location = (X - 6 + i * 3, 95.5 - w * 2, max(0.5, 9.5 - 18 * w * w))
            f["root"].rotation_euler = (-0.9 + w * 6, w * 3, fdir(0, 1)); pose(f, arms=(-2.5, 2.0), legs=(0.8, -0.8))
            hide(f["root"], w > 1.3)
    for i, s in enumerate(F_SPD):
        ts = TLV - 0.7 + i * 0.1
        v = max(0, t - ts)
        y = min(93.0, 86 + v * 9)
        z = -min(6, max(0, v - 0.6) * 3.0)
        s["root"].location = (X - 1 + i * 3, y, z)
        s["root"].rotation_euler = (0.25, 0, fdir(0, 1)); walk(s, t, 30, 1.0)
        hide(s["root"], z < -5)
    for i, o in enumerate(OOF):
        o.hide_render = t < TLV or t > TLV + 1.2
        o.location = (X - 1 + i * 3, 92, 3 + (t - TLV) * 2)
    STAR_B[0].hide_render = not (TB <= t < TB + 1.0)
    STAR_B[0].scale = (1 + (t - TB) * 0.6,) * 3 if t >= TB else (1, 1, 1)
    STAR_B[0].location = (X - 4.5, 95, 12)
    # giant walks into door and gets stuck
    G = F_GNT
    if t < TG_:
        G["root"].location = (X + 6, 86, 0); idle(G, t)
    else:
        v = t - TG_
        y = min(97.0, 86 + v * 6)
        G["root"].location = (X + 6, y, 0)
        stuck = y >= 97.0
        walk(G, t, 6 if not stuck else 20, 0.5 if not stuck else 0.25)
        if stuck:
            G["root"].location.x = X + 6 + math.sin(t * 25) * 0.15
            set_mouth(G, "open")
    if t < S(17):
        k = ease(u / 4)
        cam(vl((X - 16, 78, 6), (X - 14, 80, 9), k), (X - 3, 94, 8), 24)
    elif t < TG_ - 0.2:
        cam((X - 17, 88, 5), (X + 0.5, 92, 1.0), 28)
    else:
        v = t - (TG_ - 0.2)
        cam(vl((X + 18, 80, 8), (X + 16, 84, 10), ease(v / 2.5)), (X + 6, 96, 8), 26)

def hero_path(t):
    """hero hops platform to platform; returns pos, airborne"""
    s16 = shot_start("climb")
    v = max(0.0, t - s16)
    # jump rate accelerates
    n = v * 1.4 + (v ** 2) * 0.06
    i = int(n); f = n - i
    i = min(i, len(PLAT) - 2)
    a, b = Vector(PLAT[i]), Vector(PLAT[i + 1])
    hjump = 2.5 + i * 0.6
    p = a.lerp(b, f)
    p.z += 4 * f * (1 - f) * hjump + 0.4
    # pull a bit outward so he stands on outer edge
    return p, f, i

def do_climb(t, u, shot):
    X = SETX["climb"]
    H = HERO_C
    if shot == "clouds":
        s21 = shot_start("clouds")
        v = t - s21
        p = Vector((X - 20 + v * 9, -32, 262 + 14 * abs(math.sin(v * 1.5))))
        H["root"].location = p
        H["root"].rotation_euler = (0, 0, fdir(1, 0))
        jump_pose(H) if math.sin(v * 1.5 * 2) > -0.6 else idle(H, t)
        set_mouth(H, "smile")
        TPL = S(22)
        TWH = W(22, "what")
        PLANE.location = (p.x + 30 - max(0.0, t - (TWH - 1.4)) * 22, p.y + 9, p.z + 5)
        PLANE.rotation_euler = (0, 0, -math.pi / 2)
        PLANE.scale = (2.0, 2.0, 2.0)
        PILOT_B.parent = None
        PILOT_B.location = Vector(PLANE.location) + Vector((0, -3, 8))
        PILOT_B.rotation_euler = (0, 0, 0)
        PILOT_B.scale = (2.4, 2.4, 2.4)
        hide(PILOT_B, t < W(22, "what") - 0.2)
        JUMPTXT.hide_render = True
        for i, c in enumerate(CLOUDS):
            pass
        if t < TPL:
            cam(p + Vector((-4, -18, 2)), p + Vector((3, 0, 1)), 26)
        else:
            cam(p + Vector((-4, -24, 3)), (p + Vector(PLANE.location)) / 2, 24)
        return
    p, f, i = hero_path(t)
    H["root"].location = p
    nxt = Vector(PLAT[min(i + 1, len(PLAT) - 1)])
    H["root"].rotation_euler = (0, 0, fdir(nxt.x - p.x, nxt.y - p.y))
    if 0.08 < f < 0.92: jump_pose(H)
    else: idle(H, t)
    set_mouth(H, "smile")
    JUMPTXT.hide_render = True
    ang = math.atan2(p.y, p.x - X)
    rr = 24 + i * 0.15
    cam((X + rr * math.cos(ang - 0.3), rr * math.sin(ang - 0.3), p.z + 3 + i * 0.12), p + Vector((0, 0, 2.5)), 30)

def do_top(t, u):
    X = SETX["climb"]
    H = HERO_TOP
    T_OWN = W(23, "owner")
    k = ease(u / 3.0)
    H["root"].location = (X, lerp(-12, 3.5, k), TOPZ)
    walk(H, t, 8, 0.6 * (1 - k)) if k < 1 else idle(H, t)
    if u < 1.6:
        H["root"].location.z = TOPZ + max(0, 6 - u * 8) if u < 0.75 else TOPZ
        if u < 0.75: jump_pose(H)
    set_mouth(H, "flat")
    if t < T_OWN - 0.6:
        cam(vl((X + 14, -30, TOPZ + 10), (X + 8, -22, TOPZ + 8), ease(u / 3)), (X, 2, TOPZ + 4), 26)
    else:
        v = t - (T_OWN - 0.6)
        cam(vl((X + 2.5, -4, TOPZ + 6), (X + 1.5, -1, TOPZ + 7.5), ease(v / 2)), (X, 4.9, TOPZ + 8.0), 30)

def do_room(t, u):
    X = SETX["room"]
    H = HERO_R
    idle(H, t); set_mouth(H, "flat" if t < S(25) else "open")
    for o in SCR1: o.hide_render = t < W(24, "username") - 0.8
    for i, o in enumerate(SCR2):
        o.hide_render = t < S(25) + 1.0 + i * 0.6
    if t < S(24) + 2.0:
        cam(vl((X + 5, -10, 7.5), (X + 3, -7, 7), ease(u / 2)), (X, 6, 5), 26)
    else:
        v = t - (S(24) + 2.0)
        cam(vl((X + 2.6, -0.5, 6.6), (X + 2.0, 1.2, 6.2), ease(v / 6)), (X, 7, 5.0), 30)


if __name__ == "__main__":
    run(update, VIS_EXTRA)
