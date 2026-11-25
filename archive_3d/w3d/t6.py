import asyncio, math
from drv import Eng
import poses as P
async def main():
  e=await Eng().start()
  top={'pos':[0,4.5,0.01],'target':[0,0.8,0],'fov':30}
  for n,pa in [('f0',{}),('f05',{'fwd':0.5}),('f1',{'fwd':1.0})]:
    b={}; P.arms(b,pa,{})
    b2={}; P.arms(b2,{},pa)
    await e.shot({'t':0,'pose':{'bones':b},'cam':top},f'd_A_{n}.jpg',70)
    await e.shot({'t':0,'pose':{'bones':b2},'cam':top},f'd_B_{n}.jpg',70)
  print(await e.ev("()=>[window.boneWorld('bone_26'),window.boneWorld('bone_27'),window.boneWorld('tripo0_Right_Limb_3'),window.boneWorld('tripo0_Right_Limb_4')]"))
  await e.stop()
asyncio.run(main())
