# Implementation Plan: Queue Search, Observability & Admin Monitoring

## Overview

Enhance the admin panel with real database queries for submissions (replacing mock data), live dashboard statistics, and a dedicated submissions list page with search/filter/pagination.

## Architecture

### Components
- **Admin Submissions API** (`/api/v1/admin/submissions/route.ts`): Replace mock data with Prisma queries, add search/filter/pagination
- **Admin Stats API** (`/api/v1/admin/stats/route.ts`): Already exists with live DB queries
- **Dashboard Page** (`/admin/dashboard/page.tsx`): Replace hard-coded stats with live API data
- **Submissions List Page** (`/admin/submissions/page.tsx`): New page with search, filter, pagination

### Data Model
- Uses existing `Submission` model (no schema changes needed)
- Queries: `prisma.submission.findMany()` with `where`, `orderBy`, `skip`, `take`
- Count: `prisma.submission.count()` for pagination metadata

### API Contracts
- `GET /api/v1/admin/submissions?search=X&state=Y&page=1&limit=20&sort=createdAt:desc`: Paginated, filtered submission list
- `GET /api/v1/admin/stats`: Dashboard statistics (already exists)

## Technology Stack

- **Framework**: Next.js 15 App Router
- **ORM**: Prisma with PostgreSQL
- **Testing**: Vitest + React Testing Library

## Implementation Phases

### Phase 1: API Enhancement
- Replace mock submissions with Prisma queries
- Add search, state filter, pagination, and sort support
- Write API tests

### Phase 2: Dashboard Enhancement
- Fetch live stats from /api/v1/admin/stats
- Replace hard-coded stat cards with dynamic data
- Add state distribution display

### Phase 3: Submissions List Page
- Create /admin/submissions/page.tsx
- Add search input, state filter dropdown, pagination
- Write component tests

## Testing Strategy

- API route tests: mock Prisma, verify query params pass through correctly
- Component tests: mock fetch, verify UI renders search/filter/pagination
