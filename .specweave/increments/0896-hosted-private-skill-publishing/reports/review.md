# Review: 0896 Hosted private skill publishing

Source verdict: all confirmed findings remediated; release verdict: hold for full validation and manual acceptance. Seven high and one medium findings are retained below with their original evidence and current verification state. No outstanding material source finding at the latest review.

Reviewer context: fresh delegated session; no implementation authored by this reviewer. Initial reviewed revisions: platform `f9e6bb55` against `2e0c6247`; vskill `f7e6b9c` against `13387a6`. The in-progress private scanner file-boundary correction was also read. Final platform source reviewed: `a17599a61fdf34440ea4151a992c3d5ab02d146a` (the last commit only documents private revocation search isolation). Final CLI source reviewed: `4f9d12961035db65ca267c0f832be997d7ff5bba`, including containment and per-agent inventory corrections. This report is local release evidence, not authorization to publish or deploy.

## [high] Public aggregate and maintenance paths can expose private metadata

`vskill-platform/src/lib/stats-compute.ts:513` and the fallback at `:311` select every nondeprecated skill, including the new private rows, into `trendingSkills` with name, display name, author and repository URL. Count/category/repository SQL is unscoped too. `src/lib/cron/stats-refresh.ts:174` persists the complete result to `platform:stats`; anonymous `src/app/api/v1/stats/route.ts:8` returns it with public caching. A private row inside the top-50 cohort is returned publicly; private rows always contaminate aggregate counts.

The same boundary is missing in `src/app/api/v1/admin/rebuild-search/route.ts:52`, which writes private metadata directly into public search shards, and `admin/refresh-skills/route.ts:67`, `admin/enrich/route.ts:30` and `admin/repo-backfill/route.ts:39`. Normal maintenance can therefore bypass the correctly scoped primary search/cron paths. The public eval consumer at `src/lib/queue/eval-consumer.ts:82` and its admin enqueue/direct paths also resolve private rows into the public evaluation pipeline; `admin/scan-external/route.ts:43` bypasses the guarded external dispatcher. Fix all shared public consumers before enabling private persistence in production, including raw SQL and fallback paths.

Status: first remediation verified at platform `3e0ae0fd`: public aggregate full/minimal/raw-SQL paths, source-maintenance boundaries, search rebuild, evaluation and external dispatch checks pass 82 focused tests across 10 files. Additional read-through found remaining maintenance gaps, sent to the backend owner:

- `admin/backfill-slugs/route.ts:48` selects every hosted private row because its ownerSlug is null and name is flat. `:174` replaces the tenant-hashed identity with the public owner/repo/path identity, or `:159` deprecates it on collision. `lib/slug-migration.ts:71` does the same via admin/recompute-slugs, including deletion of same-repository collisions at `:288`.
- `admin/npm-backfill/route.ts:67` selects private repository URLs into anonymous raw.githubusercontent.com fetches at `:133`. `admin/trust-backfill/route.ts:53` and `admin/trusted-author-backfill/route.ts:42` overwrite private certification using public Submission/ScanResult evidence (`lib/trust/trust-updater.ts:208`).
- `legacy-redirect/[slug]/route.ts:28` lacks a public predicate; after slug backfill populates private legacySlug/ownerSlug it reveals the private owner/repository/path through an anonymous 301 Location.

These are the same shared-table boundary failure, requiring predicates on both reads and writes, including raw SQL. Followup `f58aad00` closes these named paths; reviewer inspected the diff and reran all 60 focused tests across five files successfully.

## [high] Public source maintenance can disable private downloads

`vskill-platform/src/app/api/v1/skills/check-source/route.ts:107` resolves a skill by name without a tenant/privacy predicate. A non-member with a previous copy of the private metadata can send its actual GitHub blob URL to this unauthenticated GET. After the 24-hour freshness guard expires, the anonymous source probe returns 404 for a private repository and `:144` marks the private row deprecated. The authenticated download at `src/app/api/v1/tenants/[tenantId]/skills/[slug]/download/route.ts:17` then returns 404 for legitimate members. Private republishing does not clear `isDeprecated` (`src/lib/private-publishing/service.ts:197`).

`src/lib/orphan-cleanup.ts:41` has the same unscoped public mutation: a public rediscovery of a repository with a privately published skill treats its hashed private slug as an orphan and deprecates it. Scope both the reads and mutation predicates to public, non-tenant records. Apply the same fail-closed boundary to anonymous registration and taint checks.

Status: resolved and independently reverified in `3e0ae0fd`; query and mutation predicates are public-only. Relevant focused tests pass. Backend also makes a deprecated private row require fresh authorization and scanning before restoring it.

## [high] Transformed-agent installs discard the tenant namespace

At vskill `f7e6b9c`, `src/commands/install-private.ts:37` passes the private install name and original frontmatter to `installSkillToAgents`. `src/installer/multi-install.ts:298` reparses the frontmatter; `:216` chooses its original `name`, so a Tier-2 transformer ignores the tenant namespace. Two tenants with `name: shared-skill` both write `.windsurf/rules/shared-skill.md`; the second overwrites the first. The transformer path also drops arbitrary supporting files and executable modes, so it cannot claim to install the frozen bundle completely.

Reproduced with the actual installer and Windsurf registry entry in an isolated temporary directory. Distinct names `private-team-a-111111111111` and `private-team-b-222222222222` produced the same output path, whose content was the second tenant's text. No user installation or credentials were touched.

Status: resolved and independently reverified at vskill `798eae5`: native-folder-only support rejects transformer-only targets before writes; forced namespace renaming follows raw artifact verification. Actual HTTP/tempfile regressions cover both tenant collision and unsupported targets. Part of 90/90 focused CLI/UI tests passed by reviewer.

## [medium] Updating one copied agent prevents later agents from catching up

At vskill `f7e6b9c`, `src/commands/install-private.ts:97` returns immediately when the shared lock version/tree matches the downloaded artifact, before inspecting selected agents. Install with `--copy` for Codex and Claude, update only Codex, then update only Claude: the first update advances the shared lock while Claude retains old content, and the second silently skips Claude forever. Reapply the verified artifact to selected installed agents even when the shared lock is unchanged, or keep per-agent revision state.

Status: content catchup fixed at `798eae5`, but a residual is confirmed. The shared `entry.files` advances at `install-private.ts:118`; a later Claude-copy update receives only the V2 manifest as previousFiles (`:113`). A V1 executable removed from V2 therefore survives in Claude. Actual installer/update reproduction with only the download boundary stubbed produced `newVersion:1.1.0`, `manifest:[SKILL.md]`, `canonicalRemoved:true`, `claudeStale:true`. Reproduction bundle: `/private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/0896-review-copy-cleanup-6VokFs/proof.mjs`. Resolved in `4f9d129`: per-agent inventories survive repeated filtered updates. Reviewer reran the real HTTP/tempfile regression through Codex V2/V3 and delayed Claude catchup; removed executables disappear and untracked user notes remain. Included in 28/28 independent final containment/install tests.

## [high] Repository lifecycle does not revoke frozen artifacts safely

At platform `3e0ae0fd`, `src/lib/webhook-handlers/installation-repositories.ts:105` matches only sourceRepoUrl and writes deletedAt, which is not a Skill column. The removal handler catches that database error and returns success. `webhook-handlers/repository.ts:137` repeats the invalid field for archived/deleted repositories. Original private publication populated repoUrl but not sourceRepoUrl, so even a valid mutation would miss those records. Authenticated download checks isDeprecated and therefore continues serving the snapshot after access is removed.

`repository.ts:164` also publicizes every matching tenant Skill, clearing tenantId and setting PUBLIC when a repository becomes public. Once private sourceRepoUrl is populated, this converts private-intent historic versions into public records. Hosted provenance must explicitly exclude these from visibility conversion.

Revocation also races a long model scan: `private-publishing/service.ts:181` serializes final publication only with Tenant, and `:204` restores isDeprecated false. If the webhook does not take that lock and invalidate matching PrivateSubmission processingToken, an in-flight job can republish immediately after revocation. The required regression holds a scan, revokes the repo, releases the scan and verifies no downloadable artifact is created/restored.

Status: resolved in `fce26b54` (including `b7ad6116`, `7c31e776`, `6552373d`). Revocation takes the Tenant lock, rejects matching jobs and clears leases before deprecating skills. Publicization excludes both private submissions and private artifacts. Rename cancels old/new source jobs and requires explicit resubmission. Empty all-to-selected removal conservatively revokes tenant private jobs/artifacts. Failures return 503 and release only the matching webhook dedup claim, allowing authenticated redelivery.

The correction uses GitHub's real `changes.repository.name.from` rename shape and handles the documented empty repositories_removed selection-reset case. Primary references: [Octokit webhook schema](https://github.com/octokit/webhooks/blob/main/payload-types/schema.d.ts), [GitHub webhook payloads](https://docs.github.com/en/webhooks/webhook-events-and-payloads?actionType=renamed#repository). Final actual-PostgreSQL race/regression run belongs to the integration release gate below.

## [high] Anonymous install tracking reveals private identities

`vskill-platform/src/app/api/v1/skills/installs/route.ts:76` calls the unscoped tracker without authentication and returns its results. `src/lib/install-tracker.ts:140` matches a guessed skillName and repoUrl against a private skillPath; `:203` returns the complete internal private:tenant:hash name, exposing the tenant identity and existence. The same path increments the private counter at `:170`. Exact-name, top-level-path and command fallbacks at `:128`, `:151` and `:162` are unscoped too. All lookups and mutation predicates must exclude private/tenant rows.

Status: tracker resolved at `f58aad00`; all four lookup paths and write predicates scoped to public, independently verified in the 60-test run. Related metadata read-through was confirmed in `problem-reports/route.ts:74` plus `problem-reports/mine/route.ts:29`: a nonmember attaches a report to a known private internal name, then reads its displayName from the included Skill relation. Resolved in `fce26b54`: new attachments require PUBLIC/null tenant, and historic/inconsistent relations serialize no private identity/displayName; responses use private,no-store. Reviewer read the final production path and regression changes.

## [high] Private update cleanup can delete files outside the skill directory

The new private updater supplies recorded file paths to the existing canonical installer. `vskill/src/installer/canonical.ts:259-274` validates paths lexically, then lstat/unlinks them without checking parent symlinks. If the installed skill's scripts directory is a symlink to another directory, removing scripts/old.sh from the next bundle deletes that outside directory's old.sh. This is an inherited installer defect now reached by the new private update path.

Confirmed with the real installer in a temporary root only: `skill/scripts -> outside`, `outside/old.sh` existed before update, and `outsideFileStillExists:false` afterward. Root: `/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/0896-review-symlink-fWRmfo`. SKILL.md direct writes and symlinked skill roots need the same containment review before claiming filesystem safety.

Status: resolved in `4f9d129`. Shared parent links are rejected; skill root and entry links are detached safely; stale cleanup walks ancestors without traversing links. Original destructive proof now returns outsideFilePreserved:true and insideSymlinkRemoved:true. Reviewer passed 28/28 final install/containment tests, including symlink, hardlink and normal Claude-link behavior. The committed artifact matches the reviewed correction.

## [high] Public visibility probe uses tenant credentials without membership

At platform `f58aad00`, `src/app/api/v1/submissions/route.ts:198` accepts an authenticated user's arbitrary tenantId with privacy public; `:217` loads that tenant's installation token without calling withTenant. `:227` sends a repository visibility request with it. A guessed private repository produces a distinct 422 PRIVACY_MISMATCH, so a nonmember can exercise the victim's scoped credential and learn private repository existence. The private launch gate does not guard this public-intent branch. Authorize the tenant before resolving credentials; a membership denial must not be swallowed by the surrounding best-effort probe catch.

Status: resolved in `de4bebc1`, included in final platform head. Membership authorization is outside the soft probe catch and precedes credential resolution. Reviewer independently reran 51/51 focused privacy/version-maintenance tests; foreign/missing tenants cause no credential, probe or persistence call.

## Verified portions and evidence boundaries

The GitHub ownership check uses immutable personal account IDs; organization onboarding requires active admin membership whose user and organization IDs match the authenticated principal and installation account. Callback state is bound to the authenticated account before OWNER membership. No arbitrary-installation-ID authorization bypass was found.

Private intake/status/download keep tenant membership and vskill bearer scopes; frozen blobs are commit-pinned and hash-checked; private jobs contain only an opaque submission ID. CLI artifact verification checks tenant/skill/version identity, individual bytes, manifest coverage, path collisions and tree integrity before writes. The private updater branches before public lookup. Model/provider output is suppressed in sensitive scan logs.

Reviewer reran 78 focused platform tests across installation ownership/provisioning/callbacks, private GitHub fetching, sensitive AI routing and Tier-2 scanning: all passed. Reviewer additionally reran 90 CLI/UI tests, 82 first-round public-boundary platform tests, 60 followup maintenance tests, 51 credential/version-boundary tests and 28 final CLI containment/install tests successfully; counterexamples outside those tests are documented above. The CLI owner reports 350/350 installer/update regressions, successful Node 22 build and package preflight with 833 entries for the final CLI commit; reviewer inspected the saved test/build/preflight logs. Existing reports show actual local PostgreSQL plus headless HTTP transport tests, with synthetic GitHub/model dependencies; those are source/integration evidence, not live provider or production proof.

Installed and registry SpecWeave both reported `3.0.14`. Active owners and worktrees were preserved; no pickup or claims were issued. No production database, account, payment or deployment mutations were performed. Hosted gates remain closed. Final build/coverage and manual release acceptance are separate gates. The full instrumented platform suite is still being investigated for timing/auth/regex failures; targeted greens are not a full-suite pass. The final integrated PostgreSQL/headless HTTP run and worker build are also pending at this report update. Screenshots from the actual headless Studio fixture were visually inspected for selected-account desktop and missing-account mobile; they are readable and the missing-account action is disabled. No real GitHub/model/private hosted production path has been demonstrated by the synthetic sandboxes.

Nits: none.
