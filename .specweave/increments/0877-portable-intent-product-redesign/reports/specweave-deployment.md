# SpecWeave website deployment

PR1940 merged with the user's explicit admin-merge approval at 2026-09-14T18:24:06Z. Merge b5e79688276b7acf78c9bfae63fae9e8ce841fba has exactly the reviewed source tree5a5c5a9f0. Pages run34880569459 completed successfully at18:26:15Z. Both the website and public report at https://spec-weave.com/releases/2.1/ are deployed.

Initial production checks passed all18 route/device interaction cases and the artwork hash, but failed overall on36 analytics console errors. The unchanged full crawl found32 email-protection404 occurrences and2 Renderpricingtimeouts. These failures were retained in *-b5e796882-first artifacts. The earlier four PR-time canonical/develop404s disappeared after the merge/deployment.

Independent causality checks found two analytics snippets using the same public identifier. The manual snippet posts to a cross-origin endpoint returning404/CORS errors; the edge-injected snippet posts to the site's same-origin endpoint and succeeds204. PR1944 removes only the manual duplicate and retains structured data and edge analytics. Cloudflare's documented email-off HTML markers protect rendered command examples from being rewritten. Account settings, authentication, and crawler filters remain unchanged.

Sources: [Cloudflare analytics FAQ](https://developers.cloudflare.com/web-analytics/faq/), [email-obfuscation exemptions](https://developers.cloudflare.com/waf/tools/scrape-shield/email-address-obfuscation/), [Docusaurus HTML injection API](https://docusaurus.io/docs/api/plugin-methods/lifecycle-apis).

Both regressions were observed before repair. All16 focused tests pass. The strict build includes the exact generated README used in CI. Independent parsing validates all183 application pages have one balanced marker pair around their application; none of256 HTML files includes the manual beacon. Final source review is in review-production-edge-final.md.

The public HTML report passes desktop/mobile keyboard and disclosure checks, four axe audits with zero violations, and zero overflow/page errors. Its exact reviewed content is preserved after removing one precisely identified Cloudflare-injected analytics script from comparison; raw HTML/hash remain recorded. A separate10-second runtime check confirms the report's existing edge-only analytics204 and zero console errors. An unload request cancellation is recorded separately.

The restored product showcase passed desktop/mobile navigation, all10 project examples, and direct links to EasyChamp, JobWeave and Verified Skills. Unsupported historic speed and zero-failure claims were removed.

Render's official pricing page remains retrievable through independent web access. Direct requests from this Mac time out before an HTTP response. This is recorded as an external connectivity limitation, with no claim of a dead page and no URL removed merely to make a check pass.

## Final deployment and checks

PR1944 merged at5d9a91cb27f49a5ad9414d55dd3f96f6089a189c. Pages34882131675 completed successfully2026-09-14T18:41:42Z. The tree matches reviewedfb727eaab. Final production browser runner exits0:18/18cases, zero runtime and console errors, matching artwork. Raw hotfix/install pages return200 with one edge beacon and no email-protection links; native same-origin RUM returns204. Navigation/context-close request cancellations remain recorded separately; no ERR_FAILED requests remain.

The unchanged full production crawl checks654links and exits1 only for two occurrences of external https://render.com/pricing timing out from this Mac. No owned route fails. The unchanged GitHub build/full crawl34881875897 and unit/E2E/smoke34881875938 both pass. External timeout evidence remains in render-link-verification.md and the full production log.

Final HTML report checks pass again on desktop/mobile, with four zero-violation axe audits and zero errors while open. Homepage project examples and their navigation also passed production checks. All release PRs1940,1944, vskill139 and platform68/69 are merged. No new package version was needed for the website-only follow-up.

## Increment closure

CLI verify passes all3explicitcommands,8/8ACs and36/36tasks. `specweave complete0877 --yes` exits0 and metadata status is completed. Configured hooks created GitHub milestone258 and ADOitem2451; the latter transitionedDone, and the empty milestone was explicitlyclosed because the hook left itopen. OptionalJira mirrorfailed404 Site temporarily unavailable, withnoissuecreated. This externalservicefailure remains documented and was not hidden or retried in a loop. No new credential or Cloudflareaccountsetting was introduced.
