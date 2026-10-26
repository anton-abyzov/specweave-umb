import json
from pathlib import Path
p=Path(__file__).parent
identity=json.loads((p/'installed-1.0.76-preflight-20261024.json').read_text())
assert identity['serverVersion']==identity['desktopVersion']=='1.0.76'
assert identity['serverSourceCommit']==identity['manifestSourceCommit']
assert identity['repairAncestry']['status'] in ('ahead','identical')
assert identity['notarization']['exitCode']==0
r=json.loads((p/'routing-live-20261025.json').read_text())
assert r['status']==200 and len(r['subagents'])==2
for lane in ('complex','routine'):
    s=next(x for x in r['subagents'] if x['routing']['lane']==lane)
    assert s['status']=='completed' and s['result']==f'1003_{lane.upper()}_OK'
    assert s['providerInstanceId']=='codex' and s['model']=='gpt-6-astra'
    assert s['routing']['billing']==s['routing']['modelBilling']=='subscription'
    assert s['completionDelivery']['state']=='acknowledged'
assert 'Grok · Grok 4.7: at 100% usage' in next(x for x in r['subagents'] if x['routing']['lane']=='complex')['routing']['skipped']
print('PASS: installed identity, source inclusion, notarization, both terminal lane results, subscription billing, exhausted-provider skip and parent delivery')
