# ADR-0702: Cross-Platform API Key Storage for Skill Studio

**Status**: Accepted
**Date**: 2026-04-24
**Deciders**: Anton Abyzov (admin@easychamp.com), verify-final-0702 agent
**Increment**: [0702-skill-studio-cross-platform-api-key-storage](../../../increments/0702-skill-studio-cross-platform-api-key-storage/)

## Context

`vskill studio` stores per-user LLM provider API keys (Anthropic, OpenAI, OpenRouter) so the eval pipeline can run without re-pasting keys on each start. Before 0702 we shipped a tiered store with two options:

1. **"Browser storage (default)"** — a label. The actual implementation was a Node-process in-memory `Map` in `settings-store.ts`. Every server restart wiped it. The label was misleading.
2. **"macOS Keychain"** — a Darwin-only shell-out to the `security` CLI. No working equivalent on Linux or Windows, so two-thirds of the dev audience had no opt-in persistence tier at all.

Three compounding failures:

1. **Windows + Linux had no working persistence path.** A Windows developer saved a key, restarted `vskill studio`, and the key was gone.
2. **The tier radio UI lied.** Users thought they were choosing between storage backends; they were choosing between "in-memory Map" and "Darwin-only Keychain".
3. **Saved keys never reached `createLlmClient`.** The eval pipeline read `process.env.ANTHROPIC_API_KEY` directly (`src/eval/llm.ts:165`) and ignored the settings-store entirely. Even on macOS with Keychain configured, the saved key silently did not flow to the provider client; evals failed with misleading "no key" errors.

Additionally, **OpenAI was not supported at all** — only Anthropic and OpenRouter had provider clients, despite OpenAI being the third-most-common provider for our eval audience.

The ideation exercise considered five approaches (plaintext file, encrypted file, OS keyring via `@napi-rs/keyring`, project-local `.env`, cloud sync) across five lenses (prior-art survey, security, cross-platform, minimalism, UX) in `.specweave/docs/brainstorms/2026-04-24-skill-studio-api-key-storage.md`.

## Decision

**One file. One code path. Three platforms. Terminal-native onboarding.**

### 1. Single plaintext file at `~/.vskill/keys.env` with `0600` on POSIX

- Path: `~/.vskill/keys.env` (override: `VSKILL_CONFIG_DIR` env var for tests, CI, and power users).
- Format: dotenv (`KEY=VALUE` per line). One file, same format on macOS, Linux, Windows.
- Writes: atomic via temp-file + `fs.rename`. On POSIX, `fs.chmodSync(tmp, 0o600)` before rename. Windows skips chmod (filesystem ACLs apply).
- Parse: lenient — malformed lines (BOM, stray whitespace, non-`KEY=VALUE` noise) are skipped with one aggregated warning. A corrupt `keys.env` does NOT crash the server.
- Implementation lives in `src/eval-server/settings-store.ts` (file-backed store replaces the old tiered store at the same module path; all 60+ import sites need no change).

### 2. Boot-time merge into `process.env`

- New module `src/eval-server/boot-preflight.ts` runs `mergeStoredKeysIntoEnv(store)` at the TOP of `eval-server.ts` — BEFORE any provider module import reads `process.env`.
- For each provider in `PROVIDERS`: if `process.env[envVarName]` is already set, leave it alone (real env vars always win). Otherwise set it from the store.
- After merge, `store.clearMemory()` empties the in-memory value map. A separate `metadataMap` retains `updatedAt` for `listKeys` reporting. Plaintext dwell time in the process heap is minimized.

### 3. Env vars ALWAYS win over stored keys (precedence)

Real `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `OPENROUTER_API_KEY` env vars are NEVER overwritten by the merge. This is the power-user escape hatch (CI, dotfile-managed shells, `direnv`, etc.) and is tested explicitly in `merge-env.test.ts`.

### 4. Three-provider support

OpenAI is added as a first-class provider alongside Anthropic and OpenRouter via a single `PROVIDERS` constant in `src/eval-server/providers.ts` that drives UI dropdown + detection API + CLI validation. Triple maintenance burden eliminated.

### 5. Honest UI

- Settings modal removes the tier radio entirely.
- Modal shows the literal storage path: `"Keys stored at <absolute-path> (protected by file permissions)"`.
- "Copy path" button copies the absolute path to clipboard.
- No references to "tier", "keychain", or "browser storage" remain anywhere in UI strings (grep-guarded in test).

### 6. Terminal-native first-run onboarding

`runEvalServe` detects "no stored key AND no env var set" and presents a yes/no prompt BEFORE `openBrowser()`:
- Yes → masked stdin paste (raw mode, no echo), prefix-validated (`sk-ant-` for Anthropic), `saveKey` before browser opens.
- No → print `vskill keys set <provider>` hint + continue to browser.
- Skipped silently if any provider env var is already set (no nagging power users).

### 7. Scriptable CLI — `vskill keys set | list | remove | path`

Shares the same `FileBackedStore` as the server. Covers dotfile-management + provisioning flows. POSIX + Windows CI matrix in `.github/workflows/ci.yml` (`keys-store-cli` job).

### 8. One-shot Darwin migration

On Darwin first-boot of new version, server offers migration of existing `vskill-anthropic` / `vskill-openrouter` Keychain entries via endpoints `GET /api/settings/legacy-keychain-available` + `POST /api/settings/migrate-legacy-keychain`. Old Keychain entries retained 30 days post-import (observability note logged on each boot that reads a retained entry). Non-Darwin platforms are no-op.

## Consequences

### Positive

1. **Works on all three OSes with one code path.** The same module serves macOS, Linux, Windows; no platform branches at the call sites.
2. **Keys actually reach `createLlmClient`.** The env-var merge means `src/eval/llm.ts` (and every other consumer that reads `process.env`) works unchanged.
3. **Net LOC reduction.** `src/eval-server/settings-store.ts` shrank by ~150 lines (tier selection, Keychain shell-out, `UnsupportedTierError`, `Tier` type, platform-specific fallback paths all deleted). `deleted-symbols.test.ts` enforces the deletion at the module-namespace level to prevent resurrection.
4. **Honest UI.** The "Browser storage" label is gone. Users see the literal path. They can inspect it, back it up, add it to their dotfile manager.
5. **Matches existing precedent.** `aws`/`kubectl`/`supabase`-fallback all use plaintext with `0600` in `~/`. We aren't inventing a weird security posture; we're following the pattern.
6. **First-run time-to-eval under 60s.** Terminal prompt → paste key → browser opens → first eval. No "open the settings, pick a tier, hit save, restart" dance.

### Negative

1. **Plaintext at rest.** The threat model is "solo developer, local tool, user-home ACLs". Not "laptop stolen while unlocked". A developer who wants OS-vault encryption can `direnv` / `1password-cli` their way to env vars (which the merge will always honor).
2. **No profile separation.** `anthropic` / `openai` / `openrouter` each store one key. Users who want `work` vs `personal` pools must swap the file or use env vars. The data-model namespace is reserved in the `PROVIDERS` constant so a future increment can add `:<profile>` suffix without a schema break.
3. **Darwin Keychain is deprecated as a storage tier.** Existing users are migrated automatically on first boot. Old Keychain entries live another 30 days as a rollback safety net, then the user can manually `security delete-generic-password` them. No breaking change — just an offered one-click import.
4. **Dropped the tier UI.** Users who liked having a "choose your backend" knob lose it. The decision is "there is one backend — it's this file — if you want encryption, set env vars from your secrets manager".

### Neutral

1. **`@napi-rs/keyring` (OS-vault native backend) is deferred, not ruled out.** A follow-up increment can add an opt-in "Store in OS keyring" tier behind a feature flag if demand materializes. The `FileBackedStore` abstraction would remain as the default and fallback.
2. **Cloud/remote key sync remains out of scope.** Users export env vars from their own secrets manager. vskill is not in the credentials-cloud business.

## Alternatives Considered

### A. `@napi-rs/keyring` / `node-keytar` native backend as default

**Rejected because**:
- Native module dependency complicates install (`node-gyp`, Windows build tools). Breaks `npm install -g vskill` for a non-trivial fraction of the audience.
- Linux keyring coverage is inconsistent — `gnome-keyring` on GNOME, `kwallet` on KDE, unlock-on-login nuances, headless CI workarounds. A surprising amount of complexity for a tool that's supposed to "just work".
- The `aws` / `kubectl` / `supabase` precedent shows the industry default for dev-tool credential storage IS a `0600` file in `~/`. Users already trust this pattern.
- Deferred as an opt-in future tier rather than abandoned. See "Negative #4" and "Neutral #1" above.

### B. Project-local `.env` file

**Rejected because**:
- Per-project duplication — developer with 10 vskill projects has 10 copies of the same key.
- Higher risk of accidental commit (developers forget `.gitignore`). User-home storage sidesteps this entirely.
- Doesn't fit the "vskill studio is a user-scoped dev tool" mental model.

### C. Windows DPAPI (ProtectedData)

**Rejected because**:
- Platform-specific. Would force a dual-path implementation (DPAPI on Windows, something else on Linux/macOS). The goal was to COLLAPSE platform branches, not add them.
- Encrypted-at-rest doesn't meaningfully defend against the "malware running as the user" threat (which is most of the realistic threats for a local dev tool), because the same process can decrypt the vault.
- DPAPI is harder to inspect, back up, copy to a new laptop. `0600` plaintext files are a known quantity.

### D. Encrypted file with user-entered passphrase (KeePass-style)

**Rejected because**:
- UX tax on every `vskill studio` start (enter passphrase) undermines the "under 60s to first eval" goal.
- If the passphrase is memorized in a keychain/keyring, we've just rebuilt the OS-vault approach with extra steps.
- Wrong security posture for a local dev tool used by the key-holder on a machine they already own.

## Implementation References

- Spec: [`.specweave/increments/0702-skill-studio-cross-platform-api-key-storage/spec.md`](../../../increments/0702-skill-studio-cross-platform-api-key-storage/spec.md)
- Plan: [`.specweave/increments/0702-skill-studio-cross-platform-api-key-storage/plan.md`](../../../increments/0702-skill-studio-cross-platform-api-key-storage/plan.md)
- Tasks: [`.specweave/increments/0702-skill-studio-cross-platform-api-key-storage/tasks.md`](../../../increments/0702-skill-studio-cross-platform-api-key-storage/tasks.md)
- AC verification: [`.specweave/increments/0702-skill-studio-cross-platform-api-key-storage/reports/ac-verification.md`](../../../increments/0702-skill-studio-cross-platform-api-key-storage/reports/ac-verification.md)
- Brainstorm: [`.specweave/docs/brainstorms/2026-04-24-skill-studio-api-key-storage.md`](../../brainstorms/2026-04-24-skill-studio-api-key-storage.md)
- Key commits (vskill repo): `f832e7a` Phase 1 store + providers, `fc99ae6` UI rewrite, `22671dd` CLI + onboarding, `b323507` CLI wiring, `33de4df` server boot + OpenAI + migration + log capture, `bd4096f` 401 toast, `d7fb800` Phase 2 defect fixes (listKeys + DELETE handler), `9ea4462` e2e specs.

## Related ADRs

- [ADR-0002: Standardize Logger Dependency Injection Pattern](0002-standardize-logger-dependency-injection-pattern.md) — the store uses the same DI pattern for the injected logger
- [ADR-0006: Use Dependency Injection for Logger Testability](0006-use-dependency-injection-for-logger-testability.md) — extends to DI'd `fs` and `configDir` in `FileBackedStore` constructor for atomic-write + chmod tests
