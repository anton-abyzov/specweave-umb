# php2shell check skill and page

## Problem

On 2026-10-21 PHP shipped emergency fixes for php2shell (CVE-2026-109618, CVE-2026-109619): unauthenticated RCE in every web SAPI below 8.2.35 / 8.3.36 / 8.4.27 / 8.5.12, with exploit attempts already seen. People are getting cold "free audit" emails asking for their URL. We have no honest, self-serve way for a developer or an agent to check exposure, and nothing on verified-skill.com that rides this news.

## Scope

In: a `php2shell-check` skill in vskill (new `security` plugin) with a portable check script; a public explainer + check page on verified-skill.com that reads a site's public PHP version header, with a "CVE watch" waitlist CTA. Out: probing third-party sites for the bug itself, outreach/email campaigns, the paid CVE-watch feature (OSV feed), deploy of anything beyond the normal release flow.

## Acceptance Criteria

- [ ] AC-01: `scripts/check.sh` reports VULNERABLE (exit 1) for PHP 8.4.26, 8.1.x, 7.4.x, 5.6.x; PATCHED (exit 0) for 8.2.35, 8.3.36, 8.4.27, 8.5.12 and newer; UNKNOWN (exit 2) when no PHP is found; `--json` prints machine-readable output.
- [ ] AC-02: The script also inspects the repo (Dockerfile `FROM php:` tags, `.php-version`, composer.json `require.php`/`config.platform.php`) and the stopgap ini settings, and warns that distro packages may carry backports under an old version string.
- [ ] AC-03: SKILL.md tells the agent how to run the check, read results and apply the fix plan (upgrade targets per branch, distro advisory, stopgaps), and is listed in the vskill marketplace as plugin `security`.
- [ ] AC-04: `GET /api/v1/check/php2shell?url=` on vskill-platform fetches only public http(s) hosts (private/loopback/link-local IPs and non-80/443 ports refused), reads `X-Powered-By`/`Server`, and returns exposed / patched / unknown with the detected version; rate-limited and cached.
- [ ] AC-05: `/check/php2shell` page explains the CVEs with primary-source links, has the URL check form, says plainly that a hidden header means "unknown, run the skill", shows the `vskill install` command and a CVE-watch waitlist CTA.

## Approach

vskill: `plugins/security/skills/php2shell-check/{SKILL.md,scripts/check.sh,tests/run.sh}` + marketplace entry. Script is POSIX sh, no deps beyond php when present; tests use a fake `php` on PATH.
vskill-platform: `src/lib/php2shell.ts` (version parsing + verdict, shared), `src/app/api/v1/check/php2shell/route.ts`, `src/app/check/php2shell/page.tsx`, vitest for lib + route. Reuse existing waitlist form and rate-limit helpers.
Rejected: actively probing a URL for the bug (unauthorized testing); scanning composer.lock (runtime bug, not a package).

## Decisions

### Asked
- D-01 Build skill + free page now → yes (Anton, 2026-10-21)
### Defaulted (change any before sw-do)
- D-02 New vskill plugin named `security` → default
- D-03 Mass cold outreach (Gmail blast, EasyChamp list, phone) → not done; targeted agency list awaits Anton's answer
### Open
- none

## Tasks

### T-01 php2shell-check skill and script
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/vskill/plugins/security/**, repositories/anton-abyzov/vskill/.claude-plugin/marketplace.json | Test: sh repositories/anton-abyzov/vskill/plugins/security/skills/php2shell-check/tests/run.sh

### T-02 Public check API and page
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/vskill-platform/src/lib/php2shell.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/check/php2shell/**, repositories/anton-abyzov/vskill-platform/src/app/check/php2shell/** | Test: npm --prefix repositories/anton-abyzov/vskill-platform exec vitest run php2shell
