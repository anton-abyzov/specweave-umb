# 0859 — Tasks

### T-001: Platform — publish `submission_decision` to UpdateHub on terminal state
**AC**: AC-US1-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given a submission reaches PUBLISHED/AUTO_APPROVED/REJECTED/BLOCKED with a non-null userId → When the decision is finalized → Then a `submission_decision` event is published to UpdateHub keyed `usr_<userId>` (idempotent eventId); an anonymous submission publishes nothing to a user-channel.

### T-002: Platform — additive `submission_decision` event type in publish schema/types
**AC**: AC-US2-01 | **Status**: [x] completed
**Test**: Given the internal publish route + DO → When a `submission_decision` event is forwarded → Then it validates and fans out; existing skill-update events are unaffected.

### T-003: Desktop — subscribe to `usr_<userId>` on the skills-stream when logged in
**AC**: AC-US1-02 | **Status**: [x] completed
**Test**: Given a logged-in user → When the skills-stream filter is built → Then it includes `usr_<userId>`; logged-out → no `usr_` id present.

### T-004: Desktop — route `submission_decision` → native notification
**AC**: AC-US1-03 | **Status**: [x] completed
**Test**: Given a `submission_decision` event arrives on the skills-stream → When dispatched → Then the native notification fires (approved=info, rejected=clickable→/submit/<id>); skill-update events still toast.

### T-005: Regression — skill-update + 0855 SSE + submissions suites green
**AC**: AC-US2-01 | **Status**: [x] completed
**Test**: Given the full change → When skills-stream, event-bus, submissions, and router-token-gate/sse suites run → Then all pass; verify harness Overall PASS.

### T-006: Single-fire dedupe across BOTH notification transports
**AC**: AC-US2-03 | **Status**: [x] completed
**Test**: Given a decision delivered over BOTH the reliable skills-stream (0859, `usr_<userId>`) AND the best-effort `?mine` panel stream (0847) → When both consumers call `notifySubmissionOutcome` → Then exactly ONE native notification fires.
**Design**: hoist a module-level idempotency guard (Set keyed `submissionId:state`) into `useSubmissionNotifications.ts` so `notifySubmissionOutcome` is idempotent per session; both `useSkillUpdates.onSubmissionDecision` and `SubmissionQueuePanel` consult it (drop the panel's local `notifiedRef`). Unit test proves dual-delivery → one notification.
