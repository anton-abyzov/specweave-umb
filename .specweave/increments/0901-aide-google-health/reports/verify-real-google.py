#!/usr/bin/env python3
"""Verify saved, sanitized native proof without starting another provider turn."""
import hashlib
import json
import argparse
import re
from datetime import datetime, timezone
from pathlib import Path


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def load(path):
    content = Path(path).read_bytes()
    return json.loads(content), hashlib.sha256(content).hexdigest()


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("status_receipt")
parser.add_argument("native_receipt")
parser.add_argument("--expected-version", required=True)
parser.add_argument("--expected-source", required=True, help="Independently verified full 40-character Git source commit")
args = parser.parse_args()
require(re.fullmatch(r"[0-9a-fA-F]{40}", args.expected_source), "Expected source must be a full 40-character Git commit")
require(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?", args.expected_version), "Expected version must be an explicit release version")
expected_source = args.expected_source.lower()
status, status_hash = load(args.status_receipt)
native, native_hash = load(args.native_receipt)
services = {"gmail", "calendar", "drive"}
expected = {
    "studio_google_status",
    "studio_google_gmail_search",
    "studio_google_calendar_events",
    "studio_google_drive_search",
}
for receipt, phase in ((status, "status"), (native, "native")):
    require(receipt.get("phase") == phase, "Receipt phase mismatch")
    require(receipt.get("serverVersion") == args.expected_version, "Observed server version differs from expected release")
    require(receipt.get("serverSourceCommit") == expected_source, "Observed server source differs from expected commit or is missing")
    require(receipt.get("projectId") == "5428ab1e-79c4-4f5f-b245-5f231b4f2cdf", "Aide project mismatch")
    require(receipt.get("consentReady") is True, "Google consent/project grants not ready")
    require(not receipt.get("failure"), "Receipt has a verification failure")
    google = receipt["google"]
    require(google["connected"] and google["clientConfigured"], "Google account is not connected/configured")
    require(set(google["services"]) == services and set(google["aideAccess"]) == services, "Missing Google service/project permission")
    cleanup = receipt["cleanup"]
    require(cleanup.get("ownedSessionRevoked") is True, "Owned temporary bearer session was not revoked")
    require(cleanup.get("existingActiveSessionsPreserved") is True, "Existing active sessions not preserved")
    require(cleanup.get("pairingLinksCreatedByRunner") == 0 and not cleanup.get("failure"), "Authentication cleanup failed")
    require(datetime.fromisoformat(receipt["finishedAt"].replace("Z", "+00:00")) <= datetime.now(timezone.utc), "Invalid receipt time")

require(status["origin"] == native["origin"] and status["baseDir"] == native["baseDir"], "Host mismatch")
require(status["serverVersion"] == native["serverVersion"] and status["serverSourceCommit"] == native["serverSourceCommit"], "Status/native source or version mismatch")
require(status["nativeTurnsRequested"] == 0 and native["nativeTurnsRequested"] == 1, "Unexpected turn count")
proof = native["native"]
require(proof.get("success") is True and proof.get("runStatus") == "completed", "Native Aide run did not successfully complete")
require(proof.get("googleToolCalls") == 4 and proof.get("unexpectedGoogleToolCalls") == 0, "Expected exactly four Google calls")
require(proof.get("additionalDynamicTools") == 0 and proof.get("delegationItems") == 0, "Unexpected tools or delegation")
require(proof.get("providerFailureClasses") == [], "Provider failure present")
results = proof["toolResults"]
require(len(results) == 4 and {row["tool"] for row in results} == expected, "Missing or duplicated Google proof")
for row in results:
    require(row.get("success") is True and row.get("runtimeStatus") == "completed", "Google call did not succeed")
    if row["tool"] == "studio_google_status":
        require(row.get("connectionState") == "verified" and row.get("checkedAt"), "Live API probe was not verified")
        require({check["service"] for check in row["serviceChecks"]} == services, "Missing health probe")
        require(all(check["status"] == "ok" for check in row["serviceChecks"]), "An API health probe failed")
    else:
        require(row.get("requestMatches") is True and 0 <= row.get("itemCount", -1) <= 1, "Read exceeded authorized limit or arguments differed")
print(json.dumps({
    "verifiedAt": datetime.now(timezone.utc).isoformat(),
    "version": native["serverVersion"],
    "sourceCommit": native["serverSourceCommit"],
    "statusReceiptSha256": status_hash,
    "nativeReceiptSha256": native_hash,
    "nativeRunCompleted": True,
    "googleHealth": "all_three_apis_verified",
    "readCounts": {row["tool"]: row["itemCount"] for row in results if "itemCount" in row},
    "ownedTemporarySessionsRevoked": True,
    "existingSessionsPreserved": True,
}))
