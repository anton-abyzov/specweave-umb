---
increment: 0575-docs-no-docs-needed-rewrite
title: "Content architecture for no-docs-needed page rewrite"
type: change-request
status: planned
created: 2026-03-18
---

# Plan: Rework no-docs-needed page to lead with SpecWeave value

## Overview

Single file content rewrite: `repositories/anton-abyzov/specweave/docs-site/docs/overview/no-docs-needed.md`, plus two minor cross-reference updates (sidebar label, inbound link text). No code changes, no new files, no structural changes.

## Problem Analysis

The current page ("You Don't Need to Learn Claude Code") has two messaging problems:

1. **Title frames SpecWeave as a Claude Code wrapper.** The headline puts Claude Code center stage and positions SpecWeave as an abstraction layer. This contradicts the introduction page which positions SpecWeave as "a spec-first AI development framework" that works with ANY AI tool.

2. **Content is Claude Code-centric.** The comparison table maps SpecWeave features 1:1 to Claude Code concepts (hooks, CLAUDE.md, plugins). The "How It Works Under the Hood" section reinforces the wrapper framing. A reader unfamiliar with Claude Code gets no value.

## Content Architecture

### New Title and Sidebar Metadata

```yaml
sidebar_position: 3          # unchanged
title: "Zero Learning Curve"
description: "Skills encode expertise so you don't have to learn it. Describe what you want, SpecWeave handles planning, architecture, testing, and documentation."
```

- **Sidebar label** in `sidebars.ts` (line 21): Update to `"Zero Learning Curve"`

### Section Flow

```
1. Hero statement       — Lead with SpecWeave's value, not Claude Code's complexity
2. The Problem          — AI tools require expertise to use well (tool-agnostic)
3. How SpecWeave Solves — Skills as packaged expertise (describe -> done)
4. What This Looks Like — Before/after: vibe coding vs SpecWeave 3-command flow
5. Why It Works         — Brief spec-first methodology connection
6. Go Deeper            — Escape hatch for power users (keep from current page)
```

### Section Details

**1. Hero**
- Lead: "Describe what you want. SpecWeave handles the rest."
- Frame: skills encode best practices so you don't need to learn them
- Do NOT mention Claude Code in the opening paragraph

**2. The Problem**
- AI coding tools are powerful but unstructured
- Good results require prompt engineering, context management, workflow discipline
- Most developers don't want to become AI-tool experts — they want to ship
- Keep generic (applies to Claude Code, Cursor, Copilot, etc.)

**3. How SpecWeave Solves It**
- Skills are structured expertise — each one packages domain knowledge
- Table: what skills handle (planning, architecture, testing, quality, docs)
- User's job: describe the feature. SpecWeave's job: everything else
- Reference ~48 built-in skills, link to `./skills-as-structured-expertise`

**4. What This Looks Like**
- Replace current "Without/With SpecWeave" comparison
- Show 3-command flow: `/sw:increment` -> `/sw:do` -> `/sw:done`
- Keep code block format (concise, scannable)

**5. Why It Works**
- Brief (3-4 sentences) on spec-first methodology as the engine
- Link to `./philosophy` and `./why-specweave` for depth
- Key points: specs persist, quality gates enforce standards, living docs stay current

**6. Go Deeper**
- Keep this section — honest and useful
- Update links: skill development, extensible skills, troubleshooting
- Frame as "power user" territory, not "learning Claude Code"

### Messaging Alignment with Adjacent Pages

| Page | Key Messaging | Alignment Point |
|------|--------------|-----------------|
| **introduction.md** | "Spec-first AI development framework" / "Configure AI, don't prompt it" | Lead with SpecWeave as a framework, not a wrapper |
| **why-specweave.md** | "AI changed how we write code. SpecWeave changes how we ship products." | Focus on shipping outcomes, not tool abstraction |
| **skills-as-structured-expertise.md** | Skills = reusable structured instructions | Reference skills as the mechanism |
| **philosophy.md** | Plan > Code, spec-first, context precision | Connect zero-learning-curve to spec-first methodology |

### Cross-Linking Updates

**Inbound link from why-specweave.md (line 148)**:
- Current: `"SpecWeave abstracts Claude Code's complexity — hooks, plugins, CLAUDE.md, context management. Install, describe your feature, skills handle the rest."`
- Update to: `"SpecWeave's skills encode expertise so you don't need to learn it yourself. Describe your feature, skills handle the rest."`
- Link target unchanged: `./no-docs-needed`

**Sidebar label in sidebars.ts (line 21)**:
- Current: `"You Don't Need Claude Code Docs"`
- Update to: `"Zero Learning Curve"`

### Content to Remove

- Claude Code concepts comparison table (hooks, CLAUDE.md, plugins mapping)
- "How It Works Under the Hood" section (describes Claude Code extension points)
- Any framing of SpecWeave as sitting "on top of" or "abstracting" Claude Code
- The assembly/Python analogy (reinforces wrapper positioning)

### Content to Keep

- Install + 3-command code block (effective, concise)
- "When You Might Want to Learn More" section (honest, builds trust)
- Similar overall length (~60-70 lines of content)

## Files to Modify

| # | File | Change |
|---|------|--------|
| 1 | `repositories/anton-abyzov/specweave/docs-site/docs/overview/no-docs-needed.md` | Full content rewrite |
| 2 | `repositories/anton-abyzov/specweave/docs-site/sidebars.ts` (line 21) | Update sidebar label |
| 3 | `repositories/anton-abyzov/specweave/docs-site/docs/overview/why-specweave.md` (line 148) | Update inbound link teaser text |

## Technical Notes

- Docusaurus frontmatter: `sidebar_position`, `title`, `description` required
- Internal links use relative paths: `./skills-as-structured-expertise`, `./philosophy`
- External doc links use absolute paths: `/docs/getting-started`
- No Mermaid diagrams — keep it text-focused
- The file ID (`overview/no-docs-needed`) does NOT change — no URL breakage
