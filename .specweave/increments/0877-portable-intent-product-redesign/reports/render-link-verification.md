# Render pricing link verification

Checked 2026-09-14. Exact URL: [Render pricing](https://render.com/pricing). The two linkinator occurrences come from `/docs/guides/deployment-platforms` and its trailing-slash variant; both use the same destination.

The URL is still Render's official pricing destination. Independent web retrieval returned the **Pricing | Render** page and Render's own Pricing navigation pointing to this URL. No replacement destination or redirect was established.

Direct checks from this Mac could not establish an HTTP response:

- Node HEAD and GET both failed after approximately 10.5 seconds.
- curl HEAD timed out connecting after 15 seconds; HTTP status remained `000`.
- Explicitly headless Chromium navigation timed out at 30 seconds before DOM readiness.

**Conclusion:** this reproduces a connection timeout from the local environment, not a confirmed dead page or HTTP error. There is no 403/challenge response proving bot blocking, and no response proving a redirect. The independent retrieval supports retaining the current official URL. The cause of the local connection failure remains undetermined; this check does not claim the direct crawl passed.

No source edits, filters, or settings changes were made. Browser execution used `headless: true`, `PWDEBUG=0`, and `PLAYWRIGHT_HTML_OPEN=never`. Raw checks: `/tmp/0877-render-http.log` and `/tmp/0877-render-headless.log`.
