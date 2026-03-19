# Architecture Plan

## Approach
Per-session state directories keyed by session_id (from hook stdin JSON).
Shared state (active-increment.json) protected with synchronous FileLock.

## Key Decisions
- ADR: Use session_id (not transcript_path UUID) as session key -- simpler, treat /resume as new session
- ADR: Remove VSCode lock auto-skip -- SPECWEAVE_DISABLE_LOCKS=1 exists for explicit opt-out
- ADR: Use synchronous FileLock (not async LockManager) for active-increment -- avoids cascading async changes
- ADR: New SessionStateManager class at src/core/session/ -- reusable by CLI commands and hooks

## Migration
Phase 1: Non-breaking additions (env bridge, per-session dirs)
Phase 2: Backward-compatible changes (per-session first, fall back to global)
Phase 3: Stop hook migration
Phase 4: Remove global auto-mode.json dependency (future increment)
