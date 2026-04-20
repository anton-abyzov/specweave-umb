---
status: completed
---
# 0671 — Skill Refinement Loop

**Status:** planned
**Priority:** P2
**Depends on:** 0670 (skill-builder-universal)
**Origin:** Brainstorm team `brainstorm-hermes-skill-builder` (2026-04-20)

## Context & Motivation

Inspired by NousResearch's Hermes Agent marketing claims of "skills self-improve during use" and "built-in learning loop". A research brainstorm (advocate/critic/pragmatist) verified that:

1. **Hermes' self-improvement is marketing, not code.** Actual Hermes skills are static markdown. The "learning loop" is README prose with no executable implementation. Dogfood is a QA workflow, not a self-editor. Critic-validated, all 3 agents agreed.
2. **SpecWeave already has ~80% of the equivalent capability** via `sw:reflect` (session → CLAUDE.md learnings), `sw:skill-gen` (signal → new skill), `rubric.md` (per-increment quality contract), `sw:grill`/`judge-llm` (closure gates).
3. **The real gap in our graph:** gate-failure signals from `judge-llm`/`rubric`/`code-review` currently die inside report JSON files. They should feed back into the same `skill-signals.json` that `sw:skill-gen` already consumes — but targeting **existing skills for refinement**, not just creating new ones.

This increment closes that edge with minimum-regret design: a new `--refine` mode for `sw:reflect` + a session-end nudge UX borrowed from Hermes' "codify this?" pattern. Red lines drawn against runtime self-mutation (which would break verified-skill.com's trust model).

Selected Hermes skill content (QA, red-teaming, inverse agent-orchestration) is imported in a separate Phase 2, gated on 0670 shipping its importer.

## In Scope

- Extend `skill-signals.json` schema to carry refinement signals (source, target skill, severity).
- Emit refinement signals from `sw:judge-llm`, rubric evaluator, and `sw:code-reviewer` when a gate failure can be traced to a specific skill's instructions.
- New skill: `sw:skill-refine <skill-slug>` — reads signals + current SKILL.md, proposes a diff via Haiku, presents it to user for approval, writes the approved diff to the skill source repo.
- Session-end nudge in `sw:reflect` stop-hook: if ≥1 high-confidence learning or ≥1 refinement signal accumulated, print a one-line prompt at `/sw:done` close: `"Detected: <summary> — persist/refine? (y/N)"`.
- Dashboard view in `sw:reflect --status`: list skills with ≥3 negative signals ranked by severity.
- ADRs codifying the four red lines from the brainstorm critic.
- **Scope cap:** local-only. No verified-skill.com registry changes. No telemetry endpoint. No auto-merge.

## Out of Scope (deferred to future increments)

- **Phase 2 (separate increment, post-0670):** Port 8-12 high-value Hermes skills (dogfood/QA, red-teaming/godmode, autonomous-ai-agents/* inverse skills) via `vskill skill import` with frontmatter remap. Depends on 0670's generator extraction.
- **Phase 3 (deferred, needs telemetry infra):** Registry-side Elo leaderboard, opt-in usage telemetry, community auto-merge tier, per-skill quality surface on verified-skill.com. Requires 3-4 weeks of privacy/GDPR/audit-log work not budgeted here.
- Runtime self-mutation of active skills (explicitly rejected — see ADR-0671-01).

## User Stories & Acceptance Criteria

### US-001 — Refinement signals flow from gates to skill-signals.json
**As a** SpecWeave user
**I want** gate failures to identify which skill's instructions contributed
**So that** repeated failures surface as refinement opportunities

- **AC-US1-01:** When `sw:judge-llm` rejects an increment and its finding references a specific skill slug, a refinement signal is appended to `.specweave/state/skill-signals.json` with `{type: "refinement", source: "judge-llm", targetSkill, severity, incrementId, evidence}`.
- **AC-US1-02:** The rubric evaluator emits a refinement signal when a rubric criterion fails and the failure traces to a skill-authored instruction (e.g., skill told agent to skip validation).
- **AC-US1-03:** `sw:code-reviewer` emits a refinement signal when a critical finding is attributable to skill-directed behavior.
- **AC-US1-04:** `skill-signals.json` schema is versioned (`schemaVersion: 2`); existing generation signals from `sw:skill-gen` continue to deserialize unchanged.

### US-002 — sw:skill-refine proposes + applies approved diffs
**As a** skill author (or SpecWeave user with write access to a project skill)
**I want** to run `sw:skill-refine <skill>` and get an AI-proposed diff against recent failure evidence
**So that** I can improve the skill with provenance

- **AC-US2-01:** `sw:skill-refine <skill-slug>` aggregates all refinement signals for the target skill from the last N increments (default N=5, configurable).
- **AC-US2-02:** Prompts Haiku with `(current SKILL.md, signal list, evidence excerpts)` and returns a unified-diff proposal + human-readable rationale.
- **AC-US2-03:** Shows the diff to the user with approve/reject/edit-inline options; never writes without explicit approval.
- **AC-US2-04:** On approval, writes the diff to the skill's source file AND emits a git commit with message `"refine(<skill>): <rationale-summary>"` (commit, not push).
- **AC-US2-05:** Records the refinement in `.specweave/state/skill-refinements.json` (ledger: who, when, which signals, diff SHA).
- **AC-US2-06:** Supports `--dry-run` (diff only), `--show-signals` (inspect without diffing), `--scope project|user` (target `.claude/skills/` or `~/.claude/skills/`).

### US-003 — Session-end nudge for refinement + persistence
**As a** SpecWeave user closing an increment
**I want** a brief session-end prompt when learnings or refinement opportunities were detected
**So that** codification doesn't require remembering to run `sw:reflect`

- **AC-US3-01:** When `/sw:done` closes an increment and `sw:reflect` has accumulated ≥1 high-confidence learning OR ≥1 refinement signal for that session, a ONE-LINE prompt is printed: `"Detected: <short summary> — run <sw:reflect|sw:skill-refine SLUG>? (y/N)"`.
- **AC-US3-02:** The nudge is OFF by default for users who have `reflect.autoNudge: false` in `.specweave/config.json`.
- **AC-US3-03:** Declining ("N" or no input within 5s) logs no penalty; the signals remain in `skill-signals.json` for later invocation.
- **AC-US3-04:** The prompt contains NO auto-execution of writes — user must explicitly run the suggested command.

### US-004 — sw:reflect --status dashboard
**As a** SpecWeave user
**I want** to see which skills have accumulated refinement signals and how severe
**So that** I can prioritize refinement work

- **AC-US4-01:** `sw:reflect --status` output includes a `## Skill Refinement Suggestions` section listing skills with ≥3 negative signals, sorted by severity × recency.
- **AC-US4-02:** Each entry shows: skill slug, signal count by source (judge-llm/rubric/code-review), last signal timestamp, one-click command `sw:skill-refine <slug>`.
- **AC-US4-03:** Section is omitted entirely when no skills meet the ≥3 threshold.

### US-005 — Red-line ADRs published
**As a** SpecWeave maintainer
**I want** the four red lines from the brainstorm baked into ADRs
**So that** future increments don't regress into unsafe self-mutation patterns

- **AC-US5-01:** ADR `skill-refinement-no-runtime-mutation` states: no skill's SKILL.md may be edited by any process during an active `/sw:do` or `/sw:done` session. Refinements are a separate, explicit user action.
- **AC-US5-02:** ADR `skill-refinement-registry-immutability` states: any skill published to verified-skill.com at version X must be bit-identical to the reviewed artifact for the lifetime of that version. Refinements require a NEW version + NEW review.
- **AC-US5-03:** ADR `skill-refinement-no-self-improving-marketing` states: SpecWeave and vskill docs/marketing may not use the phrase "self-improving skills" or equivalent until (a) reproducibility guarantees exist and (b) an audit log is shipped.
- **AC-US5-04:** ADR `skill-refinement-no-gate-goodhart-loop` states: a refinement signal MAY NOT be used as its own validation target within the same session; closing a regression loop on the gate that produced the signal is forbidden (Goodhart's law protection).

## Non-Functional

- **Determinism:** `sw:skill-refine --dry-run` with same inputs produces same diff on repeat runs (Haiku temperature pinned).
- **Privacy:** No signals leave the user's machine. `.specweave/state/` stays local. No telemetry endpoint is added.
- **Performance:** Session-end nudge adds <100ms to `/sw:done` close time.
- **Backward compat:** Existing `skill-signals.json` files (schemaVersion 1) auto-migrate on first read.

## Hermes Port Candidates (tracked for future Phase 2 increment)

The brainstorm pragmatist identified these Hermes skills as high-signal ports (requires `vskill skill import` from 0670):

1. `dogfood/` — systematic QA workflow (5-phase: plan → explore → collect → categorize → report). Fills a gap we don't have.
2. `red-teaming/godmode/` — adversarial test patterns. Complements `sw:security-review` / `sw:judge-llm`.
3. `autonomous-ai-agents/{claude-code, codex, opencode}/` — inverse orchestration skills (how Claude drives other agents). Symmetric to vskill's 49-agent emission.
4. `research/` — structured research workflow. May overlap with `sw:brainstorm`/`sw:architect`; evaluate.
5. `diagramming/` — likely overlaps `sw:diagrams`; evaluate before porting.

Skipped as off-mission: `apple/`, `gaming/`, `smart-home/`, `feeds/`, `gifs/`.

Port effort estimate (from pragmatist): ~1 week for 8-12 skills including frontmatter remap (`metadata.hermes.tags` → `tags`). Not in this increment.

## Definition of Done

- All ACs satisfied.
- Four ADRs committed under `.specweave/docs/internal/architecture/adr/`.
- `sw:skill-refine` skill published in specweave plugin, invocable via slash command.
- Unit tests (Vitest) for signal emission, aggregation, diff generation — coverage ≥90%.
- Integration test: trigger judge-llm failure → verify signal emitted → run `sw:skill-refine --dry-run` → verify diff proposed.
- Docs: update `sw:reflect` docs to mention `--refine` and nudge; add `sw:skill-refine` docs page.
- `CHANGELOG.md` entry in specweave package.
- Closure gates pass: code-review, simplify, grill, judge-llm, PM validation.
