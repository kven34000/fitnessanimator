# Spanish voice track (free, Piper es_ES-davefx) timed phrase-by-phrase to the English voice.
# python3 make_es.py <key> <words.json> <total_dur> <out.wav>
import sys, json, re, io, wave, difflib, subprocess
import numpy as np
from piper import PiperVoice, SynthesisConfig
exec(open('/home/claude/tts/es_segs.py').read())
key, wj, total, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
EN = json.load(open('/home/claude/tts/en_segs.json'))[key]; ESL = ES[key]
WH = json.load(open(wj))
from num2words import num2words
def toks(word):
    out = []
    for p in re.split(r"[-\s]+", word.lower()):
        p = re.sub(r"[^a-z0-9']", '', p)
        if not p: continue
        if p.isdigit():
            out += re.sub(r"[^a-z ]", ' ', num2words(int(p))).split()
        else: out.append(p.replace("'", ''))
    return out
ST = []  # (token, seg)
for i, s_ in enumerate(EN):
    for w_ in s_.split():
        for t_ in toks(w_): ST.append((t_, i))
WT = []  # (token, start, end)
for w_, s0_, s1_ in WH:
    for t_ in toks(w_): WT.append((t_, s0_, s1_))
sm = difflib.SequenceMatcher(None, [t for t, _ in ST], [t for t, _, _ in WT], autojunk=False); m = {}
for blk in sm.get_matching_blocks():
    for k in range(blk.size): m[blk.a + k] = blk.b + k
idx = sorted(m)
st = np.interp(range(len(ST)), idx, [WT[m[i]][1] for i in idx]); en = np.interp(range(len(ST)), idx, [WT[m[i]][2] for i in idx])
print('matched', len(m), 'of', len(ST))
seg = []
for i in range(len(EN)):
    ks = [k for k, (_, sg) in enumerate(ST) if sg == i]
    seg.append((float(st[ks[0]]), float(en[ks[-1]])))
V = PiperVoice.load('/home/claude/tts/es_ES-davefx-medium.onnx'); SR = V.config.sample_rate
def synth(text, L):
    bio = io.BytesIO()
    with wave.open(bio, 'wb') as w: V.synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=L))
    bio.seek(0); w = wave.open(bio); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    nz = np.nonzero(np.abs(x) > 0.01)[0]
    return x[max(0, nz[0] - 200): nz[-1] + 400] if len(nz) else x
def atempo(x, f):
    p = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-filter:a', f'atempo={f:.4f}', '-f', 'f32le', '-'], input=x.tobytes(), capture_output=True)
    return np.frombuffer(p.stdout, np.float32)
buf = np.zeros(int(total * SR) + SR, np.float32); log = []
for i, (s0, s1) in enumerate(seg):
    nxt = seg[i + 1][0] if i + 1 < len(seg) else total - 0.3
    tgt = s1 - s0; room = max(tgt, nxt - s0 - 0.12)
    L = 1.0; x = synth(ESL[i], L); d = len(x) / SR
    if d > room: L = max(0.72, room / d * 0.98); x = synth(ESL[i], L); d = len(x) / SR
    elif d < tgt * 0.8: L = min(1.12, tgt / d); x = synth(ESL[i], L); d = len(x) / SR
    if d > room: x = atempo(x, min(1.35, d / room)); d = len(x) / SR
    p = int(s0 * SR); x = x[:max(0, len(buf) - p)]; buf[p:p + len(x)] += x
    log.append((i, round(s0, 2), round(tgt, 2), round(room, 2), round(d, 2), round(L, 2)))
buf = buf[:int(round(total * SR))]
buf = buf / max(1e-6, np.abs(buf).max()) * 0.9
with wave.open(out, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype(np.int16).tobytes())
over = [r for r in log if r[4] > r[3] + 0.02]
print(key, 'segments', len(log), 'over', len(over), 'minL', min(r[5] for r in log), 'dur', len(buf) / SR)
json.dump(log, open(out + '.log.json', 'w'))
