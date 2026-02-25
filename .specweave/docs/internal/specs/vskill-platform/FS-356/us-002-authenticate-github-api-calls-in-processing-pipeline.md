---
id: US-002
feature: FS-356
title: Authenticate GitHub API Calls in Processing Pipeline
status: complete
priority: P1
created: 2026-02-25
project: vskill-platform
---
# US-002: Authenticate GitHub API Calls in Processing Pipeline

**Feature**: [FS-356](./FEATURE.md)

platform operator
**I want** the processing pipeline to use authenticated GitHub API calls
**So that** the rate limit increases from 60 req/hr (unauthenticated) to 5000 req/hr (authenticated), preventing 403 errors during high-volume processing

---

## Acceptance Criteria

- [x] **AC-US2-01**: `handleSubmissionQueue` in `consumer.ts` reads `GITHUB_TOKEN` from worker `env` and passes it to `processSubmission` via a new `githubToken` option field
- [x] **AC-US2-02**: `ProcessSubmissionOptions` interface gains an optional `githubToken?: string` field
- [x] **AC-US2-03**: `processSubmission` passes `githubToken` to `fetchRepoFiles(repoUrl, skillPath, githubToken)` calls (both vendor and non-vendor paths)
- [x] **AC-US2-04**: `fetchRepoFiles` accepts an optional `token` parameter and includes `Authorization: Bearer <token>` header on all `raw.githubusercontent.com` fetches and GitHub API calls when token is provided
- [x] **AC-US2-05**: `resolveCommitSha` in `github-permalink.ts` accepts an optional `token` parameter and includes `Authorization: Bearer <token>` header when provided
- [x] **AC-US2-06**: `processSubmission` passes `githubToken` to `resolveCommitSha(owner, repo, "HEAD", token)` call
- [x] **AC-US2-07**: When no token is provided (e.g. direct API route calls), all functions fall back to unauthenticated requests (backward-compatible)
- [x] **AC-US2-08**: `GITHUB_TOKEN` env binding is declared in the `handleSubmissionQueue` env type (optional string)

---

## Implementation

**Increment**: [0356-scale-queue-throughput](../../../../../increments/0356-scale-queue-throughput/spec.md)

