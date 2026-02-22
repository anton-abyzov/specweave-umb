# 0297: Dashboard Bug Fixes & Analytics Improvements

## Problem
1. Clicking a specific increment in the dashboard crashes the page (no ErrorBoundary)
2. Analytics page crashes intermittently (same root cause)
3. Navigate from increment list drops ?project= query param
4. Analytics documentation not in README/public docs/YouTube script

## User Stories

### US-001: [React ErrorBoundary for Dashboard Pages]
**As a** [dashboard user]
**I want** [the app to gracefully handle rendering errors]
**So that** [a single page crash does not kill the entire SPA]

#### Acceptance Criteria
- [x] **AC-US1-01**: A reusable ErrorBoundary component exists in components/ui/
- [x] **AC-US1-02**: The ErrorBoundary wraps Routes in App.tsx so all page crashes are caught
- [x] **AC-US1-03**: The error UI shows a friendly message with a Reload button
- [x] **AC-US1-04**: The ErrorBoundary resets on route navigation

### US-002: [Preserve Project Query Params in Navigation]
**As a** [multi-project dashboard user]
**I want** [the project param preserved when navigating between pages]
**So that** [I stay on the correct project context]

#### Acceptance Criteria
- [x] **AC-US2-01**: IncrementsPage navigate to detail preserves ?project= query param
- [x] **AC-US2-02**: All internal navigations via useNavigate preserve project context
- [x] **AC-US2-03**: The IncrementDetailPage correctly fetches data for the selected project

### US-003: [Wire Analytics Tracking into Execution Pipeline]
**As a** [SpecWeave user]
**I want** [all command/skill/agent invocations tracked in analytics]
**So that** [the dashboard shows accurate usage data including implicit calls]

#### Acceptance Criteria
- [x] **AC-US3-01**: Verify trackCommand is called for every command invocation
- [x] **AC-US3-02**: Verify trackSkill is called for every skill activation including implicit calls
- [x] **AC-US3-03**: Verify trackAgent is called for every agent spawn
- [x] **AC-US3-04**: Events include correct metadata (plugin, increment context, duration)

### US-004: [Update Docs with Analytics Dashboard Content]
**As a** [SpecWeave user reading documentation]
**I want** [to understand the analytics dashboard features]
**So that** [I can use them effectively]

#### Acceptance Criteria
- [x] **AC-US4-01**: README includes a Dashboard section describing analytics features
- [x] **AC-US4-02**: Public docs include analytics dashboard guide
- [x] **AC-US4-03**: Documentation explains multi-project support and local analytics

### US-005: [Update YouTube Script with Analytics Mention]
**As a** [potential SpecWeave user watching the tutorial]
**I want** [to see the analytics dashboard demonstrated]
**So that** [I understand the tool capabilities]

#### Acceptance Criteria
- [x] **AC-US5-01**: YouTube tutorial script mentions the analytics dashboard
- [x] **AC-US5-02**: Script includes a section on the dashboard command and what it shows
