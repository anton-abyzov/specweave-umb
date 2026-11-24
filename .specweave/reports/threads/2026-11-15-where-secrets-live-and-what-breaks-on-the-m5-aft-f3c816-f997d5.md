---
title: "Where secrets live, and what breaks on the M5 after copying specweave"
thread: "thread:delegated-task:command%3Amcp%3A2a6b5150-b95a-4974-a654-987cd01fdf6b%3Adelegate-task%3Aa0bebad1-5978-45a9-bd6d-6ef034dd997d"
threadTitle: "Moving project secrets between machines"
savedAt: "2026-11-15T00:37:51.370Z"
date: November 14, 2026
status: inventory by name only; no values read, no Keychain probes
follows: EasyChamp credentials when moving to another machine
---

# Where secrets live, and what breaks on the M5 after copying specweave

## 1. Where secrets normally live

No, secrets are not normally stored in a repo. There are four places, and each has a different answer to "what do I do on a new machine".

| Place | What belongs there | New machine |
|---|---|---|
| Per-machine logins and the Keychain | Your own access as a developer: `gh`, `az`, `gcloud`, `wrangler`, `npm`, `docker`, code-signing identities | Sign in again. Nothing is copied, and each machine can be revoked alone. |
| A secrets manager (1Password, Doppler, Infisical, a cloud key vault) | Application secrets used in development and CI: API keys, database URLs | One sign-in to the manager; repos hold references, not values. |
| Encrypted GitOps (SealedSecrets or SOPS) | What the **cluster** needs at runtime. The repo holds ciphertext; only the cluster's private key opens it. | Nothing. A workstation never needs the decryption key. |
| Plain files outside git (`.env`, `~/.config/<tool>/...`) | The practical fallback for a solo developer | Copy them over an encrypted path, or recreate them. |

Committing a plain private key, a token or a Terraform state file is wrong in every case: every clone and the Git host get it forever, and removing the file later does not remove it from history. The only fix is rotating the key.

**What EasyChamp does:** a mix. Runtime secrets for the Hetzner cluster are SealedSecrets in `ec-gitops`, which is the correct GitOps pattern. Developer access is per-machine logins plus key files in `~/.ssh` and `~/.kube`. Application secrets are 19 untracked `.env` files. There is no secrets manager. Two things break the pattern: four private keys are tracked in git, and Terraform state sits untracked on the M4 with no remote backend.

**What specweave does:** no GitOps at all. Production secrets live in Cloudflare (Worker secrets, Hyperdrive) and GitHub Actions secrets. The M4 holds 9 untracked `.env` files in the folder and about 10 tool folders under `~/.config`.

## 2. specweave umbrella on the M4

### In the project folder: the copy carries these when secrets are ticked

| File | Holds (variable names) |
|---|---|
| `.env` | `GITHUB_TOKEN`, `GH_TOKEN`, Jira and Azure DevOps tokens |
| `.env.cloudflare` | Cloudflare account and zone ids, 4 API tokens, R2 access keys |
| `.env.bak-20260715` | An old backup. Delete it instead of copying it. |
| `repositories/anton-abyzov/specwithcode/.env` | Google OAuth client id and secret |
| `repositories/anton-abyzov/vskill-platform/.env` | `DATABASE_URL`, `NEON_API_TOKEN` (Neon is decommissioned), SendGrid key |
| `repositories/anton-abyzov/vskill-platform/.env.local` | `DATABASE_URL`, `JWT_SECRET`, Stripe keys and webhook secret, ElevenLabs key |
| `repositories/anton-abyzov/vskill-platform/.dev.vars` | `DATABASE_URL`, `INTERNAL_BROADCAST_KEY` |
| `repositories/anton-abyzov/vskill-platform/crawl-worker/.env` | Worker secret, GitHub tokens, Cloudflare token |
| `repositories/anton-abyzov/vskill-platform/scanner-worker/.env` | Same, plus `GITHUB_APP_PRIVATE_KEY_PATH`, which points at a file |

No private keys are tracked in the first-party repos. The tracked `.pem` files are vendored test fixtures under `specwithcode/.repos`.

### Outside the folder: what breaks on the M5, and the fix

| Area | Breaks on the M5 | Where it lives on the M4 | Fix |
|---|---|---|---|
| GitHub | `git push`, `gh pr`, release requests | Keychain (`gh` keyring, `osxkeychain` helper) | `gh auth login`, `gh auth setup-git` |
| Cloudflare | `wrangler deploy`, Hyperdrive, KV, R2, queues for `vskill-platform` | `~/.wrangler/config/default.toml` (OAuth login) | `wrangler login`. The `.env.cloudflare` tokens arrive with the copy. |
| vskill-platform DB | Nothing, if the copy carried `.env`. Hyperdrive itself is a Cloudflare binding and needs no local secret. | `DATABASE_URL` in three `.env` files | If the Postgres port is firewalled by source address, add the M5's address on the Hetzner side. |
| Hetzner | `ssh` to the crawl VMs and Postgres host, `hcloud` | `~/.ssh` keys and config, `~/.config/hcloud/cli.toml` | New SSH key and hcloud token for the M5, as in the EasyChamp report |
| npm | `npm publish` | `~/.npmrc` (npmjs and GitHub Packages tokens) | `npm login`. Releases publish from CI, so this is only for manual publishes. |
| Apple signing | Signed Mac builds, notarization | 3 code-signing identities in the login Keychain; `~/.appstoreconnect/private_keys` (2 API keys); 60 provisioning profiles | Keep releases on the M1 runner. To sign on the M5: export the Developer ID identity from Keychain Access as a `.p12` and import it there, and send the API key files. |
| App update signing | Release signing only | `~/.config/specwithcode-release`, `~/.config/skill-studio-release-v3` (minisign key and passphrase) | Do not copy. These belong on the release machine only. |
| Connect relay | Deploying or administering the relay | `~/.config/specwithcode-connect`: `CLERK_SECRET_KEY`, `CLOUDFLARE_API_TOKEN`, Google OAuth pair, an Apple API key | Send the folder only if the M5 will deploy the relay. |
| Android | Play uploads | `~/.config/specwithcode` (upload keystore and properties) | Send the folder; a lost upload keystore needs a Google reset. |
| Stripe CLI | `stripe listen` for webhook tests | `~/.config/stripe/config.toml` | `stripe login` |
| Shell variables | Jev guard and image tools | `~/.zshrc`: `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `HF_API_KEY`, `HF_API_SECRET` | Re-add by hand |
| Marketing tools | Posting and media skills | `~/.config/postiz`, `~/.config/blotato`, `~/.config/kie`, `~/.config/live-keys` | Send only if the M5 will post |
| Claude, Codex, Copilot | Agents cannot start | Per-provider sign-in | Sign in on the M5. These never travel. |

### Problems to expect beyond "not signed in"

1. **Absolute paths.** `GITHUB_APP_PRIVATE_KEY_PATH` and `IdentityFile /Users/antonabyzov/...` lines break if the user name or folder differs on the M5.
2. **File modes.** A key that lands as `644` is refused by `ssh`. Sent files need `600`.
3. **Keychain-backed tools look copied but are not.** `~/.docker/config.json` and `~/.config/gh/hosts.yml` name a Keychain entry that does not exist on the M5.
4. **Expiring logins.** `az`, `gcloud` and `wrangler` OAuth tokens copied as files expire within hours and cannot refresh on a different machine.
5. **Stale secrets travel too.** The copy carries `.env.bak-20260715` and the dead `NEON_API_TOKEN` unless they are cleaned first.
6. **Two machines, one identity.** A copied token cannot be revoked for one machine only.
7. **One-writer state.** Local Terraform state (EasyChamp) corrupts if both machines apply.

## 3. The procedure

1. Clean the source: delete backups and dead tokens.
2. Copy the project with secrets ticked (in-folder files).
3. For each credential outside the folder: sign in on the destination if it has a login, send the file if it is file-only, skip it if that machine will not do that job.
4. Run a status check per credential on the destination.

Steps 3 and 4 are what the new copy-dialog checklist automates; it is planned as an increment in the app.
