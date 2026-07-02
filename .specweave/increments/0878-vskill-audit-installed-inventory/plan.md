# Implementation Plan: Free `vskill audit --installed` — machine-wide skill inventory + scan

## Overview

Add an `--installed` mode to the existing `vskill audit` command (repositories/anton-abyzov/vskill). Inventory every skill installed on the machine across the 53-agent registry + Claude Code plugin cache, dedupe by content hash, scan each unique bundle through the existing stack (tier1 patterns → blocklist → best-effort platform tier), and render terminal/JSON/markdown reports. Default project-audit path stays byte-for-byte unchanged.

## Design

### Components

- **`src/audit/installed-types.ts`** (new) — skill-centric result model:
  - `SkillLocation { agentId, agentName, scope: "global"|"project"|"plugin", absPath }`
  - `InstalledSkillFinding { patternId, patternName, severity, category, line, context, file }` (adapted from `ScanFinding`)
  - `InstalledSkillResult { name, contentHash, managed, locations[], patternVerdict, patternScore, findings[], blocklistHit, platform, worstSeverity }`
  - `InstalledAuditSummary { agentsDetected, skillsFound, unmanagedCount, blocklistedCount, critical..info, cachedButDisabled, score, verdict }`
  - `InstalledAuditResult { startedAt, completedAt, durationMs, hostname, offline, skills[], summary }`
- **`src/audit/installed-inventory.ts`** (new) — `inventoryInstalledSkills(cwd)`:
  1. `detectInstalledAgents()`; for each agent × {global, project} scope: `resolveAgentSkillsDir(agent, {global, projectRoot: cwd})` → `scanSkillsRoot(dir)` = immediate child dirs containing `SKILL.md`.
  2. Claude Code plugin cache: expand `agent.pluginCacheDir`; for each `{marketplace}/{plugin}`, if `plugin@marketplace ∈ listEnabledPlugins(user ∪ project)` audit highest version dir (`{ver}/skills/<name>/SKILL.md` or `{ver}/SKILL.md`); else count into `cachedButDisabled`.
  3. `readSkillBundle(dir)`: SKILL.md + sibling text files (SCANNABLE_EXTENSIONS), per-file 100 KB / bundle 512 KB caps, SKIP_DIRS, no symlink-dir traversal (`withFileTypes` + `isSymbolicLink()`), depth cap 32, all reads try/catch-skipped.
  4. `computeSha` (from `src/updater/source-fetcher.ts`, accepts `Record<string,string>`) → group by hash into `InstalledSkill { locations[] }`; managed = name ∈ `readLockfile()` ∪ `readSkillsShLock()`.
- **`src/audit/installed-audit.ts`** (new) — `runInstalledAudit(opts)`: inventory → per-unique-skill scan with ~5-wide `Promise.allSettled` pool: `runTier1Scan(bundleContent)` + `checkBlocklist(name, hash)` + (`offline ? null : checkPlatformSecurity(name)`) → verdict compose (blocklist hit ⇒ FAIL) → summary/score → format + exit code.
- **Formatter additions** (append-only in existing files): `formatInstalledTerminal` (terminal-formatter.ts), `formatInstalledReport` (report-formatter.ts — the sales artifact), `formatInstalledJson` (json-formatter.ts).
- **Edited**: `src/commands/audit.ts` (extend `AuditCommandOptions` with `installed?`, `offline?`; top-of-function branch; ignored-flag notices; hint line after `formatTerminal`), `src/index.ts` (register `--installed`, `--offline`), README + docs cli-reference.

### Offline determination

`offline = opts.offline || quick reachability probe fails`. Blocklist always runs (its own stale-cache fallback). Platform tier skipped when offline, stated explicitly in every output format.

## Rationale

- **New types instead of extending `AuditResult`**: the file-centric `AuditResult`/`AuditFinding` are load-bearing for existing formatters (group by `filePath`). Skill-centric, multi-location results forced into that shape would corrupt the default path. Sibling formatter functions reuse the architecture without touching existing exports.
- **`runTier1Scan` (53 SCAN_PATTERNS), not `runAuditScan` (23 AUDIT_PATTERNS)**: the two engines coexist in the repo; install-time trust decisions use tier1, and the wedge story ("same scan used at install time", broader coverage, offline) demands tier1. The divergence between audit modes is documented here deliberately.
- **Enabled-plugins-only for the cache**: auditing every cached version explodes runtime for stale data; `cachedButDisabled` count still surfaces the hygiene issue. `--include-cached` is a future flag.
- **Bundle scan (SKILL.md + siblings)**: malicious payloads commonly live in `scripts/*.sh` or helper files, not the manifest. `runTier1Scan` takes one string → concatenate with path delimiters so findings remain attributable.
- **No local Tier-2 LLM**: `tier2-llm.ts` requires a Cloudflare Workers AI binding; the "LLM intent" tier reaches users via `checkPlatformSecurity` (server-side verdicts) — keeping the promise "no account required".
- **SARIF excluded**: installed mode is not a CI file-diagnostics concept; warning + JSON fallback avoids a half-correct SARIF mapping.
- **ADR check**: no existing ADR conflicts; this is additive CLI surface reusing established modules (verified against `.specweave/docs/internal/architecture/adr/`).

## Testing Strategy

Vitest, repo conventions: unit tests mock modules via `vi.mock` (mirror `src/commands/__tests__/list-installed.test.ts`); command-level tests use `mkdtemp` fixtures + `vi.spyOn(process, "exit")` (mirror `src/commands/audit.test.ts`). Network tiers always mocked. TDD RED→GREEN→REFACTOR per component (see tasks.md). Existing audit tests must pass unmodified (AC-US4-01 regression gate).

## Technical Challenges

### Challenge 1: Cross-platform home/tilde expansion
**Solution**: use `resolveTilde` (canonical.ts, `os.homedir()`-based) — not the `HOME`-env-only helper; respect `win32PathOverride` from the registry.
**Risk**: Windows CI coverage is thin → add a unit test with mocked `homedir`/platform.

### Challenge 2: Noisy false positives on personal machines
**Solution**: severity filtering (`--severity`), info-level findings don't affect verdict (existing tier1 scoring already treats info as 0-cost), report groups by severity.
**Risk**: a scary-but-wrong report undermines the sales artifact — the report copy must say "findings to review", not "malware detected", except for blocklist hits.
