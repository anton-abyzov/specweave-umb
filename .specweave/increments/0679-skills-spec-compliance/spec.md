---
increment: 0679-skills-spec-compliance
title: SKILL.md Spec Compliance — Align vSkill Emitters with agentskills.io/specification
type: feature
priority: P2
status: active
created: 2026-04-22
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: SKILL.md Spec Compliance — Align vSkill Emitters with agentskills.io/specification

## Overview

The canonical SKILL.md specification at **https://agentskills.io/specification** defines a frontmatter shape where `tags` and `target-agents` are nested **under a `metadata:` block**, not at the top level. vSkill's emitters currently place these fields at the top level of the frontmatter — a quiet drift that breaks third-party tooling, validators, and importers expecting spec compliance.

This increment aligns vSkill with the spec in three places:

1. **Primary emitter** — `src/eval-server/skill-create-routes.ts` writes `tags` and `target-agents` at the top level. Fix to nest under `metadata:`.
2. **0670-skill-builder-universal templates** — 0670 is in flight (3/35 tasks done) and its template files produce the same non-compliant shape. Update its template(s) under `.specweave/increments/0670-skill-builder-universal/` in lockstep so 0670 does not ship a regression.
3. **Test fixtures** — any fixture under `src/**/__tests__/fixtures/` that asserts the old shape must be updated; golden-file tests lock the new shape.

Additionally, integrate the external validator:

- **`skills-ref validate`** runs as a post-creation step in `vskill skill new` (warn-only by default; `--strict` turns warnings into blocking errors).
- A new npm script **`lint:skills-spec`** runs the validator over all emitted fixtures in CI.

## Code Location & Scope

**Target codebase:** `repositories/anton-abyzov/vskill/`

**In scope:**
- `src/eval-server/skill-create-routes.ts` — frontmatter emission
- `.specweave/increments/0670-skill-builder-universal/` — template files referenced by 0670's tasks (do not edit tasks.md execution state; only update the templates 0670 consumes)
- `package.json` — new `lint:skills-spec` script
- `src/cli/skill.ts` (or wherever `vskill skill new` post-creation runs) — invoke `skills-ref validate`, surface warnings
- Golden-file fixtures under `src/**/__tests__/fixtures/`
- README section on SKILL.md spec compliance

**Out of scope:**
- New provider support (LM Studio) — covered by **0677**
- Source-model picker — covered by **0678**
- 0670's own increment lifecycle or other 0670 behaviors beyond the template shape

## Personas

- **P1 — Skill author**: generates a SKILL.md and wants it to pass third-party validators on first emit.
- **P2 — Ecosystem consumer**: imports vSkill-generated skills into another agent runtime that reads the canonical spec; misplaced fields break ingestion.
- **P3 — CI maintainer**: wants a blocking CI check on spec compliance so drift cannot re-accumulate.

## User Stories

### US-001: Primary Emitter Nests `tags` and `target-agents` Under `metadata:` (P1)
**Project**: vskill

**As a** user generating a skill via the vSkill CLI or Studio
**I want** the emitted SKILL.md to place `tags` and `target-agents` under `metadata:`
**So that** the file validates against the canonical agentskills.io specification

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `src/eval-server/skill-create-routes.ts` generates SKILL.md frontmatter, when it writes the frontmatter block, then `tags` and `target-agents` are emitted under a `metadata:` key (e.g., `metadata:\n  tags:\n    - foo\n  target-agents:\n    - claude-code`), and no `tags:` or `target-agents:` keys appear at the top level.
- [x] **AC-US1-02**: Given the emitted YAML, when parsed with `yaml.load()`, then `doc.metadata.tags` is an array of strings and `doc.metadata["target-agents"]` is an array of strings; `doc.tags` and `doc["target-agents"]` are `undefined` at the root.
- [x] **AC-US1-03**: Given all other fields the emitter writes today (`name`, `description`, `version`, etc.), when migration lands, then those fields remain at the top level exactly where they are today — this increment touches only `tags` and `target-agents`, nothing else changes position.
- [x] **AC-US1-04**: Given a golden-file fixture captures the before and after, when the new shape is asserted, then the diff is limited to moving the two keys plus their values into a new `metadata:` block; no other lines change.

---

### US-002: 0670 Templates Produce the Same Compliant Shape (P1)
**Project**: vskill

**As a** maintainer of 0670-skill-builder-universal
**I want** 0670's SKILL.md templates to match the new compliant shape
**So that** 0670 does not ship a regression when it completes

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given 0670's template file(s) under `.specweave/increments/0670-skill-builder-universal/` that drive SKILL.md emission, when this increment lands, then those templates also nest `tags` and `target-agents` under `metadata:`.
- [x] **AC-US2-02**: Given 0670 task documents reference the old shape (if any), when this increment lands, then any such references are updated via a follow-up note in 0670's tasks file — without marking 0670 tasks complete or interfering with 0670's execution state.
- [x] **AC-US2-03**: Given 0670 is currently at 3/35 tasks done, when this increment lands, then 0670's remaining tasks inherit the new shape automatically and 0670's own validator (if any) also uses `skills-ref validate`.

---

### US-003: `skills-ref validate` Runs Post-Creation in `vskill skill new` (P2)
**Project**: vskill

**As a** developer running `vskill skill new`
**I want** the tool to automatically validate the emitted file against the spec and warn me if it fails
**So that** I catch shape drift before committing

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `vskill skill new` completes emission of a new SKILL.md, when the post-creation step runs, then it invokes `skills-ref validate <path-to-new-skill>` as a child process and captures the exit code + stderr.
- [x] **AC-US3-02**: Given `skills-ref validate` exits non-zero, when the default (non-strict) mode is in effect, then the CLI prints a yellow warning summarizing the failures and completes with exit code 0 (the skill file remains on disk).
- [x] **AC-US3-03**: Given the user passes `--strict` on `vskill skill new`, when `skills-ref validate` exits non-zero, then the CLI prints the failures as red errors and exits with code 1; the emitted file remains on disk for inspection.
- [x] **AC-US3-04**: Given `skills-ref` is not installed on the user's machine, when post-creation runs, then the CLI prints a one-line hint ("Install `skills-ref` to enable spec validation: `npm i -g skills-ref`") and completes with exit code 0 — validation is optional by design.

---

### US-004: New `lint:skills-spec` Script in `package.json` for CI (P2)
**Project**: vskill

**As a** CI maintainer
**I want** a scripted way to validate every committed SKILL.md fixture against the spec
**So that** drift cannot re-accumulate in the repo

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `package.json`, when the `lint:skills-spec` script is added, then it runs `skills-ref validate` against every file under the repo matching `**/SKILL.md` (or a configured glob), and exits non-zero if any fail.
- [x] **AC-US4-02**: Given CI runs the `lint:skills-spec` script on every PR, when the job executes, then it surfaces per-file validation output and the PR is blocked on non-zero exit.
- [x] **AC-US4-03**: Given `skills-ref` is not available in CI, when the script runs, then it fails loudly (exit 1) with "skills-ref not found — install via `npm i -D skills-ref`" — CI must have deterministic tooling; silent skip is not acceptable.

---

### US-005: Golden-File Tests Lock the New Frontmatter Shape (P1)
**Project**: vskill

**As a** maintainer
**I want** a test that fails the moment anyone regresses the frontmatter shape
**So that** the spec alignment is guaranteed for all future changes

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a new test file `src/eval-server/__tests__/skill-create-frontmatter.test.ts`, when it runs the emitter with a known fixture input, then it asserts the emitted frontmatter equals a golden string that places `tags` and `target-agents` under `metadata:`.
- [x] **AC-US5-02**: Given the golden file is checked in at `src/eval-server/__tests__/fixtures/skill-create-frontmatter.golden.md`, when someone changes the emitter without updating the golden file, then the test fails with a clear diff showing the drift.
- [x] **AC-US5-03**: Given the golden-file test is part of the standard `npx vitest run` target, when CI runs, then it passes on the compliant shape and fails on any regression.

## Functional Requirements

- **FR-01**: `tags` and `target-agents` are nested under `metadata:` in all emitted SKILL.md frontmatter.
- **FR-02**: `skills-ref validate` runs post-creation in `vskill skill new`, warn-only by default, blocking under `--strict`.
- **FR-03**: `lint:skills-spec` npm script validates all SKILL.md files in the repo.
- **FR-04**: Golden-file test locks the new shape.

## Non-Functional Requirements

- **NFR-01 (Compatibility)**: This is a breaking-shape change for downstream consumers that read `tags` at the top level. A README migration note documents the change. Because all emitters migrate in lockstep, there is no period where the repo emits mixed shapes.
- **NFR-02 (CI)**: The `lint:skills-spec` script must run in < 5 seconds on the repo's current fixture count.
- **NFR-03 (Validator UX)**: Post-creation validation adds < 500 ms to `vskill skill new` in the happy case.

## Scope Boundaries

- **In scope**: The four deliverables above + tests + README.
- **Out of scope**: Other SKILL.md fields beyond `tags`/`target-agents`; new provider support; skill-gen model picker.

## Dependencies

- **`skills-ref` CLI** must be available (published; install instructions documented). If it is not yet published, this increment's rollout is blocked on it — call out in plan.md.
- **0670-skill-builder-universal** shares template files. This increment coordinates with 0670 (see AC-US2-01..03) but does not modify 0670's task-completion state.
