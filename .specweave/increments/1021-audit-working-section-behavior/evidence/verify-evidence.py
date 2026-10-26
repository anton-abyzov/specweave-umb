from pathlib import Path
import json,re,hashlib
p=Path(__file__).parent
for name,count in [('focused-tests.log',220),('model-tests.log',60),('reader-tests.log',16),('audit-tests.log',11)]:
 text=(p/name).read_text()
 assert re.search(r'Tests\s+'+str(count)+r' passed',text),(name,'missing passing count')
 assert not re.search(r'Test Files\s+\d+ failed',text),(name,'failed suite')
assert len(json.loads((p/'checks.json').read_text()))==11
assert len(json.loads((p/'live-classification.json').read_text())['rows'])==272
for row in json.loads((p/'source-receipt.json').read_text()):
 assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
assert 'PASS' in (p/'review.md').read_text()
assert (p/'report-preview.png').stat().st_size>1000
assert 'flowchart TD' in (p/'report.md').read_text()
assert 'desktop/web' in (p/'report.md').read_text()
print('307 passing checks retained; source hashes, 272 reconstructed rows, independent PASS, flow and preview verified.')
