# 0896 release acceptance

Status: implementation and source review complete; full runtime validation remains in progress. Production launch is not yet claimed.

Platform draft: https://github.com/anton-abyzov/vskill-platform/pull/123. CLI/Studio draft: https://github.com/anton-abyzov/vskill/pull/174. Both hosted launch gates remain closed.

## Behavior for acceptance

Studio offers Private publishing with an authenticated publishing-account selector. Missing accounts offer Connect GitHub App and keep submission disabled. Private status stays inside Studio. The CLI adds explicit private submission and tenant-scoped frozen-version installation/update. Existing local GitHub private installation remains available without a paid hosted plan.

[Selected publishing account](studio-headless/private-account-desktop.png) · [Missing account on mobile](studio-headless/missing-account-mobile.png) · [Private publication status](studio-headless/published-private-desktop.png)

## Verified behavior

- Tenant-scoped submission, scoped GitHub reads, immutable bundle verification and authenticated downloads are implemented.
- Public APIs, stats, search, scanners, maintenance and problem reports exclude private records. Fresh source review has cleared all confirmed findings.
- Repository removal, archive, deletion, rename and all-to-selected access changes cancel pending publication and deny stored downloads. Publicizing the source keeps historical private versions private.
- Installer updates preserve per-agent manifests and prevent symlink writes or cleanup outside the install directory. Focused filesystem and live-loopback HTTP tests pass.
- The initial full coverage attempts exposed timing failures in older tests; the serial rerun retains the original thresholds. The final PostgreSQL/headless sandbox and Worker build remain required.

## Production operations

1. Use reviewed platform and CLI commits after integrated tests, coverage, builds, and fresh-context review pass.
2. Add the missing VSKILL_TOKEN_KEK as a cryptographically random32-byte Base64 Worker secret through the existing secret store. Never expose it in logs or commit it. Existing encrypted-token count is0; retain the existing test tenant unchanged.
3. Apply only migration20261013050000_private_publishing: create PrivateSubmission and PrivateSkillArtifact with tenant/version foreign keys, lookup and uniqueness indexes, and a PRIVATE-only submission constraint. Existing public tables and records are retained.
4. Deploy and verify health, closed-gate rejection, and public behavior. Connect the verified-skill-studio GitHub App to the selected private skills repository through GitHub's owner-authorized install flow, then verify the tenant membership and active Pro entitlement.
5. Open platform and client gates only after acceptance criteria pass. The same platform gate also enables the existing paid checkout and pricing buttons; it does not charge the existing account. Publish dcfc-inquiry-replies privately; verify its authenticated status/download and a local isolated install/readback. Anonymous and foreign-tenant requests must not expose metadata/content, and public search must not list it.
6. Publish/install the tested CLI release through the existing release workflow. Record exact versions/commits and real runtime results.

## Rollback

Disable the hosted private publishing gate and redeploy. Keep additive schema and frozen versions intact; do not delete published private data or the encryption key. Existing private downloads remain tenant-authorized. No subscription purchase or tier change is planned: the real account is already PRO/ACTIVE.

## Required manual acceptance

Project AGENTS.md says: “Ask user for manual acceptance: new UI, auth, payments, data migrations.” This change adds UI/auth behavior and an additive migration. Ask after the complete reviewed result is available, before closing the increment.
