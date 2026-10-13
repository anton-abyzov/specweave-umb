#!/usr/bin/env python3
"""Validate saved headless evidence; this does not run a new browser or prove live Google."""
import json, hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
private=Path('/Users/antonabyzov/.local/share/specweave-studio/verification/0901/navigation')
for phase in ['108', 'linked']:
    r=json.loads((root/(phase+'-receipt.json')).read_text())
    assert r['headless'] and r['realBuiltServer'] and r['fakeGoogle'] and r['privateHomeRemoved']
    assert r['nativeTurns']==0
    checks=r['checks']
    assert {c['morningBriefingDismissal'] for c in checks if c.get('exactOriginRestored')}=={'cancel','close','escape','backdrop'}
    for key in ['nestedSelectEscapeStaysInEditor','directLinkFallbackAndHistory','localTaskCancelStaysOnList','noTasksCreatedByCancel','saveStaysOnTaskList','editCancelPreservesTask','disabledFixtureNeverRan','providerWizardCancelAndEscapeStayInSettings','themeVariantHoverAndFocusEscapeStayInSettings','secretsNotLogged']:
        assert any(c.get(key) is True for c in checks), key
    assert any(c.get('pageErrors') == [] for c in checks)
    if phase=='linked':
        assert r['linkedTaskEditorsIncluded'] is True
        assert any(c.get('linkedEditReturnsToOrigin') and c.get('directEditConsumesTaskId') for c in checks)
for path, expected in json.loads((root/'manifest.json').read_text()).items():
    assert hashlib.sha256((private/path).read_bytes()).hexdigest()==expected, path
print('PASS: two saved headless receipts and retained artifact hashes; no live Google claim')
