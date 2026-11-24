# Prevent runaway SpecWithCode database snapshots

## Problem

On November 20, 2026, a snapshot of a 15 GiB M4 store reportedly wrote 711 GiB over 18 minutes before the worker stopped it. SQLite's online backup can restart as other connections commit. The CLI currently gives it no work budget and can overwrite a file created while the copy is in progress.

## Scope

Harden the SpecWithCode CLI snapshot command and document safe use. Validate against synthetic databases only.

## Acceptance Criteria

- [ ] AC-01: Copy and verify a self-contained database with committed WAL rows, with bounded backup work and destination capacity checks.
- [ ] AC-02: Failed or competing snapshots leave existing files intact and clean up their own staging files.

## Approach

Keep the existing SQLite read-only opening flags. Copy in measured batches without pinning the source WAL. Check destination space before copying and between batches. Publish the validated file atomically with a no-replace operation.

## Decisions

### Asked

- Fix the command and validate on synthetic data. Preserve existing artifacts.

### Defaulted

- Bound copying to two passes' worth of pages and five minutes. Keep 256 MiB free on the destination volume.

### Open

- none

## Tasks

### T-01 Bound and safely publish CLI snapshots
- AC: AC-01, AC-02 | Files: apps/server/src/persistence/liveDatabaseSnapshot.ts, apps/server/src/persistence/liveDatabaseSnapshot.test.ts, docs/operations/live-database.md | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/persistence/liveDatabaseSnapshot.test.ts apps/server/src/cli/db.test.ts
