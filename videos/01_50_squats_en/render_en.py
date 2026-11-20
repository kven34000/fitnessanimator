import sys, math, subprocess
sys.path.insert(0,'/home/claude/work'); sys.path.insert(0,'/home/claude/en')
import render_v2 as R
from timewarp import to_ru, to_en, EN_DUR
from words_en import W as EW
from PIL import Image
TR={'1 МЕСЯЦ':'1 MONTH','50 ПРИСЕДАНИЙ':'50 SQUATS','50 — МНОГО?':'50 TOO MANY?','= РАЗМИНКА':'= WARM-UP','БАЛАНС':'BALANCE','БОДИБИЛДЕР':'BODYBUILDER',
'БОЛЬШИЕ ПЕРЕМЕНЫ':'BIG CHANGES','ВЫНОСЛИВОСТЬ':'ENDURANCE','ГАНТЕЛИ':'DUMBBELLS','ГДЕ УГОДНО':'ANYWHERE','ГИБКОСТЬ':'FLEXIBILITY','ГОЛЕНОСТОП':'ANKLES',
'ГОРЯТ НОГИ':'LEGS ON FIRE','ДЕЛИ: 5 × 10':'SPLIT: 5 × 10','ДОСМОТРИ ДО КОНЦА':'WATCH TILL THE END','ЗАЛ':'GYM','КАЖДЫЙ ДЕНЬ':'EVERY DAY','КОГДА УГОДНО':'ANYTIME',
'КОЛЕНИ':'KNEES','КОНТРОЛЬ НАД ЖИЗНЬЮ':'CONTROL YOUR LIFE','КООРДИНАЦИЯ':'COORDINATION','ЯГОДИЦЫ':'GLUTES','КОРПУС':'CORE','КРОВООБРАЩЕНИЕ':'CIRCULATION','ЛЕСТНИЦА ЛЕГЧЕ':'STAIRS: EASIER',
'МАЛЕНЬКИЕ ШАГИ':'SMALL STEPS','МЫШЦЫ РАСТУТ':'MUSCLES GROW','НЕ СТОИТ':'NOT WORTH IT','НЕДЕЛЯ 1':'WEEK 1','НЕДЕЛЯ 2':'WEEK 2','НЕДЕЛЯ 3':'WEEK 3',
'НОГИ СИЛЬНЕЕ':'STRONGER LEGS','НОГИ':'LEGS','ОСАНКА РОВНЕЕ':'BETTER POSTURE','ПОДВИЖНОСТЬ':'MOBILITY','ПОЯСНИЦА':'LOWER BACK','РЕЗИНА':'BANDS',
'С СОБСТВЕННЫМ ВЕСОМ':'BODYWEIGHT ONLY','СКОЛЬКО ПРИСЕДАЕШЬ ТЫ?':'HOW MANY DO YOU DO?','СТАБИЛЬНЕЕ':'STEADIER','СТОИТ':'WORTH IT','ТОЛЬКО ТЫ + ТЕЛО':'JUST YOU + BODY',
'ТОП':'TOP','УВЕРЕННЕЕ':'MORE CONFIDENT','УВЕРЕННОСТЬ':'CONFIDENCE','ХОЧЕШЬ МАССУ?':'WANT SIZE?','ЧЕСТНО:':'HONESTLY:','ШТАНГА':'BARBELL','ЭТО НОРМАЛЬНО':"THAT'S NORMAL"}
for e in R.EL:
    if 'text' in e and e['text'] in TR: e['text']=TR[e['text']]
    elif 'text' in e and any('А'<=c<='я' for c in e['text']): raise SystemExit('untranslated '+e['text'])
R.SUB_LABELS=('SUBSCRIBE','LIKE'); R.DAY_LABEL='DAY'
# English subtitle pages (max ~5 words, break at punctuation)
pages=[]; cur=[]
for w,a,b in EW:
    cur.append((w,a,b))
    end=w[-1] in '.?!,:' or w.endswith('...')
    if (end and len(cur)>=2) or len(cur)>=5 or (w[-1] in '.?!' ):
        pages.append(cur); cur=[]
if cur: pages.append(cur)
SUBS=[]
for i,p in enumerate(pages):
    s0=p[0][1]-0.05; s1=(pages[i+1][0][1]-0.05) if i+1<len(pages) else p[-1][2]+0.6
    s1=min(s1,p[-1][2]+0.9)
    SUBS.append((to_ru(s0),to_ru(s1),[(w,to_ru(a),to_ru(b)) for w,a,b in p]))
R.SUBS[:]=SUBS
def render_en(fi):
    T=fi/R.FPS
    return R.render(to_ru(T)*R.FPS)
if __name__=='__main__':
    from multiprocessing import Pool
    mode=sys.argv[1]
    if mode=='still':
        R.init()
        for ts in sys.argv[2:]:
            b=render_en(int(float(ts)*R.FPS)); Image.frombytes('RGB',(R.WD,R.HT),b).save(f'/home/claude/en/still_{ts}.png')
        sys.exit()
    n=int(EN_DUR*R.FPS); out=sys.argv[2]
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{R.WD}x{R.HT}','-r',str(R.FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    with Pool(2,initializer=R.init) as p:
        for i,b in enumerate(p.imap(render_en,range(n),chunksize=8)): ff.stdin.write(b)
    ff.stdin.close(); ff.wait()
