from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json, datetime, subprocess, hashlib, os
out=Path(__file__).parent
port=int(os.environ.get('SIDEBAR_VERIFY_PORT','5897'))
base=f'http://127.0.0.1:{port}/'
repo=Path('/Users/antonabyzov/.codex/worktrees/project-names-release/specweave-umb/repositories/anton-abyzov/specweave-studio')
receipt={'source':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'observedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'proof':'Isolated real StudioSidebar + SidebarUpdatePill + ToastProvider; real grouping/snapshot source; production CSS; fixture IPC and component-test store mocks; no live app/stores/providers','screenshots':[],'cases':[],'errors':[],'passed':False,'sourceUnchanged':False}
def screenshot(page,name):
 page.wait_for_function("(()=>{const items=Array.from(document.querySelectorAll('[data-slot=toast-viewport] > *'));return items.length===1 && items.every(el=>{const r=el.getBoundingClientRect();return r.left>=0 && r.right<=innerWidth && r.top>=0 && r.bottom<=innerHeight})})()")
 path=out/(name+'.png'); page.screenshot(path=str(path),full_page=True,animations='disabled')
 receipt['screenshots'].append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path='/Users/antonabyzov/Library/Caches/ms-playwright/chromium_headless_shell-1243/chrome-headless-shell-mac-arm64/chrome-headless-shell')
 receipt['browser']=browser.version
 try:
  for theme,width in [('light',1440),('dark',1440),('light',390),('dark',390)]:
   context=browser.new_context(viewport={'width':width,'height':900},color_scheme=theme,reduced_motion='reduce')
   page=context.new_page(); errors=[]
   page.on('pageerror',lambda error:errors.append(str(error)))
   page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
   page.route('**/*',lambda route:route.continue_() if route.request.url.startswith((base,'data:','blob:')) else route.abort())
   page.goto(f'{base}?mode=repository&theme={theme}'); page.wait_for_load_state('networkidle')
   if errors: raise AssertionError(errors)
   labels=page.locator('.sws-project-row .sws-side-row-label').all_text_contents()
   assert set(labels)=={'Aide','unnamed','EasyChamp','folder-only','JobWeave','SpecWithCode'},labels
   groups=page.evaluate('window.__groups'); easy=next(g for g in groups if g['key']=='github.com/anton-abyzov/sw_easychamp')
   assert easy['members']==3,easy
   # The actual group still has conflicting proof names; only presentation is corrected.
   assert easy['name']=='anton-abyzov/sw_easychamp',easy
   easyrow=page.locator('.sws-project-row a').filter(has_text='EasyChamp')
   assert easyrow.get_attribute('href')=='/projects/'+easy['key']
   assert json.loads(easyrow.get_attribute('data-route-search'))=={'checkout':'host:easy'}
   expect(easyrow).to_have_attribute('aria-current','page')
   easyrow.hover(); expect(page.locator('[data-slot=tooltip-popup]')).to_contain_text('EasyChamp · /work/sw_easychamp')
   page.mouse.move(width-1,899); page.locator('[data-slot=tooltip-popup]').wait_for(state='hidden')
   page.get_by_role('button',name='Actions for EasyChamp',exact=True).click()
   expect(page.get_by_role('menuitem',name='Archive project')).to_be_visible(); page.keyboard.press('Escape')
   page.get_by_role('button',name='Check for updates',exact=True).click()
   expect(page.get_by_text('No newer update available',exact=True)).to_be_visible()
   expect(page.get_by_text('SpecWithCode 1.0.10 is installed.',exact=True)).to_be_visible()
   screenshot(page,f'{width}-{theme}-update-result')
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'horizontal overflow'
   assert not errors,errors
   receipt['cases'].append({'theme':theme,'viewport':width,'labels':labels,'groupedMembers':3,'selection':True,'tooltip':True,'menu':True,'manualUpdateResult':True,'errors':errors})
   context.close()
  for selection,expected in [('remote','sw_easychamp'),('saved','EasyChamp handoff proof'),('invalid','anton-abyzov/sw_easychamp')]:
   page=browser.new_page(viewport={'width':1440,'height':900}); errors=[]
   page.on('pageerror',lambda error:errors.append(str(error)))
   page.route('**/*',lambda route:route.continue_() if route.request.url.startswith((base,'data:','blob:')) else route.abort())
   page.goto(base+'?selection='+selection); page.wait_for_load_state('networkidle')
   expect(page.locator('.sws-project-row a[aria-current=page] .sws-side-row-label')).to_have_text(expected)
   target=json.loads(page.locator('.sws-project-row a[aria-current=page]').get_attribute('data-route-search'))
   assert target==({'checkout':'remote:easy-remote'} if selection=='remote' else {'checkout':'host:easy-proof'} if selection=='saved' else {}),target
   assert not errors,errors
   receipt['cases'].append({'selection':selection,'label':expected,'errors':errors}); page.close()
  page=browser.new_page(viewport={'width':390,'height':900},reduced_motion='reduce'); errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.route('**/*',lambda route:route.continue_() if route.request.url.startswith((base,'data:','blob:')) else route.abort())
  page.goto(base+'?update=error'); page.wait_for_load_state('networkidle')
  page.get_by_role('button',name='Check for updates',exact=True).click()
  expect(page.get_by_text('Could not check for updates',exact=True)).to_be_visible()
  expect(page.get_by_text('Update server is temporarily unavailable.',exact=True)).to_be_visible()
  expect(page.get_by_text('No newer update available',exact=True)).to_have_count(0)
  screenshot(page,'390-error-result')
  assert not errors,errors
  receipt['cases'].append({'handledErrorFeedback':True,'checked':True,'errors':errors}); page.close()
  assert len(receipt['cases'])==8 and len(receipt['screenshots'])==5
  receipt['sourceUnchanged']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==receipt['source'] and not subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True).strip()
  assert receipt['sourceUnchanged']; receipt['passed']=True
 except BaseException as error:
  receipt['errors'].append(type(error).__name__+': '+str(error)); raise
 finally:
  browser.close(); receipt['completedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
  (out/'browser-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
