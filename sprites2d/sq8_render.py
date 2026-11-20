import sys, math, subprocess
import numpy as np
from PIL import Image, ImageFilter, ImageChops, ImageDraw
sys.path.insert(0,'/home/claude/work'); import render as R2
WD,HT=1920,1080
ORDER=[0,1,2,4,3,5,6,7]
S=820/878.0
def sprite(i):
  im=Image.open(f'sq8_{i}.png').convert('RGBA'); im=im.resize((int(im.width*S),int(im.height*S)),Image.LANCZOS)
  a=np.array(im.split()[3]); h=a.shape[0]; ys,xs=np.nonzero(a[int(h*0.94):]>128); fx=xs.mean()
  pad=60; big=Image.new('RGBA',(im.width+2*pad,im.height+2*pad),(0,0,0,0))
  al=Image.new('L',big.size,0); al.paste(im.split()[3],(pad,pad))
  g1=al.filter(ImageFilter.GaussianBlur(18)); g2=al.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(4))
  glow=Image.new('RGBA',big.size,R2.RED+(0,)); glow.putalpha(ImageChops.add(g1.point(lambda v:int(v*0.9)),g2.point(lambda v:int(v*0.85))))
  big=Image.alpha_composite(big,glow); big.alpha_composite(im,(pad,pad))
  return big,fx+pad,im.height+pad
SP=[sprite(i) for i in ORDER]
# frame schedule (30 fps, on twos)
seq=[]
for i in range(8): seq+=[i,i]
seq+=[7]*5
for i in range(7,-1,-1): seq+=[i,i]
seq+=[0]*6
BG=R2.make_bg(); GL=R2.make_glow()
out=sys.argv[1]; N=int(float(sys.argv[2])*30)
ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','30','-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
for f in range(N):
  t=f/30; fr=BG.copy(); fr.alpha_composite(GL)
  k=seq[f%len(seq)]; spr,fx,fy=SP[k]
  cx,cy=930,1010
  sh=Image.new('RGBA',(302,42),(0,0,0,0)); ImageDraw.Draw(sh).ellipse([0,0,301,41],fill=(255,20,50,90)); sh=sh.filter(ImageFilter.GaussianBlur(8))
  fr.alpha_composite(sh,(int(cx-151),int(cy-21)))
  fr.alpha_composite(spr,(int(cx-fx),int(cy-fy)))
  reps=f//len(seq)+(1 if (f%len(seq))>=16 else 0)
  ImageDraw.Draw(fr).text((1700,60),f'{reps}/50',fill=(255,255,255),font=R2.font(R2.F_RUSSO,60))
  ff.stdin.write(fr.convert('RGB').tobytes())
ff.stdin.close(); ff.wait()
