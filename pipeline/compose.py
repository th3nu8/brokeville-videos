"""Final video: graded/bloomed frames (render/ 432x768) -> 1080x1920, captions, episode overlays, audio -> final.mp4
usage: EP=<episode dir> python3 compose.py [out.mp4] [t0] [t1]
Episode hooks come from <EP>/fx.py (see episodes/001-*/fx.py for the full API).
"""
import math, subprocess, sys, os, importlib.util
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance, ImageChops
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing import *

spec = importlib.util.spec_from_file_location("fx", os.path.join(EP, "fx.py")); fx = importlib.util.module_from_spec(spec); spec.loader.exec_module(fx)

W_, H_, FPS = 1080, 1920, 24
RW, RH = 432, 768
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(EP, "final.mp4")
T0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
T1 = float(sys.argv[3]) if len(sys.argv) > 3 else END
FP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Montserrat[wght].ttf")
_fc = {}
def font(sz, var="Black"):
    k = (sz, var)
    if k not in _fc:
        f = ImageFont.truetype(FP, sz); f.set_variation_by_name(var); _fc[k] = f
    return _fc[k]

# ---------- captions: groups of <=3 words, active word yellow (HOT words red), "slash X" -> "/X"
words = [dict(w) for l in TL["lines"] for w in l["words"]]
merged, i = [], 0
while i < len(words):
    w = words[i]
    if w["w"].lower() == "slash" and i + 1 < len(words):
        n = words[i + 1]; merged.append({"w": "/" + n["w"], "s": w["s"], "e": n["e"]}); i += 2; continue
    merged.append(w); i += 1
groups, cur = [], []
for w in merged:
    cur.append(w)
    if len(cur) >= 3 or w["w"].endswith((".", "!", "?", ",", "...")):
        groups.append(cur); cur = []
if cur: groups.append(cur)
G = []
for gi, g in enumerate(groups):
    s = g[0]["s"]; e = groups[gi + 1][0]["s"] if gi + 1 < len(groups) else g[-1]["e"] + 0.6
    if e - g[-1]["e"] > 0.5: e = g[-1]["e"] + 0.35
    G.append({"w": g, "s": s, "e": e})
HOT = set(getattr(fx, "HOT", set()))

def draw_text(d, xy, txt, f, fill, stroke=11, shadow=True):
    x, y = xy
    if shadow: d.text((x + 5, y + 8), txt, font=f, fill=(0, 0, 0), stroke_width=stroke + 1, stroke_fill=(0, 0, 0))
    d.text((x, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))

def captions(img, t):
    g = next((g for g in G if g["s"] <= t < g["e"]), None)
    if not g: return
    ws = g["w"]; act = max([i for i, w in enumerate(ws) if w["s"] <= t] or [0])
    age = t - g["s"]; pop = 0.82 + 0.18 * min(1, age / 0.09) + 0.05 * math.sin(min(1, age / 0.16) * math.pi)
    sz = int(90 * pop); f = font(sz)
    tx = [w["w"].upper().replace("...", "…") for w in ws]
    sp = f.getlength(" "); wd = [f.getlength(x) for x in tx]
    lines, ln, lw = [], [], 0
    for i, w in enumerate(wd):
        add = w + (sp if ln else 0)
        if ln and lw + add > W_ * 0.86: lines.append(ln); ln, lw = [], 0; add = w
        ln.append(i); lw += add
    if ln: lines.append(ln)
    lh = int(sz * 1.15); y0 = int(H_ * 0.63) - lh * len(lines) // 2
    d = ImageDraw.Draw(img)
    for pas in (0, 1):
        for li, ln in enumerate(lines):
            x = (W_ - (sum(wd[i] for i in ln) + sp * (len(ln) - 1))) / 2; y = y0 + li * lh
            for i in ln:
                a = i == act
                col = (255, 222, 33) if a else (255, 255, 255)
                if a and ws[i]["w"].lower().strip(".,!?") in HOT: col = (255, 80, 60)
                if pas == 0: d.text((x + 5, y + 8), tx[i], font=f, fill=(0, 0, 0), stroke_width=12, stroke_fill=(0, 0, 0))
                else: d.text((x, y), tx[i], font=f, fill=col, stroke_width=11, stroke_fill=(0, 0, 0))
                x += wd[i] + sp

class UI:
    W, H = W_, H_
    font = staticmethod(font)
    @staticmethod
    def center_text(img, txt, y, sz, fill, scale=1.0, stroke=12):
        f = font(int(sz * scale)); d = ImageDraw.Draw(img)
        w = f.getlength(txt); draw_text(d, ((W_ - w) / 2, y), txt, f, fill, stroke)
    @staticmethod
    def pill(img, xy, txt, sz, fg, bg, pad=18):
        d = ImageDraw.Draw(img); f = font(sz, "ExtraBold")
        w = f.getlength(txt); x, y = xy
        d.rounded_rectangle([x, y, x + w + pad * 2, y + sz + pad * 1.4], radius=16, fill=bg)
        d.text((x + pad, y + pad * 0.55), txt, font=f, fill=fg)
    @staticmethod
    def dialog(img, title, lines, button, y0=520):
        """generic dark game-style popup box"""
        d = ImageDraw.Draw(img); bw, bh = 820, 380; x0 = (W_ - bw) // 2
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=28, fill=(30, 32, 38), outline=(255, 255, 255), width=4)
        f1 = font(60, "ExtraBold"); f2 = font(40, "SemiBold")
        tw = f1.getlength(title); d.text(((W_ - tw) / 2, y0 + 50), title, font=f1, fill=(255, 255, 255))
        for li, s_ in enumerate(lines):
            tw = f2.getlength(s_); d.text(((W_ - tw) / 2, y0 + 150 + li * 56), s_, font=f2, fill=(200, 205, 215))
        if button:
            d.rounded_rectangle([W_ / 2 - 150, y0 + 280, W_ / 2 + 150, y0 + 350], radius=14, fill=(255, 255, 255))
            tw = f2.getlength(button); d.text(((W_ - tw) / 2, y0 + 290), button, font=f2, fill=(30, 32, 38))

PUNCH = fx.punches() if hasattr(fx, "punches") else []
SHAKES = fx.shakes() if hasattr(fx, "shakes") else []
STUTTER = fx.stutters() if hasattr(fx, "stutters") else []
GRAY_FROM = fx.grayscale_from() if hasattr(fx, "grayscale_from") else None
HEADER = getattr(fx, "HEADER", None)
END_TEXT = fx.end_text() if hasattr(fx, "end_text") else None

def punch(t):
    z, sx = 1.0, 0.0
    for tp, a in PUNCH:
        if t >= tp: z += a * math.exp(-(t - tp) * 6)
    for tb in SHAKES:
        if tb <= t < tb + 0.4: sx += math.sin(t * 90) * 14 * math.exp(-(t - tb) * 8)
    return z, sx

def load(fi):
    p = os.path.join(EP, "render", f"f{fi:05d}.png")
    if not os.path.exists(p): return None
    return Image.open(p).convert("RGB")

_vig = None
def vignette():
    global _vig
    if _vig is None:
        m = Image.new("L", (RW, RH), 0); d = ImageDraw.Draw(m)
        for i in range(60):
            k = i / 60
            d.ellipse([-RW * 0.25 + k * RW * 0.2, -RH * 0.2 + k * RH * 0.15, RW * 1.25 - k * RW * 0.2, RH * 1.2 - k * RH * 0.15], fill=int(255 * (k ** 0.6)))
        _vig = m.filter(ImageFilter.GaussianBlur(30))
    return _vig

def grade(img):
    hi = img.point(lambda v: int(max(0, v - 222) * 2.2))
    glow = Image.blend(hi.filter(ImageFilter.GaussianBlur(10)), hi.filter(ImageFilter.GaussianBlur(28)), 0.5)
    img = ImageChops.add(img, glow, scale=1.0)
    img = ImageEnhance.Color(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    dark = ImageEnhance.Brightness(img).enhance(0.72)
    return Image.composite(img, dark, vignette())

def frame(fi):
    t = fi / FPS
    src = fi
    for (a, b) in STUTTER:  # laggy freeze-frame effect
        if a <= t < b:
            src = int(a * FPS) + int(((t - a) * FPS) // 7) * 7
    img = load(src)
    if img is None: img = load(src - 1) or Image.new("RGB", (RW, RH))
    img = grade(img)
    if GRAY_FROM is not None and t >= GRAY_FROM:
        k = min(1.0, (t - GRAY_FROM) / 0.4)
        img = Image.blend(img, ImageOps.grayscale(img).convert("RGB"), k * 0.85)
        img = ImageEnhance.Brightness(img).enhance(1 - 0.25 * k)
    z, sx = punch(t)
    if z != 1 or sx:
        cw, ch = RW / z, RH / z; cx, cy = RW / 2 - sx / 2.5, RH / 2
        img = img.transform((RW, RH), Image.EXTENT, (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2), Image.BICUBIC)
    img = img.resize((W_, H_), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2.2, percent=60, threshold=2))
    if HEADER and t < 4.0:
        a = 0.6 + 0.4 * min(1, t / 0.2)
        UI.center_text(img, HEADER[0], 250, 74, (255, 255, 255), a)
        UI.center_text(img, HEADER[1], 340, 86, (255, 222, 33), a)
    if hasattr(fx, "overlays"):
        fx.overlays(img, t, UI)
    if END_TEXT and t >= END_TEXT[1] - 0.05:
        k = min(1, (t - END_TEXT[1]) / 0.15)
        UI.center_text(img, END_TEXT[0], 1250, 150, (255, 222, 33), 0.6 + 0.4 * k, 16)
    else:
        captions(img, t)
    return img

def main():
    n0, n1 = int(T0 * FPS), int(T1 * FPS)
    enc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W_}x{H_}", "-r", str(FPS), "-i", "-",
                            "-ss", str(T0), "-i", os.path.join(EP, "mix.wav"), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-ar", "44100", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for fi in range(n0, n1):
        enc.stdin.write(frame(fi).tobytes())
    enc.stdin.close(); enc.wait()
    print("wrote", OUT, n1 - n0)

if __name__ == "__main__":
    main()
