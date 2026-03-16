# Implementation Plan: AskUserQuestion Markdown Previews for SpecWeave Skills

## Overview

Add a TypeScript utility module (`src/utils/ascii-diagrams.ts`) with four pure functions for generating ASCII diagrams, then update three SKILL.md files to instruct Claude to use `AskUserQuestion` markdown previews at decision points.

## Architecture

### Components

1. **`src/utils/ascii-diagrams.ts`** — Pure functions, zero dependencies, no I/O
   - `renderBoxDiagram(nodes, connections)` → Unicode box-drawing service diagrams
   - `renderDAG(tasks, dependencies)` → Task dependency graphs with parallel lanes
   - `renderTable(headers, rows, options?)` → Aligned ASCII tables
   - `renderTree(items)` → File/folder tree with branch characters

2. **SKILL.md updates** — Three skills get a new "Markdown Preview" section:
   - `plugins/specweave/skills/architect/SKILL.md` — Box + table previews
   - `plugins/specweave/skills/plan/SKILL.md` — DAG previews
   - `plugins/specweave/skills/increment/SKILL.md` — Tree + table previews

### Data Model

```typescript
// Box diagram
interface BoxNode { id: string; label: string; sublabel?: string }
interface BoxConnection { from: string; to: string; label?: string }

// DAG
interface DAGTask { id: string; name: string }
interface DAGDependency { from: string; to: string }

// Table
interface TableOptions { headerSeparator?: boolean; maxColWidth?: number }

// Tree
interface TreeItem { name: string; children?: TreeItem[] }
```

### Design Decisions

1. **Pure functions over class** — No state, no constructor, just `export function renderX()`. Simpler to test, import, and use.
2. **Fixed 80-char width** — No terminal detection. Truncate with `…` when content exceeds width.
3. **Unicode box-drawing** — `─│┌┐└┘├┤┬┴┼` for clean rendering in Claude Code terminal (proven to work in our earlier tests).
4. **SKILL.md instructions, not code injection** — Skills are prompts. We add a section telling Claude WHEN and HOW to use `AskUserQuestion` with markdown previews, with complete copy-paste examples.

## Implementation Phases

### Phase 1: ASCII Diagram Utility (TDD)
- Write failing tests for all four render functions
- Implement each function to pass tests
- Edge case tests: empty input, single node, overflow

### Phase 2: SKILL.md Integration
- Add "Markdown Preview Guidelines" section to architect SKILL.md
- Add "Markdown Preview Guidelines" section to plan SKILL.md
- Add "Markdown Preview Guidelines" section to increment SKILL.md
- Each section includes: when to trigger, format spec, 2+ examples

### Phase 3: Verification
- Manual verification: invoke each skill, confirm previews render
- Run full unit test suite

## Testing Strategy

- **Unit tests**: `tests/unit/ascii-diagrams.test.ts` — All four functions, edge cases, width constraints
- **Pattern**: Vitest with `describe/it/expect`, explicit imports, `.js` extension imports
- **Coverage target**: 95% for `src/utils/ascii-diagrams.ts`
- **No integration tests** — SKILL.md changes are prompt text, verified manually

## Technical Challenges

### Challenge 1: DAG Layout
Multi-lane DAG rendering is non-trivial. Simple approach: topological sort, assign lanes by depth, draw horizontal arrows.
**Mitigation**: Start with a simple linear+parallel model (max 3 lanes). Complex DAGs fall back to listing dependencies textually.

### Challenge 2: Column Width in Tables
Long content can blow past 80 chars.
**Solution**: Measure max content width per column, proportionally shrink columns that exceed their fair share, truncate with `…`.
