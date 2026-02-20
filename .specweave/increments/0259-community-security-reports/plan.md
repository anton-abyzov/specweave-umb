# Plan: 0259 Community Security Reports

## Approach
Bottom-up: Database schema → API routes (TDD) → Frontend components (TDD) → Integration

## Phase 1: Database
- Add ReportType and ReportStatus enums to Prisma schema
- Add SecurityReport model with relations to Admin
- Generate and apply migration

## Phase 2: Public API (TDD)
- POST /api/v1/reports with rate limiting and validation
- GET /api/v1/reports with pagination

## Phase 3: Admin API (TDD)
- GET /api/v1/admin/reports with status filtering
- PATCH /api/v1/admin/reports/[id] with auto-block workflow

## Phase 4: Frontend
- ReportsTab: submission form + public reports feed
- Admin reports page: moderation table with status actions

## Phase 5: Integration
- Add "Reports" to admin sidebar nav
- Wire auto-block on confirmed malware resolution

## Risks
- Rate limiting depends on RATE_LIMIT_KV binding (already exists)
- Auto-block must reuse existing BlocklistEntry creation pattern
