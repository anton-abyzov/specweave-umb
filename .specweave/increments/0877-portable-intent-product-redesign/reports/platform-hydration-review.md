# Verified Skills populated-catalog hydration — T-30

## Independently confirmed finding

**Medium: invalid nested links cause React hydration recovery on the populated production homepage.** `src/app/components/home/TrendingSkills.tsx:27` renders an outer skill `<a>`, and `:52` renders `RepoLink` inside it. `src/app/components/RepoLink.tsx:35` returns a second `<a>` for a valid repository URL. `stopPropagation` does not make this legal HTML.

On 2026-09-14, a fresh unauthenticated headless Chromium session loaded `https://verified-skill.com/?release=0877-hydration-audit`: HTTP 200, ten populated trending rows, and React error 418. Captured response HTML contains the nested anchors. After React recovers, the client DOM again contains a nested repository anchor in each row, which can conceal the parser mismatch from a simple screenshot or DOM count after hydration. Screenshot was inspected and shows the populated catalog.

Evidence: `artifacts/platform-hydration/production-repro.json`, `production-hydrated.html`, and `production-hydrated.png`. Separate observed console messages concern a Cloudflare analytics CORS failure and an unauthenticated 401; they are recorded, not asserted to cause this hydration error.

## Causal and baseline evidence

A bounded fixture imports the real async `TrendingSkillsSection` and its real `RepoLink`, mocking only `getHomeStats` with one skill containing a valid `repoUrl`. The fixture serializes with React server rendering, lets headless Chromium parse the HTML, then hydrates the same component tree.

| Variant | Browser-parsed rows | Hydration outcome |
|---|---:|---|
| Previous release `54535ca`, populated | 2 for one skill | Invalid nested-anchor warning and recoverable mismatch |
| Merged release `fe2520ad`, populated | 2 for one skill | Same warning and mismatch |
| Counterfactual outer container only changed to `div` | 1 | Zero console or recoverable errors |

This is a reproduced baseline defect, not a baseline classification based only on an unchanged source diff. Empty local stats skip the component and cannot expose it. Full diagnostics are in `artifacts/platform-hydration/causal-fixture.json`.

The first exploratory production run disabled JavaScript; its suspended server content could not be scrolled into view, so that run did not produce complete evidence. The subsequent JavaScript-enabled capture and isolated parser fixture provide the confirmed results above.

## Remediation

Commit `52eabeb385467ca1d4c2090113e63de386a8fbe6`, branch `codex/0877-hydration` in `/tmp/vskill-platform-0877-hydration`.

The row becomes a noninteractive `div` retaining its grid class. The skill name becomes a real link to its existing skill route; `RepoLink` remains a separate sibling link with its existing new-tab and `noopener noreferrer` semantics. No clickable-div handler, fake anchor, event suppression workaround or hydration-warning suppression was added. Source scope is only `TrendingSkills.tsx` and its new focused test file.

The new populated regression failed first: two failing tests (HTML parser row splitting and hydration recovery), one passing no-repository case. After the source fix, all 23 focused tests pass across TrendingSkills, RepoLink and TierBadge. Evidence: `platform-hydration-red.log` and `platform-hydration-green.log`.

`npm run build` passed; evidence `platform-hydration-build.log`. Its preparation step refreshed the generated SpecWeave version counter from the locally installed CLI; that unrelated generated-file change was restored before committing, leaving the two-file source scope intact. Native pre-commit malware/secret scan passed.

Headless browser verification uses the actual fixed server/client component, a populated fixture and intercepted read-only destinations. It checks desktop and mobile widths, no nested anchors, no console/recoverable errors, preservation of the original server DOM node, keyboard Enter to the skill, keyboard Enter opening the repository tab, and middle-click opening the skill tab. Evidence: `artifacts/platform-hydration/fixed-headless-verification.json`.

The proof and remediation are authored by the same agent after the independent finding. Root must independently review the final change; this report does not approve its own remediation or claim the fix is deployed. The product agent retains ownership of T-29 video changes.
