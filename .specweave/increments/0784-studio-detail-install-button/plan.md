# Implementation Plan: Studio detail — primary Install button + readability pass

## Architecture summary

Pure UI change to two files in the Studio find detail route. Zero backend, schema, or auth changes. Reuses existing telemetry, clipboard, and security primitives.

```
┌─────────────────────────────────────────────────────────────────┐
│ /studio/find/[owner]/[repo]/[skill]/page.tsx (Server Component) │
│ - swap --text-faint → --text-muted (informational labels)       │
│ - swap "See all versions →" color → --accent-teal               │
│                                                                 │
│   <InstallPanel skillName={...} versions={...} ... />           │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │ InstallPanel.tsx (Client Component)                       │ │
│   │   <VersionPicker />                                       │ │
│   │   ┌───────────────────────────────────────────────────┐   │ │
│   │   │ <button data-testid="studio-install-primary       │   │ │
│   │   │   -button" onClick={runInstallAction}>Install</…> │   │ │ ← NEW
│   │   └───────────────────────────────────────────────────┘   │ │
│   │   <TerminalBlock>                                         │ │
│   │     vskill install owner/repo/skill                       │ │
│   │     [Copy] ← existing overlay, also calls runInstall…     │ │
│   │   </TerminalBlock>                                        │ │
│   │   <Toast />                                               │ │
│   │   <Footer />  (--text-muted, was --text-faint)            │ │
│   └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
            │
            │ POST /api/v1/studio/telemetry/install-copy
            ▼  (existing endpoint, unchanged)
```

## Components

### Component changes

**File**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx`

1. **Refactor `onCopy` → `runInstallAction`**: rename and stabilize the callback so it's clearly the shared action. Logic is identical: SAFE_NAME guard → `copyViaClipboard` → toast → fire-and-forget telemetry.
2. **Add primary Install button** above the `TerminalBlock`. Uses Tailwind primary-blue classes mirroring [InstallButton.tsx:102](repositories/anton-abyzov/vskill-platform/src/app/studio/find/components/InstallButton.tsx). `data-testid="studio-install-primary-button"`. Disabled when `!safe`. Hidden when blocked (the blocked branch already short-circuits the panel).
3. **Footer color**: line 204 `color: "var(--text-faint)"` → `"var(--text-muted)"`.

**File**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/page.tsx`

| Line | Element | Before | After |
|---|---|---|---|
| 154 | "Skill v…" chip color | `var(--text-faint)` | `var(--text-muted)` |
| 161 | publisher prefix `<span>` color | `var(--text-faint)` | `var(--text-muted)` |
| 215 | "See all versions →" color | `var(--text-muted)` | `var(--accent-teal)` |
| 265 | `bylineStyle.color` | `var(--text-faint)` | `var(--text-muted)` |
| 270 | `bylineSep.color` (dot separator) | `var(--text-faint)` | **unchanged** (decorative) |

### Test changes

**File**: `repositories/anton-abyzov/vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/__tests__/InstallPanel.test.tsx`

Add 6 new test cases that cover AC-US1-01 through AC-US1-08. See `tasks.md` for Given/When/Then per AC.

## Dependencies

- React 18 / Next.js 15 (already in vskill-platform).
- Vitest + React Testing Library (already wired).
- Tailwind CSS (already configured — `bg-blue-600`, `hover:bg-blue-700`, etc. resolve at build time).
- `authFetch` from `@/lib/auth-fetch` (existing).
- Endpoint `POST /api/v1/studio/telemetry/install-copy` (existing, no schema change).

## ADRs

No new ADRs needed. This is a UI refinement that reuses approved patterns.

Reference: any future change that wires the Install button to perform a real local install would require a new ADR extending `install-engine-routes.ts` allow-list (currently only `vskill` and `anthropic-skill-creator` engines).

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Two buttons firing telemetry on a single click (double-count) | Low | Each button fires on its own click event; no shared timer. AC-US1-08 asserts independence. |
| Tailwind blue clashes with Studio's teal accent | Low | Marketplace already establishes "blue = install" via `InstallButton.tsx`. Visual cohesion preserved. |
| Color swap regresses dark theme | None | In dark theme `--text-faint` and `--text-muted` resolve to identical `#8B949E`. Swap is a no-op there. |
| "See all versions →" color change creates link inconsistency | None | Aligns with existing "Submit your skill →" link in the same panel. |

## Verification

See spec.md "Success Criteria" and the plan-mode verification workflow:
1. `npx vitest run …/InstallPanel.test.tsx` — all green.
2. `npm run build` (or typecheck) — no new TS errors.
3. Smoke test in browser via `npm run dev`.
4. DevTools color-pick to confirm `#666666` on swapped labels (light theme).

## Out of scope

- Real local-install action (would need new install-engine route).
- Source-tagged telemetry.
- Dark theme contrast pass.
- Restyling other Studio surfaces.
