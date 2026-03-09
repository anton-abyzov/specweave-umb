---
increment: 0459-skill-eval-enhancements
title: "Skill Eval UI Enhancements"
type: feature
priority: P1
status: active
created: 2026-03-09
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Skill Eval UI Enhancements

## Problem Statement

The vskill Skill Eval UI provides benchmarking and A/B comparison capabilities, but skill developers lack visibility into the skill definition itself, have no AI-assisted iteration workflow, cannot compare different models on the same test case, and have no awareness of MCP server dependencies required by their skills. These gaps slow down the skill development and iteration cycle.

## Goals

- Make SKILL.md content prominently visible on the SkillDetailPage so developers can read and reference it while iterating
- Enable AI-powered skill improvement with diff-based review and one-click apply
- Allow per-test-case model comparison to identify which model performs best on specific eval scenarios
- Surface MCP server dependencies automatically from SKILL.md content with copy-ready configuration

## User Stories

### US-001: Skill Definition Viewer
**Project**: vskill
**As a** skill developer
**I want** to see the SKILL.md content prominently on the skill detail page with parsed frontmatter metadata
**So that** I can reference the skill definition while editing eval cases and reviewing benchmark results

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a skill with SKILL.md containing YAML frontmatter, when the SkillDetailPage loads, then the frontmatter fields (description, allowed-tools, model, context) are displayed as structured metadata cards above the body content
- [x] **AC-US1-02**: Given a skill with SKILL.md, when the page loads, then the markdown body (after frontmatter) is displayed in a styled monospace block below the metadata cards
- [x] **AC-US1-03**: Given the `allowed-tools` frontmatter field contains tool names, when rendered, then each tool name appears as an individual pill/chip tag
- [x] **AC-US1-04**: Given a SKILL.md with no YAML frontmatter (raw markdown only), when the page loads, then only the body content block is shown with no metadata cards and no errors
- [x] **AC-US1-05**: Given the skill definition viewer section, when the user interacts with it, then it is collapsible and defaults to expanded on page load

---

### US-002: AI-Powered Skill Improvement
**Project**: vskill
**As a** skill developer
**I want** to send my SKILL.md and benchmark failures to an LLM and receive a suggested improved version with a visual diff
**So that** I can iterate on skill quality using AI assistance without manually analyzing failures

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the SkillDetailPage, when the user clicks "Improve Skill", then a panel appears with a model picker (supporting all configured providers: claude-cli, anthropic, ollama) and an "Improve" action button
- [x] **AC-US2-02**: Given the improvement is requested, when the backend processes it, then `POST /api/skills/:plugin/:skill/improve` reads the current SKILL.md, auto-includes up to 10 most recently failed assertions from the latest benchmark, constructs an improvement prompt, calls the selected LLM, and returns `{ original, improved, reasoning }`
- [x] **AC-US2-03**: Given the improvement response is received, when displayed, then a unified diff view shows line-by-line changes (green for added lines, red for removed lines) computed on the frontend without external diff libraries
- [x] **AC-US2-04**: Given the diff is displayed, when the user clicks "Apply", then `POST /api/skills/:plugin/:skill/apply-improvement` writes the improved content back to SKILL.md on disk, the viewer updates to reflect the new content, and a success confirmation is shown
- [x] **AC-US2-05**: Given the diff is displayed, when the user clicks "Discard", then the improvement panel closes and no changes are written to disk

---

### US-003: Per-Test-Case Model A/B Comparison
**Project**: vskill
**As a** skill developer
**I want** to compare two different models on the same eval test case
**So that** I can identify which model performs best for specific scenarios and make informed model selection decisions

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given an eval case on the SkillDetailPage, when the user clicks "Compare Models", then a modal appears with two model selectors (Model A and Model B) allowing independent provider and model selection
- [x] **AC-US3-02**: Given both models are selected and the comparison starts, when executing, then models run sequentially (Model A first, then Model B) with progress indicators showing which model is currently running (e.g., "Model A running..." then "Model A done, Model B running...")
- [x] **AC-US3-03**: Given both models complete, when results are displayed, then the modal shows side-by-side output with assertion pass/fail results for each model, duration, and token counts
- [x] **AC-US3-04**: Given the backend endpoint `POST /api/skills/:plugin/:skill/compare-models` receives `{ eval_id, modelA: { provider, model }, modelB: { provider, model } }`, when processing, then it uses `createLlmClient(overrides)` for each model, runs the eval case with the skill's system prompt, judges assertions for both outputs, and streams results via SSE
- [x] **AC-US3-05**: Given a model comparison completes, when results are shown, then the results are ephemeral (not saved to benchmark history) and the modal can be dismissed

---

### US-004: Skill Dependency Visibility (MCP + Skill-to-Skill)
**Project**: vskill
**As a** skill developer
**I want** to see which MCP servers and other skills my skill depends on, based on tool patterns and skill references in SKILL.md
**So that** I can ensure proper MCP configuration and prerequisite skills are installed before testing and deploying

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a SKILL.md that references tool patterns matching known MCP servers (slack_*, github_*, linear_*, gws_*, drive_*, gmail_*, sheets_*, calendar_*, chat_*), when the SkillDetailPage loads, then detected MCP dependencies are shown in a dedicated section with server name, matched tools, and MCP server URL
- [x] **AC-US4-02**: Given the `allowed-tools` YAML frontmatter field lists tool names, when parsed, then those tool names are also matched against the known MCP pattern registry for dependency detection
- [x] **AC-US4-03**: Given a detected MCP dependency, when the user clicks "Copy Config", then a Claude Code `.mcp.json` configuration snippet is copied to the clipboard (e.g., `{ "mcpServers": { "slack": { "type": "http", "url": "https://mcp.slack.com/mcp" } } }`)
- [x] **AC-US4-04**: Given the backend endpoint `GET /api/skills/:plugin/:skill/dependencies`, when called, then it returns both detected MCP servers (names, URLs, matched tool patterns, setup instructions) and detected skill-to-skill dependencies (skill names referenced in SKILL.md content via patterns like `/skill-name`, `use the ... skill`, or explicit `dependencies` frontmatter)
- [x] **AC-US4-05**: Given a SKILL.md with no MCP tool patterns or skill references detected, when the page loads, then the dependencies section shows an appropriate empty state (e.g., "No dependencies detected")
- [x] **AC-US4-06**: Given a SKILL.md that references other skills by name (e.g., "use the scout skill" or "chains with social-media-posting"), when the dependencies section renders, then referenced skills are listed with their names and links to their detail pages if they exist in the current plugin set

## Out of Scope

- Persisting model comparison results to benchmark history (Feature 3 results are ephemeral)
- Auto-installing or connecting MCP servers (Feature 4 is read-only detection and config copy)
- Multi-turn improvement conversations (Feature 2 is single-shot improve, not iterative chat)
- Concurrent model execution in Feature 3 (sequential only due to claude-cli constraints)
- External diff libraries for Feature 2 (frontend-only line-by-line diff)
- New runtime dependencies on the backend (Node.js http module only)
- Editing SKILL.md directly in the UI (only AI-suggested improvements can be applied)

## Technical Notes

### Dependencies
- Existing `createLlmClient(overrides?: { provider, model })` for per-request model switching
- Existing `GET /api/skills/:plugin/:skill` endpoint returns `{ skillContent }` (no backend changes for Feature 1)
- Existing SSE infrastructure (`initSSE`, `sendSSE`, `sendSSEDone`) for streaming results

### Constraints
- Zero new runtime deps on backend (Node.js http module only)
- All `.ts` imports must use `.js` extensions in server code (`nodenext` moduleResolution)
- Frontend uses bundler resolution (Vite) -- `.js` extensions not required
- `api-routes.ts` is 719 lines -- new endpoints MUST go in separate route files
- `SkillDetailPage.tsx` is 818 lines -- new UI MUST go in separate components
- Sequential model execution for Feature 3 (120s timeout per model call)
- Improvement prompt limited to 10 most recently failed cases (context window safety)
- TDD mode enforced (RED -> GREEN -> REFACTOR)

### Architecture Decisions
- New backend endpoints in `src/eval-server/skill-improve-routes.ts` and `src/eval-server/model-compare-routes.ts`
- MCP detection as pure function in `src/eval-server/mcp-detector.ts` with its own route file `src/eval-server/mcp-routes.ts`
- New UI components: `SkillDefinitionViewer.tsx`, `SkillImprovePanel.tsx`, `ModelCompareModal.tsx`, `McpDependencies.tsx`
- Frontend diff computation via simple line-by-line comparison (no external library)
- Hardcoded MCP pattern registry combined with `allowed-tools` frontmatter parsing

## Success Metrics

- Skill definition viewer renders correctly for skills with and without YAML frontmatter
- AI improvement generates valid diffs and apply writes back to disk successfully
- Model A/B comparison produces assertion results for both models on any eval case
- MCP detection correctly identifies dependencies from known tool patterns and frontmatter
- All new endpoints return proper error responses for edge cases (missing SKILL.md, no failures, LLM errors)
