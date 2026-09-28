"""Read-only Cloudflare deployment and exact six-consumer receipt; no token output."""
import datetime, json, pathlib, re, urllib.request, urllib.error, sys
text=pathlib.Path('/Users/antonabyzov/Library/Preferences/.wrangler/config/default.toml').read_text()
token=re.search(r'^oauth_token\s*=\s*"([^"]+)"',text,re.M).group(1)
base='https://api.cloudflare.com/client/v4/accounts/1364b528762500de4f870e064229d443'
def get(path):
    request=urllib.request.Request(base+path,headers={'Authorization':'Bearer '+token})
    try:
        with urllib.request.urlopen(request,timeout=30) as response: data=json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError('Cloudflare read status '+str(error.code)) from None
    if not data.get('success'): raise RuntimeError('Cloudflare read returned failure codes '+str([x.get('code') for x in data.get('errors',[])]))
    return data['result']
deployments=get('/workers/scripts/verified-skill-com/deployments')
expected=json.loads(pathlib.Path('/tmp/cc-work-release-20260928/0874/cloudflare-queue-readback.json').read_text())
queues=[]
for previous in expected:
    q=get('/queues/'+previous['queue_id'])
    current=q.get('consumers',[])
    exact=sorted(current,key=lambda x:x.get('consumer_id',''))==sorted(previous['consumers'],key=lambda x:x.get('consumer_id',''))
    queues.append({'queueId':q['queue_id'],'queueName':q['queue_name'],'consumers':current,'settings':q.get('settings'),'consumerMatchesReviewedBaseline':exact,'deliveryEnabled':q.get('settings',{}).get('delivery_paused') is False})
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'worker':'verified-skill-com','deployments':deployments,'queues':queues,'allSixConsumersMatch':len(queues)==6 and all(q['consumerMatchesReviewedBaseline'] and q['deliveryEnabled'] for q in queues)}
print(json.dumps(receipt,indent=2))
assert receipt['allSixConsumersMatch'], 'Consumer configuration mismatch; inspect before further action'
