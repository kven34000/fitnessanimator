import sys, os, json, math, subprocess
sys.path.insert(0, '/home/claude/work'); sys.path.insert(0, '/home/claude/v2_6ex')
import numpy as np
from PIL import Image
import render_v2 as R
from script_en import SEG, DUR

R.DUR = DUR
R.SUB_LABELS = ('SUBSCRIBE', 'LIKE'); R.DAY_LABEL = 'DAY'
SPRDIR = R.SPRDIR

# ---------------- new sheets ----------------
# name: (rows, cols, scale-mode, target)
NEW = dict(pullup=(2, 4, 'h', 760), dips=(2, 4, 'h', 760), decline=(4, 2, 'w', 1050), pushup=(4, 2, 'w', 1050),
           bulgarian=(2, 4, 'h', 740), rdl=(2, 4, 'h', 740), benchdip=(2, 4, 'h', 700), pain=(2, 4, 'h', 760),
           row=(2, 2, 'w', 1000))
SHEETDIM = dict(row=(2400, 880))
SHEET_W, SHEET_H = 2400, 1792
PERIOD = dict(pullup=2.4, dips=2.0, decline=2.0, pushup=1.6, bulgarian=2.4, rdl=2.8, benchdip=1.8, pain=3.2, row=2.0)

_orig_load = R.load_sprites
def load_sprites():
    _orig_load()
    for nm, (rows, cols, mode, tgt) in NEW.items():
        d = f'{SPRDIR}/{nm}'
        if not os.path.exists(f'{d}/fboxes.json'): continue
        boxes = json.load(open(f'{d}/fboxes.json'))
        ims = [Image.open(f'{d}/f{i}.png').convert('RGBA') for i in range(len(boxes))]
        mks = [Image.open(f'{d}/f{i}_m.png').convert('RGBA') if os.path.exists(f'{d}/f{i}_m.png') else None for i in range(len(boxes))]
        if mode == 'h': ref = sorted(i.height for i in ims)[len(ims) // 2]
        else: ref = sorted(i.width for i in ims)[len(ims) // 2]
        sc = tgt / ref
        sw, sh_ = SHEETDIM.get(nm, (SHEET_W, SHEET_H))
        cw, chh = sw / cols, sh_ / rows
        # anchor: fixed point of each cell (cell centre x, cell bottom y), shifted to typical feet line
        offs = []
        for (x0, y0, x1, y1) in boxes:
            r = int(((y0 + y1) / 2) // chh); offs.append((r + 1) * chh - y1)
        off = sorted(offs)[len(offs) // 2]
        frs = []
        for im, mk, (x0, y0, x1, y1) in zip(ims, mks, boxes):
            r = int(((y0 + y1) / 2) // chh); c = int(((x0 + x1) / 2) // cw)
            ax = (c + 0.5) * cw - x0; ay = (r + 1) * chh - off - y0
            sz = (max(1, int(im.width * sc)), max(1, int(im.height * sc)))
            im2 = im.resize(sz, Image.LANCZOS)
            mk2 = Image.merge('RGBA', [ch.resize(sz, Image.BILINEAR) for ch in mk.split()]) if mk is not None else None
            big, fx, fy, mb, raw = R._mk(im2, mk2)
            frs.append((big, ax * sc + 60, ay * sc + 60, mb, raw))
        R.ANIM[nm] = frs
        R.SPR[nm] = frs[0][:3]
R.load_sprites = load_sprites

_orig_ff = R.frame_for
def frame_for(pose, a, e):
    if pose in NEW:
        frs = R.ANIM[pose]; P = e.get('period') or PERIOD[pose]
        return frs[int((a % P) / P * len(frs)) % len(frs)]
    return _orig_ff(pose, a, e)
R.frame_for = frame_for

_orig_glow = R.apply_glow
def apply_glow(spr, mk, glow, t):
    if not glow: return spr
    cols = {g[2] for g in glow if len(g) > 2}
    if not cols: return _orig_glow(spr, mk, glow, t)
    old = R.GLOWC; R.GLOWC = list(cols)[0]
    try: return _orig_glow(spr, mk, [g[:2] for g in glow], t)
    finally: R.GLOWC = old
R.apply_glow = apply_glow

# ---------------- timeline ----------------
R.EL.clear(); R.SHAKES.clear()
EL = R.EL
char, title, big, prop, xmark = R.char, R.title, R.big, R.prop, R.xmark
def chip(text, t0, t1, x, y, style='n', size=46, anchor='l'):
    w = R.chip_img(text, size, style).width
    if anchor == 'l': x = max(10, min(x, 1905 - w))
    R.chip(text, t0, t1, x, y, style, size, anchor)
def ex(pose, t0, t1, x=960, y=968, sc=1.0, glow=None, period=None, enter='pop'):
    if pose == 'pullup' and y == 968: y = 880
    EL.append(dict(k='char', pose=pose, t0=t0, t1=t1, x=x, y=y, sc=sc, enter=enter, exit='fade', flip=False,
                   ghost=False, burn=False, zoom=0.0, glow=glow, period=period))
def fx(kind, t0, t1, **kw):
    d = dict(k=kind, t0=t0, t1=t1); d.update(kw); EL.insert(0, d)
RC = 1250  # right text column
LC = 60    # left text column
PAINRED = (255, 40, 40)
PUNCH = []

# hook
ex('pushup', 0.0, 3.6, sc=0.9, period=1.3)
title('YEARS OF TRAINING', 0.2, 3.6, y=130, size=90)
chip('SAME BODY', 2.0, 3.6, RC + 120, 330, 'strike', 54)
char('think', 3.6, 6.0, x=700)
chip('WRONG EXERCISES', 4.6, 6.0, RC - 40, 420, 'on', 54); PUNCH.append(4.6)
char('flex', 6.0, 10.6, x=700, glow=[(0, 7.4), (1, 7.4), (2, 7.4), (3, 7.4)])
big('6', 6.3, 10.6, x=1450, y=300, size=300); PUNCH.append(6.3)
chip('MOVES', 6.8, 10.6, RC + 80, 560, 'on', 60)
chip('MORE MUSCLE', 7.4, 10.6, RC + 80, 680, 'n', 54)
char('cross', 10.6, 12.5, x=700)
prop(1, 10.6, 12.5, 1450, 380, 0.42, strike=True)
prop(4, 11.4, 12.5, 1450, 640, 0.30, strike=True)
char('point', 12.5, 15.0, x=700)
title('SOUNDS IMPOSSIBLE?', 12.7, 15.0, y=130, size=90)
char('ok', 15.0, 20.0, x=700)
chip('SCIENCE', 15.2, 20.0, RC, 380, 'on', 56)
chip('BEATS THE GYM', 16.6, 20.0, RC, 500, 'check', 54)
char('point', 20.0, 27.0, x=700)
big('?', 20.2, 27.0, x=1500, y=280, size=260); PUNCH.append(20.2)
chip('TRICEPS', 22.6, 27.0, RC, 520, 'on', 54)
chip('> CLOSE-GRIP BENCH', 24.0, 27.0, RC, 630, 'n', 50)
char('thumb', 27.0, 30.0)
title('STAY WITH ME', 27.6, 30.0, y=130, size=90)
# barbell damage
ex('pain', 30.0, 37.0, x=760, glow=[(0, 32.9, PAINRED)])
prop(1, 30.4, 37.0, 1450, 300, 0.45)
chip('SPINE', 32.9, 37.0, RC + 60, 520, 'on', 56); PUNCH.append(32.9); R.SHAKES.append((32.9, 0.4))
R.squat(37.0, 39.0, x=760, period=0.55)
chip('REP AFTER REP', 37.0, 39.0, RC, 420, 'n', 52)
chip('YEAR AFTER YEAR', 37.9, 39.0, RC, 530, 'on', 52)
char('cross', 39.0, 41.0, x=760)
title('HEAVY ≠ EFFECTIVE', 39.1, 41.0, y=130, size=92)
char('point', 41.0, 43.0, x=700)
prop(5, 41.0, 43.0, 1450, 640, 0.38, strike=True)
chip('BENCH PRESS', 41.2, 43.0, RC, 380, 'strike', 52)
ex('pain', 43.0, 48.0, x=760, glow=[(0, 43.2, PAINRED)])
big('10+ YEARS', 43.2, 48.0, x=1420, y=320, size=150)
chip('JOINT DAMAGE', 45.5, 48.0, RC, 560, 'on', 54)
char('think', 48.0, 51.5, x=700)
chip('WHAT GROWS MUSCLE?', 48.4, 51.5, RC - 60, 420, 'n', 50)
char('cross', 51.5, 55.0, x=700)
prop(1, 51.6, 55.0, 1450, 420, 0.45, strike=True)
chip('NOT THE WEIGHT', 52.5, 55.0, RC, 640, 'strike', 52)
char('flex', 55.0, 56.5, x=650, glow=[(0, 55.1), (1, 55.1), (2, 55.1), (3, 55.1)])
big('TENSION', 55.1, 56.5, x=1380, y=330, size=160); PUNCH.append(55.1); R.SHAKES.append((55.1, 0.3))

# 1 pull-ups
big('#1', 56.5, 58.3, x=560, y=360, size=240); PUNCH.append(56.5)
ex('pullup', 56.5, 82.0, x=1180, y=968)
title('PULL-UPS', 56.6, 62.5, x=560, y=190, size=100)
chip('BACK ONLY?', 59.2, 62.5, LC, 450, 'strike', 54)
# muscle glow on the running pull-up element
pu = [e for e in EL if e.get('pose') == 'pullup'][0]
pu['glow'] = [(0, 63.3), (1, 64.1), (2, 64.9), (3, 65.6)]
chip('LATS', 63.3, 73.0, LC, 300, 'on', 48)
chip('UPPER BACK', 64.1, 73.0, LC, 390, 'on', 48)
chip('REAR DELTS', 64.9, 73.0, LC, 480, 'on', 48)
chip('BICEPS', 65.6, 73.0, LC, 570, 'on', 48)
chip('FOREARMS + CORE', 66.5, 73.0, LC, 660, 'n', 48)
chip('WHOLE BODY', 69.0, 73.0, LC, 780, 'check', 50)
prop(4, 73.0, 79.5, 520, 560, 0.45, strike=True)
chip('LAT PULLDOWN', 73.0, 79.5, LC, 260, 'strike', 50)
chip('STABILIZERS: OFF', 77.5, 79.5, LC, 820, 'dimx', 46)
chip('EVERY MUSCLE', 79.6, 82.0, LC, 450, 'check', 54); PUNCH.append(79.6)
ex('pullup', 82.0, 109.0, x=1180, glow=[(0, 82.0), (1, 82.0), (2, 82.0), (3, 82.0)], period=3.0)
chip('GRIP: SLIGHTLY WIDER', 82.2, 85.8, LC, 380, 'on', 46)
chip('ARMS: FULLY STRAIGHT', 83.8, 85.8, LC, 480, 'on', 46)
chip('CHEST TO BAR', 85.9, 88.0, LC, 380, 'check', 52)
chip('NOT CHIN', 86.9, 88.0, LC, 490, 'strike', 52)
big('5 SEC', 89.5, 94.0, x=480, y=330, size=170)
chip('NO MOMENTUM', 92.0, 94.0, LC, 600, 'on', 50)
chip('DEAD HANGS', 95.0, 103.0, LC, 380, 'on', 50)
chip('SLOW NEGATIVES', 96.0, 103.0, LC, 480, 'on', 50)
chip('JUMP UP, FIGHT GRAVITY', 98.6, 103.0, LC, 600, 'n', 44)
big('10', 103.1, 107.0, x=460, y=300, size=230); PUNCH.append(103.1)
chip('+ WEIGHTED VEST', 104.6, 107.0, LC, 560, 'on', 50)
chip('REAL SIZE', 107.1, 109.0, LC, 450, 'check', 56)

# 2 inverted rows
ROWPOSE = 'row' if os.path.exists(f'{SPRDIR}/row/fboxes.json') else 'pullup'
big('#2', 109.0, 111.0, x=560, y=360, size=240); PUNCH.append(109.0)
ex(ROWPOSE, 109.0, 111.0, x=1180)
title('INVERTED ROWS', 109.1, 111.0, y=130, size=96)
char('think', 111.0, 115.5, x=700)
chip('IGNORED PATTERN', 111.8, 115.5, 1120, 420, 'on', 50)
ex('pain', 115.5, 119.5, x=760, glow=[(0, 116.5, PAINRED)])
chip('ROUNDED SHOULDERS', 115.8, 119.5, RC - 40, 400, 'on', 48)
chip('CHRONIC PAIN', 117.8, 119.5, RC - 40, 510, 'on', 48)
ex('pullup', 119.5, 127.5, x=1180, glow=[(1, 120.2), (0, 121.0), (2, 122.4)], period=3.0)
chip('MID BACK', 120.2, 127.5, LC, 330, 'on', 48)
chip('TRAPS', 121.0, 127.5, LC, 420, 'on', 48)
chip('REAR DELTS', 122.4, 127.5, LC, 510, 'on', 48)
chip('RHOMBOIDS', 123.6, 127.5, LC, 600, 'on', 48)
chip('FULL RANGE', 125.2, 127.5, LC, 720, 'check', 48)
ex(ROWPOSE, 127.5, 157.5, x=1180 if ROWPOSE == 'pullup' else 1020)
chip('SPINE LOAD: 0', 127.8, 131.0, LC, 450, 'check', 54)
fx('loc', 131.0, 136.0, seq=[(131.0, 'home')])
chip('STURDY TABLE', 131.4, 136.0, LC, 330, 'on', 48)
chip('TRX STRAPS', 132.6, 136.0, LC, 420, 'on', 48)
chip('PARALLEL BARS', 133.8, 136.0, LC, 510, 'on', 48)
chip('GRIP: SLIGHTLY WIDER', 136.2, 141.0, LC, 380, 'on', 46)
chip('HEAD-TO-HEELS LINE', 138.0, 141.0, LC, 480, 'on', 46)
chip('CHEST TO BAR', 141.1, 146.0, LC, 380, 'check', 50)
chip('SQUEEZE SHOULDER BLADES', 142.8, 146.0, LC, 480, 'on', 44)
chip('LOWER WITH CONTROL', 146.1, 148.0, LC, 450, 'n', 48)
chip('BAR HIGHER = EASIER', 148.1, 154.0, LC, 330, 'n', 46)
chip('BAR LOWER = HARDER', 149.6, 154.0, LC, 420, 'on', 46)
chip('FEET ON BOX = ADVANCED', 151.4, 154.0, LC, 510, 'on', 44)
big('3 × 8–12', 154.1, 157.5, x=520, y=330, size=150); PUNCH.append(154.1)

# 3 dips
big('#3', 157.5, 160.0, x=560, y=360, size=240); PUNCH.append(157.5)
ex('dips', 157.5, 186.0, x=1220)
title('DIPS', 157.6, 162.0, y=130, size=110)
dp = [e for e in EL if e.get('pose') == 'dips'][0]
dp['glow'] = [(0, 162.5), (1, 177.2), (2, 179.0)]
chip('TRICEPS', 162.5, 166.0, LC, 380, 'on', 56)
chip('> CLOSE-GRIP BENCH', 163.4, 166.0, LC, 490, 'check', 48); PUNCH.append(165.0)
chip('SAFE vs DANGEROUS', 166.1, 170.5, LC, 450, 'n', 50)
chip('SHOULDER BLADES:', 170.6, 177.0, LC, 380, 'n', 48)
chip('DOWN & BACK', 171.6, 177.0, LC, 480, 'on', 52)
chip('LOCKED', 174.6, 177.0, LC, 580, 'check', 52)
chip('LEAN FORWARD = CHEST', 177.1, 179.5, LC, 450, 'on', 46)
chip('SHOULDERS PARALLEL', 179.6, 184.5, LC, 380, 'on', 46)
chip('1 SEC PAUSE', 182.0, 184.5, LC, 480, 'n', 48)
chip('EXPLOSIVE!', 184.6, 186.0, LC, 450, 'on', 60); PUNCH.append(184.6); R.SHAKES.append((184.6, 0.3))
ex('benchdip', 186.0, 200.0, x=1200)
chip('NOT READY?', 186.2, 189.0, LC, 330, 'n', 48)
chip('BENCH DIPS', 187.2, 200.0, LC, 430, 'on', 52)
chip('90° ANGLE', 190.6, 193.5, LC, 540, 'n', 48)
chip('15–20 REPS → BARS', 193.6, 200.0, LC, 540, 'check', 46)
chip('12–15 ON BARS → + WEIGHT', 197.1, 200.0, LC, 640, 'check', 42)
ex('dips', 200.0, 207.5, x=1220, glow=[(0, 200.4), (1, 200.4), (2, 200.4)])
chip('CHEST', 200.4, 207.5, LC, 330, 'on', 50)
chip('SHOULDERS', 200.9, 207.5, LC, 420, 'on', 50)
chip('TRICEPS', 201.4, 207.5, LC, 510, 'on', 50)
chip('FUNCTIONAL MASS', 203.5, 207.5, LC, 630, 'check', 48)

# 4 decline push-ups
big('#4', 207.5, 209.5, x=360, y=300, size=200); PUNCH.append(207.5)
ex('decline', 207.5, 209.5, x=1060, y=900)
title('DECLINE PUSH-UPS', 207.6, 209.5, y=130, size=92)
ex('pushup', 209.5, 222.0, x=1000, y=900, period=1.0)
big('20', 211.5, 216.0, x=960, y=330, size=200)
chip('STOPS WORKING', 213.5, 216.0, 1180, 270, 'strike', 50)
chip('MORE REPS?', 216.1, 222.0, 1180, 270, 'n', 50)
chip('CHEST WON\'T GROW', 218.5, 222.0, 1180, 370, 'dimx', 46)
ex('decline', 222.0, 239.0, x=1060, y=900, glow=[(0, 229.6), (1, 230.6)])
chip('RANGE OF MOTION', 222.2, 226.5, 1150, 260, 'on', 48)
chip('LOAD ANGLE', 223.6, 226.5, 1150, 350, 'on', 48)
chip('1: UPPER CHEST + FRONT DELTS', 229.6, 239.0, 60, 260, 'on', 44)
chip('2: + BODYWEIGHT EVERY REP', 233.6, 239.0, 60, 350, 'on', 44)
char('point', 239.0, 251.0, x=620)
chip('STRETCHED POSITION', 241.6, 251.0, RC - 60, 330, 'on', 50)
big('+50–100%', 247.6, 251.0, x=1380, y=520, size=150); PUNCH.append(247.6)
ex('decline', 251.0, 274.5, x=1060, y=900, period=3.6, glow=[(0, 251.0), (1, 251.0)])
chip('BOX: 18–24 IN', 251.2, 255.5, 1150, 260, 'on', 48)
chip('HANDS SLIGHTLY WIDER', 255.6, 261.5, 1100, 260, 'on', 46)
chip('BODY RIGID', 257.6, 261.5, 1100, 350, 'n', 46)
chip('NO SAGGING HIPS', 260.0, 261.5, 1100, 440, 'strike', 46)
chip('3–4 SEC DOWN', 261.6, 265.0, 1150, 260, 'on', 50)
big('3 × 8–12', 266.0, 270.0, x=960, y=330, size=150); PUNCH.append(266.0)
chip('15 CLEAN?', 270.1, 274.5, 1150, 260, 'n', 48)
chip('FEET HIGHER / VEST', 271.6, 274.5, 1150, 350, 'on', 46)

# 5 bulgarian
big('#5', 274.5, 276.5, x=560, y=360, size=240); PUNCH.append(274.5)
ex('bulgarian', 274.5, 313.5, x=1200, glow=[(0, 288.2), (1, 289.4), (2, 304.2)])
title('BULGARIAN SPLIT SQUATS', 274.6, 279.0, y=130, size=84)
chip('LEG DAY', 276.6, 286.0, LC, 420, 'on', 60)
chip('EVERYTHING CHANGES', 282.0, 286.0, LC, 540, 'n', 48)
chip('QUADS', 288.2, 295.5, LC, 300, 'on', 50)
chip('GLUTES', 289.4, 295.5, LC, 390, 'on', 50)
prop(1, 290.5, 295.5, 360, 600, 0.36, strike=True)
chip('SPINE LOAD: 0', 293.1, 295.5, LC, 780, 'check', 48)
chip('2 STEPS IN FRONT', 295.6, 302.0, LC, 380, 'on', 48)
chip('REAR FOOT: LACES DOWN', 298.0, 302.0, LC, 480, 'on', 44)
chip('KNEE TO FLOOR, SLOWLY', 302.1, 304.0, LC, 430, 'n', 46)
chip('HIP STRETCH', 304.2, 309.5, LC, 380, 'on', 50)
chip('QUAD BURN', 306.0, 309.5, LC, 480, 'on', 50)
big('3 × 8–10', 309.6, 313.5, x=520, y=330, size=150); PUNCH.append(309.6)
chip('EACH LEG', 310.6, 313.5, LC + 120, 520, 'n', 48)
char('flex', 313.5, 318.0, glow=[(0, 313.8)])
title('NEXT LEVEL LEGS', 313.7, 318.0, y=130, size=92)

# 6 single-leg RDL
big('#6', 318.0, 321.0, x=560, y=360, size=240); PUNCH.append(318.0)
ex('rdl', 318.0, 326.0, x=1200, glow=[(0, 322.4), (1, 323.6), (2, 324.6)])
title('SINGLE-LEG RDL', 318.1, 321.0, y=130, size=96)
chip('HAMSTRINGS', 322.4, 326.0, LC, 380, 'on', 50)
chip('GLUTES', 323.6, 326.0, LC, 470, 'on', 50)
chip('FLAT BACK', 324.6, 326.0, LC, 560, 'check', 50)

# recap
ex('pullup', 326.0, 333.0, x=640, sc=0.8, glow=[(0, 326.0), (1, 326.0)])
ex(ROWPOSE, 326.5, 333.0, x=1350 if ROWPOSE != 'pullup' else 1300, sc=0.8, glow=[(2, 326.5)] if ROWPOSE == 'pullup' else None)
title('THICK, FUNCTIONAL BACK', 326.2, 333.0, y=130, size=84)
ex('decline', 333.0, 342.0, x=620, y=900, sc=0.75, glow=[(0, 333.0)])
ex('dips', 333.5, 342.0, x=1400, sc=0.85, glow=[(0, 333.5), (1, 333.5)])
title('CHEST, SHOULDERS, TRICEPS', 333.2, 342.0, y=130, size=80)
ex('bulgarian', 342.0, 350.0, x=620, sc=0.85, glow=[(0, 342.0), (1, 342.0)])
ex('rdl', 342.5, 350.0, x=1350, sc=0.85, glow=[(0, 342.5)])
title('LEGS FOR REAL LIFE', 342.2, 350.0, y=130, size=88)
char('ok', 350.0, 355.0, x=700)
big('2–3× / WEEK', 350.1, 352.5, x=1380, y=330, size=130); PUNCH.append(350.1)
chip('+ REPS', 352.6, 355.0, RC, 420, 'on', 54)
chip('+ RESISTANCE', 353.4, 355.0, RC, 530, 'on', 54)
char('think', 355.0, 361.0, x=700)
chip('LOAD', 355.4, 361.0, RC, 380, 'dimx', 52)
chip('MOVEMENT FIRST', 356.4, 361.0, RC, 490, 'check', 52)
char('flex', 361.0, 368.0, x=650, glow=[(0, 361.4), (1, 361.4), (2, 361.4), (3, 361.4)])
big('6 MONTHS', 361.2, 368.0, x=1380, y=330, size=150); PUNCH.append(361.2); R.SHAKES.append((361.2, 0.3))
char('thumb', 368.0, DUR)
chip('HEALTHY JOINTS', 368.2, DUR, RC, 420, 'check', 54)
fx('loc', 361.0, DUR, seq=[(361.0, 'roof')])
for t0 in (56.5, 109.0, 157.5, 207.5, 274.5, 318.0):
    fx('burst', t0, t0 + 0.6)
R.PUNCH[:] = PUNCH

# ---------------- subtitles (estimated word timing until the voice is recorded) ----------------
def build_subs(segs, dur):
    W = []
    for i, (t0, s) in enumerate(segs):
        t1 = segs[i + 1][0] if i + 1 < len(segs) else dur
        words = s.split(); wts = [len(w) + 2 for w in words]; tot = sum(wts)
        span = (t1 - t0) * 0.92; c = t0
        for w, wt in zip(words, wts):
            d = span * wt / tot; W.append((w, c, c + d * 0.9)); c += d
    chunks = []; cur = []
    for i, (w, a, b) in enumerate(W):
        cur.append((w, a, b)); txt = ' '.join(x[0] for x in cur)
        nxt = W[i + 1] if i + 1 < len(W) else None
        if w[-1] in '.,?!:' or len(cur) >= 4 or len(txt) > 22 or (nxt and nxt[1] - b > 0.3) or nxt is None:
            chunks.append(cur); cur = []
    out = []
    for j, c in enumerate(chunks):
        s = c[0][1]; e = chunks[j + 1][0][1] if j + 1 < len(chunks) else c[-1][2] + 0.6
        out.append((s, min(e, c[-1][2] + 0.6), c))
    return out
R.SUBS[:] = build_subs(SEG, DUR)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        R.init()
        for ts in sys.argv[2:]:
            Image.frombytes('RGB', (R.WD, R.HT), R.render(int(float(ts) * R.FPS))).save(f'/home/claude/v2_6ex/still_{ts}.png')
        sys.exit()
    out = sys.argv[2]
    start = float(sys.argv[3]) if len(sys.argv) > 3 else 0; end = float(sys.argv[4]) if len(sys.argv) > 4 else DUR
    from multiprocessing import Pool
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{R.WD}x{R.HT}', '-r', str(R.FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    with Pool(4, initializer=R.init) as p:
        for i, b in enumerate(p.imap(R.render, range(int(start * R.FPS), int(end * R.FPS)), chunksize=8)):
            ff.stdin.write(b)
            if i % 900 == 0: print(i, flush=True)
    ff.stdin.close(); ff.wait()
