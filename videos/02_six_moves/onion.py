import sys; sys.path.insert(0,'/home/claude/v2_6ex')
import render_6ex as X
from PIL import Image, ImageDraw
R=X.R; R.init()
names=sys.argv[1:]
out=Image.new('RGB',(480*4,270*2*len(names)),(20,20,20))
for j,nm in enumerate(names):
    frs=R.ANIM[nm]
    for k,f in enumerate(frs):
        fr=Image.new('RGBA',(1920,1080),(20,20,20,255))
        ImageDraw.Draw(fr).line([(0,968),(1920,968)],fill=(255,0,0),width=3)
        ImageDraw.Draw(fr).line([(960,0),(960,1080)],fill=(255,0,0),width=3)
        fr.alpha_composite(f[0],(int(960-f[1]),int(968-f[2])))
        out.paste(fr.convert('RGB').resize((480,270)),((k%4)*480,(j*2+k//4)*270))
out.save('/tmp/onion.png')
