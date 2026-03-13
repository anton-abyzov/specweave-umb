# Spec: `specweave get` — Bulk Cloning (Pattern/Glob/Regex)

## Problem

`specweave get` currently clones one repository at a time (foreground). Users need to clone entire GitHub organizations or subsets matching a pattern in a single command — e.g., all `service-*` repos in an org.

The infrastructure already exists in `specweave init` (clone-worker, job-launcher, fetchGitHubRepos, selection-strategy). This increment wires it into `specweave get`.

---

## User Stories

### US-001: Glob pattern cloning

**As a** developer onboarding a new team workspace,
**I want to** run `specweave get "acme-corp/service-*"` to clone all repos matching a glob,
**So that** I don't need to run 30 individual `specweave get` commands.

**Acceptance Criteria:**
- [x] AC-US1-01: `specweave get "org/prefix-*"` detects glob pattern and enters bulk mode
- [x] AC-US1-02: GitHub org repos are fetched (up to 1000, paginated) and filtered by glob
- [x] AC-US1-03: Matching repos are queued in a background clone job via `launchCloneJob()`
- [x] AC-US1-04: User sees "Found N repos matching pattern-*. Launching background clone job..."
- [x] AC-US1-05: `specweave get "org/*"` clones all repos in org (null pattern = no filter)

### US-002: --all flag cloning

**As a** developer,
**I want to** run `specweave get --all acme-corp` to clone every repo in an org,
**So that** I can clone an entire organization without a wildcard expression.

**Acceptance Criteria:**
- [x] AC-US2-01: `specweave get --all acme-corp` treats source as org name and enters bulk mode
- [x] AC-US2-02: Combined with `--pattern "service-*"` acts as glob filter on the org

### US-003: Filtering options

**As a** developer,
**I want to** skip archived repos and forks when bulk cloning,
**So that** I only get active, first-party repositories.

**Acceptance Criteria:**
- [x] AC-US3-01: `--no-archived` filters out repos where `archived: true`
- [x] AC-US3-02: `--no-forks` filters out repos where `fork: true`
- [x] AC-US3-03: `--limit <n>` caps the number of repos fetched (default: 1000)

### US-004: Auth resolution

**As a** developer,
**I want** the command to automatically use my existing GitHub credentials,
**So that** I don't need to manually pass a token.

**Acceptance Criteria:**
- [x] AC-US4-01: Auth resolved from `GH_TOKEN` env var first
- [x] AC-US4-02: Falls back to `gh auth token` CLI
- [x] AC-US4-03: Helpful error if neither is available

### US-005: Single-repo backward compatibility

**As a** developer,
**I want** existing `specweave get owner/repo` behavior unchanged,
**So that** bulk mode doesn't break single-repo usage.

**Acceptance Criteria:**
- [x] AC-US5-01: Source without glob chars and no `--all` flag → single-repo foreground clone (existing path)
- [x] AC-US5-02: All existing options (`--branch`, `--prefix`, `--role`, `--no-init`) still work in single-repo mode
