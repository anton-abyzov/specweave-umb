# Architecture Plan: 0556-docs-overhaul

## Overview

This is a documentation restructure, not a code feature. The architecture covers file operations strategy, batch scripting, sidebar restructure, CSS fixes, content consolidation, and redirect map generation. All work targets `repositories/anton-abyzov/specweave/docs-site/`.

## Current State Analysis

| Metric | Current | Target |
|--------|---------|--------|
| Total pages | 297 | ~50 |
| Sidebars defined | 11 (docsSidebar, gettingStartedSidebar, integrationsSidebar, enterpriseSidebar, guidesSidebar, apiSidebar, commandsSidebar, referenceSidebar, skillsSidebar, academySidebar, learnSidebar) | 6 |
| Navbar items | 5 doc + blog | 5 doc + blog (same count, different labels) |
| Glossary terms | 83 files | ~20 (SpecWeave-specific only) |
| `/specweave:` stale prefixes | 784 across 90 files | 0 |
| Ghost plugins | 12 | 0 |
| Ghost commands | 9 | 0 |

### Directory Structure (Current)

```
docs/
  DOCUMENTATION-AUDIT-2025-11-25.md    # DELETE
  DOCUMENTATION-RESTRUCTURE-PLAN.md    # DELETE
  faq.md                                # KEEP
  features.md                           # MERGE into overview/features.md
  intro.md                              # DELETE (redirect exists)
  metrics.md                            # KEEP
  quick-start.md                        # MERGE into getting-started/index.md
  academy/        (32 files)            # KEEP (canonical learning)
  api/            (1 file)              # KEEP
  commands/       (12 files)            # CONSOLIDATE to ~5
  enterprise/     (9 files)             # CONSOLIDATE to ~5
  examples/       (1 file)              # EVALUATE
  getting-started/(2 files)             # KEEP
  glossary/       (86 files)            # PRUNE to ~20
  guides/         (55+ files)           # HEAVY CONSOLIDATION
  integrations/   (2 files)             # MERGE into guides/integrations
  learn/          (10 files)            # DELETE (duplicate of academy)
  overview/       (10 files)            # CONSOLIDATE to ~6
  reference/      (7 files)             # KEEP
  scripts/        (5 files)             # DELETE (non-docs)
  skills/         (18 files)            # CONSOLIDATE to ~8
  workflows/      (10 files)            # CONSOLIDATE to ~5
```

## Architecture Decision: Phased Execution Order

The overhaul runs in 6 phases. Each phase is a buildable checkpoint -- the Docusaurus build must pass after each phase before proceeding. This prevents cascading breakage.

### Phase 1: Scripted Prefix Replacement (AC-US1-01)

**What**: Replace all 784 `/specweave:` prefix instances with `/sw:` across 90 files.

**Strategy**: Single `sed` pass with dry-run verification.

```bash
# Step 1: Dry run -- count matches
grep -r '/specweave:' docs/ --include='*.md' --include='*.mdx' | wc -l

# Step 2: Execute replacement (macOS sed)
find docs/ -type f \( -name '*.md' -o -name '*.mdx' \) \
  -exec sed -i '' 's|/specweave:|/sw:|g' {} +

# Step 3: Verify zero remaining
grep -r '/specweave:' docs/ --include='*.md' --include='*.mdx' | wc -l
# Expected: 0
```

**Edge case**: Code blocks. The `sed` replacement is prefix-agnostic (works inside fenced code blocks as well as prose), which is the correct behavior per spec edge case "Stale prefix in code blocks: Replace inside fenced code blocks as well."

**Verification**: `npx docusaurus build` must succeed.

### Phase 2: File Deletion (AC-US2-01, AC-US3-03)

**What**: Remove 29+ identified files that are non-documentation, duplicates, or ghost content.

**Deletion order matters**: Delete leaf files first, then directories, so no intermediate build breaks from missing sidebar references.

**Batch 1 -- Non-documentation files (no sidebar refs)**:
- `docs/DOCUMENTATION-AUDIT-2025-11-25.md`
- `docs/DOCUMENTATION-RESTRUCTURE-PLAN.md`
- `docs/scripts/` (entire directory: .py, .md reports)
- `docs/guides/youtube-tutorial-script.md`
- `docs/guides/youtube-tutorial-script-v2.md`
- `docs/guides/youtube-tutorial-script-v3.md`

**Batch 2 -- Duplicate/stale root files**:
- `docs/intro.md` (redirect already exists to overview/introduction)
- `docs/quick-start.md` (duplicate of getting-started/index)
- `docs/features.md` (duplicate of overview/features)

**Batch 3 -- learn/ directory** (AC-US3-03):
- Delete entire `docs/learn/` directory (10 files)
- Remove `learnSidebar` from sidebars.ts
- Redirect entries: every `/learn/*` path maps to `/academy/fundamentals/*`

**Batch 4 -- Glossary generic terms** (AC-US8-01):
- Delete ~63 generic glossary term files (api.md, cli.md, docker.md, angular.md, react.md, kubernetes.md, terraform.md, etc.)
- Keep ~20 SpecWeave-specific terms: increment, skill-chain, grill-report, living-docs, spec-md, tasks-md, plan-md, metadata-json, quality-gate, brownfield, greenfield, hooks, bidirectional-sync, source-of-truth, ac-id, acceptance-criteria, user-stories, etc.
- Delete glossary category pages that become empty after term removal

**Batch 5 -- Kafka tutorials** (not SpecWeave-specific):
- `docs/guides/kafka-getting-started.md`
- `docs/guides/kafka-advanced-usage.md`
- `docs/guides/kafka-terraform.md`
- `docs/guides/kafka-troubleshooting.md`

**Verification**: Update sidebars.ts to remove references to deleted files, then `npx docusaurus build`.

### Phase 3: Ghost Plugin and Ghost Command Removal (AC-US2-02, AC-US2-03, AC-US4-01, AC-US4-02)

**What**: Audit every plugin and command reference against the actual registry/CLI, remove non-existent ones.

**Strategy**: Two-pass approach.

**Pass 1 -- Build the canonical lists**:
- Plugins: 13 total (8 SpecWeave core + 5 vskill). Source of truth: `specweave list-plugins` CLI output or plugin registry in source code.
- Skills: ~48 built-in. Source of truth: `specweave list-skills` CLI output.
- Commands: Source of truth: `specweave --help` CLI output.

**Pass 2 -- Grep and fix**:
```bash
# Find all plugin name references
grep -rn 'plugin' docs/ --include='*.md' | grep -i 'frontend:\|backend:\|payments:\|kafka:\|mobile:'
# Cross-reference against canonical list, remove/update non-matching
```

**Key files to rewrite**:
- `docs/overview/plugins-ecosystem.md` -- Rewrite to state 13 plugins, ~48 skills, 99,680+ community skills
- `docs/reference/skills.md` -- Update label from "All Skills (100+)" to "Built-in Skills (~48)"
- `docs/guides/agent-skills-extensibility-analysis.md` -- Update or remove "49 Agents" claim

**Statistics reconciliation** (AC-US5-01, AC-US5-02, AC-US5-03):
```bash
# Find all numeric claims about plugins/skills
grep -rn '\b[0-9]\+\s*plugin' docs/ --include='*.md'
grep -rn '\b[0-9]\+\s*skill' docs/ --include='*.md'
grep -rn '100+\|136\|19\|24 plugin' docs/ --include='*.md'
```
Replace every occurrence with the canonical values.

**Verification**: `npx docusaurus build` + manual spot-check of rewritten pages.

### Phase 4: Content Consolidation (AC-US3-01, AC-US3-02)

**What**: Merge duplicate/fragmented pages into single canonical pages.

**Merge strategy**: For each group, the page with the most complete content becomes canonical. Content from other pages is merged in (not rewritten from scratch). The non-canonical pages are deleted and added to the redirect map.

**Consolidation groups**:

| Group | Sources | Canonical Target |
|-------|---------|-----------------|
| Getting Started (5 pages) | `getting-started/index.md`, `quick-start.md`, `guides/getting-started/quickstart.md`, `guides/getting-started/installation.md`, `guides/getting-started/nvm-global-packages-fix.md` | `getting-started/index.md` |
| Compliance (3 pages) | `guides/compliance-standards.md`, `enterprise/compliance-standards.md`, `reference/compliance-standards.md` | `enterprise/compliance-standards.md` |
| Cost Tracking (3 pages) | `guides/cost-tracking.md`, `guides/cost-optimization.md`, `reference/cost-tracking.md` | `reference/cost-tracking.md` |
| Living Docs (3 pages) | `guides/core-concepts/living-documentation.md`, `guides/intelligent-living-docs-sync.md`, `guides/core-concepts/living-docs-sync-strategy.md` | `guides/core-concepts/living-documentation.md` |
| Features (2 pages) | `overview/features.md`, `features.md` | `overview/features.md` |
| Command Decision Tree (2 pages) | `commands/command-decision-tree.md`, `reference/command-decision-tree.md` | `commands/command-decision-tree.md` |
| Extensible Skills (4 pages) | `skills/extensible/extensible-skills.md`, `skills/extensible/extensible-skills-standard.md`, `skills/extensible/extensible-skills-guide.md`, `skills/extensible/skill-development-guidelines.md` | `skills/extensible/extensible-skills.md` (merge standard + guide into one) |
| Agent Teams (2 pages) | `guides/agent-teams-and-swarms.md`, `guides/agent-teams-setup.md` | `guides/agent-teams-and-swarms.md` |
| Sync/Status (4 pages) | `guides/status-sync-guide.md`, `guides/status-sync-migration.md`, `guides/sync-strategies.md`, `guides/sync-configuration.md` | `guides/sync-configuration.md` |
| External Tools (3 pages) | `guides/integrations/external-tools-overview.md`, `guides/external-tool-sync.md`, `integrations/issue-trackers.md` | `guides/integrations/external-tools-overview.md` |

**Additional pages to evaluate for removal** (not covered by merge groups):
- `docs/overview/ai-revolution-context.md` -- opinion piece, not reference docs
- `docs/overview/dogfooding.md` -- internal, not user-facing
- `docs/guides/life-automation.md` -- tangential to SpecWeave
- `docs/guides/ai-coding-benchmarks.md` -- tangential
- `docs/guides/specweave-vs-speckit.md` -- competitor comparison, keep if accurate
- `docs/guides/specweave-learning-journey.md` -- merge into academy/index
- `docs/guides/meta-capability.md` -- evaluate relevance
- `docs/guides/openclaw-agent-setup.md` -- third-party, evaluate
- `docs/guides/mobile/react-native-setup-guide.md` -- evaluate if plugin exists
- `docs/enterprise/case-study-migration.md` -- keep if real case study
- `docs/enterprise/knowledge-transfer-migration.md` -- merge into enterprise/index
- `docs/enterprise/monolith-to-microservices.md` -- tangential

**Verification**: After each merge group, update sidebars.ts and run `npx docusaurus build`.

### Phase 5: Sidebar Restructure and Page Template (AC-US6-01, AC-US6-02, AC-US6-03)

**Target sidebar structure** (9 top-level categories per spec, max 2 depth):

```
docsSidebar (unified, replaces docsSidebar + guidesSidebar + integrationsSidebar):
  Getting Started
    - Quick Start (getting-started/index)
    - First Increment (getting-started/first-increment)
  Core Concepts
    - What is an Increment? (guides/core-concepts/what-is-an-increment)
    - Living Documentation (guides/core-concepts/living-documentation)
    - Skills-First Architecture (guides/core-concepts/skills-first-architecture)
  Workflows
    - Complete Journey (workflows/overview)
    - Planning (workflows/planning)
    - Implementation (workflows/implementation)
    - Brownfield Projects (workflows/brownfield)
    - Autonomous Mode (guides/autonomous-execution)
  Skills & Plugins
    - Overview (skills/index)
    - Installing Skills (skills/installation)
    - Extensible Skills (skills/extensible/extensible-skills)
    - Verified Skills (skills/verified/verified-skills)
    - vskill CLI (skills/vskill-cli)
  Integrations
    - Overview (guides/integrations/external-tools-overview)
    - GitHub (academy/specweave-essentials/14-github-integration)
    - JIRA (academy/specweave-essentials/15-jira-integration)
    - Azure DevOps (academy/specweave-essentials/16-ado-integration)
  Agent Teams
    - Overview (guides/agent-teams-and-swarms)
  Enterprise
    - Overview (enterprise/index)
    - GitHub Migration (enterprise/github-migration)
    - JIRA Migration (enterprise/jira-migration)
    - Azure DevOps Migration (enterprise/azure-devops-migration)
    - Compliance (enterprise/compliance-standards)
  Academy
    - Learning Center (academy/index)
    - SpecWeave Essentials (autogenerated)
    - Fundamentals (autogenerated, collapsed)
  Reference
    - Commands (commands/overview)
    - Skills Reference (reference/skills)
    - Cost Tracking (reference/cost-tracking)
    - Glossary (glossary/index-by-category)
    - FAQ (faq)

Removed sidebars:
  - gettingStartedSidebar (merged into docsSidebar)
  - integrationsSidebar (merged into docsSidebar)
  - guidesSidebar (merged into docsSidebar)
  - learnSidebar (deleted with learn/)
  - commandsSidebar (merged into Reference section)
  - glossarySidebar (reduced to single link in Reference)
  - apiSidebar (evaluate: if api/index.md has real content, keep as autogenerated; otherwise remove)

Remaining sidebars (6):
  1. docsSidebar (unified main)
  2. skillsSidebar (dedicated Skills section -- enough depth to warrant separate)
  3. enterpriseSidebar (keep separate for enterprise nav)
  4. academySidebar (keep separate for Learn nav)
  5. referenceSidebar (keep separate for Reference nav)
  6. apiSidebar (conditional -- only if API docs have content)
```

**Navbar updates** (docusaurus.config.ts):
- "Docs" -> docsSidebar (unchanged)
- "Learn" -> academySidebar (unchanged)
- "Skills" -> skillsSidebar (unchanged)
- "Enterprise" -> enterpriseSidebar (unchanged)
- "Reference" -> referenceSidebar (unchanged)

**Footer updates** (docusaurus.config.ts):
- Fix "Skills Reference (100+)" label to "Skills Reference (~48)"
- Remove any links pointing to deleted pages

**Page template enforcement** (AC-US6-03):
- Not a runtime check, but a documented convention
- Every page must follow: Title (h1) > Subtitle (frontmatter description) > Intro paragraph > Sections (h2/h3) > Next Steps footer
- Create a template file at `docs/_page-template.md` (excluded from build by convention) or document in CONTRIBUTING.md

**Verification**: `npx docusaurus build` + manual click-through of navbar items.

### Phase 6: CSS and Design Fixes (AC-US7-01, AC-US7-02)

**Fix 1: Remove global `*` transition** (AC-US7-01)

Current (custom.css lines 12-16):
```css
* {
  transition-property: background-color, border-color, color;
  transition-duration: 0.2s;
  transition-timing-function: ease-in-out;
}
```

This causes layout shift on initial page load because every element animates its background/border/color from the browser default to the themed value.

**Replacement**: Scope transitions to interactive elements only.
```css
a, button, .navbar, .menu__link, .theme-doc-sidebar-item-link,
[data-theme='dark'] .navbar, .card, .button--primary {
  transition-property: background-color, border-color, color;
  transition-duration: 0.2s;
  transition-timing-function: ease-in-out;
}
```

**Fix 2: Footer color tokens** (AC-US7-02)

The footer uses Docusaurus's built-in `style: 'dark'` which applies hardcoded dark background colors. The fix is to override the footer CSS using the existing `--sw-*` design tokens from tokens.css.

Add to custom.css:
```css
.footer--dark {
  background-color: var(--sw-color-primary-900);
  color: var(--sw-color-primary-100);
}

.footer--dark .footer__link-item {
  color: var(--sw-color-primary-200);
}

.footer--dark .footer__link-item:hover {
  color: var(--sw-color-primary-50);
}

.footer--dark .footer__title {
  color: var(--sw-color-primary-50);
}

.footer--dark .footer__copyright {
  color: var(--sw-color-primary-300);
}
```

This ensures the footer renders correctly in both light and dark modes using theme tokens instead of hardcoded values.

**Verification**: `npx docusaurus build` + visual check in both light/dark modes.

## Redirect Map Strategy (AC-US9-01, AC-US9-02, AC-US9-03)

**Generation approach**: Build the redirect map programmatically from the deletion/merge decisions rather than manually listing URLs. This prevents missed redirects.

**Implementation**: Extend the existing `@docusaurus/plugin-client-redirects` config in `docusaurus.config.ts`.

**Redirect categories**:

1. **learn/ -> academy/fundamentals/** (AC-US9-03):
```typescript
{ from: '/docs/learn/foundations/enterprise-app-development', to: '/docs/academy/fundamentals/enterprise-app-development' },
{ from: '/docs/learn/foundations/software-engineering-roles', to: '/docs/academy/fundamentals/software-engineering-roles' },
{ from: '/docs/learn/foundations/claude-code-basics', to: '/docs/overview/claude-code-basics' },
{ from: '/docs/learn/backend/backend-fundamentals', to: '/docs/academy/fundamentals/backend-fundamentals' },
{ from: '/docs/learn/frontend/frontend-fundamentals', to: '/docs/academy/fundamentals/frontend-fundamentals' },
{ from: '/docs/learn/testing/testing-fundamentals', to: '/docs/academy/fundamentals/testing-fundamentals' },
{ from: '/docs/learn/infrastructure/iac-fundamentals', to: '/docs/academy/fundamentals/iac-fundamentals' },
{ from: '/docs/learn/ml-ai/ml-fundamentals', to: '/docs/academy/fundamentals/ml-fundamentals' },
// learn/foundations/terminal-empowerment and learn/testing/cli-integration-testing
// have no academy equivalent -- redirect to academy/index
{ from: '/docs/learn/foundations/terminal-empowerment', to: '/docs/academy' },
{ from: '/docs/learn/testing/cli-integration-testing', to: '/docs/academy' },
```

2. **Merged pages** (non-canonical -> canonical):
```typescript
{ from: '/docs/quick-start', to: '/docs/getting-started' },
{ from: '/docs/features', to: '/docs/overview/features' },
{ from: '/docs/guides/compliance-standards', to: '/docs/enterprise/compliance-standards' },
{ from: '/docs/guides/cost-tracking', to: '/docs/reference/cost-tracking' },
{ from: '/docs/guides/cost-optimization', to: '/docs/reference/cost-tracking' },
{ from: '/docs/reference/command-decision-tree', to: '/docs/commands/command-decision-tree' },
// ... all merge sources from Phase 4 consolidation groups
```

3. **Deleted pages with no direct equivalent** (redirect to parent):
```typescript
{ from: '/docs/guides/kafka-getting-started', to: '/docs/overview/introduction' },
{ from: '/docs/guides/kafka-advanced-usage', to: '/docs/overview/introduction' },
{ from: '/docs/guides/youtube-tutorial-script', to: '/docs/overview/introduction' },
// ... etc
```

4. **Glossary terms** -- generic terms redirect to the glossary index:
```typescript
{ from: '/docs/glossary/terms/api', to: '/docs/glossary/index-by-category' },
{ from: '/docs/glossary/terms/docker', to: '/docs/glossary/index-by-category' },
// ... all ~63 deleted generic terms
```

**Verification script** (run after deployment):
```bash
# Extract all redirect 'from' paths and curl each one
# Verify HTTP 200 after redirect (not 404)
```

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Cascading build failures | Phase gates: build must pass after each phase before proceeding |
| Missing redirects causing 404s | Generate redirect map from deletion list, not manually. Cross-check with git diff |
| Content loss during merges | Git provides full history; review diff of each merge before committing |
| Sidebar references to deleted files | Update sidebars.ts in the same commit as file deletions |
| Stale prefix replacement breaks code examples | Replacement is semantically correct (`/specweave:` -> `/sw:`); verify with build |
| Footer dark mode regression | Test both light/dark modes visually after CSS changes |

## Build Verification Checkpoints

After each phase, run:
```bash
cd repositories/anton-abyzov/specweave/docs-site
npx docusaurus build 2>&1 | tail -20
echo "Exit code: $?"
```

The build must exit 0. Warnings about broken links are acceptable during intermediate phases (config has `onBrokenLinks: 'warn'`) but the final build after Phase 6 should have zero link warnings for docs pages that still exist.

## Execution Order Summary

```
Phase 1: Prefix replacement (sed, ~5 min)
  |-- BUILD CHECK
Phase 2: File deletion (rm, sidebar updates, ~15 min)
  |-- BUILD CHECK
Phase 3: Ghost plugin/command removal (grep + manual edit, ~30 min)
  |-- BUILD CHECK
Phase 4: Content consolidation (merge + redirect map, ~60 min)
  |-- BUILD CHECK
Phase 5: Sidebar restructure + page template (sidebars.ts rewrite, ~30 min)
  |-- BUILD CHECK
Phase 6: CSS fixes (custom.css edits, ~10 min)
  |-- BUILD CHECK (final)
```

## Domain Skill Delegation

No domain skills needed. This is a documentation/content operation -- no frontend framework code, no backend services, no database changes. All work is:
- Shell commands (sed, grep, find, rm)
- Markdown file editing
- TypeScript config editing (sidebars.ts, docusaurus.config.ts)
- CSS editing (custom.css)

These are all handled directly without specialized domain skills.
