---
increment: 0563-vskill-studio-tests-params-integration
title: "vSkill Studio Tests Panel: Tab Filter, Parameter Store, Integration UX, and AI Generation Fixes"
status: active
priority: P1
type: feature
created: 2026-03-18
---

# vSkill Studio Tests Panel: Tab Filter, Parameter Store, Integration UX, and AI Generation Fixes

## Problem Statement

The vSkill Studio Tests panel has four related issues that degrade usability for skill developers working with integration tests and credentials. A critical tab filter bug locks users out of the panel, there is no UI to manage credential parameters, the New Test Case modal lacks integration test fields, and AI test generation ignores the user's selected model.

## Goals

- Fix the tab filter empty-state bug so users can always switch between test type tabs
- Provide a UI-based parameter store for managing credentials and config values in .env.local
- Expose integration test fields (type, requiredCredentials, requirements) in the test case creation and editing UI
- Forward the user-selected model to the generate-evals endpoint and support integration test generation

## User Stories

### US-001: Fix Tab Filter Empty State Bug
**Project**: vskill
**As a** skill developer
**I want** to switch between All/Unit/Integration tabs without losing the panel
**So that** I can browse tests by type without getting locked into an unrecoverable empty state

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the Tests panel has unit tests but no integration tests, when I click the "Integration" tab, then an inline message "No integration tests" is shown within the test list area while tabs remain visible and clickable
- [x] **AC-US1-02**: Given the Tests panel shows the inline "No integration tests" message, when I click the "All" tab, then the full list of unit tests is displayed
- [x] **AC-US1-03**: Given the evals file has zero test cases of any type, when the Tests panel loads, then the full "No test cases yet" empty state with Create/Generate buttons is shown
- [x] **AC-US1-04**: Given the evals file is null or invalid, when the Tests panel loads, then the validation error empty state is shown with the error message

### US-002: Parameter Store UI for Credentials and Config
**Project**: vskill
**As a** skill developer
**I want** to view and set credential values and config parameters from within Studio
**So that** I can configure integration test dependencies without manually editing .env.local files

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a skill with integration tests that declare requiredCredentials, when I open the parameter store UI, then each credential is listed with its name and a status badge (ready/missing)
- [x] **AC-US2-02**: Given a credential with status "ready", when it is displayed in the parameter store, then its value is masked with a toggle to reveal
- [x] **AC-US2-03**: Given I enter a value for a credential key and click Save, when the POST request completes, then the value is written to .env.local in the skill directory and the status badge updates to "ready"
- [x] **AC-US2-04**: Given a credential key already exists in .env.local, when I save a new value for that key, then the existing value is replaced (upsert behavior)
- [x] **AC-US2-05**: Given I add a new custom parameter key-value pair, when I save it, then it is appended to .env.local and appears in the parameter list

### US-003: Integration Test Type UX in Test Case Modal and Detail View
**Project**: vskill
**As a** skill developer
**I want** to set a test case's type to "integration" and configure requiredCredentials and requirements from the UI
**So that** I can create and edit integration test cases without manually editing evals.json

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given I open the New Test Case modal, when I toggle the test type to "integration", then additional fields for requiredCredentials and requirements appear below the type selector
- [x] **AC-US3-02**: Given I add credential names in the requiredCredentials field of the modal, when I save the test case, then the saved EvalCase includes testType "integration" and the requiredCredentials array
- [x] **AC-US3-03**: Given I view an existing test case in the detail view, when the case has testType "integration", then I can edit the testType, requiredCredentials, and requirements fields inline
- [x] **AC-US3-04**: Given I change an existing test case's type from "integration" to "unit", when I save, then the requiredCredentials and requirements fields are removed from the saved EvalCase

### US-004: AI Test Generation Respects Selected Model and Supports Integration Tests
**Project**: vskill
**As a** skill developer
**I want** AI test generation to use the model I selected in the config panel and offer an integration test generation option
**So that** I can generate tests with my preferred model and create integration test cases via AI

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given I have selected a specific provider and model in the Studio config panel, when I click "Generate with AI", then the generate-evals POST request includes the provider and model from my selection
- [x] **AC-US4-02**: Given the generate-evals endpoint receives provider and model in the request body, when it creates the LLM client, then it uses the provided overrides instead of the global getClient() default
- [x] **AC-US4-03**: Given I click "Generate Integration Tests", when the generation completes, then the generated test cases have testType "integration" and include requiredCredentials inferred from the skill content
- [x] **AC-US4-04**: Given I do not provide provider or model in the generate-evals request, when the endpoint processes the request, then it falls back to the current global overrides without error

## Out of Scope

- Remote/cloud credential storage (credentials stay in local .env.local only)
- Credential encryption at rest (Studio is a local development tool)
- Bulk import/export of parameters
- Integration test scheduling or CI pipeline integration
- Changes to the integration-runner.ts 5-phase execution logic

## Non-Functional Requirements

- **Compatibility**: All changes within existing React SPA (eval-ui) and Node HTTP server (eval-server)
- **Security**: Credential values must be masked by default in the UI; .env.local must be in .gitignore (existing ensureGitignore handles this)

## Edge Cases

- .env.local does not exist yet when saving first credential: writeCredential creates it
- Switching test type on existing case with populated requiredCredentials: fields cleared on switch to unit
- Tab filter with mix of types where one type has zero cases: inline empty message, not full empty state
- Generate-evals with invalid or unavailable model: endpoint returns error via existing error-classifier

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Tab filter fix changes empty state for existing unit-only users | 0.2 | 3 | 0.6 | Condition on allCases.length for true empty state, filtered length for inline message |
| Credential POST endpoint could overwrite unrelated .env.local entries | 0.1 | 5 | 0.5 | writeCredential uses line-level upsert, not full file overwrite |

## Technical Notes

- Issue 1 root cause: TestsPanel.tsx line 144 checks `cases.length === 0` (filtered array) instead of `allCases.length === 0`. Fix is a condition change plus inline empty message for filtered-empty.
- Issue 2 backend: credential-resolver.ts already has `writeCredential()` and `parseDotenv()`. Need a POST route and GET-all-params route in integration-routes.ts.
- Issue 3: NewCaseForm at line 1229 creates EvalCase without testType. Schema already supports testType, requiredCredentials, requirements, cleanup.
- Issue 4: generate-evals handler at api-routes.ts line 520 calls `getClient()` globally. Need to read provider/model from request body. `buildIntegrationEvalPrompt()` already exists in prompt-builder.ts.

## Success Metrics

- Zero user-reported incidents of tab filter lockout after fix
- Skill developers can configure all required credentials from Studio UI without touching .env.local manually
- Integration test cases can be created entirely from the UI with correct schema fields
- AI-generated tests use the model shown in the config panel
