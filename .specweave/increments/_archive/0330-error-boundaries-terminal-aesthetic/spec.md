# 0330 — Error Boundaries & Terminal Aesthetic Error Pages

## Problem
Users see Cloudflare's raw Error 1101 "Worker threw exception" page when unhandled errors occur. No global error boundaries exist — no `global-error.tsx`, `error.tsx`, or `not-found.tsx`. The existing `/auth/error` page is functional but visually plain.

## Solution
Add multiple defensive error-handling layers and make all error pages beautiful with the app's terminal/monospace aesthetic.

## User Stories

### US-001: Global Error Boundary
As a user, I want to see a beautiful error page instead of Cloudflare's raw error when something crashes, so I can understand what happened and retry.

**Acceptance Criteria:**
- [x] AC-US1-01: `global-error.tsx` exists and catches errors above the root layout
- [x] AC-US1-02: Includes own `<html>` + `<body>` tags (Next.js requirement)
- [x] AC-US1-03: Terminal aesthetic with monospace font, CSS variables
- [x] AC-US1-04: "Try again" and "Go home" buttons

### US-002: Route-Level Error Boundary
As a user, I want route errors to show a styled error page within the app's layout.

**Acceptance Criteria:**
- [x] AC-US2-01: `error.tsx` exists at app root, renders inside root layout
- [x] AC-US2-02: Terminal aesthetic matching the app design
- [x] AC-US2-03: Reset/retry button

### US-003: 404 Page
As a user, I want a styled 404 page when I visit a non-existent URL.

**Acceptance Criteria:**
- [x] AC-US3-01: `not-found.tsx` exists with terminal aesthetic
- [x] AC-US3-02: Shows helpful navigation (home, skills, submit)

### US-004: Beautiful Auth Error Page
As a user, I want the login error page to look polished and informative.

**Acceptance Criteria:**
- [x] AC-US4-01: Redesigned with terminal-style error display
- [x] AC-US4-02: Includes `oauth_init_failed` error reason
- [x] AC-US4-03: Visual step indicator showing where the flow failed
- [x] AC-US4-04: "Try again" and "Go home" buttons

### US-005: Hardened OAuth Callback
As a developer, I want the OAuth catch block to never itself throw.

**Acceptance Criteria:**
- [x] AC-US5-01: Secondary try-catch around redirect in catch block
- [x] AC-US5-02: Fallback HTML response if redirect fails
