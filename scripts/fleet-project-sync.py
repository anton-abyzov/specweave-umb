#!/usr/bin/env python3
"""Provision pinned independent checkouts; never repair existing repositories.
Bundle/receipt modes validate saved evidence; they cannot prove fresh live state.
"""
import argparse
import ctypes
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from urllib.parse import urlsplit

class Refusal(Exception):
    pass

def require(condition, message):
    if not condition:
        raise Refusal(message)

def git(args, cwd=None):
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never", "GIT_OPTIONAL_LOCKS": "0"}
    try:
        result = subprocess.run(["git", "-c", "core.hooksPath=/dev/null", *args],
                                cwd=cwd, env=env, text=True, capture_output=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Refusal("Git invocation failed: " + type(error).__name__) from error
    # Do not echo Git diagnostics: a credential helper may include sensitive values.
    require(result.returncode == 0, "Git command failed: " + args[0])
    return result.stdout.strip()

def sha(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None

def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def safe_origin(value, local_test=False):
    require(isinstance(value, str) and value, "Origin must be a string")
    if local_test and pathlib.Path(value).is_absolute():
        return
    require(not re.search(r"[\s\x00-\x1f\x7f%]|gh[pousr]_|github_pat_|sk-|token=|password=",
                          value, re.I), "Unsafe origin or credential-shaped URL")
    scp = re.fullmatch(r"git@([A-Za-z0-9.-]+):([A-Za-z0-9_.\-/]+)", value)
    if scp:
        repo_path = scp.group(2)
    else:
        parsed = urlsplit(value)
        require(parsed.scheme in ("https", "ssh") and parsed.hostname
                and re.fullmatch(r"[A-Za-z0-9.-]+", parsed.hostname)
                and not parsed.query and not parsed.fragment and not parsed.password,
                "Only credential-free HTTPS or git SSH origins are allowed")
        require(parsed.username == ("git" if parsed.scheme == "ssh" else None),
                "Origin credentials are prohibited")
        require(parsed.port is None or 1 <= parsed.port <= 65535, "Invalid origin port")
        repo_path = parsed.path.lstrip("/")
    require(re.fullmatch(r"[A-Za-z0-9_.\-/]+", repo_path) is not None
            and all(p not in ("", ".", "..") for p in repo_path.split("/"))
            and not repo_path.startswith("-"), "Unsafe repository path")

def manifest_rows(document, local_test=False):
    require(document.get("version") == 1, "Manifest version must be 1")
    rows = document.get("repositories")
    require(isinstance(rows, list) and rows, "Manifest repositories must be nonempty")
    seen = set()
    for row in rows:
        fields = {"project", "relativePath", "origin", "branch", "sha"}
        require(isinstance(row, dict) and set(row) in (fields, fields | {"bundle", "bundleSha256"}),
                "Require project, relativePath, origin, branch, sha; optional bundle and bundleSha256 together")
        require(isinstance(row["project"], str) and re.fullmatch(r"[A-Za-z0-9_-]+", row["project"]),
                "Unsafe project name")
        rel = row["relativePath"]
        require(isinstance(rel, str) and re.fullmatch(r"[A-Za-z0-9_.\-/]+", rel)
                and all(p.casefold() not in ("", ".", "..", ".git") for p in rel.split("/"))
                and not rel.startswith("-"), "Unsafe relativePath")
        require(rel not in seen, "Duplicate destination")
        seen.add(rel)
        require(sha(row["sha"]), "Expected lowercase full SHA-1 commit")
        require(isinstance(row["branch"], str) and not row["branch"].startswith("-"), "Unsafe branch")
        git(["check-ref-format", "refs/heads/" + row["branch"]])
        safe_origin(row["origin"], local_test)
        if "bundle" in row:
            require(isinstance(row["bundle"], str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*\.bundle", row["bundle"])
                    and isinstance(row["bundleSha256"], str) and re.fullmatch(r"[0-9a-f]{64}", row["bundleSha256"]), "Unsafe bundle name or digest")
    return sorted(rows, key=lambda row: (len(pathlib.PurePosixPath(row["relativePath"]).parts), row["relativePath"]))

def destination(base, relative):
    target = base / relative
    cursor = base
    for part in pathlib.PurePosixPath(relative).parts:
        cursor /= part
        require(not cursor.is_symlink(), "Symlink in destination path")
        require(not cursor.exists() or cursor.is_dir(), "Non-directory in destination path")
    require(target.resolve().is_relative_to(base), "Destination escapes base")
    return target

def remote_sha(row):
    result = git(["ls-remote", "--exit-code", "--refs", "--", row["origin"], "refs/heads/" + row["branch"]])
    require(result == row["sha"] + "\trefs/heads/" + row["branch"], "Remote branch drift: manifest is no longer current")

def verify_checkout(target, row):
    require((target / ".git").is_dir() and not (target / ".git").is_symlink(),
            "Destination is not an independent Git checkout")
    require(git(["rev-parse", "--show-toplevel"], target) == str(target), "Repository root mismatch")
    require(git(["config", "--local", "--get", "remote.origin.url"], target) == row["origin"], "Origin mismatch")
    for operation in (["remote", "get-url", "--all", "origin"],
                      ["remote", "get-url", "--push", "--all", "origin"]):
        effective = git(operation, target).splitlines()
        require(len(effective) == 1 and same_repository(row["origin"], effective[0]),
                "Effective Git transport targets a different repository")
    require(git(["symbolic-ref", "--short", "HEAD"], target) == row["branch"], "Branch mismatch")
    require(git(["rev-parse", "HEAD"], target) == row["sha"], "Commit differs; preserve existing work")
    require(git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], target)
            == "origin/" + row["branch"], "Upstream is not the intended origin branch")
    require(git(["rev-parse", "@{upstream}"], target) == row["sha"]
            and git(["rev-parse", "refs/remotes/origin/" + row["branch"]], target) == row["sha"],
            "Upstream commit differs from manifest")
    require(git(["rev-list", "--left-right", "--count", "@{upstream}...HEAD"], target) == "0\t0",
            "Checkout has ahead/behind commits")
    require(not git(["status", "--porcelain=v1", "--untracked-files=all", "--ignore-submodules=none"], target),
            "Dirty checkout; preserve existing work")

def same_repository(canonical, effective):
    """Permit a credential-free GitHub HTTPS/SSH rewrite, never a new destination."""
    if canonical == effective:
        return True
    def github_identity(value):
        match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", value)
        if not match:
            return None
        owner, repo = match.groups()
        repo = repo[:-4] if repo.endswith(".git") else repo
        if owner in (".", "..") or repo in ("", ".", ".."):
            return None
        return owner.casefold(), repo.casefold()
    expected = github_identity(canonical)
    return expected is not None and expected == github_identity(effective)

def exclusive_rename(source, target):
    """Atomic no-replace publication; ordinary os.rename can overwrite an empty target."""
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        call, args = libc.renamex_np, (os.fsencode(source), os.fsencode(target), 4)
        call.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        call, args = libc.renameat2, (-100, os.fsencode(source), -100, os.fsencode(target), 1)
        call.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    else:
        raise Refusal("Atomic exclusive rename unavailable; staging retained")
    call.restype = ctypes.c_int
    if call(*args):
        raise Refusal("Exclusive publication failed; staging retained (errno %s)" % ctypes.get_errno())

def source_for(row, bundle_dir):
    if bundle_dir is None:
        remote_sha(row)
        return row["origin"]
    require("bundle" in row, "Offline mode requires bundle metadata for every repository")
    bundle = bundle_dir / row["bundle"]
    require(bundle.is_file() and not bundle.is_symlink(), "Bundle missing or symlinked")
    require(digest_file(bundle) == row["bundleSha256"], "Bundle digest mismatch")
    heads = git(["bundle", "list-heads", str(bundle), "refs/heads/" + row["branch"]])
    require(heads == row["sha"] + " refs/heads/" + row["branch"], "Bundle branch or commit mismatch")
    return str(bundle)

def provision(base, row, apply, bundle_dir=None):
    result = {**row, "status": "failed"}
    try:
        target = destination(base, row["relativePath"])
        source = source_for(row, bundle_dir)
        if target.exists():
            verify_checkout(target, row)
            result["status"] = "already_verified"
        elif not apply:
            result["status"] = "missing"
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            destination(base, row["relativePath"])
            stage = pathlib.Path(tempfile.mkdtemp(prefix=".fleet-sync-", dir=target.parent))
            result["stagingPath"] = str(stage)
            git(["clone", "--depth=1", "--filter=blob:none", "--no-checkout", "--single-branch", "--branch",
                 row["branch"], "--", source, str(stage)])
            require(git(["rev-parse", "HEAD"], stage) == row["sha"], "Remote moved during clone; staging retained")
            if bundle_dir is not None:
                git(["remote", "set-url", "origin", row["origin"]], stage)
            git(["checkout", row["branch"]], stage)
            verify_checkout(stage, row)
            source_for(row, bundle_dir)
            destination(base, row["relativePath"])
            exclusive_rename(stage, target)
            result.pop("stagingPath")
            verify_checkout(target, row)
            result["status"] = "created_verified"
    except (Refusal, OSError, ValueError) as error:
        result["error"] = str(error)
    return result

def read_json(path):
    with open(path, encoding="utf-8") as stream:
        document = json.load(stream)
    require(isinstance(document, dict), "Expected JSON object")
    return document

def final_readback(base, results):
    for row in results:
        if row["status"] not in ("created_verified", "already_verified"):
            continue
        try:
            verify_checkout(destination(base, row["relativePath"]), row)
        except (Refusal, OSError, ValueError) as error:
            row.update(status="failed", error="Final readback: " + str(error))

def proof(value, thread=False):
    require(isinstance(value, dict) and value.get("status") == "succeeded", "Missing successful proof")
    if thread:
        require(isinstance(value.get("threadId"), str) and value["threadId"].strip(), "Missing native thread ID")
    path = pathlib.Path(value.get("evidencePath", ""))
    require(path.is_absolute() and path.is_file(), "Missing retained evidence file")
    require(digest_file(path) == value.get("evidenceSha256"), "Evidence digest mismatch")

def verify_runtime(document):
    require(document.get("version") == 1, "Receipt version must be 1")
    rows = document.get("projects", [])
    require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows), "Invalid project outcomes")
    expected = {(host, project) for host in ("M1", "M3") for project in ("sw-easychamp", "jobweave", "specweave")}
    require(len(rows) == 6 and {(r.get("host"), r.get("project")) for r in rows} == expected,
            "Require exactly six M1/M3 project outcomes")
    for row in rows:
        require(sha(row.get("expectedSha")) and row["expectedSha"] == row.get("actualSha")
                and row.get("clean") is True, "Runtime source mismatch or unclean checkout")
        proof(row.get("coordinator"), True)
        proof(row.get("worker"), True)
        require(row["coordinator"]["threadId"] != row["worker"]["threadId"], "Worker and coordinator IDs must differ")

def verify_release(document):
    require(document.get("version") == 1, "Receipt version must be 1")
    published, installed = document.get("published", {}), document.get("installed", [])
    require(isinstance(published, dict) and isinstance(installed, list)
            and all(isinstance(row, dict) for row in installed), "Invalid release outcomes")
    require(isinstance(published.get("version"), str) and re.fullmatch(r"\d+\.\d+\.\d+", published["version"])
            and sha(published.get("sourceSha")), "Missing exact published version/source")
    require(re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+/releases/tag/v" + re.escape(published["version"]),
                         published.get("url", "")), "Missing matching release URL")
    proof(published)
    require(len(installed) == 3 and {r.get("host") for r in installed} == {"M1", "M3", "M4"},
            "Require M1/M3/M4 installed readbacks")
    for row in installed:
        require((row.get("version"), row.get("sourceSha")) == (published["version"], published["sourceSha"]),
                "Installed version/source differs from published release")
        proof(row)

class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name).resolve()
        self.origin, self.base = self.root / "origin", self.root / "base"
        self.origin.mkdir(); self.base.mkdir()
        git(["init", "--initial-branch=main"], self.origin)
        git(["config", "user.email", "fixture@example.invalid"], self.origin)
        git(["config", "user.name", "Fixture"], self.origin)
        (self.origin / "file.txt").write_text("initial\n")
        git(["add", "file.txt"], self.origin)
        git(["commit", "-m", "fixture"], self.origin)
        self.row = dict(project="jobweave", relativePath="jobweave", origin=str(self.origin),
                        branch="main", sha=git(["rev-parse", "HEAD"], self.origin))

    def apply(self):
        return provision(self.base, self.row, True)

    def test_absent_and_idempotent(self):
        self.assertEqual(provision(self.base, self.row, False)["status"], "missing")
        self.assertEqual(self.apply()["status"], "created_verified")
        self.assertEqual(self.apply()["status"], "already_verified")

    def test_dirty_and_untracked_preserved(self):
        self.apply()
        target = self.base / "jobweave"
        (target / "file.txt").write_text("owner change\n")
        (target / "untracked.txt").write_text("owner asset\n")
        self.assertEqual(self.apply()["status"], "failed")
        self.assertEqual((target / "file.txt").read_text(), "owner change\n")
        self.assertEqual((target / "untracked.txt").read_text(), "owner asset\n")

    def test_unpushed_commit_preserved(self):
        self.apply()
        target = self.base / "jobweave"
        git(["-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture", "commit", "--allow-empty", "-m", "private"], target)
        before = git(["rev-parse", "HEAD"], target)
        self.assertEqual(self.apply()["status"], "failed")
        self.assertEqual(git(["rev-parse", "HEAD"], target), before)

    def test_remote_drift_preserves_old_checkout(self):
        self.apply()
        git(["commit", "--allow-empty", "-m", "new published"], self.origin)
        self.assertEqual(self.apply()["status"], "failed")
        self.assertEqual(git(["rev-parse", "HEAD"], self.base / "jobweave"), self.row["sha"])
        self.row["sha"] = git(["rev-parse", "HEAD"], self.origin)
        self.assertEqual(self.apply()["status"], "failed")

    def test_unsafe_paths_urls_and_symlinks(self):
        for value in ("../escape", "/absolute", "a/../../escape", "a/.git/b", "a/.GIT/b", "a/.GiT/b", "a//b"):
            with self.assertRaises(Refusal):
                manifest_rows({"version": 1, "repositories": [{**self.row, "relativePath": value}]}, True)
        for value in ("https://user:password@github.com/org/repo", "https://github.com/org/repo?token=x", "ext::bad"):
            with self.assertRaises(Refusal):
                safe_origin(value)
        (self.base / "jobweave").symlink_to(self.origin)
        self.assertEqual(self.apply()["status"], "failed")

    def test_existing_empty_and_atomic_race_preserved(self):
        (self.base / "jobweave").mkdir()
        self.assertEqual(self.apply()["status"], "failed")
        stage = self.base / "staging"
        stage.mkdir()
        with self.assertRaises(Refusal):
            exclusive_rename(stage, self.base / "jobweave")
        self.assertTrue(stage.exists())

    def test_final_readback_detects_descendant_and_staging(self):
        parent = self.apply()
        child = {**self.row, "relativePath": "jobweave/nested"}
        nested = provision(self.base, child, True)
        self.assertEqual(nested["status"], "created_verified")
        final_readback(self.base, [parent, nested])
        self.assertEqual(parent["status"], "failed")
        self.assertEqual(nested["status"], "created_verified")
        (self.base / "jobweave/nested/.fleet-sync-failed").mkdir()
        (self.base / "jobweave/nested/.fleet-sync-failed/data").write_text("retained")
        final_readback(self.base, [nested])
        self.assertEqual(nested["status"], "failed")

    def test_missing_or_diverged_upstream_is_preserved(self):
        self.apply()
        target = self.base / "jobweave"
        git(["branch", "--unset-upstream"], target)
        self.assertEqual(self.apply()["status"], "failed")
        git(["branch", "--set-upstream-to=origin/main"], target)
        other = git(["-c", "user.email=fixture@example.invalid", "-c", "user.name=Fixture",
                     "commit-tree", "HEAD^{tree}", "-p", "HEAD", "-m", "other upstream"], target)
        git(["update-ref", "refs/remotes/origin/main", other], target)
        self.assertEqual(self.apply()["status"], "failed")
        self.assertEqual(git(["rev-parse", "HEAD"], target), self.row["sha"])

    def test_incomplete_runtime_and_release_never_pass(self):
        for function in (verify_runtime, verify_release):
            with self.assertRaises(Refusal):
                function({"version": 1})

    def test_offline_bundle_and_bad_digest(self):
        bundle = self.root / "fixture.bundle"
        git(["bundle", "create", str(bundle), "--all"], self.origin)
        row = {**self.row, "origin": "https://github.com/fixture/absent.git", "bundle": bundle.name,
               "bundleSha256": hashlib.sha256(bundle.read_bytes()).hexdigest()}
        manifest_rows({"version": 1, "repositories": [row]})
        self.assertEqual(provision(self.base, row, True, self.root)["status"], "created_verified")
        self.assertEqual(provision(self.base, row, True, self.root)["status"], "already_verified")
        self.assertEqual(git(["rev-parse", "@{upstream}"], self.base / "jobweave"), row["sha"])
        self.assertEqual(provision(self.base, {**row, "bundleSha256": "0" * 64}, True, self.root)["status"], "failed")

    def test_scoped_transport_preserves_identity_and_rejects_redirects(self):
        self.apply()
        target = self.base / "jobweave"
        origin = "https://github.com/fixture/project.git"
        row = {**self.row, "origin": origin}
        git(["remote", "set-url", "origin", origin], target)
        key = "url.git@github.com:fixture/project.git.insteadOf"
        git(["config", "--local", key, origin], target)
        verify_checkout(target, row)
        self.assertEqual(git(["config", "--local", "--get", "remote.origin.url"], target), origin)
        git(["config", "--local", "remote.origin.pushurl", "git@github.com:foreign/project.git"], target)
        with self.assertRaises(Refusal):
            verify_checkout(target, row)
        git(["config", "--local", "--unset", "remote.origin.pushurl"], target)
        git(["config", "--local", "--unset", key], target)
        git(["config", "--local", "url.git@foreign.example:fixture/project.git.insteadOf", origin], target)
        with self.assertRaises(Refusal):
            verify_checkout(target, row)

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    for name in ("apply", "inspect", "verify-receipt", "verify-release"):
        mode.add_argument("--" + name, metavar="JSON")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--base")
    parser.add_argument("--bundle-dir", help="Use verified bundles instead of querying or cloning remote origins")
    parser.add_argument("--receipt", help="New receipt file; existing files are never overwritten")
    args = parser.parse_args()
    if args.self_test:
        return 0 if unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SafetyTests)).wasSuccessful() else 1
    try:
        if args.verify_receipt or args.verify_release:
            (verify_runtime if args.verify_receipt else verify_release)(read_json(args.verify_receipt or args.verify_release))
            print("Recorded evidence verified; this is not a fresh live probe.")
            return 0
        require(args.base and pathlib.Path(args.base).is_absolute(), "--base must be an existing absolute directory")
        base = pathlib.Path(args.base).resolve(strict=True)
        require(base.is_dir() and base != pathlib.Path("/"), "Unsafe base directory")
        require(not args.apply or args.receipt, "--apply requires a new --receipt file")
        rows = manifest_rows(read_json(args.apply or args.inspect))
        bundles = pathlib.Path(args.bundle_dir).resolve(strict=True) if args.bundle_dir else None
        require(bundles is None or bundles.is_dir(), "Bundle directory missing")
        receipt = None
        if args.receipt:
            receipt = os.fdopen(os.open(args.receipt, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w")
        try:
            results = []
            for row in rows:
                blocked = any(prior["status"] in ("failed", "missing")
                              and row["relativePath"].startswith(prior["relativePath"] + "/") for prior in results)
                results.append({**row, "status": "failed", "error": "Parent checkout not verified; descendant preserved"}
                               if blocked else provision(base, row, bool(args.apply), bundles))
            final_readback(base, results)
            output = {"version": 1, "at": datetime.now(timezone.utc).isoformat(), "base": str(base),
                      "sourceMode": "audited-offline-bundles" if bundles else "live-remote", "repositories": results}
            rendered = json.dumps(output, indent=2) + "\n"
            if receipt:
                receipt.write(rendered); receipt.flush(); os.fsync(receipt.fileno())
            print(rendered, end="")
            return int(any(row["status"] in ("failed", "missing") for row in results))
        finally:
            if receipt:
                receipt.close()
    except (Refusal, OSError, ValueError, TypeError, KeyError) as error:
        print("Refused: " + str(error), file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
