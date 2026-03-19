# Implementation Plan: Update introduction page with recent features

## Overview

This is a **documentation-only** change to a single file: `repositories/anton-abyzov/specweave/docs-site/docs/overview/introduction.md`. No code, no APIs, no data models. The plan focuses on content architecture: what sections to add, remove, and restructure to bring the introduction page up to parity with README.md's best content.

**Target file**: `docs-site/docs/overview/introduction.md` (currently ~196 lines, target ~300-350 lines)
**Format**: Docusaurus MDX with `CommandTabs` component (already imported)
**No ADR required** — documentation content change only.

## Content Architecture

### Current State Analysis

The introduction page is missing several key features that README.md covers well:

| Missing from Introduction | Present in README.md |
|---------------------------|---------------------|
| "No Commands to Memorize" natural language table | Lines 38-56 |
| Solo / Team / Brownfield workflow narratives | Lines 108-131 |
| Agent Swarms ASCII art + `/sw:team-lead` | Lines 201-216 |
| Integrations table (GitHub/JIRA/ADO) | Lines 345-358 |
| Complexity diagram ("hardest problem you can solve") | Lines 161-180 |
| Skills explanation + learning example | Lines 136-149 |
| "What You Control" config section with comments | Lines 59-81 |

The introduction also has content that overlaps with Getting Started (`docs/getting-started/index.md`):
- "Getting Started" section (lines 154-187) duplicates Quick Start steps
- "How It Works" CommandTabs (lines 59-95) repeat the same examples

### Target Section Structure

The new page will follow this information hierarchy:

```
1. Title + Hero (keep, minor edit)                        ~10 lines
2. The Problem (keep, minor edit)                         ~15 lines
3. The Solution: Configure AI, Don't Prompt It (keep)     ~25 lines
4. No Commands to Memorize (NEW — from README)            ~20 lines
5. The Workflow (REPLACE "How It Works")                  ~45 lines
   - Main workflow narrative (from README)
   - Solo developer variant
   - Agent team (parallel) variant
   - Brownfield project variant
6. Agent Swarms (NEW — from README)                       ~20 lines
7. Who Should Use SpecWeave? (keep, restructure)          ~20 lines
8. Core Features (keep)                                   ~15 lines
9. What You Get vs. Current State (keep)                  ~12 lines
10. Integrations (NEW — from README)                      ~15 lines
11. Built With SpecWeave (keep)                           ~8 lines
12. Getting Started (STREAMLINE — reduce to link)         ~10 lines
13. Next Steps (keep)                                     ~8 lines
                                                    TOTAL ~320 lines
```

### Section-by-Section Design

#### Section 1: Title + Hero (~10 lines)
**Action**: Keep existing content. No changes needed.

#### Section 2: The Problem (~15 lines)
**Action**: Keep existing content. Accurate and well-written.

#### Section 3: The Solution (~25 lines)
**Action**: Keep existing content including config JSON and flow diagram. Enhance the config JSON block to include inline comments (matching README's better-annotated version at lines 63-79).

#### Section 4: No Commands to Memorize (NEW, ~20 lines)
**Source**: README.md lines 38-56
**Action**: Add new section after "The Solution" with:
- Introductory paragraph explaining natural language routing
- The "You say / Your AI runs" table (8 rows)
- Brief closing line about direct invocation for fine-grained control

**Rationale**: This is the most distinctive UX feature and should appear early. It immediately differentiates SpecWeave from tools that require memorizing CLI commands.

#### Section 5: The Workflow (REPLACE "How It Works", ~45 lines)
**Source**: README.md lines 85-131
**Action**: Replace the current "How It Works" section (3 CommandTabs steps) with richer workflow narratives:
- Main workflow: conversational format showing AI asking clarifying questions, creating spec/plan/tasks, autonomous execution, review, close
- Solo developer: condensed 3-line version
- Agent team (parallel): showing team-lead splitting work
- Brownfield project: showing analyzer + migration

**Why replace CommandTabs**: The current 3-step CommandTabs format is thin and duplicated in Getting Started. The README's narrative format is more compelling and shows the full value proposition.

#### Section 6: Agent Swarms (NEW, ~20 lines)
**Source**: README.md lines 201-216
**Action**: Add new section with:
- ASCII art showing 3 parallel agents in iTerm2/tmux panes
- Brief explanation of `/sw:team-lead` splitting work
- Link to full agent teams guide

**Rationale**: Multi-agent orchestration is a key differentiator. The ASCII art is immediately scannable and memorable.

#### Section 7: Who Should Use SpecWeave? (~20 lines)
**Action**: Keep existing "Perfect For" and "Use Cases" subsections. No changes.

#### Section 8: Core Features (~15 lines)
**Action**: Keep existing feature comparison table. Already well-structured.

#### Section 9: What You Get vs. Current State (~12 lines)
**Action**: Keep existing before/after table. No changes.

#### Section 10: Integrations (NEW, ~15 lines)
**Source**: README.md lines 345-358
**Action**: Add integrations table showing GitHub, JIRA, Azure DevOps, and Verified Skills with what syncs for each. Include brief note about auto-sync on increment close.

**Rationale**: Production teams need to know SpecWeave fits their existing toolchain. This was a gap — the current page only mentions sync in passing.

#### Section 11: Built With SpecWeave (~8 lines)
**Action**: Keep existing content. No changes.

#### Section 12: Getting Started (STREAMLINE, ~10 lines)
**Action**: Reduce from current ~30 lines (with 3 CommandTabs) to a compact section:
- Keep the 3-line install block (`npm install`, `cd`, `specweave init`)
- One brief example line
- Link to full Getting Started page
- Remove duplicate CommandTabs (they repeat Section 5's workflow)

**Rationale**: The full Getting Started page at `/docs/getting-started` covers this thoroughly. Duplication here adds length without value.

#### Section 13: Next Steps (~8 lines)
**Action**: Keep existing link list. No changes.

### Complexity Diagram Decision

The README's "hardest problem you can solve" ASCII diagram (lines 161-180) is compelling but adds ~20 lines and may be too detailed for an introduction page. **Decision: Omit from introduction.** This content fits better on the Philosophy or Why SpecWeave page. The introduction should stay focused on "what is this" and "what can it do", not methodology depth.

## Implementation Approach

### Single-Pass Edit Strategy

Since this is a single-file modification, the implementation should be done in one focused pass:

1. **Read** the current introduction.md
2. **Edit** section by section, top to bottom:
   - Keep sections 1-3 (minor config comment enhancement only)
   - Insert new section 4 (No Commands to Memorize)
   - Replace section 5 (How It Works → The Workflow)
   - Insert new section 6 (Agent Swarms)
   - Keep sections 7-9 (no changes)
   - Insert new section 10 (Integrations)
   - Keep section 11 (no changes)
   - Streamline section 12 (Getting Started)
   - Keep section 13 (no changes)
3. **Verify** final line count is in ~300-350 range

### Content Sourcing Rules

- Content from README.md should be **adapted**, not copy-pasted — the introduction page has a different voice (more explanatory, less promotional)
- Remove badge URLs, GitHub-specific elements, and NPM links that don't belong in docs
- Keep Docusaurus-specific formatting (MDX imports, `<CommandTabs>`)
- Preserve existing internal links (`/docs/...` paths)

## Technology Stack

- **Format**: Markdown/MDX (Docusaurus)
- **Component**: `CommandTabs` (already imported, usage may decrease)
- **Build**: Docusaurus static site generator (no build changes)

## Testing Strategy

Since this is documentation only:
- **Visual review**: Verify rendered page looks correct (section ordering, table formatting, code blocks)
- **Link check**: Ensure all internal links (`/docs/...`) point to valid pages
- **Line count**: Verify target range (300-350 lines)
- **No automated tests needed** — this is markdown content

## Technical Challenges

### Challenge 1: Content Adaptation Tone
**Problem**: README.md uses a promotional/marketing tone. Introduction page should be more explanatory.
**Solution**: Rewrite adapted sections to focus on "what this does for you" rather than "why we're the best". Remove superlatives and competitive framing.

### Challenge 2: CommandTabs Component Dependency
**Problem**: Removing "How It Works" CommandTabs means the component import may become unused if no other section uses it.
**Solution**: Keep the import — the Getting Started section (streamlined) may still use one CommandTabs instance. If all are removed, remove the import line too.

### Challenge 3: Page Length Budget
**Problem**: Adding 4 new sections while keeping existing content could push past 350 lines.
**Solution**: The streamlined Getting Started section saves ~20 lines. If still over budget, reduce Agent Swarms to the ASCII art + one line + link (no prose).
