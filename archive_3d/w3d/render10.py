"""First 10 seconds with mocap (CMU) retargeted animation, cleaned texture, thin outline."""
import asyncio, base64, io, math, sys, subprocess
from PIL import Image
import render3d as RD
import poses as P
from drv import Eng

FPS = 30; W, H = 1920, 1080
sm, env, cam, camlerp, orbit = RD.sm, RD.env, RD.cam, RD.camlerp, RD.orbit
WIDE, MED, FULL = RD.WIDE, RD.MED, RD.FULL
CLIPS = ['13_29', '82_08', '79_94', '13_27']

# segments: (video_t0, video_t1, clip, clip_t0, yaw)
SEGS = [(0.0, 3.6, '13_29', 31.7, 0.0), (3.6, 5.64, '82_08', 0.5, 0.0), (5.64, 7.45, '79_94', 5.3, 0.0), (7.45, 10.5, '13_27', 1.3, 0.0)]
XF = 0.3  # crossfade

def anim_at(t):
    for i, (a, b, c, c0, yaw) in enumerate(SEGS):
        if a <= t < b or i == len(SEGS) - 1:
            cur = {'name': c, 'time': c0 + (t - a), 't0': c0, 'yaw': yaw}
            if i > 0 and t < a + XF:
                pa, pb, pc, pc0, pyaw = SEGS[i - 1]
                prev = {'name': pc, 'time': pc0 + (t - pa), 't0': pc0, 'yaw': pyaw}
                return prev, cur, sm((t - a) / XF)
            return cur, None, 0
    return None, None, 0

def state(t):
    st = {'t': t, 'muscles': {}, 'props': {}, 'charRotY': 0.0, 'project': [], 'outline': 0.0014}
    M = st['muscles']; ov = []
    a1, a2, mix = anim_at(t)
    st['anim'] = a1
    if a2: st['anim2'] = a2; st['mix'] = mix
    if t < 3.6:
        st['charRotY'] = 0.55
        st['cam'] = cam(camlerp(WIDE, MED, 0.45 * sm(t / 3.6)))
        pul = 0.5 + 0.5 * math.sin(t * 4)
        M['quads'] = 0.35 + 0.2 * pul; M['glutes'] = 0.25 + 0.15 * pul
        reps = sum(1 for b in (33.1, 36.3) if 31.7 + t >= b)
        ov.append(('counter', reps))
        st['pose'] = P.hands(0.45)
    elif t < 5.64:
        st['charRotY'] = RD.ease(0.55, 0.0, 3.6, 4.0, t)
        st['cam'] = cam(WIDE)
        if t >= 3.76:
            st['props']['barbell'] = {'pos': [-1.25, 1.25 + 0.04 * math.sin(t * 2), 0.2], 'rot': [0.15, t * 0.8, 0.15], 's': 0.75 * min(1, (t - 3.76) / 0.2)}
            st['project'].append('barbell'); ov.append(('xprop', 'barbell', 4.25))
        if t >= 4.76:
            st['props']['gym'] = {'pos': [1.35, 0, -0.3], 'rot': [0, -0.4, 0], 's': 1.0 * min(1, (t - 4.76) / 0.2)}
            st['project'].append('gym'); ov.append(('xprop', 'gym', 5.2))
        st['pose'] = P.hands(0.4)
    elif t < 7.45:
        st['charRotY'] = 0.0
        st['cam'] = cam(orbit(camlerp(WIDE, MED, sm((t - 5.64) / 1.6)), 0.25 * sm((t - 5.64) / 1.8)))
        e = env(t, 5.8, 7.3)
        for m in ('biceps', 'pecs', 'abs', 'delts'): M[m] = 0.4 * e
        st['pose'] = P.hands(0.95)
    else:
        st['charRotY'] = 0.15
        st['cam'] = cam(camlerp(MED, ([0.2, 1.35, 3.2], [0, 1.2, 0]), sm((t - 7.45) / 2.5)))
        st['pose'] = P.hands(0.5)
    return st, ov

async def main(t0, t1, out):
    e = await Eng('tex_clean.jpg').start()
    for c in CLIPS: await e.ev(f"()=>window.loadBVH('{c}','bvh/{c}.bvh')")
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for fi in range(int(t0 * FPS), int(t1 * FPS)):
        t = fi / FPS
        st, ov = state(t)
        proj = await e.pg.evaluate('(s)=>window.frame(s)', st)
        b64 = await e.pg.evaluate('()=>window.grab()')
        fr = Image.open(io.BytesIO(base64.b64decode(b64.split(',')[1]))).convert('RGBA')
        RD.overlay(fr, t, ov, proj or {})
        ff.stdin.write(fr.convert('RGB').tobytes())
        if fi % 60 == 0: print(out, fi, flush=True)
    ff.stdin.close(); ff.wait(); await e.stop()

async def stills(ts):
    e = await Eng('tex_clean.jpg').start()
    for c in CLIPS: await e.ev(f"()=>window.loadBVH('{c}','bvh/{c}.bvh')")
    for t in ts:
        st, ov = state(t)
        proj = await e.pg.evaluate('(s)=>window.frame(s)', st)
        b64 = await e.pg.evaluate('()=>window.grab()')
        fr = Image.open(io.BytesIO(base64.b64decode(b64.split(',')[1]))).convert('RGBA')
        RD.overlay(fr, t, ov, proj or {})
        fr.convert('RGB').save(f'/home/claude/w3d/m_{t}.jpg', quality=85)
    await e.stop()

if __name__ == '__main__':
    if sys.argv[1] == 'stills': asyncio.run(stills([float(x) for x in sys.argv[2:]]))
    else: asyncio.run(main(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]))
