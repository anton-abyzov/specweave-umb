#!/usr/bin/env python3
"""Read-only acceptance for the preserved 0934 hygiene reconciliation."""
from pathlib import Path
import hashlib
import json
import os

REPORTS = Path(__file__).resolve().parent
RECEIPT = REPORTS / 'hygiene-reconcile-20261021-receipt.json'


def inventory(root):
    root = Path(root)
    result = {}
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in dirs[:]:
            path = Path(base) / name
            relative = str(path.relative_to(root))
            if path.is_symlink():
                result[relative] = {'type': 'link', 'target': os.readlink(path)}
                dirs.remove(name)
            else:
                result[relative] = {'type': 'directory'}
        for name in files:
            if name.startswith('statev2.sqlite'):
                raise ValueError('Refusing a forbidden live database filename')
            path = Path(base) / name
            relative = str(path.relative_to(root))
            if path.is_symlink():
                result[relative] = {'type': 'link', 'target': os.readlink(path)}
            else:
                data = path.read_bytes()
                result[relative] = {'type': 'file', 'bytes': len(data),
                                    'sha256': hashlib.sha256(data).hexdigest()}
    return result


def main():
    receipt = json.loads(RECEIPT.read_text())
    assert receipt['state'] == 'complete'
    for entry in receipt['canonicalSkills']:
        assert inventory(entry['path']) == entry['inventory'], entry['path']
    for entry in receipt['copies']:
        original = Path(entry['path'])
        assert original.is_symlink() and original.resolve() == Path(entry['canonicalPath'])
        assert inventory(entry['backupPath']) == entry['inventory'], entry['backupPath']
    for entry in receipt['links']:
        original, backup = Path(entry['path']), Path(entry['backupPath'])
        assert not original.exists() and not original.is_symlink(), str(original)
        assert backup.is_symlink() and os.readlink(backup) == entry['target'], str(backup)
        assert (Path(entry['canonicalPath']) / 'SKILL.md').is_file()
    installer_lock = Path('/Users/antonabyzov/.agents/.skill-lock.json')
    assert hashlib.sha256(installer_lock.read_bytes()).hexdigest() == receipt['installerLockSha256']
    for name in 'hyperframes-creative hyperframes-studio asc-build-lifecycle asc-id-resolver asc-testflight-orchestration asc-screenshot-resize asc-whats-new-writer asc-apple-ads typesafe-ai reverse-engineer-anything jev-browser-use'.split():
        assert (Path('/Users/antonabyzov/.agents/skills') / name / 'SKILL.md').is_file()
    print(json.dumps({'ok': True, 'copiesPreserved': len(receipt['copies']),
                      'redundantLinksPreserved': len(receipt['links']),
                      'canonicalSkillsUnchanged': len(receipt['canonicalSkills']),
                      'installerLockUnchanged': True, 'usedSkillsPresent': 11,
                      'backupRoot': receipt['backupRoot']}))


if __name__ == '__main__':
    main()
