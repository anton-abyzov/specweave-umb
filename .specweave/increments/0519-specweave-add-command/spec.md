---
increment: 0519-specweave-add-command
title: "specweave get CLI command"
status: active
priority: P1
type: feature
created: 2026-03-13
---

# specweave get CLI command

## Problem Statement

Adding repositories to a SpecWeave umbrella workspace requires manual steps: cloning with git, placing into the correct `repositories/{org}/{repo}/` directory, editing config.json to register in `childRepos`, and optionally running `specweave init`. There is no single command that handles "give me this repo and make it part of my workspace." The existing `migrate-to-umbrella --add-repo` creates NEW GitHub repos, but there is no command for cloning and registering EXISTING repos.

## Goals

- One command to clone and register any existing git repository into a SpecWeave workspace
- Idempotent behavior: safe to run multiple times without side effects
- Smart detection: parses GitHub shorthand, HTTPS URLs, SSH URLs, and local paths
- Works both inside and outside umbrella workspaces with appropriate behavior for each

## User Stories

### US-001: Source Argument Parsing
**Project**: specweave
**As a** developer
**I want** to pass a GitHub shorthand, full URL, or local path to `specweave get`
**So that** I do not need to remember different commands for different source formats

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given the argument `owner/repo`, when the source parser runs, then it returns `{ type: "github", owner: "owner", repo: "repo", cloneUrl: "https://github.com/owner/repo.git" }`
- [ ] **AC-US1-02**: Given the argument `https://github.com/org/my-repo`, when the source parser runs, then it returns `{ type: "github", owner: "org", repo: "my-repo", cloneUrl: "https://github.com/org/my-repo.git" }`
- [ ] **AC-US1-03**: Given the argument `git@github.com:org/repo.git`, when the source parser runs, then it returns `{ type: "github", owner: "org", repo: "repo", cloneUrl: "git@github.com:org/repo.git" }`
- [ ] **AC-US1-04**: Given the argument `./path/to/repo`, when the source parser runs, then it returns `{ type: "local", absolutePath: "<resolved absolute path>" }`
- [ ] **AC-US1-05**: Given a non-GitHub git URL like `https://gitlab.com/org/repo`, when the source parser runs, then it returns `{ type: "git", cloneUrl: "https://gitlab.com/org/repo", owner: "org", repo: "repo" }`

### US-002: Clone Repository
**Project**: specweave
**As a** developer
**I want** `specweave get` to clone a remote repository into the correct directory
**So that** I do not need to manually clone and place repos

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given an umbrella workspace and source `owner/repo`, when the clone runs, then the repo is cloned to `repositories/owner/repo/`
- [ ] **AC-US2-02**: Given a non-umbrella workspace and source `owner/repo`, when the clone runs, then the repo is cloned to `./repo/` in the current directory
- [ ] **AC-US2-03**: Given `--branch feature-x` is passed, when the clone runs, then the repo is cloned with `git clone --branch feature-x`
- [ ] **AC-US2-04**: Given the target directory `repositories/owner/repo/` already exists and contains a `.git` directory, when clone is attempted, then the clone step is skipped and the command prints "Repository already exists at <path>, skipping clone"
- [ ] **AC-US2-05**: Given git authentication fails during clone, when the error is caught, then the command prints an error message suggesting `gh auth login` or SSH key setup

### US-003: Register in Umbrella Config
**Project**: specweave
**As a** developer
**I want** the cloned repo to be automatically registered in the umbrella config
**So that** SpecWeave recognizes it as a child repo for increments and sync

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given an umbrella workspace and a cloned repo at `repositories/org/repo/`, when registration runs, then `config.json` has a new entry in `umbrella.childRepos` with `id`, `path`, `name`, and `prefix`
- [ ] **AC-US3-02**: Given `--prefix BE` is passed, when registration runs, then the child repo entry uses prefix `"BE"`
- [ ] **AC-US3-03**: Given no `--prefix` is passed, when registration runs, then the prefix defaults to the first 3 uppercase characters of the repo name
- [ ] **AC-US3-04**: Given the repo is already present in `umbrella.childRepos` (matching by id), when registration runs, then no duplicate entry is created and the command prints "Already registered in umbrella config"
- [ ] **AC-US3-05**: Given `--role backend` is passed, when registration runs, then the child repo entry includes `role: "backend"` in its config

### US-004: Add Command Orchestration
**Project**: specweave
**As a** developer
**I want** a single `specweave get <source>` command that orchestrates parsing, cloning, registration, and initialization
**So that** adding a repo is a one-step operation

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given the command `specweave get org/repo`, when executed in an umbrella workspace, then the repo is cloned to `repositories/org/repo/`, registered in config, and `specweave init` is run on it
- [ ] **AC-US4-02**: Given `--no-init` is passed, when the command runs, then `specweave init` is not executed on the cloned repo
- [ ] **AC-US4-03**: Given a local path `./my-service` that exists and has a `.git` directory, when `specweave get ./my-service` runs in an umbrella workspace, then the repo is registered in config without cloning (using `detectRepository()` to extract owner/repo)
- [ ] **AC-US4-04**: Given `--yes` is passed, when the command runs, then no confirmation prompts are shown
- [ ] **AC-US4-05**: Given the directory exists but is NOT registered in config, when `specweave get org/repo` runs, then the command skips clone but completes registration and init

### US-005: sw:add Skill Definition
**Project**: specweave
**As a** developer using Claude Code
**I want** an `sw:get` skill that activates on natural language triggers for adding repos
**So that** I can say "add repo" or "clone repo" instead of remembering the CLI syntax

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given the skill SKILL.md exists at `plugins/specweave/skills/get/SKILL.md`, when a user says "add repo owner/name", then the skill activates and delegates to `specweave get`
- [ ] **AC-US5-02**: Given a user says "add a feature" or "add a task", when intent detection runs, then the `sw:get` skill does NOT activate (those route to `sw:increment`)
- [ ] **AC-US5-03**: Given the SKILL.md `description` field, when parsed, then it contains trigger phrases: "add repo", "clone repo", "add github repo to umbrella", "register this repo"

## Out of Scope

- Creating NEW GitHub repositories (handled by `migrate-to-umbrella --add-repo`)
- Non-GitHub shorthand expansion (e.g., `gitlab:org/repo`); full URLs for other providers work via pass-through to `git clone`
- Automatic dependency installation after clone (e.g., `npm install`)
- Submodule or monorepo detection within cloned repos
- Interactive repo browser / selection from GitHub org listing
- PAT or token management; relies entirely on user's existing git credentials

## Technical Notes

### Dependencies
- Commander.js (existing CLI framework)
- `addRepoToUmbrella()` from `src/core/migration/umbrella-migrator.ts`
- `persistUmbrellaConfig()` from `src/core/migration/umbrella-migrator.ts`
- `execFileNoThrow()` from `src/utils/execFileNoThrow.ts`
- `detectRepository()` from `src/utils/git-utils.ts`

### Constraints
- All imports must use `.js` extensions (ESM with `--moduleResolution nodenext`)
- Command registered in `bin/specweave.js` following existing patterns

### Architecture Decisions
- **No PAT from config**: Relies on user's existing git credential setup (SSH keys, git credential manager). On auth failure, prints helpful message suggesting `gh auth login` or SSH key setup.
- **Auto-detect URL format**: SSH if source starts with `git@`, HTTPS if starts with `https://`, HTTPS default for `owner/repo` shorthand. Config `gitUrlFormat` not consulted.
- **Coexists with migrate-to-umbrella --add-repo**: Different semantics -- `add` clones existing repos, `migrate --add-repo` creates new ones. No deprecation.

### New Files
- `src/cli/helpers/get/source-parser.ts` -- parse source argument into structured type
- `src/cli/helpers/get/clone-repo.ts` -- git clone orchestration
- `src/cli/helpers/get/register-repo.ts` -- umbrella config registration
- `src/cli/commands/get.ts` -- Commander.js command handler
- `plugins/specweave/skills/get/SKILL.md` -- skill definition

### Modified Files
- `bin/specweave.js` -- register `get` command

## Non-Functional Requirements

- **Performance**: Clone time is network-bound; no SpecWeave overhead beyond config read/write
- **Compatibility**: Works on macOS, Linux, and Windows path formats; handles both `/` and `\` separators in local paths
- **Security**: No secrets stored or transmitted by the command; relies on OS-level git credential management

## Edge Cases

- **Repo exists but not registered**: Skip clone, register only, run init if needed
- **Repo registered but directory missing**: Re-clone to the registered path, skip re-registration
- **Trailing `.git` in URL**: Strip `.git` suffix when deriving repo name
- **Trailing slash in path**: Normalize `./path/to/repo/` to `./path/to/repo`
- **Non-existent local path**: Print error "Path does not exist: <path>"
- **Local path without `.git`**: Print error "Not a git repository: <path>"
- **Owner/repo with dots or hyphens**: `my-org/my.repo-name` parses correctly
- **Running outside any SpecWeave project**: Print error suggesting `specweave init` first

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Git auth failure for private repos | 0.4 | 3 | 1.2 | Helpful error messages guiding SSH/credential setup |
| Config corruption on concurrent writes | 0.1 | 7 | 0.7 | Use existing `persistUmbrellaConfig()` which handles atomic writes |
| Name collision with future `add` subcommands | 0.2 | 4 | 0.8 | `add` takes `<source>` positional arg; subcommands would need different names |

## Success Metrics

- `specweave get owner/repo` completes clone + registration in a single invocation
- Running `specweave get` twice on the same repo produces no errors and no duplicate config entries
- `sw:get` skill activates correctly on 4+ trigger phrases and does NOT activate on "add a feature/task"
