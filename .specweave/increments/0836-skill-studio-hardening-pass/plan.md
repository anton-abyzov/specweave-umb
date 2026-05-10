# Implementation Plan: Skill Studio Hardening Pass — 6 P0 Security Findings

**Increment**: 0836-skill-studio-hardening-pass
**Author**: Architect agent
**Created**: 2026-05-10
**Status**: Ready for implementation

---

## 1. Overview

This increment closes six P0 security findings in `vskill` desktop v1.0.17 identified by the brainstorm trio (advocate / critic / pragmatist) on 2026-05-10. Pure security pass — zero new features, zero UI changes (one optional "Signing out…" toast aside), zero new Tauri capabilities, zero new npm dependencies, zero changes to `src-tauri/Entitlements.plist`.

Each finding ships as a small, surgical, independently-revertible change. Effort estimate: ~3.5 dev-days end-to-end with TDD; can be split into 6 parallel agent slices when running under team-lead.

The 6 findings, with the corresponding ADR they materialize:

| # | Finding (one-line) | ADR |
|---|---|---|
| 1 | `eval-server.listen(port)` binds 0.0.0.0 (LAN-reachable) | inline (no ADR; 1-line fix) |
| 2 | `LOCALHOST_ORIGIN_RE` CORS allowlist is permissive | [0836-01](../../docs/internal/architecture/adr/0836-01-x-studio-token-gate.md) |
| 3 | `account_get_token` IPC returns raw `gho_*` to WebView | inline (delete + replacement) |
| 4 | `Iv1.placeholder-replace-before-ship` shipped in v1.0.17 | [0836-04](../../docs/internal/architecture/adr/0836-04-build-rs-client-id-assertion.md) |
| 5 | Sign-out clears keychain but never revokes the GitHub grant | [0836-02](../../docs/internal/architecture/adr/0836-02-token-revocation-api.md) |
| 6 | Two-keychain divergence between Rust desktop and Node CLI | [0836-03](../../docs/internal/architecture/adr/0836-03-keychain-canonical-service.md) |

---

## 2. Component architecture

### 2.1 Touched files (modify)

```
repositories/anton-abyzov/vskill/
├── src-tauri/
│   ├── build.rs                              [MODIFY]  client_id assertion (US-004)
│   ├── src/
│   │   ├── lib.rs                            [MODIFY]  remove account_get_token; register get_studio_token (US-002, US-003)
│   │   ├── commands.rs                       [MODIFY]  sign_out → async + revocation; add get_studio_token (US-001, US-002, US-005)
│   │   ├── sidecar.rs                        [MODIFY]  capture studio token from sidecar stdout (US-002)
│   │   ├── auth/
│   │   │   └── github_client.rs              [MODIFY]  add revoke_grant() (US-005)
│   │   └── account/
│   │       ├── commands.rs                   [MODIFY]  delete account_get_token; add account_get_user_summary (US-003)
│   │       ├── mod.rs                        [MODIFY]  exports
│   │       └── tests.rs                      [MODIFY]  update tests for new surface
├── src/
│   ├── eval-server/
│   │   ├── eval-server.ts                    [MODIFY]  bind 127.0.0.1; print Studio token banner (US-001, US-002)
│   │   ├── router.ts                         [MODIFY]  remove LOCALHOST_ORIGIN_RE; add token gate (US-002)
│   │   └── __tests__/router.test.ts          [MODIFY]  cover token gate (new + replacement tests)
│   ├── lib/
│   │   ├── keychain.ts                       [MODIFY]  canonical service name + legacy fallback (US-006)
│   │   └── __tests__/keychain.test.ts        [MODIFY]  update assertions; cover fallback
│   └── eval-ui/src/desktop/
│       └── useDesktopBridge.ts               [MODIFY]  fetch X-Studio-Token via IPC; inject in fetch (US-002)
└── .github/workflows/
    └── desktop-release.yml                    [MODIFY]  add `strings | grep -q` step (US-004)
```

### 2.2 New files (create)

```
repositories/anton-abyzov/vskill/
├── src-tauri/src/auth/
│   └── grant_revoke.rs                       [NEW]     reqwest-based platform proxy call (US-005)
└── src/lib/migration/
    └── keychain-migration.ts                 [NEW]     file-mutex serialization + read/write/delete (US-006)
```

### 2.3 Untouched-but-load-bearing files

```
src-tauri/Entitlements.plist                  [DO NOT TOUCH]   preserves 0828 notarization
src-tauri/tauri.conf.json (capabilities)      [DO NOT TOUCH]   preserves capability allowlist
package.json (npm deps)                       [DO NOT TOUCH]   no new deps
src-tauri/Cargo.toml ([dependencies])         [DO NOT TOUCH]   reqwest, keyring, zeroize already present
src-tauri/src/auth/{device_flow,token_store}.rs [DO NOT TOUCH] runtime placeholder guard stays
```

### 2.4 Component diagram (Mermaid)

```mermaid
flowchart LR
  CLI["vskill CLI<br/>npx vskill studio"]
  EVAL["eval-server.ts<br/>Node, port 7077<br/>127.0.0.1 only"]
  WV["Tauri WebView<br/>useDesktopBridge"]
  RUST["Rust desktop<br/>Tauri runtime"]
  KC[("OS Keychain<br/>com.verifiedskill.desktop")]
  GH["github.com<br/>OAuth Apps API"]
  PLAT["verified-skill.com<br/>(platform)"]

  CLI -->|stdout: Studio token| EVAL
  EVAL -.bind 127.0.0.1.-> EVAL
  EVAL <-->|read token| KC
  WV -->|invoke get_studio_token| RUST
  RUST -->|stash token| RUST
  WV -->|fetch /api/v1/...<br/>X-Studio-Token: T| EVAL
  EVAL -->|proxy /api/v1/private/<br/>Authorization: Bearer gho_*| PLAT
  RUST -->|sign_out → revoke| PLAT
  PLAT -->|DELETE /applications/.../grant| GH
  RUST <-->|read/write/clear| KC

  style EVAL fill:#dde
  style RUST fill:#edd
  style KC fill:#ddedd
```

---

## 3. Per-user-story implementation strategy

> **Note**: spec.md is still the increment template at the time of writing. The PM agent is generating user stories in parallel. The 6 user-story slices below map 1:1 to the 6 P0 findings in the team-lead overview and the brainstorm interview state. When spec.md lands, ACs map to the headings here.

### US-001 — eval-server binds 127.0.0.1 only

**Finding**: `server.listen(port)` is the 1-arg form, which binds to `0.0.0.0` (all interfaces) on Node. A laptop on a coffee-shop wifi exposes the API to the LAN.

**Change** — `src/eval-server/eval-server.ts:175`:

```ts
// before
server.listen(port, () => { ... });
// after
server.listen(port, '127.0.0.1', () => { ... });
```

`'127.0.0.1'` (not `'localhost'`) avoids accidental IPv6 binds. We do NOT add a separate `::1` listener — the desktop's WebView and CLI both connect via 127.0.0.1, and dual-stack adds attack surface for no UX gain.

**Test** — `src/eval-server/__tests__/eval-server.test.ts` (new or extend):

```ts
test('listens only on loopback 127.0.0.1', async () => {
  const server = await startEvalServer({ port: 0 });
  const addr = server.address();
  expect(addr).toMatchObject({ address: '127.0.0.1' });
  await new Promise<void>((r) => server.close(() => r()));
});
```

**Files**: `src/eval-server/eval-server.ts` (1 line), test file (~10 lines).

**Risk**: low — Node `listen(port, host, cb)` is the documented signature. The dynamic-port allocator in the existing code already retries on `EADDRINUSE`; binding 127.0.0.1 doesn't change that path.

**Effort**: 1 hour.

---

### US-002 — replace localhost CORS with X-Studio-Token gate

**Finding**: `LOCALHOST_ORIGIN_RE` allows any browser tab on `http://localhost:*` to hit the API. See [ADR-0836-01](../../docs/internal/architecture/adr/0836-01-x-studio-token-gate.md).

**Change** — `src/eval-server/router.ts`:

1. Delete `LOCALHOST_ORIGIN_RE` constant and the Origin-based block in `sendJson`.
2. Add a `tokenGate(req, res)` middleware called from `Router.handle()` for every request whose path starts with `/api/`. Returns `true` if the request carries the right `X-Studio-Token` header (constant-time compared); writes `401` and returns `false` otherwise.
3. Static-file path and `OPTIONS` preflight bypass the gate.

**Change** — `src/eval-server/eval-server.ts`:

1. After the `Skill Studio: http://localhost:<port>` line, write `Studio token: <token>` to stdout (and log the token only at DEBUG level, never INFO).
2. Lazily generate `getStudioToken()` (defined per ADR-0836-01).

**Change** — `src-tauri/src/sidecar.rs`:

1. The sidecar spawn already pipes stdout. Add a parser that scans for the `Studio token: <token>` line, captures the value into `SharedSidecar.studio_token: Option<String>`, then continues piping through.

**Change** — `src-tauri/src/commands.rs`:

```rust
#[tauri::command]
pub fn get_studio_token(state: State<'_, SharedSidecar>) -> Option<String> {
    state.inner().lock().unwrap().studio_token.clone()
}
```

**Change** — `src-tauri/src/lib.rs`:

```rust
.invoke_handler(tauri::generate_handler![
    // ... existing commands ...
    commands::get_studio_token,   // 0836: studio token IPC
])
```

**Change** — `src/eval-ui/src/desktop/useDesktopBridge.ts`:

```ts
async function ensureStudioToken(): Promise<string | null> {
  if (_cached) return _cached;
  const token = await invoke<string | null>('get_studio_token');
  _cached = token;
  return token;
}

// Patch global fetch in Tauri context only
if (isTauri()) {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (input, init = {}) => {
    const url = typeof input === 'string' ? input : input.toString();
    if (url.startsWith('/api/') || url.startsWith(window.location.origin + '/api/')) {
      const token = await ensureStudioToken();
      if (token) {
        init.headers = { ...(init.headers || {}), 'X-Studio-Token': token };
      }
    }
    return originalFetch(input, init);
  };
}
```

**Tests**:

| Test | What it asserts |
|---|---|
| `router.test.ts: rejects /api/* without token` | 401 + empty body, no log of the missing/wrong token value |
| `router.test.ts: accepts /api/* with valid token` | Same 200 path as before |
| `router.test.ts: constant-time compare` | Length-mismatch returns 401 without invoking `timingSafeEqual` |
| `router.test.ts: OPTIONS bypasses gate` | Preflight returns 204 regardless of token |
| `router.test.ts: static files bypass gate` | `GET /index.html` returns 200 |

**Files**: ~50 lines net add to router.ts, ~20 lines to eval-server.ts, ~15 lines new IPC, ~25 lines bridge patch.

**Risk**: medium — bridge `fetch` patching is global; need explicit Tauri-only gate. CLI users curling the API will hit 401; banner is the upgrade signal.

**Effort**: 6 hours including tests.

---

### US-003 — remove `account_get_token` IPC; replace with `account_get_user_summary`

**Finding**: `src-tauri/src/account/commands.rs:25` returns the raw `gho_*` token to the WebView. A WebView XSS escalates to full GitHub grant compromise.

**Change** — `src-tauri/src/account/commands.rs`:

1. **Delete** `account_get_token` and its `read_token_from_store` helper. (Tests in `account/tests.rs` go with it.)
2. **Add** `account_get_user_summary`:

```rust
#[derive(Debug, Clone, serde::Serialize)]
#[serde(rename_all = "camelCase")]
pub struct AccountUserSummary {
    pub signed_in: bool,
    pub login: Option<String>,
    pub avatar_url: Option<String>,
    pub tier: String,  // "free" | "pro" | "enterprise"
}

#[tauri::command]
pub fn account_get_user_summary() -> AccountUserSummary {
    use crate::auth::load_identity_cache;
    use crate::quota::cache::load_quota_cache;

    let identity = load_identity_cache().ok().flatten();
    let tier = load_quota_cache().ok().flatten()
        .map(|c| c.response.tier.as_str().to_string())
        .unwrap_or_else(|| "free".into());

    match identity {
        Some(i) => AccountUserSummary {
            signed_in: true,
            login: Some(i.login),
            avatar_url: Some(i.avatar_url),
            tier,
        },
        None => AccountUserSummary {
            signed_in: false,
            login: None,
            avatar_url: None,
            tier: "free".into(),
        },
    }
}
```

3. Keep `account_get_platform_url` as-is.

**Change** — `src-tauri/src/lib.rs`:

```rust
.invoke_handler(tauri::generate_handler![
    // 0834 account — IPC for the /account WebView (US-012).
    // 0836: account_get_token REMOVED — XSS escalation path.
    account::commands::account_get_user_summary,
    account::commands::account_get_platform_url,
])
```

**WebView side** — `src/eval-ui/src/account/AccountContext.tsx` (the consumer). The original `getAuthHeader()` reached for `account_get_token` to mint `Authorization: Bearer ...`. Authenticated calls to `/api/v1/private/*` and `/api/v1/tenants/*` now flow through the eval-server's `platform-proxy.ts`, which already injects the token from the keychain on the proxy side. The WebView therefore does NOT need the raw token — it just calls relative `/api/v1/private/...` URLs and the proxy adds the bearer.

We update `AccountContext` to:

1. Remove `getAuthHeader()`.
2. Call `account_get_user_summary` for display data (avatar, login, tier).
3. For authenticated calls, fall back to relative URLs that go through the eval-server proxy.

**Tests**:

| Test | What it asserts |
|---|---|
| `account/tests.rs: account_get_user_summary signed-out returns defaults` | `{signedIn: false, login: null, avatarUrl: null, tier: "free"}` |
| `account/tests.rs: account_get_user_summary signed-in returns identity` | Returns cached values, never reads the keychain |
| `account/tests.rs: account_get_token is REMOVED` | Compile-time test (the symbol no longer exists) |
| Playwright: WebView heap never contains `gho_` | `await page.evaluate(() => document.documentElement.outerHTML).not.toContain('gho_')` |

**Risk**: medium — touches the WebView/AccountContext flow. Need to verify the proxy bearer-injection path covers every authenticated WebView request.

**Effort**: 4 hours including Playwright assertion.

---

### US-004 — `build.rs` rejects placeholder client_id; CI grep on signed binary

**Finding**: v1.0.17 shipped with `Iv1.placeholder-replace-before-ship` in the binary. See [ADR-0836-04](../../docs/internal/architecture/adr/0836-04-build-rs-client-id-assertion.md).

**Change** — `src-tauri/build.rs` (was 3 lines):

```rust
fn main() {
    println!("cargo:rerun-if-env-changed=GITHUB_OAUTH_CLIENT_ID");

    let profile = std::env::var("PROFILE").unwrap_or_default();
    if profile == "release" {
        let client_id = std::env::var("GITHUB_OAUTH_CLIENT_ID").unwrap_or_default();
        if client_id.is_empty() || client_id == "Iv1.placeholder-replace-before-ship" {
            panic!(
                "GITHUB_OAUTH_CLIENT_ID is unset or still the placeholder. \
                 Release builds REQUIRE a real OAuth App client_id. \
                 Set it in CI secrets / shell env before `cargo build --release`."
            );
        }
    }

    tauri_build::build()
}
```

**Change** — `.github/workflows/desktop-release.yml`:

```yaml
- name: Verify no placeholder client_id in release binary
  shell: bash
  run: |
    BIN_PATH="src-tauri/target/release/bundle/macos/vSkill.app/Contents/MacOS/vskill-desktop"
    if [ ! -f "$BIN_PATH" ]; then
      echo "::error::expected binary missing at $BIN_PATH"; exit 1
    fi
    if strings "$BIN_PATH" | grep -q "Iv1.placeholder-replace-before-ship"; then
      echo "::error::Placeholder GITHUB_OAUTH_CLIENT_ID found in signed binary"
      exit 1
    fi
    echo "OK: placeholder string absent from binary"
```

**Tests** — verifying build.rs logic:

```bash
# Manual / scripted
unset GITHUB_OAUTH_CLIENT_ID
cargo build --release   # MUST FAIL
GITHUB_OAUTH_CLIENT_ID=Iv1.placeholder-replace-before-ship cargo build --release  # MUST FAIL
GITHUB_OAUTH_CLIENT_ID=Iv1.real-id-1234 cargo build --release  # MUST PASS
cargo build  # debug — MUST PASS even without env (runtime guard catches it)
```

These shell scripts live under `repositories/anton-abyzov/vskill/scripts/test-build-rs.sh` and the increment's `tasks.md` references them as the manual gate before merge. Automated coverage is the CI workflow itself.

**Risk**: low — build.rs is small; changes scoped to release profile.

**Effort**: 2 hours including CI workflow verification.

---

### US-005 — sign-out revokes the GitHub OAuth grant

**Finding**: `sign_out` clears the keychain locally but never calls GitHub. See [ADR-0836-02](../../docs/internal/architecture/adr/0836-02-token-revocation-api.md).

**Change** — `src-tauri/src/auth/grant_revoke.rs` (NEW):

```rust
// Best-effort GitHub OAuth grant revocation. Posts to the platform proxy
// (vskill-platform owns the client_secret per ADR-0836-02). Returns
// quickly on success or budget-bust; never blocks longer than 5s total.

use std::time::Duration;
use zeroize::Zeroizing;

const DEFAULT_PLATFORM_URL: &str = "https://verified-skill.com";
const REVOKE_TIMEOUT: Duration = Duration::from_secs(5);

#[derive(Debug)]
pub enum RevocationOutcome {
    Revoked,           // 200/204 — grant deleted
    AlreadyInvalid,    // 401/404 — token already invalid; treated as success
    Failed(String),    // 5xx, network, timeout — log WARN, proceed with local clear
}

pub async fn revoke_grant(token: &str, platform_url: Option<&str>) -> RevocationOutcome {
    let base = platform_url.unwrap_or(DEFAULT_PLATFORM_URL);
    let url = format!("{}/api/v1/auth/github/grant", base);
    let bearer: Zeroizing<String> = Zeroizing::new(format!("Bearer {token}"));

    let client = match reqwest::Client::builder()
        .timeout(REVOKE_TIMEOUT)
        .user_agent(concat!("vskill-desktop/", env!("CARGO_PKG_VERSION")))
        .build()
    {
        Ok(c) => c,
        Err(e) => return RevocationOutcome::Failed(format!("client build: {e}")),
    };

    match client.delete(&url)
        .header(reqwest::header::AUTHORIZATION, bearer.as_str())
        .send().await
    {
        Ok(resp) => {
            let status = resp.status().as_u16();
            match status {
                200 | 204 => RevocationOutcome::Revoked,
                401 | 404 => RevocationOutcome::AlreadyInvalid,
                _ => RevocationOutcome::Failed(format!("http {status}")),
            }
        }
        Err(e) if e.is_timeout() => RevocationOutcome::Failed("timeout".into()),
        Err(e) => RevocationOutcome::Failed(format!("network: {e}")),
    }
}
```

**Change** — `src-tauri/src/auth/mod.rs`:

```rust
pub mod grant_revoke;
pub use grant_revoke::{revoke_grant, RevocationOutcome};
```

**Change** — `src-tauri/src/commands.rs:678` `sign_out`:

```rust
#[tauri::command]
pub async fn sign_out() -> Result<(), String> {
    use crate::auth::{
        clear_identity_cache, revoke_grant, RevocationOutcome, TokenStore,
    };

    let store = TokenStore::new();

    // Step 1: read token (best-effort) for the revocation call. We do NOT
    // bail on a missing token — local cleanup runs unconditionally.
    let token_for_revoke = store.load().ok().flatten();

    // Step 2: revoke if we have a token. 5s budget; never blocks beyond that.
    if let Some(token) = token_for_revoke {
        match revoke_grant(token.as_str(), None).await {
            RevocationOutcome::Revoked => log::info!("github grant revoked"),
            RevocationOutcome::AlreadyInvalid => log::info!("github grant already invalid"),
            RevocationOutcome::Failed(reason) => {
                log::warn!("github grant revocation failed (best-effort): {reason}")
            }
        }
    }

    // Step 3: ALWAYS clear local state regardless of step 2.
    let token_err = store.clear().err();
    let cache_err = clear_identity_cache().err();
    match (token_err, cache_err) {
        (None, None) => Ok(()),
        (Some(e), _) => Err(format!("clear keychain: {e}")),
        (_, Some(e)) => Err(format!("clear identity cache: {e}")),
    }
}
```

**Tests**:

| Test | What it asserts |
|---|---|
| `grant_revoke.rs: 200 → Revoked` | mockito stub returns 200; outcome is `Revoked` |
| `grant_revoke.rs: 401 → AlreadyInvalid` | success path |
| `grant_revoke.rs: 5xx → Failed` | maps to `Failed(...)` |
| `grant_revoke.rs: timeout → Failed("timeout")` | mockito delays; client times out at 5s |
| `commands.rs sign_out: keychain cleared even if revoke fails` | inject failure; assert `TokenStore::load() == None` after |

**Risk**: medium — depends on a platform endpoint that doesn't exist yet. We treat 404 as Failed (logs WARN, proceeds); follow-up increment ships the platform side.

**Effort**: 6 hours including mockito-backed tests.

---

### US-006 — canonical keychain service `com.verifiedskill.desktop` for both Rust and Node

**Finding**: Rust uses `com.verifiedskill.desktop`, Node uses `vskill-github` — divergent state. See [ADR-0836-03](../../docs/internal/architecture/adr/0836-03-keychain-canonical-service.md).

**Change** — `src/lib/keychain.ts` (constants):

```ts
export const SERVICE_NAME = 'com.verifiedskill.desktop';
export const GITHUB_TOKEN_KEY = 'github-oauth-token';
const LEGACY_SERVICE_NAME = 'vskill-github';
const LEGACY_TOKEN_KEY = 'github_token';
```

**Change** — `src/lib/keychain.ts` (read fallback):

```ts
getGitHubToken(): string | null {
  // Read canonical first.
  const r = tryKeyring((kr) => kr.getPassword(SERVICE_NAME, GITHUB_TOKEN_KEY));
  if (r.ok && r.value) return r.value;

  // 0836 compat: fall back to legacy slot for one release window.
  // TODO(0836-followup): remove after v1.0.19 ships.
  const legacy = tryKeyring((kr) => kr.getPassword(LEGACY_SERVICE_NAME, LEGACY_TOKEN_KEY));
  if (legacy.ok && legacy.value) return legacy.value;

  // ... existing fallback file logic ...
}
```

**Change** — `src/lib/migration/keychain-migration.ts` (NEW):

```ts
import * as fs from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';
import {
  SERVICE_NAME, GITHUB_TOKEN_KEY,
  type KeyringBackend
} from '../keychain.js';

const LEGACY_SERVICE = 'vskill-github';
const LEGACY_KEY = 'github_token';
const LOCK_FILE = path.join(os.homedir(), '.vskill', 'locks', 'keychain-migration.lock');
const DONE_FLAG = path.join(os.homedir(), '.vskill', 'keychain-migration.done');
const LOCK_TTL_MS = 5_000;

export interface MigrationDeps {
  keyring: KeyringBackend | null;
  fs?: typeof fs;
  now?: () => number;
}

export function runKeychainMigration(deps: MigrationDeps): 'migrated' | 'noop' | 'skipped' {
  const _fs = deps.fs ?? fs;
  const now = deps.now ?? Date.now;
  if (_fs.existsSync(DONE_FLAG)) return 'skipped';
  if (!deps.keyring) return 'skipped';

  // File-mutex acquire (with TTL steal).
  if (!acquireLock(_fs, now)) return 'skipped';

  try {
    const old = safeGet(deps.keyring, LEGACY_SERVICE, LEGACY_KEY);
    if (!old) {
      writeDoneFlag(_fs);
      return 'noop';
    }
    const canonical = safeGet(deps.keyring, SERVICE_NAME, GITHUB_TOKEN_KEY);
    if (!canonical) {
      // Old has data, new is empty — promote old to canonical.
      try { deps.keyring.setPassword(SERVICE_NAME, GITHUB_TOKEN_KEY, old); } catch {}
    }
    // Always delete old slot once we've ensured canonical is populated.
    try { deps.keyring.deletePassword(LEGACY_SERVICE, LEGACY_KEY); } catch {}
    writeDoneFlag(_fs);
    return 'migrated';
  } finally {
    releaseLock(_fs);
  }
}

// helpers (acquireLock, releaseLock, safeGet, writeDoneFlag) — see file
```

**Change** — `src/lib/keychain.ts` (`createKeychain`): call `runKeychainMigration({ keyring })` once before the first `getGitHubToken` returns, behind a per-process boolean flag.

**Change** — `src/lib/__tests__/keychain.test.ts`:

```ts
test('migration: old slot only → moved to canonical', () => { ... });
test('migration: new slot only → no-op', () => { ... });
test('migration: both populated → keep canonical, delete old', () => { ... });
test('migration: lock contention → second runner skips', () => { ... });
test('migration: stale lock (>5s) → stolen and migration runs', () => { ... });
test('migration: legacy fallback returned when canonical empty', () => { ... });
```

**Rust side** — NO CHANGE. `src-tauri/src/auth/token_store.rs:25` already uses `com.verifiedskill.desktop`. Add a single test that asserts `SERVICE_NAME` constant is `com.verifiedskill.desktop` (lock the value so a future rename trips CI):

```rust
#[test]
fn service_name_is_canonical_for_node_interop() {
    assert_eq!(
        super::SERVICE_NAME,
        "com.verifiedskill.desktop",
        "Renaming the keychain service breaks Node-side migration interop. \
         If you must rename, also update src/lib/keychain.ts and bump the migration."
    );
}
```

**Risk**: medium — file mutex on shared `~/.vskill/locks/` path. Two simultaneous CLI/desktop launches must serialize. We use TTL-based lock stealing for crashed migrations.

**Effort**: 8 hours including 6 migration tests.

---

## 4. Test plan

### 4.1 Test pyramid

| Layer | Tool | Scope | When |
|---|---|---|---|
| Unit (Rust) | `cargo test` | `commands.rs`, `auth/grant_revoke.rs`, `account/commands.rs`, `device_flow.rs` | every PR push |
| Unit (Node) | `vitest` | `keychain.ts`, `keychain-migration.ts`, `router.ts`, `eval-server.ts` | every PR push |
| Integration (Node) | `vitest` | `eval-server` boot, bind 127.0.0.1, token gate end-to-end against http.Server | every PR push |
| Integration (Rust + mockito) | `cargo test` | `grant_revoke` against simulated platform endpoint | every PR push |
| E2E (Playwright) | `npx playwright test` | WebView never receives `gho_*`; auth flow with seeded PAT | release candidate gate |
| Signed-build smoke | shell + Apple notarize | `strings | grep -q` placeholder; 127.0.0.1 listen verification on packaged `.app` | release pipeline only |
| Build.rs gate | shell | release-profile build fails on placeholder | release pipeline only |

### 4.2 Test mode: TDD

`testing.defaultTestMode: "TDD"` in `.specweave/config.json`. Each US slice runs RED → GREEN → REFACTOR with `/sw:tdd-cycle`. The agent owning a slice writes the test first, watches it fail, ships the implementation, then refactors.

### 4.3 Key new tests

- `src/eval-server/__tests__/router.test.ts` — `tokenGate` (5 cases listed in US-002).
- `src/eval-server/__tests__/eval-server-bind.test.ts` — `listens only on 127.0.0.1`.
- `src/lib/__tests__/keychain.test.ts` — 6 migration cases listed in US-006.
- `src-tauri/src/auth/grant_revoke.rs` — 4 mockito-backed cases listed in US-005.
- `src-tauri/src/account/tests.rs` — replace token-returning tests with `account_get_user_summary` cases.
- `src-tauri/src/auth/token_store.rs` — single canonical-name lock test (US-006).
- Playwright: `tests/e2e/webview-no-token-leak.spec.ts` — assert `document.documentElement.outerHTML` and `JSON.stringify(Object.entries(window))` contain no `gho_` substring after sign-in flow with a seeded fake PAT.

### 4.4 Blocking gates

Per CLAUDE.md "Testing Pipeline":

1. `npx vitest run` (unit + integration Node) — must be green before commit.
2. `cargo test` — must be green before commit.
3. `npx playwright test` — must be green before close.
4. `sw:code-reviewer` writes `code-review-report.json` — closure blocked on critical/high/medium findings.
5. `/simplify` runs after code-review — catches duplication, readability, inefficiency.
6. `/sw:grill` writes `grill-report.json` — closure blocked without it.
7. CI `desktop-release` workflow placeholder-grep step — blocks release on placeholder.
8. Signed-build manual smoke (engineer): launch the `.app`, verify the WebView loads, verify `lsof -i :7077` shows `127.0.0.1` only.

---

## 5. Risk register

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-1 | Notarization regression | low | HIGH | ZERO touches to `Entitlements.plist`, `tauri.conf.json` capabilities, or Cargo features that affect hardened-runtime. Reviewed by code-reviewer agent before merge. |
| R-2 | Keychain migration race (CLI + desktop simultaneous) | medium | medium | File mutex `~/.vskill/locks/keychain-migration.lock` with 5s TTL. Second runner sees `keychain-migration.done` flag and exits. 6 unit tests cover the contention paths. |
| R-3 | Platform endpoint for grant revocation does not exist yet | high | low | `revoke_grant` returns `Failed("http 404")` if the platform isn't ready. Local cleanup ALWAYS runs. We log WARN once per sign-out; user-visible behavior unchanged. Follow-up increment ships the platform side. |
| R-4 | `option_env!` vs `env!` semantics for client_id | low | medium | Resolved per [ADR-0836-04](../../docs/internal/architecture/adr/0836-04-build-rs-client-id-assertion.md): keep `option_env!` in `device_flow.rs` (debug builds tolerate missing); add release-only `panic!` in `build.rs`. CI grep is the second gate. |
| R-5 | WebView fetch-patching breaks non-Tauri builds | medium | medium | `if (isTauri())` guard; web build (`vskill-platform`-served studio) is unchanged. Playwright covers both paths. |
| R-6 | CLI users with scripted curls hit 401 after upgrade | medium | low | Stdout banner makes the token discoverable; release notes call this out. We accept this break as the security/UX trade. |
| R-7 | Token revocation accidentally signs out other devices | low | low | OAuth Apps issue ONE grant per user × app; revoking is global. Edge case where same user has two installs is acceptable per ADR-0836-02. |
| R-8 | `SharedSidecar.studio_token` racy on cold boot | low | medium | The token is captured BEFORE the WebView calls `get_studio_token` because the sidecar startup banner emits before the eval-server reports `/api/health` ready. Verified by sequence: spawn → stdout-line capture → stash → WebView mount → invoke. |

---

## 6. Effort estimate

| US | Effort (h) | With 30% buffer |
|---|---|---|
| US-001 (127.0.0.1 bind) | 1 | 1.5 |
| US-002 (token gate) | 6 | 8 |
| US-003 (account_get_user_summary) | 4 | 5 |
| US-004 (build.rs assertion) | 2 | 2.5 |
| US-005 (grant revocation) | 6 | 8 |
| US-006 (keychain consolidation) | 8 | 10.5 |
| **Total (sequential)** | **27** | **35** |
| **Total (4 parallel agents)** | ~9 | ~12 |

A 4-agent team-lead split is feasible: US-001 is 1h prerequisite (any agent), US-002 + US-003 share the WebView bridge so they go to one agent, US-004 + US-005 + US-006 go to three other agents in parallel. End-to-end wall time ~12-15 hours.

---

## 7. Rollback plan

Each US slice is one commit (or a tight 2-3 commit chain). Rollback is `git revert <sha>` for each:

| US | Rollback impact |
|---|---|
| US-001 | Re-binds 0.0.0.0; LAN-reachable again. Mitigated by US-002 still in place if only US-001 reverts. |
| US-002 | Re-enables Origin-CORS; WebView keeps working (the bridge fetch-patch is no-op without a token). |
| US-003 | Restores `account_get_token`; existing /account WebView still works. |
| US-004 | Build script reverts to 1-line; runtime guard remains. |
| US-005 | Sign-out reverts to keychain-clear-only; tokens re-leak on user's prior installs. |
| US-006 | CLI/desktop divergence returns; both keep working independently. |

No DB migrations, no schema changes, no config-file format changes. Reverts are safe at any point.

---

## 8. Out of scope (deferred)

- Platform-side `DELETE /api/v1/auth/github/grant` endpoint — follow-up increment.
- Removal of legacy fallback in `getGitHubToken` after one-release window — follow-up increment.
- Migrating `SERVICE_NAME` constant in Rust if we ever decide to rename — explicitly NOT planned.
- Studio-token rotation API (`POST /api/regenerate-token`) — not needed; restart rotates.
- Per-tab token isolation in WebView — single-process Tauri app, single token is sufficient.
- Hardware-backed keys (Secure Enclave, TPM) — out of scope; OS keychain is the right fence.

---

## 9. References

- [ADR-0836-01: X-Studio-Token gate](../../docs/internal/architecture/adr/0836-01-x-studio-token-gate.md)
- [ADR-0836-02: Token revocation API](../../docs/internal/architecture/adr/0836-02-token-revocation-api.md)
- [ADR-0836-03: Canonical keychain service](../../docs/internal/architecture/adr/0836-03-keychain-canonical-service.md)
- [ADR-0836-04: build.rs client_id assertion](../../docs/internal/architecture/adr/0836-04-build-rs-client-id-assertion.md)
- [ADR-0828-01: vskill desktop framework choice](../../docs/internal/architecture/adr/0828-01-vskill-desktop-framework-choice.md)
- [ADR-0831-01: Token storage — keyring](../../docs/internal/architecture/adr/0831-01-token-storage-keyring.md)
- [ADR-0831-02: OAuth-only free; App opt-in pro](../../docs/internal/architecture/adr/0831-02-oauth-free-app-paid.md)
- Brainstorm interview state: `.specweave/state/interview-0836-skill-studio-hardening-pass.json`
