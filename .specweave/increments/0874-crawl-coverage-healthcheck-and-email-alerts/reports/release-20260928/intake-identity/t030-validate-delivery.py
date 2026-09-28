"""Read-only local receipt validation for bounded T030 closure; no network calls."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
HEAD = '05f9bb6ef6a25026c3cf35f0b63b62bebdb0c4cb'
REVIEW = pathlib.Path('/Users/antonabyzov/.codex/visualizations/2026/09/28/01a0e6ab-6a15-7a40-923e-04ea3fd64426/cc-work-continuation/0874/t030-parity-review.json')


def load(path):
    return json.loads(pathlib.Path(path).read_text())


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkout', type=pathlib.Path, required=True)
    p.add_argument('--merged-source', required=True)
    p.add_argument('--worker', required=True)
    p.add_argument('--deployment', type=pathlib.Path, required=True)
    p.add_argument('--snapshot', type=pathlib.Path, required=True)
    p.add_argument('--canonical-row', type=pathlib.Path, required=True)
    p.add_argument('--public-smoke', type=pathlib.Path, required=True)
    p.add_argument('--output', type=pathlib.Path, required=True)
    a = p.parse_args()
    source = load(ROOT / 't030-source-receipt.json')
    ci = load(ROOT / 't030-ci-green.json')
    review = load(REVIEW)
    assert source['head'] == ci['headRefOid'] == review['head'] == HEAD
    assert review['findings'] == [] and review['focused']['exitCode'] == 0
    assert review['focused']['passed'] == 229
    assert {x['name'] for x in ci['statusCheckRollup']} == {'e2e', 'vitest', 'Payload scan', 'npm audit signatures'}
    assert all(x['conclusion'] == 'SUCCESS' for x in ci['statusCheckRollup'])
    review_hashes = {x['path']: x['sha256'] for x in review['manifest']}
    assert review_hashes == source['sourceSha256'] and len(review_hashes) == 4
    for file, sha in review_hashes.items():
        assert digest(a.checkout / file) == sha, 'Reviewed source changed: ' + file
        merged_bytes = subprocess.check_output(['git', '-C', str(a.checkout), 'show', a.merged_source + ':' + file])
        assert hashlib.sha256(merged_bytes).hexdigest() == sha, 'Merged source changed: ' + file
    subprocess.run(['git', '-C', str(a.checkout), 'merge-base', '--is-ancestor', HEAD, a.merged_source], check=True)
    artifact = load(ROOT / 't030-artifact-manifest.json')
    assert artifact['head'] == HEAD and artifact['workerBuildExit'] == 0
    assert artifact['sourceSha256'] == review_hashes and artifact['nodeVersion'].startswith('v22.')
    assert artifact['queueContract'] == 'queue-health build contract ok'
    deployment = load(a.deployment)
    assert deployment['allSixConsumersMatch'] is True
    spec = importlib.util.spec_from_file_location('natural_verifier', ROOT / 't030-verify-natural.py')
    natural = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(natural)
    assert natural.selftest()['passed'] == 9
    verdict = natural.evaluate(load(ROOT / 't030-natural-baseline.json'), load(a.snapshot), deployment, a.worker)
    assert verdict['verified'], json.dumps(verdict['checks'], sort_keys=True)
    row = load(a.canonical_row)
    assert row['readOnlyTransaction'] is True and row['canonicalRowAndPublicScopePreserved'] is True
    assert row['matchingRows'] == 1 and row['rows'][0]['sameOriginalRow'] is True
    assert row['rows'][0]['linkedSkillPublic'] is True and row['rows'][0]['linkedSkillTenantPresent'] is False
    latest = max(deployment['deployments']['deployments'], key=lambda d: natural.stamp(d['created_on']))
    assert natural.stamp(row['at']) >= natural.stamp(latest['created_on'])
    smoke = load(a.public_smoke)
    assert smoke['workerVersion'] == a.worker
    assert natural.stamp(smoke['at']) >= natural.stamp(latest['created_on'])
    checks = {(x['method'], x['path']): x for x in smoke['checks']}
    assert checks['GET', '/api/v1/skills?limit=3']['status'] == 200
    assert checks['GET', '/api/v1/skills?limit=3']['recordCount'] > 0
    assert checks['GET', '/api/v1/queue/health']['status'] == 200
    assert checks['GET', '/api/v1/queue/health']['schemaVersion'] == 2
    assert checks['GET', '/catalog']['status'] == 200
    assert checks['GET', '/catalog']['finalUrl'] == 'https://verified-skill.com/skills'
    for path in ['/api/v1/e2e-harness/healthz', '/api/v1/_test/healthz']:
        assert checks['GET', path]['status'] == 404
    evidence = [ROOT / 't030-source-receipt.json', ROOT / 't030-ci-green.json', REVIEW,
                ROOT / 't030-artifact-manifest.json', ROOT / 't030-verify-natural.py',
                ROOT / 't030-natural-baseline.json', a.deployment, a.snapshot, a.canonical_row, a.public_smoke]
    result = {
        'at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'verified': True, 'reviewedHead': HEAD, 'mergedSource': a.merged_source,
        'workerVersion': a.worker, 'allFourChecksGreen': True,
        'allFourReviewedSourceHashesMatch': True, 'sixConsumersUnchanged': True,
        'naturalIntakeProof': verdict, 'originalCanonicalRowPreserved': True,
        'currentVersionPublicSmokePassed': True,
        'inputSha256': {str(file): digest(file) for file in evidence},
        'fullBreadthProven': False,
        'limitation': 'Closes the exact canonical collision repair and its original blocked batch only. Full adaptive sweep and corpus coverage remain open.'
    }
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
