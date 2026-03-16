# Architecture Plan: Documentation Update — Skills, Skill Studio, Installation

## Overview

This increment adds 3 new documentation pages to the SpecWeave docs site (Docusaurus 3.9) and updates 5 existing pages with cross-references. No code changes, no new ADRs — this is purely a content and information architecture effort.

## Decision Record

**No ADR required.** This increment introduces no new code architecture, APIs, data models, or runtime behavior. The decisions below are content-structural and scoped to the docs site.

---

## D1: Content Structure for New Pages

### Decision

Each of the 3 new pages follows a consistent internal structure pattern:

```
---
title: "..."
description: "..."
keywords: [...]
sidebar_position: N
---

# Page Title

Introductory paragraph (2-3 sentences, what this page covers and who it's for)

:::tip Quick Start (where applicable)
Shortest-path command to get started
:::

---

## Sections (topic-specific)

---

## Troubleshooting / FAQ (where applicable)

---

## Next Steps (links to related pages)
```

### Rationale

Consistent structure reduces cognitive load for readers navigating between pages. The "tip Quick Start" pattern is already used in `fundamentals.md`, `skills/index.md`, and `getting-started/index.md`, making it a familiar convention. The "Next Steps" footer pattern is established in `skills/index.md` (the "Explore Further" section).

---

## D2: Page-by-Page Content Architecture

### installation.md

**Purpose**: Single source of truth for all skill installation methods. Replaces scattered fragments across `plugins-ecosystem.md`, `skill-discovery-evaluation.md`, and `fundamentals.md`.

**Internal sections**:

| Section | Content Source |
|---------|---------------|
| Prerequisites | New content (Node.js 20.12.0+, npx/bunx/pnpx/yarn dlx) |
| Install from Registry | `vskill install <name>` — source: `index.ts` L22-41 |
| Install from GitHub | `vskill install --repo <owner/repo>` — source: `index.ts` L28 |
| Install from Local Directory | `vskill install --plugin-dir <path>` — source: `index.ts` L27 |
| Install Plugins | `--plugin`, `--all`, `--repo` flags — source: `index.ts` L26-29 |
| Security Scanning | Auto-scan on install (38+ patterns + blocklist); link to Verified Skills page for details |
| Multi-Agent Install | `--agent`, `--select`, agent auto-detection (49 agents); source: `index.ts` L32, L35 |
| Scope: Global vs Project | `--global`, `--cwd` flags; source: `index.ts` L30, L33 |
| SpecWeave Plugin Auto-Loading | Brief explanation + link to `lazy-plugin-loading.md` for details |
| Skill Management | `list`, `update`, `remove`, `blocklist` commands (tables with flags) |
| Troubleshooting | Common install issues and fixes |

**Source of truth for CLI flags**: `repositories/anton-abyzov/vskill/src/index.ts` lines 21-41 (install command), 60-67 (list), 69-78 (remove), 80-89 (find), 91-99 (update), 143-149 (blocklist).

### skill-studio.md

**Purpose**: Complete guide to the Skill Studio local development IDE.

**Internal sections**:

| Section | Content Source |
|---------|---------------|
| Quick Start | `npx vskill studio` / `vskill studio --port <N> --root <path>` — source: `index.ts` L163-173 |
| UI Overview | High-level description of the two-panel layout (LeftPanel + RightPanel) — source: `App.tsx` |
| The 6 Workspace Panels | Source: `LeftRail.tsx` lines 17-39 (PANEL_GROUPS constant) |
| -- Editor (Build group) | Edit SKILL.md content inline — source: `EditorPanel.tsx` |
| -- Tests (Build group) | View and manage eval test cases — source: `TestsPanel.tsx` |
| -- Run (Evaluate group) | Execute evals and see results — source: `RunPanel.tsx` |
| -- Activation (Evaluate group) | Test skill activation triggers — source: `ActivationPanel.tsx` |
| -- History (Insights group) | View eval run history and regressions — source: `HistoryPanel.tsx` |
| -- Dependencies (Insights group) | Manage MCP/tool dependencies — source: `DepsPanel.tsx` |
| A/B Benchmarking | Model comparison via `ModelCompareModal.tsx`; benchmark page at `BenchmarkPage.tsx` |
| Creating Skills Inline | `CreateSkillInline.tsx` and `CreateSkillPage.tsx` |
| Skill Improvement Workflow | `SkillImprovePanel.tsx` — iterate, test, compare loop |
| Keyboard Shortcuts | Ctrl+1 through Ctrl+6 for panel switching (from LeftRail.tsx L22-37) |
| Related CLI Commands | `vskill studio`, `vskill eval init/run/coverage` — source: `index.ts` L152-160 |

### vskill-cli.md

**Purpose**: Complete CLI reference for all vskill commands.

**Internal sections**:

Each command gets a consistent entry format:

```markdown
### `vskill <command>`

**Description**: ...
**Alias**: ... (if any)

**Usage**:
\`\`\`bash
vskill <command> [args] [options]
\`\`\`

**Options**:

| Flag | Description |
|------|-------------|
| ... | ... |

**Example**:
\`\`\`bash
...
\`\`\`
```

**Command organization by category** (following the spec AC-US3-04):

| Category | Commands |
|----------|----------|
| **Install & Manage** | `install`, `remove`, `update`, `list` |
| **Discover** | `find`, `info` |
| **Develop** | `studio`, `eval`, `init` |
| **Security** | `scan`, `audit`, `blocklist` |
| **Publish** | `submit` |

**Source of truth**: `repositories/anton-abyzov/vskill/src/index.ts` — the complete Commander.js program definition with all commands, their flags, aliases, and descriptions.

The 13 commands (verified from source):
1. `install` (alias: `i`) — L22-41
2. `init` — L43-49
3. `scan` — L51-57
4. `list` — L59-67
5. `remove` — L69-78
6. `find` (alias: `search`) — L80-89
7. `update` — L91-99
8. `submit` — L101-108
9. `audit` — L110-133
10. `info` — L135-141
11. `blocklist` — L143-149
12. `eval` — L151-160
13. `studio` — L162-173

Note: `studio` is a 13th command (separate from `eval serve`). The spec says 12 commands but the source has 13. The CLI reference page will document all 13.

---

## D3: Sidebar Organization

### Decision

Add new pages to the existing `skillsSidebar` in `sidebars.ts`. Placement:

```
skillsSidebar:
  - Skills Overview (existing)
  - Installation Guide (NEW)          <-- early, after overview
  - Why Skills Matter (existing)
  - Skills, Plugins & Marketplaces (existing)
  - Extensible Skills Standard (existing category)
  - Verified Skills Standard (existing category)
  - Ecosystem (existing category)
    - ... existing items ...
    - Skill Studio (NEW)              <-- ecosystem tools
  - Reference (existing category)
    - All Skills (100+) (existing)
    - vskill CLI Reference (NEW)      <-- reference material
    - verifiedskill.com (existing)
```

### Rationale

- **Installation** goes early (position 2) because it answers the first question a new user has: "How do I install skills?" Natural follow-up to the Overview page.
- **Skill Studio** goes under Ecosystem because it is a development tool in the broader skills ecosystem, alongside Discovery & Evaluation and Agent Compatibility.
- **vskill CLI Reference** goes under the existing Reference category, alongside the All Skills catalog and verifiedskill.com link.

### sidebar_position Values

| Page | sidebar_position |
|------|-----------------|
| `skills/installation.md` | 2 |
| `skills/skill-studio.md` | 22 |
| `skills/vskill-cli.md` | Not needed (explicitly listed in sidebars.ts) |

---

## D4: Content Deduplication Strategy

### Decision

Apply **consolidate-and-cross-reference** pattern: authoritative install content lives in `installation.md`, existing pages keep their contextual references but link to the guide for full details.

### Pages with Install Content Analysis

| Existing Page | Current Content | Action |
|---------------|----------------|--------|
| `overview/plugins-ecosystem.md` | L18-25: "Quick Start" showing `specweave init` installs all plugins | Keep as-is (about SpecWeave plugins, not vskill skills). Add link to installation guide in Learning Resources. |
| `skills/skill-discovery-evaluation.md` | L302-312: "SpecWeave Approach" with `vskill find` and `vskill scan` examples | Keep examples (in context of evaluation). Add inline link to CLI reference. |
| `skills/fundamentals.md` | L291-304: "User Flow" about Claude Code native plugin system | Keep as-is (about Claude Code plugins, not vskill). Add link to installation guide in Next Steps. |
| `getting-started/index.md` | L49-52: "Install SpecWeave" (npm install -g specweave) | Keep as-is (about SpecWeave CLI). Add link to skill installation in Choose Your Path. |
| `guides/lazy-plugin-loading.md` | Auto-loading architecture description | Keep as-is. Link FROM installation.md TO this page. |

### Key Insight

The existing "install" content is mostly about SpecWeave (the framework) or Claude Code plugins, not about vskill (the skill package manager). The primary consolidation is ensuring `installation.md` is THE authoritative page for "how to install skills with vskill" and that other pages link to it for vskill details.

---

## D5: Cross-Reference Link Map

### Links TO new pages (from existing pages)

| From Page | Link Target | Anchor Context |
|-----------|-------------|----------------|
| `skills/index.md` Explore Further | `installation.md` | "Installation Guide" |
| `skills/index.md` Explore Further | `skill-studio.md` | "Skill Studio" |
| `skills/index.md` Explore Further | `vskill-cli.md` | "vskill CLI Reference" |
| `getting-started/index.md` Choose Your Path | `installation.md` | New table row |
| `overview/plugins-ecosystem.md` Learning Resources | `installation.md` | New list item |
| `overview/plugins-ecosystem.md` Learning Resources | `vskill-cli.md` | New list item |
| `skills/fundamentals.md` Next Steps | `installation.md` | New list item |
| `skills/fundamentals.md` Next Steps | `vskill-cli.md` | New list item |
| `skills/skill-discovery-evaluation.md` SpecWeave Approach | `vskill-cli.md` | Inline link |
| `skills/skill-discovery-evaluation.md` SpecWeave Approach | `installation.md` | Inline link |

### Links BETWEEN new pages

| From | To | Context |
|------|----|---------|
| `installation.md` | `skill-studio.md` | "For skill development, see Skill Studio" |
| `installation.md` | `vskill-cli.md` | "For complete CLI reference, see vskill CLI Reference" |
| `skill-studio.md` | `installation.md` | "To install skills, see Installation Guide" |
| `skill-studio.md` | `vskill-cli.md` | "For all CLI commands, see vskill CLI Reference" |
| `vskill-cli.md` | `installation.md` | install command links to guide |
| `vskill-cli.md` | `skill-studio.md` | studio command links to Studio docs |

---

## D6: File Organization

### New Files

```
repositories/anton-abyzov/specweave/docs-site/docs/skills/
├── index.md                        (existing)
├── installation.md                 (NEW)
├── skill-studio.md                 (NEW)
├── vskill-cli.md                   (NEW)
├── why-skills-matter.md            (existing)
├── fundamentals.md                 (existing)
├── skill-discovery-evaluation.md   (existing)
├── skill-contradiction-resolution.md (existing)
├── extensible/                     (existing)
└── verified/                       (existing)
```

### Modified Files

```
repositories/anton-abyzov/specweave/docs-site/
├── sidebars.ts                     (MODIFIED — add 3 entries)
├── docs/skills/index.md            (MODIFIED — add 3 links)
├── docs/getting-started/index.md   (MODIFIED — add 1 table row)
├── docs/overview/plugins-ecosystem.md (MODIFIED — add 2 links)
├── docs/skills/fundamentals.md     (MODIFIED — add 2 links)
└── docs/skills/skill-discovery-evaluation.md (MODIFIED — add 2 inline links)
```

---

## D7: Content Verification Strategy

### Source-of-truth validation

Every CLI command, flag, and description in the docs must match the Commander.js definitions in `repositories/anton-abyzov/vskill/src/index.ts`. During implementation:

1. Read each command's `.command()`, `.description()`, `.option()`, and `.alias()` calls from `index.ts`
2. Transcribe exact flag names, descriptions, and default values
3. Do not invent flags or behaviors not present in source

### Docusaurus build validation

After all files are written, run `npm run build` in the docs-site directory to verify:
- No broken internal links
- Valid MDX syntax
- Correct frontmatter
- Sidebar entries resolve to existing docs

---

## Estimated Scope

| Item | Estimated Lines |
|------|----------------|
| `installation.md` | ~300 |
| `skill-studio.md` | ~250 |
| `vskill-cli.md` | ~400 (13 commands with flags tables) |
| `sidebars.ts` changes | ~15 |
| Cross-reference edits (5 files) | ~20 total |
| **Total** | ~985 lines |

---

## No Domain Skill Delegation Needed

This is a documentation-only increment. No frontend, backend, or infrastructure domain skills are applicable. Implementation proceeds directly with content creation.
