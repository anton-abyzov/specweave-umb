---
increment: 0618-simplify-sync-setup-fix-triggers
---

# Tasks

### T-001: Event queue utility
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**:
- Given event queue utility → When `queueSyncEvent("0001", "user-story.completed", {usId: "US-001"})` → Then appends JSON line to pending.jsonl
- Given pending.jsonl doesn't exist → When event queued → Then file is created
- Given concurrent writes → When two events queued simultaneously → Then both are written (append-only)

### T-002: Convert LifecycleHookDispatcher to queue mode
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given `sync.mode: "queued"` → When `onTaskCompleted()` fires → Then event is queued, LivingDocsSync NOT called
- Given `sync.mode: "immediate"` → When `onTaskCompleted()` fires → Then LivingDocsSync IS called (legacy)
- Given `specweave complete` calls `onIncrementDone()` → When closure flag is set → Then direct sync runs regardless of mode

### T-003: Convert StatusChangeSyncTrigger to queue mode
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given `sync.mode: "queued"` → When status changes to "completed" → Then event queued, no direct LivingDocsSync
- Given `sync.mode: "immediate"` → When status changes → Then direct sync (legacy behavior)

### T-004: Convert post-tool-use.sh to queue mode
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan**:
- Given status change detected in post-tool-use.sh → When sync.mode is "queued" → Then writes to pending.jsonl instead of calling project-bridge-handler

### T-005: Add sync.mode config option
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**Test Plan**:
- Given no sync.mode in config → When checked → Then defaults to "queued"
- Given `sync.mode: "immediate"` → When checked → Then returns "immediate"

### T-006: Simplify sync-setup wizard
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given single-project (childRepos.length <= 1) → When sync-setup runs → Then asks 3 questions: tracker, project name, validate
- Given multi-project → When sync-setup runs → Then asks tracker + per-childRepo targets
- Given `--quick` flag → When sync-setup runs → Then auto-detects everything, no prompts
