"""Explicit final-route Git configuration interval; no host reads or writes.

Historical native source replay and the checkpoint replay remain in the caller.
Only Git configuration is projected out of the historical code bridge. Every
field is compared across the fresh interval, and the old failure stays failed.
"""
import datetime
from pathlib import PurePosixPath
import re

PROJECTS = ("sw-easychamp", "jobweave", "specweave")
HOSTS = ("m1", "m3")
HASH = re.compile(r"[a-f0-9]{64}\Z")
COMMIT = re.compile(r"[a-f0-9]{40}\Z")
def snapshot_descriptor(kind, label="final-candidate"):
    return (label + "-source-" + kind + "-native-ui",
            "Fresh actual source Git and project configuration snapshot " + kind + " " + label
            + " native UI; not a historical diagnostic baseline")


def require(value, message):
    if not value:
        raise ValueError("Git configuration interval: " + message)


def exact(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), label + " schema")


def timestamp(value):
    require(isinstance(value, str), "timestamp missing")
    parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None, "timestamp requires timezone")
    return parsed


def absolute(value):
    require(isinstance(value, str) and value, "path missing")
    path = PurePosixPath(value)
    require(path.is_absolute() and str(path) == value and ".." not in path.parts
            and not re.search(r"[\x00-\x1f]", value), "noncanonical path")
    return path


def rows_by_path(rows):
    require(isinstance(rows, list) and len(rows) >= 6, "complete row inventory required")
    required = [r for r in rows if r.get("kind") != "additional"]
    require(len(required) == 6 and {(r.get("projectKey"), r.get("kind")) for r in required}
            == {(p, k) for p in PROJECTS for k in ("root", "nested")}, "six required checkouts")
    paths = [r["path"] for r in rows]
    require(len(set(paths)) == len(paths), "duplicate checkout path")
    for row in rows:
        path = absolute(row["path"])
        require(row["projectKey"] in PROJECTS and row["kind"] in ("root", "nested", "additional"), "checkout scope")
        require(isinstance(row["head"], str) and COMMIT.fullmatch(row["head"])
                and isinstance(row["branch"], str), "checkout head/branch")
        for key in ("gitConfigSha256", "statusSha256", "indexSha256"):
            require(isinstance(row[key], str) and HASH.fullmatch(row[key]), "whole serialized state hash")
        if row["kind"] == "additional":
            root = next(r["path"] for r in required if r["projectKey"] == row["projectKey"] and r["kind"] == "root")
            require(path.is_relative_to(absolute(root)), "additional checkout outside project")
    return {r["path"]: r for r in rows}


def snapshot(evidence, reference, kind):
    exact(reference, ("path", "sha256"), "snapshot reference")
    value = evidence.json(reference)
    common = {"version", "host", "scope", "startedAt", "observedAt", "rows"}
    exact(value, common if kind == "historical" else common | {
        "kind", "sourceCommit", "collectorSha256", "gitMetadata", "configFiles", "privateFiles"}, "raw snapshot")
    require(type(value["version"]) is int and value["version"] == 1 and value["host"] == "m4", "snapshot version/host")
    require(timestamp(value["startedAt"]) <= timestamp(value["observedAt"]), "snapshot timestamps reversed")
    rows = rows_by_path(value["rows"])
    if kind == "historical":
        require(value["scope"] == "owned-source-projects", "historical snapshot scope")
    else:
        descriptors = [snapshot_descriptor(kind)]
        # Preserve actual already-captured 1.0.13 bytes without relabelling them.
        if evidence.candidate["version"] == "1.0.13":
            descriptors.append(snapshot_descriptor(kind, "final113"))
        require((value["kind"], value["scope"]) in descriptors, "candidate snapshot kind/scope")
        require(value["sourceCommit"] == evidence.candidate["sourceCommit"], "snapshot candidate differs")
        require(isinstance(value["collectorSha256"], str) and HASH.fullmatch(value["collectorSha256"]), "collector hash missing")
        metadata = value["gitMetadata"]
        require(isinstance(metadata, list) and len(metadata) == len(rows)
                and {r["path"] for r in metadata} == set(rows), "Git metadata inventory differs")
        for row in metadata:
            exact(row, ("path", "status", "origin", "originSha256"), "Git metadata")
            require(isinstance(row["status"], str) and isinstance(row["origin"], str) and row["origin"]
                    and isinstance(row["originSha256"], str) and HASH.fullmatch(row["originSha256"]), "Git metadata incomplete")
        require(isinstance(value["configFiles"], list) and isinstance(value["privateFiles"], list), "configuration arrays missing")
    return value, rows


def code_rows(rows):
    # Never modify retained snapshots or omit another field.
    return [{key: value for key, value in row.items() if key != "gitConfigSha256"} for row in rows]


def native_run_times(native):
    require(native.get("status") == "passed" and native.get("temporarySessionRevoked") is True,
            "complete successful native receipt required")
    graph = native.get("workflowVersion") == 2
    require("workflowVersion" not in native or graph, "unsupported native workflow")
    workers = native["workers"] if graph else [native["worker"]]
    expected = native["outcome"]["workerThreadIds"] if graph else [native["outcome"]["workerThreadId"]]
    require(isinstance(workers, list) and workers and isinstance(expected, list)
            and len(set(expected)) == len(expected)
            and sorted(w["thread"]["id"] for w in workers) == sorted(expected), "complete native worker inventory required")
    times = []
    for projection in [native["parent"], *workers]:
        runs = projection["runs"]
        require(isinstance(runs, list) and runs, "native run inventory missing")
        for run in runs:
            start, finish = run["startedAt"], run["completedAt"]
            require(timestamp(start) <= timestamp(finish), "native run timestamps reversed")
            times.extend((start, finish))
    return times


def route_times(evidence):
    routes = evidence.index["handoff"]["routes"]
    require(isinstance(routes, list) and len(routes) == 6
            and {(r["key"], r["host"]) for r in routes} == {(p, h) for p in PROJECTS for h in HOSTS},
            "six distinct final routes required")
    times = []
    for route in routes:
        ui = evidence.bound(evidence.json(route["ui"]))
        actions = ui["actions"]
        require(isinstance(actions, list) and [a["action"] for a in actions]
                == ["open-handoff", "select-destination", "confirm-transfer"], "complete native UI actions required")
        for action in actions:
            require(timestamp(action["startedAt"]) <= timestamp(action["observedAt"]), "UI timestamps reversed")
            times.extend((action["startedAt"], action["observedAt"]))
        times.append(evidence.json(route["sourceRecord"])["bundle"]["createdAt"])
        times.extend(native_run_times(evidence.json(route["native"])))
    return times


def validate_interval(evidence, item, advances):
    exact(item, ("host", "before", "after", "beforeAt", "afterAt", "configBeforeAt", "configAfterAt",
                 "configFilesBefore", "configFilesAfter", "privateFilesBefore", "privateFilesAfter",
                 "gitConfigurationInterval"), "preservation record")
    require(item["host"] == "m4", "only M4 supports a scoped interval")
    interval = item["gitConfigurationInterval"]
    exact(interval, ("version", "kind", "candidateCommit", "historicalSourceBefore", "beforeSnapshot",
                     "afterSnapshot", "historicalComparison"), "interval")
    require(type(interval["version"]) is int and interval["version"] == 1
            and interval["kind"] == "final-candidate-routes-only", "unsupported version/kind")
    require(interval["candidateCommit"] == evidence.candidate["sourceCommit"], "candidate differs")
    old, old_rows = snapshot(evidence, interval["historicalSourceBefore"], "historical")
    before, before_rows = snapshot(evidence, interval["beforeSnapshot"], "before")
    after, after_rows = snapshot(evidence, interval["afterSnapshot"], "after")
    require(len({interval[k]["path"] for k in ("historicalSourceBefore", "beforeSnapshot", "afterSnapshot")}) == 3,
            "snapshot references reused")
    require(item["before"] == old["rows"] and item["beforeAt"] == old["observedAt"], "historical raw binding differs")
    require(item["after"] == after["rows"] and item["afterAt"] == after["startedAt"], "final raw binding differs")
    require(item["configBeforeAt"] == before["observedAt"]
            and item["configAfterAt"] == after["startedAt"], "configuration raw timestamps differ")
    require(set(old_rows) == set(before_rows) == set(after_rows), "snapshot checkout inventory differs")
    require(before["rows"] == after["rows"], "final candidate complete rows changed")
    for key in ("gitMetadata", "configFiles", "privateFiles", "collectorSha256"):
        require(before[key] == after[key], "final candidate " + key + " changed")
    require(item["configFilesBefore"] == before["configFiles"] and item["configFilesAfter"] == after["configFiles"]
            and item["privateFilesBefore"] == before["privateFiles"] and item["privateFilesAfter"] == after["privateFiles"],
            "raw project/private configuration differs")
    start, finish = timestamp(before["observedAt"]), timestamp(after["startedAt"])
    require(timestamp(old["observedAt"]) <= timestamp(before["startedAt"]) <= start <= finish,
            "candidate snapshot chronology")
    projected_old, projected_after = code_rows(old["rows"]), code_rows(after["rows"])
    require(set(advances) <= {"sw-easychamp"}, "foreign checkpoint advance")
    for key, advance in advances.items():
        prior, current = code_rows([advance["preservation"]["before"], advance["preservation"]["after"]])
        require(prior["projectKey"] == current["projectKey"] == key and prior["kind"] == current["kind"] == "root"
                and prior["path"] == current["path"], "checkpoint row scope")
        require(projected_old.count(prior) == 1 and projected_after.count(current) == 1, "checkpoint code rows differ")
        require(timestamp(old["observedAt"]) <= timestamp(advance["finishedAt"]) <= timestamp(before["startedAt"]),
                "checkpoint must finish before fresh capture")
        projected_after[projected_after.index(current)] = prior
    require(sorted(projected_old, key=lambda r: r["path"]) == sorted(projected_after, key=lambda r: r["path"]),
            "historical code/index/status continuity failed")
    differences = [{"path": path, "historicalSha256": old_rows[path]["gitConfigSha256"],
                    "currentSha256": before_rows[path]["gitConfigSha256"]} for path in sorted(old_rows)
                   if old_rows[path]["gitConfigSha256"] != before_rows[path]["gitConfigSha256"]]
    comparison = interval["historicalComparison"]
    exact(comparison, ("status", "scope", "cause", "differences", "retainedAudit"), "historical comparison")
    require(comparison["status"] == "failed" and comparison["scope"] == "historical-source-before-to-current-candidate-before"
            and comparison["cause"] == "unattributed" and differences and comparison["differences"] == differences,
            "historical failure or exact differences missing")
    exact(comparison["retainedAudit"], ("path", "sha256"), "historical audit reference")
    audit = evidence.json(comparison["retainedAudit"])
    require(audit["version"] == 1 and audit["kind"] == "final113-existing-preservation-reference-audit"
            and audit["status"] == "remote-baselines-identified-m4-interval-boundary-unresolved"
            and audit["historicalFailure"]["status"] == "failed original Git configuration comparison remains failed"
            and audit["historicalFailure"]["normalizationAllowed"] is False, "historical audit no longer records failure")
    origin = audit["m4"]["historicalSourceRowsBefore"]
    absolute(origin["path"])
    require(origin["sha256"] == interval["historicalSourceBefore"]["sha256"]
            and origin["observedAt"] == old["observedAt"], "historical audit snapshot binding differs")
    times = route_times(evidence)
    require(times and all(start <= timestamp(at) <= finish for at in times), "fresh interval does not bracket every final route")
    return {"status": "passed-final-candidate-interval-only", "candidateCommit": interval["candidateCommit"],
            "startedAt": before["observedAt"], "finishedAt": after["startedAt"],
            "beforeSnapshot": interval["beforeSnapshot"], "afterSnapshot": interval["afterSnapshot"],
            "historicalComparisonStatus": "failed", "historicalConfigurationDifferences": differences,
            "historicalAudit": comparison["retainedAudit"], "allTimeConfigurationPreservationClaimed": False}
