import json,collections,datetime,sys
m4=json.load(open('m4-v3.json')); m5=json.load(open('m5-v3.json')); M=1e6
ser=collections.defaultdict(list)
for src in (m4,m5):
    for s in src['limit_history']:
        if s['windowId'] in('seven_day','seven_day_fable'):
            ser[(s['accountKey'].split(':')[1],s['windowId'])]+= [tuple(x) for x in s['samples']]
def day(ms): return datetime.datetime.utcfromtimestamp(ms/1000).strftime('%Y-%m-%d')
gain=collections.defaultdict(lambda:collections.defaultdict(float)); resets=[]
for k,sm in ser.items():
    sm=sorted(set(sm)); cur=None; curwin=None
    for i,(at,p,rs) in enumerate(sm):
        win=round(rs/3600e3) if rs else None
        if cur is None:
            cur=p; curwin=win; continue
        if p>=cur:
            if (at-sm[i-1][0])<48*3600e3: gain[day(at)][k]+=p-cur
            cur=p; curwin=win if win else curwin; continue
        # fall: stale if it recovers within 30 min
        rec=any(q>=cur-2 for (a2,q,_) in sm[i+1:i+40] if a2-at<=30*60e3)
        if rec: continue
        newwin = win is not None and curwin is not None and abs(win-curwin)>2
        if newwin or p<cur/2:
            resets.append((k[0].split('@')[0][:6]+('@oly' if 'olympus' in k[0] else ''),k[1][10:],datetime.datetime.utcfromtimestamp(at/1000).strftime('%m-%d %H:%M'),cur,p,'window' if newwin else 'refresh'))
            if newwin: gain[day(at)][k]+=p
            cur=p; curwin=win if win else curwin
use=collections.defaultdict(lambda:collections.defaultdict(float))
for src in (m4,m5):
    for h in src['hourly_utc_account']:
        fam=h['fam']; d=h['hour'][:10]
        if fam.startswith('advisor:'): use[d]['fable_adv' if 'fable' in fam else 'other_adv']+=h['adv_wt']
        else: use[d][fam]+=h['wt']
print('UTC day    | points gained all accounts: overall, fable | weighted M: opus, fable(+adv), other | M per overall point')
rows=[]
for d in sorted(use):
    if d<'2026-11-12': continue
    g=sum(v for k,v in gain[d].items() if k[1]=='seven_day'); gf=sum(v for k,v in gain[d].items() if k[1]=='seven_day_fable')
    o=use[d]['opus']/M; f=(use[d]['fable']+use[d]['fable_adv'])/M; x=(use[d]['other']+use[d]['other_adv'])/M
    rows.append((d,g,gf,o,f,x))
    print(d,'| %5.0f %5.0f | %7.1f %7.1f %6.1f | %s'%(g,gf,o,f,x,('%.1f'%((o+f+x)/g)) if g else '-'), {k[0].split('@')[0][:6]+('F' if 'fable' in k[1] else ''):int(v) for k,v in gain[d].items() if v})
print('resets:'); [print('  ',r) for r in sorted(resets,key=lambda r:r[2])]
# least squares points = a*opus + b*fable + c*other over days with gains
import itertools
def fit(rows):
    # normal equations 2 vars (opus+other, fable)
    A=[[r[3]+r[5],r[4]] for r in rows]; y=[r[1] for r in rows]
    s11=sum(a[0]*a[0] for a in A); s12=sum(a[0]*a[1] for a in A); s22=sum(a[1]*a[1] for a in A)
    t1=sum(a[0]*b for a,b in zip(A,y)); t2=sum(a[1]*b for a,b in zip(A,y))
    det=s11*s22-s12*s12
    return ((t1*s22-t2*s12)/det,(s11*t2-s12*t1)/det)
r2=[r for r in rows if r[1]>0]
a,b=fit(r2); print('fit overall points per M weighted: opus/other %.3f  fable %.3f  -> M per point: opus %.1f fable %.1f'%(a,b,1/a if a>0 else float('nan'),1/b if b>0 else float('nan')))
tf=sum(r[4] for r in r2); gf=sum(r[2] for r in r2); print('fable bucket: %.0f fable points for %.0f M fable weighted -> %.2f M per fable point'%(gf,tf,tf/gf))
tot=sum(r[3]+r[4]+r[5] for r in r2); g=sum(r[1] for r in r2); print('overall: %.0f points for %.0f M -> %.2f M per point; days'%(g,tot,tot/g),len(r2))
