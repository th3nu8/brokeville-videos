"""Episode 001 effects: hooks used by pipeline/compose.py and pipeline/audio.py.
All times come from timing helpers: W(line_id, "wordprefix", nth) = word start, S(line_id) = line start, shot_start(name)."""
from timing import *

HEADER = ("I GOT THE WORST", "ADMIN COMMAND")          # big title for the first 4 s (hook)
HOT = {"/jump", "/fly", "/speed", "/giant", "/money", "robux", "doom", "million", "bonk", "lava", "door", "clouds",
       "what", "username", "froze", "disappeared", "poor", "decal", "laughed", "stud", "owner"}  # caption words flashed red

T_L = W(8, "l"); T_FROZE = W(26, "froze"); T_GONE = W(26, "disappeared")
LAG = (T_L + 0.9, T_L + 2.3)
STUDS = [(W(20, "studs", 0), "10 STUDS"), (W(20, "studs", 1), "50 STUDS"), (W(20, "studs", 2), "100 STUDS")]

def punches():   # (time, zoom amount) camera punch-ins on key words
    return [(S(7) - 0.1, 0.12), (W(16, "bonk"), 0.1), (W(17, "lava"), 0.06), (W(17, "door"), 0.08), (W(22, "what"), 0.08),
            (W(24, "username"), 0.08), (T_FROZE, 0.1), (W(14, "million"), 0.08), (W(9, "stud"), 0.08)]
def shakes():    # screen shake starts
    return [W(16, "bonk")]
def stutters():  # laggy freeze-frame windows
    return [LAG]
def grayscale_from():
    return T_FROZE
def end_text():  # (text, start) replaces captions at the end
    return ("PART 2?", S(27))

def overlays(img, t, ui):
    if LAG[0] - 0.3 <= t < LAG[1] + 0.3:
        ui.pill(img, (40, 230), "PING: 9999 ms", 44, (255, 80, 60), (0, 0, 0))
    for ts, txt in STUDS:
        if ts <= t < ts + 0.9:
            ui.center_text(img, txt, 330, 120, (255, 222, 33), 0.7 + 0.3 * min(1, (t - ts) / 0.1), 14)
    if shot_start("clouds") <= t < shot_start("clouds") + 2.2:
        ui.pill(img, (ui.W // 2 - 190, 240), "STAGE 999 / 1000", 50, (255, 255, 255), (20, 20, 30))
    if t >= T_GONE + 0.9:
        ui.dialog(img, "Server Frozen", ("Every other player has", "left the game."), "Rejoin?")

def moods():     # music sections
    return [(0.0, "happy"), (shot_start("mine"), "sad"), (shot_start("mayor"), "happy"), (shot_start("climb"), "hype"),
            (shot_start("room"), "mystery"), (T_FROZE, "eerie")]

def sfx(cue):
    cue("pop", S(7) - 0.15)
    for k in range(10): cue("blip", T_L + k * 0.12)
    cue("glitch", T_L + 1.2)
    cue("boing_small", W(9, "used") - 0.1)
    cue("coin", W(12, "earned"))
    cue("fanfare", S(14))
    cue("bonk", W(16, "bonk"))
    cue("sizzle", W(17, "lava"))
    for k in range(4): cue("thud", W(17, "door") - 0.5 + k * 0.25)
    s, e = shot_start("climb"), shot_start("clouds"); k = 1
    while True:   # hero jump times in the climb (matches scene hero_path)
        v = (-1.4 + (1.96 + 0.24 * k) ** 0.5) / 0.12
        if s + v >= e: break
        cue("boing", s + v); k += 1
    cue("rumble", S(22) - 1.0, 0.6)
    cue("blip", W(24, "username")); cue("blip", S(25) + 1.0)
    cue("tapestop", T_FROZE)
    cue("reverse_whoosh", T_GONE)
