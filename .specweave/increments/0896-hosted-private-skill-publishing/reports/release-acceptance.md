# 0896 release acceptance

Status: implementation, source review, local sandbox and builds pass. Replacement dedicated CI is in progress. Production launch is not yet claimed.

Platform draft: https://github.com/anton-abyzov/vskill-platform/pull/123. CLI/Studio draft: https://github.com/anton-abyzov/vskill/pull/174. Both hosted launch gates remain closed.

## Behavior for acceptance

Studio offers Private publishing with an authenticated publishing-account selector. Missing accounts offer Connect GitHub App and keep submission disabled. Private status stays inside Studio. The CLI adds explicit private submission and tenant-scoped frozen-version installation/update. Existing local GitHub private installation remains available without a paid hosted plan.

[Selected publishing account](studio-headless/private-account-desktop.png) · [Missing account on mobile](studio-headless/missing-account-mobile.png) · [Private publication status](studio-headless/published-private-desktop.png)

## Verified behavior

- Tenant-scoped submission, scoped GitHub reads, immutable bundle verification and authenticated downloads are implemented.
- Public APIs, stats, search, scanners, maintenance and problem reports exclude private records. Fresh source review has cleared all confirmed findings.
- Repository removal, archive, deletion, rename and all-to-selected access changes cancel pending publication and deny stored downloads. Publicizing the source keeps historical private versions private.
- Installer updates preserve per-agent manifests and prevent symlink writes or cleanup outside the install directory. Focused filesystem and live-loopback HTTP tests pass.
- Full platform CI at production-source commit a17599a6 passed: 7,604 tests, 14 existing skips; line/statement coverage66.17%, above the configured60% threshold (run38354175469). Full CLI CI at1a20957 passed: 7,014 tests, 11 existing skips (run38355622953). All CLI cross-platform install/runtime and Windows Rust checks passed.
- The final local Worker build passed:297 Next app entries, OpenNext queue bundle and runtime contract checks. The final combined PostgreSQL/headless sandbox passed36/36 at8ef2818f with92.58% private-source line/statement coverage, above80%. Concurrent intake passed20 repeated runs after correcting a mocked Cloudflare context race. The47-case database-backed onboarding browser suite passed in CI38356550483. Replacement dedicated CI38357888207 remains pending.

## Production operations

1. Use reviewed platform and CLI commits after integrated tests, coverage, builds, and fresh-context review pass.
2. Add the missing VSKILL_TOKEN_KEK as a cryptographically random32-byte Base64 Worker secret through the existing secret store. Never expose it in logs or commit it. Existing encrypted-token count is0; retain the existing test tenant unchanged.
3. Apply only migration20261013050000_private_publishing: create PrivateSubmission and PrivateSkillArtifact with tenant/version foreign keys, lookup and uniqueness indexes, and a PRIVATE-only submission constraint. Existing public tables and records are retained.
4. Deploy and verify health, closed-gate rejection, and public behavior. Verify GitHub App webhook configuration: the live app currently has Contents/Metadata read and only the push event. Subscribe to repository events so archive/delete/rename/privacy changes reach the lifecycle guard. Installation and installation_repositories events are automatic. Organization onboarding additionally requires Members read; personal installation ownership uses the immutable user ID. Connect the verified-skill-studio GitHub App to only the selected private skills repository through GitHub's owner-authorized install flow, then verify tenant membership and active Pro entitlement. Confirm any new private-repository or organization permission at the actual grant step.
5. Open platform and client gates only after acceptance criteria pass. The same platform gate also enables the existing paid checkout and pricing buttons; it does not charge the existing account. Publish dcfc-inquiry-replies privately; verify its authenticated status/download and a local isolated install/readback. Anonymous and foreign-tenant requests must not expose metadata/content, and public search must not list it.
6. Publish/install CLI1.2.8 and native Skill Studio1.0.65 through their separate existing release workflows. Metadata is prepared at4359ec3, versions unpublished. Record exact versions/commits and real runtime results. The currently installed native1.0.64 sidecar has already authenticated as the correct Pro account with200 responses under a read-only personal-files sandbox; the account currently has no tenant membership.

## Rollback

Disable the hosted private publishing gate and redeploy. Keep additive schema and frozen versions intact; do not delete published private data or the encryption key. Existing private downloads remain tenant-authorized. No subscription purchase or tier change is planned: the real account is already PRO/ACTIVE.

## Required manual acceptance

Project AGENTS.md says: “Ask user for manual acceptance: new UI, auth, payments, data migrations.” This change adds UI/auth behavior and an additive migration. Ask after the complete reviewed result is available, before closing the increment.
