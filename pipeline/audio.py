"""Narration + procedural music (by mood sections) + sfx cues -> <EP>/mix.wav
usage: EP=<episode dir> python3 audio.py
Episode fx.py provides moods() -> [(start_time, mood)] and sfx(cue) which calls cue(name, t, gain=1.0).
moods: happy, sad, hype, mystery, eerie, silent
sfx names: whoosh, pop, boing, boing_small, blip, coin, fanfare, bonk, sizzle, thud, tapestop, glitch, rumble, reverse_whoosh
"""
import os, sys, importlib.util
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing import *
spec = importlib.util.spec_from_file_location("fx", os.path.join(EP, "fx.py")); fx = importlib.util.module_from_spec(spec); spec.loader.exec_module(fx)

SR = 44100
N = int(END * SR)
rng = np.random.default_rng(2)
def note(m): return 440 * 2 ** ((m - 69) / 12)
def add(dst, src, t, g=1.0):
    s = int(t * SR)
    if s >= len(dst) or s < 0: return
    e = min(len(dst), s + len(src)); dst[s:e] += src[:e - s] * g
def ks(freq, dur, decay=0.996):
    n = int(dur * SR); p = max(2, int(SR / freq)); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out
_c = {}
def pl(m, dur=0.45):
    if (m, dur) not in _c: _c[(m, dur)] = ks(note(m), dur)
    return _c[(m, dur)]

MAJOR = [[60, 64, 67, 72], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]
MINOR = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67], [52, 56, 59, 64]]
MOOD = {"happy": (118, MAJOR, 0.33), "sad": (84, MINOR, 0.22), "hype": (140, MAJOR, 0.4)}
music = np.zeros(N)
moods = sorted(fx.moods()) + [(END, "silent")]
for (st, mood), (en, _) in zip(moods[:-1], moods[1:]):
    if mood in MOOD:
        bpm, prog, g = MOOD[mood]; e8 = 60 / bpm / 2; t = st; i = 0
        while t < en:
            ch = prog[(i // 8) % 4]; pat = [0, 2, 1, 3, 2, 1, 3, 2]
            add(music, pl(ch[pat[i % 8]] + 12), t, g)
            if i % 4 == 0:
                tt = np.arange(int(0.5 * SR)) / SR; add(music, np.sin(2 * np.pi * note(ch[0] - 12) * tt) * np.exp(-tt * 4), t, 0.45)
            if mood == "hype" and i % 2 == 0:
                nn = int(0.05 * SR); add(music, rng.normal(0, 1, nn) * np.exp(-np.arange(nn) / SR * 80), t, 0.12)
            t += e8; i += 1
    elif mood == "mystery":
        seg = np.arange(int((en - st) * SR)) / SR; pad = np.zeros_like(seg)
        for m in (45, 52, 57, 60, 64):
            pad += np.sin(2 * np.pi * note(m) * seg) + 0.3 * np.sin(2 * np.pi * note(m) * 1.004 * seg)
        add(music, pad * np.minimum(1, seg / 0.6) * 0.05 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.4 * seg)), st)
    elif mood == "eerie":
        seg = np.arange(int((en - st) * SR)) / SR
        add(music, np.sin(2 * np.pi * note(40) * seg) * 0.08 * np.minimum(1, seg / 1.5), st)

sfx = np.zeros(N)
def whoosh(dur=0.35, lo=400, hi=3000):
    n = int(dur * SR); x = rng.normal(0, 1, n); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0; y = np.fft.irfft(X, n); return y / np.abs(y).max() * np.sin(np.linspace(0, np.pi, n)) ** 2
def boing(f0=300, f1=700, dur=0.25):
    tt = np.arange(int(dur * SR)) / SR; f = f0 + (f1 - f0) * (tt / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6)
def blip(f=880, dur=0.12):
    tt = np.arange(int(dur * SR)) / SR; return np.sin(2 * np.pi * f * tt) * np.exp(-tt * 25)
def sq(freq, dur, dec=5):
    tt = np.arange(int(dur * SR)) / SR; return np.sign(np.sin(2 * np.pi * freq * tt)) * np.exp(-tt * dec) * 0.5
tt3 = np.arange(int(0.3 * SR)) / SR
BONK = np.sin(2 * np.pi * (220 - 120 * tt3) * tt3) * np.exp(-tt3 * 12) + rng.normal(0, 1, len(tt3)) * np.exp(-tt3 * 60) * 0.4
def cue(name, t, gain=1.0):
    if name == "whoosh": add(sfx, whoosh(), t - 0.15, 0.12 * gain)
    elif name == "reverse_whoosh": add(sfx, whoosh(0.8, 100, 1200)[::-1], t - 0.6, 0.3 * gain)
    elif name == "pop": add(sfx, boing(500, 1200, 0.3), t, 0.4 * gain)
    elif name == "boing": add(sfx, boing(300, 700, 0.22), t, 0.25 * gain)
    elif name == "boing_small": add(sfx, boing(400, 600, 0.15), t, 0.35 * gain)
    elif name == "blip": add(sfx, blip(1200), t, 0.25 * gain)
    elif name == "coin": add(sfx, blip(1318, 0.1), t, 0.35 * gain); add(sfx, blip(1760, 0.2), t + 0.08, 0.35 * gain)
    elif name == "fanfare":
        for k, m in enumerate((72, 76, 79, 84)): add(sfx, sq(note(m), 0.25), t + k * 0.1, 0.12 * gain)
    elif name == "bonk": add(sfx, BONK, t, 0.8 * gain)
    elif name == "thud": add(sfx, BONK, t, 0.35 * gain)
    elif name == "sizzle":
        n = int(1.0 * SR); add(sfx, rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR * 2.5), t, 0.15 * gain)
    elif name == "tapestop":
        tt = np.arange(int(1.0 * SR)) / SR; add(sfx, np.sin(2 * np.pi * np.cumsum(300 * (1 - tt) ** 2) / SR) * np.exp(-tt * 2), t, 0.4 * gain)
    elif name == "glitch":
        n = int(1.2 * SR); g = rng.normal(0, 1, n) * (np.sin(np.arange(n) / SR * 2 * np.pi * 14) > 0)
        add(sfx, g * np.exp(-np.arange(n) / SR * 1.5), t, 0.08 * gain)
    elif name == "rumble":
        n = int(2.0 * SR); add(sfx, whoosh(2.0, 40, 300), t, 0.4 * gain)
    else:
        raise ValueError(name)
for _name, st in SHOTS[1:]:
    cue("whoosh", st)
fx.sfx(cue)

v, vsr = sf.read(os.path.join(EP, "voice", "narration.wav"))
if v.ndim > 1: v = v.mean(1)
idx = np.linspace(0, len(v) - 1, int(len(v) * SR / vsr)); v = np.interp(idx, np.arange(len(v)), v)
voice = np.zeros(N); add(voice, v, 0)
env = np.convolve(np.abs(voice), np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
duck = 1 - 0.55 * np.clip(env / 0.05, 0, 1)
mix = voice + music * 0.3 * duck + sfx * 0.6
mix = mix / np.abs(mix).max() * 0.95
fd = int(0.5 * SR); mix[-fd:] *= np.linspace(1, 0, fd)
sf.write(os.path.join(EP, "mix.wav"), mix.astype(np.float32), SR)
print("mix", round(len(mix) / SR, 2))
