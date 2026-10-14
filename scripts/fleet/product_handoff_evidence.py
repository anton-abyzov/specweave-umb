"""Fail-closed product evidence gates; never starts software or changes hosts.

The private product-evidence-index.json (version 1) names a candidate and
SHA-256 references for code, review, release and handoff evidence. Every ref is
{path, sha256}, relative to the evidence directory. Handoff uses the product's
persisted source/destination records, not reconstructed RPC requests.

Native validation executes only the adjacent, reviewed replay runner. Neither
the index nor a receipt can choose executable validator code.
"""
import base64
import ast
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess

PROJECTS = ("sw-easychamp", "jobweave", "specweave")
HOSTS = ("m1", "m3")
REPOSITORIES = {"sw-easychamp": ("sw-easychamp", "ec-console-ui"),
                "jobweave": ("jobweave-umb", "jobweave"), "specweave": ("specweave-umb", "specweave")}
HEX40 = re.compile(r"[a-f0-9]{40}\Z")
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
UUID = re.compile(r"[a-f0-9]{8}-[a-f0-9]{4}-[1-8][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}\Z")
RUNNER = Path(__file__).with_name("replay_product_native.mjs")
HISTORY_RUNNER = Path(__file__).with_name("replay_source_history.mjs")
CHECKPOINT_RUNNER = Path(__file__).with_name("replay_source_checkpoint.mjs")
PROJECT_RUNTIME_REGRESSION = "launches with the project's approval mode instead of the host's full-access default"
PARTIAL_CLONE_REGRESSIONS = (
    "RepositoryIdentityResolverLive resolves a real local partial-clone with an annotated origin remote",
    "RepositoryIdentityResolverLive resolves a real local partial-clone with an annotated upstream remote")
SIDEBAR_DESTINATION_REGRESSION = "offers matching registered destinations even when sidebar grouping keeps the source separate"
PREVIEW_NO_LAZY_FETCH_REGRESSION = (
    "HandoffGit real repositories previews real promisor clones without fetching missing commits or changing Git state")
PREVIEW_CONTEXT_CONSENT_REGRESSION = (
    "previews without publishing, then rechecks the selected machine before one explicit transfer")
DESTINATION_REGRESSIONS = {
    "partial-clone-identity": ("apps/server/src/project/RepositoryIdentityResolver.test.ts", PARTIAL_CLONE_REGRESSIONS),
    "sidebar-independent-destination": ("apps/web/src/components/studio/ProjectMachineHandoff.test.tsx",
                                        (SIDEBAR_DESTINATION_REGRESSION,)),
    "preview-no-lazy-fetch-preservation": ("apps/server/src/fleet/handoffGit.test.ts",
                                          (PREVIEW_NO_LAZY_FETCH_REGRESSION,)),
    "preview-context-consent": ("apps/web/src/components/studio/ProjectMachineHandoff.test.tsx",
                                (PREVIEW_CONTEXT_CONSENT_REGRESSION,))}


def require(value, message):
    if not value:
        raise ValueError(message)


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "duplicate JSON key")
        obj[key] = value
    return obj


def decode(data):
    return json.loads(data, object_pairs_hook=unique_object,
                      parse_constant=lambda _: require(False, "nonfinite JSON number"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    # MachineHandoff.ts canonical(): fixed ASCII field names, UTF-8 strings,
    # array order retained, object keys sorted, no extra whitespace.
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                      sort_keys=True, allow_nan=False).encode()


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), label)
    return value


def absolute(value):
    text(value, "absolute path required")
    path = PurePosixPath(value)
    require(path.is_absolute() and str(path) == value and ".." not in path.parts
            and not re.search(r"[\x00-\x1f]", value), "noncanonical absolute path")
    return path


def time_value(value):
    result = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.tzinfo is not None, "timestamp requires timezone")
    return result


class Evidence:
    def __init__(self, root):
        self.root = Path(root).resolve()
        index = self.root / "product-evidence-index.json"
        require(index.is_file() and not index.is_symlink(), "product evidence index missing")
        self.index = decode(index.read_bytes())
        require(self.index["version"] == 1, "unsupported product evidence version")
        self.candidate = self.index["candidate"]
        require(HEX40.fullmatch(self.candidate["sourceCommit"]), "candidate commit required")
        require(re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?", self.candidate["version"]),
                "candidate version required")
        text(self.candidate["repository"], "candidate repository required")

    def path(self, ref):
        require(isinstance(ref, dict) and HEX64.fullmatch(ref["sha256"]), "SHA256 reference required")
        rel = PurePosixPath(ref["path"])
        require(not rel.is_absolute() and str(rel) == ref["path"] and rel.parts
                and not any(p in ("..", ".") for p in rel.parts), "unsafe evidence reference")
        path = self.root / str(rel)
        require(path.resolve().is_relative_to(self.root) and path.resolve() == path
                and path.is_file() and not path.is_symlink(), "regular evidence file required")
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(chunk)
        require(h.hexdigest() == ref["sha256"], "evidence hash mismatch: " + str(rel))
        return path

    def data(self, ref):
        path = self.path(ref)
        require(path.stat().st_size <= 32 * 1024 * 1024, "structured evidence too large")
        return path.read_bytes()

    def json(self, ref):
        return decode(self.data(ref))

    def bound(self, item):
        require(item["candidateCommit"] == self.candidate["sourceCommit"], "wrong product candidate")
        return item


def node22():
    candidates = [Path.home() / ".local/share/specweave/node22/bin/node",
                  Path.home() / ".nvm/versions/node/v22.20.0/bin/node"]
    found = shutil.which("node")
    if found:
        candidates.append(Path(found))
    env = dict(os.environ)
    env.pop("NODE_OPTIONS", None)
    for candidate in candidates:
        if candidate.is_file():
            version = subprocess.run([str(candidate), "--version"], capture_output=True,
                                     text=True, timeout=10, env=env)
            if version.returncode == 0 and version.stdout.strip().startswith("v22."):
                return str(candidate), env
    raise ValueError("Node 22 is required for the fixed offline native replay")


def replay(evidence, plan_ref, receipt_ref):
    plan_path, receipt_path = evidence.path(plan_ref), evidence.path(receipt_ref)
    plan, receipt = evidence.json(plan_ref), evidence.json(receipt_ref)
    require(receipt["status"] == "passed" and receipt["temporarySessionRevoked"] is True,
            "native supervision or temporary session cleanup incomplete")
    executable, env = node22()
    result = subprocess.run([executable, str(RUNNER), str(plan_path), str(receipt_path)],
                            capture_output=True, text=True, timeout=30, env=env)
    require(result.returncode == 0 and not result.stderr, "native evidence replay failed")
    report = decode(result.stdout)
    require(report == {"verified": True, "mode": plan["mode"], "projectId": plan["projectId"],
                       "operationId": plan.get("operationId")}, "unexpected native replay output")
    return plan, receipt


def source_context(evidence, entry, plan, native, route, bundle):
    carried = [thread["threadId"] for thread in bundle["context"]["threads"]]
    original = [plan["coordinatorId"]] + [task["childThreadId"] for task in native["rawParent"]["subagents"]
                                         if task["origin"] == "app_owned"]
    require(len(set(carried)) == len(carried), "duplicate carried source thread")
    if "sourceHistory" not in route:
        require(sorted(carried) == sorted(original), "expanded source history requires terminal supplement")
        return
    refs = [entry["plan"], entry["native"], route["sourceHistory"], route["sourceRecord"]]
    # Decode every hash-bound input with the same duplicate-key/size restrictions
    # before the fixed JS runner consumes the exact original bytes.
    for reference in refs:
        evidence.json(reference)
    paths = [str(evidence.path(reference)) for reference in refs]
    executable, env = node22()
    result = subprocess.run([executable, str(HISTORY_RUNNER), *paths],
                            capture_output=True, text=True, timeout=30, env=env)
    require(result.returncode == 0 and not result.stderr, "source terminal history replay failed")
    report = decode(result.stdout)
    require(set(report) == {"verified", "projectId", "originalSuccessfulWorkerId", "threadIds",
                            "historicalOnlyThreadIds"}
            and report["verified"] is True and report["projectId"] == plan["projectId"]
            and report["originalSuccessfulWorkerId"] == native["outcome"]["workerThreadId"]
            and sorted(report["threadIds"]) == sorted(carried)
            and sorted(report["historicalOnlyThreadIds"]) == sorted(set(carried) - set(original)),
            "unexpected source history replay output")


def source_checkpoint(evidence, entry, reference, source_record=None):
    refs = [entry["plan"], entry["native"], reference] + ([source_record] if source_record else [])
    for item in refs:
        evidence.json(item)
    executable, env = node22()
    result = subprocess.run([executable, str(CHECKPOINT_RUNNER),
                             *[str(evidence.path(item)) for item in refs]],
                            capture_output=True, text=True, timeout=30, env=env)
    require(result.returncode == 0 and not result.stderr, "source checkpoint advance replay failed")
    report = decode(result.stdout)
    require(set(report) == {"verified", "projectId", "originalShas", "newShas", "preservation", "finishedAt"}
            and report["verified"] is True
            and report["projectId"] == evidence.json(entry["plan"])["projectId"],
            "unexpected source checkpoint replay output")
    return report


def command(evidence, reference):
    item = evidence.bound(evidence.json(reference))
    require(isinstance(item["argv"], list) and item["argv"]
            and all(isinstance(word, str) and word for word in item["argv"]), "command argv required")
    absolute(item["cwd"])
    require(item["exitCode"] == 0, "product check failed")
    require(time_value(item["finishedAt"]) >= time_value(item["startedAt"]), "invalid command interval")
    if "combinedOutput" in item:
        require("stdout" not in item and "stderr" not in item, "combined output cannot claim separated streams")
        owner = evidence.json(item["ownerReceipt"])
        if item.get("invocationProvenance") == "retained-r3-source-execution":
            retained_source_execution(evidence, item, owner)
            return item, evidence.data(item["combinedOutput"]).decode(), ""
        if item.get("invocationProvenance") in ("derived-from-retained-builder", "derived-from-observed-builder-launch"):
            retained_builder(evidence, item, owner)
        else:
            require(owner["command"] == item["argv"] and owner["cwd"] == item["cwd"],
                    "adapted command differs from retained owner receipt")
        require(owner["source"] == item["candidateCommit"] and owner["exitCode"] == item["exitCode"]
                and owner["startedAt"] == item["startedAt"] and owner["completedAt"] == item["finishedAt"]
                and owner["sourceUnchanged"] is True and owner["log"] == item["combinedOutput"]["originPath"],
                "adapted command differs from retained owner receipt")
        output, error = evidence.data(item["combinedOutput"]).decode(), ""
    else:
        output = evidence.data(item["stdout"]).decode()
        error = evidence.data(item["stderr"]).decode()
    return item, output, error


def retained_source_execution(evidence, item, owner):
    """Bind observed endedAt/combined-log records without inventing snapshots."""
    proof = item["executionProof"]
    common = {"kind", "start", "completionOriginPath", "startOriginPath"}
    require(proof["kind"] in ("coverage-run", "native-typescript"), "unknown retained source execution")
    coverage = proof["kind"] == "coverage-run"
    require(set(proof) == common | ({"producer", "producerOriginPath"} if coverage else set()),
            "unexpected retained execution references")
    completed, started = absolute(proof["completionOriginPath"]), absolute(proof["startOriginPath"])
    require(completed.suffix == ".json" and started == completed.with_name(completed.stem + ".start.json")
            and item["combinedOutput"]["originPath"] == str(completed.with_suffix(".log")),
            "retained execution files do not share the actual invocation")
    start = evidence.json(proof["start"])
    header = ({"source", "sourceTree", "command", "cwd", "startedAt"} if coverage else
              {"sourceBefore", "command", "cwd", "startedAt", "compilerSha256", "qualification"})
    require(set(start) == header and all(owner.get(k) == v for k, v in start.items()),
            "completion differs from retained start")
    require(owner["command"] == item["argv"] and owner["cwd"] == item["cwd"]
            and owner["startedAt"] == item["startedAt"] and owner["endedAt"] == item["finishedAt"]
            and owner["exitCode"] == 0 and owner["sourceUnchanged"] is True,
            "retained source command or outcome differs")
    if coverage:
        require(set(owner) == header | {"endedAt", "exitCode", "sourceUnchanged", "tests", "passed",
                                      "failed", "suites", "coverage"}
                and owner["source"] == item["candidateCommit"] and HEX40.fullmatch(owner["sourceTree"]),
                "coverage candidate or raw shape differs")
        report = evidence.json(item["testReport"])
        require(owner["tests"] == owner["passed"] == report["numTotalTests"] == report["numPassedTests"]
                and owner["failed"] == report["numFailedTests"] == 0
                and owner["suites"] == report["numTotalTestSuites"], "coverage report detached from execution")
        producer_path = absolute(proof["producerOriginPath"])
        require(producer_path.parent == completed.parent, "coverage producer outside invocation directory")
        producer = ast.parse(evidence.data(proof["producer"]).decode())
        constants = {n.targets[0].id: n.value for n in producer.body if isinstance(n, ast.Assign)
                     and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}
        require(ast.literal_eval(constants["source"]) == item["candidateCommit"]
                and ast.dump(constants["p"]) == ast.dump(ast.parse("pathlib.Path(" + repr(item["cwd"]) + ")", mode="eval").body),
                "retained producer source or checkout differs")
        nodes = [ast.dump(node) for node in producer.body]
        required = ["assert git('rev-parse','HEAD')==source and not git('status','--porcelain')",
                    "write(" + repr(started.name) + ",rec)",
                    "with (r/" + repr(completed.with_suffix('.log').name) + ").open('x') as f: "
                    "result=subprocess.run(cmd,cwd=p,env=env,stdout=f,stderr=subprocess.STDOUT)",
                    "rec.update(endedAt=now(),exitCode=result.returncode,"
                    "sourceUnchanged=git('rev-parse','HEAD')==source and not git('status','--porcelain'))",
                    "write(" + repr(completed.name) + ",rec)"]
        expected = [ast.dump(ast.parse(code).body[0]) for code in required]
        require(all(nodes.count(node) == 1 for node in expected)
                and [nodes.index(node) for node in expected] == sorted(nodes.index(node) for node in expected),
                "retained producer lacks ordered top-level execution and observed outcome")
        output_flags = [a.split("=", 1)[1] for a in item["argv"] if a.startswith("--outputFile=")]
        require(len(output_flags) == 1 and absolute(output_flags[0]).parent == completed.parent,
                "coverage report output path differs")
        require(item["testReportOriginPath"] == output_flags[0], "coverage report origin differs")
    else:
        require(set(owner) == header | {"endedAt", "exitCode", "sourceUnchanged", "sourceAfter", "log", "logSha256"},
                "native TypeScript raw shape differs")
        before = owner["sourceBefore"]
        require(set(before) == {"source", "tree", "status"} and before == owner["sourceAfter"]
                and before["source"] == item["candidateCommit"] and before["status"] == ""
                and HEX40.fullmatch(before["tree"]), "native TypeScript source changed")
        executable = str(absolute(item["cwd"]) / "node_modules/.pnpm/@typescript+typescript-darwin-arm64@7.0.2/node_modules/@typescript/typescript-darwin-arm64/lib/tsc")
        require(item["argv"][0] == executable and item["argv"][1:] in
                (["--noEmit", "-p", "apps/server/tsconfig.json"], ["--noEmit", "-p", "apps/web/tsconfig.json"])
                and HEX64.fullmatch(owner["compilerSha256"]), "unexpected actual native TypeScript invocation")
        require("configured Effect" in owner["qualification"] and "non-green" in owner["qualification"],
                "configured checker qualification missing")
        require(owner["log"] == item["combinedOutput"]["originPath"]
                and owner["logSha256"] == item["combinedOutput"]["sha256"], "native TypeScript log differs")


def retained_builder(evidence, command, receipt):
    """Bind a legacy receipt to its pre-run frozen creator, without inventing
    an observed argv stream. Only this exact retained spawn form is supported.
    """
    builder = evidence.data(command["builderSource"]).decode()
    prepared = evidence.json(command["builderPreparation"])
    observed_launch = command.get("invocationProvenance") == "derived-from-observed-builder-launch"
    if not observed_launch:
        require(any(row["file"] == "build-final.mjs" and row["preparedSha256"] == command["builderSource"]["sha256"]
                    for row in prepared["files"]), "builder bytes differ from pre-build preparation")
        require(time_value(prepared["preparedAt"]) <= time_value(command["startedAt"]), "builder was not frozen before execution")
    constants = {}
    for name in ("root", "stage", "node"):
        matches = re.findall(r"const " + name + r" = '([^'\n]+)';", builder)
        require(len(matches) == 1, "ambiguous retained builder constant")
        constants[name] = matches[0]
    version = evidence.candidate["version"]
    if observed_launch:
        observed_builder_launch(evidence, command, receipt, prepared, constants)
    else:
        require(prepared["repoRoot"] == constants["root"] and prepared["version"] == version,
                "prepared builder repository/version differs")
    arguments = ["scripts/build-desktop-artifact.ts", "--platform", "mac", "--target", "dmg", "--arch", "arm64",
                 "--build-version", version, "--output-dir", constants["stage"]]
    literal = "['scripts/build-desktop-artifact.ts','--platform','mac','--target','dmg','--arch','arm64','--build-version','" + version + "','--output-dir',stage]"
    require("spawnSync(node, " + literal + ", { cwd:root, env, stdio:['ignore',fd,fd] })" in builder,
            "retained builder does not contain the exact real artifact spawn")
    require(command["argv"] == [constants["node"], *arguments] and command["cwd"] == constants["root"]
            and receipt["stage"] == constants["stage"], "derived build invocation differs from frozen creator")


def observed_builder_launch(evidence, command, receipt, prepared, constants):
    """A real wrapper launch plus reviewed creator is a separate provenance
    form. Its child argv is derived; no pre-run builder hash is invented.
    """
    review = evidence.json(command["builderReview"])
    require(prepared["changes"]["build-final.mjs"]["sha256"] == command["builderSource"]["sha256"]
            == review["filesSha256"]["build-final.mjs"]
            and review["preparationSha256"] == command["builderPreparation"]["sha256"]
            and review["verdict"] == "SHIP for r2 binding/build", "observed builder bytes were not reviewed")
    time_value(review["reviewedAt"])
    binding = evidence.json(command["builderSourceBinding"])
    require(binding["schemaVersion"] == 1 and binding["sourceCommit"] == evidence.candidate["sourceCommit"]
            and binding["repoRoot"] == constants["root"] and binding["stage"] == constants["stage"]
            and binding["node22"] == constants["node"] and binding["version"] == evidence.candidate["version"]
            and time_value(binding["boundAt"]) <= time_value(command["startedAt"]),
            "observed builder lacks exact pre-run source binding")
    event = evidence.json(command["builderLaunch"])
    payload, item = event["payload"], event["payload"]["item"]
    require(event["type"] == "event_msg" and payload["type"] == "item_completed"
            and item["type"] == "CommandExecution" and item["source"] == "unified_exec_startup"
            and item["status"] == "completed" and item["exit_code"] == 0,
            "builder launch is not an actual completed command event")
    for field in ("thread_id", "turn_id"):
        text(payload[field], "builder event ownership missing")
    for field in ("id", "process_id"):
        text(item[field], "builder event identity missing")
    folder = str(absolute(str(PurePosixPath(binding["buildReceipt"]).parent)))
    require(item["cwd"] == "file://" + folder and item["command"] == [
        "/bin/zsh", "-lc", constants["node"] + " build-final.mjs"], "actual wrapper launch differs from retained creator")
    require(decode(item["aggregated_output"]) == receipt, "actual wrapper output differs from build receipt")
    start, end = payload["started_at_ms"], payload["completed_at_ms"]
    require(type(start) is int and type(end) is int and start <= end
            and start / 1000 <= time_value(command["startedAt"]).timestamp()
            <= time_value(command["finishedAt"]).timestamp() <= end / 1000
            and time_value(event["timestamp"]).timestamp() == end / 1000,
            "actual wrapper interval does not contain the build")


def test_report(evidence, reference):
    report = evidence.json(reference)
    # Vitest's JSON reporter retains named assertion results, not only a pass bit.
    require(report["success"] is True and report["numFailedTests"] == 0
            and report["numPendingTests"] == 0, "product tests not all passed")
    assertions = [case for suite in report["testResults"] for case in suite["assertionResults"]]
    require(assertions and len(assertions) == report["numTotalTests"] == report["numPassedTests"],
            "test count mismatch")
    require(all(case["status"] == "passed" and case["fullName"] for case in assertions),
            "named passing assertions required")
    return {case["fullName"] for case in assertions}


def check_invocation(argv, kind):
    """Recognize actual runner forms, not words such as 'test' in an echo."""
    require(kind in ("unit", "component", "build", "typecheck"), "unknown product check kind")
    require(not any(word.split("=", 1)[0] in ("--version", "-v", "--help", "-h", "-e", "--eval", "--print",
                    "--dry", "--dry-run", "--list", "--listFilesOnly", "--showConfig", "--init", "--ignore-scripts", "--if-present")
                    for word in argv[1:]), "version/help/eval or no-op is not a product check")
    executable, args = Path(argv[0]).name, argv[1:]
    testing = kind in ("unit", "component")
    if kind == "typecheck" and argv[0] == (
            "node_modules/.pnpm/@typescript+typescript-darwin-arm64@7.0.2/node_modules/"
            "@typescript/typescript-darwin-arm64/lib/tsc.original"):
        require(args in (["--noEmit", "-p", "apps/server/tsconfig.json"],
                         ["--noEmit", "-p", "apps/web/tsconfig.json"]),
                "unexpected native TypeScript check arguments")
        return
    if executable in ("npm", "pnpm", "bun"):
        if testing and args and args[0] == "test":
            return
        if len(args) >= 2 and args[0] == "run":
            script = args[1]
            prefix = "test" if testing else kind
            require(script == prefix or script.startswith(prefix + ":"), "wrong package check script")
            require(len(args) == 2 or args[2] == "--", "unexpected package-manager options")
            return
        if executable == "pnpm" and args[:2] == ["exec", "vitest"]:
            executable, args = "vitest", args[2:]
    elif executable in ("npx", "bunx") and args:
        if args[0] == "--no-install":
            args = args[1:]
        if args and args[0] == "vitest":
            executable, args = "vitest", args[1:]
    elif executable == "node" and args:
        target = PurePosixPath(args[0])
        if kind == "build" and target == PurePosixPath("scripts/build-desktop-artifact.ts"):
            require(len(args) == 11 and args[1::2] == ["--platform", "--target", "--arch", "--build-version", "--output-dir"]
                    and args[2:7:2] == ["mac", "dmg", "arm64"] and re.fullmatch(r"\d+\.\d+\.\d+", args[8]),
                    "unexpected desktop artifact build arguments")
            absolute(args[10])
            return
        if target.name in ("vitest.mjs", "vitest.js") and "vitest" in target.parts:
            executable, args = "vitest", args[1:]
        elif target.name == "tsc" and "typescript" in target.parts:
            executable, args = "tsc", args[1:]
        elif target.name == "vp" and "vite-plus" in target.parts:
            executable, args = "vp", args[1:]
    require((testing and executable == "vitest" and args and args[0] == "run")
            or (testing and executable == "vp" and args[:2] == ["test", "run"])
            or (kind == "typecheck" and executable == "tsc" and "--noEmit" in args)
            or (kind == "build" and executable == "tsc" and any(word in args for word in ("--build", "-b"))),
            "unrecognized actual test/build invocation")


def candidate_command(evidence, reference, kind, source_root):
    observed, output, error = command(evidence, reference)
    cwd = absolute(observed["cwd"])
    require(cwd == absolute(source_root) or cwd.is_relative_to(absolute(source_root)),
            "product check ran in another checkout")
    argv = observed["argv"]
    check_invocation(argv, kind)
    desktop_build = kind == "build" and len(argv) > 1 and argv[1] == "scripts/build-desktop-artifact.ts"
    if desktop_build:
        require(argv[-3] == evidence.candidate["version"], "desktop build version differs from candidate")
    require(not any(word in ("--prefix", "--dir", "--cwd", "-C") or word.startswith(
                ("--prefix=", "--dir=", "--cwd=")) for word in argv[1:]), "check redirects its working directory")
    for word in argv[1:]:
        if desktop_build and word == argv[-1]:
            continue  # Explicit artifact output directory, not a source input.
        if word.startswith("/") or ".." in PurePosixPath(word).parts:
            require((Path(str(cwd)) / word).resolve().is_relative_to(source_root),
                    "check path leaves candidate checkout")
    # A successful tsc --noEmit emits nothing; retain the actual empty stream.
    require(kind == "typecheck" or output or error, "empty product check evidence")
    return observed, output, error


def product_code(root):
    evidence = Evidence(root)
    record = evidence.bound(evidence.json(evidence.index["code"]))
    source = record["source"]
    require(source["head"] == evidence.candidate["sourceCommit"]
            and source["origin"] == evidence.candidate["repository"] and source["status"] == "",
            "candidate source checkout mismatch")
    source_root = str(absolute(source["path"]))
    for field, suffix, expected in (("headCommand", ["rev-parse", "HEAD"], source["head"]),
                                    ("statusCommand", ["status", "--porcelain=v1", "--untracked-files=all"], ""),
                                    ("originCommand", ["remote", "get-url", "origin"], source["origin"])):
        observed, output, error = command(evidence, source[field])
        require(observed["cwd"] == source_root and observed["argv"] in
                [[git, "--no-optional-locks", "-C", source_root, *suffix]
                 for git in ("git", "/usr/bin/git", "/Library/Developer/CommandLineTools/usr/bin/git")],
                "candidate Git command not observed in source checkout")
        require(output.rstrip("\n") == expected and not error, "raw candidate Git readback mismatch")
    kinds = set()
    for check in record["checks"]:
        kinds.add(check["kind"])
        observed, _, _ = candidate_command(evidence, check["command"], check["kind"], source_root)
        if check["kind"] in ("unit", "component"):
            require(observed["testReport"] == check["testReport"], "test report not bound to command")
            test_report(evidence, check["testReport"])
    require({"unit", "component", "build"}.issubset(kinds), "missing product source or UI checks")


def product_review(root):
    product_code(root)
    evidence = Evidence(root)
    record = evidence.bound(evidence.json(evidence.index["review"]))
    require(record["reviewer"] != record["implementationOwner"], "fresh independent reviewer required")
    text(record["reviewer"], "reviewer missing")
    require(record["unresolvedFindings"] == [], "product review has unresolved findings")
    report = evidence.data(record["report"]).decode()
    require(evidence.candidate["sourceCommit"] in report and record["reviewer"] in report,
            "review report does not bind reviewer and candidate")
    required = {"wrong-repository", "dirty-destination", "diverged-destination",
                "missing-source-object", "nested-pin-mismatch", "active-owner", "denied-transfer",
                "project-runtime-mode", *DESTINATION_REGRESSIONS}
    require(set(record["cases"]) == required, "missing adversarial review case")
    code = evidence.json(evidence.index["code"])
    executed = [check["command"] for check in code["checks"] if check["kind"] in ("unit", "component")]
    for label, case in record["cases"].items():
        additional = case.get("additionalAssertions", [])
        require(isinstance(additional, list) and all(isinstance(name, str) and name for name in additional),
                "additional review assertions must name actual tests")
        assertions = [case["assertion"], *additional]
        if "externalTest" in case:
            external = external_review_test(evidence, case["externalTest"], code, record)
            require(case["command"] == external["command"] and case["testReport"] == external["testReport"],
                    "external review case detached from actual execution")
            suites = evidence.json(external["testReport"])["testResults"]
            require(case["testPath"] in {f["path"] for f in external["testFiles"]}
                    and any(suite["name"] == case["testPath"] and all(any(
                        assertion["fullName"] == name and assertion["status"] == "passed"
                        for assertion in suite["assertionResults"]) for name in assertions) for suite in suites),
                    "external case assertion is not from its executed frozen suite")
        else:
            require(case["command"] in executed, "review refers to an unverified test execution")
        check, _, _ = command(evidence, case["command"])
        require(check["testReport"] == case["testReport"], "review test report detached from execution")
        names = test_report(evidence, case["testReport"])
        require(all(name in names for name in assertions), "review case has no actual passing assertion")
        if label in DESTINATION_REGRESSIONS:
            relative, expected = DESTINATION_REGRESSIONS[label]
            expected_path = code["source"]["path"] + "/" + relative
            require(case["assertion"] == expected[0], "destination review case names an unrelated regression")
            if label == "partial-clone-identity":
                require(additional == list(expected[1:]), "partial clone review needs the exact upstream witness")
            suites = evidence.json(case["testReport"])["testResults"]
            require("externalTest" not in case and case["testPath"] == expected_path and any(
                suite.get("name") == expected_path and all(any(
                    assertion["fullName"] == name and assertion["status"] == "passed"
                    for assertion in suite["assertionResults"]) for name in assertions) for suite in suites),
                "destination regressions are not from the actual frozen candidate suite")
        if label == "project-runtime-mode":
            expected_path = code["source"]["path"] + "/apps/server/src/project/ProjectCoordinatorService.test.ts"
            suites = evidence.json(case["testReport"])["testResults"]
            require(case["assertion"] == PROJECT_RUNTIME_REGRESSION,
                    "project runtime case does not name the scoped-approval regression")
            require("externalTest" not in case and case["testPath"] == expected_path and any(
                suite.get("name") == expected_path and any(
                    assertion["fullName"] == case["assertion"] and assertion["status"] == "passed"
                    for assertion in suite["assertionResults"]) for suite in suites),
                "project runtime regression is not from the actual coordinator suite")


def external_review_test(evidence, reference, code, review):
    """Independent reproduction files can live outside the product checkout.

    Retain their exact bytes and candidate imports; never relabel their cwd or
    treat a test name alone as evidence that production code was exercised.
    """
    external = evidence.bound(evidence.json(reference))
    observed, output, error = command(evidence, external["command"])
    require(observed["testReport"] == external["testReport"] and (output or error),
            "external test report/output detached from execution")
    check_invocation(observed["argv"], "unit")
    source_root, cwd = absolute(code["source"]["path"]), absolute(observed["cwd"])
    # Current reviewer uses the frozen candidate's installed Node runner with
    # absolute external test paths. Other forms need their own reviewed binding.
    require(Path(observed["argv"][0]).name == "node" and len(observed["argv"]) > 2,
            "external test requires explicit candidate Node runner")
    runner = PurePosixPath(os.path.normpath(str(cwd / observed["argv"][1])))
    require(runner.is_relative_to(source_root / "node_modules"), "external runner is not from candidate checkout")
    require(external["reviewer"] == review["reviewer"] != review["implementationOwner"],
            "external tests require the independent reviewer")
    reviewed = evidence.data(external["review"]).decode()
    require(evidence.candidate["sourceCommit"] in reviewed and external["reviewer"] in reviewed,
            "external review does not bind reviewer/candidate")
    require(external["testFiles"], "external test source missing")
    report = evidence.json(external["testReport"])
    require({suite["name"] for suite in report["testResults"]}
            == {file["path"] for file in external["testFiles"]}
            and all(suite["assertionResults"] for suite in report["testResults"]),
            "external JSON reporter suite paths differ from retained test files")
    bindings = None
    if "harnessBindings" in external:
        bindings = evidence.json(external["harnessBindings"])
        require(bindings["candidateCommit"] == evidence.candidate["sourceCommit"]
                and bindings["candidatePath"] == str(source_root)
                and external["harnessBindings"]["sha256"] in reviewed
                and observed["externalHarnessBindings"]["sha256"] == external["harnessBindings"]["sha256"]
                and observed["harnessUnchanged"] is True, "external harness binding is not reviewed/executed")
        reviewed += evidence.data(external["harnessBindings"]).decode()
    configured_paths = set()
    if "config" in external:
        config = external["config"]
        config_path = absolute(config["path"])
        require("--config=" + str(config_path) in observed["argv"], "external config was not used")
        config_source = evidence.data(config["bytes"]).decode().strip()
        require(config_source.startswith("export default ") and config_source.endswith(";"),
                "external config must be retained static JSON")
        config_object = decode(config_source[len("export default "):-1])
        require(set(config_object) in ({"test"}, {"test", "cacheDir"}), "external config has unreviewed runner overrides")
        settings = config_object["test"]
        require(set(settings).issubset({"root", "include", "environment", "testTimeout", "hookTimeout"}),
                "external config has unreviewed test overrides")
        require(settings["environment"] == "node", "external config environment differs")
        config_root = absolute(settings["root"])
        if "cacheDir" in config_object:
            require(absolute(config_object["cacheDir"]) == config_root / "cache",
                    "external cache must remain inside the actual harness directory")
        configured_paths = {absolute(str(config_root / rel)) for rel in settings["include"]}
        require(configured_paths == {absolute(f["path"]) for f in external["testFiles"]},
                "external config test inventory differs")
        require(bindings is not None and any(f["path"] == str(config_path.relative_to(absolute(external["harnessRoot"])))
                and f["sha256"] == config["bytes"]["sha256"] for f in bindings["harnessFiles"]),
                "external config bytes were not independently bound")
    paths = set()
    for file in external["testFiles"]:
        path = absolute(file["path"])
        require(path not in paths and not path.is_relative_to(source_root), "external test path is not distinct")
        paths.add(path)
        argv_paths = {PurePosixPath(os.path.normpath(str(cwd / word))) for word in observed["argv"][2:]
                      if word and not word.startswith("-")}
        require(path in argv_paths or path in configured_paths, "external file was not named by actual test command")
        body = evidence.data(file["bytes"]).decode()
        bound_file = bindings is not None and any(
            f["path"] == str(path.relative_to(absolute(external["harnessRoot"])))
            and f["sha256"] == file["bytes"]["sha256"] for f in bindings["harnessFiles"])
        require(bound_file or (str(path) in reviewed and file["bytes"]["sha256"] in reviewed),
                "external file bytes not independently reviewed")
        require(file["candidateImports"], "external test has no explicit candidate import")
        imports = set()
        for imported in file["candidateImports"]:
            import_path = absolute(imported["path"])
            relative = str(import_path.relative_to(source_root))
            require(import_path not in imports and relative == imported["relativePath"], "candidate import path mismatch")
            imports.add(import_path)
            require(re.search(r"(?:from\s*|import\s*\()(['\"])" + re.escape(str(import_path)) + r"\1", body),
                    "declared candidate import not present in external source")
            retained = evidence.data(imported["bytes"])
            git, actual, git_error = command(evidence, imported["gitShowCommand"])
            require(git["cwd"] == str(source_root) and git["argv"] in
                    [[executable, "--no-optional-locks", "-C", str(source_root), "show",
                      evidence.candidate["sourceCommit"] + ":" + relative]
                     for executable in ("git", "/usr/bin/git", "/Library/Developer/CommandLineTools/usr/bin/git")],
                    "candidate import not bound to actual frozen Git blob")
            require(not git_error and actual.encode() == retained and imported["bytes"]["sha256"] in reviewed,
                    "candidate import bytes differ from reviewed frozen source")
    test_report(evidence, external["testReport"])
    return external


def product_release(root):
    product_review(root)
    evidence = Evidence(root)
    record = evidence.bound(evidence.json(evidence.index["release"]))
    # The release owner must retain a build, published bytes, and all three
    # installed/runtime readbacks. A version string alone never satisfies this.
    require(record["version"] == evidence.candidate["version"], "wrong released version")
    code = evidence.json(evidence.index["code"])
    built, _, _ = candidate_command(evidence, record["build"], "build", code["source"]["path"])
    require(record["artifact"] in built["producedArtifacts"], "release artifact not bound to build")
    artifact = evidence.path(record["artifact"])
    require(artifact.stat().st_size > 0, "empty release artifact")
    published = evidence.json(record["publication"])
    require(published["sourceCommit"] == evidence.candidate["sourceCommit"]
            and published["version"] == record["version"]
            and published["artifactSha256"] == record["artifact"]["sha256"], "published artifact mismatch")
    require(published["url"].startswith("https://") and published["downloadedArtifact"] == record["artifact"],
            "published artifact download/readback missing")
    require({item["host"] for item in record["hosts"]} == {"m4", "m1", "m3"}
            and len(record["hosts"]) == 3, "three release host readbacks required")
    for item in record["hosts"]:
        observed = runtime(evidence, item["readback"], item["host"], released=True)
        if observed["kind"] == "released-worker-service":
            archive = published_runtime_archive(evidence, record["runtimeArchive"], built)
            raw = evidence.json(observed["serviceReadback"])
            require(observed["installedFromArchiveSha256"] == raw["archiveSha256"] == archive["sha256"],
                    "installed worker archive differs from public release")
        else:
            require(observed["installedFromArtifactSha256"] == record["artifact"]["sha256"], "installed artifact mismatch")


def published_runtime_archive(evidence, record, built):
    """Bind the worker archive separately from the desktop download."""
    artifact = record["artifact"]
    path = evidence.path(artifact)
    binding = evidence.json(record["buildBinding"])
    owner = evidence.json(built["ownerReceipt"])
    require(binding["verified"] is True and binding["sourceCommit"] == evidence.candidate["sourceCommit"]
            and binding["buildReceiptSha256"] == built["ownerReceipt"]["sha256"]
            and owner["source"] == evidence.candidate["sourceCommit"] and owner["sourceUnchanged"] is True
            and owner["exitCode"] == 0, "runtime archive not bound to candidate build")
    require(binding["sha256"] == artifact["sha256"] and binding["archive"] == path.name
            and type(binding["bytes"]) is int and binding["bytes"] == path.stat().st_size > 0,
            "runtime archive bytes differ from build binding")
    fingerprint = binding["serverDistFingerprint"]
    require(fingerprint == owner["serverDistFingerprint"] and HEX64.fullmatch(fingerprint["sha256"])
            and type(fingerprint["files"]) is int and fingerprint["files"] > 0
            and time_value(binding["completedAt"]) >= time_value(built["finishedAt"]),
            "runtime archive differs from built server")
    published = evidence.json(record["publication"])
    require(published["sourceCommit"] == evidence.candidate["sourceCommit"]
            and published["version"] == evidence.candidate["version"]
            and published["artifactSha256"] == artifact["sha256"]
            and published["downloadedArtifact"] == artifact and published["url"].startswith("https://"),
            "public runtime archive download/readback missing")
    return artifact


def runtime(evidence, reference, host, released=False):
    observed = evidence.bound(evidence.json(reference))
    require(observed["host"] == host and observed["version"] == evidence.candidate["version"],
            "wrong installed runtime")
    text(observed["environmentId"], "runtime environment missing")
    server = evidence.json(observed["serverReadback"])
    require(server["sourceCommit"] == evidence.candidate["sourceCommit"]
            and server["version"] == observed["version"], "server source/version differs from candidate")
    require(server["environmentId"] == observed["environmentId"], "server environment mismatch")
    worker_release = released and observed["kind"] == "released-worker-service"
    require(observed["kind"] == ("released-native-app" if released else "transfer-service") or worker_release,
            "wrong runtime evidence kind for phase")
    require(not worker_release or (host in HOSTS and "serviceReadback" in observed),
            "released worker role requires remote service proof")
    if "serviceReadback" in observed:
        require((not released or worker_release) and host in HOSTS and "wrapperReadback" not in observed
                and "appReadback" not in observed, "worker service proof cannot replace native UI or released app proof")
        client = evidence.json(observed["clientReadback"])
        require(client["sourceCommit"] == evidence.candidate["sourceCommit"]
                and client["version"] == observed["version"]
                and client["delivery"] == "http-service", "worker service client differs from candidate")
        worker_service(evidence, observed, client)
        http_client(evidence, client)
        return observed
    app = evidence.json(observed["appReadback" if released else "wrapperReadback"])
    if released:
        require(app["sourceCommit"] == evidence.candidate["sourceCommit"]
                and app["version"] == observed["version"], "released native app differs from candidate")
    else:
        # The running shell can legitimately predate the separately installed
        # server/client candidate. Preserve its observed identity without
        # relabeling it as the later released application.
        text(app["version"], "observed native wrapper version missing")
        client = evidence.json(observed["clientReadback"])
        require(client["sourceCommit"] == evidence.candidate["sourceCommit"]
                and client["version"] == observed["version"], "served client differs from candidate")
        if host == "m4":
            require(client.get("delivery") == "native-bundle", "M4 UI requires native bundled client proof")
        if client.get("delivery") == "native-bundle":
            native_client(evidence, client, app, observed)
        else:
            require(client.get("delivery", "http-service") == "http-service", "unknown client delivery")
            http_client(evidence, client)
    require(HEX64.fullmatch(app["executableSha256"]), "installed executable hash missing")
    require(app["runningExecutableSha256"] == app["executableSha256"], "running executable differs from installed")
    return observed


def http_client(evidence, client):
    require(client["assets"] and len({a["url"] for a in client["assets"]}) == len(client["assets"]),
            "distinct served client assets required")
    for asset in client["assets"]:
        require(asset["url"].startswith(("https://", "http://")), "client asset URL missing")
        built, served = evidence.path(asset["builtAsset"]), evidence.path(asset["servedAsset"])
        require(built.stat().st_size > 0 and served.stat().st_size > 0
                and asset["builtAsset"]["sha256"] == asset["servedAsset"]["sha256"] == asset["sha256"],
                "served client asset differs from candidate build")


def retained_bytes(record):
    data = base64.b64decode(record["base64"], validate=True)
    require(type(record["bytes"]) is int and len(data) == record["bytes"]
            and digest(data) == record["sha256"], "retained remote bytes differ from raw readback")
    return data


def worker_service(evidence, observed, client):
    """Remote workers need the exact running service, without a desktop UI."""
    raw = evidence.json(observed["serviceReadback"])
    owner = evidence.json(observed["serviceOwnerReadback"])
    previous = owner["readback"]
    require(owner["controllerPhase"] == "installed-verified" and owner["released"] is True
            and owner["installationVersion"] == observed["version"], "worker install readback is not verified")
    require(raw["host"] == previous["identity"] == observed["host"]
            and raw["sourceCommit"] == previous["sourceCommit"] == evidence.candidate["sourceCommit"]
            and raw["version"] == observed["version"]
            and raw["archiveSha256"] == previous["archiveSha256"]
            and HEX64.fullmatch(raw["archiveSha256"]), "worker service source/host/archive mismatch")
    require(retained_bytes(raw["environmentFile"]).decode().strip() == raw["environmentId"] == observed["environmentId"]
            and raw["environmentFile"]["sha256"] == previous["environmentIdFingerprint"],
            "worker environment differs from preserved machine identity")
    time_value(raw["observedAt"])
    require(time_value(raw["observedAt"]) >= time_value(previous["observedAtUTC"]), "worker readback predates installation")
    process, running = raw["process"], raw["runtime"]
    require(type(process["pid"]) is int and process["pid"] > 0
            and process["pid"] == running["pid"] == previous["runtime"]["pid"]
            and previous["service"]["state"] == "running", "worker service PID differs from installed process")
    executable = str(absolute(process["executable"]))
    require(executable == previous["node"]
            and HEX64.fullmatch(process["installedExecutableSha256"])
            and process["installedExecutableSha256"] == process["runningExecutableSha256"]
            and re.fullmatch(r"[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4}", process["startedAt"]),
            "worker service executable/start identity invalid")
    release = str(absolute(raw["release"]))
    state = absolute(raw["stateDir"])
    require(release == previous["release"] and str(state) == previous["stateDir"]
            and running == previous["runtime"] and running["host"] == "127.0.0.1"
            and type(running["port"]) is int and 0 < running["port"] < 65536
            and running["origin"] == f"http://127.0.0.1:{running['port']}", "worker service runtime paths differ")
    expected_argv = [executable, release + "/bin.mjs", "start", "--no-browser", "--host", "127.0.0.1",
                     "--port", str(running["port"]), "--base-dir", str(state.parent), "--mode", "web"]
    require(process["argv"] == expected_argv, "worker process is not the installed candidate server command")
    manifest = decode(retained_bytes(raw["manifest"]))
    require(manifest["sourceCommit"] == evidence.candidate["sourceCommit"]
            and manifest["version"] == observed["version"]
            and len(manifest["files"]) == previous["filesVerified"] > 0,
            "worker installed manifest differs from verified candidate")
    files = {item["path"]: item for item in manifest["files"]}
    require(len(files) == len(manifest["files"]), "duplicate installed manifest path")
    expected_files = [{"path": item["path"], "type": item["type"],
                       **({"target": item["target"]} if item["type"] == "symlink" else {"sha256": item["sha256"]})}
                      for item in manifest["files"]]
    require(raw["filesReadback"] == expected_files, "worker installed file readback differs from candidate manifest")
    entry = raw["sourceEntry"]
    require(entry["path"] == release + "/bin.mjs"
            and digest(retained_bytes(entry["content"])) == files["bin.mjs"]["sha256"],
            "running service entry differs from candidate manifest")
    require(len(raw["assets"]) == len(client["assets"]) >= 2, "worker HTML and JavaScript readbacks required")
    for retained, asset in zip(raw["assets"], client["assets"]):
        relative = retained["relativePath"]
        require(relative == asset["relativePath"] and relative.startswith("client/")
                and retained["url"] == asset["url"]
                and asset["url"] == running["origin"] + ("/" if relative == "client/index.html" else "/" + relative[7:]),
                "worker HTTP asset route differs from installed client")
        require(retained_bytes(retained["built"]) == retained_bytes(retained["served"])
                == evidence.data(asset["builtAsset"]) == evidence.data(asset["servedAsset"])
                and retained["built"]["sha256"] == files[relative]["sha256"],
                "worker HTTP bytes differ from raw response or candidate manifest")
    require(any(a["relativePath"] == "client/index.html" for a in client["assets"])
            and any(a["relativePath"].endswith(".js") for a in client["assets"]), "worker client HTML or JavaScript missing")


def asar_file(archive, name):
    """Read one packed ASAR entry as data; never load archive JavaScript."""
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and str(relative) == name and relative.parts
            and not any(part in (".", "..") for part in relative.parts)
            and not re.search(r"[\x00-\x1f]", name), "unsafe ASAR entry")
    with archive.open("rb") as stream:
        header = stream.read(16)
        require(len(header) == 16, "truncated ASAR header")
        first, header_size, payload_size, json_size = struct.unpack("<4I", header)
        length = archive.stat().st_size
        require(first == 4 and header_size == payload_size + 4
                and 0 < json_size <= min(payload_size - 4, 16 * 1024 * 1024)
                and 8 + header_size <= length, "invalid ASAR header")
        entry = decode(stream.read(json_size))
        for part in relative.parts:
            entry = entry["files"][part]
        require(not entry.get("unpacked") and "link" not in entry and "files" not in entry,
                "ASAR entry is not a packed regular file")
        require(isinstance(entry["offset"], str) and re.fullmatch(r"\d+", entry["offset"]), "invalid ASAR offset")
        offset, size = 8 + header_size + int(entry["offset"]), entry["size"]
        require(type(size) is int and 0 <= size <= 32 * 1024 * 1024
                and offset + size <= length, "ASAR entry out of bounds")
        stream.seek(offset)
        return stream.read(size)


def native_screenshot_shape(data):
    """Identify retained pixels by bytes, including JPEG supplied under a .png name."""
    if len(data) >= 33 and data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        width, height = struct.unpack(">II", data[16:24])
        encoding = "png"
    else:
        require(data[:2] == b"\xff\xd8", "native screenshot must be PNG or JPEG")
        pos, width, height = 2, 0, 0
        while pos + 4 <= len(data):
            require(data[pos] == 255, "malformed JPEG marker")
            while pos < len(data) and data[pos] == 255:
                pos += 1
            require(pos < len(data), "truncated JPEG marker")
            marker = data[pos]
            pos += 1
            if marker in (0xD9, 0xDA):
                break
            require(pos + 2 <= len(data), "truncated JPEG segment")
            length = int.from_bytes(data[pos:pos + 2], "big")
            require(length >= 2 and pos + length <= len(data), "malformed JPEG segment")
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                require(length >= 8, "JPEG dimensions missing")
                height, width = struct.unpack(">HH", data[pos + 3:pos + 7])
                break
            pos += length
        encoding = "jpeg"
    require(width >= 320 and height >= 240, "native screenshot too small")
    return {"encoding": encoding, "width": width, "height": height}


def staged_credential_creation(evidence, proof, stage, launch, readback, identity, home):
    """Permit one independently observed encrypted cache creation, without retaining its bytes."""
    transition = proof["credentialCreation"]
    require(set(transition) == {"audit", "auditOriginPath", "wrapper", "execution"},
            "closed credential creation proof required")
    audit = evidence.json(transition["audit"])
    fields = {"result", "validEncryptedEntryShape", "decryptionChecked", "entryCount", "environmentKeyHashes",
              "observedAt", "file", "regularNonSymlink", "singleHardlink", "stableBeforeDuringAfterInspection",
              "stageAndLaunchStateExactlyEqual", "credentialAbsentAtStageAndCandidateLaunch",
              "creationAfterCandidateLaunchBeforeAudit", "stage", "candidateLaunch", "binding",
              "encryptedPayloadRetained", "writeAttributionEstablished", "accountAcceptanceStillRequired",
              "nativeOrServiceActionPerformed"}
    require(set(audit) == fields and audit["result"] == "validated-exact-encrypted-cache-creation",
            "exact independent credential audit required")
    require(all(audit[k] is True for k in ("validEncryptedEntryShape", "regularNonSymlink", "singleHardlink",
                "stableBeforeDuringAfterInspection", "stageAndLaunchStateExactlyEqual",
                "credentialAbsentAtStageAndCandidateLaunch", "creationAfterCandidateLaunchBeforeAudit",
                "accountAcceptanceStillRequired")) and all(audit[k] is False for k in
                ("decryptionChecked", "encryptedPayloadRetained", "writeAttributionEstablished", "nativeOrServiceActionPerformed")),
            "credential audit overstates its evidence")
    name = "desktop-service-credentials.json"
    initial = stage["state"]
    require(stage["state"] == launch["state"] and initial["configurationHashes"][name] is None
            and type(audit["entryCount"]) is int and audit["entryCount"] == 1
            and HEX64.fullmatch(initial["service"]["environmentIdSha256"])
            and audit["environmentKeyHashes"] == [initial["service"]["environmentIdSha256"]],
            "credential creation is not first creation for the same environment")
    for field, key, filename in (("stage", "stage", "stage.json"),
                                 ("candidateLaunch", "launch", "candidate-launch.json")):
        raw = stage if key == "stage" else launch
        require(set(audit[field]) == {"path", "sha256", "at"}
                and audit[field]["sha256"] == proof[key]["sha256"] and audit[field]["at"] == raw["at"]
                and absolute(audit[field]["path"]) == absolute(launch["appPath"]).parent / filename,
                "credential audit detached from raw native baseline")
    require(set(audit["binding"]) == {"path", "sha256"}
            and audit["binding"]["sha256"] == proof["binding"]["sha256"]
            and absolute(audit["binding"]["path"]).name == "binding.json", "credential audit binding differs")
    file = audit["file"]
    require(set(file) == {"path", "uid", "mode", "bytes", "device", "inode", "mtimeNs", "birthtime", "sha256"}
            and absolute(file["path"]) == home / ".specweave-studio/m4/userdata" / name
            and type(file["uid"]) is int and file["uid"] == identity["uid"]
            and type(file["mode"]) is int and file["mode"] == 0o600
            and all(type(file[k]) is int and file[k] > 0 for k in ("bytes", "device", "inode", "mtimeNs"))
            and type(file["birthtime"]) in (int, float) and HEX64.fullmatch(file["sha256"])
            and readback["state"]["configurationHashes"][name] == file["sha256"],
            "credential metadata differs from exact observed creation")
    require(time_value(launch["at"]).timestamp() < file["birthtime"] <= file["mtimeNs"] / 1e9
            <= time_value(audit["observedAt"]).timestamp() <= time_value(readback["at"]).timestamp(),
            "credential creation is outside observed native launch window")
    executed = evidence.json(transition["execution"])
    require(set(executed) == {"at", "result", "phase", "adapterSha256", "originalHelperSha256",
                "originalBindingSha256", "credentialCreationAudit", "originalReceipt", "processesStoppedOrReaped"}
            and executed["result"] == "original-helper-phase-verified-with-reviewed-process-and-cache-transitions"
            and executed["phase"] == "readback-candidate" and executed["processesStoppedOrReaped"] is False
            and executed["adapterSha256"] == transition["wrapper"]["sha256"]
            and executed["originalHelperSha256"] == proof["helper"]["sha256"]
            and executed["originalBindingSha256"] == proof["binding"]["sha256"]
            and evidence.data(transition["wrapper"]), "successful exact-transition wrapper execution required")
    require(executed["credentialCreationAudit"] == {"path": str(absolute(transition["auditOriginPath"])),
                "sha256": transition["audit"]["sha256"], "preexistingBytesClaimedIdentical": False}
            and executed["originalReceipt"] == {"path": str(absolute(launch["appPath"]).parent / "candidate-readback.json"),
                "sha256": proof["readback"]["sha256"]}
            and time_value(executed["at"]) >= time_value(readback["at"]),
            "transition wrapper detached from audit or native readback")
    return file["sha256"]


def staged_native_process(evidence, proof, candidate, version, asar_sha):
    """Replay raw staged-app observations without inventing an installation phase."""
    fields = {"kind", "at", "binding", "helper", "stage", "launchStart", "spawn", "launch",
              "readback", "uiObservation", "uiOriginPath", "uiArtifacts"}
    require(set(proof) in (fields, fields | {"credentialCreation"}) and proof["kind"] == "staged-native-observation",
            "closed staged-native proof required")
    binding, stage, start, spawn, launch, readback, ui = [evidence.json(proof[k]) for k in
        ("binding", "stage", "launchStart", "spawn", "launch", "readback", "uiObservation")]
    require(binding["sourceCommit"] == candidate and binding["version"] == version
            and binding["asarSha256"] == asar_sha and HEX64.fullmatch(binding["runtimeArchiveSha256"]),
            "staged binding differs from candidate")
    require(stage["phase"] == "staged-only" and stage["installationPerformed"] is False
            and stage["bindingSha256"] == proof["binding"]["sha256"]
            and stage["helperSha256"] == binding["helperSha256"] == proof["helper"]["sha256"]
            and evidence.data(proof["helper"]), "stage does not bind retained producer")
    identity = launch["nativeMain"]
    executable = str(absolute(launch["appPath"]) / "Contents/MacOS/SpecWithCode")
    require(identity["executable"] == executable == stage["candidateProof"]["executable"]
            and stage["candidateProof"]["version"] == version and launch["asarSha256"] == asar_sha
            and HEX64.fullmatch(stage["candidateProof"]["treeSha256"])
            and launch["nativeUpdaterAndRouteReadbackPending"] is True,
            "staged launch does not bind app bytes")
    require(type(identity["pid"]) is int and identity["pid"] > 0 and type(identity["uid"]) is int
            and identity["uid"] > 0 and re.fullmatch(
                r"[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4}", identity["startedAt"]),
            "staged native process identity invalid")
    require(start["argv"] == [executable] and spawn["pid"] == identity["pid"]
            and spawn["executable"] == executable, "staged spawn differs from launch")
    home = absolute(start["cwd"])
    require(start["environmentOverrides"] == {"STUDIO_HOME": str(home / ".specweave-studio/m4"),
                                             "STUDIO_DISABLE_AUTO_UPDATE": "true"},
            "staged launch environment differs")
    require(readback["phase"] == "candidate-native-settings-ui-verified"
            and readback["appPath"] == launch["appPath"] and readback["sixRouteOwnerEvidenceRequired"] is True
            and readback["normalPublishedUpdaterTestStillRequired"] is False
            and readback["originalApplicationsTreeSha256"] == stage["originalProof"]["treeSha256"]
            and HEX64.fullmatch(readback["originalApplicationsTreeSha256"]),
            "staged candidate readback phase or original tree differs")
    rows = readback["nativeProcesses"]
    require(rows and len({r["pid"] for r in rows}) == len(rows), "duplicate staged native process")
    mains = [r for r in rows if r["pid"] == identity["pid"]]
    require(len(mains) == 1 and all(mains[0][k] == identity[k] for k in ("pid", "uid", "startedAt", "executable"))
            and all(r["uid"] == identity["uid"] and absolute(r["executable"]).is_relative_to(
                absolute(launch["appPath"])) for r in rows), "staged readback process differs")
    protected = ("settings.json", "environment-id", "credentials.json", "auth.json",
                 "desktop-service-credentials.json", "saved-environments.json")
    initial = stage["state"]
    require(initial["service"]["sourceCommit"] == candidate and initial["service"]["version"] == version,
            "staged managed service differs from candidate")
    created = (staged_credential_creation(evidence, proof, stage, launch, readback, identity, home)
               if "credentialCreation" in proof else None)
    for position, state in enumerate((start["before"], launch["state"], readback["state"])):
        require(all(state[k] == initial[k] for k in ("service", "profile", "defaultState"))
                and all(state["configurationHashes"][k] == (created if created is not None and position == 2
                    and k == "desktop-service-credentials.json" else initial["configurationHashes"][k]) for k in protected),
                "staged protected state changed")
    require(ui["method"] == "settings-general-ui" and ui["bridgeStateObserved"] is False
            and ui["securityWarningBypassed"] is False and ui["quitPerformed"] is False
            and ui["applicationPath"] == launch["appPath"] and ui["observedVersion"] == version
            and ui["observedTrack"] == "Stable"
            and not any(k in ui for k in ("state", "status", "currentVersion", "availableVersion", "downloadedVersion")),
            "staged UI observation is not truthful candidate Settings evidence")
    require(re.fullmatch(r"\s*" + str(identity["pid"]) + r"\s+" + re.escape(identity["startedAt"])
                         + r"\s+" + re.escape(executable) + r"\s*", ui["processRaw"]),
            "staged UI process differs")
    if "sourceCommit" in ui:
        require(ui["sourceCommit"] == candidate, "staged UI source differs")
    artifacts = proof["uiArtifacts"]
    require(set(artifacts) == {"accessibility", "screenshot"}
            and artifacts["accessibility"]["sha256"] == ui["ax"]["sha256"]
            and artifacts["screenshot"]["sha256"] == ui["screenshot"]["sha256"],
            "staged UI artifacts differ from raw observation")
    ax = evidence.data(artifacts["accessibility"]).decode("utf-8")
    headings = list(re.finditer(r"(?m)^\s*\d+ heading Version " + re.escape(version) + r", Value: 3$", ax))
    require(ax.startswith('Window: "SpecWithCode", App: SpecWithCode.')
            and 'HTML content SpecWithCode, URL: studio://app/#/settings/general' in ax
            and len(headings) == 1, "staged native About AX heading missing")
    track = re.search(r"(?m)^\s*\d+ heading Update track, Value: 3$", ax[headings[0].end():])
    require(track is not None, "staged native About update track missing")
    end = headings[0].end() + track.start()
    require(re.search(r"(?m)^\s*\d+ text " + re.escape(version) + r"$", ax[headings[0].start():end])
            and re.search(r"(?m)^\s*\d+ combo box \(settable\) Description: Update track, Value: Stable$", ax[end:end + 500]),
            "staged native About AX values missing")
    native_screenshot_shape(evidence.data(artifacts["screenshot"]))
    text(ui["screenshotLimitation"], "staged screenshot limitation missing")
    update = readback["nativeUpdateEvidence"]
    require(update["method"] == "settings-general-ui" and update["bridgeResponseObserved"] is False
            and update["receiptSha256"] == proof["uiObservation"]["sha256"]
            and update["receiptPath"] == str(absolute(proof["uiOriginPath"]))
            and update["observedAt"] == ui["observedAt"], "staged readback differs from actual UI receipt")
    stamps = [stage["at"], start["at"], spawn["at"], launch["at"], ui["startedAt"], ui["observedAt"], readback["at"]]
    require([time_value(t) for t in stamps] == sorted(time_value(t) for t in stamps)
            and proof["at"] == launch["at"] and time_value(launch["at"]) <= time_value(ui["processObservedAt"])
            and (time_value(ui["observedAt"]) - time_value(ui["startedAt"])).total_seconds() <= 30
            and abs((time_value(ui["processObservedAt"]) - time_value(ui["observedAt"])).total_seconds()) <= 30,
            "staged launch and native observations are out of order")
    return identity


def native_client(evidence, client, app, observed):
    require(app["version"] == observed["version"] and app["sourceCommit"] == evidence.candidate["sourceCommit"],
            "native UI wrapper is not the candidate")
    archive = evidence.path(client["appAsar"])
    require(app["appAsarSha256"] == app["runningAppAsarSha256"] == client["appAsar"]["sha256"],
            "running native ASAR differs from bundled client")
    audit = evidence.json(client["artifactAudit"])
    require(audit["result"] == "passed" and audit["sourceCommit"] == evidence.candidate["sourceCommit"]
            and audit["version"] == observed["version"]
            and audit["local"]["desktop"]["appAsarSha256"] == client["appAsar"]["sha256"],
            "native client archive differs from audited candidate")
    process = evidence.json(app["nativeProcessProof"])
    time_value(process["at"])
    if process.get("kind") == "staged-native-observation":
        identity = staged_native_process(evidence, process, evidence.candidate["sourceCommit"],
                                         observed["version"], client["appAsar"]["sha256"])
        require(type(app["pid"]) is int and identity["pid"] == app["pid"] > 0,
                "staged native process proof does not bind wrapper")
    else:
        identity = process["nativeProcess"]
        require(process["phase"] == "installed-process-verified" and process["protectedStatePreserved"] is True
                and process["sourceCommit"] == evidence.candidate["sourceCommit"]
                and process["version"] == observed["version"] and process["asarSha256"] == client["appAsar"]["sha256"]
                and type(app["pid"]) is int and identity["pid"] == app["pid"] > 0,
                "native process proof does not bind the candidate")
    require(absolute(identity["executable"]) == absolute(app["executable"])
            and identity["startedAt"] == app["startedAt"]
            and re.fullmatch(r"[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4}", app["startedAt"]),
            "native process executable/start time differs from wrapper readback")
    assets = client["assets"]
    prefix = "apps/server/dist/client/"
    paths = {a["entry"] for a in assets}
    require(assets and len(paths) == len(assets) and prefix + "index.html" in paths
            and any(path.startswith(prefix) and path.endswith(".js") for path in paths),
            "native client requires distinct HTML and JavaScript entries")
    for asset in assets:
        require(asset["entry"].startswith(prefix)
                and asset["url"] == "studio://app/" + asset["entry"][len(prefix):], "native client protocol entry mismatch")
        built, bundled = evidence.data(asset["builtAsset"]), evidence.data(asset["bundledAsset"])
        require(built == bundled == asar_file(archive, asset["entry"]) and built
                and digest(built) == asset["sha256"], "native bundled asset differs from actual ASAR or build")


def source_runtime(evidence, reference, plan, key):
    """Source characterization may predate the later product release."""
    started = evidence.json(reference)
    require(started["status"] == "started" and started["temporarySessionRevoked"] is True and started["key"] == key
            and started["projectId"] == plan["projectId"] and started["coordinatorId"] == plan["coordinatorId"]
            and started["environmentId"] == plan["environmentId"]
            and started["messageId"] == plan["startMessageId"]
            and started["originalShas"] == plan["originalShas"], "source start/native plan mismatch")
    observed = started["runtime"]
    require(observed["environmentId"] == plan["environmentId"], "source characterization environment mismatch")
    text(observed["serverVersion"], "observed source version missing")
    time_value(observed["observedAt"])
    return observed


def bracket(preserved, host, times, configuration=False):
    bounds = preserved[host]
    before_key, after_key = ("configBeforeAt", "configAfterAt") if configuration else ("beforeAt", "afterAt")
    before, after = time_value(bounds[before_key]), time_value(bounds[after_key])
    require(times and all(before <= time_value(at) <= after for at in times),
            "preservation snapshots do not bracket actual work")


def native_times(receipt):
    times = []
    projections = [receipt["parent"], *receipt["workers"]] if receipt.get("workflowVersion") == 2 else [receipt["parent"], receipt["worker"]]
    for projection in projections:
        for run in projection["runs"]:
            start, finish = run["startedAt"], run["completedAt"]
            require(time_value(start) <= time_value(finish), "native run interval invalid")
            times.extend((start, finish))
    return times


def preservation(evidence, refs, advances=None):
    advances = advances or {}
    require(len(refs) == 3, "all original machines require preservation readbacks")
    records = {}
    expected = {(project, kind) for project in PROJECTS for kind in ("root", "nested")}
    for ref in refs:
        item = evidence.json(ref)
        host = item["host"]
        require(host in ("m4", *HOSTS) and host not in records, "duplicate preservation host")
        before, after = item["before"], item["after"]
        require(len(before) == len(after) and len(before) >= 6, "six original checkout snapshots required per host")
        required = [r for r in before if r["kind"] != "additional"]
        require(len(required) == 6 and {(r["projectKey"], r["kind"]) for r in required} == expected,
                "original checkout omitted")
        require(len({r["path"] for r in before}) == len(before), "original checkout paths alias")
        for row in before:
            absolute(row["path"])
            require(row["projectKey"] in PROJECTS and row["kind"] in ("root", "nested", "additional"),
                    "unexpected preserved checkout")
            if row["kind"] == "additional":
                project_root = next(r["path"] for r in required if r["projectKey"] == row["projectKey"]
                                    and r["kind"] == "root")
                require(absolute(row["path"]).is_relative_to(absolute(project_root)),
                        "additional repository is outside its project")
            require(HEX40.fullmatch(row["head"]), "original checkout commit missing")
            require(isinstance(row["branch"], str), "original branch missing")
            for field in ("statusSha256", "gitConfigSha256", "indexSha256"):
                require(HEX64.fullmatch(row[field]), "original state hash missing")
        scoped = None
        if "gitConfigurationInterval" in item:
            spec = importlib.util.spec_from_file_location("product_preservation_window",
                Path(__file__).with_name("product_preservation_window.py"))
            window = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(window)
            scoped = window.validate_interval(evidence, item, advances)
        else:
            normalized_after = list(after)
            if host == "m4":
                for advance in advances.values():
                    prior, current = advance["preservation"]["before"], advance["preservation"]["after"]
                    require(before.count(prior) == 1 and after.count(current) == 1,
                            "checkpoint advance does not bind exact preservation rows")
                    require(time_value(item["beforeAt"]) <= time_value(advance["finishedAt"])
                            <= time_value(item["afterAt"]), "checkpoint advance outside preservation interval")
                    normalized_after[normalized_after.index(current)] = prior
            require(sorted(before, key=lambda r: r["path"]) == sorted(normalized_after, key=lambda r: r["path"]),
                    "an original checkout changed")
        require(time_value(item["afterAt"]) >= time_value(item["beforeAt"]), "preservation interval invalid")
        require(time_value(item["configAfterAt"]) >= time_value(item["configBeforeAt"]),
                "configuration preservation interval invalid")
        private_before, private_after = item["privateFilesBefore"], item["privateFilesAfter"]
        require(len(private_before) == (0 if host == "m4" else 7)
                and private_before == private_after, "private project configuration changed or omitted")
        require(len({r["path"] for r in private_before}) == len(private_before), "private file paths alias")
        roots = [absolute(r["path"]) for r in required if r["kind"] == "root"]
        for row in private_before:
            require(any(absolute(row["path"]).is_relative_to(p) for p in roots)
                    and row["exists"] is True and row["size"] > 0 and row["mode"] == "0600"
                    and HEX64.fullmatch(row["sha256"]), "invalid private project file preservation")
        configs_before, configs_after = item["configFilesBefore"], item["configFilesAfter"]
        require(configs_before == configs_after and len(configs_before) == len(before)
                and {r["path"] for r in configs_before} == {r["path"] + "/.specweave/config.json" for r in before},
                "project configuration changed or omitted")
        for row in configs_before:
            require(isinstance(row["exists"], bool), "configuration existence missing")
            if row["exists"]:
                require(row["size"] >= 0 and HEX64.fullmatch(row["sha256"])
                        and re.fullmatch(r"0[0-7]{3}", row["mode"]), "configuration hash/mode missing")
        records[host] = item if scoped is None else {**item, "verifiedGitConfigurationInterval": scoped}
    return records


def ui_selection(evidence, reference, source, plan, bundle, existing_project):
    ui = evidence.bound(evidence.json(reference))
    operation = bundle["manifest"]["operationId"]
    require(ui["operationId"] == operation and ui["bundleDigest"] == bundle["digest"], "UI operation mismatch")
    require(ui["source"] == {"environmentId": source["environmentId"], "projectId": source["projectId"],
                             "threadId": source["coordinatorId"]}, "wrong UI source")
    require(ui["destination"] == {"environmentId": plan["environmentId"], "projectId": existing_project["id"]},
            "wrong selected destination")
    require(ui["entryPoint"] == "ordinary-coordinator" and ui["usageLimitRequired"] is False,
            "ordinary product entrypoint was not observed")
    actions = ui["actions"]
    require([a["action"] for a in actions] == ["open-handoff", "select-destination", "confirm-transfer"],
            "ordered visible handoff actions missing")
    times = [time_value(a["observedAt"]) for a in actions]
    require(times == sorted(times), "UI actions out of order")
    for action in actions:
        require(time_value(action["startedAt"]) <= time_value(action["observedAt"]), "UI action interval invalid")
        snapshot = evidence.data(action["snapshot"]).decode()
        require(text(action["observation"], "UI observation missing") in snapshot,
                "UI observation not present in retained raw snapshot")
        pixels = evidence.data(action["screenshot"])
        require(pixels.startswith(b"\x89PNG\r\n\x1a\n") or pixels.startswith(b"\xff\xd8\xff"),
                "UI screenshot is not a retained image")
    selected = actions[1]
    require(selected["environmentId"] == plan["environmentId"]
            and selected["projectId"] == existing_project["id"], "UI target selection differs from receive")
    review = evidence.data(ui["visualReview"]).decode()
    require(ui["reviewer"] and ui["reviewer"] in review and operation in review
            and selected["observation"] in review, "explicit visual review of selected destination missing")
    return ui


# Keep exact launch-wire validation separate from the preservation verifier.
_launch_spec = importlib.util.spec_from_file_location("product_handoff_launch",
    Path(__file__).with_name("product_handoff_launch.py"))
_launch = importlib.util.module_from_spec(_launch_spec)
_launch_spec.loader.exec_module(_launch)
product_prompt, product_launch = _launch.product_prompt, _launch.product_launch


def product_handoff(root):
    evidence = Evidence(root)
    section = evidence.index["handoff"]
    advances, advance_refs = {}, {}
    for route in section["routes"]:
        if "sourceCheckpointAdvance" not in route:
            continue
        key = route["key"]
        require(key == "sw-easychamp", "checkpoint advance outside owned cleanup")
        entries = [item for item in section["sources"] if item["key"] == key]
        require(len(entries) == 1, "checkpoint source entry missing or duplicated")
        reference = route["sourceCheckpointAdvance"]
        require(advance_refs.setdefault(key, reference) == reference, "routes use different checkpoint advances")
        if key not in advances:
            advances[key] = source_checkpoint(evidence, entries[0], reference)
    for route in section["routes"]:
        if route["key"] in advances:
            require(route.get("sourceCheckpointAdvance") == advance_refs[route["key"]],
                    "both routes require the same reviewed source checkpoint")
    preserved = preservation(evidence, section["preservation"], advances)
    require(len(section["sources"]) == 3 and {s["key"] for s in section["sources"]} == set(PROJECTS),
            "three distinct source diagnostics required")
    sources, identities, workers, environments = {}, {}, set(), {}
    for item in section["sources"]:
        key = item["key"]
        plan, native = replay(evidence, item["plan"], item["native"])
        require(plan["mode"] == "source" and plan["host"] == "m4", "wrong source native mode")
        observed = source_runtime(evidence, item["start"], plan, key)
        require(environments.setdefault("m4", plan["environmentId"]) == plan["environmentId"],
                "multiple M4 source environments")
        for kind, path_field in (("root", "workspaceRoot"), ("nested", "nestedRoot")):
            original = next(r for r in preserved["m4"]["before"]
                            if r["projectKey"] == key and r["kind"] == kind)
            require(original["path"] == plan[path_field] and original["head"] == plan["originalShas"][kind],
                    "M4 preservation does not cover actual owned source checkout")
        bracket(preserved, "m4", native_times(native) + [observed["observedAt"]])
        project = evidence.json(item["project"])
        require(project["id"] == plan["projectId"] and project["workspaceRoot"] == plan["workspaceRoot"],
                "source project workspace mismatch")
        require(set(item["files"]) == {"implementation", "test", "readme", "continuation"}, "source fixture files missing")
        for name, reference in item["files"].items():
            evidence.path(reference)
            require(reference["sha256"] == plan["frozen"][name], "source frozen bytes mismatch")
        relative = str(absolute(plan["nestedRoot"]).relative_to(absolute(plan["workspaceRoot"])))
        identities[key] = item["repositoryIdentities"]
        require(identities[key] == {".": "github.com/anton-abyzov/" + REPOSITORIES[key][0],
                                   relative: "github.com/anton-abyzov/" + REPOSITORIES[key][1]},
                "unexpected root/nested repository identity")
        worker = native["outcome"]["workerThreadId"]
        require(worker not in workers, "source worker reused")
        workers.add(worker)
        sources[key] = (plan, native, relative, item)
    routes = section["routes"]
    require(len(routes) == 6 and {(r["key"], r["host"]) for r in routes}
            == {(p, h) for p in PROJECTS for h in HOSTS}, "six distinct product routes required")
    operations, workspaces = set(), set()
    for route in routes:
        key, host = route["key"], route["host"]
        source, source_native, relative, source_entry = sources[key]
        plan, native = replay(evidence, route["plan"], route["native"])
        require(plan["host"] == host and plan["mode"] == "destination", "wrong destination native mode")
        checkpoint = advances.get(key)
        source_pins = checkpoint["newShas"] if checkpoint else source["originalShas"]
        require(plan["originalShas"] == source_pins, "destination source pins differ")
        require(str(absolute(plan["nestedRoot"]).relative_to(absolute(plan["workspaceRoot"]))) == relative,
                "destination nested path differs")
        require(plan["contextRequired"] == source["contextRequired"], "continuation decisions changed")
        require(plan["expectedTestCount"] == source["expectedTestCount"], "destination test count changed")
        require(plan["branch"] == f"codex/0907-product-{key}-{host}"
                and plan["commitMessage"] == f"0907: Complete {key} handoff diagnostic", "wrong diagnostic branch or commit")
        for name in ("implementation", "test", "readme", "continuation"):
            require(plan["frozen"][name] == source["frozen"][name], "destination fixture bytes differ")
            require(absolute(plan["paths"][name]).relative_to(absolute(plan["workspaceRoot"]))
                    == absolute(source["paths"][name]).relative_to(absolute(source["workspaceRoot"])),
                    "destination fixture path differs")
        observed = runtime(evidence, route["runtime"], host)
        if "serviceReadback" in observed:
            service = evidence.json(observed["serviceReadback"])
            require(time_value(service["observedAt"]) <= min(time_value(at) for at in native_times(native)),
                    "worker candidate service readback postdates native execution")
        require(observed["environmentId"] == plan["environmentId"] != source["environmentId"],
                "destination environment mismatch")
        require(environments.setdefault(host, plan["environmentId"]) == plan["environmentId"],
                "multiple environments for one destination host")
        require(len(set(environments.values())) == len(environments), "different machines share an environment ID")
        transfer_runtime = runtime(evidence, route["sourceRuntime"], "m4")
        require(transfer_runtime["environmentId"] == source["environmentId"], "transfer source environment differs")
        bracket(preserved, host, native_times(native))
        bracket(preserved, host, native_times(native), configuration=True)
        saved = evidence.json(route["sourceRecord"])
        bundle = saved["bundle"]
        bracket(preserved, "m4", [bundle["createdAt"]])
        bracket(preserved, "m4", [bundle["createdAt"]], configuration=True)
        require(time_value(bundle["createdAt"]) >= max(time_value(at) for at in native_times(source_native)),
                "bundle predates completed source characterization")
        require(saved["publication"] == "published", "product did not publish source pins")
        require(bundle["digest"] == digest(canonical({k: v for k, v in bundle.items() if k != "digest"})),
                "product bundle digest mismatch")
        require(bundle["sourceEnvironmentId"] == source["environmentId"]
                and bundle["sourceProjectId"] == source["projectId"]
                and bundle["sourceThreadId"] == source["coordinatorId"], "bundle source identity mismatch")
        manifest = bundle["manifest"]
        operation = manifest["operationId"]
        require(UUID.fullmatch(operation) and operation == plan["operationId"] and operation not in operations,
                "operation missing, wrong or reused")
        operations.add(operation)
        require(manifest["version"] == 1 and len(manifest["repositories"]) == 2, "root/nested manifest required")
        if checkpoint:
            require(source_checkpoint(evidence, source_entry, route["sourceCheckpointAdvance"],
                                      route["sourceRecord"]) == checkpoint, "checkpoint bundle replay differs")
        expected = {".": source_pins["root"], relative: source_pins["nested"]}
        require(manifest["repositories"][0]["relativePath"] == "."
                and {r["relativePath"] for r in manifest["repositories"]} == set(expected), "manifest paths differ")
        for repo in manifest["repositories"]:
            require(repo["head"] == expected[repo["relativePath"]]
                    and repo["identity"] == identities[key][repo["relativePath"]]
                    and repo["ref"] == f"refs/heads/codex/handoff/{operation}/{repo['head']}", "wrong published repository pin")
        threads = bundle["context"]["threads"]
        source_context(evidence, source_entry, source, source_native, route, bundle)
        for thread_id, output in ((source["coordinatorId"], source_native["outcome"]["relayText"]),
                                  (source_native["outcome"]["workerThreadId"], source_native["outcome"]["workerText"])):
            require(any(t["threadId"] == thread_id and any(m["role"] == "assistant" and output in m["text"]
                        for m in t["messages"]) for t in threads), "actual source continuation text missing from bundle")
        context_bytes = evidence.data(route["context"])
        require(decode(context_bytes) == bundle and digest(context_bytes) == plan["frozen"]["context"],
                "destination retained context differs from product bundle")
        destination = evidence.json(route["destinationRecord"])
        require(destination["digest"] == bundle["digest"] and destination["configured"] is True,
                "destination server record mismatch")
        receive = destination["receipt"]
        require(receive["operationId"] == operation and receive["phase"] == "started"
                and receive["projectId"] == plan["projectId"] == "machine-handoff:" + operation
                and receive["coordinatorThreadId"] == plan["coordinatorId"]
                and receive["workspacePath"] == plan["workspaceRoot"]
                and receive["contextPath"] == plan["paths"]["context"], "product receive/native workspace mismatch")
        existing = evidence.json(route["destinationProject"])
        created = evidence.json(route["operationProject"])
        require(existing["id"] == destination["destinationProjectId"] != plan["projectId"], "selected project identity mismatch")
        require(created["id"] == plan["projectId"] and created["workspaceRoot"] == plan["workspaceRoot"],
                "operation project readback mismatch")
        original = next(r for r in preserved[host]["before"] if r["projectKey"] == key and r["kind"] == "root")
        require(existing["workspaceRoot"] == original["path"] and plan["workspaceRoot"] != original["path"],
                "product did not isolate the destination checkout")
        git_operation = evidence.json(route["gitOperation"])
        require(set(git_operation) == {"version", "manifestSha256", "registeredRoot", "manifest"}
                and git_operation["version"] == 1
                and git_operation["registeredRoot"] == existing["workspaceRoot"]
                and git_operation["manifest"] == manifest,
                "persisted Git operation differs from selected project or bundle")
        # handoffGit uses JSON.stringify(manifest), preserving insertion order;
        # this is deliberately different from the bundle's canonical digest.
        serialized_manifest = json.dumps(git_operation["manifest"], ensure_ascii=False,
                                         separators=(",", ":"), allow_nan=False).encode()
        require(git_operation["manifestSha256"] == digest(serialized_manifest),
                "persisted Git operation manifest hash mismatch")
        require(plan["workspaceRoot"] not in workspaces, "destination workspace reused")
        workspaces.add(plan["workspaceRoot"])
        parent = native["parent"]
        graph = native.get("workflowVersion") == 2
        initial_run = next(r for r in parent["runs"] if
                           (r["id"] == native["outcome"]["initialRunId"] if graph
                            else r["id"] != native["outcome"]["automaticWakeRunId"]))
        initial = next(m for m in parent["messages"] if m["id"] == initial_run["userMessageId"])
        product_launch(destination, initial, bundle)
        route_workers = native["outcome"]["workerThreadIds"] if graph else [native["outcome"]["workerThreadId"]]
        require(len(set(route_workers)) == len(route_workers) and not set(route_workers) & workers,
                "destination worker was reused")
        workers.update(route_workers)
        ui = ui_selection(evidence, route["ui"], source, plan, bundle, existing)
        transfer_app = evidence.json(transfer_runtime["wrapperReadback"])
        installed = evidence.json(transfer_app["nativeProcessProof"])
        require(time_value(installed["at"]) <= time_value(ui["actions"][0]["startedAt"]),
                "candidate native installation postdates source UI actions")
        bracket(preserved, "m4", [at for action in ui["actions"] for at in (action["startedAt"], action["observedAt"])])
        for ui_host in ("m4", host):
            bracket(preserved, ui_host, [at for action in ui["actions"]
                    for at in (action["startedAt"], action["observedAt"])], configuration=True)
        require(time_value(ui["actions"][-1]["startedAt"]) <= time_value(initial_run["startedAt"]),
                "destination was already running before UI confirmation")

    scoped = [p["verifiedGitConfigurationInterval"] for p in preserved.values() if "verifiedGitConfigurationInterval" in p]
    return {"gitConfigurationIntervals": scoped} if scoped else None


PHASES = {"product-code": product_code, "product-review": product_review,
          "product-release": product_release, "product-handoff": product_handoff}
