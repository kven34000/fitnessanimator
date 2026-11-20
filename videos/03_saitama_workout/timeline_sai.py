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
PUSH = [(0, 0), (0.4, 1), (0.7, 2), (0.9, 3), (1.2, 2), (1.4, 1), (1.6, 0)]
PUSH_BAD = [(0, 0), (0.6, 1), (1.1, 2), (1.5, 3), (2.2, 2), (2.6, 1), (3.0, 0)]
SIT = [(0, 0), (0.25, 1), (0.5, 3), (0.75, 4), (1.0, 7), (1.25, 8), (1.5, 7), (1.75, 4), (2.0, 3), (2.25, 1), (2.5, 0)]
LEG = [(0, 0), (0.5, 1), (1.0, 2), (1.5, 3), (2.3, 3), (2.8, 2), (3.3, 1), (3.8, 0), (4.0, 0)]
DEC_SLOW = [(0, 0), (1.2, 1), (2.4, 2), (3.6, 3), (4.0, 3), (4.6, 4), (5.2, 6), (5.8, 7), (6.3, 0), (6.6, 0)]
S = [t for t, _ in SEG] + [DUR]
def w(i, f): return S[i] + f * (S[i + 1] - S[i])
def squat(t0, t1, x=960, y=968, sc=1.0, period=1.0, glow=None):
    EL.append(dict(k='squat', t0=t0, t1=t1, x=x, y=y, sc=sc, period=period, enter='pop', exit='fade', glow=glow))

# ---------- hook ----------
ex('fatrobe', S[0], S[2], x=640)
for j, (txt, f) in enumerate((('100 PUSH-UPS', 0.0), ('100 SIT-UPS', 0.25), ('100 SQUATS', 0.5), ('10 KM RUN', 0.75))):
    chip(txt, w(0, f), S[2], RC, 260 + j * 105, 'on', 56)
big('EVERY DAY', w(1, 0.05), S[2], x=1450, y=760, size=110); PUNCH.append(w(1, 0.05)); R.SHAKES.append((w(1, 0.05), 0.3))
fx('loc', S[2], S[4], seq=[(S[2], 'roof')])
ex('hero', S[2], w(3, 0.55), x=960, sc=0.9, frames=[0, 5, 2], enter='fade')   # original hero look (replaceable shot)
title('THE MOST FAMOUS ANIME WORKOUT', w(2, 0.1), S[3], y=110, size=62)
chip('STRONGEST MAN ALIVE', w(3, 0.3), w(3, 0.55), RC + 100, 330, 'check', 46)
ex('hair', w(3, 0.55), S[4], x=960, frames=[0, 1])
chip('EVERY HAIR?!', w(3, 0.62), S[4], RC, 380, 'on', 60); PUNCH.append(w(3, 0.62))
ex('think', S[4], S[5], x=760)
add('bubble', w(4, 0.1), S[5], x=1400, y=230, text='NORMAL PERSON?')
ex('point', S[5], S[6], x=560)
add('bubble', w(5, 0.35), S[6], x=1330, y=250, text='WHICH ONE IS USELESS?')
ex('thumbs2', S[6], S[7], x=700)
title('THE ANSWER IS COMING', w(6, 0.1), S[7], x=1350, y=420, size=60)

# ---------- rules ----------
fx('loc', S[7], S[10], seq=[(S[7], 'home')])
ex('notepad', S[7], S[10], x=560)
add('card', w(7, 0.3), S[9], x=1250, y=470, lines=['100 PUSH-UPS', '100 SIT-UPS', '100 SQUATS', '10 KM RUN'])
chip('NO WEIGHTS', w(8, 0.0), S[9], 860, 770, 'dimx', 44)
chip('NO GYM', w(8, 0.35), S[9], 1330, 770, 'dimx', 44)
chip('NO DAYS OFF', w(8, 0.65), S[9], 1060, 865, 'dimx', 44)
add('calendar', w(9, 0.05), S[10], x=1300, y=420, text='30 DAYS')

# ---------- week 1 ----------
big('DAY 1', S[10], w(10, 0.8), x=480, y=260, size=170); PUNCH.append(S[10])
ex('pushup', S[10], S[12], x=1080, y=900, keys=PUSH, loop=1.6)
add('countdown', S[11], S[12], x=480, y=330, n0=1, n1=20, size=200, suf='')
chip('EASY', w(11, 0.4), S[12], LC, 520, 'check', 54)
ex('pushup', S[12], S[13], x=1080, y=900, keys=PUSH_BAD, loop=3.0)
big('30', S[12], w(12, 0.3), x=480, y=300, size=200)
chip('HIPS SAG', w(12, 0.45), S[13], LC, 380, 'dimx', 50)
chip('ELBOWS FLARE', w(12, 0.6), S[13], LC, 480, 'dimx', 50)
chip('UGLY REPS', w(12, 0.8), S[13], LC, 580, 'strike', 50)
ex('pushup', S[13], S[14], x=1150, y=900, keys=PUSH, loop=1.6)
chip('THE FIX', S[13], S[14], LC, 230, 'check', 56); PUNCH.append(S[13])
add('blocks', w(13, 0.3), S[14], x=80, y=380)
fx('blocks', w(13, 0.3), S[14], x=80, y=520)
chip('SAME 100, CLEAN FORM', w(13, 0.7), S[14], LC, 680, 'on', 46)
squat(S[14], S[15], x=760, period=1.0, glow=[(0, w(14, 0.55)), (1, w(14, 0.55))])
add('countdown', S[14], w(14, 0.95), x=1400, y=330, n0=1, n1=100, size=180, suf='')
chip('BURN AT REP 60', w(14, 0.6), S[15], RC, 560, 'on', 50)
ex('situp', S[15], w(15, 0.5), x=1100, y=920, keys=SIT, loop=2.5)
chip('SIT-UPS', S[15], w(15, 0.5), LC, 380, 'on', 54)
fx('loc', w(15, 0.5), S[16], seq=[(w(15, 0.5), 'park')])
ex('run', w(15, 0.5), S[16], x=1150, y=900)
chip('10 KM', w(15, 0.55), S[16], LC, 380, 'on', 60)
fx('loc', S[16], S[19], seq=[(S[16], 'home')])
ex('sore', S[16], S[17], x=960, frames=[0, 1])
title('NEXT MORNING...', S[16], S[17], y=130, size=80)
ex('sore', S[17], S[18], x=700, frames=[2, 3, 4])
chip('MUSCLE DAMAGE', w(17, 0.2), S[18], RC, 380, 'on', 52)
chip('NEW LOAD', w(17, 0.6), S[18], RC, 480, 'n', 52)
ex('tired', S[18], S[19], x=700)
chip('WEEK 1: WEAKER', w(18, 0.2), S[19], RC - 60, 380, 'dimx', 52)
chip('BODY IS REPAIRING', w(18, 0.6), S[19], RC - 60, 480, 'on', 46)
arrow(w(18, 0.2), S[19], 1000, 250, 1000, 640, w=12)

# ---------- weeks 2-3 ----------
big('WEEK 2', S[19], S[20], x=1350, y=360, size=160); PUNCH.append(S[19]); R.SHAKES.append((S[19], 0.25))
ex('thumbs2', S[19], S[20], x=600)
ex('pushup', S[20], w(20, 0.5), x=1080, y=900, keys=PUSH, loop=1.6)
chip('CLEAN', w(20, 0.05), w(20, 0.5), LC, 380, 'check', 56)
squat(w(20, 0.5), S[21], x=960, period=0.9)
chip('NO BURN', w(20, 0.55), S[21], RC + 150, 380, 'check', 56)
ex('flex', S[21], S[22], x=700, glow=[(3, w(21, 0.15)), (2, w(21, 0.3)), (0, w(21, 0.45))])
chip('HEART', w(21, 0.15), S[22], RC, 330, 'on', 52)
chip('LUNGS', w(21, 0.3), S[22], RC, 430, 'on', 52)
chip('MUSCLES', w(21, 0.45), S[22], RC, 530, 'on', 52)
chip('ADAPT FAST', w(21, 0.75), S[22], RC, 650, 'check', 52)
fx('loc', S[22], S[23], seq=[(S[22], 'park')])
ex('run', S[22], S[23], x=560, y=900)
big('70 KM / WEEK', w(22, 0.3), S[23], x=1420, y=300, size=100); PUNCH.append(w(22, 0.3))
chip('BURNS A LOT OF FAT', w(22, 0.7), S[23], RC - 30, 560, 'check', 48)
fx('loc', S[23], S[26], seq=[(S[23], 'home')])
ex('point', S[23], w(23, 0.55), x=640)
title('THE ANSWER...', S[23], w(23, 0.55), x=1350, y=420, size=80)
ex('situp', w(23, 0.55), S[24], x=1100, y=920, keys=SIT, loop=2.5)
xmark(w(23, 0.7), S[24], cx=1100, cy=720, s=360)
chip('SIT-UPS', w(23, 0.6), S[24], LC, 380, 'strike', 60); PUNCH.append(w(23, 0.7))
ex('fatrobe', S[24], S[25], x=640)
chip('ABS: ALREADY THERE', w(24, 0.1), S[25], RC - 60, 380, 'check', 50)
chip('HIDDEN UNDER FAT', w(24, 0.5), S[25], RC - 60, 480, 'on', 50)
ring(w(24, 0.5), S[25], 650, 600, 110)
ex('situp', S[25], w(25, 0.55), x=1100, y=920, keys=SIT, loop=2.5)
chip("WON'T BURN BELLY FAT", w(25, 0.05), w(25, 0.55), LC, 380, 'strike', 46)
ex('run', w(25, 0.55), S[26], x=700, y=900)
chip('RUNNING', w(25, 0.6), S[26], RC, 380, 'check', 52)
chip('+ DIET', w(25, 0.8), S[26], RC, 480, 'check', 52)
ex('stop', S[26], S[27], x=760)
title('THE REAL PROBLEM', w(26, 0.1), S[27], x=1400, y=420, size=70)
ex('pushup', S[27], S[28], x=1080, y=900, keys=PUSH, loop=1.1)
big('100', w(27, 0.2), S[28], x=460, y=280, size=200)
chip('NOT A CHALLENGE', w(27, 0.45), S[28], LC, 470, 'strike', 46)
chip('= ENDURANCE', w(27, 0.75), S[28], LC, 570, 'on', 50)
ex('lab', S[28], S[29], x=600)
title('PROGRESSIVE OVERLOAD', w(28, 0.05), S[29], x=1300, y=300, size=62)
chip('SAME WORK', w(28, 0.55), S[29], RC - 50, 480, 'n', 50)
chip('= NO GROWTH', w(28, 0.75), S[29], RC - 50, 580, 'dimx', 50)

# ---------- day 30 ----------
add('calendar', S[29], w(30, 0.2), x=960, y=420, text='30 DAYS'); PUNCH.append(S[29])
ex('fatrobe', w(30, 0.0), S[31], x=520, sc=0.85)
arrow(w(30, 0.2), S[31], 760, 560, 1120, 560, w=12)
ex('flex', w(30, 0.2), S[31], x=1350, sc=0.95)
chip('LESS BODY FAT', w(30, 0.4), S[31], 960, 230, 'check', 46, anchor='c')
fx('loc', S[31], S[32], seq=[(S[31], 'park')])
ex('run', S[31], S[32], x=700, y=900)
chip('ENDURANCE: MAX', w(31, 0.2), S[32], RC, 380, 'check', 54)
fx('loc', S[32], S[34], seq=[(S[32], 'home')])
ex('flex', S[32], S[33], x=700, glow=[(3, w(32, 0.2)), (0, w(32, 0.2))])
chip('MUSCLE: A LITTLE MORE', w(32, 0.15), S[33], RC - 60, 380, 'on', 46)
chip('SUPERHERO', w(32, 0.55), S[33], RC - 60, 480, 'strike', 54)
ex('hair', S[33], S[34], x=700, frames=[0, 2, 4])
chip('HAIR: STILL THERE', w(33, 0.25), S[34], RC - 60, 380, 'check', 50)
chip('NO LINK TO HAIR LOSS', w(33, 0.6), S[34], RC - 60, 480, 'on', 44)

# ---------- better version ----------
ex('notepad', S[34], S[35], x=600)
title('MAKE IT WORK', w(34, 0.1), S[35], x=1350, y=420, size=84)
ex('fingers', S[35], w(35, 0.25), x=960, frames=[0])
ex('decline', w(35, 0.25), S[36], x=1060, y=900, keys=DEC_SLOW, loop=6.6, glow=[(0, w(35, 0.3)), (1, w(35, 0.3))])
chip('1: HARDER PUSH-UPS', w(35, 0.1), S[36], 1100, 200, 'on', 46)
chip('FEET ON A BOX', w(35, 0.45), S[36], 1100, 290, 'n', 46)
chip('SLOWER REPS', w(35, 0.65), S[36], 1100, 380, 'n', 46)
ex('fingers', S[36], w(36, 0.2), x=960, frames=[1])
ex('plank', w(36, 0.2), w(36, 0.6), x=1080, y=920)
ex('legraise', w(36, 0.6), S[37], x=1080, y=930, keys=LEG, loop=4.0)
chip('2: PLANKS + LEG RAISES', w(36, 0.05), S[37], 960, 200, 'on', 46)
chip('WHOLE CORE', w(36, 0.65), S[37], 960, 290, 'check', 46)
ex('fingers', S[37], w(37, 0.2), x=960, frames=[2])
ex('lie', w(37, 0.2), S[38], x=960, y=900)
chip('3: 1–2 REST DAYS', w(37, 0.05), S[38], LC, 300, 'on', 48)
chip('SLEEP', w(37, 0.35), S[38], LC, 400, 'check', 52)
chip('GROWTH = RECOVERY', w(37, 0.6), S[38], LC, 500, 'on', 46)
fx('loc', S[38], S[39], seq=[(S[38], 'park')])
ex('run', S[38], S[39], x=700, y=900)
chip('10 KM DAILY', w(38, 0.05), S[39], RC, 380, 'strike', 52)
chip('30–40 MIN CARDIO', w(38, 0.45), S[39], RC, 480, 'check', 52)

# ---------- ending ----------
fx('loc', S[39], DUR, seq=[(S[39], 'roof')])
ex('hero', S[39], S[40], x=960, frames=[4], enter='fade')
chip('STRONGEST HERO', w(39, 0.2), S[40], RC, 380, 'strike', 50)
ex('flex', S[40], S[41], x=960, glow=[(0, w(40, 0.4)), (1, w(40, 0.4)), (2, w(40, 0.4)), (3, w(40, 0.4))]); PUNCH.append(w(40, 0.4))
title('STRONGER THAN YESTERDAY', w(40, 0.1), S[41], y=130, size=74)
ex('point', S[41], DUR, x=700)
chip('COMMENT: DAY 1', w(41, 0.1), DUR, RC - 80, 420, 'check', 54)
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
            elif e['k'] == 'chip': e['t0'] = nt; e['t1'] = nt + 1.0
