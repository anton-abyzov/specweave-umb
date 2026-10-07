# Fleet and installation audit

Read-only audit performed at 2026-10-07T02:52:43-04:00 (America/New_York). No installation, account, SSH trust, power, process, T3 setting or repository ownership changes were made. SpecWeave installed and npm stable were both 3.0.3. No pickup or claim ran.

## Current fleet

| Host | Identity evidence | SSH | Provider/install verification |
|---|---|---|---|
| Main M4 | Live LocalHostName Antons-MacBook-M4MAX; user antonabyzov; arm64; macOS 27.0.1 | Local execution | T3 service 0.0.45 alive at 127.0.0.1:3773; isolated official Codex 0.160.1 and Claude Code 2.1.292 present |
| M1 | Prior confirmed Antons-MacBook-Pro-M1MAX-2.local / 192.168.40.134; current SSH ED25519 equals saved public key | TCP22 reachable; noninteractive auth fails | No authenticated remote preflight possible; ports 3773/8317/9090 refused |
| M3 / Olympus | Prior confirmed Antons-MacBook-Pro.local / 192.168.40.66; current SSH ED25519 equals saved public key | TCP22 reachable; noninteractive auth fails | No authenticated remote preflight possible; ports 3773/8317/9090 refused |

Ports were checked only on these exact intended hosts. Closed LAN T3/proxy ports do not prove that no loopback service is installed remotely. DHCP IPs can change; the current key comparison guards against silently connecting to another host.

The saved SSH public-key files contain an OpenSSH banner comment before their key line. The comparison excludes comment lines and compares key type and key body. Both keys matched. Fingerprints:

- M1: SHA256:a72Agjp6kD7Eks4+czlhKo5prum6oOLPEWlgMVkKauo
- M3: SHA256:3FytqsZXyrwWAsoE/7fla+nmgHWRnC0TKNHlp3wgfro

Authenticated attempt on each host used only antonabyzov (the local account name), BatchMode=yes, StrictHostKeyChecking=yes, ConnectTimeout=5, and the corresponding saved public-key file as UserKnownHostsFile. Both returned exit 255: Permission denied (publickey,password,keyboard-interactive). No passwords or prompts were requested and no global known_hosts entry was added. No other usernames were guessed. The worker macOS username remains unverified, so this failure does not identify the remote username.

~/.ssh/config and config.d have no Mac worker aliases. This shell reports no connected SSH authentication agent. Existing private-key files were not read or copied. Existing production/GitHub aliases were left untouched.

## Local installed state

T3 app exists at /Applications/T3 Code (Alpha).app and CLI at ~/.local/bin/t3. Its launch agent com.t3tools.t3code.service is RunAtLoad=true / KeepAlive=true and runs its isolated 0.0.45 runtime. Port 3773 belongs to T3 PID 6263 and listens only on 127.0.0.1. The service uses ~/.local/share/t3-anton. No restart was performed.

T3 settings have two enabled provider instances: codex and claudeAgent. Both point to ~/.local/share/t3/providers/node_modules/.bin/ and currently use default account directories. Cursor, Grok and OpenCode are disabled. No additional provider instances or remote connection configuration were found in those settings.

The SQLite projection, read through mode=ro, has two turns: one completed Codex smoke test and one Claude error. Both corresponding provider runtime sessions are stopped. This confirms the retained prior smoke-test state, without submitting another inference task or claiming that Claude quota has reset.

Native authentication checks returned:

| Profile | Live authentication state |
|---|---|
| Isolated Codex | Logged in using ChatGPT; exit 0. Current plan/account ownership was not inferred from this output. |
| Native Claude default | loggedIn=true, authMethod=claude.ai, apiProvider=firstParty, subscriptionType=max; exit 0 |
| Claude profile 2 | loggedIn=false, authMethod=none; exit 1 |
| Claude profile 3 | loggedIn=false, authMethod=none; exit 1 |

Existing global Codex 0.153.4 and Claude 2.1.291 remain installed. Numerous Claude/Codex processes are active and were preserved. Provider installation checks used the isolated paths.

The account helper supports numeric 1|2|3. Use specweave-claude-account 1 for the native default; the literal word default returns usage exit 2. Its profile 2/3 behavior is correctly isolated with CLAUDE_CONFIG_DIR. No HOME override or credential transfer occurred.

AnyModel 1.16.1 is installed globally under Node 22.20.0. No listener exists on 127.0.0.1:9090, and neither ~/.config/anymodel nor ~/.anymodel exists. anymodel --version is not a supported version-only probe: it fell through to the client and exited with Proxy not running; package.json supplied the installed version instead. This did not start a proxy.

CLIProxyAPI was not found in the usual application/config locations or binary locations; no listener exists on 127.0.0.1:8317. Tailscale was not found in /Applications, user Applications, standard Homebrew/local bin paths, launch agents/daemons, or process names. This is bounded installation evidence, not a complete filesystem search.

Main Mac AC and battery power both still have sleep=1; logged-in and awake availability is required. No caffeinate or persistent power change was started.

## Remaining gates

1. Authenticated worker access: verify each actual macOS username and install/enable an authorized public key or use an already authenticated device connection. Then run the existing worker-preflight.sh; do not copy subscription tokens or private keys.
2. Extra native subscription sign-ins: Claude 2/3 are prepared but unsigned. Codex additional profiles are not configured. The prior seven-subscription design therefore still needs five native account sign-ins and account-to-label verification.
3. Tailscale/CLIProxyAPI: absent in bounded checks. Local setup can be performed in isolated directories, but remote rollout depends on gate 1 and native auth depends on gate 2.
4. Remote T3 pairing and provider availability: neither worker installation nor native accounts can be verified until authenticated preflight. Do not expose the T3 or proxy listener publicly.
5. Unattended availability: the chosen Mac must remain logged in and awake; current install/service status does not ensure overnight availability.

## Sources

- /Users/antonabyzov/Projects/research/claude-projects-2026-10-06/installation-receipt.md
- /Users/antonabyzov/Projects/research/claude-projects-2026-10-06/setup-guide.md
- /Users/antonabyzov/Projects/research/claude-projects-2026-10-06/fleet-manifest.json
- /Users/antonabyzov/Projects/research/claude-projects-2026-10-06/tools/worker-preflight.sh
- Saved public SSH keys in that research folder's evidence directory
- Live version, socket, launch-agent, native auth, SQLite projection and pmset readback described above
