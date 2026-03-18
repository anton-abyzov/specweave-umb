# Architecture Plan: vskill Frontmatter Compliance

## Overview

Add a pure-function frontmatter layer (`ensureFrontmatter`) that guarantees every SKILL.md written by vskill contains `name` and `description` in YAML frontmatter, per the agentskills.io standard. The function lives in a new `src/installer/frontmatter.ts` module and is called at the top of each install/update code path so that all downstream writes receive compliant content.

## Architecture Decisions

### AD-1: New file `src/installer/frontmatter.ts`

**Decision**: Create a standalone module in the installer directory. Do NOT import or modify `eval-ui/src/utils/parseFrontmatter.ts`.

**Rationale**: eval-ui is a separate build target (excluded from `tsconfig.json`), so importing from it would require config changes and create coupling between installer and UI. The new module needs different behavior: it writes/injects frontmatter rather than parsing it for display. A focused, self-contained module is easier to test and has zero risk of breaking eval-ui.

**Exports**:
- `ensureFrontmatter(content: string, skillName: string): string` -- pure function, the core of the feature
- `validateSkillNameStrict(name: string): boolean` -- pure validation per agentskills.io format
- `extractDescription(body: string, skillName: string): string` -- extracts first paragraph or humanizes skillName

### AD-2: Process content ONCE at top of installSymlink/installCopy

**Decision**: Apply `ensureFrontmatter(content, skillName)` once at the beginning of each function, then use the processed content for all downstream writes (canonical dir, copy-fallback agents, symlink-failure fallback).

**Rationale**: The current code passes `content` to multiple `writeFileSync` calls within each function. Processing once at the top eliminates the risk of missing a write site within the function, and avoids processing the same content multiple times. This satisfies AC-US2-01 through AC-US2-04.

```
installSymlink(skillName, content, agents, opts, agentFiles):
  content = ensureFrontmatter(content, skillName)   // single injection point
  writeFileSync(canonical, content)                  // uses processed content
  writeFileSync(copy-fallback, content)              // uses processed content
  writeFileSync(symlink-failure, content)            // uses processed content
```

### AD-3: update.ts gets its own call site

**Decision**: Add `ensureFrontmatter(result.content, name)` in update.ts before the writeFileSync loop (around line 162, before the agent iteration at line 162-178).

**Rationale**: update.ts fetches content from remote sources and writes directly via `writeFileSync`, completely bypassing canonical.ts. It must apply the same frontmatter guarantee. This satisfies AC-US2-05.

### AD-4: Preserve author frontmatter -- no override

**Decision**: If `name` already exists in frontmatter and differs from `skillName`, keep the author's value. Only inject `name` when it is absent. Same rule for `description`.

**Rationale**: The agentskills.io standard says name "should match the directory name" but the spec explicitly calls out preserving author intent (AC-US1-05). Overriding would break skills where authors deliberately set a different display name.

### AD-5: Name validation is warning-only

**Decision**: `validateSkillNameStrict` returns a boolean. Callers log a warning via `console.warn` but do NOT reject the install.

**Rationale**: Backward compatibility. Existing skills may have names that do not match strict agentskills.io format (uppercase, underscores). Breaking them would be a regression. Warnings guide authors toward compliance without blocking installs.

### AD-6: Frontmatter parsing strategy -- regex, no YAML library

**Decision**: Use regex-based frontmatter parsing (match `---\n...\n---` block). Check for `name:` and `description:` lines with regex. Inject missing fields by appending to the frontmatter block before the closing `---`.

**Rationale**: The vskill codebase has no YAML parsing dependency and the existing eval-ui parser also uses regex. We only need to detect and inject two specific fields, not parse arbitrary YAML. Regex is sufficient, fast, and adds no dependencies.

### AD-7: Description extraction heuristic

**Decision**: Extract description from the body by finding the first non-empty line that is not a heading (`#`) and not a frontmatter delimiter (`---`). Truncate to 200 characters. If no suitable line exists, humanize the skill name (`my-skill` becomes `my skill`).

**Rationale**: SKILL.md files commonly start with a heading followed by a description paragraph. This heuristic covers the vast majority of real-world skills. The humanized-name fallback ensures we never produce an empty description.

## Component Design

### `src/installer/frontmatter.ts`

```
+------------------------------------------+
| frontmatter.ts                           |
|------------------------------------------|
| ensureFrontmatter(content, skillName)    |
|   - detect existing frontmatter block    |
|   - check for name: and description:     |
|   - inject missing fields                |
|   - return compliant content             |
|                                          |
| validateSkillNameStrict(name)            |
|   - regex: /^[a-z0-9]([a-z0-9-]{0,62}   |
|     [a-z0-9])?$/                         |
|   - single char: /^[a-z0-9]$/           |
|                                          |
| extractDescription(body, skillName)      |
|   - scan lines for first paragraph text  |
|   - skip headings (#) and blank lines    |
|   - truncate to 200 chars               |
|   - fallback: humanize skillName         |
+------------------------------------------+
```

### Integration Points

```
  add.ts (4 direct-write paths)           canonical.ts
  +----------------------------+   +--------------------------------+
  | line ~507: writeFileSync   |   | installSymlink():              |
  | line ~521: writeFileSync   |   |   content = ensureFrontmatter()|
  | line ~1587: writeFileSync  |   |   write canonical              |
  | line ~2241: writeFileSync  |   |   write copy-fallback          |
  +----------------------------+   |   write symlink-failure        |
         |                         |                                |
         |                         | installCopy():                 |
         v                         |   content = ensureFrontmatter()|
  update.ts                        |   write per-agent              |
  +----------------------------+   +--------------------------------+
  | line ~170: writeFileSync   |
  |   content = ensureFrontmatter()
  +----------------------------+
```

**Write sites requiring changes** (7 total across 3 files):

| # | File | Line(s) | Current behavior | Change |
|---|------|---------|------------------|--------|
| 1 | canonical.ts `installSymlink` | 114 | writes raw content to canonical | Process content once at top of function |
| 2 | canonical.ts `installSymlink` | 128 | writes raw content (copy-fallback) | Covered by #1 (uses same variable) |
| 3 | canonical.ts `installSymlink` | 141 | writes raw content (symlink-failure) | Covered by #1 (uses same variable) |
| 4 | canonical.ts `installCopy` | 168 | writes raw content per agent | Process content once at top of function |
| 5 | update.ts | 170 | writes raw content in loop | Apply ensureFrontmatter before writeFileSync |
| 6 | add.ts repo plugin install | 507, 521 | writes raw fetched content | Apply ensureFrontmatter before writeFileSync |
| 7 | add.ts direct install paths | 1587, 2241 | writes raw content | Apply ensureFrontmatter before writeFileSync |

**Approach for each category**:
- **canonical.ts (sites 1-4)**: One-line change at top of each function: `content = ensureFrontmatter(content, skillName);`
- **update.ts (site 5)**: Add import, apply transform before write loop
- **add.ts (sites 6-7)**: Add import, apply before each direct writeFileSync call

### Data Flow

```
Raw SKILL.md content (from registry/GitHub/local)
        |
        v
ensureFrontmatter(content, skillName)
        |
        +-- Has frontmatter? --YES--> Parse existing fields
        |                               |
        |                               +-- Has name? --YES--> Keep it (AC-US1-05)
        |                               |              NO----> Inject skillName
        |                               |
        |                               +-- Has description? --YES--> Keep it
        |                               |                     NO----> Extract from body
        |                               |
        |                               +-- Serialize: existing fields + injected + body
        |
        +-- NO frontmatter ----> Create new block with name + description + body
        |
        v
Processed content (guaranteed name + description in frontmatter)
        |
        v
writeFileSync(path, processedContent)
```

## Implementation Phases

### Phase 1: Core function (TDD -- red/green/refactor)

1. Create `src/installer/frontmatter.test.ts` with tests for all AC scenarios and edge cases
2. Implement `src/installer/frontmatter.ts` to make tests green

### Phase 2: Integration (write-site changes)

3. Modify `src/installer/canonical.ts` -- import frontmatter.ts, process content at top of installSymlink and installCopy
4. Modify `src/commands/update.ts` -- import frontmatter.ts, apply ensureFrontmatter before write loop
5. Modify `src/commands/add.ts` -- import frontmatter.ts, apply ensureFrontmatter at each direct-write site

### Phase 3: Integration tests

6. Extend `src/installer/canonical.test.ts` with tests verifying frontmatter presence in written files
7. Run full test suite to confirm zero regressions

## Test Plan

All tests use **real filesystem** with temp directories (matching existing `canonical.test.ts` pattern). No mocking of fs.

### frontmatter.test.ts (unit -- pure functions)

| Test | AC |
|------|----|
| No frontmatter: injects name and description | AC-US1-01 |
| Has frontmatter, missing name: injects name | AC-US1-02 |
| Has frontmatter, missing description: injects description | AC-US1-03 |
| Has both name and description: returns unchanged | AC-US1-04 |
| Has different name from skillName: preserves author name | AC-US1-05 |
| Empty body: description defaults to humanized name | Edge case |
| CRLF line endings: handled without corruption | Edge case |
| Malformed YAML-like content: treated as no-frontmatter | Edge case |
| Extra frontmatter fields preserved | NFR |
| Valid names pass strict validation | AC-US3-01 |
| Uppercase names fail strict validation | AC-US3-02 |
| Underscores/spaces fail strict validation | AC-US3-03 |
| Empty/too-long names fail strict validation | AC-US3-04 |
| Leading/trailing hyphens fail strict validation | AC-US3-05 |
| Description extraction: picks first paragraph | AC-US1-03 |
| Description extraction: skips headings | AC-US1-03 |
| Description extraction: truncates to 200 chars | Edge case |

### canonical.test.ts (integration -- filesystem)

| Test | AC |
|------|----|
| installSymlink writes SKILL.md with frontmatter injected | AC-US2-01 to AC-US2-03 |
| installCopy writes SKILL.md with frontmatter injected | AC-US2-04 |
| Existing frontmatter preserved through install flow | AC-US1-04 |

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Regex parser mishandles exotic frontmatter | Test with varied real-world SKILL.md samples; regex handles only `name:` and `description:` lines |
| Existing canonical.test.ts assertions break | Tests currently pass raw content like `"# My Skill\nContent here"` -- after change, written files will include injected frontmatter. Update assertions to account for frontmatter prefix. |
| add.ts write sites missed | add.ts has 4 separate writeFileSync(SKILL.md) paths at lines ~507, ~521, ~1587, ~2241. Each must be patched. Integration tests catch gaps. |
| Performance overhead | ensureFrontmatter is a handful of string operations on small content (<100KB). Negligible. |

## Files Changed

| File | Type | Description |
|------|------|-------------|
| `src/installer/frontmatter.ts` | NEW | ensureFrontmatter, validateSkillNameStrict, extractDescription |
| `src/installer/frontmatter.test.ts` | NEW | Unit tests for all pure functions (TDD -- written first) |
| `src/installer/canonical.ts` | MODIFY | Import frontmatter.ts, process content at top of installSymlink/installCopy |
| `src/installer/canonical.test.ts` | MODIFY | Add integration tests verifying frontmatter in written files |
| `src/commands/update.ts` | MODIFY | Import frontmatter.ts, apply ensureFrontmatter before write loop |
| `src/commands/add.ts` | MODIFY | Import frontmatter.ts, apply ensureFrontmatter at 4 direct-write sites |

## Technology Stack

- **Language**: TypeScript (ESM, NodeNext module resolution, `.js` import extensions)
- **Testing**: Vitest with real filesystem (temp dirs), no fs mocking
- **Dependencies**: None added -- regex-based parsing, no YAML library
