# 0859 — Plan

## Platform (vskill-platform)

- **Producer**: at every submission terminal-state transition in `src/app/api/v1/internal/finalize-scan/route.ts` and `src/lib/queue/process-submission.ts` (the same sites where `userId` was threaded in 0847), when `userId` is non-null, call `publishToUpdateHubWithEventId()` (`src/lib/skill-update/publish-client.ts`) with a `submission_decision` event:
  - `skillSlug: "usr_" + userId` (the user-channel selector — the DO matcher already does `filter.includes(skillSlug)`, so NO DO code change),
  - `eventId`: stable per (submissionId, state) so retries are idempotent,
  - payload: `{ submissionId, state, skillName, decision: "approved"|"rejected" }`.
- Extend the publish event schema/validation (`src/app/api/v1/internal/skills/publish/route.ts` + `src/lib/skill-update/types.ts`) to accept the additive `submission_decision` type without breaking skill-update events.
- Anonymous (userId null) → skip (no owner channel).

## Desktop (vskill eval-ui)

- **Subscribe**: in the skills-stream filter builder (`src/eval-ui/src/utils/resolveSubscriptionIds.ts` / `useSkillUpdates.ts`), append `usr_<userId>` when the user is logged in (userId from `AccountContext`). Stays under the 500-id `?skills` cap.
- **Handle**: in `useSkillUpdates.ts` event dispatch, route `submission_decision` events to the native notification via `useSubmissionNotifications` (`planSubmissionNotification` / `notifySubmissionOutcome`) — approved → info, rejected → clickable → `/submit/<id>`.
- The 0847 `SubmissionQueuePanel` per-isolate `?mine` stream is unchanged (best-effort live UI); the DO channel is the reliable notification transport.

## Why reuse UpdateHub vs a new submissions DO
The UpdateHub is already the cross-isolate-reliable, idempotent, 0855-fixed channel the desktop subscribes to. A user-channel (`usr_<userId>`) overloads its existing slug-filter matcher with zero DO changes and zero new connections. A separate submissions DO would duplicate the WS↔SSE bridge + outbox machinery for no benefit.

## Tests
Platform: publish-on-terminal-state (each decision), idempotent eventId, anonymous-skip, skill-update path unaffected. Desktop: filter includes usr_<userId> only when logged in; submission_decision → native notification; skill-update events still toast; 0855 SSE untouched. Regression: existing skills-stream + submissions + event-bus suites green.
