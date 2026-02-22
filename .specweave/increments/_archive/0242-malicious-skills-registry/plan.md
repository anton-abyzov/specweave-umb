# Plan: 0242 — Malicious Skills Registry & Security Audits Dashboard

## Architecture Overview

This feature spans two repos (vskill-platform + vskill CLI) across three domains: backend API, frontend UI, and CLI integration. The core idea: a public security audits dashboard + a blocklist that prevents installation of known-malicious skills.

```
┌─────────────────────────────────────────────────────┐
│                verified-skill.com                     │
│                                                       │
│  /audits  ──────── Public audit results table         │
│  /blocklist ────── Known-malicious skills registry    │
│                                                       │
│  API:                                                 │
│  GET  /api/v1/audits ────── Paginated scan results    │
│  GET  /api/v1/blocklist ─── Queryable blocklist       │
│  POST /api/v1/admin/blocklist ── Admin: add entry     │
│  POST /api/v1/admin/scan-external ── Scan ext. skill  │
└───────────────────┬─────────────────────────────────┘
                    │
                    │ HTTP (cached)
                    │
┌───────────────────▼─────────────────────────────────┐
│                vskill CLI                             │
│                                                       │
│  vskill add <source>                                  │
│    └── blocklist check (API + local cache)            │
│        ├── BLOCKED → refuse with reason               │
│        └── CLEAR → proceed to Tier 1 scan             │
│                                                       │
│  vskill blocklist                                     │
│    ├── list ─── show cached blocklist                 │
│    ├── sync ─── refresh from API                      │
│    └── check <name> ── check single skill             │
└─────────────────────────────────────────────────────┘
```

## Technical Approach

### Phase 1: Database & API (vskill-platform)

**New Prisma model: `BlocklistEntry`**

```prisma
model BlocklistEntry {
  id            String   @id @default(cuid())
  skillName     String
  sourceUrl     String?  // original repo or registry URL
  sourceRegistry String? // "clawhub", "skills.sh", "skillsmp", etc.
  contentHash   String?  // SHA-256 of malicious SKILL.md content
  threatType    String   // "prompt-injection", "credential-theft", "reverse-shell", etc.
  severity      String   // "critical", "high", "medium"
  reason        String   // human-readable explanation
  evidenceUrls  String[] // links to reports, screenshots, articles
  discoveredAt  DateTime @default(now())
  discoveredBy  String?  // researcher name or "automated-scan"
  addedById     String?
  addedBy       Admin?   @relation(fields: [addedById], references: [id])
  isActive      Boolean  @default(true)
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  @@index([skillName])
  @@index([contentHash])
  @@index([isActive])
}
```

**API endpoints:**

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/api/v1/audits` | Public | Paginated list of all scan results with skill info |
| GET | `/api/v1/blocklist` | Public | Full blocklist (cacheable, ETag) |
| GET | `/api/v1/blocklist/check` | Public | Check single skill: `?name=X` or `?hash=Y` |
| POST | `/api/v1/admin/blocklist` | REVIEWER+ | Add entry to blocklist |
| DELETE | `/api/v1/admin/blocklist/[id]` | SUPER_ADMIN | Remove entry |
| POST | `/api/v1/admin/scan-external` | REVIEWER+ | Submit external skill URL for scanning |

**Audits endpoint** joins `ScanResult` + `Submission` + `Skill` to produce:
```json
{
  "audits": [
    {
      "skillName": "code-review-assistant",
      "repoUrl": "https://github.com/...",
      "tier1": { "verdict": "PASS", "score": 94, "criticalCount": 0, ... },
      "tier2": { "verdict": "PASS", "score": 88, ... },
      "overallStatus": "PUBLISHED",
      "verifiedAt": "2026-02-19T...",
      "blocked": false
    }
  ],
  "total": 142,
  "limit": 50,
  "offset": 0
}
```

**Blocklist API** returns lightweight, cacheable JSON:
```json
{
  "entries": [
    {
      "skillName": "polymarket-traiding-bot",
      "contentHash": "sha256:abc123...",
      "threatType": "credential-theft",
      "severity": "critical",
      "reason": "Base64-encoded AWS credential exfiltration",
      "sourceRegistry": "clawhub",
      "discoveredAt": "2026-01-27T..."
    }
  ],
  "count": 47,
  "lastUpdated": "2026-02-19T..."
}
```

Cache headers: `Cache-Control: public, max-age=300` (5 min) + ETag for conditional requests.

### Phase 2: Frontend Pages (vskill-platform)

**`/audits` page** — modeled after skills.sh/audits:
- Table with columns: #, Skill Name, Org/Repo, Tier 1 Verdict, Tier 2 Verdict, Score, Status
- Color-coded badges: PASS (green), CONCERNS (amber), FAIL (red), BLOCKED (dark red)
- Sortable by name, score, date
- Filterable by status (PASS, CONCERNS, FAIL, BLOCKED)
- Blocked skills shown with strikethrough and red "BLOCKED" badge
- No auth required — fully public

**`/blocklist` page** — the malicious skills registry:
- Table with columns: Skill Name, Source, Threat Type, Severity, Reason, Discovered
- Severity badges: critical (red), high (orange), medium (yellow)
- Expandable rows showing evidence links
- Search/filter by threat type
- Count header: "47 known-malicious skills blocked"
- No auth required — fully public

**Admin additions:**
- "Add to Blocklist" button on submission detail page (`/admin/submissions/[id]`)
- "Scan External Skill" form in admin dashboard
- Blocklist management table in admin (edit/deactivate entries)

### Phase 3: CLI Integration (vskill)

**New module: `src/blocklist/blocklist.ts`**

```typescript
interface BlocklistCache {
  entries: BlocklistEntry[];
  fetchedAt: string;
  etag?: string;
}

async function checkBlocklist(skillName: string, contentHash?: string): Promise<BlocklistEntry | null>
async function syncBlocklist(): Promise<void>
function getCachedBlocklist(): BlocklistCache | null
```

**Integration points in `add.ts`:**

1. **GitHub path** (after line 283, before Tier 1 scan):
   ```typescript
   const blocked = await checkBlocklist(skillName, contentHash);
   if (blocked && !opts.force) {
     console.error(red(`BLOCKED: "${skillName}" is a known-malicious skill`));
     console.error(red(`Threat: ${blocked.threatType} (${blocked.severity})`));
     console.error(red(`Reason: ${blocked.reason}`));
     console.error(dim(`Use --force to override (NOT recommended)`));
     process.exit(1);
   }
   ```

2. **Plugin path** (after line 130, before scan):
   Same pattern with plugin name check.

3. **Force override** (`--force` flag):
   If `--force` is used on a blocked skill, show a prominent warning but allow install. Log the override.

**New CLI command: `vskill blocklist`**
- `vskill blocklist list` — show cached blocklist entries
- `vskill blocklist sync` — refresh from API
- `vskill blocklist check <name>` — check a single skill

**Cache strategy:**
- Store blocklist in `~/.vskill/blocklist.json`
- Auto-refresh on `vskill add` if cache is >1 hour old
- Manual refresh via `vskill blocklist sync`
- Offline fallback: use cached version if API unreachable

### Phase 4: Seed Data

Pre-populate the blocklist with known malicious skills from ClawHub research:

| Actor | Skills | Threat Type |
|-------|--------|-------------|
| hightower6eu | Clawhub (x3), Polymarket Tranding, Skills Update, Skills Auto-Updater, Polymarket Trading Bot, Polymarket Automatic Trading Bot, Autoupdater Skills | platform-impersonation, credential-theft, auto-updater-trojan |
| Aslaep123 | polymarket-traiding-bot, bybit-agent, base-agent | credential-theft (base64 exfil) |
| zaycv | 40+ programmatic typosquatting skills | typosquatting |
| aztr0nutzs | clawhub, google-qx4, coding-agent-1gx, whatsapp-mgv + 39 more | prompt-injection, credential-theft |

Source: Snyk ToxicSkills report + Aikido Security research.

## Dependencies

- Prisma migration for `BlocklistEntry` model
- No new external dependencies needed
- Existing scanning pipeline unchanged — blocklist is an additional layer

## Risks

| Risk | Mitigation |
|------|------------|
| Blocklist API latency slows `vskill add` | Local cache with 1hr TTL; fail-open if API unreachable |
| False positives in blocklist | Admin review before adding; SUPER_ADMIN can deactivate entries |
| Blocklist becomes stale | Automated scanning of external platforms (Phase 4, US-004) |
| Content hash collision | Use full SHA-256; hash is supplementary to name check |
