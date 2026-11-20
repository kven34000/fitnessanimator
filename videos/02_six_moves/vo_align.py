import json, re, difflib, numpy as np
exec(open('/home/claude/v2_6ex/script_en.py').read())
WH = json.load(open('/home/claude/v2_6ex/vo/words.json'))
norm = lambda s: re.sub(r"[^a-z0-9']", '', s.lower())
ST = []  # (word, seg)
for i, (_, s) in enumerate(SEG):
    for w in s.split(): ST.append((w, i))
a = [norm(w) for w, _ in ST]; b = [norm(w[0]) for w in WH]
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
m = {}
for blk in sm.get_matching_blocks():
    for k in range(blk.size): m[blk.a + k] = blk.b + k
# times for every script word: matched -> whisper, else interpolate
idx = sorted(m)
st = np.interp(range(len(ST)), idx, [WH[m[i]][1] for i in idx])
en = np.interp(range(len(ST)), idx, [WH[m[i]][2] for i in idx])
WORDS = [(w, float(s), float(e)) for (w, _), s, e in zip(ST, st, en)]
NEWSTART = []
for i in range(len(SEG)):
    k = next(j for j, (_, sg) in enumerate(ST) if sg == i); NEWSTART.append(float(st[k]))
VO_DUR = 332.93
NEW_DUR = VO_DUR + 1.6
OLD = [s for s, _ in SEG] + [DUR]; NEW = [max(0.0, x - 0.15) if i else 0.0 for i, x in enumerate(NEWSTART)] + [NEW_DUR]
def TM(t): return float(np.interp(t, OLD, NEW))
if __name__ == '__main__':
    print('matched', len(m), 'of', len(ST))
    for i in range(0, len(SEG), 10): print(SEG[i][0], '->', round(NEW[i], 2), SEG[i][1][:40])
