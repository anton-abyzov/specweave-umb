# Implementation Plan: Build & Deploy verified-skill.com

## Overview

Two repositories already exist with working implementations:
- **vskill** (`repositories/anton-abyzov/vskill/`) — CLI npm package (v0.1.1, 2,855 LOC, 8 commands, 39 agents, Tier 1+2 scanner)
- **vskill-platform** (`repositories/anton-abyzov/vskill-platform/`) — Next.js 15 full-stack platform (34,404 LOC, 19 API routes, 11 Prisma models, admin dashboard, submission pipeline)

Both repos have Vitest configured but **zero tests written**. The primary work remaining is comprehensive test coverage, verification of all ACs, and fixing any issues found.

## Architecture

### Components
- **vskill CLI** (`@vskill/cli`): Node.js ESM CLI with commander.js, security scanner (42 patterns), 39-agent registry, lockfile management
- **vskill-platform** (`vskill-platform`): Next.js 15 App Router on Cloudflare Workers via @opennextjs/cloudflare, Neon PostgreSQL + Prisma, REST API, admin dashboard, submission pipeline

### Data Model
- 11 Prisma models: Submission, Skill, SkillVersion, ScanResult, Admin, RefreshToken, AgentCompat, EmailNotification, SubmissionJob, SubmissionStateEvent
- State machine: RECEIVED → TIER1_SCANNING → TIER2_SCANNING → AUTO_APPROVED/NEEDS_REVIEW → PUBLISHED

### API Contracts
- Public: GET /api/v1/skills, GET /api/v1/skills/:name, GET /api/v1/skills/:name/badge, POST /api/v1/submissions, GET /api/v1/submissions/:id
- Admin: POST /api/v1/auth/login, POST /api/v1/auth/refresh, GET /api/v1/admin/submissions, PATCH approve/reject, GET stats

## Implementation Phases

### Phase 1: CLI Unit Tests (vskill)
- Scanner patterns unit tests
- Agent registry unit tests
- CLI commands unit tests (mocked I/O)
- Lockfile unit tests

### Phase 2: Platform Unit Tests (vskill-platform)
- API route handler tests
- State machine transition tests
- Auth/JWT tests
- Scanner integration tests
- Data access layer tests

### Phase 3: Gap Fixes
- Fix any bugs found during testing
- Ensure all ACs are satisfied

## Testing Strategy

- **Unit tests**: Vitest for both repos (>80% coverage target)
- **Mocking**: vi.mock() for external dependencies (fs, git, network, Prisma)
- **Test files**: Colocated `*.test.ts` in same directory as source

## Technical Challenges

### Challenge 1: Cloudflare Workers Environment
**Solution**: Mock Prisma/Neon adapter in tests, test API logic independently
**Risk**: Low — pure function testing

### Challenge 2: Existing code without tests (brownfield testing)
**Solution**: Write tests that verify current behavior, fix bugs found
**Risk**: May uncover bugs in existing implementation
