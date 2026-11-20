import numpy as np, subprocess, sys, wave
sys.path.insert(0, '/home/claude/work')
import render as R

SR = 44100
DUR = R.DUR
N = int(DUR * SR)
rng = np.random.default_rng(3)

def env(n, a, d):
    t = np.arange(n) / SR
    e = np.minimum(t / max(a, 1e-4), 1) * np.exp(-np.maximum(t - a, 0) / d)
    return e

def lp(x, cut):
    # one-pole lowpass, cut can be array
    cut = np.broadcast_to(np.asarray(cut, float), x.shape)
    a = 1 - np.exp(-2 * np.pi * cut / SR)
    y = np.zeros_like(x); s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y

def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    x = x[:len(buf) - i]; buf[i:i + len(x)] += x * g

# ---------- SFX ----------
def sfx_pop():
    n = int(0.09 * SR); t = np.arange(n) / SR
    f = 500 + 900 * (t / t[-1])
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.03) * 0.6
def sfx_click():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1900 * t) * 0.5 + rng.normal(0, 0.3, n)) * env(n, 0.001, 0.012) * 0.5
def sfx_tick():
    n = int(0.02 * SR)
    return rng.normal(0, 1, n) * env(n, 0.0005, 0.004) * 0.25
def sfx_whoosh(d=0.35):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    cut = 300 + 4000 * np.sin(np.pi * t / d) ** 2
    y = lp(x, cut) - lp(lp(x, cut), 200)
    e = np.sin(np.pi * t / d) ** 2
    return y * e * 0.9
def sfx_impact():
    n = int(0.6 * SR); t = np.arange(n) / SR
    f = 120 * np.exp(-t * 8) + 45
    b = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.18)
    nz = lp(rng.normal(0, 1, n), 2500) * env(n, 0.001, 0.05)
    return (b * 0.9 + nz * 0.6)
def sfx_slash():
    n = int(0.18 * SR); t = np.arange(n) / SR
    x = rng.normal(0, 1, n); y = x - lp(x, 1500)
    return y * np.sin(np.pi * t / t[-1]) * 0.5

POP, CLICK, TICK, WH, IMP, SL = sfx_pop(), sfx_click(), sfx_tick(), sfx_whoosh(), sfx_impact(), sfx_slash()
WH2 = sfx_whoosh(0.5)

fx = np.zeros(N)
for e in R.EL:
    k = e['k']; t0 = e['t0']
    if k in ('char', 'squat'):
        en = e.get('enter', 'pop')
        if en == 'pop': add(fx, POP, t0, 0.8)
        elif en in ('up', 'left', 'right'): add(fx, WH, max(0, t0 - 0.05), 0.7)
    elif k == 'chip':
        add(fx, CLICK, t0, 0.8)
        if e['style'] == 'strike': add(fx, SL, t0 + 0.45, 0.8)
    elif k == 'title':
        if e['type']:
            for j in range(len(e['text'])):
                if e['text'][j] != ' ': add(fx, TICK, t0 + j * 0.035, 0.7)
    elif k == 'big':
        add(fx, WH2, max(0, t0 - 0.25), 0.6); add(fx, IMP, t0 + 0.05, 0.8)
    elif k == 'x':
        add(fx, SL, t0, 1.0); add(fx, SL, t0 + 0.2, 1.0); add(fx, IMP, t0 + 0.2, 0.5)
for (st, du) in R.SHAKES:
    add(fx, IMP, st, 1.0)
add(fx, POP, 73.28, 1.0)

# ---------- music (phonk-ish, 140 bpm) ----------
bpm = 140; beat = 60 / bpm; step = beat / 4
mus = np.zeros(N)
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 50 + 130 * np.exp(-t * 30)
    return np.tanh(2.5 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.12))
def clap():
    n = int(0.25 * SR); x = rng.normal(0, 1, n); y = x - lp(x, 900)
    e = env(n, 0.001, 0.06)
    return y * e * 0.7
def hat():
    n = int(0.05 * SR); x = rng.normal(0, 1, n); y = x - lp(x, 7000)
    return y * env(n, 0.0005, 0.012) * 0.35
def bell(freq, d=0.22):
    n = int(d * SR); t = np.arange(n) / SR
    sq = lambda f: np.sign(np.sin(2 * np.pi * f * t))
    x = (sq(freq) + sq(freq * 1.48)) * 0.5
    x = lp(x, 3500)
    return x * env(n, 0.002, 0.07) * 0.35
def bass(freq, d):
    n = int(d * SR); t = np.arange(n) / SR
    f = freq * (1 + 0.8 * np.exp(-t * 25))
    return np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(n, 0.003, d * 0.6) * 0.55

K, C, H = kick(), clap(), hat()
# A minor phonk pattern (16 steps per bar)
notes = {'A': 440, 'C': 523.25, 'D': 587.33, 'E': 659.25, 'G': 783.99, 'a': 880}
mel = ['A', None, 'A', 'C', None, 'A', 'E', None, 'D', None, 'C', None, 'A', None, 'G', None]
bells = {k: bell(v) for k, v in notes.items()}
bl = [55.0, 55.0, 43.65, 49.0]  # A1 A1 F1 G1 per bar
start = 0.0
nbars = int(DUR / (16 * step)) + 1
for bar in range(nbars):
    tb = start + bar * 16 * step
    for s in range(16):
        ts = tb + s * step
        if s in (0, 6, 10): add(mus, K, ts, 0.9)
        if s in (4, 12): add(mus, C, ts, 0.7)
        if s % 2 == 0: add(mus, H, ts, 0.6 if s % 4 else 0.35)
        if s in (3, 7, 15) and bar % 2: add(mus, H, ts, 0.3)
        m = mel[s]
        if m and bar >= 1: add(mus, bells[m], ts, 0.55)
    add(mus, bass(bl[bar % 4], 16 * step * 0.9), tb, 0.8)

# ---------- voice ----------
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', '/home/claude/work/vo.mp3', '-ac', '1', '-ar', str(SR), '/home/claude/work/vo.wav'], check=True)
w = wave.open('/home/claude/work/vo.wav'); v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
voice = np.zeros(N); voice[:min(N, len(v))] = v[:N]
# duck music by voice envelope
blk = 1024
ve = np.repeat([np.sqrt(np.mean(voice[i:i + blk] ** 2)) for i in range(0, N, blk)], blk)[:N]
ve = lp(ve, 4.0)
duck = 1 - 0.55 * np.clip(ve / 0.05, 0, 1)
# music fade in/out
fade = np.clip(np.arange(N) / (0.5 * SR), 0, 1) * np.clip((N - np.arange(N)) / (1.5 * SR), 0, 1)
mix = voice * 1.0 + mus * 0.11 * duck * fade + fx * 0.32
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= max(1e-6, np.abs(mix).max()) / 0.95
out = (mix * 32767).astype(np.int16)
with wave.open('/home/claude/work/mix.wav', 'w') as o:
    o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR); o.writeframes(out.tobytes())
print('ok')
r=lambda a: 20*np.log10(np.sqrt(np.mean(a**2))+1e-9)
print('voice',r(voice),'music',r(mus*0.11*duck*fade),'fx',r(fx*0.32))
