#!/usr/bin/env python3
"""Offline synthetic checks of the receipt validator; never live Google proof."""
from copy import deepcopy
from datetime import datetime, timezone
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
    status_path, native_path = (Path(directory) / name for name in ("status.json", "native.json"))

    def check(label, change=lambda _s, _n: None, expected_exit=1, extra_args=None):
        global cases
        test_status, test_native = deepcopy(status), deepcopy(native)
        change(test_status, test_native)
        status_path.write_text(json.dumps(test_status))
        native_path.write_text(json.dumps(test_native))
        result = subprocess.run([
            sys.executable, "-B", str(reports / "verify-real-google.py"), str(status_path), str(native_path),
            *(extra_args if extra_args is not None else ["--expected-version", "1.0.8", "--expected-source", fake_source]),
        ], text=True, capture_output=True, timeout=10)
        assert result.returncode == expected_exit, f"Unexpected validator exit for {label}: {result.returncode}"
        if expected_exit == 0:
            proof = json.loads(result.stdout)
            assert proof["version"] == test_native["serverVersion"]
            assert proof["sourceCommit"] == test_native["serverSourceCommit"]
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

print(json.dumps({"offlineSyntheticCasesPassed": cases, "liveCalls": 0, "realGoogleProof": False}))
