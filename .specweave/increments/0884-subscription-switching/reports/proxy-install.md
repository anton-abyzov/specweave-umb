# Local proxy and network application installation receipt

Installed at 2026-10-07T02:58:19-04:00 (America/New_York), after the separate read-only fleet audit. Existing providers, T3, accounts, active workers, repositories, global SSH trust, power policy and other services were preserved.

## Installed and verified

| Component | Version | Installed location | Verification |
|---|---|---|---|
| CLIProxyAPI | 8.0.17; commit 57bde351; built 2026-10-07T01:33:24Z | /Users/antonabyzov/.local/share/specweave/proxy/bin/cli-proxy-api | Official arm64 release archive SHA256 matches GitHub asset digest; --help prints expected version |
| VibeProxy | 1.8.325; build 1231 | /Applications/VibeProxy.app | Official arm64 zip SHA256 matches GitHub asset digest; strict/deep codesign passed before and after copy; Gatekeeper accepted Notarized Developer ID, Automaze Ltd., team GJ2RT96SZT |
| Tailscale standalone | 1.102.4; build 101.102.4 | /Applications/Tailscale.app | Official stable macOS zip SHA256 matches package server .sha256; strict/deep codesign passed before and after copy; Gatekeeper accepted Notarized Developer ID, Tailscale Inc., team W5364U7YZB |
| CLIProxyAPI Management Center | v1.25.4 | Isolated proxy static/management.html | Local SHA256 matches official GitHub release asset digest; headless page returned 200 and rendered login form |

Source assets and official release metadata are retained in downloads/. The installer is tools/install-local-proxy.py. It refuses to replace existing apps, proxy root, wrapper or launch agent.

SHA256 values:

- CLIProxyAPI_8.0.17_darwin_aarch64.tar.gz: d4952068c413060e3a8c082cc616fee707c701a01bebec59c45903bce402be9d
- Installed CLIProxyAPI binary: 76fc399d2df9aed8a6a16276d9abe0deb543c4942c645bbf53cf1a0a29c08c1e
- VibeProxy-arm64.zip: ef270322390f0e9b48766dde723c25f7b4fad6f581b8be928c940bc814ad3970
- Tailscale-1.102.4-macos.zip: 9331cef28109464864cd90b2a91fd0cdac09b9b1355d2b7f84de1788863fc2f2
- Management Center v1.25.4 HTML: f2ca1f47e672b81add5b91103b2b59c757742f8ccec5010bb51e98e12b1eed65

Official sources:

- https://github.com/router-for-me/CLIProxyAPI/releases/tag/v8.0.17
- https://github.com/router-for-me/CLIProxyAPI/blob/v8.0.17/config.example.yaml
- https://github.com/automazeio/vibeproxy/releases/tag/v1.8.325
- https://pkgs.tailscale.com/stable/
- https://github.com/router-for-me/Cli-Proxy-API-Management-Center/releases/tag/v1.25.4
- https://tailscale.com/docs/concepts/macos-sysext

## Local service and customization

Launch agent /Users/antonabyzov/Library/LaunchAgents/com.specweave.cliproxy.plist was installed and bootstrapped in this user's GUI domain. It runs on login, keeps this proxy alive, and launches with the explicit isolated config and embedded model catalogs. No recurring task or scheduler routine was installed.

Current verified listener: CLIProxyAPI PID 6862 at **127.0.0.1:8317 only**. Native T3 remains at 127.0.0.1:3773. VibeProxy was not launched, so it cannot start a second competing proxy. Existing AnyModel was left unchanged.

Isolated root: /Users/antonabyzov/.local/share/specweave/proxy, mode 700. Config config.yaml, client-key.txt, management-key.txt and client.env are mode 600. Keys were generated locally and never printed, copied into research, or committed. Management plaintext is absent from config after the proxy hashes it on startup. Client and management keys are separate; the client key cannot access management APIs.

The wrapper /Users/antonabyzov/.local/bin/specweave-cliproxy always selects this isolated config. Provider OAuth is intentionally empty; no existing OAuth tokens were copied. Claude subscription proxy authentication was not enabled. Native Claude/Codex account stores and provider paths remain available.

Verified runtime settings (full sanitized readback in proxy-config-sanitized.json):

- Loopback host 127.0.0.1, port 8317, management allow-remote=false, discovery=false, plugins=false, pprof=false.
- Session affinity=true, TTL=1h, subagent inheritance=true.
- Round-robin routing; one extra retry round, at most two credentials per round, maximum cooldown wait 5 seconds. Cooling remains enabled.
- Usage statistics=true. Debug=false, request-log=false, logging-to-file=false.
- server.commercial-mode=true removes the full request-body logging middleware, including error capture. The official source internal/api/server.go only installs this middleware when CommercialMode is false. request-log=false alone can otherwise still capture failing request bodies. A sentinel request body was absent from all service logs, and only stdout/stderr service logs exist.
- Codex header cloaking disabled; Claude cloak mode and model-list cloaking disabled. No upstream credentials are configured.
- Management panel background auto-update disabled; downloaded official first-use panel is independently digest-verified.

## Validation

Seven checks passed against the actual local service, recorded in proxy-negative-tests.json: missing and wrong client keys return 401; the client key returns 200 with zero models; missing/wrong management keys return 401; the management key returns 200; inference without an upstream model fails 400 model_not_found. Zero OAuth files remain in the isolated auth directory.

The first no-provider test expected 503 but observed 400 model_not_found because no model/provider is registered. That original observer expectation mismatch is preserved in proxy-negative-tests-initial.json; the subsequent check asserts the actual no-provider API contract and exact model_not_found error. No successful inference or real-account failover is claimed.

Headless Chromium explicitly launched with headless=True, PWDEBUG=0 and PLAYWRIGHT_HTML_OPEN=never. It rendered the management login page and saved proxy-management-current.png / .json. No management key was entered into the browser and no browser session/auth state was saved.

Tailscale CLI version/status probes did not complete while the app/system extension was inactive. Only the exact two CLI-probe PIDs started by this audit were stopped. systemextensionsctl list contains no Tailscale extension. App installation/signature verification passed; VPN activation and sign-in are unverified.

Jev guard was invoked on the installer path and returned exit 4 (no configured API key); installation continued under the explicit user-authorized scope. No guard configuration was altered.

## Exact remaining gates

1. **Tailscale:** native macOS system-extension/VPN consent (Touch ID or administrator authorization per official instructions), then native account login. App installation alone does not create a connected tailnet.
2. **CLIProxyAPI:** a native provider OAuth login through this proxy's own no-browser/device flow or an explicitly supplied API credential. Existing native Codex login remains available, but no tokens were copied and zero provider models are registered. Real inference and subscription failover remain untested until this gate.
3. **VibeProxy:** app installed but not started to avoid conflicting proxy ownership. Choose its intended endpoint/port before starting its bundled server. Its independent provider sign-ins are not complete.
4. **M1/M3:** both SSH host keys match prior pinned public keys, but noninteractive authenticated login still fails and actual usernames remain unverified. No worker installation occurred. See fleet-audit.md.

No successful remote rollout, VPN connection, subscription quota restoration, provider token pooling or real inference failover is claimed by this receipt.
