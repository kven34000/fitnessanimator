import asyncio, math
from drv import Eng
import render3d as RD
async def main():
  e=await Eng().start()
  for t in (35.0, 35.6, 36.4):
    st,ov=RD.state(t)
    st2=dict(st); st2['cam']={'pos':[st['charPos'][0],st['charPos'][1]+0.9,4.5],'target':[st['charPos'][0],st['charPos'][1]+0.8,0],'fov':30}
    await e.pg.evaluate('(s)=>window.frame(s)',st2); await e.pg.screenshot(path=f'stair_{t}.jpg',type='jpeg',quality=70)
  st,ov=RD.state(85.0); await e.pg.evaluate('(s)=>window.frame(s)',st); await e.pg.screenshot(path='pt85.jpg',type='jpeg',quality=70)
  await e.stop()
asyncio.run(main())
