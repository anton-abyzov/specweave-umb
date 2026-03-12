---
id: US-002
feature: FS-501
title: Validate Repository Exists on GitHub (P1)
status: not_started
priority: P1
created: 2026-03-12
tldr: "**As a** developer."
project: specweave
external:
  github:
    issue: 1548
    url: https://github.com/anton-abyzov/specweave/issues/1548
---

# US-002: Validate Repository Exists on GitHub (P1)

**Feature**: [FS-501](./FEATURE.md)

**As a** developer
**I want** the tool to verify the repository exists before cloning
**So that** I get a clear error instead of a cryptic git failure

---

## Acceptance Criteria

- [ ] **AC-US2-01**: Given a valid owner/repo that exists on GitHub, when validation runs via GitHub API (`GET /repos/{owner}/{repo}`), then it returns success
- [ ] **AC-US2-02**: Given a repo that does not exist or the user lacks access, when the API returns 404, then the error message reads "Repository {owner}/{repo} not found or you don't have access. Check the repo name and ensure your token has 'repo' scope."
- [ ] **AC-US2-03**: Given no GH_TOKEN or GITHUB_TOKEN is available and the input is not SSH format, when validation runs, then the command exits with a missing-token error before attempting the API call

---

## Implementation

**Increment**: [0501-single-repo-clone](../../../../../increments/0501-single-repo-clone/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-003**: Implement and test GitHub API repo validation inside cloneSingleGitHubRepo()
