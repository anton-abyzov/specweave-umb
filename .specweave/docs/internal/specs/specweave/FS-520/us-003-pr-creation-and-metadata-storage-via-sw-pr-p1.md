---
id: US-003
feature: FS-520
title: "PR Creation and Metadata Storage via sw:pr (P1)"
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As a** developer finishing increment work."
project: specweave
external:
  github:
    issue: 1564
    url: https://github.com/anton-abyzov/specweave/issues/1564
---

# US-003: PR Creation and Metadata Storage via sw:pr (P1)

**Feature**: [FS-520](./FEATURE.md)

**As a** developer finishing increment work
**I want** a `sw:pr` skill that pushes my branch and creates a pull request with an auto-generated description
**So that** my work enters the review process with full context from spec.md

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given quality gates have passed in `sw:done`, when `sw:pr` is invoked (Step 8.5), then the current branch is pushed to the remote with upstream tracking (`git push -u origin {branch}`)
- [x] **AC-US3-02**: Given the branch is pushed, when `sw:pr` creates a PR via `gh pr create`, then the PR title is the increment title from spec.md frontmatter and the PR body contains a summary section auto-generated from spec.md user stories and acceptance criteria
- [x] **AC-US3-03**: Given the PR is created successfully, when `sw:pr` updates metadata, then a `PrRef` object is appended to the `prRefs` array in `metadata.json` via an `addPrRef` helper on MetadataManager
- [x] **AC-US3-04**: Given PR creation fails (e.g., `gh` not authenticated, network error), when `sw:pr` handles the error, then a warning is logged but increment closure is NOT blocked
- [x] **AC-US3-05**: Given an umbrella workspace with multiple touched repos, when `sw:pr` runs, then it creates a separate branch and PR in each touched repo, continuing with remaining repos if one fails, and stores all `PrRef` entries in the increment metadata
- [x] **AC-US3-06**: Given a `getPrRefs` helper on MetadataManager, when called with an increment ID, then it returns the `prRefs` array from metadata (empty array if none)

---

## Implementation

**Increment**: [0520-pr-based-increment-closure](../../../../../increments/0520-pr-based-increment-closure/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-006**: Add addPrRef and getPrRefs helpers to MetadataManager
- [x] **T-007**: Create sw:pr SKILL.md — pre-flight checks and single-repo PR creation
- [x] **T-008**: Add PR body generation detail to sw:pr SKILL.md
- [x] **T-009**: Add multi-repo (umbrella) flow to sw:pr SKILL.md
- [x] **T-010**: Add Step 8.5 (PR Creation) to sw:done SKILL.md
