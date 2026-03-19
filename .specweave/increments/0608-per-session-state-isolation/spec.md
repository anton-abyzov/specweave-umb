# Per-Session State Isolation

## US-001: Session-Isolated Auto Mode
As a developer using multiple Claude Code sessions on the same project,
I want each session's auto mode state to be isolated,
so that opening a new session doesn't destroy my running auto mode session.

### Acceptance Criteria
- [ ] AC-US1-01: SessionStart hook parses stdin JSON and extracts session_id
- [ ] AC-US1-02: SessionStart bridges CLAUDE_SESSION_ID to env via CLAUDE_ENV_FILE
- [ ] AC-US1-03: Per-session directory created at .specweave/state/sessions/{session_id}/
- [ ] AC-US1-04: Dead sessions are garbage collected (dead PID + age > 5min)
- [ ] AC-US1-05: Auto-mode.json written to per-session dir when CLAUDE_SESSION_ID available
- [ ] AC-US1-06: Cancel-auto cleans per-session state
- [ ] AC-US1-07: Auto-status reads per-session state
- [ ] AC-US1-08: Stop hook reads session_id from stdin and uses per-session auto-mode.json

## US-002: Concurrent Write Protection
As a developer with multiple sessions modifying increment state,
I want shared state files to be protected from concurrent writes,
so that no data is lost from TOCTOU race conditions.

### Acceptance Criteria
- [ ] AC-US2-01: LockManager no longer auto-skips in VSCode environments
- [ ] AC-US2-02: active-increment.json writes protected with FileLock
- [ ] AC-US2-03: FileLock extracted to reusable src/utils/file-lock.ts

## US-003: Backward Compatibility
As a user on an older Claude Code version without session_id support,
I want the system to fall back gracefully to global state,
so that nothing breaks during the transition.

### Acceptance Criteria
- [ ] AC-US3-01: All per-session lookups fall back to global path when session_id unavailable
- [ ] AC-US3-02: AutoModeFlag type has optional sessionId field
