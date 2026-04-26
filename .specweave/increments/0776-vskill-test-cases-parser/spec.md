---
increment: 0776-vskill-test-cases-parser
title: 'Port ## Test Cases parser to vskill (+writer)'
type: feature
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Author-anchored activation-test fixtures in SKILL.md

## Overview

vskill (the CLI/studio) has no path to commit author-anchored ground-truth fixtures into version control. The `+`/`!` UI prefixes in the studio Trigger tab live only in textarea state. A studio reload → labels are gone. A `git pull` → no fixtures travel with the skill. CI regression → nothing to regress against.

vskill-platform (built later) already has a `## Test Cases` parser at `src/lib/eval/prompt-generator.ts:22-48` and a priority chain (`Evaluations > Test Cases > LLM auto`). The platform reads but never writes. This increment ports the parser to vskill AND adds the missing writer, then wires both into the studio Trigger tab.

This is the path-2 follow-up to increment 0775 (which fixed the FP-on-broad-scope scoring bug but didn't address the persistence gap).

## User Stories

### US-001: Author-committed fixtures load on every studio launch (P1)
**Project**: vskill

**As a** skill author who has committed activation-test fixtures into my SKILL.md
**I want** the studio Trigger tab to load my fixtures automatically on mount
**So that** I never have to re-type test prompts after a reload, and teammates pulling the repo see the same tests I do

**Acceptance Criteria**:
- [x] **AC-US1-01**: `parseTestCases(content: string)` returns the parsed prompt+expected pairs from a `## Test Cases` block in SKILL.md.
- [x] **AC-US1-02**: Section regex stops at the next `##` heading, `---` separator, or end-of-file.
- [x] **AC-US1-03**: Expected text mapping: `"should activate"` → `should_activate`, `"should not activate"` → `should_not_activate`, anything else (including `"auto"`) → `auto`.
- [x] **AC-US1-04**: GET `/api/skills/:plugin/:skill/test-cases` returns `{prompts: [...], source: "skill-md" | null}`. `source` is `null` when no fixtures are present.
- [x] **AC-US1-05**: On Trigger tab mount, `ActivationPanel` fetches `/test-cases`; if `prompts.length > 0`, the textarea is pre-populated with `+`/`!`/no-prefix lines and a "from SKILL.md" pill renders next to the "Test Prompts" label.

### US-002: Save current prompts back to SKILL.md (P1)
**Project**: vskill

**As a** skill author who just typed labeled test prompts in the textarea
**I want** a "Save as test cases" button that writes them into my SKILL.md
**So that** my labels persist across reloads, share via git, and run in CI

**Acceptance Criteria**:
- [x] **AC-US2-01**: `serializeTestCases(prompts)` emits a `## Test Cases` block matching the platform's parse regex exactly (`- Prompt: "..."\n  Expected: "..."` shape).
- [x] **AC-US2-02**: `upsertTestCasesIntoSkillMd(content, prompts)` replaces an existing block if present, otherwise appends. Frontmatter is preserved verbatim. Other body sections are preserved verbatim.
- [x] **AC-US2-03**: PUT `/api/skills/:plugin/:skill/test-cases` with `{prompts}` writes the upserted SKILL.md to disk and returns `{ok: true, count: N}`.
- [x] **AC-US2-04**: When the user clicks "Save as test cases", the current textarea is parsed (using the existing `+`/`!`/blank prefix mapping), PUT'd to the route, and on success the source badge flips back to "from SKILL.md".
- [x] **AC-US2-05**: Round-trip integrity — `parseTestCases(serializeTestCases(prompts))` returns prompts equivalent to the input (same prompt strings, same expected labels).

### US-003: Source badge tracks origin and edits (P2)
**Project**: vskill

**As a** skill author looking at the Trigger tab
**I want** a clear visual indicator of where the current prompts came from
**So that** I know at a glance whether my changes are committed or transient

**Acceptance Criteria**:
- [x] **AC-US3-01**: `WorkspaceContext` exposes `activationPromptsSource: "skill-md" | "ai-generated" | "user-typed" | null`.
- [x] **AC-US3-02**: Successful initial load sets source to `"skill-md"`; AI generation sets it to `"ai-generated"`; manual textarea edits flip it to `"user-typed"`.
- [x] **AC-US3-03**: ActivationPanel renders a green "from SKILL.md" pill when source is `"skill-md"`, a purple "AI-generated" pill for `"ai-generated"`, no pill for `"user-typed"` or `null`.
- [x] **AC-US3-04**: After Save success, the source flips back to `"skill-md"` so the badge re-appears.

## Functional Requirements

### FR-001: Parser module
New file `src/eval/test-case-parser.ts` with three exports:
- `parseTestCases(content: string): ParsedTestCase[]` — regex-driven, port of platform's `parseAuthorTestCases`.
- `serializeTestCases(prompts: ParsedTestCase[]): string` — emits the canonical `## Test Cases` block.
- `upsertTestCasesIntoSkillMd(content: string, prompts: ParsedTestCase[]): string` — replace-or-append helper that preserves all other content.

### FR-002: Server routes
Two new endpoints in `src/eval-server/api-routes.ts`:
- `GET /api/skills/:plugin/:skill/test-cases` — reads SKILL.md, parses, returns `{prompts, source}`.
- `PUT /api/skills/:plugin/:skill/test-cases` — body `{prompts}`, upserts the section, writes SKILL.md, returns `{ok, count}`.
Both use `resolveSkillDir` for path-containment (already enforced).

### FR-003: UI wiring
- ActivationPanel: initial-load fetch, "from SKILL.md" pill, "Save as test cases" button with toast on success.
- WorkspaceContext: new `activationPromptsSource` state slice + `SET_PROMPTS_SOURCE` action.
- Source flips on AI-generation, user edits, save success.

### FR-004: Empty-prompts behavior
PUT with `prompts: []` removes the `## Test Cases` block from SKILL.md entirely (does not write an empty block). This keeps SKILL.md clean when an author clears their fixtures.

## Success Criteria

- All 12 RED tests in `__tests__/test-case-parser.test.ts` and `__tests__/test-cases-routes.test.ts` go GREEN.
- `npx vitest run` — full suite, no NEW regressions vs the 18 pre-existing baseline failures.
- `npm run build:eval-ui` — clean build.
- Manual smoke test on `greet-anton/SKILL.md`:
  - Add a `## Test Cases` block → studio reload → fixtures load with the green badge.
  - Edit a prompt → badge flips to "user-typed" (or hides).
  - Click Save → SKILL.md is updated; reload picks them up again.
  - Frontmatter and other body sections remain untouched.

## Out of Scope

- Behavioral testing via `claude -p` shellout (separate increment).
- `## Evaluations` section parser (assertion-based grading is a different paradigm).
- Cohen's-kappa metric per-skill.
- Cross-skill confusion matrix.
- Active-learning queue for ambiguous cases.
- vskill-platform changes (parser already exists there; both repos read the same SKILL.md the CLI writes).
- Dual-judge scope/drift detection (separate, more invasive change).

## Dependencies

- Builds on increment 0775 (verdict scoring) — no API conflict; this increment doesn't touch activation-tester.ts.
- vskill-platform `prompt-generator.ts:22-48` (port source).
- Existing `resolveSkillDir`, `readBody`, `sendJson` helpers in api-routes.ts.
