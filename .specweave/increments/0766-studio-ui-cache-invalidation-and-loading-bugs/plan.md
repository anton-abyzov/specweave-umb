# 0766 — Plan

## Files

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useSWR.ts` | Capture errors in state, stop re-throwing, fix `loading` formula. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useSWR.error.test.tsx` | New BDD tests for AC-US1-01..03. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx` | Add `onSkillUpdated(plugin, skill)` helper; expose via context. Add defensive `currentVersion >= latestVersion` skip in `mergeUpdatesIntoSkills` (or its caller). |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/components/UpdateAction.tsx` | Replace partial invalidation with `onSkillUpdated`. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/VersionHistoryPanel.tsx` | Replace partial invalidation with `onSkillUpdated`. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/components/UpdateDropdown.tsx` | Wire any inline-update completion through `onSkillUpdated`. |

## Implementation outline

### useSWR fix

```ts
const [errorState, setErrorState] = useState<Error | undefined>(undefined);

// rejection handler
(err) => {
  inFlight.delete(key);
  if (mountedRef.current && keyRef.current === key) {
    setErrorState(err instanceof Error ? err : new Error(String(err)));
    forceUpdate((n) => n + 1);
  }
  for (const sub of flight.subscribers) sub();
  // do NOT re-throw
},

// success handler also clears errorState
(data) => {
  cache.set(key, { data, fetchedAt: Date.now() });
  inFlight.delete(key);
  if (mountedRef.current && keyRef.current === key) {
    setErrorState(undefined);
    forceUpdate((n) => n + 1);
  }
  for (const sub of flight.subscribers) sub();
},

// revalidate clears error too
const revalidate = () => {
  setErrorState(undefined);
  mutate(key);
};

return {
  data: entry?.data,
  loading: enabled && !entry && !errorState && inFlight.has(key),
  error: errorState,
  revalidate,
};
```

### StudioContext.onSkillUpdated

```ts
import { mutate } from "./hooks/useSWR";

const onSkillUpdated = useCallback((plugin: string, skill: string) => {
  void refreshUpdates();
  void refreshSkills();
  mutate(`versions/${plugin}/${skill}`);
  dismissPushUpdate(`${plugin}/${skill}`);
}, [refreshUpdates, refreshSkills, dismissPushUpdate]);

// expose via context value
return { ..., onSkillUpdated };
```

### Defensive merge skip

In `mergeUpdatesIntoSkills` (or just before stamping in `mergedSkills`):

```ts
if (skill.currentVersion && update.latestVersion && !isVersionLess(skill.currentVersion, update.latestVersion)) {
  return skill; // skill is on or ahead of latest — don't restamp
}
```

(Use a small `isVersionLess` helper, or import the one from update.ts shared logic.)

### Caller swaps

- `UpdateAction.tsx:44-48`: replace `refreshUpdates + dismissPushUpdate` with `onSkillUpdated(plugin, skill)`.
- `VersionHistoryPanel.tsx:122-125`: replace `refreshSkills + mutate(swrKey)` with `onSkillUpdated(plugin, skill)`.
- `UpdateDropdown.tsx`: same pattern at any inline-update success.

## Tests

Unit (vitest + jsdom):
- AC-US1-01: useSWR + a fetcher that rejects → `error` is the rejected Error, `loading` is false.
- AC-US1-02: rejection causes no global `unhandledrejection` in the test env.
- AC-US1-03: `revalidate()` after error clears `error`, allows next fetch to succeed.

Existing tests for `RightPanel.updateAction`, `VersionHistoryPanel`, `UpdateDropdown.0708` continue to pass (verify after wiring changes).

## Release

vskill `0.5.136` patch. Build, test, publish, install via npx, verify in browser preview.
