SHIP
Verdict: ship

Reviewed `c1a3d8c094ec657581f479e695eda57da46e2982` for T-23 / AC-36. T23R3-01 is closed. Wake ignores the cancel count, asks for status by held ID, and separates continued threads from queues eligible to resume (`apps/server/src/away/awaySleepRoute.ts:258-296,325-359`). In the reverse pairing, the receiver stops the waiting delivery but returns zero to a legacy source when an acting or done delivery exists (`apps/server/src/away/AwayIntents.ts:169-198`).

The receiver regression seeds done and waiting deliveries and checks both the reply and stored states (`apps/server/src/away/awayIntentRoute.test.ts:395-425`). The source regression checks that a positive count followed by a continuation receipt prompts without resuming the queue (`apps/server/src/away/awaySleepRoute.test.ts:419-447`). Non-blocking test gap: it does not assert that the fence callback received the thread ID.

**Red evidence:** Fail-first is not yet verified. The Checks run `44551182559` for tests-only commit `ca663201` was queued when inspected; no matching failure log was found in the supplied scratch folder.
