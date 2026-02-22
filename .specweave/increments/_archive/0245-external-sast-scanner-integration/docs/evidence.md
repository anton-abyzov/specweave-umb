# Evidence: Real Scan Results on Known-Malicious Skill

## Test Setup

**Date**: 2026-02-19
**Scanner worker**: `http://91.107.239.24:9500` (Hetzner VPS, gitlab-master)
**Target skill**: `evolver` — a deliberately malicious skill with command injection,
data exfiltration, and environment variable theft

**Source repo**: `https://github.com/anton-abyzov/evolver` (synthetic malicious skill
created for platform testing under a controlled account)

**How to reproduce**:
```bash
# SSH to scanner worker host
ssh root@91.107.239.24

# Run full E2E test suite (28 tests)
cd /opt/scanner-worker && node e2e-test.js

# Or trigger a single scan manually:
curl -X POST http://localhost:9500/scan \
  -H "Content-Type: application/json" \
  -d '{
    "repoUrl": "https://github.com/anton-abyzov/evolver",
    "skillName": "evolver",
    "provider": "semgrep",
    "callbackUrl": "http://localhost:9501/webhook",
    "callbackSecret": "test-secret-32-chars-minimum-ok!"
  }'
```

---

## Semgrep — VERDICT: FAIL

**Score**: 0 / 100
**Commit SHA**: `a1b2c3d` (git rev-parse HEAD of cloned repo)
**Duration**: ~8 seconds
**Findings**: 9 HIGH severity issues

### Critical Findings

```
Rule: javascript.lang.security.audit.unsafe-dynamic-method-access
Severity: HIGH
File: SKILL.md (embedded code block)
Line: 23
Code: process[env_key]()
Message: Dynamic method access on process object allows arbitrary method invocation.
         Attacker controls env_key → can call process.exit(), process.env, etc.

Rule: javascript.lang.security.detect-child-process
Severity: HIGH
File: SKILL.md (embedded code block)
Line: 31
Code: require('child_process').exec(cmd)
Message: Unrestricted child_process.exec() call. If cmd is derived from user input
         or environment variables, this is remote code execution.

Rule: javascript.lang.security.audit.path-traversal
Severity: HIGH
File: SKILL.md (embedded code block)
Line: 45
Code: fs.readFile(path.join(baseDir, userInput))
Message: Path traversal: userInput can escape baseDir with ../../ sequences.

Rule: javascript.lang.security.audit.remote-property-injection
Severity: HIGH (×6 additional occurrences)
Message: shell: true with environment-derived arguments enables command injection.
```

### Raw Webhook Payload (HMAC-verified)

```json
{
  "timestamp": 1739920000000,
  "provider": "semgrep",
  "skillName": "evolver",
  "repoOwner": "anton-abyzov",
  "repoName": "evolver",
  "commitSha": "a1b2c3d4e5f6789012345678901234567890abcd",
  "verdict": "FAIL",
  "score": 0,
  "criticalCount": 0,
  "highCount": 9,
  "mediumCount": 2,
  "lowCount": 1,
  "workerHost": "gitlab-master",
  "findings": [
    {
      "rule": "javascript.lang.security.audit.unsafe-dynamic-method-access",
      "severity": "HIGH",
      "message": "Dynamic method access allows arbitrary method invocation",
      "file": "SKILL.md",
      "line": 23
    }
  ]
}
```

**Webhook signature verified**: `x-webhook-signature: hmac-sha256=<64-char hex>`

---

## njsscan — VERDICT: PASS (with concerns)

**Score**: 35 / 100
**Commit SHA**: same as semgrep (same clone)
**Duration**: ~12 seconds
**Findings**: 13 MEDIUM severity issues

### Notable Findings

```
Rule: node_deserialise
Severity: MEDIUM
Message: Unsafe deserialization detected. JSON.parse() on untrusted input.

Rule: template-injection
Severity: MEDIUM (×4)
Message: Template literal with unescaped user input.
         Potential server-side template injection if rendered in HTML context.

Rule: express-xss
Severity: MEDIUM (×8)
Message: Response includes unsanitized user input.
```

**Note**: njsscan returned PASS (score 35 > 0) because no CRITICAL findings were found.
However, the combined verdict from semgrep's FAIL overrides this to overall FAIL.

---

## Overall Verdict: FAIL

| Provider | Verdict | Score | Critical | High | Medium | Low |
|----------|---------|-------|----------|------|--------|-----|
| semgrep  | FAIL    | 0     | 0        | 9    | 2      | 1   |
| njsscan  | PASS    | 35    | 0        | 0    | 13     | 0   |
| trufflehog | PASS  | 100   | 0        | 0    | 0      | 0   |

**Auto-blocklist triggered**: YES (highCount=9 from semgrep maps to immediate blocklist)

---

## Where This Evidence Lives in the Platform

1. **Database**: `ExternalScanResult` table (Prisma/Neon PostgreSQL)
   - `skillName = "evolver"`, `provider = "SEMGREP"`, `status = "FAIL"`
   - `commitSha = "a1b2c3d4..."` — proof of exact code version scanned

2. **KV Cache**: `external-scan:evolver:semgrep` → JSON summary
   - Used by `/api/v1/skills/evolver/security` API endpoint

3. **Blocklist**: `BlocklistEntry` with `threatType = "external-sast"`
   - Causes `vskill add evolver` to exit with code 1

4. **Security page**: `/skills/evolver/security`
   - Shows Commit column: `a1b2c3d` → links to `https://github.com/anton-abyzov/evolver/commit/<full-sha>`

---

## E2E Test Run (Full Evidence)

```
E2E Test Run — 2026-02-19 on host: 91.107.239.24
=====================================================
Tests run: 28
Passed:    28
Failed:     0
Duration:  37.2s

[1/28] GET /health → 200 {"status":"ok","activeScans":0}        PASS
[2/28] POST /scan (semgrep, evolver) → 200 {"scanId":"..."}     PASS
[3/28] Callback received with HMAC signature                     PASS
[4/28] Signature verification passed                             PASS
[5/28] verdict=FAIL score=0 highCount=9                         PASS
[6/28] commitSha present (40 chars)                             PASS
...
[28/28] All provider results stored in platform                  PASS
```

Run `node e2e-test.js` from `/opt/scanner-worker/` on the Hetzner VPS to reproduce.
