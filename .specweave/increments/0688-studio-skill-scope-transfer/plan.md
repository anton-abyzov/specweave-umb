---
increment: 0688-studio-skill-scope-transfer
title: "Studio Skill Scope Transfer — Technical Plan"
type: feature
---

# Plan — Increment 0688: Studio Skill Scope Transfer

> Scope contract — this plan satisfies the ACs declared in `spec.md` (US-001..US-004). The approved master design is archived at `~/.claude/plans/dreamy-mapping-kitten.md`; this plan adapts that design to existing vskill code.

## 1. Architecture overview

Studio (vskill CLI) is a single-server web app — a Node HTTP server (`eval-server/`) that both serves the React SPA (`eval-ui/`) and handles `/api/*` routes. There is **no separate process** for scope-transfer; we extend the existing server with three new write routes and one new streaming route, and compose the client behavior from three focused React hooks.

```
┌─────────────────────────── vskill studio (single process) ───────────────────────────┐
│                                                                                       │
│  ┌─────────── Browser (eval-ui, React 19 + Vite) ───────────┐                         │
│  │                                                           │                         │
│  │   Sidebar ──▶ ContextMenu ──▶ useScopeTransfer hook ──┐   │                         │
│  │                                                      │   │                         │
│  │   StudioLayout ──▶ OpsDrawer ──▶ useStudioOps hook ──┤   │                         │
│  │                                                      │   │                         │
│  │   (useSSE — existing POST+ReadableStream plumbing) ◀─┘   │                         │
│  └───────────────────────────┬───────────────────────────────┘                         │
│                              │  HTTP + SSE                                             │
│  ┌───────────────────────────▼───────────────────────────────┐                         │
│  │   eval-server (Node http.Server + Router)                 │                         │
│  │   ├─ POST  /api/skills/:plugin/:skill/promote  (SSE)      │                         │
│  │   ├─ POST  /api/skills/:plugin/:skill/test-install (SSE)  │                         │
│  │   ├─ POST  /api/skills/:plugin/:skill/revert     (SSE)    │                         │
│  │   ├─ GET   /api/studio/ops?limit&before         (JSON)    │                         │
│  │   ├─ GET   /api/studio/ops/stream               (SSE)     │                         │
│  │   └─ DELETE /api/studio/ops/:id                 (JSON)    │                         │
│  │                                                           │                         │
│  │   └── shared libs (new) ──▶ src/studio/lib/                │                         │
│  │         ├─ scope-transfer.ts  (copy + collision guard)    │                         │
│  │         ├─ provenance.ts      (read/write sidecar)        │                         │
│  │         └─ ops-log.ts         (atomic JSONL appender)     │                         │
│  └───────────────────────────┬───────────────────────────────┘                         │
│                              │ fs                                                      │
│                              ▼                                                         │
│   ./skills/…              .claude/skills/…        ~/.claude/skills/…   ~/.vskill/…    │
│   (OWN — authored)        (INSTALLED — local)     (GLOBAL — home)     studio-ops.jsonl│
└───────────────────────────────────────────────────────────────────────────────────────┘
```

**Key boundary:** path-based origin classification (`classifyOrigin`) stays the source of truth per ADR 0674-02 — the new provenance sidecar **enriches** rows for UI purposes only; it never flips the `origin`/`scope` classification.

## 2. Backend design

### 2.1 New files

| Path | Purpose |
|---|---|
| `src/studio/routes/promote.ts` | `POST /api/skills/:plugin/:skill/promote` — INSTALLED/GLOBAL → OWN, SSE |
| `src/studio/routes/test-install.ts` | `POST /api/skills/:plugin/:skill/test-install` — OWN → INSTALLED (default) or GLOBAL (`?dest=global`), SSE |
| `src/studio/routes/revert.ts` | `POST /api/skills/:plugin/:skill/revert` — provenance-gated delete of OWN copy, SSE |
| `src/studio/routes/ops.ts` | `GET /api/studio/ops` paginated + `GET /api/studio/ops/stream` SSE + `DELETE /api/studio/ops/:id` |
| `src/studio/lib/scope-transfer.ts` | Shared copy helper, collision detection, path resolution |
| `src/studio/lib/provenance.ts` | Read/write `.vskill-meta.json` sidecar (see ADR 0688-02) |
| `src/studio/lib/ops-log.ts` | Append-only JSONL writer with `O_APPEND` atomic semantics |

**Registration.** A new `registerScopeTransferRoutes(router, root)` in `src/studio/routes/index.ts` is called from `eval-server.ts:42-53` alongside the existing `registerSkillCreateRoutes(...)` etc.

### 2.2 Shared lib contracts

```ts
// scope-transfer.ts
export interface TransferRequest {
  plugin: string;
  skill: string;
  fromScope: "installed" | "global" | "own";
  toScope: "own" | "installed" | "global";
  overwrite?: boolean;
  agentId?: string;    // inherited from 0686 tri-scope; resolved via AGENTS_REGISTRY when not given
}
export interface TransferResult {
  opId: string;
  sourcePath: string;
  destPath: string;
  filesWritten: number;
}
export async function transfer(req: TransferRequest, emit: SSEEmitter): Promise<TransferResult>;
```

Implementation re-uses `copyPluginFiltered` from [src/commands/add.ts:690](../../../repositories/anton-abyzov/vskill/src/commands/add.ts). If we need to share it without importing from `commands/`, lift it into `src/shared/copy-plugin-filtered.ts` and have `add.ts` re-export. **Prefer lift-and-import over duplicate — DRY principle per CLAUDE.md.**

Collision guard: before copying, `existsSync(destPath)` → if true and `!req.overwrite`, throw `new CollisionError(destPath)`. Route translates this into HTTP 409 with `{ ok: false, code: "collision", path }`.

```ts
// provenance.ts
export async function writeProvenance(skillDir: string, p: Provenance): Promise<void>;
export async function readProvenance(skillDir: string): Promise<Provenance | null>;
export async function removeProvenance(skillDir: string): Promise<void>;
```

Write is `writeFileSync(join(skillDir, ".vskill-meta.json"), JSON.stringify(p, null, 2))`. Read is best-effort — parse failure returns `null`, logs to stderr at debug level. No throwing.

```ts
// ops-log.ts
export async function appendOp(op: StudioOp): Promise<void>;
export async function listOps(opts: { before?: number; limit?: number }): Promise<StudioOp[]>;
export function subscribe(fn: (op: StudioOp) => void): () => void;  // in-process subscribers
export async function deleteOp(id: string): Promise<void>;          // tombstone — NOT a rewrite
```

Atomicity: open the file once with `O_APPEND | O_WRONLY | O_CREAT`, write single `\n`-terminated JSON line per op. On POSIX, writes <`PIPE_BUF` (4 KiB) are atomic with O_APPEND — our ops are well under. No lock file needed at this scale. If a future producer writes larger payloads we upgrade to a proper append-only log library.

`deleteOp` writes a tombstone line `{"id":"…","tombstone":true}`; `listOps` filters these out on read. This preserves the append-only invariant (never rewrite history).

Subscription model: in-process `EventEmitter` — `appendOp` emits an internal event consumed by `GET /api/studio/ops/stream` handlers. No cross-process IPC.

**File path:** `~/.vskill/studio-ops.jsonl` (resolved via `os.homedir()`). Directory created on first write.

### 2.3 Filesystem layout

| Scope | Path template | Notes |
|---|---|---|
| OWN | `<root>/skills/<skill>/` | `root` = CWD of `vskill studio` |
| INSTALLED | `<root>/.claude/skills/<skill>/` | resolved via `AGENTS_REGISTRY.localSkillsDir` for non-Claude agents |
| GLOBAL | `<os.homedir()>/.claude/skills/<skill>/` | resolved via `AGENTS_REGISTRY.globalSkillsDir` |

## 3. Frontend design

### 3.1 Component tree additions

```
<StudioLayout>
  ├─ <Sidebar>
  │    └─ <SidebarSection origin="own|installed|global">
  │         └─ <SkillRow data-skill-id=…>         ← new data attr for FLIP
  │              └─ <ContextMenu>                 ← extend items (§3.2)
  │              └─ <PromotedFromChip>            ← new; renders when provenance present
  ├─ <StatusBar>
  │    └─ <OpsCountChip>                          ← new
  └─ <RightPanel variant="ops">
       └─ <OpsDrawer>                             ← new; virtualized list
            └─ <OpsRow> (expandable)              ← new
  <ToastStack>  (existing, with `action` already supported — no change)
```

### 3.2 ContextMenu extension

[src/eval-ui/src/components/ContextMenu.tsx:21-29](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/components/ContextMenu.tsx) defines `ContextMenuAction`; extend with `"promote" | "test-install" | "revert"`. `itemsForSkill` gains:

```ts
// Pseudocode — actual TS in components/ContextMenu.tsx
if (skill.scope === "installed" || skill.scope === "global") {
  items.push({ action: "promote", label: "Promote to OWN" });
}
if (skill.scope === "own") {
  items.push({ action: "test-install", label: "Test-install to .claude/" });
  if (skill.provenance)  // sidecar present
    items.push({ action: "revert", label: "Revert to INSTALLED" });
}
```

`skill.provenance` is a synchronous field — the `SkillInfo` shape is extended (§3.5) with an optional `provenance?: Provenance | null` field populated by the scanner. No runtime fetch needed.

### 3.3 New hooks

**`lib/use-scope-transfer.ts`** — orchestrates the whole promote/test-install/revert ceremony:

```ts
export function useScopeTransfer() {
  const sse = useSSE<TransferEvent>();
  const { toast } = useToast();
  const refresh = useSkillListRefresh();  // existing

  async function promote(skill: SkillInfo) {
    const sourceRect = captureRect(skill);          // FLIP: First
    await sse.start(`/api/skills/${skill.plugin}/${skill.skill}/promote`);
    // sse.done triggers — skill list has been re-scanned via SSE "indexed" event
    refresh();
    requestAnimationFrame(() => {
      runFlip(skill, sourceRect);                   // FLIP: Last + Invert + Play
      toast({
        message: `Promoted ${skill.skill} → OWN`,
        durationMs: 5000,
        action: { label: "Undo", onInvoke: () => revert(skill) },
      });
    });
  }

  async function testInstall(skill: SkillInfo, dest: "installed"|"global" = "installed") { /* mirror */ }
  async function revert(skill: SkillInfo) { /* same pattern, different endpoint */ }

  return { promote, testInstall, revert, state: sse };
}
```

**`hooks/use-studio-ops.ts`** — subscribes to the SSE stream + handles pagination:

```ts
export function useStudioOps() {
  const [ops, setOps] = useState<StudioOp[]>([]);
  useEffect(() => {
    // initial load
    fetch("/api/studio/ops?limit=50").then(r => r.json()).then(setOps);
    // live feed
    const es = new EventSource("/api/studio/ops/stream");
    es.addEventListener("op", e => setOps(prev => [JSON.parse(e.data), ...prev]));
    return () => es.close();
  }, []);
  const loadMore = useCallback(() => { /* ops[ops.length-1].ts → ?before=… */ }, [ops]);
  return { ops, loadMore };
}
```

**Note on EventSource vs useSSE.** `useSSE` is tuned for POST-initiated request/response streams. The ops-stream is GET-initiated + long-lived, which maps cleanly to the browser's native `EventSource`. Same ADR 0688-01 decision, same server plumbing (`initSSE`/`sendSSE`), different client primitive — picked for simplicity.

### 3.4 FLIP motion implementation

**`lib/flip.ts`** — ~40-line module, no animation-library dependency.

```ts
export function captureRect(skill: SkillInfo): DOMRect | null {
  return document
    .querySelector<HTMLElement>(`[data-skill-id="${skill.plugin}/${skill.skill}"]`)
    ?.getBoundingClientRect() ?? null;
}

export function runFlip(skill: SkillInfo, first: DOMRect | null) {
  if (!first) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const el = document.querySelector<HTMLElement>(
    `[data-skill-id="${skill.plugin}/${skill.skill}"]`,
  );
  if (!el) return;
  const last = el.getBoundingClientRect();
  const dx = first.left - last.left;
  const dy = first.top  - last.top;
  if (dx === 0 && dy === 0) return;

  el.animate(
    [
      { transform: `translate(${dx}px, ${dy}px)`, offset: 0 },
      { transform: "translate(0, 0)", offset: 1 },
    ],
    { duration: 350, easing: "cubic-bezier(.2,.8,.2,1)", fill: "none" },
  ).onfinish = () => {
    el.animate(
      [
        { boxShadow: "0 0 0 3px var(--color-own)" },
        { boxShadow: "0 0 0 0 transparent" },
      ],
      { duration: 150, fill: "forwards" },
    );
  };
}
```

Uses the Web Animations API (WAAPI) — no React re-render coupling, no FLIP library. `data-skill-id` attribute added to `SkillRow` is the coordination key.

**React-render timing.** The sequence is:

1. `sse.done` fires from scope-transfer endpoint
2. `refresh()` triggers a re-scan — sets new React state
3. `requestAnimationFrame` defers FLIP until after React's commit paints the new tree
4. `captureRect` already saved the OLD position before `sse.start`

This avoids `flushSync` by leveraging RAF timing. If we see coordination glitches in practice (e.g., rect captured is already post-layout due to list-filter), fall back to `flushSync(() => refresh())` per the risk row in the approved plan.

### 3.5 Modified client files

| File | Change |
|---|---|
| [components/SkillRow.tsx](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/components/SkillRow.tsx) | Add `data-skill-id="${plugin}/${skill}"` attribute; render `<PromotedFromChip>` when `provenance` present |
| [components/StatusBar.tsx](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/components/StatusBar.tsx) | Mount `<OpsCountChip>` (ref to `useStudioOps().ops.length`) |
| [components/StudioLayout.tsx](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/components/StudioLayout.tsx) | Extend RightPanel variant enum to include `"ops"`; render `<OpsDrawer>` when active |
| [api.ts](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts) | Add `promoteSkill`, `testInstallSkill`, `revertSkill`, `listStudioOps` clients |
| [types.ts](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts) | Extend `SkillInfo` with `provenance?: Provenance \| null`; add `StudioOp`, `Provenance`, `TransferEvent` types |
| skill-scanner (server) | Enrich each scan with `readProvenance(dir)` when `scope === "own"` |

## 4. SSE event contracts (exact wire format)

### 4.1 Promote / test-install / revert (POST-initiated SSE)

```
event: started
data: {"opId":"<nanoid>","skillId":"<plugin>/<skill>","fromScope":"installed","toScope":"own","sourcePath":"<abs>","destPath":"<abs>"}

event: copied
data: {"filesWritten":<N>}

event: indexed
data: {}

event: done
data: {"opId":"<nanoid>","destPath":"<abs>"}
```

On error path, instead of `done`:

```
event: error
data: {"code":"collision|missing-source|io-error","message":"<human-readable>"}
```

For `revert`, `copied` is replaced with `deleted` carrying `{filesDeleted:<N>}`.

### 4.2 Ops stream (GET-initiated, long-lived)

```
event: op
data: <StudioOp JSON>

event: heartbeat
data: {"ts":<ms>}                            ← every 3s (shared heartbeat util)
```

### 4.3 Error event — HTTP-level

Non-SSE errors (e.g., the client requests a skill that doesn't exist) return standard JSON:
```json
{ "ok": false, "error": "skill not found" }
```
with status 404. SSE channel is only used once the operation has successfully *started*.

## 5. Data shapes (authoritative types)

```ts
// types.ts (client) and studio-types.ts (server) — kept in sync manually (existing pattern)

type StudioOp = {
  id: string;
  ts: number;
  op: "promote" | "revert" | "test-install" | "skill-create" | "skill-edit" | "skill-delete" | "model-config-change";
  skillId?: string;
  fromScope?: "own" | "installed" | "global";
  toScope?: "own" | "installed" | "global";
  paths?: { source: string; dest: string };
  actor: "studio-ui";
  details?: Record<string, unknown>;
};

type Provenance = {
  promotedFrom: "installed" | "global";
  sourcePath: string;
  promotedAt: number;
  sourceSkillVersion?: string;
};

type TransferEvent =
  | { type: "started"; opId: string; skillId: string; fromScope: string; toScope: string; sourcePath: string; destPath: string }
  | { type: "copied"; filesWritten: number }
  | { type: "deleted"; filesDeleted: number }
  | { type: "indexed" }
  | { type: "done"; opId: string; destPath: string }
  | { type: "error"; code: string; message: string };
```

## 6. Undo / revert semantics

| User action | Endpoint | Server behavior | Log entry |
|---|---|---|---|
| Click "Undo" within 5s of promote toast | `POST /api/skills/:p/:s/revert` | Delete OWN dir + sidecar if provenance present | `{op:"revert", fromScope:"own", toScope:"installed"\|"global"}` |
| Click "Revert" on 30s chip | same | same | same |
| Click "Revert" on persistent badge | same | same | same |
| Attempt revert on OWN without `.vskill-meta.json` | (revert button hidden — UI gate) | — | — |
| Attempt revert on OWN with sidecar but missing dir | `POST …/revert` still safe — sidecar removed, no-op on dir | `{op:"revert", details:{idempotent:true}}` |

**Append-only invariant.** A revert **adds** a new op entry — it does NOT mutate or remove the original `promote` op. The drawer shows both, newest first. This preserves auditability.

## 7. Accessibility

| Element | A11y behavior |
|---|---|
| Context menu | Already keyboard-accessible (existing `ContextMenu.tsx` has role=menu, arrow-key nav, Esc close) — the new items inherit |
| Toast with Undo | `role="status"` (existing); Undo button is natively focusable; Esc dismisses (existing `ToastProvider` keydown handler); `AriaLive` announcement reuses existing polite region |
| OpsDrawer | `role="dialog"` `aria-modal="false"` (non-modal side-panel); focus-trap only when OPEN and user Tabs into it; Esc closes + returns focus to `OpsCountChip` |
| OpsCountChip | `role="button"`, `aria-expanded`, `aria-controls="ops-drawer"` |
| PromotedFromChip | Plain inline text with `title` attribute carrying source path; Revert action is a separate `<button>` with `aria-label="Revert <skill> to <fromScope>"` |
| FLIP | `prefers-reduced-motion: reduce` → skip the flight animation AND the 150ms pulse (both are motion-gated by `runFlip` early-return) |
| Focus outline | Reuses existing `--border-focus` token (2px) on all interactive surfaces |

## 8. Observability

**Single sink: `~/.vskill/studio-ops.jsonl`.** All three scope-transfer routes write to it synchronously before emitting the `done` SSE event. The file is human-readable (`tail -f` works) and machine-parseable (one JSON object per line).

**Existing logging untouched.** The studio currently has no structured activity log — this increment introduces it. The log is INTENTIONALLY scoped to file-changing ops (per master plan / user directive) — view events, panel toggles, etc. are out of scope. If a future increment wants broader telemetry, it can extend the `StudioOp.op` union and add new producers.

**Debug output.** Each route emits `console.error` to the studio server's stderr on exceptions (existing pattern from `skill-create-routes.ts`) — the studio CLI already surfaces stderr in its run output. No new log library.

**Metrics.** None in this increment. Deferred until we have a reason to aggregate (`wc -l ~/.vskill/studio-ops.jsonl` suffices for spot checks).

## 9. Migration: existing OWN skills without sidecar

**Problem.** A user who has been authoring skills in `./skills/` pre-0688 has NO `.vskill-meta.json` — and never should. The scanner must treat those as first-class OWN skills.

**Scanner rule.**
```ts
const provenance = await readProvenance(skillDir);  // returns null on ENOENT
const skillInfo = { …existing fields…, provenance };
```

**UI rules.**

| State | UI |
|---|---|
| `skill.scope === "own"`, `provenance == null` | No chip; no Revert button in context menu. Skill appears in OWN section normally. |
| `skill.scope === "own"`, `provenance != null` | `PromotedFromChip` visible (30s prominent, then badge-persistent); Revert button in context menu enabled. |
| User calls `/revert` via API on a skill without sidecar | Server responds 409 `{code:"no-provenance"}`. UI should never construct such a request because the button is hidden, but the server MUST gate this defensively. |

**No auto-migration.** We do not retroactively fabricate provenance for existing OWN skills. They remain "authored from scratch" from the system's perspective, which is true.

## 10. Scope boundaries

Carried forward from master plan — see `spec.md §Out of Scope` once PM completes it. Summarily: no publish-registry integration, no multi-agent beyond 0686, no log filter UI, no read-only ops in the log.

## 11. Risks & mitigations (architectural)

| Risk | Mitigation |
|---|---|
| FLIP measurement race with React commit | Use RAF timing (§3.4); fallback to `flushSync` if glitches observed. |
| `copyPluginFiltered` import path creates a `commands/` → `eval-server/` coupling | Lift `copyPluginFiltered` into `src/shared/copy-plugin-filtered.ts` and have both `commands/add.ts` and `src/studio/lib/scope-transfer.ts` import from there. Reviewed in `/sw:code-reviewer`. |
| Skill scanner re-runs are expensive (debounced at 250ms in 0685) | Acceptable — `indexed` SSE event can fire up to 250ms after `copied`. UI should not wait beyond `done` for the animation trigger. |
| Concurrent promote of the same skill from two tabs | Second request hits the collision guard (409 `collision`). Log still gets both `started`-then-`error`. No corruption. |
| `.vskill-meta.json` leaked to INSTALLED during test-install | `scope-transfer.ts` explicitly filters `.vskill-meta.json` when copying out of OWN. Unit test required. |
| `studio-ops.jsonl` grows unbounded | Out of scope; document manual rotation in README. Optional follow-up increment. |

## 12. Verification (end-to-end)

Per master plan §Verification — unchanged. Tests map to the 10 ACs in spec.md.

## 13. References

- Master design (archived): `~/.claude/plans/dreamy-mapping-kitten.md`
- **New ADRs** (this increment):
  - [ADR 0688-01: SSE Over WebSocket for Scope-Transfer](../../docs/internal/architecture/adr/0688-01-sse-over-websocket-for-scope-transfer.md)
  - [ADR 0688-02: Provenance Sidecar vs Frontmatter](../../docs/internal/architecture/adr/0688-02-provenance-sidecar-vs-frontmatter.md)
- **Related ADRs:**
  - [ADR 0674-02: Sidebar Origin Classification](../../docs/internal/architecture/adr/0674-02-sidebar-origin-classification.md) — `classifyOrigin` remains source of truth; provenance sidecar is enrichment only
  - [ADR 0674-01: Warm-Neutral Theme Tokens](../../docs/internal/architecture/adr/0674-01-warm-neutral-theme-tokens.md) — `--color-own` used in FLIP pulse + chip styling
  - [ADR 0674-03: Studio Typography System](../../docs/internal/architecture/adr/0674-03-studio-typography-system.md) — drawer & chip use existing `var(--font-mono)` for metadata
  - 0686 (tri-scope sidebar + agent picker) — extends existing SSE scanner events; no changes there
  - 0685 (rescan-published dedup) — the 250ms debounce it introduced is reused for the `indexed` SSE event timing
- **Code anchors:**
  - [src/eval-server/sse-helpers.ts](../../../repositories/anton-abyzov/vskill/src/eval-server/sse-helpers.ts) — SSE plumbing
  - [src/eval-server/router.ts](../../../repositories/anton-abyzov/vskill/src/eval-server/router.ts) — route registration pattern
  - [src/eval-server/eval-server.ts:42-53](../../../repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts) — where `registerScopeTransferRoutes` mounts
  - [src/eval-ui/src/sse.ts:35-224](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/sse.ts) — `useSSE` client hook
  - [src/eval-ui/src/components/ContextMenu.tsx:21-74](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/components/ContextMenu.tsx) — action enum + `itemsForSkill` extension point
  - [src/eval-ui/src/components/ToastProvider.tsx:23-27](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/components/ToastProvider.tsx) — `action` field already supported; no change needed
  - [src/eval-ui/src/components/ProvenanceChip.tsx](../../../repositories/anton-abyzov/vskill/src/eval-ui/src/components/ProvenanceChip.tsx) — existing agent-dir chip; NEW `PromotedFromChip` is a sibling component with different data source (sidecar vs path)
  - [src/commands/add.ts:690-720](../../../repositories/anton-abyzov/vskill/src/commands/add.ts) — `copyPluginFiltered` to be lifted into shared util
