"""Audio for the 3D episode: same voice + phonk bed, SFX re-timed to the new timeline."""
import sys, wave, subprocess
import numpy as np
sys.path.insert(0, '/home/claude/work'); sys.path.insert(0, '/home/claude/w3d')
import render3d as RD          # fills render.EL with the 3D episode's overlays
import render as R
src = open('/home/claude/work/audio.py').read()
# reuse synth helpers & music from audio.py, but replace the SFX event section
head = src.split("fx = np.zeros(N)")[0]
tail = src.split("# ---------- music (phonk-ish, 140 bpm) ----------")[1]
ns = {}
exec(head.replace("import render as R", "import render as R"), ns)
np_ = ns['np']; add = ns['add']; N = ns['N']; SR = ns['SR']
POP, CLICK, TICK, WH, IMP, SL, WH2 = (ns[k] for k in ('POP', 'CLICK', 'TICK', 'WH', 'IMP', 'SL', 'WH2'))
rng = ns['rng']

def shimmer():  # "power-up" for muscle glow
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 600 + 1400 * t / t[-1]
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.3
    return x * np.sin(np.pi * t / t[-1]) ** 2 * 0.35
SH = shimmer()

fx = np.zeros(N)
for e in R.EL:
    k = e['k']; t0 = e['t0']
    if k == 'chip':
        add(fx, CLICK, t0, 0.8)
        if e['style'] == 'strike': add(fx, SL, t0 + 0.45, 0.8)
    elif k == 'title':
        for j, ch in enumerate(e['text']):
            if ch != ' ': add(fx, TICK, t0 + j * 0.035, 0.7)
    elif k == 'big':
        add(fx, WH2, max(0, t0 - 0.25), 0.6); add(fx, IMP, t0 + 0.05, 0.8)
for (st, du) in R.SHAKES: add(fx, IMP, st, 1.0)
# X marks over props
for t0 in (4.25, 5.2): add(fx, SL, t0, 1.0); add(fx, SL, t0 + 0.15, 1.0); add(fx, IMP, t0 + 0.15, 0.4)
# props appear
for t0 in (3.76, 4.76, 56.1, 56.7, 57.55): add(fx, POP, t0, 0.9)
# muscle glow onsets
for t0 in (5.8, 16.5, 17.1, 17.95, 18.85, 25.5, 28.4, 32.8, 38.96, 39.52, 40.4, 46.4, 47.6, 48.75, 60.4, 61.85, 63.3, 63.8, 65.9, 89.4):
    add(fx, SH, t0 - 0.05, 0.9)
# fast camera / body turns
for t0 in (17.1, 17.95, 18.85, 19.8, 47.45, 63.28, 63.76):
    add(fx, WH, t0 - 0.05, 0.55)
add(fx, POP, 73.28, 1.0)
# soft whoosh on each squat descent
import os
for (a, b, per) in ([] if os.environ.get('NOSQ') else RD.SQUAT_SEGS):
    if per is None: continue
    t = a
    while t < b - 0.2:
        add(fx, WH, t, 0.22); t += per

ns['fx'] = fx
exec("# music\n" + tail.replace("'/home/claude/work/mix.wav'", "'/home/claude/w3d/mix3d.wav'"), ns)
