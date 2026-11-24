import json, os, pathlib, subprocess, time, urllib.request

root = pathlib.Path(__file__).resolve().parents[1]
out = root / 'reports/artifacts/graphics'
key = os.environ.get('KIE_API_KEY')
if not key:
    p = subprocess.run(['security', 'find-generic-password', '-s', 'kie-api-key', '-w'], capture_output=True, text=True)
    key = p.stdout.strip() if p.returncode == 0 else None
if not key:
    f = pathlib.Path.home() / '.config/kie/api_key'
    key = f.read_text().strip() if f.exists() else None
if not key:
    raise SystemExit('KIE_API_KEY unavailable')

prompt = '''Premium editorial product illustration, refined physical paper sculpture with beautiful soft studio lighting, matte porcelain and finely textured heavy paper on warm cream #f6f4ee backdrop. Restrained forest charcoal #252820, burnt orange #bd481f, and pale sage. A precise minimal branching track sculpted into a low circular cream platform: several small cream task tiles enter from the lower left, move through a single elegant burnt-orange switch at center, then separate into three distinct short pathways ending in three geometrically different destinations: a simple small cube, a medium stacked stepped block, and a taller architectural arch. Only one path is subtly highlighted orange. A separate small cream tray with one unresolved tile sits beside the switch, expressing handoff rather than certainty. Clear readable visual hierarchy, physically believable scale, large generous negative space, tactile detail, sophisticated art direction, subtle long shadows, overhead three-quarter isometric view, aesthetically balanced composition filling center 75 percent of image. Meaning: select among a few known actions, then verify with evidence. This is conceptual artwork, never a screenshot or data chart. No text, no letters, no numbers, no logos, no fake UI, no glowing circuitry, no robots, no floating glass panels, no gradients. Crisp 4K detail, landscape 3:2 composition.'''
payload = {'model':'nano-banana-pro','input':{'prompt':prompt,'image_input':[],'aspect_ratio':'3:2','resolution':'4K','output_format':'png'}}

def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)

receipt = {'requestedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()), 'request':payload,'pricingSource':'https://kie.ai/nano-banana-pro','estimatedPriceUSD':0.12,'priceIsReceipt':False,'documentationSource':'https://kie.ai/nano-banana-pro','qualityRationale':'User requested premium most expensive graphics; current official Kie page lists Nano Banana Pro 4K above GPT Image 2 4K. No separate quality knob is exposed.'}
submitted = call('https://api.kie.ai/api/v1/jobs/createTask',payload)
tid = submitted.get('data',{}).get('taskId')
if not tid: raise SystemExit(json.dumps(submitted))
receipt['taskId'] = tid
(out/'generation-receipt.json').write_text(json.dumps(receipt,indent=2))
print('Submitted premium 4K image; taskId='+tid,flush=True)
for attempt in range(100):
    result = call('https://api.kie.ai/api/v1/jobs/recordInfo?taskId='+tid)
    data = result.get('data',{})
    if data.get('state') == 'fail':
        receipt['result'] = data
        (out/'generation-receipt.json').write_text(json.dumps(receipt,indent=2))
        raise SystemExit('Image generation failed: '+str(data.get('failMsg')))
    if data.get('state') == 'success':
        url = json.loads(data['resultJson'])['resultUrls'][0]
        req = urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=90) as resp:
            (out/'decision-routing-4k.png').write_bytes(resp.read())
        receipt['result'] = data
        (out/'generation-receipt.json').write_text(json.dumps(receipt,indent=2))
        print('Saved '+str(out/'decision-routing-4k.png'),flush=True)
        break
    time.sleep(5)
else:
    raise SystemExit('Generation still pending; resume recordInfo with saved task id')
