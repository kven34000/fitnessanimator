import sys
from fontTools.ttLib import TTFont
sys.path.insert(0,'/home/claude/v2_6ex'); sys.path.insert(0,'/home/claude/en')
which=sys.argv[1]
if which=='six':
    import render_6ex as X
else:
    import render_en as X
R=X.R
fonts={k:set(TTFont(p).getBestCmap().keys()) for k,p in (('russo',R.F_RUSSO),('m900',R.F_M900))}
bad=set()
for e in R.EL:
    t=e.get('text') or ''
    for l in e.get('lines',[]) or []: t+=l
    f=fonts['m900'] if e['k']=='chip' else fonts['russo']
    for ch in t:
        if ord(ch)>32 and ord(ch) not in f: bad.add((ch, hex(ord(ch)), e.get('text') or e.get('lines')[0], round(e['t0'],1), e['k']))
for b in sorted(bad, key=lambda x:x[3]): print('MISSING GLYPH', b)
