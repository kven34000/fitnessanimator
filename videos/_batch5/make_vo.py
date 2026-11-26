# Free draft English voice (Piper en_US-ryan-high), phrase by phrase, for review before the paid Magnific voice.
# python3 make_vo.py <video_dir>  ->  <video_dir>/vo/vo.wav, segs.json (start/end of every phrase), dur.txt
import sys, os, io, json, wave, re
import numpy as np
from piper import PiperVoice, SynthesisConfig
from num2words import num2words
VD = sys.argv[1]; sys.path.insert(0, VD)
from script_en import SEG
V = PiperVoice.load('/home/claude/tts/en_US-ryan-high.onnx'); SR = V.config.sample_rate
GAP, LEAD = 0.38, 0.35
def clean(s):
    s = re.sub(r'(\d+)', lambda m: num2words(int(m.group(1))), s)
    return s.replace('Wi-Fi', 'Wi Fi').replace('TikTok', 'Tik Tok').replace('MRI', 'M R I').replace('L-sit', 'L sit')
def synth(text):
    bio = io.BytesIO()
    with wave.open(bio, 'wb') as w: V.synthesize_wav(clean(text), w, syn_config=SynthesisConfig(length_scale=0.9))
    bio.seek(0); w = wave.open(bio); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    nz = np.nonzero(np.abs(x) > 0.01)[0]
    return x[max(0, nz[0] - 200): nz[-1] + 600] if len(nz) else x
parts, segs, t = [np.zeros(int(LEAD * SR), np.float32)], [], LEAD
for _, s in SEG:
    x = synth(s); segs.append((round(t, 3), round(t + len(x) / SR, 3)))
    parts += [x, np.zeros(int(GAP * SR), np.float32)]; t += len(x) / SR + GAP
buf = np.concatenate(parts); buf = buf / np.abs(buf).max() * 0.9
os.makedirs(f'{VD}/vo', exist_ok=True)
with wave.open(f'{VD}/vo/vo.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype(np.int16).tobytes())
json.dump(segs, open(f'{VD}/vo/segs.json', 'w'))
open(f'{VD}/vo/dur.txt', 'w').write(f'{len(buf) / SR:.3f}')
print(VD, len(SEG), 'phrases', round(len(buf) / SR, 1), 's')
