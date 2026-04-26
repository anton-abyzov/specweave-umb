---
increment: 0772-studio-first-launch-onboarding-polish
title: Studio First-Launch Onboarding Polish
type: bug
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio First-Launch Onboarding Polish

## Overview

`npx vskill@latest studio` in a fresh project surfaces four first-launch UX issues. This increment bundles them as a coherent "first-launch polish" pass — each is small in isolation, but together they make Studio feel broken in a brand-new environment.

1. CLI prompts for an Anthropic API key claiming Studio "needs" one — even though Claude Code is installed and the UI itself says no key is needed.
2. The agent-scope badge shows `(installed · global)` but omits plugin skills, so the number disagrees with the sidebar's `AVAILABLE` count (e.g. badge `(0 · 13)` vs sidebar `94`).
3. The right pane's empty state offers no path forward when the project has no installed skills — just "Select a skill to view details" with no CTA to browse the marketplace or create one.
4. After a successful skill creation the UI sometimes fails to navigate to the new skill; clicking "Create" again then hits a 409 that surfaces as a red error banner with no recovery, even though the skill was created on disk.

## User Stories

### US-001: Skip the API-key prompt when Claude Code is installed
**Project**: vskill

**As a** user with Claude Code already installed
**I want** Skill Studio to recognize my existing Claude Code setup and not ask for an Anthropic API key
**So that** I can launch Studio with one command and start working without misleading prompts

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `claude` binary is on PATH and no provider env vars are set, `firstRunOnboarding()` returns `action: "skip"` without printing any onboarding message.
- [x] **AC-US1-02**: When neither `claude` is on PATH nor any provider key is configured, the prompt prints softened wording: it does NOT use "needs"; it mentions Claude Code as the no-key alternative; it offers an optional API key for comparison/eval scenarios.
- [x] **AC-US1-03**: When the user declines, the skip message names BOTH options: install Claude Code OR run `vskill keys set anthropic`.
- [x] **AC-US1-04**: Detection is robust across platforms: POSIX uses `which claude`, win32 uses `where claude`. Timeout is bounded (≤ 250 ms) and never throws — failure → treat as "not detected".

### US-002: Show plugin skills in the agent-scope badge
**Project**: vskill

**As a** user with multiple plugin skills installed
**I want** the agent badge above the sidebar to reflect the same total as the AVAILABLE group below
**So that** the numbers I see in the studio agree with each other

**Acceptance Criteria**:
- [x] **AC-US2-01**: `AgentScopeEntry` (server contract in `api-routes.ts`) gains a numeric `pluginSkillCount` field, populated for `claude-code` via the existing `scanInstalledPluginSkills({ agentId: "claude-code" })` and 0 for all other agents.
- [x] **AC-US2-02**: `agentsResponseToPickerEntries` adapter forwards `pluginSkillCount` onto `PickerAgentEntry` so the picker UI can render it without a second fetch.
- [x] **AC-US2-03**: The trigger button in `AgentScopePicker.tsx` renders `(N · G · P)` where N=local, G=global, P=plugins. The `title` attribute reads "project · personal · plugins".
- [x] **AC-US2-04**: The popover stats panel shows a fourth row labeled "Plugins" with the value `pluginSkillCount`, between "Global" and "Last sync".
- [x] **AC-US2-05**: For non-Claude-Code agents `pluginSkillCount === 0` and the badge renders cleanly as `(N · G · 0)` (no missing field, no NaN).

### US-003: Actionable empty state on the right pane in a fresh project
**Project**: vskill

**As a** first-time user with no installed project skills
**I want** the right pane to offer concrete next steps
**So that** I am not stranded looking at a passive "select a skill" message when there is nothing to select

**Acceptance Criteria**:
- [x] **AC-US3-01**: When no skill is selected AND the project skill bucket has zero entries, the right pane renders an onboarding empty state with the heading "No skills installed for this project yet."
- [x] **AC-US3-02**: The onboarding state shows two CTAs: a primary **Browse marketplaces** button that dispatches the existing `studio:open-marketplace` `CustomEvent`, and a secondary **Create new skill** button that opens the inline create flow (sets StudioContext `mode` to `"create"`).
- [x] **AC-US3-03**: When skills exist but none is selected, the right pane keeps the existing "Select a skill to view details" copy unchanged.

### US-004: Reliable navigation after creating a skill, with idempotent 409 handling
**Project**: vskill

**As a** user who just clicked "Create Skill"
**I want** the UI to navigate me to the new skill on success — and to recognize the skill if it already exists rather than showing an error
**So that** I am never stuck on a "Skill already exists" red banner for a skill I successfully created moments ago

**Acceptance Criteria**:
- [x] **AC-US4-01**: After a successful `POST /api/skills/create`, the URL hash is set to `#/skills/<plugin>/<skill>` AND the right-pane detail view actually renders the new skill's overview page (not the empty `renderEmptyState()` fallback). This requires the in-memory skills list to include the new entry before `selectSkill` runs — fix the existing race by awaiting `refreshSkills()` or adopting the `revealSkill + setTimeout(500)` pattern from `App.tsx:751-753`.
- [x] **AC-US4-02**: A `409 Conflict` from `POST /api/skills/create` is treated as recoverable: the client parses the existing skill identity from the response (the server returns `Skill already exists at <absolute-path>`), navigates to that skill via the same `onCreated(plugin, skill)` flow, and surfaces a neutral one-line toast/inline note ("Skill already existed — opened it for you") instead of a red error banner.
- [x] **AC-US4-03**: Double-click on the Create button during an in-flight request does NOT issue a second POST (existing `creating` state must keep the button disabled). Verify with a test that fires two clicks within 10 ms and asserts only one network call is made.

### US-005: Surface GitHub sync state on the Skill Overview tab
**Project**: vskill

**As a** user who just created a skill
**I want** the Overview tab to show whether this skill can be published to GitHub and, if not, what to do about it
**So that** I am not stuck wondering how to share my skill — without leaving the page I just landed on

**Acceptance Criteria**:
- [x] **AC-US5-01**: New endpoint `GET /api/project/github-status` returns `{ hasGit: boolean, githubOrigin: string | null, status: "no-git" | "non-github" | "github" }`. `hasGit` true iff a `.git` directory is found by walking up from the project root. `githubOrigin` is the normalized github.com URL (via existing `parseGithubRemote`) or `null` when origin is missing or non-GitHub.
- [x] **AC-US5-02**: The Skill Overview tab gains a "Publish" status row that reads alongside the existing Repo/Homepage/License rows. The row shows one of three states:
  - `status === "github"` → green "Published-ready" badge + the existing PublishButton (graduates from editor-only).
  - `status === "non-github"` → amber "Origin is not GitHub" badge + a one-line hint pointing to `gh remote add origin <github-url>` and a Copy button.
  - `status === "no-git"` → amber "No GitHub repo yet" badge + a code block `gh repo create <derived-name> --public --source=. --remote=origin --push` with a Copy button.
- [x] **AC-US5-03**: The Copy button for any suggested command writes to `navigator.clipboard.writeText` and the button's `aria-label` is "Copy GitHub setup command".
- [x] **AC-US5-04**: Suggestions live ONLY on the Overview tab. The editor's existing PublishButton is unchanged; this AC does not delete or duplicate it.
- [x] **AC-US5-05**: The Overview row caches the `/api/project/github-status` result via the existing SWR pattern (`getProjectLayout`-style). Status updates after a `git remote` change become visible on the next fetch (no stale-cache pin).

### US-006: Sparse sidebar indicator when the project has no GitHub remote
**Project**: vskill

**As a** user scanning the sidebar of a fresh project
**I want** a single, sparse visual cue that this project is not yet connected to GitHub
**So that** I see the publish-readiness gap at a glance without leaving the studio

**Acceptance Criteria**:
- [x] **AC-US6-01**: When `/api/project/github-status` returns `status !== "github"`, the sidebar's AVAILABLE → Project section header gains a single small icon (cloud-off, ⚡, or equivalent) at the right edge with `aria-label` "GitHub not connected — click for help".
- [x] **AC-US6-02**: When `status === "github"`, NO icon is rendered (absence = healthy; we do not add a green icon to avoid icon noise).
- [x] **AC-US6-03**: Clicking the icon scrolls/focuses the currently-selected skill's Overview tab to the Publish row (or, when no skill is selected, opens the inline create flow / a focused help drawer that explains setup).
- [x] **AC-US6-04**: The icon's tooltip on hover names the exact next step ("Run `gh repo create ...` to publish your skills"). Long-form help lives on the Overview tab, not in the tooltip.
- [x] **AC-US6-05**: The icon is suppressed when the user has dismissed the hint via `localStorage` key `vskill-github-hint-dismissed-<projectRoot>` (shared with the Overview tab Dismiss action so the two affordances stay coherent).

## Non-Functional Requirements

- **Performance**: First-launch detection MUST not delay studio cold-start by more than 50 ms median (250 ms hard timeout).
- **Cross-platform**: Onboarding detection works on macOS, Linux, Windows (via win32 `where`).
- **Backward compatibility**: Server `AgentScopeEntry` adds an optional field — older UI bundles tolerate it (already a permissive interface).
- **Accessibility**: New CTA buttons have visible focus, descriptive `aria-label`, and operable keyboard activation.

## Out of Scope

- Marketplace UX redesign (covered by 0700/0771).
- `CreateSkillInline` body redesign (covered by 0699/0703).
- Telemetry events for the new flows.
- Changes to `vskill-platform` or any cloud surface.
- Changes to the `/api/authoring/create-skill` (separate, modal-based path).

## References

- `src/first-run-onboarding.ts` — onboarding gate
- `src/eval-server/api-routes.ts:120-275` — `AgentScopeEntry` and `buildAgentsResponse`
- `src/eval-ui/src/components/AgentScopePicker.tsx:185` — badge render
- `src/eval-ui/src/components/AgentScopePicker.Popover.tsx:294,482-487` — popover stats
- `src/eval-ui/src/components/RightPanel.tsx:194-200,367-406` — create handler + bare state
- `src/eval-ui/src/hooks/useCreateSkill.ts:615-645` — create flow
- `src/eval-server/skill-create-routes.ts:1149-1204` — 409 contract
- `src/eval-ui/src/components/Sidebar.tsx:447-451,505-526` — sidebar AVAILABLE counting + marketplace event
- `src/eval-ui/src/strings.ts:331,419` — existing "no API key needed" copy
