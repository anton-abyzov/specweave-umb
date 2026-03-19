# Plan: Sync Routing Evolutionary Cleanup

## Architecture Decision

**Strategy: Upstream Input Population** — activate the existing 3-phase sync resolver by populating its inputs at creation time, rather than modifying the resolver itself.

The resolver (`sync-target-resolver.ts`) is correct and complete. Phase 1 (name/ID match) and Phase 2 (prefix routing) are dormant because upstream systems never populate `metadata.json.project` or generate `US-{PREFIX}-NNN` story IDs. This increment fixes the inputs, not the engine.

See **ADR-0246: Upstream Input Population for Sync Routing Activation** for the formal decision record.

---

## Component Design

### C1: Project Auto-Detection for Metadata (US-SPE-001)

**Problem**: `template-creator.ts:216-228` creates metadata without a `project` field. The `projectId` parameter IS passed in (line 153) but only used for spec.md templates — never written to metadata.json.

**Solution**: Add `project` field to the metadata object in `createIncrementTemplates()`, with auto-detection from cwd when not explicitly provided.

**Files to modify**:
- `src/core/increment/template-creator.ts` — add `project` to metadata object (line ~228)
- `src/cli/commands/create-increment.ts` — auto-detect project from cwd when `--project` not passed

**Detection logic** (new utility function in `template-creator.ts` or inline):

```
detectProjectFromCwd(config, cwd):
  if !config.umbrella?.enabled → return undefined (no-op for non-umbrella)

  resolvedCwd = path.resolve(cwd)
  umbrellaRoot = resolveEffectiveRoot()

  for each childRepo in config.umbrella.childRepos:
    repoAbsPath = path.resolve(umbrellaRoot, childRepo.path)
    if resolvedCwd starts with repoAbsPath:
      return childRepo.id  // e.g., "specweave"

  return config.umbrella.projectName  // cwd at umbrella root → "specweave-umb"
```

**Integration point**: After the metadata object is built (line 228), before `fs.writeFileSync`:

```typescript
// Auto-populate project field for umbrella routing
if (projectId) {
  metadata.project = projectId;
} else {
  const detectedProject = detectProjectFromCwd(config, process.cwd());
  if (detectedProject) {
    metadata.project = detectedProject;
  }
}
```

**Backward compatibility**: No `project` field = Phase 3 fallback (existing behavior preserved). The `IncrementMetadataV2` type already declares `projectId?: string` at line 577 of `increment-metadata.ts`.

**Edge cases**:
- Deep nested cwd: `repositories/anton-abyzov/specweave/src/sync/` — longest prefix match → `specweave`
- Disabled child repo (`vskill-platform`): still matched for identification (disabled only controls sync)
- No umbrella config: function returns `undefined`, no field added

---

### C2: Wizard Simplification (US-SPE-002)

**Problem**: `prompt-consolidator.ts:34-54` always returns the architecture question with a single option (`github-parent`). When `umbrella.enabled: true`, this question has only one valid answer — wasting user time.

**Solution**: Skip the architecture prompt when umbrella mode is detected. The caller (`repo-structure-manager.ts`) should check config before calling `getArchitecturePrompt()`.

**Files to modify**:
- `src/core/repo-structure/repo-structure-manager.ts` — add umbrella auto-detection guard before architecture prompt (around line 139-147)
- `src/cli/helpers/issue-tracker/github-multi-repo.ts` — respect umbrella config in `promptGitHubSetupType()`

**Logic**:

```
In promptStructure() / promptGitHubSetupType():
  config = loadConfig(projectRoot)
  if config.umbrella?.enabled:
    // Skip architecture question
    architecture = 'github-parent'  // auto-select multi-repo
    activeChildRepos = config.umbrella.childRepos.filter(r => !r.disabled)
    log("Detected umbrella mode with ${activeChildRepos.length} active child repos: ${names}")
    // Proceed directly to per-repo configuration
  else:
    // Existing behavior: ask architecture question
    prompt = getArchitecturePrompt()
    ...
```

**Rate-limit fallback (AC-US2-03)**: If GitHub API calls fail during repo detection, fall back to `config.umbrella.childRepos` for the repo list — no API needed since repos are already declared in config.

**Display (AC-US2-04)**: Show detected repos in setup summary, e.g., `"Detected 2 active child repos: specweave, vskill"`.

---

### C3: Prefixed User Story IDs (US-SPE-003)

**Problem**: `us-id-generator.ts` only generates `US-NNN` format. The `story-router.ts:29-37` already parses `US-{PREFIX}-NNN` but no upstream system generates prefixed IDs.

**Solution**: Extend `us-id-generator.ts` to accept an optional prefix parameter. Update `parseUsId` regex to handle both formats.

**Files to modify**:
- `src/id-generators/us-id-generator.ts` — extend `formatUsId`, `parseUsId`, `getNextUsId` for prefix support
- `src/generators/spec/spec-parser.ts` — update regex to parse prefixed story headers
- PM skill template (if needed) — the template at `plugins/specweave/skills/pm/phases/02-spec-creation.md` already documents `US-FE-001` format for multi-project mode

**Updated functions**:

```typescript
// parseUsId — handle both US-001 and US-SPE-001
const match = id.match(/^US-(?:([A-Za-z]{2,6})-)?(\d+)(E)?$/);
// Group 1: optional prefix, Group 2: number, Group 3: optional E suffix

// formatUsId — accept optional prefix
function formatUsId(number: number, origin: Origin, prefix?: string): string {
  const num = String(number).padStart(3, '0');
  const suffix = origin === 'external' ? 'E' : '';
  return prefix ? `US-${prefix}-${num}${suffix}` : `US-${num}${suffix}`;
}

// getNextUsId — accept optional prefix, filter by prefix when counting
export function getNextUsId(existingIds: string[], origin: Origin, prefix?: string): string {
  // Parse all existing IDs (both prefixed and non-prefixed)
  // Find max number across matching prefix (or all if no prefix)
  // Return next sequential with prefix applied
}
```

**Spec parser update** (`spec-parser.ts:217`):

```
// Before: /^###?\s+(US-\d{3,}E?):\s*(.+)$/
// After:  /^###?\s+(US-(?:[A-Za-z]{2,6}-)?\d{3,}E?):\s*(.+)$/
```

**AC ID format**: AC IDs remain `AC-US{N}-{NN}` where N is the story number only (not the prefix). This preserves the existing bidirectional linking system. Example: `US-SPE-001` → `AC-US1-01`.

**Backward compatibility (AC-US3-05)**:
- Old `US-001` IDs continue to work — they parse as "no prefix"
- Phase 3 global fallback handles them
- `getNextUsId` with no prefix generates old format

**When to inject prefix**: The prefix comes from `config.umbrella.childRepos[].prefix` based on the increment's `project` field. This is resolved at spec creation time (in the PM agent flow), not at the ID generator level — the generator just accepts the prefix parameter.

---

### C4: Project Validation Rule (US-SPE-004)

**Problem**: `sw:validate` doesn't check for missing `project` field in umbrella setups, so routing gaps are only discovered at sync time.

**Solution**: Add a new validation rule to the validator that checks metadata.json for project field presence and validity.

**Files to modify**:
- `src/core/validation/three-file-validator.ts` — add new `ValidationErrorCode` values and validation logic

**New error codes**:

```typescript
// In ValidationErrorCode enum:
METADATA_MISSING_PROJECT = 'METADATA_MISSING_PROJECT',
METADATA_UNKNOWN_PROJECT = 'METADATA_UNKNOWN_PROJECT',
```

**Validation rules**:

| Rule | Condition | Severity | Message |
|------|-----------|----------|---------|
| Missing project | `umbrella.enabled && childRepos.length > 1 && !metadata.project` | WARNING | "Increment has no `project` field — sync will use global fallback. Consider re-creating with `--project`" |
| Unknown project | `metadata.project && !matchesAnyChildRepo(project) && project !== umbrella.projectName` | WARNING | "Project '{name}' not found in config.json childRepos or umbrella.projectName" |
| Non-umbrella OK | `!umbrella.enabled && !metadata.project` | (skip) | No warning for single-repo setups |

**Implementation approach**: Extend `validateIncrement()` which already receives `incrementDir`. Load metadata.json and config to check the project field. Since this validation crosses file boundaries (metadata.json + config.json), it belongs in the existing method which already loads files from the increment directory.

---

## Data Flow

```
Increment Creation Flow (with changes marked *):

  CLI: specweave create-increment "feature-name"
    |
    v
  create-increment.ts
    | * Auto-detect project from cwd via childRepos[].path matching
    |
    v
  createIncrementTemplates({ projectId: "specweave", ... })
    | * Write project field to metadata.json
    | * Pass prefix ("SPE") to PM agent for story ID generation
    |
    v
  metadata.json: { "id": "0618-...", "project": "specweave", ... }
    |
    v
  PM agent generates spec.md
    | * Story IDs use US-SPE-001 format (prefix from config)
    |
    v
  Sync triggered (existing flow)
    |
    v
  resolveSyncTarget("specweave", config)
    | Phase 1: childRepos.find(r => r.id === "specweave") -- MATCH
    | Returns: { github: { owner: "anton-abyzov", repo: "specweave" }, ... }
    |
    v
  Routed to per-repo sync targets (not global fallback)
```

---

## Dependency Order

```
C1 (project auto-detect) --> C3 (prefix injection needs project for prefix lookup)
C1 (project auto-detect) --> C4 (validation checks project field)
C2 (wizard simplification) --> independent (no dependencies)
```

**Implementation order**: C1 -> C3 -> C4 -> C2 (C2 is independent but least critical)

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| `parseUsId` regex change breaks existing ID parsing | New regex is a superset — `US-001` still matches (prefix group is optional). Unit tests cover both formats. |
| Auto-detected project doesn't match config | Validation rule (C4) catches mismatches as warnings. Phase 3 fallback handles unknown projects. |
| Wizard skip breaks non-umbrella setups | Guard condition is explicit: `config.umbrella?.enabled === true`. All other cases fall through to existing prompt. |
| spec-parser regex update misses edge cases | Regex change is minimal (add optional prefix group). Existing tests + new tests for prefixed IDs. |

---

## Out of Scope (per spec)

- Backfilling `project` field on existing 80+ increments
- Per-user-story external project targeting
- Multi-target fan-out sync
- Renaming "umbrella" to "workspace" in config schema
