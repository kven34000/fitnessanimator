import asyncio,time,sys
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--allow-file-access-from-files'])
    pg=await b.new_page(viewport={'width':1920,'height':1080})
    pg.on('console',lambda m:print('C:',m.text))
    await pg.goto('file:///home/claude/w3d/test.html'); await pg.wait_for_function('window.ready===true',timeout=20000)
    print(await pg.evaluate("(()=>{const gl=document.getElementById('c').getContext('webgl2');return gl?gl.getParameter(gl.VERSION):'none'})()"))
    t=time.time()
    for i in range(20):
      await pg.evaluate(f'window.frame({i/30})')
      await pg.locator('#c').screenshot(path=f'/tmp/f{i}.png') if i==19 else None
    print('20 frames',time.time()-t)
    await b.close()
asyncio.run(main())
