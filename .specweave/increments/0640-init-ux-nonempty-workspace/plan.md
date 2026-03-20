# Architecture Plan — 0640-init-ux-nonempty-workspace

## Overview

Three surgical changes to `specweave init` in `repositories/anton-abyzov/specweave/`:

1. **Non-empty folder detection** — new `workspace-setup.ts` module with 3-option menu + restructure/copy logic
2. **Root repo GitHub connection** — moved from config-update phase to early flow + auto-detection
3. **Repository input validation** — additive change to `parseRepoInput()` returning errors alongside parsed repos

All changes scoped to `src/cli/helpers/init/` and `src/cli/commands/init.ts`. No new dependencies.

## Architecture Decisions

### AD-1: Extract workspace-setup.ts for non-empty folder logic

**Decision**: New `workspace-setup.ts` module (~200-250 lines) rather than expanding init.ts.

**Rationale**: init.ts is 815 lines. The non-empty detection + 3-option menu + restructure + local-copy logic is a self-contained concern. Extracting keeps init.ts as orchestrator and puts testable domain logic in its own module.

**Alternatives rejected**:
- Inline in init.ts → rejected, approaches 1500-line limit
- Extend greenfield-detection.ts → rejected, that module answers "is it empty?"; this answers "what to do about non-empty?" with user interaction

### AD-2: Reorder init flow — root repo GitHub before child repos

**Decision**: Move "Connect workspace root to GitHub?" from the config-update phase (init.ts lines 452-476) to immediately after guard clauses, BEFORE `promptProjectSetup()`.

**Rationale**: Currently buried after scaffolding + config creation + repo cloning. Users who init in a folder with `.git` remote already have the answer — auto-detect it. For greenfield workspaces, naming the container before filling it follows natural mental flow.

**Auto-detection cascade** (spec §Org Detection Priority):
1. `detectProvider()` — parses `.git/config` → `owner`/`repo` (already exists)
2. `package.json` → `repository.url` or `repository` string field
3. `package.json` → `@scope/name` → scope as org
4. Interactive prompt fallback

### AD-3: Additive parseRepoInput return type (no breaking change)

**Decision**: Add `validateAndParseRepoInput()` alongside existing `parseRepoInput()`. New function returns `{ repos: ParsedRepo[], errors: RepoInputError[] }`. Existing function stays unchanged for backward compat.

**Rationale**: Changing `parseRepoInput()` return type would break all callers (used by `promptRepoUrls`, `promptRepoUrlsLoop`, `cloneReposIntoWorkspace`). Adding a parallel function lets new code use validation while existing code keeps working.

### AD-4: Restructure uses rename with EXDEV fallback

**Decision**: `fs.renameSync()` for same-filesystem moves (atomic per entry), catching `EXDEV` and falling back to `fs-extra` `copySync` + `rmSync` for cross-device edge cases.

**Rationale**: Same-filesystem rename is O(1) — just inode pointer update. Covers 99% of cases. EXDEV fallback handles rare Docker/mount scenarios.

## Component Design

### Component 1: workspace-setup.ts (NEW)
**Project**: specweave
**Location**: `src/cli/helpers/init/workspace-setup.ts`

Satisfies: AC-US1-01 through AC-US1-05, AC-US2-01 through AC-US2-04

```typescript
// --- Types ---

interface WorkspaceContentScan {
  hasSourceFiles: boolean;         // .ts, .js, .py, .go, etc. (reuse SOURCE_EXTENSIONS from greenfield-detection)
  hasPackageManager: boolean;      // package.json, go.mod, Cargo.toml, etc.
  hasGitRepo: boolean;             // .git/ exists
  hasUncommittedChanges: boolean;  // git status --porcelain non-empty
  fileCount: number;               // non-hidden file count at depth 0-1
  detectedLanguages: string[];     // from file extensions found
}

type MigrationChoice = 'start-empty' | 'restructure' | 'continue-in-place';

type StartEmptySubChoice = 'clone-github' | 'copy-local' | 'add-later';

interface OrgRepoDetection {
  org: string;
  repoName: string;
  source: 'git-remote' | 'package-json-repo' | 'package-json-scope' | 'directory-name' | 'user-input';
}

interface RestructureResult {
  moved: string[];       // paths successfully moved
  skipped: string[];     // paths intentionally skipped (.git, .specweave, etc.)
  errors: string[];      // paths that failed to move
  targetDir: string;     // repositories/{org}/{name}/
}

interface LocalCopyResult {
  copied: string[];
  skipped: string[];
  errors: string[];
  targetDir: string;
}

// --- Functions ---

// Scan target dir (depth 0-1 only for speed)
function scanWorkspaceContent(targetDir: string): WorkspaceContentScan;

// 3-option menu (AC-US1-01)
function promptMigrationChoice(
  scan: WorkspaceContentScan,
  language: SupportedLanguage,
  isCI: boolean,
): Promise<MigrationChoice>;

// Sub-menu for "Start empty" (AC-US1-02)
function promptStartEmptySubChoice(
  language: SupportedLanguage,
): Promise<StartEmptySubChoice>;

// Detect org/repo from git remote, package.json, directory name (AC-US1-04, AC-US1-05)
function detectOrgRepo(targetDir: string): OrgRepoDetection | null;

// Prompt for org/repo with auto-detect pre-fill (AC-US1-05)
function promptOrgRepo(
  targetDir: string,
  language: SupportedLanguage,
): Promise<OrgRepoDetection>;

// Move files into repositories/{org}/{name}/ (AC-US2-02)
function restructureIntoRepositories(
  targetDir: string,
  org: string,
  repoName: string,
): RestructureResult;

// Copy local path into repositories/{org}/{name}/ (AC-US1-03)
function copyLocalPathIntoRepositories(
  targetDir: string,
  sourcePath: string,
  org: string,
  repoName: string,
): LocalCopyResult;

// Show restructure warnings (AC-US2-01, AC-US2-03)
function showRestructureWarnings(scan: WorkspaceContentScan): void;
```

**Key implementation details**:

`scanWorkspaceContent()`:
- Imports `SOURCE_EXTENSIONS` and `SKIP_DIRS` from `greenfield-detection.ts` (DRY)
- Scans depth 0-1 only (fast, sufficient for detection)
- Checks `git status --porcelain` via `execFileNoThrowSync` for uncommitted changes

`promptMigrationChoice()`:
- Uses `@inquirer/prompts` `select` with 3 choices
- "Start empty (recommended)" — default, explains workspace model
- "Restructure here" — moves existing files into `repositories/{org}/{repo}/`
- "Continue in-place" — current behavior, non-destructive
- CI mode: returns `'continue-in-place'` immediately (non-destructive default)

`restructureIntoRepositories()` safety:
- **Skip list**: `.git/`, `.specweave/`, `node_modules/`, `repositories/`, hidden dotfiles
- **Uncommitted warning**: Checked by caller via `scan.hasUncommittedChanges` → `showRestructureWarnings()` + confirm (AC-US2-01)
- **Symlinks**: `fs.lstatSync()` on each entry — skip (don't move) symlinks, report in `skipped[]`
- **Atomic rename**: `fs.renameSync()` per top-level entry; catch `EXDEV` → fallback to `fs.copySync()` + `fs.rmSync()`
- **Target validation**: Fail if `repositories/{org}/{name}/` already exists (no silent overwrite)
- **Post-move warning**: Log warning about CI paths, relative imports, symlinks (AC-US2-03)

`copyLocalPathIntoRepositories()`:
- Resolves relative paths to absolute (`path.resolve()`)
- Rejects if source === targetDir (same directory check)
- Uses `fs.copySync()` with filter to exclude `.git/` directories
- Validates source exists and is a directory

### Component 2: root-repo-detection.ts (NEW)
**Project**: specweave
**Location**: `src/cli/helpers/init/root-repo-detection.ts`

Satisfies: AC-US3-01 through AC-US3-04

```typescript
interface RootRepoInfo {
  owner: string;
  repo: string;
  source: 'git-remote' | 'package-json' | 'user-input';
}

// Auto-detect root repo from git remote or package.json
function detectRootRepo(targetDir: string): RootRepoInfo | null;

// Interactive prompt with auto-detect pre-fill (AC-US3-01, AC-US3-02, AC-US3-03)
function promptRootRepoConnection(
  targetDir: string,
  language: SupportedLanguage,
  isCI: boolean,
): Promise<RootRepoInfo | null>;
```

**`detectRootRepo()` cascade**:
1. Call existing `detectProvider(targetDir)` — if GitHub provider, use `owner` + `repo`
2. Read `package.json` → `repository` field:
   - String: parse with HTTPS_RE / SSH_RE from repo-connect.ts
   - Object with `url`: parse url field
3. Read `package.json` → `name` field: extract `@scope/name` → scope as org, name as repo
4. Return null if nothing found

**`promptRootRepoConnection()` flow**:
1. CI/quick mode → call `detectRootRepo()`, return result or null (AC-US3-04)
2. Call `detectRootRepo()` for auto-detection
3. If found: display "Detected: {owner}/{repo}" + confirm (AC-US3-02)
4. If not found: "Connect workspace root to a GitHub repo? (optional)" with explanation text (AC-US3-01)
5. If user says yes: prompt owner + repo with `validateOwnerRepo()` validation (AC-US3-02)
6. If user says no: return null (AC-US3-03)

### Component 3: repo-connect.ts (MODIFIED)
**Project**: specweave
**Location**: `src/cli/helpers/init/repo-connect.ts`

Satisfies: AC-US4-01 through AC-US4-04

**New types and functions** (added alongside existing code):

```typescript
type RepoInputErrorType = 'org-only' | 'invalid-chars' | 'malformed-url' | 'empty';

interface RepoInputError {
  token: string;
  type: RepoInputErrorType;
  message: string;       // user-facing error message
  suggestion?: string;   // suggested correction
}

interface RepoInputValidation {
  repos: ParsedRepo[];
  errors: RepoInputError[];
}

// Validate + parse with error reporting (AC-US4-01, AC-US4-04)
function validateAndParseRepoInput(rawInput: string): RepoInputValidation;

// Validate single owner/repo string — for use as inquirer validate callback
function validateOwnerRepo(value: string): string | true;

// Format errors for console display (AC-US4-02, AC-US4-03)
function formatRepoInputErrors(errors: RepoInputError[]): string;
```

**`validateAndParseRepoInput()` token classification**:
- Matches SHORTHAND_RE, HTTPS_RE, or SSH_RE → add to `repos[]` (existing logic)
- Contains no `/` and matches `^[a-zA-Z0-9._-]+$` → `org-only` error (AC-US4-01)
  - Suggestion: `"Use '{token}/repo-name' or '{token}/*' to clone all repos"` (AC-US4-02)
- Contains `/` but doesn't match any pattern → `malformed-url` (AC-US4-03)
  - Message: `"Could not parse '{token}' — expected: org/repo, https://github.com/org/repo, or git@github.com:org/repo.git"`
- Everything else → `invalid-chars` with message showing allowed characters
- Empty/whitespace-only input → single `empty` error

**Backward compatibility**: Existing `parseRepoInput()` unchanged. New callers in `promptRepoUrlsLoop()` switch to `validateAndParseRepoInput()` and display errors via `formatRepoInputErrors()`.

### Component 4: init.ts (MODIFIED)
**Project**: specweave
**Location**: `src/cli/commands/init.ts`

**Surgical changes** (minimal diff to existing flow):

1. **New imports** at top:
   ```typescript
   import { scanWorkspaceContent, promptMigrationChoice, promptStartEmptySubChoice,
            restructureIntoRepositories, copyLocalPathIntoRepositories,
            showRestructureWarnings, promptOrgRepo } from '../helpers/init/workspace-setup.js';
   import { promptRootRepoConnection } from '../helpers/init/root-repo-detection.js';
   import { validateAndParseRepoInput, formatRepoInputErrors } from '../helpers/init/repo-connect.js';
   ```

2. **Replace non-empty message** (lines 210-215) with workspace setup flow:
   ```
   // OLD: console.log(chalk.gray(`ℹ Directory contains ${existingFiles.length} file(s)...`));
   // NEW:
   const scan = scanWorkspaceContent(targetDir);
   if (scan.hasSourceFiles || scan.hasPackageManager || scan.fileCount > 0) {
     const choice = await promptMigrationChoice(scan, language, isCI);
     if (choice === 'start-empty') {
       const subChoice = await promptStartEmptySubChoice(language);
       // handle clone-github → falls through to existing promptProjectSetup
       // handle copy-local → promptOrgRepo + copyLocalPathIntoRepositories
       // handle add-later → proceed normally
     } else if (choice === 'restructure') {
       showRestructureWarnings(scan);
       const confirmed = await confirm({ message: 'Proceed with restructure?', default: false });
       if (confirmed) {
         const orgRepo = await promptOrgRepo(targetDir, language);
         const result = restructureIntoRepositories(targetDir, orgRepo.org, orgRepo.repoName);
         // log result summary
       }
     }
     // choice === 'continue-in-place' → proceed as current behavior
   }
   ```

3. **Insert root repo prompt** after guard clauses (line ~238), BEFORE scaffold:
   ```typescript
   let rootRepoInfo: RootRepoInfo | null = null;
   if (!isCI && !continueExisting) {
     rootRepoInfo = await promptRootRepoConnection(targetDir, language, isCI);
   }
   ```

4. **Remove old root repo code** (lines 452-476) — replaced by early `rootRepoInfo`

5. **Apply rootRepoInfo to config** in config-update phase:
   ```typescript
   if (rootRepoInfo && config.workspace) {
     config.workspace.rootRepo = {
       github: { owner: rootRepoInfo.owner, repo: rootRepoInfo.repo },
     };
   }
   ```

6. **Update promptRepoUrlsLoop** to use validation:
   Replace `parseRepoInput(individualTokens.join(' '))` with `validateAndParseRepoInput()`, display errors.

### Component 5: index.ts barrel (MODIFIED)
**Project**: specweave
**Location**: `src/cli/helpers/init/index.ts`

**Add exports**:
```typescript
export {
  scanWorkspaceContent, promptMigrationChoice, promptStartEmptySubChoice,
  restructureIntoRepositories, copyLocalPathIntoRepositories,
  showRestructureWarnings, detectOrgRepo, promptOrgRepo,
  type WorkspaceContentScan, type MigrationChoice, type RestructureResult,
} from './workspace-setup.js';

export {
  detectRootRepo, promptRootRepoConnection,
  type RootRepoInfo,
} from './root-repo-detection.js';

export {
  validateAndParseRepoInput, validateOwnerRepo, formatRepoInputErrors,
  type RepoInputValidation, type RepoInputError,
} from './repo-connect.js';
```

## Revised Init Flow

```
STEP 1: Language selection
STEP 2: Path resolution (targetDir, projectName)
STEP 2a: Guard clauses (umbrella, suspicious path, nested .specweave)
STEP 2b: Reinit check (if .specweave/ exists → promptSmartReinit)
STEP 2c: NON-EMPTY DETECTION (NEW — replaces simple "ℹ Directory contains N file(s)" message)
  └─ scanWorkspaceContent(targetDir)
  └─ if non-empty:
     ├─ promptMigrationChoice() → start-empty | restructure | continue-in-place
     ├─ start-empty → promptStartEmptySubChoice() → clone/copy/add-later
     ├─ restructure → showRestructureWarnings() → confirm → promptOrgRepo() → restructureIntoRepositories()
     └─ continue-in-place → proceed (current behavior)
STEP 2d: ROOT REPO GITHUB (MOVED UP from config phase)
  └─ promptRootRepoConnection(targetDir, language, isCI)
  └─ Store rootRepoInfo for config phase
STEP 3: Scaffold (.specweave/ dirs, templates, minimal config)
STEP 4: Adapter detection
STEP 5: Provider detection (detectProvider from .git/config)
STEP 6: Workspace repo scan (scanWorkspaceRepos)
STEP 7: Project setup (promptProjectSetup → repo cloning with VALIDATED input)
STEP 8: Git init
STEP 9: Config finalization (apply rootRepoInfo, smart defaults, workspace config)
STEP 10: Plugins, hooks, living docs, summary banner
```

## File Move Safety (restructure + copy)

| Edge Case | Handling |
|-----------|----------|
| **Symlinks** | `lstatSync()` detects — added to `skipped[]`, not moved |
| **Cross-device** | Catch `EXDEV` from `renameSync()` → fallback to `copySync()` + `rmSync()` |
| **Skip list** | `.git/`, `.specweave/`, `node_modules/`, `repositories/`, all dotfiles/dotdirs |
| **Target exists** | Refuse — return error, don't overwrite |
| **Uncommitted changes** | Warning + confirm gate before proceeding (AC-US2-01) |
| **No .git directory** | Skip git-based org detection, prompt manually (AC-US1-05) |
| **Paths with spaces** | All fs operations use variables, not shell commands — safe by default |
| **Same dir as source** | `path.resolve()` comparison rejects source === targetDir |
| **Post-move** | Log warning: "CI paths, relative imports from outside may need manual updating" (AC-US2-03) |

## Testing Strategy

**Unit tests** (Vitest, mocked fs/prompts):
- `workspace-setup.test.ts`: scanWorkspaceContent accuracy, migration prompt choices, restructure moves + skip list + symlinks + EXDEV fallback, local copy + same-dir rejection
- `root-repo-detection.test.ts`: detection cascade (git remote → package.json → scope → null), prompt flow with/without auto-detect, CI mode skip
- `repo-connect-validation.test.ts`: org-only token → error, malformed URL → error, mixed valid+invalid → both parsed + errors, empty input → error

**Integration tests** (extend existing `init.test.ts`):
- Verify new flow ordering: non-empty detection before scaffold, root repo before child repos
- Verify `validateAndParseRepoInput()` integration in `promptRepoUrlsLoop()`

**Test file locations**:
- `tests/unit/cli/helpers/init/workspace-setup.test.ts`
- `tests/unit/cli/helpers/init/root-repo-detection.test.ts`
- `tests/unit/cli/helpers/init/repo-connect-validation.test.ts`

## Technical Challenges

### Challenge 1: Restructure atomicity
**Problem**: If move fails midway (disk full, permission denied), workspace is in partial state.
**Solution**: Move is per-top-level-entry. Partial restructure is acceptable — errors reported in `RestructureResult.errors[]`. No rollback attempted (rolling back could fail too). User can manually fix via `mv` commands.

### Challenge 2: parseRepoInput backward compatibility
**Problem**: Changing return type breaks all callers.
**Solution**: New `validateAndParseRepoInput()` function alongside existing `parseRepoInput()`. Only `promptRepoUrlsLoop()` switches to validated version. All other callers unchanged.

### Challenge 3: Root repo prompt timing
**Problem**: Root repo question needs git remote data, but provider detection happens later in flow.
**Solution**: `detectRootRepo()` calls `detectProvider()` independently — that function is pure (just reads `.git/config`), safe to call early. No dependency on scaffold being complete.
