# Implementation Plan: Studio skill detail — clickable GitHub source link

## Overview

Pure data-threading change. The receiving component (`SourceFileLink`) and the rendering site (`DetailHeader`) already exist. The platform endpoint that supplies the data already exists. The gap is two missing fields in the install receipt + four wiring changes (receipt write, receipt read, type extension, DetailHeader prop pass).

## Architecture

### Affected files

| File | Change | Why |
| ---- | ------ | --- |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts` | Add optional `repoUrl?: string \| null` and `skillPath?: string \| null` fields to `SkillInfo` (declared near line 119-238) | Frontend type contract |
| `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` | Extend `buildSkillMetadata()` (~L755-791) to read `sourceRepoUrl` + `sourceSkillPath` from the install receipt and emit them as `repoUrl` + `skillPath` on the returned metadata | Server payload |
| `repositories/anton-abyzov/vskill/src/eval-server/<install-receipt-module>` | Extend the install-receipt write path to persist `sourceRepoUrl` + `sourceSkillPath` from the platform response. Exact module location resolved during RED phase | Receipt persistence |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx` | Update lines 195-200 to pass `skill.repoUrl ?? skill.homepage` and `skill.skillPath` to AuthorLink and SourceFileLink | Component wiring |

### Data flow

```
verified-skill.com platform
   │  GET /api/v1/skills/:owner/:repo/:skill
   ▼  { repoUrl, skillPath, ... }
vskill install (eval-server route or CLI command)
   │  writes to .vskill/installs/<id>.json
   ▼  { method: "copied", sourceRepoUrl, sourceSkillPath }
buildSkillMetadata() reads receipt + frontmatter
   │
   ▼  SkillInfo { ..., repoUrl, skillPath }
GET /api/skills/:plugin/:skill response
   │
   ▼
DetailHeader.tsx byline row
   │
   ├─ AuthorLink(repoUrl)        → <a href="https://github.com/owner/repo">
   └─ SourceFileLink(repoUrl,    → <a href="https://github.com/owner/repo/blob/HEAD/skills/foo">
       skillPath)
```

### Source-of-truth resolution

`skill.repoUrl ?? skill.homepage`:
- `??` (not `||`) so empty-string `homepage` doesn't fall through.
- Receipt `repoUrl` wins because it's the canonical install-time provenance, not author-declared frontmatter intent.
- Frontmatter `homepage` is the documented secondary signal — preserves backward compatibility for skills installed before this change.

### URL construction (already implemented)

`SourceFileLink.tsx` already does the right thing:
- `canonicalRepoUrl(url)` strips `/tree/<ref>` and `/blob/<ref>[/path]` suffixes.
- `buildBlobUrl(repoUrl, skillPath)` returns `{base}/blob/HEAD/{trimmed-path}`.
- `canLink` requires HTTPS scheme.
- `target=_blank rel="noopener noreferrer"` already set.

### ADR

No new ADR. This work is incremental data threading; no architectural decision to record.

## Technology Stack

- **Frontend**: React 19 + TypeScript 5.7 (existing `eval-ui` Vite-built bundle).
- **Backend**: Node.js ESM (existing `eval-server`).
- **Tests**: Vitest (existing). Component tests use `@testing-library/react`.
- **No new dependencies.**

## Implementation Phases

Strict TDD. Each phase produces one or more failing tests, then the minimum code to make them pass.

### Phase 1 (RED → GREEN): SkillInfo type + buildSkillMetadata

1. **RED**: Add a Vitest case to `api-routes.test.ts` (or nearest existing buildSkillMetadata test) asserting that when an install receipt contains `sourceRepoUrl` + `sourceSkillPath`, the returned metadata exposes `repoUrl` + `skillPath`. Test with both fields, only one, neither.
2. **GREEN**: Add fields to `SkillMetadataFields` type and `SkillInfo` interface; wire them through `buildSkillMetadata()` reading the receipt that's already loaded for `installMethod`.

### Phase 2 (RED → GREEN): Install receipt write path

1. **RED**: Add a test that the receipt-write helper persists `sourceRepoUrl` + `sourceSkillPath` when those fields are present in the source-of-install payload.
2. **GREEN**: Extend the receipt-write helper. Locate via grep for `sourceAgent` or `installMethod` write site.

### Phase 3 (RED → GREEN): DetailHeader wiring

1. **RED**: Add a Vitest case to `DetailHeader.test.tsx` (or nearest) that renders DetailHeader with `skill = { ..., repoUrl: "https://github.com/x/y", skillPath: "skills/z" }` and asserts:
   - `data-testid="source-file-link"` exists with href `https://github.com/x/y/blob/HEAD/skills/z`.
   - `target="_blank"` and `rel="noopener noreferrer"` set.
2. **GREEN**: Update `DetailHeader.tsx` lines 195-200 to pass the new props.

### Phase 4 (REFACTOR): Verify regression cases

1. Existing tests for the copy-chip path still pass.
2. Existing tests for the homepage-only anchor path still pass.
3. `vitest run` clean across `eval-ui` + `eval-server` test suites.

### Phase 5 (Build + Release)

1. Build the `eval-ui` Vite bundle so `eval-server` serves the new component code.
2. Bump `vskill` version (patch).
3. `npm publish` (or whatever the repo's release script is — check `package.json` scripts).
4. Self-verify per AC-US1-03 and SC-003 below.

### Phase 6 (Self-verification)

1. `npx vskill@<new-version> studio` from a temporary directory.
2. Use Claude_Preview MCP tools (`preview_start`, `preview_snapshot`, `preview_click`, `preview_screenshot`) to confirm:
   - For an installed skill with known `repoUrl`: anchor is visible in the byline, clicking opens the blob URL.
   - For `greet-anton` (authored, no provenance): copy-chip path still renders, no broken anchor.

## Testing Strategy

| Layer | Test | Tool |
| ----- | ---- | ---- |
| Unit (server) | `buildSkillMetadata` reads receipt and emits `repoUrl` + `skillPath` | Vitest |
| Unit (server) | Install-receipt write persists `sourceRepoUrl` + `sourceSkillPath` | Vitest |
| Unit (client) | `DetailHeader` renders source-file anchor when `repoUrl` + `skillPath` present | Vitest + RTL |
| Unit (client) | `DetailHeader` falls back to copy-chip when only `homepage` is set + isn't HTTPS | Vitest + RTL |
| Unit (client) | `DetailHeader` falls back to copy-chip when neither is set | Vitest + RTL |
| Integration | `GET /api/skills/:plugin/:skill` response includes the new fields when receipt has them | Vitest |
| Manual / Self-verify | `npx vskill@<v> studio` shows clickable anchor on a real installed skill | preview-tools |

Coverage target: 90% (per increment metadata).

## Technical Challenges

### Challenge 1: Locating the install-receipt write path
**Solution**: grep for the literal string `installMethod` or `sourceAgent` in eval-server source. The same module that writes those will be where `sourceRepoUrl` belongs.
**Risk**: Multiple write sites (e.g. `vskill install` CLI vs. Studio install). **Mitigation**: cover both with the same test fixture; if only one needs touching for the v1 ship, document the other in tasks.md as a follow-up rather than introducing inconsistency silently.

### Challenge 2: Pre-built bundle
**Solution**: `eval-server` serves a pre-built `eval-ui` bundle (per `project_vskill_studio_runtime.md` memory — `eval-server.ts` is NOT a Vite dev server). Run the existing build script before publishing — likely `npm run build` in the `vskill` package or in `src/eval-ui/`.
**Risk**: Forgetting to rebuild ships a stale bundle. **Mitigation**: build is in tasks.md as an explicit step before npm publish; CI release script (if any) should cover it; manual self-verification will catch a missed build because the anchor won't appear.

### Challenge 3: Backward compatibility
**Solution**: All new fields are optional everywhere — receipt schema, `SkillInfo` type, component props. Pre-existing receipts without the new fields produce `undefined`, the component falls through to the existing copy-chip / homepage-anchor path.
**Risk**: None significant — the change is purely additive.
