# Brokeville daily Short — runbook

Follow this top to bottom to make **one new Short** and schedule it on YouTube. Expect about 4 hours, most of it rendering. Work in the foreground: keep polling with `sleep` calls under 10 minutes each. Background jobs stop when the session goes idle.

## The channel

- **Name:** Brokeville. YouTube channel connected through Metricool (brand/blogId **8340054**, timezone America/Chicago).
- **Format:** Roblox-themed 3D animated stories, **at least 2:00 long** (aim for 2:05–2:30, never over 2:50). They are narrated in first person by the same broke kid. Every story has a "power/quirk" that everyone in the town has, and the poor kid gets the worst or cheapest version. Hook in the first line, escalating jokes, a twist, and a **"Part 2?"** cliffhanger at the end.
- **Look:** cinematic Cycles render, R15-style blocky characters with faces, studded baseplates, soft light, glow, word-by-word captions, higher-pitched kid narrator.
- **Hero (always the same):** `avatar(..., shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)`, a gray patched shirt and brown pants. Handle on screens: `BrokeKid_2014`.
- **Audience:** NOT made for kids. Keep it family-friendly anyway: no swearing, no gore, no romance.
- **IP rules:** the title and description can say "Roblox" for search. Inside the video, use only original characters, maps and UI. No Roblox logo, no real Roblox games or brand UI copied exactly, and no famous characters (no default yellow "Noob" either).

## 0. Setup (each session)

```bash
git clone --depth 1 https://github.com/th3nu8/brokeville-videos ~/bv   # skip if the repo is already in your workspace
cd ~/bv && bash pipeline/setup.sh
```

## 1. Pick today's story

- Read `episodes.md`. Never repeat a premise.
- If the newest episode ended on "Part 2?" and has **not** been continued, and the previous run was *not* already a Part 2, then today make **its Part 2**. Reuse the same hero and town style, and pick up from the cliffhanger. Otherwise invent a **new** premise.
- Premise ideas, use a fresh one each time: in my Roblox town everyone… gets a pet that grants a power (I got a pet rock); has a gamepass (mine was a refund); spawns with Robux every morning (I get -1); can buy a tycoon (mine sells dirt); has a VIP server (mine has one player: me); gets a sword (I got a pool noodle); is a different block color (mine is see-through); levels up when they jump (I level down), and so on.
- Name the episode `episodes/NNN-short-slug/`, where NNN is the next number in `episodes.md`.

## 2. Script → `script.json`

```json
{"title": "...", "lines": [{"id": 1, "shot": "town", "text": "In my Roblox town, ...", "pre": 0.0}, ...]}
```

- 24–30 lines, **340–420 words** total. The `shot` value is the name of the 3D set the line plays over. Consecutive lines can share a shot. Use 10–14 different shots.
- Write numbers as words ("one million Robux", "stage nine hundred ninety nine"). Write commands as "slash jump" (captions turn it into "/jump").
- `"pre"` adds a dramatic pause before a line (0.2–0.5 s) before reveals and punchlines.
- Last line: "Part two if this gets a thousand likes." (or a variation).

```bash
export EP=~/bv/episodes/NNN-slug
python3 ~/bv/pipeline/voice.py am_michael 1.0 1.2
```

It prints the total. **Must be ≥ 120 s.** If it's shorter, add 2–4 funny lines and re-run.

## 3. Scenes → `scene.py` (+ `fx.py`)

Copy `episodes/001-worst-admin-command/scene.py` and `fx.py` as templates and **rewrite the sets and shot functions** for the new story. Keep this structure:

```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "pipeline"))
from lib import *
SHOT_LIGHT = {...}   # per shot: day | dusk | cave | room | high | sunset | interior
SHOT_FSTOP = {...}   # 1.4 (blurry bg, close-ups) .. 3.5 (wide shots)
VIS_EXTRA = {...}    # shot -> other set collections that must also be visible
setup_shots(SHOT_LIGHT, SHOT_FSTOP)
X = at("town", 0)    # each set is its own collection; put sets >= 300 units apart on x
baseplate(X, 60, 500) ; house(...) ; tree(...) ; lamp(...) ; bush(...) ; fence(...) ; cloud(...) ; spawnpad(...)
HERO = avatar((X, 0, 0), fdir(0, -1), shirt="8f8f8f", pants="5a4a3a", hair="4a2c17", patched=True)
def update(t):
    CAMTIME[0] = t
    shot, u = shot_at(t)          # u = seconds since the shot started
    apply_shot(shot, VIS_EXTRA)
    if shot == "town": do_town(t, u)
    ...
    return shot
if __name__ == "__main__":
    run(update, VIS_EXTRA)
```

**Library cheat-sheet (`pipeline/lib.py`)**
- Geometry: `box(loc, (sx,sy,sz), "hex", parent, rot, r=bevel, emit=, metal=, rough=)` (true size, rounded edges), `cyl/sph(loc, scale, "hex", ...)`, `wedge`, `text("TXT", loc, size, "hex", parent, emit=)` (faces −Y), `empty()`, `bubble("chat text", loc)` (chat bubble), `hide(obj, bool)`.
- Glow: `emit=2–8` on materials (lasers, screens, lava, neon). Add point/area lights with `bpy.data.lights.new` for dark scenes.
- Characters: `a = avatar(loc, rz, shirt, pants, hair, hat="crown|cap|tophat|hardhat", shades=True, scale=2.5)`. Its parts are `a["root"], a["hips"], a["torso"], a["head"], a["legs"], a["knees"], a["arms"], a["elbows"]`. Characters face −Y; `fdir(dx, dy)` gives the rotation to face a direction.
- Animation: `idle(a, t, ph)`, `walk(a, t, speed, amp)`, `jump_pose(a)`, `crouch_pose(a)`, `fly_pose(a, t)`, `laugh(a, t, ph)`, `pose(a, legs, arms, arms_out, head, knees, elbows, lean)`, `set_mouth(a, "smile|sad|open|flat")`, `blink(a, t)`. Easing: `ease, lerp, vl`.
- Camera: `cam(position, target, lens)`. Depth of field focuses on the target, and a light handheld shake is added automatically. Move the camera slowly within a shot, cut between angles on key words, and use close-ups for reactions and wides for reveals.
- Timing: `S(line_id)` = line start, `W(line_id, "word", nth)` = word start, `shot_start(name)`. Trigger actions **on the word**.

**Preview before the full render.** Render one or two frames per shot at the midpoint of each shot, then **look at every image with the Read tool**:

```bash
ONLY=<comma list of frame numbers = seconds*24> python3 $EP/scene.py 0 -1 432 768 $EP/preview 4
```

Fix any of these and preview again:
- the camera inside a wall, head or building (red or black full-frame)
- the hero not visible on his own lines
- characters hidden behind others
- an empty frame

## 4. Full render (~3 h)

```bash
cd $EP && nohup python3 ~/bv/pipeline/render.py 2 4 > $EP/render.log 2>&1 &
# then poll:  sleep 590; ls $EP/render | wc -l ; cat $EP/render.log   (until "ALLDONE ... missing 0")
```

If frames are missing, run it again: it only renders what's missing. Midway through, spot-check a few finished frames for mistakes. Fix them in `scene.py` and re-render just those frames with `FORCE=1 python3 $EP/scene.py <start> <end> 432 768 $EP/render 4`.

## 5. Audio + final video

Fill in `fx.py`: `HEADER` (2-line hook title for the first 4 s), `HOT` caption words, `punches()`, `shakes()`, `stutters()`, `grayscale_from()`, `end_text()`, `overlays(img, t, ui)` (with `ui.pill`, `ui.center_text`, `ui.dialog`), `moods()` (happy/sad/hype/mystery/eerie), `sfx(cue)` (whoosh, pop, boing, boing_small, blip, coin, fanfare, bonk, thud, sizzle, tapestop, glitch, rumble, reverse_whoosh).

```bash
python3 ~/bv/pipeline/audio.py && python3 ~/bv/pipeline/compose.py      # -> $EP/final.mp4 (~7 min)
ffprobe -v error -show_entries format=duration -of csv=p=0 $EP/final.mp4   # must be >= 120
```

Extract 6–8 frames across the video (`ffmpeg -ss T -i final.mp4 -frames:v 1 x.jpg`) and look at them: check captions, overlays and the ending.

## 6. Upload + schedule

```bash
cd ~/bv && cp $EP/final.mp4 videos/NNN-slug.mp4
git add videos/NNN-slug.mp4 episodes/NNN-slug/script.json episodes/NNN-slug/scene.py episodes/NNN-slug/fx.py episodes/NNN-slug/voice/timeline.json
git commit -m "Short NNN: <title>" && git -c push.negotiate=true push origin main
curl -sI https://raw.githubusercontent.com/th3nu8/brokeville-videos/main/videos/NNN-slug.mp4 | head -1   # expect 200
```

Then call Metricool `createScheduledPost` with blogId `8340054`:
- **date:** today **17:00 America/Chicago**. If that's already past, use now + 15 minutes.
- **media:** the raw.githubusercontent URL.
- **providers:** `[{"network":"youtube"}]`.
- **text:** 2–3 line hook description, plus "Part 2 if this gets 1,000 likes!", plus `#roblox #robloxanimation #shorts #robloxstory #animation`.
- **youtubeData:** `{"title": "<≤100 chars, ends with #shorts>", "type": "short", "privacy": "public", "madeForKids": false, "category": "ENTERTAINMENT", "isAiGeneratedContent": false, "tags": [...]}`.

If Metricool refuses, for example over the free-plan limit of 20 posts per month, still push the video and tell the owner the exact error.

## 7. Log it

Append to `episodes.md`: the number, date, title, one-line premise, the cliffhanger, the video path, the Metricool post id, and whether it's a Part 2 of an earlier episode. Commit and push. Finish with a short message to the owner: the title, the post time, and the Metricool planner link.

**Never post a broken or under-2-minute video.** If something fails that you can't fix, stop and report what happened instead.
