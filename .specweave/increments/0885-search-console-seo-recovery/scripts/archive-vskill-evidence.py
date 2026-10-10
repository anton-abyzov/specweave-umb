"""Archive curated sanitized evidence; retain full long logs beside excerpts."""
import gzip
import hashlib
import json
from pathlib import Path

SOURCE = Path('/tmp/easychamp-seo-audit-20261007')
REPORTS = Path(__file__).resolve().parents[1] / 'reports'
manifest = []
upstream = json.loads((SOURCE / 'vskill-index-archive-sha256.json').read_text())
upstream = upstream['files'] if isinstance(upstream, dict) else upstream
for row in upstream:
    original = (SOURCE / row['path']).read_bytes()
    assert len(original) == row['bytes']
    assert hashlib.sha256(original).hexdigest() == row['sha256'], row['path']

for name in (SOURCE / 'vskill-index-archive-manifest.txt').read_text().splitlines():
    source = SOURCE / name
    if 'headless-report' in name:
        # Generated HTML renderer is local; native log and all screenshots are retained.
        continue
    paths = sorted(source.rglob('*')) if source.is_dir() else [source]
    for path in paths:
        if not path.is_file():
            continue
        relative = path.relative_to(SOURCE)
        target = REPORTS / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        original = path.read_bytes()
        if path.suffix == '.png':
            archived = original
            method = 'complete original screenshot'
        else:
            text = original.decode('utf-8')
            lines = text.splitlines()
            if len(lines) > 1500:
                archived = ('\n'.join(line.rstrip() for line in lines[-300:]).rstrip() + '\n').encode()
                Path(str(target) + '.gz').write_bytes(gzip.compress(original, mtime=0))
                method = 'last 300 lines; complete unchanged gzip also archived'
            else:
                archived = ('\n'.join(line.rstrip() for line in lines).rstrip() + ('\n' if lines else '')).encode()
                method = 'complete text; LF and trailing whitespace only'
        target.write_bytes(archived)
        manifest.append({
            'file': str(relative),
            'originalBytes': len(original),
            'originalSha256': hashlib.sha256(original).hexdigest(),
            'archivedSha256': hashlib.sha256(archived).hexdigest(),
            'method': method,
        })

screenshots = sum(row['file'].endswith('.png') for row in manifest)
excluded = [dict(row, reason='Generated HTML renderer omitted; native log, status and all original screenshots retained')
            for row in upstream if 'headless-report' in row['path']]
(REPORTS / 'vskill-index-artifact-manifest.json').write_text(json.dumps({
    'files': manifest,
    'excluded': excluded,
    'note': f'Curated sanitized native receipts. Long logs retain complete unchanged gzip. Generated HTML reports remain local; native test logs and all {screenshots} original screenshots are archived. Runtime gates are recorded separately in the current-release receipt.',
}, indent=2) + '\n')
print(f'Archived {len(manifest)} complete artifacts or full-log excerpts with hashes')
