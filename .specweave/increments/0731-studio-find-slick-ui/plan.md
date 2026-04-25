---
increment: 0731-studio-find-slick-ui
title: "Studio Find — Slick Search → Select → Install"
type: feature
created: 2026-04-25
plan_authors: ["architect"]
related_adr: "0731-01-studio-search-palette-reuse.md"
target_repo: "repositories/anton-abyzov/vskill-platform"
runtime: "Cloudflare Workers (Next.js 15 App Router via @opennextjs/cloudflare)"
---

# Plan: Studio Find — Slick Search → Select → Install

## 1. Architecture Overview

End-to-end user flow inside `/studio/*`:

```
┌──────────────────────────────────────────────────────────────────────┐
│ Studio chrome (studio/layout.tsx — server component)                 │
│                                                                      │
│   ┌────────────────┐  ┌──────────────────┐                           │
│   │ FindNavButton  │  │ SubmitNavButton  │   ⟵ studio-nav-extras    │
│   └──────┬─────────┘  └──────────────────┘                           │
│          │ click / ⌘K                                                │
│          │ window.dispatchEvent(new CustomEvent("openSearch"))       │
│          ▼                                                           │
│   ┌──────────────────────────────────────┐                           │
│   │ StudioSearchPalette (client island)  │                           │
│   │   wraps <SearchPalette                │                           │
│   │     searchUrl="/api/v1/studio/search" │                           │
│   │     selectHref={(r) => "/studio/      │                           │
│   │       find/{owner}/{repo}/{skill}"}   │                           │
│   │     onSelect={(r, q) => POST          │                           │
│   │       /api/v1/studio/telemetry/       │                           │
│   │       search-select                   │                           │
│   │   />                                  │                           │
│   └──────────────────┬───────────────────┘                           │
│                      │ router.push(selectHref(result))               │
│                      ▼                                                │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │ /studio/find/[owner]/[repo]/[skill]/page.tsx (server)        │  │
│   │   getSkillByName + getSkillVersions                          │  │
│   │   ├─ Hero (TrustBadge, TierBadge, RepoLink, RepoHealthBadge) │  │
│   │   ├─ TaintWarning (when isTainted)                           │  │
│   │   ├─ <VersionPicker versions={...} /> (client island)        │  │
│   │   │      ↓ onChange(version) → useState in InstallPanel      │  │
│   │   ├─ <InstallPanel skillName version /> (client island)      │  │
│   │   │      TerminalBlock + Copy → clipboard + toast            │  │
│   │   │      POST /api/v1/studio/telemetry/install-copy          │  │
│   │   │             { skillName, version?, q: "", ts }           │  │
│   │   └─ Submit-find link in install footer (US-005)             │  │
│   └──────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

**Server vs client split**:

| File | Type | Reason |
|---|---|---|
| `studio/layout.tsx` | Server (default) | Static chrome; mounts client islands as children |
| `studio/components/FindNavButton.tsx` | **Client** (`"use client"`) | dispatches custom event, listens to keydown |
| `studio/components/StudioSearchPalette.tsx` | **Client** | wraps already-client `SearchPalette`; passes callbacks |
| `studio/find/[owner]/[repo]/[skill]/page.tsx` | Server (default) | DB reads via `getSkillByName` / `getSkillVersions`; ISR `revalidate = 3600` |
| `studio/find/[owner]/[repo]/[skill]/VersionPicker.tsx` | **Client** | useState for selected version |
| `studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx` | **Client** | clipboard, toast, telemetry beacon |
| `studio/page.tsx` | Server | Static home; the new CTA card uses an inline `"use client"` button or reuses `<FindNavButton />` |

**Cloudflare Workers constraints applied**:

- No Node-only APIs. Telemetry uses `fetch(..., { keepalive: true })` (NOT `sendBeacon`, because we need `X-Workspace-Fingerprint` header).
- ISR via `export const revalidate = 3600` on the server page (matches existing `/skills/[owner]/[repo]/[skill]/page.tsx`).
- Bundle impact: ~0 net new deps. `SearchPalette` is already shipped on `/skills`; the studio mount adds the wrapper (~30 LOC) + page (~250 LOC).

## 2. SearchPalette Refactor Strategy — Option A (Decision)

**Decision: Option A (props refactor)**. Rationale captured in **ADR 0731-01**. Summary:

- Pathname branching (Option B) couples studio's telemetry obligations into a generic component and obscures the new `search-select` telemetry side-effect.
- Full extraction into a hook (Option C) is overkill for two consumers and risks regressions against the 59-case existing test suite.
- Option A is a ~80-line diff with backward-compatible defaults — the platform mount keeps working unchanged.

### 2.1 New props (added to `SearchPalette`)

```ts
import type { SearchResult } from "./SearchPalette"; // export the type

interface SearchPaletteProps {
  /** Search API endpoint. Default: "/api/v1/skills/search" */
  searchUrl?: string;
  /** Build navigation href for a selected result. Default: skillUrl(result.name) */
  selectHref?: (result: SearchResult) => string;
  /** Fire-and-forget hook on result selection. Default: undefined (no-op) */
  onSelect?: (result: SearchResult, query: string) => void;
}

const DEFAULT_SEARCH_URL = "/api/v1/skills/search";
const DEFAULT_SELECT_HREF = (r: SearchResult) => skillUrl(r.name);

export default function SearchPalette({
  searchUrl = DEFAULT_SEARCH_URL,
  selectHref = DEFAULT_SELECT_HREF,
  onSelect,
}: SearchPaletteProps = {}) { ... }
```

### 2.2 Minimal diff inside `SearchPalette.tsx`

Three groups of edits (line numbers reference current file; will drift):

1. **Debounced search fetch (line 309) + SWR background-revalidate fetch (line 291)**: replace hard-coded `/api/v1/skills/search` with `${searchUrl}`.

2. **`handleLoadMore` fetch (line 337)**: same swap.

3. **`allItems` builder (line 428)** — href computation:
   ```diff
   - href: skillUrl(r.name),
   + href: selectHref(r as SearchResult),
   ```
   Pass the full `r` so studio callers can use `ownerSlug`/`repoSlug`/`skillSlug` directly. **Cleaner alternative** (preferred for execution): also store `sourceResult: r` on each skill item, so `navigate()` can fire `onSelect(item.sourceResult, query)` without a reverse lookup.

4. **`navigate` callback (line 435)** — add `onSelect` invocation BEFORE `router.push`:
   ```diff
   const navigate = useCallback((href: string) => {
   +  const item = allItems[selected];
   +  if (item?.type === "skill" && item.sourceResult && onSelect) {
   +    onSelect(item.sourceResult, query);
   +  }
     setOpen(false);
     router.push(href);
   }, [router, allItems, selected, onSelect, query]);
   ```
   Note: telemetry only fires for `type === "skill"` items (not category/action items).

5. **Export the `SearchResult` interface** at module scope so the studio wrapper can type its callbacks.

### 2.3 Backwards compatibility

The existing platform mount (`<SearchPalette />` with no props) is unchanged. All defaults preserve current behavior. The 59-case test suite (`SearchPalette.test.tsx`, 713 LOC) MUST pass without edits — this is the primary regression gate for the refactor.

## 3. New Files Spec

### 3.1 `src/app/studio/components/FindNavButton.tsx` (client, ~70 LOC)

**Purpose**: Discoverable nav entry for ⌘K palette inside studio chrome.

**Exports**: default `FindNavButton()` (no props).

**Behavior**:
- `<button>` styled identically to `SubmitNavButton` (mono font, `var(--bg-subtle)`, `borderRadius: 6`, `padding: "0.375rem 0.75rem"`).
- 14×14 search icon SVG (lucide-style: `<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>`).
- Label: "Find skills".
- `<kbd>` shortcut hint on the right edge: "⌘K" (Mac) / "Ctrl+K" (Win/Linux). Detect via `navigator.platform.includes("Mac")` lazily inside `useEffect` — SSR-safe with default "⌘K".
- `onClick` → `window.dispatchEvent(new CustomEvent("openSearch"))`.
- **Does NOT register its own keydown listener** — `SearchPalette` already handles ⌘K globally. We avoid double-toggle.
- `data-testid="studio-find-nav-button"`.
- `aria-label="Find verified skills — opens search (⌘K)"`.
- Reduced-motion: detect via `window.matchMedia("(prefers-reduced-motion: reduce)")` — when reduced, no shortcut-hint pulse animation. Simplest implementation: don't animate at all → AC-US1-05 satisfied trivially.

**Satisfies**: AC-US1-01, AC-US1-02, AC-US1-03 (via SearchPalette's existing listener), AC-US1-04, AC-US1-05.

### 3.2 `src/app/studio/components/StudioSearchPalette.tsx` (client, ~40 LOC)

**Purpose**: Thin wrapper that mounts `SearchPalette` with studio-flavored props.

**Exports**: default `StudioSearchPalette()` (no props).

**Implementation**:
```tsx
"use client";

import SearchPalette, { type SearchResult } from "@/app/components/SearchPalette";
import { useCallback } from "react";

const STUDIO_SEARCH_URL = "/api/v1/studio/search";
const TELEMETRY_URL = "/api/v1/studio/telemetry/search-select";

function buildStudioHref(r: SearchResult): string {
  if (r.ownerSlug && r.repoSlug && r.skillSlug) {
    return `/studio/find/${encodeURIComponent(r.ownerSlug)}/${encodeURIComponent(r.repoSlug)}/${encodeURIComponent(r.skillSlug)}`;
  }
  const parts = r.name.split("/");
  if (parts.length === 3) {
    return `/studio/find/${encodeURIComponent(parts[0])}/${encodeURIComponent(parts[1])}/${encodeURIComponent(parts[2])}`;
  }
  return `/studio/find/${encodeURIComponent(r.name)}`;
}

export default function StudioSearchPalette() {
  const onSelect = useCallback((r: SearchResult, q: string) => {
    const payload = JSON.stringify({ skillName: r.name, q, ts: Date.now() });
    try {
      // Custom header (X-Workspace-Fingerprint) is required by the telemetry route.
      // sendBeacon does not support custom headers, so we use fetch with keepalive.
      const fp = readWorkspaceFingerprint(); // helper exported from studio/lib (existing 0723 work)
      void fetch(TELEMETRY_URL, {
        method: "POST",
        body: payload,
        headers: { "Content-Type": "application/json", "X-Workspace-Fingerprint": fp },
        keepalive: true,
      });
    } catch { /* telemetry failure is non-fatal */ }
  }, []);

  return (
    <SearchPalette
      searchUrl={STUDIO_SEARCH_URL}
      selectHref={buildStudioHref}
      onSelect={onSelect}
    />
  );
}
```

**Note for `/sw:do`**: `readWorkspaceFingerprint` is the canonical helper used by `InstallButton` (and other studio telemetry callers). Confirm exact import path during implementation; existing pattern is in `src/app/studio/lib/` from 0723. If absent, lift the cookie-read logic into a shared helper before continuing.

**Satisfies**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06.

### 3.3 `src/app/studio/find/[owner]/[repo]/[skill]/page.tsx` (server, ~250 LOC)

**Purpose**: In-Studio skill detail with version selector and slick install panel.

**Implementation strategy**: Mirror the platform `/skills/[owner]/[repo]/[skill]/page.tsx` (909 LOC) but **slim down** to studio's needs — drop eval/popularity/agent-pills/extension-points/badge-embed sections. Keep:
- Back link (`<BackLink fallbackHref="/studio/find?q=<q-from-url>" />`).
- Hero: TrustBadge, name in `publisher/skill` format, byline (author · category · RepoLink · RepoHealthBadge · pluginName · skillPath · updatedAt).
- TaintWarning (when `isTainted`).
- Description.
- Labels.
- **Versions + Install** combined into one client island `<VersionedInstallSection>` (renders `<VersionPicker>` above `<InstallPanel>` and shares the `selectedVersion` state — see §3.4 / §3.5).
- BlockedSkillView (reuse the same component already in the platform page; lift to a shared module — see §3.7).
- Submit-find link in install footer (US-005).

**Caching**: `export const revalidate = 3600;` (same as platform).

**Metadata**: `generateMetadata` mirrors platform but title says "{name} (Studio Preview) | verified-skill.com" to disambiguate.

**Satisfies**: AC-US3-01, AC-US3-02, AC-US3-07, AC-US3-08.

### 3.4 `src/app/studio/find/[owner]/[repo]/[skill]/VersionPicker.tsx` (client, ~80 LOC)

**Purpose**: Renders the version list as accessible radio-group; emits selection upward via callback.

**Props**:
```ts
interface VersionPickerProps {
  versions: Array<{
    id: string;
    version: string;
    createdAt: Date;
    certTier: string;
  }>;
  selectedVersion: string;            // controlled
  onSelect: (version: string) => void;
}
```

**Markup**: `<div role="radiogroup" aria-label="Select skill version">` containing one `<button role="radio" aria-checked={...}>` per version. Each row shows `v{version} · {formattedDate} · {tier}`. The selected row shows a `›` indicator + bold text.

**Keyboard** (per ARIA APG radio-group pattern):
- Tab moves focus AWAY from the radiogroup.
- Inside the radiogroup, only the selected radio has `tabIndex={0}`; others have `tabIndex={-1}`.
- ↑/↓ moves focus + selection between versions.
- Enter / Space activates (button default behavior).

Reduced-motion respected (no transitions).

**Satisfies**: AC-US3-03, AC-US3-09 (partial — version rows are buttons; Enter activates).

### 3.5 `src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx` (client, ~120 LOC)

**Purpose**: Stateful container — version state + install command box + clipboard + toast + telemetry. Composes `<VersionPicker>` above the terminal block. Renders BLOCKED panel when `isBlocked`.

**Props**:
```ts
interface InstallPanelProps {
  skillName: string;                  // e.g., "anton-abyzov/vskill/0731-studio-find"
  defaultVersion: string;             // latest by default
  versions: Array<{ id: string; version: string; createdAt: Date; certTier: string }>;
  isBlocked?: boolean;
  blockedEntry?: BlockedSkillData;    // when isBlocked === true
}
```

**Behavior**:
- `useState<string>(defaultVersion)` — selected version.
- Install command derives from selection:
  - `selectedVersion === defaultVersion` (latest): `vskill install <skillName>`.
  - Otherwise: `vskill install <skillName>@<selectedVersion>`.
- Sanitize regex per AC-US3-04: `/^[a-zA-Z0-9._@/-]+$/`. If `skillName` fails, render the panel without copy button (defensive — should never happen for DB-stored skills).
- Renders `<VersionPicker>` ABOVE `<TerminalBlock>{installCmd}</TerminalBlock>` with copy button on the right.
- Copy: `navigator.clipboard.writeText(installCmd)` with insecure-context fallback (the existing `InstallButton.tsx` pattern using a hidden textarea + `document.execCommand("copy")`).
- Toast: `role="status" aria-live="polite"`, message `Run \`{installCmd}\` in your terminal`, auto-dismiss 3.5 s. Reuses styling from `SubmitNavButton`'s toast.
- Telemetry: fire-and-forget POST to `/api/v1/studio/telemetry/install-copy` with `{ skillName, version: selectedVersion === defaultVersion ? undefined : selectedVersion, q: "", ts }`. **Note**: `version` is omitted (not `null`) when latest — keeps the Zod schema additive and backward-compatible with existing `InstallButton` payloads. Use `fetch(..., { keepalive: true, headers: { "X-Workspace-Fingerprint": fp } })`.
- Footer (when not blocked): "Don't see what you need? Submit your skill →" link via existing `useSubmitDeepLink` hook.

**Blocked path**: if `isBlocked === true`, render the BLOCKED panel (mirrors `BlockedSkillView` from platform page §3.3). No version picker, no command, no copy button.

**Satisfies**: AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07, AC-US3-09 (Tab order: back → versions → copy).

### 3.6 Telemetry route — extend existing `[kind]` handler (NO new file)

**Discovery**: `src/app/api/v1/studio/telemetry/[kind]/route.ts` already exists as a dynamic-kind dispatcher (handles `submit-click`, `install-copy`, `lockdown`). Adding `search-select` requires:

1. Add `"search-select"` to the `KINDS` const tuple.
2. Add the schema:
   ```ts
   const searchSelectSchema = z.object({
     skillName: z.string().min(1).max(200),
     q: z.string().max(200).optional(),
     ts: z.number().int().positive(),
   });
   ```
3. Add the case in `schemaForKind()`.
4. Extend `installCopySchema` with optional `version` (backward-compatible):
   ```ts
   const installCopySchema = z.object({
     skillName: z.string().min(1).max(200),
     q: z.string().max(200).optional(),
     version: z.string().min(1).max(64).optional(),  // NEW (AC-US3-06)
     ts: z.number().int().positive(),
   });
   ```

**Important**: this means **NO new file is needed** — the original plan's "search-select telemetry route.ts" item collapses into a 4-line edit of the existing route. Workspace-fingerprint enforcement is automatic for non-lockdown kinds.

**Satisfies**: AC-US2-05, AC-US3-06.

### 3.7 `src/lib/skill-detail-view.tsx` — DEFERRED (not in scope)

The platform `/skills/[owner]/[repo]/[skill]/page.tsx` is 909 LOC with many platform-specific sections (eval, popularity, agent-pills, extension points, badge-embed) that the studio variant explicitly **does not** show. Lifting it into a shared component would either:
- Expose all those sections to studio (undesired), or
- Require ~12 boolean toggles bloating the API.

**Decision**: do NOT extract `lib/skill-detail-view.tsx`. Reuse the **leaf primitives** (TrustBadge, TierBadge, RepoLink, RepoHealthBadge, TaintWarning, SectionDivider, TerminalBlock, BackLink) directly. Some duplication of hero markup (~40 LOC) is acceptable — it's the part that intentionally diverges between surfaces.

**One small extraction is worth it**: lift `BlockedSkillView` (and its `BlockedRow` helper) from `skills/[owner]/[repo]/[skill]/page.tsx` to `src/app/components/BlockedSkillView.tsx` so both detail pages render the same blocked state. ~80 LOC, mechanical move.

## 4. Modified Files Spec

| File | Change | Approx LOC diff |
|---|---|---|
| `src/app/components/SearchPalette.tsx` | Add 3 optional props (`searchUrl`, `selectHref`, `onSelect`); swap 3 fetch sites + 1 href computation; add 1 onSelect call inside `navigate`; export `SearchResult` type. | +30 / −5 |
| `src/app/components/BlockedSkillView.tsx` (NEW via lift) | Move `BlockedSkillView` + `BlockedRow` out of platform page into shared component. | +90 / −90 |
| `src/app/skills/[owner]/[repo]/[skill]/page.tsx` | Remove now-extracted `BlockedSkillView` definition; import from `@/app/components/BlockedSkillView`. | −90 |
| `src/app/studio/layout.tsx` | Import `<FindNavButton />` and mount BEFORE `<SubmitNavButton />` in `studio-nav-extras`. Mount `<StudioSearchPalette />` once at end of layout (sibling of `{children}`). | +6 |
| `src/app/studio/page.tsx` | Add a feature-card-style block ABOVE the existing FEATURES grid: title "Find verified skills", copy "Search the registry. Trust signals inline. Install in one click.", primary CTA "Search skills (⌘K)" that dispatches `openSearch`. Accent `#06b6d4` (cyan) — matches existing studio aesthetic + QUICK_CMD button. Mobile: stacks above hero CopyButton via flex. | +30 |
| `src/app/studio/find/FindClient.tsx` | Wire `<ResultGrid>` row body click to navigate to `/studio/find/[owner]/[repo]/[skill]`. **Strategy**: keep card-level `<InstallButton>` (one-click fast install for power users); add separate "View details" affordance on card body that navigates to the new route. Two distinct affordances → two distinct test scenarios. | +20 |
| `src/app/api/v1/studio/telemetry/[kind]/route.ts` | (a) Add `"search-select"` to `KINDS`, schema, and `schemaForKind()`. (b) Extend `installCopySchema` with optional `version` field. | +12 |

## 5. Data Flow

### 5.1 Search → Detail navigation

1. User opens palette (⌘K via `SearchPalette`'s own listener, OR `<FindNavButton />` click → `window.dispatchEvent("openSearch")`) → `<StudioSearchPalette>` already mounted in `studio/layout.tsx`.
2. User types ≥2 chars → `SearchPalette` debounces 150 ms → `fetch("/api/v1/studio/search?q=...")` (studio-flavored URL via prop).
3. Studio `/api/v1/studio/search` route (existing, from increment 0716) returns same shape (`{ results, pagination }`); no changes.
4. User selects a result (Enter / click) →
   - `SearchPalette.navigate(href)` calls `onSelect(result, query)` → studio wrapper fires `fetch` to `/api/v1/studio/telemetry/search-select`.
   - `router.push(href)` where `href = "/studio/find/{owner}/{repo}/{skill}?from={encodedQuery}"` (`?from` appended by `selectHref` so the back link can return to the search results — see §5.3).

### 5.2 Detail → Install command derivation (NO server roundtrip on version change)

1. Server: `page.tsx` calls `Promise.all([getSkillByName(name), getSkillVersions(owner, repo, skill)])`.
2. `versions` is sorted desc by `createdAt` (already done in `getSkillVersions`). `defaultVersion = versions[0]?.version ?? skill.currentVersion`.
3. Server renders `<VersionedInstallSection skillName={skill.name} defaultVersion={defaultVersion} versions={versions.slice(0, 5)} />`.
4. Client (`InstallPanel`): `useState(defaultVersion)`. Render `vskill install ${skillName}` (no `@version`) when state === defaultVersion; otherwise `vskill install ${skillName}@${state}`.
5. `<VersionPicker selectedVersion={state} onSelect={setState} />` flips state on click. **No server roundtrip** — pure client state.

### 5.3 Back link

- `BackLink` reads `document.referrer`. If same-origin matches `/studio/find`, `router.back()` returns to cached search results (browser preserves scroll + state). Otherwise, fallback href is `/studio/find?q={q from ?from param}`.
- The `?from` param is set by `StudioSearchPalette.buildStudioHref` to preserve last query.

## 6. Telemetry Payloads

### 6.1 NEW: `POST /api/v1/studio/telemetry/search-select`

Request:
```json
{
  "skillName": "anton-abyzov/vskill/0731-studio-find-slick-ui",
  "q": "studio find",
  "ts": 1729900800000
}
```

Headers:
- `Content-Type: application/json`
- `X-Workspace-Fingerprint: <12-char hex>` (REQUIRED — enforced by `assertWorkspaceFingerprint`)

Response: `204 No Content` (success), `400 invalid_payload`, `403 workspace_mismatch`, `429 rate_limited`.

Persistence: `studioTelemetry` Prisma table, `kind = "search-select"`, `payload = parsed.data`.

Schema:
```ts
const searchSelectSchema = z.object({
  skillName: z.string().min(1).max(200),
  q: z.string().max(200).optional(),
  ts: z.number().int().positive(),
});
```

### 6.2 EXTENDED: `POST /api/v1/studio/telemetry/install-copy`

Add optional `version` field (backward-compatible):

```ts
const installCopySchema = z.object({
  skillName: z.string().min(1).max(200),
  q: z.string().max(200).optional(),
  version: z.string().min(1).max(64).optional(), // NEW
  ts: z.number().int().positive(),
});
```

- User copies the latest-version command → `version` omitted from the payload.
- User copies a non-latest command (e.g., `vskill install foo@1.2.3`) → `version: "1.2.3"`.
- Existing callers (`InstallButton` on result cards) do NOT send `version` → payload remains valid.

## 7. Accessibility Plan

### 7.1 Palette focus management

- `SearchPalette` already focuses `inputRef` on open. Studio mount inherits — no change.
- On close (Esc / backdrop click / route change), focus returns to `<FindNavButton>` via a ref + `useEffect` watching the palette open state.
- Implementation strategy: `FindNavButton` listens for the `openSearch` custom event AND a `closeSearch` event (or watches DOM mutations on the palette root). Simpler approach for `/sw:do`: add an `onClose?: () => void` prop to `SearchPalette` (3-line addition) and call it from the existing `setOpen(false)` sites. The studio wrapper passes `onClose={() => findNavRef.current?.focus()}`.

### 7.2 Version-row roles — `radiogroup` + `radio` (decision)

**Decision: ARIA `radiogroup` + `radio`** (not plain buttons). Reason: semantically there is exactly one selected version; selection drives downstream state (the install command). NVDA/JAWS announce "radio button, 3 of 5, v1.2.3, selected" — plain buttons announce only "button" without the selection state.

Implementation:
- Container: `<div role="radiogroup" aria-label="Select skill version">`.
- Rows: `<button type="button" role="radio" aria-checked={isSelected} tabIndex={isSelected ? 0 : -1}>`.
- Manual ↑/↓ key handler on the radiogroup that moves focus + selection.
- Tab moves focus AWAY from the radiogroup (per ARIA APG radio-group pattern).

### 7.3 Back-link behavior

- `BackLink` is keyboard-accessible (anchor with `onClick` calling `router.back()`). No additional work.
- Tab order on detail page: BackLink → version radios → copy button → submit-find link.

### 7.4 Reduced-motion strategy

- Palette open/close: no transition currently animates (instant render). No change needed.
- `FindNavButton` shortcut hint: render statically with no animation (simplest path to AC-US1-05).
- Toast: existing pattern uses no motion; reuse as-is.
- VersionPicker: no transitions on selection change.

### 7.5 ARIA labels recap

- FindNavButton: `aria-label="Find verified skills — opens search (⌘K)"`.
- StudioSearchPalette: inherits SearchPalette's existing labels.
- VersionPicker: `aria-label="Select skill version"` on radiogroup.
- InstallPanel copy button: `aria-label="Copy install command to clipboard"`.

## 8. Test Strategy

### 8.1 Unit tests (Vitest + React Testing Library)

| Test file | Coverage |
|---|---|
| `src/app/components/__tests__/SearchPalette.test.tsx` (existing, 713 LOC, 59 cases) | MUST keep passing without edits — backward-compat regression gate. |
| `src/app/components/__tests__/SearchPalette.props.test.tsx` (NEW) | Asserts: `searchUrl` is forwarded to `fetch` (debounced + load-more + SWR-revalidate sites); `selectHref(r)` produces the expected URL and is used by `router.push`; `onSelect(r, q)` fires once per skill selection (NOT for category/action items); existing platform mount with no props uses defaults unchanged. |
| `src/app/components/__tests__/BlockedSkillView.test.tsx` (NEW) | Renders BLOCKED banner with severity color, threat type, source URL, discovered-by, blocked-since. Lifted-component smoke. |
| `src/app/studio/components/FindNavButton.test.tsx` (NEW) | Renders, has correct testid + ARIA, click dispatches `openSearch`, ⌘K hint visible (Mac) / Ctrl+K (Win), reduced-motion respected (no animation classes/attributes). |
| `src/app/studio/components/StudioSearchPalette.test.tsx` (NEW) | Wraps SearchPalette with correct studio URL/selectHref/onSelect; telemetry POST fires on select with correct payload shape (`{skillName, q, ts}`); X-Workspace-Fingerprint header attached; `keepalive: true`. |
| `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/page.test.tsx` (NEW) | Server component — mock `getSkillByName`/`getSkillVersions`; assert hero, byline, version section, install panel render. 404 path. Blocked path. Tainted path. Metadata title contains "Studio Preview". |
| `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/VersionPicker.test.tsx` (NEW) | radiogroup ARIA, ↑/↓ key handling, Enter activates, onSelect fires with version string, default selected = first version, only selected has tabIndex 0. |
| `src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.test.tsx` (NEW) | Latest version → no `@version` suffix; older version → `@version` suffix. Clipboard write succeeds → toast appears. Clipboard missing → fallback used. Telemetry POST shape: `version` omitted for latest, populated otherwise. Sanitize regex blocks unsafe names. Blocked panel renders when `isBlocked`. |
| `src/app/api/v1/studio/telemetry/[kind]/__tests__/route.test.ts` (existing — extend) | Add cases for `search-select` (200 OK valid, 400 invalid, 403 workspace_mismatch, 429 rate_limited), `install-copy` with `version` field (additive — old payload still valid). |
| `src/app/studio/__tests__/page.test.tsx` (existing — extend) | Asserts new Find CTA card renders above feature grid with cyan accent and dispatches `openSearch` on click. |
| `src/app/studio/find/__tests__/FindClient.test.tsx` (existing — extend) | Asserts result-card body click navigates to `/studio/find/[owner]/[repo]/[skill]`; existing InstallButton-on-card scenarios continue to pass. |

Coverage targets: 95% line + branch on new files; existing `SearchPalette.tsx` net coverage MUST not drop.

### 8.2 E2E (Playwright)

`tests/e2e/studio-find-slick.spec.ts` (NEW):

**Scenarios**:
1. **Golden path (mouse)**: visit `/studio` → see Find CTA card → click "Search skills (⌘K)" → palette opens → type "vskill" → results appear → click first row → land on `/studio/find/.../...` → see version list → click older version → install panel updates to `@<version>` → click Copy → toast appears → assert clipboard contains correct command.
2. **Keyboard-only path**: visit `/studio` → press ⌘K → palette opens with focus on input → type "vskill" → ↓ → Enter → land on detail → Tab → first version radio focused → ↓ to second → Enter to select → Tab → copy button focused → Enter → toast appears.
3. **Back navigation**: from detail page, click "← Back to results" → land on `/studio/find?q=vskill` with results pre-loaded.
4. **Blocked skill path**: navigate directly to `/studio/find/<blocked-owner>/<blocked-repo>/<blocked-skill>` → assert BLOCKED panel renders, no copy button.
5. **Telemetry assertions**: spy on POSTs to `/api/v1/studio/telemetry/{search-select,install-copy}` — assert correct payload shapes per scenario; assert `X-Workspace-Fingerprint` header is set.

**Visual smoke**: `--project=chromium` at 1280×720 + mobile viewport (`iPhone 14`); dark + light themes (toggle via `<ThemeToggle>`).

### 8.3 TDD strict mode

`testing.tddEnforcement: "strict"` is active. Every task in `tasks.md` starts RED:
1. Write failing test(s) for the AC.
2. Run `npx vitest run <test-file>` → confirm FAIL.
3. Implement minimal code → confirm GREEN.
4. Refactor with safety net.

For E2E: scenario test written first against TODO selectors → confirm FAIL → implement components → confirm GREEN.

## 9. ADR

**Written**: `.specweave/docs/internal/architecture/adr/0731-01-studio-search-palette-reuse.md`.

**Decision**: Refactor `SearchPalette` via three optional props (`searchUrl`, `selectHref`, `onSelect`) with backward-compatible defaults. Both consumers share the same component module. Pathname branching (Option B) and full hook extraction (Option C) are rejected — see ADR for full rationale.

## 10. Risk Mitigations

| Risk | Mitigation |
|---|---|
| **R1**: `SearchPalette` prop refactor breaks the existing platform mount | Defaults match current hard-coded values exactly. The 59-case test suite (`SearchPalette.test.tsx`, 713 LOC) MUST pass without edits. New behavior covered by separate `SearchPalette.props.test.tsx`. |
| **R2**: `navigator.sendBeacon` cannot send custom headers (workspace fingerprint required) | Use `fetch(..., { keepalive: true, headers: { "X-Workspace-Fingerprint": fp } })` instead. `keepalive` survives navigation in CF Workers fetch contract. |
| **R3**: Studio palette ⌘K conflicts with platform palette ⌘K if both are mounted on the same page | `studio/layout.tsx` only renders inside `/studio/*`; platform palette is in the root layout. Verify root `layout.tsx` does NOT wrap `/studio/*` routes with `<SearchPalette />` — if it does, gate via `usePathname().startsWith("/studio")` in the platform mount. **Action item for `/sw:do`**: confirm mount sites first; remove platform palette from `/studio/*` if needed. |
| **R4**: `getSkillByName` returns null for skills present in search but not yet enriched | Mirror platform page handling: check blocklist, then rejected, then `notFound()`. Add smoke test calling studio detail page with a stub-only skill name → expect 404. |
| **R5**: Version selection state desyncs between `VersionPicker` and command output | Single source of truth: `useState` lives in `InstallPanel`, both children (VersionPicker + TerminalBlock) render from the same value. No prop drilling beyond one level. Unit test asserts: change version → command updates in same render tick. |
| **R6**: Cloudflare bundle size grows from new pages/components | +400 LOC ≈ +5 KB minified worst case. Studio bundle was ~80 KB; total well within CF Workers 1 MB compressed budget. Validate post-build via `npx next build` size report. |
| **R7**: `?from=` query parameter exceeds URL length on long queries | `q` is server-clamped to ≤200 chars (per `searchSelectSchema`). 200 URL-encoded chars ≤ 800 chars — within practical limits. |
| **R8**: ResultCard `onClick` regression — current behavior triggers immediate copy | Per §4: keep card-level `<InstallButton>` (copy), add separate "View details" affordance on card body (navigate). Two distinct affordances; existing InstallButton test continues to pass; add new test for card-body navigation. |
| **R9**: TDD strict gate blocks if any task lacks RED phase | Plan structures every task to start with a failing test (see tasks.md generated by `sw-planner`). Architect explicitly notes this for the planner. |
| **R10**: Adding `search-select` to telemetry route's lockdown branch breaks lockdown self-bypass | New kind goes through standard fingerprint + rate-limit path; lockdown self-bypass is unchanged. Existing test suite for `[kind]/route.ts` extended with `search-select` cases — adds, doesn't modify, lockdown tests. |
| **R11**: `BlockedSkillView` lift breaks the existing platform skill detail page | Mechanical move (cut from platform page, paste into shared component, re-import). Run `SearchPalette.test.tsx` + the existing platform page tests after lift to confirm no behavior change. |
| **R12**: Workspace fingerprint helper does not exist (needed by StudioSearchPalette) | Existing 0723 work created this for `InstallButton`. Confirm path during `/sw:do` exploration; if absent, lift the cookie-read into `src/app/studio/lib/workspace-fingerprint.ts` as a 1-task prereq. |

## 11. Implementation Sequence (suggested for `/sw:do`)

1. **T-001 to T-002**: BlockedSkillView lift (mechanical move). RED with `BlockedSkillView.test.tsx`, GREEN with platform page re-import.
2. **T-003 to T-005**: SearchPalette refactor (props + tests). PROVES backward compat first via existing 713-LOC suite.
3. **T-006**: FindNavButton + tests.
4. **T-007**: StudioSearchPalette wrapper + tests.
5. **T-008**: Studio layout integration (mount FindNavButton + StudioSearchPalette).
6. **T-009**: Telemetry route extension (`search-select` kind + `install-copy` version field) + tests.
7. **T-010 to T-012**: Studio find detail page + VersionPicker + InstallPanel + tests.
8. **T-013**: FindClient — wire result-card body click to navigate.
9. **T-014**: Studio home CTA card + tests.
10. **T-015**: Submit-find footer link on detail page (US-005).
11. **T-016**: E2E `studio-find-slick.spec.ts` golden path + keyboard path + back-nav + blocked path + telemetry assertions.

`sw-planner` agent generates the final `tasks.md` from this plan; the sequence above is a suggestion, not normative.

---

**Plan author**: architect (2026-04-25)
**Spec coverage**: All ACs from the approved plan (US-001 through US-005, AC-US1-01..05, AC-US2-01..06, AC-US3-01..09, AC-US4-01..03, AC-US5-01..02) addressed. Spec.md is being authored concurrently by `pm`; this plan was structured per the approved-plan ACs (`~/.claude/plans/declarative-marinating-rivest.md`) and reads trivially against the formal spec once `pm` finalizes.
