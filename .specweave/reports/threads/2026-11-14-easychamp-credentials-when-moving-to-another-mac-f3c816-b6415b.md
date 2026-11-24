---
title: "EasyChamp credentials when moving to another machine"
thread: "thread:delegated-task:command%3Amcp%3A2a6b5150-b95a-4974-a654-987cd01fdf6b%3Adelegate-task%3Aa0bebad1-5978-45a9-bd6d-6ef034dd997d"
threadTitle: "Moving project secrets between machines"
savedAt: "2026-11-14T22:41:28.561Z"
date: November 14, 2026
status: recommendation, no code changed
scope: M4 inventory (names only), options ranked, M5 steps, SpecWithCode additions
---

# EasyChamp credentials when moving to another machine

**Recommendation:** sign in again on the M5 for everything that has a login, give the M5 its own SSH key and Hetzner token, and send only the five things that cannot be recreated through SpecWithCode's encrypted transfer. Do not copy `~/.ssh`, `~/.kube/config` or `~/.azure` wholesale. Later, move the `.env` files to one secrets manager so a new machine needs one sign-in instead of 19 files.

No secret value was read into this report. The inventory used file names, context names and key names only. No Keychain probe was run.

## 1. What EasyChamp needs on the M4

The project is at `/Users/antonabyzov/Projects/sw-easychamp` (not `sw-easychamp-fleet`): 38 git repositories, 37 with `https://github.com/anton-abyzov` remotes.

### Outside the project folder (the project copy never carries these)

| Item | Where on the M4 | How it authenticates | On a new machine |
|---|---|---|---|
| AKS, 3 contexts (`easychamp-prod-aks`, `ec-aks-prod-east-us-v2`, `sc-aks-prod-east-us`) | `~/.kube/config` | Static client certificate plus token written by `az aks get-credentials`. No kubelogin. | `az login`, then `az aks get-credentials` per cluster. Nothing to copy. |
| GKE, 1 context (`ec-gke-prod-us-east1`) | `~/.kube/config`, `~/.config/gcloud` | `gke-gcloud-auth-plugin` exec | `gcloud auth login`, `gcloud container clusters get-credentials`. Nothing to copy. |
| Hetzner cluster `ec-ash-prod` | `~/.kube/ec-ash-prod.yaml` | Static client certificate and key in the file. 8 scripts in `ec-iac-infrastructure/scripts` point `KUBECONFIG` at it. | File only. Send it, or re-fetch it from the control-plane node over SSH. |
| Hetzner Cloud CLI | `~/.config/hcloud/cli.toml`, context `easychamp` | API token in the file | Create a second token named for the M5 in the Hetzner console, `hcloud context create easychamp`. |
| SSH to servers | `~/.ssh/config`: `hetzner`, `ec-postgres`, `azure1`, `azure2`; keys `aws_yahoo_centos7.pem`, `id_rsa`, `ec_hetzner_ash` | Private key files | New key on the M5, public key added to each server and to the hcloud project. |
| Azure CLI | `~/.azure` | 3 subscriptions as a user login, 1 saved service principal | `az login`. The service principal entry does not come with a login; re-add it only if a script needs it. |
| gcloud | `~/.config/gcloud` | User login, application default credentials, 2 service-account key files (`cli-admin-key.json`, `crawl-admin-key.json`) | `gcloud auth login` and `gcloud auth application-default login`. Send the two key files only if EasyChamp scripts use them. |
| GitHub | `gh` (keyring), git `osxkeychain` helper, SSH key `github_anton-abyzov_new` | Keychain-held token | `gh auth login`, `gh auth setup-git`. Nothing to copy. |
| Container registries | `~/.docker/config.json`, hosts `ghcr.io` and `harbor.easychamp.com`, store `desktop` | Keychain | `docker login` twice. |
| ArgoCD CLI | `~/.config/argocd/config` | Session tokens | `argocd login`. |
| npm and NuGet | `~/.npmrc` (npmjs and GitHub Packages tokens), `~/.nuget/NuGet/NuGet.Config` (source `github-anton`) | Tokens in files | `npm login`; re-add the NuGet source with a fresh GitHub token. |
| Mobile signing and store keys | `~/.config/easychamp/`: upload keystores, `signing/` (p12, key, provisioning profile), `play-publisher.json`, `firebase-adminsdk-fcm-v1.json`, `sendgrid.env` | Files | Files only, and some cannot be reissued (Android upload keystores). Send the folder. |
| Shell variables | `~/.zshrc`: `GEMINI_API_KEY_EASYCHAMP`, `GOOGLE_CLOUD_PROJECT`, `USE_GKE_GCLOUD_AUTH_PLUGIN`, others | Plain exports | Re-add the EasyChamp ones by hand, or move them to the manager. |

Not present on the M4: SOPS or age keys, direnv (`.envrc`), 1Password, Bitwarden, Doppler or Infisical CLIs, Terraform Cloud credentials, kubelogin.

### Inside the project folder (the copy carries these when secrets are ticked)

- **19 local-only secret files across 9 repositories**: `.env` files in `ec-iac-infrastructure` (7), `ec-mobile` (5), `ec-arena-ui` (2), `ec-chat-api` (2), and one each in `ec-coach-ui`, `ec-console-ui`, `ec-landing`, `ec-ml-api`, `ec-sim-ui`.
- **Terraform state is local and untracked.** `ec-iac-infrastructure/environments/prod/terraform.tfstate` and `modules/gcp/keycloak-config/terraform.tfstate` have no remote backend. The M4 holds the only copy, and state files contain secret values. `terraform.tfvars` files (3) are local too.
- `ec-mobile/apps/expo`: upload keystore and iOS distribution p12 and key, local only.
- Cluster secrets are **SealedSecrets** on `hetzner-ash-prod` (public sealing certificate tracked in `ec-gitops`). The private sealing key lives in the cluster, with `backup-sealing-key.sh` and `restore-sealing-key.sh` in `ec-iac-infrastructure/scripts/cluster-secrets`. A workstation does not need it.

### Two things found on the way

1. **Private key material is tracked in git**: `ec-security-api/ec-security-api/certificate-easychamp-com.pfx` and `certificate-easychamp-tech.key`, `ec-iac-infrastructure/keys/pgVM_aws_yahoo_centos7.pem` (also under `live/keys/`), `ec-iac-infrastructure/modules/azure/kong/certs/tls.key`. Every clone already has them, and so does GitHub. The `aws_yahoo_centos7.pem` key is the one `~/.ssh/config` uses for `hetzner`, `azure1` and `azure2`. If those are live, rotate that key. This matches the existing "EasyChamp credential rotation plan 2026-10" note title; I did not open it.
2. `ec-iac-infrastructure` Ansible inventory names `~/.ssh/kafka_cluster_key`, which does not exist on the M4. Stale, or already broken.

### What Obsidian already holds (titles only, contents not opened)

Present: a Hetzner Cloud API token note, "Prod AKS kubectl access runbook", "EasyChamp ops — Hetzner cluster and Postgres access", `github-ssh-easychamp-20260710`, two secrets rotation runbooks, "EasyChamp CI Credentials — Hub", "EasyChamp CI App — Registry (pointers, no secrets)", `ec-matchcam GITOPS_DEPLOY_KEY`, and an `EasyChamp` subfolder under Credentials.

Not found by title: the `ec-ash-prod` kubeconfig, the server SSH private keys, Terraform state, the `~/.config/easychamp` signing files, the per-repo `.env` files. Anton's guess is right: the file-shaped credentials are not in the vault.

Which of the five clusters are still live is not something file names can tell. The `cluster-migration/cutover/step7-retire-gke.sh` script suggests GKE and AKS are being retired in favour of Hetzner. Skip any retired cluster on the M5.

## 2. Approaches, ranked

| Rank | Approach | Safety | Effort now | At hundreds of repos | Revocation |
|---|---|---|---|---|---|
| 1 | Sign in again per machine (`az`, `gcloud`, `gh`, `docker`, `argocd`, new hcloud token, new SSH key) | Best. Each machine has its own identity; nothing secret travels. | About 20 minutes, once per machine | Flat. Logins are per machine, not per repo. | Per machine: revoke one token or key. |
| 2 | Secrets manager with `op run` or similar; repos commit a `.env.tpl` of references | High. Values never sit in files; one audit trail. | 1 to 2 days to move 19 files and the shell exports | Best. New machine or new repo costs one sign-in. | Deauthorize the device; rotate in one place. |
| 3 | SpecWithCode encrypted transfer of chosen files | Good for transport. The key is still shared between machines afterwards. | Minutes | Poor as the main method; fine for the short list of file-only items. | None per machine. Rotating means replacing it everywhere. |
| 4 | SOPS with age, encrypted files in git, one key per machine | High, and no vendor. | 2 to 3 days, plus a `.sops.yaml` per repo | Medium. Adding a machine means re-encrypting every repo. | Remove the recipient and re-encrypt everywhere; old commits stay readable to the old key. |
| 5 | Copy `~/.kube`, `~/.ssh`, `~/.azure`, `~/.config` wholesale | Worst. Clones tokens for unrelated clients (Colibri AWS profiles, old contractor keys) and every machine becomes the same identity. | Minutes | Looks easy, fails quietly: Keychain-held tokens (`gh`, docker, git) do not come along. | None. One lost laptop means rotating everything. |

A "machine profile" bundle is not a sixth method. It is rank 1 and rank 3 packaged: a manifest that says which items are logins and which are files. That is the right product shape (section 4).

Why this order:

- **Most of EasyChamp's access is already login-based.** AKS, GKE, GitHub, registries and ArgoCD all rebuild from a sign-in. Copying their files saves 10 minutes and gives up per-machine revocation.
- **Repository count barely matters for machine credentials.** 36 or 300 repos still use one Azure login, one Hetzner token, one SSH key. What grows with repo count is `.env` files, and only a manager (rank 2) fixes that.
- **Rank 2 over rank 4 for Anton**: he works solo across four machines and adds machines often. A manager makes a new machine one sign-in. SOPS makes it a re-encrypt across every repo. SOPS wins only if avoiding a vendor matters more than that.
- **Rank 3 has a real job**: a small set of files cannot be recreated by signing in.

## 3. Recommended for EasyChamp now: steps for the M5

### A. Copy the project (carries the in-folder files)

1. In SpecWithCode, **Copy to another machine** for `sw-easychamp` with secrets ticked. This carries the 19 `.env` files, the Terraform state and `tfvars`, and the `ec-mobile` signing files.
2. From then on, run `terraform apply` on one machine only. The state has no remote backend and no lock, so two machines applying will corrupt it. Moving it to a remote backend (an Azure Storage or Hetzner object storage bucket) removes this limit and is the single most useful infra fix here.

### B. Send the file-only items (encrypted transfer, 5 items)

Send with `studio_file_transfer`, never chat, AirDrop or SSH:

```
/Users/antonabyzov/.kube/ec-ash-prod.yaml
/Users/antonabyzov/.config/easychamp
/Users/antonabyzov/.config/gcloud/cli-admin-key.json
/Users/antonabyzov/.config/gcloud/crawl-admin-key.json
/Users/antonabyzov/.config/hcloud/cli.toml
```

The last three are optional: prefer a new M5 hcloud token (step C4), and send the two gcloud key files only if an EasyChamp script reads them. Set mode `600` on each after it lands.

### C. Sign in on the M5 (about 20 minutes)

1. Tools: `brew install kubectl azure-cli hcloud terraform gh helm argocd` and `brew install --cask google-cloud-sdk`, then `gcloud components install gke-gcloud-auth-plugin`.
2. GitHub: `gh auth login`, then `gh auth setup-git`.
3. Azure and AKS: `az login`, `az account set --subscription "Microsoft Azure Sponsorship"`, then for each live cluster `az aks get-credentials --resource-group <rg> --name <cluster>`. Resource groups: `rg-easychamp-prod-aks`, `rg-ec-aks-prod-east-us-v2`, `rg-sc-aks-prod-east-us`.
4. Hetzner: create an API token named `m5` in the Hetzner console for the EasyChamp project, then `hcloud context create easychamp` and paste it at the prompt.
5. SSH: `ssh-keygen -t ed25519 -f ~/.ssh/ec_m5 -C "m5"`, `hcloud ssh-key create --name m5 --public-key-from-file ~/.ssh/ec_m5.pub`, then from the M4 append `ec_m5.pub` to `authorized_keys` on `hetzner`, `ec-postgres`, `azure1` and `azure2`. Copy the four `Host` blocks from the M4's `~/.ssh/config` with `IdentityFile ~/.ssh/ec_m5`.
6. Hetzner cluster: `export KUBECONFIG=~/.kube/config:~/.kube/ec-ash-prod.yaml`, then `kubectl --context ec-ash-prod get nodes`.
7. GKE, only if still live: `gcloud auth login`, `gcloud auth application-default login`, `gcloud container clusters get-credentials ec-gke-prod-us-east1 --region us-east1 --project easychamp`.
8. Registries and ArgoCD: `docker login ghcr.io`, `docker login harbor.easychamp.com`, `argocd login <server>`.
9. Packages: `npm login`; add the `github-anton` NuGet source with a new GitHub token.
10. Shell: add the EasyChamp exports (`GEMINI_API_KEY_EASYCHAMP`, `GOOGLE_CLOUD_PROJECT`, `USE_GKE_GCLOUD_AUTH_PLUGIN=True`) to `~/.zshrc`.

### D. Check it

```
gh auth status
az account show --query name
kubectl config get-contexts
kubectl --context ec-ash-prod get nodes
hcloud server list
ssh hetzner true && ssh ec-postgres true
terraform -chdir=repositories/anton-abyzov/ec-iac-infrastructure/environments/prod plan
```

### E. Next, when there is a free day

1. Move the 19 `.env` files and the shell exports into one manager and commit `.env.tpl` reference files. Then a new machine needs steps B and C only, and step A needs no secrets tick.
2. Remote Terraform backend with locking.
3. Rotate and remove the tracked private keys listed in section 1.

## 4. What SpecWithCode could add

1. **"Credentials this project uses" checklist in the copy dialog.** Scan the project for markers and show one row per need: Terraform providers (`azurerm`, `hcloud`, `google`), kube contexts and `KUBECONFIG` paths named in scripts, SSH hosts in Ansible inventories, registries in workflows and Dockerfiles, package registries in `.npmrc` and `NuGet.Config`, `.env` keys. Names only, never values.
2. **Probe the destination, no secrets involved.** For each row run a status command there (`gh auth status`, `az account show`, `hcloud context list`, `kubectl config get-contexts`, `docker login` state) and mark it Ready, Not signed in or Tool missing.
3. **Three actions per row**: Sign in there (opens a terminal on the destination with the login command), Send file (encrypted transfer, offered only for file-only items, mode `600`, with an explicit list), or Skip. Never offer to copy a whole `~/.ssh` or `~/.kube`.
4. **A committed manifest**, `.specweave/project/credentials.json`: what the project needs, how each item is obtained (login command, or file path and where its source of truth is), no values. This is the "machine profile", and it is what makes the tenth machine as easy as the second.
5. **Warnings the scan can raise for free**: Terraform state with no remote backend, private keys tracked in git (extends increment 1328's tracked-secret flag), a key path named in config that does not exist on the source.
6. **Per-machine identity by default.** Where a provider supports it (SSH keys, Hetzner and GitHub tokens), generate a new one named after the destination machine instead of sending the old one, so removing a machine from the fleet can list exactly what to revoke.

Items 1 to 3 are one increment and fit next to the copy flow in 1325, 1328 and 1334. Item 4 is small and should land with it. Items 5 and 6 can follow.
