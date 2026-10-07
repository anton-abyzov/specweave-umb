"""Public, read-only release checks. Does not claim Google index validation."""
import argparse
import concurrent.futures
import json
import re
import ssl
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

try:
    import certifi
    TLS_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    TLS_CONTEXT = ssl.create_default_context()


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.canonicals, self.meta, self.schemas = [], {}, []
        self.iframes = []
        self.in_schema = False
        self.schema_text = ''
        self.h1_count = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs.get('href'))
        if tag == 'meta':
            name = attrs.get('name') or attrs.get('property')
            if name:
                self.meta[name] = attrs.get('content', '')
        if tag == 'h1':
            self.h1_count += 1
        if tag == 'iframe':
            self.iframes.append(attrs)
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.in_schema = True
            self.schema_text = ''

    def handle_data(self, data):
        if self.in_schema:
            self.schema_text += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.in_schema:
            self.schemas.append(json.loads(self.schema_text))
            self.in_schema = False


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 SEO Release Verification', 'Cache-Control': 'no-cache'})
    try:
        response = urllib.request.urlopen(req, timeout=30, context=TLS_CONTEXT)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.status, response.url, response.headers, response.read().decode('utf-8', errors='replace')


def objects(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from objects(value)
    elif isinstance(node, list):
        for value in node:
            yield from objects(value)


def page(url, *, canonical=None, noindex=False, status=200, h1=False, min_videos=0, require_players=False, event=False):
    actual, final, headers, body = fetch(url)
    assert actual == status, f'{url}: HTTP {actual}, expected {status}'
    doc = Document(body)
    if canonical:
        assert doc.canonicals == [canonical], f'{url}: canonical {doc.canonicals}, expected {canonical}'
        assert doc.meta.get('description', '').strip(), f'{url}: missing description'
        assert doc.meta.get('og:url') == canonical, f'{url}: incorrect og:url {doc.meta.get("og:url")}'
    if noindex:
        assert 'noindex' in doc.meta.get('robots', '') + headers.get('X-Robots-Tag', ''), f'{url}: missing noindex'
    elif status == 200:
        assert 'noindex' not in doc.meta.get('robots', ''), f'{url}: unintended noindex'
    if h1:
        assert doc.h1_count >= 1, f'{url}: missing H1'
    videos = [node for schema in doc.schemas for node in objects(schema) if node.get('@type') == 'VideoObject']
    assert len(videos) >= min_videos, f'{url}: expected at least {min_videos} videos, found {len(videos)}'
    if require_players:
        for video in videos:
            embed = video.get('embedUrl', '')
            identity = embed.split('?', 1)[0].rstrip('/')
            frames = [frame for frame in doc.iframes if frame.get('src', '').split('?', 1)[0].rstrip('/') == identity]
            assert len(frames) == 1, f'{url}: video player absent or inconsistent in initial HTML: {identity}'
            frame = frames[0]
            assert frame.get('title', '').strip(), f'{url}: video player lacks accessible title'
            assert 'autoplay=1' not in frame.get('src', ''), f'{url}: video autoplays'
    for video in videos:
        assert video.get('name') and video.get('thumbnailUrl'), f'{url}: incomplete video'
        stamp = video.get('uploadDate', '')
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', stamp), f'{url}: invalid video uploadDate {stamp}'
        assert datetime.fromisoformat(stamp.replace('Z', '+00:00')) <= datetime.now(timezone.utc), f'{url}: future video uploadDate'
        for thumbnail in video['thumbnailUrl'] if isinstance(video['thumbnailUrl'], list) else [video['thumbnailUrl']]:
            asset_status, _, asset_headers, asset_body = fetch(thumbnail)
            assert asset_status == 200 and asset_headers.get('Content-Type', '').startswith('image/') and len(asset_body) > 100, f'{url}: unavailable video thumbnail {thumbnail}'
    if event:
        events = [node for schema in doc.schemas for node in objects(schema) if node.get('@type') == 'SportsEvent']
        assert events, f'{url}: missing SportsEvent'
        for item in events:
            assert all(item.get(field) for field in ['startDate', 'location', 'image', 'description', 'eventStatus', 'organizer', 'performer']), f'{url}: incomplete SportsEvent'
            location = item['location']
            assert (location.get('@type') == 'Place' and location.get('address')) or (location.get('@type') == 'VirtualLocation' and location.get('url')), f'{url}: invalid Event location'
            assert item['organizer'].get('url'), f'{url}: missing organizer URL'
    return {'url': url, 'finalUrl': final, 'status': actual, 'canonical': doc.canonicals, 'robots': doc.meta.get('robots'), 'h1': doc.h1_count, 'videoObjects': len(videos), 'initialHtmlIframes': len(doc.iframes)}


def sitemap(host, forbidden):
    status, _, _, body = fetch(host + '/sitemap.xml')
    assert status == 200
    root = ET.fromstring(body)
    urls = [node.text for node in root.iter() if node.tag.endswith('}loc')]
    assert urls and len(urls) == len(set(urls)), f'{host}: empty or duplicate sitemap'
    for path in forbidden:
        assert not any(url.rstrip('/') == host + path for url in urls), f'{host}: excluded {path} is submitted'
    return {'url': host + '/sitemap.xml', 'status': status, 'submittedUrls': len(urls)}


parser = argparse.ArgumentParser()
parser.add_argument('--site', choices=['all', 'specweave', 'vskill', 'easychamp'], default='all')
parser.add_argument('--crawl-specweave', action='store_true', help='Check every deployed SpecWeave sitemap URL')
args = parser.parse_args()
checks = []
if args.site in ('all', 'specweave'):
    paths = ['/', '/docs/getting-started/', '/docs/overview/introduction/', '/blog/introducing-specweave/']
    if args.crawl_specweave:
        sitemap_status, _, _, sitemap_body = fetch('https://spec-weave.com/sitemap.xml')
        assert sitemap_status == 200
        sitemap_urls = [node.text for node in ET.fromstring(sitemap_body).iter() if node.tag.endswith('}loc')]
        paths = [url.removeprefix('https://spec-weave.com') for url in sitemap_urls]
    checks += [(page, ('https://spec-weave.com' + path,), {'canonical': 'https://spec-weave.com' + path}) for path in paths]
    checks += [(page, ('https://spec-weave.com/search/',), {'noindex': True}), (sitemap, ('https://spec-weave.com', ['/search']), {})]
if args.site in ('all', 'vskill'):
    checks += [(page, ('https://verified-skill.com' + path,), {'canonical': 'https://verified-skill.com' + path, 'h1': path in ['/skills', '/publishers']}) for path in ['/skills', '/publishers', '/docs', '/docs/plugins', '/insights', '/pricing', '/watch', '/watch/getting-started-101']]
    checks += [(page, ('https://verified-skill.com' + path,), {'noindex': True}) for path in ['/queue', '/submit']]
    checks += [(page, ('https://verified-skill.com/watch/specweave-workflow-101',), {'status': 404}), (sitemap, ('https://verified-skill.com', ['/queue', '/submit', '/blocklist']), {})]
if args.site in ('all', 'easychamp'):
    checks += [(page, ('https://easychamp.com' + path,), {'canonical': 'https://easychamp.com' + path}) for path in ['/pro-clubs', '/ko', '/sim', '/ko/sim', '/ko/coach', '/tr/sim', '/tools/round-robin-generator']]
    checks += [(page, ('https://easychamp.com/help',), {'canonical': 'https://easychamp.com/help'})]
    checks += [(page, ('https://easychamp.com/help/league-console/create-league-or-tournament',), {'canonical': 'https://easychamp.com/help/league-console/create-league-or-tournament', 'min_videos': 2, 'require_players': True})]
    for path in ['/match/south-africa-vs-iraq-40aff015-26af-40cb-961a-414886763cd1', '/match/new-zealand-vs-spain-11fc4398-1253-421b-8aef-950e6c672275', '/match/brazil-vs-egypt-2c1643e4-01de-4014-840f-e3aa59700e1d']:
        checks.append((page, ('https://watch.easychamp.com' + path,), {'canonical': 'https://watch.easychamp.com' + path, 'event': True}))
results, errors = [], []
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    pending = [pool.submit(fn, *positional, **keyword) for fn, positional, keyword in checks]
    for job in pending:
        try:
            results.append(job.result())
        except Exception as error:
            errors.append(str(error))
report = {'checkedAt': datetime.now(timezone.utc).isoformat(), 'site': args.site, 'passed': len(results), 'failed': len(errors), 'results': results, 'errors': errors}
destination = Path(__file__).resolve().parents[1] / 'reports' / ('public-verification-' + args.site + '.json')
# Preserve every result while keeping generated receipts within the project's
# 1,500-line limit when the complete public sitemap is crawled.
lines = ['{']
for index, (key, value) in enumerate(report.items()):
    comma = ',' if index < len(report) - 1 else ''
    if isinstance(value, list):
        lines.append('  ' + json.dumps(key) + ': [')
        lines.extend('    ' + json.dumps(item, separators=(',', ':')) + (',' if i < len(value) - 1 else '') for i, item in enumerate(value))
        lines.append('  ]' + comma)
    else:
        lines.append('  ' + json.dumps(key) + ': ' + json.dumps(value) + comma)
lines.append('}')
destination.write_text('\n'.join(lines) + '\n')
print(json.dumps({'passed': len(results), 'failed': len(errors), 'errors': errors}))
raise SystemExit(bool(errors))
