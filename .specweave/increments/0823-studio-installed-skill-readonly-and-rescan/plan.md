# Implementation Plan: Studio installed-skill read-only Source view + comprehensive origin resolver + rescan endpoint

## Overview

Three coupled deliverables in one increment:

1. **UI: Read-only Source tab** — new `SourcePanel` + `SourceFileTree` components mounted via a new `source` tab in `RightPanel.tsx`. Visible to all personas (read-only). Consumes the already-existing `GET /api/skills/:plugin/:skill/files` and `/file` endpoints.
2. **Backend: Comprehensive Origin Resolver** — new `src/eval-server/origin-resolver.ts` walks a five-tier provenance chain (project lockfile → user-global lockfile → frontmatter source → Anthropic-skill registry → bare-name) and returns a complete `OriginEnvelope`. `skill-name-resolver.ts` delegates to it. `/api/skills/:plugin/:skill/versions` envelope is extended with `trackedForUpdates` + `provider` fields.
3. **Backend: Rescan endpoint** — `POST /api/v1/skills/:id/rescan` validates the slug, resolves origin, fetches upstream versions, emits `skill.updated` via `dataEventBus`, returns `{ jobId }`. The SSE event reaches `useStudio().updatesById` so `CheckNowButton` clears its spinner via existing polling logic.

Q3 (Models tab) is documented as investigated-no-action — the per-model leaderboard is correct behavior for both author and consumer personas.

## Architecture

### Components

#### Backend (`src/eval-server/`)

- **`origin-resolver.ts`** (NEW)
  - `resolveSkillOrigin(skill, plugin, root): Promise<OriginEnvelope>` — full provenance resolution.
  - `OriginEnvelope` type: `{ source: "platform" | "anthropic-registry" | "local", owner: string | null, repo: string | null, provider: "vskill" | "anthropic" | "local", trackedForUpdates: boolean, lockfilePath?: string, frontmatterSource?: string, registryMatch?: string }`.
  - `ANTHROPIC_SKILL_REGISTRY` const map: well-known Anthropic-shipped skill names → `{owner: "anthropic-skills", repo: <name>}`.
  - Cache key: `${plugin ?? ""}::${skill}` (mirrors existing resolver). Reuses `resolverCache` import or its own cache instance — TBD during implementation.
  - Walks tiers in order; first hit wins; bare-name fallback preserves the no-poison guard from `skill-name-resolver.ts:50`.

- **`skill-name-resolver.ts`** (MODIFIED)
  - Delegate to `resolveSkillOrigin()` for all resolution paths.
  - Preserve existing `resolveSkillApiName(skill, root, plugin)` signature (returns string `owner/repo/skill` or bare name) so existing callers (api-routes.ts) don't change.
  - Implementation becomes: call `resolveSkillOrigin()`, if `owner && repo` return `${owner}/${repo}/${skill}`, else return bare `skill`.

- **`api-routes.ts`** (MODIFIED)
  - Extract `fetchUpstreamVersions(skill, plugin, root)` helper from existing `/versions` route (lines 2102-2184) so both `/versions` and the new `/rescan` use it.
  - Extend `/versions` envelope: add `trackedForUpdates` (boolean) and `provider` (string) fields. Compute `trackedForUpdates = origin.trackedForUpdates && versions.length > 0`.
  - Add new `router.post("/api/v1/skills/:id/rescan", ...)` route after the SSE update route (~line 2310). URL-decode `:id` into `(plugin, skill)`, validate via `isSafeSkillName`, call `fetchUpstreamVersions`, emit `skill.updated` via `emitDataEvent`, return `{ jobId: crypto.randomUUID() }`.

- **`data-events.ts`** (MODIFIED if needed)
  - Verify `skill.updated` is in the `DataEventType` union; add if missing.
  - Confirm `dataEventBus` subscriber path reaches the SSE stream consumed by `useSkillUpdates` (the existing `platform-proxy.ts:248` emission may bypass the bus and write directly — need to either align both paths to use the bus, or have rescan write directly to the same SSE writer).

#### Frontend (`src/eval-ui/src/`)

- **`components/SourcePanel.tsx`** (NEW)
  - Two-pane layout: `SourceFileTree` on left (~280px), content viewer on right (flex).
  - Fetches `GET /api/skills/:plugin/:skill/files` on mount, defaults selection to `SKILL.md`.
  - On file select: fetches `GET /api/skills/:plugin/:skill/file?path=<relative>`, dispatches to renderer based on extension/mime.
  - Renderers: `<SkillContentViewer />` for `.md`, `<TextFileViewer />` for code/text, `<ImageFileViewer />` for images, `<BinaryFilePlaceholder />` for everything else.
  - Renders provider chip in the header.

- **`components/SourceFileTree.tsx`** (NEW)
  - Pure presentational recursive tree. Folders collapsible. Active file highlighted. File icons by extension. Keyboard nav: arrows + Enter + Escape.
  - Receives `files: FileEntry[]`, `activePath: string`, `onSelect: (path: string) => void`.

- **`components/TextFileViewer.tsx`** (NEW, small)
  - Monospace `<pre>` with optional line numbers. No syntax highlighting in v1 (defer to follow-up to keep bundle small).

- **`components/RightPanel.tsx`** (MODIFIED)
  - Add `"source"` to `DetailTab` type (line 51), `ALL_TABS` (line 76), `LEGACY_REDIRECTS` (identity), and `TAB_DESCRIPTORS` BEFORE the `edit` entry (line 60).
  - Mount `<SourcePanel />` in the panel switch (`WorkspacePanel`).
  - Update `applyPersonaRedirect`: read-only personas land on `source` instead of `overview` for unknown deep links and as the default tab.
  - Update `panelIdToDetail` legacy bridge: `"editor"` panel id → `{tab: "source"}` for read-only or `{tab: "edit"}` for authors.

- **`components/VersionHistoryPanel.tsx`** (MODIFIED)
  - Read `provider` and `trackedForUpdates` from versions envelope.
  - Replace "Local-only — this skill is not registered on verified-skill.com" with "No upstream registry — this skill ships without origin metadata, so update tracking is unavailable" when `source === "none"`.
  - Render provider chip on each version row.
  - Hide `<CheckNowButton />` when `trackedForUpdates === false`.

- **`components/CheckNowButton.tsx`** (UNCHANGED — already respects `trackedForUpdates` prop)
  - Caller (RightPanel/VersionHistoryPanel) passes the new envelope flag through.

- **`components/ProviderChip.tsx`** (NEW, small)
  - Inline pill with three variants: `vskill` (light blue), `Anthropic` (orange), `Local` (gray).

- **`api.ts`** (MODIFIED)
  - Add `listSkillFiles(plugin, skill): Promise<FileEntry[]>` — calls existing `GET /files`.
  - Add `getSkillFile(plugin, skill, path): Promise<{ content: string, mimeType: string, size: number, isBinary: boolean }>` — calls existing `GET /file`.
  - Existing `rescanSkill` is unchanged on the client (it was correct all along; the fix is server-side).

### Data Flow

```
Source tab opens
  → SourcePanel mounts
  → GET /api/skills/:plugin/:skill/files  (returns FileEntry[])
  → render SourceFileTree, default-select SKILL.md
  → GET /api/skills/:plugin/:skill/file?path=SKILL.md
  → render via SkillContentViewer

Click another file
  → onSelect(path)
  → GET /api/skills/:plugin/:skill/file?path=<path>
  → dispatch renderer by ext/mime

Versions tab opens
  → GET /api/skills/:plugin/:skill/versions
  → server: resolveSkillOrigin → fetchUpstreamVersions
  → envelope: { versions, count, source, trackedForUpdates, provider }
  → UI renders provider chip + version list (or no-upstream message)
  → if trackedForUpdates: render CheckNowButton

Click Check now
  → POST /api/v1/skills/.claude%2Fnanobanana/rescan
  → server: validate slug → resolveSkillOrigin → fetchUpstreamVersions
  → emitDataEvent("skill.updated", { plugin, skill, versions, ... })
  → SSE stream pushes to client useSkillUpdates → updatesById.set(...)
  → CheckNowButton's polling detects entry → clears spinner
```

### ADRs to reference / create

- Reference existing **0707** (Versions tab + diff endpoint design) and **0747** (single-skill SSE update endpoint).
- Reference existing **0708** (Check now button + tracked state).
- Reference existing **0764** (isInstalled enrichment for versions endpoint).
- Reference existing **0765** (plugin-aware resolver for installed-agent dirs).
- New ADR (optional, lightweight in `.specweave/docs/internal/architecture/adr/`): **ADR-XXXX: Comprehensive Origin Resolver for Skill Provenance** — motivates the five-tier chain and the Anthropic registry.

### Critical files

| File | Change |
|------|--------|
| `src/eval-server/origin-resolver.ts` | NEW — five-tier provenance resolver + Anthropic registry |
| `src/eval-server/skill-name-resolver.ts` | MOD — delegate to origin-resolver |
| `src/eval-server/api-routes.ts` | MOD — extract fetchUpstreamVersions helper, extend /versions envelope, add /rescan route |
| `src/eval-server/data-events.ts` | MOD if needed — ensure `skill.updated` in event union and bus reaches SSE consumer |
| `src/eval-ui/src/components/RightPanel.tsx` | MOD — register Source tab |
| `src/eval-ui/src/components/SourcePanel.tsx` | NEW — two-pane layout + renderer dispatch |
| `src/eval-ui/src/components/SourceFileTree.tsx` | NEW — recursive tree |
| `src/eval-ui/src/components/TextFileViewer.tsx` | NEW |
| `src/eval-ui/src/components/ImageFileViewer.tsx` | NEW (small) |
| `src/eval-ui/src/components/BinaryFilePlaceholder.tsx` | NEW (small) |
| `src/eval-ui/src/components/ProviderChip.tsx` | NEW |
| `src/eval-ui/src/components/VersionHistoryPanel.tsx` | MOD — message swap + provider chip + CheckNow gate |
| `src/eval-ui/src/api.ts` | MOD — listSkillFiles + getSkillFile |
| `tests/playwright/source-tab.spec.ts` | NEW |
| `tests/playwright/check-now.spec.ts` | NEW |
| `tests/playwright/version-tracking.spec.ts` | NEW |

### Existing utilities to reuse (do NOT reimplement)

- `resolveAllowedSkillDir(root, plugin, skill, allowedRoots)` — `src/eval-server/skill-resolver.ts:61` — traversal-safe skill dir resolution. Already used by `/files` route.
- `resolveSkillDirForFsRoute(plugin, skill)` — `src/eval-server/api-routes.ts:2408`.
- `isSafeSkillName(s)` — `src/eval-server/api-routes.ts:2245`.
- `dataEventBus` / `emitDataEvent` — `src/eval-server/data-events.ts:28`.
- `parseSource` — `src/eval-server/resolvers/source-resolver.ts`.
- `readLockfile(dir)` — `src/lockfile/lockfile.ts:22`.
- `SkillContentViewer` — `src/eval-ui/src/components/SkillContentViewer.tsx`.
- `parseFrontmatter` / `renderMarkdown` — existing UI utilities.
- `useStudio()` — `src/eval-ui/src/StudioContext.tsx:412`.

## Testing Strategy

TDD discipline (RED → GREEN → REFACTOR) per AC. Tests run via `npx vitest run` (unit/integration) and `npx playwright test` (E2E). Each task in tasks.md begins with a failing test before implementation.

### Unit / Integration (Vitest)
- `src/eval-server/__tests__/origin-resolver.test.ts` — five-tier precedence, registry hits, cache key
- `src/eval-server/__tests__/skill-name-resolver.test.ts` (extended) — delegates to origin-resolver, preserves bare-name fallback
- `src/eval-server/__tests__/api-routes.versions-envelope.test.ts` — trackedForUpdates + provider fields
- `src/eval-server/__tests__/api-routes.rescan.test.ts` — 200/400/SSE emission/idempotency
- `src/eval-ui/src/components/__tests__/SourcePanel.test.tsx` — tree + content viewer dispatch
- `src/eval-ui/src/components/__tests__/SourceFileTree.test.tsx` — keyboard nav, collapse/expand
- `src/eval-ui/src/components/__tests__/RightPanel.sourceTab.test.tsx` — tab visibility per persona
- `src/eval-ui/src/components/__tests__/VersionHistoryPanel.providerChip.test.tsx` — message swap + chip render

### E2E (Playwright)
- `tests/playwright/source-tab.spec.ts` — open Studio → click Source → assert SKILL.md + tree → click file → assert content updates
- `tests/playwright/check-now.spec.ts` — click Check now on tracked skill → POST 200 → spinner clears within 30s
- `tests/playwright/version-tracking.spec.ts` — Anthropic-shipped skill (slack-messaging) shows upstream versions + Anthropic chip; vskill-installed (nanobanana) shows vskill chip; genuinely-local shows clear no-upstream message + no Check now button

### Manual browser verification (Claude Preview MCP)
8-step flow defined in user-approved plan at `/Users/antonabyzov/.claude/plans/starry-bubbling-summit.md`. Screenshots captured at steps 4, 5, 6, 8 for the increment closure record.

## Risks & Open Questions

1. **`skill.updated` event-bus vs direct SSE write** — `platform-proxy.ts:248` may write directly to the SSE stream rather than going through `dataEventBus`. If so, rescan must use the same writer rather than the bus, OR both paths must be unified through the bus. Decision deferred to implementation; will be made when wiring the rescan SSE emission.
2. **Anthropic skill registry maintenance** — hardcoded list will drift over time. Mitigation: ship updates with new vskill releases; future increment can move to a remote-fetched manifest.
3. **Cache invalidation** — origin-resolver cache lives for the studio process lifetime. After `vskill install --global` writes a new lockfile entry, the studio must be restarted to pick it up. Acceptable for now (existing resolver has the same property); document in user-facing notes if needed.
4. **TextFileViewer line numbers performance** — for files >5,000 lines, line-number rendering may be slow. Mitigation: cap line-number rendering at 5,000 lines and show "(truncated for display)".
5. **Bundle size** — adding SourcePanel + tree + 4 renderers grows the UI bundle. Estimate: ~8-12 KB minified gz. Acceptable.

## Verification

After implementation, run inside `repositories/anton-abyzov/vskill`:
```bash
npx vitest run                                # unit + integration (target: 95%+ pass)
npm run build                                 # bundle UI changes
node dist/cli/cli.js studio &                 # start local studio on port 3157
npx playwright test                            # E2E
```

Browser verification via Claude Preview MCP — 8-step flow:
1. `preview_start` against `http://localhost:3157`
2. Navigate to `#/skills/project/.claude/slack-messaging`
3. `preview_snapshot` — confirm Source tab visible (US-001)
4. `preview_click` Source → `preview_snapshot` — confirm SKILL.md body + folder tree
5. `preview_click` a file in the tree → confirm content updates
6. Navigate to `#/skills/project/.claude/nanobanana` → click Versions → confirm upstream versions render with vskill provider chip
7. Click Check now → `preview_network` — confirm POST /rescan returns 200, spinner clears
8. Return to `slack-messaging` Versions tab → confirm "Anthropic" chip + upstream versions render (registry hit) — OR if registry doesn't include slack-messaging, confirm "No upstream registry" message and Check now hidden
