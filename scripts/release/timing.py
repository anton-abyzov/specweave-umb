#!/usr/bin/env python3
"""Release timing records, regression check and CI workflow lint.

  timing.py ingest FILE | --gh SLUG RUN_ID [--cache-log]   add step timings from `gh run view --json jobs`
  timing.py record --repo R --step S --seconds N [...]       add one record (release phases, local suites)
  timing.py check [--ratio 1.5] [--floor 60] [--json]       flag slow steps and permanent cache misses (exit 2)
  timing.py scan-ci PATH... [--json] [--history]            lint .github/workflows in each repo
  timing.py --self-test                                      run the inline fixtures

Records live in .specweave/metrics/release-timings.jsonl, one JSON object per line.
"""
import argparse
import datetime
import fcntl
import json
import os
import pathlib
import re
import statistics
import subprocess
import sys
import tempfile
import unittest
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_LOG = pathlib.Path(os.environ.get('RELEASE_TIMINGS_LOG') or ROOT / '.specweave' / 'metrics' / 'release-timings.jsonl')
MANIFEST = ROOT / '.specweave' / 'release' / 'manifest.json'
RUN_FIELDS = 'databaseId,workflowName,headSha,headBranch,event,conclusion,createdAt,startedAt,updatedAt,attempt,url,jobs'


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_time(value):
    if not value or value.startswith('0001-'):
        return None
    return datetime.datetime.strptime(value[:19], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=datetime.timezone.utc)


def span(start, end):
    a, b = parse_time(start), parse_time(end)
    if a is None or b is None or b < a:
        return None
    return (b - a).total_seconds()


def gh(args, timeout=120):
    result = subprocess.run(['gh'] + args, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise SystemExit('gh %s failed: %s' % (args[0], (result.stderr.strip().splitlines() or ['?'])[-1]))
    return result.stdout


# ---------------------------------------------------------------- records

def load(log):
    records = []
    if log.exists():
        for number, line in enumerate(log.read_text().splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except ValueError:
                print('warning: %s:%d is not JSON, skipped' % (log, number), file=sys.stderr)
    return records


def identity(record):
    if record.get('run_id') is None:
        return None
    return (record.get('repo'), record.get('run_id'), record.get('attempt'), record.get('job'),
            record.get('step'), record.get('kind'))


def append(log, new_records):
    # Parallel tracks and ci-wait calls append at once: hold a lock across the
    # dedupe read and the write.
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(str(log) + '.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        known = {identity(r) for r in load(log)}
        fresh = []
        for record in new_records:
            key = identity(record)
            if key is not None and key in known:
                continue
            known.add(key)
            fresh.append(record)
        if fresh:
            with log.open('a') as stream:
                for record in fresh:
                    stream.write(json.dumps(record, sort_keys=True) + '\n')
    return fresh


def slug_from_url(url):
    match = re.match(r'https://github\.com/([^/]+/[^/]+)/', url or '')
    return match.group(1) if match else None


def records_from_run(run, repo=None):
    repo = repo or slug_from_url(run.get('url'))
    if not repo:
        raise SystemExit('cannot tell the repo of this run; pass --repo')
    base = {'repo': repo, 'workflow': run.get('workflowName'), 'run_id': run.get('databaseId'),
            'attempt': run.get('attempt'), 'sha': run.get('headSha'), 'branch': run.get('headBranch'),
            'event': run.get('event'), 'source': 'gh'}
    out = []
    jobs = run.get('jobs') or []
    total = span(run.get('startedAt') or run.get('createdAt'), run.get('updatedAt'))
    if total is not None:
        out.append(dict(base, kind='run', job=None, step=None, seconds=total, conclusion=run.get('conclusion'),
                        at=run.get('updatedAt')))
    for job in jobs:
        seconds = span(job.get('startedAt'), job.get('completedAt'))
        if seconds is not None:
            out.append(dict(base, kind='job', job=job.get('name'), step=None, seconds=seconds,
                            conclusion=job.get('conclusion'), at=job.get('completedAt')))
        for step in job.get('steps') or []:
            seconds = span(step.get('startedAt'), step.get('completedAt'))
            if seconds is None or step.get('conclusion') == 'skipped':
                continue
            out.append(dict(base, kind='step', job=job.get('name'), step=step.get('name'), seconds=seconds,
                            conclusion=step.get('conclusion'), at=step.get('completedAt')))
    return out


CACHE_PATTERNS = [
    (re.compile(r'No cache found|Cache not found for input keys|(npm|pnpm|yarn|pip) cache is not found'), False),
    (re.compile(r'Cache restored from key|Restored from cache key'), True),
]
GROUP_RUN = re.compile(r'##\[group\]Run (\S+)')


def cache_label(uses):
    """`Swatinem/rust-cache@v2` -> `Swatinem/rust-cache`: a version bump keeps the history."""
    return uses.split('@', 1)[0]


def cache_events(log_text):
    """[(step label, hit)] from a job log, attributed to the last `Run <action>` group."""
    events, current = [], None
    for line in log_text.splitlines():
        group = GROUP_RUN.search(line)
        if group:
            current = cache_label(group.group(1))
            continue
        for pattern, hit in CACHE_PATTERNS:
            if pattern.search(line):
                events.append((current or 'cache', hit))
                break
    return events


def records_from_cache_logs(run, repo):
    out = []
    for job in run.get('jobs') or []:
        job_id = job.get('databaseId')
        if not job_id:
            continue
        try:
            text = gh(['api', 'repos/%s/actions/jobs/%s/logs' % (repo, job_id)], timeout=300)
        except SystemExit as error:
            print('warning: no log for job %s: %s' % (job.get('name'), error), file=sys.stderr)
            continue
        for label, hit in cache_events(text):
            out.append({'repo': repo, 'workflow': run.get('workflowName'), 'run_id': run.get('databaseId'),
                        'attempt': run.get('attempt'), 'sha': run.get('headSha'), 'kind': 'cache',
                        'job': job.get('name'), 'step': label, 'hit': hit, 'seconds': 0,
                        'at': job.get('completedAt'), 'source': 'gh-log'})
    return out


def cmd_ingest(args):
    log = pathlib.Path(args.log)
    if args.gh:
        repo, run_id = args.gh
        extra = ['--attempt', str(args.attempt)] if args.attempt else []
        run = json.loads(gh(['run', 'view', str(run_id), '-R', repo, '--json', RUN_FIELDS] + extra))
    else:
        if not args.file:
            raise SystemExit('ingest needs FILE or --gh SLUG RUN_ID')
        text = sys.stdin.read() if args.file == '-' else pathlib.Path(args.file).read_text()
        run, repo = json.loads(text), args.repo
    records = records_from_run(run, repo)
    if args.cache_log:
        records += records_from_cache_logs(run, repo or slug_from_url(run.get('url')))
    fresh = append(log, records)
    print('ingested %d new record(s) from run %s (%d already present)'
          % (len(fresh), run.get('databaseId'), len(records) - len(fresh)))
    return 0


def cmd_record(args):
    record = {'repo': args.repo, 'workflow': args.workflow, 'job': args.job, 'step': args.step,
              'kind': args.kind, 'seconds': float(args.seconds), 'at': args.at or now_iso(),
              'run_id': args.run_id, 'attempt': args.attempt, 'sha': args.sha,
              'conclusion': args.conclusion, 'source': args.source}
    if args.hit is not None:
        record['hit'] = args.hit == 'true'
    if args.note:
        record['note'] = args.note
    fresh = append(pathlib.Path(args.log), [record])
    print('recorded' if fresh else 'already recorded')
    return 0


# ---------------------------------------------------------------- check

def key_of(record):
    step = record.get('step')
    if record.get('kind') == 'cache' and step:
        step = cache_label(step)
    return (record.get('repo'), record.get('workflow'), record.get('job'), step, record.get('kind'))


def label(key):
    repo, workflow, job, step, kind = key
    parts = [p for p in (workflow, job, step) if p]
    return '%s %s [%s]' % (repo, ' / '.join(parts), kind)


def check(records, ratio=1.5, floor=60.0, window=10, min_samples=3, miss_runs=3, include_failed=False, repo=None):
    flags = []
    groups = {}
    for record in records:
        if repo and record.get('repo') != repo:
            continue
        groups.setdefault(key_of(record), []).append(record)
    for key, items in sorted(groups.items(), key=lambda kv: label(kv[0])):
        items.sort(key=lambda r: r.get('at') or '')
        if key[4] == 'cache':
            # One verdict per run: a run hit when any restore under this key hit.
            runs, order = {}, []
            for r in items:
                run = (r.get('run_id'), r.get('attempt')) if r.get('run_id') is not None else ('at', r.get('at'))
                if run not in runs:
                    order.append(run)
                    runs[run] = False
                runs[run] = runs[run] or r.get('hit') is True
            recent = order[-miss_runs:]
            if len(recent) >= miss_runs and not any(runs[run] for run in recent):
                flags.append({'type': 'cache-miss', 'key': label(key), 'runs': len(recent),
                              'message': 'cache missed on the last %d runs' % len(recent)})
            continue
        usable = [r for r in items if include_failed or r.get('conclusion') in (None, 'success')]
        if len(usable) < 2:
            continue
        latest = usable[-1]
        previous = [r for r in usable[:-1] if r.get('run_id') is None or r.get('run_id') != latest.get('run_id')]
        baseline_items = previous[-window:]
        if len(baseline_items) < min_samples:
            continue
        baseline = statistics.median(float(r['seconds']) for r in baseline_items)
        seconds = float(latest['seconds'])
        if seconds > baseline * ratio and seconds - baseline > floor:
            flags.append({'type': 'slow', 'key': label(key), 'seconds': seconds, 'baseline': baseline,
                          'samples': len(baseline_items), 'run_id': latest.get('run_id'),
                          'message': '%.0fs vs baseline %.0fs (median of %d): x%.2f, +%.0fs'
                                     % (seconds, baseline, len(baseline_items), seconds / baseline if baseline else 0,
                                        seconds - baseline)})
    return flags


def cmd_check(args):
    flags = check(load(pathlib.Path(args.log)), args.ratio, args.floor, args.window, args.min_samples,
                  args.miss_runs, args.include_failed, args.repo)
    if args.json:
        print(json.dumps(flags, indent=2))
    else:
        for flag in flags:
            print('%-10s %s: %s' % (flag['type'].upper(), flag['key'], flag['message']))
        print('check: %d flag(s)' % len(flags))
    return 2 if flags else 0


# ---------------------------------------------------------------- scan-ci

RULES = [
    ('job-timeout', 'error', 'job has no timeout-minutes, so a hang runs for the 6-hour default'),
    ('workflow-concurrency', 'warn', 'push/pull_request workflow has no concurrency group; superseded runs keep going'),
    ('push-unfiltered', 'warn', 'push trigger runs on every branch, or skips the paths filter its pull_request has'),
    ('dep-cache-missing', 'warn', 'dependencies installed or compiled without a cache'),
    ('rust-cache-no-main-save', 'warn', 'rust-cache is never saved on the default branch under this key, so it never restores'),
    ('gate-swallowed', 'error', "a gating command ends in '|| true', so it cannot fail"),
    ('continue-on-error', 'warn', 'continue-on-error on a job or step: its failure never blocks'),
    ('unpinned-action', 'warn', 'third-party action is pinned to a tag or branch, not a commit SHA'),
    ('vitest-private-workers', 'warn', 'vitest on a 2-vCPU private-repo runner without --maxWorkers runs on one worker'),
    ('continue-on-error-red', 'warn', 'continue-on-error check is red on most recent PRs (from --history)'),
    ('workflow-invalid', 'error', 'workflow file is not valid YAML, so GitHub cannot run it'),
]
SEVERITY = {rule: severity for rule, severity, _ in RULES}
FIRST_PARTY = ('actions', 'github')
GATING = re.compile(r'\b(test|tests|lint|check|verify|validate|spctl|stapler|codesign|notary|notariz\w*|audit|scan'
                    r'|vitest|jest|pytest|playwright|tsc|eslint|clippy)\b', re.I)
SWALLOW = re.compile(r'\|\|\s*(true|:)\s*(;|$|\)|&&)')
TRIVIAL = re.compile(r'^\s*(echo|printf|rm|kill|pkill|mkdir|ls|cat|cp|mv|ln|chmod|which|command|type|true|docker\s+rm|'
                     r'killall|unlink|rmdir|touch)\b')
INSTALL_JS = re.compile(r'\b(npm\s+(ci|install|i)\b|pnpm\s+(i|install)\b|yarn(\s+install)?\s*($|--))')
INSTALL_PY = re.compile(r'\b(pip3?\s+install|poetry\s+install|uv\s+sync|pipenv\s+install)\b')
CARGO = re.compile(r'\bcargo\s+(build|test|check|clippy|run|install|tauri)\b')
SHA = re.compile(r'^[0-9a-f]{40}$')
EXCLUDE_ARG = re.compile(r'--exclude[= ]+("[^"]*"|\'[^\']*\'|\S+)')
# A command that runs vitest tests (not .vitest-reports paths, vitest-* scripts
# or --merge-reports, which runs no tests).
VITEST_RUN = re.compile(r'(^|[\s;&|(])((npx|bunx|yarn)\s+|pnpm\s+(exec\s+)?|npm\s+exec\s+)?vitest(\s|$)')


def triggers(doc):
    on = doc.get('on', doc.get(True))
    if isinstance(on, str):
        return {on: None}
    if isinstance(on, list):
        return {name: None for name in on}
    return on if isinstance(on, dict) else {}


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def glob_match(pattern, branch):
    regex = '^' + re.escape(pattern).replace(r'\*\*', '.*').replace(r'\*', '[^/]*') + '$'
    return re.match(regex, branch) is not None


def runs_on_default(on, default):
    if 'schedule' in on:
        return True
    if 'push' not in on:
        return False
    push = on.get('push') or {}
    branches = as_list(push.get('branches')) if isinstance(push, dict) else []
    if isinstance(push, dict) and not branches and (push.get('tags') or push.get('tags-ignore')) and not push.get('branches-ignore'):
        return False
    if not branches:
        return True
    return any(glob_match(str(b), default) for b in branches)


def uses_of(step):
    uses = step.get('uses') if isinstance(step, dict) else None
    return uses if isinstance(uses, str) else ''


def action_name(uses):
    return uses.split('@', 1)[0].lower()


def line_of(text, needle, after=0):
    pattern = re.compile(r'^\s*' + re.escape(str(needle)) + r'\s*:', re.M)
    match = pattern.search(text, after)
    return text.count('\n', 0, match.start()) + 1 if match else None


def line_of_literal(text, literal, after=0):
    index = text.find(literal, after)
    return text.count('\n', 0, index) + 1 if index >= 0 else None


def manifest_repos():
    try:
        return json.loads(MANIFEST.read_text()).get('repos', [])
    except (OSError, ValueError):
        return []


def scan_workflow(repo_name, rel, text, doc, private=False, default='main', rust_keys=None):
    findings = []
    jobs_at = text.find('\njobs:')
    jobs_at = 0 if jobs_at < 0 else jobs_at

    def add(rule, job, message, literal=None):
        line = line_of(text, job, jobs_at) if job else None
        if literal:
            start = text.find('\n', jobs_at + 1)
            if line:
                start = len('\n'.join(text.split('\n')[:line - 1]))
            line = line_of_literal(text, literal, max(start, 0)) or line
        findings.append({'rule': rule, 'severity': SEVERITY[rule], 'repo': repo_name, 'file': rel,
                         'line': line, 'job': job, 'message': message})

    if not isinstance(doc, dict):
        return findings
    on = triggers(doc)
    jobs = doc.get('jobs') if isinstance(doc.get('jobs'), dict) else {}
    ci_triggered = 'push' in on or 'pull_request' in on or 'pull_request_target' in on

    if ci_triggered and not doc.get('concurrency') and not all(isinstance(j, dict) and j.get('concurrency') for j in jobs.values()):
        add('workflow-concurrency', None, RULES[1][2])

    if 'push' in on:
        push = on.get('push')
        push = push if isinstance(push, dict) else {}
        filters = ('branches', 'branches-ignore', 'tags', 'tags-ignore', 'paths', 'paths-ignore')
        pr = on.get('pull_request') if isinstance(on.get('pull_request'), dict) else {}
        branches = [str(b) for b in as_list(push.get('branches'))]
        only_default = bool(branches) and all(b == default for b in branches)
        if not any(push.get(f) for f in filters):
            add('push-unfiltered', None, 'push trigger has no branches, tags or paths filter: it runs on every push')
        elif (pr.get('paths') or pr.get('paths-ignore')) and not (push.get('paths') or push.get('paths-ignore')) \
                and not only_default and not push.get('tags'):
            add('push-unfiltered', None, 'push on %s has no paths filter, but pull_request does'
                % (', '.join(branches) or 'every branch'))

    on_default = runs_on_default(on, default)
    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            continue
        name = job_id
        if 'uses' in job:
            uses = job['uses']
            if isinstance(uses, str) and not uses.startswith('./') and uses.split('/')[0].lower() not in FIRST_PARTY \
                    and not SHA.match(uses.rsplit('@', 1)[-1]):
                add('unpinned-action', name, 'reusable workflow %s is not pinned to a SHA' % uses)
            continue
        if job.get('timeout-minutes') is None:
            add('job-timeout', name, RULES[0][2])
        coe = job.get('continue-on-error')
        if coe is True or (isinstance(coe, str) and coe.strip().lower() == 'true'):
            add('continue-on-error', name, 'job-level continue-on-error: the run reports success while this check is red')
        steps = [s for s in (job.get('steps') or []) if isinstance(s, dict)]
        runs_text = '\n'.join(str(s.get('run', '')) for s in steps)
        actions = [action_name(uses_of(s)) for s in steps]
        has_cache_action = any(a in ('actions/cache', 'actions/cache/restore') for a in actions)
        has_local_action = any(a.startswith('./') for a in actions)
        runner = ' '.join(str(x) for x in as_list(job.get('runs-on')))
        for step in steps:
            uses = uses_of(step)
            step_name = str(step.get('name') or uses or step.get('run', '')[:40]).strip()
            if uses and not uses.startswith(('./', 'docker://')):
                owner = uses.split('/')[0].lower()
                ref = uses.rsplit('@', 1)[-1] if '@' in uses else ''
                if owner not in FIRST_PARTY and not SHA.match(ref):
                    add('unpinned-action', name, '%s is not pinned to a commit SHA' % uses, literal=uses)
            scoe = step.get('continue-on-error')
            if scoe is True or (isinstance(scoe, str) and scoe.strip().lower() == 'true'):
                if GATING.search(step_name) or GATING.search(str(step.get('run', ''))):
                    add('continue-on-error', name, "step '%s' has continue-on-error" % step_name, literal=step_name)
            run = str(step.get('run', ''))
            for line in run.splitlines():
                if not SWALLOW.search(line):
                    continue
                command = SWALLOW.split(line)[0]
                if TRIVIAL.match(command) or SWALLOW.search(line).group(2) == ')':
                    continue  # cleanup, or output captured by $(...) and checked afterwards
                if GATING.search(command) or GATING.search(step_name):
                    add('gate-swallowed', name, "step '%s': %s" % (step_name, line.strip()[:120]),
                        literal=line.strip())
            action = action_name(uses)
            with_ = step.get('with') if isinstance(step.get('with'), dict) else {}
            if action == 'actions/setup-node' and not with_.get('cache') and INSTALL_JS.search(runs_text) \
                    and not has_cache_action and not has_local_action:
                add('dep-cache-missing', name, 'setup-node has no cache input and the job installs packages')
            if action == 'actions/setup-python' and not with_.get('cache') and INSTALL_PY.search(runs_text) \
                    and not has_cache_action and not has_local_action:
                add('dep-cache-missing', name, 'setup-python has no cache input and the job installs packages')
            if action == 'swatinem/rust-cache':
                key = str(with_.get('shared-key') or '')
                shared_on_default = key and rust_keys is not None and key in rust_keys
                if not on_default and not shared_on_default:
                    add('rust-cache-no-main-save', name,
                        'rust-cache%s in a workflow that never runs on %s; no main-branch save can feed it'
                        % (" (shared-key '%s')" % key if key else '', default))
        compiles = CARGO.search(runs_text) or any(a == 'tauri-apps/tauri-action' for a in actions)
        if compiles and not any(a in ('swatinem/rust-cache', 'mozilla-actions/sccache-action') for a in actions) \
                and not has_cache_action and not has_local_action:
            add('dep-cache-missing', name, 'job compiles Rust without rust-cache or actions/cache')
        suites = [line for line in runs_text.splitlines() if VITEST_RUN.search(line)
                  and '--merge-reports' not in line and not TRIVIAL.match(line) and not line.lstrip().startswith('#')
                  and not re.search(r'\.(test|spec)\.[cm]?[jt]sx?\b', EXCLUDE_ARG.sub('', line))]
        if private and 'ubuntu' in runner and suites \
                and not any(re.search(r'--max-?workers|maxWorkers=', line, re.I) for line in suites):
            add('vitest-private-workers', name, RULES[8][2], literal=suites[0].strip())
    return findings


def history_red_rate(slug, check_name, prs=20):
    raw = gh(['pr', 'list', '-R', slug, '--state', 'all', '-L', str(prs), '--json', 'headRefOid'])
    reds = total = 0
    for pr in json.loads(raw):
        body = json.loads(gh(['api', 'repos/%s/commits/%s/check-runs?check_name=%s'
                              % (slug, pr['headRefOid'], urllib.parse.quote(check_name, safe=''))]))
        runs = [r for r in body.get('check_runs', []) if r.get('status') == 'completed']
        if not runs:
            continue
        total += 1
        reds += 1 if runs[0].get('conclusion') in ('failure', 'timed_out', 'startup_failure') else 0
    return reds, total


def remote_slug(path):
    """owner/name of the origin remote, or None."""
    try:
        url = subprocess.run(['git', '-C', str(path), 'remote', 'get-url', 'origin'], capture_output=True,
                             text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    match = re.search(r'github\.com[:/]([^/]+/[^/]+?)(\.git)?/?$', url)
    return match.group(1) if match else None


def repo_meta(path, repos):
    """Manifest entry for a checkout: by directory name, else (worktrees) by origin slug."""
    meta = next((r for r in repos if pathlib.Path(r.get('path', '')).name == path.name), None)
    if meta is None:
        slug = remote_slug(path)
        meta = next((r for r in repos if slug and r.get('slug', '').lower() == slug.lower()), None)
    return meta or {}


def scan_repo(path, private=None, history=False):
    import yaml  # PyYAML; only scan-ci needs it.
    path = pathlib.Path(path)
    name = path.name
    meta = repo_meta(path, manifest_repos())
    if private is None:
        private = meta.get('visibility') == 'private'
    default = meta.get('default_branch') or 'main'
    wf_dir = path / '.github' / 'workflows'
    files = sorted(list(wf_dir.glob('*.yml')) + list(wf_dir.glob('*.yaml'))) if wf_dir.is_dir() else []
    parsed = []
    for file in files:
        text = file.read_text()
        try:
            doc = yaml.safe_load(text)
        except yaml.YAMLError as error:
            parsed.append((file, text, None, str(error).splitlines()[0]))
            continue
        parsed.append((file, text, doc, None))
    rust_keys = set()
    for _, _, doc, _ in parsed:
        if not isinstance(doc, dict) or not runs_on_default(triggers(doc), default):
            continue
        for job in (doc.get('jobs') or {}).values():
            for step in (job.get('steps') or []) if isinstance(job, dict) else []:
                if isinstance(step, dict) and action_name(uses_of(step)) == 'swatinem/rust-cache':
                    with_ = step.get('with') if isinstance(step.get('with'), dict) else {}
                    if with_.get('shared-key') and str(with_.get('save-if', 'true')).strip().lower() != 'false':
                        rust_keys.add(str(with_['shared-key']))
    findings = []
    for file, text, doc, error in parsed:
        rel = str(file.relative_to(path))
        if error:
            findings.append({'rule': 'workflow-invalid', 'severity': SEVERITY['workflow-invalid'], 'repo': name,
                             'file': rel, 'line': None, 'job': None, 'message': 'workflow is not valid YAML: ' + error})
            continue
        findings += scan_workflow(name, rel, text, doc, private, default, rust_keys)
    if history:
        slug = meta.get('slug')
        for finding in [f for f in findings if f['rule'] == 'continue-on-error' and f['job']]:
            if not slug:
                break
            reds, total = history_red_rate(slug, finding['job'])
            if total >= 5 and reds / total > 0.8:
                findings.append(dict(finding, rule='continue-on-error-red', severity=SEVERITY['continue-on-error-red'],
                                     message='check %s red on %d of the last %d PRs' % (finding['job'], reds, total)))
    return findings, len(files)


def cmd_scan(args):
    findings, workflows = [], 0
    for path in args.paths:
        if not pathlib.Path(path).is_dir():
            raise SystemExit('not a directory: %s' % path)
        private = True if pathlib.Path(path).name in (args.private or []) else None
        found, count = scan_repo(path, private, args.history)
        findings += found
        workflows += count
    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        for f in findings:
            where = f['file'] + (':%d' % f['line'] if f.get('line') else '')
            print('%-5s %-24s %s/%s%s  %s' % (f['severity'].upper(), f['rule'], f['repo'], where,
                                              ' [%s]' % f['job'] if f.get('job') else '', f['message']))
        by_rule = {}
        for f in findings:
            by_rule[f['rule']] = by_rule.get(f['rule'], 0) + 1
        errors = sum(1 for f in findings if f['severity'] == 'error')
        print('scan-ci: %d finding(s) (%d error, %d warn) in %d workflow(s) across %d repo(s)'
              % (len(findings), errors, len(findings) - errors, workflows, len(args.paths)))
        if by_rule:
            print('by rule: ' + ', '.join('%s=%d' % kv for kv in sorted(by_rule.items())))
    levels = {'none': None, 'warn': ('warn', 'error'), 'error': ('error',)}[args.fail_on]
    return 1 if levels and any(f['severity'] in levels for f in findings) else 0


# ---------------------------------------------------------------- self-test

BAD_WORKFLOW = """
name: bad
on:
  push:
  pull_request:
    paths: ['src/**']
jobs:
  build:
    runs-on: ubuntu-latest
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - uses: dtolnay/rust-toolchain@stable
      - run: npm ci
      - run: npx vitest run --coverage --exclude "src/a.test.tsx"
      - run: npm test || true
      - run: cargo test --locked
  desktop:
    runs-on: macos-latest
    timeout-minutes: 30
    steps:
      - uses: Swatinem/rust-cache@6323deb102c322ba6fcbdcafc7e3dddab59af2b6
      - run: cargo build --release
"""

BAD_TAG_WORKFLOW = """
name: tag-release
on:
  push:
    tags: ['desktop-v*']
concurrency: { group: rel, cancel-in-progress: false }
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - uses: Swatinem/rust-cache@6323deb102c322ba6fcbdcafc7e3dddab59af2b6
        with: { workspaces: 'src-tauri -> target' }
      - run: cargo build --release
"""

SIDE_WORKFLOW = """
name: side
on:
  push:
    branches: ['fix/**']
  pull_request:
    paths: ['src-tauri/**']
concurrency: { group: side, cancel-in-progress: true }
jobs:
  rust:
    runs-on: windows-latest
    timeout-minutes: 20
    steps:
      - uses: Swatinem/rust-cache@6323deb102c322ba6fcbdcafc7e3dddab59af2b6
      - run: cargo test
"""

GOOD_WORKFLOW = """
name: good
on:
  push:
    branches: [main]
  pull_request:
    paths: ['src/**']
concurrency:
  group: good-${{ github.ref }}
  cancel-in-progress: true
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - uses: dtolnay/rust-toolchain@683b588c487a69d01f6c6ddf40f036ff682cc2c8
      - run: npm ci
      - run: npx vitest run --maxWorkers=2
      - run: rm -f stale.lock || true
      - run: |
          HITS=$(grep -rn "process.env.X" src/ 2>/dev/null || true)
          test -z "$HITS"
      - run: npx vitest run tests/one-file.test.ts
      - run: npx vitest run --merge-reports --coverage --reporter=dot
      - run: node scripts/ci/vitest-timing-summary.mjs .vitest-reports
      - run: echo "vitest shards finished"
      - name: Show disk usage
        run: du -sh . || true
  desktop:
    runs-on: macos-latest
    timeout-minutes: 30
    steps:
      - uses: Swatinem/rust-cache@6323deb102c322ba6fcbdcafc7e3dddab59af2b6
        with: { shared-key: desktop-mac }
      - run: cargo build --release
  reuse:
    uses: ./.github/workflows/other.yml
"""

GOOD_TAG_WORKFLOW = """
name: tag-good
on:
  push:
    tags: ['desktop-v*']
concurrency: { group: rel, cancel-in-progress: false }
jobs:
  build:
    runs-on: macos-latest
    timeout-minutes: 60
    steps:
      - uses: Swatinem/rust-cache@6323deb102c322ba6fcbdcafc7e3dddab59af2b6
        with: { shared-key: desktop-mac, save-if: false }
      - run: cargo build --release
"""

RUN_JSON = {
    'databaseId': 101, 'workflowName': 'CI', 'headSha': 'a' * 40, 'headBranch': 'main', 'event': 'push',
    'conclusion': 'success', 'attempt': 1, 'url': 'https://github.com/o/r/actions/runs/101',
    'startedAt': '2026-10-16T10:00:00Z', 'updatedAt': '2026-10-16T10:05:00Z',
    'jobs': [
        {'name': 'unit', 'databaseId': 7, 'startedAt': '2026-10-16T10:00:05Z', 'completedAt': '2026-10-16T10:04:05Z',
         'conclusion': 'success', 'steps': [
             {'name': 'Set up job', 'startedAt': '2026-10-16T10:00:05Z', 'completedAt': '2026-10-16T10:00:10Z',
              'conclusion': 'success'},
             {'name': 'Vitest', 'startedAt': '2026-10-16T10:00:10Z', 'completedAt': '2026-10-16T10:03:30Z',
              'conclusion': 'success'},
             {'name': 'Skipped', 'startedAt': '2026-10-16T10:03:30Z', 'completedAt': '2026-10-16T10:03:30Z',
              'conclusion': 'skipped'}]},
    ],
}

CACHE_LOG = """2026-10-16T14:50:01.0Z ##[group]Run Swatinem/rust-cache@v2
2026-10-16T14:50:02.0Z ... Restoring cache ...
2026-10-16T14:50:03.0Z No cache found.
2026-10-16T14:50:04.0Z ##[group]Run actions/setup-node@v4
2026-10-16T14:50:05.0Z Cache restored from key: node-cache-Linux-x64-npm-abc
2026-10-16T14:50:06.0Z ##[group]Run actions/cache@v4
2026-10-16T14:50:07.0Z Cache not found for input keys: next-cache-abc
"""


def rec(seconds, at, run_id=None, conclusion='success', kind='step', hit=None, step='Vitest'):
    record = {'repo': 'o/r', 'workflow': 'CI', 'job': 'unit', 'step': step, 'kind': kind, 'seconds': seconds,
              'at': at, 'run_id': run_id, 'conclusion': conclusion}
    if hit is not None:
        record['hit'] = hit
    return record


class SelfTest(unittest.TestCase):
    def scan(self, *texts, private=False, default='main'):
        import yaml
        docs = [yaml.safe_load(t) for t in texts]
        keys = set()
        for doc in docs:
            if runs_on_default(triggers(doc), default):
                for job in doc['jobs'].values():
                    for step in job.get('steps', []):
                        if action_name(uses_of(step)) == 'swatinem/rust-cache' and (step.get('with') or {}).get('shared-key'):
                            keys.add(step['with']['shared-key'])
        out = []
        for i, (text, doc) in enumerate(zip(texts, docs)):
            out += scan_workflow('r', 'wf%d.yml' % i, text, doc, private, default, keys)
        return out

    def test_bad_workflow_hits_every_rule(self):
        rules = {f['rule'] for f in self.scan(BAD_WORKFLOW, private=True)}
        for rule in ('job-timeout', 'workflow-concurrency', 'push-unfiltered', 'dep-cache-missing',
                     'gate-swallowed', 'continue-on-error', 'unpinned-action', 'vitest-private-workers'):
            self.assertIn(rule, rules)
        # A bare push trigger also runs on main, so its rust-cache is saved there.
        self.assertNotIn('rust-cache-no-main-save', rules)

    def test_on_key_parsed_as_boolean(self):
        import yaml
        self.assertIn('push', triggers(yaml.safe_load(BAD_WORKFLOW)))

    def test_good_workflows_are_clean(self):
        findings = self.scan(GOOD_WORKFLOW, GOOD_TAG_WORKFLOW, private=True)
        self.assertEqual(findings, [], findings)

    def test_tag_only_rust_cache_without_shared_key(self):
        rules = [f['rule'] for f in self.scan(BAD_TAG_WORKFLOW)]
        self.assertEqual(rules, ['rust-cache-no-main-save'])

    def test_fix_branch_push_without_paths(self):
        found = self.scan(SIDE_WORKFLOW)
        self.assertEqual(sorted(f['rule'] for f in found), ['push-unfiltered', 'rust-cache-no-main-save'])

    def test_vitest_rule_only_for_private_repos(self):
        self.assertNotIn('vitest-private-workers', {f['rule'] for f in self.scan(BAD_WORKFLOW, private=False)})

    def test_slow_step_flagged_with_ratio_and_floor(self):
        base = [rec(s, '2026-10-0%dT00:00:00Z' % (i + 1), run_id=i) for i, s in enumerate([100, 110, 105, 95])]
        flags = check(base + [rec(300, '2026-10-09T00:00:00Z', run_id=9)])
        self.assertEqual([f['type'] for f in flags], ['slow'])
        self.assertEqual(flags[0]['baseline'], 102.5)
        self.assertEqual(check(base + [rec(140, '2026-10-09T00:00:00Z', run_id=9)]), [])

    def test_floor_suppresses_small_absolute_jumps(self):
        base = [rec(10, '2026-10-0%dT00:00:00Z' % (i + 1), run_id=i) for i in range(4)]
        self.assertEqual(check(base + [rec(40, '2026-10-09T00:00:00Z', run_id=9)]), [])

    def test_failed_runs_and_short_history_ignored(self):
        base = [rec(100, '2026-10-0%dT00:00:00Z' % (i + 1), run_id=i) for i in range(4)]
        self.assertEqual(check(base + [rec(900, '2026-10-09T00:00:00Z', run_id=9, conclusion='failure')]), [])
        self.assertEqual(check(base[:2] + [rec(900, '2026-10-09T00:00:00Z', run_id=9)]), [])

    def test_permanent_cache_miss(self):
        misses = [rec(0, '2026-10-0%dT00:00:00Z' % (i + 1), run_id=i, kind='cache', hit=False, step='rust-cache')
                  for i in range(3)]
        self.assertEqual([f['type'] for f in check(misses)], ['cache-miss'])
        mixed = misses[:1] + [rec(0, '2026-10-05T00:00:00Z', run_id=5, kind='cache', hit=True, step='rust-cache')] + misses[1:]
        mixed.sort(key=lambda r: r['at'])
        self.assertEqual(check(mixed), [])

    def test_ingest_and_dedupe(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = pathlib.Path(tmp) / 'timings.jsonl'
            records = records_from_run(RUN_JSON)
            kinds = sorted((r['kind'], r['step'] or '') for r in records)
            self.assertEqual(kinds, [('job', ''), ('run', ''), ('step', 'Set up job'), ('step', 'Vitest')])
            vitest = [r for r in records if r['step'] == 'Vitest'][0]
            self.assertEqual((vitest['seconds'], vitest['repo'], vitest['run_id']), (200.0, 'o/r', 101))
            self.assertEqual(len(append(log, records)), 4)
            self.assertEqual(len(append(log, records_from_run(RUN_JSON))), 0)
            self.assertEqual(len(load(log)), 4)

    def test_cache_log_parse(self):
        self.assertEqual(cache_events(CACHE_LOG), [('Swatinem/rust-cache', False), ('actions/setup-node', True),
                                                   ('actions/cache', False)])

    def test_cache_miss_counts_runs_not_lines(self):
        # Three miss lines from one run are one run, not three.
        one_run = [rec(0, '2026-10-01T00:00:0%dZ' % i, run_id=1, kind='cache', hit=False, step='rust-cache')
                   for i in range(3)]
        self.assertEqual(check(one_run), [])
        # A hit anywhere in a run makes that run a hit.
        runs = [rec(0, '2026-10-0%dT00:00:00Z' % (i + 1), run_id=i, kind='cache', hit=False, step='rust-cache')
                for i in range(3)]
        runs.append(rec(0, '2026-10-03T00:00:01Z', run_id=2, kind='cache', hit=True, step='rust-cache'))
        self.assertEqual(check(runs), [])

    def test_cache_label_ignores_action_version(self):
        old = [rec(0, '2026-10-0%dT00:00:00Z' % (i + 1), run_id=i, kind='cache', hit=False,
                   step='actions/setup-node@v4') for i in range(2)]
        new = [rec(0, '2026-10-05T00:00:00Z', run_id=5, kind='cache', hit=False, step='actions/setup-node@v7')]
        self.assertEqual([f['type'] for f in check(old + new)], ['cache-miss'])

    def test_invalid_yaml_has_its_own_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            wf = pathlib.Path(tmp) / '.github' / 'workflows'
            wf.mkdir(parents=True)
            (wf / 'broken.yml').write_text('on: [push\njobs: {')
            findings, count = scan_repo(tmp)
            self.assertEqual((count, [f['rule'] for f in findings]), (1, ['workflow-invalid']))

    def test_worktree_matched_to_manifest_by_remote(self):
        repos = [{'name': 'vskill-platform', 'slug': 'anton-abyzov/vskill-platform',
                  'path': 'repositories/anton-abyzov/vskill-platform', 'visibility': 'private'}]
        with tempfile.TemporaryDirectory() as tmp:
            checkout = pathlib.Path(tmp) / 'relperf-platform'
            checkout.mkdir()
            subprocess.run(['git', 'init', '-q', str(checkout)], check=True)
            subprocess.run(['git', '-C', str(checkout), 'remote', 'add', 'origin',
                            'https://github.com/anton-abyzov/vskill-platform.git'], check=True)
            self.assertEqual(repo_meta(checkout, repos).get('visibility'), 'private')
            self.assertEqual(repo_meta(pathlib.Path(tmp), repos), {})

    def test_record_cli_appends(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = os.path.join(tmp, 'x.jsonl')
            self.assertEqual(main(['--log', log, 'record', '--repo', 'o/r', '--step', 'server suite',
                                   '--seconds', '1385.1', '--kind', 'suite']), 0)
            rows = load(pathlib.Path(log))
            self.assertEqual((rows[0]['step'], rows[0]['seconds'], rows[0]['kind']), ('server suite', 1385.1, 'suite'))


def self_test():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SelfTest)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


# ---------------------------------------------------------------- cli

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--log', default=str(DEFAULT_LOG), help='timings file (default: %(default)s)')
    parser.add_argument('--self-test', action='store_true')
    sub = parser.add_subparsers(dest='cmd')

    p = sub.add_parser('ingest', help='add timings from gh run view --json')
    p.add_argument('file', nargs='?', help="gh run view --json output, or '-' for stdin")
    p.add_argument('--gh', nargs=2, metavar=('SLUG', 'RUN_ID'), help='fetch the run with gh')
    p.add_argument('--repo', help='owner/name when FILE has no url')
    p.add_argument('--attempt', type=int, help='with --gh: a specific run attempt')
    p.add_argument('--cache-log', action='store_true', help='also parse job logs for cache hits and misses')

    p = sub.add_parser('record', help='add one record')
    p.add_argument('--repo', required=True)
    p.add_argument('--workflow')
    p.add_argument('--job')
    p.add_argument('--step', required=True)
    p.add_argument('--seconds', required=True, type=float)
    p.add_argument('--kind', default='phase', choices=['run', 'job', 'step', 'cache', 'phase', 'wait', 'suite'])
    p.add_argument('--run-id')
    p.add_argument('--attempt', type=int)
    p.add_argument('--sha')
    p.add_argument('--at')
    p.add_argument('--conclusion', default='success')
    p.add_argument('--hit', choices=['true', 'false'])
    p.add_argument('--source', default='manual')
    p.add_argument('--note')

    p = sub.add_parser('check', help='flag regressions against the baseline')
    p.add_argument('--ratio', type=float, default=1.5)
    p.add_argument('--floor', type=float, default=60.0, help='minimum absolute slowdown in seconds')
    p.add_argument('--window', type=int, default=10)
    p.add_argument('--min-samples', type=int, default=3)
    p.add_argument('--miss-runs', type=int, default=3)
    p.add_argument('--include-failed', action='store_true')
    p.add_argument('--repo')
    p.add_argument('--json', action='store_true')

    p = sub.add_parser('scan-ci', help='lint .github/workflows in each repo path')
    p.add_argument('paths', nargs='+')
    p.add_argument('--json', action='store_true')
    p.add_argument('--private', action='append', help='treat this repo dir name as private (repeatable)')
    p.add_argument('--history', action='store_true', help='read recent PR check-runs with gh')
    p.add_argument('--fail-on', choices=['none', 'warn', 'error'], default='error')

    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    handlers = {'ingest': cmd_ingest, 'record': cmd_record, 'check': cmd_check, 'scan-ci': cmd_scan}
    if args.cmd not in handlers:
        parser.print_help()
        return 64
    return handlers[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main())
