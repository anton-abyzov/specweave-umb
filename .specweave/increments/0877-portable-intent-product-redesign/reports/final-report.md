# SpecWeave and Verified Skills: redesign, cleanup, and release report

Date: 2026-09-14. Increment: 0877. SpecWeave 2.1.0 and vskill 1.1.1 are published and installed. Both redesigned websites are deployed and verified. All release PRs are merged; the final delivery fix is live.

## Product decision

Keep both products, with a narrower purpose. SpecWeave preserves requested outcomes and evidence when work moves between coding tools. Verified Skills helps people find focused expertise, inspect its source and security evidence, and evaluate whether it improves their actual work. A generic board and a large prompt catalog do not justify a business by themselves. This release establishes a testable product direction; it does not prove paid demand or productivity gains.

The product layers are now **intent → specification and evidence → execution history → optional connections**. An intent represents a desired outcome. It can span several conversations, agents, and models; a single conversation can contain several intents. Small work can remain an intent without creating an increment.

Both requested OpenAI articles were read in full: [Rethinking skills and prompts](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) and [Managing usage](https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex). Detailed analysis and primary-source comparisons with Linear, Jira, Azure Boards, and agent platforms appear in [product-research.md](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/product-research.md). Alternatives and the chosen direction appear in [brainstorm.md](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/brainstorm.md) and [research.md](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/research.md).

## Delivery status

| Deliverable | Status | Evidence |
|---|---|---|
| SpecWeave 2.1.0 | Published through trusted OIDC; registry package installed and verified | [Release](https://github.com/anton-abyzov/specweave/releases/tag/v2.1.0), [installation evidence](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/specweave-local-install.md) |
| SpecWeave website | Live; final Pages deployment succeeded and 18/18 production flows passed with zero runtime/console errors | [Site](https://spec-weave.com), [HTML report](https://spec-weave.com/releases/2.1/), [PR 1940](https://github.com/anton-abyzov/specweave/pull/1940), [delivery fix PR 1944](https://github.com/anton-abyzov/specweave/pull/1944) |
| vskill 1.1.1 | Published after scoped credential replacement; registry package installed and verified | [Release](https://github.com/anton-abyzov/vskill/releases/tag/v1.1.1), [installation evidence](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/vskill-local-install.md) |
| Verified Skills website | Live; real catalog, navigation, downloads, video and 12 accessibility audits passed | [verified-skill.com](https://verified-skill.com), [deployment evidence](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/platform-deployment.md) |
| Personal/project skill cleanup | Complete, with reversible backups | [skills-audit.md](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/skills-audit.md) and [cleanup-manifest.json](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/cleanup-manifest.json) |

The user explicitly approved all merges and final delivery. PR #1940 merged at `b5e796882`; its production verification found two inherited delivery defects, repaired in independently reviewed PR #1944. Final merge `5d9a91cb27f49a5ad9414d55dd3f96f6089a189c` deployed successfully in [Pages run 34882131675](https://github.com/anton-abyzov/specweave/actions/runs/34882131675). Final GitHub unit/E2E/smoke CI and documentation build/full crawl pass. The native CLI installations remain SpecWeave 2.1.0 and vskill 1.1.1; these later changes affect website delivery only.

[Open the concise HTML report](https://spec-weave.com/releases/2.1/) for changes, reasons, cleanup, limitations and product links. The source report was independently reviewed; desktop/mobile keyboard checks and four final production accessibility audits pass with zero violations. Its reviewed bytes match production after accounting for one precisely identified Cloudflare analytics insertion.

The completed production crawl checks 654 links. All owned routes and former email/canonical/edit-link failures are resolved; two occurrences of the same external Render pricing URL time out from this Mac. The identical CI crawler passes, and independent web access confirms the official page remains available. This external connectivity limit is retained in the logs, not hidden by a new exclusion.

Increment 0877 is completed through the CLI: **36/36 tasks, 8/8 acceptance criteria**, verification green. Its configured closure hooks created GitHub milestone #258 and ADO item #2451; both are closed/Done. The optional Jira mirror returned 404 “Site temporarily unavailable” and did not create an issue. The CLI left the new empty GitHub milestone open, so it was explicitly closed after verification. These provider-side results are recorded separately from successful package/site delivery; Jira is not claimed synchronized.

## SpecWeave: what changed

### Live work board and trustworthy progress

The dashboard now opens on a work board with concise intent summaries, persistent workflow states, optional clickable increment links, drag-and-drop movement, and equivalent accessible controls. Evidence and sessions have their own surfaces; secondary diagnostics no longer dominate the entry screen. The layout works on desktop and mobile.

The board reads current task ledgers and acceptance criteria. Older task formats remain supported. A card moved to Done does not fabricate a passed check or mark its linked increment complete. Verification becomes stale when its authoritative inputs change. Corrupt history records are isolated and reported; unsafe revision updates are rejected instead of silently overwriting newer history.

Intent state lives in `.specweave/intents/board.jsonl`. Filesystem events and a reconciliation poll refresh the board. Session metadata also refreshes while the board stays open. Reading and updating this state invokes no language model. SessionStart and handoff output carry a small, scrubbed intent summary and a pointer to the durable file, including work with no increment.

### Harness and model history

Execution records distinguish harness, model, effort, provider, surface, actor, and session. Declared configuration, ledger actors, and observed native session metadata are labeled separately. Explicit association avoids assigning an unrelated session to a task simply because it used the same project directory.

Codex and Claude Code adapters read bounded local log windows and cache results. Large logs are marked partial. The API returns execution metadata, not conversation text, tool payloads, or native transcript paths. The dashboard binds to loopback and checks Host and Origin on requests.

Model identities remain exact. An unrecognized model is not relabeled as an older supported model. Missing, mixed, or unpriced usage displays Unknown; a known subtotal is separate from an incomplete total. Existing exact-model pricing is labeled as an estimate, not a bill. The current cost view describes available Claude Code usage, not universal Codex subscription spending.

OpenRouter belongs under provider/router unless it supplies the actual agent loop. VS Code or terminal belongs under surface. Changing harness while retaining a model can change behavior, but unrelated task histories cannot establish which configuration is better.

### Fewer hooks

Default plugin hooks are now SessionStart and Stop. Default PreToolUse interception and PreCompact capture are removed. Ordinary Stop events return before loading the CLI; explicitly enabled auto mode retains continuation. Supported session identifiers and existing worker deadlines remain covered by regression tests. Actual Codex cache contents and all four existing Claude registrations now point to 2.1.0. Two stale project registrations pointing to missing 1.0.591 caches were repaired. Nine independent configuration files and five unrelated Claude registrations were preserved.

The installed hook-health history contained 150 compaction deadline expirations at roughly eight seconds each: about 20 minutes of recorded waiting. This is historical evidence of overhead, not a measured failure rate or a claim that every future run saves that much time.

### Integrations and limits

GitHub, Jira, and Azure DevOps remain optional and have a dedicated connections/documentation area. Their enterprise usefulness depends on preserving existing team records, not on making everyone adopt another tracker.

The release repairs external pull reporting: failures are visible, successful partial results survive, explicit GitHub configuration wins, and incomplete pulls exit unsuccessfully. Pull currently reports external changes; it does not promise a conflict-resolving bidirectional merge. No live enterprise records were modified during verification.

The proposed next reconciliation design uses stable external IDs, last-synced field snapshots, field ownership, idempotent operations, provider cursors, and explicit conflicts when both sides change. That algorithm is documented as future work. See [integration-failures.md](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/integration-failures.md).

The active-increment limit was already advisory in SpecWeave 2. `limits.activeIncrements: 0` disables its note. The new board has no hard card cap.

## Websites and Verified Skills

A compact Built with SpecWeave section now restores EasyChamp, JobWeave and Verified Skills to the homepage. The project guide retains ten examples, including the mobile apps and EduFeed. It explicitly distinguishes ongoing EasyChamp work from its earlier history and removes unsupported development-speed and zero-failure claims. AnyModel is omitted because this audit did not establish its relationship to the workflow.

SpecWeave's website now explains portability, actual evidence, lightweight intent, and optional integrations through layered product pages. The old skill-count and orchestration emphasis is removed. The interactive homepage board is clearly an illustration; it does not pretend to show live customer results. Navigation, installation copy, integration disclosures, and mobile behavior are exercised in headless browser checks. The strict broken-link build gate is restored, old aliases are replaced with canonical destinations, and the placeholder template is excluded from publication. Two root README links now work after the exact CI copy into the documentation tree; a reproduced failed deployment build passes after the fix. Current dashboard, hook, model-selection and cost guides now describe shipped 2.1 behavior; two older routing articles are labeled historical. Documentation navigation was repaired without inventing missing pages or suppressing the existing link-check configuration. See [semantic corrections](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/docs-2.1-semantics.md) and [link cleanup](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/docs-link-cleanup.md).

Verified Skills now separates discovery, source/security evidence, usefulness, and Studio. Real catalog search and existing skill data remain connected. The methodology page explains what evidence can establish and what it cannot. The Studio page explains the local/cloud boundary, retains useful actions and video playback, and labels the older recorded version. The legacy Studio URL redirects to the canonical page. Live testing caught a production-only video failure: the asset server ignored byte ranges, so chapter seeking restarted at zero. A streaming adapter now serves exact partial responses for the two existing recordings. It avoids buffering the entire file, though a late seek still reads and discards the upstream prefix. No storage service or credential was added. Populated trending rows also had nested links that triggered hydration recovery; separate skill and repository links now preserve valid server-rendered markup.

Kie.ai GPT Image 2 produced two original graphics: a continuity ribbon for SpecWeave and a layered evidence image for Verified Skills. Optimized WebP assets are approximately 175 KB and 139 KB. They explain the product direction without replacing real interface data. Desktop, mobile, dark-mode, keyboard, and contrast checks informed the final styles.

Production verification also isolated a duplicated Cloudflare analytics snippet: the manual cross-origin request failed, while the edge-injected same-origin request succeeds with HTTP 204. The duplicate is removed. Documented HTML comment boundaries preserve email-like command examples without changing Cloudflare account settings. All 183 generated app pages have balanced boundaries, and all 256 HTML files omit the manual beacon. Live pages now have a single working beacon and no rewritten email-protection URLs. No browser errors or crawler targets were filtered to obtain those results.

No new private-repository backend, database migration, desktop binary, or universal skill quality certification is implied by this redesign. Existing repository-wide TypeScript diagnostics remain documented; production builds passing are not presented as a clean full-repository typecheck.

## Skill cleanup and vskill fixes

48 obsolete installed locations were backed up and removed:

| Removed installation | Locations | Reason |
|---|---:|---|
| `greet-anton` | 13 | Unconditional greeting conflicts with current preferences and supplies no expertise |
| Tiny test plugin | 6 | Runtime test fixture leaked into active skill discovery |
| Malformed Postiz wrapper | 14 | Unresolved pointer instead of usable skill instructions |
| Old project Obsidian Brain | 12 | Shadows the newer global workflow with obsolete scheduling guidance |
| `my-skill` | 1 | Exact cold-email duplicate with malformed metadata |
| Broken Remotion link | 1 | Target no longer exists |
| Archived Excalidraw installation | 1 | Still discoverable despite being archived |

Actual Postiz plugins, current global Obsidian Brain, working Remotion guidance, domain procedures, App Store skills, release credentials, source fixtures, and explicit style preferences remain. Divergent social-media skills were retained because they contain different accumulated knowledge; consolidation needs a content merge and outcome checks.

Across six primary personal/project roots, references fell from 180 to 168, physical skill files from 129 to 119, and distinct names from 85 to 80. The 48-location cleanup also includes other harness directories, so those numbers measure different scopes. No token savings percentage is invented from installation counts.

vskill previously compared global plugin registrations against a project lock and could remove valid global plugins and shared caches. Cleanup/removal now respect local and global ownership, legacy home locks, nested project locks, and registered external plugins. An unreadable local ownership file stops unsafe fallback. A fixed cleanup dry run on this machine proposes no remaining removals.

Backups are outside all discovery roots at `/Users/antonabyzov/.codex/skill-backups/0877`, with mode 0700. Restore one name with `python3 /Users/antonabyzov/.codex/skill-backups/0877/restore.py NAME`, or omit names to restore all 48 locations. Recovery refuses to overwrite current files and merges missing lock entries. Already-running harnesses need a new session to refresh their loaded skill catalog.

## Installation and credential recovery

Every installed SpecWeave package file (4,125) and vskill package file (758) matches its published registry tarball. The compiled dashboards and Studio assets match the tested builds. Both installations preserve refreshed plugin caches and user configuration. Backups contain the previous package payloads and registries; installation lifecycle scripts were disabled defensively. The existing preuninstall script deletes shared plugin caches if run directly; a disposable npm 10.9.3 uninstall did not invoke it or remove its cache sentinel.

Start a fresh Codex session and restart Claude Code to load the new plugin manifests. Restart any already-running dashboard or Studio process to use the newly installed code. No user session was terminated. Open the board with `specweave dashboard`, or `specweave dashboard --no-browser` to obtain its URL.

Nine distinct older npm credentials found across the authorized project/vault/config search were invalid. After the user completed npm login, a new granular credential was created for **vskill only**, with package write permission, no organization access, CI 2FA bypass and expiry **2026-12-13**. It was validated against npm, stored as plaintext with file mode 0600 using Obsidian Brain, and supplied to the repository's `NPM_TOKEN` secret through stdin. The retry published 1.1.1 successfully. SpecWeave continues using trusted OIDC and does not need this token.

Private credential location: [vskill npm publishing token 2026-09-14.md](</Users/antonabyzov/Projects/Obsidian/personal-docs/003 Resources/Technical Knowledge/Credentials-Secrets-Passwords/Developer-Tools/npm/vskill npm publishing token 2026-09-14.md>). The master npm note links to it. Obsidian's routing log contains metadata only; no credential is copied into this report, source repositories, wiki content, or tool output.

## Verification and review

| Surface | Observed result | Limits |
|---|---|---|
| SpecWeave standard unit suite | 16,495 passed; 160 existing skips; 740 passing files. Line coverage 68.67%, statements 68.10%, branches 60.95%, functions 70.58%. | Node 22, standard repository command. Earlier fast-config timing failures are retained in logs; the standard run passed. |
| SpecWeave dashboard | 20 dedicated headless checks passed, covering intent persistence, drag and accessible movement, linked evidence, session association/live updates, rejected cross-origin writes, exact model costs and mobile behavior. | Disposable fixtures exercise mutations; installed real-project validation is read-only. |
| Installed real-project dashboard | 257 items, 6 active; 3,219/3,633 tasks complete at capture. Zero page errors, HTTP failures, mutation requests or model calls. | Snapshot of actual project files, not a claim that all completed cards have passing verification. |
| Hooks, packaging and portability | Supported-OS hook checks, skills lint, builds and package preflight passed. Independent final portability review: 98 focused tests and 21 additional schema/path assertions passed. | Final delivery-head unit, E2E and smoke CI 34881875938 all pass; earlier runs recorded an intermittent unchanged LSP wall-clock benchmark. An earlier full E2E run passed all 89 executed cases. CLI-hint timeout was fixed by reducing unnecessary work with identical scan results. The lifecycle contract correction passes all eight CLI cases. Failed attempts remain recorded. |
| Integrations | 894 broad sync tests and 27 focused checks passed; changed-file coverage 93.18%; disposable CLI smoke passed. | No live Jira, ADO or GitHub records changed for testing; full conflict reconciliation remains future work. |
| vskill | 6,167 tests passed, 2 existing skips; 625 passing files. Coverage: 64.81% lines/statements, 80.12% branches, 75.11% functions. CLI/Studio build and package preflight passed. | Installed Studio navigation passed. Existing signed-out optional account requests repeatedly return 401 and remain unfixed. |
| SpecWeave website | Production builds and dedicated headless desktop/mobile navigation passed; final six guide routes, 19 semantic checks and 14 canonical guide links passed. | Final Pages deployment and all 18 production route/device flows pass with zero runtime/console errors. GitHub full link crawl 34881875897 passes; local production crawl retains only the two external Render pricing timeouts. Source typecheck has 102 existing diagnostics. Full docs tests: 190 passed / 10 failed; all remaining failures reproduced on v2.0.3. Current config/navigation/footer: 16 passed, including the two reproduced delivery regressions. Neither full suite nor full typecheck is claimed green. |
| Verified Skills website | Production Worker build, queue contract, 32 hotfix checks and three focused browser flows passed. Live catalog/search, three installer links, both exact video byte ranges, cold chapter seeking, captions and mobile navigation passed. All 12 live route/theme/viewport axe checks had zero serious/critical findings, overflow or browser errors. | Final full unit CI passed 5,858 tests across 629 passing files, with 14 tests and 4 files skipped. Production checks are recorded in the deployment report. Whole-repository typecheck/lint remain imperfect; see below. |

Independent reviews covered the dashboard, site/hooks, integration failure paths, vskill ownership, cost reporting, portable context and current documentation. Confirmed findings were fixed with regression evidence and independently rechecked. [Review evidence](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/review.md) records coverage and remaining limitations.

The repaired platform private-workspace E2E workflow now executes its 46 cases: **35 passed, 5 failed, 3 flaky, 3 skipped**. All three authenticated accessibility cases pass after the account-menu fix. Remaining failures cover private-publish feedback, a mock catalog seed and three expected HTTP 404 statuses that instead arrive as streamed 200 responses containing the 404 page. Inspected responses contain no private description or banner. These paths are unchanged relative to the pre-redesign source; a complete baseline runtime replay was not performed. This is not a claim that the suite is green or a proof that all five failures predate the release.

Platform source TypeScript comparison found 291 baseline diagnostics versus 290 final diagnostics, with none added; the full generated-artifact check reports 314. Next already ignores build-time type errors, and its lint script lacks configured ESLint. No tests, thresholds or rules were weakened to hide these limits. Detailed logs: [platform verification](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/platform-verification.md) and [deployment evidence](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/platform-deployment.md).

Deployment details and reproducible checks are in [specweave-deployment.md](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/specweave-deployment.md).

All automated browser tests and visual verification ran headlessly with inspector/UI opening disabled. The explicitly authorized npm credential recovery used Chrome separately. Screenshots, recordings, and logs are saved locally under `reports/artifacts/`. Existing unrelated dirty checkouts were preserved; changes were developed in isolated worktrees and committed in their owning repositories.

## Captured interface

Installed published SpecWeave 2.1.0 against this real project, before increment closure. Counts can change as agents finish work.

![Installed SpecWeave work board](/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0877-portable-intent-product-redesign/reports/artifacts/installed-dashboard-real-project.png)

## What is deliberately not claimed

There is no universal automatic transcript-to-intent assignment, remote telemetry service, matched harness leaderboard, calibrated completion forecast, or proven reduction in software delivery time. No synthetic project deadline or subscription dollar figure is displayed as measured fact. Existing enterprise synchronization was improved and scoped, not fully replaced with the proposed reconciliation engine.

## Business validation and kill criteria

Run a four-week pilot with people who switch coding tools during real work. Compare against a short checked-in handoff document. Measure re-explaining time, missed acceptance criteria, reopened work, handoff time, confidence in completion evidence, and repeated use. For skills, compare representative tasks with and without each skill while holding model, harness, effort, and outcome checks constant.

The initial customer is a developer or small team already switching between two or more coding tools on the same repository. The concrete offer is a shorter, more reliable handoff with visible acceptance evidence. A proposed pilot gate—not an observed result—is at least five weekly returning users and 30 real handoffs, with at least 25% less median re-explaining time than the Markdown baseline and no increase in missed acceptance criteria. For skills, require repeated outcome improvement on representative tasks; token reduction alone does not count as better work.

The main strategic risk is that native harnesses make portable handoff and evaluation routine. A board's appearance and a prompt catalog offer little protection from that. Keep the state format open; consider charging only for team coordination, policy/evidence retention and reliable enterprise connectors when customers ask for them and commit to pay. Avoid building those layers merely to justify the current codebase.

Seek paid pilot commitments before enterprise administration. If the board does not outperform checked-in Markdown, stop expanding it and retain a small interoperable CLI/state format. If skills do not show repeatable benefit, narrow the registry to provenance and maintenance. If neither produces recurring user value, stop product expansion. The honest case for continuing is cross-tool continuity and inspectable evidence; the business still has to earn its existence.
