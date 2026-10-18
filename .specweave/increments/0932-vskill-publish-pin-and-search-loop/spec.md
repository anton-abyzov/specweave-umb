# 0932 vSkill publish, pin and search loop

## Problem

A live end-to-end test on 2026-10-18 (plan: https://claude.ai/artifact/Hto9NvYYpvDDFuGo5SwwxF) showed that `vskill install` from GitHub works in 2 to 6 seconds, but the publish, pin and search loop does not. `vskill install --tenant t x --version 1.0.0` prints `1.2.9` and exits 0 because the program-level `-v, --version` flag swallows the value (src/index.ts:14, :47). Public skills have no `owner/repo/skill@1.2.3` form and `vskill pin` prints that broken command (src/commands/pin.ts:63). Install never reads the registry: it fetches GitHub HEAD (3.1.0) while the registry knows 1.0.0, and stamps the lock `tier: VERIFIED` regardless (src/commands/add.ts:1559, 2155, 3020). The platform security check is called with the bare skill name, gets 404, and the CRITICAL block can never fire (add.ts:1687, :3133). `install sw-do -y` auto-selects `anthropics/knowledge-work-plugins/inbox-sweep` and crashes on an object-typed `plugin.source` (add.ts:584, :2394, :2702). Search drops `do` as an English stopword so `sw-do` is unfindable through the API, and `/skills?search=` runs a 5-column ILIKE over the catalog and returns HTTP 500 after 15 seconds (vskill-platform src/lib/search.ts:353, src/lib/data.ts:145). Each install costs 22 to 27 GitHub REST calls, so an anonymous user dies on the third install and the fallback guesses branch `main` (default is develop) and blames a private repo (src/discovery/github-tree.ts:168). `update` leaves `sourceCommitSha` stale and `outdated` disagrees with it; the compare route reports a null side as "removed". The registry description is the repo name (publish.ts:387, :428) and nothing rescans on push. Private publishing is blocked because the account has no tenant although GitHub App installation 135567134 exists. The nightly live E2E is red 10 of 10 for a missing `VSKILL_PLATFORM_TOKEN` secret (vskill#184). The PATH binary is 1.2.7 while npm has 1.2.9.

## Scope

In: the CLI fixes above in anton-abyzov/vskill, the platform fixes in anton-abyzov/vskill-platform, docs and messages, release vskill 1.2.10 and deploy the platform, the tenant connection and the nightly secret, a rerun of the private publish probe (1.0.0 then 1.0.1), and resubmitting the six specweave skills so the registry carries 3.1.0. Out: the Studio skills view (0934), the hackathon copy repo, any change to the registry schema.

## Acceptance Criteria

- [ ] AC-01: `vskill install --tenant <t> <skill> --version 1.0.0` (space form) reaches the install command; a unit test asserts the parsed option and that the program version is not printed.
- [ ] AC-02: `vskill install owner/repo/skill@1.0.0` resolves the version through the registry's versions endpoint to its commit and installs that content; an unknown version exits 1 with the available versions listed; `vskill pin` prints a command that works.
- [ ] AC-03: The lock `tier` comes from the registry: VERIFIED only when the installed content hash equals a registry version's hash, otherwise UNSCANNED with the registry's latest version named in the output; the hardcoded VERIFIED literals are gone.
- [ ] AC-04: Both platform security checks pass the full `owner/repo/skill` name, and a mocked CRITICAL response blocks the install with exit 1.
- [ ] AC-05: With `-y`, a short name auto-selects only an exact skill-slug match and otherwise exits 1 listing the candidates; an object-typed `plugin.source` is skipped, not thrown.
- [ ] AC-06: One `owner/repo/skill` install makes at most 6 GitHub REST calls (asserted with a fetch spy); on a rate limit the fallback fetches raw `HEAD`, not `main`, and the message says the API limit was hit, not that the repo may be private.
- [ ] AC-07: `update` writes the new `sourceCommitSha`; `outdated` reports an update when the source hash differs for GitHub-sourced skills; the compare route returns `status: "unavailable"` for a null side instead of "removed".
- [ ] AC-08: `vskill doctor` accepts `<namespace>/<name>` frontmatter names and name-mismatch is namespace-aware (apify-data-gathering produces no bad-name finding).
- [ ] AC-09: `GET /api/v1/skills/search?q=sw-do` returns `anton-abyzov/specweave/sw-do` first, and `/skills?search=sw-do` renders 200 in under 3 seconds through the same index.
- [ ] AC-10: A published skill's description comes from its SKILL.md frontmatter, and a scheduled rescan re-verifies any skill whose source HEAD SKILL.md hash differs from its latest version's content hash.
- [ ] AC-11: Messages and docs match behaviour: a 404 source says "not found", `submit` prints the full name for `vskill info`, a rejected submission is not reported as a duplicate, "Installed (symlinked)" says "copied" when it copies, and the CLI reference documents `--private`, `--tenant`, `--version`, `pin` and resubmit-to-republish.
- [ ] AC-12: The account anton-abyzov has a tenant mapped to its GitHub App installation, `VSKILL_PLATFORM_TOKEN` is set on anton-abyzov/vskill, and the nightly live E2E is green once.
- [ ] AC-13: vskill 1.2.10 is on npm and installed globally on this Mac; the private probe `e2e-probe-20261018` publishes at 1.0.0 and 1.0.1, installs pinned at both, updates to 1.0.1, and is then removed; the six specweave skills show 3.1.0 with real descriptions on verified-skill.com.

## Approach

CLI first (one worktree, one PR to main), platform second (one worktree, one PR to main), then release and ops. In the CLI: `program.enablePositionalOptions()` plus `passThroughOptions` on `install`; a `resolveRegistryVersion(owner, repo, skill, version)` helper used by `@version`, by the tier decision and by `pin`; `checkPlatformSecurity(fullName)`; `resolveViaSearch` exact-slug gate; a single `fetchRepoTree` call cached per install with raw `HEAD` reads. Platform: `simple` tsvector config for the slug column with an exact-slug boost, SSR search routed through `searchSkills`, description from frontmatter at publish and recovery, a cron route `/api/v1/cron/rescan-stale` guarded by the existing cron secret. Rejected: shipping `name@version` by fetching GitHub tags (the registry already stores gitSha per version). Risk: the rescan job must respect the installation rate limit (src/lib/installation-rate-limit.ts).

## Decisions

- D-01 Tenant connection: go through the platform's own Connect flow at /settings/integrations so the callback creates the tenant with the real user id; the webhook path is the fallback.
- D-02 Version pin flag stays `--version` for compatibility; the fix is option parsing, not a rename.
- D-03 Resubmitting the specweave skills publishes to the public registry (approved by the owner, 2026-10-18, D4).

## Open questions

- Why installation 135567134 produced no tenant (webhook failure or install outside the callback). Answer from the audit log once the tenant exists.

## Tasks

### T-01 Option parsing and name@version
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/vskill/src/index.ts, repositories/anton-abyzov/vskill/src/commands/add.ts, repositories/anton-abyzov/vskill/src/commands/pin.ts, repositories/anton-abyzov/vskill/src/lib/registry-version.ts, repositories/anton-abyzov/vskill/src/commands/__tests__/install-version.test.ts | Test: cd repositories/anton-abyzov/vskill && npx vitest run src/commands/__tests__/install-version.test.ts

### T-02 Registry-aware tier and the security gate
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/vskill/src/commands/add.ts, repositories/anton-abyzov/vskill/src/lib/platform-security.ts, repositories/anton-abyzov/vskill/src/commands/__tests__/install-tier.test.ts | Test: cd repositories/anton-abyzov/vskill && npx vitest run src/commands/__tests__/install-tier.test.ts

### T-03 Short-name resolution and plugin.source guard
- AC: AC-05 | Files: repositories/anton-abyzov/vskill/src/commands/add.ts, repositories/anton-abyzov/vskill/src/commands/__tests__/install-shortname.test.ts | Test: cd repositories/anton-abyzov/vskill && npx vitest run src/commands/__tests__/install-shortname.test.ts

### T-04 Fewer GitHub calls and a HEAD fallback
- AC: AC-06 | Files: repositories/anton-abyzov/vskill/src/discovery/github-tree.ts, repositories/anton-abyzov/vskill/src/commands/add.ts, repositories/anton-abyzov/vskill/src/discovery/__tests__/github-calls.test.ts | Test: cd repositories/anton-abyzov/vskill && npx vitest run src/discovery/__tests__/github-calls.test.ts

### T-05 update, outdated and doctor names
- AC: AC-07, AC-08 | Files: repositories/anton-abyzov/vskill/src/commands/update.ts, repositories/anton-abyzov/vskill/src/commands/outdated.ts, repositories/anton-abyzov/vskill/src/commands/doctor.ts, repositories/anton-abyzov/vskill/src/installer/frontmatter.ts, repositories/anton-abyzov/vskill/src/commands/__tests__/update-outdated.test.ts, repositories/anton-abyzov/vskill/src/commands/__tests__/doctor-namespace.test.ts | Test: cd repositories/anton-abyzov/vskill && npx vitest run src/commands/__tests__/update-outdated.test.ts src/commands/__tests__/doctor-namespace.test.ts

### T-06 Messages and docs
- AC: AC-11 | Files: repositories/anton-abyzov/vskill/src/lib/private-source.ts, repositories/anton-abyzov/vskill/src/commands/submit.ts, repositories/anton-abyzov/vskill/src/commands/add.ts, repositories/anton-abyzov/vskill/README.md, repositories/anton-abyzov/vskill-platform/src/app/docs/cli-reference/page.mdx, repositories/anton-abyzov/vskill-platform/src/app/docs/submitting/page.tsx | Test: cd repositories/anton-abyzov/vskill && npm test

### T-07 Platform search
- AC: AC-09 | Files: repositories/anton-abyzov/vskill-platform/src/lib/search.ts, repositories/anton-abyzov/vskill-platform/src/lib/data.ts, repositories/anton-abyzov/vskill-platform/src/app/skills/page.tsx, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/search-slug.test.ts | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/__tests__/search-slug.test.ts

### T-08 Descriptions, rescan and compare
- AC: AC-07, AC-10 | Files: repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts, repositories/anton-abyzov/vskill-platform/src/lib/queue/recovery.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/cron/rescan-stale/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/compare/route.ts, repositories/anton-abyzov/vskill-platform/wrangler.toml, repositories/anton-abyzov/vskill-platform/src/app/api/v1/cron/rescan-stale/__tests__/route.test.ts | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/app/api/v1/cron/rescan-stale src/app/api/v1/skills

### T-09 Release vskill 1.2.10 and deploy the platform
- AC: AC-13 | Files: repositories/anton-abyzov/vskill/package.json, repositories/anton-abyzov/vskill/CHANGELOG.md, .specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/release.md | Test: npm view vskill version | grep -q 1.2.10 && vskill --version | grep -q 1.2.10

### T-10 Tenant, nightly secret and the live probe
- AC: AC-12, AC-13 | Files: .specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/probe.md | Test: vskill whoami | grep -q 'Active tenant: anton-abyzov' && gh run list -R anton-abyzov/vskill -w 'E2E Live (nightly)' -L 1 --json conclusion -q '.[0].conclusion' | grep -q success

### T-11 Resubmit the specweave skills
- AC: AC-13 | Files: .specweave/increments/0932-vskill-publish-pin-and-search-loop/reports/resubmit.md | Test: curl -s https://verified-skill.com/api/v1/skills/anton-abyzov/specweave/sw-do | grep -q '"3.1.0"'
