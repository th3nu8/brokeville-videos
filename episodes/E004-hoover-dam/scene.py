"""Explainer E004 — How the Hoover Dam was built. Diorama cutaway: section plane at y=0 through the river, camera in front (y<0).
River flows along +x (upstream = left). Far canyon wall at y>=11. Dam spans y 0..11.5, curved (arch) in plan."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pipeline"))
from lib import *
from bpy_extras.object_utils import world_to_camera_view

SHOT_LIGHT = {"hook": "day", "tunnels": "day", "divert": "day", "grout": "day", "blocks": "day", "cool": "day", "lake": "day",
              "shape": "day", "arch": "day", "power": "day", "spill": "day", "ask": "dusk"}
SHOT_FSTOP = {"hook": 5.6, "tunnels": 4.0, "divert": 5.6, "grout": 4.0, "blocks": 5.6, "cool": 4.0, "lake": 5.6, "shape": 5.6,
              "arch": 5.6, "power": 4.0, "spill": 4.0, "ask": 8.0}
VIS_EXTRA = {s: {"site"} for s in SHOT_LIGHT}
setup_shots(SHOT_LIGHT, SHOT_FSTOP)
LIGHTS["dusk"] = ("2a2a5a", "ff9a6a", "c8a0c0", 0.6, 2.6, "ff9a60", (math.radians(74), 0, math.radians(-30)))
LIGHTS["day"] = ("3a86d8", "d6ecff", "c8dcf5", 0.9, 4.0, "fff2e0", (math.radians(48), math.radians(8), math.radians(-28)))

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
def boolcut(target, cutter):
    m = target.modifiers.new("b", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = cutter
    try: m.solver = "EXACT"
    except Exception: pass
    return m
AWAY = (0, 200, 200)
def cutter(r):
    o = obj(M_CYL, AWAY, (2 * r, 2 * r, 0.01), "ff00ff"); o.hide_render = True; o.display_type = "WIRE"; o["r"] = r
    return o
def seg_place(o, a, b, frac, r=None, extra=0.0):
    """place cylinder o along segment a->b (x,z points at y=0) covering fraction frac"""
    if frac <= 0.001:
        o.location = AWAY; o.scale = (0.01, 0.01, 0.01); return False
    a = Vector((a[0], 0, a[1])); b = Vector((b[0], 0, b[1]))
    d = b - a; L = d.length * frac
    dn = d.normalized()
    c = a + dn * (L / 2)
    r = r or o["r"]
    o.location = c; o.rotation_euler = (0, math.atan2(dn.x, dn.z), 0); o.scale = (2 * r, 2 * r, L + extra)
    return True

# ---------------------------------------------------------------- timeline (from narration)
def stage(t):
    shot, u = shot_at(t)
    fin = shot == "hook"
    def k(a, b):
        return 1.0 if fin else ease((t - a) / max(0.01, b - a))
    return dict(fin=fin, dig=k(S(2) + 0.1, S(3) - 0.3), div=k(S(3) + 0.1, S(4) - 0.3),
                exc=k(S(4) - 0.1, S(4) + 0.9), drill=k(W(4, "drilled"), W(4, "filled")), grt=k(W(4, "filled"), W(4, "underneath")),
                blk=k(S(5) + 0.1, S(6) - 0.15), heat=k(S(6) + 0.2, W(6, "years")), cool=k(S(7) + 0.2, S(8) - 0.3),
                built=fin or t >= S(8) - 0.1, gate=k(S(8) + 0.1, W(8, "closed") + 0.4), fill=k(W(8, "lake") - 0.4, S(9) - 0.2),
                flood=(k(S(12) - 0.05, S(12) + 1.0) if shot == "spill" else 0.0))

# ---------------------------------------------------------------- world
CUR[0] = "site"
X0, X1, ZB = -30.0, 26.0, -12.0
FY = 11.0           # far wall face
ZTOP = 26.0         # canyon rim
# bedrock under floor (front cut face)
GRAV = "c2a27a"; R1 = "9a5a3c"; R2 = "6e5048"
PIT_X0, PIT_X1 = -8.5, 16.8
G_L = ubox(X0, PIT_X0, 0, FY, -1.5, 0, GRAV, rough=0.95)
G_P = ubox(PIT_X0, PIT_X1, 0, FY, -1.5, 0, GRAV, rough=0.95)
G_R = ubox(PIT_X1, X1, 0, FY, -1.5, 0, GRAV, rough=0.95)
ROCK1 = ubox(X0, X1, 0, FY, -6.0, -1.5, R1)
ROCK2 = ubox(X0, X1, 0, FY, ZB, -6.0, R2)
ROCKS = [G_L, G_P, G_R, ROCK1, ROCK2]
random.seed(3)
for i in range(46):
    x = random.uniform(X0 + 0.5, X1 - 0.5); z = random.uniform(-11.5, -2.0)
    if -27.5 < x < 25.5 and -10.0 < z < -7.0: continue
    if -13.3 < x < -11.7 or 12.4 < x < 14.0 or -7.4 < x < -6.2: continue
    sph((x, -0.02, z), (random.uniform(0.2, 0.5), 0.12, random.uniform(0.12, 0.3)), random.choice(["5a4038", "7d5a48", "a07a60"]), rough=0.8)
# far canyon wall: banded rock, with a lower ledge for the spillway
BANDS = [(ZB, -1.5, "6e5048"), (-1.5, 6, "8a4f36"), (6, 13, "9e5d3e"), (13, 20, "86503a"), (20, ZTOP, "a86a48")]
def wall_block(x0, x1, y0, y1, ztop):
    for a, b, c in BANDS:
        top = min(b, ztop)
        if top > a: ubox(x0, x1, y0, y1, a, top, c)
SPX0, SPX1, SPY1, SPZ = -17.0, -5.0, 14.5, 20.0
wall_block(X0, X1, SPY1, 30, ZTOP)
wall_block(X0, SPX0, FY, SPY1, ZTOP); wall_block(SPX1, X1, FY, SPY1, ZTOP)
wall_block(SPX0, SPX1, FY, SPY1, SPZ)
ubox(X0, X1, FY, 30, ZTOP, ZTOP + 0.25, "c9a26e", rough=0.95)
ubox(SPX0, SPX1, FY, SPY1, SPZ, SPZ + 0.06, "c9a26e", rough=0.95)
for i in range(26):
    x = random.uniform(X0 + 1, X1 - 1); y = random.uniform(FY + 1, 29)
    if SPX0 - 0.5 < x < SPX1 + 0.5 and y < SPY1 + 0.5: continue
    sph((x, y, ZTOP + 0.2), (random.uniform(0.5, 1.2),) * 2 + (random.uniform(0.3, 0.6),), random.choice(["7a8a4a", "8f9a5a", "b08a5a"]), rough=0.9)
# rocky texture on wall face
for i in range(40):
    x = random.uniform(X0 + 1, X1 - 1); z = random.uniform(1, ZTOP - 1)
    if SPX0 < x < SPX1 and z > SPZ - 0.5: continue
    sph((x, FY - 0.05, z), (random.uniform(0.6, 1.6), 0.35, random.uniform(0.3, 0.9)), random.choice(["7d4630", "94583a", "6e4030"]), rough=0.9)
for (x, y, z, s) in ((-18, 50, 34, 2.2), (14, 55, 38, 2.6), (2, 70, 42, 3)):
    cloud((x, y, z), s)

# ---------------------------------------------------------------- water
WMAT = mat("2e86c9", 0.06, 0.0, 0.25, ecol="2a78b8")
WFOAM = mat("bfe6ff", 0.2, 0.0, 1.2, ecol="bfe6ff")
def wbox(x0, x1, y0, y1, z0, z1):
    o = ubox(x0, x1, y0, y1, z0, z1, "2e86c9", m=WMAT); return o
R_UP = wbox(X0, -16, 0.03, FY, 0, 0.6)
R_MID = wbox(-16, PIT_X1, 0.03, FY, 0, 0.6)
R_MID2 = wbox(PIT_X1 - 0.2, 18.5, 0.03, FY, 0, 0.6)
R_DS = wbox(18.5, X1, 0.03, FY, 0, 0.6)

# ---------------------------------------------------------------- diversion tunnel (one of four) in the cut face
TR = 1.25
TPTS = [(-27.5, -0.5), (-19.0, -8.5), (19.0, -8.5), (25.5, -0.5)]
TCUT = [cutter(TR) for _ in range(3)]
for c_ in TCUT:
    for r_ in ROCKS: boolcut(r_, c_)
TSEG = [(TPTS[i], TPTS[i + 1], (Vector(TPTS[i + 1]) - Vector(TPTS[i])).length) for i in range(3)]
TLEN = sum(s[2] for s in TSEG)
# lining ring visible in the face
LINER = []
for (a, b, L) in TSEG:
    o = obj(M_CYL, (0, 0, 0), (1, 1, 1), "b9b6ae", rough=0.6)
    LINER.append(o)
LINER_IN = [cutter(TR - 0.18) for _ in range(3)]
HALF = ubox(-80, 80, -40, 0, -60, 80, "ff00ff"); HALF.hide_render = True; HALF.display_type = "WIRE"
for o, ci in zip(LINER, LINER_IN):
    boolcut(o, ci); boolcut(o, HALF)
# water in the tunnel (behind the face)
TWATER = [obj(M_U, (0, 0, 0), (1, 1, 1), m=WMAT) for _ in range(3)]
def tw_place(o, a, b, frac=1.0, depth=0.55):
    if not seg_place(o, a, b, frac, r=0.5): o.hide_render = True; return
    a = Vector((a[0], 0, a[1])); b = Vector((b[0], 0, b[1])); dn = (b - a).normalized()
    n = Vector((dn.z, 0, -dn.x))
    L = (b - a).length * frac
    o.location = a + dn * (L / 2) + n * (TR - 0.18 - depth / 2) + Vector((0, 0.5, 0))
    o.scale = (depth, 0.95, L + 0.4); o.hide_render = False
TFLOW = [sph((0, 0, 0), (0.16, 0.16, 0.16), "bfe6ff", m=WFOAM) for _ in range(30)]
def tpath(q):
    """point along tunnel path q in 0..1 (near the tunnel floor, just in front of face)"""
    s = q * TLEN
    for (a, b, L) in TSEG:
        if s <= L:
            a = Vector((a[0], 0, a[1])); b = Vector((b[0], 0, b[1])); dn = (b - a).normalized(); n = Vector((dn.z, 0, -dn.x))
            return a + dn * s + n * (TR - 0.45) + Vector((0, -0.02, 0))
        s -= L
    return Vector((TPTS[-1][0], -0.02, TPTS[-1][1]))
DUSTP = [sph((0, 0, 0), (0.35, 0.35, 0.35), "c8b090", rough=0.9) for _ in range(8)]
# closing gate at the inlet
GATE = ubox(-26.0, -25.4, -0.05, 1.3, -2.4, 0.9, "7a2e22", rough=0.4, metal=0.6)

# cofferdams
COF = []
for xc in (-14.0, 20.5):
    COF.append(obj(M_WEDGE, (xc, FY / 2, 1.6), (FY, 5.0, 3.2), "8b6a45", rot=(0, 0, math.pi / 2), rough=0.95))

# ---------------------------------------------------------------- grout curtain under the heel
GX = -6.6
GROUT_D = []
GROUT_W = []
for y in (0.0, 1.8, 3.6, 5.4, 7.2, 9.0, 10.6):
    GROUT_D.append(obj(M_CYL, (GX, y, -3.5), (0.34, 0.34, 4.0), "1f1a18", rough=0.9))
    GROUT_W.append(obj(M_CYL, (GX, y, -3.5), (0.36, 0.36, 4.0), "efeae0", rough=0.5))
CURTAIN = ubox(GX - 0.45, GX + 0.45, -0.03, 0.02, -5.6, -1.5, "efeae0", rough=0.5)
RIG = empty((GX + 0.2, 4.6, -1.5))
box((0, 0, 0.35), (1.6, 1.1, 0.7), "f4b400", RIG, r=0.08)
box((-0.5, 0, 2.0), (0.18, 0.18, 3.2), "f4b400", RIG)
box((-0.2, 0, 3.55), (0.8, 0.18, 0.15), "f4b400", RIG)
cyl((-0.5, 0, 0.6), (0.1, 0.1, 1.4), "555555", RIG, metal=0.8)

# ---------------------------------------------------------------- dam
ZD0, ZD1 = -1.5, 21.5
HD = ZD1 - ZD0
YD1 = 11.6
def xu(h): return -7.0 + 1.0 * h
def xd(h): return -4.6 + 16.6 * (1 - h) ** 1.3
def dx(y): return 0.018 * y * y
CONC = "c9c4b8"
def dam_mesh():
    ny, nh = 24, 26
    ys = [YD1 * j / (ny - 1) for j in range(ny)]
    hs = [i / (nh - 1) for i in range(nh)]
    V = []; F = []
    def vid(side, i, j): return side * nh * ny + i * ny + j
    for side in (0, 1):
        for i, h in enumerate(hs):
            for j, y in enumerate(ys):
                x = (xu(h) if side == 0 else xd(h)) + dx(y)
                V.append((x, y, ZD0 + h * HD))
    for i in range(nh - 1):
        for j in range(ny - 1):
            F.append((vid(0, i, j), vid(0, i, j + 1), vid(0, i + 1, j + 1), vid(0, i + 1, j)))
            F.append((vid(1, i, j), vid(1, i + 1, j), vid(1, i + 1, j + 1), vid(1, i, j + 1)))
    for j in range(ny - 1):
        F.append((vid(0, nh - 1, j), vid(0, nh - 1, j + 1), vid(1, nh - 1, j + 1), vid(1, nh - 1, j)))   # crest
        F.append((vid(0, 0, j), vid(1, 0, j), vid(1, 0, j + 1), vid(0, 0, j + 1)))                       # base
    F.append(tuple([vid(0, i, 0) for i in range(nh)] + [vid(1, i, 0) for i in reversed(range(nh))]))   # cut face y=0
    F.append(tuple([vid(0, i, ny - 1) for i in reversed(range(nh))] + [vid(1, i, ny - 1) for i in range(nh)]))
    me = bpy.data.meshes.new("dam"); me.from_pydata(V, [], F); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    return me
DAM = obj(dam_mesh(), (0, 0, 0), (1, 1, 1), CONC, rough=0.7)
def crest_mesh(w0, w1, z):
    ny = 24; V = []; F = []
    for j in range(ny):
        y = YD1 * j / (ny - 1)
        V.append((xu(1) + dx(y) + w0, y, z)); V.append((xd(1) + dx(y) - w1, y, z))
    for j in range(ny - 1):
        F.append((2 * j, 2 * j + 1, 2 * j + 3, 2 * j + 2))
    me = bpy.data.meshes.new("crest"); me.from_pydata(V, [], F); me.update(); return me
ROAD = obj(crest_mesh(0.15, 0.15, ZD1 + 0.02), (0, 0, 0), (1, 1, 1), "4a4a4e", rough=0.8)
ARCHLINE = obj(crest_mesh(0.45, 0.45, ZD1 + 0.06), (0, 0, 0), (1, 1, 1), "ffd23a", emit=3.0)
# construction blocks (columns rising in lifts)
NL = 11
DZL = HD / NL
COLY = [(0, 2.3), (2.3, 4.6), (4.6, 6.9), (6.9, 9.2), (9.2, YD1)]
OFF = [0.0, 0.12, 0.05, 0.17, 0.08]
HOTM = [mat(CONC if k == 0 else "d9c7aa", 0.7, 0, 0.7 * k / 10, ecol="ff5a10", name=f"hot{k}") for k in range(11)]
BLOCKS = []
for j, (y0, y1) in enumerate(COLY):
    yc = (y0 + y1) / 2
    for i in range(NL):
        hm = (i + 0.5) / NL
        z0 = ZD0 + i * DZL; z1 = z0 + DZL - 0.06
        o = ubox(xu(hm) + dx(yc), xd(hm) + dx(yc), y0 + (0.03 if j else 0.0), y1 - 0.03, z0, z1, CONC, rough=0.7)
        o["ij"] = (i, j); BLOCKS.append(o)
# cooling pipes in the cut face of the front column
PIPEM = mat("5fd8ff", 0.3, 0.2, 2.5)
PIPES = []
for i in range(NL):
    hm = (i + 0.5) / NL; zc = ZD0 + i * DZL + DZL / 2
    a, b = xu(hm) + 0.4, xd(hm) - 0.4
    PIPES.append(obj(M_CYL, ((a + b) / 2, -0.02, zc), (0.16, 0.16, b - a), m=PIPEM, rot=(0, math.pi / 2, 0)))
PIPES.append(obj(M_CYL, (xu(0.5) + 0.35, -0.02, (ZD0 + ZD1) / 2), (0.16, 0.16, HD - 1.4), m=PIPEM))
PFLOW = [sph((0, 0, 0), (0.17, 0.17, 0.17), "e8fbff", emit=4.0) for _ in range(26)]

# ---------------------------------------------------------------- lake (strips that follow the curved upstream face)
def lake_mesh():
    ny = 24; V = []; F = []
    pts = [(X0, 0.03)] + [(-5.95 + dx(0.03 + (FY - 0.03) * j / (ny - 1)), 0.03 + (FY - 0.03) * j / (ny - 1)) for j in range(ny)] + [(X0, FY)]
    n = len(pts)
    for z in (0.0, 1.0):
        for (x, y) in pts: V.append((x, y, z))
    F.append(tuple(reversed(range(n)))); F.append(tuple(range(n, 2 * n)))
    for i in range(n):
        j = (i + 1) % n
        F.append((i, j, n + j, n + i))
    me = bpy.data.meshes.new("lake"); me.from_pydata(V, [], F); me.update()
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    return me
LAKEO = obj(lake_mesh(), (0, 0, 0), (1, 1, 1), m=WMAT)
LAKE = [(LAKEO, 0, 0, 0)]
def set_lake(level):
    LAKEO.scale = (1, 1, max(0.001, level))

# intake towers (front one cut in half, hollow)
TW_X = -12.5
TOWER = obj(M_CYL, (TW_X, 0.0, 11.25), (2.3, 2.3, 22.5), "d8d2c4", rough=0.6)
TOWER_IN = cutter(0.72); TOWER_IN.location = (TW_X, 0, 11.6); TOWER_IN.scale = (1.44, 1.44, 23.5)
boolcut(TOWER, TOWER_IN); boolcut(TOWER, HALF)
TCAP = obj(M_CYL, (TW_X, 0.0, 22.8), (3.0, 3.0, 0.6), "e8e2d4", rough=0.6); boolcut(TCAP, HALF)
TOP2 = obj(M_CYL, (TW_X, 0.0, 23.6), (1.6, 1.6, 1.0), "e8e2d4", rough=0.6); boolcut(TOP2, HALF)
TOWER2 = empty((TW_X - 0.5, 9.6, 0))
cyl((0, 0, 11.25), (2.3, 2.3, 22.5), "d8d2c4", TOWER2, rough=0.6)
cyl((0, 0, 22.8), (3.0, 3.0, 0.6), "e8e2d4", TOWER2, rough=0.6)
cyl((0, 0, 23.6), (1.6, 1.6, 1.0), "e8e2d4", TOWER2, rough=0.6)
sph((0, 0, 24.2), (1.4, 1.4, 0.9), "e8e2d4", TOWER2, rough=0.6)
# penstock (steel pipe, half-sectioned) from tower base to the turbines
PR = 0.55
PPTS = [(TW_X, 0.2), (TW_X, -6.6), (13.3, -6.6), (13.3, -1.3)]
PCUT = [cutter(PR + 0.06) for _ in range(3)]
for c_ in PCUT:
    for r_ in ROCKS: boolcut(r_, c_)
PPIPE = []
for i in range(3):
    o = obj(M_CYL, (0, 0, 0), (1, 1, 1), "7d8790", metal=0.7, rough=0.35)
    seg_place(o, PPTS[i], PPTS[i + 1], 1.0, r=PR, extra=2 * PR)
    ci = cutter(PR - 0.12); seg_place(ci, PPTS[i], PPTS[i + 1], 1.0, r=PR - 0.12, extra=2 * PR + 0.5)
    boolcut(o, ci); boolcut(o, HALF); PPIPE.append(o)
PFLOW2 = [sph((0, 0, 0), (0.17, 0.17, 0.17), "bfe6ff", m=WFOAM) for _ in range(34)]
PPATH = [(TW_X + 0.1, 18.0)] + PPTS
PSEG = [(Vector((PPATH[i][0], 0, PPATH[i][1])), Vector((PPATH[i + 1][0], 0, PPATH[i + 1][1]))) for i in range(len(PPATH) - 1)]
PLEN = sum((b - a).length for a, b in PSEG)
def ppath(q):
    s = q * PLEN
    for a, b in PSEG:
        L = (b - a).length
        if s <= L: return a + (b - a).normalized() * s + Vector((0, -0.05, 0))
        s -= L
    return PSEG[-1][1]

# powerhouse at the toe, sectioned at y=0
PH0, PH1, PHZ0, PHZ1 = 12.3, 16.6, -1.5, 4.8
PHC = "e0d8c8"
PHP = [ubox(PH0, PH1, 0, FY - 0.2, PHZ0, PHZ0 + 0.3, "9a9a9a"),
       ubox(PH1 - 0.35, PH1, 0, FY - 0.2, PHZ0 + 0.3, PHZ1 - 0.4, PHC),
       ubox(PH0, PH0 + 0.35, 0, FY - 0.2, PHZ0 + 0.3, PHZ1 - 0.4, PHC),
       ubox(PH0, PH1, FY - 0.6, FY - 0.2, PHZ0 + 0.3, PHZ1 - 0.4, PHC),
       ubox(PH0 - 0.1, PH1 + 0.1, 0, FY - 0.2, PHZ1 - 0.4, PHZ1, "cfc6b4")]
for k in range(5):
    PHP.append(ubox(PH1 + 0.0, PH1 + 0.05, 1.0 + k * 2.0, 2.0 + k * 2.0, 1.6, 3.4, "9fd8ff", rough=0.1))
GENS = []
for y in (1.7, 4.6, 7.5):
    g = empty(((PH0 + PH1) / 2 + 0.1, y, PHZ0 + 0.3))
    cyl((0, 0, 0.5), (2.3, 2.3, 1.0), "4b5563", g, metal=0.5, rough=0.4)
    cyl((0, 0, 1.6), (1.9, 1.9, 1.3), "e3a82b", g, rough=0.4)
    rot_ = empty((0, 0, 2.35), g)
    cyl((0, 0, 0), (1.5, 1.5, 0.2), "c0392b", rot_, rough=0.4)
    box((0, 0, 0.13), (1.4, 0.2, 0.06), "ffffff", rot_)
    GENS.append((g, rot_))
_pl = bpy.data.lights.new("phl", "POINT"); _pl.energy = 0; _pl.color = (1.0, 0.9, 0.75); _pl.shadow_soft_size = 1.0
PHL = bpy.data.objects.new("phl", _pl); col("site").objects.link(PHL); PHL.location = (14.4, 3.0, 3.6)
# power line to the canyon rim
PYL = empty((15.0, 15.5, ZTOP))
box((0, 0, 3.0), (0.35, 0.35, 6.0), "3a3f47", PYL, metal=0.6)
box((0, 0, 5.6), (2.6, 0.25, 0.25), "3a3f47", PYL, metal=0.6)
LA, LB = Vector((15.0, 6.0, PHZ1)), Vector((15.0, 15.5, ZTOP + 5.6))
dl = LB - LA
WIRE = obj(M_CYL, (LA + LB) / 2, (0.07, 0.07, dl.length), "222222", rot=(-math.atan2(dl.y, dl.z), 0, 0))
SPARK = [sph((0, 0, 0), (0.22, 0.22, 0.22), "ffe14d", emit=8.0) for _ in range(8)]

# spillway on the canyon-wall ledge
SPW = [ubox(SPX0 + 0.5, SPX1, FY + 0.4, SPY1 - 0.4, SPZ, SPZ + 0.25, "d0cabd", rough=0.6),
       ubox(SPX0 + 0.5, SPX1, FY + 0.15, FY + 0.4, SPZ, SPZ + 0.45, "d0cabd", rough=0.6),
       ubox(SPX0 + 0.5, SPX1, SPY1 - 0.4, SPY1 - 0.15, SPZ, SPZ + 0.9, "d0cabd", rough=0.6),
       ubox(SPX1 - 0.05, SPX1 + 0.02, FY + 0.5, SPY1 - 0.5, SPZ + 0.1, SPZ + 2.2, "1a1410", rough=0.9)]
SPWATER = wbox(SPX0 + 0.5, SPX1 - 0.05, FY + 0.4, SPY1 - 0.4, SPZ + 0.25, SPZ + 0.55)
SFLOW = [sph((0, 0, 0), (0.45, 0.45, 0.3), "e8fbff", m=WFOAM) for _ in range(30)]
OUTW = wbox(23.0, X1, 0.03, 1.4, -0.2, 0.75)

# arrows
ARM = mat("39b6ff", 0.4, 0, 2.5)
def arrow(tip, L, rot, color_m=ARM):
    a = empty(tip, rot=rot)
    obj(M_CONE, (0, 0, -0.35), (0.8, 0.8, 0.7), m=color_m, parent=a)
    obj(M_CYL, (0, 0, -0.7 - L / 2), (0.3, 0.3, L), m=color_m, parent=a)
    return a
PRESS = []
for z in (17.5, 14.5, 11.5, 8.5, 5.5, 2.5):
    h = (z - ZD0) / HD
    L = 0.4 + 4.0 * (19.2 - z) / 19.2
    PRESS.append((arrow((xu(h) - 0.15, -0.35, z), L, (0, math.pi / 2, 0)), z))
PUSH = []
for y in (1.0, 3.5, 6.0, 8.5, 10.4):
    PUSH.append(arrow((xu(0.93) + dx(y) - 0.3, y, 20.0), 2.2, (0, math.pi / 2, 0)))
YM = mat("ffd23a", 0.4, 0, 3.0)
WEIGHT = arrow((2.0, 5.5, ZD1 + 1.2), 3.0, (math.pi, 0, 0), YM)
BASEBAR = [ubox(xu(0) + 0.1, xd(0) - 0.3, -0.12, -0.02, ZD0 + 0.5, ZD0 + 0.72, "ffd23a", emit=3.0),
           ubox(xu(0) + 0.1, xu(0) + 0.32, -0.12, -0.02, ZD0 + 0.2, ZD0 + 1.4, "ffd23a", emit=3.0),
           ubox(xd(0) - 0.52, xd(0) - 0.3, -0.12, -0.02, ZD0 + 0.2, ZD0 + 1.4, "ffd23a", emit=3.0)]

# ---------------------------------------------------------------- per-frame state
ANCH = {"tunnel": (2.0, 0.0, -8.5), "coffer": (-14.0, 0.0, 2.4), "dry": (4.0, 5.0, 0.0), "grout": (GX, 0.0, -4.2),
        "blocks": (3.0, 0.0, 8.0), "pipes": (1.0, 0.0, 6.6), "lake": (-21.0, 5.0, 19.2), "base": (2.5, 0.0, ZD0 + 0.6),
        "press": None, "arch": (xu(1) + dx(6.0), 6.0, ZD1), "weight": (2.0, 5.5, ZD1 + 1.2), "tower": (TW_X, 0.0, 24.0),
        "turbines": (14.5, 1.7, 1.4), "spill": (-11.0, 12.8, SPZ + 0.5), "outlet": (24.5, 0.0, 0.4), "gate": (-25.7, 0.0, 0.6),
        "dam": (4.0, 0.0, 6.0), "bedrock": (-2.5, 0.0, -9.0), "tflow": (6.0, 0.0, -9.2), "front": None}
FRONT = [Vector((0, 0, 0))]
ANCH["press"] = (xu((2.5 - ZD0) / HD) - 0.3, -0.35, 2.5)

def update(t):
    CAMTIME[0] = t
    shot, u = shot_at(t)
    apply_shot(shot, VIS_EXTRA)
    st = stage(t)
    fin = st["fin"]; built = st["built"]
    # tunnel digging (fraction of whole path)
    s = st["dig"] * TLEN
    for i, (a, b, L) in enumerate(TSEG):
        fr = max(0.0, min(1.0, s / L)); s -= L
        seg_place(TCUT[i], a, b, fr, extra=0.0 if fr < 1 else 2 * TR)
        if seg_place(LINER[i], a, b, fr, r=TR - 0.02, extra=0.0 if fr < 1 else 2 * TR):
            LINER[i].hide_render = False
            seg_place(LINER_IN[i], a, b, fr, extra=1.0 + 2 * TR)
        else:
            LINER[i].hide_render = True
    # dust at the digging face
    front = tpath(min(1, st["dig"])); FRONT[0] = front
    for i, d in enumerate(DUSTP):
        on = shot == "tunnels" and 0.02 < st["dig"] < 0.99
        d.hide_render = not on
        if on:
            ph = (t * 1.7 + i / len(DUSTP)) % 1.0
            d.location = front + Vector((math.sin(i * 2.1) * 0.6, -0.2 - ph * 0.6, 0.5 + ph * 0.9))
            sc = 0.2 + 0.5 * ph; d.scale = (sc, sc, sc)
    # tunnel water
    tw_on = (not fin) and (S(3) <= t < W(8, "closed"))
    spill = shot == "spill"
    for i, (a, b, L) in enumerate(TSEG):
        if tw_on: tw_place(TWATER[i], a, b, min(1.0, st["div"] * 1.6 - i * 0.25) if t < S(4) else 1.0)
        elif spill and i >= 1: tw_place(TWATER[i], a, b, 1.0, depth=0.8)
        else: TWATER[i].hide_render = True
    for i, p in enumerate(TFLOW):
        on = tw_on and shot in ("divert", "grout") or spill
        p.hide_render = not on
        if on:
            q = (t * 0.22 + i / len(TFLOW)) % 1.0
            if spill: q = 0.35 + 0.65 * q
            p.location = tpath(q)
    GATE.hide_render = not (fin or t >= S(8))
    gz = 0.0 if (fin or t >= S(9)) else (1 - st["gate"]) * 3.0
    GATE.location = (-25.7, 0.62, -0.75 + gz)
    # cofferdams + river
    cof = st["div"] if t < S(8) else 0.0
    for c_ in COF:
        c_.hide_render = cof < 0.02 or fin
        c_.scale = (FY, 5.0, 3.2 * cof); c_.location.z = 1.6 * cof
    up_lvl = 0.6 + 0.5 * st["div"]
    set_ext(R_UP, X0, -16, 0.03, FY, 0, up_lvl) if (st["fill"] <= 0.001 and not fin) else setattr(R_UP, "hide_render", True)
    mid = 0.6 * (1 - st["div"]) if t < S(4) else 0.0
    set_ext(R_MID, -16, PIT_X1, 0.03, FY, 0, mid) if not fin else setattr(R_MID, "hide_render", True)
    R_MID2.hide_render = not (fin or built or t < S(3) + 0.3)
    # excavation of the riverbed gravel
    e = st["exc"]
    set_ext(G_P, PIT_X0, PIT_X1, 0, FY, -1.5, -1.5 + 1.5 * (1 - e))
    # grout curtain
    dr = st["drill"]; gr = st["grt"]
    for d_, w_ in zip(GROUT_D, GROUT_W):
        L = 4.1 * dr
        d_.hide_render = dr < 0.01 or gr > 0.99
        d_.scale = (0.34, 0.34, max(0.01, L)); d_.location.z = -1.5 - L / 2 + 0.05
        Lw = 4.1 * gr
        w_.hide_render = gr < 0.01
        w_.scale = (0.36, 0.36, max(0.01, Lw)); w_.location.z = -5.6 + Lw / 2
    set_ext(CURTAIN, GX - 0.45, GX + 0.45, -0.03, 0.02, -5.6, -5.6 + 4.1 * gr)
    hide(RIG, shot != "grout")
    RIG.location.z = -1.5 + (0.0 if e > 0.99 else 1.5 * (1 - e))
    # dam blocks
    show_blocks = (not fin) and S(5) - 0.1 <= t < S(8) - 0.1
    p = st["blk"]
    for o in BLOCKS:
        i, j = o["ij"]
        if not show_blocks: o.hide_render = True; continue
        q = max(0.0, min(1.0, (p - OFF[j]) / (1 - 0.17)))
        nl = int(q * NL + 1e-4)
        o.hide_render = i >= nl
        age = (p - (OFF[j] + (i + 1) / NL * 0.83))
        if shot == "blocks":
            hk = 3 if age < 0.06 else 1
        else:
            hk = 2 + 8 * st["heat"]
            hk = hk * (1 - st["cool"])
        o.material_slots[0].material = HOTM[int(max(0, min(10, round(hk))))]
    pipes_on = (not fin) and shot == "cool" and t >= S(7) - 0.05
    pk = ease((t - S(7) + 0.05) / 0.8)
    for i, o in enumerate(PIPES):
        o.hide_render = not pipes_on or (i < NL and i / NL > pk)
    for i, f_ in enumerate(PFLOW):
        f_.hide_render = not pipes_on
        if pipes_on:
            li = i % NL; hm = (li + 0.5) / NL; zc = ZD0 + li * DZL + DZL / 2
            a, b = xu(hm) + 0.5, xd(hm) - 0.5
            ph = (t * 0.45 + i * 0.37) % 1.0
            f_.location = (a + (b - a) * ph, -0.1, zc)
    DAM.hide_render = not built
    ROAD.hide_render = not built
    ARCHLINE.hide_render = shot != "arch"
    # lake
    lvl = 19.2 if fin else (0.6 + (19.2 - 0.6) * st["fill"] if t >= S(8) - 0.1 else 0.0)
    lvl += 1.2 * st["flood"]
    for o, y0, y1, kz in LAKE:
        o.hide_render = lvl <= 0.01
    if lvl > 0.01: set_lake(lvl)
    # towers, penstock, powerhouse
    for o in (TOWER, TCAP, TOP2): o.hide_render = not built
    hide(TOWER2, not built)
    for i, c_ in enumerate(PCUT):
        if built: seg_place(c_, PPTS[i], PPTS[i + 1], 1.0, extra=2 * PR)
        else: seg_place(c_, PPTS[i], PPTS[i + 1], 0.0)
    for o in PPIPE: o.hide_render = not built
    for o in PHP: o.hide_render = not built
    for g, r_ in GENS:
        hide(g, not built)
        r_.rotation_euler = (0, 0, t * (6.0 if shot in ("power", "hook", "ask", "spill") else 1.5))
    _pl.energy = 350 if built else 0
    power_on = shot == "power"
    for i, f_ in enumerate(PFLOW2):
        f_.hide_render = not power_on
        if power_on: f_.location = ppath((t * 0.16 + i / len(PFLOW2)) % 1.0)
    hide(PYL, not built); WIRE.hide_render = not built
    for i, sp in enumerate(SPARK):
        on = power_on and t > W(11, "electricity") - 0.6
        sp.hide_render = not on
        if on: sp.location = LA.lerp(LB, (t * 0.5 + i / len(SPARK)) % 1.0)
    # spillway
    for o in SPW: o.hide_render = not built
    SPWATER.hide_render = not spill
    if spill: set_ext(SPWATER, SPX0 + 0.5, SPX1 - 0.05, FY + 0.4, SPY1 - 0.4, SPZ + 0.25, SPZ + 0.25 + 0.4 * st["flood"] + 0.01)
    for i, f_ in enumerate(SFLOW):
        f_.hide_render = not spill or st["flood"] < 0.3
        if spill:
            ph = (t * 0.35 + i / len(SFLOW)) % 1.0
            if ph < 0.15: f_.location = (SPX0 + 1.0 + ph * 10, FY - 0.6 + ph / 0.15 * 1.6, SPZ + 0.5)
            else: f_.location = (SPX0 + 2.5 + (ph - 0.15) / 0.85 * (SPX1 - SPX0 - 3.2), FY + 1.0 + (i % 4) * 0.7, SPZ + 0.55)
    OUTW.hide_render = not spill
    # arrows
    for a, z in PRESS:
        on = shot == "shape" and t >= W(9, "water") - 0.2 + (17.5 - z) * 0.05
        hide(a, not on)
    for a in PUSH: hide(a, shot != "arch")
    hide(WEIGHT, not (shot == "arch" and t >= W(10, "weight") - 0.15))
    for o in BASEBAR: o.hide_render = not (shot == "shape" and t >= W(9, "six") - 0.1)
    # cameras (section at y=0, camera at y<0)
    if shot == "hook":
        k = ease(u / 4.4)
        cam(vl((30, -30, 27), (24, -26, 22), k), vl((-2.0, 4.0, 4.0), (-1.0, 4.0, 5.0), k), 20)
    elif shot == "tunnels":
        fp = tpath(min(1, st["dig"]))
        fx_ = max(-24.5, min(18.0, fp.x)); fz_ = max(-6.5, fp.z - 1.0)
        cam((fx_ + 3.5, -8.0, fz_ + 0.8), (fx_ + 0.5, 1.0, fz_ - 1.3), 22)
    elif shot == "divert":
        k = ease(u / 3.4)
        cam(vl((19, -19, 8), (17, -18, 7), k), (-3, 4, -3.0), 22)
    elif shot == "grout":
        k = ease(u / 4.8)
        cam(vl((0.5, -12, 2.5), (-1.5, -10.5, 0.5), k), (GX, 2.5, -3.2), 22)
    elif shot == "blocks":
        k = ease(u / 4.3)
        cam(vl((20, -20, 18), (17, -18, 17), k), (2.0, 5, 7.0), 22)
    elif shot == "cool":
        k = ease(u / 7.7)
        cam(vl((12, -19, 9), (7, -16, 7), k), (2.5, 1.0, 7.5), 22)
    elif shot == "lake":
        k = ease(u / 3.1)
        cam(vl((-9, -26, 12), (-11, -28, 15), k), (-15, 4, 3.5), 22)
    elif shot == "shape":
        k = ease(u / 4.8)
        cam(vl((3, -28, 7), (2, -26, 7), k), (2.0, 4, 6.5), 22)
    elif shot == "arch":
        k = ease(u / 3.1)
        cam(vl((18, -21, 44), (14, -19, 45), k), (-1.0, 6.0, 15.0), 22)
    elif shot == "power":
        k = ease(u / 4.3)
        cam(vl((-1, -31, 6), (3, -29, 5), k), (0.5, 3, 2.0), 20)
    elif shot == "spill":
        k = ease(u / 2.8)
        cam(vl((3, -7, 31), (-1, -9, 33), k), (-11, 12, 20), 22)
    else:  # ask
        k = ease(u / 2.6)
        cam(vl((26, -28, 20), (32, -38, 26), k), (-1, 5, 5), 22)
    return shot

LBL_DIR = os.path.join(EP, "labels")
os.makedirs(LBL_DIR, exist_ok=True)
def after_frame(f, t):
    out = {}
    pts = dict(ANCH); pts["front"] = tuple(FRONT[0])
    for nm, p in pts.items():
        v = world_to_camera_view(scn, CAM, Vector(p))
        out[nm] = [round(v.x, 4), round(1 - v.y, 4), round(v.z, 3)]
    json.dump(out, open(os.path.join(LBL_DIR, f"f{f:05d}.json"), "w"))

if __name__ == "__main__":
    run(update, VIS_EXTRA, after_frame)
