# 0341: Search Performance & Reliability

## Problem
Production search (Cmd+K) on verified-skill.com is slow (574ms-6s), sends redundant requests, has race conditions, and misses substring matches.

## User Stories

### US-001: Race-free search with AbortController
**As a** user typing in the search palette
**I want** only the latest search results displayed
**So that** stale responses never overwrite fresh results

**ACs:**
- [x] AC-US1-01: AbortController cancels in-flight fetch when query changes
- [x] AC-US1-02: AbortError silently ignored (no error flash)
- [x] AC-US1-03: Loading state not reset in cleanup (no flash between queries)

### US-002: Reduced request volume with 300ms debounce
**As a** user typing quickly
**I want** search to wait 300ms after I stop typing
**So that** fewer unnecessary API requests are made

**ACs:**
- [x] AC-US2-01: Debounce increased from 150ms to 300ms
- [x] AC-US2-02: No fetch for queries < 2 characters

### US-003: Lean response payload
**As a** search consumer
**I want** only the fields I need in the response
**So that** payload is smaller and faster to parse

**ACs:**
- [x] AC-US3-01: Response trimmed from 18 to 8 fields (name, displayName, author, repoUrl, category, certTier, githubStars, highlight)
- [x] AC-US3-02: SearchResult/SkillSearchRow interfaces updated
- [x] AC-US3-03: SQL SELECT reduced to match

### US-004: Consolidated SQL queries
**As a** maintainer
**I want** a single parameterized SQL query
**So that** 4 duplicate branches are eliminated

**ACs:**
- [x] AC-US4-01: Prisma.sql fragment composition for tsquery expression
- [x] AC-US4-02: Dynamic WHERE clause for optional category filter
- [x] AC-US4-03: Single SQL template replaces 4 branches

### US-005: ILIKE fallback for substring matching
**As a** user searching for "ado"
**I want** results even when tsvector prefix match finds nothing
**So that** substring matches are not missed

**ACs:**
- [x] AC-US5-01: ILIKE fallback runs only when tsvector returns 0 results
- [x] AC-US5-02: LIKE special chars escaped (%, _, \)
- [x] AC-US5-03: Fallback results ordered by githubStars DESC
- [x] AC-US5-04: Case-insensitive highlight generated for fallback results

### US-006: Search timeout reduction
**As a** user
**I want** search to fail fast rather than hang
**So that** I get feedback within 8 seconds

**ACs:**
- [x] AC-US6-01: SEARCH_TIMEOUT_MS reduced from 20000 to 8000
