import asyncio
from drv import Eng
ALL={m:1 for m in ['quads','glutes','abs','pecs','biceps','calves']}
async def main():
  e=await Eng().start()
  await e.shot({'t':0},'v_front.jpg')
  await e.shot({'t':0,'charRotY':1.5708},'v_side.jpg')
  await e.shot({'t':0,'charRotY':3.1416,'muscles':{'glutes':1,'hams':1,'calves':1,'lowback':1,'lats':1,'traps':1,'triceps':1}},'v_back.jpg')
  await e.shot({'t':0,'muscles':{'quads':1,'abs':1,'pecs':1,'biceps':1,'delts':1,'obliques':1,'knees':0,'forearms':1}},'v_musc.jpg')
  await e.stop()
asyncio.run(main())
