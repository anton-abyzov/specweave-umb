# ADR 0702-01: vskill credential storage — file-backed, plaintext with `0600`

**Status**: Accepted
**Date**: 2026-04-24
**Increment**: [0702-skill-studio-cross-platform-api-key-storage](../../../increments/0702-skill-studio-cross-platform-api-key-storage/)
**Deciders**: Anton (user), sw:architect

## Context

vskill Studio needs a single credential-persistence strategy for API keys across macOS, Linux, and Windows. The prior implementation had three compounding failures:

1. **Windows had no working persistence path.** "Browser storage (default)" was actually a Node-process in-memory `Map` — lost on every server restart. The UI label was a lie.
2. **macOS Keychain was Darwin-only.** Shelled out to the `security` CLI — no equivalent on Linux/Windows, so 2/3 of the dev audience had no opt-in tier.
3. **Saved keys never reached `createLlmClient`.** The eval pipeline read `process.env.ANTHROPIC_API_KEY` directly (`src/eval/llm.ts`) and ignored the settings-store. Users saved a key, restarted, and the eval still failed.

Plus, OpenAI was not supported at all.

The threat model is "solo developer, local CLI tool, user-home ACLs on a single-user machine." It is NOT a multi-tenant server, not a shared workstation, and not a cloud service. This matches the deployment profile of `aws`, `kubectl`, `gh`, `supabase` (keychain fallback), and every other developer CLI — all of which persist credentials to user-mode files protected by POSIX permissions.

We considered four storage strategies.

## Options considered

### Option A — file-backed plaintext at `~/.vskill/keys.env` with `0600` **(chosen)**

Single KEY=VALUE dotenv file. Atomic write via temp-file + rename. POSIX `chmod 0600` after write. Boot-time merge of file contents into `process.env` (only for keys NOT already set in the real environment).

- **Pros**: Zero native deps. Same mental model as every other CLI tool (`aws`, `kubectl`, etc.). Works identically on all three platforms. Debuggable — `cat ~/.vskill/keys.env` tells you everything. Scriptable provisioning via `vskill keys set` + piped stdin. Real env vars always win, so power users have a clean escape hatch.
- **Cons**: Plaintext at rest. An attacker with local read access to `~/.vskill/keys.env` sees every key. `0600` mitigates cross-user read on multi-user machines; does not mitigate malware running as the same UID.

### Option B — `@napi-rs/keyring` OS-vault backend

Use the OS credential vault (macOS Keychain, Windows Credential Manager, libsecret on Linux) via a pure-Rust native binding that ships prebuilt binaries for all three platforms.

- **Pros**: Encryption at rest. No plaintext file. Matches OS-native security posture.
- **Cons**: Native dependency adds install complexity, prebuild-matrix risk (musl vs glibc, Win ARM64), and doubles npm install time on first run. Linux keyring (libsecret) requires a running D-Bus session — fails in headless CI, SSH sessions without forwarding, and Docker without the secret-service sidecar. Debugging "why doesn't my key persist" becomes OS-specific. Our threat model does not justify this cost; deferred behind a feature flag for a future increment.

### Option C — encrypted file using a user-derived key

Write an encrypted file. Key derived from something only this user has (machine ID + username, or a passphrase).

- **Pros**: Encryption at rest without native deps.
- **Cons**: Any local attacker running as the same UID can derive the key too (the whole protection boundary is the OS ACL, same as plaintext). Passphrase-based encryption trades UX (re-enter on every restart) for marginal security. Snake oil — looks more secure than plaintext+`0600` but has equivalent local-threat properties.

### Option D — remote key sync via cloud provider

Sync keys via an external key-management service (e.g., 1Password CLI, AWS Secrets Manager).

- **Pros**: Single source of truth across machines.
- **Cons**: Adds a required external dependency. Our users already have their own secrets manager; we should respect real env vars as the integration point rather than bolting on a sync layer. Users who want this export env vars from their secrets manager of choice — zero code required from vskill.

## Decision

**Option A: file-backed plaintext at `~/.vskill/keys.env` with `0600`.**

## Consequences

### Positive
- Windows/Linux/macOS all get first-class persistence with a single code path.
- No native module compilation, no D-Bus dependency, no prebuild matrix.
- `vskill keys set/list/remove/path` CLI works identically on all three platforms.
- Debuggability is maximal — the file is one command away (`cat ~/.vskill/keys.env`).
- Scriptable via piped stdin, suitable for dotfiles/CI provisioning.
- Real env vars always win — power users with their own secrets managers need no code change.

### Negative
- Plaintext at rest. Users with shared machines or who worry about malware running as their UID should use env vars from their own secrets manager instead.
- No encryption key-rotation capability; users rotate by re-running `vskill keys set`.

### Accepted risk
Malware running as the same user can read `~/.vskill/keys.env`. This is the same risk profile as every other developer CLI (`aws`, `kubectl`, `gh`, etc.) — accepted by the industry for this class of tool. Users requiring stronger isolation (ephemeral sessions, hardware keys, enterprise-vault integration) should use env vars sourced from their enterprise tooling — documented in README.

### Future work
The `@napi-rs/keyring` backend (Option B) is deferred to a future increment behind a feature flag. If user feedback demands encryption at rest, revisit.

## Implementation notes

### Boot-time env merge (FR-002)

The `mergeStoredKeysIntoEnv(store)` function runs at the **very top** of `eval-server.ts` module body, before any provider client module is imported. Merge semantics: for each provider in `PROVIDERS`, if `process.env[envVarName]` is already set, do nothing; otherwise read the stored key and set `process.env[envVarName]`. Real env vars are never overwritten.

A dedicated `src/eval-server/boot-preflight.ts` module contains the merge call and is imported as the **first** import in `eval-server.ts` — with a file-header comment warning future maintainers not to reorder. An integration test (T-020) spawns the server in a subprocess with only a stored key (no env var) and asserts `/api/eval` succeeds — regression-guards boot ordering.

### Dual-map pattern for `listKeys` after merge

After merging stored keys into `process.env`, the in-memory value `Map` is cleared to shrink plaintext dwell time (security hygiene). But `listKeys` still needs to report `stored: true` with `updatedAt` timestamps for UI display.

Naive single-map approach (`Map<Provider, {value, updatedAt}>`): clearing the map after merge also clears the `updatedAt` metadata, and `listKeys` then reports every provider as `stored: false` even though the keys are on disk and in `process.env`.

**Solution**: split into two maps.
- `memoryMap: Map<Provider, {value: string}>` — plaintext values, **cleared** post-merge.
- `metadataMap: Map<Provider, {updatedAt: string}>` — metadata only, **retained** across merge.

`listKeys()` reports `stored: true` when any of:
1. The provider is in `metadataMap` (remembered from boot merge).
2. The real env var is set (`process.env[envVarName]`).
3. The on-disk `keys.env` file contains the provider (lazy re-read).

`hasKeySync()`, `saveKey()`, `removeKey()`, and `resetSettingsStore()` all updated to operate on both maps consistently. `removeKey()` additionally deletes `process.env[envVarName]` so `readKey()` post-remove returns `null`.

This was identified during Playwright E2E verification in Phase 3 (defect P0 in `reports/verification-report.md`). Pre-fix, a saved key survived a server restart on disk but the UI reported "No key stored" — violating AC-US1-01.

**Security invariant preserved**: raw plaintext still leaves `memoryMap` after merge. Only `{updatedAt}` metadata is retained. All logs and error messages continue to go through `redactKey()` only (AC-US7-01/02).

### Lenient parser (FR-001)

The `keys.env` parser skips malformed lines with a single aggregated warning (not per-line spam), handles BOM prefix, trims whitespace, and never throws from parse. Users who hand-edit the file and introduce a typo don't crash the server — they get a warning and the valid lines continue to work.

### `~/.vskill/` vs `envPaths("vskill").config`

We use `~/.vskill/` (or `$VSKILL_CONFIG_DIR` override) rather than the XDG-spec location from `env-paths`. This matches Claude Code's `~/.claude/` convention — our target audience's mental model — and is short, memorable, scriptable. XDG purists can set `VSKILL_CONFIG_DIR=$XDG_CONFIG_HOME/vskill`.

### Single `PROVIDERS` constant (FR-003)

`src/eval-server/providers.ts` exports a single `PROVIDERS` array driving the UI dropdown, detection API, and CLI validation. Adding OpenAI as a third provider touched this one constant; the prior architecture required edits in three places and had a latent bug (the UI listed Anthropic+OpenRouter but the detection logic lived in a separate hardcoded switch).

## References

- Increment: [0702-skill-studio-cross-platform-api-key-storage](../../../increments/0702-skill-studio-cross-platform-api-key-storage/)
- Brainstorm: `.specweave/docs/brainstorms/2026-04-24-skill-studio-api-key-storage.md`
- Implementation: `repositories/anton-abyzov/vskill/src/eval-server/settings-store.ts`, `repositories/anton-abyzov/vskill/src/eval-server/boot-preflight.ts`, `repositories/anton-abyzov/vskill/src/eval-server/providers.ts`
- Verification: `.specweave/increments/0702-skill-studio-cross-platform-api-key-storage/reports/verification-report.md`
- Similar-precedent prior art: `aws` (`~/.aws/credentials`), `kubectl` (`~/.kube/config`), `supabase` CLI fallback, `gh` CLI (`~/.config/gh/hosts.yml`)
