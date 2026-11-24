"""Invented offline launch traces only; never operational release evidence."""
import unittest

import test_product_handoff_evidence as fixtures

V, encode, ref = fixtures.V, fixtures.encode, fixtures.ref


class ObservedBuilderLaunchTests(unittest.TestCase):
    setUp = fixtures.ProductReleaseEvidenceTests.setUp
    read = fixtures.ProductReleaseEvidenceTests.read
    replace = fixtures.ProductReleaseEvidenceTests.replace

    def fixture(self):
        evidence, reference, command, source = fixtures.ProductReleaseEvidenceTests.retained_desktop_builder(self)
        owner = self.read(command["ownerReceipt"])
        prepared = {"state": "unbound", "changes": {"build-final.mjs": {"sha256": command["builderSource"]["sha256"]}}}
        command["builderPreparation"] = ref(self.root, "untimed-preparation.json", prepared)
        review = {"filesSha256": {"build-final.mjs": command["builderSource"]["sha256"]},
                  "preparationSha256": command["builderPreparation"]["sha256"],
                  "verdict": "SHIP for r2 binding/build", "reviewedAt": command["finishedAt"]}
        binding = {"schemaVersion": 1, "sourceCommit": evidence.candidate["sourceCommit"], "repoRoot": source,
                   "stage": owner["stage"], "node22": command["argv"][0], "version": "1.0.10",
                   "boundAt": "2026-10-12T00:00:00Z", "buildReceipt": "/synthetic/evidence/build.json"}
        start, end = (int(V.time_value(command[field]).timestamp() * 1000) for field in ("startedAt", "finishedAt"))
        event = {"type": "event_msg", "timestamp": command["finishedAt"], "payload": {
            "type": "item_completed", "thread_id": "synthetic-thread", "turn_id": "synthetic-turn",
            "started_at_ms": start, "completed_at_ms": end, "item": {"type": "CommandExecution",
                "id": "synthetic-item", "process_id": "123", "source": "unified_exec_startup",
                "status": "completed", "exit_code": 0, "cwd": "file:///synthetic/evidence",
                "command": ["/bin/zsh", "-lc", command["argv"][0] + " build-final.mjs"],
                "aggregated_output": encode(owner).decode()}}}
        command.update(invocationProvenance="derived-from-observed-builder-launch",
                       builderReview=ref(self.root, "builder-review.json", review),
                       builderSourceBinding=ref(self.root, "source-binding.json", binding),
                       builderLaunch=ref(self.root, "actual-launch.json", event))
        self.replace(reference, command)
        return evidence, reference, command, source

    def mutate(self, field, change):
        evidence, reference, command, source = self.fixture()
        data = self.read(command[field])
        change(data)
        self.replace(command[field], data)
        self.replace(reference, command)
        with self.assertRaises((ValueError, KeyError)):
            V.candidate_command(evidence, reference, "build", source)

    def test_real_shape_can_bind_untimed_preparation_without_invented_freeze(self):
        evidence, reference, _, source = self.fixture()
        V.candidate_command(evidence, reference, "build", source)

    def test_later_source_binding_is_rejected(self):
        self.mutate("builderSourceBinding", lambda d: d.update(boundAt="2027-01-01T00:00:00Z"))

    def test_other_source_binding_is_rejected(self):
        self.mutate("builderSourceBinding", lambda d: d.update(sourceCommit="a" * 40))

    def test_reviewed_creator_hash_cannot_be_substituted(self):
        self.mutate("builderReview", lambda d: d["filesSha256"].update({"build-final.mjs": "a" * 64}))

    def test_unknown_review_verdict_is_rejected(self):
        self.mutate("builderReview", lambda d: d.update(verdict="pending"))

    def test_failed_actual_wrapper_is_rejected(self):
        self.mutate("builderLaunch", lambda d: d["payload"]["item"].update(exit_code=1))

    def test_invented_wrapper_output_is_rejected(self):
        self.mutate("builderLaunch", lambda d: d["payload"]["item"].update(aggregated_output='{"exitCode":0}'))

    def test_wrong_launch_working_directory_is_rejected(self):
        self.mutate("builderLaunch", lambda d: d["payload"]["item"].update(cwd="file:///different"))

    def test_echo_wrapper_is_rejected(self):
        self.mutate("builderLaunch", lambda d: d["payload"]["item"].update(command=["/bin/zsh", "-lc", "echo build-final.mjs"]))

    def test_unrelated_execution_interval_is_rejected(self):
        self.mutate("builderLaunch", lambda d: d["payload"].update(started_at_ms=d["payload"]["completed_at_ms"] + 1))

    def test_missing_actual_launch_is_rejected(self):
        evidence, reference, command, source = self.fixture()
        del command["builderLaunch"]
        self.replace(reference, command)
        with self.assertRaises(KeyError):
            V.candidate_command(evidence, reference, "build", source)
