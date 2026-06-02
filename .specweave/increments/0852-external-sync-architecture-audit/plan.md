# Implementation Plan: External Sync Architecture Audit and Hardening

## Overview

Treat this as a bounded hardening pass, not a full sync rewrite. The code already contains a target architecture (`SyncEngine` plus provider adapters), but runtime commands still use older paths (`SyncCoordinator`, `ExternalIssueAutoCreator`, living docs GitHub sync, and command-specific credential logic). This increment audits those seams, fixes confirmed low-risk defects, and records larger simplifications as follow-up architecture work.

## Architecture

### Components
- Sync CLI commands
  **Project**: specweave
  `src/cli/commands/sync-progress.ts`, `sync-health.ts`, `sync-status.ts`, `sync-gaps.ts`, and `sync-retry.ts`.
- Sync routing
  **Project**: specweave
  `src/sync/sync-target-resolver.ts`, `src/sync/story-router.ts`, and project resolution services.
- Provider integrations
  **Project**: specweave
  GitHub, Jira, and ADO adapters, wrappers, reconcilers, and health checks.
- Analytics
  **Project**: specweave
  `src/core/analytics/*`, analytics CLI, and `.specweave/state` metrics outputs.
- Secret handling
  **Project**: specweave
  Credential helpers, `.env*` parsing, redaction utilities, and Obsidian credential note discovery.

### Data Model
- `metadata.json`: increment status, external links, legacy provider fields, `project`, and optional `syncTarget`.
- `spec.md`: source-of-truth user stories and per-story `**Project**:` fields.
- `config.json`: umbrella child repos, provider config, sync profiles, and permissions.
- `.env*`: local credential values, never copied into increment artifacts.

### API Contracts
- CLI `specweave sync-progress <increment> [--no-*] [--force]`: push task/spec progress into living docs and providers.
- CLI `specweave sync-health [--provider] [--json]`: validate configured provider credentials and access.
- CLI `specweave analytics`: report command, skill, and agent usage telemetry.

## Technology Stack

- **Language/Framework**: TypeScript on Node.js.
- **Libraries**: Vitest, Playwright, yaml, fs-extra, provider SDKs/REST clients.
- **Tools**: local SpecWeave CLI, `rg`, git, Obsidian filesystem scan, GitHub CLI where available.

**Architecture Decisions**:
- Keep fixes small and command-facing. A full `SyncEngine` migration is higher risk and belongs in a separate increment.
- Prefer shared project and credential resolution helpers when already present. Add only minimal local helpers when importing a heavier service would create side effects.
- Reports stay under `.specweave/increments/0852-external-sync-architecture-audit/reports/`.

## Implementation Phases

### Phase 1: Foundation
- Replace template spec/plan/tasks with real scope.
- Scan ADRs, runtime commands, and provider integration code.
- Run analytics and secret-safe credential scans.

### Phase 2: Core Functionality
- Fix confirmed defects with focused tests.
- Run targeted tests around sync routing and health checks.

### Phase 3: Enhancement
- Run broader local gates.
- Produce architecture report with recommended simplification path.
- Attempt release/push/deploy only if gates and worktree state are safe.

## Testing Strategy

- Focused Vitest tests for every fix.
- `npm run build`.
- `npm run test:unit:fast`, `npm run test:integration`, `npm run test:e2e`, `npm run test:coverage`.
- `npx playwright test` only if Playwright config is present and runnable locally.

## Technical Challenges

### Challenge 1: Dirty umbrella workspace
**Solution**: Keep code edits in the clean `specweave` child repo and increment artifacts in root.
**Risk**: Release/push may be blocked by unrelated user changes. Do not stage unrelated files.

### Challenge 2: Credentials
**Solution**: Detect variable presence and scan patterns only. Never print values.
**Risk**: External live checks may skip or fail if credentials are absent.

### Challenge 3: Sync architecture drift
**Solution**: Fix small command-level bugs now and document the larger `SyncEngine` migration separately.
**Risk**: Full simplification cannot be safely completed as part of a broad audit without larger regression work.
