# Put a recorded voice (whole script in one file) under <video_dir>/vo: vo.wav, words.json (faster-whisper),
# segs.json (start/end of every script phrase, found by matching script words to whisper words), dur.txt.
# python3 apply_vo.py <video_dir> <voice.mp3|wav>      (the previous vo/ is kept as vo_prev/)
import sys, os, json, re, shutil, subprocess, difflib
VD, SRC = sys.argv[1], sys.argv[2]
sys.path.insert(0, VD)
from script_en import SEG
if os.path.exists(f'{VD}/vo') and not os.path.exists(f'{VD}/vo_prev'): shutil.copytree(f'{VD}/vo', f'{VD}/vo_prev')
os.makedirs(f'{VD}/vo', exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-ac', '1', '-ar', '44100', f'{VD}/vo/vo.wav'], check=True)
subprocess.run(['python3', '/home/claude/fitnessanimator/tools/es_dub/whisper_words.py', f'{VD}/vo/vo.wav', f'{VD}/vo/words.json'], check=True)
WH = json.load(open(f'{VD}/vo/words.json'))
norm = lambda s: re.sub(r"[^a-z0-9']", '', s.lower())
ST = [(w, i) for i, (_, s) in enumerate(SEG) for w in s.split()]
sm = difflib.SequenceMatcher(None, [norm(w) for w, _ in ST], [norm(w[0]) for w in WH], autojunk=False)
m = {}
for b in sm.get_matching_blocks():
    for k in range(b.size): m[b.a + k] = b.b + k
segs = []
for i in range(len(SEG)):
    ks = [k for k, (_, g) in enumerate(ST) if g == i and k in m]
    if ks: segs.append([WH[m[ks[0]]][1], WH[m[ks[-1]]][2]])
    else: segs.append(None)
# fill phrases with no matched words by interpolation between neighbours
for i, s in enumerate(segs):
    if s is None:
        a = segs[i - 1][1] if i and segs[i - 1] else 0.0
        b = next((x[0] for x in segs[i + 1:] if x), a + 1.0)
        segs[i] = [a + 0.1, max(a + 0.2, b - 0.1)]
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{VD}/vo/vo.wav'], capture_output=True, text=True).stdout)
json.dump([[round(a, 3), round(b, 3)] for a, b in segs], open(f'{VD}/vo/segs.json', 'w'))
open(f'{VD}/vo/dur.txt', 'w').write(f'{dur:.3f}')
print(VD, 'phrases', len(segs), 'matched words', len(m), '/', len(ST), 'dur', round(dur, 1))
