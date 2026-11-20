# ---------------- timeline v3: closer to the reference (camera moves, pauses, callouts) ----------------
R.EL.clear(); R.SHAKES.clear(); R.CAM.clear()
EL = R.EL
title, big, prop, xmark = R.title, R.big, R.prop, R.xmark
def chip(text, t0, t1, x, y, style='n', size=46, anchor='l'):
    w = R.chip_img(text, size, style).width
    if anchor == 'l': x = max(10, min(x, 1905 - w))
    R.chip(text, t0, t1, x, y, style, size, anchor)
def ex(pose, t0, t1, x=960, y=968, sc=1.0, glow=None, period=None, enter='pop', frames=None, keys=None, loop=None, flip=False):
    if pose == 'pullup' and y == 968: y = 900
    EL.append(dict(k='char', pose=pose, t0=t0, t1=t1, x=x, y=y, sc=sc, enter=enter, exit='fade', flip=flip,
                   ghost=False, burn=False, zoom=0.0, glow=glow, period=period, frames=frames, keys=keys, loop=loop))
char = ex
def fx(kind, t0, t1, **kw):
    d = dict(k=kind, t0=t0, t1=t1); d.update(kw); EL.insert(0, d)
def add(kind, t0, t1, **kw):
    d = dict(k=kind, t0=t0, t1=t1); d.update(kw); EL.append(d)
def inset(t0, t1, x, y, r, pose, fr, box, chans=(), col=None, label=None):
    add('inset', t0, t1, x=x, y=y, r=r, pose=pose, fr=fr, box=box, chans=tuple(chans), col=col, label=label)
def cam(t0, t1, x, y, z, ein=0.6, eout=0.5):
    R.CAM.append((t0, t1, x, y, z, ein, eout))
def arrow(t0, t1, x0, y0, x1, y1, bend=0.0, loop=None, w=10, col=None):
    add('arrow', t0, t1, p=(x0, y0, x1, y1), bend=bend, loop=loop, w=w, col=col or R.RED)
def ring(t0, t1, x, y, r=55, col=None):
    add('ring', t0, t1, x=x, y=y, r=r, col=col or (255, 215, 40))
RC, LC = 1250, 60
PAINRED = (255, 40, 40)
PUNCH = []
BACKBOX = (0.22, 0.12, 0.78, 0.55)

# motion programs (time, frame) — loop length given separately
PU_REP = [(0, 0), (0.35, 1), (0.8, 2), (2.0, 4), (2.6, 1), (3.0, 0)]                       # up, pause on top, down
PU_SLOW = [(0, 0), (0.3, 1), (0.7, 2), (2.2, 4), (2.5, 2), (5.2, 1), (7.2, 0), (7.8, 0)]  # pause + 5 s negative
PUSH = [(0, 0), (0.4, 1), (0.7, 2), (0.9, 3), (1.2, 2), (1.4, 1), (1.6, 0)]
ROW = [(0, 0), (0.4, 1), (0.8, 2), (1.1, 3), (1.4, 4), (2.3, 4), (2.6, 3), (2.9, 2), (3.2, 1), (3.5, 0)]
DEC_SLOW = [(0, 0), (1.2, 1), (2.4, 2), (3.6, 3), (4.2, 4), (4.6, 6), (5.0, 7), (5.4, 0)]
DIP_PAUSE = [(0, 0), (0.5, 1), (1.0, 2), (1.4, 3), (2.6, 4), (2.9, 6), (3.1, 7), (3.3, 0)]
JUMP = [(0, 0), (0.4, 1), (0.8, 2), (1.2, 3), (2.6, 3), (3.3, 4), (4.0, 5), (4.7, 6), (5.3, 7), (5.7, 0)]

# 0:00 hook
ex('lazy', 0.0, 2.0, y=930, sc=0.95)
title('YEARS OF TRAINING', 0.2, 3.6, y=130, size=90)
ex('fatrobe', 2.0, 3.6, x=760)
chip('SAME BODY', 2.2, 3.6, RC, 420, 'strike', 56); PUNCH.append(2.2)
ex('think', 3.6, 4.6, x=760)
add('bubble', 3.7, 4.6, x=1150, y=230, text='WHY?')
ex('cross', 4.6, 6.0, x=760)
xmark(4.7, 6.0, cx=760, cy=560, s=380)
chip('WRONG EXERCISES', 4.8, 6.0, RC, 420, 'on', 54); PUNCH.append(4.8)
ex('flex', 6.0, 10.6, y=1000, glow=[(0, 9.0), (1, 9.0), (2, 9.0), (3, 9.0)])
CIRC = [('pullup', 4), ('tablerow', 4), ('dips', 3), ('decline', 3), ('bulgarian', 3), ('rdl', 3)]
POS = [(300, 700), (380, 420), (620, 230), (1300, 230), (1540, 420), (1620, 700)]
for i, ((p, f), (x, y)) in enumerate(zip(CIRC, POS)):
    inset(6.2 + i * 0.35, 10.6, x, y, 120, p, f, (0.0, 0.0, 1.0, 1.0))
cam(6.0, 10.6, 960, 560, 0.94, 0.1, 0.3)
big('6', 6.1, 7.4, x=960, y=100, size=130); PUNCH.append(6.1)
ex('cross', 10.6, 12.5, x=700)
prop(1, 10.6, 12.5, 1450, 380, 0.42, strike=True)
prop(4, 11.4, 12.5, 1450, 640, 0.30, strike=True)
ex('think', 12.5, 15.0, x=760)
add('bubble', 12.7, 15.0, x=1150, y=230, text='WHAT?')
title('SOUNDS IMPOSSIBLE', 13.0, 15.0, x=1380, y=520, size=70)
ex('lab', 15.0, 20.0, x=700)
title('SCIENCE EXPLAINS WHY', 15.2, 20.0, x=1350, y=330, size=64)
# "which one?" — pointing at the viewer, push-in
ex('point', 20.0, 24.0, x=760)
cam(20.0, 24.0, 820, 420, 1.35, 3.0, 0.3)
add('bubble', 20.6, 24.0, x=1400, y=200, text='WHICH ONE?')
ex('lab', 24.0, 27.0, x=600)
inset(24.3, 27.0, 1180, 380, 140, 'dips', 4, (0.2, 0.05, 0.85, 0.5), chans=(0,), label='TRICEPS')
chip('> CLOSE-GRIP BENCH', 25.0, 27.0, 1050, 640, 'n', 46)
ex('thumbs2', 27.0, 30.0)
title('STAY WITH ME', 27.6, 30.0, y=130, size=90)
# barbell damage
ex('heavysquat', 30.0, 33.0, x=760, period=2.6)
chip('HUNDREDS OF POUNDS', 31.2, 33.0, 1250, 420, 'on', 50)
ex('pain', 33.0, 37.0, x=760, glow=[(0, 33.1, PAINRED)])
cam(33.0, 37.0, 700, 520, 1.3, 0.8, 0.4)
chip('SPINE', 33.4, 37.0, 1350, 300, 'on', 56); PUNCH.append(33.4); R.SHAKES.append((33.4, 0.4))
ex('heavysquat', 37.0, 41.0, x=760, period=1.4)
chip('REP AFTER REP', 37.1, 39.0, 1250, 380, 'n', 50)
chip('YEAR AFTER YEAR', 37.9, 39.0, 1250, 480, 'on', 50)
title("HEAVY ISN'T EFFECTIVE", 39.1, 41.0, y=130, size=84); R.SHAKES.append((39.1, 0.3))
ex('benchpress', 41.0, 43.0, x=1150, y=968, sc=0.85, keys=[(0, 0), (0.5, 1), (0.9, 2), (1.3, 3), (1.6, 3), (2.0, 2), (2.3, 1), (2.6, 0)], loop=2.6)
chip('SAME WITH', 41.1, 43.0, LC, 380, 'n', 52)
chip('THE BENCH PRESS', 41.5, 43.0, LC, 480, 'strike', 52)
ex('wheel', 43.0, 48.0, x=760, enter='fade')
cam(43.0, 48.0, 760, 600, 1.15, 4.0, 0.2)
big('10+ YEARS', 43.2, 48.0, x=1450, y=300, size=130)
chip('JOINT DAMAGE', 45.5, 48.0, RC, 560, 'on', 54)
ex('lab', 48.0, 51.5, x=700)
title('WHAT SCIENCE SAYS', 48.2, 51.5, x=1350, y=360, size=66)
ex('cross', 51.5, 55.0, x=700)
prop(1, 51.6, 55.0, 1450, 420, 0.45, strike=True)
chip('NOT THE WEIGHT', 52.5, 55.0, RC, 640, 'strike', 52)
ex('flex', 55.0, 56.5, x=650, enter='fade', glow=[(0, 55.1), (1, 55.1), (2, 55.1), (3, 55.1)])
big('TENSION', 55.1, 56.5, x=1380, y=330, size=160); PUNCH.append(55.1); R.SHAKES.append((55.1, 0.3))

# #1 pull-ups
big('#1', 56.5, 58.3, x=560, y=360, size=240); PUNCH.append(56.5)
title('PULL-UPS', 56.6, 62.5, x=470, y=580, size=100)
ex('pullup', 56.5, 62.5, x=1180, keys=PU_REP, loop=3.0)
cam(58.5, 62.5, 1250, 330, 1.3, 1.5, 0.4)   # slow push-in to the bar
chip('BACK ONLY?', 59.2, 62.5, LC, 450, 'strike', 54)
ex('ok', 62.5, 68.0, x=600)
for i, (nm, ch, tt) in enumerate((('LATS', 0, 63.3), ('UPPER BACK', 1, 64.1), ('REAR DELTS', 2, 64.9), ('BICEPS', 3, 65.6))):
    inset(tt, 68.0, 1130 + (i % 2) * 360, 250 + (i // 2) * 360, 125, 'pullup', 4, BACKBOX, chans=(ch,), label=nm)
chip('+ FOREARMS + CORE', 66.5, 68.0, 1100, 880, 'n', 44)
ex('pullup', 68.0, 73.0, x=960, keys=PU_REP, loop=3.0, glow=[(0, 68.0), (1, 68.0), (2, 68.0), (3, 68.0)])
arrow(68.6, 73.0, 650, 820, 680, 300, bend=0.25, loop=3.0)
arrow(68.6, 73.0, 1270, 820, 1240, 300, bend=-0.25, loop=3.0)
chip('WHOLE BODY', 69.0, 73.0, LC, 450, 'check', 54)
ex('latpull', 73.0, 79.5, x=1150)
cam(76.5, 79.5, 1000, 420, 1.45, 1.2, 0.3)
chip('LAT PULLDOWN', 73.2, 79.5, LC, 300, 'strike', 50)
chip('MACHINE PICKS THE PATH', 76.6, 79.5, LC, 400, 'n', 44)
chip('STABILIZERS: OFF', 77.5, 79.5, LC, 500, 'dimx', 46)
# every muscle -> close-up of the glowing back
ex('pullup', 79.5, 85.8, x=1180, keys=[(0, 4), (1, 4)], glow=[(0, 79.6), (1, 79.6), (2, 79.6), (3, 79.6)])
cam(79.5, 82.0, 1180, 380, 1.3, 0.8, 0.5)
chip('EVERY MUSCLE', 79.6, 82.0, LC, 450, 'check', 54); PUNCH.append(79.6)
ring(82.2, 85.8, 1020, 135, 62); ring(82.2, 85.8, 1340, 135, 62)
chip('GRIP: SLIGHTLY WIDER', 82.2, 85.8, LC, 380, 'on', 46)
chip('ARMS: FULLY STRAIGHT', 83.8, 85.8, LC, 480, 'on', 46)
ex('pullup', 85.8, 88.0, x=1180, keys=[(0, 2), (0.2, 4), (3, 4)])
cam(86.6, 88.0, 1180, 260, 1.6, 0.5, 0.3)
chip('CHEST TO BAR', 86.0, 88.0, LC, 380, 'check', 52)
chip('NOT CHIN', 86.9, 88.0, LC, 490, 'strike', 52)
# pause on top + 5-second negative, shown literally
ex('pullup', 88.0, 94.0, x=1180, keys=[(0, 4), (1.6, 4), (1.9, 2), (4.4, 1), (6.0, 0)])
chip('PAUSE AT THE TOP', 88.1, 89.6, LC, 450, 'on', 52); PUNCH.append(88.1)
add('countdown', 89.6, 94.0, x=470, y=330, n0=5, n1=1, size=220, suf='')
chip('LOWER SLOWLY', 89.8, 94.0, LC, 560, 'on', 50)
arrow(89.8, 94.0, 1500, 300, 1500, 760, bend=0.0, w=12)
chip('NO MOMENTUM', 92.0, 94.0, LC, 660, 'dimx', 46)
ex('fatbar', 94.0, 98.5, x=1180, y=900)
cam(94.0, 98.5, 1180, 520, 1.12, 3.0, 0.3)
chip("CAN'T DO ONE?", 94.2, 98.5, LC, 300, 'n', 50)
chip('DEAD HANGS', 95.0, 98.5, LC, 400, 'on', 50)
chip('SLOW NEGATIVES', 96.0, 98.5, LC, 500, 'on', 50)
ex('pullup', 98.5, 103.0, x=1180, keys=[(0, 0), (0.45, 4), (1.8, 4), (2.3, 2), (3.6, 1), (4.5, 0)])
arrow(98.6, 99.6, 1500, 760, 1500, 300, bend=0.0, w=12)
arrow(100.4, 103.0, 1500, 300, 1500, 760, bend=0.0, w=12)
chip('JUMP TO THE TOP', 98.6, 103.0, LC, 380, 'on', 48)
chip('FIGHT GRAVITY DOWN', 100.4, 103.0, LC, 480, 'on', 48)
ex('pullup', 103.0, 107.0, x=1180, keys=PU_REP, loop=3.0)
big('10', 103.1, 107.0, x=460, y=300, size=230); PUNCH.append(103.1)
chip('+ WEIGHTED VEST', 104.6, 107.0, LC, 560, 'on', 50)
ex('back', 107.0, 109.0, x=960, sc=1.05, glow=[(0, 107.2), (1, 107.2)])
cam(107.0, 109.0, 960, 520, 1.25, 0.1, 1.4)   # starts close, pulls out
chip('REAL SIZE', 107.1, 109.0, LC, 450, 'check', 56); R.SHAKES.append((107.1, 0.25))

# #2 inverted rows
big('#2', 109.0, 111.0, x=560, y=360, size=240); PUNCH.append(109.0)
ex('fingers', 109.0, 111.0, x=1250, frames=[1, 6])
title('INVERTED ROWS', 109.1, 111.0, y=130, size=96)
ex('cross', 111.0, 115.5, x=700)
chip('IGNORED PATTERN', 111.8, 115.5, 1120, 420, 'on', 50)
ex('shoulder', 115.5, 119.5, x=760)
cam(115.5, 119.5, 760, 380, 1.55, 1.0, 0.3)
ring(116.0, 119.5, 655, 395, 60, col=PAINRED)
chip('ROUNDED SHOULDERS', 115.8, 119.5, 1250, 400, 'on', 48)
chip('CHRONIC PAIN', 117.8, 119.5, 1250, 510, 'on', 48)
ex('tablerow', 119.5, 127.5, x=1260, keys=ROW, loop=3.6)
for i, (nm, ch, tt) in enumerate((('MID BACK', 1, 120.2), ('REAR DELTS', 2, 122.4))):
    inset(tt, 127.5, 330 + i * 330, 330, 140, 'pullup', 4, BACKBOX, chans=(ch,), label=nm)
chip('TRAPS + RHOMBOIDS', 123.6, 127.5, LC, 600, 'on', 46)
chip('FULL RANGE', 125.3, 127.5, LC, 700, 'check', 46)
ex('heavysquat', 127.5, 131.0, x=1250, sc=0.8)
xmark(127.8, 131.0, cx=1250, cy=600, s=320)
chip('SPINE LOAD: 0', 128.0, 131.0, LC, 450, 'check', 56)
fx('loc', 131.0, 136.0, seq=[(131.0, 'home')])
ex('tablerow', 131.0, 154.0, x=1340, keys=ROW, loop=3.6)
chip('STURDY TABLE', 131.4, 136.0, LC, 330, 'on', 48)
chip('TRX STRAPS', 132.6, 136.0, LC, 420, 'on', 48)
chip('PARALLEL BARS', 133.8, 136.0, LC, 510, 'on', 48)
chip('GRIP: SLIGHTLY WIDER', 136.2, 141.0, LC, 380, 'on', 46)
chip('HEAD-TO-HEELS LINE', 138.0, 141.0, LC, 480, 'on', 46)
chip('CHEST TO BAR', 141.1, 146.0, LC, 380, 'check', 50)
chip('SQUEEZE SHOULDER BLADES', 142.8, 146.0, LC, 480, 'on', 44)
chip('LOWER WITH CONTROL', 146.1, 148.0, LC, 450, 'n', 48)
chip('BAR HIGHER = EASIER', 148.1, 154.0, LC, 330, 'n', 46)
arrow(148.2, 149.6, 1800, 560, 1800, 330, w=10)
chip('BAR LOWER = HARDER', 149.6, 154.0, LC, 420, 'on', 46)
arrow(149.7, 151.4, 1800, 330, 1800, 560, w=10)
chip('FEET ON BOX = ADVANCED', 151.4, 154.0, LC, 510, 'on', 44)
ex('point', 154.0, 157.5, x=560)
add('card', 154.1, 157.5, x=1280, y=470, lines=['3 SETS', '8–12 REPS', '1 SEC HOLD AT TOP'])

# #3 dips
ex('fingers', 157.5, 160.0, x=700, frames=[2])
big('#3', 157.6, 160.0, x=1300, y=300, size=220); PUNCH.append(157.6)
title('DIPS', 157.8, 160.0, x=1300, y=560, size=110)
ex('point', 160.0, 166.0, x=760)
cam(160.0, 163.0, 820, 420, 1.3, 2.0, 0.4)
add('bubble', 160.6, 166.0, x=1420, y=160, text='MORE EFFECTIVE?')
inset(163.2, 166.0, 1450, 640, 140, 'dips', 4, (0.2, 0.05, 0.85, 0.5), chans=(0,), label='TRICEPS')
ex('dips', 166.0, 177.0, x=1220)
chip('SAFE vs DANGEROUS', 166.1, 170.5, LC, 450, 'n', 50)
inset(170.6, 177.0, 380, 300, 150, 'pullup', 4, BACKBOX, chans=(1,), label='SHOULDER BLADES')
chip('DOWN & BACK', 171.6, 177.0, LC, 620, 'on', 52)
chip('LOCKED', 174.6, 177.0, LC, 720, 'check', 52)
ex('dips', 177.0, 186.0, x=1220, keys=DIP_PAUSE, loop=3.3, glow=[(1, 177.2), (0, 179.0)])
arrow(177.2, 179.5, 1180, 300, 1420, 380, bend=-0.3, w=10)
chip('LEAN FORWARD = CHEST', 177.1, 179.5, LC, 450, 'on', 46)
chip('SHOULDERS PARALLEL', 179.6, 184.5, LC, 380, 'on', 46)
chip('1 SEC PAUSE', 182.0, 184.5, LC, 480, 'n', 48)
cam(179.6, 184.5, 1220, 520, 1.35, 0.8, 0.3)
chip('EXPLOSIVE!', 184.6, 186.0, LC, 450, 'on', 60); PUNCH.append(184.6); R.SHAKES.append((184.6, 0.3))
ex('benchdip', 186.0, 197.0, x=1200)
chip('NOT READY?', 186.2, 189.0, LC, 330, 'n', 48)
chip('BENCH DIPS', 187.2, 197.0, LC, 430, 'on', 52)
chip('90° ANGLE', 190.6, 193.5, LC, 540, 'n', 48)
cam(190.6, 193.5, 1250, 480, 1.15, 0.6, 0.3)
chip('15–20 REPS? GO TO BARS', 193.6, 197.0, LC, 540, 'check', 44)
ex('weightdip', 197.0, 200.0, x=1220)
chip('12–15 ON BARS?', 197.1, 200.0, LC, 380, 'n', 48)
chip('+ WEIGHT', 197.8, 200.0, LC, 480, 'on', 56)
ex('point', 200.0, 207.5, x=560)
inset(200.4, 207.0, 1180, 330, 140, 'dips', 4, (0.2, 0.05, 0.85, 0.5), chans=(1,), label='CHEST')
inset(200.9, 207.0, 1510, 330, 140, 'dips', 4, (0.2, 0.05, 0.85, 0.5), chans=(2,), label='SHOULDERS')
inset(201.4, 207.0, 1345, 700, 140, 'dips', 4, (0.2, 0.05, 0.85, 0.5), chans=(0,), label='TRICEPS')

# #4 decline push-ups
ex('fingers', 207.5, 209.5, x=700, frames=[3])
big('#4', 207.6, 209.5, x=1300, y=300, size=220); PUNCH.append(207.6)
title('DECLINE PUSH-UPS', 207.7, 209.5, x=1300, y=560, size=80)
ex('pushup', 209.5, 219.0, x=1000, y=900, keys=PUSH, loop=1.6)
cam(213.0, 219.0, 1000, 640, 1.4, 1.5, 0.3)
big('20', 211.5, 216.0, x=420, y=200, size=200)
chip('CLEAN REPS', 212.4, 216.0, 1150, 150, 'on', 48)
chip('STOPS BUILDING MUSCLE', 213.8, 216.0, 1050, 240, 'strike', 46)
chip('MORE REPS?', 216.1, 219.0, 1150, 160, 'n', 50)
ex('facepalm', 219.0, 222.0, x=760)
chip("CHEST WON'T GROW", 219.2, 222.0, RC, 420, 'dimx', 50)
ex('decline', 222.0, 226.5, x=1060, y=900)
title('NOT VOLUME', 222.2, 226.5, y=130, size=84)
chip('RANGE OF MOTION', 223.0, 226.5, 1150, 300, 'on', 48)
chip('LOAD ANGLE', 224.4, 226.5, 1150, 390, 'on', 48)
ex('fingers', 226.5, 233.5, x=330, sc=0.8, frames=[1, 6])
ex('decline', 226.5, 239.0, x=1180, y=900, sc=0.85, glow=[(0, 229.6), (1, 230.6)])
chip('1: UPPER CHEST + FRONT DELTS', 229.6, 239.0, 640, 260, 'on', 42)
chip('2: + BODYWEIGHT EVERY REP', 233.6, 239.0, 640, 350, 'on', 42)
ex('stop', 239.0, 241.5, x=760)
cam(239.0, 241.5, 760, 420, 1.3, 0.4, 0.3)
chip('THE KEY DETAIL', 239.2, 241.5, RC, 420, 'on', 54)
ex('lab', 241.5, 247.5, x=700)
chip('STRETCHED POSITION', 241.6, 247.5, RC - 60, 330, 'on', 50)
ex('decline', 243.5, 247.5, x=1350, y=900, sc=0.55, keys=[(0, 3), (1, 3)], glow=[(0, 243.6)])
ex('point', 247.5, 251.0, x=620)
big('+50–100%', 247.6, 251.0, x=1380, y=520, size=150); PUNCH.append(247.6)
ex('decline', 251.0, 266.0, x=1060, y=900, keys=DEC_SLOW, loop=5.4, glow=[(0, 251.0), (1, 251.0)])
add('measure', 251.3, 255.5, x=520, y0=770, y1=900, text='18–24 IN', left=True)
cam(251.0, 255.5, 900, 720, 1.2, 0.8, 0.4)
chip('HANDS SLIGHTLY WIDER', 255.6, 261.5, 1100, 260, 'on', 46)
chip('BODY RIGID', 257.6, 261.5, 1100, 350, 'n', 46)
chip('NO SAGGING HIPS', 260.0, 261.5, 1100, 440, 'strike', 46)
arrow(261.6, 266.0, 1330, 560, 1330, 820, w=12)
add('countdown', 261.8, 265.6, x=960, y=280, n0=4, n1=1, size=170)
chip('3–4 SEC DOWN', 261.6, 266.0, 1150, 260, 'on', 50)
ex('point', 266.0, 270.0, x=560)
add('card', 266.1, 270.0, x=1280, y=470, lines=['3 SETS', '8–12 REPS', '3–4 SEC DOWN'])
ex('decline', 270.0, 274.5, x=1060, y=900)
chip('15 CLEAN?', 270.1, 274.5, 1150, 260, 'n', 48)
chip('FEET HIGHER / VEST', 271.6, 274.5, 1150, 350, 'on', 46)
arrow(271.8, 274.5, 650, 830, 650, 640, w=10)

# #5 bulgarian
ex('fingers', 274.5, 276.5, x=700, frames=[4])
big('#5', 274.6, 276.5, x=1300, y=300, size=220); PUNCH.append(274.6)
title('BULGARIAN SPLIT SQUATS', 274.7, 276.5, x=1300, y=560, size=60)
ex('thumbs2', 276.5, 279.0, x=700)
chip('LEG DAY', 276.6, 279.0, RC, 420, 'on', 60)
ex('point', 279.0, 282.0, x=560)
inset(279.2, 282.0, 1300, 520, 200, 'bulgarian', 3, (0.0, 0.0, 1.0, 1.0))
ex('flex', 282.0, 286.0, x=960, glow=[(0, 282.6)])
cam(282.6, 286.0, 960, 600, 1.15, 0.8, 0.4)
chip('EVERYTHING CHANGES', 282.2, 286.0, LC, 480, 'n', 44)
ex('bulgarian', 286.0, 295.5, x=1200, glow=[(0, 288.2), (1, 289.4)])
inset(288.2, 295.5, 330, 300, 130, 'bulgarian', 3, (0.25, 0.35, 0.95, 0.85), chans=(0,), label='QUADS')
inset(289.4, 295.5, 660, 300, 130, 'bulgarian', 3, (0.25, 0.35, 0.95, 0.85), chans=(1,), label='GLUTES')
ex('heavysquat', 290.6, 295.5, x=500, y=968, sc=0.45)
xmark(291.0, 295.5, cx=500, cy=780, s=200)
chip('SPINE LOAD: 0', 293.1, 295.5, LC, 110, 'check', 44)
ex('bulgarian', 295.5, 313.5, x=1200, glow=[(0, 295.5), (2, 304.2)])
chip('2 STEPS IN FRONT', 295.6, 302.0, LC, 380, 'on', 48)
chip('REAR FOOT: LACES DOWN', 298.0, 302.0, LC, 480, 'on', 44)
cam(298.0, 302.0, 1100, 650, 1.2, 0.8, 0.4)
chip('KNEE TO FLOOR, SLOWLY', 302.1, 304.0, LC, 430, 'n', 46)
arrow(302.2, 304.0, 1080, 650, 1080, 900, w=10)
chip('HIP STRETCH', 304.2, 309.5, LC, 380, 'on', 50)
chip('QUAD BURN', 306.0, 309.5, LC, 480, 'on', 50)
cam(304.2, 309.5, 1200, 640, 1.25, 0.8, 0.4)
big('3 × 8–10', 309.6, 313.5, x=520, y=330, size=150); PUNCH.append(309.6)
chip('EACH LEG', 310.6, 313.5, LC + 120, 520, 'n', 48)
ex('stretch', 313.5, 315.5, x=700)
title('NEXT LEVEL LEGS', 313.7, 318.0, x=1350, y=400, size=72)
ex('pray', 315.5, 318.0, x=700)

# #6 single-leg RDL
big('#6', 318.0, 321.0, x=560, y=360, size=240); PUNCH.append(318.0)
ex('rdl', 318.0, 326.0, x=1200, glow=[(0, 322.4), (1, 323.6), (2, 324.6)])
title('SINGLE-LEG RDL', 318.1, 321.0, y=130, size=96)
chip('HAMSTRINGS', 322.4, 326.0, LC, 380, 'on', 50)
chip('GLUTES', 323.6, 326.0, LC, 470, 'on', 50)
chip('FLAT BACK', 324.6, 326.0, LC, 300, 'check', 50)
cam(322.4, 326.0, 1300, 600, 1.15, 0.8, 0.4)

# recap
ex('fingers', 326.0, 333.0, x=960, sc=0.9, frames=[1, 6])
ex('pullup', 326.3, 333.0, x=420, sc=0.6, keys=PU_REP, loop=3.0, glow=[(0, 326.3), (1, 326.3)])
ex('tablerow', 326.6, 333.0, x=1500, sc=0.65, keys=ROW, loop=3.6)
title('THICK, FUNCTIONAL BACK', 326.2, 333.0, y=130, size=84)
ex('decline', 333.0, 342.0, x=620, y=900, sc=0.75, glow=[(0, 333.0)])
ex('dips', 333.5, 342.0, x=1400, sc=0.85, glow=[(0, 333.5), (1, 333.5)])
title('CHEST, SHOULDERS, TRICEPS', 333.2, 342.0, y=130, size=80)
ex('bulgarian', 342.0, 350.0, x=620, sc=0.85, glow=[(0, 342.0), (1, 342.0)])
ex('rdl', 342.5, 350.0, x=1350, sc=0.85, glow=[(0, 342.5)])
title('LEGS FOR REAL LIFE', 342.2, 350.0, y=130, size=88)
ex('dumbbell', 350.0, 352.5, x=700)
big('2–3× / WEEK', 350.1, 352.5, x=1400, y=330, size=120); PUNCH.append(350.1)
ex('notepad', 352.5, 355.0, x=700)
chip('+ REPS', 352.6, 355.0, RC, 420, 'on', 54)
chip('+ RESISTANCE', 353.4, 355.0, RC, 530, 'on', 54)
ex('think', 355.0, 358.5, x=700)
chip("DON'T CHASE LOAD", 355.4, 358.5, RC - 60, 380, 'dimx', 50)
chip('OWN THE MOVEMENT', 356.4, 358.5, RC - 60, 490, 'check', 50)
ex('tools', 358.5, 361.0, x=700)
title('MOVEMENT = MECHANISM', 358.6, 361.0, x=1350, y=420, size=60)
fx('loc', 361.0, 370.6, seq=[(361.0, 'roof')])
ex('fatrobe', 361.0, 368.0, x=420, sc=0.85)
add('calendar', 361.2, 368.0, x=960, y=420, text='6 MONTHS')
ex('flex', 362.0, 368.0, x=1480, glow=[(0, 362.4), (1, 362.4), (2, 362.4), (3, 362.4)]); PUNCH.append(362.0); R.SHAKES.append((362.0, 0.3))
ex('pray', 368.0, DUR, x=700)
chip('HEALTHY JOINTS', 368.2, DUR, RC, 420, 'check', 54)
for t0 in (56.5, 109.0, 157.5, 207.5, 274.5, 318.0):
    fx('burst', t0, t0 + 0.6)
R.PUNCH[:] = PUNCH

# ---- sync on-screen text to the spoken word (same rule as the QA check) ----
import re as _re
def _norm(s): return _re.sub(r'[^a-z0-9%]', '', s.lower())
_STOP = set('the and you your with for not are this that its it is of to a in on at be up all'.split())
def sync_text(words):
    for e in R.EL:
        if e['k'] not in ('chip', 'title', 'big') or not e.get('text'): continue
        toks = [_norm(x) for x in _re.split(r'[\s/+•→=≠×?]+', e['text'])]
        toks = [x for x in toks if (len(x) >= 3 and x not in _STOP) or x.isdigit()]
        best = None
        for (w, a, b) in words:
            nw = _norm(w)
            if nw and any(nw == k or (len(k) >= 4 and (nw.startswith(k[:5]) or k.startswith(nw[:5]))) for k in toks):
                if abs(a - e['t0']) < 8 and (best is None or abs(a - e['t0']) < abs(best - e['t0'])): best = a
        if best is None: continue
        if e['t0'] - best > 1.2 or e['t0'] - best < -1.0:
            nt = best - 0.15
            if nt < e['t1'] - 0.4: e['t0'] = nt
