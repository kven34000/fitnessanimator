import asyncio
from drv import Eng
from PIL import Image, ImageDraw
async def main():
  e=Eng('tex_clean.jpg','engine2.html'); await e.start()
  for n in ['Idle','Flex','Point']: await e.ev(f"()=>window.loadClip('{n}','hero_{n}.glb')")
  ims=[]
  cam={'pos':[0,1.25,2.5],'target':[0,1.1,0],'fov':30}
  shots=[('A new default',{}, 'Idle',1.0,{},0.3),
         ('B back glutes',{}, 'AirSquat',0.9,{'glutes':1,'hams':0.8,'lowback':0.8},0.3),
         ('C glow abs/pecs',{}, 'Flex',2.0,{'abs':1,'pecs':1,'biceps':1},0.12),
         ('D quads',{}, 'AirSquat',0.9,{'quads':1,'glutes':1},0.12),
         ('E curl0',{}, 'Point',0.8,{},0.0),
         ('F curl.5',{}, 'Point',0.8,{},0.5)]
  for nm,L,clip,t,mus,curl in shots:
    c=cam if clip!='AirSquat' else {'pos':[0,0.85,2.6],'target':[0,0.65,0],'fov':30}
    st={'t':0.4,'cam':c,'outline':0.0014,'charRotY':(2.9 if nm.startswith('B') else (0.25 if clip!='AirSquat' else 0.7)),'clips':[{'name':clip,'time':t}],'muscles':mus,'light':L,'fingerCurl':curl}
    await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='/tmp/a.jpg',type='jpeg',quality=85)
    im=Image.open('/tmp/a.jpg').crop((420,0,1500,1080)).resize((480,480)); ImageDraw.Draw(im).text((4,4),nm,fill='yellow'); ims.append(im)
  o=Image.new('RGB',(480*3,480*2))
  for i,im in enumerate(ims): o.paste(im,((i%3)*480,(i//3)*480))
  o.save('look2.png'); await e.stop()
asyncio.run(main())
