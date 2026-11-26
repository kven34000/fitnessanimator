import sys, json
from faster_whisper import WhisperModel
m = WhisperModel('base.en', device='cpu', compute_type='int8')
import subprocess, numpy as np
a = np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',sys.argv[1],'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True).stdout, np.int16).astype(np.float32)/32768
segs, _ = m.transcribe(a, word_timestamps=True, language='en')
W = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in segs for w in s.words]
json.dump(W, open(sys.argv[2], 'w')); print(len(W), W[-1])
