# Provider Details: External SAST Tools

## Semgrep

**Purpose**: Static analysis for cross-function data flow vulnerabilities, insecure patterns,
and known CVE signatures.

**Rule sets used** (scanner-worker default):
- `p/javascript` — JS/TS anti-patterns
- `p/security-audit` — OWASP Top 10 patterns
- `p/command-injection` — sink-to-source command injection

**Key findings in malicious skills**:
| Rule | Severity | Example |
|------|----------|---------|
| `javascript.lang.security.audit.unsafe-dynamic-method-access` | HIGH | `obj[userInput]()` |
| `javascript.lang.security.detect-child-process` | HIGH | `exec(shell_cmd)` |
| `javascript.lang.security.audit.path-traversal` | HIGH | `fs.readFile(user_path)` |
| `javascript.lang.security.audit.remote-property-injection` | HIGH | `shell: true` with env |

**Score formula**: `max(0, 100 - (criticalCount*25 + highCount*10 + mediumCount*3 + lowCount*1))`

**Invocation**:
```bash
semgrep scan --config=p/javascript --config=p/security-audit --config=p/command-injection \
  --json --output=semgrep-results.json <repoDir>
```

**Version tested**: semgrep 1.111.0 (pysemgrep backend)

---

## njsscan

**Purpose**: Node.js-specific security scanner. Detects unsafe `eval`, `innerHTML`,
prototype pollution, hardcoded secrets, SSRF patterns, and template injection.

**Rule categories**:
- `node-deserialise` — unsafe deserialization
- `node-serialize` — serialization with code execution risk
- `express-xss` — XSS sinks in Express responses
- `template-injection` — server-side template injection
- `hardcoded-credentials` — API keys, passwords in source

**Score formula**: same as Semgrep (criticalCount*25 + highCount*10 + ...)

**Invocation**:
```bash
njsscan --json -o njsscan-results.json <repoDir>
```

**Version tested**: njsscan 0.4.1

---

## Trufflehog

**Purpose**: Secret detection across git history. Finds API keys, tokens, certificates,
and private keys using 700+ detector signatures with entropy analysis.

**Detects**:
- GitHub Personal Access Tokens
- AWS Access Keys
- OpenAI API Keys
- GCP Service Account JSON
- Stripe Secret Keys
- SSH private keys
- Generic high-entropy strings (>3.5 Shannon entropy)

**Special capability**: Scans full git history, not just current HEAD. Can find secrets
that were committed then deleted.

**Invocation**:
```bash
trufflehog filesystem --json --no-update <repoDir>
```

**Version tested**: trufflehog 3.93.4

**Note**: Trufflehog findings are always `severity: high` or `severity: critical`.
A PASS from Trufflehog is a strong signal that no secrets were ever committed.

---

## Finding Normalization Format

All provider findings are normalized to a common structure before storage:

```json
{
  "rule": "javascript.lang.security.audit.unsafe-dynamic-method-access",
  "severity": "HIGH",
  "message": "Dynamic method access can allow attackers to call arbitrary methods",
  "file": "SKILL.md",
  "line": 42,
  "code": "obj[userInput]()",
  "provider": "semgrep"
}
```

Stored as a JSON array in `ExternalScanResult.findings` (capped at 100 findings per provider).

---

## Provider Score Interpretation

| Score | Verdict | Meaning |
|-------|---------|---------|
| 80–100 | PASS | No significant issues |
| 50–79 | PASS | Minor issues, acceptable |
| 1–49 | FAIL | Significant findings |
| 0 | FAIL | Critical or catastrophic |

Overall verdict = FAIL if ANY provider returns FAIL.
