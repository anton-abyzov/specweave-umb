# Verified Skills deployed and verified — 0877

[Verified Skills](https://verified-skill.com) is live and verified. [PR68](https://github.com/anton-abyzov/vskill-platform/pull/68) redesigned the product; [PR69](https://github.com/anton-abyzov/vskill-platform/pull/69) repaired defects found during live verification. Both merged normally, without admin bypass, after independent root review.

| Release evidence | Current value |
|---|---|
| Source | `51032632b3da86de89ee262b257735109c9f21a6`, PR69 squash merge at 2026-09-14T07:44:24Z; tree identical to reviewed `093bdc0` |
| Worker version | `671dfaed-3df4-4aec-8520-755f52085f53` |
| Deployment | `3eec2517-0a33-4341-a000-b3f665755082`, 2026-09-14T07:45:03.129558Z, 100% traffic |
| Validation | Fresh OpenNext Worker build, queue build contract, Wrangler dry-run, and public/internal queue deployment smoke all pass |

Existing bindings and remote variables were preserved with `--keep-vars`. No production database migration ran.

Live headless verification passes: 16-category/10-trending catalog data; TypeScript search with 20 results; actual result navigation to `microsoft/fast/typescript` with its install command visible; canonical Studio redirect; all three published native installer links (1.0.63); exact 1,024-byte 206 responses for both recording formats; cold native video seeking from 7→75→7 seconds; 11 caption cues; and mobile navigation. The final video sample has readyState 4 at 7.020467 seconds.

Twelve route/viewport/theme combinations (`/`, `/methodology`, `/studio`; 1440/390px; light/dark) have **zero serious/critical WCAG violations, zero overflow, and zero browser errors**. Desktop/mobile screenshots were visually inspected. Evidence is in `artifacts/platform-redesign/production/report.json`, `catalog-navigation.json`, and 12 screenshots named `{home,methodology,studio}-{1440,390}-{light,dark}.png`.

Hotfix validation: **32 focused tests pass**, including three real-workerd ASSETS/range/HEAD/routing tests; **3 product E2E tests pass**. Exact-head unit CI [`34819085901`](https://github.com/anton-abyzov/vskill-platform/actions/runs/34819085901) is **green: 5,858 passed, 14 skipped; 629 files passed, 4 skipped**. It completed at 2026-09-14T07:52:12Z (9m51s). PR68's earlier full CI `34816692738` passed 5,826 tests with 14 skips.

Private-workspace CI `34819086030` finished with the same disclosed result: **35 passed, 5 failed, 3 flaky, 3 existing skips** in 2.3 minutes. The remaining failures concern private publish feedback, a mock catalog seed, and three streamed-notFound HTTP status assertions; the 404 bodies contain no private content. Their backend/test expressions are unchanged by the redesign. A complete pre-change runtime replay was not performed.

Rollback targets: the immediately preceding reviewed redesign version `9d71aeab-3b57-4af2-9f2c-425d87e3b8d7` (PR68, with the two diagnosed defects), or pre-redesign version `2ff7bf82-5deb-4d82-8f6a-fe201661210f`. No rollback was needed. Deployment inventories and logs are preserved under `artifacts/platform-redesign/release/`.

Root independently approved T30 `52eabeb` (integrated as `f94f88d`) and T29 `093bdc0` before redeployment. The media adapter streams selected bytes from the existing asset cache. Late seeks still read/discard their prefix internally; this bounded-memory tradeoff avoids new storage/bindings and should be revisited if recording sizes or traffic justify native range-backed storage.

Older sections below preserve diagnostic history; this section records the current release.

## Deployment target and build

This is an OpenNext Cloudflare Worker, not a static Next export or Cloudflare Pages project. `wrangler.jsonc` targets Worker `verified-skill-com`, with custom domains `verified-skill.com` and `www.verified-skill.com`; main entry is `.open-next/worker-with-queues.js` and assets are `.open-next/assets`.

The repository’s explicit deployment chain is:

```sh
npm run deploy
# clean -> build:worker -> verify-queue-health-build -> wrangler deploy -> verify-queue-health-deploy
```

`build:worker` invokes OpenNext and then `scripts/build-worker-entry.ts`. The wrapper retains the existing fetch handler, scheduled jobs, queue consumers, and Durable Object exports. A successful plain `npm run build` does not prove the Worker bundle can deploy; the OpenNext build and queue-health contract checks remain required at release time.

Build requirements: Node 22 is used in repaired CI; installed dependencies, `npm run setup` (allowlisted native rebuilds and Prisma client generation), and canonical companion vskill source either at `../vskill` or `node_modules/vskill`. `scripts/sync-agents-json.cjs` derives supported agents/counts and looks up the SpecWeave version. CI now checks out pinned vskill commit `075fcc4209c540bf08e0376448c7ce5f645062a3` into `node_modules/vskill` after npm installation.

The new artwork is 135.3 KiB WebP and the walkthrough poster is about 9 KiB. Studio references existing tracked video assets: MP4 about 9 MiB, WebM about 10 MiB, plus VTT. Those individual assets are below the repository-documented 25 MiB Worker asset limit. The separate ignored oversize homepage demo must remain excluded.

## Existing production bindings and verification

The unchanged Worker configuration includes Hyperdrive, Workers AI, existing KV namespaces, queues, analytics datasets, Durable Objects, an audit archive bucket, desktop-release R2 bucket, and self-reference. Retain those bindings. The product redesign adds no database schema, migration, secret, queue, cron, or Worker-binding change.

Wrangler needs the existing deployment authorization. The final queue-health smoke script also requires `INTERNAL_BROADCAST_KEY` from the environment or local `.dev.vars`/`.env.local`/`.env`. Check presence without printing its value. It verifies the public queue-health schema/freshness and calls the internal queue-health endpoint with `dryRun=1`.

`scripts/push-deploy.sh` additionally pushes Git and runs Prisma migrations. It is broader than the UI deployment itself. This PR adds no migration; establish the existing database migration state before choosing that wrapper. Do not infer migration success from a frontend build.

After deployment, verify real catalog search/category/trending data, canonical `/studio` and `/skill-studio` redirect, `/methodology`, desktop download links from the live manifest, native video range loading/captions/chapter seeking, mobile navigation, and the queue-health checks. Keep browser checks explicitly headless. The local preview had no production database/KV, so a passing local search-dialog interaction is not a production catalog query result.

## CI status at repair handoff

Original E2E run `34813054940` failed before tests: setup-node referenced `repositories/anton-abyzov/vskill-platform/package-lock.json` inside a standalone checkout. All subsequent working directories had the same invalid prefix. This defect is present before the redesign.

Commit `55bcd49` repairs those paths, uses Node 22, supplies canonical build data, removes an inappropriate global `NODE_ENV=test` during Next production build/start, and configures Playwright `headless: true`, HTML `open: 'never'`, `PWDEBUG=0`, and `PLAYWRIGHT_HTML_OPEN=never`. Localhost `E2E_BYPASS=1` remains enabled for the existing private-repo test harness; its production-host guard is unchanged.

No 0826 test is removed, weakened, or newly skipped. Discovery lists 46 tests across eight files. That suite already contains conditional skips (including unshipped mock routes); a future green result must report actual executed/skipped counts. The separate product flow still passes: two production-build headless tests. New remote run `34813542931` was pending at handoff; inspect the latest exact PR head before merge.

## CI follow-up at `85096d0`

A subsequent run exposed two more existing fixture prerequisites after the checkout-path failure was removed. `d0459ec` pins `@axe-core/playwright`4.13.0 and its transitive axe-core in the lockfile, replacing dynamic installation. Comparing lockfile versions confirmed zero version changes to existing packages; the resolved Wrangler4.65.0/OpenNext1.16.5 toolchain is retained.

The next run reached Prisma and failed because the historical migrations begin after the original database schema: migration `20260220170000_add_dequeued_state_and_priority` alters an absent `SubmissionState` type. With root approval, `85096d0` bootstraps the disposable E2E database from the current Prisma schema using `db push --skip-generate`. An explicit URL guard permits only localhost/127.0.0.1 and database `/vskill_test`; other targets fail before schema setup. No production database operation or production migration change is performed. This validates application behavior against the current schema, **not historical migration replay**; repairing that historical baseline is separate work.

Run `34814135060` passed dependency install, canonical companion source, browser setup, guarded schema setup, Next production build, and server startup, and reached the existing46-test private-repo suite. Its final result must still be checked.

## Authenticated CI fixture diagnosis and review

Root independently reviewed the product T18 commit `e2fe683` and prior workflow commits `55bcd49`, `d0459ec`, `85096d0`, finding no confirmed regression. The fresh T18 OpenNext Worker build and `verify-queue-health-build.mjs` pass. Deployment remains gated on the new full unit CI result and final release checks.

Run `34814135060` was cancelled by the T18 push after the existing suite had logged 19 distinct passing tests, 19 distinct failing tests and one existing skip, out of 46 declared tests. These are partial results, not a passing suite. Logs and traces survived cancellation. The trace records harness health/reset/seed 200, sign-in 500, and org pages displaying the auth gate's 404. The workflow had no `JWT_SECRET`; unchanged `getJwtSecret()` requires at least32 characters. The existing test helper swallows sign-in failure, causing subsequent private/audit assertions to time out.

A local production-build probe reproduced the prerequisite exactly: without an E2E signing key, localhost sign-in returns500/no session cookie; with a fresh random key, it returns200/a session cookie. T22 supplies a32-byte random signing key, masks it before export to subsequent job steps, and checks localhost sign-in returns200 plus a session cookie before launching the suite. It also specifies the disposable database name in `pg_isready`, removing unrelated missing-default-database noise. Production auth code and all tests remain unchanged.

The CI-only commit uses the previously documented pre-commit false-positive path because the unchanged disposable PostgreSQL URI is still flagged. Complete workflow diff was inspected; no production credentials are added.

## Authenticated suite result

Run `34815773792` at `e6b45b0` completed in2.7 minutes after authenticated readiness passed: **32 passed,8 failed,3 flaky,3 skipped**. It finished before the next CSS push; this result is not cancelled or green.

The remaining failures are newly observable in unchanged private-workspace components and test paths: three accessibility assertions report `button-name` on `src/components/UserMenu.tsx`'s authenticated avatar button; private publishing lacks the expected success message; the mock public catalog seed is not displayed; three isolation assertions expect404 but receive200. Trace bodies for those three isolation responses contain the rendered404 page, no private description, and no private banner. This is consistent with a streamed Next not-found response, not evidence of private content exposure. The org/auth/catalog/publish code and0826 tests are unchanged relative to pre-redesign `54535ca`; a complete pre-change E2E runtime replay has not been performed, so this is source-based attribution, not a claimed fully proven baseline run.

No test was weakened or removed to conceal those results. The release lane preserves the8-failure result and traces while requiring green full unit CI and direct production checks for the reviewed product changes.

## Final reviewed candidate `1673da8`

Root independently approved the seven-line scoped catalog contrast patch `495f0fa` and account-menu accessible-name patch `1673da8` with its failing-first interaction regressions. The final Worker build, queue-health build contract, and two production-build product E2E tests pass. Source worktree is clean after restoring the build-derived version metadata.

Final private-workspace CI `34816692739` executes all46 declared cases: **35 passed,5 failed,3 flaky,3 skipped**, in2.2minutes. All three authenticated accessibility audits now pass. The five remaining failures are private-publish success feedback, the mock public catalog seed, and the three streamed-notFound transport-status assertions described above. No test was removed or weakened, and existing conditional skips remain visible. Full unit CI `34816692738` is the remaining merge gate for this candidate.

Pre-deployment live checks: the catalog stats endpoint returns200 with16 categories and10 trending entries; TypeScript search returns200 with real results. Public queue health returns schema2 with updatedAt-based freshness inside the six-hour window. The existing internal verification key is present, checked without printing its value. Deployment uses existing Wrangler OAuth, unchanged bindings, and `--keep-vars` to preserve remote variables.
