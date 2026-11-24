# Gemini CLI model availability

## Problem
The Gemini CLI Vertex picker shows Argon and older CLI models, omitting Carbon and Neon. Current source adds Argon statically. Increment 1277 AC-05 already planned Carbon; reconcile its owner and evidence before implementation.

## Scope
Investigate installed/runtime CLI version and catalog, ACP discovery and cache, official Google model IDs and account metadata. Repair confirmed catalog omissions with honest access status. Preserve configured accounts, credentials, favorites, ordering and no automatic paid Gemini fallback. No paid inference, auth or billing changes.

## Acceptance Criteria
- [ ] AC-01: Report traces runtime catalog through discovery, cache and UI with official current model evidence and account access uncertainty separated.
- [ ] AC-02: Every confirmed supported omitted model is exposed without duplicates or invented access claims, preserving custom entries and user ordering.
- [ ] AC-03: Focused regression tests pass; required review, merge and normal release have independent scoped verification or explicit outstanding gates.

## Approach
Read-only investigation first. Coordinate exact overlap with 1432 and reconcile 1277 AC-05. Work in an app-owned worktree. Inspect AcpRegistryDriver modelsFromDiscovery and its tests, CLI package model constants and set_model validation. Compare primary Google docs/release source and read-only configured Vertex model metadata. Only then choose the smallest catalog change; account access must never be inferred from Copilot or Cursor. Use checks copy/checks run for full suites. Required review order: Gemini4 Neon Copilot Enterprise then GPT6.2 Sol, never Grok4.7. Merge and request existing release, then independently verify installed catalog without inference spend.

## Decisions
### Defaulted
- D-01: Metadata/catalog visibility is not proof of inference entitlement; report unverified access honestly.
- D-02: 1277 Cursor billing and credits stay with their owner; this increment reconciles only Gemini catalog overlap.
### Open
- Exact shared-file overlap pending owner response.

## Tasks
### T-01 Investigate CLI and availability
- AC: AC-01 | Files: .specweave/increments/1433-gemini-cli-model-availability/reports/investigation.md | Test: verify source links and read-only runtime catalog receipts
### T-02 Repair confirmed discovery omissions
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/AcpRegistryDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/AcpRegistryDriver.test.ts | Test: focused AcpRegistryDriver catalog tests through checks runner
### T-03 Review, deliver, verify and close 1433
- AC: AC-03 | Files: .specweave/increments/1433-gemini-cli-model-availability/reports/delivery.md | Test: specweave verify 1433-gemini-cli-model-availability
