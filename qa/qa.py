"""Automated QA for render_v2-based videos.
usage: python3 qa.py six|squats  -> /home/claude/qa/<name>/report.md + contact sheets for visual review
Checks
 1. text: text over character, text over text, text outside frame, subtitle jumps, element timing vs voice
 2. objects: sprite jitter (feet/equipment sliding between phases), character cut by frame edge
 3. richness: long spans with no new visual event, repeated pose runs
"""
import sys, os, re, json, math
import numpy as np
from PIL import Image, ImageDraw
name = sys.argv[1]
OUT = f'/home/claude/qa/{name.replace(":", "_")}'; os.makedirs(OUT, exist_ok=True)
STEP = 0.25

if name.startswith('b5:'):
    os.environ['VDIR'] = '/home/claude/fitnessanimator/videos/' + name[3:]
    sys.path.insert(0, '/home/claude/fitnessanimator/videos/_batch5'); _a = sys.argv; sys.argv = ['x']; import render_b5 as X; sys.argv = _a
    R = X.R
    DUR = X.DUR; to_eng = lambda T: T; to_out = lambda t: t
    WORDS = []
    for sw in R.SUBS:
        WORDS += [(w, a, b) for (w, a, b) in sw[2]]
elif name in ('six', 'sai', 'walk'):
    if name == 'six': sys.path.insert(0, '/home/claude/v2_6ex'); import render_6ex as X
    elif name == 'walk':
        sys.path.insert(0, '/home/claude/fitnessanimator/videos/04_walking_belly_fat'); _a = sys.argv; sys.argv = ['x']; import render_walk as X; sys.argv = _a
    else: sys.path.insert(0, '/home/claude/v3_sai'); import render_sai as X
    R = X.R
    DUR = X.DUR; to_eng = lambda T: T; to_out = lambda t: t
    WORDS = []
    for sw in R.SUBS:
        WORDS += [(w, a, b) for (w, a, b) in sw[2]]
else:
    sys.path.insert(0, '/home/claude/en'); import render_en as X; R = X.R
    from timewarp import to_ru, to_en, EN_DUR
    DUR = EN_DUR; to_eng = to_ru; to_out = to_en
    from words_en import W as EW
    WORDS = list(EW)
R.init()
WD, HT = R.WD, R.HT
UIK = {'chip', 'title', 'big', 'inset', 'card', 'bubble', 'calendar', 'countdown', 'measure', 'count', 'days', 'blocks', 'sub', 'meter'}

def norm(s): return re.sub(r'[^a-z0-9%]', '', s.lower())
issues = {k: [] for k in ('text_char', 'text_text', 'text_edge', 'sub_jump', 'timing', 'char_edge', 'jitter', 'static', 'pose_run')}

# ---------- frame sampling ----------
sub_pos = []
prev_sub = None
T = 0.0
while T < DUR - 0.05:
    t = to_eng(T)
    R.AUDIT = {'txt': [], 'chr': []}
    R.render(int(round(t * R.FPS)))
    mask = Image.new('L', (WD, HT), 0)
    for al, (x, y) in R.AUDIT['chr']:
        mask.paste(255, (x, y), al.point(lambda v: 255 if v > 200 else 0))
    if R.CAM: mask = R.apply_cam(mask, t)
    m = np.array(mask) > 0
    # character cut by frame edge (left/right/top)
    if m[:, :3].sum() > 400 or m[:, -3:].sum() > 400 or m[:3, :].sum() > 400:
        issues['char_edge'].append(T)
    rects = []
    for key, (x0, y0, x1, y1) in R.AUDIT['txt']:
        if key[1] == 'chip': x0, y0, x1, y1 = x0 + 22, y0 + 22, x1 - 22, y1 - 22
        rects.append((key, (x0, y0, x1, y1)))
        _el = R.EL[key[0]] if isinstance(key[0], int) and key[0] < len(R.EL) else None
        _entering = _el is not None and t - _el['t0'] < 0.35
        if (x0 < -6 or y0 < -6 or x1 > WD + 6 or y1 > HT + 6) and not _entering:
            issues['text_edge'].append((T, key[2] or key[1]))
        X0, Y0, X1, Y1 = max(0, int(x0)), max(0, int(y0)), min(WD, int(x1)), min(HT, int(y1))
        if X1 > X0 and Y1 > Y0:
            ov = int(m[Y0:Y1, X0:X1].sum())
            if ov > 600: issues['text_char'].append((T, key[1], key[2], ov))
    # text over text (different elements)
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            (ka, a), (kb, b) = rects[i], rects[j]
            if ka == kb or (ka[0] == kb[0]): continue
            ix = min(a[2], b[2]) - max(a[0], b[0]); iy = min(a[3], b[3]) - max(a[1], b[1])
            if ix > 12 and iy > 12 and ix * iy > 900:
                issues['text_text'].append((T, ka[2] or ka[1], kb[2] or kb[1], int(ix * iy)))
    subs = [r for k, r in rects if k[0] == 'SUB']
    if subs:
        y = (min(r[1] for r in subs) + max(r[3] for r in subs)) / 2
        pos = 'top' if y < HT / 2 else 'bottom'
        if prev_sub and pos != prev_sub[1]: sub_pos.append((T, prev_sub[1], pos))
        prev_sub = (T, pos)
    T += STEP
R.AUDIT = None
for i, (T, a, b) in enumerate(sub_pos):
    back = [s for s in sub_pos[i + 1:] if s[0] - T < 2.0]
    issues['sub_jump'].append((T, f'{a}->{b}' + (' (flicker: back within 2s)' if back else '')))

# ---------- timing of on-screen text vs the words ----------
STOP = set('the and you your with for not are this that its it is of to a in on at be up all'.split())
for e in R.EL:
    if e['k'] not in ('chip', 'title', 'big') or not e.get('text'): continue
    toks = [norm(w) for w in re.split(r'[\s/+•→=≠×]+', e['text'])]
    toks = [w for w in toks if len(w) >= 3 and w not in STOP or w.isdigit()]
    if not toks: continue
    t0 = to_out(e['t0']); best = None
    for (w, a, b) in WORDS:
        nw = norm(w)
        if not nw: continue
        if any(nw == k or (len(k) >= 4 and (nw.startswith(k[:5]) or k.startswith(nw[:5]))) for k in toks):
            if abs(a - t0) < 8 and (best is None or abs(a - t0) < abs(best[0] - t0)): best = (a, w)
    if best is None: continue
    dt = t0 - best[0]
    if dt > 1.2 or dt < -1.0:
        issues['timing'].append((round(t0, 2), e['text'], best[1], round(best[0], 2), round(dt, 2)))

# ---------- sprite jitter: contact band (lowest 8% of the figure) between phases ----------
used = {}
for e in R.EL:
    if e['k'] == 'char': used.setdefault(e['pose'], []).append(to_out(e['t0']))
for pose, ts in used.items():
    frs = R.ANIM.get(pose)
    if not frs or len(frs) < 2: continue
    xs, ys = [], []
    for (big, fx, fy, mk, raw) in frs:
        a = np.array(big.split()[3]) > 200
        rr = np.nonzero(a.any(1))[0]
        if not len(rr): continue
        bot = rr[-1]; band = a[max(0, bot - int(0.08 * (bot - rr[0]))):bot + 1]
        cx = np.nonzero(band.any(0))[0]
        xs.append(cx.mean() - fx); ys.append(bot - fy)
    sx, sy = (max(xs) - min(xs)) if xs else 0, (max(ys) - min(ys)) if ys else 0
    if (sx > 30 or sy > 25) and pose not in ('run',):
        issues['jitter'].append((pose, round(sx), round(sy), [round(t, 1) for t in ts[:6]]))

# ---------- richness: gaps without a new visual event, long runs of the same pose ----------
ev = sorted(set([round(to_out(e['t0']), 2) for e in R.EL if e['k'] not in ('sub',)] + [round(to_out(c[0]), 2) for c in R.CAM]))
ev = [0.0] + [x for x in ev if 0 <= x <= DUR] + [DUR]
for a, b in zip(ev, ev[1:]):
    if b - a > 4.5: issues['static'].append((round(a, 1), round(b, 1), round(b - a, 1)))
chars = sorted([e for e in R.EL if e['k'] == 'char'], key=lambda e: e['t0'])
run = None
for e in chars:
    p = e['pose']; t0, t1 = to_out(e['t0']), to_out(e['t1'])
    if run and run[0] == p and t0 - run[2] < 0.3: run = (p, run[1], max(run[2], t1))
    else:
        if run and run[2] - run[1] > 12: issues['pose_run'].append((run[0], round(run[1], 1), round(run[2], 1)))
        run = (p, t0, t1)
if run and run[2] - run[1] > 12: issues['pose_run'].append((run[0], round(run[1], 1), round(run[2], 1)))

# ---------- contact sheets for the visual review (one frame shortly after each visual event) ----------
shots = [] if os.environ.get('NOSHEETS') else sorted(set(round(min(DUR - 0.1, x + 0.45), 2) for x in ev[:-1]))
per = 20; sheets = []
for si in range(0, len(shots), per):
    im = Image.new('RGB', (4 * 480, 5 * 290), (0, 0, 0)); d = ImageDraw.Draw(im)
    for j, T in enumerate(shots[si:si + per]):
        fr = Image.frombytes('RGB', (WD, HT), R.render(int(round(to_eng(T) * R.FPS)))).resize((480, 270))
        im.paste(fr, ((j % 4) * 480, (j // 4) * 290)); d.text(((j % 4) * 480 + 4, (j // 4) * 290 + 272), f'{T:.2f}s', fill=(255, 255, 0))
    p = f'{OUT}/sheet_{si // per:02d}.png'; im.save(p); sheets.append(p)

# ---------- report ----------
def fold(lst, key=lambda x: x[0]):
    out = [];
    for it in lst:
        if out and key(it) - key(out[-1][-1]) <= STEP * 2.01 and it[1:3] == out[-1][-1][1:3]: out[-1].append(it)
        else: out.append([it])
    return out
L = [f'# QA report: {name}  ({DUR:.1f} s)', '']
def sec(title, rows):
    L.append(f'## {title} — {len(rows)}'); L.extend(rows if rows else ['- none']); L.append('')
sec('1a. Text over character', [f'- {g[0][0]:.2f}–{g[-1][0]:.2f}s  {g[0][1]} «{g[0][2]}» (max {max(x[3] for x in g)} px)' for g in fold(issues['text_char'])])
sec('1b. Text over text', [f'- {g[0][0]:.2f}–{g[-1][0]:.2f}s  «{g[0][1]}» × «{g[0][2]}»' for g in fold(issues['text_text'])])
sec('1c. Text outside the frame', [f'- {g[0][0]:.2f}–{g[-1][0]:.2f}s  «{g[0][1]}»' for g in fold(issues['text_edge'], key=lambda x: x[0])])
sec('1d. Subtitle position changes', [f'- {T:.2f}s {s}' for T, s in issues['sub_jump']])
sec('1e. On-screen text early/late vs the voice (>1.2 s late or >1 s early)', [f'- {a}s «{b}» — word «{c}» at {d}s (Δ {e:+.2f}s)' for a, b, c, d, e in issues['timing']])
ce = issues['char_edge']; groups = []
for T in ce:
    if groups and T - groups[-1][1] <= 0.51: groups[-1][1] = T
    else: groups.append([T, T])
sec('2a. Character cut by the frame edge (sides/top)', [f'- {a:.2f}–{b:.2f}s' for a, b in groups])
sec('2b. Sprite jitter: contact point slides between phases', [f'- {p}: Δx {x}px Δy {y}px (used at {ts})' for p, x, y, ts in issues['jitter']])
sec('3a. Spans with no new visual event > 4.5 s', [f'- {a}–{b}s ({d}s)' for a, b, d in issues['static']])
sec('3b. Same pose on screen > 12 s', [f'- {p}: {a}–{b}s ({b - a:.1f}s)' for p, a, b in issues['pose_run']])
L.append('## Contact sheets for manual review'); L += [f'- {s}' for s in sheets]
open(f'{OUT}/report.md', 'w').write('\n'.join(L))
json.dump({k: [list(map(str, x)) if isinstance(x, (list, tuple)) else str(x) for x in v] for k, v in issues.items()}, open(f'{OUT}/issues.json', 'w'), ensure_ascii=False, indent=0)
print('\n'.join(L[:400]))
