# Implementation Plan: Admin Queue Actions & Trust Center Consolidation

## Overview

Three parallel workstreams: (1) add admin action buttons to the public queue page with new API endpoints, (2) create a unified Trust Center page at `/trust` that combines audits and blocklist content with tabbed navigation, (3) update site navigation and add redirects from old routes. All work is frontend-heavy with two small API additions.

## Architecture

### Components

- **TrustCenterPage** (`src/app/trust/page.tsx`): New top-level page with tab controller
- **TrustTabs** (`src/app/trust/TrustTabs.tsx`): Client component managing tab state via URL search params
- **VerifiedSkillsTab**: Extracted from existing `audits/page.tsx` - audit table with filters/sort/pagination
- **BlockedSkillsTab**: Extracted from existing `blocklist/page.tsx` - blocklist table with search/expand
- **ReportsTab**: Placeholder component for future community reports
- **AdminQueueActions** (`src/app/queue/AdminQueueActions.tsx`): Conditional admin action buttons for queue cards
- **useAdminStatus** (`src/app/hooks/useAdminStatus.ts`): Hook to detect admin role from `/api/v1/auth/me`

### Data Model

No new database tables needed. Two new submission state transitions:

- `DEQUEUED`: New state for submissions removed from queue by admin
- Reprioritize: Updates `updatedAt` timestamp to control processing order (or uses a new `priority` field if the queue consumer supports it)

**Decision**: Use `updatedAt` for priority since the queue consumer already processes by creation order - bumping to front means re-creating with a new timestamp. However, simpler approach: add a `priority` integer field (0=normal, 1=high) to Submission model if Prisma schema supports it, or use the existing re-enqueue endpoint.

### API Contracts

- `POST /api/v1/admin/submissions/:id/dequeue`
  - Auth: Admin JWT required
  - Response: `{ success: true, submission: { id, state: "DEQUEUED" } }`
  - Error: 401/403/404

- `POST /api/v1/admin/submissions/:id/reprioritize`
  - Auth: Admin JWT required
  - Body: `{ position: "front" | "back" }`
  - Response: `{ success: true, submission: { id, position } }`
  - Error: 401/403/404

### Route Changes

| Old Route | New Route | Method |
|-----------|-----------|--------|
| `/audits` | `/trust?tab=verified` | Redirect (308) |
| `/blocklist` | `/trust?tab=blocked` | Redirect (308) |
| (new) `/trust` | Trust Center page | Page |

### Navigation Updates

**Main nav** (layout.tsx): Replace "Audits" and "Blocklist" links with single "Trust Center" link to `/trust`

**Footer** (layout.tsx): Same consolidation

**MobileNav**: Replace "Audits" and "Blocklist" with "Trust Center"

## Technology Stack

- **Framework**: Next.js 15 (App Router)
- **UI**: Inline CSS-in-JS (project convention - no CSS modules or Tailwind)
- **State**: React useState + useSearchParams for tab state
- **Auth**: Existing JWT-based admin auth via localStorage
- **Testing**: Vitest + React Testing Library

**Architecture Decisions**:
- **Tabs via URL params, not route segments**: Using `/trust?tab=verified` instead of `/trust/verified` because the content is lightweight enough for a single page and URL params enable back-button/sharing while keeping the component tree simple.
- **Extract tab content as components, not pages**: The audits and blocklist content become standalone components imported by the Trust Center page. This avoids code duplication and makes the old route pages simple redirect stubs.
- **Admin detection via existing auth endpoint**: The `/api/v1/auth/me` endpoint already returns user data. We check for admin role there rather than adding a new endpoint. The queue page already calls this endpoint for auth checks.

## Implementation Phases

### Phase 1: Foundation (T-001 to T-003)
- Create `useAdminStatus` hook
- Build Trust Center page shell with tab navigation
- Extract audit/blocklist content into reusable components

### Phase 2: Core Functionality (T-004 to T-008)
- Implement admin queue actions (dequeue, reprioritize) UI + API
- Wire up Trust Center tabs with real content
- Add redirects from old routes

### Phase 3: Polish (T-009 to T-011)
- Update site navigation (navbar, footer, mobile nav)
- Add Reports placeholder tab
- Integration testing and verify redirects

## Testing Strategy

- **Unit tests**: useAdminStatus hook, tab state management, admin action handlers
- **Component tests**: TrustTabs renders correct tab content, AdminQueueActions shows/hides based on role
- **API tests**: Dequeue and reprioritize endpoints with auth checks
- **Integration**: Redirect verification, navigation link updates

TDD mode: Write tests first for hooks and API endpoints, test-after for UI components.

## Technical Challenges

### Challenge 1: Preserving filter/sort state across tab switches
**Solution**: Each tab component manages its own local state. When switching tabs, the component remounts but the URL param preserves which tab is active. No global state needed.
**Risk**: Low - standard React pattern.

### Challenge 2: Admin detection race condition on queue page
**Solution**: The `useAdminStatus` hook returns a loading state. Admin action buttons only render after the auth check completes. During loading, no buttons shown (same as non-admin experience).
**Risk**: Low - the queue page already does this auth check pattern.

### Challenge 3: Old URL bookmarks and external links
**Solution**: Next.js redirects in the old page files using `redirect()` from `next/navigation`. This handles both server-side and client-side navigation.
**Risk**: Low - standard Next.js pattern. Test with curl and browser.
