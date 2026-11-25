import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--allow-file-access-from-files'])
    pg=await b.new_page(); await pg.goto('file:///home/claude/w3d/dump.html')
    await pg.wait_for_function('window.dump',timeout=60000); print(await pg.evaluate('window.dump')); await b.close()
asyncio.run(main())
