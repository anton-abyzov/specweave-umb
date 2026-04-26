# 0768 — Plan

## Files touched

| File | Change |
|---|---|
| `wrangler.jsonc` | Add second cron `5,15,25,35,45,55 * * * *` to `triggers.crons`. |
| `scripts/build-worker-entry.ts` | Branch on `controller.cron` inside `scheduled(...)`. Refactor existing two `waitUntil` blocks into a `runLightCohort()` and `runHeavyCohort()` selected by cron string. Default unrecognized cron → light. |
| `scripts/__tests__/build-worker-entry.cohort.test.ts` (new) | Unit-test the cohort dispatcher in isolation: light vs heavy vs unrecognized. |

## Design

```typescript
const LIGHT_CRON = "*/10 * * * *";
const HEAVY_CRON = "5,15,25,35,45,55 * * * *";

async scheduled(controller, env, ctx) {
  const cohort = controller.cron === HEAVY_CRON ? "heavy" : "light";
  ctx.waitUntil(
    runWithWorkerEnv(env, () =>
      cohort === "heavy" ? runHeavyCohort(env) : runLightCohort(env),
    ),
  );
}

async function runLightCohort(env) {
  // DB prewarm + ensureFreshStats + recoverStuckSubmissions +
  //   releaseStuckScanning + recoverStaleReceived + healthchecks
}

async function runHeavyCohort(env) {
  // DB prewarm + refreshPlatformStats + refreshQueueStats (full) +
  //   warmQueueListCache + refreshSkillsCache + refreshPublishersCache +
  //   runEnrichmentBatch + reconcile* + (search index on minute===5 && hour%2===0) +
  //   runGitHubDiscovery on minute===5
}
```

Notes:
- Existing minute/hour gating shifts: `minute===0` becomes `minute===5` for the heavy cohort because the offset cron fires at :05/:15/.../:55. The :05 mark is the "every 10 min" anchor of the heavy cohort — equivalent semantically to the prior :00 anchor.
- The light cohort already has work that must run every 10 min; preserve its existing structure.

## Risks

- **Cloudflare picking up new schedule**: confirmed by `wrangler triggers deploy` running as part of `npx @opennextjs/cloudflare deploy`. Both schedules deploy atomically.
- **Heavy cohort runs longer than 30s**: fall-through. The next heavy tick (10 min later) reattempts. Light cohort is unaffected.
- **Cron drift between schedules**: irrelevant — both write the same KV keys. Last-write-wins. The watchdog only writes if KV is older than 15 min, so the heavy cron's writes are not overwritten by stale snapshots.

## Validation

- [ ] Unit: cohort dispatcher selects correctly for each cron string + unknown.
- [ ] After deploy, `wrangler tail` shows two distinct cohort runs within one 10-min window.
- [ ] `/api/v1/submissions/stats` returns `rejectionBreakdown` populated within 15 min of deploy.
- [ ] Playwright on `https://verified-skill.com/queue?filter=rejected` shows reason pills.
