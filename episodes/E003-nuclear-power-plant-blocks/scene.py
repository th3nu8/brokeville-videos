"""Explainer E003 — How a nuclear power plant works, built from blocks (original voxel style, no game assets)."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pipeline"))
from lib import *
from bpy_extras.object_utils import world_to_camera_view

SHOT_LIGHT = {s: "day" for s in ("hook", "pellet", "core", "fission", "rods", "loop", "steam", "turbine", "condenser", "tower")}
SHOT_FSTOP = {"hook": 8, "pellet": 2.0, "core": 4.0, "fission": 2.8, "rods": 4.0, "loop": 5.6, "steam": 4.0, "turbine": 4.0,
              "condenser": 4.0, "tower": 8}
LIGHTS["day"] = ("3f8ff0", "cfe9ff", "c8dcf5", 0.95, 4.2, "fff2df", (math.radians(50), math.radians(6), math.radians(-32)))
VIS_EXTRA = {s: {"plant"} for s in SHOT_LIGHT}
VIS_EXTRA["pellet"] = {"pellet"}
VIS_EXTRA["fission"] = {"fission"}
setup_shots(SHOT_LIGHT, SHOT_FSTOP)
random.seed(11)

# ---------------------------------------------------------------- block material (edge lines + subtle pixel noise)
_bm = {}
def block_mat(h, emit=0.0, rough=0.75, ecol=None):
    key = (h, emit, rough, ecol)
    if key in _bm: return _bm[key]
    m = bpy.data.materials.new("blk_" + h); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; L = nt.links
    b = n.get("Principled BSDF"); b.inputs["Roughness"].default_value = rough
    tc = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    absd = []
    for ax in ("X", "Y", "Z"):
        f = n.new("ShaderNodeMath"); f.operation = "FRACT"; L.new(sep.outputs[ax], f.inputs[0])
        s_ = n.new("ShaderNodeMath"); s_.operation = "SUBTRACT"; s_.inputs[1].default_value = 0.5; L.new(f.outputs[0], s_.inputs[0])
        a_ = n.new("ShaderNodeMath"); a_.operation = "ABSOLUTE"; L.new(s_.outputs[0], a_.inputs[0]); absd.append(a_)
    def op(o, x, y):
        q = n.new("ShaderNodeMath"); q.operation = o; L.new(x.outputs[0], q.inputs[0]); L.new(y.outputs[0], q.inputs[1]); return q
    mx = op("MAXIMUM", op("MAXIMUM", absd[0], absd[1]), absd[2]); mn = op("MINIMUM", op("MINIMUM", absd[0], absd[1]), absd[2])
    sm = op("ADD", op("ADD", absd[0], absd[1]), absd[2]); mid = op("SUBTRACT", op("SUBTRACT", sm, mx), mn)
    edge = n.new("ShaderNodeMapRange"); edge.inputs["From Min"].default_value = 0.44; edge.inputs["From Max"].default_value = 0.49
    L.new(mid.outputs[0], edge.inputs["Value"])
    vm = n.new("ShaderNodeVectorMath"); vm.operation = "SCALE"; vm.inputs["Scale"].default_value = 6.0; L.new(tc.outputs["Object"], vm.inputs[0])
    fl = n.new("ShaderNodeVectorMath"); fl.operation = "FLOOR"; L.new(vm.outputs[0], fl.inputs[0])
    wn = n.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "3D"; L.new(fl.outputs[0], wn.inputs["Vector"])
    f1 = n.new("ShaderNodeMath"); f1.operation = "MULTIPLY_ADD"; f1.inputs[1].default_value = 0.16; f1.inputs[2].default_value = 0.92
    L.new(wn.outputs["Value"], f1.inputs[0])
    f2 = n.new("ShaderNodeMath"); f2.operation = "MULTIPLY_ADD"; f2.inputs[1].default_value = -0.32; f2.inputs[2].default_value = 1.0
    L.new(edge.outputs["Result"], f2.inputs[0])
    ff = op("MULTIPLY", f1, f2)
    col_ = n.new("ShaderNodeVectorMath"); col_.operation = "SCALE"; col_.inputs[0].default_value = hexc(h)
    L.new(ff.outputs[0], col_.inputs["Scale"]); L.new(col_.outputs[0], b.inputs["Base Color"])
    if emit > 0:
        b.inputs["Emission Color"].default_value = (*hexc(ecol or h), 1); b.inputs["Emission Strength"].default_value = emit
    _bm[key] = m; return m

def vox(cells, name="vox", parent=None, origin=(0, 0, 0)):
    """cells: {(x,y,z): (hex, emit)} -> one merged mesh object; each cell spans [x,x+1] relative to origin"""
    me = bpy.data.meshes.new(name); verts, faces, fmat = [], [], []
    keys = {}
    mats = []
    for (x, y, z), (h, e) in cells.items():
        if (h, e) not in keys: keys[(h, e)] = len(mats); mats.append(block_mat(h, e))
        mi = keys[(h, e)]
        for (dx, dy, dz, quad) in ((1, 0, 0, [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]), (-1, 0, 0, [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
                                   (0, 1, 0, [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]), (0, -1, 0, [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
                                   (0, 0, 1, [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]), (0, 0, -1, [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)])):
            if (x + dx, y + dy, z + dz) in cells: continue
            base = len(verts)
            verts += [(x + a, y + b_, z + c) for (a, b_, c) in quad]
            faces.append((base, base + 1, base + 2, base + 3)); fmat.append(mi)
    me.from_pydata(verts, [], faces); me.update()
    for m in mats: me.materials.append(m)
    for p, mi in zip(me.polygons, fmat): p.material_index = mi
    o = bpy.data.objects.new(name, me); col(CUR[0]).objects.link(o); o.location = origin
    if parent is not None: o.parent = parent
    return o

def bl(x, y, z, sx, sy, sz, h, emit=0.0, parent=None):
    """single animated block-ish box with the block material"""
    o = obj(rbox_mesh(sx, sy, sz, r=0.02), (x, y, z), (1, 1, 1), parent=parent, m=block_mat(h, emit))
    return o

def jit(hs):
    return random.choice(hs)
GRASS = ["5fa83a", "58a035", "66b041"]; DIRT = ["8a5a34", "7f5230", "93613a"]; STONE = ["7d7d7d", "868686", "737373"]
CONC = ["c9c9c4", "c2c2bd", "d0d0cb"]; STEEL = ["8a96a3", "828e9b", "93a0ad"]

# ================================================================ PLANT
CUR[0] = "plant"
CUT = 12            # cutaway: blocks with y < CUT removed for interior structures
cells = {}
for x in range(-8, 70):
    for y in range(0, 30):
        for z in range(-5, 0):
            h = jit(GRASS) if z == -1 else (jit(DIRT) if z >= -3 else jit(STONE))
            cells[(x, y, z)] = (h, 0.0)
pad = {}
for x in range(-1, 44):
    for y in range(4, 22):
        pad[(x, y, -1)] = (jit(CONC), 0.0)
for k in pad: cells.pop(k, None)
GROUND = vox(cells, "ground")
PAD = vox(pad, "pad")

def cyl_cells(cx, cy, r_in, r_out, z0, z1, hs, cut=None, dome=False):
    out = {}
    for z in range(z0, z1):
        rr_out = r_out(z) if callable(r_out) else r_out
        rr_in = r_in(z) if callable(r_in) else r_in
        R = int(math.ceil(rr_out)) + 1
        for x in range(cx - R, cx + R + 1):
            for y in range(cy - R, cy + R + 1):
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if rr_in <= d < rr_out and (cut is None or y >= cut):
                    out[(x, y, z)] = (jit(hs), 0.0)
    return out

# containment building with dome (cut)
RC = (8, 14)
cont = cyl_cells(RC[0], RC[1], 7.0, 8.0, 0, 12, CONC, cut=CUT)
for z in range(12, 20):
    r = 8.0 * math.sqrt(max(0.0, 1 - ((z - 11.5) / 8.0) ** 2))
    cont.update(cyl_cells(RC[0], RC[1], max(0, r - 1.2), r, z, z + 1, CONC, cut=CUT))
CONT = vox(cont, "containment")
# reactor vessel (steel, cut)
vess = cyl_cells(RC[0], RC[1], 2.6, 3.6, 1, 10, STEEL, cut=CUT)
vess.update(cyl_cells(RC[0], RC[1], 0, 3.6, 0, 1, STEEL, cut=CUT))
VESSEL = vox(vess, "vessel")
# core water glow at the back of the vessel
GLOW = vox({(x, y, z): ("4fd8ff", 2.5) for x in range(RC[0] - 2, RC[0] + 3) for y in (RC[1] + 2,) for z in range(1, 8)}, "coreglow")
# fuel rods (rise in during 'core'), control rods (drop in during 'rods')
FUEL = [vox({(0, 0, z): ("3e7d3e", 1.2) for z in range(0, 6)}, "fuel", origin=(RC[0] - 2 + i * 2, CUT, 1)) for i in range(3)]
for f_ in FUEL:
    for m in f_.data.materials: pass
CROD = [vox({(0, 0, z): ("3a3a3a", 0.0) for z in range(0, 7)}, "crod", origin=(RC[0] - 1 + i * 2, CUT, 9)) for i in range(2)]
# primary loop pipes: hot (red) at z=7, cold (blue) at z=3, from vessel to steam generator
SG = (20, 14)
hot = {(x, CUT, 7): ("d64541", 0.6) for x in range(RC[0] + 4, SG[0] - 2)}
cold = {(x, CUT, 3): ("3d7fd6", 0.4) for x in range(RC[0] + 4, SG[0] - 2)}
HOT = vox(hot, "hotleg"); COLD = vox(cold, "coldleg")
# steam generator (cut)
sgc = cyl_cells(SG[0], SG[1], 1.6, 2.6, 0, 13, STEEL, cut=CUT)
SGEN = vox(sgc, "steamgen")
UTUBE = vox({(x, CUT, z): ("d64541", 0.5) for x in (SG[0] - 1, SG[0]) for z in range(2, 8)}, "utube")
# steam line to turbine hall
sline = {}
for z in range(13, 15): sline[(SG[0], CUT, z)] = ("e8e8e8", 0.0)
for x in range(SG[0], 27): sline[(x, CUT, 15)] = ("e8e8e8", 0.0)
for z in range(7, 15): sline[(27, CUT, z)] = ("e8e8e8", 0.0)
SLINE = vox(sline, "steamline")
# turbine hall walls (cut front), roof slab partially
hall = {}
for x in range(25, 44):
    for z in range(0, 11):
        hall[(x, 21, z)] = (jit(CONC), 0.0)
for y in range(CUT, 22):
    for z in range(0, 11):
        hall[(25, y, z)] = (jit(CONC), 0.0); hall[(43, y, z)] = (jit(CONC), 0.0)
for x in range(25, 44):
    for y in range(CUT + 3, 22):
        hall[(x, y, 11)] = (jit(["6d8fb3", "6a8aae"]), 0.0)
HALL = vox(hall, "hall")
# turbine: shaft + rotating blade discs (separate object so it can spin)
TURB = empty((28, CUT + 1.5, 6.5))
for i, x in enumerate(range(0, 8, 2)):
    r = 1.5 + i * 0.5
    disc = {}
    R = int(r) + 1
    for yy in range(-R, R):
        for zz in range(-R, R):
            if math.hypot(yy + 0.5, zz + 0.5) < r: disc[(x, yy, zz)] = ("b8c2cc" if (yy + zz) % 2 else "9aa6b2", 0.0)
    vox(disc, "disc", parent=TURB)
vox({(x, -1, -1): ("555555", 0.0) for x in range(-1, 15)} | {(x, 0, -1): ("555555", 0.0) for x in range(-1, 15)} |
    {(x, -1, 0): ("555555", 0.0) for x in range(-1, 15)} | {(x, 0, 0): ("555555", 0.0) for x in range(-1, 15)}, "shaft", parent=TURB)
# generator housing (green) with copper coil glimpses
gen = {}
for x in range(36, 42):
    for y in range(CUT, CUT + 4):
        for z in range(3, 10):
            if (y == CUT and 4 <= z <= 8 and 37 <= x <= 40): gen[(x, y, z)] = ("c87533", 0.4)
            else: gen[(x, y, z)] = (jit(["2f7d4f", "2b744a"]), 0.0)
GEN = vox(gen, "generator")
# condenser below turbine
cond = {(x, y, z): (jit(["5f8fbf", "5a89b8"]), 0.0) for x in range(27, 35) for y in range(CUT, CUT + 4) for z in range(0, 3)}
COND = vox(cond, "condenser")
# cooling water pipe to tower
cw = {(x, CUT, 0): ("3d7fd6", 0.3) for x in range(35, 52)}
CWP = vox(cw, "coolpipe")
# cooling tower (hyperboloid, cut)
CT = (56, 15)
ctc = cyl_cells(CT[0], CT[1], lambda z: 4.2 + 2.4 * ((z - 13) / 13.0) ** 2 - 1.0, lambda z: 4.2 + 2.4 * ((z - 13) / 13.0) ** 2, 0, 24, CONC, cut=CT[1] - 1)
TOWER = vox(ctc, "tower")
TWATER = vox({(x, y, 0): ("3d7fd6", 0.3) for x in range(CT[0] - 5, CT[0] + 6) for y in range(CT[1] - 1, CT[1] + 6) if math.hypot(x + 0.5 - CT[0], y + 0.5 - CT[1]) < 5.5}, "twater")
VAPOR = [bl(0, 0, 0, 1.6, 1.6, 1.6, "f4f6f8") for _ in range(26)]
# power lines + houses
for px in (46, 54, 62):
    vox({(0, 0, z): ("6f6f6f", 0.0) for z in range(0, 9)} | {(dx, 0, 9): ("6f6f6f", 0.0) for dx in (-1, 0, 1)}, "pylon", origin=(px, 4, 0))
WIRES = [bl((44 + 62) / 2, 4.5, 9.2 + k * 0.0, 18.5, 0.12, 0.12, "222222") for k in range(1)]
HOUSES = []
for i, (hx, hy) in enumerate(((60, 22), (64, 22), (60, 26), (66, 26))):
    hc = {}
    for x in range(0, 3):
        for y in range(0, 3):
            for z in range(0, 3): hc[(x, y, z)] = (jit(["c9a27a", "b8916a"]), 0.0)
    for x in range(0, 3):
        for y in range(0, 3): hc[(x, y, 3)] = (jit(["a63d32", "9a382e"]), 0.0)
    vox(hc, "house", origin=(hx, hy, 0))
    w = bl(hx + 1.5, hy - 0.02, 1.5, 0.9, 0.06, 0.9, "ffd36b", emit=0.0)
    HOUSES.append(w)
# trees + clouds
for i in range(14):
    tx = random.choice([random.randint(-7, -2), random.randint(44, 68)]); ty = random.randint(18, 28)
    t_ = {(0, 0, z): ("6b4a2b", 0.0) for z in range(0, 3)}
    for x in range(-1, 2):
        for y in range(-1, 2):
            for z in range(3, 6): t_[(x, y, z)] = (jit(["3d8f36", "357f2f", "449c3c"]), 0.0)
    vox(t_, "tree", origin=(tx, ty, 0))
for (cx, cy, cz) in ((-10, 60, 34), (30, 70, 40), (70, 65, 36)):
    vox({(x, y, 0): ("ffffff", 0.0) for x in range(0, 10) for y in range(0, 5) if random.random() > 0.15}, "cloud", origin=(cx, cy, cz))
# flow particles
def path_pts(pts, n):
    segs = []
    for a, b in zip(pts[:-1], pts[1:]): segs.append((Vector(a), Vector(b)))
    total = sum((b - a).length for a, b in segs)
    def at(u):
        d = (u % 1.0) * total
        for a, b in segs:
            Lg = (b - a).length
            if d <= Lg: return a.lerp(b, d / Lg)
            d -= Lg
        return segs[-1][1]
    return at
P_HOT = path_pts([(RC[0] + 2.5, CUT - 0.1, 7.5), (SG[0] - 1.5, CUT - 0.1, 7.5)], 0)
P_COLD = path_pts([(SG[0] - 1.5, CUT - 0.1, 3.5), (RC[0] + 2.5, CUT - 0.1, 3.5)], 0)
P_STEAM = path_pts([(SG[0] + 0.5, CUT - 0.1, 9), (SG[0] + 0.5, CUT - 0.1, 15.5), (27.5, CUT - 0.1, 15.5), (27.5, CUT - 0.1, 8), (35, CUT + 1.5, 6.5)], 0)
P_COND = path_pts([(30, CUT - 0.1, 4.5), (30, CUT - 0.1, 1.5), (34, CUT - 0.1, 1.5)], 0)
P_CW = path_pts([(35, CUT - 0.1, 0.5), (51.5, CUT - 0.1, 0.5)], 0)
PART = {k: [bl(0, 0, 0, 0.45, 0.45, 0.45, c, emit=e) for _ in range(n)] for k, c, e, n in
        (("hot", "ff5a3c", 2.0, 8), ("cold", "5aa8ff", 1.5, 8), ("steam", "ffffff", 0.6, 16), ("cond", "5aa8ff", 1.2, 6), ("cw", "5aa8ff", 1.2, 10))}
_cl = bpy.data.lights.new("core", "POINT"); _cl.energy = 0; _cl.color = (0.45, 0.85, 1.0); _cl.shadow_soft_size = 1.0
CORE_L = bpy.data.objects.new("core", _cl); col("plant").objects.link(CORE_L); CORE_L.location = (RC[0] + 0.5, CUT - 1.0, 4.5)
_hl = bpy.data.lights.new("hall", "AREA"); _hl.energy = 1500; _hl.size = 12; _hl.color = (1.0, 0.95, 0.85)
HALL_L = bpy.data.objects.new("hall", _hl); col("plant").objects.link(HALL_L); HALL_L.location = (34, CUT + 4, 10.5)

# ================================================================ PELLET (micro set in the sky)
CUR[0] = "pellet"
PZ = 200
vox({(x, y, z): (jit(STONE), 0.0) for x in range(-2, 2) for y in range(-2, 2) for z in range(-2, 0)}, "pedestal", origin=(0, 0, PZ))
PELLET = obj(M_CYL, (0.0, 0.0, PZ + 0.45), (0.8, 0.8, 0.9), "4a4f46", rough=0.45, metal=0.3)
PEL_GLOW = obj(M_CYL, (0.0, 0.0, PZ + 0.45), (0.86, 0.86, 0.82), "b6ff7a", emit=0.0)
coal = {}
for z in range(0, 5):
    for x in range(-5 + z, 6 - z):
        for y in range(-4 + z, 5 - z):
            coal[(x, y, z)] = (jit(["262626", "2e2e2e", "1f1f1f"]), 0.0)
COAL_LAYERS = []
for z in range(0, 5):
    COAL_LAYERS.append(vox({k: v for k, v in coal.items() if k[2] == z}, "coal", origin=(10, 6, PZ - 2)))
vox({(x, y, z): (jit(GRASS if z == -1 else DIRT), 0.0) for x in range(-8, 18) for y in range(-6, 16) for z in range(-4, -2) if not (-2 <= x < 2 and -2 <= y < 2)}, "pelletisle", origin=(0, 0, PZ))

# ================================================================ FISSION (micro set)
CUR[0] = "fission"
FX = (0, 0, 400)
def nucleus(r=2.6):
    c = {}
    R = int(r) + 1
    for x in range(-R, R):
        for y in range(-R, R):
            for z in range(-R, R):
                if math.hypot(x + 0.5, y + 0.5, z + 0.5) < r:
                    c[(x, y, z)] = (random.choice(["d9534f", "f0ad4e"]), 0.6)
    left = {k: v for k, v in c.items() if k[0] < 0}; right = {k: v for k, v in c.items() if k[0] >= 0}
    return left, right
ATOMS = []
for i, p in enumerate(((0, 0, 0), (8, 2, 4), (8, -1, -4), (16, 0, 2), (16, 3, -3))):
    l, r = nucleus()
    e = empty((FX[0] + p[0], FX[1] + p[1], FX[2] + p[2]))
    L_ = vox(l, "half", parent=e); R_ = vox(r, "half", parent=e)
    ATOMS.append((e, L_, R_))
NEUT = [bl(0, 0, 0, 0.5, 0.5, 0.5, "7fe7ff", emit=4.0) for _ in range(10)]
FLASH = [obj(M_SPH, (0, 0, 0), (1, 1, 1), "fff2b0", emit=8.0) for _ in range(5)]

# ================================================================ timing + animation
T_PEL, T_COAL = S(2), W(3, "holds")
T_CORE0, T_CORE1 = S(4), W(4, "core")
T_FIS = S(5)
T_ROD0, T_ROD1 = W(6, "slide"), W(6, "steady")
T_LOOP = S(7)
T_STEAM = S(8)
T_TURB, T_ELEC = S(9), W(9, "electricity")
T_COND = S(10)
T_TOWER = S(11)

def flows(t, on):
    for k, at in (("hot", P_HOT), ("cold", P_COLD), ("steam", P_STEAM), ("cond", P_COND), ("cw", P_CW)):
        ps = PART[k]
        for i, o in enumerate(ps):
            o.hide_render = k not in on
            if k in on:
                o.location = at(t * (0.35 if k != "steam" else 0.25) + i / len(ps))

def update(t):
    CAMTIME[0] = t
    shot, u = shot_at(t)
    apply_shot(shot, VIS_EXTRA)
    fin = shot in ("hook", "tower") or t >= T_TURB
    # fuel rods rise in during the core line
    for i, f_ in enumerate(FUEL):
        k = 1.0 if (shot == "hook" or t >= T_CORE1 + i * 0.3 + 0.6) else ease((t - T_CORE0 - i * 0.3) / 1.6)
        f_.location.z = 1 + (1 - k) * -7.0
        f_.hide_render = k <= 0.001
    # control rods: up until 'slide', then drop in
    kr = 1.0 if shot == "hook" or t >= T_ROD1 else ease((t - T_ROD0) / (T_ROD1 - T_ROD0))
    for c in CROD:
        c.location.z = 9 - kr * 7
    reacting = shot == "hook" or t >= T_CORE1
    _cl.energy = 0 if not reacting else (1600 if kr < 0.5 else 900) * (1 + 0.08 * math.sin(t * 9))
    GLOW.hide_render = not reacting
    # flows
    on = set()
    if shot in ("hook", "tower"): on = {"hot", "cold", "steam", "cond", "cw"}
    elif shot == "loop": on = {"hot", "cold"}
    elif shot == "steam": on = {"hot", "cold", "steam"}
    elif shot == "turbine": on = {"steam"}
    elif shot == "condenser": on = {"steam", "cond", "cw"}
    elif shot in ("core", "rods"): on = set()
    flows(t, on)
    # turbine spin
    spin = 0.0
    if shot in ("hook", "tower", "condenser"): spin = 9.0
    elif shot == "turbine": spin = 9.0 * ease((t - T_TURB) / 2.0)
    TURB.rotation_euler = (t * spin * 0.9 if spin else 0.0, 0, 0)
    if shot == "turbine": TURB.rotation_euler = (sum(9.0 * ease((x - T_TURB) / 2.0) for x in [t]) * (t - T_TURB) * 0.6, 0, 0)
    # houses light up on 'electricity'
    lit = shot in ("hook", "tower", "condenser") or t >= T_ELEC
    for w in HOUSES: w.material_slots[0].material = block_mat("ffd36b", 4.0 if lit else 0.0)
    # vapor from the tower
    for i, v in enumerate(VAPOR):
        on_v = shot in ("hook", "tower", "condenser")
        v.hide_render = not on_v
        if on_v:
            random.seed(500 + i)
            ph = (t * 0.12 + i / len(VAPOR)) % 1.0
            v.location = (CT[0] + random.uniform(-3, 3) + ph * 6, CT[1] + 2 + random.uniform(-3, 3), 24 + ph * 18)
            s_ = 1.0 + ph * 2.2 - max(0, ph - 0.75) * 9
            v.scale = (max(0.05, s_),) * 3
    # pellet set
    if shot == "pellet":
        PEL_GLOW.hide_render = True
        PELLET.rotation_euler = (0, 0, t * 0.6)
        for i, Lr in enumerate(COAL_LAYERS):
            k = ease((t - T_COAL - i * 0.12) / 0.3)
            Lr.hide_render = k <= 0.001; Lr.scale = (1, 1, max(0.001, k))
    # fission set: atom 0 hit by neutron, splits; neutrons hit atoms 1,2 then 3,4
    if shot == "fission":
        v = t - T_FIS
        hits = [0.9, 2.1, 2.1, 3.3, 3.3]
        for i, (e, Lh, Rh) in enumerate(ATOMS):
            d = max(0.0, v - hits[i])
            Lh.location = (-d * 1.8, 0, d * 0.3); Rh.location = (d * 1.8, 0, -d * 0.3)
            Lh.rotation_euler = (0, d * 0.8, 0); Rh.rotation_euler = (0, -d * 0.8, 0)
            fl = FLASH[i]; fl.location = e.location
            s_ = 2.2 * math.exp(-d * 5) if v >= hits[i] else 0.0
            fl.scale = (max(0.001, s_),) * 3; fl.hide_render = s_ < 0.02
        # neutrons
        srcs = [((-8, 0, 0), 0, -0.3, 0.9)] + [(None, 0, hits[0], hits[1]), (None, 0, hits[0], hits[2]), (None, 1, hits[1], hits[3]), (None, 2, hits[2], hits[4])]
        tg = [0, 1, 2, 3, 4]
        for j, n_ in enumerate(NEUT):
            n_.hide_render = True
        for j, (p0, src_i, ta, tb) in enumerate(srcs):
            n_ = NEUT[j]
            a = Vector(p0) + Vector(FX) if p0 else Vector(ATOMS[src_i][0].location)
            b = Vector(ATOMS[tg[j]][0].location)
            if ta <= v <= tb + 0.05:
                n_.hide_render = False; n_.location = a.lerp(b, (v - ta) / max(0.01, tb - ta))
        for j in range(5, 10):
            n_ = NEUT[j]; i = j - 5
            if v >= hits[3] + 0.1:
                d = v - hits[3]; e = ATOMS[3 + (i % 2)][0].location
                n_.hide_render = False; n_.location = Vector(e) + Vector((d * 4, (i - 2) * d * 1.5, (i % 3 - 1) * d * 1.2))
    # cameras
    X0 = RC[0]
    if shot == "hook":
        k = ease(u / 3.4)
        cam(vl((44, -26, 24), (36, -30, 20), k), vl((26, 14, 4), (25, 14, 5), k), 30)
    elif shot == "pellet":
        k = ease(u / 8.0)
        if t < T_COAL - 0.2:
            cam(vl((1.6, -4.2, PZ + 1.6), (2.2, -5.5, PZ + 2.0), ease(u / 4)), (0, 0, PZ + 0.5), 40)
        else:
            w_ = ease((t - T_COAL + 0.2) / 1.6)
            cam(vl((2.2, -5.5, PZ + 2.0), (-3, -22, PZ + 7), w_), vl((0, 0, PZ + 0.5), (5, 3, PZ), w_), 34)
    elif shot == "core":
        k = ease(u / 4.3)
        cam(vl((X0 + 9, -6, 12), (X0 + 4, -2, 7), k), (X0 + 0.5, CUT + 1, 4.5), 30)
    elif shot == "fission":
        k = ease(u / 5.7)
        cam(vl((-3, -11, FX[2] + 3), (9, -14, FX[2] + 2), k), vl((0, 0, FX[2]), (9, 1, FX[2]), k), 30)
    elif shot == "rods":
        k = ease(u / 4.5)
        cam(vl((X0 + 3, -3, 9), (X0 + 1, -4, 7), k), (X0 + 0.5, CUT + 1, 5.5), 30)
    elif shot == "loop":
        k = ease(u / 3.6)
        cam(vl((14, -12, 12), (15, -11, 9), k), (14, CUT, 5), 30)
    elif shot == "steam":
        k = ease(u / 3.2)
        cam(vl((SG[0] + 6, -8, 10), (SG[0] + 4, -9, 13), k), (SG[0] + 0.5, CUT, 9), 30)
    elif shot == "turbine":
        k = ease(u / 5.8)
        cam(vl((30, -9, 9), (42, -12, 11), k), vl((31, CUT + 1, 6), (40, CUT + 1, 6), k), 28)
    elif shot == "condenser":
        k = ease(u / 3.3)
        cam(vl((31, -8, 5), (38, -10, 6), k), (32, CUT + 1, 2), 30)
    else:  # tower
        k = ease(u / 5.4)
        cam(vl((58, -18, 12), (44, -34, 24), k), vl((56, 15, 16), (36, 14, 8), k), 30)
    return shot

ANCH = {"pellet": (0, 0, PZ + 0.95), "coal": (10.5, 6.5, PZ + 3.2), "core": (RC[0] + 0.5, CUT, 7.5), "rods": (RC[0] + 0.5, CUT, 9.5),
        "loop": (14, CUT, 7.5), "sg": (SG[0] + 0.5, CUT, 12.5), "turbine": (30, CUT, 9), "generator": (39, CUT, 10.2),
        "condenser": (31, CUT, 3.2), "tower": (CT[0] - 3, CT[1] - 1, 20), "vapor": (CT[0] + 2, CT[1] + 2, 30), "houses": (62, 22, 4.5),
        "neutron": (FX[0] - 4, FX[1], FX[2])}
LBL_DIR = os.path.join(EP, "labels"); os.makedirs(LBL_DIR, exist_ok=True)
def after_frame(f, t):
    out = {}
    for nm, p in ANCH.items():
        v = world_to_camera_view(scn, CAM, Vector(p))
        out[nm] = [round(v.x, 4), round(1 - v.y, 4), round(v.z, 3)]
    json.dump(out, open(os.path.join(LBL_DIR, f"f{f:05d}.json"), "w"))

if __name__ == "__main__":
    run(update, VIS_EXTRA, after_frame)
