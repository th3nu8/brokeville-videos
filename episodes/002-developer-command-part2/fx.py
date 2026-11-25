"""Episode 002 effects: hooks used by pipeline/compose.py and pipeline/audio.py.
All times come from timing helpers: W(line_id, "wordprefix", nth) = word start, S(line_id) = line start, shot_start(name)."""
from timing import *
from PIL import Image, ImageOps

HEADER = ("PART 2: MY TOWN", "DISAPPEARED")
HOT = {"disappeared", "nobody", "frozen", "gray", "throne", "boring", "free", "trial", "shoebox", "foot", "mine", "patches",
       "mayor", "giant", "broke", "million", "premium", "slowly", "developer", "game", "purpose", "stronger", "red", "ten",
       "white", "me", "/spawn", "/bring", "/undo", "/jump", "secret", "three"}

T_GRAY = W(3, "gray")
T_LOW = W(7, "low")
CMDS = [(W(8, "slash"), "/spawn house", 2), (W(11, "slash"), "/bring everyone back", 1), (W(17, "slash"), "/undo", 0)]
T_SORRY = W(18, "sorry")
T_SHUT = W(26, "server")
T_RED = W(26, "red")

def punches():   # (time, zoom amount) camera punch-ins on key words
    return [(W(9, "shoebox"), 0.1), (W(13, "mine"), 0.12), (W(14, "mayor"), 0.06), (W(14, "giant"), 0.06), (W(15, "broke"), 0.08),
            (W(18, "premium"), 0.08), (W(23, "made"), 0.12), (T_RED, 0.1), (W(27, "not"), 0.12), (W(16, "million"), 0.06),
            (W(19, "slowly"), 0.06), (W(5, "ten"), 0.05)]
def shakes():    # screen shake starts
    return [T_RED, W(9, "spawned")]
def stutters():  # laggy freeze-frame windows
    return [(W(3, "frozen"), W(3, "frozen") + 0.7)]
def grayscale_from():
    return None
def end_text():  # (text, start) replaces captions at the end
    return ("PART 3?", S(28))

def _console(img, ui, t, ts, cmd):
    n = max(0, min(len(cmd), int((t - ts) / 0.06) + 1))
    cur = "_" if int(t * 3) % 2 else " "
    ui.pill(img, (60, 230), "> " + cmd[:n] + cur, 50, (120, 255, 140), (10, 14, 20))

def overlays(img, t, ui):
    # frozen + gray town (header is gone by then)
    if T_GRAY <= t < shot_start("mansion"):
        k = min(1.0, (t - T_GRAY) / 0.3)
        g = Image.blend(img, ImageOps.grayscale(img).convert("RGB"), 0.9 * k)
        img.paste(g)
    if S(2) <= t < shot_start("mansion"):
        ui.pill(img, (40, 470), "PLAYERS ONLINE: 1", 44, (255, 255, 255), (20, 20, 30))
    # low quality mode: pixelate
    if T_LOW <= t < T_LOW + 1.4:
        small = img.resize((img.width // 22, img.height // 22), Image.BILINEAR)
        img.paste(small.resize(img.size, Image.NEAREST))
        ui.pill(img, (60, 230), "LOW QUALITY MODE", 50, (255, 230, 80), (40, 20, 10))
    if W(7, "free") - 0.1 <= t < T_LOW:
        ui.pill(img, (60, 230), "FREE TRIAL: 3 COMMANDS", 50, (255, 255, 255), (200, 40, 40))
    for ts, cmd, left in CMDS:
        if ts - 0.1 <= t < ts + 2.6:
            _console(img, ui, t, ts - 0.1, cmd)
        if ts + 1.6 <= t < ts + 3.4:
            ui.pill(img, (60, 340), f"COMMANDS LEFT: {left}", 40, (255, 255, 255), (200, 40, 40) if left == 0 else (40, 40, 50))
    if W(12, "every") <= t < shot_start("clones"):
        ui.pill(img, (40, 470), "PLAYERS ONLINE: 48", 44, (255, 255, 255), (30, 140, 60))
    if W(16, "dad") <= t < shot_start("crowd"):
        ui.center_text(img, "DAD: 1 R$ / DAY", 380, 70, (255, 222, 33), 1.0, 12)
    if T_SORRY - 0.1 <= t < S(19) + 0.3:
        ui.dialog(img, "Sorry!", ("Undo is a", "PREMIUM feature."), "Upgrade?")
    if W(24, "slash") <= t < W(24, "it's"):
        ui.center_text(img, "/jump", 360, 130, (255, 222, 33), 1.0, 14)
    if t >= T_SHUT:
        n = max(0, 10 - int(t - T_SHUT))
        col = (255, 255, 255) if int(t * 4) % 2 else (255, 230, 230)
        ui.pill(img, (ui.W // 2 - 330, 230), f"SERVER SHUTDOWN IN {n}", 54, col, (190, 20, 20))

def moods():     # music sections
    return [(0.0, "eerie"), (shot_start("mansion"), "happy"), (W(5, "being") - 0.2, "sad"), (shot_start("room"), "mystery"),
            (shot_start("tiny"), "happy"), (T_SORRY, "sad"), (shot_start("mine"), "hype"), (shot_start("dad"), "mystery"),
            (shot_start("alarm"), "eerie")]

def sfx(cue):
    cue("glitch", W(3, "frozen"))
    cue("tapestop", T_GRAY)
    cue("fanfare", W(4, "throne"))
    cue("coin", W(5, "best"))
    cue("blip", W(6, "developer")); cue("blip", W(6, "type"))
    cue("glitch", T_LOW, 1.5)
    for ts, cmd, left in CMDS:
        for k in range(len(cmd)): cue("blip", ts - 0.1 + k * 0.06, 0.35)
    cue("pop", W(9, "spawned")); cue("boing_small", W(10, "foot"))
    for k in range(14): cue("pop", W(12, "worked") - 0.1 + k * 0.17, 0.5)
    cue("fanfare", W(12, "every"))
    cue("bonk", W(13, "mine"), 0.6)
    cue("coin", W(16, "million"))
    cue("thud", T_SORRY); cue("thud", W(18, "premium"))
    cue("rumble", S(19) + 0.5, 0.7)
    cue("reverse_whoosh", W(22, "developer")); cue("blip", W(22, "logged"))
    cue("fanfare", W(23, "made"))
    cue("boing", W(24, "jump"))
    cue("glitch", T_RED, 2.0); cue("rumble", T_RED)
    for k in range(10): cue("blip", T_SHUT + k, 0.8)
    cue("tapestop", W(27, "not"))
