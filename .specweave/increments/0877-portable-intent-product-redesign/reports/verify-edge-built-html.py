from pathlib import Path
from html.parser import HTMLParser
import json
import datetime

ROOT = Path('/tmp/specweave-0877-root/docs-site/build')
REPORT = Path(__file__).parent / 'review-production-edge-final.json'
class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.position = 0
        self.opens = []
        self.closes = []
        self.app_start = None
        self.app_end = None
        self.div_depth = 0
        self.manual_beacons = []
    def handle_starttag(self, tag, attrs):
        self.position += 1
        values = dict(attrs)
        if tag == 'div':
            if values.get('id') == '__docusaurus':
                assert self.app_start is None, 'duplicate application root'
                self.app_start = self.position
                self.div_depth = 1
            elif self.div_depth:
                self.div_depth += 1
        if tag == 'script' and 'cloudflareinsights.com' in values.get('src', ''):
            self.manual_beacons.append(values['src'])
    def handle_endtag(self, tag):
        self.position += 1
        if tag == 'div' and self.div_depth:
            self.div_depth -= 1
            if self.div_depth == 0:
                self.app_end = self.position
    def handle_comment(self, data):
        self.position += 1
        if data == 'email_off': self.opens.append(self.position)
        if data == '/email_off': self.closes.append(self.position)

report = {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'root': str(ROOT), 'pages': [], 'nonAppHtml': [], 'failures': [], 'samples': {}, 'passed': False}
for path in sorted(ROOT.rglob('*.html')):
    source = path.read_text()
    parser = Structure()
    try:
        parser.feed(source)
        relative = str(path.relative_to(ROOT))
        assert not parser.manual_beacons, 'manual Cloudflare beacon in static artifact'
        if parser.app_start is None:
            report['nonAppHtml'].append(relative)
            continue
        assert len(parser.opens) == len(parser.closes) == 1, 'expected one balanced email_off pair'
        assert parser.app_end is not None, 'missing application close'
        assert parser.opens[0] < parser.app_start < parser.app_end < parser.closes[0], 'email_off pair does not bracket complete application'
        report['pages'].append(relative)
    except Exception as error:
        report['failures'].append({'file': str(path.relative_to(ROOT)), 'error': str(error)})

for relative in ['index.html', 'docs/workflows/hotfix/index.html', 'docs/getting-started/installation/index.html']:
    path = ROOT / relative
    source = path.read_text()
    assert relative in report['pages'], relative
    report['samples'][relative] = {'validated': True, 'emailOffPairs': source.count('<!--email_off-->'), 'appRoot': '__docusaurus' in source, 'protectedEmailLinks': source.count('/cdn-cgi/l/email-protection')}
    assert not report['samples'][relative]['protectedEmailLinks'], relative

report['passed'] = len(report['pages']) > 0 and not report['failures']
REPORT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'appPages': len(report['pages']), 'nonAppHtml': len(report['nonAppHtml']), 'failures': report['failures'], 'samples': report['samples']}, indent=2))
raise SystemExit(0 if report['passed'] else 1)
