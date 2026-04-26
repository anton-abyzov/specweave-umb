---
increment: 0734-studio-create-skill-engine-selector
title: "Studio Create-Skill UI: Engine Selector + Versioning"
type: feature
priority: P1
status: active
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Create-Skill UI: Engine Selector + Versioning

## Overview

The Studio "create skill" page (`vskill/src/eval-ui/src/pages/CreateSkillPage.tsx`) currently lets users author a skill with a description, model, and target agents — but exposes **no engine selector** and **no version input**. The backend silently uses the universal vskill generator and hard-codes `version: "1.0.0"`. That hides two facts users care about:

1. **Anthropic's `skill-creator` plugin** is a powerful, first-class Claude-native authoring engine. Its schema is slightly richer than the cross-universal subset VSkill emits (richer `allowed-tools` semantics, plugin-specific metadata) — so its output is *more expressive on Claude* — but it does not portably translate to other agents.
2. **VSkill's own `skill-builder` SKILL.md** (shipped by 0670 at `vskill/plugins/skills/skills/skill-builder/SKILL.md`, version `0.1.0`) emits *cross-universal* skills across all 8 universal targets — Claude, Codex, Cursor, Cline, Gemini CLI, OpenCode, Kimi, Amp. The trade-off: it constrains output to the common-denominator schema.

Both are first-class peer choices. The trade-off is real — **richer Claude-only output (Anthropic) vs. portable cross-tool output (VSkill)** — and the user should make it deliberately. Today Studio hides both behind a silent default.

This increment makes the choice explicit with a tri-state engine selector, adds a per-skill semver version input, and lets users one-click-install an engine they haven't installed yet (with consent). It is a UI + backend wiring increment, narrowly scoped: no aesthetic redesign, no new versioning infrastructure (all primitives already exist).

## Problem Statement

Today a user landing on `/create` in Studio:
- Cannot see whether `~/.claude/skills/skill-creator/` is installed and available as an engine.
- Cannot see whether the local `plugins/skills/skills/skill-builder/SKILL.md` is available.
- Cannot pick which engine to use — the backend silently picks the universal vskill path.
- Cannot set the version of the skill they're authoring (defaults to `1.0.0` server-side).
- If they want to install a missing engine, must drop to a terminal and run a CLI manually.

Result: users ship skills they didn't deliberately scope (cross-tool vs. Claude-only) and can't see/edit the version that will appear in the registry.

## Goals

- Render an explicit tri-state engine selector on the create-skill page (VSkill / Anthropic / none).
- Detect which engines are installed via the local eval-server (no browser → verified-skill.com calls — CORS-free by construction).
- Frame **Anthropic skill-creator as a first-class peer**, not a fallback. Tooltip copy must communicate the trade-off, not a hierarchy.
- Apply default-checked precedence: VSkill if detected → else Anthropic if detected → else "No engine".
- Add a per-skill semver version input prefilled with `1.0.0` (or current version in update mode), validated client-side via existing `isValidSemver()`.
- Offer a one-click [Install] flow for missing engines with **explicit user consent** showing the exact shell command, hard-coded server-side (no shell injection surface), localhost-only, with SSE progress streaming.
- Persist `metadata.engine` in the SKILL.md frontmatter so future updates know how the skill was produced.
- Ship a vskill npm patch release as the closure gate ("must be deployed and available").

## Out of Scope

- Versions sub-route in Studio (link out to the existing `https://verified-skill.com/skills/.../versions` route instead).
- Diff / changelog viewer.
- Plugin or CLI version editing — only skill `metadata.version`.
- Migrating existing skills to add `metadata.engine` field — additive, forward-only.
- UI redesign / aesthetic changes.
- Mobile-responsive selector layout (Studio is desktop-only today).
- Persisting engine selection across sessions in localStorage (potential follow-up).

## User Stories

### US-001: Detect installed skill-authoring engines (P1)
**Project**: vskill

**As a** Studio user opening the create-skill page
**I want** the page to know which authoring engines are installed locally
**So that** the engine selector reflects reality and tells me which option I can pick right now

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `GET /api/studio/detect-engines` returns `200` with `{ vskillSkillBuilder: boolean, anthropicSkillCreator: boolean, vskillVersion: string|null, anthropicPath: string|null }` (path follows the existing `/api/studio/*` convention used by `/api/studio/ops`).
- [ ] **AC-US1-02**: `anthropicSkillCreator` is the result of existing `isSkillCreatorInstalled(root)` (`src/utils/skill-creator-detection.ts:23-79`) — no new logic. `anthropicPath` is the first matched path from that helper, or `null`.
- [ ] **AC-US1-03**: `vskillSkillBuilder` is `true` when any of: (a) `plugins/skills/skills/skill-builder/SKILL.md` exists in the workspace root, (b) `~/.agents/skills/skill-builder/` exists, or (c) any agent's `localSkillsDir/skill-builder/` exists. Implementation: a new `isSkillBuilderInstalled(root)` helper at `src/utils/skill-builder-detection.ts` mirrors `skill-creator-detection.ts`'s 7-path search but for `skill-builder`.
- [ ] **AC-US1-04**: When `vskillSkillBuilder=true`, `vskillVersion` is parsed from the SKILL.md frontmatter using existing `parseFrontmatter()` (`vskill-platform/src/lib/frontmatter-parser.ts`). Returns `null` when missing or invalid.
- [ ] **AC-US1-05**: Endpoint is registered through `src/studio/routes/index.ts` (same registration mechanism used by `/api/studio/ops` and the scope-transfer routes) so it lands automatically when `registerScopeTransferRoutes(router, root)` runs.
- [ ] **AC-US1-06**: Vitest unit test mocks `fs.existsSync` for all 4 cases (both, vskill-only, anthropic-only, neither) and asserts response shape and field values.

---

### US-002: Engine selector UI on CreateSkillPage (P1)
**Project**: vskill

**As a** Studio user creating a new skill
**I want** to explicitly pick the authoring engine — VSkill (cross-universal), Anthropic (Claude-native), or none — with the trade-off visible in tooltips
**So that** I make a deliberate choice between portability and Claude-only expressiveness rather than relying on a silent default

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A new `EngineSelector` component is rendered at the top of the AI-Assisted form (above the provider/model picker). Uses the same `role="tablist"` pattern as the existing mode toggle (CreateSkillPage.tsx:340–373) — no new UI library.
- [ ] **AC-US2-02**: On mount, `useCreateSkill` hook calls `GET /api/studio/detect-engines` and stores the result. Loading state shows a skeleton.
- [ ] **AC-US2-03**: Default selection precedence: `vskillSkillBuilder=true` → `"vskill"`. Else `anthropicSkillCreator=true` → `"anthropic-skill-creator"`. Else → `"none"`.
- [ ] **AC-US2-04**: Each option has a tooltip (native `title` attribute, matching existing pattern):
  - VSkill: `"Cross-universal — emits the same skill to 8 universal agents (Claude, Codex, Cursor, Cline, Gemini CLI, OpenCode, Kimi, Amp). Constrains output to the common schema across all agents. Recommended for portable skills."`
  - Anthropic: `"Powerful Claude-native engine — Anthropic's built-in skill-creator with a slightly richer schema (more expressive on Claude) but Claude-only. Pick this when you only target Claude Code and want full expressiveness."`
  - None: `"Generate raw — no engine assistance, you provide the full SKILL.md body."`
- [ ] **AC-US2-05**: Missing engines render with reduced opacity (`opacity 0.6`) and a small inline `[Install]` button next to the label. Hover tooltip on the option label: `"Not installed. Click [Install] to run: <install command>"`. The engine label itself stays clickable (so user can pre-select it) but Submit is gated until installation completes. See US-005 for the install flow.
- [ ] **AC-US2-06**: `data-testid="engine-selector-{vskill|anthropic-skill-creator|none}"` for E2E hooks.
- [ ] **AC-US2-07**: Reduced-motion respected — no transition animations under `prefers-reduced-motion: reduce`.

---

### US-003: Backend accepts and routes the engine field (P1)
**Project**: vskill

**As a** Studio backend
**I want** `POST /api/v1/skills/create` to accept an `engine` field and route to the appropriate generator path
**So that** the UI selection actually changes what gets emitted

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `CreateSkillRequest` interface (`src/eval-server/skill-create-routes.ts:46–87`) gains `engine?: "vskill" | "anthropic-skill-creator" | "none"` (default `"vskill"`).
- [ ] **AC-US3-02**: `engine="vskill"` continues to call the existing universal generator (no behavior change versus today).
- [ ] **AC-US3-03**: `engine="anthropic-skill-creator"` first calls `isSkillCreatorInstalled(root)`. If `true`: delegate to Anthropic's skill-creator and emit a Claude-only skill with its full Claude-native schema (no warning banner — this is a deliberate first-class choice). Response includes `{ engine: "anthropic-skill-creator", emittedTargets: ["claude-code"] }`. If `false`: respond `400` with `{ error: "skill-creator-not-installed", remediation: "claude plugin install skill-creator" }`.
- [ ] **AC-US3-04**: `engine="none"` skips generation entirely — the body is taken verbatim from `request.body.body` (already supported in manual mode). Frontmatter is built minimally without AI metadata.
- [ ] **AC-US3-05**: Vitest test covers all 3 success branches plus the "anthropic requested but not installed" failure.
- [ ] **AC-US3-06**: The engine value is persisted in the SKILL.md frontmatter under `metadata.engine` so future updates (`update` mode) know what produced the skill. Older skills without this field default to `"vskill"` on update.

---

### US-004: Per-skill version input (P1)
**Project**: vskill

**As a** Studio user creating or updating a skill
**I want** to set the semver version of the skill in the create form
**So that** I can ship explicit versions and match the version field that already exists in the SKILL.md frontmatter and the platform versions sub-route

**Acceptance Criteria**:
- [ ] **AC-US4-01**: A "Version" text input renders next to the Name field, prefilled with `"1.0.0"` (or, in update mode, the current version read from the existing SKILL.md frontmatter).
- [ ] **AC-US4-02**: Input uses pattern validation: client-side calls `isValidSemver()` (`vskill-platform/src/lib/integrity/semver.ts`) on blur. Invalid → red border + helper text `"Must be valid semver (e.g. 1.0.0, 2.1.3-beta.1)"`.
- [ ] **AC-US4-03**: Submit is disabled while the semver is invalid.
- [ ] **AC-US4-04**: `useCreateSkill` hook sends `version` in the POST body. Backend already honors it (`src/eval-server/skill-create-routes.ts:1161-1174`) — no backend change needed.
- [ ] **AC-US4-05**: A tooltip on the field reads: `"Skill version (semver). Auto-bumps on update unless versioningMode=author."`
- [ ] **AC-US4-06**: Vitest test for the hook asserts `version` is included in the POST payload, and that invalid input is rejected client-side before submit.
- [ ] **AC-US4-07**: A small "Versions" link appears below the field when in update mode, linking to `https://verified-skill.com/skills/{owner}/{repo}/{name}/versions` (existing route in vskill-platform). The link is omitted in create mode (no history yet).

---

### US-005: One-click engine install from Studio (P1)
**Project**: vskill

**As a** Studio user who picked an engine that isn't detected
**I want** Studio to offer to install it for me, show me the exact command first, and stream progress
**So that** I don't have to drop to a terminal and can keep my flow

**Acceptance Criteria**:
- [ ] **AC-US5-01**: New endpoint `POST /api/studio/install-engine` accepts `{ engine: "vskill" | "anthropic-skill-creator" }`. Returns `202 Accepted` with `{ jobId: "<uuid>" }` and starts the install asynchronously. Returns `400` for unknown engine names.
- [ ] **AC-US5-02**: Install commands (single source of truth, defined in `src/eval-server/install-engine-routes.ts`):
  - `anthropic-skill-creator` → `claude plugin install skill-creator` (requires `claude` CLI on PATH; if missing, return `412 Precondition Failed` with `{ error: "claude-cli-missing", remediation: "Install Claude Code CLI first: https://docs.claude.com/claude-code" }`).
  - `vskill` → `vskill install anton-abyzov/vskill/plugins/skills/skills/skill-builder` (requires `vskill` on PATH — should always be true since Studio is launched as `vskill studio`).
- [ ] **AC-US5-03**: Streaming endpoint `GET /api/studio/install-engine/:jobId/stream` (Server-Sent Events) emits `progress` events with command stdout/stderr lines and a final `done` event with `{ success: bool, exitCode: int, stderr: string }`. Times out after 120 seconds.
- [ ] **AC-US5-04**: When the user clicks `[Install]` next to a missing engine in `EngineSelector`, a confirmation modal appears with the **exact command** that will run (`claude plugin install skill-creator` or `vskill install ...`), a security note (`"This runs the command in your terminal as your user. Inspect before approving."`), and `[Run install]` / `[Cancel]` buttons. No install runs without explicit click.
- [ ] **AC-US5-05**: While installing, the option shows a spinner + live tail of the last line of stdout (max 60 chars). On success: green checkmark, auto-refresh detection, the option becomes selectable. On failure: red X, full stderr in expandable details, `[Retry]` button.
- [ ] **AC-US5-06**: After successful install, the UI calls `GET /api/studio/detect-engines` again and updates state. The just-installed engine becomes the selected default if the user had it pre-selected during the missing-state UX.
- [ ] **AC-US5-07**: Security: install commands are **hard-coded server-side** (NOT taken from request body) — the request body only carries the engine *name*; the eval-server maps name → command from a fixed allow-list. No shell injection surface.
- [ ] **AC-US5-08**: The install endpoint is gated to `localhost`-bound requests only. Reject any request whose `req.socket.remoteAddress` is not `127.0.0.1` / `::1` with `403`. Belt-and-suspenders against accidental exposure.
- [ ] **AC-US5-09**: Vitest integration test mocks `child_process.spawn` and asserts: (a) success path emits expected events, (b) non-zero exit code surfaces stderr, (c) timeout after 120s closes the SSE stream with `done {success:false, exitCode:-1, stderr:"timeout"}`, (d) unknown-engine returns `400`, (e) non-localhost remoteAddress returns `403`, (f) missing prerequisite CLI returns `412`.
- [ ] **AC-US5-10**: Component test for `EngineSelector` covers the full flow: missing → click `[Install]` → confirm modal → spinner → success → option auto-selects.

---

### US-006: Bundle rebuild + vskill npm release gate (P1)
**Project**: vskill

**As a** release engineer
**I want** closure of 0734 to be blocked until the vskill bundle is rebuilt and a patch release is published
**So that** "deployed and available" is a verifiable gate, not a TODO

**Acceptance Criteria**:
- [ ] **AC-US6-01**: `npm run build:eval-ui` succeeds (zero errors) and produces an updated `dist/eval-ui/` with the new selector, version input, and install modal present in the bundle.
- [ ] **AC-US6-02**: A Playwright E2E test (or programmatic smoke) launches `vskill studio`, navigates to `/create`, asserts the engine selector + version input + (when an engine is missing) the `[Install]` button are present in the rendered DOM.
- [ ] **AC-US6-03**: `sw:release-npm` (or `sw:npm`) executes successfully — vskill patch version bumps, npm publishes, GitHub Release created. Closure is **blocked** until the release lands.
- [ ] **AC-US6-04**: Umbrella sync commit lands on the umbrella repo main branch (`sync umbrella after vskill v0.5.X release`) — same pattern as 0670 AC-US9-03.

## Definition of Done

- All 6 user stories' ACs marked `[x]` with passing tests.
- `npx vitest run` passes for all new / extended test files (unit + integration).
- `npx playwright test tests/e2e/studio-create-skill-engine.spec.ts` passes locally.
- `npm run build:eval-ui` succeeds; bundle size delta ≤ +50 KB gzipped.
- `sw:release-npm` lands a vskill patch release (npm publish + GitHub Release).
- Umbrella sync commit lands on `main`.
- `code-review-report.json`, `simplify-report.json`, `grill-report.json`, `judge-llm-report.json` all in `reports/` with no critical/high/medium findings outstanding.
- `specweave validate 0734-studio-create-skill-engine-selector` passes.

## Dependencies

- **0670-skill-builder-universal** — provides `plugins/skills/skills/skill-builder/SKILL.md` (already shipped, version 0.1.0) and `isSkillCreatorInstalled()` helper. 0670 AC-US1-01..04 are already `[x]`; this increment can proceed independently of 0670's remaining ACs because the SKILL.md file and detection helper exist on disk today.
- **vskill-platform** — read-only reuse of `isValidSemver()` and `parseFrontmatter()`; no platform deploy required (per user decision: bundle + npm release only).
