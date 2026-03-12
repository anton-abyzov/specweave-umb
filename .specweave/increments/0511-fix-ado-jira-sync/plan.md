# Architecture Plan: Fix ADO/JIRA Sync Bugs (0511)

## 1. Problem Summary

Five bugs in the ADO/JIRA sync layer cause incorrect state transitions, missing parent links, wrong work item types, missing metadata fallbacks, and silently swallowed transition failures. All bugs stem from the ADO adapter (`ado.ts`) and sync coordinator (`sync-coordinator.ts`) ignoring existing process template detection infrastructure, and the JIRA adapter (`jira.ts`) silently dropping transition mismatches.

## 2. Architecture Overview

### Affected Components

```
src/sync/providers/ado.ts         AdoAdapter class (ProviderAdapter impl)
src/sync/providers/jira.ts        JiraAdapter class (ProviderAdapter impl)
src/sync/sync-coordinator.ts      SyncCoordinator (closure orchestration)
src/integrations/ado/ado-client.ts AdoClient (existing detectProcessTemplate)
```

### Component Relationships

```
SyncCoordinator
  ├── closeJiraIssuesForUserStories()  ─── uses JiraClient (integration)
  ├── closeAdoWorkItemsForUserStories() ─── uses AdoClient (integration)
  └── reads metadata.json for ID fallback

SyncEngine
  ├── AdoAdapter  (ProviderAdapter)  ─── direct ADO REST API calls
  └── JiraAdapter (ProviderAdapter)  ─── direct JIRA REST API calls

AdoClient (integration layer)
  └── detectProcessTemplate()  ─── queries ADO project capabilities API
```

**Key constraint**: `AdoAdapter` and `AdoClient` are separate classes. `AdoAdapter` makes its own REST calls and does NOT import `AdoClient`. The template detection logic must be implemented directly in `AdoAdapter` using its own `apiRequest()` method, not by importing `AdoClient`.

## 3. Design Decisions

### DD-1: Inline Template Detection in AdoAdapter (not AdoClient import)

**Decision**: Implement a lightweight `getTemplate()` method directly in `AdoAdapter` that queries the same ADO project capabilities API endpoint as `AdoClient.detectProcessTemplate()`, but uses `AdoAdapter`'s own `apiRequest()` infrastructure.

**Rationale**: The `AdoAdapter` and `AdoClient` serve different architectural layers -- `AdoAdapter` is the sync engine's `ProviderAdapter`, while `AdoClient` is the integration layer used by importers and the sync coordinator. Coupling them would violate the adapter pattern boundary. The detection logic is ~15 lines and queries a single endpoint.

**Alternative rejected**: Importing `AdoClient` into `AdoAdapter` -- would create a circular dependency concern and conflate two different abstraction layers.

### DD-2: Lazy Caching with Private Field

**Decision**: `private cachedTemplate?: AdoProcessTemplateInfo` on `AdoAdapter`. A private `async getTemplate()` method calls the API on first invocation, stores the result, and returns it. All process-aware methods call `getTemplate()`.

**Cache lifetime**: Instance-scoped (one `AdoAdapter` per sync session). No TTL needed -- process templates do not change mid-session.

**Failure mode**: If the API call fails, `getTemplate()` returns `undefined`. Every caller has a fallback: `this.config.closedState || 'Closed'`, `this.config.activeState || 'Active'`, `this.config.workItemType || 'User Story'`.

### DD-3: Process-to-State Mapping Table

Terminal and active states per process template:

```
Template  | Terminal State | Active State  | User Story Type
----------|---------------|---------------|------------------
Basic     | Done          | Doing         | Issue
Agile     | Closed        | Active        | User Story
Scrum     | Done          | Committed     | Product Backlog Item
CMMI      | Closed        | Active        | Requirement
SAFe      | (per base)    | (per base)    | (per base)
```

This table is encoded as a simple `Record` in `ado.ts` -- not a separate constant file. The data is small, stable, and only consumed in one place.

### DD-4: Parent Linking via Hierarchy-Reverse Relation

**Decision**: When `feature.externalRef?.id` exists, add a `System.LinkTypes.Hierarchy-Reverse` relation to the PATCH operations array in `createIssue()`.

**Note**: `FeatureData` currently only has `{ id, title }`. The `externalRef` field needs to be added as an optional property: `externalRef?: { id: string; url?: string }`. This is a minor type extension, not a new interface.

**Format**: ADO link relations use a URL reference:
```json
{
  "op": "add",
  "path": "/relations/-",
  "value": {
    "rel": "System.LinkTypes.Hierarchy-Reverse",
    "url": "https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{parentId}"
  }
}
```

### DD-5: ADO Metadata Fallback (Mirror JIRA Pattern)

**Decision**: Copy the JIRA 3-layer resolution pattern from `closeJiraIssuesForUserStories()` lines 170-186 into `closeAdoWorkItemsForUserStories()`. Read `metadata.json` once per closure call, cache it in a local variable, and check `metadata.ado?.work_item_id` as third fallback.

Resolution order: `usFile.external_tools?.ado?.id` -> `usFile.external_id` -> `metadata.ado.work_item_id`

### DD-6: JIRA Transition Warning (Resilient, Not Throwing)

**Decision**: When `transitionIssue()` finds no matching transition, log a warning with diagnostic data (issue key, target status, available transitions) and return without error. This preserves the existing resilient-sync behavior while making silent failures visible.

`closeIssue()` reads target status from config. Since the `JiraAdapter` class doesn't currently receive the full `SpecWeaveConfig`, this is implemented by adding an optional `closedStatus` field to `JiraAdapterConfig` that the caller can populate from config. Fallback remains `'Done'`.

## 4. Change Specifications

### 4.1 `src/sync/providers/ado.ts`

**New import**: `AdoProcessTemplateInfo` from `../../integrations/ado/ado-client.js`

**New private field**:
```
private cachedTemplate?: AdoProcessTemplateInfo;
```

**New private method `getTemplate()`**:
- Calls `GET https://dev.azure.com/{org}/_apis/projects/{project}?includeCapabilities=true&api-version=7.1`
- Extracts `capabilities.processTemplate.templateName`
- Calls `GET /wit/workitemtypes?api-version=7.1` to check for Capability type
- Returns `AdoProcessTemplateInfo` object
- Caches result in `this.cachedTemplate`
- Returns `undefined` on failure (try/catch, no throw)

**Modified `createIssue()`**:
- Call `await this.getTemplate()` to get process info
- Resolve work item type: `template ? TEMPLATE_WIT_MAP[template.template] : (this.config.workItemType || 'User Story')`
- If `feature.externalRef?.id` exists, add hierarchy-reverse relation to operations array
- No change to error handling

**Modified `closeIssue()`**:
- Call `await this.getTemplate()` to get process info
- Resolve terminal state: `template ? TEMPLATE_CLOSED_MAP[template.template] : (this.config.closedState || 'Closed')`

**Modified `reopenIssue()`**:
- Call `await this.getTemplate()` to get process info
- Resolve active state: `template ? TEMPLATE_ACTIVE_MAP[template.template] : (this.config.activeState || 'Active')`

**Modified `mapStatusToAdo()`** (make async):
- Call `await this.getTemplate()` to resolve `completed` and `done` mappings
- If template available, use template-specific terminal state instead of hardcoded `'Closed'`
- Since `mapStatusToAdo` is called from `updateIssue` which is already async, making it async is safe

**Process-to-state lookup maps** (private constants at module level):
```
TEMPLATE_CLOSED_MAP:  { Basic: 'Done', Agile: 'Closed', Scrum: 'Done', CMMI: 'Closed', SAFe: 'Closed' }
TEMPLATE_ACTIVE_MAP:  { Basic: 'Doing', Agile: 'Active', Scrum: 'Committed', CMMI: 'Active', SAFe: 'Active' }
TEMPLATE_WIT_MAP:     { Basic: 'Issue', Agile: 'User Story', Scrum: 'Product Backlog Item', CMMI: 'Requirement', SAFe: 'User Story' }
```

### 4.2 `src/sync/engine.ts`

**Modified `FeatureData`**:
```
export interface FeatureData {
  id: string;
  title: string;
  externalRef?: { id: string; url?: string };
}
```

This is a backwards-compatible additive change. No existing callers break.

### 4.3 `src/sync/sync-coordinator.ts`

**Modified `closeAdoWorkItemsForUserStories()`**:
- Add metadata.json read block (copied from JIRA closure path, lines 170-186)
- Read once, extract `metadata.ado?.work_item_id`
- Add as third fallback in ID resolution: `usFile.external_tools?.ado?.id || usFile.external_id || metadataAdoId`

### 4.4 `src/sync/providers/jira.ts`

**Modified `JiraAdapterConfig`**:
- Add `closedStatus?: string` optional field

**Modified `transitionIssue()`**:
- After the `find()` call, if no transition found: `console.warn(`[SpecWeave] No matching transition for ${issueKey} to "${targetStatusName}". Available: ${data.transitions.map(t => t.to.name).join(', ')}`)`
- Existing return behavior unchanged (no throw)

**Modified `closeIssue()`**:
- Replace hardcoded `'Done'` with `this.closedStatus || 'Done'` where `this.closedStatus` is set from `config.closedStatus` in the constructor
- One-line change (fallback preserves current default)

## 5. Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Template detection API call adds latency | Lazy caching -- only one call per adapter instance, not per operation |
| ADO project capabilities API unavailable | Graceful fallback to config or hardcoded defaults (no regression) |
| `FeatureData.externalRef` not populated by callers | Parent link is skipped gracefully when missing (AC-US2-03) |
| `mapStatusToAdo()` becoming async | Only called from `updateIssue()` which is already async; call sites handle promises |
| JIRA warning logs are noisy | `console.warn` only fires when transition is genuinely missing -- this is actionable info, not noise |

## 6. Files Modified (No New Files)

1. `src/sync/providers/ado.ts` -- template caching, state/type resolution, parent linking
2. `src/sync/engine.ts` -- `FeatureData.externalRef` optional field
3. `src/sync/sync-coordinator.ts` -- ADO metadata.json fallback
4. `src/sync/providers/jira.ts` -- configurable close status, transition warning

## 7. Testing Strategy

All changes are testable with unit tests mocking the `apiRequest`/`fetch` calls:

- **ADO template detection**: Mock project capabilities response, verify correct state/type resolution per template
- **ADO parent linking**: Mock `createIssue` with and without `feature.externalRef`, verify relation in operations
- **ADO metadata fallback**: Mock metadata.json read, verify 3-layer resolution
- **JIRA transition warning**: Mock transitions response with missing target, verify `console.warn` called with diagnostic data
- **JIRA configurable status**: Verify `closedStatus` config propagates to `transitionIssue()` call

## 8. No ADR Required

These are bug fixes within existing adapter boundaries. No new components, no new external dependencies, no architectural pattern changes. The lazy caching pattern is standard and local to one class.
