# Plan: External SAST Scanner Integration

## Architecture

```
POST /api/v1/submissions (existing, unchanged)
  ├── Tier 1 regex (immediate, CF Worker)
  ├── Tier 2 LLM (immediate, CF Workers AI)
  ├── Publish/Reject (immediate)
  └── [ASYNC] ctx.waitUntil(dispatchExternalScans())
       ├── HTTP POST to Hetzner scanner workers (round-robin)
       │   ├── Semgrep (p/nodejs + p/command-injection + p/ssrf)
       │   ├── njsscan (Node.js SAST + SSRF)
       │   └── Trufflehog (700+ secret detectors)
       └── POST /api/v1/webhooks/scan-results (HMAC auth)
            ├── Store in Prisma + KV
            ├── Auto-block on CRITICAL
            └── SSE event for UI
```

## Infrastructure

- **Worker 1**: wordpress (cpx11, 2 vCPU / 2GB RAM, 5.161.69.232)
- **Worker 2**: gitlab-master (cpx31, 4 vCPU / 8GB RAM, 91.107.239.24)
- **Scanner**: Docker container with semgrep + njsscan + trufflehog
- **Dispatch**: Direct HTTP from CF Worker → Hetzner (round-robin via KV counter)
- **Callback**: HMAC-signed webhook from Hetzner → platform
- **Fallback**: GitHub Actions repository_dispatch (if no workers configured)

## Phases

1. **Database + Storage** (T-001, T-002): Prisma model, KV store module
2. **Webhook + Auth** (T-003, T-004): HMAC auth, results endpoint
3. **Scanner Runner** (T-005, T-006): Docker worker, result parser
4. **Dispatch** (T-007, T-008): Dispatch module (HTTP round-robin), submission integration
5. **APIs + Badges** (T-009, T-010, T-011): Security APIs, SVG badges
6. **UI Pages** (T-012-T-015): Security overview, provider detail, skill page, audits
7. **CLI** (T-016, T-017): Platform security check, `vskill add` gate
8. **Hardening** (T-018, T-019): Admin rescan, timeout sweep

## Key Decisions

- **Scanner compute**: Hetzner VPS (reusing existing servers, Docker containers)
- **Dispatch method**: Direct HTTP with shared secret auth (round-robin across workers)
- **Scan timing**: Post-publish async (non-blocking, auto-block on CRITICAL)
- **Tools**: Semgrep + njsscan + Trufflehog (covers SAST + SSRF + secrets gaps)
- **Storage**: Separate `ExternalScanResult` model (not reusing `ScanResult`)
- **Fallback**: GitHub Actions repository_dispatch if no workers configured

## Env Vars (Platform)

- `SCANNER_WORKERS`: comma-separated worker URLs (e.g. `http://5.161.69.232:9500,http://91.107.239.24:9500`)
- `SCANNER_WORKER_SECRET`: shared secret for authenticating dispatch requests
- `WEBHOOK_SECRET`: HMAC secret for callback signature verification
- `PLATFORM_URL`: base URL for callback (default: `https://verified-skill.com`)
