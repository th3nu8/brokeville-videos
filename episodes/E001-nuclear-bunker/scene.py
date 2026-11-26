"""Explainer E001 — How a nuclear bunker is built. Diorama cutaway: section plane at y=0, camera in front (y<0)."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pipeline"))
from lib import *
from bpy_extras.object_utils import world_to_camera_view

SHOT_LIGHT = {"hook": "day", "dig": "day", "rebar": "day", "pour": "day", "door": "day", "hatch": "day", "air": "day",
              "pressure": "day", "inside": "day", "bury": "day", "wait": "dusk"}
SHOT_FSTOP = {"hook": 3.5, "dig": 5.6, "rebar": 4.0, "pour": 4.0, "door": 2.4, "hatch": 4.0, "air": 2.4, "pressure": 4.0,
              "inside": 2.8, "bury": 5.6, "wait": 5.6}
VIS_EXTRA = {s: {"site"} for s in SHOT_LIGHT}
setup_shots(SHOT_LIGHT, SHOT_FSTOP)
LIGHTS["dusk"] = ("2a2a5a", "ff9a6a", "c8a0c0", 0.55, 2.4, "ff9a60", (math.radians(80), 0, math.radians(-30)))
LIGHTS["day"] = ("3a86d8", "d6ecff", "c8dcf5", 0.9, 4.0, "fff2e0", (math.radians(48), math.radians(8), math.radians(-28)))

M_U = rbox_mesh(1, 1, 1, r=0)
def ubox(x0, x1, y0, y1, z0, z1, color, rough=0.85, coll=None, **k):
    o = obj(M_U, ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), color, rough=rough, **k)
    o["ext"] = (x0, x1, y0, y1, z0, z1)
    return o
def set_ext(o, x0, x1, y0, y1, z0, z1):
    if z1 - z0 < 0.002 or x1 - x0 < 0.002 or y1 - y0 < 0.002:
        o.hide_render = True; return
    o.hide_render = False
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); o.scale = (x1 - x0, y1 - y0, z1 - z0)

# ---------------------------------------------------------------- timeline (from narration)
T_DIG0, T_DIG1 = W(2, "dig"), S(4) - 0.3
T_REB0, T_REB1 = S(4), S(5) + 0.6
T_POUR0, T_POUR1 = W(5, "concrete"), S(6) - 0.1
T_DOOR0, T_DOOR1 = W(6, "blast") , W(6, "shock")
T_HATCH0, T_HATCH1 = S(7) + 0.2, W(7, "emergency")
T_AIR0 = S(8)
T_PRE, T_HEPA, T_CARB = W(8, "pre"), W(8, "hepa"), W(8, "activated")
T_PRESS = S(9)
T_BUNK, T_WATER, T_FOOD, T_POWER, T_RADIO = W(10, "bunks"), W(10, "water"), W(10, "food"), W(10, "power"), W(10, "radio")
T_BURY0, T_BURY1 = S(11) + 0.2, S(11) + 2.6
T_WAIT = S(12)

def stage(t):
    """construction progress state; hook shows the finished bunker"""
    shot, u = shot_at(t)
    fin = shot == "hook"
    def k(a, b):
        return 1.0 if fin else ease((t - a) / max(0.01, b - a))
    return dict(fin=fin, dig=k(T_DIG0, T_DIG1), reb=k(T_REB0, T_REB1), pour=k(T_POUR0, T_POUR1), door=k(T_DOOR0, T_DOOR1),
                hatch=k(T_HATCH0, T_HATCH1), air=1.0 if (fin or t >= T_AIR0) else 0.0, bury=k(T_BURY0, T_BURY1))

# ---------------------------------------------------------------- world
CUR[0] = "site"
GX0, GX1, GY0, GY1, GZ0 = -22, 22, 0, 26, -12
PX0, PX1, PY1, PZ0 = -6.2, 6.2, 11.2, -8.8   # pit
STRATA = [(0.0, -0.7, "5b3c22"), (-0.7, -3.6, "8b5a33"), (-3.6, -6.6, "c19a5e"), (-6.6, -12.0, "77706a")]
def strata_block(x0, x1, y0, y1, ztop, zbot):
    for a, b, c in STRATA:
        top, bot = min(a, ztop), max(b, zbot)
        if top > bot: ubox(x0, x1, y0, y1, bot, top, c)
strata_block(GX0, PX0, GY0, GY1, 0, GZ0)
strata_block(PX1, GX1, GY0, GY1, 0, GZ0)
strata_block(PX0, PX1, PY1, GY1, 0, GZ0)
strata_block(PX0, PX1, GY0, PY1, PZ0, GZ0)
# grass top + pebbles in section face
ubox(GX0, PX0, GY0, GY1, 0, 0.18, "4e9a3c", rough=0.9)
ubox(PX1, GX1, GY0, GY1, 0, 0.18, "4e9a3c", rough=0.9)
ubox(PX0, PX1, PY1, GY1, 0, 0.18, "4e9a3c", rough=0.9)
random.seed(3)
for i in range(70):
    x = random.uniform(GX0 + 0.5, GX1 - 0.5)
    if PX0 - 0.3 < x < PX1 + 0.3: continue
    z = random.uniform(-11.5, -0.9)
    sph((x, -0.02, z), (random.uniform(0.15, 0.45), 0.12, random.uniform(0.12, 0.3)), random.choice(["6a6158", "8d8378", "a39782"]), rough=0.8)
for i in range(8):
    tree((random.choice([random.uniform(-20, -9), random.uniform(9, 20)]), random.uniform(10, 24), 0.1), random.uniform(0.45, 0.7))
# pit fill (removed while digging) split by strata
PIT = []
for a, b, c in STRATA:
    top, bot = a, max(b, PZ0)
    if top > bot: PIT.append((ubox(PX0, PX1, GY0, PY1, bot, top, c), top, bot))
PIT_GRASS = ubox(PX0, PX1, GY0, PY1, 0, 0.18, "4e9a3c", rough=0.9)
# dirt pile from digging
PILE = cone((-12.5, 6, 0.1), (5, 4, 3), "8b5a33", rough=0.95)

# ---------------------------------------------------------------- bunker (cut at y=0)
BX0, BX1, BY1, BZ0, BZ1 = -5.0, 5.0, 10.0, -8.6, -4.2
WT = 0.5
CONC = "a9a8a2"
FLOOR = ubox(BX0, BX1, 0, BY1, BZ0, BZ0 + WT, CONC)
WALLS = [ubox(BX0, BX0 + WT, 0, BY1, BZ0 + WT, BZ1 - WT, CONC), ubox(BX1 - WT, BX1, 0, BY1, BZ0 + WT, BZ1 - WT, CONC),
         ubox(BX0 + WT, BX1 - WT, BY1 - WT, BY1, BZ0 + WT, BZ1 - WT, CONC)]
ROOF = ubox(BX0, BX1, 0, BY1, BZ1 - WT, BZ1, CONC)
for o in [FLOOR, ROOF] + WALLS: o["full"] = o["ext"]
# interior floor finish
INFLOOR = ubox(BX0 + WT, BX1 - WT, 0, BY1 - WT, BZ0 + WT, BZ0 + WT + 0.04, "8a8f96", rough=0.6)
# rebar cage
REBAR = []
def bars_plane(axis, fixed, a0, a1, b0, b1, step=0.55):
    out = []
    n_a = int((a1 - a0) / step); n_b = int((b1 - b0) / step)
    for i in range(n_a + 1):
        p = a0 + i * (a1 - a0) / n_a
        out.append((axis, fixed, "a", p, b0, b1))
    for j in range(n_b + 1):
        q = b0 + j * (b1 - b0) / n_b
        out.append((axis, fixed, "b", q, a0, a1))
    return out
specs = []
specs += bars_plane("z", BZ0 + 0.25, BX0 + 0.2, BX1 - 0.2, 0.1, BY1 - 0.2)            # floor (a=x, b=y)
for xw in (BX0 + 0.25, BX1 - 0.25):
    specs += bars_plane("x", xw, 0.1, BY1 - 0.2, BZ0 + 0.3, BZ1 - 0.3)                   # side walls (a=y, b=z)
specs += bars_plane("y", BY1 - 0.25, BX0 + 0.2, BX1 - 0.2, BZ0 + 0.3, BZ1 - 0.3)       # back wall (a=x, b=z)
specs += bars_plane("z", BZ1 - 0.25, BX0 + 0.2, BX1 - 0.2, 0.1, BY1 - 0.2)            # roof
RB = mat("9a4a2a", 0.5, 0.6)
for (axis, f, kind, p, c0, c1) in specs:
    L = c1 - c0; mid = (c0 + c1) / 2
    if axis == "z":
        loc = (p, mid, f) if kind == "a" else (mid, p, f)
        rot = (math.pi / 2, 0, 0) if kind == "a" else (0, math.pi / 2, 0)
    elif axis == "x":
        loc = (f, p, mid) if kind == "a" else (f, mid, p)
        rot = (0, 0, 0) if kind == "a" else (math.pi / 2, 0, 0)
    else:
        loc = (p, f, mid) if kind == "a" else (mid, f, p)
        rot = (0, 0, 0) if kind == "a" else (0, math.pi / 2, 0)
    o = obj(M_CYL, loc, (0.06, 0.06, L), m=RB, rot=rot)
    o["order"] = (0 if axis == "z" and f < -8 else 1 if axis != "z" else 2, loc[2])
    REBAR.append(o)
REBAR.sort(key=lambda o: (o["order"][0], o["order"][1]))

# blast door on back wall
DOORX, DOORZ = 1.6, BZ0 + WT + 1.15
DFRAME = [ubox(DOORX - 1.15, DOORX + 1.15, BY1 - WT - 0.12, BY1 - WT + 0.02, DOORZ - 1.25, DOORZ + 1.3, "3b4048", rough=0.4, metal=0.7)]
DREC = ubox(DOORX - 0.85, DOORX + 0.85, BY1 - WT - 0.13, BY1 - WT + 0.03, DOORZ - 1.05, DOORZ + 1.05, "15181c", rough=0.6)
DHINGE = empty((DOORX - 0.85, BY1 - WT - 0.2, DOORZ))
box((0.85, 0, 0), (1.66, 0.32, 2.06), "6f7984", DHINGE, r=0.05, metal=0.85, rough=0.32)
cyl((0.85, -0.2, 0.0), (0.7, 0.7, 0.08), "c0392b", DHINGE, rot=(math.pi / 2, 0, 0), metal=0.5, rough=0.35)
cyl((0.85, -0.25, 0.0), (0.2, 0.2, 0.12), "c0392b", DHINGE, rot=(math.pi / 2, 0, 0))
for i in range(4):
    a = i * math.pi / 4
    box((0.85, -0.22, 0), (0.75, 0.06, 0.06), "c0392b", DHINGE, rot=(0, a, 0), r=0.02)
DOOR_PARTS = DFRAME + [DREC, DHINGE]

# escape hatch tube (half-sectioned at y=0) + surface lid
HX = -3.4
HATCH_TUBE = obj(M_CYL, (HX, 0.0, (BZ1 + 0.0) / 2), (0.75, 0.75, 1.0), "7c858f", metal=0.7, rough=0.4)
HATCH_RINGS = [obj(M_CYL, (HX, 0.0, 0), (0.82, 0.82, 0.06), "5d6670", metal=0.7, rough=0.4) for _ in range(6)]
HATCH_LID = obj(M_CYL, (HX, 0.0, 0.3), (1.0, 1.0, 0.18), "c0392b", metal=0.5, rough=0.35)
LADDER = [box((HX, -0.05, BZ1 + 0.3 + i * 0.45), (0.5, 0.05, 0.05), "c9ccd1", metal=0.8) for i in range(9)]

# air intake pipe + mushroom vent + NBC filter unit
AX = -0.9
AIR_PIPE = obj(M_CYL, (AX, 0.0, (BZ1 + 1.2) / 2), (0.32, 0.32, 1.0), "8d96a0", metal=0.7, rough=0.35)
VENT = empty((AX, 0.0, 1.2))
cyl((0, 0, 0), (0.34, 0.34, 0.6), "8d96a0", VENT, metal=0.7, rough=0.35)
sph((0, 0, 0.42), (0.9, 0.9, 0.45), "8d96a0", VENT, metal=0.7, rough=0.35)
DUCT = ubox(-4.4, AX + 0.16, 0.0, 0.32, BZ1 - WT - 0.32, BZ1 - WT, "8d96a0", rough=0.35, metal=0.7)
FILT = empty((BX0 + WT + 0.35, 3.2, BZ0 + WT + 1.5))
box((0, 0, 0), (0.7, 2.2, 1.3), "dfe3e8", FILT, r=0.06, rough=0.4)
CARTS = []
for i, c in enumerate(("9aa3ad", "f2f2f2", "2d2d2d")):
    CARTS.append(box((0.38, -0.7 + i * 0.7, 0), (0.08, 0.6, 1.1), c, FILT, r=0.03, rough=0.5))
cyl((0, 1.3, 0.45), (0.28, 0.28, 0.5), "8d96a0", FILT, rot=(math.pi / 2, 0, 0), metal=0.7)
FILT_RISER = ubox(-4.45, -4.13, 0.0, 0.32, BZ0 + WT + 2.0, BZ1 - WT - 0.3, "8d96a0", rough=0.35, metal=0.7)
GLOWS = [mat("ffd34d", 0.4, 0, 0), mat("ffffff", 0.4, 0, 0), mat("4dd0ff", 0.4, 0, 0)]
DUST = [sph((0, 0, 0), (0.1, 0.1, 0.1), "6b6460", rough=0.9) for _ in range(24)]
CLEAN = [sph((0, 0, 0), (0.09, 0.09, 0.09), "7fd6ff", emit=3.0) for _ in range(14)]
ARROWS = []
for (x, y, z, rz) in ((DOORX, BY1 - 0.9, DOORZ + 1.5, 0), (HX + 1.0, 0.6, BZ1 - 1.0, 0), (AX + 2.0, 0.6, BZ1 - 1.0, 0)):
    a = empty((x, y, z))
    cyl((0, 0, 0), (0.14, 0.14, 1.0), "39b6ff", a, emit=2.5)
    cone((0, 0, 0.65), (0.34, 0.34, 0.45), "39b6ff", a, emit=2.5)
    ARROWS.append(a)

# interior items (pop in on words)
def bunks():
    r = empty((BX1 - WT - 0.75, 7.0, BZ0 + WT))
    for z in (0.5, 1.8):
        box((0, 0, z), (1.3, 3.4, 0.16), "4b5563", r, r=0.03, metal=0.5)
        box((0, 0, z + 0.2), (1.2, 3.2, 0.25), "3a6ea5", r, r=0.1, rough=0.8)
        box((0, 1.35, z + 0.42), (1.0, 0.45, 0.2), "f1f1f1", r, r=0.08)
    for sx in (-0.6, 0.6):
        for sy in (-1.65, 1.65):
            box((sx, sy, 1.25), (0.08, 0.08, 2.5), "4b5563", r, metal=0.6)
    return r
def water():
    r = empty((BX1 - WT - 0.7, 1.4, BZ0 + WT))
    for i, y in enumerate((0, 1.0)):
        cyl((0, y, 0.6), (0.85, 0.85, 1.2), "2f7fd1", r, rough=0.35)
        cyl((0, y, 1.22), (0.3, 0.3, 0.08), "1d4f87", r)
    return r
def food():
    r = empty((-2.9, BY1 - WT - 0.35, BZ0 + WT))
    for z in (0.3, 1.0, 1.7, 2.4):
        box((0, 0, z), (2.4, 0.6, 0.06), "8b5a2b", r, r=0.02)
        for i in range(7):
            cyl((-1.0 + i * 0.33, 0, z + 0.2), (0.24, 0.24, 0.34), random.choice(["e74c3c", "f1c40f", "27ae60", "e67e22", "ecf0f1"]), r, metal=0.4, rough=0.35)
    for sx in (-1.2, 1.2): box((sx, 0, 1.4), (0.06, 0.6, 2.8), "6b4220", r)
    return r
def power():
    r = empty((BX0 + WT + 0.55, 6.8, BZ0 + WT))
    box((0, 0, 0.55), (0.9, 1.6, 1.1), "f1c40f", r, r=0.06, rough=0.45)
    box((0.46, 0, 0.75), (0.04, 0.9, 0.4), "222222", r)
    box((0.47, -0.3, 0.75), (0.03, 0.15, 0.1), "2ecc71", r, emit=3.0)
    return r
def radio():
    r = empty((0.6, 4.5, BZ0 + WT))
    box((0, 0, 0.75), (1.6, 0.9, 0.08), "8b5a2b", r, r=0.02)
    for sx in (-0.7, 0.7):
        for sy in (-0.35, 0.35): box((sx, sy, 0.37), (0.07, 0.07, 0.74), "6b4220", r)
    box((0, 0, 0.98), (0.7, 0.35, 0.4), "2d3436", r, r=0.04)
    cyl((0.18, -0.18, 1.0), (0.2, 0.2, 0.05), "c8c8c8", r, rot=(math.pi / 2, 0, 0))
    box((-0.12, -0.18, 1.05), (0.25, 0.02, 0.12), "7bd389", r, emit=2.0)
    cyl((0.25, 0, 1.6), (0.03, 0.03, 0.9), "c8c8c8", r, metal=0.8)
    return r
ITEMS = {"bunks": bunks(), "water": water(), "food": food(), "power": power(), "radio": radio()}
LED = ubox(-3.5, 3.5, 4.0, 4.3, BZ1 - WT - 0.06, BZ1 - WT - 0.02, "fff3d6", emit=6.0)
_il = bpy.data.lights.new("inl", "POINT"); _il.energy = 0; _il.color = (1.0, 0.86, 0.66); _il.shadow_soft_size = 1.5
INL = bpy.data.objects.new("inl", _il); col("site").objects.link(INL); INL.location = (0, 4.5, BZ1 - 1.2)

# excavator on the right of the pit
EXC = empty((10.2, 4.5, 0.18), rot=(0, 0, 0))
box((0, -1.1, 0.45), (3.8, 0.8, 0.9), "2d2d2d", EXC, r=0.2); box((0, 1.1, 0.45), (3.8, 0.8, 0.9), "2d2d2d", EXC, r=0.2)
TURRET = empty((0, 0, 0.95), EXC)
box((0.3, 0, 0.75), (3.0, 2.4, 1.3), "f4b400", TURRET, r=0.15, rough=0.45)
box((-0.6, 0.55, 1.9), (1.2, 1.1, 1.2), "f4b400", TURRET, r=0.1); box((-1.22, 0.55, 1.9), (0.05, 0.95, 0.9), "9fd8ff", TURRET, rough=0.1)
BOOM = empty((-1.2, -0.4, 1.0), TURRET)
box((-1.9, 0, 0), (3.8, 0.45, 0.55), "f4b400", BOOM, r=0.12)
STICK = empty((-3.8, 0, 0), BOOM)
box((0, 0, -1.4), (0.38, 0.4, 2.8), "f4b400", STICK, r=0.1)
BUCKET = empty((0, 0, -2.8), STICK)
box((-0.35, 0, -0.25), (0.8, 0.9, 0.7), "3a3a3a", BUCKET, r=0.1, metal=0.6)

# fallout dust (wait shot) + clouds
FALL = [sph((0, 0, 0), (0.07, 0.07, 0.07), "9a948c", rough=0.9) for _ in range(60)]
for (x, y, z, s) in ((-18, 40, 18, 2.2), (14, 45, 22, 2.6), (2, 60, 26, 3)):
    cloud((x, y, z), s)

# ---------------------------------------------------------------- per-frame state
ANCH = {"wall": (BX0 + WT / 2, 0.0, BZ0 + 2.2), "door": (DOORX, BY1 - WT - 0.3, DOORZ + 0.6), "hatch": (HX, 0.0, -1.2),
        "pre": None, "hepa": None, "carbon": None, "room": (0.0, 4.5, BZ0 + 1.6), "bunks": (BX1 - WT - 0.75, 7.0, BZ0 + 2.6),
        "water": (BX1 - WT - 0.7, 1.9, BZ0 + 1.9), "food": (-2.9, BY1 - 0.9, BZ0 + 3.0), "power": (BX0 + WT + 0.55, 6.8, BZ0 + 1.8),
        "radio": (0.6, 4.5, BZ0 + 2.2), "earth": (0.0, 0.0, -2.2), "pit": (0.0, 0.0, -4.5)}

def update(t):
    CAMTIME[0] = t
    shot, u = shot_at(t)
    apply_shot(shot, VIS_EXTRA)
    st = stage(t)
    # pit / digging
    dz = 0.0 - (0.0 - PZ0) * st["dig"]
    for o, top, bot in PIT:
        set_ext(o, PX0, PX1, GY0, PY1, bot, min(top, dz))
    PIT_GRASS.hide_render = st["dig"] > 0.02 and st["bury"] < 0.98
    PILE.scale = (5 * (0.2 + 0.8 * st["dig"]) * (1 - 0.85 * st["bury"]), 4 * (0.2 + 0.8 * st["dig"]) * (1 - 0.85 * st["bury"]), 3 * st["dig"] * (1 - 0.9 * st["bury"]) + 0.001)
    PILE.hide_render = st["dig"] < 0.03 or st["bury"] > 0.97
    # excavator animation
    EXC.hide_render = False
    hide(EXC, st["fin"] or st["bury"] > 0.98 or t > T_POUR1 + 0.5 and t < T_BURY0)
    sw = math.sin(t * 2.2)
    TURRET.rotation_euler = (0, 0, 0.25 * math.sin(t * 0.9))
    BOOM.rotation_euler = (0, 0.25 + 0.25 * sw, 0)
    STICK.rotation_euler = (0, -0.4 + 0.45 * math.sin(t * 2.2 + 0.8), 0)
    BUCKET.rotation_euler = (0, 0.6 * math.sin(t * 2.2 + 1.6), 0)
    # rebar progressive
    nr = int(len(REBAR) * st["reb"])
    for i, o in enumerate(REBAR):
        o.hide_render = i >= nr or st["pour"] >= 0.999
    # concrete pour: floor, walls rise, roof
    p = st["pour"]
    fx0, fx1, fy0, fy1, fz0, fz1 = FLOOR["full"]
    set_ext(FLOOR, fx0, fx1, fy0, fy1, fz0, fz0 + (fz1 - fz0) * min(1, p / 0.15))
    for w in WALLS:
        x0, x1, y0, y1, z0, z1 = w["full"]
        set_ext(w, x0, x1, y0, y1, z0, z0 + (z1 - z0) * max(0, min(1, (p - 0.15) / 0.65)))
    x0, x1, y0, y1, z0, z1 = ROOF["full"]
    set_ext(ROOF, x0, x1, y0, y0 + (y1 - y0) * max(0, min(1, (p - 0.8) / 0.2)), z0, z1)
    INFLOOR.hide_render = p < 0.999
    # door
    for o in DOOR_PARTS: hide(o, p < 0.999)
    DHINGE.rotation_euler = (0, 0, -1.45 * (1 - st["door"]) if not st["fin"] else 0)
    # hatch tube grows upward from roof
    h = st["hatch"]
    top = BZ1 + (0.15 - BZ1) * h
    HATCH_TUBE.hide_render = h < 0.01
    HATCH_TUBE.location = (HX, 0.0, (BZ1 - WT + top) / 2); HATCH_TUBE.scale = (0.75, 0.75, max(0.01, top - (BZ1 - WT)))
    for i, r_ in enumerate(HATCH_RINGS):
        zr = BZ1 + 0.4 + i * 0.75
        r_.location = (HX, 0.0, zr); r_.hide_render = zr > top or h < 0.01
    HATCH_LID.hide_render = h < 0.98
    for i, l_ in enumerate(LADDER): l_.hide_render = l_.location.z > top or h < 0.01
    # air system
    a_on = st["air"] > 0.5
    for o in (AIR_PIPE, DUCT, FILT_RISER): o.hide_render = not a_on
    hide(VENT, not a_on); hide(FILT, not a_on)
    AIR_PIPE.location = (AX, 0.0, (BZ1 - WT + 1.2) / 2); AIR_PIPE.scale = (0.32, 0.32, 1.2 - (BZ1 - WT))
    hi = None
    if shot == "air":
        hi = 0 if t >= T_PRE - 0.1 else None
        if t >= T_HEPA - 0.1: hi = 1
        if t >= T_CARB - 0.1: hi = 2
    for i, c in enumerate(CARTS):
        b = c.material_slots[0].material.node_tree.nodes.get("Principled BSDF")
    for i, c in enumerate(CARTS):
        base = ("9aa3ad", "f2f2f2", "2d2d2d")[i]
        c.material_slots[0].material = mat(base, 0.5, 0, 2.5 if hi == i else 0.0, ecol="ffd34d")
    # dust down the intake, clean air out of the filter
    show_air = shot in ("air", "pressure")
    random.seed(4)
    for i, d in enumerate(DUST):
        ph = (t * 0.6 + i / len(DUST)) % 1.0
        if ph < 0.55:
            q = ph / 0.55; pos = Vector((AX + random.uniform(-0.12, 0.12), -0.05, 1.0 - q * (1.0 - (BZ1 - WT - 0.15))))
        else:
            q = (ph - 0.55) / 0.45; pos = Vector((AX - q * (AX + 4.3), 0.16, BZ1 - WT - 0.16))
        d.location = pos; d.hide_render = not show_air or shot == "pressure"
    for i, c in enumerate(CLEAN):
        ph = (t * 0.5 + i / len(CLEAN)) % 1.0
        c.location = (BX0 + WT + 0.8 + ph * 6.5, 3.2 + math.sin(ph * 6 + i) * 1.4, BZ0 + WT + 1.5 + math.sin(ph * 9 + i * 2) * 0.6)
        c.hide_render = not show_air or t < T_CARB
    # pressure arrows pulse outward
    for i, a in enumerate(ARROWS):
        on = shot == "pressure"
        hide(a, not on)
        k = (t * 1.2 + i * 0.33) % 1.0
        if i == 0:
            a.rotation_euler = (-math.pi / 2, 0, 0); a.location = (DOORX, BY1 - 1.2 + k * 0.9, DOORZ + 1.5)
        else:
            a.rotation_euler = (0, 0, 0); a.location = ((HX if i == 1 else AX) + 0.9, 0.6, BZ1 - 1.6 + k * 1.2)
        a.scale = (1, 1, 0.6 + 0.4 * math.sin(k * math.pi))
    # interior items
    for name, tt in (("bunks", T_BUNK), ("water", T_WATER), ("food", T_FOOD), ("power", T_POWER), ("radio", T_RADIO)):
        vis = st["fin"] or t >= tt - 0.1
        hide(ITEMS[name], not vis)
        if vis and not st["fin"] and t < tt + 0.25:
            s_ = 0.3 + 0.7 * ease((t - tt + 0.1) / 0.35); ITEMS[name].scale = (s_, s_, s_)
        else:
            ITEMS[name].scale = (1, 1, 1)
    lit = st["fin"] or t >= T_POWER - 0.1
    LED.hide_render = not (p >= 0.999)
    _il.energy = 900 if lit else (250 if p >= 0.999 else 0)
    LED.material_slots[0].material = mat("fff3d6", 0.4, 0, 6.0 if lit else 0.5, name=None)
    # backfill over roof
    b = st["bury"]
    if st["fin"]: b = 1.0
    zf = BZ1 + (0.0 - BZ1) * b
    for o, top_, bot in PIT:
        if b > 0:
            set_ext(o, PX0, PX1, GY0, PY1, max(bot, BZ1), min(top_, zf)) if top_ > BZ1 else None
    if b > 0:
        for o, top_, bot in PIT:
            if top_ <= BZ1:
                o.hide_render = True
    PIT_GRASS.hide_render = not (b > 0.98)
    # fallout dust in wait shot
    for i, f_ in enumerate(FALL):
        on = shot == "wait"
        f_.hide_render = not on
        if on:
            random.seed(100 + i)
            x = random.uniform(-20, 20); y = random.uniform(-2, 22)
            z = 14 - ((t * 1.3 + random.random() * 14) % 14)
            f_.location = (x, y, max(0.25, z))
    # cameras
    if shot == "hook":
        k = ease(u / 3.8)
        cam(vl((1.5, -7.0, -6.2), (9.0, -27.0, 5.0), k), vl((0.0, 5.0, -6.6), (0.0, 6.0, -3.5), k), lerp(24, 26, k))
    elif shot == "dig":
        k = ease(u / 9.0)
        cam(vl((15, -20, 9), (11, -19, 4), k), vl((2, 5, -1.5), (1, 5, -4.5), k), 26)
    elif shot == "rebar":
        k = ease(u / 2.3)
        cam(vl((7, -11, -1.0), (5, -10, -2.0), k), (0, 5, -6.4), 26)
    elif shot == "pour":
        k = ease(u / 6.6)
        cam(vl((-9, -13, -1.5), (-5, -12.5, -3.0), k), (0, 5, -6.4), 26)
    elif shot == "door":
        k = ease(u / 6.0)
        cam(vl((-1.2, -2.5, -5.9), (0.2, 3.0, -6.3), k), (DOORX, BY1 - 0.6, DOORZ + 0.2), 28)
    elif shot == "hatch":
        k = ease(u / 3.9)
        cam(vl((-8.5, -8.0, -6.0), (-8.0, -9.5, 1.5), k), vl((HX, 0, -5.2), (HX, 0, -0.3), k), 28)
    elif shot == "air":
        k = ease(u / 6.8)
        cam(vl((-0.8, -4.2, -5.4), (-1.6, -3.0, -6.0), k), (BX0 + WT + 0.5, 2.6, BZ0 + WT + 1.6), 28)
    elif shot == "pressure":
        k = ease(u / 5.7)
        cam(vl((4, -14, -2.5), (2, -15, -1.5), k), (0, 4, -5.2), 26)
    elif shot == "inside":
        k = ease(u / 3.8)
        cam(vl((-2.6, -4.6, -5.9), (2.6, -4.6, -5.9), k), (0, 5, -6.6), 24)
    elif shot == "bury":
        k = ease(u / 3.0)
        cam(vl((10, -24, 3), (7, -28, 7), k), (0, 6, -3.5), 26)
    else:  # wait
        k = ease(u / 6.6)
        cam(vl((3, -26, 6), (0, -40, 15), k), (0, 7, -3.0), 26)
    return shot

LBL_DIR = os.path.join(EP, "labels")
os.makedirs(LBL_DIR, exist_ok=True)
def after_frame(f, t):
    dg = bpy.context.evaluated_depsgraph_get()
    out = {}
    pts = dict(ANCH)
    fw = FILT.matrix_world
    for i, nm in enumerate(("pre", "hepa", "carbon")):
        pts[nm] = tuple(fw @ Vector((0.42, -0.7 + i * 0.7, 0.35)))
    for nm, p in pts.items():
        v = world_to_camera_view(scn, CAM, Vector(p))
        out[nm] = [round(v.x, 4), round(1 - v.y, 4), round(v.z, 3)]
    json.dump(out, open(os.path.join(LBL_DIR, f"f{f:05d}.json"), "w"))

if __name__ == "__main__":
    run(update, VIS_EXTRA, after_frame)
