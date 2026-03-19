# Implementation Plan: Configuration Properties Reference Page

## Overview

Create a single comprehensive Configuration Reference page at `docs-site/docs/reference/configuration.md` documenting all `config.json` properties, `metadata.json` properties, environment variables, and a disableable features quick-reference table. The page uses the same Docusaurus MDX patterns as existing reference pages (commands.md, skills.md).

## Architecture Decision: Single Page vs Multi-Page

**Decision: Single page with anchored sections.**

**Rationale:**
1. **Existing precedent** -- `commands.md` (642 lines) and `skills.md` (889 lines) are both single comprehensive pages. A configuration reference of ~800-1000 lines fits this pattern.
2. **Searchability** -- Users Cmd+F within a single page for property names. Splitting across pages fragments search.
3. **Docusaurus TOC** -- Docusaurus auto-generates a right-hand Table of Contents from headings, providing in-page navigation equivalent to a multi-page sidebar.
4. **Cross-reference density** -- Config properties often relate to each other (e.g., `sync.settings.autoSyncOnCompletion` relates to `hooks.post_increment_done`). Internal anchor links on a single page are smoother than cross-page links.
5. **Maintenance** -- One file to update when config types change, rather than coordinating across multiple files.

**Trade-off acknowledged:** If the page exceeds ~1500 lines, consider extracting `sync` (the largest section) into a sub-page. Current estimate: ~900-1100 lines, well within single-page territory.

## Page Structure

```
reference/configuration.md
├── Frontmatter (sidebar_position: 4, title, description)
├── Introduction (what config.json is, where it lives, how to edit)
├── Quick Reference: Disableable Features (table)
├── config.json Reference
│   ├── Top-Level Properties (version, language)
│   ├── project (ProjectMetadata)
│   ├── testing (TestingConfig)
│   ├── limits (LimitsConfig)
│   ├── sync (SyncConfiguration) -- largest section
│   ├── hooks (HookConfiguration)
│   ├── umbrella (UmbrellaConfig)
│   ├── cicd (CiCdConfig)
│   ├── archiving (ArchivingConfig)
│   ├── livingDocs (LivingDocsConfig)
│   ├── apiDocs (ApiDocsConfig)
│   ├── documentation (DocumentationConfig)
│   ├── planning (PlanningConfig)
│   ├── translation (TranslationConfiguration)
│   ├── pluginAutoLoad (PluginAutoLoadConfig)
│   ├── incrementAssist (IncrementAssistConfig)
│   ├── contextBudget (ContextBudgetConfig)
│   ├── deduplication (DeduplicationConfig)
│   ├── statusLine (StatusLineConfiguration)
│   ├── grill (GrillConfig)
│   ├── skillGen (SkillGenConfig)
│   └── adapters (AdapterConfiguration)
├── metadata.json Reference
│   ├── Core Fields (id, status, type, created, lastActivity)
│   ├── Status Lifecycle (IncrementStatus enum values)
│   ├── Increment Types (IncrementType enum values)
│   ├── Testing Overrides (testMode, coverageTarget)
│   ├── State Transition Fields (pausedAt, abandonedAt, etc.)
│   ├── Multi-Project Fields (projectId, multiProject, externalContainer)
│   ├── Sync Fields (syncTarget, externalRefs)
│   └── PR Fields (prRefs)
├── Environment Variables
│   ├── Core (SPECWEAVE_DISABLE_HOOKS, SPECWEAVE_DISABLE_AUTO_LOAD, etc.)
│   ├── External Tool Auth (GITHUB_TOKEN, JIRA_API_TOKEN, JIRA_EMAIL, AZURE_DEVOPS_PAT)
│   ├── Import (SPECWEAVE_IMPORT_ENABLED, SPECWEAVE_IMPORT_TIME_RANGE_MONTHS, SPECWEAVE_IMPORT_PAGE_SIZE)
│   ├── Debug/Development (DEBUG, SPECWEAVE_DISABLE_LOCKS, SPECWEAVE_FORCE_LOCKS)
│   └── Miscellaneous (SPECWEAVE_SHELL, SPECWEAVE_AUTO_INSTALL, VSKILL_NO_TELEMETRY)
└── See Also (links to sync-configuration guide, dashboard config page, etc.)
```

## Technology Stack

- **Format**: Docusaurus MDX (`.md` with optional JSX)
- **Components used**: Standard Docusaurus admonitions (`:::tip`, `:::warning`, `:::info`), tables, code blocks
- **No custom components needed** -- existing `CommandTabs` is for commands, not config reference. Standard markdown tables + code blocks are the right fit for property documentation.

## Documentation Style

Each config section follows a consistent pattern:

```markdown
### `sectionName`

Brief description of what this section controls.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `property1` | `string` | `"value"` | What it does |
| `property2` | `boolean` | `true` | What it does |

**Example:**
```json
{
  "sectionName": {
    "property1": "value",
    "property2": true
  }
}
```
```

This matches the tabular style used in `commands.md` quick reference tables and provides scannable, grep-friendly documentation.

## Sidebar Integration

Add the new page to `sidebars.ts` under the `Reference` category:

```typescript
{
  type: 'category',
  label: 'Reference',
  collapsed: true,
  items: [
    {type: 'doc', id: 'reference/index', label: 'Reference Overview'},
    // ... existing items ...
    {type: 'doc', id: 'reference/configuration', label: 'Configuration Reference'},  // NEW
    // ... rest of items ...
  ],
}
```

Position it after "Skills & Cost" and before "Changelog" since configuration is a fundamental reference topic.

## Reference Index Update

Update `reference/index.md` to add a "Configuration Reference" entry in the Quick Navigation section, linking to the new page.

## Source of Truth

All property names, types, and defaults are derived from `src/core/config/types.ts` (the `SpecWeaveConfig` interface and `DEFAULT_CONFIG` constant) and `src/core/types/increment-metadata.ts` (the `IncrementMetadata` and `IncrementMetadataV2` interfaces). Environment variables are collected from grep of `process.env.SPECWEAVE_*` and related patterns across the source.

## Testing Strategy

This is a documentation-only increment. Verification:
1. `npm run build` in docs-site must succeed (validates MDX syntax, broken links)
2. All internal links resolve (Docusaurus broken link checker)
3. Sidebar renders correctly with new entry
4. Visual inspection of rendered page

## Technical Challenges

### Challenge 1: Keeping docs in sync with source types
**Solution**: Document the source file (`src/core/config/types.ts`) prominently at the top of the page so future contributors know where to verify properties.
**Risk**: Low -- config types change infrequently and the page includes version annotations (e.g., "v1.0.231+") matching the source code JSDoc.

### Challenge 2: Page length management
**Solution**: Use Docusaurus right-hand TOC (auto-generated from H2/H3 headings) for navigation. Keep individual property descriptions concise (1 sentence). Use collapsible `<details>` blocks for lengthy examples only if needed.
**Risk**: Low -- estimated ~900-1100 lines, comparable to existing reference pages.

## Implementation Phases

### Phase 1: Create the page
- Create `reference/configuration.md` with frontmatter and all sections
- Document all `config.json` properties from `SpecWeaveConfig` interface
- Document `metadata.json` properties from `IncrementMetadata`/`IncrementMetadataV2`
- Document environment variables

### Phase 2: Integration
- Update `sidebars.ts` to include the new page
- Update `reference/index.md` Quick Navigation to link to new page
- Add cross-links from/to related pages (sync-configuration, dashboard/config)

### Phase 3: Verification
- Build docs-site and verify no broken links
- Verify sidebar rendering
- Verify TOC navigation works
