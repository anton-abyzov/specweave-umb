---
increment: 0702-skill-studio-cross-platform-api-key-storage
title: Skill Studio Cross-Platform API Key Storage
type: feature
priority: P1
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio Cross-Platform API Key Storage

## Overview

Replace broken tiered in-memory / Darwin-Keychain storage with a single file-backed store at `~/.vskill/keys.env`, merged into `process.env` at boot. Add OpenAI as third provider. Add terminal-native first-run onboarding BEFORE the browser opens. Windows is first-class. `@napi-rs/keyring` backend deferred to a future increment.

**Brainstorm basis**: [.specweave/docs/brainstorms/2026-04-24-skill-studio-api-key-storage.md](../../docs/brainstorms/2026-04-24-skill-studio-api-key-storage.md) — approaches A (minimalist file) + D (terminal onboarding) selected from deep multi-lens ideation (five approaches evaluated across prior-art-survey, security, cross-platform, minimalism, UX lenses).

**Target repo**: `repositories/anton-abyzov/vskill/`

## Problem

Three compounding failures:

1. **Windows has no working persistence path.** "Browser storage (default)" is actually a Node-process in-memory `Map` — lost on every server restart. The label is a lie.
2. **macOS Keychain is Darwin-only.** Shells out to the `security` CLI — no equivalent on Linux/Windows, so 2/3 of the dev audience has no opt-in tier.
3. **Saved keys never reach `createLlmClient`.** The eval pipeline reads `process.env.ANTHROPIC_API_KEY` directly (`src/eval/llm.ts:165`) and ignores the settings-store. Users save a key, restart, and the eval still fails.

Plus: **OpenAI is not supported at all.**

## Goals

- One credential-persistence strategy that works first-class on macOS, Linux, **and Windows**
- Keys actually reach `createLlmClient` (via `process.env` merge at boot)
- Support Anthropic + OpenRouter + **OpenAI** (new)
- **Honest labels** — show the literal storage path, drop tier radio
- No native module dependencies (defer `@napi-rs/keyring` to follow-up)

## Non-Goals (explicitly deferred)

- **Encryption at rest** via OS vaults. Today's threat model is "solo dev, local tool, user-home ACLs"; plaintext with `0600` matches `aws`/`kubectl`/`supabase`-fallback precedent. Deferred to a follow-up increment behind a feature flag.
- **Multiple profiles per provider** (work/personal/billing pools). Data-model namespace reserved, not wired.
- **Cloud/remote key sync.** Users export env vars from their own secrets manager.
- **`--ephemeral` session flag.** Noted for future.

## User Stories

### US-001: Windows/Linux developer persists a key across restarts (P1)
**Project**: vskill

**As a** developer on Windows or Linux running `vskill studio` locally
**I want** my API key to persist across server restarts
**So that** I don't have to re-paste it every time I open Skill Studio

**Acceptance Criteria**:
- [x] **AC-US1-01**: Setting an API key via the Settings modal persists across `vskill studio` restart on macOS, Linux, and Windows (integration test with temp `VSKILL_CONFIG_DIR`)
- [x] **AC-US1-02**: An existing `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `OPENROUTER_API_KEY` env var ALWAYS wins over a stored key (power-user escape hatch — real env vars are NEVER overwritten by the merge)
- [x] **AC-US1-03**: On POSIX platforms, the keys file has mode `0600` after write (explicit `fs.chmod` after atomic write, verified in Linux CI)
- [x] **AC-US1-04**: A malformed `keys.env` (bad line, BOM, stray whitespace) does NOT crash the server — the parser skips malformed lines with a warning and continues with whatever parsed cleanly
- [x] **AC-US1-05**: `VSKILL_CONFIG_DIR` env var overrides the default location (enables hermetic tests and CI)

---

### US-002: First-time developer reaches "run an eval" in under 60 seconds (P1)
**Project**: vskill

**As a** developer running `vskill studio` for the first time with no API keys configured
**I want** the tool to guide me to a working state immediately
**So that** I can run my first eval without reading docs

**Acceptance Criteria**:
- [x] **AC-US2-01**: First-run `vskill studio` with no stored key AND no env var presents a terminal prompt BEFORE opening the browser, with three options: `[1] paste Anthropic key (masked stdin)` / `[2] use current Claude CLI session` / `[3] open browser to configure`
- [x] **AC-US2-02**: Choosing "use Claude CLI session" sets `VSKILL_EVAL_PROVIDER=claude-cli` for this session and opens the browser — no key needed
- [x] **AC-US2-03**: Choosing "paste key" uses masked stdin (characters not echoed), validates the provider prefix (`sk-ant-` for Anthropic), and persists before opening the browser
- [x] **AC-US2-04**: If ANY of the three provider env vars is already set, the first-run prompt is skipped silently (don't nag power users)
- [x] **AC-US2-05**: If a 401 is returned by any provider mid-session, the UI surfaces a dismissible toast linking to Settings (`Cmd+,`) with copy: "Your [provider] key may be revoked or expired. Update it in Settings."

---

### US-003: Scriptable CLI for key management (P2)
**Project**: vskill

**As a** developer automating setup across machines or a dotfiles user
**I want** a scriptable CLI to manage keys without the browser UI
**So that** I can provision vskill on a new laptop or CI with one shell script

**Acceptance Criteria**:
- [x] **AC-US3-01**: `vskill keys set <provider>` prompts for a masked value on stdin, and also accepts piped stdin: `echo "$KEY" | vskill keys set anthropic`
- [x] **AC-US3-02**: `vskill keys list` prints a table of providers with stored/not-stored status and `updatedAt` — NEVER prints the key, only `****<last-4>`
- [x] **AC-US3-03**: `vskill keys remove <provider>` removes the key and is idempotent (no error if not present)
- [x] **AC-US3-04**: `vskill keys path` prints the absolute path to the keys file
- [x] **AC-US3-05**: All four subcommands work on macOS, Linux, and Windows (cross-platform matrix in CI)

---

### US-004: OpenAI as third provider (P1)
**Project**: vskill

**As a** developer who uses OpenAI models for evals
**I want** OpenAI to be a first-class provider alongside Anthropic and OpenRouter
**So that** I don't have to juggle env vars or switch tools

**Acceptance Criteria**:
- [x] **AC-US4-01**: OpenAI appears in the Settings modal provider list with key-issuance URL `https://platform.openai.com/api-keys` and key prefix `sk-`
- [x] **AC-US4-02**: OpenAI appears in the provider detection API response (`detectAvailableProviders()` in `api-routes.ts`) with a model list — available when `OPENAI_API_KEY` is set OR a key is stored
- [x] **AC-US4-03**: An OpenAI client is wired in `src/eval/llm.ts` (`createOpenAIClient`) that reads `process.env.OPENAI_API_KEY`, same pattern as the Anthropic client
- [x] **AC-US4-04**: Provider list in UI + detection API + CLI all derive from a SINGLE source-of-truth constant (no triple maintenance burden)

---

### US-005: Honest UI labels — no fake tiers (P1)
**Project**: vskill

**As a** security-conscious developer reading the Settings modal
**I want** the UI to tell me the literal truth about where my key lives
**So that** I can make an informed decision about whether to trust this tool with my key

**Acceptance Criteria**:
- [x] **AC-US5-01**: The Settings modal REMOVES the "Browser storage" / "macOS Keychain" tier radio entirely
- [x] **AC-US5-02**: The Settings modal shows the literal storage path: "Keys stored at `<absolute-path>` (protected by file permissions)"
- [x] **AC-US5-03**: The Settings modal surfaces a "Copy path" button that copies the absolute keys.env path to clipboard
- [x] **AC-US5-04**: No reference to "tier", "keychain", or "browser storage" remains anywhere in UI strings (verified by grep in test)

---

### US-006: Migration from the old Darwin Keychain tier (P2)
**Project**: vskill

**As an** existing vskill user on macOS who stored keys via the old tier
**I want** my keys imported automatically with no data loss
**So that** upgrading vskill doesn't force me to re-enter keys

**Acceptance Criteria**:
- [x] **AC-US6-01**: On first boot of the new version, the server detects old `vskill-anthropic` / `vskill-openrouter` entries in the macOS Keychain (via `security find-generic-password`) and offers one-click import via a UI banner
- [x] **AC-US6-02**: After import, old Keychain entries are NOT deleted immediately — they remain for a 30-day grace period
- [x] **AC-US6-03**: Migration is idempotent — rerunning it does not duplicate, corrupt, or re-prompt
- [x] **AC-US6-04**: Migration works if only one of the two old entries exists (partial import is fine)
- [x] **AC-US6-05**: On non-Darwin platforms, migration is a no-op (silently skipped)

---

### US-007: Keys never leak to logs or stdout (P1)
**Project**: vskill

**As a** developer pair-programming or screen-sharing while using Skill Studio
**I want** strong guarantees that my raw API key never appears in any log, error, toast, URL, or stdout
**So that** I don't leak credentials in recordings, support tickets, or CI output

**Acceptance Criteria**:
- [x] **AC-US7-01**: No raw key appears in any log line, error, toast, network URL, or stdout — only the redacted form `****<last-4>` via `redactKey()` is ever emitted (verified by unit test that intercepts all logger calls for an injected key containing a known unique substring)
- [x] **AC-US7-02**: When `fs.rename` fails during atomic write, the error handler uses `redactKey()` exclusively — the raw key is NEVER embedded in the exception message (verified via test with injected failing `fs.rename`)
- [x] **AC-US7-03**: The browser paste flow never stores the raw key in React component state across a render boundary — POST to `/api/settings/keys` happens synchronously with input cleared immediately after

## Functional Requirements

### FR-001: File-backed credential store
Single file at `~/.vskill/keys.env` (override: `VSKILL_CONFIG_DIR`). KEY=VALUE dotenv format. Atomic write via temp-file + rename. `chmod 0600` on POSIX after write. Lenient parser (skip bad lines with warning).

### FR-002: Boot-time env merge
On server start (`eval-server.ts`), BEFORE any provider module import, read `keys.env` and merge MISSING provider env vars into `process.env`. Real env vars always win. After merge, the in-memory key `Map` is cleared to shrink plaintext dwell time.

### FR-003: Three-provider support
Anthropic + OpenRouter + OpenAI. Single `PROVIDERS` constant drives UI dropdown, detection API, and CLI validation.

### FR-004: Terminal-native first-run prompt
Detect "cold boot with no credentials" at `vskill studio` entry. Present 3-option prompt via masked stdin BEFORE invoking `openBrowser()`. Skip silently if any provider env var is set.

### FR-005: `vskill keys` CLI subcommand
`set | list | remove | path`, all POSIX+Windows compatible, sharing the same `FileBackedStore` as the server.

### FR-006: Honest Settings modal
Drop tier radio. Show literal storage path in footer. Add OpenAI row. Add "Copy path" button.

### FR-007: 401 toast
When any provider returns 401 mid-session, surface a dismissible toast linking to Settings (`Cmd+,`).

### FR-008: One-shot Darwin migration
On Darwin first-boot of new version, check for old `vskill-<provider>` Keychain entries. On user accept, read → write to file → mark migrated in state. Old entries remain for 30 days.

## Success Criteria

- **Functional**: All 33 ACs pass on macOS, Linux, and Windows CI matrix
- **Performance**: Boot-time file read + merge adds <50ms on cold cache
- **Code size**: Net LOC reduction in `settings-store.ts` (~150 LOC deleted from tier + Keychain bridge)
- **UX**: Time from fresh `npm install -g vskill` to "first eval runs" <60s in first-run-integration test
- **Security**: Zero raw-key occurrences in a full-pipeline log-capture test with a known-unique injected key substring

## Out of Scope

- `@napi-rs/keyring` OS-vault backend (future increment, feature-flagged)
- Per-provider profiles (namespace reserved, not wired)
- Cloud/remote key sync
- `--ephemeral` flag

## Dependencies

- `env-paths` npm package (pure JS, zero native deps)
- Node `fs` / `os` / `path` / `readline` stdlib
- Existing `redactKey()` utility (retained and expanded)
- Existing Darwin `security` CLI (for migration only — not used in new store)
