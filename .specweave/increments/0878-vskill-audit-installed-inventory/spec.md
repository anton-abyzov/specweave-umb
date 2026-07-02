---
increment: 0878-vskill-audit-installed-inventory
title: 'Free vskill audit --installed: machine-wide skill inventory + scan'
type: feature
priority: P1
status: completed
created: 2026-07-02T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Free `vskill audit --installed` — machine-wide skill inventory + scan

## Overview

GTM context: the free audit is the #1 cold-outreach wedge ("Snyk found prompt injection in 36% of public skills — do you know what's installed on your engineers' machines?"). The findings report doubles as the artifact delivered in free 30-min design-partner audits. No account required; the pattern tier works fully offline.

`vskill audit` today scans *project files* (23 `AUDIT_PATTERNS` via `runAuditScan`). There is no way to answer "what AI-agent skills are installed on this machine, and are any of them dangerous?" — across Claude Code skills/plugins/marketplaces, Cursor skills, and the rest of the 53-agent registry. Unmanaged skills (manually copied, absent from `vskill.lock`) are invisible today and are exactly what the wedge highlights. This increment adds an `--installed` mode that inventories, dedupes, scans, and reports — reusing the existing scan stack (no new scanners) and leaving the default project-audit path byte-for-byte unchanged.

## User Stories

### US-001: Inventory installed skills across all agents (P1)
**Project**: vskill

**As a** platform engineer (or the founder running a sales audit)
**I want** `vskill audit --installed` to enumerate every skill installed on this machine across all detected agents
**So that** I get a complete inventory including manually-copied skills nobody tracks

**Acceptance Criteria**:
- [x] **AC-US1-01**: For every agent from `detectInstalledAgents()`, both global and project skills dirs (via `resolveAgentSkillsDir`) are walked; a skill = a directory containing `SKILL.md`. Missing dirs contribute 0 skills without error.
- [x] **AC-US1-02**: Claude Code plugin cache (`~/.claude/plugins/cache/{marketplace}/{plugin}/{version}`) is inventoried for ENABLED plugins only (per `listEnabledPlugins` user+project scopes), highest version per plugin; skills found at `{version}/skills/<name>/SKILL.md` or `{version}/SKILL.md`. Cached-but-disabled versions are counted (`cachedButDisabled`) but not deep-scanned.
- [x] **AC-US1-03**: Identical skill content installed to N agents/scopes is deduped by content hash (`computeSha` over the file bundle) into ONE result row carrying all N locations; same name with different content stays separate rows (drift signal).
- [x] **AC-US1-04**: Each skill is marked `managed: true/false` by cross-referencing `readLockfile()` (vskill.lock) and `readSkillsShLock()` (.skill-lock.json); the summary exposes `unmanagedCount`.
- [x] **AC-US1-05**: Walk is safe: symlinked directories are not traversed, recursion depth capped, unreadable dirs/files skipped without crashing, only known text extensions read, per-file (100 KB) and per-skill-bundle (512 KB) size caps, `node_modules`/`.git`/`dist` skipped.

---

### US-002: Flag every inventoried skill via the existing scan stack (P1)
**Project**: vskill

**As a** security-conscious engineering lead
**I want** each inventoried skill flagged by the same scan stack used at install time
**So that** the report is trustworthy and works without an account, even offline

**Acceptance Criteria**:
- [x] **AC-US2-01**: Each unique skill bundle (SKILL.md + sibling text files, concatenated with path delimiters) is scanned with `runTier1Scan` (53 `SCAN_PATTERNS`); findings map to skill-centric findings (patternId, severity, file, line, context). Works fully offline.
- [x] **AC-US2-02**: `checkBlocklist(name, contentHash)` runs per skill using the existing 1-hour cache with stale fallback; a blocklist hit forces skill verdict FAIL and overall exit code 2.
- [x] **AC-US2-03**: `checkPlatformSecurity(name)` runs best-effort with bounded concurrency (~5); when offline or `--offline` is passed, the platform tier is skipped, `result.offline = true`, and the report states "Platform tier: skipped (offline)". No account/API key required.
- [x] **AC-US2-04**: Per-skill verdict composes tier1 verdict + blocklist + platform `hasCritical`; aggregate summary (score 0–100, PASS/CONCERNS/FAIL, severity counts) follows existing tier1 scoring conventions.

---

### US-003: Shareable report — terminal, JSON, markdown (P1)
**Project**: vskill

**As a** founder delivering a free audit (and as a CI-curious user)
**I want** a readable terminal summary plus exportable report files
**So that** the audit result works as a standalone sales/security artifact

**Acceptance Criteria**:
- [x] **AC-US3-01**: Default terminal output shows a summary header (agents detected, skills found, unmanaged count, blocklisted count, severity counts, verdict) and a table: skill · agents · scope/source · managed? · verdict · findings count.
- [x] **AC-US3-02**: `--json` emits a valid `InstalledAuditResult` JSON document (machine-parseable, no ANSI); `--report <file>` writes a markdown report (host, date, summary, per-skill sections, blocklist callouts, offline notes) via new `formatInstalledReport`.
- [x] **AC-US3-03**: Exit codes match existing audit semantics: PASS→0, CONCERNS→1, FAIL→2.
- [x] **AC-US3-04**: `--ci` (SARIF) combined with `--installed` prints a warning and falls back to JSON (SARIF stays project-audit-only).

---

### US-004: CLI wiring, default-path hint, docs (P2)
**Project**: vskill

**As an** existing vskill user
**I want** the new mode discoverable without any change to current behavior
**So that** nothing breaks and the wedge advertises itself

**Acceptance Criteria**:
- [x] **AC-US4-01**: `--installed` and `--offline` options registered on the existing `audit` command; `auditCommand` branches to `runInstalledAudit` at the top; the default project-audit path is unchanged (existing audit tests still pass).
- [x] **AC-US4-02**: Incompatible flags (`[path]`, `--fix`, `--tier1-only`, `--exclude`, `--max-files`) combined with `--installed` produce a one-line notice and are ignored; `--json`/`--report`/`--severity` are honored.
- [x] **AC-US4-03**: Default project-audit terminal output (non-`--json`/`--ci` only) appends one dim hint line: `Tip: run 'vskill audit --installed' to inventory skills on this machine.`
- [x] **AC-US4-04**: README CLI section and docs cli-reference mention the new mode with a one-paragraph description and an example invocation.

## Functional Requirements

### FR-001: Reuse-only scanning
No new pattern engines. Tier-1 = `runTier1Scan` (`src/scanner/tier1.ts`), blocklist = `src/blocklist/blocklist.ts`, platform = `src/security/platform-security.ts`. Tier-2 LLM (`tier2-llm.ts`) is Workers-AI-bound and MUST NOT be called locally.

### FR-002: Skill-centric result model
New `InstalledAuditResult` type family (skill-centric, multi-location) — deliberately NOT an extension of the file-centric `AuditResult`, so existing formatters stay untouched. New formatter functions live alongside existing ones in the same formatter files.

## Success Criteria

- `npx vskill@latest audit --installed` on a machine with Claude Code + Cursor produces a complete inventory in <30s online, <10s offline, with zero crashes on permission-denied dirs.
- Existing `vskill audit` tests pass unmodified (default path untouched).
- The markdown report is usable verbatim as the free-audit sales artifact (host, date, unmanaged-count headline).

## Out of Scope

- Loose format-converted rules discovery (e.g. `.cursor/rules/*.mdc`) — deferred; report notes the limitation.
- SARIF output for installed mode; Tier-2 LLM local execution; auditing cached-but-disabled plugin versions (future `--include-cached`).
- Platform/website changes (marketing pages are increment 0877).

## Dependencies

- Existing modules: `src/agents/agents-registry.ts`, `src/installer/canonical.ts`, `src/scanner/tier1.ts`, `src/blocklist/blocklist.ts`, `src/security/platform-security.ts`, `src/settings/settings.ts`, `src/lockfile/*`, `src/updater/source-fetcher.ts` (`computeSha`), `src/audit/formatters/*`, `src/utils/output.ts`.
