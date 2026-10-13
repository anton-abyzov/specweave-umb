#!/usr/bin/env python3
"""Validate private operational receipts without loading environment secrets."""
import argparse
import hashlib
import json
from pathlib import Path

PROJECTS = ("sw-easychamp", "jobweave", "specweave")


def read(root, name):
    return json.loads((root / name).read_text())


def audit(root):
    source = read(root, "m4-current-work-audit.json")
    assert source["readOnly"] is True
    assert source["cliVersion"] == source["npmStableVersion"]
    for host in ("m1", "m3"):
        repos = read(root, f"{host}-clone-type-audit.json")["repositories"]
        assert len(repos) == 46
        for repo in repos:
            assert repo["clean"] and repo["isShallow"] == "false"
            assert repo["independentDotGitDirectory"] and not repo["objectAlternatesExists"]
    reuse = read(root, "m1-original-easychamp-reuse-audit.json")
    assert reuse["readOnly"] is True


def cycle(root, name):
    receipt = read(root, name)
    assert receipt["status"] == "passed", name
    assert receipt["temporarySessionRevoked"] is True
    assert len(receipt["observedRuns"]) == 3
    assert all(r["status"] == "completed" for r in receipt["observedRuns"])
    assert receipt["finalSourceState"] == receipt["baseline"]
    assert all(r["status"] == "" for r in receipt["baseline"])
    for state in receipt["quiescence"]:
        assert all(not value for key, value in state.items() if key != "threadId")
    outcome = receipt["outcome"]
    assert outcome["automaticWakeRunId"]
    assert outcome["completionState"] in ("acknowledged", "delivered")
    for field in ("workerText", "relayText"):
        text = outcome[field]
        assert receipt["marker"] in text and receipt["decision"] in text
        assert all(source["sha"] in text for source in receipt["baseline"])
    return receipt


def handoff(root):
    for project in PROJECTS:
        source = cycle(root, f"m4-{project}-source.json")
        assert source["mode"] == "source" and source["host"] == "m4"
        expected_context = hashlib.sha256(source["outcome"]["relayText"].encode()).hexdigest()
        children = {source["outcome"]["workerThreadId"]}
        for host in ("m1", "m3"):
            target = cycle(root, f"{host}-{project}-destination.json")
            assert target["host"] == host and target["mode"] == "destination"
            assert target["sourceCheckpointSha256"] == expected_context
            assert target["marker"] == source["marker"]
            assert target["baseline"][1]["sha"] == source["baseline"][1]["sha"]
            assert target["outcome"]["workerThreadId"] not in children
            children.add(target["outcome"]["workerThreadId"])
            assert target["packageInspection"]["verified"] is True


def environment(root):
    # The private aggregate is authored only from per-host copy/start/readback receipts.
    report = read(root, "local-development-verification.json")
    assert report["status"] == "passed"
    assert set(report["hosts"]) == {"m1", "m3"}
    for host in report["hosts"].values():
        assert host["sourceUnchanged"] is True
        assert host["configurationVerified"] is True
        assert set(host["projects"]) == set(PROJECTS)
        assert all(p["status"] == "passed" for p in host["projects"].values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("audit", "handoff", "environment", "all"), required=True)
    parser.add_argument("--evidence", type=Path, default=Path.home() / ".local/share/specweave/fleet/handoff-proof-20261013")
    args = parser.parse_args()
    phases = {"audit": audit, "handoff": handoff, "environment": environment}
    for name, check in phases.items():
        if args.phase in (name, "all"):
            check(args.evidence)
            print(f"{name}: passed")
