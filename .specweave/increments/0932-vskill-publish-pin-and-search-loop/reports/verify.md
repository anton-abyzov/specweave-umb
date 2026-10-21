# Verify — 0932-vskill-publish-pin-and-search-loop

PASS · 2026-10-21T06:50:48.343Z · commands from explicit

## Commands

### `npm --prefix repositories/anton-abyzov/vskill test -- --maxWorkers=2` → exit 0 (154s)

```
See https://react.dev/link/invalid-hook-call for tips about how to debug and fix this problem.

stderr | src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx > T-059 TopRail — breadcrumb navigation > shows no breadcrumb navigation segments when nothing is selected
Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://react.dev/link/invalid-hook-call for tips about how to debug and fix this problem.

stderr | src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx > T-060 TopRail — model selector wiring > renders the ModelSelector slot in the right-side action cluster
Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://react.dev/link/invalid-hook-call for tips about how to debug and fix this problem.

stderr | src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx > T-060 TopRail — model selector wiring > the find-skills slot (Group A) is positioned before the model-selector slot (Group B)
Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://react.dev/link/invalid-hook-call for tips about how to debug and fix this problem.

 ✓ src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx (8 tests) 7ms
 ✓ src/eval-ui/src/pages/workspace/__tests__/EditorPanel.publishSkillPath.test.tsx (4 tests) 5ms
 ✓ src/eval-ui/src/components/__tests__/DetailHeader.copy.test.tsx (4 tests) 4ms
 ✓ src/eval-ui/src/components/__tests__/0800-editor-runall.test.tsx (4 tests) 4ms
stderr | src/eval-ui/src/components/__tests__/App.versions-tab.test.tsx > RightPanel — top-level tab wiring (0792 IA) > History tab panel renders the HistoryShell when allSkills is supplied
Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://react.dev/link/invalid-hook-call for tips about how to debug and fix this problem.

 ✓ src/eval-ui/src/components/__tests__/App.versions-tab.test.tsx (4 tests) 4ms
 ✓ src/eval-ui/src/__tests__/openFetchEventStream.onClose.test.ts (3 tests) 4ms
 ✓ src/eval-ui/src/hooks/__tests__/useSubmissionNotifications.test.ts (19 tests) 4ms
 ✓ src/eval-ui/src/utils/__tests__/toastQueue.test.ts (8 tests) 4ms
 ✓ src/eval-ui/src/preferences/lib/useDesktopBridge.test.ts (6 tests) 4ms
 ✓ src/eval-ui/src/hooks/__tests__/useStudioPreferences-skill-gen.test.ts (9 tests) 4ms
 ✓ src/eval-ui/src/pages/workspace/__tests__/VersionHistoryPanel.empty-state.test.tsx (5 tests) 3ms
 ✓ src/eval-ui/src/hooks/__tests__/useStudioPreferences.test.ts (5 tests) 6ms
 ✓ src/eval-ui/src/hooks/__tests__/useStudioPreferences.activeAgent.test.ts (4 tests) 2ms
 ✓ src/eval-ui/src/pages/workspace/__tests__/VersionHistoryPanel.local-fallback.test.tsx (3 tests) 2ms
 ✓ src/eval-ui/src/components/__tests__/StudioLayout.test.tsx (4 tests) 2ms

 Test Files  678 passed (678)
      Tests  7132 passed | 2 skipped (7134)
   Start at  02:48:06
   Duration  153.50s (transform 6.17s, setup 0ms, collect 23.33s, tests 173.88s, environment 30.07s, prepare 18.59s)
```

### `cd /Users/antonabyzov/Projects/github/wt-0932-0934/platform-finalize && npx --no-install vitest run src/lib/__tests__/search-slug.test.ts src/app/api/v1/cron/rescan-stale src/app/api/v1/skills src/app/api/v1/internal/finalize-scan src/lib/submission/__tests__/publish.test.ts --maxWorkers=2 --no-cache` → exit 0 (4s)

```
stderr | src/lib/submission/__tests__/publish.test.ts > publishSkill — search-index dirty flag (0752 US-002) > does not call markSearchIndexDirty when a guard throws inside the transaction
[publishSkill] skipping post-write steps for submission sub_dirty — no SkillVersion row was written.

 ✓ src/lib/submission/__tests__/publish.test.ts (12 tests) 59ms
 ✓ src/app/api/v1/skills/stream/__tests__/route.test.ts (12 tests) 25ms
 ✓ src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/diff/__tests__/route.test.ts (8 tests) 38ms
 ✓ src/app/api/v1/skills/search/__tests__/route-publisher.test.ts (7 tests) 20ms
 ✓ src/app/api/v1/cron/rescan-stale/__tests__/route.test.ts (9 tests) 13ms
 ✓ src/app/api/v1/skills/by-id/[id]/register-tracking/__tests__/route.test.ts (9 tests) 11ms
stderr | src/app/api/v1/skills/__tests__/route.test.ts > GET /api/v1/skills > returns 500 when getSkills throws
GET /api/v1/skills error: Error: DB down
    at /Users/antonabyzov/Projects/github/wt-0932-0934/platform-finalize/src/app/api/v1/skills/__tests__/route.test.ts:147:41
    at file:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/node_modules/@vitest/runner/dist/chunk-hooks.js:155:11
    at file:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/node_modules/@vitest/runner/dist/chunk-hooks.js:752:26
    at file:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/node_modules/@vitest/runner/dist/chunk-hooks.js:1897:20
    at new Promise (<anonymous>)
    at runWithTimeout (file:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/node_modules/@vitest/runner/dist/chunk-hooks.js:1863:10)
    at runTest (file:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/node_modules/@vitest/runner/dist/chunk-hooks.js:1574:12)
    at runSuite (file:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/node_modules/@vitest/runner/dist/chunk-hooks.js:1729:8)
    at runSuite (file:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/node_modules/@vitest/runner/dist/chunk-hooks.js:1729:8)
    at runFiles (file:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/node_modules/@vitest/runner/dist/chunk-hooks.js:1787:3)

 ✓ src/app/api/v1/skills/__tests__/route.test.ts (20 tests) 29ms
 ✓ src/app/api/v1/skills/lookup-by-name/__tests__/route.test.ts (9 tests) 62ms
 ✓ src/lib/__tests__/search-slug.test.ts (10 tests) 17ms
stdout | src/app/api/v1/skills/__tests__/check-source.waitUntil.test.ts > GET /api/v1/skills/check-source — waitUntil deprecation pipeline > threads deprecateStaleSkill through ctx.waitUntil and writes isDeprecated:true to DB on 404
[check-source] Auto-deprecated owner/repo/skill

stdout | src/app/api/v1/skills/__tests__/check-source.waitUntil.test.ts > GET /api/v1/skills/check-source — waitUntil deprecation pipeline > falls through to inline await when no Cloudflare context is available (local dev)
[check-source] Auto-deprecated owner/repo/skill

 ✓ src/app/api/v1/skills/__tests__/check-source.waitUntil.test.ts (5 tests) 29ms
 ✓ src/app/api/v1/skills/by-id/[id]/rescan/__tests__/route.test.ts (8 tests) 22ms
 ✓ src/app/api/v1/skills/search/__tests__/route-bwc-vskill-find.test.ts (3 tests) 7ms
 ✓ src/app/api/v1/skills/search/__tests__/dedup.test.ts (7 tests) 3ms
 ✓ src/app/api/v1/skills/search/__tests__/route-publisher-degrade.test.ts (3 tests) 57ms
 ✓ src/app/api/v1/skills/check-updates/__tests__/route.tenant-isolation.test.ts (2 tests) 27ms
 ✓ src/app/api/v1/skills/lookup-by-name/__tests__/route.tenant-isolation.test.ts (2 tests) 25ms
 ✓ src/app/api/v1/skills/installs/__tests__/route.test.ts (7 tests) 35ms
 ✓ src/app/api/v1/skills/stream/__tests__/route.submission-decision.test.ts (2 tests) 4ms
 ✓ src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.tenant-isolation.test.ts (3 tests) 17ms
 ✓ src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/[version]/__tests__/route.tenant-isolation.test.ts (3 tests) 18ms
 ✓ src/app/api/v1/skills/[owner]/[repo]/[skill]/eval/history/__tests__/route.tenant-isolation.test.ts (3 tests) 42ms
 ✓ src/app/api/v1/skills/lookup-by-name/__tests__/route.delimiter-collision.test.ts (1 test) 30ms
 ✓ src/app/api/v1/skills/[owner]/[repo]/[skill]/badge/__tests__/route.delisted.test.ts (2 tests) 5ms

 Test Files  29 passed (29)
      Tests  331 passed (331)
   Start at  02:50:40
   Duration  3.31s (transform 698ms, setup 150ms, collect 1.26s, tests 1.11s, environment 2ms, prepare 920ms)
```

### `cd /Users/antonabyzov/Projects/github/wt-0932-0934/platform-finalize && node --test crawl-worker/sources/submission-scanner.test.js` → exit 0 (2s)

```
      duration_ms: 20.0775
      type: 'test'
      ...
# [submission-scanner] helper: PUBLISHED (score=100) in 0.0s
# [submission-scanner] done: batches=2 checked=1 processed=1 skipped=0 errors=0 paused=0 abandoned=0
# [submission-scanner] CF_ACCOUNT_ID or CF_API_TOKEN not set — Tier 2 LLM will be skipped
# [submission-scanner] GEMINI_API_KEY not set — external LLM fallback disabled
# [submission-scanner] starting (concurrency=20, batchSize=50, t2=disabled, gemini=disabled)
# [submission-scanner] page 1: 1 submissions (concurrency=20)
    # Subtest: carries frontmatter bytes, SHA-256 and the pinned commit for acme
    ok 2 - carries frontmatter bytes, SHA-256 and the pinned commit for acme
      ---
      duration_ms: 21.824041
      type: 'test'
      ...
# [submission-scanner] helper: SKILL.md fetch failed (transient) — unclaiming for retry
# [submission-scanner] unclaim content-sub: requeued (retries=1)
# [submission-scanner] done: batches=2 checked=1 processed=0 skipped=1 errors=0 paused=0 abandoned=0
# [submission-scanner] CF_ACCOUNT_ID or CF_API_TOKEN not set — Tier 2 LLM will be skipped
# [submission-scanner] GEMINI_API_KEY not set — external LLM fallback disabled
# [submission-scanner] starting (concurrency=20, batchSize=50, t2=disabled, gemini=disabled)
# [submission-scanner] page 1: 1 submissions (concurrency=20)
# [submission-scanner] done: batches=2 checked=1 processed=1 skipped=0 errors=0 paused=0 abandoned=0
    # Subtest: retries a transient vendor document failure without finalizing
    ok 3 - retries a transient vendor document failure without finalizing
      ---
      duration_ms: 1758.04225
      type: 'test'
      ...
    # Subtest: reports a missing vendor document without vendor approval
    ok 4 - reports a missing vendor document without vendor approval
      ---
      duration_ms: 1.031208
      type: 'test'
      ...
    1..4
ok 1 - VM finalization carries the scanned document and identity
  ---
  duration_ms: 1801.722416
  type: 'suite'
  ...
1..1
# tests 4
# suites 1
# pass 4
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 1852.82125
```

### `npm view vskill version | grep -q 1.2.10 && vskill --version | grep -q 1.2.10` → exit 0 (1s)

```
(no output)
```

### `vskill whoami | python3 -c 'import sys; assert "Active tenant: anton-abyzov" in sys.stdin.read()' && gh run view 39383673080 -R anton-abyzov/vskill --json conclusion --jq .conclusion | grep -q success` → exit 0 (2s)

```
(no output)
```

### `curl --fail --silent https://verified-skill.com/api/v1/skills/anton-abyzov/specweave/sw-do | grep -q '"3.1.0"'` → exit 0 (0s)

```
(no output)
```

## Acceptance criteria

13/13 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | `vskill install --tenant <t> <skill> --version 1.0.0` (space form) reaches the install command; a unit test asserts the parsed option and that the program version is not printed. |
| AC-02 | x (tasks) | `vskill install owner/repo/skill@1.0.0` resolves the version through the registry's versions endpoint to its commit and installs that content; an unknown version exits 1 with the available versions listed; `vskill pin` prints a command that works. |
| AC-03 | x (tasks) | The lock `tier` comes from the registry: VERIFIED only when the installed content hash equals a registry version's hash, otherwise UNSCANNED with the registry's latest version named in the output; the hardcoded VERIFIED literals are gone. |
| AC-04 | x (tasks) | Both platform security checks pass the full `owner/repo/skill` name, and a mocked CRITICAL response blocks the install with exit 1. |
| AC-05 | x (tasks) | With `-y`, a short name auto-selects only an exact skill-slug match and otherwise exits 1 listing the candidates; an object-typed `plugin.source` is skipped, not thrown. |
| AC-06 | x (tasks) | One `owner/repo/skill` install makes at most 6 GitHub REST calls (asserted with a fetch spy); on a rate limit the fallback fetches raw `HEAD`, not `main`, and the message says the API limit was hit, not that the repo may be private. |
| AC-07 | x (tasks) | `update` writes the new `sourceCommitSha`; `outdated` reports an update when the source hash differs for GitHub-sourced skills; the compare route returns `status: "unavailable"` for a null side instead of "removed". |
| AC-08 | x (tasks) | `vskill doctor` accepts `<namespace>/<name>` frontmatter names and name-mismatch is namespace-aware (apify-data-gathering produces no bad-name finding). |
| AC-09 | x (tasks) | `GET /api/v1/skills/search?q=sw-do` returns `anton-abyzov/specweave/sw-do` first, and `/skills?search=sw-do` renders 200 in under 3 seconds through the same index. |
| AC-10 | x (tasks) | A published skill's description comes from its SKILL.md frontmatter, and a scheduled rescan re-verifies any skill whose source HEAD SKILL.md hash differs from its latest version's content hash. |
| AC-11 | x (tasks) | Messages and docs match behaviour: a 404 source says "not found", `submit` prints the full name for `vskill info`, a rejected submission is not reported as a duplicate, "Installed (symlinked)" says "copied" when it copies, and the CLI reference documents `--private`, `--tenant`, `--version`, `pin` and resubmit-to-republish. |
| AC-12 | x (tasks) | The account anton-abyzov has a tenant mapped to its GitHub App installation, `VSKILL_PLATFORM_TOKEN` is set on anton-abyzov/vskill, and the nightly live E2E is green once. |
| AC-13 | x (tasks) | vskill 1.2.10 is on npm and installed globally on this Mac; the private probe `e2e-probe-20261018` publishes at 1.0.0 and 1.0.1, installs pinned at both, updates to 1.0.1, and is then removed; the six specweave skills show their SKILL.md versions (3.1.0; sw-handoff is 3.0.0 in source) with real descriptions on verified-skill.com. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | 75791ba; npx vitest run src/commands/__tests__/install-vers… |  |
| T-02 | done | claude@antons-macbook-m4max | 89f2102; npx vitest run src/commands/__tests__/install-tier… |  |
| T-03 | done | claude@antons-macbook-m4max | 0a54436 + 77bf2a0 (object-source plugin selected by name no… |  |
| T-04 | done | claude@antons-macbook-m4max | 61123b6 (PR https://github.com/anton-abyzov/vskill/pull/189… |  |
| T-05 | done | claude@antons-macbook-m4max | 7404a33 + 56bbbe4 (PR https://github.com/anton-abyzov/vskil… |  |
| T-06 | done | claude@antons-macbook-m4max | CLI: 3a7623c in PR https://github.com/anton-abyzov/vskill/p… |  |
| T-07 | done | claude@antons-macbook-m4max | vskill-platform 41443b10 (PR #154): search-slug.test.ts 10/… |  |
| T-08 | done | claude@antons-macbook-m4max | vskill-platform 41443b10 (PR #154): rescan-stale + skills r… |  |
| T-09 | done | claude@antons-macbook-m4max | vskill 1.2.10 tagged v1.2.10 on 92e35a7 (PR https://github.… |  |
| T-10 | done | cli@antons-macbook-m4max | vskill whoami \| grep -q 'Active tenant: anton-abyzov' && g… |  |
| T-11 | done | claude@antons-macbook-m4max | All six core specweave skills now on verified-skill.com at … |  |
| T-12 | done | codex-0932-finalize | 14dc664cb9a40834bcbdb0ae3be4c88e19749ba5; Node22, npx vites… |  |
| T-13 | done | codex-0932-finalize | 5d9a4dbe03b0c148d5fd96e94f89e16b0fd57d23; merged current ma… |  |

13/13 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
