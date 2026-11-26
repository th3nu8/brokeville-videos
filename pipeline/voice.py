"""Narrator: Kokoro TTS per line -> word timings -> pitched-up kid voice.
usage: EP=<episode dir> python3 voice.py [voice=af_heart] [speed=1.0] [pitch=1.0]
Natural mode (default): consecutive lines with the same "shot" (max 3) are read in ONE pass so the intonation
flows like a real narrator; word/line timings inside a passage are estimated from word lengths and punctuation.
pitch != 1.0 applies a rubberband pitch shift (only for character voices); pitch == 1.0 applies a light
"room" polish (EQ, gentle compression, tiny early reflections) that takes the dry/robotic edge off.
Best-sounding Kokoro voices: af_heart (A), af_bella (A-), then af_nicole, bf_emma; male: am_michael / am_fenrir (C+).
Reads <EP>/script.json {"title", "lines":[{"id","shot","text","pre"(optional pause before, s)}]}
Writes <EP>/voice/narration.wav and <EP>/voice/timeline.json. Prints total length (must be >= 120 s).
Model files: ~/kokoro/kokoro-v1.0.onnx and voices-v1.0.bin (see RUNBOOK setup).
"""
import json, sys, re, os, subprocess
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

EP = os.environ.get("EP") or os.getcwd()
voice = sys.argv[1] if len(sys.argv) > 1 else "af_heart"
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
pitch = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
MD = os.path.expanduser("~/kokoro")
k = Kokoro(f"{MD}/kokoro-v1.0.onnx", f"{MD}/voices-v1.0.bin")
script = json.load(open(os.path.join(EP, "script.json")))
os.makedirs(os.path.join(EP, "voice"), exist_ok=True)
SR = 24000; GAP = 0.18
out, t, timeline = [], 0.0, []
def trim(a, thr=0.01):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0: return a
    return a[max(0, idx[0] - int(0.03 * SR)): min(len(a), idx[-1] + int(0.06 * SR))]
def weights(words):
    w = []
    for x in words:
        core = re.sub(r"[^A-Za-z0-9']", "", x); wt = 0.12 + 0.065 * len(core)
        if x.endswith("..."): wt += 0.35
        elif x.endswith((".", "!", "?")): wt += 0.2
        elif x.endswith(","): wt += 0.12
        w.append(wt)
    return np.array(w)
lines = script["lines"]
passages, cur_p = [], []
for ln in lines:
    if cur_p and (ln["shot"] != cur_p[-1]["shot"] or len(cur_p) >= 3 or float(ln.get("pre", 0)) >= 0.3):
        passages.append(cur_p); cur_p = []
    cur_p.append(ln)
if cur_p: passages.append(cur_p)
for pg in passages:
    pre = float(pg[0].get("pre", 0))
    if pre: out.append(np.zeros(int(pre * SR), dtype=np.float32)); t += pre
    text = " ".join(l["text"] for l in pg)
    samples, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
    a = trim(np.asarray(samples, dtype=np.float32)); dur = len(a) / SR
    words_all, owner = [], []
    for li, l in enumerate(pg):
        ws = l["text"].split(); words_all += ws; owner += [li] * len(ws)
    w = weights(words_all)
    for i in range(len(words_all)):
        if i + 1 < len(words_all) and owner[i + 1] != owner[i]: w[i] += 0.12   # sentence gap inside passage
    w = w / w.sum() * dur
    cur = t; per = {li: [] for li in range(len(pg))}
    for word, d, li in zip(words_all, w, owner):
        per[li].append({"w": word, "s": round(cur, 3), "e": round(cur + d, 3)}); cur += d
    for li, l in enumerate(pg):
        wl = per[li]
        timeline.append({"id": l["id"], "shot": l["shot"], "start": wl[0]["s"], "end": wl[-1]["e"], "words": wl})
    out.append(a); out.append(np.zeros(int(GAP * SR), dtype=np.float32)); t += dur + GAP
audio = np.concatenate(out); audio = audio / max(1e-6, np.abs(audio).max()) * 0.9
raw = os.path.join(EP, "voice", "narration_raw.wav"); sf.write(raw, audio, SR)
af = (f"rubberband=pitch={pitch}:transients=smooth:formant=shifted:pitchq=quality" if abs(pitch - 1.0) > 1e-3 else
      "highpass=f=70,equalizer=f=180:t=q:w=1.0:g=2,equalizer=f=3500:t=q:w=1.2:g=1.5,lowpass=f=15000,"
      "acompressor=threshold=-22dB:ratio=2.2:attack=8:release=120,aecho=0.85:0.5:18|31:0.06|0.04")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", af, os.path.join(EP, "voice", "narration.wav")], check=True)
json.dump({"duration": round(t, 3), "lines": timeline}, open(os.path.join(EP, "voice", "timeline.json"), "w"), indent=1)
print("total", round(t, 2))
for l in timeline: print(l["id"], l["shot"], l["start"], l["end"])
