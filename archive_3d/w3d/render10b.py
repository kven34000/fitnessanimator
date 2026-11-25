"""First 10 s on the Mixamo-compatible rig (Mixamo clips), clean shorts."""
import asyncio, base64, io, math, sys, subprocess
from PIL import Image
import render3d as RD
from drv import Eng

FPS = 30; W, H = 1920, 1080
sm, env, cam, camlerp, orbit = RD.sm, RD.env, RD.cam, RD.camlerp, RD.orbit
WIDE = ([0, 1.15, 5.4], [0, 0.95, 0]); MED = ([0, 1.1, 3.9], [0, 1.0, 0])
SQ = 1.8667  # AirSquat clip length
XF = 0.35
# (t0, t1, clip, clip_start, loop)
SEGS = [(0.0, 3.6, 'AirSquat', 0.0, True), (3.6, 5.64, 'Idle', 0.0, True), (5.64, 7.45, 'Flex', 1.2, False),
        (7.45, 9.2, 'Point', 0.35, False), (9.2, 10.5, 'Idle', 1.0, True)]
DUR = {'AirSquat': SQ, 'Idle': 3.333, 'Flex': 3.9, 'Point': 2.0}

def ctime(seg, t):
    a, b, c, c0, loop = seg
    x = c0 + (t - a)
    return (x % DUR[c]) if loop else min(x, DUR[c] - 0.01)

def clips_at(t):
    for i, seg in enumerate(SEGS):
        if seg[0] <= t < seg[1] or i == len(SEGS) - 1:
            cur = {'name': seg[2], 'time': ctime(seg, t), 'w': 1.0}
            if i > 0 and t < seg[0] + XF:
                k = sm((t - seg[0]) / XF); prev = SEGS[i - 1]
                return [{'name': prev[2], 'time': ctime(prev, t), 'w': 1 - k}, dict(cur, w=k)]
            return [cur]
    return []

def state(t):
    st = {'t': t, 'muscles': {}, 'props': {}, 'charRotY': 0.0, 'project': [], 'outline': 0.0014, 'clips': clips_at(t), 'fingerCurl': 0.3}
    M = st['muscles']; ov = []
    if t < 3.6:
        st['charRotY'] = 0.6
        st['cam'] = cam(camlerp(WIDE, MED, 0.5 * sm(t / 3.6)))
        ph = (t % SQ) / SQ; depth = math.sin(math.pi * min(1, ph / 0.95)) ** 2
        M['quads'] = 0.3 + 0.6 * depth; M['glutes'] = 0.2 + 0.5 * depth
        ov.append(('counter', int((t + SQ - 0.85) / SQ)))
    elif t < 5.64:
        st['charRotY'] = RD.ease(0.6, 0.15, 3.6, 4.1, t)
        st['cam'] = cam(WIDE)
        if t >= 3.76:
            st['props']['barbell'] = {'pos': [-1.25, 1.3 + 0.04 * math.sin(t * 2), 0.2], 'rot': [0.15, t * 0.8, 0.15], 's': 0.75 * min(1, (t - 3.76) / 0.2)}
            st['project'].append('barbell'); ov.append(('xprop', 'barbell', 4.25))
        if t >= 4.76:
            st['props']['gym'] = {'pos': [1.35, 0, -0.3], 'rot': [0, -0.4, 0], 's': 1.0 * min(1, (t - 4.76) / 0.2)}
            st['project'].append('gym'); ov.append(('xprop', 'gym', 5.2))
    elif t < 7.45:
        st['charRotY'] = 0.1
        st['cam'] = cam(orbit(camlerp(WIDE, MED, sm((t - 5.64) / 1.4)), 0.25 * sm((t - 5.64) / 1.8)))
        e = env(t, 5.9, 7.3)
        for m in ('biceps', 'pecs', 'abs', 'delts'): M[m] = 0.45 * e
    else:
        st['charRotY'] = RD.ease(0.1, -0.55, 7.45, 7.8, t)
        st['cam'] = cam(camlerp(MED, ([0.3, 1.3, 3.3], [0, 1.15, 0]), sm((t - 7.45) / 2.5)))
    return st, ov

async def make(t0, t1, out=None, stills=None):
    e = Eng('tex_clean.jpg', 'engine2.html'); await e.start()
    for c in ('Idle', 'Flex', 'Point'): await e.ev(f"()=>window.loadClip('{c}','hero_{c}.glb')")
    ff = None
    if out:
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    times = stills if stills else [i / FPS for i in range(int(t0 * FPS), int(t1 * FPS))]
    for t in times:
        st, ov = state(t)
        proj = await e.pg.evaluate('(s)=>window.frame(s)', st)
        b64 = await e.pg.evaluate('()=>window.grab()')
        fr = Image.open(io.BytesIO(base64.b64decode(b64.split(',')[1]))).convert('RGBA')
        RD.overlay(fr, t, ov, proj or {})
        if ff: ff.stdin.write(fr.convert('RGB').tobytes())
        else: fr.convert('RGB').save(f'/home/claude/w3d/n_{t}.jpg', quality=85)
    if ff: ff.stdin.close(); ff.wait()
    await e.stop()

if __name__ == '__main__':
    if sys.argv[1] == 'stills': asyncio.run(make(0, 0, stills=[float(x) for x in sys.argv[2:]]))
    else: asyncio.run(make(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]))
