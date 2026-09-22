"""Run only after deployment confirmation: exact HTML + headless product report checks."""
import hashlib
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

os.environ['PWDEBUG'] = '0'
os.environ['PLAYWRIGHT_HTML_OPEN'] = 'never'
URL = 'https://spec-weave.com/releases/2.1/'
REPORTS = Path(__file__).resolve().parent
SOURCE = Path('/tmp/specweave-0877-root/docs-site/static/releases/2.1/index.html')
AXE = Path('/tmp/vskill-platform-0877-product/node_modules/axe-core/axe.min.js')
result = {'url': URL, 'headless': True, 'expectedSha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'cases': []}
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    try:
        for name, viewport in [('desktop', {'width': 1440, 'height': 1050}), ('mobile', {'width': 390, 'height': 844})]:
            page = browser.new_page(viewport=viewport, reduced_motion='reduce')
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            response = page.goto(URL, wait_until='domcontentloaded', timeout=60000)
            assert response.status == 200
            body = response.body()
            digest = hashlib.sha256(body).hexdigest()
            # Pages adds this independently observed analytics tag at delivery time.
            # Preserve raw bytes/hash and allow no other difference from reviewed HTML.
            pattern = rb'<script type="module" src="https://static\.cloudflareinsights\.com/beacon\.min\.js/[^"<>]+" integrity="[^"<>]+" data-cf-beacon=\'[^\'<>]+\' crossorigin="anonymous"></script>\n'
            normalized, injected = re.subn(pattern, b'', body)
            assert injected in [0, 1]
            normalized_digest = hashlib.sha256(normalized).hexdigest()
            assert normalized_digest == result['expectedSha256'], 'Live report differs beyond the identified Cloudflare analytics insertion'
            (REPORTS / f'artifacts/html-report-review/production-{name}-response.html').write_bytes(body)
            expect(page.get_by_role('heading', level=1)).to_have_text('Change tools.Keep the work.')
            expect(page.get_by_role('banner')).to_have_count(1)
            page.keyboard.press('Tab')
            expect(page.get_by_role('link', name='Skip to report')).to_be_focused()
            page.keyboard.press('Enter')
            assert page.evaluate('location.hash') == '#main'
            for anchor in ['#changes', '#cleanup', '#evidence', '#products']:
                page.locator(f'a[href="{anchor}"]').click()
                assert page.evaluate('location.hash') == anchor
                expect(page.locator(anchor)).to_have_count(1)
            for summary in page.locator('summary').all():
                summary.focus()
                page.keyboard.press('Enter')
                assert summary.locator('..').get_attribute('open') is not None
                page.keyboard.press('Space')
                assert summary.locator('..').get_attribute('open') is None
            page.add_script_tag(path=str(AXE))
            audits = []
            for state in ['closed', 'open']:
                if state == 'open':
                    page.locator('details').evaluate_all('(ds)=>ds.forEach(d=>d.open=true)')
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                audit = page.evaluate('async()=>{const a=await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa","best-practice"]}});return {violations:a.violations,passes:a.passes.length}}')
                assert not audit['violations']
                audits.append({'state': state, **audit})
            assert not errors
            page.screenshot(path=str(REPORTS / f'artifacts/html-report-review/production-{name}.png'), full_page=True)
            result['cases'].append({'name': name, 'status': response.status, 'actualSha256': digest, 'normalizedSha256': normalized_digest, 'cloudflareAnalyticsInsertions': injected, 'pageErrors': errors, 'axe': audits})
            page.close()
    finally:
        browser.close()
        (REPORTS / 'html-report-production-check.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
