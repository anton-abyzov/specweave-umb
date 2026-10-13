#!/usr/bin/env python3
"""Read back the shipped release and existing verification receipts; no mutations."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

STAGE = Path('/Users/antonabyzov/.specweave-studio/release-staging/0901-1.0.7')
EVIDENCE = Path('/Users/antonabyzov/.local/share/specweave-studio/verification/0901')
SOURCE = '54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f'


def fetch(url, method='GET'):
    # Native curl uses the host's trusted certificate store; TLS verification stays enabled.
    args = ['/usr/bin/curl', '--fail', '--silent', '--show-error', '--location',
            '--max-time', '60', '--proto', '=https', '--user-agent', 'SpecWithCode-release-verification']
    if method == 'HEAD':
        status = subprocess.check_output(args + ['--head', '--output', '/dev/null',
                                                '--write-out', '%{http_code}', url])
        assert status == b'200', status
        return 200
    return subprocess.check_output(args + [url])


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


expected = {line.split('  ', 1)[1]: line.split('  ', 1)[0]
            for line in (STAGE / 'SHA256SUMS').read_text().splitlines()}
for name, sha in expected.items():
    assert digest(STAGE / name) == sha, name
expected['SHA256SUMS'] = digest(STAGE / 'SHA256SUMS')
releases = []
for repo in ('anton-abyzov/specweave-studio', 'anton-abyzov/specwithcode'):
    endpoint = f'repos/{repo}/releases/latest'
    data = (json.loads(fetch('https://api.github.com/' + endpoint)) if repo.endswith('/specwithcode')
            else json.loads(subprocess.check_output(['gh', 'api', endpoint])))
    assert data['tag_name'] == 'v1.0.7' and not data['draft'] and not data['prerelease']
    assets = {asset['name']: asset for asset in data['assets']}
    assert set(assets) == set(expected)
    for name, sha in expected.items():
        assert assets[name]['digest'] == 'sha256:' + sha, (repo, name)
        assert assets[name]['size'] == (STAGE / name).stat().st_size, (repo, name)
    if repo.endswith('/specwithcode'):
        for name in ('SHA256SUMS', 'studio-update.json', 'latest-mac.yml'):
            assert fetch(assets[name]['browser_download_url']) == (STAGE / name).read_bytes(), name
        assert fetch(assets['SpecWithCode-1.0.7-arm64.dmg']['browser_download_url'], 'HEAD') == 200
        assert fetch(assets['SpecWithCode-1.0.7-arm64.zip']['browser_download_url'], 'HEAD') == 200
    releases.append({'repository': repo, 'tag': data['tag_name'], 'publishedAt': data['published_at'],
                     'url': data['html_url'], 'assetsVerified': len(assets),
                     'publicUnauthenticatedReadback': repo.endswith('/specwithcode')})

plan = json.loads((STAGE / 'studio-update.json').read_text())
assert plan['sourceCommit'] == SOURCE and plan['version'] == '1.0.7'
headless = json.loads((EVIDENCE / 'google-headless-4/google-receipt.json').read_text())
assert headless['headless'] and headless['realBuiltServer'] and headless['fakeGoogle']
assert headless['privateHomeRemoved'] and headless['nativeTurns'] == 0
assert any(check.get('compiledGoogleClientAvailable') and check.get('noRuntimeGoogleClient') for check in headless['checks'])
assert any(check.get('secretsNotLogged') for check in headless['checks'])
assert any(check.get('pageErrors') == [] for check in headless['checks'])
coverage = json.loads((EVIDENCE / 'coverage-final/coverage-summary.json').read_text())['total']
assert all(coverage[key]['pct'] >= 60 for key in ('lines', 'statements', 'branches', 'functions'))
receipt = {'checkedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'version': '1.0.7',
           'sourceCommit': SOURCE, 'releases': releases, 'headlessGoogleProof': 'passed with fake Google',
           'realGoogleAccount': 'not connected; user sign-in and project grants required',
           'coveragePercent': {key: coverage[key]['pct'] for key in ('lines', 'statements', 'branches', 'functions')}}
(EVIDENCE / 'release-readback.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
