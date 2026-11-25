"""Render every frame of an episode with N parallel workers, one scene.py launch per shot chunk (each launch prunes the scene to that shot).
usage: EP=<episode dir> python3 render.py [workers=2] [samples=4]
Frames land in <EP>/render/f00000.png ... (432x768). Re-running skips finished frames. Logs in <EP>/logs/.
Run it in the background and poll `ls $EP/render | wc -l` until it prints ALLDONE in <EP>/render.log.
"""
import subprocess, sys, os, math, threading, queue
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing import SHOTS, END, EP
FPS = 24
N = int(math.ceil(END * FPS))
workers = int(sys.argv[1]) if len(sys.argv) > 1 else 2
samples = sys.argv[2] if len(sys.argv) > 2 else "4"
bounds = [int(round(st * FPS)) for _, st in SHOTS] + [N]
jobs = []
for i in range(len(SHOTS)):
    a, b = bounds[i], bounds[i + 1]
    for x in range(a, b, 220):
        jobs.append((x, min(b, x + 220)))
jobs.sort(key=lambda j: -(j[1] - j[0]))
q = queue.Queue()
for j in jobs: q.put(j)
os.makedirs(os.path.join(EP, "logs"), exist_ok=True)
def worker(wid):
    while True:
        try: a, b = q.get_nowait()
        except queue.Empty: return
        env = dict(os.environ, THREADS="1", EP=EP)
        with open(os.path.join(EP, "logs", f"w{wid}_{a}.log"), "w") as lf:
            subprocess.run(["python3", os.path.join(EP, "scene.py"), str(a), str(b), "432", "768", os.path.join(EP, "render"), samples],
                           stdout=lf, stderr=subprocess.STDOUT, env=env)
ths = [threading.Thread(target=worker, args=(i,)) for i in range(workers)]
for t in ths: t.start()
for t in ths: t.join()
missing = [f for f in range(N) if not os.path.exists(os.path.join(EP, "render", f"f{f:05d}.png"))]
print("ALLDONE", N, "missing", len(missing), missing[:20])
