R.PUNCH[:] = PUNCH

# ---- sync on-screen text to the spoken word (same rule as the QA check) ----
import re as _re
def _norm(s): return _re.sub(r'[^a-z0-9%]', '', s.lower())
_STOP = set('the and you your with for not are this that its it is of to a in on at be up all'.split())
def sync_text(words):
    for e in R.EL:
        if e['k'] not in ('chip', 'title', 'big') or not e.get('text'): continue
        toks = [_norm(x) for x in _re.split(r'[\s/+•→=≠×?]+', e['text'])]
        toks = [x for x in toks if (len(x) >= 3 and x not in _STOP) or x.isdigit()]
        best = None
        for (w_, a, b) in words:
            nw = _norm(w_)
            if nw and any(nw == k or (len(k) >= 4 and (nw.startswith(k[:5]) or k.startswith(nw[:5]))) for k in toks):
                if abs(a - e['t0']) < 8 and (best is None or abs(a - e['t0']) < abs(best - e['t0'])): best = a
        if best is None: continue
        if e['t0'] - best > 1.2 or e['t0'] - best < -1.0:
            nt = best - 0.15
            if nt < e['t1'] - 0.4: e['t0'] = nt
            elif e['k'] == 'chip': e['t0'] = nt; e['t1'] = nt + 1.0
