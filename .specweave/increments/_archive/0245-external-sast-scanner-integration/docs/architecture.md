# Architecture: External SAST Scanner Integration

## System Overview

External SAST scanning adds a Tier 1.5 layer between the existing Tier 1 (37 regex patterns)
and Tier 2 (LLM semantic analysis). It runs asynchronously after skill publication using
GitHub Actions as the compute backend (Cloudflare Workers cannot exec child processes).

## Trigger Flow

```
Skill Published (POST /api/v1/admin/skills/publish)
         │
         ▼
GitHub Actions repository_dispatch
  event: "external-scan"
  payload: { skill_name, repo_url, callback_url }
         │
         ▼
  ┌──────────────────────┐
  │  github-scan.yml     │
  │  (matrix: 3 jobs)    │
  ├──────────────────────┤
  │  job: semgrep        │──► POSTs result to callback_url
  │  job: njsscan        │──► POSTs result to callback_url
  │  job: trufflehog     │──► POSTs result to callback_url
  └──────────────────────┘
         │
         ▼
  POST /api/v1/webhooks/scan-results
  Header: x-webhook-signature: hmac-sha256(payload, WEBHOOK_SECRET)
         │
         ├──► Prisma: ExternalScanResult upsert
         ├──► KV: external-scan:{name}:{provider} = summary JSON
         └──► If criticalCount > 0: BlocklistEntry create
```

## Alternative: Scanner Worker

For self-hosted scanning without GitHub Actions dependency, a standalone Node.js HTTP
server (`scanner-worker/scanner.js`) runs on a Hetzner VPS.

```
POST /scan
  { repoUrl, skillName, provider, callbackUrl, callbackSecret }
         │
         ├──► git clone <repoUrl>
         ├──► git rev-parse HEAD → commitSha (version proof)
         ├──► run provider tool
         ├──► normalize findings
         └──► POST callbackUrl (HMAC-signed)
```

**Production endpoint**: `http://91.107.239.24:9500`
**Health check**: `GET /health` → `{"status":"ok","activeScans":N,"maxConcurrent":3}`

## Version Integrity (commitSha)

A critical trust property: the platform must prove *which exact code version* was scanned.

After `git clone`, the worker captures:
```js
const commitSha = execSync(`git -C ${repoDir} rev-parse HEAD`).toString().trim();
```

This SHA is:
1. Sent in the callback payload as `commitSha`
2. Stored in `ExternalScanResult.commitSha` (Prisma DB)
3. Stored in `ExternalScanSummary.commitSha` (KV cache)
4. Displayed on `/skills/{name}/security` as a 7-char link to GitHub commit

This prevents "scan laundering" — running a scan on cleaned code and claiming the
original malicious version passed.

## Storage Architecture

Two-tier storage for scan results:

| Layer | Key pattern | Purpose |
|-------|-------------|---------|
| KV | `external-scan:{name}:{provider}` | Single provider fast read |
| KV | `external-scans:{name}` | All providers list for overview page |
| Prisma | `ExternalScanResult` | Durable audit trail with full findings JSON |

TTL on KV entries: 365 days (1 year).

## Auto-blocklist

If `criticalCount > 0` in any scan result, a `BlocklistEntry` is created automatically:
```
threatType: "external-sast"
severity:   "critical"
reason:     "<provider> found N critical findings"
discoveredBy: "external-scan"
```

This causes `vskill install <skill>` to fail with exit code 1 and a link to the report.

## Deduplication and Rate Limiting

- Dispatches are skipped if scan already `PENDING` or `RUNNING` for that skill+provider
- Max 100 dispatches/hour (rate-limited at webhook ingress)
- Pending scans older than 20 minutes are lazily promoted to `TIMED_OUT` on read
