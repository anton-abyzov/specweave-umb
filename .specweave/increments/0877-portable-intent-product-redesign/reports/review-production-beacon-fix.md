# Independent review — T36 manual analytics beacon removal

Reviewed the uncommitted `docusaurus.config.ts` and `src/__tests__/docusaurus-config.test.ts` diff in `/tmp/specweave-0877-root` on 2026-09-14. This reviewer diagnosed the production behavior independently and did not author the source fix or tests.

**Approved.** The diff removes only the manually configured Cloudflare beacon that the controlled headless diagnostic proves causes the cross-origin404/CORS errors. Production's independently verified edge-injected beacon remains responsible for analytics and returns same-origin204. Both scripts used the same public site token; the repair is removal of a duplicate, not credential replacement.

The test imports the actual config, prohibits the duplicate manual analytics script, and asserts the Organization JSON-LD remains. Existing strict-link assertions are unchanged. Independently ran all three focused config/sidebar/footer files: **15 tests passed** (`docs-beacon-independent-tests.log`). No skipped/removed tests, dependency changes, or checker weakening.

Evidence of actual browser causality: `specweave-production-beacon-causality.json`. Full strict build and deployment remain root-owned follow-up checks; the first production run is preserved with its nonzero result under filenames ending `-b5e796882-first`.

## Email obfuscation options

Cloudflare's official [Email Address Obfuscation documentation](https://developers.cloudflare.com/waf/tools/scrape-shield/email-address-obfuscation/) supports HTML `<!--email_off-->` / `<!--/email_off-->` boundaries or a zone/endpoint setting. A source-level boundary can target this static documentation without changing unrelated zone behavior. Docusaurus 3.9.2's installed `HtmlTags` type accepts raw strings, and `injectHtmlTags` supports `preBodyTags`/`postBodyTags`.

Any such follow-up must verify the comments surround the actual document content and survive the production HTML minifier; a config-object assertion alone is insufficient. Then inspect the real Cloudflare response after deployment to prove email-protection links are absent. This review does not approve an unimplemented boundary or claim it has already fixed the edge transformation.
