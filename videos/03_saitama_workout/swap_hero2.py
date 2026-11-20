# Replace old hero (hook + final) in draft2 with new caped suit from hero2/ sprites
import numpy as np, json, subprocess, math, sys
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
W,H,FPS=1920,1080,30
SRC='Saitama_workout_EN_draft2_novoice.mp4'; OUT=sys.argv[1] if len(sys.argv)>1 else 'Saitama_workout_EN_draft3_novoice.mp4'
ONLY=sys.argv[2] if len(sys.argv)>2 else None   # 'hook'/'final' preview
info=json.load(open('hero2/info.json'))
SPR=[Image.open(f'hero2/p{i}.png') for i in range(8)]
REF_H=861  # pose 0 bbox height
SEGS=[dict(name='hook',plate='hook_plate_0m07-0m16.mp4',t0=7.2,n=255,cx=937,feet=978,h=723,steady=110000,box=(700,110,1150,996),
           sched=[(7.2,5),(8.4,0),(9.8,1),(10.4,3),(12.0,0),(13.4,7),(13.8,2)]),
      dict(name='final',plate='final_plate_2m54-2m58.mp4',t0=173.85,n=113,cx=940,feet=980,h=830,steady=125000,box=(700,100,1180,996),
           sched=[(173.85,4)])]
def glowify(im):
    a=im.split()[3]
    wide=a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(9))
    rim=a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2.5))
    g=np.maximum(np.asarray(wide,np.float32)*0.85,np.asarray(rim,np.float32)*1.0)
    out=Image.new('RGBA',im.size,(255,35,60,0)); out.putalpha(Image.fromarray(g.clip(0,255).astype(np.uint8)))
    out.alpha_composite(im); return out
PAD=30
def prep(seg):
    sc=seg['h']/REF_H; cache={}
    for i in set(p for _,p in seg['sched']):
        im=SPR[i]; sz=(round(im.width*sc),round(im.height*sc)); r=im.resize(sz,Image.LANCZOS)
        c=Image.new('RGBA',(sz[0]+2*PAD,sz[1]+2*PAD)); c.paste(r,(PAD,PAD)); c=glowify(c)
        cache[i]=(c, info[i]['ax']*sc+PAD, info[i]['ay']*sc+PAD)
    return cache
def frames(path,ss,n):
    a=['ffmpeg','-v','error']+(['-ss',str(ss)] if ss else [])+['-i',path]+(['-frames:v',str(n)] if n else [])+['-f','rawvideo','-pix_fmt','rgb24','-']
    p=subprocess.Popen(a,stdout=subprocess.PIPE)
    while True:
        b=p.stdout.read(W*H*3)
        if len(b)<W*H*3: return
        yield np.frombuffer(b,np.uint8).reshape(H,W,3)
def pose_at(seg,t):
    cur=seg['sched'][0]
    for s in seg['sched']:
        if t>=s[0]-1e-6: cur=s
    return cur
def do_frame(fr,pl,seg,cache,k):
    t=seg['t0']+k/FPS
    d=np.abs(fr.astype(int)-pl.astype(int)).max(2)>30
    x0,y0,x1,y1=seg['box']; m=np.zeros_like(d); m[y0:y1,x0:x1]=d[y0:y1,x0:x1]
    n=int(m.sum())
    if d.mean()>0.5 or n<300: return fr     # scene mismatch / no hero
    op=min(1.0,n/seg['steady'])
    m=ndi.binary_dilation(m,iterations=6)
    m=np.asarray(Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)),np.float32)[...,None]/255
    base=(fr*(1-m)+pl*m).astype(np.uint8)
    ts,pi=pose_at(seg,t); spr,ax,ay=cache[pi]
    dt=t-ts; pop=1+0.05*max(0,1-dt/0.12) if dt<0.12 and ts>seg['t0']+0.01 else 1.0
    br=0.008*math.sin(2*math.pi*(t-seg['t0'])/2.4)
    sx,sy=pop*(1-br*0.5),pop*(1+br)
    if abs(sx-1)>1e-3 or abs(sy-1)>1e-3:
        spr=spr.resize((round(spr.width*sx),round(spr.height*sy)),Image.BILINEAR); ax*=sx; ay*=sy
    if op<1: a=spr.split()[3].point(lambda v:int(v*op)); spr=spr.copy(); spr.putalpha(a)
    img=Image.fromarray(base).convert('RGBA')
    img.alpha_composite(spr,(round(seg['cx']-ax),round(seg['feet']-ay)))
    return np.asarray(img.convert('RGB'))
segs=[s for s in SEGS if ONLY in (None,s['name'])]
if ONLY:
    s=segs[0]; cache=prep(s)
    w=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-c:v','libx264','-crf','16','-preset','veryfast','-pix_fmt','yuv420p',OUT],stdin=subprocess.PIPE)
    for k,(fr,pl) in enumerate(zip(frames(SRC,s['t0'],s['n']),frames(s['plate'],0,s['n']))):
        w.stdin.write(do_frame(fr,pl,s,cache,k).tobytes())
    w.stdin.close(); w.wait(); sys.exit()
# full render: walk whole draft, swap in ranges
caches={s['name']:prep(s) for s in SEGS}
starts={round(s['t0']*FPS):s for s in SEGS}
w=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','30','-i','-','-i',SRC,'-map','0:v','-map','1:a','-c:v','libx264','-crf','17','-preset','veryfast','-pix_fmt','yuv420p','-c:a','copy','-shortest',OUT],stdin=subprocess.PIPE)
active=None
for f,fr in enumerate(frames(SRC,None,None)):
    if f in starts: active=starts[f]; pg=frames(active['plate'],0,active['n']); k0=f
    if active is not None:
        k=f-k0
        if k<active['n']:
            pl=next(pg,None)
            if pl is not None: fr=do_frame(fr,pl,active,caches[active['name']],k)
        else: active=None
    w.stdin.write(fr.tobytes())
w.stdin.close(); w.wait()
