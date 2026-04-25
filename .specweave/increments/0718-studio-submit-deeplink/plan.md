# Implementation Plan: Local Studio Submit-your-skill deep-link

## Overview

Smallest of the three sibling increments. Three pieces:
1. **Workspace-info resolver** — server-side endpoint at `/api/v1/studio/workspace-info` that runs `git config --get remote.origin.url` and returns a normalized `repoUrl`.
2. **`useSubmitDeepLink` hook** — single source of truth for: workspace-info fetch (200ms timeout) → URL compose → telemetry POST (fire-and-forget) → `window.open`.
3. **Two CTA placements** — Studio nav button + binding of 0717's `SubmitDeepLink` stub on `/studio/find`. Both invoke the same hook.

## Component / file map

```
vskill-platform/src/app/
├── api/v1/studio/workspace-info/
│   └── route.ts                           # NEW — resolver endpoint
├── studio/
│   ├── hooks/
│   │   └── useSubmitDeepLink.ts           # NEW — single-source-of-truth hook
│   ├── components/
│   │   └── SubmitNavButton.tsx            # NEW — nav placement (uses hook)
│   └── find/components/
│       └── SubmitDeepLink.tsx             # OWNED BY 0717 (stub) — this increment binds the hook
└── studio/lib/
    ├── repo-url-normalize.ts              # NEW — pure normalization (testable)
    └── workspace-info-cache.ts            # NEW — per-process Map cache
```

## Key data flow — click handler

```ts
// useSubmitDeepLink.ts
function useSubmitDeepLink() {
  const router = useRouter();
  const lastClickRef = useRef(0);

  return useCallback(async () => {
    // Debounce 500ms (AC-US3-03)
    const now = Date.now();
    if (now - lastClickRef.current < 500) return;
    lastClickRef.current = now;

    // 1. Resolve workspace repoUrl with 200ms timeout (AC-US2-06)
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), 200);
    let repoUrl: string | null = null;
    try {
      const r = await fetch('/api/v1/studio/workspace-info', { signal: ac.signal });
      if (r.ok) {
        const data = await r.json();
        repoUrl = data.repoUrl;
      }
    } catch { /* timeout or network — proceed without repoUrl */ }
    finally { clearTimeout(timer); }

    // 2. Compose URL via URL constructor (AC-US2-07)
    const url = new URL('https://verified-skill.com/submit');
    if (repoUrl) url.searchParams.set('repoUrl', repoUrl);

    // 3. Telemetry POST — fire-and-forget (AC-US3-02)
    const q = new URLSearchParams(window.location.search).get('q') || undefined;
    fetch('/api/v1/studio/telemetry/submit-click', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repoUrl: repoUrl ?? undefined, q, ts: Date.now() }),
    }).catch(() => {/* swallow per AC-US3-04 */});

    // 4. Open new tab (AC-US1-05) + fallback (AC-US2-08)
    const win = window.open(url.toString(), '_blank', 'noopener,noreferrer');
    if (!win) {
      toast.show(
        <span>Click <a href={url.toString()} target="_blank" rel="noopener noreferrer">here</a> to open verified-skill.com/submit</span>
      );
    } else {
      toast.show('Opening verified-skill.com…', { duration: 2000 });
      try {
        localStorage.setItem('studio.lastSubmitOpenedAt', new Date().toISOString());
      } catch { /* swallow per FR-002 */ }
    }
  }, []);
}
```

## Workspace-info resolver

```ts
// src/app/api/v1/studio/workspace-info/route.ts
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { access } from 'node:fs/promises';
import { normalizeGitHubRemote } from '@/app/studio/lib/repo-url-normalize';
import { workspaceInfoCache } from '@/app/studio/lib/workspace-info-cache';

const exec = promisify(execFile);

export async function GET() {
  const root = getStudioWorkspaceRoot(); // existing helper
  if (!root) return Response.json({ repoUrl: null });

  const cached = workspaceInfoCache.get(root);
  if (cached !== undefined) return Response.json({ repoUrl: cached });

  try {
    await access(root); // sanity (AC-US2-02)
    const { stdout } = await exec('git', ['-C', root, 'config', '--get', 'remote.origin.url'], { timeout: 1000 });
    const repoUrl = normalizeGitHubRemote(stdout.trim()); // AC-US2-04 + AC-US2-05
    workspaceInfoCache.set(root, repoUrl);
    return Response.json({ repoUrl });
  } catch {
    workspaceInfoCache.set(root, null);
    return Response.json({ repoUrl: null });
  }
}
```

## Normalizer (pure, testable)

```ts
// src/app/studio/lib/repo-url-normalize.ts
export function normalizeGitHubRemote(raw: string): string | null {
  if (!raw) return null;
  // SSH: git@github.com:owner/repo[.git]
  const ssh = raw.match(/^git@github\.com:([^/]+)\/([^/]+?)(?:\.git)?$/);
  if (ssh) return `https://github.com/${ssh[1]}/${ssh[2]}`;
  // HTTPS: https://github.com/owner/repo[.git]
  try {
    const u = new URL(raw);
    if (u.hostname !== 'github.com') return null; // AC-US2-05
    const m = u.pathname.match(/^\/([^/]+)\/([^/]+?)(?:\.git)?\/?$/);
    if (!m) return null;
    return `https://github.com/${m[1]}/${m[2]}`;
  } catch {
    return null;
  }
}
```

## Test strategy

| Layer | Target | Tool |
|---|---|---|
| Unit | `normalizeGitHubRemote` (matrix: ssh / https / .git / gitlab / malformed) | Vitest |
| Unit | `workspaceInfoCache` per-process Map | Vitest |
| Integration | `/api/v1/studio/workspace-info` (mock execFile) | Vitest |
| Integration | `useSubmitDeepLink` hook (mock fetch + window.open + localStorage) | Vitest + RTL |
| E2E | Playwright: click nav button → assert window.open call args contain correct URL | Playwright |
| E2E | Playwright: in a non-github workspace, URL has no `?repoUrl=` | Playwright |

Mock harness for parallel build with 0716: MSW handler `rest.post('/api/v1/studio/telemetry/submit-click', () => res(ctx.status(204)))` (already provided by 0717's harness — this increment imports it).

## Coordination with siblings

- **0717** owns the `SubmitDeepLink.tsx` file as a stub. This increment edits that file (or imports it) to bind `useSubmitDeepLink`. Coordinate via spec FR-003 — both increments expect the file to exist; if 0717 ships first, this increment binds. If 0718 ships first, the stub is created here.
- **0716** owns the `submit-click` telemetry endpoint. This increment uses MSW until 0716 deploys. Final task swaps mock for live.
- **No shared state** between siblings — purely contractual.

## Design decisions (skeptic-tested)

| Decision | Choice | Why |
|---|---|---|
| In-Studio OAuth? | **No, never** | 1-week careful build, real attack surface, zero feature gain (verified-skill.com already has OAuth). User-confirmed hard rule. |
| Block click on workspace-info? | **No — 200ms timeout** | UX must feel instant; cold path on slow filesystem still feels broken if we wait. |
| Cache workspace-info? | **Per-process Map** | Eval-server lifetime is the Studio session; no need for persistent cache. |
| Support GitLab / self-hosted? | **No** | Out of scope; broadens trust boundary. User pastes manually on website. |
| Telemetry awaited? | **No — fire-and-forget** | Telemetry must never break UX (consistent with 0716's design). |
| Pushstate vs window.open? | **window.open** | Submit lives on a different origin (verified-skill.com); same-origin nav doesn't apply. |
| Same component file in nav and find? | **Yes — single hook** | DRY; both placements import `useSubmitDeepLink`. |

## ADR stubs

- **ADR-XXXa**: Studio submit is deep-link-only — no in-Studio OAuth or token storage. Hard architectural rule.
- **ADR-XXXb**: workspace-info resolver is server-side; browser never reads filesystem.
- **ADR-XXXc**: 200ms client-side timeout caps perceived latency on cold workspace-info path.

## Risk register (linked from spec.md)

See spec.md "Risk register" — duplicated here for plan-mode review.
