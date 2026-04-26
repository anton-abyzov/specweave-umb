# Implementation Plan: Studio Skill Version Display — Fallback & Consistency

## Design

A single pure resolver function on the **backend** computes a non-empty version string and a provenance label for every skill. The resolver is fed three optional inputs (frontmatter version, registry currentVersion, plugin.json version) and returns `{ version: string, versionSource: 'frontmatter' | 'registry' | 'plugin' | 'default' }`. It applies the precedence chain `frontmatter > registry > plugin > "0.0.0"` and validates each candidate as semver before accepting it.

Both code paths that produce `SkillInfo` — the local scanner (`vskill/src/scanner/`) and the eval-server's `/api/skills` handler — call this resolver. The frontend trusts what the backend sends and does no fallback logic.

### Components

- **`resolveSkillVersion`** — pure function in `vskill/src/scanner/version-resolver.ts` (new file). Inputs: `{ frontmatterVersion?: string|null, registryCurrentVersion?: string|null, pluginVersion?: string|null }`. Output: `{ version: string, versionSource: 'frontmatter' | 'registry' | 'plugin' | 'default' }`. No I/O. ~30 lines.
- **Plugin.json cache** — `vskill/src/scanner/plugin-version-cache.ts` (new file). Wraps the existing read pattern from `marketplace.ts:50-66` with a `Map<pluginDir, string|null>` so a single scan reads each plugin.json at most once. ~25 lines.
- **Scanner integration** — call sites in `vskill/src/scanner/` that emit `SkillInfo` resolve via the resolver. The plugin path of each skill is determined by walking up to the nearest `.claude-plugin/plugin.json`.
- **`SkillInfo` type evolution** — `vskill/src/types.ts`: `version` becomes required `string`; new `versionSource: 'frontmatter' | 'registry' | 'plugin' | 'default'`. Backward-compat: old consumers still see a string in `version`.
- **`normalizeSkillInfo`** — `vskill/src/api.ts:226` coerces `version` to string (never null), passes `versionSource` through with a default of `'default'` if absent.
- **`VersionBadge`** — `vskill/src/eval-ui/src/components/VersionBadge.tsx`: drops the null-return branch (line 29); adds `source?: 'frontmatter' | 'registry' | 'plugin' | 'default'` prop; if `source !== 'frontmatter'` renders italic + `title` attribute with provenance message.
- **`SkillRow`** — `vskill/src/eval-ui/src/components/SkillRow.tsx:139-141`: drops `{skill.version && (...)}` conditional; always renders `<VersionBadge version={skill.version} source={skill.versionSource} ... />`.

### Data Model

`SkillInfo` (vskill/src/types.ts) — additive change:

```typescript
interface SkillInfo {
  // ... existing fields
  version: string;                     // was: string | null | undefined — now REQUIRED non-empty string
  versionSource: 'frontmatter' | 'registry' | 'plugin' | 'default';  // NEW
  currentVersion?: string;             // unchanged — installed version, separate concern
}
```

No DB schema changes. No registry API changes.

### API Contracts

No external API changes. The `/api/skills` local endpoint and the proxied `/api/v1/studio/search` continue to return `SkillInfo[]`; the only difference is `version` is now always populated and `versionSource` is included.

## Rationale

**Why a backend resolver instead of frontend fallback?** Single source of truth. The resolver is one pure function with one set of unit tests. If we put fallback logic in the frontend, both `/api/skills` and `/api/v1/studio/search` consumers would need the same logic duplicated. Backend resolution also means the data shape is consistent for any future consumer (CLI commands like `vskill list`, etc.).

**Why `versionSource` as a discriminated string instead of a boolean `isInherited`?** Three reasons:
1. The tooltip text differs by source (registry vs plugin vs default each get distinct provenance messages).
2. Future telemetry / analytics can segment by source without re-deriving.
3. Minimal extra cost — one string field per skill.

**Why italic + tooltip instead of a different color or icon?** Italic + native `title` tooltip is the lowest-risk visual treatment. It works in dark and light themes, requires no new design tokens, no new icon assets, and degrades gracefully for screen readers (tooltip text is announced). If product later wants a stronger visual distinction (e.g., color, icon), the `versionSource` field is already in the data shape — only the badge component changes.

**Why `"0.0.0"` for the default fallback?** It's an unambiguous "pre-release / undeclared" semver. `"0.0.0"` italic + tooltip "No version declared" reads as honest signal rather than fake confidence (which `"1.0.0"` would imply).

**Why no DB backfill?** The registry already defaults `currentVersion` to `"1.0.0"` on first publish (`vskill-platform/src/lib/search.ts:303,429`), so existing rows are correct. The reason badges are hidden is purely a frontend conditional, not a data gap. Touching the DB introduces risk for zero benefit.

**Why reuse `marketplace.ts:50-66` instead of refactoring?** That file already has a working `JSON.parse(readFileSync(...))` pattern over `.claude-plugin/plugin.json` with try/catch. The cache wrapper is small (~25 lines) and the original site stays untouched. Refactoring marketplace.ts to share code is out of scope and introduces broader-blast-radius risk.

**Architecture Decisions**:

- **ADR-style decision**: Resolution lives in the scanner/server (backend), not the React component. Alternative considered: frontend-side fallback chain in `SkillRow.tsx`. Rejected because it duplicates logic across API consumers and pushes test surface area to component tests.
- **ADR-style decision**: `versionSource` is a string union, not a boolean. Alternative: `isInherited: boolean`. Rejected — loses provenance detail needed for tooltip text.
- **ADR-style decision**: New file `version-resolver.ts` instead of inlining into existing scanner files. Reason: pure function with comprehensive unit tests is cheaper to verify in isolation; isolating side-effect-free logic from I/O-heavy scanner code is a long-standing pattern in this codebase.

## Technology Stack

- **Language**: TypeScript (vskill is ESM `--moduleResolution nodenext` per existing project memory; imports must use `.js` extensions)
- **Frontend**: React (vskill/src/eval-ui — Vite-built bundle served by eval-server)
- **Tests**: Vitest (existing)
- **Tools**: existing — no new dependencies

## Implementation Phases

### Phase 1: Backend resolver (RED → GREEN)
- T-001 RED: Write resolver unit tests covering all four precedence branches + edge cases (invalid semver, all-null inputs)
- T-002 GREEN: Implement `resolveSkillVersion` + `plugin-version-cache`. Wire into scanner + eval-server `/api/skills`.

### Phase 2: Type evolution
- T-003: Update `SkillInfo` type, `normalizeSkillInfo`, and any TypeScript callers that destructure `skill.version` assuming it could be null.

### Phase 3: Frontend (RED → GREEN)
- T-004 RED: VersionBadge + SkillRow component tests (source-aware styling, tooltip text, no-null-return).
- T-005 GREEN: Update `VersionBadge.tsx` and `SkillRow.tsx` per design above.

### Phase 4: Manual verification
- T-006: Start `npx vskill studio`, verify every AVAILABLE skill shows a badge with correct styling + tooltip.

## Testing Strategy

- **Unit (Vitest)**: `resolveSkillVersion` — every precedence branch, semver validation, all-null fallback. Target 100% branch coverage on the resolver itself.
- **Component (Vitest + Testing Library)**: `VersionBadge` — renders with each `versionSource` value, tooltip text matches expected provenance message, never returns null.
- **Integration (Vitest)**: scanner produces `SkillInfo` with required `version` string for fixtures (a) skill with frontmatter, (b) skill without frontmatter inside plugin dir, (c) skill without frontmatter or plugin (default).
- **E2E (manual)**: studio sidebar visual check per Verification section in the plan file.

## Technical Challenges

### Challenge 1: Plugin path discovery for a given skill
**Solution**: Walk up from the skill directory looking for `.claude-plugin/plugin.json`. The existing scanner already knows skill source paths.
**Risk**: Skills outside any plugin (e.g., user-created in `~/.claude/skills/foo/`). **Mitigation**: When no plugin.json is found and registry has no entry, resolver falls through to `'default'` → `"0.0.0"`.

### Challenge 2: Scanner already runs frequently — additional plugin.json reads cost
**Solution**: Per-scan in-memory cache (`Map<pluginDir, string|null>`) populated on first access.
**Risk**: Cache invalidation if plugin.json changes mid-session. **Mitigation**: Cache is per-scan (recreated each invocation), so changes are picked up on the next scan — same staleness window as the rest of the scanner.

### Challenge 3: TypeScript breaking change — `version` was nullable, now required
**Solution**: Audit all callers of `SkillInfo.version` and remove any null-handling that becomes dead code.
**Risk**: Missed call sites cause type errors at build. **Mitigation**: TypeScript compiler will surface every site; fix in same task.
