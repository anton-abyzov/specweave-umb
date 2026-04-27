---
increment: 0796-plugin-update-banner-notifier
title: Session-Start Banner Notifier for Plugin/Skill Updates
type: feature
priority: P2
status: completed
created: 2026-04-27T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Session-Start Banner Notifier for Plugin/Skill Updates

## Overview

Surface plugin and skill update signals proactively to SpecWeave users at the start of each Claude Code session via a `UserPromptSubmit` hook. The hook calls `specweave doctor --quick --quiet --json`, parses the result for "Plugin Currency" / "Skill Currency" findings, and prints a one-line stderr banner only when updates are available — throttled to once per 24h to avoid spam.

This is the Phase 2 follow-up to **0794-plugin-update-visibility-foundation** (which added the doctor checkers). 0794 made the signals reachable on demand; 0796 makes them visible without the user having to ask.

**Why this matters**: Today, users only see plugin/skill update warnings if they manually run `specweave doctor`. Most don't. Users on stale plugin versions miss security fixes and feature updates indefinitely.

**Design constraints** (from 0794 brainstorm + 0796 architecture interview):
- Hook fires on every `UserPromptSubmit` — must short-circuit cheaply when throttled (<10ms)
- Hook errors MUST NEVER block the user's prompt — silent `process.exit(0)` on any exception
- Banner output goes to stderr (preserves stdout for tool I/O)
- Opt-out via single config flag, not removal
- Reuses 0794 doctor checkers — no new currency-detection logic

## User Stories

### US-001: Session-Start Update Banner (P1)
**Project**: specweave

**As a** SpecWeave user starting a Claude Code session
**I want** to see a one-line banner if my plugins or skills have updates available
**So that** I never silently miss a security fix or feature update

**Acceptance Criteria**:
- [x] **AC-US1-01**: After running `specweave init` (or `specweave init --upgrade` on an existing project), `~/.claude/settings.json` contains a `UserPromptSubmit` hook entry pointing to `plugins/specweave/hooks/user-prompt-submit/check-updates.js`
- [x] **AC-US1-02**: On first prompt of a session (no throttle file yet), the hook invokes `specweave doctor --quick --quiet --json` and parses the result
- [x] **AC-US1-03**: When doctor reports `warn` or `fail` in either "Plugin Currency" or "Skill Currency" categories, the hook prints a one-line banner to **stderr** in the format: `[specweave] N plugin update(s) and M skill update(s) available — run \`specweave refresh-plugins\` and \`vskill update\``
- [x] **AC-US1-04**: When N=0, banner reads `M skill update(s) available — run \`vskill update\``. When M=0, banner reads `N plugin update(s) available — run \`specweave refresh-plugins\``. When both 0, no banner is printed
- [x] **AC-US1-05**: Banner is printed to stderr, never stdout, so tool output is unaffected
- [x] **AC-US1-06**: Hook completes in <800ms in the cold path (doctor invoked) and <10ms in the throttled path
- [x] **AC-US1-07**: Hook is registered for the `specweave` plugin only — does NOT pollute Claude Code settings for projects without `.specweave/` initialized

**Test Plan**:
- Given a fresh project with `.specweave/` initialized AND `~/.claude/plugins/installed_plugins.json` containing one outdated plugin (e.g., `specweave@2.0.0` while marketplace has `2.1.0`)
- When the user submits their first prompt
- Then stderr contains the line `[specweave] 1 plugin update(s) available — run \`specweave refresh-plugins\``
- And stdout is unaffected
- And `.specweave/state/banner-last-check.json` is created with `hadUpdates: true`

---

### US-002: 24-Hour Throttle (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** the banner throttled to once per 24 hours
**So that** it doesn't spam me on every prompt within the same workday

**Acceptance Criteria**:
- [x] **AC-US2-01**: After a successful doctor run with `hadUpdates: false`, the hook writes `.specweave/state/banner-last-check.json` containing `{ "lastCheck": "<ISO>", "hadUpdates": false, "expiresAt": "<ISO + 24h>" }`
- [x] **AC-US2-02**: On subsequent prompts within 24h of a `hadUpdates: false` check, the hook reads the throttle file, sees `expiresAt > now`, and exits immediately without invoking doctor
- [x] **AC-US2-03**: When `hadUpdates: true`, the throttle is still set but `expiresAt` is shorter (default: 4 hours) so the user gets re-prompted later in the same workday if they haven't acted on it yet
- [x] **AC-US2-04**: After `expiresAt < now`, the next prompt re-runs doctor and refreshes the throttle file
- [x] **AC-US2-05**: The throttle file uses **atomic write semantics** (write to `.tmp`, then rename) so concurrent agents don't corrupt it
- [x] **AC-US2-06**: A corrupted or unparseable throttle file is treated as "never checked" — hook re-runs doctor and overwrites the file, no error surfaced to user
- [x] **AC-US2-07**: Throttle path round-trip (read file, parse JSON, compare timestamps, exit) completes in <10ms on a typical local SSD

**Test Plan**:
- Given a throttle file written 1 hour ago with `hadUpdates: false` and `expiresAt: now + 23h`
- When the hook fires
- Then doctor is NOT invoked (verified via spy/mock)
- And the hook returns within 10ms
- And the throttle file is unchanged

---

### US-003: Opt-Out via Config (P2)
**Project**: specweave

**As a** SpecWeave user who finds the banner annoying or who runs in a CI-like context
**I want** to disable the banner via a single config flag
**So that** I retain control without uninstalling the plugin

**Acceptance Criteria**:
- [x] **AC-US3-01**: `.specweave/config.json` schema includes a new optional path `hooks.banner.disabled` (boolean, default `false`)
- [x] **AC-US3-02**: Running `specweave config set hooks.banner.disabled true` writes the value to `.specweave/config.json` and prints a confirmation
- [x] **AC-US3-03**: When `hooks.banner.disabled === true`, the hook exits immediately without reading the throttle file or invoking doctor (path returns in <5ms)
- [x] **AC-US3-04**: Re-enabling via `specweave config set hooks.banner.disabled false` (or removing the key) restores normal behavior on the next prompt
- [x] **AC-US3-05**: The opt-out is per-project (lives in `.specweave/config.json`), not global — different projects can have different settings
- [x] **AC-US3-06**: Config schema validation rejects non-boolean values for `hooks.banner.disabled` with a clear error message

**Test Plan**:
- Given `.specweave/config.json` with `hooks.banner.disabled: true`
- When the hook fires
- Then doctor is NOT invoked
- And no banner is printed
- And no throttle file write occurs
- And the hook exits with code 0 in <5ms

---

### US-004: Robust Error Isolation (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the hook to handle every failure mode silently
**So that** a broken doctor command, network failure, or corrupted state never blocks a user's prompt

**Acceptance Criteria**:
- [x] **AC-US4-01**: All hook I/O (config read, throttle file read/write, doctor spawn, JSON parse) is wrapped in `try/catch` blocks that swallow errors and `process.exit(0)`
- [x] **AC-US4-02**: When doctor exits non-zero, the hook treats it as "no banner" (not "error to user") and continues silently
- [x] **AC-US4-03**: When doctor stdout is not valid JSON, the hook silently skips banner printing (does not throw)
- [x] **AC-US4-04**: When doctor takes longer than a 5-second timeout, the hook kills the child process and exits silently
- [x] **AC-US4-05**: Errors are logged best-effort to `.specweave/state/banner-error.log` (append-only, capped at 100KB via rotation) for postmortem debugging — but log write failures are themselves swallowed
- [x] **AC-US4-06**: When the user has no network connectivity AND doctor needs network for marketplace check, doctor must report "skipped" not "fail" — hook treats "skipped" as "no updates" (silent)
- [x] **AC-US4-07**: When `~/.claude/plugins/installed_plugins.json` is missing (user hasn't installed any plugins yet), hook exits silently — no banner, no error
- [x] **AC-US4-08**: When `.specweave/state/` directory doesn't exist, the hook creates it (with `mkdir -p` semantics) before writing the throttle file

**Test Plan**:
- Given `specweave doctor --quick --quiet --json` is replaced with a script that exits with code 1 and prints garbage to stdout
- When the hook fires
- Then no banner is printed
- And the hook exits with code 0
- And the user's prompt proceeds unaffected
- And `.specweave/state/banner-error.log` contains a single line capturing the failure

---

### US-005: Doctor Command Flag Support (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the doctor command to support `--quick`, `--quiet`, and `--json` flags
**So that** the banner hook can invoke it efficiently and parse output reliably

**Acceptance Criteria**:
- [x] **AC-US5-01**: `specweave doctor --quick` skips slow checkers (deep marketplace network probes, full skill registry validation) and runs only the fast currency checks (PluginCurrencyChecker, SkillCurrencyChecker, plus existing fast checks)
- [x] **AC-US5-02**: `specweave doctor --quiet` suppresses informational and `pass` lines on stdout, leaving only `warn` and `fail` results in the human-readable output (when not combined with `--json`)
- [x] **AC-US5-03**: `specweave doctor --json` emits a structured JSON document on stdout containing an array of check results, each with `{ category, name, status, message, details? }` — no human-formatted lines mixed in
- [x] **AC-US5-04**: Flags compose correctly: `--quick --quiet --json` produces JSON output of fast-check-only results with no extra logging on stdout
- [x] **AC-US5-05**: When the JSON schema is updated, a sample fixture is added to test data so the hook's parser is regression-tested against the contract
- [x] **AC-US5-06**: Existing `specweave doctor` (no flags) behavior is unchanged for backward compatibility — flags are purely additive

**Test Plan**:
- Given the SpecWeave CLI is built with the doctor command
- When `specweave doctor --quick --quiet --json` runs in a test fixture project with one outdated plugin
- Then stdout contains parseable JSON
- And the JSON includes a result with `category: "Plugin Currency", status: "warn"`
- And no human-formatted text appears on stdout
- And the command exits with code 0 (warnings don't fail the command)

## Functional Requirements

### FR-001: Hook Registration via specweave init
`specweave init` (and `specweave init --upgrade` for existing projects) writes a `UserPromptSubmit` hook entry to `~/.claude/settings.json`. The entry runs `node <plugin-root>/hooks/user-prompt-submit/check-updates.js` with the project working directory passed via env var (`SPECWEAVE_PROJECT_ROOT`). If the entry already exists from a prior install, init is idempotent — does not duplicate.

### FR-002: Throttle File Schema and Location
Path: `.specweave/state/banner-last-check.json`
Schema:
```json
{
  "lastCheck": "2026-04-27T14:32:00.000Z",
  "hadUpdates": false,
  "expiresAt": "2026-04-28T14:32:00.000Z"
}
```
Default cooldowns: 24h when `hadUpdates: false`, 4h when `hadUpdates: true` (so users who don't act get reminded within the same workday).

### FR-003: Banner Format Specification
Output goes to stderr, exactly one line, no leading/trailing whitespace beyond the newline:
- Both: `[specweave] N plugin update(s) and M skill update(s) available — run \`specweave refresh-plugins\` and \`vskill update\``
- Plugins only: `[specweave] N plugin update(s) available — run \`specweave refresh-plugins\``
- Skills only: `[specweave] M skill update(s) available — run \`vskill update\``

Pluralization: `1 plugin update` (no s on plugin), `2 plugin updates`. The `(s)` form in the spec is shorthand — the actual implementation chooses singular/plural based on count.

### FR-004: Config Schema Extension
Add to `src/core/config/schema.ts`:
```ts
hooks?: {
  banner?: {
    disabled?: boolean;  // default: false
  }
}
```
Validation: `disabled` must be boolean if present. Unknown keys under `hooks.banner` are tolerated for forward compatibility.

### FR-005: Error Log Rotation
`.specweave/state/banner-error.log` rotates when it exceeds 100KB: rename to `.banner-error.log.1`, start fresh. Only one rotation kept; older logs are discarded. Rotation logic itself is wrapped in try/catch — failures swallowed.

## Success Criteria

- **Visibility**: 100% of SpecWeave users with outdated plugins/skills see the banner within their first session post-upgrade (vs. ~5% who manually run doctor today)
- **Performance**: P95 hook latency in throttled path < 10ms; P95 cold-path latency < 800ms (measured on macOS SSD)
- **Reliability**: 0 user-prompt blockages caused by hook errors over a 30-day rollout window (verified via opt-in telemetry or absence of user reports)
- **Adoption**: <2% of users opt out via `hooks.banner.disabled` (signal that the banner is useful, not annoying)

## Out of Scope

- **Push notifications / SSE / persistent daemon**: CLI is short-lived, polling on `UserPromptSubmit` is the right transport. Deferred indefinitely.
- **Notifying about specweave CLI itself being outdated**: Already covered by `installation-health-checker` in 0794. This increment focuses on plugins + skills only.
- **Cross-marketplace conflict detection**: When two plugins from different marketplaces conflict, that's a separate Phase 3 concern.
- **Banner hooks for non-Claude-Code agents**: Cursor, Copilot, Aider, etc. don't have an equivalent `UserPromptSubmit` hook surface. They get no banner — same as today. A future increment may explore CLI wrapper-based banners.
- **Telemetry collection on banner display rate**: No phone-home. The success metrics are inferred from issue volume, not measured directly.
- **Auto-update functionality**: The banner tells the user what to run; it does NOT run `refresh-plugins` or `vskill update` on their behalf. That would violate the "never modify state without consent" principle.

## Dependencies

- **0794-plugin-update-visibility-foundation** (closed): provides `PluginCurrencyChecker` and `SkillCurrencyChecker` in `specweave doctor`. This increment depends on those checkers reporting accurate `warn`/`fail` for outdated installations.
- **`specweave doctor` command**: Must support `--quick`, `--quiet`, `--json` flags (verified during implementation; added if missing per US-005).
- **`vskill outdated --json`**: Already shipped. Used by `SkillCurrencyChecker` from 0794. No additional dependency from this increment.
- **Claude Code `UserPromptSubmit` hook system**: Stable API in `~/.claude/settings.json`. No special version requirement.
