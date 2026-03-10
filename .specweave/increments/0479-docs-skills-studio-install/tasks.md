---
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003]
  US-003: [T-004]
  US-004: [T-005]
  US-005: [T-006, T-007]
---

# Tasks: Documentation Update — Skills, Skill Studio, Installation

## Task Notation

- `[ ]` pending | `[x]` completed
- `[P]` parallelizable with other marked tasks
- Model hints: haiku (simple edits), opus (long-form content creation)

---

## User Story: US-001 — Skill Installation Guide

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09, AC-US1-10
**Tasks**: 2 total, all completed

---

### T-001: Read vskill source and create installation.md

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09
**Status**: [x] completed

**Test Plan**:
- **Given** the vskill CLI source at `repositories/anton-abyzov/vskill/src/index.ts` is the source of truth
- **When** `docs/skills/installation.md` is created with all required sections
- **Then** the file has valid frontmatter, covers all 3 install sources (registry/GitHub/local), documents security scanning, multi-agent install, global vs project scope, plugin bundles, skill management commands, SpecWeave auto-loading, and a troubleshooting section

**Test Cases**:
1. **Manual content check**: `repositories/anton-abyzov/specweave/docs-site/docs/skills/installation.md`
   - TC-001: Frontmatter present with title, description, keywords, sidebar_position: 2
   - TC-002: "Install from Registry" section with `vskill install <name>` command
   - TC-003: "Install from GitHub" section with `--repo` flag
   - TC-004: "Install from Local Directory" section with `--plugin-dir` flag
   - TC-005: "Install Plugins" section covering `--plugin`, `--all` flags, references 13 plugins
   - TC-006: "Security Scanning" section covering 38 patterns, blocklist, optional LLM verify
   - TC-007: "Multi-Agent Install" section covering `--agent`, `--select`, 49 AI agents auto-detect
   - TC-008: "Global vs Project Scope" section covering `--global`, `--cwd` flags
   - TC-009: "SpecWeave Plugin Auto-Loading" section with link to `lazy-plugin-loading.md`
   - TC-010: "Skill Management" section covering list, update, remove, blocklist commands with flag tables
   - TC-011: "Troubleshooting" section present with at least 3 common issues

**Implementation**:
1. Read `repositories/anton-abyzov/vskill/src/index.ts` lines 21-149 to extract exact command flags, aliases, descriptions
2. Read `repositories/anton-abyzov/specweave/docs-site/docs/skills/fundamentals.md` to understand existing install mentions
3. Read `repositories/anton-abyzov/specweave/docs-site/docs/overview/plugins-ecosystem.md` for context on the 13 plugins
4. Create `repositories/anton-abyzov/specweave/docs-site/docs/skills/installation.md` with:
   - Frontmatter: title, description, keywords, sidebar_position: 2
   - Quick Start tip admonition with shortest install command
   - Prerequisites section (Node.js 20.12.0+, npx/bunx/pnpx/yarn dlx)
   - Install from Registry, GitHub, Local Directory sections
   - Install Plugins section
   - Security Scanning section
   - Multi-Agent Install section
   - Global vs Project Scope section
   - SpecWeave Plugin Auto-Loading section (brief, links to lazy-plugin-loading.md)
   - Skill Management section with flag tables for list, update, remove, blocklist
   - Troubleshooting section
   - Next Steps links to skill-studio.md and vskill-cli.md

---

### T-002: Verify Phase 1 build passes

**User Story**: US-001
**Satisfies ACs**: AC-US1-10
**Status**: [x] completed

**Test Plan**:
- **Given** `installation.md` exists in `docs/skills/`
- **When** `npm run build` is run in `repositories/anton-abyzov/specweave/docs-site/`
- **Then** the build exits 0 with no errors or broken link warnings for the new page

**Test Cases**:
1. **Build gate**: `cd repositories/anton-abyzov/specweave/docs-site && npm run build`
   - TC-001: Exit code is 0
   - TC-002: No "broken link" errors in build output referencing installation.md
   - TC-003: No MDX parse errors for installation.md

**Implementation**:
1. Run `cd repositories/anton-abyzov/specweave/docs-site && npm run build`
2. If build fails, fix frontmatter or MDX syntax errors in installation.md and rebuild

---

## User Story: US-002 — Skill Studio Documentation

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08, AC-US2-09
**Tasks**: 1 total, all completed

---

### T-003: [P] Read vskill Studio source and create skill-studio.md

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08, AC-US2-09
**Status**: [x] completed

**Test Plan**:
- **Given** the Skill Studio source components exist in the vskill repo
- **When** `docs/skills/skill-studio.md` is created with all required sections
- **Then** the file documents all 6 workspace panels, A/B benchmarking, skill improvement workflow, inline skill creation, keyboard shortcuts, and related CLI commands

**Test Cases**:
1. **Manual content check**: `repositories/anton-abyzov/specweave/docs-site/docs/skills/skill-studio.md`
   - TC-001: Frontmatter present with title, description, keywords, sidebar_position: 22
   - TC-002: Quick Start section with `npx vskill studio` command and port/root flags
   - TC-003: "Workspace Panels" section documents all 6 panels: Editor, Tests, Run, Activation, History, Dependencies
   - TC-004: Each panel description includes its group (Build/Evaluate/Insights) and purpose
   - TC-005: "A/B Benchmarking" section documents model comparison feature
   - TC-006: "Skill Improvement Workflow" section documents iterate-test-compare loop
   - TC-007: "Creating Skills Inline" section present
   - TC-008: "Keyboard Shortcuts" table present (Ctrl+1 through Ctrl+6)
   - TC-009: "Related CLI Commands" section lists vskill studio and vskill eval commands
2. **Build gate**: `cd repositories/anton-abyzov/specweave/docs-site && npm run build` — exits 0 after this file is created (can share build run with T-004 verification)

**Implementation**:
1. Read `repositories/anton-abyzov/vskill/src/index.ts` lines 152-173 for studio and eval command flags
2. Read vskill Studio component files to understand panels: `LeftRail.tsx`, `EditorPanel.tsx`, `TestsPanel.tsx`, `RunPanel.tsx`, `ActivationPanel.tsx`, `HistoryPanel.tsx`, `DepsPanel.tsx`
3. Read `App.tsx` for top-level layout understanding
4. Read `ModelCompareModal.tsx` and `BenchmarkPage.tsx` for A/B benchmarking details
5. Read `CreateSkillInline.tsx` / `CreateSkillPage.tsx` for inline creation details
6. Read `SkillImprovePanel.tsx` for improvement workflow details
7. Create `repositories/anton-abyzov/specweave/docs-site/docs/skills/skill-studio.md` with:
   - Frontmatter: title, description, keywords, sidebar_position: 22
   - Quick Start tip admonition
   - UI Overview section (two-panel layout)
   - The 6 Workspace Panels section with subsections per panel
   - A/B Benchmarking section
   - Creating Skills Inline section
   - Skill Improvement Workflow section
   - Keyboard Shortcuts reference table
   - Related CLI Commands section
   - Next Steps links to installation.md and vskill-cli.md

---

## User Story: US-003 — vskill CLI Reference

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 1 total, all completed

---

### T-004: [P] Read vskill index.ts and create vskill-cli.md

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** `repositories/anton-abyzov/vskill/src/index.ts` contains 13 Commander.js command definitions
- **When** `docs/skills/vskill-cli.md` is created with one entry per command
- **Then** every command has: description, usage syntax, flags/options table, and at least one example; commands are organized into 4 categories

**Test Cases**:
1. **Manual content check**: `repositories/anton-abyzov/specweave/docs-site/docs/skills/vskill-cli.md`
   - TC-001: Frontmatter present with title, description, keywords
   - TC-002: All 13 commands documented: install, init, scan, list, remove, find, update, submit, audit, info, blocklist, eval, studio
   - TC-003: Each command entry has description, usage block, flags table, and example
   - TC-004: Commands organized into categories: Install & Manage, Discover, Develop, Security, Publish
   - TC-005: Aliases documented where applicable (install→i, find→search)
   - TC-006: Flags match exact names from `index.ts` (no invented flags)
2. **Build gate**: `cd repositories/anton-abyzov/specweave/docs-site && npm run build` — exits 0 (shared with T-003 verification)

**Implementation**:
1. Read the full `repositories/anton-abyzov/vskill/src/index.ts` to extract all 13 commands with exact flags, aliases, descriptions, and argument patterns
2. Create `repositories/anton-abyzov/specweave/docs-site/docs/skills/vskill-cli.md` with:
   - Frontmatter: title, description, keywords (no sidebar_position — explicitly listed in sidebars.ts)
   - Brief intro paragraph
   - Category sections: Install & Manage, Discover, Develop, Security, Publish
   - Each command subsection: description, alias (if any), usage code block, options table, example code block
   - Cross-links to installation.md (install command) and skill-studio.md (studio command)

---

## User Story: US-004 — Sidebar and Navigation Updates

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: 1 total, all completed

---

### T-005: Update sidebars.ts and verify navigation links

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [x] completed

**Test Plan**:
- **Given** the 3 new docs pages exist in `docs/skills/`
- **When** `sidebars.ts` is updated with the 3 new sidebar entries
- **Then** all 3 pages appear in the skillsSidebar at the correct positions and the build passes with no 404 errors

**Test Cases**:
1. **File check**: `repositories/anton-abyzov/specweave/docs-site/sidebars.ts`
   - TC-001: `skills/installation` entry present, positioned early in skillsSidebar (after Overview)
   - TC-002: `skills/skill-studio` entry present, placed under Ecosystem category
   - TC-003: `skills/vskill-cli` entry present, placed under Reference category
2. **Build gate**: `cd repositories/anton-abyzov/specweave/docs-site && npm run build`
   - TC-004: Build exits 0 with all sidebar entries resolving to existing docs
   - TC-005: No "docs page [...] not found" errors in build output

**Implementation**:
1. Read `repositories/anton-abyzov/specweave/docs-site/sidebars.ts` in full to understand current structure
2. Add `skills/installation` after the Skills Overview entry (early position)
3. Add `skills/skill-studio` within the Ecosystem category items
4. Add `skills/vskill-cli` within the Reference category items
5. Read `repositories/anton-abyzov/specweave/docs-site/docusaurus.config.ts` — if navbar items reference skills pages, update accordingly; otherwise no change needed (AC-US4-04)
6. Run `cd repositories/anton-abyzov/specweave/docs-site && npm run build` to confirm all links resolve

---

## User Story: US-005 — Existing Page Cross-Reference Updates

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06
**Tasks**: 2 total, all completed

---

### T-006: Add cross-reference links to skills/index.md, getting-started/index.md, overview/plugins-ecosystem.md

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** installation.md, skill-studio.md, and vskill-cli.md exist and are in the sidebar
- **When** the 3 existing pages are updated with contextual cross-reference links
- **Then** each updated page has links to the relevant new pages in the correct sections without duplicating content

**Test Cases**:
1. **File checks**:
   - TC-001: `skills/index.md` "Explore Further" section has links to installation.md, skill-studio.md, and vskill-cli.md
   - TC-002: `getting-started/index.md` "Choose Your Path" section references installation guide where skill installation is mentioned
   - TC-003: `overview/plugins-ecosystem.md` Learning Resources section has links to installation.md and vskill-cli.md
2. **Link format**: Links use Docusaurus relative path format (e.g., `./installation` or `../skills/installation`)

**Implementation**:
1. Read `repositories/anton-abyzov/specweave/docs-site/docs/skills/index.md` — locate "Explore Further" section and add 3 links
2. Read `repositories/anton-abyzov/specweave/docs-site/docs/getting-started/index.md` — locate skill/plugin install mention and add link to installation guide
3. Read `repositories/anton-abyzov/specweave/docs-site/docs/overview/plugins-ecosystem.md` — locate Learning Resources section and add 2 links

---

### T-007: Add cross-reference links to fundamentals.md and skill-discovery-evaluation.md; final build verification

**User Story**: US-005
**Satisfies ACs**: AC-US5-04, AC-US5-05, AC-US5-06
**Status**: [x] completed

**Test Plan**:
- **Given** all new pages and prior cross-references are in place
- **When** the 2 remaining existing pages are updated and a final `npm run build` is run
- **Then** fundamentals.md and skill-discovery-evaluation.md have correct links, and the full build passes with 0 errors

**Test Cases**:
1. **File checks**:
   - TC-001: `skills/fundamentals.md` Next Steps section has links to installation.md and vskill-cli.md
   - TC-002: `skills/skill-discovery-evaluation.md` SpecWeave Approach section has inline links to installation.md and vskill-cli.md
2. **Final build gate**: `cd repositories/anton-abyzov/specweave/docs-site && npm run build`
   - TC-003: Exit code 0
   - TC-004: No broken internal link errors across any skills page
   - TC-005: No MDX syntax errors in any modified file

**Implementation**:
1. Read `repositories/anton-abyzov/specweave/docs-site/docs/skills/fundamentals.md` — locate Next Steps section and add links to installation.md and vskill-cli.md
2. Read `repositories/anton-abyzov/specweave/docs-site/docs/skills/skill-discovery-evaluation.md` — locate SpecWeave Approach section and add inline links to installation.md and vskill-cli.md
3. Run final `cd repositories/anton-abyzov/specweave/docs-site && npm run build`
4. If build fails, inspect error output, fix the specific file causing the issue, and rerun

---

## Execution Order

| Phase | Tasks | Can Parallelize |
|-------|-------|-----------------|
| Phase 1 — Installation page | T-001, T-002 | T-001 runs first; T-002 verifies |
| Phase 2 — Studio + CLI pages | T-003, T-004 | Yes — run in parallel |
| Phase 3 — Navigation + cross-refs | T-005, T-006, T-007 | T-005 first; T-006 and T-007 after T-005 |

Build verification: T-002 (Phase 1), shared build after T-003+T-004 (Phase 2), T-007 final build (Phase 3).
