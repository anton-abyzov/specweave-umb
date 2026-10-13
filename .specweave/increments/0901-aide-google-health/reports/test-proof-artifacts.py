#!/usr/bin/env python3
"""Offline synthetic checks of the receipt validator; never live Google proof."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

reports = Path(__file__).resolve().parent
fake_source = "a" * 40
now = datetime.now(timezone.utc).isoformat()
services = ["gmail", "calendar", "drive"]
base = {
    "serverVersion": "1.0.8", "serverSourceCommit": fake_source,
    "projectId": "5428ab1e-79c4-4f5f-b245-5f231b4f2cdf", "consentReady": True,
    "origin": "http://127.0.0.1:8319", "baseDir": "/synthetic-only", "finishedAt": now,
    "google": {"connected": True, "clientConfigured": True, "services": services, "aideAccess": services},
    "cleanup": {"ownedSessionRevoked": True, "existingActiveSessionsPreserved": True, "pairingLinksCreatedByRunner": 0},
}
status = {**deepcopy(base), "phase": "status", "nativeTurnsRequested": 0}
native = {**deepcopy(base), "phase": "native", "nativeTurnsRequested": 1, "native": {
    "commandId": "00000000-0000-4000-8000-000000000001",
    "threadId": "project-coordinator:5428ab1e-79c4-4f5f-b245-5f231b4f2cdf",
    "dispatched": True, "resumedReceipt": False, "dispatchAttemptedAt": now,
    "dispatchBoundToSource": True, "healthBeforeReads": True, "additionalNativeTools": 0,
    "success": True, "runStatus": "completed", "googleToolCalls": 4,
    "unexpectedGoogleToolCalls": 0, "additionalDynamicTools": 0, "delegationItems": 0,
    "providerFailureClasses": [], "toolResults": [
        {"tool": "studio_google_status", "success": True, "runtimeStatus": "completed", "connectionState": "verified", "checkedAt": now,
         "serviceChecks": [{"service": service, "status": "ok"} for service in services]},
        *[{"tool": tool, "success": True, "runtimeStatus": "completed", "requestMatches": True, "itemCount": 1}
          for tool in ["studio_google_gmail_search", "studio_google_calendar_events", "studio_google_drive_search"]],
    ],
}}
cases = 0
with tempfile.TemporaryDirectory(prefix=".synthetic-proof-test-", dir=reports) as directory:
    status_path, native_path, dispatch_path = (Path(directory) / name for name in ("status.json", "native.json", "dispatch.json"))

    def check(label, change=lambda _s, _n: None, expected_exit=1, extra_args=None,
              recovery=False, original_change=lambda _o: None, include_dispatch=True):
        global cases
        test_status, test_native = deepcopy(status), deepcopy(native)
        if recovery:
            original = deepcopy(native)
            original["failure"] = "studio_rpc_timeout"
            original["native"].update(dispatched=False, success=False, runStatus="running", toolResults=[], googleToolCalls=0)
            original_change(original)
            dispatch_path.write_text(json.dumps(original))
            test_native.update(phase="inspect", nativeTurnsRequested=0,
                               dispatchReceiptSha256=hashlib.sha256(dispatch_path.read_bytes()).hexdigest())
            test_native["native"].update(dispatched=False, resumedReceipt=True)
        change(test_status, test_native)
        status_path.write_text(json.dumps(test_status))
        native_path.write_text(json.dumps(test_native))
        result = subprocess.run([
            sys.executable, "-B", str(reports / "verify-real-google.py"), str(status_path), str(native_path),
            *(extra_args if extra_args is not None else ["--expected-version", "1.0.8", "--expected-source", fake_source]),
            *(["--dispatch-receipt", str(dispatch_path)] if recovery and include_dispatch else []),
        ], text=True, capture_output=True, timeout=10)
        assert result.returncode == expected_exit, f"Unexpected validator exit for {label}: {result.returncode}"
        if expected_exit == 0:
            proof = json.loads(result.stdout)
            assert proof["version"] == test_native["serverVersion"]
            assert proof["sourceCommit"] == test_native["serverSourceCommit"]
            assert proof["proofPhase"] == test_native["phase"]
            assert proof["dispatchReceiptSha256"] == test_native.get("dispatchReceiptSha256")
        cases += 1

    check("synthetic complete proof", expected_exit=0)
    check("missing explicit release", extra_args=[], expected_exit=2)
    check("partial expected source", extra_args=["--expected-version", "1.0.8", "--expected-source", "aaaa"])
    check("missing observed source", lambda s, n: s.pop("serverSourceCommit"))
    check("status source mismatch", lambda s, n: s.update(serverSourceCommit="b" * 40))
    check("native source mismatch", lambda s, n: n.update(serverSourceCommit="b" * 40))
    check("version mismatch", lambda s, n: n.update(serverVersion="1.0.7"))
    check("native failure", lambda s, n: n.update(failure="native_verification_incomplete"))
    check("missing service grant", lambda s, n: n["google"].update(aideAccess=["gmail"]))
    check("missing Google tool", lambda s, n: n["native"]["toolResults"].pop())
    check("extra dynamic tool", lambda s, n: n["native"].update(additionalDynamicTools=1))
    check("delegation", lambda s, n: n["native"].update(delegationItems=1))
    check("unrevoked owned auth", lambda s, n: n["cleanup"].update(ownedSessionRevoked=False))
    check("content limit", lambda s, n: n["native"]["toolResults"][1].update(itemCount=2))
    check("extra native tool", lambda s, n: n["native"].update(additionalNativeTools=1))
    check("missing native tool count", lambda s, n: n["native"].pop("additionalNativeTools"))
    check("false native tool count", lambda s, n: n["native"].update(additionalNativeTools=False))
    check("health after reads", lambda s, n: n["native"].update(healthBeforeReads=False))
    check("missing health order", lambda s, n: n["native"].pop("healthBeforeReads"))
    check("unbound native source", lambda s, n: n["native"].update(dispatchBoundToSource=False))
    check("missing native source binding", lambda s, n: n["native"].pop("dispatchBoundToSource"))
    check("native receipt reused old run", lambda s, n: n["native"].update(resumedReceipt=True))
    check("fresh native missing dispatch time", lambda s, n: n["native"].pop("dispatchAttemptedAt"))
    check("fresh native not dispatched", lambda s, n: n["native"].update(dispatched=False))
    check("valid inspect recovery from original timeout", recovery=True, expected_exit=0)
    check("inspect missing dispatch argument", recovery=True, include_dispatch=False)
    check("inspect wrong dispatch hash", lambda s, n: n.update(dispatchReceiptSha256="b" * 64), recovery=True)
    check("inspect missing dispatch hash", lambda s, n: n.pop("dispatchReceiptSha256"), recovery=True)
    check("inspect requests a turn", lambda s, n: n.update(nativeTurnsRequested=1), recovery=True)
    check("inspect dispatches", lambda s, n: n["native"].update(dispatched=True), recovery=True)
    check("inspect incomplete result", lambda s, n: n["native"].update(success=False, runStatus="running"), recovery=True)
    check("inspect original source mismatch", recovery=True, original_change=lambda o: o.update(serverSourceCommit="b" * 40))
    check("inspect original version mismatch", recovery=True, original_change=lambda o: o.update(serverVersion="1.0.7"))
    check("inspect original host mismatch", recovery=True, original_change=lambda o: o.update(origin="http://127.0.0.1:8320"))
    check("inspect original base directory mismatch", recovery=True, original_change=lambda o: o.update(baseDir="/other-synthetic"))
    check("inspect original project mismatch", recovery=True, original_change=lambda o: o.update(projectId="another-project"))
    check("inspect original command mismatch", recovery=True, original_change=lambda o: o["native"].update(commandId="other-command"))
    check("inspect original thread mismatch", recovery=True, original_change=lambda o: o["native"].update(threadId="other-thread"))
    check("inspect original phase wrong", recovery=True, original_change=lambda o: o.update(phase="inspect"))
    check("inspect original turn count wrong", recovery=True, original_change=lambda o: o.update(nativeTurnsRequested=0))
    check("inspect original dispatch time missing", recovery=True, original_change=lambda o: o["native"].pop("dispatchAttemptedAt"))
    check("inspect original dispatch time invalid", recovery=True, original_change=lambda o: o["native"].update(dispatchAttemptedAt="invalid"))
    check("inspect original auth not revoked", recovery=True, original_change=lambda o: o["cleanup"].update(ownedSessionRevoked=False))
    check("inspect original auth cleanup failure", recovery=True, original_change=lambda o: o["cleanup"].update(failure="owned_session_cleanup_failed"))
    check("inspect original source unbound", recovery=True, original_change=lambda o: o["native"].update(dispatchBoundToSource=False))
    check("inspect original reuses run", recovery=True, original_change=lambda o: o["native"].update(resumedReceipt=True))

print(json.dumps({"offlineSyntheticCasesPassed": cases, "liveCalls": 0, "realGoogleProof": False}))
