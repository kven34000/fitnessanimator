# ---------------- timeline: walking vs belly fat ----------------
from script_en import SEG, DUR
R.EL.clear(); R.SHAKES.clear(); R.CAM.clear()
EL = R.EL
title, big, xmark = R.title, R.big, R.xmark
def chip(text, t0, t1, x, y, style='n', size=46, anchor='l'):
    w_ = R.chip_img(text, size, style).width
    if anchor == 'l': x = max(10, min(x, 1905 - w_))
    R.chip(text, t0, t1, x, y, style, size, anchor)
def ex(pose, t0, t1, x=960, y=968, sc=1.0, glow=None, period=None, enter='pop', frames=None, keys=None, loop=None, flip=False, **kw):
    d = dict(k='char', pose=pose, t0=t0, t1=t1, x=x, y=y, sc=sc, enter=enter, exit='fade', flip=flip,
             ghost=False, burn=False, zoom=0.0, glow=glow, period=period, frames=frames, keys=keys, loop=loop)
    d.update(kw); EL.append(d)
def fx(kind, t0, t1, **kw):
    d = dict(k=kind, t0=t0, t1=t1); d.update(kw); EL.insert(0, d)
def add(kind, t0, t1, **kw):
    d = dict(k=kind, t0=t0, t1=t1); d.update(kw); EL.append(d)
def cam(t0, t1, x, y, z, ein=0.6, eout=0.5):
    R.CAM.append((t0, t1, x, y, z, ein, eout))
def arrow(t0, t1, x0, y0, x1, y1, bend=0.0, w=10, col=None):
    add('arrow', t0, t1, p=(x0, y0, x1, y1), bend=bend, loop=None, w=w, col=col or R.RED)
def ring(t0, t1, x, y, r=55, col=None):
    add('ring', t0, t1, x=x, y=y, r=r, col=col or (255, 215, 40))
def loc(t0, t1, name):
    fx('loc', t0, t1, seq=[(t0, name)])
def pan(t0, t1, name, speed=45):
    fx('bgpan', t0, t1, name=name, speed=speed)
P2D_ = '/home/claude/p2d/spr'
PROPS_ = dict(cookie=('props2', 0), car=('props2', 1), can=('props2', 2), tank=('props2', 3), trash=('props2', 4), engine=('props2', 5),
              pump=('props2', 6), sandwich=('props2', 7), treadmill=('props3', 0), sofa=('props3', 1), salad=('props3', 2), breakfast=('props3', 3),
              lunch=('props3', 4), dinner=('props3', 5), pantry=('props3', 6), elevator=('props3', 7), red=('props4', 0), green=('props4', 1),
              lock=('props4', 2), shield=('props4', 3), cell=('props4', 4), steps=('props4', 5), watch=('props4', 6), stomach=('props4', 7))
def img(name, t0, t1, x, y, h, under=False, **kw):
    s, i = PROPS_[name]
    d = dict(k='img', t0=t0, t1=t1, path=f'{P2D_}/{s}/f{i}.png', x=x, y=y, h=h); d.update(kw)
    if under: EL.insert(len([e for e in EL if e['k'] in ('loc', 'bgpan')]), d)
    else: EL.append(d)
def meter(t0, t1, label, x, y, to=1.0, col=(255, 40, 70), dur=1.2):
    add('meter', t0, t1, label=label, x=x, y=y, to=to, col=col, dur=dur)
RC, LC = 1220, 60
RED_ = (255, 40, 40); GRN = (40, 255, 110)
PUNCH = []
S = [t for t, _ in SEG] + [DUR]
def w(i, f): return S[i] + f * (S[i + 1] - S[i])
TM_Y = 958   # treadmill belt line

# ================= A. hook =================
loc(S[0], S[1], 'kitchen')
ex('cookie', S[0], S[1], x=700, frames=[0, 1])
big('600 KCAL', w(0, 0.35), S[1], x=1480, y=360, size=120); PUNCH.append(w(0, 0.35))
cam(S[0], S[1], 700, 520, 1.18)
loc(S[1], S[3], 'gym')
ex('run', S[1], S[2], x=700, y=930)
fx('speed', S[1], S[2], mode='h')
add('countdown', w(1, 0.15), S[2], x=1520, y=300, n0=1, n1=55, size=160, suf=' MIN')
ex('tired', S[2], S[3], x=640, frames=[0, 1, 2])
for j, txt in enumerate(('SWEAT', 'GASPING', 'PAIN')):
    chip(txt, w(2, 0.12 + 0.18 * j), S[3], RC, 300 + 110 * j, 'on', 60)
chip('FOR ONE SNACK', w(2, 0.75), S[3], RC, 640, 'dimx', 50); R.SHAKES.append((w(2, 0.6), 0.3))
ex('stop', S[3], S[4], x=560, frames=[2, 3])
ex('run', S[3], S[4], x=1420, y=930, sc=0.6, enter='pop')
xmark(w(3, 0.3), S[4], cx=1420, cy=700, s=230); PUNCH.append(w(3, 0.3))
ex('think', S[4], S[5], x=640)
add('bubble', w(4, 0.25), S[5], x=1320, y=300, text='OUTSMART IT')
title('PAIN CONTEST?', S[5], S[6], y=150, size=96)
ex('sore', S[5], S[6], x=960, frames=[5, 2])
fx('burst', S[5], w(5, 0.4))
ex('fatrobe', S[6], S[7], x=520, sc=0.82, frames=[0, 1])
ex('fatrobe', w(6, 0.35), S[7], x=1400, sc=0.82, frames=[5, 6])
chip('DAY 1', S[6], S[7], 520, 230, 'on', 52, anchor='c')
chip('MONTH 6', w(6, 0.35), S[7], 1400, 230, 'on', 52, anchor='c')
arrow(w(6, 0.35), S[7], 760, 560, 1150, 560, w=12)
chip('NO CHANGE', w(6, 0.7), S[7], 960, 400, 'dimx', 46, anchor='c')
pan(S[7], S[9], 'street_pm', 50)
ex('walk', S[7], S[8], x=700, y=975)
title('WALKING PROTOCOL', w(7, 0.05), S[8], x=1330, y=300, size=66)
chip('NOT JUST CALORIES', w(7, 0.4), S[8], RC - 40, 470, 'n', 48)
chip('INSULIN HACK', w(7, 0.7), S[8], RC - 40, 580, 'check', 56); PUNCH.append(w(7, 0.7))
ex('thumbs2', S[8], S[9], x=640)
chip('10 YEARS OF CARDIO', w(8, 0.4), S[9], RC - 60, 330, 'strike', 50)
big('6 MIN', w(8, 0.1), S[9], x=1450, y=560, size=150); PUNCH.append(w(8, 0.1))

# ================= B. stubborn belly =================
loc(S[9], S[12], 'kitchen')
ex('fatrobe', S[9], S[10], x=620, frames=[0, 2])
img('salad', w(9, 0.05), S[10], 1000, 760, 200)
chip('FACE: LEANER', w(9, 0.45), S[10], RC, 330, 'check', 52)
chip('ARMS: LEANER', w(9, 0.75), S[10], RC, 440, 'check', 52)
ex('tape', S[10], S[11], x=760, frames=[0, 1, 2, 3])
chip('WAIST: SAME', w(10, 0.4), S[11], RC + 40, 380, 'dimx', 54)
cam(S[10], S[11], 760, 620, 1.3); PUNCH.append(w(10, 0.4))
ex('fatrobe', S[11], S[12], x=640, frames=[2])
img('shield', w(11, 0.35), S[12], 655, 600, 300)
title('DEFENSE SYSTEM', w(11, 0.3), S[12], x=1380, y=360, size=70)
loc(S[12], S[14], 'lab')
ex('lab', S[12], S[14], x=520, frames=[0, 1, 4])
img('cell', w(12, 0.3), S[14], 1250, 560, 280)
chip('FAT CELL SWITCHES', w(12, 0.4), w(13, 0.05), RC - 120, 260, 'on', 50)
img('green', S[13], S[14], 1600, 520, 380)
chip('BETA = GREEN LIGHT', w(13, 0.05), S[14], RC - 120, 260, 'check', 50)
add('fire', w(13, 0.6), S[14], x=1310, y=700)
chip('ENERGY BURNS', w(13, 0.6), S[14], RC - 60, 860, 'on', 46)
ex('flex', S[14], S[15], x=640, frames=[3], glow=[(3, w(14, 0.25)), (1, w(14, 0.35))])
for j, txt in enumerate(('FACE', 'ARMS', 'CHEST')):
    chip(txt, w(14, 0.15 + 0.15 * j), S[15], RC, 320 + 105 * j, 'check', 54)
chip('LEAN OUT FIRST', w(14, 0.75), S[15], RC, 660, 'on', 50)
ex('fatrobe', S[15], S[16], x=620, frames=[2])
img('red', w(15, 0.05), S[16], 1230, 520, 380)
img('lock', w(15, 0.5), S[16], 640, 610, 170); PUNCH.append(w(15, 0.5))
chip('ALPHA = RED LIGHT', w(15, 0.1), S[16], RC + 120, 300, 'on', 48)
chip('DOORS LOCKED', w(15, 0.55), S[16], RC + 120, 410, 'dimx', 48)
ex('flex', S[16], S[17], x=760, frames=[0], glow=[(2, w(16, 0.1), RED_)])
for j, (dx_, dy_) in enumerate(((-230, -40), (210, -60), (-250, 140), (230, 120), (0, 260))):
    img('red', w(16, 0.25 + 0.1 * j), S[17], 760 + dx_, 560 + dy_, 110)
chip('BELLY: WAY MORE', w(16, 0.4), S[17], RC + 80, 330, 'on', 50)
cam(S[16], S[17], 760, 560, 1.2)
loc(S[17], S[18], 'cave')
ex('caveman', S[17], S[18], x=640, frames=[1, 5])
add('fire', w(17, 0.1), S[18], x=1300, y=930)
chip('STARVATION INSURANCE', w(17, 0.35), S[18], RC - 60, 300, 'on', 46)

# ================= C. cardio trap =================
loc(S[18], S[23], 'gym')
ex('run', S[18], w(18, 0.34), x=760, y=930)
ex('dumbbell', w(18, 0.34), w(18, 0.67), x=760)
ex('pushup', w(18, 0.67), S[19], x=760, y=900, keys=[(0, 0), (0.25, 1), (0.45, 3), (0.65, 1), (0.8, 0)], loop=0.8)
for j, txt in enumerate(('SPRINTS', 'CROSSFIT', 'INTERVALS')):
    chip(txt, w(18, 0.02 + 0.33 * j), S[19], 1400, 280 + 105 * j, 'on', 54)
fx('speed', S[18], S[19], mode='r')
ex('tired', S[19], S[20], x=600, frames=[0, 3])
meter(w(19, 0.15), S[20], 'ADRENALINE', 1180, 380)
meter(w(19, 0.55), S[20], 'CORTISOL', 1180, 560); R.SHAKES.append((w(19, 0.55), 0.25))
ex('flex', S[20], S[21], x=700, frames=[3], glow=[(1, w(20, 0.05)), (2, w(20, 0.5), RED_)])
img('green', w(20, 0.05), S[21], 1280, 330, 200)
chip('ARMS', w(20, 0.05), S[21], 1400, 330, 'check', 50)
img('red', w(20, 0.5), S[21], 1280, 620, 200)
chip('BELLY', w(20, 0.5), S[21], 1400, 620, 'on', 50)
ex('fatrobe', S[21], S[22], x=640, frames=[0, 2])
chip('CORTISOL', w(21, 0.05), S[22], RC + 60, 260, 'on', 56)
arrow(w(21, 0.2), S[22], 1260, 330, 780, 600, bend=0.25, w=12)
fx('flow', w(21, 0.3), S[22], x=650, y=760)
chip('= BELLY FAT STORAGE', w(21, 0.55), S[22], RC + 140, 470, 'n', 46)
cam(S[21], S[22], 640, 600, 1.15)
ex('crawl', S[22], S[23], x=820, y=968, frames=[0, 1, 2, 5])
title('HARDER = FATTER?', w(22, 0.05), S[23], y=170, size=90); PUNCH.append(w(22, 0.2))

# ================= D. two fuel tanks =================
ex('point', S[23], S[24], x=520)
title('TWO FUEL TANKS', w(23, 0.0), S[24], x=1320, y=230, size=70)
img('can', w(23, 0.2), S[24], 1100, 620, 260)
img('tank', w(23, 0.45), S[24], 1550, 620, 330)
ex('ok', S[24], S[25], x=520)
img('can', S[24], S[25], 1050, 600, 380)
chip('TANK A = SUGAR', w(24, 0.2), S[25], RC + 120, 330, 'on', 50)
chip('SPRINTS', w(24, 0.55), S[25], RC + 120, 440, 'n', 46)
chip('HEAVY LIFTS', w(24, 0.75), S[25], RC + 120, 540, 'n', 46)
ex('tanker', S[25], S[26], x=700, sc=0.86, keys=[(0, 0), (0.5, 1), (1.0, 2), (1.5, 3), (2.0, 4), (3.5, 5)], loop=None)
chip('TANK B = BODY FAT', w(25, 0.25), S[26], RC + 100, 330, 'check', 48)
chip('SLOW, LONG, EASY', w(25, 0.6), S[26], RC + 100, 440, 'n', 46)
loc(S[26], S[27], 'lab')
ex('lab', S[26], S[27], x=520, frames=[1, 3])
add('card', w(26, 0.25), S[27], x=1300, y=470, lines=['54 STUDIES', 'ONE ANSWER'])
ex('run', S[27], S[29], x=520, y=930, sc=0.85)
ex('walk', S[27], S[29], x=1360, sc=0.88)
chip('HIGH: SUGAR', w(27, 0.05), S[29], 520, 240, 'on', 48, anchor='c')
chip('LOW: FAT', w(27, 0.5), S[29], 1360, 240, 'check', 48, anchor='c')
img('lunch', w(28, 0.05), S[29], 950, 720, 170)
img('cell', w(28, 0.5), S[29], 1660, 560, 170, shrink=True, sdelay=0.4, sdur=1.6)
chip('YOUR BELLY', w(28, 0.5), S[29], 1660, 400, 'n', 40, anchor='c')
pan(S[29], S[30], 'park', 45)
ex('walkphone', S[29], S[30], x=640, y=975)
add('card', w(29, 0.1), w(29, 0.55), x=1350, y=470, lines=['ZONE 2', 'YOU CAN STILL TALK'])
chip('CORTISOL: LOW', w(29, 0.55), S[30], RC + 40, 380, 'check', 50)
chip('RED LIGHTS: OFF', w(29, 0.75), S[30], RC + 40, 490, 'check', 50)
fx('burst', S[30], S[31])
big('WALKING', S[30], S[31], x=960, y=480, size=200); PUNCH.append(S[30]); R.SHAKES.append((S[30], 0.25))
loc(S[31], S[32], 'home')
ex('mailman', S[31], S[32], x=620, frames=[0, 2, 4, 6])
chip('COUCH STROLL', w(31, 0.05), S[32], RC + 40, 300, 'dimx', 48)
chip('MAILMAN = SHREDDED?', w(31, 0.5), S[32], RC - 40, 420, 'strike', 46)

# ================= E. calorie myth =================
ex('notepad', S[32], S[33], x=560, y=990)
chip('30 MIN RUN: 350 KCAL', w(32, 0.15), S[33], RC - 100, 340, 'on', 46)
chip('30 MIN WALK: 150 KCAL', w(32, 0.5), S[33], RC - 100, 450, 'n', 46)
ex('flex', S[33], S[34], x=600, frames=[0])
img('stomach', w(33, 0.35), S[34], 1350, 540, 330)
chip('GHRELIN = HUNGER', w(33, 0.5), S[34], RC, 270, 'on', 50); R.SHAKES.append((w(33, 0.6), 0.35))
loc(S[34], S[36], 'kitchen')
ex('fateat', S[34], S[35], x=700, frames=[0, 1, 2, 3, 4])
chip('1 HOUR LATER', w(34, 0.0), S[35], RC + 60, 280, 'n', 48)
chip('+400 KCAL', w(34, 0.55), S[35], RC + 60, 390, 'on', 60); PUNCH.append(w(34, 0.55))
ex('facepalm', S[35], S[36], x=620)
chip('-350 BURNED', w(35, 0.15), S[36], RC, 300, 'n', 48)
chip('+400 EATEN', w(35, 0.35), S[36], RC, 400, 'n', 48)
big('+50', w(35, 0.6), S[36], x=1420, y=620, size=170); PUNCH.append(w(35, 0.6))
loc(S[36], w(36, 0.55), 'home')
ex('lazy', S[36], w(36, 0.55), x=960, y=900)
chip('COUCH', w(36, 0.1), w(36, 0.55), 960, 260, 'on', 54, anchor='c')
loc(w(36, 0.55), S[37], 'elevator')
ex('tired', w(36, 0.55), S[37], x=760, frames=[4, 5])
chip('ELEVATOR', w(36, 0.6), S[37], RC + 80, 330, 'on', 52)
chip('LESS MOVING', w(36, 0.8), S[37], RC + 80, 440, 'dimx', 50)
pan(S[37], S[38], 'street_am', 50)
ex('walk', S[37], S[38], x=640, y=975)
meter(w(37, 0.1), S[38], 'HUNGER', 1180, 380, to=0.25, col=GRN)
meter(w(37, 0.45), S[38], 'ENERGY', 1180, 560, to=0.9, col=GRN)
ex('point', S[38], S[39], x=560)
fx('loc', S[38], S[39], seq=[(S[38], 'park')])
chip('1 HOUR = 300 KCAL', w(38, 0.05), S[39], RC - 80, 300, 'on', 48)
chip('1 WEEK = 2100 KCAL', w(38, 0.35), S[39], RC - 80, 410, 'on', 48)
chip('1 YEAR = ~14 KG FAT', w(38, 0.65), S[39], RC - 80, 520, 'check', 50); PUNCH.append(w(38, 0.65))
ex('pain', S[39], S[40], x=520, frames=[2, 3], sc=0.9)
chip('QUITS IN 3 WEEKS', w(39, 0.1), S[40], 520, 230, 'dimx', 44, anchor='c')
ex('walk', w(39, 0.45), S[40], x=1380, y=975, sc=0.9)
chip('NEVER STOPS', w(39, 0.55), S[40], 1380, 230, 'check', 48, anchor='c')

# ================= F. step 1 =================
ex('flex', S[40], S[41], x=560, frames=[0], glow=[(2, w(40, 0.3), RED_)])
img('pantry', w(40, 0.05), S[41], 1450, 560, 520)
meter(w(40, 0.15), S[41], 'INSULIN', 900, 230, to=0.95)
chip('FAT BURNING: OFF', w(40, 0.6), S[41], 900, 340, 'dimx', 46)
ex('fingers', S[41], S[42], x=600, frames=[0])
title('STEP 1', w(41, 0.0), S[42], x=1330, y=360, size=110)
chip('WALK AFTER MEALS', w(41, 0.3), S[42], RC, 500, 'on', 54); PUNCH.append(S[41])
loc(S[42], S[43], 'lab')
ex('lab', S[42], S[43], x=520, frames=[1, 4])
add('card', w(42, 0.1), S[43], x=1300, y=430, lines=['10 MIN WALK', 'RIGHT AFTER EATING'])
chip('BLOOD SUGAR: CONTROLLED', w(42, 0.6), S[43], 1300, 760, 'check', 44, anchor='c')
_B = (0.0, 0.72, 0.86, 1.0)
for j, (bgn, plate, lab_) in enumerate((('street_am', 'breakfast', 'AFTER BREAKFAST'), ('park', 'lunch', 'AFTER LUNCH'), ('street_pm', 'dinner', 'AFTER DINNER'))):
    a_, b_ = w(43, _B[j]), w(43, _B[j + 1])
    pan(a_, b_, bgn, 50)
    ex('walk', a_, b_, x=760, y=975, enter='none' if j else 'pop')
    img(plate, a_ + 0.05, b_, 1420, 400, 230)
    chip(lab_, a_ + 0.1, b_, 1420, 620, 'on', 46, anchor='c')
chip('3 WALKS x 10 MIN', w(43, 0.05), w(43, 0.7), 1420, 760, 'check', 44, anchor='c')
pan(S[44], S[45], 'street_pm', 50)
ex('walk', S[44], S[45], x=640, y=975, enter='none')
chip('30 MIN CARDIO', w(44, 0.05), S[45], RC, 300, 'on', 50)
chip('3000 STEPS', w(44, 0.35), S[45], RC, 410, 'on', 50)
chip('NO GYM CLOTHES', w(44, 0.65), S[45], RC, 520, 'check', 50)
ex('flex', S[45], S[46], x=760, frames=[3], glow=[(0, w(45, 0.35)), (1, w(45, 0.35)), (3, w(45, 0.35))])
img('dinner', S[45], w(45, 0.45), 1450, 420, 220)
arrow(w(45, 0.2), S[46], 1350, 470, 950, 520, bend=-0.2, w=12, col=GRN)
chip('MEAL = FUEL', w(45, 0.45), S[46], RC + 80, 640, 'check', 54)

# ================= G. step 2 NEAT =================
ex('fingers', S[46], w(46, 0.25), x=960, frames=[1], sc=0.9)
title('STEP 2: NEAT', S[46], S[47], y=150, size=78); PUNCH.append(S[46])
ex('flex', w(46, 0.25), S[47], x=560, sc=0.85, frames=[0])
ex('fatrobe', w(46, 0.25), S[47], x=1360, sc=0.85, frames=[0])
chip('UP TO 2000 KCAL / DAY', w(46, 0.55), S[47], 960, 300, 'on', 46, anchor='c')
loc(S[47], S[48], 'parking')
img('car', w(47, 0.0), S[48], 1500, 900, 230)
ex('walk', S[47], S[48], x=1050, y=975, flip=True, vx=-130)
chip('HACK 1: PARK FAR', w(47, 0.05), S[48], 1330, 280, 'on', 50)
chip('+400 STEPS', w(47, 0.5), S[48], 1330, 390, 'check', 56); PUNCH.append(w(47, 0.5))
loc(S[48], S[49], 'office')
ex('walkphone', S[48], S[49], x=380, y=975, vx=170)
chip('HACK 2: WALK ON CALLS', w(48, 0.1), S[49], 960, 130, 'on', 48, anchor='c')
loc(S[49], S[50], 'stairs')
ex('walk', S[49], S[50], x=900, y=975)
img('elevator', S[49], S[50], 360, 600, 380, bob=False)
xmark(w(49, 0.2), S[50], cx=360, cy=600, s=170)
chip('HACK 3: TAKE THE STAIRS', w(49, 0.1), S[50], RC - 100, 260, 'on', 46)
big('3X', w(49, 0.55), S[50], x=1500, y=520, size=170); PUNCH.append(w(49, 0.55))
ex('thumbs2', S[50], S[51], x=600)
img('steps', w(50, 0.05), S[51], 1350, 560, 460)
add('count', w(50, 0.2), S[51], x=1350, y=180, n0=0, n1=10000)
chip('8-10K STEPS', w(50, 0.6), S[51], 600, 170, 'check', 50, anchor='c')

# ================= H. step 3 incline =================
ex('fingers', S[51], S[52], x=560, frames=[2])
title('STEP 3: INCLINE', w(51, 0.05), S[52], x=1330, y=300, size=70)
img('treadmill', w(51, 0.3), S[52], 1380, 700, 400, rot=10)
fx('burst', w(51, 0.45), w(51, 0.95)); R.SHAKES.append((w(51, 0.45), 0.35)); PUNCH.append(w(51, 0.45))
chip('THE NUCLEAR OPTION', w(51, 0.5), S[52], 1330, 470, 'on', 44, anchor='c')
loc(S[52], S[56], 'gym')
TMX = 860
HANDX, HANDY = 1040, 560
import math as _m
TM_H = 820
def treadmill(t0, t1, rot, fx_=TMX, fy_=968, H=TM_H):
    W_ = 529 / 409 * H
    vx, vy = (0.42 - 0.5) * W_, (0.755 - 0.5) * H
    th = _m.radians(rot)
    rx, ry = vx * _m.cos(th) + vy * _m.sin(th), -vx * _m.sin(th) + vy * _m.cos(th)
    img('treadmill', t0, t1, fx_ - rx, fy_ - ry, H, rot=rot, bob=False, pop=False, under=True)
treadmill(S[52], S[54], 10)
ex('walk', S[52], S[54], x=TMX, y=968, sc=0.85, glow=[(2, w(52, 0.45))], enter='fade')
big('2X', w(52, 0.05), w(52, 0.45), x=1500, y=300, size=150)
chip('GLUTES', w(52, 0.5), S[53], RC + 160, 300, 'check', 52)
chip('HAMSTRINGS', w(52, 0.65), S[53], RC + 160, 410, 'check', 52)
cam(w(52, 0.45), S[53], TMX - 40, 700, 1.25)
add('card', w(53, 0.05), S[54], x=1470, y=360, lines=['12 / 3 / 30', 'INCLINE / SPEED / MIN'])
treadmill(S[54], S[55], 10)
ex('rails', S[54], S[55], x=TMX, y=968, sc=0.85, enter='none')
chip('INCLINE 12', w(54, 0.2), S[55], RC + 160, 300, 'strike', 54)
big('= 2', w(54, 0.6), S[55], x=1550, y=520, size=160); PUNCH.append(w(54, 0.6))
xmark(w(54, 0.3), S[55], cx=HANDX, cy=HANDY, s=80)
treadmill(S[55], S[56], 7)
ex('walk', S[55], S[56], x=TMX, y=968, sc=0.85, enter='none')
chip('HANDS FREE', w(55, 0.05), S[56], RC + 160, 300, 'check', 50)
chip('DROP TO 8', w(55, 0.3), S[56], RC + 160, 410, 'n', 46)
chip('2-3 TIMES / WEEK', w(55, 0.6), S[56], RC + 160, 520, 'on', 46)

# ================= I. nutrition =================
loc(S[56], S[58], 'kitchen')
ex('facepalm', S[56], S[57], x=600)
img('trash', w(56, 0.1), S[57], 1350, 600, 420)
xmark(w(56, 0.5), S[57], cx=1350, cy=600, s=230)
ex('cookie', S[57], S[58], x=600, frames=[0, 4])
chip('60 MIN TO BURN', w(57, 0.2), S[58], RC, 330, 'on', 52)
chip('45 SEC TO EAT', w(57, 0.55), S[58], RC, 440, 'dimx', 52)
img('watch', w(57, 0.55), S[58], 1600, 690, 200)
img('engine', S[58], S[59], 520, 560, 330)
chip('FOOD = ENGINE', w(58, 0.05), S[59], 520, 300, 'on', 46, anchor='c')
chip('WALKING = TURBO', w(58, 0.35), S[59], 960, 830, 'check', 46, anchor='c')
img('pump', w(58, 0.6), S[59], 1450, 560, 360)
chip('NO FUEL = NO DRIVE', w(58, 0.65), S[59], 1450, 300, 'dimx', 44, anchor='c')
ex('flex', S[59], S[60], x=640, frames=[3], glow=[(0, w(59, 0.3)), (1, w(59, 0.3)), (2, w(59, 0.3)), (3, w(59, 0.3))])
chip('SMALL DEFICIT', w(59, 0.05), S[60], RC, 300, 'on', 50)
chip('+ THIS PROTOCOL', w(59, 0.3), S[60], RC, 410, 'check', 50)
img('cell', w(59, 0.5), S[60], 1500, 650, 200, shrink=True, sdelay=0.3, sdur=1.4)

# ================= J. 12-week plan + challenge =================
pan(S[60], S[61], 'street_am', 45)
ex('walk', S[60], S[61], x=600, y=975)
add('calendar', w(60, 0.0), S[61], x=1400, y=380, text='1-4 WEEKS')
chip('+2000 STEPS', w(60, 0.4), S[61], RC - 30, 760, 'on', 46)
chip('WALK AFTER MEALS', w(60, 0.7), S[61], RC - 30, 860, 'check', 44)
pan(S[61], S[62], 'street_pm', 45)
fx('rain', w(61, 0.45), w(61, 0.75))
fx('rain', w(61, 0.75), S[62], snow=True)
ex('walkphone', S[61], S[62], x=600, y=975)
add('calendar', w(61, 0.0), S[62], x=1400, y=380, text='5-8 WEEKS')
chip('8000+ STEPS', w(61, 0.3), S[62], RC - 30, 760, 'on', 46)
chip('RAIN OR SNOW', w(61, 0.6), S[62], RC - 30, 860, 'check', 44)
loc(S[62], S[63], 'gym')
treadmill(S[62], S[63], 10)
ex('walk', S[62], S[63], x=TMX, y=968, sc=0.85, glow=[(2, w(62, 0.5))])
add('calendar', w(62, 0.0), S[63], x=1660, y=360, text='9-12 WEEKS')
chip('10-12K STEPS', w(62, 0.35), S[63], RC + 60, 760, 'on', 46)
chip('+2 INCLINE SESSIONS', w(62, 0.6), S[63], RC + 60, 860, 'check', 42)
loc(S[63], w(63, 0.3), 'cave')
ex('caveman', S[63], w(63, 0.3), x=960, frames=[0])
pan(w(63, 0.3), S[64], 'park', 45)
ex('walk', w(63, 0.3), S[64], x=600, y=975)
chip('CLEARS YOUR HEAD', w(63, 0.45), S[64], RC, 300, 'check', 48)
chip('SAVES YOUR JOINTS', w(63, 0.62), S[64], RC, 410, 'check', 48)
chip('BURNS BELLY FAT', w(63, 0.8), S[64], RC, 520, 'check', 48)
ex('point', S[64], S[65], x=560)
add('calendar', w(64, 0.05), S[65], x=1300, y=390, text='7 DAYS'); PUNCH.append(w(64, 0.05))
chip('TRACK STEPS', w(64, 0.45), S[65], 1300, 760, 'on', 44, anchor='c')
chip('10 MIN AFTER MEALS', w(64, 0.65), S[65], 1300, 860, 'check', 42, anchor='c')
loc(S[65], DUR, 'roof')
ex('flex', S[65], DUR, x=700, frames=[3], glow=[(0, w(65, 0.2)), (1, w(65, 0.2)), (2, w(65, 0.2)), (3, w(65, 0.2))])
chip('MORE ENERGY', w(65, 0.15), DUR, RC, 300, 'check', 50)
chip('LESS BLOATING', w(65, 0.4), DUR, RC, 410, 'check', 50)
chip('LOOSER PANTS', w(65, 0.65), DUR, RC, 520, 'check', 50); PUNCH.append(w(65, 0.65))
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
        for (w_, a, b) in words:
            nw = _norm(w_)
            if nw and any(nw == k or (len(k) >= 4 and (nw.startswith(k[:5]) or k.startswith(nw[:5]))) for k in toks):
                if abs(a - e['t0']) < 8 and (best is None or abs(a - e['t0']) < abs(best - e['t0'])): best = a
        if best is None: continue
        if e['t0'] - best > 1.2 or e['t0'] - best < -1.0:
            nt = best - 0.15
            if nt < e['t1'] - 0.4: e['t0'] = nt
            elif e['k'] == 'chip': e['t0'] = nt; e['t1'] = nt + 1.0
