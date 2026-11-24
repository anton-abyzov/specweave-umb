"""Run shipped Jev module in a one-off pod subprocess, never enable deployment.

OPENROUTER_API_KEY is passed over kubectl stdin, never argv or a saved file.
Only an authored public sentence goes to provider; EasyChamp API is a local
HTTP fixture and session state is in memory. No customer data or DB writes.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

SMOKE = r'''
import asyncio, hashlib, json, logging, os, sys, time
from dataclasses import asdict
from unittest.mock import AsyncMock
config=json.loads(sys.stdin.read())
inherited_mode=os.getenv('JEV_READ_ROUTING_MODE','off')
os.environ['OPENROUTER_API_KEY']=config['api_key']
os.environ['JEV_READ_ROUTING_MODE']='enabled'
os.environ.pop('LOGFIRE_API_KEY',None)
logging.disable(logging.CRITICAL)
import httpx
from services.intent_router import IntentRouter
from services import jev_read_router, session_context
from services.direct_api_service import direct_api_service

async def main():
    api_calls=[]
    def fixture(request):
        api_calls.append({'method':request.method,'path':request.url.path})
        if request.method=='GET' and request.url.path=='/aioptimize/champ-leagues/my':
            return httpx.Response(200,json=[{'id':'demo-league','name':'Demo Community League','sportKind':'Soccer'}])
        return httpx.Response(500,json={'error':'unexpected fixture call'})
    ctx=session_context.ChatSessionContext(chat_id='jev-isolated-smoke')
    session_context.context_manager.get_context_async=AsyncMock(return_value=ctx)
    old_client=direct_api_service.client
    direct_api_service.client=httpx.AsyncClient(transport=httpx.MockTransport(fixture))
    original=jev_read_router.classify_read
    decisions=[]
    async def measured(message):
        decision=await original(message)
        decisions.append(asdict(decision))
        return decision
    jev_read_router.classify_read=measured
    router=IntentRouter(jwt_token='synthetic-fixture-token',api_url='https://fixture.invalid',chat_id='jev-isolated-smoke')
    start=time.perf_counter()
    response,handled=await router.handle('Could I see the leagues available to me?')
    result={'status':'pass' if handled and 'Demo Community League' in response else 'abstained_or_failed','handled':handled,'response':response,'latency_ms':(time.perf_counter()-start)*1000,'decisions':decisions,'api_calls':api_calls,'module_sha256':hashlib.sha256(open(jev_read_router.__file__,'rb').read()).hexdigest(),'process_mode':os.environ['JEV_READ_ROUTING_MODE'],'customer_data_used':False,'deployment_mode_changed':False,'inherited_mode':inherited_mode}
    await direct_api_service.client.aclose()
    await old_client.aclose()
    print(json.dumps(result))
asyncio.run(main())
'''

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--pod',required=True)
parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args()
if args.out.exists():
    raise SystemExit('Refusing to overwrite an earlier smoke receipt; use a new output path')
if not os.getenv('OPENROUTER_API_KEY'):
    raise SystemExit('OPENROUTER_API_KEY required')
pre=json.loads(subprocess.check_output(['kubectl','get','pod',args.pod,'-n','ec-chat-api','-o','json'],text=True))
main_container=next(c for c in pre['spec']['containers'] if 'ec-chat-api' in c['image'])
mode=next((e.get('value','secret-ref') for e in main_container.get('env',[]) if e['name']=='JEV_READ_ROUTING_MODE'),'unset (default off)')
try:
    result=subprocess.run(['kubectl','exec','-i',args.pod,'-n','ec-chat-api','-c',main_container['name'],'--','python','-c',SMOKE],input=json.dumps({'api_key':os.environ['OPENROUTER_API_KEY']}),text=True,capture_output=True,timeout=30)
    if result.returncode:
        # No library stderr, which could contain diagnostics with secrets.
        receipt={'status':'process_failed','returncode':result.returncode,'provider_result':'unknown'}
    else:
        try:
            receipt=json.loads(result.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            receipt={'status':'invalid_process_output','provider_result':'unknown'}
except subprocess.TimeoutExpired:
    receipt={'status':'process_timeout','provider_result':'unknown'}
receipt.update({'measured_at':datetime.now(timezone.utc).isoformat(),'pod':args.pod,'image':main_container['image'],'image_id':next(s['imageID'] for s in pre['status']['containerStatuses'] if s['name']==main_container['name']),'deployment_mode':mode})
args.out.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
