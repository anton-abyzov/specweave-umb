# Implementation Plan: Community Problem Reporting

## Overview

Add a ProblemReport model and supporting API + UI to allow registered users to report bugs, feature requests, content issues, and general feedback. The feature reuses existing auth (requireUser), rate-limit, and email infrastructure. It is entirely separate from the SecurityReport model.

## Architecture

### Components

- **ProblemReport Prisma model**: New model with enums ProblemReportType and ProblemReportStatus
- **POST /api/v1/problem-reports**: Create report (user auth required)
- **GET /api/v1/problem-reports/mine**: List user's own reports (user auth required)
- **ReportProblemModal**: Client component -- modal form on skill detail page
- **/report page**: Standalone report form with optional skill selector
- **/report/my-reports page**: List of user's submitted reports with status tracking
- **Admin email notification**: Best-effort email on new report via existing email infrastructure

### Data Model

```prisma
enum ProblemReportType {
  BUG
  FEATURE_REQUEST
  CONTENT_ISSUE
  OTHER
}

enum ProblemReportStatus {
  OPEN
  IN_REVIEW
  RESOLVED
  CLOSED
}

model ProblemReport {
  id          String              @id @default(cuid())
  userId      String
  user        User                @relation(fields: [userId], references: [id], onDelete: Cascade)
  skillId     String?
  skill       Skill?              @relation(fields: [skillId], references: [id], onDelete: SetNull)
  type        ProblemReportType
  title       String              // max 200 chars (validated in API)
  description String              // max 5000 chars (validated in API)
  status      ProblemReportStatus @default(OPEN)

  createdAt   DateTime            @default(now())
  updatedAt   DateTime            @updatedAt

  @@index([userId])
  @@index([skillId])
  @@index([status])
  @@index([createdAt(sort: Desc)])
}
```

Relation additions:
- User: `problemReports ProblemReport[]`
- Skill: `problemReports ProblemReport[]`

### API Contracts

**POST /api/v1/problem-reports**
- Auth: `requireUser` (vskill_access cookie)
- Rate limit: 10/hour per user
- Request body:
  ```json
  {
    "skillName": "optional-skill-name",
    "type": "BUG | FEATURE_REQUEST | CONTENT_ISSUE | OTHER",
    "title": "string (1-200 chars)",
    "description": "string (1-5000 chars)"
  }
  ```
- Response 201: `{ "report": { "id", "type", "title", "status", "createdAt" } }`
- Resolves skillName to skillId internally (null if not found or not provided)

**GET /api/v1/problem-reports/mine**
- Auth: `requireUser`
- Query params: `page` (default 1), `limit` (default 20, max 50)
- Response 200:
  ```json
  {
    "reports": [{ "id", "type", "title", "skillName", "status", "createdAt" }],
    "total": 42,
    "page": 1,
    "limit": 20
  }
  ```

## Technology Stack

- **Framework**: Next.js 15 App Router (existing)
- **ORM**: Prisma (existing)
- **Auth**: requireUser middleware with JWT cookie (existing)
- **Rate Limiting**: RATE_LIMIT_KV (existing)
- **Email**: Resend API (or existing email infrastructure)
- **UI**: Server + Client components, inline styles (existing pattern), Geist Mono

**Architecture Decisions**:
- **Separate model from SecurityReport**: SecurityReport is for security concerns (malware, typosquatting) with IP hashing and public submission. ProblemReport is for authenticated user feedback -- different trust model and lifecycle.
- **skillName in API, skillId in DB**: API accepts skill name (user-facing), resolves to skillId internally for referential integrity.
- **No admin dashboard in this increment**: Keep scope focused. Admin can query DB directly or through future increment.

## Implementation Phases

### Phase 1: Data Layer (T-001 to T-003)
- Add Prisma model + enums + migration
- Create API route for POST with validation and rate limiting
- Create API route for GET /mine with pagination

### Phase 2: Core UI (T-004 to T-006)
- ReportProblemModal client component on skill detail page
- Standalone /report page with skill selector
- My Reports page with status tracking

### Phase 3: Notifications (T-007)
- Admin email notification on new report

## Testing Strategy

- TDD mode: Write failing tests first, then implement
- API routes: Vitest unit tests with mocked Prisma and auth
- Client components: Basic render tests
- Coverage target: 80%

## Technical Challenges

### Challenge 1: Modal on Server-Rendered Skill Page
**Solution**: ReportProblemModal is a "use client" component imported into the server-rendered skill detail page. It manages its own open/close state and fetches user auth status client-side.
**Risk**: Low -- same pattern used by UserNav component already.

### Challenge 2: Skill Selector on Standalone Page
**Solution**: Fetch published skills via existing /api/v1/skills endpoint with minimal fields. Use a simple dropdown with search/filter.
**Risk**: Low -- skills list is small enough for client-side filtering.
