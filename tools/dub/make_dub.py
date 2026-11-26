# Free dubbed voice track (Piper) timed phrase-by-phrase to the English voice, same length as the EN video.
#   python3 make_dub.py <lang es|fr|ar> <key> <out.wav> <total_dur> [words.json]
# Timing source:
#   videos 05+ : videos/<key>/vo/segs.json (exact phrase starts/ends of the Magnific EN voice = video time)
#   videos 01-04: tools/es_dub/en_segs.json phrases matched to faster-whisper words.json of the final EN video
# Translations: tools/dub/<lang>_b5.py (D[key]) and tools/dub/<lang>_old.py (D[key]); Spanish 01-04 in tools/es_dub/es_segs.py (ES[key]).
import sys, os, json, re, io, wave, difflib, subprocess
import numpy as np
from piper import PiperVoice, SynthesisConfig
ROOT = '/home/claude/fitnessanimator'
lang, key, out, total = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
wj = sys.argv[5] if len(sys.argv) > 5 else None
VOICE = dict(es='es_ES-davefx-medium', fr='fr_FR-tom-medium', ar='ar_JO-kareem-medium')[lang]
TR = {}
for f in (f'{ROOT}/tools/dub/{lang}_b5.py', f'{ROOT}/tools/dub/{lang}_old.py'):
    if os.path.exists(f):
        g = {}; exec(open(f).read(), g); TR.update(g['D'])
if lang == 'es':
    g = {}; exec(open(f'{ROOT}/tools/es_dub/es_segs.py').read(), g); TR.update(g['ES'])
LINES = TR[key]
if os.path.exists(f'{ROOT}/videos/{key}/vo/segs.json') and not wj:
    seg = [tuple(s) for s in json.load(open(f'{ROOT}/videos/{key}/vo/segs.json'))]
else:
    from num2words import num2words
    EN = json.load(open(f'{ROOT}/tools/es_dub/en_segs.json'))[key]
    WH = json.load(open(wj))
    def toks(word):
        o = []
        for p in re.split(r"[-\s]+", word.lower()):
            p = re.sub(r"[^a-z0-9']", '', p)
            if not p: continue
            if p.isdigit(): o += re.sub(r"[^a-z ]", ' ', num2words(int(p))).split()
            else: o.append(p.replace("'", ''))
        return o
    ST = [(t, i) for i, s in enumerate(EN) for w in s.split() for t in toks(w)]
    WT = [(t, a, b) for w, a, b in WH for t in toks(w)]
    sm = difflib.SequenceMatcher(None, [t for t, _ in ST], [t for t, _, _ in WT], autojunk=False); m = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): m[blk.a + k] = blk.b + k
    idx = sorted(m)
    st = np.interp(range(len(ST)), idx, [WT[m[i]][1] for i in idx]); en = np.interp(range(len(ST)), idx, [WT[m[i]][2] for i in idx])
    seg = []
    for i in range(len(EN)):
        ks = [k for k, (_, g_) in enumerate(ST) if g_ == i]
        seg.append((float(st[ks[0]]), float(en[ks[-1]])))
assert len(seg) == len(LINES), (len(seg), len(LINES))
MAXT = 1.5 if lang == 'ar' else 1.35
V = PiperVoice.load(f'/home/claude/tts/{VOICE}.onnx'); SR = V.config.sample_rate
def prep(t):
    if lang == 'fr':
        from num2words import num2words
        t = re.sub(r'\d+', lambda m_: num2words(int(m_.group()), lang='fr'), t)
    return t
def synth(text, L):
    bio = io.BytesIO()
    with wave.open(bio, 'wb') as w: V.synthesize_wav(prep(text), w, syn_config=SynthesisConfig(length_scale=L))
    bio.seek(0); w = wave.open(bio); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    nz = np.nonzero(np.abs(x) > 0.01)[0]
    return x[max(0, nz[0] - 200): nz[-1] + 400] if len(nz) else x
def atempo(x, f):
    p = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-filter:a', f'atempo={f:.4f}', '-f', 'f32le', '-'], input=x.tobytes(), capture_output=True)
    return np.frombuffer(p.stdout, np.float32)
buf = np.zeros(int(total * SR) + SR, np.float32); log = []; cur = 0.0
for i, (s0, s1) in enumerate(seg):
    nxt = seg[i + 1][0] if i + 1 < len(seg) else total - 0.3
    tgt = s1 - s0; room = max(tgt, nxt - s0 - 0.12)
    L = 1.0; x = synth(LINES[i], L); d = len(x) / SR
    if d > room: L = max(0.72, room / d * 0.98); x = synth(LINES[i], L); d = len(x) / SR
    elif d < tgt * 0.8: L = min(1.12, tgt / d); x = synth(LINES[i], L); d = len(x) / SR
    if d > room: x = atempo(x, min(MAXT, d / room)); d = len(x) / SR
    t0 = max(s0, cur + 0.08); cur = t0 + d
    p = int(t0 * SR); x = x[:max(0, len(buf) - p)]; buf[p:p + len(x)] += x
    log.append((i, round(s0, 2), round(tgt, 2), round(room, 2), round(d, 2), round(L, 2)))
buf = buf[:int(round(total * SR))]
buf = buf / max(1e-6, np.abs(buf).max()) * 0.9
with wave.open(out, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype(np.int16).tobytes())
over = [r for r in log if r[4] > r[3] + 0.02]; print('end', round(cur, 2), 'total', total)
print(lang, key, 'phrases', len(log), 'over', len(over), 'minL', min(r[5] for r in log), 'dur', round(len(buf) / SR, 2))
