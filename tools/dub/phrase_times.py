# Phrase start times of an old video (01-04) from en_segs.json + whisper words.json.  python3 phrase_times.py <key> <words.json>
import sys, json, re, difflib
import numpy as np
from num2words import num2words
EN = json.load(open('/home/claude/fitnessanimator/tools/es_dub/en_segs.json'))[sys.argv[1]]; WH = json.load(open(sys.argv[2]))
def toks(word):
    o = []
    for p in re.split(r"[-\s]+", word.lower()):
        p = re.sub(r"[^a-z0-9']", '', p)
        if not p: continue
        if p.isdigit(): o += re.sub(r"[^a-z ]", ' ', num2words(int(p))).split()
        else: o.append(p.replace("'", ''))
    return o
ST = [(t, i) for i, s in enumerate(EN) for w in s.split() for t in toks(w)]
WT = [(t, a) for w, a, b in WH for t in toks(w)]
sm = difflib.SequenceMatcher(None, [t for t, _ in ST], [t for t, _ in WT], autojunk=False); m = {}
for b in sm.get_matching_blocks():
    for k in range(b.size): m[b.a + k] = b.b + k
idx = sorted(m); st = np.interp(range(len(ST)), idx, [WT[m[i]][1] for i in idx])
for i, s in enumerate(EN):
    k = next(k for k, (_, g) in enumerate(ST) if g == i)
    print(i, '%d:%02d' % divmod(int(st[k]), 60), s[:60])
