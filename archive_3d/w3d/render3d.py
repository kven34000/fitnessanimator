"""3D red-neon episode: timeline -> engine frames -> 2D overlays -> ffmpeg."""
import asyncio, base64, io, math, sys, subprocess
from PIL import Image, ImageDraw
sys.path.insert(0, '/home/claude/work')
import render as R          # 2D helpers (fonts, chips, titles, subtitles)
import poses as P
from drv import Eng

FPS = 30; DUR = 92.0; W, H = 1920, 1080
PI = math.pi

def sm(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
def ease(a, b, t0, t1, t):
    return a + (b - a) * sm((t - t0) / (t1 - t0)) if t1 > t0 else b
def env(t, t0, t1, fin=0.25, fout=0.3):
    """0..1 envelope on [t0,t1]"""
    if t < t0 or t > t1 + fout: return 0.
    return min(sm((t - t0) / fin), 1 - sm((t - t1) / fout))
def keys(t, kf):
    """kf: list of (time, value or list); smooth interpolation"""
    if t <= kf[0][0]: return kf[0][1]
    for (ta, va), (tb, vb) in zip(kf, kf[1:]):
        if ta <= t <= tb:
            k = sm((t - ta) / (tb - ta)) if tb > ta else 1
            if isinstance(va, (list, tuple)): return [a + (b - a) * k for a, b in zip(va, vb)]
            return va + (vb - va) * k
    return kf[-1][1]

# camera presets (world: character at origin, faces +Z, height ~1.75)
FULL = ([0, 1.1, 4.5], [0, 1.0, 0])
WIDE = ([0, 1.15, 5.6], [0, 0.95, 0])
MED = ([0, 1.15, 3.9], [0, 1.05, 0])
LEGS = ([0, 0.62, 2.5], [0, 0.55, 0])
TORSO = ([0, 1.35, 2.7], [0, 1.25, 0])
KNEE = ([0.15, 0.55, 1.55], [0, 0.48, 0])
ANKLE = ([0.15, 0.25, 1.35], [0, 0.14, 0])
def cam(c, fov=30): return {'pos': list(c[0]), 'target': list(c[1]), 'fov': fov}
def camlerp(c1, c2, k):
    return ([a + (b - a) * k for a, b in zip(c1[0], c2[0])], [a + (b - a) * k for a, b in zip(c1[1], c2[1])])
def orbit(c, ang):
    (x, y, z), tg = c
    r = math.hypot(x, z); a0 = math.atan2(x, z)
    return ([r * math.sin(a0 + ang), y, r * math.cos(a0 + ang)], tg)

# ---------------- squat schedule with rep counting ----------------
SQUAT_SEGS = [  # (t0, t1, period)
    (0.0, 3.6, 1.2), (11.85, 23.85, 1.5), (25.1, 27.3, None), (31.15, 34.8, 1.6),
    (43.7, 46.3, 0.62), (58.25, 60.3, 1.6), (74.65, 77.3, 1.3), (77.3, 81.9, 0.85)]
def squat_at(t):
    for (a, b, per) in SQUAT_SEGS:
        if a <= t < b:
            if per is None:  # hold deep with tremble
                d = min(1, sm((t - a) / 0.6)) * (0.97 + 0.03 * math.sin(t * 40))
                return P.squat(d, t), d
            ph = ((t - a) % per) / per
            if ph < 0.45: d = sm(ph / 0.45)
            elif ph < 0.55: d = 1
            else: d = 1 - sm((ph - 0.55) / 0.45)
            return P.squat(d, t), d
    return None, 0
def reps_until(t, seg):
    a, b, per = seg
    if per is None or t < a: return 0
    return int((min(t, b) - a + per * 0.5) / per)

# ---------------- timeline ----------------
def state(t):
    st = {'t': t, 'muscles': {}, 'props': {}, 'charRotY': 0.0, 'project': []}
    M = st['muscles']; ov = []   # overlays: list of dicts
    pose = None; c = cam(FULL)

    sq, depth = squat_at(t)

    # S1 hook: squats right away
    if t < 3.6:
        pose = sq; st['charRotY'] = 0.55
        c = cam(camlerp(WIDE, MED, sm(t / 3.6)))
        M['quads'] = 0.35 * depth; M['glutes'] = 0.25 * depth
        ov.append(('counter', reps_until(t, SQUAT_SEGS[0])))
    # S2 no barbell / no gym / only body
    elif t < 7.45:
        k = t - 3.6
        if t < 5.64:
            pose = P.stand(t); c = cam(WIDE)
            if t >= 3.76:
                st['props']['barbell'] = {'pos': [-1.25, 1.25 + 0.04 * math.sin(t * 2), 0.2], 'rot': [0.15, t * 0.8, 0.15], 's': 0.75 * min(1, (t - 3.76) / 0.2)}
                st['project'].append('barbell'); ov.append(('xprop', 'barbell', 4.25))
            if t >= 4.76:
                st['props']['gym'] = {'pos': [1.35, 0, -0.3], 'rot': [0, -0.4, 0], 's': 1.0 * min(1, (t - 4.76) / 0.2)}
                st['project'].append('gym'); ov.append(('xprop', 'gym', 5.2))
        else:
            kk = sm((t - 5.64) / 0.4)
            pose = P.blend(P.stand(t), P.double_biceps(t), kk)
            c = cam(orbit(camlerp(WIDE, MED, sm((t - 5.64) / 1.6)), 0.25 * sm((t - 5.64) / 1.8)))
            e = env(t, 5.8, 7.3)
            for m in ('biceps', 'pecs', 'abs'): M[m] = 0.35 * e
    # S3 watch to the end: point at viewer
    elif t < 11.85:
        pose = P.blend(P.stand(t), P.point(t), sm((t - 7.45) / 0.4))
        st['charRotY'] = 0.25
        c = cam(camlerp(MED, ([0.2, 1.35, 3.2], [0, 1.2, 0]), sm((t - 7.45) / 4)))
    # S4/S5 squats + muscles by words
    elif t < 19.8:
        pose = sq
        if t < 16.5: st['charRotY'] = ease(1.2, 0.6, 11.85, 12.6, t); c = cam(MED)
        if 16.5 <= t < 17.1: st['charRotY'] = 0.6; c = cam(camlerp(MED, LEGS, sm((t - 16.5) / 0.4)))
        if 17.1 <= t < 17.95: st['charRotY'] = ease(0.6, PI - 0.55, 17.1, 17.45, t); c = cam(LEGS)
        if 17.95 <= t < 18.85: st['charRotY'] = ease(PI - 0.55, 0.45, 17.95, 18.3, t); c = cam(camlerp(LEGS, TORSO, sm((t - 17.95) / 0.35)))
        if t >= 18.85: st['charRotY'] = ease(0.45, PI - 0.3, 18.85, 19.2, t); c = cam(camlerp(TORSO, MED, sm((t - 18.85) / 0.5)))
        M['quads'] = env(t, 16.5, 17.1)
        M['glutes'] = env(t, 17.1, 17.95); M['hams'] = 0.6 * env(t, 17.1, 17.95)
        M['abs'] = env(t, 17.95, 18.85); M['obliques'] = env(t, 17.95, 18.85)
        M['lowback'] = env(t, 18.85, 19.8)
        ov.append(('counter', reps_until(t, SQUAT_SEGS[1])))
    # S6 anywhere/anytime: orbit
    elif t < 23.85:
        pose = sq; st['charRotY'] = ease(PI - 0.3, 0.5, 19.8, 20.3, t)
        c = cam(orbit(FULL, (t - 20.3) * 0.9 if t > 20.3 else 0))
        ov.append(('counter', reps_until(t, SQUAT_SEGS[1])))
    # S7 week 1: burn
    elif t < 31.15:
        if t < 25.1:
            pose = P.stand(t); c = cam(WIDE); st['char'] = t > 24.6
        elif t < 27.3:
            pose = sq; st['charRotY'] = 0.7; c = cam(camlerp(MED, LEGS, 0.55 * sm((t - 25.1) / 1.2)))
            fl = 0.75 + 0.25 * math.sin(t * 22)
            M['quads'] = fl * env(t, 25.5, 27.2); M['glutes'] = fl * env(t, 25.8, 27.2)
        else:
            pose = P.blend(P.squat(1.0 - sm((t - 27.3) / 0.5)), P.double_biceps(t), sm((t - 27.9) / 0.6))
            c = cam(orbit(camlerp(LEGS, MED, sm((t - 27.3) / 0.8)), 0.3 * sm((t - 28) / 3)))
            st['charRotY'] = ease(0.7, 0.1, 27.3, 28, t)
            e = env(t, 28.4, 30.9)
            # wave of "rebuilding" glow
            for i, m in enumerate(('calves', 'quads', 'glutes', 'abs', 'pecs', 'delts', 'biceps')):
                M[m] = e * (0.5 + 0.5 * math.sin(t * 6 - i * 0.9))
    # S8 week 2: stability then stairs
    elif t < 37.6:
        if t < 34.8:
            pose = sq; st['charRotY'] = 0.5; c = cam(MED)
            M['quads'] = 0.7 * env(t, 32.8, 34.8); M['ankles'] = env(t, 32.8, 34.8); M['knees'] = 0.7 * env(t, 32.8, 34.8)
        else:
            k = t - 34.8
            # climb: 0.44m forward and 0.175m up per half cycle of run(speed 9)
            steps = k / (PI / 9)
            px = -1.6 + 0.4375 * steps; py = 0.175 * (min(steps, 7.5) + 0.0)
            st['charPos'] = [px, py, 0]; st['charRotY'] = PI / 2
            pose = P.run(t)
            c = cam(([px + 0.4, py + 1.1, 4.2], [px + 0.3, py + 0.85, 0]))
            M['quads'] = 0.8; M['calves'] = 0.6
        st['props']['stairs'] = {'pos': [-1.6 + 0.4375, 0, 0], 'rot': [0, -PI / 2, 0], 's': 1.75}
        if t < 34.8: st['props']['stairs']['pos'] = [1.3, 0, -0.6]; st['props']['stairs']['rot'] = [0, -PI / 2 + 0.3, 0]
    # S9 week 3: balance
    elif t < 42.9:
        pose = P.blend(P.stand(t), P.balance(t), sm((t - 38.7) / 0.5))
        c = cam(orbit(MED, 0.4 * math.sin((t - 37.6) * 0.5)))
        M['abs'] = env(t, 38.96, 42.6); M['obliques'] = env(t, 39.52, 42.6); M['calves'] = env(t, 40.4, 42.6); M['glutes'] = 0.6 * env(t, 40.4, 42.6)
    # S10 month
    elif t < 50.5:
        if t < 46.35:
            pose = sq if sq else P.stand(t); st['charRotY'] = 0.6; c = cam(FULL)
            M['quads'] = 0.5
            ov.append(('counter', min(50, int(reps_until(t, SQUAT_SEGS[4]) * 50 / 4.2))))
        elif t < 48.6:
            pose = P.blend(P.stand(t), P.legs_flex(t), sm((t - 46.35) / 0.4)); st['charRotY'] = 0.3
            c = cam(camlerp(FULL, LEGS, sm((t - 46.35) / 0.6)))
            M['quads'] = env(t, 46.4, 47.4); M['calves'] = env(t, 46.6, 47.4)
            if t > 47.45: st['charRotY'] = ease(0.3, PI / 2, 47.45, 47.85, t); c = cam(camlerp(LEGS, FULL, sm((t - 47.45) / 0.5))); pose = P.tall(t)
            M['lowback'] = env(t, 47.6, 50.3); M['abs'] = env(t, 48.75, 50.3)
        else:
            pose = P.tall(t); st['charRotY'] = ease(PI / 2, 0.2, 48.6, 49.2, t); c = cam(FULL)
            M['lowback'] = env(t, 47.6, 50.3); M['abs'] = env(t, 48.75, 50.3); M['obliques'] = env(t, 48.75, 50.3)
    # S11 honest
    elif t < 54.05:
        pose = P.stand(t); st['charRotY'] = 0.15
        c = cam(camlerp(MED, TORSO, sm((t - 50.5) / 3)))
    # S12 add weight: props
    elif t < 58.25:
        pose = P.blend(P.stand(t), P.point(t), sm((t - 54.1) / 0.4)); st['charRotY'] = 0.2; c = cam(WIDE)
        if t >= 56.1: st['props']['dumbbell'] = {'pos': [-0.95, 1.15 + 0.05 * math.sin(t * 3), 0.4], 'rot': [0.3, t * 1.5, 0.2], 's': 2.6 * min(1, (t - 56.1) / 0.2)}
        if t >= 56.7: st['props']['barbell'] = {'pos': [0, 1.95 + 0.03 * math.sin(t * 2), -0.4], 'rot': [0.1, 0.25 * math.sin(t), 0], 's': 1.1 * min(1, (t - 56.7) / 0.2)}
        if t >= 57.55: st['props']['band'] = {'pos': [0.95, 1.1 + 0.05 * math.sin(t * 3), 0.4], 'rot': [1.2, t * 1.5, 0], 's': 2.4 * min(1, (t - 57.55) / 0.2)}
        c = cam(([0, 1.2, 5.0], [0, 1.0, 0]))
    # S13 base = top: mobility, circulation, knees, ankles
    elif t < 64.7:
        if t < 60.4:
            pose = sq; st['charRotY'] = 0.6; c = cam(MED)
        elif t < 61.8:
            pose = P.squat(1.0 + 0.0 * math.sin(t), t); st['charRotY'] = ease(0.6, 1.3, 60.4, 61.6, t)
            c = cam(orbit(MED, 0.3 * sm((t - 60.4) / 1.4)))
            M['hipjoint'] = env(t, 60.4, 61.7); M['ankles'] = 0.7 * env(t, 61.2, 61.7); M['knees'] = 0.6 * env(t, 61.2, 61.7)
        elif t < 63.28:
            pose = P.blend(P.squat(1.0), P.stand(t), sm((t - 61.8) / 0.5)); st['charRotY'] = 0.1
            c = cam(FULL)
            # circulation: wave going up the body
            for i, m in enumerate(('calves', 'hams', 'quads', 'glutes', 'abs', 'lowback', 'pecs', 'lats', 'delts', 'biceps', 'triceps', 'traps')):
                M[m] = env(t, 61.85, 63.2) * max(0, math.sin(t * 7 - i * 0.55)) ** 2
        else:
            pose = P.stand(t); st['charRotY'] = 0.35
            if t < 63.76:
                c = cam(camlerp(FULL, KNEE, sm((t - 63.28) / 0.35))); M['knees'] = env(t, 63.3, 63.76, 0.15, 0.2)
            else:
                c = cam(camlerp(KNEE, ANKLE, sm((t - 63.76) / 0.35))); M['ankles'] = env(t, 63.8, 64.65, 0.15, 0.15)
    # S14 confidence
    elif t < 71.5:
        pose = P.blend(P.stand(t), P.double_biceps(t), sm((t - 65.6) / 0.5))
        c = cam(orbit(camlerp(FULL, MED, sm((t - 64.7) / 2)), 0.6 * math.sin((t - 64.7) * 0.45)))
        e = env(t, 65.9, 71.3)
        for m in ('biceps', 'pecs', 'abs'): M[m] = 0.3 * e
    # S15 worth it?
    elif t < 74.65:
        pose = P.blend(P.stand(t), P.point(t), sm((t - 73.2) / 0.3)); st['charRotY'] = 0.2; c = cam(MED)
    # S16 sets / 75-100
    elif t < 82.0:
        pose = sq; st['charRotY'] = 0.55
        c = cam(FULL if t < 77.3 else orbit(FULL, (t - 77.3) * 0.35))
        M['quads'] = 0.4 * depth; M['glutes'] = 0.3 * depth
        if t < 77.3: ov.append(('counter10', reps_until(t, SQUAT_SEGS[6])))
        else: ov.append(('counter', min(100, 50 + int(reps_until(t, SQUAT_SEGS[7]) * 50 / 5))))
    # S17 subscribe
    elif t < 87.45:
        pose = P.blend(P.stand(t), P.point(t), sm((t - 82.0) / 0.35)); st['charRotY'] = 0.2
        c = cam(camlerp(MED, ([0, 1.3, 3.4], [0, 1.2, 0]), sm((t - 82) / 5)))
    # S18 outro
    else:
        pose = P.blend(P.stand(t), P.double_biceps(t), sm((t - 87.6) / 0.5))
        c = cam(orbit(camlerp(MED, WIDE, sm((t - 87.45) / 4.5)), 0.5 * sm((t - 87.45) / 4.5)))
        e = env(t, 89.4, 92)
        for m in ('biceps', 'pecs', 'abs'): M[m] = 0.35 * e
    st['pose'] = pose or P.stand(t)
    st['cam'] = c
    return st, ov

# ---------------- 2D overlay (reuse render.py elements, minus its characters) ----------------
KEEP = ('chip', 'title', 'big', 'sub')
R.EL[:] = []
def chip(*a, **k): R.chip(*a, **k)
def title(*a, **k): R.title(*a, **k)
def big(*a, **k): R.big(*a, **k)
title('50 ПРИСЕДАНИЙ', 1.3, 3.6, y=110, size=110)
title('КАЖДЫЙ ДЕНЬ', 2.7, 3.6, y=225, size=70, col=R.RED2)
title('ТОЛЬКО ТЫ И ТВОЁ ТЕЛО', 5.7, 7.45, y=110, size=80)
title('ДОСМОТРИ ДО КОНЦА', 7.6, 11.85, y=110, size=90)
title('С СОБСТВЕННЫМ ВЕСОМ', 13.9, 16.4, y=110, size=80)
chip('НОГИ', 16.5, 19.8, 70, 330, 'on', 54)
chip('ЯГОДИЦЫ', 17.1, 19.8, 70, 440, 'on', 54)
chip('КОРПУС', 17.95, 19.8, 70, 550, 'on', 54)
chip('ПОЯСНИЦА', 18.85, 19.8, 70, 660, 'on', 54)
title('ГДЕ УГОДНО', 21.5, 23.85, x=1300, y=150, size=80)
title('КОГДА УГОДНО', 22.55, 23.85, x=1300, y=255, size=80, col=R.RED2)
big('НЕДЕЛЯ 1', 23.95, 25.2, size=210)
chip('ГОРЯТ НОГИ И ЯГОДИЦЫ', 25.75, 27.3, 70, 330, 'on', 50)
chip('ЭТО НОРМАЛЬНО', 27.6, 31.15, 70, 330, 'on', 52)
chip('МЫШЦЫ ПЕРЕСТРАИВАЮТСЯ', 28.6, 31.15, 70, 440, 'n', 50)
big('НЕДЕЛЯ 2', 31.15, 32.3, size=210)
chip('СТАБИЛЬНЕЕ', 32.8, 34.8, 70, 330, 'on', 52)
chip('УВЕРЕННЕЕ', 34.08, 34.8, 70, 440, 'on', 52)
title('ЛЕСТНИЦА — ЛЕГЧЕ', 35.4, 37.6, y=120, size=80, col=R.RED2)
big('НЕДЕЛЯ 3', 37.6, 38.75, size=210)
chip('БАЛАНС', 38.96, 42.9, 70, 330, 'on', 52)
chip('КООРДИНАЦИЯ', 39.52, 42.9, 70, 440, 'on', 52)
chip('ВЫНОСЛИВОСТЬ', 40.4, 42.9, 70, 550, 'on', 52)
big('1 МЕСЯЦ', 42.9, 43.7, size=210)
chip('50 = РАЗМИНКА', 45.4, 46.35, 70, 330, 'on', 56)
chip('НОГИ СИЛЬНЕЕ', 46.4, 50.5, 70, 330, 'on', 50)
chip('ОСАНКА РОВНЕЕ', 47.5, 50.5, 70, 440, 'on', 50)
chip('КРЕПКИЙ КОРПУС', 48.75, 50.5, 70, 550, 'on', 50)
title('ЧЕСТНО:', 50.6, 54.05, y=110, size=90, col=R.RED2)
chip('БОДИБИЛДЕР', 51.9, 54.05, 1300, 380, 'strike', 58)
title('ХОЧЕШЬ МАССУ? +ВЕС', 54.1, 58.25, y=110, size=84)
chip('ГАНТЕЛИ', 56.1, 58.25, 120, 860, 'on', 50)
chip('ШТАНГА', 56.7, 58.25, 840, 860, 'on', 50)
chip('РЕЗИНА', 57.55, 58.25, 1560, 860, 'on', 50)
big('ТОП', 59.8, 60.5, y=300, size=280)
chip('ПОДВИЖНОСТЬ', 60.4, 61.8, 70, 330, 'on', 50)
chip('ГИБКОСТЬ', 61.2, 61.8, 70, 440, 'on', 50)
chip('КРОВООБРАЩЕНИЕ', 61.8, 63.28, 70, 330, 'on', 50)
chip('КОЛЕНИ', 63.28, 63.76, 70, 330, 'on', 56)
chip('ГОЛЕНОСТОП', 63.76, 64.7, 70, 330, 'on', 56)
title('УВЕРЕННОСТЬ', 65.9, 71.5, y=120, size=110, col=R.RED2)
title('КОНТРОЛЬ НАД ЖИЗНЬЮ', 70.2, 71.5, y=230, size=60)
chip('НЕ СТОИТ', 71.95, 74.65, 560, 330, 'dimx', 56, anchor='c')
chip('СТОИТ', 72.05, 74.65, 1360, 330, 'check', 56, anchor='c')
chip('50 — МНОГО?', 74.7, 77.3, 70, 330, 'n', 52)
chip('ДЕЛИ: 5 × 10', 76.24, 77.3, 70, 440, 'on', 52)
title('75–100', 78.6, 82.0, y=130, size=150, col=R.RED2)
title('КАЖДЫЙ ДЕНЬ', 80.2, 82.0, y=255, size=66)
chip('ПОДПИСАТЬСЯ', 82.1, 87.45, 420, 560, 'on', 54, anchor='c')
chip('СКОЛЬКО ПРИСЕДАЕШЬ ТЫ?', 84.8, 87.45, 960, 120, 'on', 56, anchor='c')
title('МАЛЕНЬКИЕ ШАГИ', 87.5, 92.0, y=110, size=90)
title('БОЛЬШИЕ ПЕРЕМЕНЫ', 89.45, 92.0, y=220, size=90, col=R.RED2)
R.SHAKES[:] = [(59.84, 0.35), (65.92, 0.25)]

def overlay(fr, t, ov, proj):
    """draws 2D elements via render.py's frame logic but only for our EL + subs"""
    import types
    d = ImageDraw.Draw(fr)
    # chips/titles/big using R's code path: emulate by calling element drawers
    sx = sy = 0
    for (s0, du) in R.SHAKES:
        if s0 <= t < s0 + du:
            k = 1 - (t - s0) / du; sx = int(math.sin(t * 90) * 16 * k); sy = int(math.cos(t * 77) * 12 * k)
    for e in R.EL:
        if not (e['t0'] <= t < e['t1']): continue
        draw_el(fr, e, t, sx, sy)
    for item in ov:
        if item[0] in ('counter', 'counter10'):
            n = item[1]
            tot = 10 if item[0] == 'counter10' else (100 if t > 77 else 50)
            f = R.font(R.F_RUSSO, 64)
            im = R.cached(('cnt', n, tot), lambda: R.text_img(f'{n}/{tot}', f, (255, 255, 255, 255), stroke=3, stroke_fill=(20, 0, 5), glow=12))
            lab = R.cached(('cntl',), lambda: R.text_img('ПОВТОРЫ', R.font(R.F_M900, 30), R.RED2 + (255,), stroke=2, glow=6))
            fr.alpha_composite(lab, (W - 60 - lab.width, 60))
            fr.alpha_composite(im, (W - 60 - im.width, 100))
        if item[0] == 'xprop' and item[1] in proj:
            cx, cy = proj[item[1]]; a = t - item[2]
            if item[1] == 'gym': cy -= 230
            S = 150
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            p1 = R.clamp(a / 0.15); p2 = R.clamp((a - 0.15) / 0.15)
            if p1 > 0: dd.line([(cx - S, cy - S), (cx - S + 2 * S * p1, cy - S + 2 * S * p1)], fill=R.RED + (255,), width=26)
            if p2 > 0: dd.line([(cx + S, cy - S), (cx + S - 2 * S * p2, cy - S + 2 * S * p2)], fill=R.RED + (255,), width=26)
            from PIL import ImageFilter
            fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10))); fr.alpha_composite(lay)
    # subtitles
    draw_subs(fr, t)
    if t < 0.25 or t > DUR - 0.6:
        k2 = R.clamp(t / 0.25) if t < 0.25 else R.clamp((DUR - t) / 0.6)
        fr.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - k2)))))

def draw_el(fr, e, t, sx, sy):
    k = e['k']; a = t - e['t0']
    if k == 'chip':
        im = R.chip_img(e['text'], e['size'], e['style'])
        s = R.out_back(a / 0.28, 2.4); al = R.clamp(a / 0.08)
        b = e['t1'] - t
        if b < 0.12: al *= R.clamp(b / 0.12)
        if e['style'] == 'check' and t >= 73.28: s *= 1 + 0.12 * math.exp(-(t - 73.28) * 5) + 0.03 * math.sin(t * 8)
        if e['style'] == 'dimx' and t >= 73.28: al *= 0.45
        ax = 0 if e['anchor'] == 'l' else 0.5
        R.paste_scaled(fr, im, e['x'] + sx, e['y'] + sy, s, al, ax=ax, ay=0.5)
        if e['style'] == 'strike':
            p = R.clamp((a - 0.45) / 0.25)
            R.draw_strike(fr, e['x'] + 22, e['y'] - im.height / 2 + 22, im.width - 44, im.height - 44, p)
    elif k == 'title':
        txt = e['text']; n = min(len(txt), int(a / 0.035) + 1)
        f = R.font(R.F_RUSSO, e['size'])
        im = R.cached(('t', txt[:n], e['size'], e['col']), lambda: R.text_img(txt[:n], f, e['col'] + (255,), stroke=3, stroke_fill=(20, 0, 5), glow=14))
        al = 1.0; b = e['t1'] - t
        if b < 0.12: al = R.clamp(b / 0.12)
        full = R.cached(('tw', txt, e['size']), lambda: R.text_img(txt, f, (255, 255, 255, 255), stroke=3, glow=14).width)
        x0 = e['x'] - full / 2 if e['anchor'] == 'c' else e['x']
        R.paste_scaled(fr, im, x0 + sx, e['y'] + sy, 1, al, ax=0, ay=0.5)
    elif k == 'big':
        b = e['t1'] - t
        f = R.font(R.F_RUSSO, e['size'])
        im = R.cached(('big', e['text'], e['size']), lambda: R.text_img(e['text'], f, (255, 255, 255, 255), stroke=5, stroke_fill=R.RED, glow=30))
        s = 1.6 - 0.6 * R.out_cubic(a / 0.18); al = R.clamp(a / 0.08)
        if b < 0.15: al *= R.clamp(b / 0.15); s *= 1 + (0.15 - b)
        if a < 0.2 and int(a * 60) % 3 == 0: R.paste_scaled(fr, im, e['x'] + 14, e['y'] + sy, s, al * 0.5)
        R.paste_scaled(fr, im, e['x'] + sx, e['y'] + sy, s, al)

def draw_subs(fr, t):
    for (s0, s1, c) in R.SUBS:
        if s0 <= t < s1:
            f = R.font(R.F_M900, 58)
            words = [w for w, _, _ in c]
            act = 0
            for i, (w, a, b) in enumerate(c):
                if t >= a: act = i
            sp = f.getlength(' ')
            ws = [f.getlength(w.upper()) for w in words]
            tot = sum(ws) + sp * (len(ws) - 1)
            x = W / 2 - tot / 2; y = 985
            pop = R.out_back((t - c[act][1]) / 0.15, 3)
            for i, w in enumerate(words):
                up = w.upper(); isnum = any(ch.isdigit() for ch in w)
                col = R.RED2 if (i == act or isnum) else (255, 255, 255)
                im = R.cached(('sw', up, col), lambda: R.text_img(up, f, col + (255,), stroke=6, stroke_fill=(0, 0, 0), glow=0))
                sc = 1.0 if i != act else 0.9 + 0.1 * pop
                R.paste_scaled(fr, im, x + ws[i] / 2, y, sc, 1.0)
                x += ws[i] + sp
            break

async def main(t0, t1, out):
    e = await Eng().start()
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    n0, n1 = int(t0 * FPS), int(t1 * FPS)
    for fi in range(n0, n1):
        t = fi / FPS
        st, ov = state(t)
        proj = await e.pg.evaluate('(s)=>window.frame(s)', st)
        b64 = await e.pg.evaluate('()=>window.grab()')
        fr = Image.open(io.BytesIO(base64.b64decode(b64.split(',')[1]))).convert('RGBA')
        overlay(fr, t, ov, proj or {})
        ff.stdin.write(fr.convert('RGB').tobytes())
        if fi % 150 == 0: print(out, fi, flush=True)
    ff.stdin.close(); ff.wait(); await e.stop()

async def stills(ts):
    e = await Eng().start()
    for t in ts:
        st, ov = state(t)
        proj = await e.pg.evaluate('(s)=>window.frame(s)', st)
        b64 = await e.pg.evaluate('()=>window.grab()')
        fr = Image.open(io.BytesIO(base64.b64decode(b64.split(',')[1]))).convert('RGBA')
        overlay(fr, t, ov, proj or {})
        fr.convert('RGB').save(f'/home/claude/w3d/st_{t}.jpg', quality=85)
    await e.stop()

if __name__ == '__main__':
    if sys.argv[1] == 'stills':
        asyncio.run(stills([float(x) for x in sys.argv[2:]]))
    else:
        asyncio.run(main(float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]))
