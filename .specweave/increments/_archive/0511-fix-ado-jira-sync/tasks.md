---
increment: 0511-fix-ado-jira-sync
title: "Fix ADO/JIRA Sync Bugs"
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003]
  US-003: [T-004]
  US-004: [T-005]
  US-005: [T-006, T-007]
total_tasks: 7
completed_tasks: 7
---

# Tasks: Fix ADO/JIRA Sync Bugs

## User Story: US-001 - ADO Process-Aware State Transitions

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 2 total, 2 completed

---

### T-001: Add lazy-cached template detection to AdoAdapter

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Test Plan**:
- **Given** an `AdoAdapter` instance with valid org/project config
- **When** `getTemplate()` is called for the first time
- **Then** it calls the ADO project capabilities API and caches the result
- **And** subsequent calls return the cached value without a second API call
- **And** if the API call fails, `getTemplate()` returns `undefined` (no throw)

**Test Cases**:
1. **Unit**: `tests/unit/sync/ado-process-template.test.ts`
   - `getTemplateCallsCapabilitiesApiOnFirstInvocation()`: mock `apiRequest` to return Basic template, assert result is `{ template: 'Basic', ... }`
   - `getTemplateReturnsCachedResultOnSecondCall()`: assert `apiRequest` called exactly once across two `getTemplate()` calls
   - `getTemplateReturnsUndefinedOnApiFailure()`: mock `apiRequest` to throw, assert resolved value is `undefined`
   - `closeIssueUsesTemplateClosedStateForBasicProcess()`: mock `getTemplate` returning Basic, assert PATCH body contains `{ 'System.State': 'Done' }`
   - `closeIssueUsesConfigFallbackWhenTemplateUndefined()`: no template, config `closedState: 'Resolved'`, assert PATCH body has `Resolved`
   - `closeIssueUsesHardcodedClosedFallbackWhenNoConfig()`: no template, no config, assert PATCH body has `Closed`
   - **Coverage Target**: 95%

**Implementation**:
1. Add `private cachedTemplate?: AdoProcessTemplateInfo` field to `AdoAdapter`
2. Add module-level `TEMPLATE_CLOSED_MAP`: `{ Basic: 'Done', Agile: 'Closed', Scrum: 'Done', CMMI: 'Closed', SAFe: 'Closed' }`
3. Implement `private async getTemplate()`: calls GET `_apis/projects/{project}?includeCapabilities=true&api-version=7.1`, extracts `capabilities.processTemplate.templateName`, builds `AdoProcessTemplateInfo`, stores in `this.cachedTemplate`, returns `undefined` on failure (try/catch)
4. Modify `closeIssue()`: replace `this.config.closedState || 'Closed'` with template-aware resolution using `TEMPLATE_CLOSED_MAP`
5. Run: `npx vitest run tests/unit/sync/ado-process-template.test.ts`

---

### T-002: Wire cached template to mapStatusToAdo and reopenIssue

**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed

**Test Plan**:
- **Given** an `AdoAdapter` with a detected Basic process template
- **When** `mapStatusToAdo('completed')` is called
- **Then** it returns `'Done'` instead of `'Closed'`
- **And** when `reopenIssue()` is called on a Basic process adapter
- **Then** the PATCH request targets `'Doing'` instead of `'Active'`

**Test Cases**:
1. **Unit**: `tests/unit/sync/ado-process-template.test.ts`
   - `mapStatusToAdoCompletedReturnsTemplateTerminalState()`: Basic → `'Done'`, Agile → `'Closed'`
   - `mapStatusToAdoDoneReturnsTemplateTerminalState()`: Scrum → `'Done'`
   - `mapStatusToAdoFallsBackToClosedWhenNoTemplate()`: no template → `'Closed'`
   - `reopenIssueUsesTemplateActiveStateForBasic()`: Basic → PATCH contains `Doing`
   - `reopenIssueUsesTemplateActiveStateForAgile()`: Agile → PATCH contains `Active`
   - `reopenIssueUsesConfigFallbackWhenNoTemplate()`: no template, config `activeState: 'In Progress'` → PATCH contains `In Progress`
   - **Coverage Target**: 90%

**Implementation**:
1. Add module-level `TEMPLATE_ACTIVE_MAP`: `{ Basic: 'Doing', Agile: 'Active', Scrum: 'Committed', CMMI: 'Active', SAFe: 'Active' }`
2. Make `mapStatusToAdo()` async; update `await` at the `updateIssue()` call site
3. In `mapStatusToAdo()` for `'completed'`/`'done'` cases: call `await this.getTemplate()`, return `TEMPLATE_CLOSED_MAP[template.template] ?? 'Closed'` or fallback
4. In `reopenIssue()`: call `await this.getTemplate()`, use `TEMPLATE_ACTIVE_MAP[template?.template] ?? (this.config.activeState || 'Active')`
5. Run: `npx vitest run tests/unit/sync/ado-process-template.test.ts`

---

## User Story: US-002 - ADO Parent Work Item Linking

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 1 completed

---

### T-003: Add hierarchy-reverse parent link in createIssue

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Test Plan**:
- **Given** a `createIssue()` call where `feature.externalRef.id` is populated
- **When** the PATCH request is assembled
- **Then** the operations array contains a `System.LinkTypes.Hierarchy-Reverse` relation pointing to the parent work item URL
- **And** when `feature.externalRef` is absent, creation proceeds without error and no relation is added

**Test Cases**:
1. **Unit**: `tests/unit/sync/ado-parent-linking.test.ts`
   - `createIssueAddsHierarchyLinkWhenParentIdExists()`: feature `externalRef: { id: '42' }`, assert operations include `{ rel: 'System.LinkTypes.Hierarchy-Reverse', url: '...workitems/42' }`
   - `createIssueSkipsLinkWhenNoExternalRef()`: no `externalRef`, assert no relation op in operations array
   - `createIssueSkipsLinkWhenExternalRefIdIsEmpty()`: `externalRef: { id: '' }`, assert no relation op
   - **Coverage Target**: 90%

**Implementation**:
1. Add `externalRef?: { id: string; url?: string }` to `FeatureData` interface in `src/sync/engine.ts`
2. In `createIssue()`, after building base operations array, check `feature.externalRef?.id`
3. If truthy, push `{ op: 'add', path: '/relations/-', value: { rel: 'System.LinkTypes.Hierarchy-Reverse', url: \`https://dev.azure.com/${this.config.org}/${this.config.project}/_apis/wit/workitems/${feature.externalRef.id}\` } }` to operations
4. Run: `npx vitest run tests/unit/sync/ado-parent-linking.test.ts`

---

## User Story: US-003 - ADO Process-Aware Work Item Types

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 1 total, 1 completed

---

### T-004: Resolve correct work item type from template in createIssue

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Test Plan**:
- **Given** an `AdoAdapter` for a Basic process project
- **When** `createIssue()` is called
- **Then** the PATCH request URL targets the `Issue` work item type (not `User Story`)
- **And** given no template (detection fails), `createIssue()` falls back to `config.workItemType || 'User Story'`

**Test Cases**:
1. **Unit**: `tests/unit/sync/ado-process-template.test.ts`
   - `createIssueUsesIssueTypeForBasicProcess()`: mock `getTemplate` returning Basic, assert API URL contains `/Issue`
   - `createIssueUsesPBIForScrumProcess()`: Scrum template, assert URL contains `Product Backlog Item` (encoded)
   - `createIssueFallsBackToConfigWorkItemType()`: no template, config `workItemType: 'Task'`, assert URL contains `/Task`
   - `createIssueFallsBackToUserStoryWhenNoConfigAndNoTemplate()`: no template, no config, assert URL contains `User Story`
   - **Coverage Target**: 90%

**Implementation**:
1. Add module-level `TEMPLATE_WIT_MAP`: `{ Basic: 'Issue', Agile: 'User Story', Scrum: 'Product Backlog Item', CMMI: 'Requirement', SAFe: 'User Story' }`
2. In `createIssue()`, call `await this.getTemplate()`
3. Resolve: `const wit = template ? (TEMPLATE_WIT_MAP[template.template] ?? this.config.workItemType ?? 'User Story') : (this.config.workItemType ?? 'User Story')`
4. Use `wit` in the PATCH URL instead of the current hardcoded default
5. Run: `npx vitest run tests/unit/sync/ado-process-template.test.ts`

---

## User Story: US-004 - ADO Metadata Fallback for Closure

**Linked ACs**: AC-US4-01, AC-US4-02
**Tasks**: 1 total, 1 completed

---

### T-005: Add metadata.json fallback to closeAdoWorkItemsForUserStories

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed

**Test Plan**:
- **Given** user story files with no `external_tools.ado.id` and no `external_id`
- **When** `closeAdoWorkItemsForUserStories()` runs and `metadata.json` contains `ado.work_item_id: 99`
- **Then** the ADO work item with ID `99` is closed
- **And** `metadata.json` is read only once regardless of how many user stories are processed
- **And** when `external_tools.ado.id` is present, it takes priority over the metadata fallback

**Test Cases**:
1. **Unit**: `tests/unit/sync/sync-coordinator.test.ts` (extend existing describe block)
   - `closeAdoWorkItemsUsesMetadataFallbackWhenNoExternalId()`: no external IDs in US file, metadata has `ado.work_item_id: 99`, assert ADO close called with `99`
   - `closeAdoWorkItemsPrefersFrontmatterAdoIdOverMetadata()`: US file has `external_tools.ado.id: 10`, assert ADO close called with `10` not metadata value
   - `closeAdoWorkItemsReadsMetadataOnceForMultipleStories()`: 3 US files, assert `readFile` for metadata.json called exactly once
   - **Coverage Target**: 90%

**Implementation**:
1. In `closeAdoWorkItemsForUserStories()`, before the per-story loop, read metadata.json once: use the existing `readMetadataSafe` helper (or equivalent `readFile` + `JSON.parse` with try/catch)
2. Extract `const metadataAdoId: string | undefined = metadata?.ado?.work_item_id`
3. Update ID resolution: `const workItemId = usFile.external_tools?.ado?.id || usFile.external_id || metadataAdoId`
4. Run: `npx vitest run tests/unit/sync/sync-coordinator.test.ts`

---

## User Story: US-005 - JIRA Transition Warning on Skip

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Tasks**: 2 total, 2 completed

---

### T-006: Log warning when JIRA transition target is not found

**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-03 | **Status**: [x] completed

**Test Plan**:
- **Given** a `transitionIssue()` call where the available JIRA transitions do not include the target status
- **When** the transitions API response is processed
- **Then** `console.warn` is called with the issue key, target status, and list of available transition names
- **And** the function returns without throwing an error

**Test Cases**:
1. **Unit**: `tests/unit/sync/jira-sync-coordinator.test.ts` (extend existing describe block)
   - `transitionIssueWarnsWhenNoMatchingTransitionFound()`: mock transitions `[{ to: { name: 'In Progress' } }]`, call `transitionIssue('PROJ-1', 'Done')`, assert `console.warn` called with string containing `'PROJ-1'`, `'Done'`, and `'In Progress'`
   - `transitionIssueDoesNotThrowOnMissingTransition()`: same setup, assert function resolves without error
   - `transitionIssueDoesNotWarnWhenMatchingTransitionExists()`: mock includes `{ to: { name: 'Done' } }`, assert `console.warn` NOT called
   - **Coverage Target**: 90%

**Implementation**:
1. In `transitionIssue()` in `src/sync/providers/jira.ts`, locate the `find()` call for matching transition
2. After `find()`, if no match found: `console.warn(\`[SpecWeave] No matching JIRA transition for ${issueKey} to "${targetStatusName}". Available: ${data.transitions.map((t: any) => t.to.name).join(', ')}\`)`
3. Keep existing early `return` (no throw change)
4. Run: `npx vitest run tests/unit/sync/jira-sync-coordinator.test.ts`

---

### T-007: Make JIRA close status configurable via JiraAdapterConfig

**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed

**Test Plan**:
- **Given** a `JiraAdapter` configured with `closedStatus: 'Complete'`
- **When** `closeIssue()` is called
- **Then** `transitionIssue()` is invoked with `'Complete'` as the target status
- **And** when no `closedStatus` is configured, `transitionIssue()` is invoked with `'Done'`

**Test Cases**:
1. **Unit**: `tests/unit/sync/jira-sync-coordinator.test.ts` (extend existing describe block)
   - `closeIssueUsesConfiguredClosedStatus()`: adapter config `{ closedStatus: 'Complete' }`, assert `transitionIssue` called with `'Complete'`
   - `closeIssueDefaultsToDoneWhenNoClosedStatusInConfig()`: no `closedStatus`, assert `transitionIssue` called with `'Done'`
   - **Coverage Target**: 90%

**Implementation**:
1. Add `closedStatus?: string` to `JiraAdapterConfig` interface in `src/sync/providers/jira.ts`
2. Add `private readonly closedStatus?: string` field to `JiraAdapter`
3. In constructor, set `this.closedStatus = config.closedStatus`
4. In `closeIssue()`, replace hardcoded `'Done'` with `this.closedStatus || 'Done'`
5. Run: `npx vitest run tests/unit/sync/jira-sync-coordinator.test.ts`
