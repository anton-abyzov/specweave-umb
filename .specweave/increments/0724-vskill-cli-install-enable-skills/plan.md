---
increment: 0724-vskill-cli-install-enable-skills
plan_version: 1
---

# Architecture Plan

## Tech Stack

- **Runtime**: Node.js ≥ 20 (per `package.json` engines).
- **Language**: TypeScript 5.7, strict mode, ESM (`"type": "module"`).
- **CLI framework**: Commander 14 (`src/index.ts` is the dispatcher; per-command handlers live in `src/commands/*.ts` and are dynamically imported).
- **Test stack**: Vitest 3 (`*.test.ts` co-located with source); existing patterns use `vi.mock` and `vi.hoisted` for ESM mocking.
- **Subprocess control**: `node:child_process` `execFileSync` (already wrapped in `src/utils/claude-plugin.ts` and `src/utils/resolve-binary.ts`).
- **No new dependencies** required — everything builds on existing modules. (`commander`, `node:fs`, `node:path`, `node:os`, `node:child_process` are already in.)

## Component Map

### New files

| Path | Role |
|---|---|
| `src/commands/enable.ts` | `vskill enable <name>` handler. Reads lockfile, resolves plugin id, calls `claudePluginInstall`, emits per-agent report. |
| `src/commands/disable.ts` | `vskill disable <name>` handler. Same shape as enable, calls `claudePluginUninstall`. |
| `src/commands/__tests__/enable.test.ts` | Unit tests for enable (mocked claude CLI, mocked lockfile). |
| `src/commands/__tests__/disable.test.ts` | Unit tests for disable. |
| `src/lib/skill-lifecycle.ts` | Shared logic: `resolvePluginId(skillName, lock)`, `classifyAgentSurface(agent)`, `buildPerAgentReport(skillName, scope, action)`. Pure functions, fully unit-tested. |
| `src/lib/__tests__/skill-lifecycle.test.ts` | Unit tests for the pure helpers. |
| `e2e/enable-disable.test.ts` | End-to-end Playwright/CLI test: scaffold a temp project, run `vskill install --no-enable foo` → `vskill enable foo` → `vskill disable foo` → assert `enabledPlugins` state + on-disk files at each step. |
| `.specweave/docs/internal/architecture/adr/ADR-0024-skill-enable-disable-via-claude-cli.md` | Records the decision to delegate every `enabledPlugins` mutation to `claude plugin install/uninstall` rather than touching `settings.json` directly. |

### Modified files

| Path | Change |
|---|---|
| `src/index.ts` | Register `enable` and `disable` Commander commands; add `--no-enable`, `--scope`, `--dry-run`, `--verbose` flags to `install`; add `--installed` flag to `list`. |
| `src/commands/add.ts` | Honour `--no-enable` flag (skip `claudePluginInstall` step); plug in per-agent reporter from `skill-lifecycle.ts`; rollback on plugin-install failure (AC-US1-05). |
| `src/commands/list.ts` | Add `--installed` branch that joins lockfile with `isPluginEnabled` for both scopes; emit table or JSON. |
| `src/commands/remove.ts` | Replace inline "Plugin uninstalled: …" log with the structured per-agent reporter from `skill-lifecycle.ts` (consistency, not behaviour change). |
| `src/commands/cleanup.ts` | Add `--dry-run` flag; emit reconciliation summary (US-007). |

### Reused files (no changes)

- `src/utils/claude-plugin.ts` — `claudePluginInstall`, `claudePluginUninstall`, `uninstallStalePlugins` (already covers everything we need).
- `src/settings/settings.ts` — `isPluginEnabled`, `listEnabledPlugins`, `purgeStalePlugins` (all read-only — perfect for the `list --installed` and `cleanup --dry-run` paths).
- `src/agents/agents-registry.ts` — `detectInstalledAgents`, `AGENTS_REGISTRY`, `AgentDefinition` (per-agent reporting).
- `src/lockfile/index.ts` — `readLockfile`, `writeLockfile`, `removeSkillFromLock` (already atomic).
- `src/utils/resolve-binary.ts` — `resolveCliBinary("claude")` (handles claude-not-installed errors).

## Data Model

No schema changes. The increment is entirely a new behaviour layer over the existing `vskill.lock` `SkillLockEntry` schema (`src/lockfile/types.ts`):

```ts
interface SkillLockEntry {
  version: string;
  sha: string;
  tier: string;
  installedAt: string;
  source: string;
  marketplace?: string;        // ← used to derive pluginId = `${name}@${marketplace}`
  pluginDir?: boolean;
  scope?: "user" | "project";
  installedPath?: string;
  files?: string[];
  pinnedVersion?: string;
}
```

Plugin id format remains the existing convention: `<skillName>@<marketplace>`. Resolution rule: if `marketplace` is missing, the skill is auto-discovered (no plugin entry to enable/disable — `n/a` in list output, no-op on enable/disable).

The single source of truth for "is this skill currently enabled" is `~/.claude/settings.json` and `<projectDir>/.claude/settings.json` — both queried via the existing `isPluginEnabled` helper.

## CLI Surface

| Command | Flags | Behaviour |
|---|---|---|
| `vskill install [source]` (existing) | `--no-enable`, `--scope user\|project`, `--dry-run` (new); existing `--global`, `--force`, `--agent`, `--copy`, `--select`, `--only-skills`, `-y` retained | Installs files + lockfile entry; if marketplace plugin AND not `--no-enable`, calls `claudePluginInstall` per scope. |
| `vskill enable <name>` (NEW) | `--scope user\|project` (default `user`), `--dry-run`, `--verbose` | Reads lockfile, derives `<name>@<marketplace>`, calls `claudePluginInstall`. Idempotent. Per-agent report. |
| `vskill disable <name>` (NEW) | `--scope user\|project` (default `user`), `--dry-run`, `--verbose` | Calls `claudePluginUninstall`. Lockfile and on-disk files untouched. Idempotent. |
| `vskill list` (existing) | `--installed` (new), existing `--agents`, `--json` | With `--installed`: table with `Skill | Version | Source | User Scope | Project Scope`. JSON output extends to `{enabledUser, enabledProject, autoDiscovered}`. |
| `vskill remove <name>` (existing) | unchanged | Refactored internally to use the structured per-agent reporter (AC-US5-01 cosmetic alignment). |
| `vskill cleanup` (existing) | `--dry-run` (new) | Lists stale plugin ids with scope before running uninstalls; prints reconciliation summary. |

## ADRs to write

1. **ADR-0024 — Delegate every `enabledPlugins` mutation to the `claude` CLI** (recording why vskill never writes `settings.json` directly even though that would be one fewer subprocess; references the read-only invariant in `src/settings/settings.ts`).

No further ADRs needed — the rest of the increment is straightforward CRUD over an already-decided data model.

## Risks and mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | `claude plugin install` semantics drift in a future Claude Code release (e.g., requires `--force` or new flag), breaking idempotency | Medium | High | Pin the subprocess invocation in a single helper (`claudePluginInstall` already exists). Add an integration test that asserts the exact argv passed. Surface drift via clear error in `--verbose` mode. |
| R2 | User has the skill enabled at user scope AND project scope, runs `vskill disable --scope project` and is confused that it still loads | Medium | Medium | Per-agent report explicitly names every scope state. `vskill list --installed` makes both scopes visible. Disable output ends with `Hint: still enabled in user scope. Run vskill disable --scope user to fully disable.` when the other scope is true. |
| R3 | Rollback in AC-US1-05 leaves orphan files if file rm fails after `claudePluginInstall` throws | Low | Medium | Wrap rollback in try/catch and log specifically; emit a `vskill cleanup` hint at the end of the failure message. |
| R4 | Test flakiness from real `claude` CLI in CI | Medium | Low | All tests mock `execFileSync` via `vi.mock("node:child_process")`. E2E test uses a stub `claude` binary on PATH. |

## Test Strategy

- **Unit (Vitest)**: every new pure function in `src/lib/skill-lifecycle.ts` has 100% line coverage. `enable.ts` and `disable.ts` mock `child_process` and `lockfile/index.ts` to assert exact subprocess argv per scope, idempotency branches, missing-lockfile error paths, dry-run no-op, and rollback paths.
- **Integration (Vitest)**: temp-directory test that writes a real `vskill.lock`, stubs `claude` to a JS shim, and asserts that `enable` → `disable` round-trips `~/.claude/settings.json` byte-equally (AC-US6-03).
- **E2E (Playwright/CLI)**: `e2e/enable-disable.test.ts` — full-process spawn, exit codes, stdout snapshots, settings.json deep-equality.
- **Coverage gate**: ≥ 90% for the new files (matches the `coverage_target` in metadata).
- **Mocking pattern**: reuse the existing `vi.hoisted({ ... })` + `vi.mock("node:child_process", ...)` pattern from `add.test.ts` and `remove.test.ts`.
