# Implementation Plan: Studio First-Launch Onboarding Polish

## Design

This increment is a four-part bundle inside the `vskill` package only. No `vskill-platform` or other repo changes.

### Part A — CLI onboarding (US-001)

`src/first-run-onboarding.ts` currently calls `anyProviderConfigured(env)` and prompts when ALL three providers (anthropic, openai, openrouter) are unset. It does not consider that `claude` (the Claude Code CLI binary) is itself a valid no-key runner.

**Change**:
1. Add `detectClaudeBinary(): boolean` — uses `child_process.spawnSync` with a 250 ms timeout. POSIX → `which claude`. win32 → `where claude`. Any non-zero exit, ENOENT, or timeout → `false`. Never throws.
2. In `firstRunOnboarding()`, call `detectClaudeBinary()` BEFORE `anyProviderConfigured()`. If either is true, return `{ action: "skip" }` silently — no stdout write.
3. When the prompt does fire (no claude, no keys), soften the wording. New copy lives in a constants block at the top of the file so tests can import it. Decline message gets a second line mentioning Claude Code as the no-key alternative.

**No architectural risk**: this is a pure additive guard at the top of one function.

### Part B — Server `pluginSkillCount` (US-002)

`src/eval-server/api-routes.ts` already imports `scanInstalledPluginSkills` indirectly (used by `skill-dir-registry.ts:72` and `utils/scan-install-locations.ts:124`). The agent-scope build at line 230-275 walks `AGENTS_REGISTRY` and computes per-agent `localSkillCount` + `globalSkillCount`. Plugin skills are a Claude-Code-only concept (the marketplace plugin model belongs to CC), so we count them once for `claude-code` and emit 0 for every other agent.

**Change**:
1. Extend `AgentScopeEntry` interface with `pluginSkillCount: number`.
2. In `buildAgentsResponse`, before the per-agent loop, call `scanInstalledPluginSkills({ agentId: "claude-code" })` once and cache its `length` as `claudePluginCount`.
3. Inside the loop, set `pluginSkillCount = agent.id === "claude-code" ? claudePluginCount : 0` on each entry.
4. Do **not** include `pluginSkillCount` in the `agentPresenceCache` cache-key — its value depends on the same filesystem state already keyed by `binariesKey + rootKey + homeKey`, so the existing 30 s TTL is correct.

**Risk**: `scanInstalledPluginSkills` walks the plugins cache directory. We already pay this cost elsewhere on warm paths; once-per-30-s in `buildAgentsResponse` is negligible.

### Part C — UI badge + popover (US-002)

`AgentScopeEntry → PickerAgentEntry` adapter at `AgentScopePicker.tsx:60-90` propagates the new count. Trigger render at line 185 expands from `(N · G)` to `(N · G · P)`. Popover stats grid at `AgentScopePicker.Popover.tsx:482-487` adds a Plugins row.

**Change**:
1. `PickerAgentEntry` gains `pluginCount: number`.
2. `agentsResponseToPickerEntries` maps `a.pluginSkillCount` → `pluginCount`.
3. `AgentScopePicker.tsx:177-186` trigger renders `({inst} · {glob} · {plug})` and the `<button>` gets `title="project · personal · plugins"`.
4. `AgentScopePicker.Popover.tsx` `AgentRow` at line 286-296 renders `{installedCount}·{globalCount}·{pluginCount}`.
5. The popover stats grid (`getDetailPaneContent` ~line 482) inserts a `<Row label={strings.scopePicker.statsPlugins} value={String(agent.pluginCount)} />` between Global and Last sync.
6. New string: `strings.scopePicker.statsPlugins = "Plugins"`.

**Backward compatibility**: server's older test fixtures may not emit `pluginSkillCount`. Make the adapter default to `0` when undefined (`a.pluginSkillCount ?? 0`). UI tests that assert badge text need a count fixture update.

### Part D — RightPanel onboarding empty state (US-003)

`RightPanel.tsx` has two empty-state surfaces:
- `EmptyState` component (line 209-211) — used in the "no skills at all" case via `state.skills.length === 0`.
- `renderEmptyState()` inline (line 367-405) — used when a skill IS selected but lookup misses, OR when the panel is in the test/standalone shell path.

The user's reported case: the project bucket has zero entries (no `.claude/skills/*` in the project), but `state.skills.length` may be > 0 because of global/plugin skills. The current branching does not distinguish "no project skills" from "no selection". Adding a richer check:

**Change**:
1. `RightPanel.tsx` derives `projectSkillsCount` by filtering `state.skills` where `s.scopeV2 === "available-project"` (existing field on `SkillInfo`).
2. New variant `EmptyState variant="empty-project"` rendered when no skill is selected AND `projectSkillsCount === 0`. Keep the existing `no-skills` variant for the global-and-all-empty case.
3. The new variant exposes two CTAs:
   - **Browse marketplaces** → `window.dispatchEvent(new CustomEvent("studio:open-marketplace"))` (existing, works because `App.tsx` already listens).
   - **Create new skill** → `setMode("create")` from `useStudio()` (existing — same path the no-skills variant uses).
4. Heading: `"No skills installed for this project yet."` Subhead: `"Browse the marketplace to install one, or author a new skill from scratch."`

**Why not modify `renderEmptyState()` directly?** That helper is a stateless test-friendly render. It has no access to `useStudio()` hooks. Putting the new logic at the StudioContext-aware top-level branch (line 205-213) keeps the test render pure.

### Part E — Create-skill flow hardening (US-004)

Two coupled fixes in `useCreateSkill.handleCreate` and the `RightPanel` `onCreated` callback.

#### E.1 — Reliable post-create navigation (AC-US4-01)

Current race in `RightPanel.tsx:194-198`:
```tsx
onCreated={(plugin, skill) => {
  setMode("browse");
  refreshSkills();      // async, no await
  selectSkill({ plugin, skill, origin: "source" });
}}
```

`selectSkill` (StudioContext.tsx:276-278) sets `window.location.hash` AND updates state. The hash flip is fine — that's the "URL of the new skill". But the right-pane render reads `state.skills.find(...)` to look up `skillInfo`; the new skill isn't in the list yet, so `skillInfo === null`, and `renderEmptyState()` runs. The user sees no change.

**Change**: mirror the working pattern from `App.tsx:751-753`:
```tsx
onCreated={async (plugin, skill) => {
  setMode("browse");
  await refreshSkills();
  selectSkill({ plugin, skill, origin: "source" });
}}
```
Or equivalently, use `revealSkill(plugin, skill)` after the await. The `await refreshSkills()` is the key — it guarantees the new skill is in `state.skills` before navigation reads it.

#### E.2 — 409 as idempotent recover-and-navigate (AC-US4-02)

Server contract at `skill-create-routes.ts:1202`:
```ts
sendJson(res, { error: `Skill already exists at ${targetDir}` }, 409, req);
```

`targetDir` is computed by `computeSkillDir(root, body.layout, body.plugin || "", body.name)` — the same target the client requested. The plugin and skill are knowable to the client (they were in the request body), so we don't need to parse the path; we already have the identity.

**Change** in `useCreateSkill.handleCreate`:
1. Wrap the `api.createSkill` call. If it throws an error whose message contains `already exists` (or, better, harden by adding a structured `409` code response from the server in a follow-up — for now string-match because `fetchJson` strips status), call `onCreated(effectivePlugin || basenameOfRoot, kebabName)` with the same identity the request carried.
2. Surface a neutral inline note instead of `setError(...)`: `setInfo("Skill already existed — opened it.")`. Add a new `info` state alongside `error` in the hook.
3. The component (`CreateSkillInline`, `CreateSkillPage`) renders `info` in a neutral pill; existing `error` styling stays for true errors.

**Server hardening** (defensive, not strictly required by the AC): change line 1202 to also include a structured field:
```ts
sendJson(res, {
  error: `Skill already exists at ${targetDir}`,
  code: "skill-already-exists",
  plugin: body.layout === 3 ? (basename(root) || "default") : body.plugin,
  skill: body.name,
}, 409, req);
```
This lets the client recognize the case without string matching. We will do this — small and safer.

#### E.3 — Double-click guard (AC-US4-03)

`useCreateSkill.handleCreate` already gates on `setCreating(true)` and the consuming components (`CreateSkillInline`, `CreateSkillPage`) disable the button via the `creating` flag. The acceptance test still asserts "two clicks → one POST" by spying on `api.createSkill`. No code change expected; AC is a guard against regression.

### Part F — GitHub sync visibility (US-005, US-006)

The user reported two coupled gaps: (1) the existing `PublishButton` is hidden inside the editor — invisible to first-launch users; (2) when the project has no GitHub remote at all, there is no contextual cue on what to do next. We surface this state in two places, deliberately sparse.

**Server**:
1. New endpoint `GET /api/project/github-status` in `api-routes.ts`. Reuses existing helpers:
   - The parent-walking `.git` locator (already at `api-routes.ts:790+`) → `hasGit`.
   - `parseGithubRemote(originRemote)` (line 769) on the value of `git -C <root> remote get-url origin` → `githubOrigin`.
2. Returns `{ hasGit, githubOrigin, status: "no-git" | "non-github" | "github" }`. Status decision is deterministic from the two booleans.
3. Uses `child_process.spawnSync('git', ['-C', root, 'remote', 'get-url', 'origin'])` with a 250 ms timeout — same robustness pattern as the onboarding detection. Failure → `hasGit: false, githubOrigin: null`.

**Client — Overview tab (US-005)**:
1. New component `PublishStatusRow` in `src/eval-ui/src/components/`. Renders inside `SkillOverview` alongside Repo/Homepage/License rows.
2. Three states drive the row content:
   - `github` — green "Publish-ready" badge + the existing `<PublishButton />` reused inline.
   - `non-github` — amber badge + one-line hint + Copy button for `gh remote add origin <github-url>`.
   - `no-git` — amber badge + code block + Copy button for `gh repo create <basename> --public --source=. --remote=origin --push`.
3. Fetches `/api/project/github-status` via SWR with cache key `project-github-status`. The hook is shared with the sidebar icon so a single fetch hydrates both surfaces.

**Client — Sidebar indicator (US-006)**:
1. The sidebar `AVAILABLE → Project` `NamedScopeSection` header (`Sidebar.tsx`) accepts an optional right-edge slot.
2. When `github-status !== "github"` AND the dismiss-key is not set, a single small `cloud-off` icon (Lucide-style, 12 px, color = `var(--color-warn)`) renders in the slot with an `aria-label` and `title` describing the next step.
3. Click handler:
   - If a skill is currently selected → focuses the `PublishStatusRow` on the Overview tab (sets `activeDetailTab='overview'` + scrolls the row into view via `ref.scrollIntoView({ behavior: "smooth", block: "center" })`).
   - If nothing is selected → opens the inline create flow OR a focused help drawer (`setMode("create")` is the cheapest path since the next user action is creating a skill).
4. Dismiss button on the Overview row writes `vskill-github-hint-dismissed-<projectRoot>` to localStorage; the sidebar icon listens to a `storage` event (or re-reads on next render) and disappears.

**Why "absence = healthy" instead of a green icon?** Sidebar real estate is precious; cluttering every healthy project with a green checkmark is noise. Only failure states deserve a glyph. This matches the existing pattern (e.g., `outdatedByOrigin`/`outdatedByScope` only renders when there ARE updates to surface).

**Why does the editor's PublishButton stay?** It already works for in-flight publishing — removing it would be a regression. The Overview row reuses the same component (composition, not duplication), so we have one publish source-of-truth at component level.

## Rationale

- **Why bundle four fixes?** They share a "first-launch UX polish" theme and touch overlapping files (RightPanel, AgentScopePicker, onboarding flow). Splitting would mean three near-identical PRs and three context-window costs for closure pipeline. Reviewer cost is amortized across one coherent narrative.
- **Why not migrate to `/api/authoring/create-skill`?** That's a larger architectural choice (the modal-based path vs the inline/page path); 0699/0703 already track that work. This increment fixes the existing path so users on `0.5.138` aren't broken today.
- **Why string-match the 409 message AND add a structured field?** String match keeps the fix self-contained when older servers exist in the wild (vskill-platform shipped pre-0.5.138 still emit the string-only payload). The new structured field is a forward-looking cleanup that future code can rely on.
- **Why count plugin skills only for `claude-code`?** Plugins are a Claude-Code-specific concept by current registry design (`scanInstalledPluginSkills` only walks `~/.claude/plugins/cache`). Other agents (Cursor, kimi, etc) don't have a plugin layer. Surfacing `0` for them is correct and avoids misleading users into thinking the count is missing.
- **Why `renderEmptyState` left alone, with the new logic above it?** The inline render is stateless by contract (used in `__tests__/detail-right-panel.test.tsx`). Pushing context-aware branching into the top-level component keeps test seams clean.
- **Why 250 ms timeout on `which claude`?** A cold first-run on a slow disk can pay 50-150 ms for a binary stat. 250 ms is a safe ceiling; in practice we see 5-30 ms. spawnSync is acceptable here because this is the first thing the studio does — no event loop to block.

## ADRs

No new ADRs. This increment respects:
- Existing studio-runtime architecture (eval-server.ts hosts a pre-built bundle; UI changes need `npm run build`).
- Existing scope model (project / personal / plugin) from 0686/0698.
- Existing event vocabulary (`studio:open-marketplace`, hash routing).
