"""Invented review envelopes exercising actual observed product regressions."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import test_product_handoff_evidence as fixtures


class DestinationRegressionReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="invented-r3-review-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.index = fixtures.invented_evidence(self.root)
        fixtures.invented_release_evidence(self.root, self.index)
        self.review = self.read(self.index["review"])

    def read(self, reference):
        return json.loads((self.root / reference["path"]).read_bytes())

    def save(self):
        self.index["review"] = fixtures.ref(self.root, self.index["review"]["path"], self.review)
        (self.root / "product-evidence-index.json").write_bytes(fixtures.encode(self.index))

    def reject(self, message):
        self.save()
        with self.assertRaisesRegex(ValueError, message):
            fixtures.V.product_review(self.root)

    def replace_report(self, report):
        reference = fixtures.ref(self.root, "synthetic-vitest-report.json", report)
        code = self.read(self.index["code"])
        commands = {}
        for check in code["checks"]:
            if "testReport" in check:
                record = self.read(check["command"])
                record["testReport"] = reference
                check["command"] = fixtures.ref(self.root, check["command"]["path"], record)
                commands[check["command"]["path"]] = check["command"]
                check["testReport"] = reference
        self.index["code"] = fixtures.ref(self.root, self.index["code"]["path"], code)
        for case in self.review["cases"].values():
            case["testReport"] = reference
            case["command"] = commands[case["command"]["path"]]

    def test_eleven_case_fixture_binds_identity_sidebar_and_local_preview(self):
        self.assertEqual(len(self.review["cases"]), 11)
        self.save()
        fixtures.V.product_review(self.root)

    def test_each_new_case_is_required(self):
        baseline = copy.deepcopy(self.review)
        for label in fixtures.V.DESTINATION_REGRESSIONS:
            with self.subTest(label=label):
                self.review = copy.deepcopy(baseline)
                del self.review["cases"][label]
                self.reject("missing adversarial review case")

    def test_unrelated_passing_assertion_in_same_suite_cannot_substitute(self):
        baseline = copy.deepcopy(self.review)
        for label in fixtures.V.DESTINATION_REGRESSIONS:
            with self.subTest(label=label):
                self.review = copy.deepcopy(baseline)
                self.review["cases"][label]["assertion"] = "unrelated synthetic " + label
                self.reject("destination review case names an unrelated regression")

    def test_origin_alone_or_duplicate_origin_cannot_substitute_for_upstream(self):
        case = self.review["cases"]["partial-clone-identity"]
        for additional in ([], [case["assertion"]], ["unrelated synthetic partial-clone-identity"],
                           list(fixtures.V.PARTIAL_CLONE_REGRESSIONS)):
            with self.subTest(additional=additional):
                case["additionalAssertions"] = additional
                self.reject("partial clone review needs the exact upstream witness")

    def test_additional_assertions_are_actual_names_not_status_or_summary(self):
        case = self.review["cases"]["partial-clone-identity"]
        for additional in (True, "passed", [None], [{"status": "passed"}]):
            with self.subTest(additional=additional):
                case["additionalAssertions"] = additional
                self.reject("additional review assertions must name actual tests")

    def test_exact_test_path_is_frozen_to_candidate_checkout(self):
        baseline = copy.deepcopy(self.review)
        for label in fixtures.V.DESTINATION_REGRESSIONS:
            with self.subTest(label=label):
                self.review = copy.deepcopy(baseline)
                self.review["cases"][label]["testPath"] = "/foreign/" + Path(
                    self.review["cases"][label]["testPath"]).name
                self.reject("actual frozen candidate suite")

    def test_upstream_witness_in_another_suite_does_not_count(self):
        report = self.read(self.review["cases"]["partial-clone-identity"]["testReport"])
        suite = next(s for s in report["testResults"] if s.get("name", "").endswith("RepositoryIdentityResolver.test.ts"))
        witness = next(a for a in suite["assertionResults"] if a["fullName"] == fixtures.V.PARTIAL_CLONE_REGRESSIONS[1])
        suite["assertionResults"].remove(witness)
        report["testResults"].append({"name": "/foreign/RepositoryIdentityResolver.test.ts", "assertionResults": [witness]})
        self.replace_report(report)
        self.reject("actual frozen candidate suite")

    def test_failed_upstream_cannot_hide_behind_passed_report_summary(self):
        report = self.read(self.review["cases"]["partial-clone-identity"]["testReport"])
        witness = next(a for s in report["testResults"] for a in s["assertionResults"]
                       if a["fullName"] == fixtures.V.PARTIAL_CLONE_REGRESSIONS[1])
        witness["status"] = "failed"
        self.replace_report(report)
        self.reject("failed|assertion")

    def test_sidebar_assertion_in_unrelated_report_is_not_the_executed_report(self):
        case = self.review["cases"]["sidebar-independent-destination"]
        case["testReport"] = fixtures.ref(self.root, "detached-report.json", self.read(case["testReport"]))
        self.reject("review test report detached from execution")

    def test_preview_witness_in_another_suite_does_not_count(self):
        case = self.review["cases"]["preview-no-lazy-fetch-preservation"]
        report = self.read(case["testReport"])
        suite = next(s for s in report["testResults"] if s.get("name") == case["testPath"])
        witness = next(a for a in suite["assertionResults"] if a["fullName"] == case["assertion"])
        suite["assertionResults"].remove(witness)
        report["testResults"].append({"name": "/foreign/preview.test.ts", "assertionResults": [witness]})
        self.replace_report(report)
        self.reject("actual frozen candidate suite")

    def test_failed_or_skipped_preview_cannot_hide_behind_passed_report_summary(self):
        case = self.review["cases"]["preview-no-lazy-fetch-preservation"]
        baseline = self.read(case["testReport"])
        for status in ("failed", "skipped", "pending"):
            with self.subTest(status=status):
                report = copy.deepcopy(baseline)
                witness = next(a for s in report["testResults"] for a in s["assertionResults"]
                               if a["fullName"] == case["assertion"])
                witness["status"] = status
                self.replace_report(report)
                self.reject("failed|assertion")

    def test_preview_report_must_be_from_its_retained_execution(self):
        case = self.review["cases"]["preview-no-lazy-fetch-preservation"]
        case["testReport"] = fixtures.ref(self.root, "detached-preview-report.json", self.read(case["testReport"]))
        self.reject("review test report detached from execution")

    def test_preview_command_cannot_be_relabelled_from_another_candidate(self):
        case = self.review["cases"]["preview-no-lazy-fetch-preservation"]
        command = self.read(case["command"])
        command["candidateCommit"] = "f" * 40
        replacement = fixtures.ref(self.root, case["command"]["path"], command)
        code = self.read(self.index["code"])
        for check in code["checks"]:
            if check["command"]["path"] == replacement["path"]:
                check["command"] = replacement
        self.index["code"] = fixtures.ref(self.root, self.index["code"]["path"], code)
        case["command"] = replacement
        self.reject("wrong product candidate")
