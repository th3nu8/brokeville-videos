# Daily explainer Short — runbook

Follow this top to bottom to make **one new explainer Short** and schedule it on YouTube. Expect about 1.5–2 hours, most of it rendering. Work in the foreground: keep polling with `sleep` calls under 10 minutes each. Background jobs stop when the session goes idle.

(The old Roblox story format is archived in `RUNBOOK-roblox-stories.md`. Don't make those any more.)

## The format

- **Channels:** YouTube + TikTok, both connected through Metricool (brand/blogId **8340054**, timezone America/Chicago). Brokeville now posts explainers only.
- **What:** 45–60 s 3D **cutaway explainers**: "How a nuclear bunker is built", "What's inside a submarine", "How a skyscraper survives an earthquake", "How a tunnel is dug under the ocean", "What's inside a volcano", "How a dam holds back a lake", "How an elevator stops from falling", "How a space toilet works", "What's under a city street", "How a cruise ship floats", and so on.
- **Style:** ONLY the smooth diorama style of `episodes/E001-nuclear-bunker/`. Do not use the blocky voxel style (E003 was a rejected experiment). The look is a diorama cutaway (a slice of the world, with the cut face toward the camera). The thing gets built or revealed step by step, in sync with the words. Labels with leader lines track objects. There's a 2-line title for the first 4 s, word-by-word captions, a calm adult narrator and soft music.
- **Voice:** `af_heart` at speed 1.0, pitch 1.0 (most natural free voice; whole passages read together). Keep the same voice on every video.
- **Audience:** NOT made for kids. Everything is family-friendly. **Never** make how-to content for weapons, explosives, drugs, hacking or anything dangerous. Explain how things are built and how they work, not how to cause harm. No graphic medical gore.
- **Accuracy:** every fact said or shown must come from what you looked up today (step 2). Prefer round, hedged numbers ("about", "often") over precise ones you can't back up.

## 0. Setup

```bash
git clone --depth 1 https://github.com/th3nu8/brokeville-videos ~/bv   # skip if the repo is already in your workspace
cd ~/bv && bash pipeline/setup.sh
```

## 1. Pick today's topic

Read the **Explainers** table in `episodes.md`. Pick a topic that hasn't been done, and avoid repeating the same category twice in a row (bunker → bunker-like). It has to be visual: a structure or machine you can show being built or opened up in 8–11 steps. Name the folder `episodes/E<NNN>-slug/`, with the next E number.

## 2. Research (required)

Run at least 3 web searches, plus fetches where needed, from reputable sources: encyclopedias, agencies, engineering and science outlets, manufacturer docs. Write `episodes/E<NNN>-slug/facts.md` with 6–10 bullet facts. Put the source URL after each one. The script may only use these facts.

## 3. Script → `script.json` + voice

```json
{"title": "How X works", "tail": 0.6, "lines": [{"id": 1, "shot": "hook", "text": "...", "pre": 0.0}, ...]}
```

- 11–14 lines and **125–150 words**. Each line's `shot` names its step. Use 9–12 different shots.
- **Line 1** is the hook and plays over the finished thing ("This is how you build a bunker that can survive a nuclear war."). **The last line** is a viewer question ("Would you last a month down here?").
- Write numbers as words. Add `"pre": 0.2` before new steps.

```bash
export EP=~/bv/episodes/E<NNN>-slug
python3 ~/bv/pipeline/voice.py af_heart 1.0 1.0   # natural mode: passages read together, room polish
```

The total must be **42–59 s**. If it's over, cut words. If it's under, add a fact line.

## 4. Scene → `scene.py`, `fx.py`

Copy `episodes/E001-nuclear-bunker/scene.py` and `fx.py` and rebuild them for the new topic. Keep:
- `VIS_EXTRA = {s: {"site"} for s in SHOT_LIGHT}`, and put everything in the `"site"` collection (`CUR[0] = "site"`).
- `stage(t)`: progress values per build step, eased between word times. The **hook** shot shows the finished state.
- `ubox`/`set_ext` for things that grow, `rbox`-based `box/cyl/sph/cone/wedge` for parts, and `emit=` for glowing elements. Add lights for interiors.
- `ANCH` = world positions for labels, plus `after_frame` writing `labels/fNNNNN.json` (keep as in E001).
- **Frame the diorama so it fills the vertical frame.** Avoid big empty void below or above it. Close-ups on details, wides on reveals, slow moves within each shot.
- `pipeline/lib.py` API: see `RUNBOOK-roblox-stories.md` §3 (geometry, lights `LIGHTS` presets day/dusk/cave/room/high/sunset/interior, `cam(pos, target, lens)`, timing `S/W/shot_start`).

`fx.py`: `HEADER` (2 lines, caps), `HOT` key words, `LABELS` = (anchor, text, start, end), optional on-screen graphics in `overlays`, `moods()` (mystery/happy/eerie), `sfx(cue)`, and `punches()` on key moments.

**Preview** one frame per shot (the midpoint of each shot) and **look at every image with the Read tool**:

```bash
ONLY=<frame list> python3 $EP/scene.py 0 -1 432 768 $EP/preview 4
```

Fix these before going on:
- the camera inside geometry
- the key object off-screen or hidden
- empty or black frames
- a lot of empty space

## 5. Render, audio, final

```bash
cd $EP && nohup python3 ~/bv/pipeline/render.py 2 4 > $EP/render.log 2>&1 &
# poll: sleep 590; ls $EP/render | wc -l ; cat $EP/render.log   (until "ALLDONE ... missing 0", ~1 h for 60 s)
python3 ~/bv/pipeline/audio.py && python3 ~/bv/pipeline/compose.py
ffprobe -v error -show_entries format=duration -of csv=p=0 $EP/final.mp4   # 45–60
```

Extract 8–10 frames across `final.mp4` and look at them. Check labels, the title, captions and the ending.

## 6. Upload + schedule

```bash
cd ~/bv && git pull --rebase -q && cp $EP/final.mp4 videos/E<NNN>-slug.mp4
git add videos/E<NNN>-slug.mp4 episodes/E<NNN>-slug/{script.json,scene.py,fx.py,facts.md,voice/timeline.json}
git commit -m "Explainer E<NNN>: <title>" && git -c push.negotiate=true push origin main
curl -sI https://raw.githubusercontent.com/th3nu8/brokeville-videos/main/videos/E<NNN>-slug.mp4 | head -1   # expect 200
```

Then call Metricool `createScheduledPost` with blogId `8340054`:
- **date:** today **17:00 America/Chicago**. If that's already past, use now + 15 minutes.
- **media:** the raw.githubusercontent URL.
- **providers:** `[{"network":"youtube"}, {"network":"tiktok"}]` (one post goes to both; TikTok account "Brokeville Animation").
- **text:** 1–2 sentence hook, plus the viewer question, plus `#shorts #howitsmade #engineering #science #explained` (adjust the hashtags to the topic).
- **youtubeData:** `{"title": "<How X works / is built> 🤯 #shorts (≤100 chars)", "type": "short", "privacy": "public", "madeForKids": false, "category": "EDUCATION", "isAiGeneratedContent": false, "tags": [...]}`.
- **tiktokData:** `{"privacyOption": "PUBLIC_TO_EVERYONE", "title": "<same title without #shorts>", "disableComment": false, "disableDuet": false, "disableStitch": false, "autoAddMusic": false, "isAigc": true, "commercialContentThirdParty": false, "commercialContentOwnBrand": false}`. `isAigc` is true because the narration is a synthetic voice.

If Metricool refuses (for example the free plan's 20-posts-per-month limit), still push the video and report the exact error.

## 7. Log it

Add a row to the **Explainers** table in `episodes.md` (E number, date, title, topic category, video path, Metricool post id). Then commit, pull with rebase, and push. Finish with a short message to the owner: the title, the post time and the Metricool planner link.

**Never post a broken video, one under 45 s or over 60 s, or one with facts you couldn't source.** If something fails that you can't fix, stop and report what happened.
