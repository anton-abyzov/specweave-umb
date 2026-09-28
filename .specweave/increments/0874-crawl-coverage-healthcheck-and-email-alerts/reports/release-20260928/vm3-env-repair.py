"""Run on VM3 only after independent review. No secrets emitted. No restart."""
import hashlib, json, os, pathlib, subprocess, tempfile, time, urllib.request, urllib.error
import sys
CONTAINER = "scanner-worker-crawl-worker-1"
EXPECTED_CONTAINER = "f92748edbe5c6f4a615347b6fceed52e4273d447e64eede83a1ce4d4d5c74b07"
EXPECTED = {
 "/opt/scanner-worker/.env": "3fcc8c97401e92ea9cbe2f6de028d7584fec17104717be73f0761f20b9342b98",
 "/opt/crawl-worker/.env": "b9c17e1f80ba2a92d8dcce001366f54ef9626cdd3e835bfc6539a4eadd5adf6b",
}
c = json.loads(subprocess.check_output(["docker", "inspect", CONTAINER]))[0]
assert c["Id"] == EXPECTED_CONTAINER, "Container changed; review fresh prestate"
runtime = dict(x.split("=", 1) for x in c["Config"]["Env"])
tokens = [x.strip() for x in runtime["GITHUB_TOKENS"].split(",") if x.strip()]
assert len(tokens) == 2, "Token pool changed"
def probe(token):
 req = urllib.request.Request("https://api.github.com/search/code?q=filename%3ASKILL.md%20size%3A0..200&per_page=1", headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json", "User-Agent": "vskill-release-preflight"})
 try:
  with urllib.request.urlopen(req, timeout=15) as r: return r.status, json.load(r).get("total_count", 0)
 except urllib.error.HTTPError as e: return e.code, 0
assert probe(tokens[0])[0] == 401, "First token status changed; do not remove"
valid_status, count = probe(tokens[1])
assert valid_status == 200 and count > 0, "Existing second token lacks live code search"
originals = {}
metadata = {}
for name, digest in EXPECTED.items():
 p = pathlib.Path(name); b = p.read_bytes()
 assert hashlib.sha256(b).hexdigest() == digest, "Environment prestate changed: " + name
 lines = b.decode().splitlines()
 matches = [line.split("=",1)[1].strip().strip(chr(34)).strip(chr(39)) for line in lines if line.startswith("GITHUB_TOKENS=")]
 assert len(matches) == 1 and [x.strip() for x in matches[0].split(",")] == tokens, "Token pool differs: " + name
 originals[name] = b
 metadata[name] = p.stat()
backup = pathlib.Path("/root/vskill-release-backups") / ("0874-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
backup.mkdir(parents=True, mode=0o700, exist_ok=False)
os.chmod(backup.parent, 0o700)
replacements = {}
for index, (name, b) in enumerate(originals.items()):
 saved = backup / (str(index) + ".env")
 saved.write_bytes(b); saved.chmod(0o600)
 lines = b.decode().splitlines(keepends=True)
 out = "".join("GITHUB_TOKENS=" + tokens[1] + "\n" if line.startswith("GITHUB_TOKENS=") else line for line in lines)
 replacements[name] = out.encode()
# Recheck container and each original immediately before its own replacement.
applied = []
replace_attempted = []
try:
 for name, b in replacements.items():
  current = json.loads(subprocess.check_output(["docker", "inspect", CONTAINER]))[0]
  assert current["Id"] == EXPECTED_CONTAINER, "Container changed before write"
  p = pathlib.Path(name)
  fd, staging = tempfile.mkstemp(prefix=".0874-env-", dir=str(p.parent))
  try:
   with os.fdopen(fd,"wb") as f:
    f.write(b); f.flush(); os.fchown(f.fileno(), metadata[name].st_uid, metadata[name].st_gid)
    os.fchmod(f.fileno(), metadata[name].st_mode & 0o777); os.fsync(f.fileno())
   assert p.read_bytes() == originals[name], "Environment changed before write: " + name
   replace_attempted.append(name)
   os.replace(staging, p)
   receipt = {"path":name,"sha256":hashlib.sha256(b).hexdigest(),"replacementCompleted":True,"readbackMatches":None}
   applied.append(receipt)
   print(json.dumps(receipt), flush=True)
   directory = os.open(str(p.parent), os.O_RDONLY | os.O_DIRECTORY)
   try: os.fsync(directory)
   finally: os.close(directory)
   valid = p.read_bytes() == b
   receipt["readbackMatches"] = valid
   print(json.dumps(receipt), flush=True)
   assert valid, "Environment readback differs: " + name
  finally:
   if os.path.exists(staging): os.unlink(staging)
except Exception as error:
 print(json.dumps({"status":"partial_or_uncertain" if replace_attempted else "not-applied","replaceAttempted":replace_attempted,"applied":applied,"backupDirectory":str(backup),"errorType":type(error).__name__,"restarted":False,"next":"Review fresh files; do not blindly retry or restore over drift"}),flush=True)
 sys.exit(1)
print(json.dumps({"status":"applied","changedKeys":["GITHUB_TOKENS"],"existingEntrySelected":1,"searchStatus":valid_status,"searchCount":count,"backupDirectory":str(backup),"files":applied,"restarted":False}))
