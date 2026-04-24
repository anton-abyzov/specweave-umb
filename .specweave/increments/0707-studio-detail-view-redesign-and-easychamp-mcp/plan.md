# Implementation Plan — 0707 Skill Studio Detail View Redesign + EasyChamp MCP

## Design

### Four disjoint workstreams with soft coupling
This increment is implemented by four parallel agents with no shared-file writes:

| Workstream | Agent | Owns (exclusive write) | Reads |
|------------|-------|-----------------------|-------|
| A Studio frontend | **studio-frontend** | `vskill/src/eval-ui/src/**` | spec.md, api.ts types |
| B Eval-server API | **studio-backend** | `vskill/src/eval-server/**`, new fixtures under `vskill/e2e/fixtures/` | spec.md |
| C MCP fixture + registry | **studio-fixture** | `vskill/plugins/easychamp/**`, `vskill/src/eval/mcp-detector.ts` | spec.md |
| D EasyChamp MCP server | **easychamp-mcp** | `repositories/anton-abyzov/easychamp-mcp/**` (new repo) | spec.md |

The only cross-workstream contract is the EasyChamp tool-name list (`easychamp_generate_league`, `easychamp_generate_tournament`, `easychamp_generate_bracket`, `easychamp_create_schedule`, `easychamp_enter_results`). This is frozen in the spec (US-005, US-006) so no CONTRACT_READY handshake is strictly needed — studio-fixture and easychamp-mcp can both code against the frozen names immediately.

### A. Studio Frontend Architecture

**Component tree (new):**
```
RightPanel.tsx
├─ DetailHeader.tsx (sticky, includes VersionBadge + AuthorLink + SourceFileLink)
├─ TabBar.tsx (flat, 9 tabs)
└─ <active-tab content>
    ├─ Overview → SkillOverview.tsx
    │   └─ MetricCard.tsx × 8 (responsive grid)
    ├─ Editor → EditorTab (existing, unchanged)
    ├─ Tests → TestsTab (existing, unchanged)
    ├─ Run → RunTab (existing, unchanged)
    ├─ Activation → ActivationTab (existing, unchanged)
    ├─ History → HistoryTab (existing, unchanged)
    ├─ Leaderboard → LeaderboardTab (existing, unchanged)
    ├─ Deps → McpDependencies.tsx (existing, unchanged)
    └─ Versions → VersionHistoryPanel.tsx (existing, unchanged)
```

**New files:**
- `vskill/src/eval-ui/src/components/SkillOverview.tsx` — replaces inline `MetadataTab` wiring in `RightPanel`; renders header + 8-card metric grid.
- `vskill/src/eval-ui/src/components/MetricCard.tsx` — port of `vskill-platform/src/app/components/MetricCard.tsx`, same CSS-var styling.
- `vskill/src/eval-ui/src/components/VersionBadge.tsx` — inline-flex chip used in header, sidebar rows, test runs, activation log.
- `vskill/src/eval-ui/src/components/AuthorLink.tsx` — `<a>` to `https://github.com/{owner}` when `repoUrl` parses, else `CopyButton`.
- `vskill/src/eval-ui/src/components/SourceFileLink.tsx` — `{repoUrl}/blob/HEAD/{path} ↗` or `CopyButton` with absolute path.
- `vskill/src/eval-ui/src/components/BenchmarkInfoPopover.tsx` — ℹ popover with methodology text + tab-navigation links.

**Modified files:**
- `RightPanel.tsx` (lines ~183-422): replace 2-tab layout with 9-tab `TabBar` driven by `PanelId`.
- `TabBar.tsx`: accept `overview` + `versions` into the existing Build/Evaluate/Insights group structure or add new "Summary" group.
- `DetailHeader.tsx` (lines ~171-214): slot in VersionBadge (visible state), AuthorLink, SourceFileLink; demote the current plain-text author/version rendering.
- `LeftPanel.tsx` (skill sidebar rows): render `<VersionBadge />` next to skill name.
- `TestsTab` / `ActivationTab` result cards: render `<VersionBadge />` on each run entry.
- `pages/workspace/VersionHistoryPanel.tsx`: consume updated `api.getSkillVersions` response shape if it changes.
- `api.ts`: add/adjust type annotations for the 4 backend envelopes.

**Responsive grid (CSS):**
```css
.skill-overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
}
.skill-overview-grid .metric-card {
  padding: 1rem;
  word-break: break-word;
  overflow-wrap: anywhere;
}
```
Auto-fit + minmax avoids the need for explicit breakpoints — columns drop naturally at 4→3→2→1 as width shrinks. Explicit `@media` rules adjust typography and card density.

### B. Eval-Server API Architecture

All four endpoints live in `vskill/src/eval-server/api-routes.ts` and already exist — the work is hardening, not adding. Pattern for each:

```typescript
router.get("/api/skills/:plugin/:skill/<artifact>", async (req, res) => {
  try {
    const payload = await load<Artifact>(req.params);
    return res.json(payload);
  } catch (err) {
    if (isMissingFile(err)) {
      return res.json(emptyEnvelope());   // 200 with {exists:false, count:0, data:[]}
    }
    if (isValidationError(err)) {
      return res.status(422).json({ error: err.details });
    }
    // real 500 only for genuine I/O errors
    return res.status(500).json({ error: classifyError(err) });
  }
});
```

**Consistent envelope shape:**
```typescript
// versions
{ versions: VersionEntry[], count: number, source: "git" | "none" }
// benchmark/latest
BenchmarkPayload | null  // 200 null preferred to 404
// evals
{ tasks: EvalTask[], exists: boolean }
// activation-history
{ runs: ActivationRun[], count: number }
```

**Router pattern fix (B2):** `vskill/src/eval-server/router.ts` — audit the `:plugin` and `:skill` param extraction. If the pattern is a simple regex like `/^([^/]+)\/([^/]+)$/`, plugin slugs with dashes already match. But if the pattern uses `\w+`, `google-workspace` will fail. Fix by using `[^/]+` throughout.

**Git-safety (B1):** wrap `execSync("git log ...")` in try/catch; on failure, set `X-Skill-VCS: unavailable` response header and return `{ versions: [], count: 0, source: "none" }`. Do NOT attempt to detect `.git` directory upfront — just catch the failure.

### C. MCP Fixture + Registry Architecture

**New fixture layout:**
```
vskill/plugins/easychamp/skills/tournament-manager/
├─ SKILL.md                  # frontmatter declares mcp-deps: [easychamp]
├─ references/
│   └─ schemas.md            # tool input/output schemas reference
└─ evals/
    └─ evals.yaml            # 1 smoke eval per tool (5 total) — run in demo mode
```

**MCP Registry entry** (appended to existing array in `mcp-detector.ts` lines 25-80):
```typescript
{
  server: "EasyChamp",
  prefixes: ["easychamp_"],
  url: "https://easychamp.com/mcp",
  transport: "stdio",
  docsUrl: "https://easychamp.com/docs/mcp",
  configSnippet: {
    easychamp: {
      command: "npx",
      args: ["-y", "easychamp-mcp"],
      env: { EASYCHAMP_API_KEY: "${EASYCHAMP_API_KEY}" }
    }
  }
}
```

The existing auto-detection (scans skill body for `easychamp_*` patterns) picks up the fixture automatically. The explicit `mcp-deps: [easychamp]` frontmatter field doubles as an assertion the detector can validate against.

### D. EasyChamp MCP Server Architecture

**Repo layout (new `repositories/anton-abyzov/easychamp-mcp/`):**
```
easychamp-mcp/
├─ package.json              # name: "easychamp-mcp", bin: {"easychamp-mcp":"dist/index.js"}
├─ tsconfig.json             # moduleResolution: nodenext, .js import extensions
├─ .gitignore
├─ .env.example              # EASYCHAMP_API_KEY=..., EASYCHAMP_API_URL=..., EASYCHAMP_DEMO=1
├─ README.md
├─ src/
│   ├─ index.ts              # shebang, boots stdio MCP server
│   ├─ server.ts             # registers all 5 tools
│   ├─ tools/
│   │   ├─ generate-league.ts
│   │   ├─ generate-tournament.ts
│   │   ├─ generate-bracket.ts
│   │   ├─ create-schedule.ts
│   │   └─ enter-results.ts
│   ├─ auth/
│   │   ├─ api-key.ts        # reads EASYCHAMP_API_KEY, returns {missing|present, headers}
│   │   └─ oauth.ts          # scaffolded, disabled (stretch)
│   ├─ client/
│   │   └─ easychamp-client.ts   # fetch wrapper with auth header + timeout + retry
│   ├─ mocks/
│   │   └─ demo-responses.ts # believable mock payloads for demo mode
│   └─ errors.ts             # structured error helpers
├─ test/
│   ├─ tools.test.ts         # per-tool unit tests
│   ├─ server.test.ts        # stdio integration test
│   └─ auth.test.ts
└─ .github/
    └─ workflows/
        └─ test.yml          # CI: lint + vitest
```

**Tool execution flow:**
```
MCP call → Zod-validated input → auth.apiKey() →
  { mode: "live"   → easychampClient.fetch(endpoint, body) → response
  | mode: "demo"   → mocks.demoResponses[toolName](input) → response
  | mode: "no-auth" → structuredError("Missing EASYCHAMP_API_KEY, see https://easychamp.com/account/api-keys") }
```

## Rationale

1. **Why 9 flat tabs instead of keeping Overview + Versions as top-level with nested Workspace inside Overview?**
   The nested structure is the direct cause of the user's complaint: to reach Tests/Run/etc. you must scroll past the whole Overview. Flattening removes the hierarchy entirely. The alternative (making Overview shorter via collapse) still leaves the tab bar out of view on narrow viewports and still makes the user click twice (Overview → nested tab). Flat wins on every dimension.

2. **Why port `MetricCard` instead of building a new component?**
   The existing `vskill-platform/src/app/components/MetricCard.tsx` uses the same CSS-variable design language as the Skill Studio (both apps share the same `globals.css` token system). Porting preserves visual consistency with the public portal — which is what the user referenced as the "best-in-class" target.

3. **Why `grid-template-columns: repeat(auto-fit, minmax(180px, 1fr))` instead of explicit breakpoints?**
   Auto-fit gives natural column dropping at arbitrary widths — more robust than hard breakpoints that can skip a column count when the viewport falls between them. Explicit `@media` rules remain for typography and header layout, which benefit from sharper transitions.

4. **Why 200-empty envelopes instead of 404 for missing artifacts?**
   404 is semantic ("this URL doesn't exist") — incorrect when the endpoint exists but the fixture skill simply hasn't generated that artifact yet. The Studio UI needs to distinguish "I can't render because the feature is absent" (normal case) from "I can't render because the endpoint is broken" (bug). Conflating them with 404 makes every fixture skill show red errors for routine empty state.

5. **Why build the EasyChamp MCP in a separate repo (workstream D) rather than inside `vskill/plugins/`?**
   MCPs are Claude-ecosystem citizens independent of SpecWeave. Publishing EasyChamp MCP to npm requires its own repo with its own `package.json` so `npx -y easychamp-mcp` works for users who don't use SpecWeave. The fixture skill (workstream C) declares the dependency; the MCP (workstream D) fulfills it — but they are loose-coupled.

6. **Why demo mode (`EASYCHAMP_DEMO=1`)?**
   Without demo mode, the MCP can't be used until the real EasyChamp backend exposes the required endpoints. The showcase fixture in the Deps tab would be blocked on an unrelated backend project. Demo mode lets the showcase work today and smoothly transitions to live mode once the key is provided.

7. **Why Zod for tool input schemas instead of hand-rolled validation?**
   Zod schemas auto-generate the JSON Schema the MCP protocol requires, eliminating drift between runtime validation and the `ListTools` response. It's also the dominant pattern in the MCP ecosystem (nearly every community MCP uses it).

8. **Why not publish to npm in this increment?**
   Build + pack verifies the package is shippable; publish is a separate, governance-heavy step (npm credentials, scope decisions, semver policy). Keeping it out of this increment avoids coupling a UX fix to a release operation.

## Technology Stack

- **Frontend**: React 18 + TypeScript + CSS variables (no Tailwind) + Geist fonts (existing).
- **Backend**: Node.js + existing eval-server Router (Express-compatible) + Prisma client (existing).
- **MCP server**: Node.js (ESM) + TypeScript (`moduleResolution: nodenext`) + `@modelcontextprotocol/sdk` + Zod + undici (fetch).
- **Tests**: Vitest (unit + integration), Playwright (E2E).

## Implementation Phases

Per `sw:team-lead`, all four agents run in parallel from the start — no strict Phase 1 → Phase 2 split, because the cross-workstream tool-name contract is frozen in the spec.

| Phase | Agents | Duration estimate |
|-------|--------|-------------------|
| Plan & approve | main (done) | — |
| Parallel implementation | studio-frontend + studio-backend + studio-fixture + easychamp-mcp | ~4 hours wall clock |
| Each agent runs its own TDD loop | — | — |
| Closure | sw-closer (spawned by team-lead) | ~20 min |

## Testing Strategy

- **Unit (Vitest)**: every new component (SkillOverview, MetricCard, VersionBadge, AuthorLink, SourceFileLink, BenchmarkInfoPopover) has rendering + interaction tests. Every MCP tool has happy/error/demo tests. MCP detector has a new test for EasyChamp detection. Router pattern has tests for dash-containing slugs. Each endpoint has tests for missing/malformed/valid artifact cases.
- **Integration (Vitest)**: eval-server endpoint tests using a temp fixture dir (git and non-git). MCP server integration test boots a child process and exchanges ListTools/CallTool over stdio.
- **E2E (Playwright)**: Studio redesign tests (tabs visible, deep-links, benchmark popover, Deps tab shows EasyChamp), responsive tests (480/768/1024/1440 viewports).

## Technical Challenges

### Challenge 1: Router param extraction for dash-containing plugin slugs
**Solution**: audit `vskill/src/eval-server/router.ts` pattern and ensure `[^/]+` (not `\w+` or `[a-z]+`). Add explicit test for `google-workspace/gws`.
**Risk**: other endpoints may have the same issue — fix the base pattern once.

### Challenge 2: Nested SkillWorkspaceInner → flat tabs migration preserves existing tab content
**Solution**: the `PanelId` union already drives all 7 inner tabs; we only need to move the mount point from "inside Overview" to "directly under RightPanel". The inner tab components don't change.
**Risk**: URL hash handling (`?panel=tests`) is currently handled inside `SkillWorkspaceInner`; needs to hoist one level.

### Challenge 3: EasyChamp MCP demo mode realism
**Solution**: `src/mocks/demo-responses.ts` returns deterministic fake data (stable leagueId, tournamentId seeds) so evals pass reproducibly.
**Risk**: drift between mock schemas and real API once the latter ships — mitigated by Zod schemas being the single source of truth (mocks satisfy the same schemas).

### Challenge 4: Consistent empty-state envelopes without breaking existing callers
**Solution**: envelopes are additive — existing callers that ignore new fields continue to work. `api.ts` type annotations are updated; callers that consume them get compile-time signals.
**Risk**: minor: low.

## ADR References

No new ADRs in this increment — the decisions above stay internal to the increment. If EasyChamp MCP evolves into a broader pattern (multiple custom MCPs for EasyChamp-style third-party integrations), a follow-up increment would write ADR-0041 "Custom MCP hosting + auth pattern".
