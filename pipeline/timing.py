"""Timing helpers shared by scene, audio and compose. Episode folder comes from env EP."""
import json, os
EP = os.environ.get("EP") or os.getcwd()
TL = json.load(open(os.path.join(EP, "voice", "timeline.json")))
LN = {l["id"]: l for l in TL["lines"]}
def W(line, prefix, nth=0):
    """start time of the nth word in a line starting with prefix (case-insensitive, punctuation stripped)"""
    c = 0
    for w in LN[line]["words"]:
        if w["w"].lower().strip(".,?!").startswith(prefix.lower()):
            if c == nth:
                return w["s"]
            c += 1
    raise KeyError((line, prefix))
def S(line):
    return LN[line]["start"]
END = TL["duration"] + 1.6
SHOTS = [(TL["lines"][0]["shot"], 0.0)]
_prev = SHOTS[0][0]
for _l in TL["lines"]:
    if _l["shot"] != _prev:
        SHOTS.append((_l["shot"], _l["start"] - 0.08)); _prev = _l["shot"]
def shot_at(t):
    cur = SHOTS[0]
    for s in SHOTS:
        if t >= s[1]:
            cur = s
    return cur[0], t - cur[1]
def shot_start(n):
    return dict(SHOTS)[n]
