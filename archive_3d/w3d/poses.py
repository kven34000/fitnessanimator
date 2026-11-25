"""Procedural poses for the Tripo-rigged hero.
Native model space: forward +X, up +Y, lateral Z (arm/leg A at -Z, B at +Z).
Each pose = {'bones': {name: [[axis, angle], ...]}, 'root': [dx, dy, dz]}.
Angles are deltas in the rest (T-pose) world frame; children inherit parents (FK).
"""
import math

Z = [0, 0, 1]; X = [1, 0, 0]; Y = [0, 1, 0]
LEG_A = ['tripo0_Left_Limb_0', 'tripo0_Left_Limb_1', 'tripo0_Left_Limb_2']
LEG_B = ['tripo1_Left_Limb_0', 'tripo1_Left_Limb_1', 'tripo1_Left_Limb_2']
PELVIS, CHEST = 'tripo0_Right_Limb_0', 'tripo0_Right_Limb_1'
ARM_A = ['tripo0_Right_Limb_2', 'tripo0_Right_Limb_3', 'tripo0_Right_Limb_4', 'tripo0_Right_Limb_5']  # clav, shoulder, elbow, wrist (-Z)
ARM_B = ['tripoSpine_0', 'bone_26', 'bone_27', 'bone_28']  # (+Z)
NECK, HEAD = 'bone_39', 'tripoHead_0'
FING_A = ['bone_15', 'bone_16', 'bone_17', 'bone_18', 'bone_19', 'bone_20', 'tripo0_Right_Limb_6', 'tripo0_Right_Limb_7', 'bone_23', 'bone_24']
FING_B = ['bone_29', 'bone_30', 'bone_31', 'bone_32', 'bone_33', 'bone_34', 'bone_35', 'bone_36', 'bone_37', 'bone_38']

HIP = (0.002, 0.509); KNEE = (-0.014, 0.286); ANK = (-0.029, 0.075)
L1 = math.dist(HIP, KNEE); L2 = math.dist(KNEE, ANK)
def ang(v): return math.atan2(v[0], -v[1])  # 0 = straight down, + = forward
R_TH = ang((KNEE[0] - HIP[0], KNEE[1] - HIP[1])); R_SH = ang((ANK[0] - KNEE[0], ANK[1] - KNEE[1]))

def lerp(a, b, t): return a + (b - a) * t
def smooth(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)

def leg_ik(hx, hy, ax=ANK[0], ay=ANK[1]):
    vx, vy = ax - hx, ay - hy
    d = min(math.hypot(vx, vy), L1 + L2 - 1e-4)
    base = ang((vx, vy))
    a1 = base + math.acos(max(-1, min(1, (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))))
    a2 = base - math.acos(max(-1, min(1, (L2 * L2 + d * d - L1 * L1) / (2 * L2 * d))))
    th = a1 - R_TH; sh = a2 - R_SH
    return th, sh - th, -sh  # hip delta, knee relative, ankle relative (foot flat)

def add(b, name, axis, a):
    if abs(a) < 1e-6: return
    b.setdefault(name, []).append([axis, a])

def arms(b, A, B):
    """A/B dicts: down (0..1 arm lowered), fwd (0..1 arm forward), up, elbow (rad bend), twist"""
    for side, chain, sgn in (('A', ARM_A, -1), ('B', ARM_B, 1)):
        p = A if side == 'A' else B
        sh = chain[1]
        add(b, sh, Y, sgn * p.get('fwd', 0) * math.pi / 2)           # swing forward
        add(b, sh, X, sgn * p.get('down', 0) * math.radians(78))     # lower to side
        add(b, sh, X, -sgn * p.get('up', 0) * math.radians(80))      # raise above
        e = p.get('elbow', 0)
        if e:
            if p.get('fwd', 0) > 0.5 or p.get('ebend') == 'y':
                add(b, chain[2], Y, sgn * e)                          # bend inward (horizontal)
            else:
                add(b, chain[2], X, -sgn * e)                         # bend upward (biceps curl)
        if p.get('fist'):
            for f in (FING_A if side == 'A' else FING_B):
                add(b, f, Y if p.get('fwd', 0) > 0.5 else X, sgn * 1.2 * (1 if side == 'B' else 1))

def stand(t=0.0, arms_mode='down'):
    b = {}
    br = math.sin(t * 2.2)
    add(b, CHEST, Z, -0.02 * br)
    add(b, HEAD, Z, 0.015 * math.sin(t * 1.3))
    if arms_mode == 'down':
        arms(b, {'down': 0.92, 'elbow': 0.15}, {'down': 0.92, 'elbow': 0.15})
    return {'bones': b, 'root': [0, 0.002 * br, 0]}

def squat(depth, t=0.0, arms_fwd=True):
    """depth 0..1 (1 = thighs parallel). Feet stay planted."""
    d = depth
    hx = HIP[0] - 0.085 * d; hy = HIP[1] - 0.205 * d
    b = {}
    for leg, zs in ((LEG_A, 1), (LEG_B, 1)):
        th, kn, an = leg_ik(hx, hy)
        add(b, leg[0], Z, th); add(b, leg[1], Z, kn); add(b, leg[2], Z, an)
        add(b, leg[0], X, (0.12 if leg is LEG_B else -0.12) * d)  # knees slightly out
    lean = -0.62 * d
    add(b, PELVIS, Z, lean)
    add(b, NECK, Z, 0.35 * d)
    a = smooth(d * 2) if arms_fwd else 0
    arms(b, {'down': 0.92 * (1 - a), 'fwd': a, 'elbow': 0.1}, {'down': 0.92 * (1 - a), 'fwd': a, 'elbow': 0.1})
    # compensate shoulders for torso lean so arms stay ~horizontal
    if a > 0:
        add(b, ARM_A[1], Z, -lean * 0.9 * a); add(b, ARM_B[1], Z, -lean * 0.9 * a)
    return {'bones': b, 'root': [hx - HIP[0], hy - HIP[1], 0]}

def squat_cycle(tt, period=1.6):
    """smooth rep: down 45%, hold 10%, up 45%"""
    ph = (tt % period) / period
    if ph < 0.45: d = smooth(ph / 0.45)
    elif ph < 0.55: d = 1
    else: d = 1 - smooth((ph - 0.55) / 0.45)
    return squat(d, tt)

def double_biceps(t=0.0, k=1.0):
    b = {}
    arms(b, {'up': 0.08 * k, 'elbow': 1.9 * k, 'fist': k > 0.5}, {'up': 0.08 * k, 'elbow': 1.9 * k, 'fist': k > 0.5})
    add(b, CHEST, Z, 0.04 * k + 0.015 * math.sin(t * 6))
    return {'bones': b, 'root': [0, 0, 0]}

def point(t=0.0):
    b = {}
    arms(b, {'down': 0.92, 'elbow': 0.2}, {'fwd': 0.55, 'elbow': 0.05})
    add(b, ARM_B[1], Z, 0.12)
    add(b, CHEST, Y, 0.12)
    return {'bones': b, 'root': [0, 0, 0]}

def think(t=0.0):
    b = {}
    arms(b, {'down': 0.85, 'fwd': 0.25, 'elbow': 1.3, 'ebend': 'y'}, {'down': 0.55, 'fwd': 0.75, 'elbow': 2.3})
    add(b, ARM_B[1], X, 0.35)
    add(b, HEAD, X, -0.12)
    return {'bones': b, 'root': [0, 0, 0]}

def cross_arms(t=0.0):
    b = {}
    arms(b, {'down': 0.55, 'fwd': 0.75, 'elbow': 1.75}, {'down': 0.45, 'fwd': 0.75, 'elbow': 1.75})
    return {'bones': b, 'root': [0, 0, 0]}

def run(t, speed=9.0):
    b = {}
    s = math.sin(t * speed); c = math.cos(t * speed)
    for leg, sg in ((LEG_A, 1), (LEG_B, -1)):
        sw = sg * s
        add(b, leg[0], Z, 0.55 * sw + 0.15)
        add(b, leg[1], Z, -(0.35 + 0.65 * max(0, -sw * 0 + (1 - abs(sw)) * 0.5 + max(0, sw) * 0.9)))
    arms(b, {'down': 0.9, 'elbow': 1.4}, {'down': 0.9, 'elbow': 1.4})
    add(b, ARM_A[1], Z, -0.6 * s); add(b, ARM_B[1], Z, 0.6 * s)
    add(b, PELVIS, Z, -0.15)
    return {'bones': b, 'root': [0, 0.015 * abs(c), 0]}

def blend(p, q, k):
    """linear blend of two poses (angles per bone/axis summed with weights)"""
    if k <= 0: return p
    if k >= 1: return q
    out = {'bones': {}, 'root': [lerp(a, c, k) for a, c in zip(p.get('root', [0, 0, 0]), q.get('root', [0, 0, 0]))]}
    for src, w in ((p, 1 - k), (q, k)):
        for n, rots in src['bones'].items():
            for ax, a in rots:
                out['bones'].setdefault(n, []).append([ax, a * w])
    return out

def balance(t=0.0):
    b = {}
    sw = 0.04 * math.sin(t * 2.0)
    add(b, LEG_B[0], Z, 1.25); add(b, LEG_B[1], Z, -1.75); add(b, LEG_B[2], Z, 0.3)
    add(b, LEG_A[0], X, sw * 0.5)
    add(b, PELVIS, X, sw)
    arms(b, {'down': 0.1 + 0.05 * math.sin(t * 2.3)}, {'down': 0.1 - 0.05 * math.sin(t * 2.3)})
    return {'bones': b, 'root': [0, 0, 0]}

def legs_flex(t=0.0):
    """standing, fists on hips-ish, one leg forward on toes to show quads"""
    b = {}
    add(b, LEG_B[0], Z, 0.22); add(b, LEG_B[0], X, 0.12); add(b, LEG_B[1], Z, -0.25); add(b, LEG_B[2], Z, -0.35)
    arms(b, {'down': 0.75, 'elbow': 1.2, 'ebend': 'y', 'fist': True}, {'down': 0.75, 'elbow': 1.2, 'ebend': 'y', 'fist': True})
    add(b, CHEST, Z, 0.05)
    return {'bones': b, 'root': [0, 0, 0]}

def tall(t=0.0):
    b = {}
    add(b, CHEST, Z, 0.06); add(b, HEAD, Z, 0.04)
    arms(b, {'down': 0.95, 'elbow': 0.1}, {'down': 0.95, 'elbow': 0.1})
    add(b, ARM_A[1], Z, -0.12); add(b, ARM_B[1], Z, -0.12)
    return {'bones': b, 'root': [0, 0.003 * math.sin(t * 2), 0]}

THUMB_A = ['bone_15', 'bone_16']; THUMB_B = ['bone_29', 'bone_30']
FING_A4 = [('bone_17', 'bone_18'), ('bone_19', 'bone_20'), ('tripo0_Right_Limb_6', 'tripo0_Right_Limb_7'), ('bone_23', 'bone_24')]
FING_B4 = [('bone_31', 'bone_32'), ('bone_33', 'bone_34'), ('bone_35', 'bone_36'), ('bone_37', 'bone_38')]
def hands(k=0.55, kB=None, axis=None):
    """finger curl 0 (flat) .. 1 (fist). Curl axis = native Y (palm faces +X in rest)."""
    kB = k if kB is None else kB
    b = {}
    ax = axis or X
    for chain, sg, kk in ((FING_A4, -1, k), (FING_B4, 1, kB)):
        for i, (b1, b2) in enumerate(chain):
            add(b, b1, ax, sg * kk * (1.0 + 0.08 * i))
            add(b, b2, ax, sg * kk * 1.25)
    for th, sg, kk in ((THUMB_A, -1, k), (THUMB_B, 1, kB)):
        add(b, th[0], ax, sg * kk * 0.35); add(b, th[1], ax, sg * kk * 0.5)
    return {'bones': b, 'root': [0, 0, 0]}
