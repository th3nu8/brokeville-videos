"""Brokeville render library: Cycles setup, rounded-plastic primitives, R15-style avatars, props, lighting, camera, render loop.
Episode scene.py does `from lib import *`, builds its sets with at()/CUR, defines SHOT_LIGHT, SHOT_FSTOP, VIS_EXTRA and update(t), then calls run(update).
usage (via render.py): EP=<episode dir> python3 scene.py <start> <end> [rx ry outdir samples]
"""
import bpy, bmesh, math, json, sys, os, random
from mathutils import Vector

EP = os.environ.get("EP") or os.getcwd()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
FPS = 24
F0 = int(sys.argv[1]) if len(sys.argv) > 1 else 0
F1 = int(sys.argv[2]) if len(sys.argv) > 2 else -1
RX = int(sys.argv[3]) if len(sys.argv) > 3 else 540
RY = int(sys.argv[4]) if len(sys.argv) > 4 else 960
OUTDIR = sys.argv[5] if len(sys.argv) > 5 else os.path.join(EP, "render")
SAMPLES = int(sys.argv[6]) if len(sys.argv) > 6 else 8

from timing import *

# ------------------------------------------------------------------ render setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.engine = "CYCLES"
cy = scn.cycles
cy.device = "CPU"; cy.samples = SAMPLES; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.06
cy.use_denoising = True
try: cy.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
try:
    cy.denoising_quality = "FAST"; cy.denoising_prefilter = "NONE"
except Exception: pass
cy.max_bounces = 3; cy.diffuse_bounces = 2; cy.glossy_bounces = 1; cy.transmission_bounces = 0
cy.volume_bounces = 0; cy.transparent_max_bounces = 2; cy.caustics_reflective = False; cy.caustics_refractive = False
cy.blur_glossy = 1.0
scn.render.use_persistent_data = True
if os.environ.get("THREADS"):
    scn.render.threads_mode = "FIXED"; scn.render.threads = int(os.environ["THREADS"])
scn.render.resolution_x = RX; scn.render.resolution_y = RY
scn.render.image_settings.file_format = "PNG"
scn.render.image_settings.color_mode = "RGB"
scn.render.image_settings.compression = 15
try:
    scn.view_settings.view_transform = "AgX"; scn.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    try: scn.view_settings.look = "None"
    except Exception: pass
_FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
FONT = bpy.data.fonts.load(os.path.join(_FD, "Montserrat[wght].ttf"))
FONTB = bpy.data.fonts.load(os.path.join(_FD, "Poppins-Bold.ttf"))

def _mk(name, fn, smooth=False):
    bm = bmesh.new(); fn(bm)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = smooth
    return me
M_CYL = _mk("cyl", lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=0.5, radius2=0.5, depth=1.0), smooth=True)
for p in M_CYL.polygons: p.use_smooth = abs(p.normal.z) < 0.5
M_SPH = _mk("sph", lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=0.5), smooth=True)
def _wedge():
    me = bpy.data.meshes.new("wedge")
    v = [(-.5, -.5, -.5), (.5, -.5, -.5), (.5, .5, -.5), (-.5, .5, -.5), (-.5, 0, .5), (.5, 0, .5)]
    f = [(0, 1, 2, 3), (0, 4, 5, 1), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2)]
    me.from_pydata(v, [], f); me.update(); return me
M_WEDGE = _wedge()

_rb = {}
def rbox_mesh(sx, sy, sz, r=None):
    sx, sy, sz = max(sx, 0.02), max(sy, 0.02), max(sz, 0.02)
    if r is None:
        r = min(0.09, 0.22 * min(sx, sy, sz))
    key = (round(sx, 2), round(sy, 2), round(sz, 2), round(r, 3))
    if key in _rb: return _rb[key]
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
    if r > 0.004:
        bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=r, segments=3 if r > 0.05 else 2, affect="EDGES", profile=0.5)
    me = bpy.data.meshes.new("rb"); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    try:
        me.shade_smooth_by_angle = True
    except Exception:
        pass
    _rb[key] = me
    return me

_m = {}
def hexc(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x ** 2.2 for x in c)
def mat(h, rough=0.42, metal=0.0, emit=0.0, ecol=None, name=None):
    key = name or (h, rough, metal, emit, ecol)
    if key in _m: return _m[key]
    m = bpy.data.materials.new(str(name or h)); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*hexc(h), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    try: b.inputs["Specular IOR Level"].default_value = 0.45
    except Exception: pass
    if emit > 0:
        b.inputs["Emission Color"].default_value = (*hexc(ecol or h), 1)
        b.inputs["Emission Strength"].default_value = emit
    _m[key] = m; return m

def studs_mat(h, name):
    """baseplate with roblox-like stud bumps"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; n = nt.nodes; L = nt.links
    b = n.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*hexc(h), 1); b.inputs["Roughness"].default_value = 0.55
    tc = n.new("ShaderNodeTexCoord"); sep = n.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    def fr(sock):
        m1 = n.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; m1.inputs[1].default_value = 1.0
        L.new(sock, m1.inputs[0])
        f = n.new("ShaderNodeMath"); f.operation = "FRACT"; L.new(m1.outputs[0], f.inputs[0])
        s = n.new("ShaderNodeMath"); s.operation = "SUBTRACT"; s.inputs[1].default_value = 0.5; L.new(f.outputs[0], s.inputs[0])
        return s
    fx, fy = fr(sep.outputs["X"]), fr(sep.outputs["Y"])
    cmb = n.new("ShaderNodeCombineXYZ"); L.new(fx.outputs[0], cmb.inputs[0]); L.new(fy.outputs[0], cmb.inputs[1])
    ln = n.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; L.new(cmb.outputs[0], ln.inputs[0])
    mr = n.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.28; mr.inputs["From Max"].default_value = 0.34
    mr.inputs["To Min"].default_value = 1.0; mr.inputs["To Max"].default_value = 0.0
    L.new(ln.outputs["Value"], mr.inputs["Value"])
    bump = n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35; bump.inputs["Distance"].default_value = 0.05
    L.new(mr.outputs["Result"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], b.inputs["Normal"])
    # subtle color variation
    noise = n.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 0.08
    L.new(tc.outputs["Object"], noise.inputs["Vector"])
    mix = n.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.inputs["Factor"].default_value = 0.12
    mix.inputs[6].default_value = (*hexc(h), 1)
    L.new(noise.outputs["Color"], mix.inputs[7])
    L.new(mix.outputs[2], b.inputs["Base Color"])
    return m

COLS = {}
CUR = ["global"]
def col(n):
    if n not in COLS:
        c = bpy.data.collections.new(n); scn.collection.children.link(c); COLS[n] = c
    return COLS[n]

def _setmat(o, m):
    if len(o.data.materials) == 0: o.data.materials.append(None)
    o.material_slots[0].link = "OBJECT"; o.material_slots[0].material = m

def obj(mesh, loc=(0, 0, 0), size=(1, 1, 1), color="cccccc", parent=None, rot=(0, 0, 0), name="o", rough=0.42, metal=0.0, emit=0.0, m=None):
    o = bpy.data.objects.new(name, mesh); col(CUR[0]).objects.link(o)
    _setmat(o, m or mat(color, rough, metal, emit))
    o.location = loc; o.scale = size; o.rotation_euler = rot
    if parent is not None: o.parent = parent
    return o
def box(loc, size, color, parent=None, rot=(0, 0, 0), r=None, **k):
    return obj(rbox_mesh(*size, r=r), loc, (1, 1, 1), color, parent, rot, "b", **k)
def cyl(loc, size, color, parent=None, rot=(0, 0, 0), **k): return obj(M_CYL, loc, size, color, parent, rot, "c", **k)
def sph(loc, size, color, parent=None, rot=(0, 0, 0), **k): return obj(M_SPH, loc, size, color, parent, rot, "s", **k)
def wedge(loc, size, color, parent=None, rot=(0, 0, 0), **k): return obj(M_WEDGE, loc, size, color, parent, rot, "w", **k)
def empty(loc=(0, 0, 0), parent=None, rot=(0, 0, 0), name="e"):
    e = bpy.data.objects.new(name, None); col(CUR[0]).objects.link(e)
    e.location = loc; e.rotation_euler = rot
    if parent is not None: e.parent = parent
    return e
def text(body, loc, size, color, parent=None, rot=(math.radians(90), 0, 0), font=None, extrude=0.03, align="CENTER", emit=0.0):
    cu = bpy.data.curves.new("t", "FONT"); cu.body = body; cu.font = font or FONTB
    cu.align_x = align; cu.align_y = "CENTER"; cu.size = size; cu.extrude = extrude; cu.bevel_depth = 0.004
    o = bpy.data.objects.new("text", cu); col(CUR[0]).objects.link(o)
    o.data.materials.append(mat(color, 0.4, 0, emit)); o.location = loc; o.rotation_euler = rot
    if parent is not None: o.parent = parent
    return o
def hide(o, h=True):
    o.hide_render = h
    for c in o.children_recursive: c.hide_render = h
def fdir(dx, dy): return math.atan2(dx, -dy)

# ------------------------------------------------------------------ R15-style avatar
SKIN = "f5cd9a"
def avatar(loc, rz=0.0, shirt="3a7bd5", pants="2b3a55", hair="4a2c17", skin=SKIN, hat=None, shades=False, patched=False, scale=1.0, face="smile", name="av", shoes="2d2d2d", sleeves=True):
    r = empty(loc, rot=(0, 0, rz), name=name); r.scale = (scale,) * 3
    a = {"root": r}
    hips = empty((0, 0, 0), r); a["hips"] = hips
    box((0, 0, 2.3), (2.0, 1.0, 0.62), pants, hips)
    torso = empty((0, 0, 2.6), hips); a["torso"] = torso
    box((0, 0, 0.72), (2.0, 1.0, 1.42), shirt, torso)
    box((0, -0.5, 1.35), (0.7, 0.06, 0.16), "ffffff" if shirt != "ffffff" else "dddddd", torso, r=0.02)  # collar accent
    if patched:
        box((0.45, -0.52, 0.45), (0.42, 0.05, 0.42), "a07850", torso, rot=(0, 0.2, 0), r=0.03)
        box((-0.5, -0.52, 0.95), (0.32, 0.05, 0.32), "6f8f4f", torso, rot=(0, -0.15, 0), r=0.03)
    legs, knees = [], []
    for sx in (-1, 1):
        pv = empty((0.5 * sx, 0, 2.05), hips)
        box((0, 0, -0.5), (0.94, 0.94, 1.0), pants, pv)
        kn = empty((0, 0, -1.0), pv)
        box((0, 0, -0.42), (0.92, 0.92, 0.84), pants, kn)
        box((0, -0.07, -0.93), (0.96, 1.12, 0.26), shoes, kn)
        if patched and sx > 0: box((0.0, -0.47, -0.3), (0.3, 0.04, 0.3), "6b5240", kn, r=0.03)
        legs.append(pv); knees.append(kn)
    a["legs"] = legs; a["knees"] = knees
    arms, elbows = [], []
    for sx in (-1, 1):
        pv = empty((1.47 * sx, 0, 1.25), torso)
        box((0, 0, -0.42), (0.9, 0.9, 0.98), shirt, pv)
        el = empty((0, 0, -0.92), pv)
        box((0, 0, -0.33), (0.88, 0.88, 0.7), shirt if sleeves else skin, el)
        box((0, 0, -0.84), (0.9, 0.9, 0.38), skin, el)
        arms.append(pv); elbows.append(el)
    a["arms"] = arms; a["elbows"] = elbows
    head = empty((0, 0, 1.45), torso); a["head"] = head
    box((0, 0, 0.62), (1.3, 1.18, 1.24), skin, head, r=0.36)
    box((0, 0, 0.0), (0.6, 0.6, 0.3), skin, head, r=0.1)  # neck
    if hair:
        box((0, 0.06, 1.16), (1.4, 1.3, 0.42), hair, head, r=0.16)
        box((0, 0.5, 0.78), (1.36, 0.42, 0.95), hair, head, r=0.15)
        for i, (x, rz_) in enumerate(((-0.42, 0.3), (0.0, -0.1), (0.42, -0.35))):
            box((x, -0.52, 1.05), (0.5, 0.34, 0.3), hair, head, rot=(0.5, 0, rz_), r=0.1)
        for sx in (-1, 1):
            box((0.66 * sx, 0.12, 0.85), (0.16, 0.9, 0.6), hair, head, r=0.06)
    eyes, pupils, brows = [], [], []
    for sx in (-1, 1):
        e = sph((0.25 * sx, -0.57, 0.68), (0.24, 0.08, 0.3), "ffffff", head, rough=0.25); eyes.append(e)
        p = sph((0.25 * sx, -0.61, 0.66), (0.14, 0.05, 0.19), "1b1b1b", head, rough=0.2); pupils.append(p)
        sph((0.25 * sx + 0.04, -0.635, 0.71), (0.05, 0.02, 0.05), "ffffff", head, emit=2.0)
        b = box((0.27 * sx, -0.6, 0.93), (0.3, 0.06, 0.08), hair or "3a2a1a", head, r=0.03); brows.append(b)
    a["eyes"] = eyes; a["pupils"] = pupils; a["brows"] = brows
    mouth = []
    for i in range(5):
        u = (i - 2) / 2
        mouth.append(box((u * 0.12, -0.6, 0.36 - (1 - u * u) * 0.06), (0.08, 0.05, 0.05), "3a1414", head, r=0.02))
    a["mouth"] = mouth
    mo = sph((0, -0.6, 0.34), (0.32, 0.06, 0.2), "4a1414", head); a["mouth_open"] = mo
    sph((0, -0.615, 0.29), (0.18, 0.03, 0.07), "e86a6a", mo); mo.scale = (0.0001,) * 3
    if shades:
        box((0, -0.64, 0.7), (0.9, 0.06, 0.26), "111111", head, metal=0.6, rough=0.15, r=0.04)
    if hat == "crown":
        cyl((0, 0, 1.48), (0.95, 0.95, 0.32), "ffc83d", head, metal=1, rough=0.22)
        for i in range(5):
            ang = i / 5 * math.tau
            box((0.42 * math.cos(ang), 0.42 * math.sin(ang), 1.74), (0.2, 0.2, 0.34), "ffc83d", head, rot=(0, 0, ang), metal=1, rough=0.22)
            sph((0.42 * math.cos(ang), 0.42 * math.sin(ang) - 0.06, 1.55), (0.12, 0.12, 0.12), "e84a4a", head, emit=0.5, rough=0.1)
    elif hat == "hardhat":
        sph((0, 0, 1.25), (1.45, 1.45, 0.9), "ffc400", head, rough=0.3); cyl((0, -0.2, 1.08), (1.75, 1.9, 0.08), "ffc400", head)
        cyl((0, -0.72, 1.45), (0.3, 0.12, 0.3), "fff6c0", head, rot=(math.pi / 2, 0, 0), emit=3.0)
    elif hat == "tophat":
        cyl((0, 0, 1.6), (0.95, 0.95, 1.0), "151515", head, rough=0.3); cyl((0, 0, 1.12), (1.5, 1.5, 0.08), "151515", head)
        cyl((0, 0, 1.25), (0.97, 0.97, 0.18), "c0392b", head)
    elif hat == "cap":
        box((0, 0.0, 1.3), (1.42, 1.35, 0.36), "e84a4a", head, r=0.14); box((0, -0.86, 1.18), (1.0, 0.65, 0.1), "e84a4a", head, r=0.04)
    return a

def set_mouth(a, kind):
    open_ = kind == "open"
    a["mouth_open"].scale = (1, 1, 1) if open_ else (0.0001,) * 3
    for i, b in enumerate(a["mouth"]):
        u = (i - 2) / 2
        b.hide_render = open_
        if kind == "smile": b.location.z = 0.36 - (1 - u * u) * 0.07
        elif kind == "sad": b.location.z = 0.26 + (1 - u * u) * 0.07
        elif kind == "flat": b.location.z = 0.3
    for i, br in enumerate(a["brows"]):
        sx = -1 if i == 0 else 1
        if kind == "sad": br.rotation_euler = (0, 0.35 * sx, 0); br.location.z = 0.95
        elif kind == "open": br.rotation_euler = (0, 0, 0); br.location.z = 1.0
        elif kind == "flat": br.rotation_euler = (0, -0.12 * sx, 0); br.location.z = 0.92
        else: br.rotation_euler = (0, 0, 0); br.location.z = 0.94

def blink(a, t, ph=0.0):
    c = ((t + ph * 1.7) % 3.3) < 0.09
    for e in a["eyes"] + a["pupils"]:
        e.scale.z = abs(e.scale.z) if not c else 0.02

def pose(a, legs=(0, 0), arms=(0, 0), arms_out=(0, 0), head=(0, 0, 0), knees=None, elbows=None, lean=0.0):
    a["legs"][0].rotation_euler = (legs[0], 0, 0); a["legs"][1].rotation_euler = (legs[1], 0, 0)
    if knees is None:
        knees = (max(0.0, -legs[0]) * 1.1 + 0.05, max(0.0, -legs[1]) * 1.1 + 0.05)
    a["knees"][0].rotation_euler = (knees[0], 0, 0); a["knees"][1].rotation_euler = (knees[1], 0, 0)
    a["arms"][0].rotation_euler = (arms[0], -arms_out[0], 0); a["arms"][1].rotation_euler = (arms[1], arms_out[1], 0)
    if elbows is None:
        elbows = (-0.25 - max(0.0, -arms[0]) * 0.25, -0.25 - max(0.0, -arms[1]) * 0.25)
    a["elbows"][0].rotation_euler = (elbows[0], 0, 0); a["elbows"][1].rotation_euler = (elbows[1], 0, 0)
    a["head"].rotation_euler = head
    a["torso"].rotation_euler = (lean, 0, 0)
    a["hips"].location.z = 0.0

def walk(a, t, speed=9.0, amp=0.7):
    s = math.sin(t * speed); c = math.cos(t * speed)
    pose(a, legs=(s * amp, -s * amp), arms=(-s * amp * 0.9, s * amp * 0.9),
         knees=(max(0, c) * amp * 1.3 + 0.05, max(0, -c) * amp * 1.3 + 0.05), lean=0.08 * min(1, amp))
    a["hips"].location.z = abs(c) * 0.12 * amp
    a["head"].rotation_euler = (-0.04, 0, s * 0.06)

def jump_pose(a, k=1.0):
    pose(a, legs=(0.6 * k, -0.4 * k), arms=(-2.7 * k, -2.7 * k), arms_out=(0.3, 0.3), knees=(1.1 * k, 0.5 * k), elbows=(-0.3, -0.3), head=(-0.15, 0, 0))

def crouch_pose(a, k=1.0):
    pose(a, legs=(-0.9 * k, -0.9 * k), arms=(0.6 * k, 0.6 * k), knees=(1.6 * k, 1.6 * k), lean=0.35 * k, head=(-0.25 * k, 0, 0))
    a["hips"].location.z = -0.55 * k

def fly_pose(a, t):
    pose(a, legs=(0.15 + math.sin(t * 6) * 0.08, 0.05 - math.sin(t * 6) * 0.08), arms=(-3.0, -0.15), arms_out=(0.0, 0.15), knees=(0.2, 0.4), elbows=(0, -0.3))

def bubble(text_, loc, parent=None, w=None, color="ffffff"):
    e = empty(loc, parent)
    w = w or max(1.2, 0.42 * len(text_) + 0.6)
    box((0, 0, 0), (w, 0.18, 1.05), color, e, r=0.25)
    wedge((0, 0, -0.62), (0.4, 0.14, 0.3), color, e, rot=(math.pi, 0, 0))
    text(text_, (0, -0.12, 0.02), 0.62, "1a1a1a", e, font=FONTB)
    return e

# ================================================================== global
CUR[0] = "global"
CAMD = bpy.data.cameras.new("cam"); CAMD.sensor_fit = "VERTICAL"; CAMD.sensor_height = 36; CAMD.lens = 28; CAMD.clip_end = 3000
CAM = bpy.data.objects.new("cam", CAMD); col("global").objects.link(CAM)
CAMT = bpy.data.objects.new("camt", None); col("global").objects.link(CAMT)
con = CAM.constraints.new("TRACK_TO"); con.target = CAMT; con.track_axis = "TRACK_NEGATIVE_Z"; con.up_axis = "UP_Y"
scn.camera = CAM
CAMD.dof.use_dof = True
CAMD.dof.focus_object = CAMT
CAMD.dof.aperture_fstop = 2.0
sun_d = bpy.data.lights.new("sun", "SUN"); sun_d.energy = 4.0; sun_d.angle = math.radians(4)
SUN = bpy.data.objects.new("sun", sun_d); col("global").objects.link(SUN)
SUN.rotation_euler = (math.radians(45), math.radians(12), math.radians(-35))
world = bpy.data.worlds.new("w"); scn.world = world
try: world.use_nodes = True
except Exception: pass
wn = world.node_tree.nodes; wl = world.node_tree.links
for n_ in list(wn): wn.remove(n_)
w_out = wn.new("ShaderNodeOutputWorld"); w_amb = wn.new("ShaderNodeBackground"); w_sky = wn.new("ShaderNodeBackground")
w_mix = wn.new("ShaderNodeMixShader"); w_lp = wn.new("ShaderNodeLightPath"); w_tc = wn.new("ShaderNodeTexCoord")
w_sep = wn.new("ShaderNodeSeparateXYZ"); w_ramp = wn.new("ShaderNodeValToRGB")
wl.new(w_tc.outputs["Window"], w_sep.inputs[0]); wl.new(w_sep.outputs["Y"], w_ramp.inputs["Fac"])
wl.new(w_ramp.outputs["Color"], w_sky.inputs["Color"]); wl.new(w_lp.outputs["Is Camera Ray"], w_mix.inputs["Fac"])
wl.new(w_amb.outputs[0], w_mix.inputs[1]); wl.new(w_sky.outputs[0], w_mix.inputs[2]); wl.new(w_mix.outputs[0], w_out.inputs["Surface"])
def set_light(top, horizon, amb, amb_s, sun_e, sun_c, sun_rot):
    w_ramp.color_ramp.elements[0].position = 0.2; w_ramp.color_ramp.elements[1].position = 1.0
    w_ramp.color_ramp.elements[0].color = (*hexc(horizon), 1); w_ramp.color_ramp.elements[1].color = (*hexc(top), 1)
    w_amb.inputs["Color"].default_value = (*hexc(amb), 1); w_amb.inputs["Strength"].default_value = amb_s
    sun_d.energy = sun_e; sun_d.color = hexc(sun_c); SUN.rotation_euler = sun_rot
DAYROT = (math.radians(42), math.radians(10), math.radians(-38))
LIGHTS = {
 "day": ("2a7fe0", "cfeeff", "bcdcff", 0.85, 4.2, "fff4e0", DAYROT),
 "dusk": ("5a4fb0", "ffb57a", "ffc49a", 0.7, 3.2, "ffb070", (math.radians(76), 0, math.radians(200))),
 "cave": ("120c08", "2a1d14", "6a5040", 0.45, 0.6, "ffd9a0", DAYROT),
 "room": ("06060c", "10101c", "202040", 0.08, 0.0, "ffffff", DAYROT),
 "high": ("0a3fa8", "dff1ff", "cfe6ff", 1.0, 4.6, "ffffff", (math.radians(35), 0, math.radians(-20))),
 "sunset": ("3a2a8a", "ffa06a", "ffb88a", 0.75, 3.4, "ff9a50", (math.radians(78), 0, math.radians(160))),
 "interior": ("2a7fe0", "cfeeff", "ffe8cc", 0.55, 2.6, "fff4e0", DAYROT),
}

_studm = {}
def baseplate(cx, cy, size=400, color="4fb34a"):
    if color not in _studm: _studm[color] = studs_mat(color, "studs_" + color)
    obj(rbox_mesh(size, size, 1, r=0), (cx, cy, -0.5), (1, 1, 1), parent=None, m=_studm[color])

def house(loc, rz, wall, roof, w=10, d=8, h=7):
    r = empty(loc, rot=(0, 0, rz))
    box((0, 0, h / 2), (w, d, h), wall, r)
    wedge((0, 0, h + 1.5), (w + 1, d + 1, 3), roof, r, rot=(0, 0, math.pi / 2))
    box((0, -d / 2 - 0.05, 2), (2, 0.2, 4), "6b3f22", r)
    for sx in (-1, 1):
        box((2.8 * sx, -d / 2 - 0.05, 4.2), (1.8, 0.2, 1.8), "9fd8ff", r)
    return r

def tree(loc, s=1.0):
    r = empty(loc)
    box((0, 0, 2 * s), (1 * s, 1 * s, 4 * s), "7a4a24", r)
    box((0, 0, 5 * s), (4.5 * s, 4.5 * s, 3.5 * s), "2f9e44", r)
    box((0, 0, 7.2 * s), (3 * s, 3 * s, 2 * s), "37b24d", r)
    return r

def cloud(loc, s=1.0):
    r = empty(loc)
    for (x, y, z, a, b, c) in ((0, 0, 0, 8, 5, 3), (4, 1, 1, 6, 4, 3.5), (-4, -1, 0.5, 5, 4, 2.5), (1, 0, 2, 5, 3.5, 2.5)):
        box((x * s, y * s, z * s), (a * s, b * s, c * s), "ffffff", r)
    return r

def spawnpad(loc, s=1.0):
    r = empty(loc)
    box((0, 0, 0.2), (8 * s, 8 * s, 0.4), "9aa0a8", r)
    cyl((0, 0, 0.42), (5 * s, 5 * s, 0.06), "3a3f47", r)
    return r


# ------------------------------------------------------------------ sets helper
SETX = {}
def at(name, x):
    CUR[0] = name; SETX[name] = x; return x

def bush(loc, s=1.0):
    r = empty(loc)
    for (x, y, z, a) in ((0, 0, 0.6, 1.6), (0.9, 0.3, 0.5, 1.2), (-0.8, -0.2, 0.5, 1.1)):
        box((x * s, y * s, z * s), (a * s, a * s, a * 0.9 * s), random.choice(["3fa34d", "2f9e44", "4cb85c"]), r, r=0.25 * s)
    if random.random() < 0.5:
        for k in range(3):
            sph((random.uniform(-0.8, 0.8) * s, -0.75 * s, random.uniform(0.6, 1.2) * s), (0.22 * s,) * 3, random.choice(["ff6b9a", "ffd34d", "ffffff"]))
    return r
def lamp(loc):
    r = empty(loc)
    cyl((0, 0, 3.5), (0.35, 0.35, 7), "2d3436", r, metal=0.6, rough=0.3)
    box((0, 0, 7.2), (1.0, 1.0, 0.8), "2d3436", r)
    box((0, 0, 6.75), (0.8, 0.8, 0.4), "fff2c0", r, emit=4.0)
    return r
def fence(p0, p1, color="ffffff"):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; n = max(2, int(d.length / 2.5))
    ang = math.atan2(d.y, d.x)
    for i in range(n + 1):
        q = p0 + d * (i / n); box((q.x, q.y, 0.9), (0.35, 0.35, 1.8), color, r=0.06)
    mid = (p0 + p1) / 2
    for z in (0.7, 1.4): box((mid.x, mid.y, z), (d.length, 0.18, 0.22), color, rot=(0, 0, ang), r=0.04)

# ------------------------------------------------------------------ animation helpers
def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def vl(a, b, x): return Vector(a).lerp(Vector(b), x)
CAMTIME = [0.0]
def cam(p, t_, lens=28):
    tt = CAMTIME[0]
    sh = Vector((math.sin(tt * 1.3) * 0.06 + math.sin(tt * 3.1) * 0.02, math.sin(tt * 1.1 + 2) * 0.04, math.sin(tt * 1.7 + 1) * 0.05 + math.sin(tt * 2.9) * 0.02))
    CAM.location = Vector(p) + sh; CAMT.location = t_; CAMD.lens = lens

def idle(a, t, ph=0):
    br = math.sin(t * 2.2 + ph)
    pose(a, legs=(0, 0), arms=(br * 0.04, -br * 0.04), arms_out=(0.06 + br * 0.02, 0.06 + br * 0.02), knees=(0.04, 0.04),
         head=(math.sin(t * 0.7 + ph) * 0.05, 0, math.sin(t * 0.9 + ph) * 0.18), lean=br * 0.015)
    a["hips"].location.z = br * 0.02
    blink(a, t, ph)

def laugh(a, t, ph=0):
    b = abs(math.sin(t * 10 + ph))
    a["root"].location.z = b * 0.35
    pose(a, legs=(0, 0), arms=(-0.6 - b * 0.3, -0.6 - b * 0.3), arms_out=(0.3, 0.3), head=(-0.3 - b * 0.2, 0, 0))
    set_mouth(a, "open")

def hop(t, period, height):
    ph = (t % period) / period
    return 4 * ph * (1 - ph) * height

def explode(a, k):
    """roblox-style break apart, k 0..1"""
    for i, ch in enumerate([a["torso"], a["head"]] + a["arms"] + a["legs"]):
        pass


def apply_shot(shot, vis_extra):
    """show only the shot's collections, set its light preset and DOF. Episode must define SHOT_LIGHT/SHOT_FSTOP dicts and pass them via setup_shots()."""
    vis = {"global", shot} | set(vis_extra.get(shot, ()))
    for n, c in COLS.items():
        c.hide_render = n not in vis
    set_light(*LIGHTS[_SHOTCFG["light"].get(shot, "day")])
    CAMD.dof.aperture_fstop = _SHOTCFG["fstop"].get(shot, 2.4)
_SHOTCFG = {"light": {}, "fstop": {}}
def setup_shots(light, fstop):
    _SHOTCFG["light"] = light; _SHOTCFG["fstop"] = fstop

def run(update, vis_extra):
    import time
    os.makedirs(OUTDIR, exist_ok=True)
    n = int(math.ceil(END * FPS))
    f1 = F1 if (F1 >= 0 and F1 <= n) else n
    only = os.environ.get("ONLY")
    frames = [int(x) for x in only.split(",")] if only else range(F0, f1)
    need = {"global"}
    for f in frames:
        sname = shot_at(f / FPS)[0]
        need |= {sname} | set(vis_extra.get(sname, ()))
    for n_, c_ in list(COLS.items()):
        if n_ not in need:
            for o_ in list(c_.objects):
                bpy.data.objects.remove(o_, do_unlink=True)
    print("KEEP", sorted(need), flush=True)
    for f in frames:
        out = f"{OUTDIR}/f{f:05d}.png"
        if os.path.exists(out) and not os.environ.get("FORCE"):
            continue
        t = f / FPS
        CAMTIME[0] = t
        shot = update(t)
        scn.render.filepath = out
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"FRAME {f} t={t:.2f} {shot} {time.time() - t0:.2f}s", flush=True)
    print("DONE", n)
