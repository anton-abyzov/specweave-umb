---
increment: 0845-cross-tool-skill-installation
title: Cross-tool skill installation in Skill Studio
type: feature
priority: P1
status: completed
created: 2026-05-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Cross-tool skill installation in Skill Studio

## Overview

Skill Studio (`vskill studio`) currently surfaces an install action only for agentic tools whose binary is on `$PATH`. The user has the obsidian-brain skill at https://verified-skill.com/skills/anton-abyzov/vskill/obsidian-brain and cannot install it on a machine running Codex CLI because Studio shows "NOT DETECTED" with no install button. Antigravity is missing from the picker entirely.

This increment delivers four changes to the vskill installer + eval-ui:

1. **Decouple installability from binary detection** — every non-cloud-only tool in the agent registry becomes installable regardless of whether its binary is on `$PATH`.
2. **Add an Install Targets modal** — a multi-select checkbox modal that lets a user install a skill to N tools in one click, with the currently-active tool pre-checked, a "Select all detected" convenience action, and validation requiring at least one selection.
3. **Add format transformers** for Tier 2 tools that don't natively accept Claude-style `SKILL.md` — Cursor (`.mdc`), Windsurf, GitHub Copilot (`.instructions.md`), Junie, Kiro, Continue.dev, Aider conventions, Trae.
4. **Add clipboard/export support** for Tier 3 cloud-only tools (ChatGPT Custom Instructions, ChatGPT Custom GPT, ChatGPT Project Instructions, v0, bolt.new) — outputs a paste-ready blob plus a link to the tool's paste-instructions documentation.

The reference design is captured in `/Users/antonabyzov/.claude/plans/misty-wishing-gadget.md` (approved via ExitPlanMode).

## User Stories

### US-001: Surface all supported tools as install targets (P1)
**Project**: vskill

**As a** Skill Studio user installing a published skill onto my machine
**I want** to see every agentic tool that supports skills listed as an install target, not only the ones whose binary happens to be on `$PATH`
**So that** I can install obsidian-brain onto Codex CLI (and other tools whose binary isn't detected) without leaving Studio.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `GET /api/studio/supported-agents` returns every `AgentDefinition` in the registry where `isRemoteOnly !== true`, each enriched with `{ id, displayName, detected: boolean, tier: 1|2|3, installMode: "filesystem"|"clipboard", resolvedGlobalDir, resolvedLocalDir }`. _(0845 T-003 added the `chatgpt` Tier 3 entry, so the registry now has 54 entries with 5 isRemoteOnly. The exclusion gate moved from `isRemoteOnly` to `installMode` so Tier 3 clipboard agents — chatgpt, bolt-new, v0 — surface alongside Tier 1/2 filesystem agents. devin + replit remain excluded as pure remote-only. Updated count: 52 agents returned.)_
- [x] **AC-US1-02**: The endpoint is distinct from `/api/studio/detected-agents` — calling `/api/studio/detected-agents` still returns only the subset with `detected: true` (no behavior change for existing callers).
- [x] **AC-US1-03**: In the Studio UI, `AgentScopePicker.Popover.tsx` renders three sections: "Detected on this machine", "Available to install", and "Cloud only (paste required)". The passive "Not Detected" section is removed. Given Codex CLI is supported but its binary is not on `$PATH`, when the picker opens, then Codex CLI appears under "Available to install" with a `+ Install here` inline CTA.
- [x] **AC-US1-04**: Each row in "Available to install" shows the resolved install path (e.g., `~/.codex/skills/<name>/SKILL.md`) so the user knows where files will be written.
- [x] **AC-US1-05**: Clicking `+ Install here` opens the Install Targets modal (US-002) pre-checked with that tool selected.
- [x] **AC-US1-06**: A tool flagged `isRemoteOnly: true` (Devin, Replit Agent) does NOT appear in any section — those remain link-out only.

---

### US-002: Install a skill to multiple tools in one click (P1)
**Project**: vskill

**As a** Skill Studio user who works across multiple agentic tools (Claude Code, Codex, Cursor) on the same machine
**I want** a checkbox modal that lets me pick any combination of supported tools and install a skill to all of them in one click
**So that** I don't have to repeat the install action once per tool.

**Acceptance Criteria**:
- [x] **AC-US2-01**: The "Install" button on the skill detail panel (the button labeled "Active" in the user's screenshot) opens the `InstallTargetsModal` instead of doing a single-agent install. The existing keyboard shortcut is preserved.
- [x] **AC-US2-02**: The modal title reads "Install <skill name> to:" and groups checkbox rows by tier: "Drop-in" (Tier 1), "Format-converted" (Tier 2), "Cloud only (paste required)" (Tier 3). Within each group, detected tools sort above undetected.
- [x] **AC-US2-03**: When the modal opens, only the currently-active tool (the tool whose scope the user is operating in) is pre-checked. All other rows start unchecked. Given the user is on Claude Code and clicks Install on a skill, when the modal opens, then Claude Code is checked and no other row is checked.
- [x] **AC-US2-04**: Quick action "Select all detected" checks every row whose `detected: true`. Quick action "Clear" unchecks every row. Both actions update validation state immediately.
- [x] **AC-US2-05**: The Install button is disabled when zero rows are selected. Given the user opens the modal and clicks "Clear", when the selection count is 0, then the Install button is disabled and shows a tooltip "Select at least one target".
- [x] **AC-US2-06**: Submitting the modal calls `POST /api/studio/install-skill` with body `{ skill, agentIds: string[], scope: "project" | "user" }` and opens an SSE progress stream that emits one event per agent: `{ agentId, status: "installed" | "exported" | "skipped" | "error", detail?: string }`.
- [x] **AC-US2-07**: After submit, a per-target result toast displays each outcome: ✓ Installed (<path>) for filesystem writes, ⧉ Copied to clipboard (open paste instructions →) for Tier 3, ✗ Error (<message>) for failures. A partial failure (one transformer throws) does NOT abort the others — every selected agent gets an outcome row.
- [x] **AC-US2-08**: Clicking Cancel closes the modal without firing any API call, mutating any state, or showing a toast.
- [x] **AC-US2-09**: The existing single-agent install flow remains backward-compatible: when `POST /api/studio/install-skill` is called with the legacy `agent: string` field (no `agentIds[]`), the route dispatches to the same single-agent path as today.

---

### US-003: Install to Antigravity with the correct path (P1)
**Project**: vskill

**As a** Skill Studio user running Google Antigravity
**I want** Antigravity to appear in the Install Targets modal and write SKILL.md to its expected directory
**So that** my skills load in Antigravity sessions without manual file copying.

**Acceptance Criteria**:
- [x] **AC-US3-01**: The `AgentDefinition` entry for Antigravity in `src/agents/agents-registry.ts` is verified present, NOT marked `isRemoteOnly: true`, classified as `tier: 1`, `installMode: "filesystem"`.
- [x] **AC-US3-02**: Antigravity's `globalSkillsDir` resolves to `~/.gemini/antigravity/skills/` and its `localSkillsDir` resolves to `.agent/skills/` (singular `agent` — matches the existing registry entry at `agents-registry.ts:255` and the binding `agents-registry-0845.test.ts` assertion at line 67; the earlier draft `.agents/skills/` was a typo corrected 2026-05-11 during the foundation phase). Given a skill named `obsidian-brain` is installed to Antigravity with scope=user, when the install completes, then `~/.gemini/antigravity/skills/obsidian-brain/SKILL.md` exists with the correct content. _(registry-level path resolution complete in T-002; actual install side-effect verified in Phase-2 multi-install.)_
- [x] **AC-US3-03**: An optional environment variable `VSKILL_ANTIGRAVITY_SKILLS_DIR` overrides the global path. Given `VSKILL_ANTIGRAVITY_SKILLS_DIR=/tmp/ag-test` is set, when a user-scope install runs, then the file is written under `/tmp/ag-test/obsidian-brain/SKILL.md`. _(env override honored by getSupportedAgents → resolvedGlobalDir in T-004; multi-install dispatch wires through in Phase-2.)_
- [x] **AC-US3-04**: Antigravity appears in the modal's "Drop-in" section regardless of binary detection (covered by US-001 contract but verified here for this specific agent).

---

### US-004: Format-converted install for Tier 2 tools (P1)
**Project**: vskill

**As a** Skill Studio user installing skills onto tools that don't natively accept Claude-style `SKILL.md`
**I want** my skill auto-converted to each tool's native format on install (Cursor `.mdc`, Windsurf, GitHub Copilot `.instructions.md`, Junie, Kiro, Continue.dev, Aider, Trae)
**So that** I author once in SKILL.md and consume everywhere without manual rewrites.

**Acceptance Criteria**:
- [x] **AC-US4-01**: The `AgentDefinition` interface gains four optional fields: `tier: 1 | 2 | 3`, `installMode: "filesystem" | "clipboard"`, `formatTransformer?: (parsedSkill) => TransformedFile[]`, `pasteInstructionsUrl?: string`. Registry entries without these fields default to `tier: 1`, `installMode: "filesystem"`, no transformer.
- [x] **AC-US4-02**: Eight transformer modules exist under `src/installer/transformers/`: `cursor.ts`, `windsurf.ts`, `github-copilot.ts`, `junie.ts`, `kiro.ts`, `continue-dev.ts`, `aider.ts`, `trae.ts`. Each exports a pure function `(parsedSkill) => TransformedFile[]` where `TransformedFile = { relativePath: string, content: string }`.
- [x] **AC-US4-03**: `cursor.ts` outputs a file at `.cursor/rules/<name>.mdc` with frontmatter `description: <original description>`, `globs: ""`, `alwaysApply: false`. Given a SKILL.md with `name: obsidian-brain` and `description: "PARA + LLM Wiki"`, when the Cursor transformer runs, then the output is one file at relative path `.cursor/rules/obsidian-brain.mdc` containing the three frontmatter keys above and the original body.
- [x] **AC-US4-04**: `windsurf.ts` outputs `.windsurf/rules/<name>.md` with all frontmatter stripped (plain markdown body only).
- [x] **AC-US4-05**: `github-copilot.ts` outputs `.github/instructions/<name>.instructions.md` with frontmatter `applyTo: "**"` and the original body.
- [x] **AC-US4-06**: `junie.ts` outputs `.junie/rules/<name>.md` as plain markdown; `kiro.ts` outputs `.kiro/steering/<name>.md`; `continue-dev.ts` outputs `.continue/rules/<name>.md`; `trae.ts` outputs `.trae/<name>.md`. All four strip frontmatter.
- [x] **AC-US4-07**: `aider.ts` is special — it returns TWO files: (1) `~/.aider/conventions/<name>.md` (plain markdown) and (2) a mutation directive against `~/.aider.conf.yml` to append the convention path to the `read:` list. The installer applies the mutation via a backup-write pattern: writes `~/.aider.conf.yml.bak` first, then parses the YAML, appends the entry only if not already present, then writes back. A `.bak` collision uses `.bak.1`, `.bak.2`, etc. — never overwrites an existing backup.
- [x] **AC-US4-08**: `installSkillToMultipleAgents` in `src/installer/multi-install.ts` invokes the transformer when `AgentDefinition.formatTransformer` is set; otherwise it falls back to the existing `installSymlink` / `installCopy` flow in `src/installer/canonical.ts`. Tier 1 tools (Claude Code, Codex CLI, OpenClaw, OpenCode, Antigravity, Gemini CLI) go through the existing path with zero behavior change.
- [x] **AC-US4-09**: Re-installing the same skill to the same tool overwrites the file cleanly — no duplicate frontmatter blocks, no appended sections. Given Cursor install runs twice for obsidian-brain, when the second install completes, then `.cursor/rules/obsidian-brain.mdc` has exactly one frontmatter block and is byte-identical to the first run.
- [x] **AC-US4-10**: A transformer that throws on malformed frontmatter fails ONLY its own target — other selected agents complete. Given the user selects Cursor + Windsurf + Junie and the Windsurf transformer throws, when the install runs, then Cursor and Junie return `status: "installed"` and Windsurf returns `status: "error"` with the throw message in `detail`.
- [x] **AC-US4-11**: All filesystem writes resolve under the agent's `globalSkillsDir` (scope=user) or `localSkillsDir` (scope=project). Given a transformer produces a relative path, when the install writes the file, then `path.relative(agentDir, absoluteWritePath)` does NOT start with `..` (no path traversal — same guard used in canonical.ts:21).
- [x] **AC-US4-12**: On Windows, agents with a `win32PathOverride` field use that path instead of the POSIX `globalSkillsDir` (the field already exists in registry entries).

---

### US-005: Clipboard / export support for cloud tools (P1)
**Project**: vskill

**As a** Skill Studio user who works with ChatGPT, v0, or bolt.new where there's no local filesystem to install into
**I want** the modal to offer those tools as paste-able blobs with a Copy button and a link to the tool's paste-instructions
**So that** I can use my Skill Studio skills in cloud agentic tools without a separate workflow.

**Acceptance Criteria**:
- [x] **AC-US5-01**: Tier 3 tools appear in the modal under "Cloud only (paste required)": ChatGPT Custom Instructions, ChatGPT Custom GPT, ChatGPT Project Instructions, v0 (Knowledge), bolt.new (first-message paste).
- [x] **AC-US5-02**: Each Tier 3 row shows "Copy to clipboard" instead of a filesystem path.
- [x] **AC-US5-03**: `POST /api/studio/export-skill` accepts `{ skill, agentId }` and returns `{ tool, blob: string, pasteInstructionsUrl: string, docsUrl?: string }`. The endpoint does NOT write to disk — there is no filesystem side effect for Tier 3.
- [x] **AC-US5-04**: After install submit, if any Tier 3 target was selected, a `ClipboardExportDialog` opens for each. The dialog renders the blob inside a `<pre>` block, exposes a "Copy" button, and a link to `pasteInstructionsUrl`.
- [x] **AC-US5-05**: The Copy button calls `navigator.clipboard.writeText(blob)` only on a user gesture (the click handler). No background clipboard write is attempted (which would be blocked by browsers).
- [x] **AC-US5-06**: When project-scope is selected for a Tier 3 tool, the install gracefully downgrades to user-scope — the blob is still produced and a toast warns "ChatGPT does not support project-scoped skills; exported as user-scope blob." The result status is `exported`, not `error`.
- [x] **AC-US5-07**: Selecting ONLY Tier 3 targets (no Tier 1/2) skips disk writes entirely. Given the user checks ChatGPT Custom Instructions and clicks Install, when the request completes, then `agentIds[]` includes only the ChatGPT id, no filesystem writes occur, and the ClipboardExportDialog opens directly.
- [x] **AC-US5-08**: Mixed selection works as expected: Given the user selects Claude Code + Cursor + ChatGPT, when the install runs, then Claude Code is symlinked, Cursor's `.mdc` file is written, and the ChatGPT clipboard dialog opens after — all three result statuses appear in the toast.

---

### US-006: Decouple install picker from binary detection (P2)
**Project**: vskill

**As a** vskill maintainer
**I want** the install picker driven by registry membership, not by binary detection probes
**So that** adding a new tool (or fixing a path) requires only a registry update — no UI changes, no detection logic to maintain in two places.

**Acceptance Criteria**:
- [x] **AC-US6-01**: The `AgentScopePicker.Popover.tsx` component does NOT contain a hardcoded list of tool ids. All sections are derived from the response of `/api/studio/supported-agents`. Given a new `AgentDefinition` is added to the registry without `isRemoteOnly: true`, when the picker renders, then the new tool appears in the appropriate tier section automatically.
- [x] **AC-US6-02**: Detection latency is bounded: each `detectBinary` probe in the `/api/studio/supported-agents` handler runs in parallel and is capped (existing detection infra honored). Tools whose detection times out are returned with `detected: false` but still appear in the picker.
- [x] **AC-US6-03**: The existing `detectInstalledAgents()` function in `agents-registry.ts:853` is unchanged — its callers continue to receive the detected-only subset. The new picker logic uses a different code path that includes undetected supported agents.

---

## Functional Requirements

### FR-001: Backward compatibility
The legacy single-agent install path (`POST /api/studio/install-skill` with `{ agent: string }`) MUST continue to function. Existing CLI commands and any external callers must not break.

### FR-002: Sequential per-agent execution
Multi-agent installs execute sequentially (not in parallel) for predictable filesystem state and deterministic test assertions. N ≤ 12 tools makes sequential acceptable; latency budget per agent is ≤ 200ms.

### FR-003: Idempotency
Every transformer output is fully deterministic given the same input. Re-installs overwrite cleanly; no append, no duplicate frontmatter, no orphan files.

### FR-004: Path safety
All filesystem writes resolve under the target agent's `globalSkillsDir` or `localSkillsDir`. Path traversal is rejected (existing `path.relative()` guard reused).

### FR-005: Aider config safety
Mutations to `~/.aider.conf.yml` use backup-write: `.bak` (with collision-safe `.bak.1`, `.bak.2` suffix) before edit; append-only; YAML-parse before write; never replace pre-existing entries.

### FR-006: SSE progress stream
The install route streams per-agent progress events so the UI can render a live result toast. Stream emits one event per agent in the order they execute, then a terminal `{ done: true }` event.

### FR-007: Localhost-only endpoints
All new routes (`/api/studio/supported-agents`, `/api/studio/export-skill`, extended `/api/studio/install-skill`) follow the existing eval-server localhost-only architecture. Same `SAFE_NAME` validation extends to every entry in `agentIds[]`.

## Success Criteria

- A user can open obsidian-brain in Skill Studio on a machine with Codex installed (but `codex` binary not on `$PATH`) and successfully install it to Codex CLI via the modal — no manual file editing required.
- A user can install a single skill to Claude Code + Cursor + Windsurf + ChatGPT in one click and see four result rows in the post-install toast.
- Antigravity appears in the picker and writes to `~/.gemini/antigravity/skills/` correctly.
- All eight Tier 2 transformers emit byte-identical output on re-install (idempotency).
- E2E Playwright test `studio/install-targets.spec.ts` passes end-to-end against a tmpdir-rooted filesystem.
- Unit test coverage ≥ 90% across new transformer modules and `installSkillToMultipleAgents`.

## Out of Scope

- Marketplace/registry changes on verified-skill.com (server-side skill catalog stays the same).
- Skill authoring UX changes — the Skill Studio's "+ New Skill" / editor flow is untouched.
- Detection probe improvements for individual binaries (e.g., adding new search paths for `codex`). Detection is intentionally decoupled from installability.
- Changes to increment 0843 (workspace-tree) — runs in parallel, no shared files.
- Per-tool skill format AUTHORING guidance (e.g., teaching users how to write a Cursor `.mdc` natively). This increment converts at install time, not at author time.
- Telemetry / analytics on which tools users install to (out of scope; can be added later).

## Dependencies

- vskill repo: `src/agents/agents-registry.ts` (53 existing AgentDefinition entries, including Codex, Antigravity, Cursor, Windsurf, etc. — verified by Phase 1 research).
- vskill repo: existing installer primitives — `parseFrontmatter`, `ensureFrontmatter`, `stripClaudeFields` (`src/installer/frontmatter.ts`); `installSymlink`, `installCopy` (`src/installer/canonical.ts`); `detectBinary` (`src/utils/resolve-binary.ts`).
- vskill repo: existing SSE infra in `src/eval-server/install-skill-routes.ts:30-85`.
- vskill repo: React eval-ui served from pre-built bundle at `dist/eval-ui/` (NOT Vite dev — per project memory `project_vskill_studio_runtime.md`). UI changes require `npm run build:ui`.
- No external service dependencies, no schema migrations, no new authentication surfaces.
