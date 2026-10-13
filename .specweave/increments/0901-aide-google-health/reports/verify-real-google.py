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


def timestamp(value, label):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(parsed.tzinfo is not None and parsed <= datetime.now(timezone.utc), label)
        return parsed
    except (AttributeError, TypeError, ValueError):
        raise SystemExit(label)


def exact_number(value, expected):
    return type(value) in (int, float) and value == expected


def verify_cleanup(receipt):
    cleanup = receipt.get("cleanup", {})
    require(cleanup.get("ownedSessionRevoked") is True, "Owned temporary bearer session was not revoked")
    require(cleanup.get("existingActiveSessionsPreserved") is True, "Existing active sessions not preserved")
    require(cleanup.get("pairingLinksCreatedByRunner") == 0 and not cleanup.get("failure"), "Authentication cleanup failed")


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("status_receipt")
parser.add_argument("native_receipt")
parser.add_argument("--expected-version", required=True)
parser.add_argument("--expected-source", required=True, help="Independently verified full 40-character Git source commit")
parser.add_argument("--dispatch-receipt", help="Original native/1 dispatch receipt required for inspect/0 recovery")
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
require(status.get("phase") == "status", "Status receipt phase mismatch")
require(native.get("phase") in ("native", "inspect"), "Native proof receipt phase mismatch")
for receipt in (status, native):
    require(receipt.get("serverVersion") == args.expected_version, "Observed server version differs from expected release")
    require(receipt.get("serverSourceCommit") == expected_source, "Observed server source differs from expected commit or is missing")
    require(receipt.get("projectId") == "5428ab1e-79c4-4f5f-b245-5f231b4f2cdf", "Aide project mismatch")
    require(receipt.get("consentReady") is True, "Google consent/project grants not ready")
    require(not receipt.get("failure"), "Receipt has a verification failure")
    google = receipt["google"]
    require(google["connected"] and google["clientConfigured"], "Google account is not connected/configured")
    require(set(google["services"]) == services and set(google["aideAccess"]) == services, "Missing Google service/project permission")
    verify_cleanup(receipt)
    timestamp(receipt.get("finishedAt"), "Invalid receipt time")

require(status["origin"] == native["origin"] and status["baseDir"] == native["baseDir"], "Host mismatch")
require(status["serverVersion"] == native["serverVersion"] and status["serverSourceCommit"] == native["serverSourceCommit"], "Status/native source or version mismatch")
require(exact_number(status.get("nativeTurnsRequested"), 0), "Status receipt requested a native turn")
proof = native["native"]
require(proof.get("dispatchBoundToSource") is True, "Native dispatch was not bound to the observed source")
dispatch_hash = None
if native["phase"] == "native":
    require(exact_number(native.get("nativeTurnsRequested"), 1), "Fresh native receipt must request one turn")
    require(proof.get("dispatched") is True and proof.get("resumedReceipt") is False, "Native receipt is not a fresh dispatch")
    require(not args.dispatch_receipt and not native.get("dispatchReceiptSha256"), "Fresh native receipt cannot use recovery provenance")
    require(timestamp(proof.get("dispatchAttemptedAt"), "Invalid native dispatch time") <= timestamp(native.get("finishedAt"), "Invalid native finish time"), "Native dispatch occurred after receipt finished")
else:
    require(exact_number(native.get("nativeTurnsRequested"), 0), "Inspect recovery must request zero turns")
    require(proof.get("dispatched") is False and proof.get("resumedReceipt") is True, "Inspect recovery must only read the original run")
    require(args.dispatch_receipt, "Inspect recovery requires --dispatch-receipt")
    original, dispatch_hash = load(args.dispatch_receipt)
    require(native.get("dispatchReceiptSha256") == dispatch_hash, "Inspect dispatch receipt hash mismatch")
    require(original.get("phase") == "native" and exact_number(original.get("nativeTurnsRequested"), 1), "Original dispatch must be native/1")
    for key in ("serverVersion", "serverSourceCommit", "origin", "baseDir", "projectId"):
        require(original.get(key) == native.get(key), "Original dispatch identity/source mismatch")
    original_proof = original.get("native", {})
    for key in ("commandId", "threadId"):
        require(isinstance(proof.get(key), str) and bool(proof[key]) and original_proof.get(key) == proof[key], "Original dispatch command/thread mismatch")
    require(original_proof.get("resumedReceipt") is False and original_proof.get("dispatchBoundToSource") is True, "Original dispatch was not fresh and source-bound")
    require(timestamp(original_proof.get("dispatchAttemptedAt"), "Invalid original dispatch time") <= timestamp(original.get("finishedAt"), "Invalid original finish time"), "Original dispatch occurred after receipt finished")
    verify_cleanup(original)
    # Original failure/timeout is provenance only. Success must come from the
    # separately completed inspect result and its four persisted tool results.
require(proof.get("success") is True and proof.get("runStatus") == "completed", "Native Aide run did not successfully complete")
require(proof.get("googleToolCalls") == 4 and proof.get("unexpectedGoogleToolCalls") == 0, "Expected exactly four Google calls")
require(proof.get("additionalDynamicTools") == 0 and proof.get("delegationItems") == 0, "Unexpected tools or delegation")
require(exact_number(proof.get("additionalNativeTools"), 0), "Unexpected or uncounted native tools")
require(proof.get("healthBeforeReads") is True, "Google health did not pass before content reads")
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
    "dispatchReceiptSha256": dispatch_hash,
    "proofPhase": native["phase"],
    "nativeRunCompleted": True,
    "googleHealth": "all_three_apis_verified",
    "readCounts": {row["tool"]: row["itemCount"] for row in results if "itemCount" in row},
    "ownedTemporarySessionsRevoked": True,
    "existingSessionsPreserved": True,
}))
