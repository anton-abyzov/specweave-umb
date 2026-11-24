"""Read-only verification of this release's published and installed receipts."""
import hashlib
import json
from pathlib import Path
import plistlib
import subprocess

release = json.loads(subprocess.check_output([
    "gh", "release", "view", "v1.0.14", "--repo", "anton-abyzov/specwithcode",
    "--json", "tagName,isDraft,publishedAt,url,assets",
]))
assert release["tagName"] == "v1.0.14" and not release["isDraft"]
assert release["publishedAt"] and len(release["assets"]) == 11
base = Path("/Volumes/SanDisk APFS/SpecWithCodeReleases/0907-114")
anonymous = base / "anonymous-939a-1/receipt.json"
assert hashlib.sha256(anonymous.read_bytes()).hexdigest() == "07699a99d84e461b455fdefa9e1d1d3f40e495aadae8123eeb4257e15ea336a2"
for machine, digest in [
    ("m1", "08edabc4fb7c8a597062e67c42be6996190f276d380285d55f47dbca507f7fc0"),
    ("m3", "05280c4089fe3f9782e41e335f4893a845c801f8f36870189f3827c43118d132"),
]:
    path = base / f"worker-install-939a-1/remote-execution-{machine}-root-939a-1/final-readback-final-readback-final-1/final-readback.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    receipt = json.loads(path.read_text())
    assert receipt["installationVersion"] == "1.0.14"
    assert receipt["controllerPhase"] == "installed-verified"
    print(f"{machine}: installed 1.0.14, sealed readback verified")
with open("/Applications/SpecWithCode.app/Contents/Info.plist", "rb") as file:
    assert plistlib.load(file)["CFBundleShortVersionString"] == "1.0.14"
print("Mac app: installed 1.0.14")
print("Public release: 1.0.14, 11 assets, anonymous readback receipt verified")
print("Live paid inference and six-route handoff acceptance are not asserted.")
