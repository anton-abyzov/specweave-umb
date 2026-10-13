# Real Aide Google verification, 2026-10-13

Google is connected and Aide is authorized for Gmail, Calendar and Drive. Real Google reads remain **unverified** because Aide's configured Codex provider was denied before any Google tool ran.

The user confirmed completion of Google consent and Aide access. SpecWeave installed/stable were both 3.0.14. T-06 was released in the prior handoff, then claimed as `codex-aide-google-live` for this bounded live check.

## Actual results

- Status receipt `live-google-status-20261013T0556.json`: runtime 1.0.7, official Studio OAuth client, connected true, all three globally granted services and all three Aide project grants, no pending sign-in or connection error. Finished 05:55:58.819Z.
- Native receipt `live-google-native-20261013T0557.json`: one prompt dispatched to Aide's existing coordinator, command ID `be0f17f6-0942-4d5c-a3ba-7eb962184cba`; run ordinal 4 failed at 05:57:41.100Z. Zero Google calls, zero other dynamic tools, zero delegation. No Google health probes or content reads occurred.
- Read-only inspection receipt `live-google-inspect-20261013T0600.json`: inspected the same completed run without dispatching. Failure class `provider_error`, code/retryable/reset time null. Finished 05:59:54.531Z.

Exact transport-safe error, with no personal content:

> The effective Codex route for this workspace is not verified as a native subscription. Configure custom endpoints as an explicit API instance.

Source `apps/server/src/studio/Capacity.ts:102-103` emits this after native authorization succeeds but `nativeRoute.verify(entry, cwd, baseEnv)` returns false. It precedes quota admission and provider start. This identifies native route verification as the gate; it does not prove an actual custom endpoint exists. It is separate from Google consent, API errors, and the original screenshot's Claude quota failure.

## Boundaries and cleanup

All three official temporary Studio bearer sessions were individually revoked; existing active sessions were preserved, zero unowned active sessions were added, and the runner created zero pairing links. Tokens remained in process memory. Revocation retains the normal audit row. No browser or listener ran. No Google/provider credentials were read or copied, no provider setting or project grant changed, no schedule or external message was created, and no native retry was issued.

The report runner now has an `inspect` phase with only `orchestration:read`, requiring the existing command ID and refusing dispatch if the run is absent. Its syntax check passes. `verify-real-google.py` verifies saved sanitized evidence without issuing another turn; it correctly exits 1 on this failed native receipt. T-06 is incomplete and must not be marked done from account readiness alone.

## Next gate

Resolve why Aide's effective Codex route cannot be verified, preserving the selected account and provider settings unless separately authorized. Coordinate any new native run with the root task. The completed command ID above must be reused for read-only inspection, never treated as proof that a new retry was dispatched. After the provider gate is resolved, a fresh status receipt and explicitly coordinated single native verification can establish the real health and three bounded read results.
