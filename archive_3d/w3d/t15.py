import asyncio
from drv import Eng
import poses as P
async def main():
  e=await Eng('tex_clean.jpg').start()
  cam={'pos':[0.75,1.45,0.9],'target':[0.72,1.37,0],'fov':30}
  for k,ax in [(0,None),(0.6,None),(1.0,None),(0.6,[1,0,0]),(0.6,[0,0,1])]:
    await e.shot({'t':0,'pose':P.hands(k,axis=ax),'cam':cam},f'hand_{k}_{ax}.jpg',70)
  await e.stop()
asyncio.run(main())
