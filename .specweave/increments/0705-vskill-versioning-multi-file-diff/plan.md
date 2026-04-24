---
increment: 0705-vskill-versioning-multi-file-diff
title: "Fix vskill versioning pipeline + GitHub-backed multi-file diff"
---

# Implementation Plan: Fix vskill versioning pipeline + GitHub-backed multi-file diff

## Design

### System Overview

Two code locations change. Everything else (Prisma schema, KV bindings, Queue consumers, Neon DB, crawl-worker VMs) stays as-is.

```
repositories/anton-abyzov/vskill-platform/   ← Next.js 15 + CF Workers + Prisma
  src/app/api/v1/submissions/route.ts                        [modify]
  src/lib/submission/upsert.ts                               [modify]
  src/lib/submission/publish.ts                              [modify]
  src/app/api/v1/admin/rescan-published/route.ts             [modify]
  src/app/api/v1/skills/[o]/[r]/[s]/versions/[v]/route.ts    [modify]
  src/app/api/v1/skills/[o]/[r]/[s]/versions/compare/        [NEW route]
  src/app/skills/[o]/[r]/[s]/versions/compare/page.tsx       [modify]
  src/lib/github/compare.ts                                  [NEW module]
  src/lib/diff/parse-unified-patch.ts                        [NEW module]
  scripts/backfill-skill-version-ghosts.ts                   [NEW script]
  wrangler.jsonc                                             [secret binding]

repositories/anton-abyzov/vskill/            ← Node 22 ESM CLI
  src/commands/diff.ts                                       [NEW command]
  src/index.ts                                               [register command]
  src/api/client.ts                                          [add compareVersions()]
```

### Phase A — Platform: Unblock republish (US-001)

**A1. Route `POST /api/v1/submissions` through `upsertSubmission` with P2002 caught.**

Today `src/app/api/v1/submissions/route.ts:719` calls `prisma.submission.create()` directly inside a try/catch that re-throws. Replace with an `upsertSubmission()` call. The upsert helper already knows how to catch P2002 and map existing row state to a `kind`. Removing the raw `create()` call kills the 500.

**A2. Harden `upsertSubmission` for the "content changed" case.**

In `src/lib/submission/upsert.ts:101-120`, the PUBLISHED branch currently returns `{kind: "verified"}` unconditionally. Add:

```ts
if (existing.state === "PUBLISHED") {
  const latestVersion = await db.skillVersion.findFirst({
    where: { skillId: existing.skillId },
    orderBy: { createdAt: "desc" },
    select: { contentHash: true }
  });
  const newHash = await sha256OfSkillMd(existing.repoUrl, input.skillPath); // fetch from GitHub
  if (latestVersion && newHash === latestVersion.contentHash) {
    return { kind: "verified", skillId: existing.skillId, skillName: existing.skillName };
  }
  await db.submission.update({
    where: { id: existing.id },
    data: { state: "RECEIVED", updatedAt: new Date() }
  });
  await env.SUBMISSION_QUEUE.send({ submissionId: existing.id });
  return { kind: "requeued", submissionId: existing.id };
}
```

**A3. Populate `manifest` on SkillVersion.create().**

In `src/lib/submission/publish.ts:337-356`, the `create()` payload currently omits `manifest`. The `treeFiles` map (line 264) already has every file's content in memory. Add:

```ts
manifest: Object.entries(treeFiles).map(([path, content]) => ({
  path,
  sha256: sha256(content),
  size: content.length
})),
```

This fills the column that was declared but never written. No migration — column already exists.

**A4. Replace `buildDiffSummary()` with a manifest-aware version.**

Current implementation (`publish.ts:32-45`) returns `"Content updated (+N lines)"` — just a line-count. Replace with a per-file summary derived from old vs new manifest:

```ts
function buildDiffSummary(oldManifest: Manifest | null, newManifest: Manifest): string {
  if (!oldManifest) return `${newManifest.length} files`;
  const oldByPath = new Map(oldManifest.map(f => [f.path, f.sha256]));
  const newByPath = new Map(newManifest.map(f => [f.path, f.sha256]));
  let added = 0, modified = 0, removed = 0;
  for (const [p, sha] of newByPath) {
    if (!oldByPath.has(p)) added++;
    else if (oldByPath.get(p) !== sha) modified++;
  }
  for (const [p] of oldByPath) if (!newByPath.has(p)) removed++;
  const parts = [];
  if (added) parts.push(`+${added} new`);
  if (modified) parts.push(`~${modified} modified`);
  if (removed) parts.push(`-${removed} removed`);
  return parts.length ? parts.join(", ") : "no file changes";
}
```

### Phase B — Platform: Stop ghost rows (US-002)

**B1. Admin rescan: skip row creation on unchanged content.**

In `src/app/api/v1/admin/rescan-published/route.ts`, before `db.skillVersion.create()`, load the latest SkillVersion and compare `contentHash`:

```ts
const latest = await db.skillVersion.findFirst({ where: { skillId }, orderBy: { createdAt: "desc" }});
const rescanHash = sha256(fetchedContent);
if (latest && latest.contentHash === rescanHash) {
  await db.skillVersion.update({ where: { id: latest.id }, data: { certTier, certScore, certifiedAt: new Date() }});
  return { updated: true, created: false };
}
// else: create a new row with all fields populated (same payload as A3)
```

**B2. Backfill script: `scripts/backfill-skill-version-ghosts.ts`.**

```
npm run backfill:ghost-versions -- --dry-run
npm run backfill:ghost-versions -- --apply
```

Queries: `SELECT * FROM SkillVersion WHERE content = '' OR contentHash = '' ORDER BY skillId, createdAt`.

For each row:
- If `gitSha` is non-empty and the repo URL is GitHub, refetch SKILL.md at that SHA; repopulate `content`, `contentHash`, `treeHash`, `manifest`.
- Else if a sibling row on the same `skillId` has a valid `contentHash` and identical `certTier`/`certScore`, delete the ghost.
- Else flag the row ID in a `to-review.log` for manual action.

Dry-run prints proposed actions without writing.

### Phase C — Platform: GitHub-backed compare endpoint (US-003, US-005)

**C1. New module `src/lib/github/compare.ts`.**

```ts
export async function githubCompare(opts: {
  owner: string; repo: string; base: string; head: string;
  token?: string; kv?: KVNamespace;
}): Promise<GitHubCompareResponse | null> {
  if (!isValidSha(opts.base) || !isValidSha(opts.head)) return null;
  const cacheKey = `compare:${opts.owner}/${opts.repo}:${opts.base}...${opts.head}`;
  const cached = await opts.kv?.get(cacheKey, "json");
  if (cached) return cached;
  const headers: Record<string, string> = { "User-Agent": "verified-skill-bot" };
  if (opts.token) headers["Authorization"] = `Bearer ${opts.token}`;
  const r = await fetch(`https://api.github.com/repos/${opts.owner}/${opts.repo}/compare/${opts.base}...${opts.head}`, { headers });
  if (!r.ok) return null;
  const data = await r.json();
  await opts.kv?.put(cacheKey, JSON.stringify(data), { expirationTtl: 300 });
  return data;
}

export function isValidSha(s: string): boolean { return /^[0-9a-f]{7,40}$/i.test(s); }

export function filterBySkillPath(files: GitHubFile[], skillPath: string | null): GitHubFile[] {
  if (!skillPath) return files;
  const prefix = skillPath.replace(/\/SKILL\.md$/, "").replace(/\/$/, "") + "/";
  return files.filter(f =>
    f.filename.startsWith(prefix) ||
    f.filename === `${prefix}SKILL.md`.replace(/^\/+/, "")
  );
}
```

**C2. New route `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/compare/route.ts`.**

```ts
export async function GET(req: Request, ctx: RouteParams) {
  const { owner, repo, skill } = await ctx.params;
  const url = new URL(req.url);
  const fromV = url.searchParams.get("from");
  const toV = url.searchParams.get("to");
  const [fromRow, toRow] = await Promise.all([getVersion(skill, fromV), getVersion(skill, toV)]);
  const repoUrl = await getSkillRepoUrl(skill);
  const isGitHub = /github\.com/.test(repoUrl);
  if (!isGitHub || !fromRow.gitSha || !toRow.gitSha || !isValidSha(fromRow.gitSha) || !isValidSha(toRow.gitSha)) {
    return NextResponse.json({
      source: "local-content",
      files: [{ filename: "SKILL.md", status: "modified", patch: buildLcsPatch(fromRow.content, toRow.content), additions, deletions }]
    });
  }
  const ghRepo = parseGitHubOwnerRepo(repoUrl);
  const compare = await githubCompare({ ...ghRepo, base: fromRow.gitSha, head: toRow.gitSha, token: env.GITHUB_TOKEN, kv: env.KV });
  if (!compare) return fallbackToLocal();
  const skillPath = await getSkillPath(skill);
  const files = filterBySkillPath(compare.files, skillPath);
  return NextResponse.json({
    source: "github",
    baseSha: compare.base_commit.sha,
    headSha: compare.merge_base_commit.sha,
    files: files.map(f => ({ filename: f.filename, status: f.status, additions: f.additions, deletions: f.deletions, patch: truncate(f.patch, 1_000_000) })),
    githubCompareUrl: `https://github.com/${ghRepo.owner}/${ghRepo.repo}/compare/${fromRow.gitSha}...${toRow.gitSha}`
  });
}
```

**C3. Expose manifest/treeHash/gitSha on version detail endpoint.**

In `src/app/api/v1/skills/[o]/[r]/[s]/versions/[v]/route.ts:27-40`, extend `select:`:

```ts
select: { ...existing, treeHash: true, manifest: true, gitSha: true }
```

Parse `manifest` JSON if stored as string.

### Phase D — Platform: Compare UI (US-003)

**D1. Update `src/app/skills/[o]/[r]/[s]/versions/compare/page.tsx`.**

Current page fetches `/versions/:v` twice to get `content`. Replace with one fetch to the new `/compare` endpoint. Render:

- Left column (250px): file tree with `status` icon + `filename` + `+N/-M` badge. Clicking sets `selectedFile`.
- Right column: existing `UnifiedDiff` / `SideBySideDiff` renderer, fed with `diff = parseUnifiedPatch(files[selectedFile].patch)` instead of `computeDiff(fromContent, toContent)`.
- Banner if `source === "local-content"`: "Showing SKILL.md diff only — full bundle diff unavailable for this version."
- "View on GitHub" link when `source === "github"`, using `githubCompareUrl`.
- Preserve unified/side-by-side toggle (per selected file).

**D2. New helper `src/lib/diff/parse-unified-patch.ts`.**

Parses GitHub's `patch` strings into the existing `DiffLine[]` shape that the current renderer understands. Keeps `computeDiff()` unchanged for the fallback path.

### Phase E — CLI: `vskill diff` (US-004)

**E1. New command `vskill/src/commands/diff.ts`.**

```ts
export async function diffCommand(skill: string, from: string, to: string, opts: DiffOpts) {
  const slug = parseSkillSlug(skill);
  const url = `${API_BASE}/api/v1/skills/${slug}/versions/compare?from=${from}&to=${to}`;
  const res = await fetch(url);
  if (!res.ok) { process.stderr.write(`Compare failed: ${res.status}\n`); process.exit(1); }
  const data = await res.json();
  let files = data.files;
  if (opts.files) files = files.filter((f: any) => minimatch(f.filename, opts.files));
  if (opts.json) { process.stdout.write(JSON.stringify({...data, files}, null, 2)); return; }
  if (opts.stat) { printStat(files); return; }
  for (const f of files) printColorDiff(f);
}
```

`printColorDiff` uses raw ANSI codes: `\x1b[32m` (green), `\x1b[31m` (red), `\x1b[90m` (grey), `\x1b[0m` (reset). Windows Terminal and modern cmd.exe handle these natively. CI/non-TTY: no colors (detect via `process.stdout.isTTY`).

Zero shell-outs. Pure `fetch()` + `stdout.write()`. Works on PowerShell, cmd.exe, Bash, Zsh.

**E2. Register command in `vskill/src/index.ts`:**

```ts
program.command("diff <skill> <from> <to>")
  .option("--stat", "summary only")
  .option("--json", "machine-readable")
  .option("--files <pattern>", "glob filter")
  .action(diffCommand);
```

### Phase F — Integration Test

**F1. Golden test case using scout `4f2285d...71a9132`.**

Mock `fetch("https://api.github.com/...")` to return a fixture recorded from the real call (trimmed to files under `plugins/skills/skills/scout/`). Assert:
- `files.length === 4`
- `files[0].filename.endsWith("scout/SKILL.md")` (or similar depending on filter)
- `files[0].patch.includes("Skill Discovery")` (known substring from the real commit)
- Totals: `+additions === 590`, `-deletions === 8`.

Run as part of the CF Worker test suite (vitest).

## Rationale

### Why GitHub as source of truth (not R2)

The platform already delegates fetching SKILL.md content to GitHub during submission. Scaling that to "fetch the full bundle diff from GitHub at a stored SHA" reuses the trust boundary, avoids the cost + complexity of a blob store, and gives users a "View on GitHub" deep link as a bonus. The only platform-side obligation is storing `gitSha` correctly and writing `manifest` — both are minor tweaks to existing code paths.

### Why LCS diff stays as fallback

Removing LCS risks breaking the UI for:
- Historical rows where `gitSha` was never populated or is literal `"latest"`.
- Non-GitHub repos (GitLab, Bitbucket, self-hosted).
- GitHub outages / rate-limit 429.

Keeping LCS as fallback is ~40 lines of existing working code. Cost is negligible; resilience is significant. A future increment can add GitLab/Bitbucket compare APIs.

### Why the backfill is idempotent + dry-run

The ghost-version rows are a data integrity bug. Blindly deleting rows could lose recoverable history. Dry-run + apply split lets the operator review exactly what will change before committing. Idempotent re-runs are safe because the detection predicate (`content = '' OR contentHash = ''`) is stable across invocations.

### Why CLI uses raw ANSI codes (not `chalk`)

`chalk` adds a dep, enables TTY detection but adds complexity for Windows compat. Raw ANSI sequences are 3 constants and a TTY check. Windows Terminal, PowerShell 7+, and modern cmd.exe all render ANSI natively. For non-TTY (CI, piped output), skip colors entirely.

### Why manifest is JSON blob, not normalized table

Per-file records never need to be queried in isolation — they're only read as part of a SkillVersion row or diff computation. A `File` table with 4 columns for every skill version row would multiply storage 3-10x with no query benefit. JSON blob in Prisma's existing `Json?` column is cheaper and already schema-compatible.

### ADRs referenced

- **ADR-002 (Integrity)** — `treeHash` already in use, `manifest` finally populated (was declared for this purpose).
- **ADR-003** — `FOR UPDATE` lock on Skill row during publish is preserved.
- **ADR-004** — SemVer components remain managed by existing `parseSemver` logic.

### Rollout order

1. Phase A (republish fix) — unblocks users, low risk since it only changes error-handling path.
2. Phase B1 (admin rescan) — stops the bleeding of new ghost rows.
3. Phase B2 (backfill) — cleans up historical ghost rows. Run in dry-run first, review log, then apply.
4. Phase C + D + E (compare + CLI) — additive, cannot break existing UI.
5. Phase F (tests) — runs in CI alongside merge.

Each phase is independently deployable. Phase A alone is a worthwhile hotfix.
