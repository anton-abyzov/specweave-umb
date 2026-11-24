import json,collections,datetime
m4=json.load(open('m4-v3.json')); m5=json.load(open('m5-v3.json')); M=1e6
print('accounts', m4['accounts'], m5['accounts'])
name={'f4797a8e':'admin@easychamp.com','1ae55f97':'anton.abyzov@easychamp.com','3865fcdb':'marketing@easychamp.com','0d759728':'anton.abyzov@olympus'}
def hr(ms): return datetime.datetime.utcfromtimestamp(ms/1000).strftime('%Y-%m-%dT%H')
ser=collections.defaultdict(list)
for src in (m4,m5):
    for s in src['limit_history']:
        if s['windowId'] in('seven_day','seven_day_fable'):
            ser[(s['accountKey'].split(':')[1],s['windowId'])]+= [tuple(x) for x in s['samples']]
print({k:len(v) for k,v in ser.items()})
gain=collections.defaultdict(float)  # (acctname,win,hour)
for k,sm in ser.items():
    sm=sorted(set(sm)); cur=None; curwin=None
    for i,(at,p,rs) in enumerate(sm):
        win=round(rs/3600e3) if rs else None
        if cur is None: cur=p; curwin=win; continue
        if p>=cur:
            if (at-sm[i-1][0])<6*3600e3: gain[(k[0],k[1],hr(at))]+=p-cur
            else: gain[(k[0],k[1],hr(at))]+=0; gain[(k[0],k[1]+'_gap',hr(at))]+=p-cur
            cur=p; curwin=win or curwin; continue
        rec=any(q>=cur-2 for (a2,q,_) in sm[i+1:i+40] if a2-at<=30*60e3)
        if rec: continue
        newwin = win is not None and curwin is not None and abs(win-curwin)>2
        if newwin or p<cur/2:
            if newwin: gain[(k[0],k[1],hr(at))]+=p
            cur=p; curwin=win or curwin
use=collections.defaultdict(lambda:collections.defaultdict(float))
for src in (m4,m5):
    for h in src['hourly_utc_account']:
        fam=h['fam']; a=h['acct']
        key=(a,h['hour'])
        if fam.startswith('advisor:'): use[key]['fable' if 'fable' in fam else 'opus']+=h['adv_wt']
        else: use[key]['fable' if fam=='fable' else ('opus' if fam=='opus' else 'other')]+=h['wt']
# per account per UTC day
def match(nm):
    for k,v in name.items():
        if nm.startswith(v.split('@')[0]) and (('olympus' in nm)==('olympus' in v)): return k
days=sorted({h[:10] for (_,h) in use if h>='2026-11-12'})
print('day acct | pts overall, fable, (gap pts) | own opus M, fable M, other M | unattributed fleet M that day | M/pt')
rows=[]
for d in days:
    none=sum(sum(v.values()) for (a,h),v in use.items() if a=='None' and h[:10]==d)/M
    for an in sorted({k[0] for k in ser}):
        aid=match(an)
        g=sum(v for (a,w,h),v in gain.items() if a==an and w=='seven_day' and h[:10]==d)
        gg=sum(v for (a,w,h),v in gain.items() if a==an and w=='seven_day_gap' and h[:10]==d)
        gf=sum(v for (a,w,h),v in gain.items() if a==an and w=='seven_day_fable' and h[:10]==d)
        o=sum(v['opus'] for (a,h),v in use.items() if a==aid and h[:10]==d)/M
        f=sum(v['fable'] for (a,h),v in use.items() if a==aid and h[:10]==d)/M
        x=sum(v['other'] for (a,h),v in use.items() if a==aid and h[:10]==d)/M
        if g+gf+gg+o+f<1: continue
        tot=o+f+x
        print(d,'%-14s'%an[:14],aid,'| %4.0f %4.0f (%3.0f) | %7.1f %7.1f %5.1f | none %6.1f | %s  fable%%=%s'%(g,gf,gg,o,f,x,none,('%.2f'%(tot/g)) if g>=5 else '-', ('%.0f'%(100*f/tot)) if tot else '-'))
        rows.append((d,an,g,gf,o,f,x,none))
