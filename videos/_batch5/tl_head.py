TMX = 860
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
              lock=('props4', 2), shield=('props4', 3), cell=('props4', 4), steps=('props4', 5), watch=('props4', 6), stomach=('props4', 7),
              alarm=('props5', 0), phone=('props5', 1), bed=('props5', 2), card=('props5', 3), shaker=('props5', 4), steak=('props5', 5), wallet=('props5', 6), doorbar=('props5', 7),
              gripper=('props6', 0), mri=('props6', 1), spine=('props6', 2), box=('props6', 3), notebook=('props6', 4), dog=('props6', 5), vial=('props6', 6), moon=('props6', 7),
              dumbbells=('props', 0), barbell=('props', 1), band=('props', 2), kettlebell=('props', 3), cable=('props', 4), bench=('props', 5), scale=('props', 6), stepsbox=('props', 7),
              planche=('skills', 0), muscleup=('skills', 1), handstand=('skills', 2), pushpose=('skills', 3), lsit=('skills', 4), onearm=('skills', 5), archer=('skills', 6), pistol=('skills', 7))
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


HANDX, HANDY = 1040, 560
import math as _m
TM_H = 820
def treadmill(t0, t1, rot, fx_=TMX, fy_=968, H=TM_H):
    W_ = 529 / 409 * H
    vx, vy = (0.42 - 0.5) * W_, (0.755 - 0.5) * H
    th = _m.radians(rot)
    rx, ry = vx * _m.cos(th) + vy * _m.sin(th), -vx * _m.sin(th) + vy * _m.cos(th)
    img('treadmill', t0, t1, fx_ - rx, fy_ - ry, H, rot=rot, bob=False, pop=False, under=True)

TMX = 860
def inset(t0, t1, x, y, r, pose, fr, box, chans=(), col=None, label=None):
    add('inset', t0, t1, x=x, y=y, r=r, pose=pose, fr=fr, box=box, chans=tuple(chans), col=col, label=label)
def card(t0, t1, x, y, lines): add('card', t0, t1, x=x, y=y, lines=lines)
def bubble(t0, t1, x, y, text): add('bubble', t0, t1, x=x, y=y, text=text)
def cal(t0, t1, x, y, text): add('calendar', t0, t1, x=x, y=y, text=text)
def count(t0, t1, x, y, n0, n1, suf='', size=170): add('countdown', t0, t1, x=x, y=y, n0=n0, n1=n1, suf=suf, size=size)
def squat(t0, t1, x=960, y=968, sc=1.0, period=1.0, enter='pop', exit='fade', glow=None):
    EL.append(dict(k='squat', t0=t0, t1=t1, x=x, y=y, sc=sc, period=period, enter=enter, exit=exit, glow=glow))
