"""Synthetic scoped preservation only; never a real route or after observation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import test_product_handoff_evidence as f
import test_product_source_checkpoint_handoff_evidence as checkpoints

BEFORE_SCOPE = "Fresh actual source Git and project configuration snapshot before final-candidate native UI; not a historical diagnostic baseline"
AFTER_SCOPE = "Fresh actual source Git and project configuration snapshot after final-candidate native UI; not a historical diagnostic baseline"


class PreservationWindowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="synthetic-preservation-window-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.index = f.invented_evidence(self.root)
        self.item = self.read(self.index["handoff"]["preservation"][0])
        self.historical = {"version": 1, "host": "m4", "scope": "owned-source-projects",
            "startedAt": "2025-12-31T23:59:00Z", "observedAt": self.item["beforeAt"],
            "rows": copy.deepcopy(self.item["before"])}
        self.before = {"version": 1, "host": "m4", "kind": "final-candidate-source-before-native-ui",
            "scope": BEFORE_SCOPE, "sourceCommit": f.CANDIDATE["sourceCommit"], "collectorSha256": "f" * 64,
            "startedAt": "2026-10-13T12:01:20Z", "observedAt": "2026-10-13T12:01:30Z",
            "rows": copy.deepcopy(self.item["before"]), "gitMetadata": [],
            "configFiles": copy.deepcopy(self.item["configFilesBefore"]), "privateFiles": []}
        for row in self.before["rows"]:
            row["gitConfigSha256"] = f.V.digest(("changed historical config " + row["path"]).encode())
            self.before["gitMetadata"].append({"path": row["path"], "status": "",
                "origin": "https://example.invalid/synthetic.git", "originSha256": "b" * 64})
        self.after = copy.deepcopy(self.before)
        self.after.update(kind="final-candidate-source-after-native-ui", scope=AFTER_SCOPE,
                          startedAt="2026-10-13T12:08:00Z", observedAt="2026-10-13T12:08:01Z")
        self.item.update(after=copy.deepcopy(self.after["rows"]), afterAt=self.after["startedAt"],
                         configBeforeAt=self.before["observedAt"], configAfterAt=self.after["startedAt"])
        historical_ref = f.ref(self.root, "raw-historical.json", self.historical)
        self.audit = {"version": 1, "kind": "final113-existing-preservation-reference-audit",
            "status": "remote-baselines-identified-m4-interval-boundary-unresolved",
            "historicalFailure": {"status": "failed original Git configuration comparison remains failed", "normalizationAllowed": False},
            "m4": {"historicalSourceRowsBefore": {"path": "/synthetic/original-historical.json",
                "sha256": historical_ref["sha256"], "observedAt": self.historical["observedAt"]}}}
        self.item["gitConfigurationInterval"] = {"version": 1, "kind": "final-candidate-routes-only",
            "candidateCommit": f.CANDIDATE["sourceCommit"], "historicalSourceBefore": historical_ref,
            "beforeSnapshot": {}, "afterSnapshot": {}, "historicalComparison": {"status": "failed",
                "scope": "historical-source-before-to-current-candidate-before", "cause": "unattributed",
                "differences": self.differences(), "retainedAudit": {}}}
        self.advances = {}

    def read(self, reference):
        return json.loads((self.root / reference["path"]).read_bytes())

    def differences(self):
        current = {r["path"]: r for r in self.before["rows"]}
        return [{"path": r["path"], "historicalSha256": r["gitConfigSha256"],
                 "currentSha256": current[r["path"]]["gitConfigSha256"]}
                for r in sorted(self.historical["rows"], key=lambda r: r["path"])
                if r["gitConfigSha256"] != current[r["path"]]["gitConfigSha256"]]

    def sync(self):
        interval = self.item.get("gitConfigurationInterval")
        if interval is not None:
            for key, name, value in (("historicalSourceBefore", "raw-historical.json", self.historical),
                                     ("beforeSnapshot", "raw-before.json", self.before),
                                     ("afterSnapshot", "raw-after.json", self.after)):
                interval[key] = f.ref(self.root, name, value)
            interval["historicalComparison"]["retainedAudit"] = f.ref(self.root, "raw-audit.json", self.audit)
        self.index["handoff"]["preservation"][0] = f.ref(self.root, "m4-preservation.json", self.item)
        (self.root / "product-evidence-index.json").write_bytes(f.encode(self.index))
        return f.V.Evidence(self.root)

    def verify(self):
        evidence = self.sync()
        return f.V.preservation(evidence, self.index["handoff"]["preservation"], self.advances)

    def saved_state(self):
        return {"attrs": copy.deepcopy({k: getattr(self, k) for k in
                    ("index", "item", "historical", "before", "after", "audit", "advances")}),
                "files": {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}}

    def restore(self, state):
        for key, value in copy.deepcopy(state["attrs"]).items():
            setattr(self, key, value)
        for relative, value in state["files"].items():
            (self.root / relative).write_bytes(value)

    def change_reference(self, reference, mutate):
        value = self.read(reference)
        mutate(value)
        reference.update(f.ref(self.root, reference["path"], value))

    def test_full_synthetic_gate_keeps_historical_failure_and_validates_future_routes(self):
        originals = copy.deepcopy(self.historical)
        records = self.verify()
        result = records["m4"]["verifiedGitConfigurationInterval"]
        self.assertEqual(result["historicalComparisonStatus"], "failed")
        self.assertFalse(result["allTimeConfigurationPreservationClaimed"])
        self.assertEqual(len(result["historicalConfigurationDifferences"]), 6)
        self.assertEqual(self.historical, originals)
        self.assertEqual(f.V.product_handoff(self.root), {"gitConfigurationIntervals": [result]})

    def test_legacy_config_drift_still_fails_without_interval(self):
        del self.item["gitConfigurationInterval"]
        with self.assertRaisesRegex(ValueError, "an original checkout changed"):
            self.verify()

    def test_unknown_interval_schema_version_kind_candidate_scope_and_remote_host_fail(self):
        baseline = self.saved_state()
        mutations = [lambda x: x.update(version=2), lambda x: x.update(version=True),
                     lambda x: x.update(kind="all-time"), lambda x: x.update(candidateCommit="0" * 40),
                     lambda x: x.update(activityTimes=["2026-10-13T12:04:00Z"])]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                self.restore(baseline)
                mutate(self.item["gitConfigurationInterval"])
                with self.assertRaises(ValueError): self.verify()
        self.restore(baseline)
        self.item["activityTimes"] = ["2026-10-13T12:04:00Z"]
        with self.assertRaisesRegex(ValueError, "preservation record schema"): self.verify()
        self.restore(baseline)
        evidence = self.sync()
        remote_ref = self.index["handoff"]["preservation"][1]
        remote = self.read(remote_ref)
        remote["gitConfigurationInterval"] = self.item["gitConfigurationInterval"]
        remote_ref.update(f.ref(self.root, remote_ref["path"], remote))
        with self.assertRaisesRegex(ValueError, "only M4"):
            f.V.preservation(evidence, self.index["handoff"]["preservation"])

    def test_snapshot_schema_identity_and_raw_timestamp_binding_fail(self):
        baseline = self.saved_state()
        mutations = [lambda: self.before.update(extra=True), lambda: self.before.update(host="m1"),
                     lambda: self.before.update(version=True), lambda: self.before.update(sourceCommit="0" * 40),
                     lambda: self.before.update(kind="other"), lambda: self.before.update(scope="all-time"),
                     lambda: self.after.update(collectorSha256="0" * 64),
                     lambda: self.item.update(beforeAt="2026-10-13T12:01:30Z"),
                     lambda: self.item.update(afterAt="2027-01-01T00:00:00Z"),
                     lambda: self.item["before"][0].update(head="0" * 40),
                     lambda: self.after.update(observedAt="2026-10-13T12:07:59Z")]
        for number, mutate in enumerate(mutations):
            with self.subTest(number=number):
                self.restore(baseline)
                mutate()
                with self.assertRaises(ValueError): self.verify()

    def test_missing_symlinked_or_hash_changed_raw_file_is_not_a_snapshot(self):
        baseline = self.saved_state()
        for mode in ("missing", "symlink", "stale-hash"):
            with self.subTest(mode=mode):
                self.restore(baseline)
                evidence = self.sync()
                path = self.root / self.item["gitConfigurationInterval"]["beforeSnapshot"]["path"]
                data = path.read_bytes()
                path.unlink()
                if mode == "symlink":
                    (self.root / "elsewhere.json").write_bytes(data)
                    path.symlink_to(self.root / "elsewhere.json")
                elif mode == "stale-hash": path.write_bytes(data + b" ")
                with self.assertRaises(ValueError):
                    f.V.preservation(evidence, self.index["handoff"]["preservation"])
                if path.is_symlink(): path.unlink()

    def test_each_ui_bundle_parent_and_worker_timestamp_must_fit_fresh_window(self):
        baseline = self.saved_state()
        cases = [("ui", lambda d: d["actions"][0].update(startedAt="2026-10-13T12:01:29Z")),
                 ("ui", lambda d: d["actions"][-1].update(observedAt="2026-10-13T12:08:01Z")),
                 ("sourceRecord", lambda d: d["bundle"].update(createdAt="2026-10-13T12:01:29Z")),
                 ("native", lambda d: d["parent"]["runs"][0].update(startedAt="2026-10-13T12:01:29Z")),
                 ("native", lambda d: d["worker"]["runs"][0].update(completedAt="2026-10-13T12:08:01Z"))]
        for host_index in range(6):
            for field, mutate in cases:
                with self.subTest(route=host_index, field=field):
                    self.restore(baseline)
                    self.sync()
                    self.change_reference(self.index["handoff"]["routes"][host_index][field], mutate)
                    with self.assertRaisesRegex(ValueError, "does not bracket every final route"): self.verify()

    def test_later_before_completion_and_earlier_after_start_cannot_hide_work(self):
        self.before.update(observedAt="2026-10-13T12:02:01Z")
        self.item["configBeforeAt"] = self.before["observedAt"]
        with self.assertRaisesRegex(ValueError, "does not bracket every final route"): self.verify()
        self.before.update(observedAt="2026-10-13T12:01:30Z")
        self.item["configBeforeAt"] = self.before["observedAt"]
        self.after.update(startedAt="2026-10-13T12:06:59Z")
        self.item["afterAt"] = self.item["configAfterAt"] = self.after["startedAt"]
        with self.assertRaisesRegex(ValueError, "does not bracket every final route"): self.verify()

    def test_missing_route_action_worker_or_run_timestamp_is_not_abbreviated_proof(self):
        baseline = self.saved_state()
        for mode in ("route", "action", "worker-id", "worker-runs", "worker-start", "parent-finish"):
            with self.subTest(mode=mode):
                self.restore(baseline)
                self.sync()
                route = self.index["handoff"]["routes"][0]
                if mode == "route": self.index["handoff"]["routes"].pop()
                elif mode == "action": self.change_reference(route["ui"], lambda d: d["actions"].pop())
                else:
                    def mutate(d):
                        if mode == "worker-id": d["outcome"]["workerThreadId"] = "omitted-worker"
                        elif mode == "worker-runs": d["worker"]["runs"] = []
                        elif mode == "worker-start": del d["worker"]["runs"][0]["startedAt"]
                        else: del d["parent"]["runs"][0]["completedAt"]
                    self.change_reference(route["native"], mutate)
                with self.assertRaises((ValueError, KeyError, TypeError)): self.verify()

    def test_every_final_row_field_including_one_lfs_config_hash_must_stay_exact(self):
        baseline = self.saved_state()
        for row in range(6):
            for key, value in (("gitConfigSha256", f.V.digest(b"lfs.endpoint.access=basic\n")),
                               ("head", "0" * 40), ("branch", "foreign"), ("statusSha256", "1" * 64),
                               ("indexSha256", "2" * 64), ("extraRecordedIdentity", "changed")):
                with self.subTest(row=row, field=key):
                    self.restore(baseline)
                    self.after["rows"][row][key] = value
                    self.item["after"] = copy.deepcopy(self.after["rows"])
                    with self.assertRaisesRegex(ValueError, "complete rows changed"): self.verify()

    def test_duplicate_aliased_omitted_or_substituted_checkout_is_rejected(self):
        baseline = self.saved_state()
        for mode in ("duplicate", "alias", "omitted", "substituted"):
            with self.subTest(mode=mode):
                self.restore(baseline)
                if mode == "duplicate": self.after["rows"][1]["path"] = self.after["rows"][0]["path"]
                elif mode == "alias": self.after["rows"][1]["path"] += "/../other"
                elif mode == "omitted": self.after["rows"].pop()
                else: self.after["rows"][1]["path"] = "/synthetic/substituted"
                self.item["after"] = copy.deepcopy(self.after["rows"])
                with self.assertRaises(ValueError): self.verify()

    def test_additional_checkout_inventory_and_recorded_fields_remain_strict(self):
        row = dict(self.historical["rows"][0], kind="additional",
                   path=self.historical["rows"][0]["path"] + "/extra", recordedIdentity="same")
        for raw in (self.historical, self.before, self.after): raw["rows"].append(copy.deepcopy(row))
        for raw in (self.before, self.after):
            raw["gitMetadata"].append(dict(raw["gitMetadata"][0], path=row["path"]))
            raw["configFiles"].append({"path": row["path"] + "/.specweave/config.json", "exists": False})
        self.item.update(before=copy.deepcopy(self.historical["rows"]), after=copy.deepcopy(self.after["rows"]),
            configFilesBefore=copy.deepcopy(self.before["configFiles"]), configFilesAfter=copy.deepcopy(self.after["configFiles"]))
        self.audit["m4"]["historicalSourceRowsBefore"]["sha256"] = f.ref(self.root, "raw-historical.json", self.historical)["sha256"]
        self.verify()
        self.after["rows"][-1]["recordedIdentity"] = "changed"
        self.item["after"] = copy.deepcopy(self.after["rows"])
        with self.assertRaisesRegex(ValueError, "complete rows changed"): self.verify()

    def test_code_bridge_drops_only_git_config_and_requires_replayed_easy_advance(self):
        baseline = self.saved_state()
        for key, value in (("head", "1" * 40), ("branch", "other"), ("indexSha256", "2" * 64),
                           ("statusSha256", "3" * 64), ("extraRecordedField", True)):
            with self.subTest(field=key):
                self.restore(baseline)
                self.before["rows"][0][key] = value
                self.after["rows"][0][key] = value
                self.item["after"] = copy.deepcopy(self.after["rows"])
                with self.assertRaisesRegex(ValueError, "historical code/index/status continuity failed"): self.verify()

    def test_historical_failure_cannot_be_removed_passed_attributed_or_normalized(self):
        baseline = self.saved_state()
        for field, value in (("status", "passed"), ("cause", "LFS-safe"), ("scope", "all-time"),
                             ("differences", []), ("extra", "normalize")):
            with self.subTest(field=field):
                self.restore(baseline)
                self.item["gitConfigurationInterval"]["historicalComparison"][field] = value
                with self.assertRaises(ValueError): self.verify()
        for mode in ("omitted", "reversed", "changed"):
            self.restore(baseline)
            differences = self.item["gitConfigurationInterval"]["historicalComparison"]["differences"]
            if mode == "omitted": differences.pop()
            elif mode == "reversed": differences.reverse()
            else: differences[0]["historicalSha256"] = "0" * 64
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "exact differences missing"): self.verify()
        self.restore(baseline)
        self.audit["historicalFailure"]["normalizationAllowed"] = True
        with self.assertRaisesRegex(ValueError, "audit no longer records failure"): self.verify()

    def test_project_config_and_private_mode_existence_or_content_remain_guarded(self):
        baseline = self.saved_state()
        for field in ("configFilesAfter", "privateFilesAfter"):
            self.restore(baseline)
            self.item[field].append({"path": "/synthetic/foreign", "exists": True, "size": 1,
                                     "sha256": "a" * 64, "mode": "0600"})
            with self.subTest(field=field), self.assertRaises(ValueError): self.verify()
        for mutation in ({"exists": True}, {"mode": "0777"}, {"sha256": "c" * 64}):
            self.restore(baseline)
            self.after["configFiles"][0].update(mutation)
            self.item["configFilesAfter"] = copy.deepcopy(self.after["configFiles"])
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.verify()

    def test_source_native_config_drift_still_fails_separate_replay(self):
        self.sync()
        source = self.index["handoff"]["sources"][0]
        def mutate(native):
            native["after"]["repos"]["root"]["configSha256"] = "f" * 64
            f.rehash_native(native)
        self.change_reference(source["native"], mutate)
        self.sync()
        with self.assertRaisesRegex(ValueError, "native evidence replay failed"): f.V.product_handoff(self.root)

    def test_candidate_is_bound_from_index_and_legacy_snapshot_labels_are_version_scoped(self):
        # This synthetic source deliberately differs from both the real113 source
        # and the default test source; no production commit constant is accepted.
        self.index["candidate"] = dict(self.index["candidate"], sourceCommit="7" * 40, version="1.0.14")
        self.before["sourceCommit"] = self.after["sourceCommit"] = "7" * 40
        self.item["gitConfigurationInterval"]["candidateCommit"] = "7" * 40
        for route in self.index["handoff"]["routes"]:
            self.change_reference(route["ui"], lambda ui: ui.update(candidateCommit="7" * 40))
        self.verify()
        self.before["sourceCommit"] = "d" * 40
        with self.assertRaisesRegex(ValueError, "snapshot candidate differs"): self.verify()
        self.before["sourceCommit"] = "7" * 40
        for raw, phase in ((self.before, "before"), (self.after, "after")):
            raw["kind"] = "final113-source-" + phase + "-native-ui"
            raw["scope"] = raw["scope"].replace("final-candidate", "final113")
        with self.assertRaisesRegex(ValueError, "candidate snapshot kind/scope"): self.verify()
        self.index["candidate"]["version"] = "1.0.13"
        self.verify()

    def test_configuration_interval_cannot_copy_unbound_earlier_or_later_timestamps(self):
        baseline = self.saved_state()
        for field, time in (("configBeforeAt", "2020-01-01T00:00:00Z"),
                            ("configAfterAt", "2030-01-01T00:00:00Z")):
            with self.subTest(field=field):
                self.restore(baseline)
                self.item[field] = time
                with self.assertRaisesRegex(ValueError, "configuration raw timestamps differ"): self.verify()

    def test_complete_metadata_and_private_arrays_cannot_drift(self):
        baseline = self.saved_state()
        for field in ("status", "origin", "originSha256"):
            with self.subTest(field=field):
                self.restore(baseline)
                self.after["gitMetadata"][0][field] = "a" * 64 if field.endswith("Sha256") else "changed"
                with self.assertRaisesRegex(ValueError, "final candidate gitMetadata changed"): self.verify()
        self.restore(baseline)
        self.after["gitMetadata"][0]["extra"] = "cannot-hide-a-field"
        with self.assertRaisesRegex(ValueError, "Git metadata schema"): self.verify()
        self.restore(baseline)
        self.after["gitMetadata"].pop()
        with self.assertRaisesRegex(ValueError, "Git metadata inventory differs"): self.verify()

    def test_all_serial_graph_workers_and_all_coordinator_wakes_are_bracketed(self):
        route = self.index["handoff"]["routes"][0]
        def graph(native):
            native["workflowVersion"] = 2
            worker = native.pop("worker")
            native["workers"] = [copy.deepcopy(worker) for _ in range(3)]
            for i, child in enumerate(native["workers"]):
                child["thread"]["id"] = "synthetic-serial-worker-" + str(i)
                child["runs"][0]["startedAt"] = "2026-10-13T12:06:0" + str(i * 2) + "Z"
                child["runs"][0]["completedAt"] = "2026-10-13T12:06:0" + str(i * 2 + 1) + "Z"
            native["outcome"]["workerThreadIds"] = [w["thread"]["id"] for w in native["workers"]]
        self.change_reference(route["native"], graph)
        self.verify()  # Timestamp gate only; synthetic graph is not a replay pass.
        baseline = self.saved_state()
        for i in range(3):
            for field, time in (("startedAt", "2026-10-13T12:01:29Z"),
                                ("completedAt", "2026-10-13T12:08:01Z")):
                with self.subTest(worker=i, field=field):
                    self.restore(baseline)
                    self.change_reference(self.index["handoff"]["routes"][0]["native"],
                        lambda n: n["workers"][i]["runs"][0].update({field: time}))
                    with self.assertRaisesRegex(ValueError, "does not bracket every final route"): self.verify()
        self.restore(baseline)
        self.change_reference(self.index["handoff"]["routes"][0]["native"],
            lambda n: n["parent"]["runs"][-1].update(completedAt="2026-10-13T12:08:01Z"))
        with self.assertRaisesRegex(ValueError, "does not bracket every final route"): self.verify()

    def test_replayed_checkpoint_is_the_only_permitted_historical_code_advance(self):
        checkpoint = checkpoints.CheckpointTests()
        checkpoint.setUp()
        self.addCleanup(checkpoint.doCleanups)
        # Use the real unchanged Git-object/checkpoint replay, with synthetic
        # inputs, before passing its result to the preservation comparison.
        checkpoint.native["startedAt"] = "2026-10-13T12:00:00Z"
        checkpoint.entry["native"] = f.ref(checkpoint.root, "advance-source-native.json", checkpoint.native)
        checkpoint.advance["source"]["nativeSha256"] = checkpoint.entry["native"]["sha256"]
        checkpoint.advance["startedAt"] = "2026-10-13T12:01:10Z"
        checkpoint.advance["finishedAt"] = "2026-10-13T12:01:15Z"
        for side, second in (("before", 11), ("after", 13)):
            checkpoint.advance["tests"][side].update(
                startedAt="2026-10-13T12:01:" + str(second) + "Z",
                finishedAt="2026-10-13T12:01:" + str(second + 1) + "Z")
        advance = checkpoint.replay()
        prior, current = advance["preservation"]["before"], advance["preservation"]["after"]
        index = next(i for i, r in enumerate(self.historical["rows"])
                     if r["projectKey"] == "sw-easychamp" and r["kind"] == "root")
        old_path = self.historical["rows"][index]["path"]
        self.historical["rows"][index] = copy.deepcopy(prior)
        for raw in (self.before, self.after):
            raw["rows"][index] = dict(current, gitConfigSha256="9" * 64)
            next(r for r in raw["gitMetadata"] if r["path"] == old_path)["path"] = prior["path"]
            next(r for r in raw["configFiles"] if r["path"] == old_path + "/.specweave/config.json")["path"] = prior["path"] + "/.specweave/config.json"
        self.item.update(before=copy.deepcopy(self.historical["rows"]), after=copy.deepcopy(self.after["rows"]),
            configFilesBefore=copy.deepcopy(self.before["configFiles"]), configFilesAfter=copy.deepcopy(self.after["configFiles"]))
        self.item["gitConfigurationInterval"]["historicalComparison"]["differences"] = self.differences()
        self.audit["m4"]["historicalSourceRowsBefore"]["sha256"] = f.ref(self.root, "raw-historical.json", self.historical)["sha256"]
        self.advances = {"sw-easychamp": advance}
        self.verify()
        self.advances = {}
        with self.assertRaisesRegex(ValueError, "historical code/index/status continuity failed"): self.verify()
        self.advances = {"sw-easychamp": dict(advance, finishedAt=self.before["observedAt"])}
        with self.assertRaisesRegex(ValueError, "checkpoint must finish before fresh capture"): self.verify()

    def test_runtime_only_source_cannot_replace_native_bundle_proof(self):
        self.sync()
        route = self.index["handoff"]["routes"][0]
        runtime = self.read(route["sourceRuntime"])
        self.change_reference(runtime["clientReadback"], lambda c: c.update(delivery="http-service"))
        route["sourceRuntime"].update(f.ref(self.root, route["sourceRuntime"]["path"], runtime))
        self.sync()
        with self.assertRaisesRegex(ValueError, "native bundled client proof"): f.V.product_handoff(self.root)


if __name__ == "__main__":
    unittest.main()
