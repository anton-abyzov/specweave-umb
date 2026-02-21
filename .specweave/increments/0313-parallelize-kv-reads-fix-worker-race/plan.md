# Plan: 0313 — Parallelize remaining sequential KV reads + fix worker-context race

## Approach

All three fixes follow the same pattern established in 0281. TDD: RED → GREEN.

---

## T-001: Parallelize getStuckSubmissions

**Pattern (same as getSubmissionsFresh fix in 0281):**

```typescript
// BEFORE
for (const key of keys) {
  const raw = await kv.get(key.name); // sequential
  ...
}

// AFTER
const settled = await Promise.allSettled(
  keys.map(async (key): Promise<StuckSubmission | null> => {
    const raw = await kv.get(key.name);
    if (!raw) return null;
    const sub: StoredSubmission = JSON.parse(raw);
    if (!STUCK_STATES.includes(sub.state)) return null;
    const updatedMs = new Date(sub.updatedAt).getTime();
    const elapsed = now - updatedMs;
    if (elapsed < STUCK_THRESHOLD_MS) return null;
    return { id: sub.id, state: sub.state, repoUrl: sub.repoUrl, skillName: sub.skillName, skillPath: sub.skillPath, updatedAt: sub.updatedAt, stuckForMs: elapsed };
  }),
);
return settled
  .filter((r): r is PromiseFulfilledResult<StuckSubmission | null> => r.status === "fulfilled")
  .map((r) => r.value)
  .filter((v): v is StuckSubmission => v !== null);
```

---

## T-002: Parallelize enumeratePublishedSkills

**Same pattern:**

```typescript
// AFTER
const settled = await Promise.allSettled(
  skillKeys.map(async (key): Promise<PublishedSkillSummary | null> => {
    const raw = await kv.get(key.name);
    if (!raw) return null;
    const skill = JSON.parse(raw) as Record<string, unknown>;
    const slug = key.name.slice("skill:".length);
    return { slug, name: (skill.name as string) ?? slug, repoUrl: (skill.repoUrl as string) ?? "", ... };
  }),
);
return settled
  .filter((r): r is PromiseFulfilledResult<PublishedSkillSummary | null> => r.status === "fulfilled")
  .map((r) => r.value)
  .filter((v): v is PublishedSkillSummary => v !== null);
```

---

## T-003: AsyncLocalStorage for worker-context

**New worker-context.ts API:**

```typescript
import { AsyncLocalStorage } from "async_hooks";

const workerEnvStorage = new AsyncLocalStorage<CloudflareEnv>();

export function getWorkerEnv(): CloudflareEnv | null {
  return workerEnvStorage.getStore() ?? null;
}

export function runWithWorkerEnv<T>(env: CloudflareEnv, callback: () => Promise<T>): Promise<T> {
  return workerEnvStorage.run(env, callback);
}
```

**Updated consumer.ts pattern:**

```typescript
// BEFORE
setWorkerEnv(env);
try {
  // ... process batch
} finally {
  clearWorkerEnv();
}

// AFTER
await runWithWorkerEnv(env, async () => {
  // ... process batch
});
```

The `run()` scope automatically isolates the context. When the callback returns (or throws), the storage is restored to whatever it was before. No manual `clearWorkerEnv()` needed.

---

## Files to Modify

1. `src/lib/submission-store.ts` — `getStuckSubmissions`, `enumeratePublishedSkills`
2. `src/lib/worker-context.ts` — replace module-level var with AsyncLocalStorage
3. `src/lib/queue/consumer.ts` — use `runWithWorkerEnv` instead of set/clear
4. `src/lib/__tests__/submission-store.test.ts` — TC-056, TC-057
5. `src/lib/queue/__tests__/consumer.test.ts` — TC-058, update existing tests for new API
