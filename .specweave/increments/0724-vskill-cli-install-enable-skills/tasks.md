---
increment: 0724-vskill-cli-install-enable-skills
tasks_version: 1
---

# Implementation Tasks

> All file paths below are relative to `repositories/anton-abyzov/vskill/`.
> Phase A = scaffolding & shared lib, Phase B = new commands, Phase C = mods to existing commands + e2e.
> TDD order: write tests first (RED), implement (GREEN), refactor.

---

### T-001: Add helper module `src/lib/skill-lifecycle.ts` (pure functions)
**User Story**: US-002, US-003, US-005 | **Satisfies ACs**: AC-US2-01, AC-US3-01, AC-US5-01, AC-US5-02 | **Phase**: A | **Estimate**: 1.5h | **Status**: [ ] pending
**Files**: `src/lib/skill-lifecycle.ts` (NEW), `src/lib/__tests__/skill-lifecycle.test.ts` (NEW)
**Depends on**: none
**Test plan**:
- Given a `SkillLockEntry` with `marketplace: "specweave"` → When `resolvePluginId("foo", entry)` → Then returns `"foo@specweave"`.
- Given a `SkillLockEntry` with `marketplace` undefined → When `resolvePluginId(...)` → Then returns `null` (auto-discovered).
- Given an `AgentDefinition` for `claude-code` → When `classifyAgentSurface(agent)` → Then returns `"claude-code-style"`.
- Given an `AgentDefinition` for `cursor`/`codex`/`cline` → When `classifyAgentSurface(agent)` → Then returns `"auto-discover"`.
- Given a list of agents and an action → When `buildPerAgentReport("foo", "user", "enabled", agents)` → Then returns one line per agent with classification-appropriate text.

---

### T-002: Register Commander commands `enable` and `disable` in `src/index.ts`
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-04, AC-US2-05, AC-US3-05, AC-US6-01, AC-US6-02 | **Phase**: A | **Estimate**: 0.5h | **Status**: [ ] pending
**Files**: `src/index.ts` (MODIFY)
**Depends on**: T-001
**Test plan**:
- Given `vskill enable --help` invoked through Commander parse → When help text rendered → Then it lists `--scope`, `--dry-run`, `--verbose` options.
- Given `vskill disable --help` → Then same flags listed.
- (Functional behaviour tested in T-003 / T-004; this task is wiring only.)

---

### T-003: Implement `vskill enable <name>` command (`src/commands/enable.ts`)
**User Story**: US-002, US-005, US-006 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US5-02, AC-US5-04, AC-US6-01, AC-US6-02 | **Phase**: B | **Estimate**: 3h | **Status**: [ ] pending
**Files**: `src/commands/enable.ts` (NEW), `src/commands/__tests__/enable.test.ts` (NEW)
**Depends on**: T-001, T-002
**Test plan**:
- Given lockfile contains `foo` with `marketplace: "m"` AND `enabledPlugins["foo@m"]` is false at user scope → When `enable foo --scope user` → Then `claudePluginInstall("foo@m", "user")` called once AND `isPluginEnabled` returns true. Exit 0.
- Given `foo` is NOT in lockfile → When `enable foo` → Then exits 1 with message containing `vskill install foo`.
- Given `foo` is already enabled at user scope → When `enable foo --scope user` → Then `claudePluginInstall` is NOT called, output contains `already enabled in user scope`, exit 0.
- Given `enable foo --dry-run` → Then output contains the exact `claude plugin install --scope user -- foo@m` invocation, no subprocess spawned, exit 0.
- Given `--scope project` → Then settings.json path resolves to `<cwd>/.claude/settings.json` and `claudePluginInstall(id, "project", { cwd })` called.
- Given `--json` → Then stdout is valid JSON with shape `{skill, scope, perAgent: [...]}`.

---

### T-004: Implement `vskill disable <name>` command (`src/commands/disable.ts`)
**User Story**: US-003, US-005, US-006 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US5-03, AC-US6-01, AC-US6-02 | **Phase**: B | **Estimate**: 2.5h | **Status**: [ ] pending
**Files**: `src/commands/disable.ts` (NEW), `src/commands/__tests__/disable.test.ts` (NEW)
**Depends on**: T-001, T-002
**Test plan**:
- Given `foo` is enabled at user scope → When `disable foo --scope user` → Then `claudePluginUninstall("foo@m", "user")` called once AND `isPluginEnabled` returns false AND lockfile entry for `foo` UNCHANGED AND skill files at `<localSkillsDir>/foo` STILL exist.
- Given `foo` lockfile entry has no `marketplace` field → When `disable foo` → Then no subprocess spawned, output contains `auto-discovered — no plugin entry to disable. To stop loading, run vskill remove foo.`, exit 0.
- Given `foo` is already disabled → When `disable foo` → Then no subprocess spawned, output contains `already disabled in <scope> scope`, exit 0.
- Given `foo` is enabled at user AND project scope → When `disable foo --scope project` → Then user-scope `enabledPlugins["foo@m"]` is still true; project-scope is false; output hint includes `still enabled in user scope`.
- Given `--dry-run` → Then output contains the `claude plugin uninstall ...` invocation, no spawn.

---

### T-005: Extend `vskill list --installed` (`src/commands/list.ts`)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Phase**: B | **Estimate**: 1.5h | **Status**: [ ] pending
**Files**: `src/commands/list.ts` (MODIFY), `src/commands/__tests__/list-installed.test.ts` (NEW)
**Depends on**: T-001
**Test plan**:
- Given lockfile with two skills (`foo` enabled at user, `bar` enabled at project, `baz` no marketplace) → When `list --installed` → Then table prints three rows with scope columns showing `enabled / disabled / n/a` correctly.
- Given the same setup with `--installed --json` → Then stdout is JSON array with three objects, each having `enabledUser`, `enabledProject`, `autoDiscovered`.
- Given no lockfile present → When `list --installed` → Then exits with the same friendly message as the existing `listSkills` no-lockfile branch.
- Given lockfile present but `~/.claude/settings.json` missing → When `list --installed` → Then no crash; both scope columns show `disabled` for marketplace skills.

---

### T-006: Add `--no-enable` and `--scope` flags to `vskill install` (`src/commands/add.ts`)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Phase**: C | **Estimate**: 2.5h | **Status**: [ ] pending
**Files**: `src/commands/add.ts` (MODIFY), `src/commands/__tests__/add-no-enable.test.ts` (NEW)
**Depends on**: T-001, T-002
**Test plan**:
- Given marketplace plugin source AND no `--no-enable` → When `vskill install foo` succeeds → Then `claudePluginInstall("foo@m", scope)` called once and lockfile entry written.
- Given `--no-enable` → Then `claudePluginInstall` NOT called; lockfile entry still written; on-disk files still extracted.
- Given non-marketplace source (single SKILL.md) → Then `claudePluginInstall` NOT called regardless of `--no-enable`; output contains `Auto-discovered by agents from skills dir — no enable step needed`.
- Given `claudePluginInstall` throws → Then on-disk files at `<localSkillsDir>/foo` removed AND lockfile entry removed AND exit code non-zero AND stderr contains failed scope.
- Given `--scope project` → Then `claudePluginInstall` invoked with `"project"` and `{ cwd }`.

---

### T-007: Refactor `vskill remove` to use structured per-agent reporter (`src/commands/remove.ts`)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 (consistency) | **Phase**: C | **Estimate**: 0.75h | **Status**: [ ] pending
**Files**: `src/commands/remove.ts` (MODIFY), `src/commands/remove.test.ts` (UPDATE existing tests)
**Depends on**: T-001
**Test plan**:
- Given `foo` removed → When invoked → Then output contains structured per-agent lines (`<displayName> (<scope>) — <action>`) instead of the legacy free-form `Plugin uninstalled: foo@m` log.
- Given `--json` (new) → Then stdout is JSON object matching the shape used by `enable`/`disable`.
- Existing tests for filesystem cleanup and `claudePluginUninstall` invocation remain green.

---

### T-008: Add `--dry-run` to `vskill cleanup` and emit reconciliation summary (`src/commands/cleanup.ts`)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02, AC-US7-03, AC-US7-04 | **Phase**: C | **Estimate**: 1h | **Status**: [ ] pending
**Files**: `src/commands/cleanup.ts` (MODIFY), `src/commands/__tests__/cleanup-dryrun.test.ts` (NEW)
**Depends on**: T-001
**Test plan**:
- Given two stale entries at user scope and one at project scope → When `cleanup --dry-run` → Then output lists three `claude plugin uninstall …` invocations with scopes; no subprocess spawned; exit 0.
- Given a lockfile-only skill (in lockfile, NOT in `enabledPlugins`) → When `cleanup` → Then that skill is NOT touched (AC-US7-04 — user-disabled skills survive).
- Given mixed state → Then the reconciliation summary line `<N> stale entries removed from user scope, <M> from project scope, <K> in-sync skills left untouched.` appears at end of stdout.

---

### T-009: Author ADR-0024 — settings.json mutations must go through the claude CLI
**User Story**: US-006 (NFR-001) | **Satisfies ACs**: AC-US6-04 | **Phase**: A | **Estimate**: 0.5h | **Status**: [ ] pending
**Files**: `.specweave/docs/internal/architecture/adr/ADR-0024-skill-enable-disable-via-claude-cli.md` (NEW)
**Depends on**: none
**Test plan**:
- Given the ADR exists → When `lint:adr` (existing) runs → Then ADR passes structural validation (status, context, decision, consequences).
- Given the ADR is referenced from `plan.md` → Then the link resolves.

---

### T-010: E2E test — install / enable / disable / list round-trip (`e2e/enable-disable.test.ts`)
**User Story**: US-001, US-002, US-003, US-006 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-01, AC-US6-03 | **Phase**: C | **Estimate**: 2h | **Status**: [ ] pending
**Files**: `e2e/enable-disable.test.ts` (NEW)
**Depends on**: T-003, T-004, T-005, T-006
**Test plan**:
- Given a temp project + stub `claude` binary on PATH → When `vskill install foo --scope user` then `vskill disable foo --scope user` then `vskill enable foo --scope user` → Then final `~/.claude/settings.json` is byte-equal (deep-JSON-equal on `enabledPlugins`) to the post-install state. (AC-US6-03)
- Given the round-trip → Then on-disk skill files at `<userScope>/.claude/skills/foo` exist at every step.
- Given the round-trip → Then `vskill.lock` entry for `foo` exists at every step.

---

### T-011: Per-agent reporter integration tests (multi-agent surfaces)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Phase**: C | **Estimate**: 1h | **Status**: [ ] pending
**Files**: `src/commands/__tests__/per-agent-report.test.ts` (NEW)
**Depends on**: T-001, T-003, T-004, T-006
**Test plan**:
- Given `detectInstalledAgents` mocked to return `[claude-code, cursor, codex]` → When `enable foo` → Then output has three lines: `Claude Code (user) — enabled via claude CLI`, `Cursor — auto-discovers (no plugin enable needed)`, `Codex CLI — auto-discovers (no plugin enable needed)`.
- Given only `[cursor]` detected → When `enable foo` → Then output is `No agent requires explicit enable — Cursor auto-discovers from .cursor/skills/. Skill is already on disk and live.` and exit 0 (AC-US5-03).
- Given `--json` flag → Then stdout is one-line JSON object matching `{skill, scope, perAgent: [{id, displayName, action}]}`.

---

### T-012: Idempotency and rollback integration tests
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-05, AC-US2-03, AC-US3-03 | **Phase**: C | **Estimate**: 1.5h | **Status**: [ ] pending
**Files**: `src/commands/__tests__/idempotency-rollback.test.ts` (NEW)
**Depends on**: T-003, T-004, T-006
**Test plan**:
- Given `enable foo` succeeds → When `enable foo` invoked a second time → Then `claudePluginInstall` invocation count remains 1; output matches `already enabled`; exit 0.
- Given `disable foo` succeeds → When `disable foo` invoked a second time → Then `claudePluginUninstall` invocation count remains 1; output matches `already disabled`; exit 0.
- Given `claudePluginInstall` is mocked to throw on first call → When `vskill install foo` → Then on-disk files removed, lockfile entry absent after the failed run, exit non-zero, stderr names the failed scope.

---

### T-013: Update vskill `README.md` documenting `enable` / `disable` / `--no-enable` / `list --installed`
**User Story**: US-001 to US-007 | **Satisfies ACs**: documentation supporting AC-US2-04, AC-US3-04, AC-US4-01, AC-US5-01 | **Phase**: C | **Estimate**: 0.75h | **Status**: [ ] pending
**Files**: `README.md` (MODIFY)
**Depends on**: T-003, T-004, T-005, T-006
**Test plan**:
- Given the README is updated → When CI's `lint:skills-spec` (existing) runs → Then it passes.
- Given a manual review → Then a new "Enable / Disable" section exists with concrete `vskill enable foo` / `vskill disable foo` examples and a `list --installed` sample table.
- Given the new flags → Then each is described in the Commands table.

---

### T-014: Coverage and CI sanity check
**User Story**: NFR-006 | **Satisfies NFRs**: NFR-006 | **Phase**: C | **Estimate**: 0.5h | **Status**: [ ] pending
**Files**: none (CI)
**Depends on**: T-001 .. T-013
**Test plan**:
- Given the increment is implemented → When `npm run test -- --coverage` runs → Then per-file coverage for `src/commands/enable.ts`, `src/commands/disable.ts`, `src/lib/skill-lifecycle.ts` is ≥ 90% lines AND ≥ 90% branches.
- Given `npm run lint:bundle-size` runs → Then the bundle does not regress beyond the existing budget.
- Given `npx playwright test e2e/enable-disable.test.ts` runs → Then it passes.

---

## Summary

- **Phase A** (scaffolding & ADR): T-001, T-002, T-009 — ~2.5h
- **Phase B** (new commands + list extension): T-003, T-004, T-005 — ~7h
- **Phase C** (modify existing + e2e + docs): T-006, T-007, T-008, T-010, T-011, T-012, T-013, T-014 — ~10h
- **Total estimate**: ~19.5 hours of focused work; fits inside the team-lead 15-task cap.
