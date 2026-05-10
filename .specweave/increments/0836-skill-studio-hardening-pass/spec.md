---
increment: 0836-skill-studio-hardening-pass
title: "Skill Studio Hardening Pass — 6 P0 Security Findings"
type: feature
priority: P0
status: planned
created: 2026-05-10
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio Hardening Pass — 6 P0 Security Findings

## Overview

This increment closes 6 P0 security findings against the shipping vskill macOS desktop app (v1.0.17). The findings were surfaced by a brainstorm trio (advocate / critic / pragmatist) on 2026-05-09 and independently verified in the codebase. All six are surgical, server-side / Rust-side / build-pipeline changes — no user-facing UI work, no new features, no new dependencies, and zero changes to `src-tauri/Entitlements.plist` (preserves 0828 Apple notarization).

The six findings, each one US below:

1. **P0-1** — eval-server binds dual-stack (LAN-reachable) instead of loopback-only.
2. **P0-2** — Permissive `localhost` CORS regex allows any local browser tab to abuse the bearer-injecting proxy (DNS-rebinding-friendly).
3. **P0-3** — `account_get_token` IPC ships the raw `gho_*` token to the WebView JS heap, where any XSS or compromised npm dep can exfiltrate it.
4. **P0-4** — Release binaries can ship with the placeholder OAuth `client_id` (already happened once in 0831 DoD note); device-flow sign-in silently broken in production.
5. **P0-5** — Sign-out clears the local keychain but never revokes the token on github.com; compliance reviewers cannot prove session termination.
6. **P0-6** — Rust desktop and Node CLI use different macOS Keychain service names (`com.verifiedskill.desktop` vs `vskill-github`), so the same physical token lives in two slots that cannot stay in sync.

This is **pure hardening**. Mounting `ConnectedRepoWidget`, `SkillCountBadge`, building `WorkspaceTree`, adding `lucide-react`, and any new `/account` UI all defer to **0837**. GitHub App / GHES / SSO / MDM defer to a Phase 3 increment. Stripe / Team tier defer to Phase 2.

**Non-functional contract**:
- ZERO changes to `src-tauri/Entitlements.plist` (preserves 0828 Apple notarization).
- ZERO new Tauri capabilities or plugin allowlist changes.
- ZERO new npm dependencies. Only Rust dev-deps are reused (`mockito`, already in `Cargo.toml`).
- The 0828 Phase 1 baseline must continue to pass: signed `.dmg` notarizes, Studio loads in WebView, sidecar lifecycle works.

## Personas

- **Skill Studio (the app itself)** — runs as a Tauri desktop process plus a sidecar Node eval-server on `127.0.0.1:<dynamic-port>`. Today its proxy injects a GitHub bearer token; that proxy is the asset every finding circles around.
- **vskill end user** — a developer signed in with GitHub OAuth device-flow; expects the token to stay on their device and to be actually revoked when they sign out.
- **Release pipeline / CI** — must guarantee a release binary never ships with the placeholder `client_id`.
- **Compliance reviewer (future enterprise/Team-tier customer)** — wants documentary evidence that "sign out" terminates the github.com session, not just clears local cache.
- **Threat actor model**:
  - LAN attacker on the same Wi-Fi (closed by US-001).
  - Malicious local browser tab (closed by US-002, defends against DNS rebinding).
  - WebView XSS or compromised npm dep inside the app (closed by US-003).

## Scope

In scope:
- `src/eval-server/eval-server.ts` — bind to `127.0.0.1` explicitly.
- `src/eval-server/router.ts` — replace `LOCALHOST_ORIGIN_RE` allowlist with `X-Studio-Token` header gate (constant-time compare).
- `src/eval-server/keychain.ts` — switch service name from `vskill-github` to `com.verifiedskill.desktop`; one-time migration on boot.
- `src-tauri/src/account/commands.rs` — delete `account_get_token`; add `account_get_user_summary`.
- `src-tauri/src/auth/sign_out.rs` (new) — github.com OAuth-grant revocation before keychain clear; best-effort with 5s timeout.
- `src-tauri/build.rs` — release-build assertion on `GITHUB_OAUTH_CLIENT_ID`.
- CI release pipeline — `strings | grep` step on the release binary to assert the placeholder is absent.
- New Tauri IPC `get_studio_token` (returns the per-launch shared secret to the WebView only).
- Documentation: `src-tauri/README.md` build-arg note + a runbook in `.specweave/docs/internal/specs/` for rotating the OAuth `client_id`.

Out of scope (deferred — see Out of Scope section).

## User Stories

### US-001: Loopback-only eval-server bind (P0)
**Project**: vskill

**As** Skill Studio
**I want** my local HTTP eval-server to bind to `127.0.0.1` only (not the dual-stack default that includes LAN-reachable interfaces)
**So that** the LAN cannot reach my GitHub-token-injecting proxy.

**Context**: `src/eval-server/eval-server.ts` currently calls `server.listen(port)` with no host arg. Node's default binds dual-stack, including LAN-reachable interfaces — anyone on the same Wi-Fi can hit the proxy and have their requests authenticated as the user.

**Acceptance Criteria**:
- [x] **AC-US1-01**: The `server.listen(...)` call in `src/eval-server/eval-server.ts` includes an explicit `"127.0.0.1"` host argument (e.g., `server.listen(port, "127.0.0.1", ...)`).
- [x] **AC-US1-02**: After app launch, `lsof -i -P | grep <eval-server-port>` shows ONLY `127.0.0.1` for the eval-server process; never `*.*` and never `0.0.0.0`.
- [x] **AC-US1-03**: The existing "Studio loads in WebView" smoke test still passes — loopback access continues to work.
- [x] **AC-US1-04**: A request from a non-loopback interface (test rig binds to the host's `en0` IP and curls the eval-server port) returns `ECONNREFUSED` (no TCP handshake).
- [x] **AC-US1-05**: If the requested port is already in use, the existing dynamic-port allocator retries the next port; the bind-host argument is preserved across retries.

---

### US-002: X-Studio-Token gate replaces permissive localhost CORS (P0)
**Project**: vskill

**As** Skill Studio
**I want** every API call to my eval-server to require a per-launch shared-secret token
**So that** a malicious local browser tab (or a DNS-rebinding attack) cannot abuse the bearer-injecting proxy via the open `localhost` Origin allowlist.

**Context**: `src/eval-server/router.ts` currently allows ANY localhost port via the `LOCALHOST_ORIGIN_RE` Origin regex. That is defeated by DNS rebinding (a remote site can rebind a hostname to `127.0.0.1` and still satisfy the regex). The fix is a per-launch shared secret that the WebView reads via Tauri IPC and sends as `X-Studio-Token` — the regex goes away.

**Acceptance Criteria**:
- [x] **AC-US2-01**: At eval-server boot, a 256-bit random token is generated using `crypto.randomBytes(32).toString('base64url')` and held in eval-server process memory only (never persisted to disk, never written to keychain).
- [x] **AC-US2-02**: A new Tauri IPC command `get_studio_token` is exposed via `tauri::generate_handler!` and returns the current token to the WebView. It is reachable only via Tauri's IPC ACL (NOT exposed as a public HTTP endpoint on the eval-server).
- [x] **AC-US2-03**: Every HTTP request to the eval-server requires header `X-Studio-Token: <token>`. Missing or wrong header returns `401` with an empty body; the response logs at WARN with **no** token value in the log line.
- [x] **AC-US2-04**: The previous `LOCALHOST_ORIGIN_RE` allowlist is REMOVED from `router.ts`. CORS now reflects the request's `Origin` header back ONLY when the `X-Studio-Token` matches; otherwise no `Access-Control-Allow-Origin` is set.
- [x] **AC-US2-05**: A request from `Origin: http://localhost:9999` WITHOUT `X-Studio-Token` returns `401`; the same request WITH the correct `X-Studio-Token` returns `200` (or the proxied upstream response).
- [x] **AC-US2-06**: Token comparison uses `crypto.timingSafeEqual` (over equal-length buffers) to prevent timing oracles. Length-mismatch is rejected before the compare without leaking length.
- [x] **AC-US2-07**: The CLI entry point (`npx vskill studio`) prints `Studio token: <token>` to stdout on startup so power users can `curl` the eval-server. In the desktop sidecar build the eval-server still emits the same banner (the Tauri `sidecar.rs` stdout parser uses it to capture the token), but `sidecar.rs` consumes the matching line via its `parse_studio_token` step and never forwards it to user-visible Tauri logs — the WebView reads the token via `get_studio_token` IPC and the user never sees the value. Compliance with this AC is enforced by `webview-no-token-leak.spec.ts` and `parse_studio_token` unit tests.
- [x] **AC-US2-08**: The studio-token is rotated on every eval-server process start; a token from a previous launch returns `401`.

---

### US-003: Remove `account_get_token` IPC from WebView surface (P0)
**Project**: vskill

**As** Skill Studio
**I want** the raw GitHub `gho_*` token to never reach the WebView's JS heap
**So that** a WebView XSS or a compromised npm dep cannot exfiltrate it.

**Context**: `src-tauri/src/account/commands.rs` currently exposes `account_get_token` IPC, which returns the raw token to the WebView as a `String`. Any reachable XSS or supply-chain compromise inside the WebView can read that string, screenshot it, or POST it to an attacker. The WebView never legitimately needs the token — all GitHub-bound HTTP goes through the eval-server, which already injects the bearer Rust-side from the keychain.

**Acceptance Criteria**:
- [x] **AC-US3-01**: The `account_get_token` IPC command is REMOVED from `src-tauri/src/account/commands.rs` (handler deleted from `tauri::generate_handler!` registration and the function body itself).
- [x] **AC-US3-02**: A new IPC `account_get_user_summary` is added; it returns `{ login: string | null, avatarUrl: string | null, tier: "free" | "pro" | "team", signedIn: boolean }` with no token field.
- [x] **AC-US3-03**: All WebView callers that previously called `account_get_token` are migrated to call `/api/v1/private/*` or `/api/v1/tenants/*` through the eval-server proxy (which injects the bearer Rust-side from the keychain). No WebView code reads or stores the bearer.
- [x] **AC-US3-04**: `git grep -n "account_get_token" -- src/` returns zero matches in WebView code; `git grep -n "account_get_token" -- src-tauri/src/` returns zero matches.
- [x] **AC-US3-05**: A Playwright E2E asserts: open the app signed in, run `page.evaluate(() => document.documentElement.outerHTML.match(/gho_[A-Za-z0-9]+/))` and confirm the result is `null`. Repeat after navigating between Studio tabs.
- [x] **AC-US3-06**: `account_get_user_summary` returns `{ signedIn: false, login: null, avatarUrl: null, tier: "free" }` when called while not signed in (never throws, never returns an error to the WebView).

---

### US-004: Build-time `client_id` assertion (P0)
**Project**: vskill

**As** Skill Studio's release pipeline
**I want** the build to fail loudly if the placeholder OAuth `client_id` (`Iv1.placeholder-replace-before-ship`) ever appears in a release binary
**So that** device-flow sign-in is never silently broken in production again (it shipped that way once, per 0831 DoD).

**Context**: `src-tauri/src/auth/device_flow.rs` defines `DEFAULT_CLIENT_ID = "Iv1.placeholder-replace-before-ship"` as a fallback. Without an environment-driven build, that placeholder lands in the shipped binary and every user's first sign-in attempt fails with an opaque GitHub error.

**Acceptance Criteria**:
- [x] **AC-US4-01**: `src-tauri/build.rs` panics with a clear, actionable error message ("GITHUB_OAUTH_CLIENT_ID is unset or equals the placeholder; set it to a real OAuth App client_id before release") if `GITHUB_OAUTH_CLIENT_ID` is unset OR equals `Iv1.placeholder-replace-before-ship`, gated by `cfg(not(debug_assertions))` so the assertion fires for `cargo build --release` and notarized .dmg builds.
- [x] **AC-US4-02**: Local debug builds (`cfg(debug_assertions)`) tolerate the placeholder so day-to-day local development is unaffected.
- [x] **AC-US4-03**: A CI step `assert-no-placeholder-client-id` runs `strings ./vskill | grep -q 'Iv1.placeholder-replace-before-ship' && exit 1` against the release binary and fails the release pipeline if the placeholder string is found.
- [x] **AC-US4-04**: `src-tauri/README.md` documents the `GITHUB_OAUTH_CLIENT_ID` build-arg requirement (where to set it in CI secrets, what value to use, what happens if it's missing).
- [x] **AC-US4-05**: A runbook for rotating the OAuth `client_id` is added under `.specweave/docs/internal/specs/` (steps to register a new OAuth App, update CI secret, verify, retire the old App).
- [x] **AC-US4-06**: The release CI job's failure on missing `GITHUB_OAUTH_CLIENT_ID` is verified by an intentionally-broken dry-run (CI logs show the panic message and the job fails red).

---

### US-005: Token revocation on sign-out (P0)
**Project**: vskill

**As** a Skill Studio user
**I want** my GitHub access to be actually revoked on github.com when I sign out
**So that** compliance reviewers can prove session termination, not just local-cache clear.

**Context**: Sign-out today only deletes the keychain entry. The OAuth grant on github.com remains live until the user revokes it manually under github.com/settings/applications. For Team-tier compliance posture, that gap is unacceptable.

**Acceptance Criteria**:
- [x] **AC-US5-01**: A new module `src-tauri/src/auth/sign_out.rs` (or extension of the existing auth module) calls the GitHub OAuth-app token-revocation endpoint with the user's access token BEFORE clearing the keychain. The call uses `reqwest`.
- [x] **AC-US5-02**: The endpoint is `DELETE https://api.github.com/applications/{client_id}/grant` (revokes the grant, killing all tokens) using HTTP Basic auth with `client_id:client_secret`. If the registered OAuth App has no client secret available client-side (which is the case for the device-flow OAuth App used here), use `DELETE https://api.github.com/applications/{client_id}/token` instead. The implementation MUST pick whichever endpoint is correct for the existing OAuth App registration and document the choice in a code comment.
- [x] **AC-US5-03**: The revocation call runs in a `tokio::spawn` task with a 5-second timeout. On network failure, timeout, or any 5xx response, the keychain is STILL cleared (best-effort revocation) and the user-visible sign-out succeeds.
- [x] **AC-US5-04**: A revocation `401` response (token already expired) is treated as success and logged at INFO; the keychain is cleared.
- [x] **AC-US5-05**: An integration test using `mockito` (already in `Cargo.toml` dev-deps) asserts that on sign-out, the DELETE call to the revocation endpoint is issued BEFORE `keychain.delete()` runs. Order is enforced via call-sequence assertion.
- [x] **AC-US5-06**: A revocation failure is logged at WARN level. The `gho_*` token value is NEVER written to logs (use `Zeroizing<String>` and a `Debug` impl that redacts; log only the endpoint, status, and elapsed time).
- [x] **AC-US5-07**: The user-visible sign-out latency increases by at most ~500ms in the typical case and is bounded above at 5 seconds (the tokio timeout). A "Signing out..." UI affordance is acceptable but not required for closure.

---

### US-006: Canonical keychain service consolidation (P0)
**Project**: vskill

**As** a vskill user with both the desktop app and the `npx` CLI installed
**I want** a sign-in or sign-out from one process to be reflected in the other on the next invocation
**So that** I do not have to re-authenticate per surface and the two processes do not diverge.

**Context**: Rust uses Keychain service `com.verifiedskill.desktop`; Node uses `vskill-github`. Same physical token, two slots. Sign in via desktop and the CLI doesn't see it; sign in via CLI and the desktop doesn't see it. The fix is a canonical service name with a one-time migration.

**Acceptance Criteria**:
- [x] **AC-US6-01**: `com.verifiedskill.desktop` is adopted as the canonical macOS Keychain service name. Rust code is unchanged.
- [x] **AC-US6-02**: `src/eval-server/keychain.ts` (Node `@napi-rs/keyring`) is updated to read and write `com.verifiedskill.desktop` instead of `vskill-github`. All callers go through the same constant.
- [x] **AC-US6-03**: On first boot post-upgrade, a one-time migration runs in `keychain.ts`: read from old slot `vskill-github`, write to new slot `com.verifiedskill.desktop` (only if new slot is empty), delete old slot. Migration is idempotent (running twice is a no-op).
- [x] **AC-US6-04**: Migration is guarded by a file mutex `~/.vskill/.keychain-migration.lock` with a 5-second TTL to serialize concurrent CLI + desktop startups. A second runner that finds the old slot already empty performs a no-op.
- [x] **AC-US6-05**: After sign-in via desktop, the CLI's `vskill auth status` shows the same `login` on its next invocation (without requiring a re-auth prompt).
- [x] **AC-US6-06**: After sign-out via CLI (which now revokes per US-005 and clears the canonical slot), the desktop's identity cache is cleared on its next boot — no stale `signedIn: true` rendered.
- [x] **AC-US6-07**: The migration code path is feature-flagged (env var `VSKILL_KEYCHAIN_MIGRATE=1` default-on) and scheduled for removal in a follow-up release; the migration block carries a `// REMOVE AFTER vskill 1.1.x` comment with a target version.
- [x] **AC-US6-08**: A unit test simulates: (a) old slot populated, new slot empty → migration moves the token; (b) both slots populated → new slot wins, old slot deleted; (c) both slots empty → no-op; (d) migration lock held by another process → second runner waits up to 5s, then no-ops.

## Functional Requirements

### FR-001: Loopback-only bind on eval-server
The eval-server's HTTP listen call MUST pass `"127.0.0.1"` as the explicit host argument. The dynamic-port allocator MUST preserve the host argument across retries.

### FR-002: Per-launch X-Studio-Token gate
The eval-server MUST generate a 256-bit random token at boot, expose it to the WebView only via Tauri IPC `get_studio_token`, require `X-Studio-Token` on every HTTP request, and compare with `crypto.timingSafeEqual`. The previous Origin-regex allowlist MUST be deleted.

### FR-003: WebView token isolation
`account_get_token` IPC MUST be removed. A replacement `account_get_user_summary` IPC returns `{ login, avatarUrl, tier, signedIn }` only. WebView callers route GitHub-bound traffic through the eval-server proxy.

### FR-004: Release-binary placeholder assertion
`build.rs` MUST panic in release builds when `GITHUB_OAUTH_CLIENT_ID` is unset or equals the placeholder. CI MUST `strings | grep -q` the release binary for the placeholder and fail the build on any match.

### FR-005: Best-effort GitHub revocation on sign-out
Sign-out MUST issue a `DELETE` to the GitHub OAuth-app revocation endpoint (correct variant for the registered OAuth App), with a 5s tokio timeout, BEFORE clearing the keychain. The keychain MUST be cleared even on revocation failure. The token MUST NOT be logged.

### FR-006: Keychain service consolidation with one-time migration
The Node side MUST switch to service `com.verifiedskill.desktop`. A one-time, idempotent, mutex-guarded migration MUST move any value from `vskill-github` to `com.verifiedskill.desktop` on first boot post-upgrade.

## Risks / Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `127.0.0.1` bind breaks an undocumented LAN integration users rely on | Low | Med | None known internally; CHANGELOG note + opt-in flag deferred to a follow-up if a real user surfaces it. Keep the change simple — do not ship a config knob preemptively. |
| WebView code that legitimately needs the token gets broken when `account_get_token` is removed | Med | High | AC-US3-04 grep gate; replace ALL call sites BEFORE removing the IPC; keep both IPCs side-by-side for one PR if needed (then a follow-up PR removes `account_get_token`). |
| `build.rs` panic blocks contributors who forget to set the env var locally | Med | Low | `cfg(debug_assertions)` carve-out — local debug builds tolerate the placeholder. |
| GitHub revocation endpoint differs between OAuth Apps and GitHub Apps; we call the wrong one | Med | Med | Document the chosen endpoint in a code comment + integration test against a `mockito` stub of the correct path. Confirm endpoint by registration record before merging. |
| Keychain migration race causes data loss when two processes run simultaneously | Low | High | File-mutex with 5s TTL + read-old/write-only-if-new-empty/delete-old order ensures atomicity at the slot level. Unit tests cover the four state combinations. |
| Apple notarization regression (the 0828 baseline) from any change in this increment | Low | High | Hard constraint: ZERO entitlement changes, ZERO new capabilities. Pre-merge checklist: signed `.dmg` notarizes locally; CI re-runs the 0828 notarization smoke. |
| X-Studio-Token leaks via WebView devtools / user screenshot | Low | Low | Token is per-launch and rotated on every restart; expiry is process lifetime. Not persisted. |
| CI `strings | grep` step exits 0 on a binary that compresses/encrypts the literal | Low | Med | Standard `cargo build --release` does not compress strings; if a future feature changes that, the placeholder check moves to a more reliable mechanism (e.g., a build-script-emitted compile-time assertion). |
| `tokio::spawn` for revocation outlives the process and is killed mid-request | Low | Low | 5s timeout bound; revocation is best-effort by design. Keychain is cleared regardless. |

## Success Criteria

- All 6 P0 findings have a closed acceptance test that demonstrates the threat is no longer reachable.
- The 0828 Phase 1 baseline still passes: signed `.dmg` notarizes, Studio loads in WebView, sidecar lifecycle works.
- `lsof` shows the eval-server bound to `127.0.0.1` only.
- A LAN-side curl to the eval-server returns `ECONNREFUSED`.
- A localhost curl without `X-Studio-Token` returns `401`; with it returns `200`.
- WebView DOM contains no `gho_*` substring at any point during signed-in usage (Playwright assertion).
- A release build with `GITHUB_OAUTH_CLIENT_ID` unset fails red in CI; the `strings | grep` step passes against a properly-built release binary.
- After sign-out, the GitHub OAuth grant page shows the App revoked (manual verification gate).
- Sign-in via desktop is visible to the CLI on next invocation (and vice versa) on the same machine.
- No new npm dependencies in `package.json`. No new Rust runtime dependencies in `Cargo.toml` (only existing `mockito` dev-dep is reused).
- `Entitlements.plist` is byte-identical to the 0828 baseline.
- Test coverage ≥ 90% on changed lines.

## Out of Scope

Explicitly deferred:
- Mounting `ConnectedRepoWidget` into `Sidebar.tsx` → **0837**
- Mounting `SkillCountBadge` into `StatusBar.tsx` → **0837**
- Adding `lucide-react` or any new icons → **0837**
- Building the `WorkspaceTree` component → **0837**
- Any new `/account` UI surface → **0837**
- GitHub App migration (vs OAuth App) → Phase 3 (separate increment)
- GitHub Enterprise Server (GHES) support → Phase 3
- SAML SSO → Phase 3
- MDM / managed-device policies → Phase 3
- Stripe billing wiring → Phase 2
- Team tier feature surface → Phase 2

Explicitly NOT included in this increment:
- A user-facing toggle for the eval-server bind host.
- A user-facing setting to view or rotate the studio-token.
- Telemetry on revocation success/failure.
- Cross-platform keychain migration (Windows/Linux) — desktop is macOS-only at v1.0.17.

## Dependencies

**Upstream (must already be in tree):**
- 0828 vskill desktop app baseline — signed `.dmg`, notarization, sidecar lifecycle.
- 0831 enterprise-tier OAuth surface — provides `device_flow.rs`, `token_store.rs`, `github_client.rs`, `account/commands.rs` which this increment hardens.
- `mockito` 1.x dev-dep already present in `src-tauri/Cargo.toml`.
- `keyring` v3 (Rust) and `@napi-rs/keyring` (Node) — both already shipped.
- `Zeroizing<String>` wrapper — already shipped in 0831.

**Downstream (consumers of this increment's surface):**
- 0837 GitHub Connection UI — will mount widgets that use `account_get_user_summary` and route HTTP through the studio-token-gated eval-server.

**External:**
- A real GitHub OAuth App `client_id` (and, depending on US-005's endpoint choice, possibly a `client_secret`) registered with the device-flow scope, available as a CI secret named `GITHUB_OAUTH_CLIENT_ID`.

**Cross-cutting:**
- Apple notarization workflow (0828) must remain green.

## Definition of Done

- [ ] All 6 user stories have every AC marked `[x]`.
- [ ] Unit tests cover keychain migration state matrix, X-Studio-Token compare, sign-out call ordering, and `account_get_user_summary` not-signed-in shape.
- [ ] Integration tests via `mockito` cover the GitHub revocation call (200 / 401 / 5xx / timeout).
- [ ] Playwright E2E asserts `gho_*` is absent from the WebView DOM in signed-in flows.
- [ ] CI `assert-no-placeholder-client-id` step passes on a real release binary; an intentionally-broken dry-run shows the step fails red.
- [ ] `lsof` on a launched app shows the eval-server bound to `127.0.0.1` only.
- [ ] A non-loopback curl to the eval-server returns `ECONNREFUSED` (manual verification gate).
- [ ] After sign-out, the OAuth App is revoked on github.com (manual verification gate against a real account).
- [ ] Sign-in via desktop is visible to `vskill auth status` (CLI) on next invocation (manual verification gate).
- [ ] Signed `.dmg` notarizes successfully (re-runs the 0828 smoke).
- [ ] `Entitlements.plist` diff against the 0828 baseline is empty.
- [ ] No new entries in `package.json` `dependencies`. No new entries in `Cargo.toml` `[dependencies]`.
- [ ] `code-review-report.json` clean (no critical/high/medium findings; or all addressed in fix loop).
- [ ] `simplify` pass complete; no duplication or readability flags remain.
- [ ] `grill-report.json` written and findings addressed.
- [ ] `judge-llm-report.json` written (or WAIVED with consent).
- [ ] `src-tauri/README.md` documents the `GITHUB_OAUTH_CLIENT_ID` build-arg.
- [ ] Runbook for rotating the OAuth `client_id` lives under `.specweave/docs/internal/specs/`.
- [ ] CHANGELOG entry under "Security" for vskill 1.0.18.

## Brainstorm Provenance

User stories synthesized from the advocate / critic / pragmatist trio brainstorm on 2026-05-09 against vskill v1.0.17. The critic surfaced findings P0-1 through P0-6 against the shipping codebase; the pragmatist scoped the surgical fix set; the advocate locked the non-functional contract (zero entitlement changes, zero new deps, zero UI work). All six findings were independently re-verified in the codebase before this spec was written.
