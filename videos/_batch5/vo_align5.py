# Map the estimated timeline of <VDIR> onto its recorded voice: phrase starts from vo/segs.json (exact, phrase-by-phrase TTS),
# word timings for subtitles from vo/words.json (faster-whisper) matched to the script words.
import os, json, re, difflib, numpy as np
VD = os.environ['VDIR']
exec(open(f'{VD}/script_en.py').read().replace("if __name__ == '__main__'", 'if False'))
SG = json.load(open(f'{VD}/vo/segs.json'))
WH = json.load(open(f'{VD}/vo/words.json')) if os.path.exists(f'{VD}/vo/words.json') else []
norm = lambda s: re.sub(r"[^a-z0-9']", '', s.lower())
ST = []
for i, (_, s) in enumerate(SEG):
    for w in s.split(): ST.append((w, i))
m = {}
if WH:
    a = [norm(w) for w, _ in ST]; b = [norm(w[0]) for w in WH]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): m[blk.a + k] = blk.b + k
WORDS = []
for i, (s0, s1) in enumerate(SG):
    ks = [k for k, (_, sg) in enumerate(ST) if sg == i]
    # anchor points inside this phrase: phrase edges + matched whisper words that fall inside it
    xs, ys0, ys1 = [ks[0] - 0.5, ks[-1] + 0.5], [s0, s1], [s0, s1]
    for k in ks:
        if k in m:
            ws, we = WH[m[k]][1], WH[m[k]][2]
            if s0 - 0.2 <= ws <= s1 + 0.2: xs.append(k); ys0.append(ws); ys1.append(we)
    o = np.argsort(xs); xs = np.array(xs)[o]; ys0 = np.array(ys0)[o]; ys1 = np.array(ys1)[o]
    for k in ks:
        st = float(np.interp(k, xs, ys0)) if k in m else float(np.interp(k - 0.5, xs, ys0))
        en = float(np.interp(k, xs, ys1)) if k in m else float(np.interp(k + 0.5, xs, ys0))
        WORDS.append((ST[k][0], st, max(st + 0.08, en)))
VO_DUR = float(open(f'{VD}/vo/dur.txt').read())
NEW_DUR = VO_DUR + 1.6
OLD = [s for s, _ in SEG] + [DUR]
NEW = [0.0] + [max(0.0, SG[i][0] - 0.15) for i in range(1, len(SG))] + [NEW_DUR]
def TM(t): return float(np.interp(t, OLD, NEW))
