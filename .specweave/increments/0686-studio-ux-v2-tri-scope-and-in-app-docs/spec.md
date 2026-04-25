---
status: ready_for_review
---
# 0686 — Studio UX v2: Tri-Scope Sidebar, Agent-Scope Picker, In-App Setup Docs

**Status:** planned • **Project:** vskill • **Priority:** high • **Test mode:** TDD • **Coverage target:** 90%

## 1. Context

Skill Studio today shows a two-section sidebar (OWN / INSTALLED) scoped to the project cwd and implicitly to Claude Code. As vskill grows to cover 49 agents with both local (`.<agent>/skills/`) and global (`~/.<agent>/skills/`) scopes, users cannot:
- Switch the studio's "active agent" without rebooting the app.
- See skills installed globally for the active agent (they only see the project-local wrapper).
- Find inline guidance on "how do I connect to OpenRouter" — the studio points to external docs.
- Perceive the OWN vs INSTALLED separation strongly enough (the 1px hairline reads as a group break, not a scope change).

0686 ships a cohesive v2 of the studio's navigation model built on four pillars:
1. **Home navigation** — clicking the "Skill Studio" brand returns to a canonical home (hash `#/`).
2. **Agent-scope picker** above the skill list — first-class selection of which agent's install surface we're browsing.
3. **Tri-scope sidebar** — OWN (user-authored, outside any wrapper) / INSTALLED (the selected agent's project-local skills) / GLOBAL (the selected agent's home-level skills). Bolder section dividers.
4. **In-app setup docs** — 480px right-slide SetupDrawer with provider-specific inline content (env vars, key URLs, local-provider start commands) — never a separate page.

Cross-cutting: full Mac + Windows + Linux path correctness, and first-class symlink transparency (users know whether a skill is a symlink or a copy, and to where).

## 2. Terminology

| Term | Definition |
| --- | --- |
| **Scope** | A filesystem territory where a skill lives. OWN / INSTALLED / GLOBAL. |
| **Active agent** | The agent whose INSTALLED + GLOBAL scopes populate the sidebar. Persisted in `studio.json` via 0682's `saveStudioSelection`. Claude Code is the default when present. |
| **Agent-scope picker** | The full-width control above the sidebar. Replaces the ambient "claude-code everywhere" assumption. |
| **SetupDrawer** | Right-slide 480px drawer surfacing per-provider setup content. Opens from the AgentModelPicker's "Need help connecting?" affordance and from scope-specific empty states. |
| **Installed (scope)** | Skills present in `<cwd>/<agent.localSkillsDir>/...` resolved for the active agent. |
| **Global (scope)** | Skills present in `<home>/<agent.globalSkillsDir>/...` resolved for the active agent. |
| **Own (scope)** | Skills found by the current source-layout scanner that are NOT inside an agent-wrapper folder. |

## 3. User Stories and Acceptance Criteria

### US-001 — Home navigation from the brand mark
**As a** studio user  
**I want** the "Skill Studio" logo top-left to behave as a home link  
**So that** I can return to the canonical landing view from any deep route (detail / updates / settings modal).

- **AC-US1-01**: Clicking the logo sets `window.location.hash = "#/"` and clears any selected skill.
- **AC-US1-02**: The logo renders as an `<a href="#/">` with `role="link"`, focusable via Tab, activatable via Enter and Space. (Not a `<button>` — semantics match destination.)
- **AC-US1-03**: The logo has a visible focus ring (2px `var(--border-focus)`) and `cursor: pointer`; hover state is a 4% surface tint, not an underline.

### US-002 — Agent-scope picker above the sidebar
**As a** studio user with multiple agents installed  
**I want** a first-class picker above the sidebar to choose which agent's install surface the sidebar shows  
**So that** I don't have to restart the app or edit config to browse Cursor's skills when I'm also a Claude Code user.

- **AC-US2-01**: A full-width 40px control is rendered at the top of the left pane, above the existing search input. The control is sticky — it remains visible when the scroll pane scrolls.
- **AC-US2-02**: The control shows the active agent's display name with a dot indicator (green = detected, amber = detected-but-locked, grey = no presence). Shape matches the `AgentModelPicker` trigger (same tokens).
- **AC-US2-03**: Clicking the control opens a two-pane popover (AgentList left, "scope stats" right) that follows the 0682 popover shell pattern (600px wide, top-center, fade-in 120ms, `Esc` closes).
- **AC-US2-04**: The AgentList is filtered to agents with presence — binary detected (`detectInstalled`) OR local folder exists OR global folder exists. Agents with zero presence appear at the bottom under a dim "Not detected" subheading, each showing a "Set up..." CTA that opens the SetupDrawer.
- **AC-US2-05**: The right pane (scope stats) shows, for the currently-focused agent: installed-skill count, global-skill count, last-sync timestamp (from `sync.ts` lockfile), and health ("ok" / "stale > 7d" / "missing"). Values come from a new `/api/agents/scopes` endpoint (see T-005).
- **AC-US2-06**: Clicking "Switch for this studio session" in the right pane sets the active agent, persists via `saveStudioSelection`, dispatches the `agent-changed` data event, and closes the popover. The sidebar re-fetches with the new agent.
- **AC-US2-07**: When multiple agents share a folder (e.g. `kimi` and `qwen` both use `~/.config/agents/skills`), the picker groups them under a single aggregate row showing: folder path, combined skill count, and a chip list of consumer IDs ("kimi", "qwen", ...). Selecting the aggregate row enters "shared-folder" mode — the sidebar shows all skills in that folder with a persistent banner listing consumers.

### US-003 — Tri-scope sidebar (OWN / INSTALLED / GLOBAL)
**As a** user authoring skills and using them across agents  
**I want** three distinct sections in the sidebar — my own drafts, what's installed for the active agent locally, what's installed globally — clearly separated  
**So that** I can reason about "where does this skill live?" without reading paths.

- **AC-US3-01**: The sidebar renders exactly three `SidebarSection` instances in the order OWN → INSTALLED → GLOBAL. Each has a kicker, count, collapse toggle, and status indicator.
- **AC-US3-02**: Each section is partitioned from the `/api/skills` response using `SkillInfo.scope` (new field, see T-003). Missing scope defaults to OWN for backward compatibility.
- **AC-US3-03**: Status indicator dot color: green when `filteredCount > 0` and `updateCount === 0`, amber when `updateCount > 0`, grey when `total === 0`.
- **AC-US3-04**: Each section's empty state is scope-aware: OWN says "No authored skills — run `vskill new`"; INSTALLED says "No skills installed for `<agent>` in this project — run `vskill install`"; GLOBAL says "No global skills for `<agent>` — run `vskill install --global`".
- **AC-US3-05**: Collapse state persists per-section in localStorage under keys `vskill-sidebar-own-collapsed`, `vskill-sidebar-installed-collapsed`, `vskill-sidebar-global-collapsed`. Default: expanded.
- **AC-US3-06**: When query filter is active, each section header shows `(N of M)` format (reusing existing `SidebarSection` behavior).
- **AC-US3-07**: `j`/`k` keyboard navigation walks flat across all three sections in order (existing flat-sort logic extends to three-section input).

### US-004 — Bolder section separation

> **SUPERSEDED by 0698-studio-multiproject-anthropic-scopes** (completed 2026-04-24).
>
> 0698 redesigns the sidebar away from the OWN/INSTALLED/GLOBAL tri-scope into a two-tier
> AVAILABLE/AUTHORING grouping (each split by source channel) using the existing `GroupHeader`
> small-caps utility — see 0698 §US-002. The 14px Source Serif 4 kicker / 3px divider block
> direction in this story (US-004) is no longer the target visual language; 0698 §3
> explicitly states "no new typography scale, no new fonts" and reuses the muted small-caps
> `GroupHeader` instead. Per-agent collapse storage keys also migrated to
> `vskill-sidebar-<agentId>-{available,authoring}-{project,personal,plugins}-collapsed`
> (see 0698 AC-US2-06 + the migration map). The dedicated `ScopeSection.tsx` primitive that
> shipped under T-009 was orphaned by that redesign and has been deleted (see plan.md note,
> 2026-04-25).
>
> AC-US4-01..04 below are kept for audit-trail traceability but mark `[ ] superseded`.

**As a** user scanning the sidebar
**I want** the divider between sections to read as a strong scope change, not a visual hairline
**So that** I don't mistake GLOBAL skills for more of the same INSTALLED list.

- **AC-US4-01**: [ ] superseded (by 0698 GroupHeader small-caps direction) — original target: section header uses 14px Source Serif 4 (display serif), all-caps letter-spacing `0.12em`, weight 600.
- **AC-US4-02**: [ ] superseded (by 0698 — no bold dividers; sub-sections separated by GroupHeader hierarchy) — original target: 3px solid `var(--color-rule)` divider block between sections.
- **AC-US4-03**: [ ] superseded (by 0698 — kicker color/typography tokens unused) — original target: 12px top / 4px bottom padding; colorized kicker per scope.
- **AC-US4-04**: [ ] superseded (by 0698 — visual baseline rebased on AVAILABLE/AUTHORING layout) — original target: Playwright visual-regression snapshot of three-section layout.

### US-005 — In-app setup docs (SetupDrawer)
**As a** user trying to connect a new provider  
**I want** inline setup instructions inside the studio  
**So that** I don't context-switch to a browser and lose my place.

- **AC-US5-01**: A `SetupDrawer` component renders as a right-slide drawer, 480px wide, overlaying the studio shell with a 40% backdrop, `role="dialog"`, `aria-modal="true"`, focus-trapped.
- **AC-US5-02**: The drawer is opened from three entry points: (1) the AgentModelPicker's "Need help connecting?" affordance on a locked-provider row; (2) the AgentScopePicker's "Set up..." CTA for agents with no presence; (3) scope-specific empty states ("Run `vskill install` — need help?").
- **AC-US5-03**: Drawer content is provider-specific. Supported providers on initial ship: `anthropic-api`, `openai`, `openrouter`, `gemini`, `ollama`, `lm-studio`, `claude-code`. Each provider's content renders a `SetupProviderView` via a registry lookup — no hardcoded switch in the drawer shell.
- **AC-US5-04**: Each `SetupProviderView` shows, in this order: (a) 1-sentence "what this is", (b) required env-var names in monospace with copy buttons, (c) a "Where to get the key" link to the provider console (see verified URLs below), (d) for local providers (Ollama / LM Studio): install command + start-server instructions + a pull-model example in bash code blocks, (e) a "Learn more" footer link to first-party docs.
- **AC-US5-05**: Verified provider URLs (research-sourced, immutable):
  - Anthropic API: `https://platform.claude.com/settings/keys`
  - OpenAI: `https://platform.openai.com/api-keys`
  - OpenRouter: `https://openrouter.ai/keys`
  - Gemini: `https://aistudio.google.com/apikey`
- **AC-US5-06**: For `claude-code` the view explicitly says: "No API key needed — vskill runs the official `claude` binary under your Pro/Max subscription. If you're not logged in, run `claude` in your terminal and authenticate with your Pro/Max account." (Matches research-verified copy.)
- **AC-US5-07**: The drawer never stacks on top of the SettingsModal. If SettingsModal is open, clicking "Set up..." closes the modal first, then opens the drawer (single-modal-at-a-time contract).

### US-006 — Max/Pro label accuracy on the Claude Code provider row
**As a** Claude Pro/Max subscriber  
**I want** the picker to accurately describe how my usage is billed  
**So that** I don't guess whether API keys are needed.

- **AC-US6-01**: The Claude Code row in `AgentModelPicker` shows a compact billing label tokenized in `strings.ts`. Original target literal was `"Covered by Max/Pro · overflow billed at API rates"`; **superseded by 0682 AC-US5-01** (voice policy bans the literal "Max/Pro" / "subscription" tokens in user copy). Shipped literal: `"Uses your Claude Code session · overflow billed at API rates"` — voice-lint enforces this wording.
- **AC-US6-02**: Hovering the row shows a tooltip with the exact research-verified copy: *"Your Claude Code CLI usage runs under your Pro/Max subscription quota. If you've enabled extra usage in your account settings, excess usage continues at standard API rates. Run `/usage` in Claude Code or visit claude.com Settings → Usage to see remaining quota — vskill can't display it directly."*
- **AC-US6-03**: On first-time selection of Claude Code as the active agent, an inline banner (dismissable, sessionStorage-scoped `vskill-ccode-banner-dismissed`) shows: *"Claude Code uses your Pro/Max subscription. No API key needed — vskill just runs the official `claude` binary on your behalf. Learn more."* The "Learn more" link opens the SetupDrawer for `claude-code`.
- **AC-US6-04**: The UI MUST NOT display numeric quota caps or 5-hour window values. The SetupDrawer explicitly links out rather than quoting numbers.

### US-007 — Cross-platform correctness (Mac + Windows + Linux)
**As a** Windows user  
**I want** the studio to correctly resolve `~/...` paths and never display POSIX literals  
**So that** I can browse global skills on Windows without filesystem errors.

- **AC-US7-01**: All tilde (`~`) resolution goes through a single utility `expandHome(p: string): string` in `src/utils/paths.ts` that uses `os.homedir()` + `path.join()`. No template-string splicing. No literal `/` separators.
- **AC-US7-02**: `expandHome("~/.claude/skills")` returns: darwin `/Users/<user>/.claude/skills`, linux `/home/<user>/.claude/skills`, win32 `C:\Users\<user>\.claude\skills`.
- **AC-US7-03**: Registry entries with POSIX-only semantics (e.g. `~/.config/agents/skills`) are mapped on `win32` via a `win32PathOverride?: string` field on `AgentDefinition`. When the override is absent, a deterministic fallback applies: `~/.config/X/` → `%APPDATA%/X/` expanded via `os.homedir() + "/AppData/Roaming/" + X`.
- **AC-US7-04**: The server's `/api/skills` endpoint MUST NOT return any path containing `~` — all paths in responses are fully resolved absolute paths with platform-native separators.
- **AC-US7-05**: Unit tests for `expandHome` and `resolveAgentGlobalDir` cover all 3 platforms by mocking `os.platform()` and `os.homedir()`.

### US-008 — Symlink transparency
**As a** user debugging why a skill won't update  
**I want** to see whether each skill is a symlink and to where  
**So that** I can trace edits back to their canonical plugin source.

- **AC-US8-01**: Every `SkillInfo` returned by `/api/skills` carries: `isSymlink: boolean`, `symlinkTarget: string | null` (absolute realpath), `installMethod: "symlinked" | "copied" | "authored"`. `"authored"` applies to OWN-scope skills.
- **AC-US8-02**: The sidebar `SkillRow` shows a small chain-link glyph when `isSymlink === true`. Hovering the glyph reveals a tooltip with `symlinkTarget`.
- **AC-US8-03**: The detail panel (RightPanel) adds an "Install method" row below existing metadata. Value renders: "Symlinked from `/Users/me/.claude/plugins/cache/foo/`" OR "Copied (independent)" OR "Authored" (for OWN scope).
- **AC-US8-04**: Symlink cycle detection — if realpath traversal visits the same inode twice, the scanner logs a warning and records `installMethod: "symlinked"` with `symlinkTarget: null` rather than hanging.

### US-009 — Shared-folder agent transparency
**As a** Kimi + Qwen user (both write to `~/.config/agents/skills`)  
**I want** the UI to represent the shared folder honestly  
**So that** I don't think a skill is installed twice when it's one file consumed by multiple agents.

- **AC-US9-01**: When two or more agents in the registry resolve to the same absolute `globalSkillsDir` (after `expandHome`), the AgentScopePicker groups them under a single aggregate row showing: the shared folder path (shortened as `~/.config/agents/skills`), combined skill count, and chip list of consumer display names.
- **AC-US9-02**: Selecting the aggregate row activates shared-folder mode. The sidebar header shows a persistent banner: "Shared folder — consumed by Kimi, Qwen". GLOBAL section skills render once; each skill row shows a "consumed by" chip list when `sourceAgent` metadata is ambiguous.
- **AC-US9-03**: De-dup algorithm: normalize path via `path.resolve(expandHome(dir))` and group agents keyed by that normalized path. Tested on the 49-agent registry fixture.

## 4. Non-Functional Requirements

- **Performance**: `/api/skills` with tri-scope scanning completes in ≤ 400ms on a cold cache for a home dir containing ≤ 200 skills. Warm cache ≤ 50ms (10s in-memory TTL).
- **Accessibility**: All new interactive elements meet WCAG AA. Agent-scope picker is keyboard-operable (Cmd+Shift+A or `a` to focus). Section dividers are `aria-hidden`; section headers are `<h2>`.
- **Theming**: New `--color-global` token added to both light + dark tokens (slate violet `#8B8FB1` light, `#6F748F` dark). All section-kicker colors respect `prefers-contrast: more`.
- **Security**: No new network egress introduced. SetupDrawer links use `rel="noopener noreferrer"` + `target="_blank"`.
- **i18n**: All user-facing strings live in `strings.ts`; component code reads from keys — no inline literals.

## 5. Out of Scope

- Editing GLOBAL-scope skills in-place (read-only; see "Copy to OWN" escape hatch — already exists in 0682 context-menu).
- Remote agent scopes (Cloud agents without filesystem presence).
- i18n translation files.
- Migrating existing `vskill-sidebar-installed-collapsed` localStorage key — kept as-is for continuity.

## 6. Dependencies

- **0682 studio-agent-model-picker** — SettingsModal, `useCredentialStorage` hook, `saveStudioSelection`, AgentModelPicker popover shell pattern.
- **0683 studio-update-notifications** — `/api/skills/updates` endpoint + `updateCount` prop plumbing. Extend `outdatedByOrigin` from `{source, installed}` to `{own, installed, global}`.

## 7. Traceability

| AC-ID | Task | E2E |
| --- | --- | --- |
| AC-US1-01..03 | T-001 | E2E-01 |
| AC-US2-01..07 | T-002, T-005, T-006 | E2E-02, E2E-06 |
| AC-US3-01..07 | T-003, T-007, T-008 | E2E-03 |
| AC-US4-01..04 | T-009 | E2E-03 |
| AC-US5-01..07 | T-010, T-011 | E2E-04 |
| AC-US6-01..04 | T-012 | E2E-04 |
| AC-US7-01..05 | T-013, T-014 | — |
| AC-US8-01..04 | T-004, T-015 | E2E-05 |
| AC-US9-01..03 | T-016 | E2E-06 |
