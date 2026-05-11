---
increment: 0845-cross-tool-skill-installation
title: "Cross-tool skill installation in Skill Studio"
target_repo: repositories/anton-abyzov/vskill
test_mode: TDD
coverage_target: 90
last_updated: 2026-05-11
---

# Tasks: Cross-tool skill installation in Skill Studio

## Summary

**Total tasks**: 24
**Domain distribution**: Server-side: 15 | Frontend: 6 | E2E/Verification: 3

## AC Coverage Matrix

All 42 ACs across US-001..US-006 are covered. Coverage by task:

| AC | Task(s) |
|---|---|
| AC-US1-01 | T-004, T-005 |
| AC-US1-02 | T-005 |
| AC-US1-03 | T-018 |
| AC-US1-04 | T-018 |
| AC-US1-05 | T-018 |
| AC-US1-06 | T-001, T-004 |
| AC-US2-01 | T-022 |
| AC-US2-02 | T-019 |
| AC-US2-03 | T-019 |
| AC-US2-04 | T-019 |
| AC-US2-05 | T-019 |
| AC-US2-06 | T-011, T-017 |
| AC-US2-07 | T-021 |
| AC-US2-08 | T-019 |
| AC-US2-09 | T-017 |
| AC-US3-01 | T-002 |
| AC-US3-02 | T-002 |
| AC-US3-03 | T-002 |
| AC-US3-04 | T-002, T-003 |
| AC-US4-01 | T-001 |
| AC-US4-02 | T-006, T-007, T-008, T-009 |
| AC-US4-03 | T-006 |
| AC-US4-04 | T-007 |
| AC-US4-05 | T-008 |
| AC-US4-06 | T-009 |
| AC-US4-07 | T-010 |
| AC-US4-08 | T-011, T-012 |
| AC-US4-09 | T-013 |
| AC-US4-10 | T-011 |
| AC-US4-11 | T-011 |
| AC-US4-12 | T-014 |
| AC-US5-01 | T-019 |
| AC-US5-02 | T-019 |
| AC-US5-03 | T-015 |
| AC-US5-04 | T-020 |
| AC-US5-05 | T-020 |
| AC-US5-06 | T-016 |
| AC-US5-07 | T-015, T-020 |
| AC-US5-08 | T-020, T-021 |
| AC-US6-01 | T-018 |
| AC-US6-02 | T-004, T-005 |
| AC-US6-03 | T-004 |

**Uncovered ACs**: None. All 42 ACs have at least one task.

---

## FOUNDATION (server-side — must complete before other server tasks)

### T-001: Extend AgentDefinition interface with tier, installMode, formatTransformer, pasteInstructionsUrl
**User Story**: US-004, US-006 | **AC**: AC-US4-01, AC-US1-06 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given an existing registry entry has none of the new optional fields
- When the registry is loaded
- Then `tier` defaults to `1`, `installMode` defaults to `"filesystem"`, `formatTransformer` is `undefined`, `pasteInstructionsUrl` is `undefined`
- Given a Tier 3 entry has `installMode: "clipboard"` and `isRemoteOnly: true`
- When `getSupportedAgents()` filters the registry
- Then the entry is included (clipboard mode is a valid install surface)
**Files**:
- `repositories/anton-abyzov/vskill/src/agents/agents-registry.ts` (modified — interface extension only)
- `repositories/anton-abyzov/vskill/src/installer/transformers/index.ts` (new — `ParsedSkill`, `TransformedFile`, `FormatTransformer` interfaces)
**Notes**: All four fields are optional — zero behavior change to the 53 existing entries. Also add `docsUrl?: string` to `AgentDefinition` for Tier 3.

---

### T-002: Verify and fix Antigravity registry entry; add VSKILL_ANTIGRAVITY_SKILLS_DIR override
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given the Antigravity `AgentDefinition` in the registry
- When the entry is read
- Then `globalSkillsDir` equals `~/.gemini/antigravity/skills`, `isRemoteOnly` is falsy, `tier` is `1`, `installMode` is `"filesystem"`
- Given `VSKILL_ANTIGRAVITY_SKILLS_DIR=/tmp/ag-test` is set
- When `resolveAgentSkillsDir` is called for the antigravity agent with scope=user
- Then the returned path starts with `/tmp/ag-test`
- Given a skill `obsidian-brain` is installed to Antigravity scope=user with no env override
- When the install completes
- Then `~/.gemini/antigravity/skills/obsidian-brain/SKILL.md` exists with correct content
**Files**:
- `repositories/anton-abyzov/vskill/src/agents/agents-registry.ts` (modified — verify/fix Antigravity entry, add `tier: 1`, `installMode: "filesystem"`)
- `repositories/anton-abyzov/vskill/src/installer/canonical.ts` (modified — env override for Antigravity in `resolveAgentSkillsDir`)
- `repositories/anton-abyzov/vskill/src/agents/__tests__/agents-registry.test.ts` (modified — Antigravity path assertions)
**Notes**: Antigravity entry is confirmed at agents-registry.ts:211. Run `grep -n "antigravity" repositories/anton-abyzov/vskill/src/agents/agents-registry.ts` to confirm current path before changing.

---

### T-003: Populate tier and installMode on all registry entries; add chatgpt, v0, bolt-new Tier 3 entries
**User Story**: US-003, US-004, US-005 | **AC**: AC-US3-04, AC-US5-01 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given all registry entries are loaded
- When each entry's `tier` and `installMode` are read
- Then Tier 1 entries (Claude Code, Codex, OpenClaw, OpenCode, Antigravity, Gemini CLI, Amp, Cline, Kimi) have `tier: 1, installMode: "filesystem"`
- And Tier 2 entries (Cursor, Windsurf, GitHub Copilot Ext, Junie, Kiro, Continue, Aider, Trae) have `tier: 2, installMode: "filesystem"`
- And Tier 3 entries (ChatGPT, v0, bolt.new) have `tier: 3, installMode: "clipboard"` and `isRemoteOnly: true`
- Given a new ChatGPT entry is added to the registry
- When `getAgent("chatgpt")` is called
- Then it returns the entry with `pasteInstructionsUrl: "https://chatgpt.com/#settings/Personalization"`
**Files**:
- `repositories/anton-abyzov/vskill/src/agents/agents-registry.ts` (modified — add `tier`/`installMode` to all entries; add `chatgpt` entry; verify `v0` and `bolt-new` entries already exist)
**Notes**: plan.md §12 concern #1: chatgpt entry does not yet exist in the registry. Add it with `isRemoteOnly: true, installMode: "clipboard", tier: 3`. Existing Tier 1 entries without explicit fields default correctly via T-001, so only annotate Tier 2 and Tier 3 explicitly where behavior must be non-default.

---

### T-004: Add getSupportedAgents() to agents-registry.ts
**User Story**: US-001, US-006 | **AC**: AC-US1-01, AC-US6-02, AC-US6-03 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given the registry has 53 entries where Devin and Replit are `isRemoteOnly: true` with no `installMode`, and ChatGPT/v0/bolt.new are `isRemoteOnly: true` with `installMode: "clipboard"`
- When `getSupportedAgents()` is called
- Then it returns all entries that have `installMode: "filesystem"` or `installMode: "clipboard"` (excludes Devin, Replit, and any without installMode)
- When `detectInstalledAgents()` is called separately
- Then it still returns only the subset with `detected: true` (unchanged behavior — AC-US6-03)
- Given a new entry is added with `installMode: "filesystem"` but no binary on PATH
- When `getSupportedAgents()` runs
- Then the new entry is included (detection irrelevant to supportability)
**Files**:
- `repositories/anton-abyzov/vskill/src/agents/agents-registry.ts` (modified — add `getSupportedAgents()` export)
- `repositories/anton-abyzov/vskill/src/agents/__tests__/agents-registry.test.ts` (modified — new test cases for `getSupportedAgents`)
**Notes**: Keep `detectInstalledAgents()` at line 853 completely unchanged (AC-US6-03). Filter logic: `a.installMode === "filesystem" || a.installMode === "clipboard"`. Cross-reference ADR-0845-01 for rationale.

---

### T-005: New eval-server route GET /api/studio/supported-agents
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US6-02 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given the Studio server is running and the request comes from localhost
- When `GET /api/studio/supported-agents` is called
- Then the response is `{ agents: SupportedAgent[] }` where each agent has `{ id, displayName, detected, tier, installMode, resolvedGlobalDir, resolvedLocalDir }`
- And Tier 3 entries additionally have `pasteInstructionsUrl`
- Given `GET /api/studio/detected-agents` is called separately
- When the response is compared to the new route
- Then `detected-agents` returns only the subset where `detected === true`, unchanged
- Given Codex CLI's binary is NOT on $PATH
- When `GET /api/studio/supported-agents` is called
- Then Codex appears in the response with `detected: false` (not filtered out)
- Given a non-localhost client sends the request
- When the server evaluates the `isLocalhost()` guard
- Then the response is 403
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/install-state-routes.ts` (modified — add `GET /api/studio/supported-agents` handler)
- `repositories/anton-abyzov/vskill/src/eval-server/__tests__/install-state-routes.test.ts` (modified — new cases for the new route)
- `repositories/anton-abyzov/vskill/src/studio/routes/index.ts` (modified — register handler)
**Notes**: Reuse existing `isLocalhost()` guard from install-skill-routes.ts:54-58. Each `detectBinary` probe MUST run in parallel for all agents (AC-US6-02 — detection latency bounded). Tilde-expand `resolvedGlobalDir` using `os.homedir()`.

---

## TRANSFORMERS (server-side — parallelizable after T-001)

### T-006: Cursor transformer (cursor.ts) + unit tests
**User Story**: US-004 | **AC**: AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given a `ParsedSkill` with `name: "obsidian-brain"` and `description: "PARA + LLM Wiki"` and a non-empty body
- When the Cursor transformer runs
- Then it returns exactly one `TransformedFile` with `relativePath: "rules/obsidian-brain.mdc"`
- And the content starts with `---\ndescription: PARA + LLM Wiki\nglobs: ""\nalwaysApply: false\n---`
- And the body after the frontmatter is byte-equal to `parsedSkill.body`
- Given the transformer is called twice with the same input
- When both outputs are compared
- Then they are byte-equal (idempotency)
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/transformers/cursor.ts` (new)
- `repositories/anton-abyzov/vskill/src/installer/transformers/__tests__/cursor.test.ts` (new)
**Notes**: No I/O inside the transformer. `relativePath` uses POSIX forward slashes. Wire `formatTransformer: cursorTransformer` in agents-registry.ts Cursor entry (part of T-003 or here — coordinate to avoid duplicate edits).

---

### T-007: Windsurf transformer (windsurf.ts) + unit tests
**User Story**: US-004 | **AC**: AC-US4-02, AC-US4-04 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given a `ParsedSkill` with name `"obsidian-brain"` and any frontmatter
- When the Windsurf transformer runs
- Then it returns one `TransformedFile` with `relativePath: "rules/obsidian-brain.md"`
- And the content is plain markdown — no YAML frontmatter block present
- And the body is `parsedSkill.body` verbatim
- Given the transformer is called twice with the same input
- When outputs are compared
- Then they are byte-equal
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/transformers/windsurf.ts` (new)
- `repositories/anton-abyzov/vskill/src/installer/transformers/__tests__/windsurf.test.ts` (new)

---

### T-008: GitHub Copilot transformer (github-copilot.ts) + unit tests
**User Story**: US-004 | **AC**: AC-US4-02, AC-US4-05 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given a `ParsedSkill` with name `"obsidian-brain"`
- When the GitHub Copilot transformer runs
- Then it returns one `TransformedFile` with `relativePath: "instructions/obsidian-brain.instructions.md"`
- And the content starts with `---\napplyTo: "**"\n---`
- And the body follows the frontmatter verbatim
- Given the transformer runs twice with the same input
- Then outputs are byte-equal
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/transformers/github-copilot.ts` (new)
- `repositories/anton-abyzov/vskill/src/installer/transformers/__tests__/github-copilot.test.ts` (new)

---

### T-009: Junie, Kiro, Continue.dev, Trae transformers + unit tests
**User Story**: US-004 | **AC**: AC-US4-02, AC-US4-06 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given a `ParsedSkill` with name `"obsidian-brain"` and non-trivial frontmatter
- When `junieTransformer` runs — Then one file at `"rules/obsidian-brain.md"`, plain markdown (no frontmatter), body verbatim
- When `kiroTransformer` runs — Then one file at `"steering/obsidian-brain.md"`, plain markdown, body verbatim
- When `continueDevTransformer` runs — Then one file at `"rules/obsidian-brain.md"`, plain markdown, body verbatim
- When `traeTransformer` runs — Then one file at `"obsidian-brain.md"`, plain markdown, body verbatim
- Given any of the four transformers runs twice with identical input
- Then output is byte-equal (idempotency for each)
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/transformers/junie.ts` (new)
- `repositories/anton-abyzov/vskill/src/installer/transformers/kiro.ts` (new)
- `repositories/anton-abyzov/vskill/src/installer/transformers/continue-dev.ts` (new)
- `repositories/anton-abyzov/vskill/src/installer/transformers/trae.ts` (new)
- `repositories/anton-abyzov/vskill/src/installer/transformers/__tests__/plain-markdown-transformers.test.ts` (new — covers all four)
**Notes**: All four strip frontmatter and emit plain markdown. A single test file covering all four avoids repetitive boilerplate.

---

### T-010: Aider transformer (aider.ts) + yaml-safe-mutate.ts + unit tests
**User Story**: US-004 | **AC**: AC-US4-02, AC-US4-07 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given a `ParsedSkill` with name `"obsidian-brain"`
- When the Aider transformer runs
- Then it returns TWO `TransformedFile`s:
  - File 1: `relativePath: "conventions/obsidian-brain.md"`, `op: "write"`, body = `parsedSkill.body` (plain markdown)
  - File 2: `relativePath: "../../.aider.conf.yml"`, `op: "append-yaml-list"`, `yamlListKey: "read"`, `yamlListValue: "~/.aider/conventions/obsidian-brain.md"`
- Given `safeAppendYamlList` is called when `~/.aider.conf.yml` does not exist
- Then it creates the file with `read:\n  - <path>` and returns `{ status: "created" }`
- Given `safeAppendYamlList` is called when conf.yml exists with `read: [existing-path]` and the new value is absent
- Then the value is appended, a `.bak.<ts>` file is created, and `{ status: "appended", backupPath }` is returned
- Given `safeAppendYamlList` is called with a value already present in the list
- Then no write occurs and `{ status: "already-present" }` is returned
- Given conf.yml is malformed YAML
- Then `MalformedConfigError` is thrown and the file is untouched
- Given conf.yml has `read: "single-string"` (not an array)
- Then `IncompatibleConfigError` is thrown
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/transformers/aider.ts` (new)
- `repositories/anton-abyzov/vskill/src/installer/yaml-safe-mutate.ts` (new — `safeAppendYamlList()`)
- `repositories/anton-abyzov/vskill/src/installer/transformers/__tests__/aider.test.ts` (new — transformer unit tests)
- `repositories/anton-abyzov/vskill/src/installer/__tests__/yaml-safe-mutate.test.ts` (new — all 8 scenarios from ADR-0845-03)
**Notes**: Aider transformer stays pure — no I/O. The `yamlListValue` uses `~/.aider/conventions/<name>.md` (tilde path); the dispatcher in T-011 resolves it to absolute at write time. Uses `js-yaml` (existing vskill dependency). See ADR-0845-03 for full algorithm.

---

## INSTALL PIPELINE (server-side — requires T-001 through T-010 complete)

### T-011: New src/installer/multi-install.ts with installSkillToMultipleAgents
**User Story**: US-002, US-004 | **AC**: AC-US2-06, AC-US4-08, AC-US4-10, AC-US4-11 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given `agentIds: ["codex", "cursor"]` (Tier 1 + Tier 2) and a valid skill
- When `installSkillToMultipleAgents` runs against a tmpdir HOME
- Then Codex writes `<tmpHome>/.codex/skills/obsidian-brain/SKILL.md` (canonical path)
- And Cursor writes `<tmpHome>/.cursor/rules/obsidian-brain.mdc` (transformer path)
- And both `AgentInstallResult` entries have `status: "installed"`
- Given one of the selected transformers throws an error
- When `installSkillToMultipleAgents` runs
- Then the throwing agent returns `status: "error"` with the throw message
- And all other agents still return `status: "installed"` (AC-US4-10)
- Given a transformer produces `relativePath: "../../etc/passwd"` (path traversal attempt)
- When the write is attempted
- Then a path-traversal error is thrown and `status: "error"` is returned for that agent (AC-US4-11)
- Given `agentIds: ["chatgpt"]` (Tier 3)
- When `installSkillToMultipleAgents` runs
- Then no filesystem write occurs and the result has `status: "exported"` with blob and `pasteInstructionsUrl`
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/multi-install.ts` (new)
- `repositories/anton-abyzov/vskill/src/installer/__tests__/multi-install.test.ts` (new — unit tests with memfs)
- `repositories/anton-abyzov/vskill/src/installer/__tests__/multi-install.integration.test.ts` (new — real tmpdir)
**Notes**: Sequential per-agent loop (FR-002). Path traversal guard: `path.relative(agentRoot, absoluteWritePath).startsWith('..')` → reject. The `append-yaml-list` op routes to `safeAppendYamlList`. The Tier-3 path calls `buildClipboardBlob` (from T-015) and returns without writing to disk.

---

### T-012: Add resolveAgentInstallRoot helper to canonical.ts; wire Tier 2 dispatch
**User Story**: US-004 | **AC**: AC-US4-08 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given a Cursor `AgentDefinition` with `localSkillsDir: ".cursor/skills"` and `globalSkillsDir: "~/.cursor/skills"`
- When `resolveAgentInstallRoot(agent, { global: true })` is called
- Then it returns `~/.cursor` (the parent of `globalSkillsDir`)
- Given a Tier 1 agent (Codex) with `globalSkillsDir: "~/.codex/skills"`
- When `resolveAgentInstallRoot(agent, { global: true })` is called
- Then it returns `~/.codex` (parent)
- Given Tier 1 `installSymlink` is called (existing path)
- Then behavior is identical to pre-T-012 (zero regression)
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/canonical.ts` (modified — add `resolveAgentInstallRoot` export)
- `repositories/anton-abyzov/vskill/src/installer/__tests__/canonical.test.ts` (modified — new case for `resolveAgentInstallRoot`)
**Notes**: The parent is computed as `path.dirname(resolveAgentSkillsDir(agent, opts))`. `installSymlink` and `installCopy` themselves are NOT modified — they stay on the Tier 1 path.

---

### T-013: Idempotency assertions for all transformers + integration test
**User Story**: US-004 | **AC**: AC-US4-09, FR-003 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given a skill `obsidian-brain` is installed to Cursor via `installSkillToMultipleAgents` twice
- When the second install completes
- Then `.cursor/rules/obsidian-brain.mdc` is byte-identical to the first run
- And there is exactly one frontmatter block in the file (no duplicates)
- Given the same test for Windsurf, Junie, Kiro, Continue, Aider, Trae
- Then each respective output file is byte-identical across both runs
- Given Aider's `safeAppendYamlList` runs twice for the same entry
- Then the second run is `status: "already-present"` and the `read:` list has exactly one copy of the entry
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/__tests__/idempotency.integration.test.ts` (new — runs against real tmpdir for all 8 Tier 2 transformers)
**Notes**: Each transformer's unit test (T-006..T-010) already asserts byte-equality on same input; this file runs multi-install twice end-to-end to verify at the pipeline level.

---

### T-014: Win32 path handling via win32PathOverride in multi-install
**User Story**: US-004 | **AC**: AC-US4-12 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given an agent with `win32PathOverride: "C:\\Users\\user\\AppData\\Roaming\\Cursor"` and the platform is `win32`
- When `resolveAgentInstallRoot` is called
- Then the returned path uses the `win32PathOverride` value
- Given the platform is NOT `win32`
- When `resolveAgentInstallRoot` is called
- Then the POSIX `globalSkillsDir` / `localSkillsDir` is used (override ignored)
- Given a transformer produces `relativePath: "rules/obsidian-brain.mdc"` with forward slashes
- When the dispatcher joins it with the install root on win32
- Then `path.join()` produces the correct backslash-separated path
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/canonical.ts` (modified — honor `win32PathOverride` in `resolveAgentInstallRoot`)
- `repositories/anton-abyzov/vskill/src/installer/__tests__/canonical.test.ts` (modified — win32 path cases using `process.platform` mock)
**Notes**: Use `path.join(root, ...relativePath.split('/'))` at write time so POSIX forward slashes work on win32.

---

## CLIPBOARD / TIER 3 (server-side)

### T-015: clipboard-export.ts buildClipboardBlob + POST /api/studio/export-skill route
**User Story**: US-005 | **AC**: AC-US5-03, AC-US5-07 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given a Tier 3 agentId `"chatgpt"` and a valid skill
- When `buildClipboardBlob(skill, "chatgpt")` is called
- Then it returns `{ blob: string, pasteInstructionsUrl: "https://chatgpt.com/#settings/Personalization", docsUrl: string }`
- And the blob contains the skill name, description, and body
- And NO disk write occurs
- Given `POST /api/studio/export-skill { skill: "obsidian-brain", agentId: "chatgpt" }` from localhost
- When the route handler runs
- Then the response is `{ skill, agentId, blob, pasteInstructionsUrl, docsUrl }` with status 200
- Given `POST /api/studio/export-skill { skill, agentId: "codex" }` (Tier 1)
- Then response is 400 (not a Tier 3 agent)
- Given request from non-localhost
- Then response is 403
- Given `agentIds` contains ONLY Tier 3 tools in a multi-install
- When `installSkillToMultipleAgents` runs
- Then no filesystem writes occur (AC-US5-07)
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/clipboard-export.ts` (new)
- `repositories/anton-abyzov/vskill/src/eval-server/export-skill-routes.ts` (new)
- `repositories/anton-abyzov/vskill/src/eval-server/__tests__/export-skill-routes.test.ts` (new)
- `repositories/anton-abyzov/vskill/src/installer/__tests__/clipboard-export.test.ts` (new)
- `repositories/anton-abyzov/vskill/src/studio/routes/index.ts` (modified — register `registerExportSkillRoutes`)
**Notes**: Apply the same `SAFE_NAME` regex to `agentId`. Validate with existing `isLocalhost()` guard. Route returns JSON; no SSE on this endpoint.

---

### T-016: Project-scope downgrade logic for Tier 3 with toast warning
**User Story**: US-005 | **AC**: AC-US5-06 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given a multi-install request includes a Tier 3 agent with `scope: "project"`
- When `installSkillToMultipleAgents` runs
- Then the Tier 3 result has `status: "exported"` (not `"error"`)
- And the `detail` field contains the string "does not support project-scoped skills; exported as user-scope blob"
- Given the same request with `scope: "user"`
- Then the Tier 3 result has `status: "exported"` with no downgrade warning in `detail`
**Files**:
- `repositories/anton-abyzov/vskill/src/installer/multi-install.ts` (modified — add scope-downgrade logic for Tier 3 inside the agent loop)
**Notes**: The scope downgrade is silent on the server side except for the `detail` message. The UI (T-021) surfaces it as a toast warning.

---

## EXTEND INSTALL-SKILL ROUTE (server-side)

### T-017: Extend POST /api/studio/install-skill to accept agentIds[] + SSE per-agent events
**User Story**: US-002 | **AC**: AC-US2-06, AC-US2-09, FR-006 | **Status**: [x] completed
**Domain**: server
**Test Plan**:
- Given `POST /api/studio/install-skill { skill, agentIds: ["codex", "cursor"], scope: "user" }` from localhost
- When the route handler runs
- Then `installSkillToMultipleAgents` is called and SSE emits one event per agent: `{ agentId, status, detail }`
- And a terminal `{ done: true }` event is emitted after all agents
- Given `POST /api/studio/install-skill { skill, agent: "codex", scope: "user" }` (legacy shape)
- When the route handler runs
- Then it dispatches to the same single-agent path as today (AC-US2-09)
- And all existing callers continue to work without modification
- Given `agentIds: ["invalid-name"]` where the id is not in the registry
- When the route validates
- Then response is 400 with a descriptive error
- Given any entry in `agentIds` fails the `SAFE_NAME` regex
- Then response is 400 immediately (FR-007)
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/install-skill-routes.ts` (modified — accept `agentIds?: string[]`, validate each, dispatch to `installSkillToMultipleAgents`)
- `repositories/anton-abyzov/vskill/src/eval-server/__tests__/install-skill-routes.test.ts` (modified — new cases for `agentIds[]`, legacy backward-compat)
**Notes**: Reuse existing SSE job infrastructure from `install-jobs.ts` (lines 30-85). `agentIds[]` and `agent: string` are mutually exclusive; if both are present prefer `agentIds[]`. Each entry in `agentIds` must pass the `SAFE_NAME` regex AND resolve via `getAgent(id)`.

---

## FRONTEND (eval-ui React — run npm run build:ui after each task)

### T-018: Restructure AgentScopePicker.Popover.tsx into 3 sections driven by /api/studio/supported-agents
**User Story**: US-001, US-006 | **AC**: AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US6-01 | **Status**: [x] completed
**Domain**: frontend
**Test Plan**:
- Given the Studio is loaded and `/api/studio/supported-agents` returns agents across all three tiers
- When `AgentScopePicker.Popover.tsx` renders
- Then three sections are visible: "Detected on this machine", "Available to install", "Cloud only (paste required)"
- And the old "Not Detected" passive section is absent
- Given Codex CLI is in the registry but its binary is not on $PATH (`detected: false`)
- When the popover opens
- Then Codex appears in "Available to install" with its resolved install path (e.g., `~/.codex/skills/<name>/SKILL.md`)
- And an inline `+ Install here` CTA is visible
- Given an agent is flagged `isRemoteOnly: true` with no `installMode` (Devin, Replit)
- When the popover renders
- Then that agent does NOT appear in any section (AC-US1-06)
- Given a new AgentDefinition is added to the registry with `installMode: "filesystem"`
- When the popover renders (after API refresh)
- Then the new tool appears in the appropriate section automatically — no hardcoded id list (AC-US6-01)
- Given clicking `+ Install here` on an "Available to install" row
- When the click handler fires
- Then `InstallTargetsModal` opens with that tool pre-checked
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/AgentScopePicker.Popover.tsx` (modified)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/api/install.ts` (modified — add `fetchSupportedAgents()` helper)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts` (modified — add `SupportedAgent` type)
- `dist/eval-ui/` (rebuild via `npm run build:ui`)
**Notes**: Existing snapshot tests for the "detected/absent" view must stay green. Introduce a `groupBy="installMode"` prop to control which rendering mode the popover uses. The new three-section view is the default for Studio; old view kept behind prop for backward compatibility per plan.md §12 R12.

---

### T-019: New InstallTargetsModal.tsx — tier-grouped checkboxes, validation, SSE consumer
**User Story**: US-002, US-005 | **AC**: AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-08, AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Domain**: frontend
**Test Plan**:
- Given the modal opens for a skill while the active tool is Claude Code
- When the modal renders
- Then the title reads "Install <skill name> to:"
- And rows are grouped: "Drop-in" (Tier 1), "Format-converted" (Tier 2), "Cloud only (paste required)" (Tier 3)
- And detected tools sort above undetected within each group
- And only the Claude Code row is pre-checked (AC-US2-03)
- Given the user clicks "Select all detected"
- When the action fires
- Then all rows with `detected: true` become checked and the Install button is enabled
- Given the user clicks "Clear"
- When the action fires
- Then all rows are unchecked and the Install button is disabled with tooltip "Select at least one target"
- Given the user clicks Cancel
- When the handler fires
- Then the modal closes, no API call is made, no toast appears (AC-US2-08)
- Given a Tier 3 row (ChatGPT) is visible
- When the row renders
- Then it shows "Copy to clipboard" instead of a filesystem path (AC-US5-02)
- Given the Install button is clicked with at least one row checked
- When the submit fires
- Then `POST /api/studio/install-skill` is called with `{ skill, agentIds: string[], scope }`
- And the SSE stream is consumed, updating a live progress indicator per agent
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/InstallTargetsModal.tsx` (new)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/InstallTargetsModal.test.tsx` (new)
- `dist/eval-ui/` (rebuild via `npm run build:ui`)
**Notes**: If the submit includes any Tier 3 agents, the modal passes their results to open `ClipboardExportDialog` (T-020) after the SSE stream ends. SSE consumer: use `EventSource` or `fetch` with streaming. Do NOT open a real SSE connection in unit tests — mock the API helper.

---

### T-020: New ClipboardExportDialog.tsx — blob pre-block, Copy button, paste-instructions link
**User Story**: US-005 | **AC**: AC-US5-04, AC-US5-05, AC-US5-07, AC-US5-08 | **Status**: [x] completed
**Domain**: frontend
**Test Plan**:
- Given a Tier 3 install result includes a blob and `pasteInstructionsUrl`
- When `ClipboardExportDialog` renders
- Then the blob is visible inside a `<pre>` block
- And a "Copy" button is visible
- And a link to `pasteInstructionsUrl` is visible
- Given the user clicks the "Copy" button
- When the click handler fires
- Then `navigator.clipboard.writeText(blob)` is called exactly once (user-gesture path, AC-US5-05)
- Given the dialog is for ChatGPT and no filesystem agents were selected
- When the dialog mounts
- Then no filesystem writes have occurred (AC-US5-07)
- Given mixed selection: Claude Code + Cursor + ChatGPT
- When all three installs complete
- Then the dialog opens for ChatGPT after Claude Code and Cursor filesystem writes are confirmed (AC-US5-08)
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ClipboardExportDialog.tsx` (new)
- `dist/eval-ui/` (rebuild via `npm run build:ui`)
**Notes**: The dialog renders AFTER the SSE stream from InstallTargetsModal closes. No background clipboard write (rejected by browsers without user gesture). Multiple Tier 3 targets = one dialog opened sequentially per target.

---

### T-021: Per-target result toast with mixed-outcome display
**User Story**: US-002, US-005 | **AC**: AC-US2-07, AC-US5-08 | **Status**: [x] completed
**Domain**: frontend
**Test Plan**:
- Given a multi-install completes with Claude Code=installed, Cursor=installed, Windsurf=error, ChatGPT=exported
- When the result toast renders
- Then it shows four rows:
  - Installed row for Claude Code with the written path
  - Installed row for Cursor with the `.mdc` path
  - Error row for Windsurf with the error message
  - Exported/clipboard row for ChatGPT with a "open paste instructions" link
- Given Windsurf=error
- When the toast renders
- Then the Claude Code and Cursor rows still show success — partial failure does not abort others (AC-US2-07)
- Given a Tier 3 scope-downgrade warning is in the ChatGPT `detail`
- When the toast renders
- Then the warning text is visible in the ChatGPT row
**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/InstallTargetsModal.tsx` (modified — add toast render after SSE stream closes)
- `dist/eval-ui/` (rebuild via `npm run build:ui`)
**Notes**: Reuse existing toast infrastructure if present in eval-ui. Each row is driven by one `AgentInstallResult` from the SSE stream.

---

### T-022: Wire skill detail "Install" button to open InstallTargetsModal
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**Domain**: frontend
**Test Plan**:
- Given the skill detail panel is open for an installable skill
- When the "Install" button (currently labeled "Active" in screenshot) is clicked
- Then `InstallTargetsModal` opens — no single-agent install fires
- Given the button had a keyboard shortcut before
- When the modal is open
- Then the same keyboard shortcut still functions (opens modal, not a legacy install)
- Given the user cancels the modal
- When they return to the skill detail panel
- Then the button state is unchanged (no spurious install was triggered)
**Files**:
- Identify component via `grep -rn "Active" repositories/anton-abyzov/vskill/src/eval-ui/src/components/` before editing
- Modified component file (modified — rewire `onClick` to set modal-open state)
- `dist/eval-ui/` (rebuild via `npm run build:ui`)
**Notes**: Identify the exact component before editing. Do NOT remove the existing button — rewire its `onClick` to set modal-open state.

---

## E2E + VERIFICATION

### T-023: Playwright E2E install-targets.spec.ts
**User Story**: US-001, US-002, US-005 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08, AC-US5-04, AC-US5-05, AC-US5-06, AC-US5-07, AC-US5-08 | **Status**: [x] completed
**Domain**: tests
**Test Plan**:
- Given a Studio instance booted with `process.env.HOME` pointing to a tmpdir
- When the user navigates to the obsidian-brain skill detail page and clicks "Install Globally"
- Then `InstallTargetsModal` opens (assert modal title contains "Install obsidian-brain to:")
- And Claude Code is the only pre-checked row
- Given the user checks Codex + Cursor + Antigravity + ChatGPT rows
- When Install is clicked
- Then the SSE stream begins and the modal shows per-agent progress
- When the stream ends
- Then filesystem assertions:
  - `<tmpHome>/.codex/skills/obsidian-brain/SKILL.md` exists with valid frontmatter
  - `<tmpHome>/.cursor/rules/obsidian-brain.mdc` exists with `alwaysApply: false` in frontmatter
  - `<tmpHome>/.gemini/antigravity/skills/obsidian-brain/SKILL.md` exists
  - No disk write under `<tmpHome>` for ChatGPT
- And `ClipboardExportDialog` opens for ChatGPT with blob visible
- When the user clicks "Copy"
- Then `navigator.clipboard.readText()` returns the blob (using `context.grantPermissions(['clipboard-read'])`)
- Given the user re-opens the modal and clicks "Clear"
- Then the Install button is disabled and clicking it fires no API request
**Files**:
- `repositories/anton-abyzov/vskill/tests/e2e/studio/install-targets.spec.ts` (new)
**Notes**: Boot Studio against tmpdir HOME. Use `page.route()` to mock the ChatGPT clipboard since no real clipboard API in headless Playwright by default. Assert Antigravity with env override `VSKILL_ANTIGRAVITY_SKILLS_DIR=<tmpHome>/.gemini/antigravity/skills` set before boot.

---

### T-024: Build sequence verification + smoke test
**User Story**: All | **AC**: All filesystem-write ACs | **Status**: [x] completed
**Domain**: tests
**Test Plan**:
- Given all prior tasks are complete and code is staged
- When the full build sequence runs:
  ```
  cd repositories/anton-abyzov/vskill
  npm run build
  npm run build:ui
  npx vitest run
  npx playwright test tests/e2e/studio/install-targets.spec.ts
  ```
- Then all steps exit with code 0
- Given `npx vskill studio` is started fresh
- When a skill is navigated to and "Install Globally" is clicked
- Then the InstallTargetsModal with three tier sections is visible
- When at least one Tier 1, one Tier 2, and one Tier 3 tool are checked and Install is clicked
- Then filesystem writes are confirmed for Tier 1 and Tier 2 targets
- And the ClipboardExportDialog opens for the Tier 3 target
- Given the same skill is re-installed
- Then output files are byte-identical (idempotency from user perspective)
**Files**: N/A (verification step only)
**Notes**: This is the mandatory gate before `/sw:done`. Run `npm run build:ui` before every UI-touching test. Manual gate for ChatGPT clipboard flow per CLAUDE.md "Manual Verification Gates" — paste the blob into ChatGPT Custom Instructions and confirm GPT acknowledges the skill on next turn.

---

## Execution Strategy Recommendation

**Recommended runner**: `sw:team-lead` with a 2-domain split.

- **Server-side agent** (Tasks T-001 through T-017): Foundation → Transformers → Install pipeline → Clipboard/Tier3 → Route extension. All in `src/agents/`, `src/installer/`, `src/eval-server/`.
- **Frontend agent** (Tasks T-018 through T-022): Can start after T-005 (supported-agents API) is done. All in `src/eval-ui/src/`.
- **E2E/verification agent** (Tasks T-023, T-024): Runs after both domains are complete.

**Parallelization within server-side**: T-006 through T-009 (transformers) are fully independent once T-001 and the `transformers/index.ts` interfaces exist. A sub-agent can run all four in parallel.

**Fallback**: `sw:do` sequential is safe but adds ~2x wall time as noted in plan.md §12.
