# Architecture Plan: Redesign SpecWeave Documentation Site

## Approach

Content restructure across 5 phases. No new architecture decisions (ADRs) needed -- this is a sidebar + content reorganization within the existing Docusaurus setup.

**Key constraint**: No file moves or renames. All changes preserve existing URLs. Sidebar-only restructure for orphaned files; new files only for dashboard docs.

## Phase 1: Sidebar Restructure (sidebars.ts)

### Design

Modify `sidebars.ts` to surface all 46 orphaned files. Changes are additive -- no existing entries removed or reordered.

#### New Categories in docsSidebar

1. **"Dashboard & Observability"** -- top-level category (collapsed: true), positioned after Agent Teams
   - `guides/analytics-dashboard` (existing orphan, serves as overview/entry point)
   - 10 new dashboard pages from US-003: `guides/dashboard/errors`, `guides/dashboard/sync`, `guides/dashboard/activity`, `guides/dashboard/config`, `guides/dashboard/services`, `guides/dashboard/notifications`, `guides/dashboard/marketplace`, `guides/dashboard/plugins`, `guides/dashboard/agents`, `guides/dashboard/hooks`

2. **"Sync Deep Dives"** subcategory under Integrations (collapsed: true)
   - `guides/sync-configuration`
   - `guides/sync-strategies`
   - `guides/spec-bidirectional-sync`
   - `guides/spec-commit-sync`
   - `guides/status-sync-guide`
   - `guides/status-sync-migration`
   - `guides/multi-project-sync-architecture`
   - `guides/umbrella-sync-routing`
   - `guides/hierarchy-mapping`

3. **"Migration Guides"** subcategory under Reference (collapsed: true)
   - `guides/migration-v024`
   - `guides/migration-v031-project-fields`
   - `reference/changelog`

#### Additions to Existing Categories

4. **Commands** section -- add 4 orphaned command pages:
   - `commands/abandon`
   - `commands/pause`
   - `commands/resume`
   - `commands/status`

5. **Skills** section -- add:
   - `skills/skill-contradiction-resolution` (after skill-discovery-evaluation)

6. **Enterprise sidebar** Migration category -- add:
   - `enterprise/knowledge-transfer-migration`

7. **Integrations** -- add:
   - `integrations/generic-ai-tools`

8. **Overview** -- add:
   - `overview/ai-revolution-context` (after philosophy)

9. **Core Concepts** -- add:
   - `guides/core-concepts/who-benefits-from-living-docs` (after living-documentation)

10. **Guides** -- reorganize with new subcategories:

    **"Advanced Topics"** subcategory (collapsed: true):
    - `guides/plugin-management`
    - `guides/lazy-plugin-loading`
    - `guides/deployment-platforms`
    - `guides/github-action-setup`
    - `guides/project-specific-tasks`
    - `guides/repository-selection`
    - `guides/increment-status-reference`
    - `guides/scheduling-and-planning`
    - `guides/specs-organization-guide`
    - `guides/meta-capability`
    - `guides/deep-interview-mode`

    **"Learning & Comparison"** subcategory (collapsed: true):
    - `guides/specweave-learning-journey`
    - `guides/specweave-vs-speckit`
    - `guides/ai-coding-benchmarks`
    - `guides/why-verified-skill-matters`

    **"Platform-Specific"** subcategory (collapsed: true):
    - `guides/mobile/react-native-setup-guide`
    - `guides/openclaw-agent-setup`
    - `guides/ado-multi-project-migration`

    **Remaining orphans** as direct items under Guides:
    - `guides/agent-skills-extensibility-analysis`
    - `guides/command-reference-by-priority`
    - `guides/life-automation`
    - `guides/multilingual-guide`

11. **Standalone items** at bottom of docsSidebar:
    - `api/index` (label: "API Reference")
    - `examples/index` (label: "Examples")

### Sidebar Ordering Rationale

The new "Dashboard & Observability" category is placed after Agent Teams because:
- It is a feature exploration section (how-to), not a core concept
- Agent Teams comes before it in the learning journey (you use agents, then observe them)
- Keeping it near Integrations groups operational concerns together

## Phase 2: Features Page Trim (overview/features.md)

### Design

Replace the 605-line features.md with a ~150-line hub page. Strategy:

1. Keep the page title, intro paragraph, and "Three Ways to Work" section (already concise)
2. For each remaining feature section, condense to:
   - 2-3 sentence summary
   - "Learn more" link to the relevant detail page
3. Feature sections to link out to:
   - Specification-First Development -> `guides/core-concepts/what-is-an-increment`
   - Multi-Agent Architecture -> `guides/agent-teams-and-swarms`
   - Skills & Plugins -> `skills/index`
   - Autonomous Execution -> `guides/autonomous-execution`
   - Dashboard & Observability -> `guides/analytics-dashboard`
   - External Tool Integration -> `guides/integrations/external-tools-overview`
   - Quality Gates -> `workflows/validation`
   - Testing -> `academy/fundamentals/testing-fundamentals`
   - Cost Tracking -> `reference/cost-tracking`
   - Living Documentation -> `guides/core-concepts/living-documentation`
   - Multi-Project Setup -> `guides/multi-project-setup`
   - Model Selection -> `guides/model-selection`

### Content Preservation

Every feature currently described in the monolith has a corresponding detail page already in the docs. The trimmed page becomes a navigation hub -- no information is deleted from the site.

## Phase 3: Dashboard Documentation (10 new files)

### Design

Create `docs/guides/dashboard/` directory with 10 new markdown files. Each file documents one dashboard page based on the actual source code in `src/dashboard/client/src/pages/`.

#### File List and Source Mapping

| New Doc File | Source Component | Key Features to Document |
|---|---|---|
| `errors.md` | `ErrorsPage.tsx` | Error grouping by type, session context, timeline buckets, paginated error list, KPI cards (total/unique/sessions) |
| `sync.md` | `SyncPage.tsx` | Platform connection status, per-repo sync status, sync permissions, diagnostic messages, import/skip counts |
| `activity.md` | `ActivityPage.tsx` | Activity event feed, category filters (command/hook/notification/cost), severity filters, real-time SSE updates |
| `config.md` | `ConfigPage.tsx` | Live config.json editing, expandable sections, field-level edits, validation errors, save/reset, SSE-driven refresh |
| `services.md` | `ServicesPage.tsx` | Service status monitoring, port conflict detection, start/stop commands, external links, KPI cards |
| `notifications.md` | `NotificationsPage.tsx` | Notification feed (info/warning/critical), dismiss/dismiss-all, filter by status (pending/dismissed/all), severity sorting |
| `marketplace.md` | `MarketplacePage.tsx` | Scanner status, discovery queue, verified skills list, approve/reject workflow, security scores, rate limiting |
| `plugins.md` | `PluginsPage.tsx` | Installed plugins list, skill usage stats (count/success/failure/duration), LSP status, bar charts |
| `agents.md` | `AgentsPage.tsx` | Agent lifecycle tracking (started/stopped/duration), session filtering, real-time agent events via SSE |
| `hooks.md` | `HooksPage.tsx` | Hook event log, event type filtering (PreToolUse, PostToolUse, Stop, etc.), time range filtering, consecutive event collapsing |

#### Page Template (consistent structure)

```markdown
---
sidebar_label: Page Title
description: One-line description
---

# Dashboard: Page Title

Brief description of what this page shows and when to use it.

## What You'll See

- Key UI elements and data displayed
- KPI cards and their meaning

## Key Features

### Feature 1
Description of the feature.

### Feature 2
Description.

## How to Access

`specweave dashboard` -> navigate to page

## Related Pages

- [Link to related dashboard page](../dashboard/related.md)
- [Link to related concept page](../../path/to/concept.md)
```

Each page stays under 150 lines per AC-US3-06.

## Phase 4: Cross-Linking Pass

### Design

Add contextual links in 4 areas:

1. **analytics-dashboard.md** (existing): Add a "Dashboard Pages" section at the end linking to all 10 new capability pages
2. **Sync guides**: Each of the 9 sync guides gets a small "Related" footer linking to `guides/integrations/external-tools-overview` and 1-2 most relevant sibling sync guides
3. **Migration guides**: Link to `reference/changelog` from each migration guide
4. **Features page** (trimmed): Already handled in Phase 2 -- each section links to its detail page (15+ links total)

Cross-linking is minimal and purposeful -- no "see also" spam. Each link connects genuinely related topics.

## Phase 5: Build Verification

### Design

Run `npm run build` in docs-site directory. Expected checks:
- Exit code 0
- No broken link warnings (onBrokenLinks: 'warn' in docusaurus.config.ts)
- All 10 new pages render (valid frontmatter)
- No duplicate doc IDs

If build fails, fix issues (likely: typos in doc IDs, missing frontmatter). Re-run until clean.

## Task Dependencies

```
Phase 1 (sidebar) ---+
                     +--> Phase 4 (cross-links) --> Phase 5 (build)
Phase 2 (features) --+
                     |
Phase 3 (dashboard) -+
```

Phases 1, 2, and 3 are independent and can be parallelized. Phase 4 depends on all three (needs the new dashboard files to exist and the sidebar entries to be correct). Phase 5 is the final gate.

## Risk Mitigation

1. **Doc ID typos**: Each orphaned file was identified by automated scan -- IDs are exact matches from the filesystem
2. **Frontmatter issues in orphaned files**: These files already exist and were presumably buildable when created. If any have invalid frontmatter, fix during Phase 5
3. **Features page link rot**: All target pages are already in the docs. Cross-reference against the orphan list to ensure nothing links to a still-orphaned page
4. **Dashboard doc accuracy**: Each new page is derived from reading the actual TypeScript interfaces and component code -- not guessing at features

## Files Modified

| File | Change Type | Phase |
|---|---|---|
| `docs-site/sidebars.ts` | Modified (add categories + items) | 1, 3 |
| `docs-site/docs/overview/features.md` | Modified (trim from 605 to ~150 lines) | 2 |
| `docs-site/docs/guides/dashboard/errors.md` | New | 3 |
| `docs-site/docs/guides/dashboard/sync.md` | New | 3 |
| `docs-site/docs/guides/dashboard/activity.md` | New | 3 |
| `docs-site/docs/guides/dashboard/config.md` | New | 3 |
| `docs-site/docs/guides/dashboard/services.md` | New | 3 |
| `docs-site/docs/guides/dashboard/notifications.md` | New | 3 |
| `docs-site/docs/guides/dashboard/marketplace.md` | New | 3 |
| `docs-site/docs/guides/dashboard/plugins.md` | New | 3 |
| `docs-site/docs/guides/dashboard/agents.md` | New | 3 |
| `docs-site/docs/guides/dashboard/hooks.md` | New | 3 |
| `docs-site/docs/guides/analytics-dashboard.md` | Modified (add dashboard page links) | 4 |
| 9 sync guide files | Modified (add Related footer) | 4 |
| 2 migration guide files | Modified (add changelog link) | 4 |

**Total**: 1 modified sidebar + 1 trimmed features page + 10 new dashboard pages + ~12 files with cross-link additions = ~24 file touches
