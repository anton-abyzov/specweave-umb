# Public HTML report console and network follow-up

The report’s edge-injected analytics works during the observed load. An explicit-headless Chromium session stayed on `https://spec-weave.com/releases/2.1/` for10seconds: **zero console errors/warnings, page errors, failed requests or HTTP failures**. The single versioned Cloudflare module script returned200; its same-origin POST to `https://spec-weave.com/cdn-cgi/rum` returned204.

After the deliberate navigation to `about:blank`, one unload ping to the same-origin RUM endpoint was marked `net::ERR_ABORTED`. This is retained in the raw results; the complete12-second observation is not claimed to contain zero request failures. No errors or requests were suppressed or filtered. URL query/fragment data is omitted from stored output, and no request payload or credential value was captured.

## Source comparison

The static report source contains no analytics script. Cloudflare injects exactly one `type="module"` script at a versioned `https://static.cloudflareinsights.com/beacon.min.js/v31…` URL. Docusaurus configuration separately declares one unversioned `https://static.cloudflareinsights.com/beacon.min.js` classic script with defer.

The edge script’s public site-identifier hash equals the manual configuration’s identifier hash. Therefore an invalid identifier is not established by this evidence. The successful edge script’s same-origin RUM204 is a useful contrast with the main-site cross-origin failures under investigation. This report probe does not itself prove duplicate execution on Docusaurus pages.

Evidence: `html-report-console-check.py`, `.json`, `.log`. The prior report checks covered page errors and accessibility but did not observe console/request events; this follow-up fills that gap. No source or account-setting changes.

Repeated after final Pages run `34882131675`, source `5d9a91cb27f49a5ad9414d55dd3f96f6089a189c`: zero console errors/warnings or request failures during10seconds open; same-origin RUM204. The subsequent intentional-navigation unload abort remains separately recorded.
