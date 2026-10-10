"""Validate retained release evidence, without claiming Google or global coverage."""
import gzip
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

BASE = Path(__file__).resolve().parents[1]
REPORTS = BASE / 'reports'


def read(name):
    return json.loads((REPORTS / name).read_text())


def read_lines(name):
    return [json.loads(line) for line in (REPORTS / name).read_text().splitlines()]


def timestamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


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
else:
    worker = vskill['worker']
    fresh = vskill['postAuthentication']
    rollout = read(worker['proofFile'])
    assert rollout == fresh['rollout']
    assert fresh['source'] == rollout['source'] == worker['source'] == vskill['source']['mergedMain']
    assert fresh['sourceCleanBeforeAndAfterBuild'] and rollout['sourceCleanAfterBuild']
    assert worker['freshPostIndexIdentityReadback'] == 'PASS'
    assert worker['version'] == rollout['currentVersion'] == '230dca40-7d6b-462a-9ed2-48cda828f345'
    assert worker['deployment'] == rollout['deployment']['id'] == 'e92d344b-3892-49f8-83f2-03a02e6b1f5d'
    assert timestamp(public['checkedAt']) > timestamp(worker['deployedAt'])
    assert worker['percentage'] == 100
    assert rollout['deployment']['versions'] == [{'version_id': worker['version'], 'percentage': 100}]
    assert fresh['postProofWorkerIdentityUnchanged']
    assert fresh['canonicalWorkerBuild'] == fresh['queueHealthBuild'] == fresh['queueHealthDeploy'] == 'PASS'
    assert rollout['queueHealthBuild'] == rollout['queueHealthDeploy'] == 'PASS'
    assert rollout['canonicalDeployInitialExit'] == 1 and 'Post-deploy guard lacked' in rollout['canonicalDeployInitialFailure']
    assert not rollout['dbMigrationsRun'] and not rollout['indexReapplied']
    assert rollout['immutableOldNewVersionBindingsExactEquality']
    assert not rollout['preDeploymentLiveConsumerSettingsSnapshotRetained']
    assert not rollout['initialPreDeploymentToolOutput']['fullSnapshotRetained']
    assert all(rollout['retainedLivePostDeploymentSnapshotsParity'].values())
    inventories = []
    for filename, recorded in rollout['retainedLiveSnapshotTimes'].items():
        inventory = read(filename)
        assert timestamp(inventory['recordedAt']) == timestamp(recorded) > timestamp(worker['deployedAt'])
        assert inventory['bindingsCount'] == len(inventory['bindings']) == worker['bindings'] == 66
        assert inventory['consumerCount'] == worker['queueConsumers'] == 6
        assert inventory['producerCount'] == worker['queueProducers'] == 5
        assert len(inventory['cronSchedules']) == worker['cronTriggers'] == 7
        assert all(set(binding) == {'name', 'type', 'signature'} for binding in inventory['bindings'])
        inventories.append(inventory)
    for key in ['bindings', 'cronSchedules']:
        assert all(row[key] == inventories[0][key] for row in inventories)
    # The final readback also retains DLQ names; compare fields present in every
    # post-deploy snapshot, then verify final DLQ mappings against config below.
    queue_snapshots = [[dict(queue, consumers=[{key: consumer[key] for key in ['type', 'script', 'settings']}
                                               for consumer in queue['consumers']])
                        for queue in row['queueInventory']] for row in inventories]
    assert all(row == queue_snapshots[0] for row in queue_snapshots)
    config = read(rollout['actualConfigReadbackFile'])
    actual = read(config['actualInventoryFile'])
    assert config['configUnchangedFromPreviousDeployedSource']
    assert config['currentSource'] == worker['source']
    assert config['previousRuntimeSource'] == vskill['source']['runtimeSourceComparedWith']
    assert config['configSha256'] == '33ac0ba76848b23e1094b16cb536daf254511245a803456f76f2655dba50788e'
    assert rollout['currentActualConsumerProducerCronConfigMatchesByteIdenticalPreviousRuntimeConfig']
    comparisons = config['consumerSettingsComparedWithUnchangedCanonicalConfig']
    assert len(comparisons) == 6
    for comparison in comparisons:
        queue = next(row for row in actual['queueInventory'] if row['queue'] == comparison['queue'])
        assert len(queue['consumers']) == 1
        consumer = queue['consumers'][0]
        assert consumer['settings'] == comparison['actualSettings']
        assert all(consumer['settings'][key] == value for key, value in comparison['expectedSettings'].items())
        assert consumer['deadLetterQueue'] == comparison['deadLetterQueue']
        assert consumer['script'] == comparison['script'] == rollout['worker'] and comparison['parity']
    assert config['producerParity'] and config['cronParity']
    assert config['producerQueues'] == sorted(row['queue'] for row in actual['queueInventory'] if row['producerCount'])
    assert config['cronSchedules'] == actual['cronSchedules']

    cache = read(fresh['defaultPublisherCache']['proofFile'])
    assert cache['workerVersion'] == worker['version']
    assert cache['controlPlaneAbsenceImmediatelyBefore'] and cache['observedWriteThrough']
    assert cache['ssrCachePayloadParity'] and cache['repeatedResponsePayloadParity']
    assert cache['expirationUnchangedDuringRepeatedResponses']
    assert not cache['exactBoundedKeyDeletion'] and not cache['directHitMissTelemetryAvailable']
    events = cache['events']
    assert all(timestamp(a['recordedAt']) < timestamp(b['recordedAt']) for a, b in zip(events, events[1:]))
    assert all(row['status'] == 404 for row in events[:2])
    assert events[2]['kind'] == 'authenticatedExactKeyList' and not events[2]['exactKeys']
    first = next(row for row in events if row['kind'] == 'defaultFirstAfterAuthenticatedAbsence')
    assert first == fresh['defaultPublisherCache']['firstResponse']
    populated = next(row for row in events if row['kind'] == 'authenticatedControlPlaneValue' and row['status'] == 200)
    repeats = [row for row in events if row['kind'] == 'repeatedDefaultResponse']
    api = next(row for row in events if row['kind'] == 'defaultApiPayloadParity')
    assert len(repeats) == 3
    assert all(row['status'] == 200 and row['cards'] == 20 and row['total'] == 101704 for row in [first, populated, *repeats, api])
    assert timestamp(first['recordedAt']) < timestamp(populated['recordedAt'])
    assert [row['elapsedSeconds'] for row in repeats] == fresh['defaultPublisherCache']['repeatedResponseSeconds']
    lists = [row for row in events if row['kind'] == 'authenticatedExactKeyList']
    assert all(not row['unrelatedKeysMutated'] for row in lists)
    assert lists[1]['exactKeys'] == lists[2]['exactKeys']
    assert lists[1]['exactKeys'][0]['name'] == cache['key']
    assert not fresh['defaultPublisherCache']['directHitMissBranchesObserved']
    assert vskill['gates']['authenticatedDefaultKvAbsenceHitProof'] == 'PASS_OBSERVED_ABSENCE_WRITE_THROUGH_PARITY_NO_DIRECT_BRANCH_TELEMETRY'
    assert vskill['gates']['freshAuthenticatedWorkerRolloutAndBindings'] == 'PASS'

    matrix = read(fresh['publicMatrix']['proofFile'])
    assert len(matrix) == fresh['publicMatrix']['assertionsPassed'] == 31
    assert max(row['elapsedSeconds'] for row in matrix) == fresh['publicMatrix']['maxResponseSeconds']
    assert all(row['status'] == (404 if parse_qs(urlsplit(row['path']).query).get('page') == ['999999'] and row['path'].startswith('/publishers?') else 200) for row in matrix)
    assert sum(row['status'] == 404 and row['cards'] == 0 for row in matrix) == 2
    uncached_fresh = read(fresh['guaranteedUncacheableSorts']['proofFile'])
    assert len(uncached_fresh) == 3
    assert {parse_qs(urlsplit(row['path']).query)['sort'][0] for row in uncached_fresh} == {'stars', 'skills', 'trust'}
    assert all(parse_qs(urlsplit(row['path']).query)['limit'] == ['21'] and row['status'] == 200
               and row['cards'] == 21 and row['total'] == 101704 and not row['publisherKVCacheEligible'] for row in uncached_fresh)
    assert [row['elapsedSeconds'] for row in uncached_fresh] == fresh['guaranteedUncacheableSorts']['responseSeconds']
    assert fresh['guaranteedUncacheableSorts']['publisherKvBypassGuaranteedBySourcePredicate']
    assert fresh['guaranteedUncacheableSorts']['freshUniqueSeoProbeUrls']
    assert fresh['guaranteedUncacheableSorts']['apiResponseCacheControl'].startswith('public, max-age=120')
    catalog = read(fresh['freshIndexReadback']['proofFile'])
    assert catalog['readonlyCatalogOnly'] and catalog['index']['oid'] == applied['after']['oid']
    assert catalog['index']['definition'] == applied['after']['definition']
    assert all(catalog['index'][flag] for flag in ['indisvalid', 'indisready', 'indislive'])
    assert catalog['ledger']['finished'] and catalog['ledger']['not_rolled_back']
    assert catalog['ledger']['checksum'] == vskill['database']['checksum']
    headless = fresh['headlessProduction']
    assert headless['casesPassed'] == 6 and headless['workers'] == 1 and headless['retries'] == 0
    assert headless['explicitHeadless'] and headless['PWDEBUG'] == '0'
    assert headless['PLAYWRIGHT_HTML_OPEN'] == headless['htmlReporterOpen'] == 'never'
    assert '6 passed' in (REPORTS / headless['proofFile']).read_text()
    assert len(list((REPORTS / headless['screenshotsDirectory']).rglob('*.png'))) == 20
    release = read(fresh['publishedReleaseMetadata']['proofFile'])
    assert len(release) == 3 and all(row['status'] == 200 for row in release)
    assert all(row.get('visibleCurrentVskillVersion', True) for row in release)
    assert all(release[2][key] for key in ['metadataSkills19', 'hasAllPublishedPluginNames', 'hasFiveNewPublishedSkills', 'specweaveInstallCommandCorrect'])
    archive = read('vskill-index-artifact-manifest.json')
    assert len(archive['files']) == 96 and sum(row['file'].endswith('.png') for row in archive['files']) == 40
    assert len(archive['excluded']) == 2 and all('headless-report/index.html' in row['path'] for row in archive['excluded'])
    assert not (REPORTS / 'vskill-auth-final-predeploy-inventory.json').exists()

mail = read('mailbox-auth-resume-readback.json')
assert mail['mailbox'] == 'admin@easychamp.com' and mail['matchingMessages'] == 88
assert mail['paginationComplete'] and mail['previousInventoryMatchesCurrent']
assert mail['newMatchingMessages'] == mail['removedMatchingMessages'] == 0
easy = read('easychamp-auth-resume-current-release.json')
assert easy['ownersAndCheckoutsPreserved']
current_landing, arena = easy['cluster']['deployments']
assert current_landing['images'] == landing['images']
assert current_landing['ready'] == current_landing['updated'] == current_landing['replicas'] == 2
assert arena['ready'] == arena['updated'] == arena['replicas'] == 5
assert arena['images'] == ['ghcr.io/anton-abyzov/ec-arena-ui:develop-817f749']
assert all(row['argocdSync'] == 'Synced' and row['argocdHealth'] == 'Healthy' for row in [current_landing, arena])
assert all(row['argocdRevision'] == 'f08289e78974443b9be2ae73757089d6bd03c466' for row in [current_landing, arena])
assert all(container['ready'] and container['imageID'] == help_release['deployment']['digest']
           for pod in current_landing['pods'] for container in pod['containers'])
assert all(container['ready'] and container['imageID'].endswith('sha256:6524b9f96fea921f4dbeb3df0d6d0904ddcccb2c251968ce03cfe965aa49f430')
           for pod in arena['pods'] for container in pod['containers'])
assert easy['source'][1]['deployedDescendantOfSEO'] and easy['source'][1]['newerOwnerReleasesPreserved']
assert all(row['seoMergeBlob'] == row['deployedBlob'] == row['latestDevelopBlob'] and row['unchangedSinceSEO'] for row in easy['arenaSEOBlobChecks'])
assert easy['arenaCurrentCI'][0]['conclusion'] == 'failure' and easy['arenaCurrentCI'][1]['conclusion'] == 'success'
watch = read('auth-resume-watch-simulated-crawler-headless.json')
assert watch['headless'] and watch['httpStatus'] == 200 and watch['status'] == 'passed'
assert 'simulated' in watch['proofType'] and 'not actual Google URL Inspection' in watch['proofType']
assert watch['state']['scrollWidth'] <= watch['state']['width'] == 390
assert not any(row.get('@type') == 'VideoObject' for row in watch['state']['nodes'])
raw_watch = read('auth-resume-watch-raw-seo.json')
assert raw_watch['httpStatus'] == 200 and raw_watch['SportsEventCount'] == 1 and raw_watch['VideoObjectCount'] == 0

for filename in ['source-tests/manifest.json', 'help-player-artifact-manifest.json', 'vskill-index-artifact-manifest.json', 'auth-resume-artifact-manifest.json']:
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
print(f'PASS: 120 public checks, 32 design cases, Help deployment/playback, current owner-preserving EasyChamp readback, Verified Skills authenticated rollout/config/cache observation/31 public/3 uncached/6 headless, archive hashes and {checked} text artifacts; global coverage and Google indexing gates remain explicit')
