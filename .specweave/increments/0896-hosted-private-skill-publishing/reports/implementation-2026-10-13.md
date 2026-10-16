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

- A second read-only production check confirms latest migration20261011220000_skill_delisted_reason is applied; private tables are absent. The only tenant is an existing test fixture, not Anton's account, and it has no encrypted installation token. No production row was changed. GitHub's user/installations endpoint rejects the existing classic PAT with403, so its presence cannot prove App authorization.

- Independent integration final23/23 passed; coverage of errors/github/http/scan/service is92.45% lines/statements,94.44% functions,73.76% branches (80% line/statement gate passed). The sandbox database was cleaned and released. Source/report copies are preserved locally; the backend runs one final integrated replay after scanner hardening.
- CLI private workflow commit f7e6b9c adds submit/install/update;121 focused/regression checks pass, including64 new tests. A real authenticated loopback HTTP test exercised actual Codex/Claude canonical install and link readback, exact pinning, executable mode and integrity failures. This is synthetic transport proof, not hosted production proof. Temporary installs removed; global credentials and personal skills unchanged.
- Umbrella repository is public. Account/credential-prestate reports are local-only and must not be pushed or copied into a public PR. Product PR descriptions contain generic behavior and synthetic validation only.

## Current status

Release metadata prepared at CLI4359ec3: npm1.2.8 and native1.0.65; both remain unpublished. Version consistency and package preflight833 entries passed. The actual installed native1.0.64 sidecar ran with personal writes denied and returned200 for profile and tenant list, matching direct authentication as Anton's Pro account with0 tenants. Credentials/runtime directory unchanged; exact test PID stopped. Receipt/tmp/0896-native-readonly-proof.json. The stale OS credential does not affect this packaged binary, which uses the protected fallback credential store.

Live GitHub App metadata confirms owneranton-abyzov, Contents/Metadata read, events[push] (push only). Repository lifecycle delivery needs repository subscription before launch; organization ownership verification additionally requires Members read. No App setting was changed. GitHub documentation confirms installation and installation_repositories delivery is automatic. Visible browser use is now authorized by Anton's replacement AGENTS instructions dated2026-10-13; routine tests remain headless. Browser tab creation timed out twice without a verified settings page or account mutation.

Production source passed fresh independent review at platforma17599a6 and CLI4f9d129. The CLI's subsequent test-fixture-only head1a20957 passed every PR check, including fullunit7,014 passed/11 skipped (run38355622953), three-OS sidecar runtime, install/diff/key-store smoke, and Windows Rust. Platform full coverage CI passed7,604 tests/14 skipped with66.17% lines/statements,80.99% branches and81.49% functions (run38354175469). Local final Worker build passed at unchanged production source; log/tmp/0896-platform-worker-build.log.

Final local platform8ef2818f passed36/36 combined PostgreSQL/headless checks with92.58% private line/statement coverage. Concurrent intake passed20 repeated runs after a test-only Worker environment correction; clean CI had exposed mocked dynamic-import nondeterminism, not a database defect. Onboarding CI38356550483 passed47/47. Replacement dedicated CI38357888207 remains pending. Both hosted launch gates remain closed. No production migration, hosted private submission, deployment, public publication, or payment was performed.

## Activation candidate verification

Platform adfa8e12 passed CI38358831309:36/36 real PostgreSQL/headless publication checks,92.58% private-source coverage and the Worker build/runtime contract. CI38358831353 passed47/47 onboarding browser checks. Full activation coverage passed7607 tests but failed2 stale pricing assertions that assumed the former closed default; the owner is preserving explicit rollback assertions and adding actual release-default coverage. CLI8cd6181 passed all7014 tests plus cross-platform install/diff/key-store and sidecar checks. The unchanged Windows settings test fixed-sleep race is being rerun once before considering any fixture edit.

Visible Chrome now works. The authenticated anton-abyzov settings page confirms existing Verified Skill Studio installation135567134. Opening its settings reaches GitHub Confirm access; the user has been asked to complete passkey/authenticator confirmation. No repository grant or GitHub App setting has changed.

Pricing test followup fd173ea6 preserves the original rollback assertions and adds actual-enabled Pro/Team coverage;81/81 focused checks and fresh review pass. Its sandbox/Worker CI38360468721 and47-case browser CI38360468634 pass; final full unit/coverage38360468659 is pending. CLI Windows Rust rerun38359089539 attempt2 passed168/168 without edits; all CLI8cd6181 PR checks now pass.

Read-only Cloudflare prestate: production deployment033f8654-77f2-4fd9-b2a7-7ddc6493944f serves version09e5b23a-a99a-4267-a2d7-fc2aed208b51 at100%, created2026-10-12T20:05:41Z. Original platform checkout remains clean at2e0c6247 (2026-10-12T20:01:15Z). Live-source comparison is being checked independently; no deployment performed.

## Native proof boundary

Tauri launcher sidecar.rs232 starts vskill-server with --port0 and does not inject credential overrides. Hosted publishing, tenant discovery and online entitlement use the same-origin Node proxy and protected vsk token. Locked Cargo keyring3.6.3 resolves only default with no native backend features (cargo tree --locked --offline -e features -i keyring); legacy Rust quota uses its mock store in this build. The standalone1.0.64 sidecar proof is not full GUI proof. Post-release acceptance must verify installed1.0.65, a fresh sidecar/port, the X-Studio-Token bridge, matching live profile/Pro/tenants, enabled Private selection and the authorized publish/status/download flow. No GUI launch or credential mutation was performed for this source check.

## Live baseline comparison

Independent read-only comparison found no Worker artifact/config drift: both deployed modules match the clean2e0c6247 checkout's existing-artifact Wrangler dry-run byte for byte;162 direct source-map inputs match Git HEAD;71 config checks, both custom domains and current version bindings match. Details and hashes are in review.md. The prebuilt Next handler was not rebuilt from tracked source; deployed sourcemap/commit annotation is absent. Static assets, secret values, queue consumer settings and DB/provider state remain separate release checks. No production write occurred.

## Final candidate checks and pending acceptance

All platform PR123 checks pass at fd173ea6:7611 tests/14 existing skips,718 files/4 skips,66.17% lines/statements above60%,81.02% branches,81.49% functions (CI38360468659);36-case sandbox/Worker CI38360468721 and47-case browser CI38360468634 pass. All CLI PR174 checks pass at8cd6181, including7014 unit tests and168 Windows native tests. Fresh source review and read-only live baseline comparison pass.

Concrete manual acceptance/release approval was requested for the reviewed UI, additive migration, encryption-key setup, Cloudflare deployment, npm1.2.8 and native1.0.65 releases; no response yet. GitHub passkey confirmation remains independently pending. No production secret, migration, grant, deployment, hosted submission, release tag, npm publication or payment has been performed.
