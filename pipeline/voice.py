"""Narrator: Kokoro TTS per line -> word timings -> pitched-up kid voice.
usage: EP=<episode dir> python3 voice.py [voice=am_michael] [speed=1.0] [pitch=1.2]
Reads <EP>/script.json {"title", "lines":[{"id","shot","text","pre"(optional pause before, s)}]}
Writes <EP>/voice/narration.wav and <EP>/voice/timeline.json. Prints total length (must be >= 120 s).
Model files: ~/kokoro/kokoro-v1.0.onnx and voices-v1.0.bin (see RUNBOOK setup).
"""
import json, sys, re, os, subprocess
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

EP = os.environ.get("EP") or os.getcwd()
voice = sys.argv[1] if len(sys.argv) > 1 else "am_michael"
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
pitch = float(sys.argv[3]) if len(sys.argv) > 3 else 1.2
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
for ln in script["lines"]:
    pre = float(ln.get("pre", 0))
    if pre: out.append(np.zeros(int(pre * SR), dtype=np.float32)); t += pre
    samples, sr = k.create(ln["text"], voice=voice, speed=speed, lang="en-us")
    a = trim(np.asarray(samples, dtype=np.float32)); dur = len(a) / SR
    words = ln["text"].split(); w = weights(words); w = w / w.sum() * dur
    cur, wl = t, []
    for word, d in zip(words, w):
        wl.append({"w": word, "s": round(cur, 3), "e": round(cur + d, 3)}); cur += d
    timeline.append({"id": ln["id"], "shot": ln["shot"], "start": round(t, 3), "end": round(t + dur, 3), "words": wl})
    out.append(a); out.append(np.zeros(int(GAP * SR), dtype=np.float32)); t += dur + GAP
audio = np.concatenate(out); audio = audio / max(1e-6, np.abs(audio).max()) * 0.9
raw = os.path.join(EP, "voice", "narration_raw.wav"); sf.write(raw, audio, SR)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", f"rubberband=pitch={pitch}:transients=smooth:formant=shifted:pitchq=quality",
                os.path.join(EP, "voice", "narration.wav")], check=True)
json.dump({"duration": round(t, 3), "lines": timeline}, open(os.path.join(EP, "voice", "timeline.json"), "w"), indent=1)
print("total", round(t, 2))
for l in timeline: print(l["id"], l["shot"], l["start"], l["end"])
