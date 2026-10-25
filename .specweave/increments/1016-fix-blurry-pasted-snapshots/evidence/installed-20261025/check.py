"""Validate retained capture and provider receipts without reading live state."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
receipt = json.loads((root / 'installed-receipt.json').read_text())
provider = json.loads((root / 'provider-result.json').read_text())
upload = json.loads((root / 'upload-receipt.json').read_text())
assert receipt['appVersion'] == '1.0.76'
assert receipt['headless'] and receipt['offscreen'] and not receipt['show']
assert receipt['retina']['sourceSha256'] == receipt['retina']['outputSha256']
assert receipt['retina']['width'] == 3024 and receipt['retina']['height'] == 1964
assert [case['zoom'] for case in receipt['cases']] == [0.75, 1, 1.5]
for case in receipt['cases']:
    image = root / f"installed-annotation-{case['zoom']}-after.png"
    assert hashlib.sha256(image.read_bytes()).hexdigest() == case['sha256']
    assert case['green'] > 1000
    assert case['comment'] == 'Keep installed annotation text'
    assert 'SELECTED CONTEXT TEXT' in case['html']
image_hash = hashlib.sha256((root / 'installed-annotation-1.5-after.png').read_bytes()).hexdigest()
assert image_hash == provider['receivedSha256'] == upload['sha256']
assert provider['matchesCapturedFile']
assert provider['visualExtraction'] == 'PASS'
assert provider['headingObserved'] == 'SELECTED CONTEXT TEXT'
assert provider['elementLabelObserved'] == 'h1#selected'
assert not provider['transcriptionUsedFileTools']
assert provider['messageId'] and provider['runId']
assert upload['status'] == 204
print('PASS: installed-artifact harness, three zoom crops, preserved context, identical uploaded image and provider visual extraction.')
print('OPEN: live installed desktop shortcut and annotation UI acceptance; these receipts do not close it.')
