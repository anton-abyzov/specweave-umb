---
increment: 0553-vskill-install-verification-scope
title: 'Fix vskill install: verification name collision + restore scope prompt'
type: bug
priority: P1
status: completed
created: 2026-03-17T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix vskill install: verification name collision + restore scope prompt

## Problem Statement

Two bugs degrade the `npx vskill i` experience:

1. **False rejection warnings**: The blocklist check API queries rejected submissions by `skillName` only, not scoped by `repoUrl`. When any author's skill with a given name was previously rejected, ALL skills with that name -- regardless of author or repository -- display a false "WARNING: Skill failed platform verification / Verification failed (REJECTED)" message. This erodes trust in the verification system.

2. **Missing scope selection**: The interactive prompt allowing users to choose between project-local and global installation was removed in commit `af41f86`. Users can no longer install skills globally through the interactive flow without knowing the `--global` flag.

## Goals

- Eliminate false-positive rejection warnings for skills that share a name but come from different repositories
- Restore user choice between project and global installation scope during interactive install
- Maintain backward compatibility with older vskill-platform deployments that do not yet handle `repoUrl`

## User Stories

### US-PLATFORM-001: Scope rejection query by repository URL
**Project**: vskill-platform
**As a** skill author
**I want** the blocklist check API to scope rejection lookups by both skill name and repository URL
**So that** my skill is not falsely flagged as rejected because a different author's skill with the same name was rejected

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a submission with `skillName: "skill-creator"` and `repoUrl: "https://github.com/alice/skill-creator"` in REJECTED state, when the API receives `GET /api/v1/blocklist/check?name=skill-creator&repoUrl=https://github.com/bob/skill-creator`, then the response has `rejected: false`
- [x] **AC-US1-02**: Given the same rejected submission, when the API receives `GET /api/v1/blocklist/check?name=skill-creator&repoUrl=https://github.com/alice/skill-creator`, then the response has `rejected: true` with the rejection details
- [x] **AC-US1-03**: Given the same rejected submission, when the API receives `GET /api/v1/blocklist/check?name=skill-creator` without a `repoUrl` parameter, then the response falls back to name-only matching and returns `rejected: true` (backward compatibility)
- [x] **AC-US1-04**: Given the rejection query adds a `repoUrl` WHERE clause, then the query uses the existing compound index `[repoUrl, skillName]` on the Submission table (no new index needed)

---

### US-VSKILL-001: Pass repoUrl to blocklist check API
**Project**: vskill
**As a** vskill CLI user
**I want** the install command to send the skill's repository URL when checking the blocklist
**So that** the server can accurately scope rejection lookups to my specific skill

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a skill being installed has a known `repoUrl`, when `checkInstallSafety` is called, then the HTTP request includes `repoUrl` as a query parameter
- [x] **AC-US2-02**: Given a skill being installed has no `repoUrl` (e.g., name-only registry install), when `checkInstallSafety` is called, then the HTTP request omits the `repoUrl` parameter (no empty string sent)
- [x] **AC-US2-03**: Given an older vskill-platform deployment that ignores the `repoUrl` parameter, when the client sends `repoUrl`, then the install proceeds normally with no errors (parameter is additive, not breaking)

---

### US-VSKILL-002: Restore project vs global scope prompt
**Project**: vskill
**As a** vskill CLI user
**I want** to be prompted to choose between project and global installation scope
**So that** I can install skills globally through the interactive flow without memorizing CLI flags

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the user runs `npx vskill i <skill>` in an interactive TTY without `--global` or `--cwd` flags, when the install options are prompted, then a "Installation scope" prompt appears with options "Project" (install in current project root) and "Global" (install in user home directory)
- [x] **AC-US3-02**: Given the user runs `npx vskill i <skill> --global`, when the install options are prompted, then the scope prompt is skipped and installation proceeds with global scope
- [x] **AC-US3-03**: Given the user runs `npx vskill i <skill> --cwd`, when the install options are prompted, then the scope prompt is skipped and installation proceeds with project scope
- [x] **AC-US3-04**: Given the user runs `npx vskill i <skill> --yes` (non-interactive mode), when the install executes, then the scope prompt is skipped and defaults to project scope

## Out of Scope

- Taint check scoping by `repoUrl` -- taint is intentionally author-level, not repo-scoped
- Blocklist entry lookups (the `findActiveBlocklistEntry` path already accepts `repoUrl`)
- Hash-only blocklist lookups (no `repoUrl` applicable)
- Migration of historical rejection data
- Changes to the `--global` or `--cwd` flag behavior themselves

## Technical Notes

### Dependencies
- `vskill-platform`: Prisma Submission model with existing compound index `[repoUrl, skillName]`
- `vskill`: `checkInstallSafety()` in `src/blocklist/blocklist.ts`, `promptInstallOptions()` in `src/commands/add.ts`

### Constraints
- `repoUrl` must be optional at every layer (API param, query WHERE clause, client function signature) for backward compatibility
- The scope prompt restoration must match the exact UX from before commit `af41f86`: `promptChoice` with "Project" and "Global" options, skipped when `--global` or `--cwd` is set

### Architecture Decisions
- Server-side: Add optional `repoUrl` to the rejection query WHERE clause only when the parameter is present; omit it otherwise (name-only fallback)
- Client-side: Thread `repoUrl` through `checkInstallSafety` as an optional parameter; callers pass it when available

## Non-Functional Requirements

- **Performance**: No regression -- the scoped rejection query hits the existing compound index
- **Compatibility**: Older vskill clients (without `repoUrl`) must continue to work against updated server; updated clients must work against older server
- **Security**: Scoping by `repoUrl` prevents cross-author information leakage where one author's rejection falsely taints another author's identically-named skill

## Edge Cases

- **Same name, different repos**: Two skills named "my-tool" from different repos -- only the rejected one shows warning
- **repoUrl absent on server**: Falls back to current name-only behavior (AC-US1-03)
- **repoUrl absent on client**: Omits param entirely, server falls back (AC-US2-02)
- **Non-TTY environment**: Scope prompt skipped, defaults to project (AC-US3-04)
- **Both --global and --cwd set**: Existing flag precedence applies (out of scope for this fix)

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Staggered deployment: client sends repoUrl, server ignores it | 0.3 | 2 | 0.6 | repoUrl is optional; server ignores unknown params gracefully |
| Compound index not covering the new query pattern | 0.1 | 3 | 0.3 | Verified: index `[repoUrl, skillName]` already exists on Submission |

## Success Metrics

- Zero false-positive rejection warnings for skills with distinct repoUrls
- Users presented with scope choice during interactive install (measurable via prompt display)
- No breaking changes for existing vskill or vskill-platform deployments
