"""Validate retained release evidence, without claiming Google or global coverage."""
import gzip
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

BASE = Path(__file__).resolve().parents[1]
REPORTS = BASE / 'reports'


def read(name):
    return json.loads((REPORTS / name).read_text())


def read_lines(name):
    return [json.loads(line) for line in (REPORTS / name).read_text().splitlines()]


def plan_nodes(node):
    yield node
    for child in node.get('Plans', []):
        yield from plan_nodes(child)


public = read('public-verification-all.json')
assert public['passed'] == len(public['results']) == 120
assert public['failed'] == 0 and not public['errors']
assert len({row['url'] for row in public['results']}) == 120

design = read('public-design/specweave.json')
assert design['passed'] == len(design['results']) == 32
assert design['failed'] == 0 and not design['errors']

help_release = read('help-player-final-release-receipt.json')
assert help_release['deployment']['status'] == help_release['public']['status'] == 'passed'
assert help_release['mergedCommit'] == help_release['deployment']['exactSha']
assert help_release['deployment']['replicas'] == help_release['deployment']['ready'] == help_release['deployment']['updated'] == 2
assert {sample['width'] for sample in help_release['public']['isolatedPlayback']} == {320, 390}
assert len(help_release['public']['isolatedPlayback']) == 2
ci = read(help_release['deployment']['ciReceipt'])
assert ci['headSha'] == help_release['mergedCommit'] and ci['conclusion'] == 'success'
assert len(ci['jobs']) == 3 and all(job['conclusion'] == 'success' for job in ci['jobs'])
cluster = read(help_release['deployment']['clusterReceipt'])
landing = next(row for row in cluster['deployments'] if row['name'] == 'ec-landing')
assert landing['images'] == [help_release['deployment']['image']]
assert landing['replicas'] == landing['ready'] == landing['updated'] == 2
assert landing['argocdRevision'] == help_release['deployment']['gitopsCommit']
assert landing['argocdSync'] == 'Synced' and landing['argocdHealth'] == 'Healthy'
assert len(landing['pods']) == 2
for pod in landing['pods']:
    assert pod['phase'] == 'Running'
    assert all(container['ready'] and container['imageID'] == help_release['deployment']['digest'] for container in pod['containers'])
raw = read(help_release['public']['receipt'])
assert raw['status'] == 'passed' and raw['headless'] is True
assert len(raw['rawHtml']) == 12 and sum(row['videoObjects'] for row in raw['rawHtml']) == 14
assert sum(row['iframes'] for row in raw['rawHtml']) == 14
assert len(raw['geometry']) == 36 and sum(len(row['players']) for row in raw['geometry']) == 42
for row in raw['geometry']:
    assert row['scrollWidth'] <= row['width']
    for player in row['players']:
        assert player['width'] >= 200 and player['height'] >= 200
        assert player['display'] != 'none' and player['visibility'] == 'visible'
        assert player['opacity'] == '1' and player['overlayButtons'] == 0
assert help_release['public']['rawPages'] == 12
assert help_release['public']['videoObjects'] == help_release['public']['matchingInitialPlayers'] == 14
assert help_release['public']['geometryRows'] == 36
for sample in help_release['public']['isolatedPlayback']:
    standalone = read(sample['receipt'])
    assert standalone['headless'] is True and standalone['status'] == 'passed'
    assert standalone['width'] == sample['width']
    assert standalone['before'] == sample['before'] and standalone['after'] == sample['after']
    assert sample['status'] == 'passed'
    assert sample['before']['paused'] and sample['before']['time'] == 0
    assert not sample['after']['paused'] and sample['after']['time'] > 1
    assert sample['after']['readyState'] == 4

vskill = read('vskill-index-current-release-receipt.json')
assert vskill['source']['mergedMain'] == '4e4690cad68bc3b19e4fdf17ba774f4cd46f52ce'
assert vskill['source']['applicationPublicConfigDependencySourceIdentical'] is True
assert vskill['source']['mergedWorkerBuild'] == vskill['source']['queueHealthBuild'] == 'PASS'
checks = read('vskill-pr89-checks.json')
assert len(checks) == 4 and all(row['state'] == 'SUCCESS' for row in checks)
applied = read('vskill-index-production-apply.json')
assert applied['migrationRecorded'] and applied['before']['index'] is None
assert applied['checksum'] == vskill['database']['checksum']
assert applied['after']['oid'] == vskill['database']['index']['oid'] == '199021'
assert applied['after']['definition'] == vskill['database']['index']['definition']
assert all(applied['after'][flag] for flag in ['indisvalid', 'indisready', 'indislive'])
plans = read_lines('vskill-merged-query-plan-after-visible.jsonl')
assert len(plans) == 3
for row, milliseconds in zip(plans, vskill['performance']['databaseExecutionMs']):
    plan = row['plan'][0]['QUERY PLAN'][0]
    assert plan['Execution Time'] == milliseconds and milliseconds < 10000
    assert any(node['Node Type'] == 'Index Only Scan' and node.get('Index Name') == 'Skill_public_author_metrics_idx'
               for node in plan_nodes(plan['Plan']))
source = read_lines('vskill-index-source-proof.jsonl')
assert len(source) == vskill['performance']['actualSourceMatrixCases'] == 13
assert all(row.get('allUntainted', True) and row.get('allMatch', True) for row in source)
http = read('vskill-publisher-index-release-existing-worker.json')
assert len(http) == vskill['performance']['publicMatrixAssertions'] == 31
assert max(row['elapsedSeconds'] for row in http) == vskill['performance']['publicMaxResponseSeconds']
assert all(row['status'] == (404 if row['path'].startswith('/publishers?') and parse_qs(urlsplit(row['path']).query).get('page') == ['999999'] else 200) for row in http)
assert sum(row['status'] == 404 and row['cards'] == 0 for row in http) == 2
uncached = read('vskill-index-uncached-sort-proof.json')
assert len(uncached) == 3
assert all(row['status'] == 200 and row['cards'] == 21 and row['total'] == vskill['performance']['publicTotalAtMatrix']
           and row['publisherKVCacheEligible'] is False and row['elapsedSeconds'] < 10 for row in uncached)
assert vskill['verification']['headlessExplicit'] is True
assert vskill['verification']['headlessProductionCasesPassed'] == 6
assert '6 passed' in (REPORTS / 'vskill-index-production-headless.log').read_text()
assert len(list((REPORTS / 'vskill-index-production-headless').rglob('*.png'))) == 20
coverage = read('vskill-public-index-coverage/coverage-summary.json')['total']
assert coverage['lines']['pct'] == coverage['statements']['pct'] == vskill['coverage']['globalLinesAndStatementsPct'] == 48.97
assert vskill['coverage']['enforcedExitCode'] == 1 and vskill['coverage']['unchangedRequiredThresholdPct'] == 60
assert vskill['coverage']['thresholdsAndExcludesWeakened'] is False
assert vskill['gates']['sourceReviewCiUnitsBuild'] == vskill['gates']['databaseIndexMigrationAndDefaultPlanner'] == 'PASS'
assert vskill['gates']['publicFunctionalMetadataDataPlaybackDesign'] == 'PASS'
if not vskill['worker']['newRolloutPerformed']:
    assert vskill['worker']['freshPostIndexIdentityReadback'] == 'PENDING_AUTH'
    assert vskill['performance']['defaultKeyAbsenceAuthenticatedImmediatelyBefore'] is False
    assert vskill['gates']['freshAuthenticatedWorkerRolloutAndBindings'] == 'BLOCKED_CLOUDFLARE_AUTH'
    assert vskill['gates']['authenticatedDefaultKvAbsenceHitProof'] == 'BLOCKED_CLOUDFLARE_AUTH'

for filename in ['source-tests/manifest.json', 'help-player-artifact-manifest.json', 'vskill-index-artifact-manifest.json']:
    for row in read(filename)['files']:
        path = REPORTS / row['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['archivedSha256'], path
        compressed = Path(str(path) + '.gz')
        if compressed.exists():
            assert hashlib.sha256(gzip.decompress(compressed.read_bytes())).hexdigest() == row['originalSha256'], compressed

secret = re.compile(r'(?:AIza[\w-]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{32,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
sensitive_query = re.compile(r'https?://[^\s\"<>]*[?&](?:access_token|token|signature|sig|key|utm_\w+|gclid|fbclid)=[^&\s\"<>]+', re.IGNORECASE)
credential_url = re.compile(r'(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^/\s:\"]+:[^@/\s\"]+@', re.IGNORECASE)
checked = 0
for path in BASE.rglob('*'):
    if not path.is_file() or '__pycache__' in path.parts or path.suffix in {'.png', '.jpg'}:
        continue
    raw = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    content = raw.decode('utf-8')
    if path.suffix != '.gz':
        assert len(content.splitlines()) <= 1500, path
    assert not secret.search(content), f'secret-shaped value in {path}'
    assert not sensitive_query.search(content), f'credential or tracking query in {path}'
    assert not credential_url.search(content), f'credential-bearing database URL in {path}'
    checked += 1

assert json.loads((BASE / 'metadata.json').read_text())['status'] == 'active'
print(f'PASS: 120 public checks, 32 design cases, Help deployment/playback, Verified Skills live index/uncached queries/headless proof, archive hashes and {checked} text artifacts; rollout/auth and global coverage gates remain explicit')
