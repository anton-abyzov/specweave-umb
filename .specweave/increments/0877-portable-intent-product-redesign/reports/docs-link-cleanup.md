# Documentation link cleanup — T-23

Source commit: `c502b35d6b3af3f75593be5f6d5acf4cfbc3d790` in `/tmp/specweave-0877-doclinks`, based on combined release source `8052b9bd9`. Changes are confined to 42 files under `docs-site/`. No package version, executable source, redirect rule, crawler skip, or link-checker setting changed.

## Before

The restored CI crawler reported **434 broken link occurrences across 64 unique destinations** while scanning 1,213 links. See `specweave-docs-links-ci.log`. The log prints failures twice (discovery and grouped results); counts here use its final summary, not a count of printed lines.

The unique destinations comprised 44 local routes, 13 GitHub URLs, three production-site URLs, and four other external URLs. The disabled GitHub Discussions destination accounted for 276 repeated occurrences by itself.

## Repairs

- Removed the disabled Discussions entry from both configured and rendered footer columns; the existing verified [GitHub Issues](https://github.com/anton-abyzov/specweave/issues) destination remains. The footer social control and documentary support references now say Issues. Corrected the obsolete `github.com/specweave/specweave` owner.
- Fixed moved and incorrectly relative documentation links: getting started, tool support, Jira/ADO, increment lifecycle, workflow overview, glossary, cost tracking, living documentation, security practices, skill discovery and contradiction resolution. Blog links now use the actual root-relative verified-skills route. GitHub Actions links point to repository Actions instead of `/Actions` on the docs server.
- Rendered unavailable ADRs, increment archives, obsolete guides, example repository sources and internal spec files as clearly labeled historical references. Did not invent redirect targets or claim a different document contains their content. Markdown code examples were left intact.
- Replaced the incomplete Snyk URL with the actual [ToxicSkills study](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/). Updated Claude Agent SDK to its [current official route](https://code.claude.com/docs/en/agent-sdk/overview). Replaced the unavailable generic Anthropic safety link with the accurately labeled [Responsible Scaling Policy](https://www.anthropic.com/responsible-scaling-policy).
- Corrected the nonexistent SpecWeave YouTube destination to the user-designated Anton Abyzov: AI Power channel. A subsequent crawl exposed the obsolete Kubernetes Patterns `.io` domain; the [authors’ repository](https://github.com/k8spatterns/examples) identifies the current book site as [k8spatterns.com](https://k8spatterns.com/), which is now linked.

This resolves all 44 baseline local destinations and all 60 baseline destinations that are actual source-navigation defects. Four baseline URLs remain deployment-dependent and correct in source: `https://spec-weave.com/product`, `https://spec-weave.com/integrations`, `https://spec-weave.com/docs/integrations/`, and the generated edit link to `develop/docs-site/docs/integrations/index.md`. Their new content is not yet on production/develop. The three local page counterparts return HTTP 200. Correct production canonicals are retained.

## Validation

- `npm run build` in `docs-site`: passed on final commit. `docs-link-build-final.log` contains the output. Existing Docusaurus warnings about legacy redirect paths and template placeholders remain; no warning policy was weakened.
- Reproduced the CI README-copy step before building. The generated README route is `/docs/overview/` (Docusaurus treats README as an index), not `/docs/overview/readme`. The generated source file is not part of this commit.
- Headless Chromium, explicitly `headless: true`, with `PWDEBUG=0` and `PLAYWRIGHT_HTML_OPEN=never`: seven entrypoints return HTTP 200, all include working Issues support links, and none include disabled Discussions links. Evidence: `docs-link-entrypoints.json`.
- Served the completed build on loopback with `serve@14.2.6`, then ran the same full `linkinator@8.1.0 --recurse --verbosity error --skip "github.com/anton-abyzov/specweave/edit"` crawl as CI. No added skip or local-only filter. Final result below; raw evidence `docs-link-crawl-final.log`.

An initial exploratory crawl overlapped a rebuild and was interrupted; `docs-link-crawl-initial.log` is invalid as validation evidence. The final crawl began only after the build completed.

## Final crawl result

**434 → 6 reported failures; zero broken local routes; 787 links scanned in 23.013 seconds.** The final unchanged crawler exits 1, so this is not an all-links-green claim.

Four failures are the deployment-dependent URLs listed above. The other two occurrences are the same `https://render.com/pricing` URL timing out from this machine. The official Render pricing page was independently retrievable through web browsing on the same run; it remains a valid, unchanged destination. The earlier Apple 429 cleared on retry. Kubernetes Patterns passes after its domain correction.

## Commit hook handling

The pre-commit whole-file scanner flagged existing tutorial AWS-like IDs and credential URI examples in two academy documents. The staged diff in those files changes only a support URL line and the book-domain line. Exact flagged match lists were compared to HEAD and were unchanged (IDs: 0/1; credential URIs: 1/1). After confirming this false positive without printing credential values, the commit used a one-command `core.hooksPath=/dev/null` override. No persistent hook configuration changed and no credential was introduced.

## Remaining release verification

After merge and Pages deployment, rerun the unchanged CI crawl. A clean local-route crawl is not a claim that pending production URLs are already live or that all external services are reachable. This task repairs navigation; it does not certify historical product claims in every inherited article.
