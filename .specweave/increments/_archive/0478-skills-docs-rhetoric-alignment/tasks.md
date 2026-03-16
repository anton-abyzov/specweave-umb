---
increment: 0478-skills-docs-rhetoric-alignment
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001, T-002, T-003, T-004, T-005]
  US-002: [T-006, T-007, T-008, T-009, T-010]
  US-003: [T-011]
total_tasks: 11
completed: 11
---

# Tasks: Align skills documentation rhetoric with Anthropic official terminology

## User Story: US-001 - Replace invented terminology with Anthropic-aligned language

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 5 total, 5 completed

---

### T-001: Apply DCI + Extensible Skills Standard replacements in high-density extensible/ files

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05 | **Status**: [x] completed

**Scope**: Edit all four files in `skills/extensible/` in a single pass:
- `skills/extensible/extensible-skills-standard.md`
- `skills/extensible/extensible-skills-guide.md`
- `skills/extensible/extensible-skills.md`
- `skills/extensible/index.md`

**Replacement rules**:
- First occurrence of "Dynamic Context Injection (DCI)" or "Dynamic Context Injection" on each page: replace with `dynamic context injection (Claude Code's built-in !command syntax)`
- Subsequent occurrences on the same page: `dynamic context injection`
- All standalone uppercase `DCI` (not inside code fences): expand to `dynamic context injection`
- All `Extensible Skills Standard`: replace with `Extensible Skills`

**Test Plan**:
- **Given** the four `skills/extensible/` files have been edited
- **When** grep runs against each file for banned patterns (excluding code fences)
- **Then** zero matches are returned for: `DCI`, `Dynamic Context Injection`, `Extensible Skills Standard`

**Verification**:
```bash
DOCS="repositories/anton-abyzov/specweave/docs-site/docs/skills/extensible"
grep -n "\bDCI\b" "$DOCS/extensible-skills-standard.md" "$DOCS/extensible-skills-guide.md" "$DOCS/extensible-skills.md" "$DOCS/index.md"
grep -n "Dynamic Context Injection" "$DOCS/extensible-skills-standard.md" "$DOCS/extensible-skills-guide.md" "$DOCS/extensible-skills.md" "$DOCS/index.md"
grep -n "Extensible Skills Standard" "$DOCS/extensible-skills-standard.md" "$DOCS/extensible-skills-guide.md" "$DOCS/extensible-skills.md" "$DOCS/index.md"
# All three commands must return empty output
```

**Implementation**:
1. Edit `extensible-skills-standard.md`: apply R1 (17 occurrences) and R2 (2 occurrences)
2. Edit `extensible-skills-guide.md`: apply R1 (15 occurrences) and R2 (3 occurrences)
3. Edit `extensible-skills.md`: apply R1 (5 occurrences) and R2 (2 occurrences)
4. Edit `extensible/index.md`: apply R1 (4 occurrences) and R2 (3 occurrences)
5. Run verification commands; fix any missed instances

---

### T-002: Apply DCI + Extensible Skills Standard replacements in skills/index.md

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05 | **Status**: [x] completed

**Scope**: Edit `skills/index.md` for DCI and Extensible Skills Standard occurrences only. The tagline replacement and additive-framing addition are handled in T-011 (US-003).

**Replacement rules** (same as T-001):
- First DCI occurrence: `dynamic context injection (Claude Code's built-in !command syntax)`
- Subsequent: `dynamic context injection`
- `Extensible Skills Standard` -> `Extensible Skills`

**Test Plan**:
- **Given** `skills/index.md` has been edited for DCI and Extensible Skills Standard
- **When** grep runs against the file
- **Then** zero matches for `DCI` (standalone acronym), `Dynamic Context Injection`, `Extensible Skills Standard`

**Verification**:
```bash
FILE="repositories/anton-abyzov/specweave/docs-site/docs/skills/index.md"
grep -n "\bDCI\b" "$FILE"
grep -n "Dynamic Context Injection" "$FILE"
grep -n "Extensible Skills Standard" "$FILE"
# All three must return empty output
```

**Implementation**:
1. Edit `skills/index.md`: apply R1 (3 occurrences) and R2 (3 occurrences)
2. Run verification commands

---

### T-003: Apply DCI replacements in medium-density verified/ and skills/ files

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-05 | **Status**: [x] completed

**Scope**:
- `skills/verified/skills-ecosystem-security.md` (R1: 4 occurrences; R4 glossary fix handled in T-004)
- `skills/verified/verified-skills.md` (R1: 1 occurrence; R2 handled in T-005)
- `skills/fundamentals.md` (R1: 1 occurrence; R2 handled in T-005)
- `skills/skill-discovery-evaluation.md` (R1: 1 occurrence)

**Replacement rules**: Apply R1 only (first/subsequent distinction per page). Do not touch R2 or R4 here.

**Test Plan**:
- **Given** the four medium-density files have been edited for DCI
- **When** grep runs for DCI patterns
- **Then** zero matches for `DCI` (standalone) and `Dynamic Context Injection` in those four files

**Verification**:
```bash
DOCS="repositories/anton-abyzov/specweave/docs-site/docs"
grep -n "\bDCI\b" \
  "$DOCS/skills/verified/skills-ecosystem-security.md" \
  "$DOCS/skills/verified/verified-skills.md" \
  "$DOCS/skills/fundamentals.md" \
  "$DOCS/skills/skill-discovery-evaluation.md"
grep -n "Dynamic Context Injection" \
  "$DOCS/skills/verified/skills-ecosystem-security.md" \
  "$DOCS/skills/verified/verified-skills.md" \
  "$DOCS/skills/fundamentals.md" \
  "$DOCS/skills/skill-discovery-evaluation.md"
# Both commands must return empty output
```

**Implementation**:
1. Edit each file applying R1 replacements
2. Run verification commands

---

### T-004: Fix glossary error "Direct Command Injection" in skills-ecosystem-security.md

**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed

**Scope**: `skills/verified/skills-ecosystem-security.md` — targeted single fix in the glossary section.

**Replacement**: `Direct Command Injection` -> `dynamic context injection`

**Test Plan**:
- **Given** `skills-ecosystem-security.md` glossary section has been corrected
- **When** grep searches for the incorrect term and the correct term
- **Then** zero matches for `Direct Command Injection`; at least one match for `dynamic context injection`

**Verification**:
```bash
FILE="repositories/anton-abyzov/specweave/docs-site/docs/skills/verified/skills-ecosystem-security.md"
grep -n "Direct Command Injection" "$FILE"
# Must return empty
grep -n "dynamic context injection" "$FILE"
# Must have at least one hit
```

**Implementation**:
1. Locate the glossary entry containing "Direct Command Injection"
2. Replace with "dynamic context injection"
3. Run verification commands

---

### T-005: Apply Extensible Skills Standard replacements in remaining single-category files

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed

**Scope** (R2 only, 1 occurrence each):
- `skills/verified/verified-skills.md`
- `skills/fundamentals.md`
- `skills/verified/index.md`
- `academy/talks/skills-plugins-marketplaces.md`
- `guides/core-concepts/skills-first-architecture.md`
- `glossary/terms/skills-vs-agents.md`

**Replacement**: `Extensible Skills Standard` -> `Extensible Skills`

**Test Plan**:
- **Given** all six files have been edited
- **When** grep searches for "Extensible Skills Standard"
- **Then** zero matches across all six files

**Verification**:
```bash
DOCS="repositories/anton-abyzov/specweave/docs-site/docs"
grep -rn "Extensible Skills Standard" \
  "$DOCS/skills/verified/verified-skills.md" \
  "$DOCS/skills/fundamentals.md" \
  "$DOCS/skills/verified/index.md" \
  "$DOCS/academy/talks/skills-plugins-marketplaces.md" \
  "$DOCS/guides/core-concepts/skills-first-architecture.md" \
  "$DOCS/glossary/terms/skills-vs-agents.md"
# Must return empty output
```

**Implementation**:
1. Edit each file replacing `Extensible Skills Standard` with `Extensible Skills`
2. Run verification commands

---

## User Story: US-002 - Remove SOLID/OCP references from skill customization docs

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 5 total, 5 completed

---

### T-006: Replace SOLID/OCP references in high-density extensible/ files

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Scope**:
- `skills/extensible/extensible-skills-standard.md` (R3: 1 occurrence)
- `skills/extensible/extensible-skills-guide.md` (R3: 2 occurrences)
- `skills/extensible/extensible-skills.md` (R3: 4 occurrences)
- `skills/extensible/index.md` (R3: 4 occurrences)

**Replacement rule (R3)**: Replace `Open/Closed Principle`, `Open-Closed Principle`, or `SOLID` with plain-language equivalent. Preferred: "core skill logic stays stable; your project-specific customizations layer on top". Remove standalone `SOLID` mentions that add no meaning.

**Test Plan**:
- **Given** the four extensible/ files have been edited for SOLID/OCP
- **When** grep runs for SOLID and Open/Closed patterns
- **Then** zero matches in those files

**Verification**:
```bash
DOCS="repositories/anton-abyzov/specweave/docs-site/docs/skills/extensible"
grep -in "Open.Closed Principle\|Open-Closed Principle\|\bSOLID\b" \
  "$DOCS/extensible-skills-standard.md" \
  "$DOCS/extensible-skills-guide.md" \
  "$DOCS/extensible-skills.md" \
  "$DOCS/index.md"
# Must return empty output
```

**Implementation**:
1. Edit each file, replacing each SOLID/OCP reference with the plain-language equivalent
2. Run verification commands

---

### T-007: Replace SOLID/OCP references in skills/index.md

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Scope**: `skills/index.md` (R3: 1 occurrence)

**Replacement rule**: Same as T-006.

**Test Plan**:
- **Given** `skills/index.md` has been edited for SOLID/OCP
- **When** grep runs
- **Then** zero matches for `Open/Closed Principle`, `Open-Closed Principle`, `SOLID`

**Verification**:
```bash
FILE="repositories/anton-abyzov/specweave/docs-site/docs/skills/index.md"
grep -in "Open.Closed Principle\|Open-Closed Principle\|\bSOLID\b" "$FILE"
# Must return empty output
```

**Implementation**:
1. Locate the SOLID/OCP reference in `skills/index.md`
2. Replace with plain-language equivalent
3. Run verification command

---

### T-008: Replace SOLID/OCP references in skill-development-guidelines.md

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Scope**: `skills/extensible/skill-development-guidelines.md` (R3: 4 occurrences)

**Replacement rule**: Same as T-006.

**Test Plan**:
- **Given** `skill-development-guidelines.md` has been edited
- **When** grep runs for SOLID/OCP patterns
- **Then** zero matches

**Verification**:
```bash
FILE="repositories/anton-abyzov/specweave/docs-site/docs/skills/extensible/skill-development-guidelines.md"
grep -in "Open.Closed Principle\|Open-Closed Principle\|\bSOLID\b" "$FILE"
# Must return empty output
```

**Implementation**:
1. Edit all 4 SOLID/OCP occurrences in the file
2. Run verification command

---

### T-009: Replace SOLID/OCP references in single-category R3 files

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Scope** (R3 only):
- `overview/skills-as-programs.md` (2 occurrences)
- `quick-start.md` (2 occurrences)
- `guides/youtube-tutorial-script.md` (2 occurrences; tagline handled in T-010)
- `glossary/categories/architecture.md` (1 occurrence)
- `glossary/index-by-category.md` (1 occurrence)
- `academy/fundamentals/software-engineering-roles.md` (1 occurrence)

**Replacement rule**: Same as T-006.

**Test Plan**:
- **Given** all six files have been edited for SOLID/OCP
- **When** grep runs across all six
- **Then** zero matches for SOLID/OCP patterns in any of those files

**Verification**:
```bash
DOCS="repositories/anton-abyzov/specweave/docs-site/docs"
grep -in "Open.Closed Principle\|Open-Closed Principle\|\bSOLID\b" \
  "$DOCS/overview/skills-as-programs.md" \
  "$DOCS/quick-start.md" \
  "$DOCS/guides/youtube-tutorial-script.md" \
  "$DOCS/glossary/categories/architecture.md" \
  "$DOCS/glossary/index-by-category.md" \
  "$DOCS/academy/fundamentals/software-engineering-roles.md"
# Must return empty output
```

**Implementation**:
1. Edit each file replacing SOLID/OCP occurrences with plain-language equivalents
2. Run verification commands

---

### T-010: Replace "programs written in English" tagline in guides/youtube-tutorial-script.md

**User Story**: US-002 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed

**Scope**: `guides/youtube-tutorial-script.md` — targeted tagline replacement.

**Replacement**: `programs written in English` -> `Skills extend what AI coding agents can do -- structured markdown files that define how an agent behaves in specific domains` (use shorter form "structured markdown instructions" if context is space-constrained)

**Test Plan**:
- **Given** `guides/youtube-tutorial-script.md` has been edited
- **When** grep runs for the old tagline
- **Then** zero matches for `programs written in English`

**Verification**:
```bash
FILE="repositories/anton-abyzov/specweave/docs-site/docs/guides/youtube-tutorial-script.md"
grep -n "programs written in English" "$FILE"
# Must return empty output
```

**Implementation**:
1. Locate the tagline in the file
2. Replace with Anthropic-aligned framing
3. Run verification command

---

## User Story: US-003 - Clarify SpecWeave's additive value over Claude Code native features

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US1-03
**Tasks**: 1 total, 5 completed

---

### T-011: Update skills/index.md with tagline replacement and additive-value framing

**User Story**: US-003 | **Satisfies ACs**: AC-US1-03, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Scope**: `skills/index.md` — two targeted edits:

1. **Tagline replacement (AC-US1-03)**: Replace `programs written in English` with:
   `Skills extend what AI coding agents can do -- structured markdown files that define how an agent behaves in specific domains`

2. **Additive-value note (AC-US3-01/02/03)**: Add a brief section or inline note that:
   - Acknowledges Claude Code's native skill system
   - Positions SpecWeave contributions (Verified Skills, vskill CLI, marketplace, extensibility conventions) as building on top
   - Uses collaborative tone: "SpecWeave builds on Claude Code's native skill system by adding..."
   - References dynamic context injection as a Claude Code built-in capability SpecWeave leverages

**Test Plan**:
- **Given** `skills/index.md` has received both edits
- **When** grep runs for banned patterns and presence checks
- **Then** zero matches for `programs written in English`; at least one match for `SpecWeave builds on` or `Claude Code's native skill system`; at least one match for `Claude Code's built-in` (from DCI first-occurrence framing)

**Verification**:
```bash
FILE="repositories/anton-abyzov/specweave/docs-site/docs/skills/index.md"
grep -n "programs written in English" "$FILE"
# Must return empty

grep -n "Claude Code's native skill system\|SpecWeave builds on" "$FILE"
# Must have at least one hit

grep -n "Claude Code's built-in" "$FILE"
# Must have at least one hit (from DCI first-occurrence framing added in T-002)
```

**Implementation**:
1. Locate tagline line in `skills/index.md` and apply replacement
2. Identify appropriate location (intro or short subsection) for the additive-value note
3. Draft the note using collaborative tone per AC-US3-02
4. Confirm DCI first-occurrence form already applied (by T-002)
5. Run all three verification commands

---

## Final Verification (run after all tasks complete)

Run this sweep against all docs-site markdown (excluding drafts/) to confirm zero banned patterns remain:

```bash
DOCS="repositories/anton-abyzov/specweave/docs-site/docs"

echo "=== DCI acronym ==="
grep -rn --include="*.md" "\bDCI\b" "$DOCS" --exclude-dir=drafts

echo "=== Dynamic Context Injection (capitalized) ==="
grep -rn --include="*.md" "Dynamic Context Injection" "$DOCS" --exclude-dir=drafts

echo "=== Extensible Skills Standard ==="
grep -rn --include="*.md" "Extensible Skills Standard" "$DOCS" --exclude-dir=drafts

echo "=== Open/Closed or SOLID ==="
grep -rni --include="*.md" "Open.Closed Principle\|Open-Closed Principle\|\bSOLID\b" "$DOCS" --exclude-dir=drafts

echo "=== Direct Command Injection ==="
grep -rn --include="*.md" "Direct Command Injection" "$DOCS" --exclude-dir=drafts

echo "=== programs written in English ==="
grep -rn --include="*.md" "programs written in English" "$DOCS" --exclude-dir=drafts

# All sections must output nothing after their header line
```
