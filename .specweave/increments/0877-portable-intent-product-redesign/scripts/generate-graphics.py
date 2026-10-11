import os,json,subprocess,urllib.request,time,concurrent.futures
from pathlib import Path
out=Path(__file__).resolve().parents[1]/"reports"/"artifacts"
key=os.environ.get("KIE_API_KEY", "")
if not key:
 r=subprocess.run(["security","find-generic-password","-s","kie-api-key","-w"],capture_output=True,text=True); key=r.stdout.strip() if r.returncode==0 else ""
if not key:
 p=Path.home()/".config/kie/api_key"; key=p.read_text().strip() if p.exists() else ""
if not key: raise SystemExit("KIE_API_KEY unavailable")

def call(route,payload=None):
 req=urllib.request.Request("https://api.kie.ai/api/v1/jobs/"+route,data=json.dumps(payload).encode() if payload else None,headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
 with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)

prompts={
"continuity":"Premium editorial still life for an open-source software product about continuity of work across changing tools. A single vivid burnt-orange woven ribbon travels horizontally through three separate upright dark graphite rectangular frames, looping gently through each frame, staying one unbroken strand. Frames stand on warm off-white matte stone surface. Fine woven textile texture in orange, precise machined graphite edges, subtle shadows, photographic studio lighting from upper left. Composition: subject occupies right two-thirds, left third calm warm ivory negative space; all three frames visible. A small ivory folded sheet rests at final frame, representing durable evidence. Architectural product photography, physical realistic materials, elevated design magazine, quiet confidence. Colors only warm ivory #f6f4ed, near-black #20221e, burnt orange #e56b36. No words, no letters, no text, no software UI, no logos, no glow, no gradients, no purple, no people. Wide 16:9.",
"skill-evidence":"Premium editorial still life for a developer skill verification product. Three thin square white ceramic plates arranged as staggered layers on a warm ivory tabletop, the top layer is lifted and inspected by a large precision circular smoked-glass lens held in a matte graphite ring. A small burnt-orange woven tab extends from one plate, a restrained green inset mark in the inspected layer. The lens clearly magnifies the physical fine etched texture; do not add text or symbols. Architectural product photography, macro material detail, studio soft side light, natural shadows. Object centered right with generous calm negative space to left, sophisticated asymmetrical composition. Palette warm ivory #f6f4ed, near-black #20221e, orange #e56b36, tiny forest green. No words, no letters, no UI, no shield, no checkmarks, no robot, no glow, no gradients, no logos. Wide 16:9."
}

def generate(name,prompt):
 payload={"model":"gpt-image-2-text-to-image","input":{"prompt":prompt,"aspect_ratio":"16:9","resolution":"2K"}}
 result=call("createTask",payload)
 tid=result.get("data",{}).get("taskId")
 if not tid: raise RuntimeError(name+": create failed "+str(result.get("code"))+" "+str(result.get("msg")))
 (out/(name+"-generation.json")).write_text(json.dumps({"taskId":tid,**payload},indent=2))
 print(name+" submitted "+tid,flush=True)
 for i in range(120):
  r=call("recordInfo?taskId="+tid).get("data",{})
  if r.get("state")=="success":
   url=json.loads(r["resultJson"])["resultUrls"][0]
   req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
   with urllib.request.urlopen(req,timeout=60) as img:(out/(name+".png")).write_bytes(img.read())
   print(name+" saved",flush=True);return
  if r.get("state")=="fail":raise RuntimeError(name+": "+str(r.get("failMsg") or r.get("failCode")))
  time.sleep(5)
 raise RuntimeError(name+": timed out")
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for f in [pool.submit(generate,k,v) for k,v in prompts.items()]:f.result()
