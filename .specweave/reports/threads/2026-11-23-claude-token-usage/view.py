import json,sys,collections
d=json.load(open(sys.argv[1]))
M=1e6
print(d['machine'],d['roots'],'files',d['files_scanned'],'calls',d['calls'],'sessions',d['sessions_n'],'accounts',d['accounts'])
print('\nDAY        calls   wtM   readM  w1hM  w5M  outM  hit%  read%ofwt write%ofwt out%ofwt')
for r in d['by_day']:
    den=r['read']+r['w5']+r['w1h']+r['inp']
    wt=r['wt'] or 1
    print(r['day'],'%6d %6.1f %7.1f %5.1f %5.1f %5.2f %5.1f %6.1f %6.1f %6.1f'%(r['calls'],r['wt']/M,r['read']/M,r['w1h']/M,r['w5']/M,r['out']/M,100*r['read']/den if den else 0,10*r['read']/wt,100*(2*r['w1h']+1.25*r['w5'])/wt,500*r['out']/wt))
print('\nMODEL x kind (wtM)')
agg=collections.defaultdict(float)
for r in d['by_day_model']: agg[(r['model'],r['kind'])]+=r['wt']
for k,v in sorted(agg.items(),key=lambda x:-x[1]): print('  %-28s %-5s %8.1f'%(k[0],k[1],v/M))
print('\nSPIKES by cause (n, tokM, wtM)')
agg=collections.defaultdict(lambda:[0,0,0])
for r in d['spikes']:
    a=agg[(r['kind'],r['cause'])]; a[0]+=r['n'];a[1]+=r['tok'];a[2]+=r['wt']
for k,v in sorted(agg.items(),key=lambda x:-x[1][2]): print('  %-5s %-26s %5d %8.1f %8.1f'%(k[0],k[1],v[0],v[1]/M,v[2]/M))
print('\nTTL by kind (wtM, w1hM, w5M)')
agg=collections.defaultdict(lambda:[0,0,0])
for r in d['by_day_ttl']:
    a=agg[(r['kind'],r['ttl'])]; a[0]+=r['wt'];a[1]+=r['w1h'];a[2]+=r['w5']
for k,v in sorted(agg.items()): print('  ',k,['%.1f'%(x/M) for x in v])
print('\nCTX buckets (wtM, readM)')
agg=collections.defaultdict(lambda:[0,0])
for r in d['by_day_ctx_bucket']:
    a=agg[(r['kind'],r['bucket'])]; a[0]+=r['wt'];a[1]+=r['read']
for k,v in sorted(agg.items()): print('  ',k,['%.1f'%(x/M) for x in v])
print('\nFIRST CALL CTX'); 
for r in d['first_call_ctx']: print('  ',r)
print('\nORIGIN');
for r in d['by_day_origin']: print('  ',r['day'],r['origin'],'%.1f'%(r['wt']/M),r['sessions'])
print('\nTOP SESSIONS')
for s in d['sessions'][:int(sys.argv[2]) if len(sys.argv)>2 else 25]:
    print('  %s %-7s %7.1fM sub%6.1fM calls%5d hit%.3f maxctx%7d mc%d cmp%d sa%3d pr%3d>200k:%3d %s..%s %s | %s | %s %s'%(s['sid'],s['origin'],s['wt']/M,s['wt_sub']/M,s['calls'],s['hit'] or 0,s['maxctx'],s['model_changes'],s['compactions'],s['subagents'],s['prompts'],s['prompts_over_200k'],s['first'][5:],s['last'][5:],(s['thread'] or s['cwd'])[:60],','.join('%s:%d'%(k.replace('claude-',''),v) for k,v in s['models'].items()),s['efforts'],s['spikes']))
