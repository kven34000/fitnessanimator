import asyncio, json
from drv import Eng
async def main():
  e=await Eng().start()
  await e.ev("()=>window.loadBVH('87_02','bvh/87_02.bvh')")
  r=await e.ev("()=>window.restDbg()")
  for k in ['tripoRoot','tripo0_Left_Limb_0','tripo0_Left_Limb_2','tripo0_Right_Limb_1','tripoHead_0','bone_26']: print('rest',k,r[k])
  print('src',await e.ev("()=>window.srcDbg('87_02',0.5)"))
  await e.pg.evaluate('(s)=>window.frame(s)',{'t':0,'anim':{'name':'87_02','time':0.5,'t0':0.5},'charScale':1,'cam':{'pos':[0,1.0,4.5],'target':[0,0.6,0],'fov':30}})
  print("after",await e.ev("()=>window.dbg()"));print(await e.ev("()=>window.dbg2()"))
  await e.pg.screenshot(path='tpose.jpg',type='jpeg',quality=70)
  await e.stop()
asyncio.run(main())
