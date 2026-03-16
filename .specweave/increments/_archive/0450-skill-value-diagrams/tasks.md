---
increment: 0450-skill-value-diagrams
title: "Skill Value Diagrams & Content Assets"
by_user_story:
  US-SW-001: [T-001, T-002]
  US-SW-002: [T-003, T-004]
  US-SW-003: [T-005, T-006]
  US-SW-004: [T-007, T-008]
  US-SW-005: [T-009, T-010]
  US-SW-006: [T-011]
total_tasks: 11
completed: 11
---

# Tasks: Skill Value Diagrams & Content Assets

## User Story: US-SW-001 - "What is a Skill?" Diagram

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 2 completed

### T-001: Create directory structure and Excalidraw source for "What is a Skill?"

**User Story**: US-SW-001
**Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `docs-site/static/img/skills/diagrams/` directory does not yet exist
- **When** the directory is created and `what-is-a-skill.excalidraw` is written
- **Then** the file exists at the correct path, is valid JSON with Excalidraw structure (`elements`, `appState`, `files` keys), uses `#FF6B6B` on the "without" side and `#51CF66` on the "with" side, and all text elements use Virgil font (fontFamily: 1) at >= 16px

**Test Cases**:
1. **File existence**: `test -f repositories/anton-abyzov/specweave/docs-site/static/img/skills/diagrams/what-is-a-skill.excalidraw`
2. **JSON validity**: `python3 -m json.tool <path>` exits without error
3. **Color check**: File contains `#FF6B6B` (red, without-side) and `#51CF66` (green, with-side)
4. **Font check**: File contains `"fontFamily": 1` on text elements (Virgil)
5. **Layout check**: File contains a vertical divider element separating left and right halves

**Implementation**:
1. Create directory: `repositories/anton-abyzov/specweave/docs-site/static/img/skills/diagrams/`
2. Author `what-is-a-skill.excalidraw` as valid Excalidraw JSON following the design system:
   - Canvas ~1200x600px
   - Left (red `#FF6B6B`): Prompt box → "Raw LLM" box → "Generic Output" label
   - Right (green `#51CF66`): Same prompt → "LLM + Skill" box → "Production-Grade Output" label
   - Vertical dashed gray (`#868E96`) divider at center
   - Annotation arrow: "Domain knowledge injected here" pointing to skill component
   - Section headers: "Without Skills" (red) and "With Skills" (green)
   - All text >= 16px, Virgil font (fontFamily: 1)
3. Verify JSON is parseable

---

### T-002: Export SVG for "What is a Skill?" diagram

**User Story**: US-SW-001
**Satisfies ACs**: AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** the `what-is-a-skill.excalidraw` source file exists
- **When** the SVG is exported and saved to `docs-site/static/img/skills/`
- **Then** the SVG file exists at the correct path and is valid SVG (starts with `<svg`)

**Test Cases**:
1. **File existence**: `test -f repositories/anton-abyzov/specweave/docs-site/static/img/skills/what-is-a-skill.svg`
2. **SVG validity**: File content starts with `<svg` tag
3. **No broken refs**: File does not contain `undefined` or `null` in dimension attributes

**Implementation**:
1. Generate SVG from the Excalidraw JSON (white background, 1x scale, no embedded scene data)
2. Save to `repositories/anton-abyzov/specweave/docs-site/static/img/skills/what-is-a-skill.svg`
3. Verify SVG opens in a browser without rendering errors

---

## User Story: US-SW-002 - "How Skills Work" Diagram

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, 2 completed

### T-003: Create Excalidraw source for "How Skills Work"

**User Story**: US-SW-002
**Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** the diagrams directory exists (created in T-001)
- **When** `how-skills-work.excalidraw` is written
- **Then** the file is valid Excalidraw JSON, shows a red LLM-only path with "?" quality markers and a green skill-augmented LLM path with checkmark quality markers, and uses consistent style with T-001 (same colors, Virgil font, 1200x600px canvas)

**Test Cases**:
1. **File existence**: `test -f repositories/anton-abyzov/specweave/docs-site/static/img/skills/diagrams/how-skills-work.excalidraw`
2. **JSON validity**: Parseable without error
3. **Color consistency**: Contains `#FF6B6B` and `#51CF66`
4. **Knowledge panel labels**: Contains text "Patterns", "Rules", and "Examples" (skill knowledge panel per design system)

**Implementation**:
1. Author `how-skills-work.excalidraw` following design system:
   - Left (red): Prompt → plain LLM box → Output with "?" quality markers
   - Right (green): Prompt → LLM box augmented with "Skill Knowledge" side-panel (labels: "Patterns", "Rules", "Examples") → Output with checkmark markers
   - Same 1200x600px canvas, Virgil font, vertical gray divider
2. Verify JSON is parseable

---

### T-004: Export SVG for "How Skills Work" diagram

**User Story**: US-SW-002
**Satisfies ACs**: AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** `how-skills-work.excalidraw` exists
- **When** SVG is exported to `static/img/skills/`
- **Then** file exists at correct path and is valid SVG

**Test Cases**:
1. **File existence**: `test -f repositories/anton-abyzov/specweave/docs-site/static/img/skills/how-skills-work.svg`
2. **SVG validity**: File starts with `<svg` tag

**Implementation**:
1. Generate SVG from `how-skills-work.excalidraw` (white background, 1x scale)
2. Save to `repositories/anton-abyzov/specweave/docs-site/static/img/skills/how-skills-work.svg`

---

## User Story: US-SW-003 - "Creating Skills" Diagram

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 2 completed

### T-005: Create Excalidraw source for "Creating Skills"

**User Story**: US-SW-003
**Satisfies ACs**: AC-US3-01, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** the diagrams directory exists
- **When** `creating-skills.excalidraw` is written
- **Then** the file is valid Excalidraw JSON showing scattered text bubbles on the red side and a structured SKILL.md anatomy on the green side, with labeled blocks for frontmatter, instructions body, and supporting files

**Test Cases**:
1. **File existence**: `test -f repositories/anton-abyzov/specweave/docs-site/static/img/skills/diagrams/creating-skills.excalidraw`
2. **JSON validity**: Parseable without error
3. **Required labels**: File contains text labels "Frontmatter", "Instructions Body", and "Supporting Files"
4. **Annotation present**: Contains connecting annotation text (e.g., "Formalize into SKILL.md")

**Implementation**:
1. Author `creating-skills.excalidraw` following design system:
   - Left (red): 3-4 scattered overlapping text bubbles: "use TypeScript", "handle errors", "add tests", "be consistent" -- ad-hoc, disorganized
   - Right (green): Structured SKILL.md anatomy with distinct labeled blocks: "Frontmatter", "Instructions Body", "Supporting Files"
   - Arrow from left side to right side with label "Formalize into SKILL.md"
   - Same canvas size, colors, Virgil font
2. Verify JSON is parseable

---

### T-006: Export SVG for "Creating Skills" diagram

**User Story**: US-SW-003
**Satisfies ACs**: AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** `creating-skills.excalidraw` exists
- **When** SVG is exported
- **Then** file exists at correct path and is valid SVG

**Test Cases**:
1. **File existence**: `test -f repositories/anton-abyzov/specweave/docs-site/static/img/skills/creating-skills.svg`
2. **SVG validity**: File starts with `<svg` tag

**Implementation**:
1. Generate SVG from `creating-skills.excalidraw` (white background, 1x scale)
2. Save to `repositories/anton-abyzov/specweave/docs-site/static/img/skills/creating-skills.svg`

---

## User Story: US-SW-004 - "Skill Eval/Testing" Diagram

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 2 total, 2 completed

### T-007: Create Excalidraw source for "Skill Eval/Testing"

**User Story**: US-SW-004
**Satisfies ACs**: AC-US4-01, AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** the diagrams directory exists
- **When** `skill-eval-testing.excalidraw` is written
- **Then** the file is valid Excalidraw JSON showing a linear dead-end flow on the red side and a closed feedback cycle on the green side, using only generic eval concepts with no specific tool names

**Test Cases**:
1. **File existence**: `test -f repositories/anton-abyzov/specweave/docs-site/static/img/skills/diagrams/skill-eval-testing.excalidraw`
2. **JSON validity**: Parseable without error
3. **Tool-agnostic**: File element labels do NOT contain specific tool names (no "SpecWeave", "pytest", "Jest", "vitest" in text elements)
4. **Cycle present**: File contains arrow elements forming a cycle with labels "Run Eval", "Measure Quality", and "Improve"

**Implementation**:
1. Author `skill-eval-testing.excalidraw` following design system:
   - Left (red): Linear "Write Skill" → "Deploy" → "Hope it works" dead-end (no return arrow)
   - Right (green): Cycle: "Write Skill" → "Run Eval" → "Measure Quality" → "Improve" → back to "Run Eval", with an abstract quality metrics badge
   - Generic labels only -- no specific tool names
   - Same canvas size, colors, Virgil font
2. Verify JSON is parseable

---

### T-008: Export SVG for "Skill Eval/Testing" diagram

**User Story**: US-SW-004
**Satisfies ACs**: AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** `skill-eval-testing.excalidraw` exists
- **When** SVG is exported
- **Then** file exists at correct path and is valid SVG

**Test Cases**:
1. **File existence**: `test -f repositories/anton-abyzov/specweave/docs-site/static/img/skills/skill-eval-testing.svg`
2. **SVG validity**: File starts with `<svg` tag

**Implementation**:
1. Generate SVG from `skill-eval-testing.excalidraw` (white background, 1x scale)
2. Save to `repositories/anton-abyzov/specweave/docs-site/static/img/skills/skill-eval-testing.svg`

---

## User Story: US-SW-005 - "Why Skills Matter" Documentation Page

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Tasks**: 2 total, 2 completed

### T-009: Create "Why Skills Matter" doc page embedding all 4 diagrams

**User Story**: US-SW-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** all 4 SVG files exist in `static/img/skills/`
- **When** `why-skills-matter.md` is created at `docs-site/docs/skills/`
- **Then** the file has valid Docusaurus frontmatter with `sidebar_position: 2`, embeds all 4 SVGs using absolute static paths with descriptive alt text, includes 2-4 sentences of explanatory context per diagram, links forward to `fundamentals.md`, and includes a "coming soon" video tip admonition

**Test Cases**:
1. **File existence**: `test -f repositories/anton-abyzov/specweave/docs-site/docs/skills/why-skills-matter.md`
2. **Frontmatter check**: File contains `sidebar_position: 2` in YAML frontmatter block
3. **All 4 SVGs embedded**: File contains all 4 image paths:
   - `/img/skills/what-is-a-skill.svg`
   - `/img/skills/how-skills-work.svg`
   - `/img/skills/creating-skills.svg`
   - `/img/skills/skill-eval-testing.svg`
4. **Alt text check**: Each `![]()` image tag has a non-empty, descriptive alt text string
5. **Forward link**: File contains a link to `fundamentals.md` or `/docs/skills/fundamentals`
6. **Video tip**: File contains a `:::tip` admonition with "coming soon" or "video" in the text

**Implementation**:
1. Create `repositories/anton-abyzov/specweave/docs-site/docs/skills/why-skills-matter.md` with:
   ```yaml
   ---
   title: "Why Skills Matter"
   description: "See the dramatic difference skills make -- 4 before/after comparisons showing why generic AI output is not enough"
   sidebar_position: 2
   keywords: [skills, before-after, value-proposition, why-skills-matter]
   ---
   ```
2. Add video tip admonition: `:::tip Video version` with "coming soon" placeholder
3. Add 4 sections, each with one SVG embed (absolute path from static root) + 2-4 sentences of context:
   - "What is a Skill?" -- `what-is-a-skill.svg`
   - "How Skills Work" -- `how-skills-work.svg`
   - "Creating Skills" -- `creating-skills.svg`
   - "Testing & Evaluating Skills" -- `skill-eval-testing.svg`
4. Add forward link CTA: "Ready to dive deeper? Learn [how skills, plugins, and marketplaces work together](/docs/skills/fundamentals)."

---

### T-010: Update sidebars.ts to insert "Why Skills Matter" into skillsSidebar

**User Story**: US-SW-005
**Satisfies ACs**: AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** the current `sidebars.ts` has `skills/index` followed immediately by `skills/fundamentals` in `skillsSidebar`
- **When** `skills/why-skills-matter` entry is inserted between them
- **Then** `sidebars.ts` contains the new entry with `id: 'skills/why-skills-matter'` and `label: 'Why Skills Matter'`, positioned between `skills/index` and `skills/fundamentals`, and the file is syntactically valid TypeScript

**Test Cases**:
1. **Entry present**: `grep -c "skills/why-skills-matter" sidebars.ts` returns >= 1
2. **Correct order**: In the file, the string `skills/index` appears before `skills/why-skills-matter`, which appears before `skills/fundamentals`
3. **Correct label**: File contains `label: 'Why Skills Matter'`

**Implementation**:
1. Edit `repositories/anton-abyzov/specweave/docs-site/sidebars.ts`
2. In the `skillsSidebar` array, insert after the `skills/index` entry:
   ```typescript
   { type: 'doc', id: 'skills/why-skills-matter', label: 'Why Skills Matter' },
   ```
3. Verify the array order is: `skills/index` → `skills/why-skills-matter` → `skills/fundamentals` → rest

---

## User Story: US-SW-006 - YouTube Script Outline

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05
**Tasks**: 1 total, 1 completed

### T-011: Write YouTube script outline for "Why Skills Matter"

**User Story**: US-SW-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05
**Status**: [x] completed

**Test Plan**:
- **Given** the video template at `.specweave/docs/public/academy/videos/_TEMPLATE.md` and existing videos 001-003
- **When** `004-why-skills-matter.md` is created at `.specweave/docs/public/academy/videos/`
- **Then** the file follows the template structure, targets developers unfamiliar with skills (minimal prerequisites), references all 4 diagrams as visual aids, has timed sections totaling ~8-10 minutes, and includes a Related Videos section linking 001, 002, and 003

**Test Cases**:
1. **File existence**: `test -f .specweave/docs/public/academy/videos/004-why-skills-matter.md`
2. **Template sections present**: File contains headings `## Video`, `## Summary`, `## What You'll Learn`, `## Step-by-Step`, `## Related Videos`
3. **All 4 diagrams referenced**: File contains slugs or filenames for all 4 diagrams: `what-is-a-skill`, `how-skills-work`, `creating-skills`, `skill-eval-testing`
4. **Timed sections**: File contains timestamps such as `(0:00)`, `(1:00)`, `(3:00)`, `(5:00)`, `(6:30)`, `(8:00)`
5. **Related videos**: File contains references to `001`, `002`, and `003`
6. **Beginner audience**: Intro section does not assume prior Claude Code knowledge; contains framing like "generic AI output" or "you've been getting generic results"

**Implementation**:
1. Create `.specweave/docs/public/academy/videos/004-why-skills-matter.md` following `_TEMPLATE.md`:
   - **Title**: Video 004: Why Skills Matter
   - **Duration**: ~8-10 minutes
   - **Summary**: For developers getting generic AI output who want to understand how skills produce production-grade results
   - **What You'll Learn**: 4 objectives -- one per diagram concept
   - **Step-by-Step** with timestamps:
     - (0:00) Intro -- "You've been getting generic AI output. Here's how to fix that." (~1 min)
     - (1:00) What is a Skill? -- diagram visual + narrative (~2 min)
     - (3:00) How Skills Work -- diagram visual + mechanism explanation (~2 min)
     - (5:00) Creating Skills -- diagram visual + formalization narrative (~1.5 min)
     - (6:30) Testing & Evaluating Skills -- diagram visual + feedback loop (~1.5 min)
     - (8:00) Call to action -- link to docs, related videos (~1 min)
   - **Related Videos**: `001-specweave-complete-masterclass.md`, `002-toxicskills-security.md`, `003-clawhub-postmortem.md`
