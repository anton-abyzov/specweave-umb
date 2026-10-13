# 0896 implementation and release evidence

## Authorization and boundaries

Anton explicitly selected **Complete hosted private publishing** on 2026-10-13. Complete the feature and its privacy checks; purchase a license only if needed. No purchase is needed: the authenticated production billing API confirms an active personal Pro subscription. Source work and automated validation proceed in isolated worktrees. New UI and production migration require concrete manual acceptance before increment closure, per AGENTS.md.

## Verified prestate

- SpecWeave installed/stable: 3.0.14 / 3.0.14. Jev routing unavailable because no API key; continued without it.
- vskill package/npm stable: 1.2.7. Shell global binary reports 1.2.6; upgrade is pending the completed release.
- Platform baseline: 2e0c6247ae627c69e8307a1d4e4d9f90c0767611; vskill baseline 13387a6.
- Production /pricing returns HTTP200 and explicitly states hosted private publishing and new subscriptions are unavailable.
- CLI's actual platform credential: billing API HTTP200, PRO, ACTIVE, monthly, period end 2026-10-22, privateSkillLimit 0. Account has no tenant memberships.
- The desktop's separate native keychain platform credential returned401; it is not the valid credential currently selected by CLI. No credential was revoked or platform tier changed.
- The implicit local GitHub credential had only read:user and got404 for Anton's private skills repository. The existing gh credential identifies the same numeric GitHub user and reads the private repository with200.
- Repaired the selected local GitHub credential using that same-account existing gh credential through vskill's existing credential store; readback and default private GET200 passed. The working platform token was preserved exactly. No token value is in this report.
- dcfc-inquiry-replies is correctly installed in ~/.agents/skills, with Claude linkage and Codex shared discovery. Private source matches installed content after expected namespacing. Fresh local security scan100/100, zero findings.
- GitHub App connect preflight HTTP200; app slug verified-skill-studio. Runtime GitHub App permissions/provisioning still need live verification after implementation.

## Ownership

Main umbrella's existing dirty0896 ledger note was copied, preserving the October12 decision that the free hosted private allowance is0. Other owners and worktrees were not modified.

- Umbrella: /Users/antonabyzov/.codex/worktrees/hosted-private-publishing/specweave-umb, codex/0896-hosted-private-publishing.
- Platform: repositories/anton-abyzov/vskill-platform, codex/0896-private-platform (T01,T06,T07).
- Studio: repositories/anton-abyzov/vskill, codex/0896-private-studio (T04,T05).
- Independent integration tests: ../platform-isolation-tests, codex/0896-private-isolation (T02,T08).
- GitHub onboarding: ../platform-onboarding, codex/0896-private-onboarding (T10).

## Test isolation

Postgres14 local-only databases vskill_0896_private (integration lane) and vskill_0896_ui (UI sandbox) created on127.0.0.1:5432. Never inherit the original checkout's production DATABASE_URL. Browser automation must explicitly set headless:true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never. Processes stop by exact PID only.

## Implementation proof

- Studio commit e11b58b:171 focused assertions in16 files pass; CLI root TypeScript check and Studio production build pass. Headless actual Studio UI proof covers selected tenant, successful private status, missing-account mobile, and closed-gate mobile; screenshots and assertions preserved in studio-headless/. Root visually inspected selected-account desktop and missing-account mobile. Whole eval-ui typecheck has unrelated existing errors; not claimed green.
- Onboarding commit3154d458:59 tests pass. Personal ownership checks immutable GitHub account IDs; organization access requires active admin membership. Verified callbacks provision tenant membership and exclude private repositories from public resync; webhook provisioning uses authoritative installation account.
- Independent sandbox initial23/23 passes: actual production public/private processors and authenticated routes backed by isolated PostgreSQL. Headless browser checks traverse an HTTP test server importing production handlers, not the Next website UI. Coverage/trace run in progress.
- Production VSKILL_TOKEN_KEK is absent according to secret-name inventory; no encrypted installation credentials exist. The additive migration creates PrivateSubmission and PrivateSkillArtifact, with tenant/version foreign keys and PRIVATE-only constraint. Both need release validation before live private publishing.

## Current status

Implementation in progress; hosted launch gate remains closed. No production migration, hosted private submission, deployment, public publication, or payment was performed.
