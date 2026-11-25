import asyncio, json
from drv import Eng
async def main():
  e=Eng('tex_clean.jpg','engine2.html'); await e.start()
  await e.pg.evaluate('(s)=>window.frame(s)',{'t':0,'clips':[]})
  print(json.dumps(await e.ev("()=>window.dbgB()"),indent=0))
  await e.stop()
asyncio.run(main())
