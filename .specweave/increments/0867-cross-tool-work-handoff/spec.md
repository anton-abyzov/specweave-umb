---
increment: 0867-cross-tool-work-handoff
title: Cross-Tool Work Handoff
type: feature
priority: P1
status: completed
created: 2026-06-01T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Cross-Tool Work Handoff

## Overview

A portable **work handoff** lets a developer stop work in one AI coding tool — typically when running low on subscription tokens — and continue in another (Claude Code, Codex, OpenCode, Gemini, Antigravity, or Cursor), on **any** project, picking up exactly where they left off.

No AI coding tool can read another's transcript (each locks its session in a proprietary `.jsonl`, SQLite DB, or encrypted `.pb`). The only portable thing is a **self-contained handoff document**. SpecWeave already knows everything a resume needs — active increment, task/AC state, decisions, ambient rules — but never assembles it into one resumable artifact, and there is nothing for non-SpecWeave projects at all.

Architecture (decided, mirrors the proven `verify` pattern): a **core engine** (`specweave handoff` CLI subcommand) does all expensive, deterministic assembly + secret scrub + free full-diff dump; a **thin `/sw:handoff` command + skill** shells to it inside Claude Code; and a **self-contained vskill `handoff` skill** distributes the capability to all other tools, calling `specweave handoff` only as an optional accelerator. All paths emit the **same doc format + same paste-prompt**, so a handoff written in Claude Code is continuable in Codex unchanged. A PreCompact hook auto-writes a handoff so one survives even a token crash.

## Problem

When a developer exhausts their token budget on Tool A mid-task, the in-flight context (goal, current task, decisions made, uncommitted edits) is trapped in that tool's proprietary session store. Switching to Tool B (a different subscription, or a free tier) means re-explaining everything from scratch — and uncommitted edits are invisible to the new tool. There is no portable, tool-agnostic artifact that captures "where I am" so any AI agent can resume cleanly. SpecWeave has all the durable state on disk but never serializes it; non-SpecWeave projects have nothing.

## Goal

One command (`/sw:handoff` in Claude Code, or the installed `handoff` skill in any other tool) writes a durable, secret-scrubbed handoff doc plus a full diff of uncommitted edits, prints the absolute path + a clickable link + a copy-paste resume prompt, and works on any project — SpecWeave or not. A PreCompact/Stop hook auto-writes one so a handoff survives context exhaustion. The doc — not any tool's transcript — is the portable context.

## User Stories

### US-001: Generate a portable handoff doc in Claude Code (P1)
**Project**: specweave

**As a** developer running low on tokens in Claude Code on a SpecWeave project
**I want** `/sw:handoff` to assemble my current work state into one portable document
**So that** I can hand the work to another AI tool without re-explaining anything.

**Acceptance Criteria**:
- [x] **AC-US1-01**: A `/sw:handoff [incrementId] [--reason --summary --next --gotcha --decision]` command exists and runs end-to-end, shelling to the `specweave handoff` CLI subcommand.
- [x] **AC-US1-02**: The command output leads with the **absolute doc path as plain text FIRST**, then a clickable markdown link, then the `.diff` path, then a fenced copy-paste resume prompt, then per-tool "find your source session" tips — in that order.
- [x] **AC-US1-03**: SpecWeave workspace is detected via `resolveEffectiveRoot()` + reading `.specweave/state/active-increment.json` — NOT a raw `.specweave/` directory-presence test (so a stale child-repo `.specweave/` does not misclassify).
- [x] **AC-US1-04**: The handoff doc is written to `.specweave/increments/{id}/reports/handoff.md` (honoring the increment-root-file rule) AND a stable convenience copy to `.specweave/state/handoff-latest.md`.
- [x] **AC-US1-05**: The doc contains the active increment id + status, the current task and the next pending task, done vs pending tasks and ACs with counts/percentage (via `parseTasksWithUSLinks` + `calculateProgressFromTasksFile`), the `acSyncEvents` AC/task drift from `metadata.json`, key decisions from `plan.md`, and ambient rules from `config.json` (test mode, coverage target, WIP limit).
- [x] **AC-US1-06**: `getActive()` is handled as the `string[]` it returns: length 1 → use it; length 0 → write a git+config-only doc noting "no active increment"; length 2+ → require the explicit `incrementId` arg and, if absent, error with a message listing the candidate ids.
- [x] **AC-US1-07**: Re-running the command overwrites the same files (idempotent refresh); the operation is read-only except for the doc, the `.diff`, and gitignore entries it writes — zero network.

---

### US-002: Use the handoff skill inside other AI tools (P1)
**Project**: vskill

**As a** developer continuing work in Codex, OpenCode, Gemini, or Cursor
**I want** the `handoff` skill to work natively in that tool, without requiring SpecWeave to be installed
**So that** the cross-tool capability actually reaches the tools I am switching between.

**Acceptance Criteria**:
- [x] **AC-US2-01**: A `handoff` skill exists in vskill (`skills/handoff/SKILL.md`) and is distributed by `emitSkill()` to all transpile targets (codex, opencode, cursor, gemini-cli, github-copilot, antigravity, …).
- [x] **AC-US2-02**: The SKILL.md is **self-contained**: the handoff doc template is inlined in the skill body (the emitter does NOT copy sibling files), so the skill has NO hard dependency on specweave being installed.
- [x] **AC-US2-03**: The skill calls `specweave handoff` only as an **optional accelerator** when the binary is on PATH; otherwise it builds a byte-compatible doc from `git` state plus a short interview using only shell — verified that the resulting doc matches the CLI doc format.
- [x] **AC-US2-04**: A handoff doc written by Claude Code (`specweave handoff`) and one written by the vskill skill in another tool produce the **same doc format and same paste-prompt**, so either is continuable in the other tool unchanged.
- [x] **AC-US2-05**: The skill `version` is set to `"1.0.0"` and the slug `handoff` (and sw-plugin namespace `sw/handoff`) is reserved without collision.

---

### US-003: Graceful degrade on non-SpecWeave projects (P1)
**Project**: specweave

**As a** developer on an ordinary git project with no `.specweave/` workspace
**I want** the handoff to still capture my work via git state plus a short interview
**So that** the feature works on **any** project, not only SpecWeave ones.

**Acceptance Criteria**:
- [x] **AC-US3-01**: When `resolveEffectiveRoot()` / `active-increment.json` resolution finds no SpecWeave workspace (absent or empty even if a stale `.specweave/` dir exists), the command skips all increment reads and degrades to git-state + a short interview for the non-derivable fields.
- [x] **AC-US3-02**: The non-SpecWeave doc is written to `.handoff/HANDOFF.md` at the repo root, with the full in-flight diff at `.handoff/handoff.diff`.
- [x] **AC-US3-03**: A `.handoff/.gitignore` containing `*` is self-created on first write, so neither the doc, the diff, nor any scrubbed secrets enter git by default.
- [x] **AC-US3-04**: An ownership sentinel refuses to overwrite a foreign root `./HANDOFF.md` that lacks the `Doc format v1` footer marker — in that case it writes to `.handoff/HANDOFF.md` instead, never clobbering a project's own HANDOFF file.
- [x] **AC-US3-05**: The absolute path of whatever was written is printed first, as plain text, regardless of which fallback path was chosen.

---

### US-004: Capture uncommitted in-flight edits (P1)
**Project**: specweave

**As a** developer with unsaved changes when I hand off
**I want** the exact uncommitted edits captured, not just filenames
**So that** the next agent can see precisely what I changed without re-deriving it.

**Acceptance Criteria**:
- [x] **AC-US4-01**: The full `git diff` concatenated with `git diff --cached` is dumped to a sibling `.diff` file (`.specweave/state/handoff-latest.diff` for SpecWeave, `.handoff/handoff.diff` otherwise) — captured for free via git, with no LLM tokens spent.
- [x] **AC-US4-02**: The handoff doc links to the `.diff` by absolute path and instructs the next agent to read it or run `git apply --check` to see the exact uncommitted edits.
- [x] **AC-US4-03**: `git status --porcelain` and `git diff --stat` are shown inline in the doc's "Files Touched / UNCOMMITTED" section (filenames + line counts), with the full edits deferred to the `.diff` file so the markdown stays small.
- [x] **AC-US4-04**: When there are uncommitted changes, the doc shows a warning advising the next agent to commit, stash, or continue editing before doing anything destructive.

---

### US-005: Per-tool resume guidance + cross-machine safety (P1)
**Project**: specweave

**As a** developer resuming in a specific tool (possibly on a different machine)
**I want** exact "find your source session" commands per tool and a paste-prompt that fails safe when the path is missing
**So that** I can optionally recover the raw transcript and never let the new agent improvise wrong context.

**Acceptance Criteria**:
- [x] **AC-US5-01**: The resume output includes a per-tool "find your source session" block with the verified commands: Claude `claude -r <uuid>`, Codex `codex resume <uuid>` (and `--last`; NO `--continue`), OpenCode `opencode -s <id>` (long form `--session`), Gemini `/chat resume <tag>`, Antigravity Agent Manager, Aider `aider --restore-chat-history`.
- [x] **AC-US5-02**: The Claude munge rule is documented with an explicit double-dash example (every non-alphanumeric char → `-`, runs NOT collapsed; e.g. `.../specweave-umb/.claude-worktrees/...` → `-...-specweave-umb--claude-worktrees-...`).
- [x] **AC-US5-03**: The paste-prompt instructs the resuming agent that, if the doc path does NOT exist on the current machine, it must **STOP and ask the user to paste the handoff** rather than improvise.
- [x] **AC-US5-04**: `--inline` / `--clipboard` mode embeds the FULL scrubbed doc body inside the paste-prompt (between BEGIN/END markers) for cross-machine resume where the file is unreachable.
- [x] **AC-US5-05**: A build-time pin test (`cross-tool-commands.test.ts`) asserts one resume command string + key path per tool, so the matrix cannot silently drift when those CLIs update — covering the Claude double-dash munge and the OpenCode `-s` flag.

---

### US-006: Secret scrubbing and gitignore by default (P1)
**Project**: specweave

**As a** developer handing off work that touched API keys or secrets
**I want** the doc and diff scrubbed and gitignored by default
**So that** generating a handoff never leaks credentials into a file or git history.

**Acceptance Criteria**:
- [x] **AC-US6-01**: Before any write, a regex secret scrub runs over BOTH the free-text fields AND the captured diff for these patterns: `sk-`, `ghp_`, `gho_`, `ghs_`, `AKIA`, `ASIA`, `-----BEGIN`, `vsk_`, `xox[bap]-`, `Bearer `, `password=`, `api_key=` — replacing matches with a `[REDACTED-<type>]` marker.
- [x] **AC-US6-02**: Per-pattern redaction counts are recorded in a "Redaction" section of the doc (e.g. "3 token-like strings masked in handoff.diff").
- [x] **AC-US6-03**: The gitignore generator (`GITIGNORE_ENTRIES.specweave`) is extended to include `.handoff/` and `.specweave/state/handoff-latest.*`; the non-SpecWeave path self-creates `.handoff/.gitignore` = `*`.
- [x] **AC-US6-04**: The handoff is gitignored / NOT auto-committed by default; no `git add` hint that would push secrets to a remote is printed.
- [x] **AC-US6-05**: The "Redaction" section notes that scrubbing is heuristic — an empty redaction list is NOT a guarantee the file is clean — and the doc advises reviewing before sharing or committing.

---

### US-007: Auto-trigger on PreCompact and gated Stop (P1)
**Project**: specweave

**As a** developer whose session may die at context exhaustion before I explicitly run handoff
**I want** a handoff to be auto-written when context is about to be compacted
**So that** a handoff doc + diff always exist even if I never call the command.

**Acceptance Criteria**:
- [x] **AC-US7-01**: A real `pre-compact` handler is registered in `hook-router.ts` (currently a safe no-op) so that on PreCompact a handoff doc + `.diff` are written with whatever short fields the agent last stated (may be empty).
- [x] **AC-US7-02**: A `stop` variant of the handler is registered and gated (PreCompact fires always; Stop fires only under an `--auto`/handoff session flag) so turn-end writes are not noisy.
- [x] **AC-US7-03**: The hook handler invokes the same `buildWorkHandoff` builder as the CLI (single code path), so an auto-generated doc is byte-compatible with a manually generated one.
- [x] **AC-US7-04**: The agent passes only ~5 short strings as args (reason, summary, next, gotcha, decision) so the trigger stays cheap even at token exhaustion; the CLI does all expensive deterministic assembly + the free diff dump.
- [x] **AC-US7-05**: `plugins/specweave/hooks/hooks.json` already wires the PreCompact + Stop arrays to the `specweave hook` dispatcher; no structural change is needed there — the behavior comes from the new router handler.

---

### US-008: Living-doc page + verified-skill.com marketing angle (P2)
**Project**: specweave

**As a** prospective user discovering the handoff feature
**I want** a documentation page with the cross-tool matrix and the marketing positioning
**So that** I understand what the feature does and find it via search.

**Acceptance Criteria**:
- [x] **AC-US8-01**: A living-doc page (`docs/.../handoff.md`) is created containing the full cross-tool matrix table (Tool | session storage path | find current session | native resume cmd | export/transferable) for Claude Code, Codex, OpenCode, Gemini, Antigravity, Cursor, Aider, Cline/Roo, Windsurf, and SpecWeave.
- [x] **AC-US8-02**: The page includes the verified-skill.com SEO/marketing angle: lead card "**Works in 8+ tools**" and the headline "Run out of tokens? Hand off your work to any AI tool — pick up exactly where you left off, uncommitted edits and all."
- [x] **AC-US8-03**: The page features the four differentiator moats: captures uncommitted edits (not just filenames), survives a token crash (auto-trigger), secret-scrubbed + gitignored by default, and cross-machine `--inline` mode.
- [x] **AC-US8-04**: The page includes the long-tail SEO keywords (e.g. "switch from Claude Code to Codex mid-task", "out of tokens Claude continue elsewhere", "opencode export session", "continue AI session on another machine", "portable AI context handoff").

## Functional Requirements

### FR-001: Core engine (`specweave handoff`)
A deterministic CLI subcommand `specweave handoff [incrementId] [--reason --summary --next --gotcha --decision] [--inline|--clipboard] [--non-specweave] [--out <path>] [--json]` that does all expensive assembly: workspace detection, increment/task/AC parsing via existing parsers, git state capture, full-diff dump, secret scrub, doc + paste-prompt rendering, and ordered stdout. New modules under `src/core/session/`: `work-handoff.ts` (builder), `handoff-git-state.ts` (git capture + diff dump), `handoff-secret-scrub.ts` (regex redaction), `handoff-doc-format.ts` (single-source-of-truth renderer). The existing unrelated `handoff-context.ts` (plugin-install code) is NOT extended; optionally renamed `install-handoff-context.ts` to remove the name collision.

### FR-002: Reuse existing parsers (DRY)
The builder reuses `parseTasksWithUSLinks` (`task-parser.ts`), `calculateProgressFromTasksFile` (`us-progress-tracker.ts`), `ActiveIncrementManager.getActive()`, `MetadataManager.read()`, `resolveEffectiveRoot()`, and `GITIGNORE_ENTRIES.specweave` — no re-implementation of increment/task/AC/workspace logic.

### FR-003: Single doc format across all paths
`handoff-doc-format.ts` is the single source of truth for the doc template + paste-prompt and is consumed by the CLI, the hook handler, and vitest, so the format cannot drift. The vskill skill inlines a byte-compatible template.

## Success Criteria

- `npx vitest run` in specweave passes, including new tests for SpecWeave 1/0/2+-active increments, non-SpecWeave fallback, uncommitted `.diff` capture, `acSyncEvents` surfaced, secret scrub redacting planted `sk-`/`ghp_`/`Bearer` strings, stale-orphan-`.specweave` ignored, and the ownership sentinel refusing a foreign `HANDOFF.md`.
- Manual: from the umbrella repo, `specweave handoff` picks the right active increment (handling 2+), writes to `reports/`, scrubs a planted `sk-` key, dumps a real `.diff`, and prints abs-path-first output + paste-prompt. In a non-git/non-specweave temp dir it falls back to `.handoff/` + `.gitignore`.
- Cross-tool smoke: vskill emits the `handoff` skill, installs into a Codex/OpenCode dir, and the SKILL.md is self-contained (no specweave dependency) with the inlined template rendering correctly.
- The pin test (`cross-tool-commands.test.ts`) asserts the resume strings match the live CLIs.

## Out of Scope

- A machine-readable `handoff.json` sidecar (deferred to v1.1).
- Shelling out to external secret scanners (gitleaks/trufflehog) — regex baseline only for v1; opportunistic scanner support is a later enhancement.
- A `--commit` mode that force-adds the scrubbed `.handoff/` to travel via the git remote — `--inline` is the only cross-machine path for v1.
- Auto-distilling last-N turns from each tool's own transcript store beyond best-effort where a cheap CLI exists.

## Dependencies

- specweave core parsers and helpers (`task-parser.ts`, `us-progress-tracker.ts`, `active-increment-manager.ts`, `metadata-manager.ts`, `find-project-root.ts`, `gitignore-generator.ts`, `hook-router.ts`).
- vskill `emitSkill()` skill-emitter for cross-tool distribution.
- An installed `git` binary for state capture (the only external runtime dependency; degrades gracefully on the non-SpecWeave path).
