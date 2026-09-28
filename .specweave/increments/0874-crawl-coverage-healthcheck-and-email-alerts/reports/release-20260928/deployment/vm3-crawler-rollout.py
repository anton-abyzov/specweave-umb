import hashlib
import json
import pathlib
import subprocess
import time
import urllib.request
from datetime import datetime, timezone

SHA = "a066df378c8f42ef6e5515d906d7feb996c2d475"
NAME = "scanner-worker-crawl-worker-1"
OLD_ID = "f92748edbe5c6f4a615347b6fceed52e4273d447e64eede83a1ce4d4d5c74b07"
OLD_IMAGE = "sha256:30ab3d044ff029b283144a1fae6540a267ca606d44165bfd0752e2fbed04f99a"
SCANNER = "scanner-worker-scanner-worker-1"
SCANNER_ID = "2633c121f4f10ed37a6a23f0b7b762a228ab6bd3d12d2a149c30f2b79e8919ff"
NEW_IMAGE = "sha256:52ff7bbdd69eeb895bd34f16c501aad3d898ba5546fa0ddee4e3c5c574e31d14"
FILES = {
    "/opt/scanner-worker/.env": "94a681b1f67f786a39d20fbce9c41c492c1c9a3b85cb25f891e61d5ca076055e",
    "/opt/crawl-worker/.env": "8d7f11b89c1f3a9ef67abb417d8603b32076966711199ef167b838ec7c5f28d7",
    "/opt/scanner-worker/docker-compose.yml": "3d17aee7fbf5876cb28ad8331e2310b133ba7bcbebba9c1cf3a0f4feb5b7e875",
}
HASHES = {
    "server.js": "107e47757cbc0df85af1927ff40f5e64116035f6e969078f7a537d3f8bf79c67",
    "scheduler.js": "55a555d090ac9e9bd414ccd6da717ccc960c6291aa1b63d0937c11d99594d2a2",
    "sources/github-sharded.js": "46c7c3c8273f937c00e554780a0ca4c5ecc2fa9eb098fb2d43f61b8cccf8b97c",
    "lib/inline-submitter.js": "14c4e5d167bfb61c62d09709d1ceb5d9ccf1d99747cd5e1a7e2a8fc7e5e2f334",
}

def inspect(name):
    return json.loads(subprocess.check_output(["docker", "inspect", name]))[0]

def emit(phase, **data):
    print(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "phase": phase, **data}), flush=True)

def guard():
    c = inspect(NAME)
    assert c["Id"] == OLD_ID and c["Image"] == OLD_IMAGE, "Crawler identity drift"
    assert inspect(SCANNER)["Id"] == SCANNER_ID, "Scanner identity drift"
    assert all(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() == h for p, h in FILES.items()), "Configuration drift"
    assert any(m.get("Name") == "scanner-worker_crawl-state" and m["Destination"] == "/tmp/crawl-state" for m in c["Mounts"])
    status = json.load(urllib.request.urlopen("http://127.0.0.1:9600/status", timeout=10))
    assert status["activeCrawls"] == 0, "Manual crawl active"
    assert all(s["status"] not in ["running", "crawling"] for s in status["scheduler"]["sources"].values()), "Scheduled source active"
    return status

attempted = False
try:
    status = guard()
    image = inspect("vskill-crawl-worker:" + SHA)
    assert image["Id"] == NEW_IMAGE and image["Config"]["Labels"]["org.opencontainers.image.revision"] == SHA
    raw = subprocess.check_output(["docker", "run", "--rm", "--entrypoint", "sha256sum", "vskill-crawl-worker:" + SHA, *HASHES], text=True)
    assert dict((line.split()[1], line.split()[0]) for line in raw.splitlines()) == HASHES
    # Verify the selected existing credential from the already repaired file.
    lines = pathlib.Path("/opt/scanner-worker/.env").read_text().splitlines()
    value = next(line.split("=", 1)[1].strip().strip("\"'") for line in lines if line.startswith("GITHUB_TOKENS="))
    tokens = [t.strip() for t in value.split(",") if t.strip()]
    assert len(tokens) == 1
    request = urllib.request.Request("https://api.github.com/search/code?q=filename%3ASKILL.md+size%3A0..200&per_page=1", headers={"Authorization": "Bearer " + tokens[0], "Accept": "application/vnd.github+json", "User-Agent": "vskill-0874-release-verification"})
    with urllib.request.urlopen(request, timeout=20) as response:
        assert response.status == 200
        emit("credential-readback", status=response.status, tokenCount=len(tokens), remaining=response.headers.get("X-RateLimit-Remaining"), totalCount=json.load(response)["total_count"])
    assert inspect("scanner-worker-crawl-worker")["Id"] == OLD_IMAGE, "Compose image tag drift"
    subprocess.run(["docker", "tag", OLD_IMAGE, "vskill-crawl-worker:rollback-0874-f92748ed"], check=True)
    status = guard()  # immediately before image promotion and service recreation
    emit("prestate", crawlerId=OLD_ID, scannerId=SCANNER_ID, oldImage=OLD_IMAGE, newImage=NEW_IMAGE, sourceStatuses={k:v["status"] for k,v in status["scheduler"]["sources"].items()}, files=FILES)
    attempted = True
    emit("recreate-attempted", mergeSha=SHA)
    subprocess.run(["docker", "tag", "vskill-crawl-worker:" + SHA, "scanner-worker-crawl-worker"], check=True)
    result = subprocess.run(["docker", "compose", "up", "-d", "--no-deps", "--no-build", "--force-recreate", "crawl-worker"], cwd="/opt/scanner-worker", capture_output=True, text=True)
    emit("compose-returned", exitCode=result.returncode)
    c = inspect(NAME)
    env = dict(x.split("=", 1) for x in c["Config"]["Env"] if "=" in x)
    assert c["Id"] != OLD_ID and c["Image"] == NEW_IMAGE
    assert inspect(SCANNER)["Id"] == SCANNER_ID
    assert env.get("SHARD_BISECT") != "1" and env.get("SHARD_MODE") == "size-date"
    assert len([t for t in env.get("GITHUB_TOKENS", "").split(",") if t.strip()]) == 1
    assert env.get("ASSIGNED_SOURCES") == "github-sharded,skills-sh,submission-scanner"
    assert any(m.get("Name") == "scanner-worker_crawl-state" and m["Destination"] == "/tmp/crawl-state" for m in c["Mounts"])
    raw = subprocess.check_output(["docker", "exec", NAME, "sha256sum", *HASHES], text=True)
    assert dict((line.split()[1], line.split()[0]) for line in raw.splitlines()) == HASHES
    emit("readback", crawlerId=c["Id"], image=c["Image"], revision=c["Config"]["Labels"].get("org.opencontainers.image.revision"), scannerId=SCANNER_ID, tokenCount=1, shardMode=env.get("SHARD_MODE"), adaptive=False, sources=env.get("ASSIGNED_SOURCES"), stateVolume="scanner-worker_crawl-state", sourceHashes=HASHES)
    assert result.returncode == 0, "Compose returned failure despite readback; inspect before further actions"
except Exception as error:
    emit("partial_or_uncertain" if attempted else "not-applied", errorType=type(error).__name__, reason=str(error)[:250], requireFreshReadback=attempted)
    raise SystemExit(1)
