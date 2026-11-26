# list hard cuts (big frame-to-frame jumps) in a rendered mp4: python3 cuts.py video.mp4
import subprocess, sys, numpy as np
W, H = 96, 54
p = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[1], '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
f = np.frombuffer(p, np.uint8).reshape(-1, H, W).astype(np.float32)
d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
for i in np.nonzero(d > 18)[0]: print(f'{(i + 1) / 30:.2f}s  diff {d[i]:.0f}')
print(len(f), 'frames')
