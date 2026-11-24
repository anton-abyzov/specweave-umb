# 0922 release readback and remaining gates

Recorded 2026-10-15 by Claude Code.

## Shipped
- PR #183 merge dc0116de724e0a15bea727076ba0a44112ae8473 is an ancestor of the 1.0.19 source F = 1ca53135463163a59b588b2f51880645afd67941. 1.0.19 was published 2026-10-14T23:58Z (11 assets, digests and anonymous downloads verified) and is installed on all three machines: M4 app and service, M1 and M3 services report installedVersion 1.0.19. This covers the installed-rollout half of T-03.
- Tests on F: server 8987/0 failed, desktop 1767/0, web 8106/0, client-runtime 2145/0, contracts 788/0.

## Typechecks on F (T-03 other half): not clean
Run 2026-10-15 in `~/Projects/github/cw-rel119` at F (logs `~/Projects/github/.cw-runs/close/typecheck-F.log`, `tc-desktop.log`, `tc-server.log`):
- 13 of 15 workspace typechecks pass, including apps/web, client-runtime, contracts and shared.
- apps/desktop: 0 errors, but exit 1 on one Effect warning (TS377033 multipleEffectProvide, `src/backend/DesktopLocalService.test.ts:377`).
- apps/server: 78 Effect-policy errors (TS3770xx/TS3771xx, for example TS377030 "any in the requirements channel" in `src/server.ts`, `src/ws.layer-types.ts`) and 0 standard TypeScript errors. The first workspace run was killed with exit 137 (memory). The standalone rerun completed.
T-03 says "supported server and web typechecks". The web typecheck passes. The server typecheck does not, so T-03 stays open.

## Muse account acceptance
Anton approved "Ship Muse preview; validate my account later". The spec's manual acceptance gate says not to close until installation/sign-in, Wonder Full discovery, an authorised turn, approval, cancellation and reconnect are accepted on an eligible native account. Tracked as T-04.
