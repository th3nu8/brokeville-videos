"""Explainer E002 — How an elevator stops itself from falling. Building cutaway: section plane at y=0, camera in front (y<0).
Shaft in the middle, office floors on both sides, machine room on the roof, pit below ground."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pipeline"))
from lib import *
from bpy_extras.object_utils import world_to_camera_view

SHOTS_ = ("hook", "shaft", "car", "ropes", "machine", "counter", "brake", "governor", "safeties", "buffer", "otis")
SHOT_LIGHT = {s: "day" for s in SHOTS_}
SHOT_FSTOP = {"hook": 5.6, "shaft": 8.0, "car": 4.0, "ropes": 5.6, "machine": 4.0, "counter": 8.0, "brake": 2.8, "governor": 4.0,
              "safeties": 2.8, "buffer": 3.5, "otis": 5.6}
VIS_EXTRA = {s: {"site"} for s in SHOT_LIGHT}
setup_shots(SHOT_LIGHT, SHOT_FSTOP)
LIGHTS["day"] = ("3a86d8", "d6ecff", "c8dcf5", 0.9, 4.0, "fff2e0", (math.radians(50), math.radians(8), math.radians(-24)))

M_U = rbox_mesh(1, 1, 1, r=0)
def ubox(x0, x1, y0, y1, z0, z1, color, rough=0.85, **k):
    o = obj(M_U, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), color, rough=rough, **k)
    o["ext"] = (x0, x1, y0, y1, z0, z1)
    return o
def set_ext(o, x0, x1, y0, y1, z0, z1):
    if z1 - z0 < 0.002 or x1 - x0 < 0.002 or y1 - y0 < 0.002:
        o.hide_render = True; return
    o.hide_render = False
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); o.scale = (x1 - x0, y1 - y0, z1 - z0)
def seg(o, p0, p1, r):
    """place a unit cylinder o between two points (vertical or horizontal in xz)"""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length
    if L < 0.01: o.hide_render = True; return
    o.hide_render = False
    o.location = (p0 + p1) / 2; o.scale = (r * 2, r * 2, L)
    o.rotation_euler = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler()

# ---------------------------------------------------------------- timeline (from narration)
T_WALL0, T_WALL1 = W(2, "first"), W(2, "rails")
T_RAIL0, T_RAIL1 = W(2, "guide"), S(3) - 0.1
T_CAR0, T_CAR1 = S(3) + 0.1, W(3, "rails") + 0.2
T_ROPE0, T_ROPE1 = W(4, "several"), W(4, "and")
T_ONE = W(4, "one")
T_MOTOR, T_TURN = W(5, "motor") - 0.1, W(5, "turns")
T_CW0, T_CW1 = S(6) - 0.05, W(6, "balances") + 0.1
T_RISE0, T_RISE1 = W(6, "balances") + 0.2, S(7) - 0.15
T_PWR = W(7, "power") + 0.25
T_CLAMP0, T_CLAMP1 = W(7, "springs"), W(7, "clamp") + 0.25
T_GOV = W(8, "governor") - 0.1
T_UP0, T_UP1 = W(8, "spun"), S(9) - 0.05
T_FAST0 = W(9, "car")
T_GRAB = W(9, "grabs")
T_WEDGE = W(10, "tight")
T_BUF0, T_BUF1 = W(11, "buffers") - 0.4, W(11, "act")
T_CUT = W(12, "cut")

def keyz(t, keys):
    """piecewise eased car height"""
    if t <= keys[0][0]: return keys[0][1]
    for (a, za), (b, zb) in zip(keys[:-1], keys[1:]):
        if a <= t <= b: return lerp(za, zb, ease((t - a) / max(0.01, b - a)))
    return keys[-1][1]
Z_TOP_DROP, Z_GROUND, Z_MID, Z_UP, Z_STOP = 7.0, 0.25, 8.25, 11.0, 6.4
def fall_z(t):
    u = max(0.0, min(1.0, (t - T_FAST0) / (T_WEDGE - T_FAST0)))
    f = 0.85 * (u / 0.75) ** 2 if u < 0.75 else 0.85 + 0.15 * (1 - (1 - (u - 0.75) / 0.25) ** 2)
    return lerp(Z_UP, Z_STOP, f)
def car_z(t):
    shot, u = shot_at(t)
    if shot == "hook": return 12.25
    if t < T_RISE1 + 0.01:
        return keyz(t, [(T_CAR0, Z_TOP_DROP), (T_CAR1, Z_GROUND), (T_RISE0, Z_GROUND), (T_RISE1, Z_MID)])
    if t < T_FAST0:
        return keyz(t, [(T_UP0, Z_MID), (T_UP1, Z_UP)])
    return fall_z(t)

def stage(t):
    shot, u = shot_at(t)
    fin = shot == "hook"
    def k(a, b):
        return 1.0 if fin else ease((t - a) / max(0.01, b - a))
    def on(a):
        return fin or t >= a
    return dict(fin=fin, wall=k(T_WALL0, T_WALL1), rail=k(T_RAIL0, T_RAIL1), car=on(T_CAR0 - 0.05), rope=k(T_ROPE0, T_ROPE1),
                motor=on(T_MOTOR), cw=on(T_CW0), gov=on(T_GOV), buf=k(T_BUF0, T_BUF1), cut=(not fin) and t >= T_CUT)

# ---------------------------------------------------------------- world
CUR[0] = "site"
LV = [0, 4, 8, 12, 16, 20, 24]
BXW = 11.0                 # building half width
BY = 9.0                   # building depth
SX0, SX1, SY1 = -3.2, 3.2, 3.6      # shaft interior
ST = 0.3
PITZ = -2.3
# ground + earth section
STRATA = [(0.0, -0.6, "5b3c22"), (-0.6, -2.8, "8b5a33"), (-2.8, -5.0, "a77f4e")]
def earth(x0, x1, y0, y1, ztop=0.0, zbot=-5.0):
    for a, b, c in STRATA:
        top, bot = min(a, ztop), max(b, zbot)
        if top > bot: ubox(x0, x1, y0, y1, bot, top, c)
earth(-34, SX0 - ST, 0, 40); earth(SX1 + ST, 34, 0, 40); earth(SX0 - ST, SX1 + ST, SY1 + ST, 40)
earth(SX0 - ST, SX1 + ST, 0, SY1 + ST, PITZ - 0.3, -5.0)
ubox(-34, -BXW, 0, 40, 0, 0.12, "4e9a3c", rough=0.9); ubox(BXW, 34, 0, 40, 0, 0.12, "4e9a3c", rough=0.9)
ubox(-BXW, BXW, BY + 0.3, 40, 0, 0.12, "4e9a3c", rough=0.9)
ubox(-BXW - 1.2, SX0 - ST, 0.0, 1.0, 0.0, 0.14, "b8b3a8", rough=0.8); ubox(SX1 + ST, BXW + 1.2, 0.0, 1.0, 0.0, 0.14, "b8b3a8", rough=0.8)
random.seed(3)
for i in range(40):
    x = random.uniform(-33, 33)
    if -4.0 < x < 4.0: continue
    sph((x, -0.02, random.uniform(-4.6, -0.8)), (random.uniform(0.15, 0.4), 0.12, random.uniform(0.12, 0.28)), random.choice(["6a6158", "8d8378", "a39782"]), rough=0.8)
for i in range(10):
    tree((random.choice([random.uniform(-30, -14), random.uniform(14, 30)]), random.uniform(4, 30), 0.1), random.uniform(0.5, 0.8))
for (x, y, z, s) in ((-18, 60, 30, 2.4), (16, 70, 36, 2.8), (2, 90, 44, 3.2)):
    cloud((x, y, z), s)

# building wings: slabs, back wall, outer walls, rooms
SLAB = "b9b6ae"
ROOMC = ["e9e1d3", "d8e6ef", "efe0d0", "dfe9d9", "ece4ef", "f0e7cf"]
for side in (-1, 1):
    xa, xb = (-BXW, SX0 - ST) if side < 0 else (SX1 + ST, BXW)
    for i, L in enumerate(LV):
        ubox(xa, xb, 0, BY + 0.3, L - 0.35, L, SLAB, rough=0.8)
        if L < 24:
            ubox(xa, xb, BY, BY + 0.3, L, L + 4 - 0.35, ROOMC[(i + (side > 0)) % 6], rough=0.9)       # back wall
            ubox(xa + 0.8, xb - 0.8, BY - 0.02, BY, L + 1.0, L + 2.8, "a9d6f5", rough=0.15, emit=0.25)  # window
            ox = xa if side < 0 else xb - 0.3
            ubox(ox, ox + 0.3, 0, BY + 0.3, L, L + 4 - 0.35, "cfc8bc")                                  # outer wall
            ubox(xa + 0.2, xb - 0.2, 0, BY, L, L + 0.04, ["8a6b4f", "7d8794", "a58a6a"][i % 3], rough=0.6)  # floor finish
            # furniture
            random.seed(10 + i * 2 + (side > 0))
            cx = (xa + xb) / 2 + random.uniform(-1.2, 1.2)
            box((cx, 5.5, L + 0.8), (2.2, 1.0, 0.08), "8b5a2b", r=0.02)
            for sx in (-1, 1): box((cx + sx * 1.0, 5.5, L + 0.4), (0.08, 0.9, 0.8), "6b4220")
            box((cx, 5.7, L + 1.15), (0.8, 0.06, 0.5), "2d3436", r=0.02)
            box((cx, 5.66, L + 1.15), (0.7, 0.02, 0.4), "7fd0ff", emit=1.2)
            box((cx, 4.6, L + 0.5), (0.6, 0.6, 0.1), "34495e", r=0.04); box((cx, 4.9, L + 0.85), (0.6, 0.1, 0.7), "34495e", r=0.04)
            px = xa + 1.0 if side < 0 else xb - 1.0
            cyl((px, 7.8, L + 0.3), (0.6, 0.6, 0.6), "c0643b"); sph((px, 7.8, L + 1.0), (1.0, 1.0, 1.2), "2f9e44", rough=0.8)
            if random.random() < 0.6:
                sx_ = xb - 2.2 if side < 0 else xa + 2.2
                box((sx_, 2.2, L + 0.35), (1.4, 0.8, 0.5), random.choice(["c0392b", "2980b9", "16a085"]), r=0.12, rough=0.8)
    ubox(xa, xb, 0, 0.3, 24, 24.8, "cfc8bc")                     # parapet front
    ubox(xa, xb, BY, BY + 0.3, 24, 24.8, "cfc8bc")
# shaft walls (grow)
SHW = [ubox(SX0 - ST, SX1 + ST, SY1, SY1 + ST, PITZ - 0.3, 24.0, "a9a8a2"), ubox(SX0 - ST, SX0, 0, SY1, PITZ - 0.3, 24.0, "a9a8a2"),
       ubox(SX1, SX1 + ST, 0, SY1, PITZ - 0.3, 24.0, "a9a8a2")]
for o in SHW: o["full"] = o["ext"]
PITFLOOR = ubox(SX0, SX1, 0, SY1, PITZ - 0.3, PITZ, "8f8e88")
# shaft cap / machine room floor, with rope holes
CAP = [ubox(SX0 - ST, -3.05, 0, SY1 + ST, 24.0, 24.4, SLAB), ubox(-2.25, -1.0, 0, SY1 + ST, 24.0, 24.4, SLAB),
       ubox(2.35, SX1 + ST, 0, SY1 + ST, 24.0, 24.4, SLAB), ubox(-1.0, 2.35, 2.4, SY1 + ST, 24.0, 24.4, SLAB),
       ubox(-1.0, 2.35, 0, 1.0, 24.0, 24.4, SLAB), ubox(-3.05, -2.25, 0.8, SY1 + ST, 24.0, 24.4, SLAB)]
# machine room
MRX0, MRX1 = -4.0, 4.0
ubox(MRX0, MRX1, 4.2, 4.5, 24.4, 28.6, "d9d2c4"); ubox(MRX0 - 0.3, MRX0, 0, 4.5, 24.4, 28.6, "d9d2c4"); ubox(MRX1, MRX1 + 0.3, 0, 4.5, 24.4, 28.6, "d9d2c4")
ubox(MRX0 - 0.3, MRX1 + 0.3, 0, 4.5, 28.6, 29.0, SLAB)
ubox(-1.2, 1.2, 4.18, 4.2, 25.0, 27.4, "5d6d7e", rough=0.5)        # back door
_ml = bpy.data.lights.new("mrl", "POINT"); _ml.energy = 500; _ml.color = (1.0, 0.92, 0.8); _ml.shadow_soft_size = 1.0
MRL = bpy.data.objects.new("mrl", _ml); col("site").objects.link(MRL); MRL.location = (-1.5, 1.5, 28.2)
MR_LAMP = ubox(-2.3, -0.7, 1.2, 1.8, 28.5, 28.58, "fff3d6", emit=5.0)
# shaft fill light (follows the car)
_sl = bpy.data.lights.new("shl", "POINT"); _sl.energy = 300; _sl.color = (1.0, 0.95, 0.88); _sl.shadow_soft_size = 2.0
SHL = bpy.data.objects.new("shl", _sl); col("site").objects.link(SHL)

# ---------------------------------------------------------------- rails
CX, CY = -0.7, 1.7            # car centre
CWX, CWY = 2.0, 1.7           # counterweight centre
RAILX = [CX - 1.45, CX + 1.45]
CWRAILX = [CWX - 0.8, CWX + 0.8]
RAILS = []
for x in RAILX:
    RAILS.append(ubox(x - 0.07, x + 0.07, CY - 0.15, CY + 0.15, PITZ, 24.0, "9aa3ad", rough=0.3, metal=0.85))
for x in CWRAILX:
    RAILS.append(ubox(x - 0.05, x + 0.05, CWY - 0.1, CWY + 0.1, PITZ, 24.0, "8d96a0", rough=0.3, metal=0.85))
for o in RAILS: o["full"] = o["ext"]
BRACK = [box((x, CY + 1.0, z), (0.12, 1.9, 0.12), "6f7984", metal=0.6) for x in RAILX for z in range(0, 24, 3)]

# ---------------------------------------------------------------- car
CAR = empty((CX, CY, Z_GROUND))
STEEL = "4a5560"
box((0, 0, 0.1), (2.4, 2.6, 0.2), "3b4048", CAR, r=0.03, metal=0.5)
box((0, 1.25, 1.45), (2.4, 0.1, 2.5), "c9a27a", CAR, r=0.02)
box((-1.15, 0, 1.45), (0.1, 2.6, 2.5), "b88f66", CAR, r=0.02); box((1.15, 0, 1.45), (0.1, 2.6, 2.5), "b88f66", CAR, r=0.02)
box((0, 0, 2.76), (2.4, 2.6, 0.12), "cfd4da", CAR, r=0.02, metal=0.6)
CAR_LAMP = box((0, 0.2, 2.68), (1.4, 1.2, 0.04), "fff3d6", CAR, emit=4.0)
box((0, 1.14, 1.0), (2.0, 0.06, 0.06), "dfe4ea", CAR, metal=0.9, rough=0.2)
box((0.9, 1.18, 1.5), (0.25, 0.04, 0.5), "2d3436", CAR); box((0.9, 1.15, 1.6), (0.12, 0.02, 0.12), "ffd34d", CAR, emit=2.0)
box((0, 0, 3.08), (3.0, 0.32, 0.26), STEEL, CAR, metal=0.6)                       # crosshead
for sx in (-1, 1): box((sx * 1.3, 0, 1.45), (0.14, 0.32, 3.4), STEEL, CAR, metal=0.6)  # stiles
box((0, 0, 3.27), (0.5, 1.2, 0.14), "2d2d2d", CAR, metal=0.6)                      # hitch plate
for sx in (-1, 1):
    for z in (0.05, 3.05): box((sx * 1.38, 0, z), (0.12, 0.42, 0.24), "222222", CAR, metal=0.4)
# safeties (under the car, at each rail)
SAF = []
for sx in (-1, 1):
    box((sx * 1.45, 0, -0.2), (0.62, 0.55, 0.38), "2d2d2d", CAR, r=0.04, metal=0.5)      # housing
    pair = []
    for side in (-1, 1):
        w = box((sx * 1.45 + side * 0.2, -0.3, -0.2), (0.12, 0.08, 0.34), "e67e22", CAR, r=0.02, metal=0.4)
        pair.append((w, side))
    SAF.append((sx, pair))
LINK = box((0, -0.3, -0.12), (2.9, 0.07, 0.07), "c0392b", CAR, metal=0.4)              # linkage bar
GOVARM = [box((-1.55, -0.78, -0.12), (0.08, 0.95, 0.08), "f1c40f", CAR), box((-1.62, -1.25, -0.12), (0.2, 0.08, 0.08), "f1c40f", CAR),
          box((-1.65, -1.25, -0.12), (0.14, 0.14, 0.24), "2d2d2d", CAR)]
SPARKS = [sph((0, 0, 0), (0.07, 0.07, 0.07), "ffcf5a", emit=12.0) for _ in range(24)]
STUBS = [obj(M_CYL, (0, 0, 0), (0.07, 0.07, 0.6), "8d96a0", metal=0.8, rough=0.35) for _ in range(6)]

# ---------------------------------------------------------------- counterweight
CW = empty((CWX, CWY, 15.0))
for sx in (-1, 1): box((sx * 0.62, 0, 1.5), (0.1, 1.3, 3.0), STEEL, CW, metal=0.6)
for z in (0.1, 2.9): box((0, 0, z), (1.34, 1.3, 0.2), STEEL, CW, metal=0.6)
for i in range(8): box((0, 0, 0.38 + i * 0.32), (1.12, 1.1, 0.29), ("6d737a", "5a6067")[i % 2], CW, r=0.02, metal=0.5)
box((0, 0, 3.07), (0.4, 1.1, 0.14), "2d2d2d", CW, metal=0.6)
for sx in (-1, 1):
    for z in (0.1, 2.9): box((sx * 0.74, 0, z), (0.1, 0.3, 0.2), "222222", CW)
CW_SAF = [box((sx * 0.8, -0.25, 0.0), (0.12, 0.08, 0.3), "e67e22", CW, r=0.02) for sx in (-1, 1)]

# ---------------------------------------------------------------- hoist ropes + machine
ROPEY = [1.2 + i * 0.2 for i in range(6)]
SHX, SHZ, SHR = (CX + CWX) / 2, 26.0, (CWX - CX) / 2
CAR_ROPES = [obj(M_CYL, (0, 0, 0), (0.07, 0.07, 1), "8d96a0", metal=0.8, rough=0.35) for _ in ROPEY]
CW_ROPES = [obj(M_CYL, (0, 0, 0), (0.07, 0.07, 1), "8d96a0", metal=0.8, rough=0.35) for _ in ROPEY]
ARC = []
for y in ROPEY:
    pcs = []
    for j in range(10):
        a0, a1 = math.pi * j / 10, math.pi * (j + 1) / 10
        o = obj(M_CYL, (0, 0, 0), (1, 1, 1), "8d96a0", metal=0.8, rough=0.35)
        seg(o, (SHX - SHR * math.cos(a0), y, SHZ + SHR * math.sin(a0) + 0.04), (SHX - SHR * math.cos(a1), y, SHZ + SHR * math.sin(a1) + 0.04), 0.04)
        pcs.append(o)
    ARC.append(pcs)
GLOWROPE = mat("ffd34d", 0.3, 0.3, 4.0)
ROPEM = mat("8d96a0", 0.35, 0.8)
SHEAVE = empty((SHX, 1.7, SHZ))
cyl((0, 0, 0), (2 * SHR - 0.1, 2 * SHR - 0.1, 1.2), "7c858f", SHEAVE, rot=(math.pi / 2, 0, 0), metal=0.8, rough=0.3)
for y in ROPEY: cyl((0, y - 1.7, 0), (2 * SHR + 0.02, 2 * SHR + 0.02, 0.05), "3a3f45", SHEAVE, rot=(math.pi / 2, 0, 0), metal=0.6)
SPIN = empty((0, 0, 0), SHEAVE)
box((0, -0.62, 0), (2.3, 0.05, 0.26), "c0392b", SPIN); box((0, -0.62, 0), (0.26, 0.05, 2.3), "c0392b", SPIN)
cyl((0, -0.64, 0), (0.5, 0.5, 0.05), "2d2d2d", SPIN, rot=(math.pi / 2, 0, 0))
MOTOR = empty((SHX, 0, SHZ))
cyl((0, 2.95, 0), (1.9, 1.9, 1.2), "2f6db5", MOTOR, rot=(math.pi / 2, 0, 0), rough=0.4)
for i in range(6): cyl((0, 2.45 + i * 0.2, 0), (2.0, 2.0, 0.06), "275a96", MOTOR, rot=(math.pi / 2, 0, 0))
box((0, 2.95, -1.2), (2.2, 1.4, 0.75), "34495e", MOTOR, r=0.05)                     # bedplate
cyl((0, 1.6, 0), (0.32, 0.32, 3.2), "c8ccd1", MOTOR, rot=(math.pi / 2, 0, 0), metal=0.9, rough=0.2)  # axle
DRUM = cyl((0, 0.72, 0), (1.1, 1.1, 0.36), "9aa2ab", MOTOR, rot=(math.pi / 2, 0, 0), metal=0.9, rough=0.2)
box((0, 0.72, -1.05), (0.5, 0.4, 1.0), "34495e", MOTOR, r=0.04)                     # brake stand
SHOES = []
for sx in (-1, 1):
    a = empty((sx * 0.95, 0.72, 0), MOTOR)
    box((0, 0, 0), (0.16, 0.36, 1.2), "f1c40f", a, r=0.03)
    box((-sx * 0.1, 0, 0), (0.08, 0.34, 0.8), "6b3f22", a, rough=0.9)
    SHOES.append((a, sx))
SPRING = [cyl((0, 0.72, 0.9), (0.24, 0.24, 0.07), "c0392b", MOTOR, rot=(0, math.pi / 2, 0)) for _ in range(9)]
MAGNET = box((0, 0.72, 0.95), (0.5, 0.42, 0.34), "2d3436", MOTOR, r=0.04)
MAG_GLOW = box((0, 0.5, 0.95), (0.3, 0.02, 0.12), "4dd0ff", MOTOR, emit=4.0)

# ---------------------------------------------------------------- governor + its rope
GX, GZ, GR, GY = -2.65, 25.6, 0.3, 0.45
TENZ = PITZ + 0.7
GOV = empty((GX, GY, GZ))
cyl((0, 0, 0), (2 * GR, 2 * GR, 0.14), "7c858f", GOV, rot=(math.pi / 2, 0, 0), metal=0.8, rough=0.3)
box((0, 0.3, -0.62), (0.4, 0.4, 0.95), "34495e", GOV, r=0.04)
GOVSPIN = empty((0, -0.09, 0), GOV)
FLY = []
for sx in (-1, 1):
    p = empty((sx * 0.06, 0, 0), GOVSPIN)
    box((sx * 0.14, 0, 0), (0.24, 0.05, 0.1), "c0392b", p, r=0.02)
    box((sx * 0.26, 0, 0.05), (0.08, 0.05, 0.12), "e74c3c", p, r=0.02)
    FLY.append((p, sx))
box((0, -0.01, 0), (0.06, 0.04, 0.5), "f1c40f", GOVSPIN)
GOVR = [obj(M_CYL, (0, 0, 0), (0.06, 0.06, 1), "d9b44a", metal=0.6, rough=0.4) for _ in range(2)]
TENS = empty((GX, GY, TENZ))
cyl((0, 0, 0), (2 * GR, 2 * GR, 0.12), "7c858f", TENS, rot=(math.pi / 2, 0, 0), metal=0.8)
box((0, 0.1, -0.45), (0.5, 0.3, 0.4), "34495e", TENS, r=0.04)
BEADS = [sph((0, 0, 0), (0.1, 0.1, 0.1), "ff6b3d", emit=3.0) for _ in range(10)]

# ---------------------------------------------------------------- buffers in the pit
BUF = empty((0, 0, 0))
hb = empty((CX, CY, PITZ), BUF)
cyl((0, 0, 0.05), (0.9, 0.9, 0.1), "34495e", hb)
cyl((0, 0, 0.55), (0.5, 0.5, 1.0), "f1c40f", hb, rough=0.4)
HB_PIST = cyl((0, 0, 1.25), (0.26, 0.26, 0.5), "d5d9de", hb, metal=0.9, rough=0.2)
cyl((0, 0, 1.53), (0.6, 0.6, 0.08), "2d2d2d", hb)
sb = empty((CWX, CWY, PITZ), BUF)
cyl((0, 0, 0.05), (0.8, 0.8, 0.1), "34495e", sb)
for i in range(7): cyl((0, 0, 0.18 + i * 0.12), (0.6, 0.6, 0.06), "c0392b", sb, metal=0.4)
cyl((0, 0, 0.55), (0.3, 0.3, 0.8), "7f8c8d", sb)
cyl((0, 0, 1.02), (0.7, 0.7, 0.08), "2d2d2d", sb)
BUFS = [hb, sb]

# ---------------------------------------------------------------- per-frame state
ANCH = {}
_prev = {"z": None, "t": None, "gang": 0.0, "sang": 0.0}

def update(t):
    CAMTIME[0] = t
    shot, u = shot_at(t)
    apply_shot(shot, VIS_EXTRA)
    st = stage(t)
    fin = st["fin"]
    # shaft walls rise
    for o in SHW:
        x0, x1, y0, y1, z0, z1 = o["full"]
        set_ext(o, x0, x1, y0, y1, z0, z0 + (z1 - z0) * st["wall"])
    for o in CAP: o.hide_render = st["wall"] < 0.999
    for o in RAILS:
        x0, x1, y0, y1, z0, z1 = o["full"]
        set_ext(o, x0, x1, y0, y1, z0, z0 + (z1 - z0) * st["rail"])
    for b in BRACK: b.hide_render = b.location.z > PITZ + (24 - PITZ) * st["rail"]
    # car
    zc = car_z(t)
    CAR.location = (CX, CY, zc)
    hide(CAR, not st["car"])
    if st["car"]:
        for o in GOVARM: o.hide_render = not st["gov"]
    SHL.location = (0.4, -1.5, zc + 1.8 if shot not in ("machine", "brake", "buffer") else (26 if shot != "buffer" else -0.5))
    _sl.energy = 450
    # counterweight
    zcw = 23.9 - zc - 3.15
    CW.location = (CWX, CWY, zcw)
    hide(CW, not st["cw"])
    if shot == "counter" and t < T_CW1:
        k = ease((t - T_CW0) / (T_CW1 - T_CW0)); CW.location.z = lerp(zcw + 5.0, zcw, k)
        zcw = CW.location.z
    # hoist ropes
    rp = st["rope"]
    top_car = zc + 3.34
    for i, (o, y) in enumerate(zip(CAR_ROPES, ROPEY)):
        if not st["car"]: o.hide_render = True; continue
        ki = max(0.0, min(1.0, rp * 1.6 - i * 0.12))
        ztop = top_car + (SHZ - top_car) * ki
        if st["cut"]:
            ztop = top_car + 0.0
        seg(o, (CX, y, top_car - 0.05), (CX, y, ztop), 0.045)
        if ki < 0.02 or st["cut"]: o.hide_render = True
        one = (not fin) and shot == "ropes" and t >= T_ONE and i == 3
        o.material_slots[0].material = GLOWROPE if one else ROPEM
    for i, (o, y) in enumerate(zip(CW_ROPES, ROPEY)):
        seg(o, (CWX, y, zcw + 3.12), (CWX, y, SHZ), 0.045)
        o.hide_render = not st["cw"] or st["cut"]
    for i, pcs in enumerate(ARC):
        for o in pcs: o.hide_render = not st["cw"] or st["cut"] or rp < 0.99
    # machine
    hide(SHEAVE, not st["motor"]); hide(MOTOR, not st["motor"])
    if not st["motor"]:
        hide(SHEAVE, True)
    dt = 0.0 if _prev["t"] is None else t - _prev["t"]
    vz = 0.0 if (_prev["z"] is None or abs(dt) > 0.2 or dt <= 0) else (zc - _prev["z"]) / dt
    _prev["z"], _prev["t"] = zc, t
    power = fin or t < T_PWR or shot not in ("brake",)
    if shot == "machine" and t >= T_TURN:
        ang = (t - T_TURN) * 1.4
    elif shot == "brake":
        ang = 0.0 if t >= T_CLAMP1 else (t - S(7)) * 1.6 * (1 - ease((t - T_PWR) / 0.6))
    else:
        ang = -zc / SHR
    SPIN.rotation_euler = (0, ang, 0)
    # brake shoes: open while running in brake shot, else closed
    if shot == "brake":
        cl = ease((t - T_CLAMP0) / (T_CLAMP1 - T_CLAMP0))
    elif shot == "machine":
        cl = 0.0
    else:
        cl = 1.0
    for a, sx in SHOES:
        a.location.x = sx * (0.95 - (1 - cl) * 0.0 + (1 - cl) * 0.22)
    gap = SHOES[1][0].location.x - SHOES[0][0].location.x
    for i, s in enumerate(SPRING):
        s.location = (-gap / 2 + 0.1 + i * (gap - 0.2) / 8, 0.72, 0.9)
    lit = not (shot == "brake" and t >= T_PWR)
    _ml.energy = 520 if lit else 60
    MR_LAMP.material_slots[0].material = mat("fff3d6", 0.4, 0, 5.0 if lit else 0.2)
    MAG_GLOW.material_slots[0].material = mat("4dd0ff", 0.4, 0, 4.0 if lit and cl < 0.5 else 0.0)
    CAR_LAMP.material_slots[0].material = mat("fff3d6", 0.4, 0, 4.0)
    # governor
    hide(GOV, not st["gov"]); hide(TENS, not st["gov"])
    grabbed = (not fin) and t >= T_GRAB and shot in ("governor", "safeties", "buffer", "otis")
    if shot == "governor" and t < T_GRAB:
        gang = -zc / GR
    elif grabbed:
        gang = -fall_z(T_GRAB) / GR
    else:
        gang = -zc / GR
    GOVSPIN.rotation_euler = (0, gang, 0)
    swing = 0.0
    if shot == "governor" and t >= T_FAST0:
        swing = 0.75 * ease((t - T_FAST0) / max(0.1, T_GRAB - T_FAST0))
    if grabbed: swing = 0.75
    for p, sx in FLY:
        p.rotation_euler = (0, -sx * swing, 0)
    xa, xb = GX - GR, GX + GR
    seg(GOVR[0], (xa, GY, TENZ), (xa, GY, GZ), 0.035)
    seg(GOVR[1], (xb, GY, TENZ), (xb, GY, GZ), 0.035)
    for o in GOVR:
        o.hide_render = not st["gov"]
        o.material_slots[0].material = mat("ffd34d", 0.3, 0.3, 3.0) if (grabbed and shot in ("governor", "safeties")) else mat("d9b44a", 0.4, 0.6)
    # moving beads on governor rope show it travelling with the car
    zrope = zc if not grabbed else fall_z(T_GRAB)
    span = GZ - TENZ
    for i, b in enumerate(BEADS):
        on = st["gov"] and shot in ("governor",)
        b.hide_render = not on
        if on:
            side = i % 2
            ph = ((i // 2) / 5.0 + (zrope if side else -zrope) / span) % 1.0
            b.location = (xb if side else xa, GY - 0.04, TENZ + ph * span)
    # safeties: wedges slide up and clamp after the governor grabs
    if fin:
        cs = 0.0
    elif shot == "safeties" or (shot == "governor" and t >= T_GRAB):
        cs = ease((t - T_GRAB - 0.2) / max(0.1, T_WEDGE - T_GRAB - 0.2))
    elif shot in ("buffer", "otis"):
        cs = 1.0
    else:
        cs = 0.0
    for sx, pair in SAF:
        for w, side in pair:
            w.location = (sx * 1.45 + side * (0.2 - 0.11 * cs), -0.3, -0.2 + 0.14 * cs)
            w.material_slots[0].material = mat("ff7a1a", 0.4, 0.3, 3.5) if cs > 0.95 and shot in ("safeties", "otis") else mat("e67e22", 0.4, 0.4)
    for w in GOVARM[:1]:
        w.rotation_euler = (0.25 * cs, 0, 0)
    for o in CW_SAF:
        o.material_slots[0].material = mat("ff7a1a", 0.4, 0.3, 3.5) if st["cut"] else mat("e67e22", 0.4, 0.4)
    # sparks at the clamp
    random.seed(int(t * 24) * 7)
    spark_on = shot == "safeties" and T_WEDGE - 0.5 <= t < T_WEDGE + 0.5
    for i, s in enumerate(SPARKS):
        s.hide_render = not spark_on
        if spark_on:
            rx = RAILX[i % 2]
            s.location = (rx + random.uniform(-0.3, 0.3), CY - 0.35 + random.uniform(-0.1, 0.1), zc - 0.2 + random.uniform(-0.6, 0.4))
    # cut rope stubs
    for i, (s, y) in enumerate(zip(STUBS, ROPEY)):
        s.hide_render = not st["cut"]
        if st["cut"]:
            k = min(1.0, (t - T_CUT) / 0.5)
            ang = 0.6 * math.sin(i * 1.7 + 1) * (1 - 0.5 * k) + 0.25 * math.sin(t * 3 + i)
            p0 = Vector((CX, y, top_car - 0.05)); p1 = p0 + Vector((math.sin(ang) * 0.9, 0, math.cos(ang) * 0.9))
            seg(s, p0, p1, 0.045)
    # buffers
    b = st["buf"]
    if shot in ("buffer", "otis") or fin:
        hide(BUF, False)
        bs = max(0.001, b if shot == "buffer" else 1.0)
        for o in BUFS: o.scale = (1, 1, bs)
        HB_PIST.location.z = 1.25 - (0.12 * (0.5 + 0.5 * math.sin(t * 5)) if shot == "buffer" and t > T_BUF1 else 0)
    else:
        hide(BUF, True)
    # cameras
    if shot == "hook":
        k = ease(u / 3.0)
        cam(vl((5.0, -17.0, 15.5), (9.0, -33.0, 13.5), k), vl((-0.6, 2.0, 13.5), (0.0, 3.0, 12.5), k), 28)
    elif shot == "shaft":
        k = ease(u / 3.2)
        cam(vl((4.0, -27.0, 6.0), (6.0, -31.0, 11.0), k), vl((0.0, 2.0, 8.0), (0.0, 2.0, 11.5), k), 28)
    elif shot == "car":
        k = ease(u / 2.9)
        cam(vl((-4.6, -8.5, 5.2), (-3.4, -7.6, 3.4), k), (CX, CY, zc + 1.2), 26)
    elif shot == "ropes":
        k = ease(u / 4.4)
        cam(vl((3.2, -8.5, 1.6), (3.5, -13.0, 9.5), k), vl((CX, CY, 3.0), (CX, CY, 14.0), k), 26)
    elif shot == "machine":
        k = ease(u / 2.4)
        cam(vl((4.6, -7.4, 28.6), (3.2, -6.4, 27.4), k), (SHX - 0.2, 1.4, 25.7), 24)
    elif shot == "counter":
        k = ease(u / 5.1)
        cam(vl((7.0, -22.0, 10.0), (5.5, -24.0, 13.0), k), vl((0.6, 2.0, 10.0), (0.6, 2.0, 12.5), k), 28)
    elif shot == "brake":
        k = ease(u / 3.3)
        cam(vl((-1.4, -3.6, 27.2), (-0.4, -3.0, 26.6), k), (SHX, 0.8, 26.0), 30)
    elif shot == "governor":
        if t < S(9) - 0.08:
            k = ease((t - S(8)) / 3.8)
            cam(vl((-8.0, -11.5, zc + 4.0), (-7.0, -10.5, zc + 3.0), k), (-1.8, 1.0, zc + 2.8), 26)
        else:
            k = ease((t - S(9)) / 3.4)
            cam(vl((-4.6, -3.6, 26.6), (-4.0, -3.0, 26.2), k), (GX + 0.1, GY, GZ - 0.2), 28)
    elif shot == "safeties":
        k = ease(u / 3.5)
        cam(vl((-0.6, -3.6, zc - 0.2), (-1.0, -3.0, zc - 0.5), k), (RAILX[0] + 0.25, CY - 0.4, zc - 0.05), 28)
    elif shot == "buffer":
        k = ease(u / 4.0)
        cam(vl((3.4, -6.0, 0.4), (2.4, -5.4, -0.2), k), (0.6, 1.7, PITZ + 0.9), 24)
    else:  # otis
        if t < S(13) - 0.08:
            k = ease((t - S(12)) / 5.5)
            cam(vl((3.5, -9.5, zc + 5.5), (4.0, -12.0, zc + 6.5), k), (0.2, CY, zc + 3.0), 26)
        else:
            k = ease((t - S(13)) / 3.6)
            cam(vl((4.0, -13.0, zc + 6.5), (9.0, -34.0, 13.0), k), vl((0.2, CY, zc + 3.0), (0.0, 3.0, 12.5), k), 28)
    # label anchors
    ANCH.clear()
    ANCH.update({"rails": (RAILX[0], CY, 4.0 if shot != "shaft" else 9.0), "car": (CX, CY - 1.2, zc + 1.6), "ropes": (CX, ROPEY[0], zc + 7.0),
                 "onerope": (CX, ROPEY[3], zc + 5.0), "sheave": (SHX - 0.6, 1.05, SHZ + 0.6), "cw": (CWX, CWY - 0.65, zcw + 1.8),
                 "brake": (SHX + 0.95, 0.55, SHZ + 0.2), "governor": (GX, GY - 0.1, GZ), "govrope": (GX + GR, GY, zc + 4.5),
                 "wedges": (RAILX[0], CY - 0.35, zc - 0.25), "buffer": (CX, CY - 0.5, PITZ + 1.3), "buffer2": (CWX, CWY - 0.5, PITZ + 0.9)})
    return shot

LBL_DIR = os.path.join(EP, "labels")
os.makedirs(LBL_DIR, exist_ok=True)
def after_frame(f, t):
    out = {}
    for nm, p in ANCH.items():
        v = world_to_camera_view(scn, CAM, Vector(p))
        out[nm] = [round(v.x, 4), round(1 - v.y, 4), round(v.z, 3)]
    json.dump(out, open(os.path.join(LBL_DIR, f"f{f:05d}.json"), "w"))

if __name__ == "__main__":
    run(update, VIS_EXTRA, after_frame)
