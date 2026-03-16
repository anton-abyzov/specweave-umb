# Architecture Plan: Filter Framework Plugin Skills from Marketplace

## Overview

Add a second path-rejection filter to vskill-platform that prevents SpecWeave's own framework-bundled skills (paths matching `plugins/specweave*/skills/`) from appearing in the community marketplace. The change is additive: a new `isFrameworkPluginPath()` function is composed with the existing `isAgentConfigPath()` into a unified `shouldRejectSkillPath()` wrapper, then propagated to all 12 call sites (8 TS, 4 JS) plus a one-time DB cleanup script.

## Architecture Decision: Composition Over Extension

**Decision**: Add `isFrameworkPluginPath()` as a peer function alongside `isAgentConfigPath()`, composed by a new `shouldRejectSkillPath()` wrapper. Do NOT add the regex to `AGENT_CONFIG_PREFIXES`.

**Rationale**:
- The two rejection categories have different semantics: agent-config paths are user-installed copies; framework plugin paths are first-party framework code. Conflating them in one list would muddy the rejection reason messages and make it harder to reason about filtering behavior.
- Separate functions allow separate rejection reason strings, enabling accurate audit trails in SubmissionStateEvent records.
- `isAgentConfigPath()` stays exported for backward compatibility (AC-US2-04).
- `shouldRejectSkillPath()` becomes the single recommended call-site entry point, simplifying future additions (just add another `is*Path()` and compose it in).

**Pattern reference**: This follows the same additive-filter composition used by `isAgentConfigPath()` + `agentConfigRejectionReason()` -- we mirror it with `isFrameworkPluginPath()` + `frameworkPluginRejectionReason()`.

## Component Design

### C1: Core Filter Module (`src/lib/skill-path-validation.ts`)

**Current exports**: `AGENT_CONFIG_PREFIXES`, `isAgentConfigPath()`, `agentConfigRejectionReason()`

**New exports**:

```
FRAMEWORK_PLUGIN_RE         RegExp   /^plugins\/specweave[^/]*\/skills\//
isFrameworkPluginPath()     boolean  Tests normalized path against FRAMEWORK_PLUGIN_RE
frameworkPluginRejectionReason()  string   Human-readable reason string
shouldRejectSkillPath()     boolean  isAgentConfigPath(p) || isFrameworkPluginPath(p)
rejectionReason()           string | null  Returns matching reason or null
```

**Internal logic**:

```
isFrameworkPluginPath(skillPath: string): boolean
  1. Guard: if (!skillPath) return false
  2. Normalize: replace backslashes with forward slashes, strip leading slashes
  3. Test: FRAMEWORK_PLUGIN_RE.test(normalized)

shouldRejectSkillPath(skillPath: string): boolean
  return isAgentConfigPath(skillPath) || isFrameworkPluginPath(skillPath)

rejectionReason(skillPath: string): string | null
  if (isAgentConfigPath(skillPath)) return agentConfigRejectionReason(skillPath)
  if (isFrameworkPluginPath(skillPath)) return frameworkPluginRejectionReason(skillPath)
  return null
```

**Why a compiled regex instead of prefix array**: The pattern uses a character class (`specweave[^/]*`) which cannot be expressed as a simple `startsWith` check. A single compiled `RegExp` constant is the natural fit -- it is evaluated once at module load time (zero runtime allocation), unlike `AGENT_CONFIG_PREFIXES.some()` which creates a closure per call.

### C2: TypeScript Call Sites (8 sites across 5 files)

All call sites currently import `isAgentConfigPath` (and in some cases `agentConfigRejectionReason`). The migration is mechanical: replace import + usage.

| File | Sites | Current | New |
|------|-------|---------|-----|
| `src/lib/scanner.ts` L220 | 1 | `!isAgentConfigPath(item.path)` | `!shouldRejectSkillPath(item.path)` |
| `src/lib/scanner.ts` L548 | 1 | `isAgentConfigPath(item.path)` + `agentConfigRejectionReason` | `shouldRejectSkillPath(item.path)` + `rejectionReason` |
| `src/app/api/v1/submissions/route.ts` L549 | 1 | `isAgentConfigPath(skillPath)` | `shouldRejectSkillPath(skillPath)` |
| `src/app/api/v1/submissions/route.ts` L625 | 1 | `!isAgentConfigPath(s.path)` | `!shouldRejectSkillPath(s.path)` |
| `src/app/api/v1/submissions/bulk/route.ts` L143 | 1 | `isAgentConfigPath(resolvedPath)` | `shouldRejectSkillPath(resolvedPath)` |
| `src/lib/crawler/github-discovery.ts` L348 | 1 | `isAgentConfigPath(item.path)` | `shouldRejectSkillPath(item.path)` |
| `src/lib/crawler/github-discovery.ts` L624 | 1 | `isAgentConfigPath(entry.path)` | `shouldRejectSkillPath(entry.path)` |
| `src/lib/crawler/vendor-org-discovery.ts` L168 | 1 | `isAgentConfigPath(entry.path)` | `shouldRejectSkillPath(entry.path)` |

Import changes: Replace `isAgentConfigPath, agentConfigRejectionReason` with `shouldRejectSkillPath, rejectionReason` (or just `shouldRejectSkillPath` where no reason string is needed). Keep `isAgentConfigPath` exported from the module for backward compat, but call sites switch to the unified wrapper.

### C3: Crawl-Worker JS Files (4 files)

The crawl-worker runs on Hetzner VMs as plain JS (no TS compilation). Two of the four files import from `repo-files.js`; two use inline copies.

| File | Strategy | Reason |
|------|----------|--------|
| `crawl-worker/lib/repo-files.js` | Add `isFrameworkPluginPath()` and `shouldRejectSkillPath()` as new exports | This is the shared utility module |
| `crawl-worker/lib/skill-discovery.js` | Import `shouldRejectSkillPath` from `repo-files.js`, replace `isAgentConfigPath` | Already imports from repo-files |
| `crawl-worker/sources/queue-processor.js` | Add inline `FRAMEWORK_PLUGIN_RE` + `isFrameworkPluginPath()`, combine with existing inline `isAgentConfigPath()` | Spec requires inline (AC-US4-03) |
| `crawl-worker/sources/vendor-org-discovery.js` | Add inline `FRAMEWORK_PLUGIN_RE` test to existing regex-based `isAgentConfigPath()` check | Spec requires inline (AC-US4-04); this file already uses regex-based detection |

### C4: Cleanup Script (`scripts/cleanup-framework-plugins.ts`)

A one-time Prisma script to remove existing misclassified entries.

**Location**: `scripts/cleanup-framework-plugins.ts`

**Algorithm**:
```
1. Find all Submissions where skillPath matches FRAMEWORK_PLUGIN_RE
   SELECT * FROM Submission WHERE skillPath ~ 'plugins/specweave[^/]*/skills/'

2. For each matching submission:
   a. If state != REJECTED:
      - Update state to REJECTED
      - Create SubmissionStateEvent {
          fromState: current state,
          toState: REJECTED,
          trigger: "framework_plugin",
          actor: "system",
          actorType: "system",
          metadata: { reason: "Framework plugin skill -- not a community contribution" }
        }
   b. If skillId is set:
      - Record the skillId for deletion

3. Delete all Skill rows by collected skillIds
   (CASCADE: SkillVersion, ScanResult, etc. follow FK constraints)

4. Log summary: N submissions rejected, M skills deleted

5. Idempotency: submissions already in REJECTED state with trigger "framework_plugin"
   are skipped. Skills already deleted produce 0-count deletes.
```

**Data flow**:

```
+--------------------------------------------------------------+
|                  cleanup-framework-plugins.ts                 |
|                                                               |
|  1. Query Submissions                                         |
|     WHERE skillPath LIKE 'plugins/specweave%/skills/%'        |
|                                                               |
|  2. For non-REJECTED submissions:                             |
|     +-------------------------+  +-------------------------+  |
|     | UPDATE Submission       |  | INSERT StateEvent       |  |
|     |   state = REJECTED      |  |   trigger = "framework  |  |
|     |                         |  |     _plugin"            |  |
|     +-------------------------+  +-------------------------+  |
|                                                               |
|  3. For linked Skills:                                        |
|     +-------------------------+                               |
|     | DELETE FROM Skill       |                               |
|     |   WHERE id IN (...)     |                               |
|     +-------------------------+                               |
|                                                               |
|  4. Log: "Rejected N submissions, deleted M skills"           |
+--------------------------------------------------------------+
```

**Execution**: Run via `npx tsx scripts/cleanup-framework-plugins.ts` with DATABASE_URL set. Must be run after the filter code is deployed to prevent re-ingestion.

### C5: Test Updates

**5a. `src/lib/__tests__/skill-path-validation.test.ts`** -- extend with new test suites:

- `describe("isFrameworkPluginPath")` -- covers AC-US1-01 through AC-US1-03:
  - Rejects `plugins/specweave/skills/pm/SKILL.md`
  - Rejects `plugins/specweave-frontend/skills/nextjs/SKILL.md` (variant prefix)
  - Accepts `plugins/community-tool/skills/foo/SKILL.md` (non-specweave)
  - Accepts `plugins/specweave-frontend/commands/SKILL.md` (commands, not skills)
  - Edge cases: empty string, backslashes, leading slashes

- `describe("frameworkPluginRejectionReason")` -- covers AC-US1-04:
  - Returns human-readable string containing "framework plugin"

- `describe("shouldRejectSkillPath")` -- covers AC-US2-01 through AC-US2-03:
  - Rejects `.claude/skills/foo/SKILL.md` (agent-config still works)
  - Rejects `plugins/specweave/skills/do/SKILL.md` (framework-plugin works)
  - Accepts `skills/frontend/SKILL.md` (legitimate path)

- Update existing test at line 127: the `isAgentConfigPath("plugins/specweave/skills/do/SKILL.md")` assertion stays `false` (it only checks agent config dirs), but add a complementary `shouldRejectSkillPath` test that returns `true` for the same path.

**5b. `src/lib/__tests__/scanner-discovery.test.ts`** -- this test uses `plugins/specweave-frontend/skills/` and `plugins/specweave-github/skills/` paths as mock data. These paths will now be rejected by `shouldRejectSkillPath()`. Fix: change mock paths to non-specweave names (e.g., `plugins/community-frontend/skills/`).

**5c. `src/lib/queue/__tests__/multi-skill-expand.test.ts`** -- lines 77-79 use `plugins/specweave/skills/{pm,architect,do}/SKILL.md` as test data. After the filter is deployed, these would be rejected before reaching the expand step. Fix: change to non-specweave paths (e.g., `plugins/my-plugin/skills/pm/SKILL.md`).

## Deployment Sequence

The order matters to prevent re-ingestion of cleaned-up entries:

```
1. Deploy filter code   (TS platform + JS crawl-workers)
   -- New submissions with framework plugin paths are blocked
2. Run cleanup script   (npx tsx scripts/cleanup-framework-plugins.ts)
   -- Existing misclassified entries are cleaned
3. Verify               (query DB for remaining framework plugin skills)
```

If cleanup runs before deployment, crawl-workers could re-ingest the cleaned entries before the filter is live. Deploying first ensures the gate is up before the cleanup.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Regex too broad (catches non-specweave plugins) | Legitimate skills rejected | Regex is SpecWeave-specific: `specweave[^/]*` -- only matches `specweave`, `specweave-frontend`, etc. |
| Regex too narrow (misses variants) | Framework skills leak through | The character class `[^/]*` matches any suffix up to a path separator, covering all known variants |
| Crawl-worker inline copies drift from canonical TS | Silent filter gaps | Comment in each inline copy references the canonical source file. Deploy script copies to all 3 VMs. |
| Cleanup script deletes Skills with active installs | Users lose installed skills | Installed skills live in user project dirs, not the DB. DB Skill rows are marketplace listings only. |
| FK cascade on Skill delete removes SkillVersion/ScanResult | Loss of audit data | These are derived data that will not be regenerated for rejected skills. Acceptable. |

## No Schema Changes

The cleanup script uses existing Prisma models and SubmissionState enum (REJECTED is already defined). No new columns, tables, or enums are needed. The `trigger: "framework_plugin"` string in SubmissionStateEvent is a free-text field, not an enum value.

## Out of Scope (Confirmed)

- Generic `plugins/*/skills/` filtering -- regex stays SpecWeave-specific
- KV cleanup -- skills are not in KV
- `plugins/specweave*/commands/` paths -- scanner only indexes SKILL.md
- UI changes
