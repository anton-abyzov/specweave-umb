# Implementation Plan: Skill Studio Cross-Platform API Key Storage

## Overview

Replace the current tiered settings-store (`browser` in-memory + `keychain` Darwin-only) with a single `FileBackedStore` persisting to `~/.vskill/keys.env`. Wire a boot-time env merge into `eval-server.ts` so stored keys reach `createLlmClient`. Add OpenAI as a first-class provider. Add a terminal-native first-run onboarding prompt before the browser opens. Provide a `vskill keys` CLI subcommand. Migrate existing Darwin Keychain users via a one-shot UI banner with a 30-day grace period.

No native module dependencies. Pure Node stdlib + `env-paths` (pure JS).

## Architecture

### Components

- **`FileBackedStore`** (`src/eval-server/settings-store.ts`, rewritten) — read/write `keys.env`, atomic writes, `0600` on POSIX, lenient parser, injectable logger + `fs` for tests. Public API: `saveKey`, `readKey`, `hasKey`, `removeKey`, `listKeys`, `redactKey`, `getKeysFilePath`.
- **`mergeStoredKeysIntoEnv(store)`** (new, same module) — called ONCE at server boot BEFORE any provider module import. Iterates providers, writes `process.env.X_API_KEY = store.read(provider)` ONLY if the env var is unset. Clears in-memory `Map` after merge.
- **`PROVIDERS` constant** (new, `src/eval-server/providers.ts`) — single source of truth: `{ id, envVarName, keyPrefix, keyIssuanceUrl, label }[]`. Consumed by UI dropdown, detection API, CLI, and strings.
- **`createOpenAIClient`** (`src/eval/llm.ts`) — new provider client mirroring `createAnthropicClient`; reads `process.env.OPENAI_API_KEY`.
- **`vskill keys` CLI** (`src/cli/keys-command.ts`, new) — subcommand dispatcher for `set | list | remove | path`. Shares `FileBackedStore` with the server.
- **`firstRunOnboarding(store)`** (`src/cli/first-run.ts`, new) — called from `vskill studio` entry. Detects "no creds" state. Masked-stdin prompt with 3 options. Skipped if any provider env var is set.
- **`DarwinKeychainMigrator`** (`src/eval-server/darwin-migrator.ts`, new) — one-shot `security find-generic-password` reader. Non-Darwin no-op. Writes migration state to `~/.vskill/.migrated-from-keychain.json`.
- **SettingsModal** (`src/eval-ui/src/components/SettingsModal.tsx`, rewritten) — drops tier radio, adds OpenAI row, shows literal storage path, adds "Copy path" button, adds 401-toast handler at router level.

### Data Model

**`keys.env` file format** (KEY=VALUE dotenv):
```
# vskill credentials — do not commit. Managed by `vskill keys` or Skill Studio Settings.
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...
OPENROUTER_API_KEY=sk-or-v1-...
```

**`KeyMetadata`** (unchanged shape, `tier` field removed):
```ts
interface KeyMetadata {
  stored: boolean;
  updatedAt: string | null;
}

interface ListKeysResponse {
  anthropic: KeyMetadata;
  openai: KeyMetadata;
  openrouter: KeyMetadata;
}
```

**Migration state** (`~/.vskill/.migrated-from-keychain.json`):
```json
{
  "version": 1,
  "migratedAt": "2026-04-24T16:00:00Z",
  "providers": ["anthropic", "openrouter"],
  "keychainEntriesRetainUntil": "2026-05-24T16:00:00Z"
}
```

### API Contracts

**Existing endpoints updated** (no route changes, just semantics):
- `POST /api/settings/keys` — body `{ provider, key }`; no `tier` field accepted; writes to file.
- `GET /api/settings/keys` — returns `ListKeysResponse` with new `openai` field; no `tier` field.
- `DELETE /api/settings/keys/:provider` — unchanged.
- `GET /api/settings/storage-path` (NEW) — returns `{ path: "/Users/.../.vskill/keys.env" }` for UI footer.

**New endpoint:**
- `GET /api/settings/legacy-keychain-available` (Darwin-only) — returns `{ available: boolean, providers: string[] }`; drives the migration banner.
- `POST /api/settings/migrate-legacy-keychain` (Darwin-only) — performs one-shot read of old Keychain entries, writes to file, returns `{ migrated: string[] }`.

## Technology Stack

- **Language/Framework**: TypeScript (ESM, existing vskill stack)
- **Libraries**:
  - `env-paths` (new dep, pure JS, zero transitive deps) — cross-platform config-dir resolution (reference for default; actual path is `~/.vskill/keys.env` to match Claude Code convention; `env-paths` used only as documented alternative)
  - Existing: `@anthropic-ai/sdk`, `openai` (new for OpenAI client), `ink` or raw `readline` for masked stdin
  - No native deps — `@napi-rs/keyring` deliberately NOT added
- **Tools**: Existing Vitest + Playwright + TypeScript configured on vskill repo

### Architecture Decisions (new ADR)

**ADR-proposed**: `.specweave/docs/internal/architecture/adr/ADR-00NN-vskill-credential-storage.md` (increment author to assign next ADR number during Phase 1). Decisions:

1. **File-backed over OS-vault backend** — Plaintext at `~/.vskill/keys.env` with `0600` matches `aws`/`kubectl`/`supabase`-fallback precedent. Threat model (solo dev, local tool, user-home ACLs) does not justify node-gyp/prebuilt-binary overhead of `@napi-rs/keyring`. Revisit if user feedback demands encryption at rest.
2. **`~/.vskill/` over `envPaths("vskill").config`** — Matches Claude Code's `~/.claude/` convention (our audience's mental model). Short, memorable, scriptable. XDG purists can set `VSKILL_CONFIG_DIR`.
3. **Boot-time env merge** — Delivers stored keys to `createLlmClient` without changing any provider-client code. Real env vars always win (merge order: `process.env.X ??= storedValue`). In-memory map cleared after merge to shrink plaintext dwell window.
4. **Single `PROVIDERS` constant** — Eliminates the current dual-list bug (UI lists Anthropic+OpenRouter but detection logic lives in a separate switch). Adding OpenAI touches one place.
5. **Terminal-first onboarding** — Browser paste exposes keys to clipboard, screen-share, and React DevTools snapshots. Masked stdin prompt mitigates all three on first run. Browser modal retained for editing.
6. **30-day Keychain grace period** — Don't delete old entries on migration. Read-before-delete with observability log on every boot that reads them lets users rollback without data loss.

## Implementation Phases

### Phase 1: Foundation (Tests + `FileBackedStore`)
- Write RED tests for `FileBackedStore` (save, read, list, remove, atomic-write, chmod 0600, lenient parser, `VSKILL_CONFIG_DIR` override, redacted logging on failures)
- Implement `FileBackedStore` (GREEN)
- Write RED tests for `mergeStoredKeysIntoEnv` (merges missing keys, preserves real env vars, clears map)
- Implement merge function (GREEN)
- Add `PROVIDERS` constant + replace scattered lists
- Delete old tier state, Darwin Keychain bridge, `UnsupportedTierError` (paired with RED tests asserting symbols are gone)

### Phase 2: Server Wiring + OpenAI
- Wire `mergeStoredKeysIntoEnv` into `eval-server.ts` boot (BEFORE provider imports)
- Add boot-ordering integration test (start server, verify `process.env.X_API_KEY` set before first HTTP request)
- Add `createOpenAIClient` to `src/eval/llm.ts` + unit tests
- Add OpenAI to `detectAvailableProviders` via `PROVIDERS` iteration
- Add `GET /api/settings/storage-path` endpoint

### Phase 3: CLI Subcommand
- `vskill keys set | list | remove | path` via new subcommand dispatcher
- Masked-stdin helper (retain + export for first-run onboarding reuse)
- Cross-platform CI matrix (macOS / Ubuntu / Windows runners)

### Phase 4: First-Run Onboarding
- `firstRunOnboarding(store)` function + unit tests (mocked stdin)
- Wire into `vskill studio` entry BEFORE `openBrowser()`
- Skip-silently behavior when any provider env var is set

### Phase 5: UI Rewrite
- Update `SettingsModal.tsx`: drop tier radio, add OpenAI row, add path footer, add "Copy path" button
- Update `useCredentialStorage` hook: remove `StorageTier` type
- Add global 401-toast handler (fetch wrapper or axios interceptor depending on current pattern)
- Grep-based test: no "tier" / "keychain" / "browser storage" strings remain

### Phase 6: Darwin Migration
- `DarwinKeychainMigrator` module + tests (Darwin path + non-Darwin no-op)
- `GET /api/settings/legacy-keychain-available` endpoint + `POST .../migrate-legacy-keychain`
- Migration banner UI component + idempotency tests
- Observability log on each boot that reads a retained Keychain entry (redacted)

### Phase 7: Closure
- Full Linux+macOS+Windows CI pass
- Log-capture security test with unique injected key substring
- ADR finalized and linked from plan.md
- Update existing `src/eval-ui/src/hooks/useCredentialStorage.ts` tests to match new contract

## Testing Strategy

- **TDD (strict)** — every new module has a RED test before GREEN implementation
- **Deletion tests** — each deleted symbol/code path paired with an assertion that it's gone (e.g., `expect((settingsStore as any).setTier).toBeUndefined()`)
- **Unit**: Vitest with injectable logger + `fs` mocks (pattern exists in current `settings-store.test.ts`)
- **Integration**: real temp `VSKILL_CONFIG_DIR` dir, real file I/O, real `chmod` verification
- **Cross-platform CI matrix**: macOS 13+, Ubuntu 22.04+, Windows Server 2022 — for at least the `vskill keys` CLI and `FileBackedStore` integration tests
- **E2E (Playwright)**: Settings modal round-trip (save → restart-server-in-test → read); migration banner flow on Darwin; 401-toast flow with mocked 401 response
- **Security log-capture**: inject a key containing a known unique substring, exercise save/read/error/toast/fetch paths, assert the substring never appears in any sink output
- **Coverage targets** (from config): unit 60%, integration 90%, e2e 100% of AC scenarios

## Technical Challenges

### Challenge 1: Boot-ordering — merge MUST happen before provider module imports
**Solution**: Move the merge call to the very top of `eval-server.ts` module body, before any other imports that might transitively touch `process.env.*_API_KEY`. Use a dedicated `boot-preflight.ts` module imported first.
**Risk**: Future contributor reorders imports → merge runs late → stored keys look "broken" again. **Mitigation**: boot-ordering integration test that starts the server with only a stored key (no env var) and asserts a first HTTP request succeeds.

### Challenge 2: Atomic-write failure paths leak keys
**Solution**: Centralize all key-accepting error paths through a single wrapper that calls `redactKey()` before passing to the logger. Typed as `(rawKey: string, err: Error) => void`; impossible to accidentally log the raw key.
**Risk**: A new `throw new Error("failed to save " + key)` slips into the PR. **Mitigation**: log-capture security test + ESLint rule (or a Vitest custom matcher) that forbids raw-key substrings in log sinks.

### Challenge 3: Windows CI matrix slow + flaky
**Solution**: Scope the Windows matrix to just the `vskill keys` CLI test + `FileBackedStore` integration test (not the full e2e suite). macOS + Ubuntu run the full suite.
**Risk**: Regression in Windows-only code path. **Mitigation**: `FileBackedStore` has zero platform-conditional code (except chmod), so macOS/Ubuntu coverage transfers.

### Challenge 4: Users hand-edit `keys.env` and malform it
**Solution**: Lenient parser — per-line try/catch, skip malformed lines with a single aggregated warning (not per-line spam). Never throw from parse.
**Risk**: User thinks their key worked but parser silently dropped it. **Mitigation**: warning includes line number and a redacted preview so user can diagnose.

### Challenge 5: Migration race — user opens Settings and edits while migration banner is showing
**Solution**: Migration banner shows BEFORE rendering the provider rows. User acknowledges (Import / Skip) first. Edits unlocked after.
**Risk**: Accepting migration overwrites a key the user just typed. **Mitigation**: read-modify-write with "file has content → don't overwrite, prompt merge" fallback (rare path; logged).

## References

- Brainstorm: `.specweave/docs/brainstorms/2026-04-24-skill-studio-api-key-storage.md` — 5 approaches evaluated, A+D selected
- Interview state: `.specweave/state/interview-0702-skill-studio-cross-platform-api-key-storage.json`
- Current broken code:
  - `repositories/anton-abyzov/vskill/src/eval-server/settings-store.ts`
  - `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts:840-901`
  - `repositories/anton-abyzov/vskill/src/eval/llm.ts:165`
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SettingsModal.tsx`
