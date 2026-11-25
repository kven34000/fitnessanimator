import asyncio, json, sys
from playwright.async_api import async_playwright

ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--allow-file-access-from-files', '--ignore-gpu-blocklist']

class Eng:
    def __init__(self, tex=None, page='engine.html', pre=None): self.tex = tex; self.page = page; self.pre = pre
    async def start(self):
        self.p = await async_playwright().start()
        self.b = await self.p.chromium.launch(executable_path='/usr/bin/google-chrome', args=ARGS)
        self.pg = await self.b.new_page(viewport={'width': 1920, 'height': 1080})
        self.pg.on('console', lambda m: print('C:', m.text) if 'GPU stall' not in m.text else None)
        self.pg.on('pageerror', lambda e: print('PAGEERR', e))
        await self.pg.goto('file:///home/claude/w3d/' + self.page)
        await self.pg.wait_for_function('window.ready===true', timeout=30000)
        if self.pre: await self.pg.evaluate(self.pre)
        self.bones = await self.pg.evaluate('(t)=>window.load(t)', getattr(self,'tex',None))
        return self
    async def shot(self, st, path, q=92):
        await self.pg.evaluate('(s)=>window.frame(s)', st)
        await self.pg.screenshot(path=path, type='jpeg', quality=q)
    async def ev(self, js, arg=None):
        return await self.pg.evaluate(js, arg)
    async def stop(self):
        await self.b.close(); await self.p.stop()
