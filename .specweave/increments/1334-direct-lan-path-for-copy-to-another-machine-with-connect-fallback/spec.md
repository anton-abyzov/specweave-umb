# Direct LAN path for Copy to another machine, with Connect fallback

## Problem

"Copy to another machine" always moves files through SpecWithCode Connect, even when both Macs sit on the same network. The destination pulls from the source's Connect address. Every byte goes out through the source's internet upload, across the Cloudflare edge and back down to the destination. On November 14, 2026, Anton copied specweave (122,249 files, 7.5 GB) from m4 to m5 in the same house. The transfer was capped by m4's upload speed: about 10 minutes at 100 Mbit/s, against well under a minute over a gigabit LAN. Each request also paid a round trip to Cloudflare.

The destination client already supports a second address for the same source (`fallbackBaseUrl` in `apps/server/src/fleet/folderTransfer/sourceClient.ts`). It moves on a network error or a 5xx, and only after `/.well-known/studio/environment` confirms the machine. `checkSourceUrl` only accepts Connect and `*.ts.net` names, and nothing offers a LAN address.

## Scope

In:
- The source offers one or more LAN addresses for a copy: a private IPv4 or IPv6 address and port, plus the SHA-256 fingerprint of a certificate generated for that copy.
- The destination tries the LAN address first. It pins the certificate by fingerprint, confirms the source's environment id, and falls back to Connect on any failure. Once the LAN address fails, the rest of the copy stays on Connect.
- A listener on the source that serves only the folder-transfer routes over TLS. It is bound to the private addresses, opens with the first LAN offer, and closes when no copy is offered or running.
- A setting, off by default for the first release, "Copy over the local network when both machines are on it", plus a line in the copy dialog saying which path the copy took.
- A security review before building, and an adversarial review of the result.

Out:
- LAN discovery for anything other than folder copies: threads, file transfer and Connect traffic.
- NAT traversal, relays or peer-to-peer outside one network.
- mDNS/Bonjour browsing. The address travels inside the authenticated offer instead.

## Acceptance Criteria

- [ ] AC-01: With both machines on one network and the setting on, a copy pulls its manifest and chunks from the source's LAN address, and the dialog says "Over your local network".
- [ ] AC-02: When the LAN address does not answer, presents a different certificate, or names a different environment, the copy continues over Connect without failing, and the dialog says "Over SpecWithCode Connect".
- [ ] AC-03: The LAN listener accepts only folder-transfer routes with a valid per-copy transfer token. Without one it answers 401 before reading a body, and it is closed when no copy is offered or running.
- [ ] AC-04: Each operation gets its own certificate and key, generated in memory and never written to disk or logged. The certificate (IP SANs only, `CA: false`, `serverAuth`) and its fingerprint reach the destination only inside the copy offer, over the already-authenticated Connect channel.
- [ ] AC-05: An older destination ignores the LAN offer and copies over Connect. An older source never offers one.
- [ ] AC-06: The security review's findings are recorded in reports/ and each one is fixed or accepted with a reason before the setting can be turned on.
- [ ] AC-07: A real-socket test puts an impostor at the offered address with a different self-signed certificate and the correct environment id; it receives no request carrying the token, and the copy completes over Connect.
- [ ] AC-08: A certificate whose DER hash differs from the pin is refused before any HTTP byte is sent, tested through the production fetch stack, not an injected mock.
- [ ] AC-09: The listener closes when every operation is terminal, after 15 minutes without an authenticated request, after 2 hours at most, and on a network change; after sleep, wake or an address change it rebinds with a fresh offer or stays closed.
- [ ] AC-10: Port scans and unauthenticated probes get only TLS and a generic 401 or 404: no environment endpoint, no identifying header or certificate subject, bodies over 4 MB refused while streaming, and 401 floods from one address do not block a valid token from another.
- [ ] AC-11: Killing, blackholing or trickling the LAN path at any point, mid-manifest or mid-chunk, latches the operation to Connect within one total deadline, across client restarts and keepalives, and the dialog reports a mixed path.
- [ ] AC-12: Address admission refuses `172.15.x`, `172.32.x`, `100.64.x`, `169.254.x`, `fe80::` with a zone id, `::ffff:192.168.0.1`, global IPv6 and any hostname; each offered address is bound on its own socket, never a wildcard.
- [ ] AC-13: Secret files travel the LAN path only under the same pin, and a LAN failure during the secret step falls back without re-sending a secret to an unverified peer.
- [ ] AC-14: The `lan` block appears in no log, crash report or telemetry, is stored only in the 0600 destination record and is removed with it; the destination's setting must be on too.

## Approach

Files, in order:
1. `packages/contracts/src/folderCopy.ts`: `FolderCopyOffer` gains an optional `lan` with `{ addresses: [{ host, port }], certificateSha256 }`.
2. `apps/server/src/fleet/folderTransfer/lanListener.ts` (new): a TLS server bound to the private interface addresses (RFC 1918, RFC 4193 and link-local excluded by default). It has a self-signed ECDSA P-256 certificate generated in memory, routes only to `handleSourceRequest`, and opens and closes with offered copies.
3. `apps/server/src/fleet/folderTransfer/sourceService.ts` offer(): adds the `lan` block when the setting is on and the listener is up.
4. `apps/server/src/fleet/folderTransfer/sourceClient.ts`: `checkSourceUrl` admits a private IP literal only together with the offered certificate. Every LAN request, retries included, goes through a dispatcher that trusts only that certificate (`ca`) and compares its DER SHA-256 with the pin, or a connector that checks `fingerprint256` on `secureConnect` and destroys the socket before any HTTP byte. Never `connect.checkServerIdentity` with undici: it does not pin (security review, P0). No environment probe on LAN: the pinned handshake, then the authenticated `hello`, which checks `environmentId` and `operationId`. The LAN address becomes `baseUrl`, Connect `fallbackBaseUrl`; `wrong_machine` is fatal only on Connect.
5. `apps/server/src/fleet/folderTransfer/destinationService.ts`: one total deadline for the LAN attempt; any LAN failure, pin change mid-transfer included, latches the operation to Connect in its record, so resume, retry and keepalive never re-probe. Records the bytes served per path for the label.
7. The listener reuses `folderTransferRoute.ts`'s gate (failure limiter keyed by socket peer, streamed 4 MB body cap, update hold), caps connections and handshakes, sets short TLS, header and request timeouts, and sends no `Server` or CORS headers. It binds only RFC 1918 and RFC 4193 addresses, one socket each, skipping tunnel and virtual interfaces, and runs in the signed server process.
6. `apps/web`: the setting and the path line in the dialog's progress panel.

Security review topics (T-01):
- The transfer token must never reach an unpinned peer. The environment check and every request go over the pinned TLS connection, and the token is sent only after the pin matches.
- An attacker on the same network could answer at the offered address with another certificate, or replay an old offer. Each listener lifetime gets a fresh certificate and the offer carries its fingerprint, which defeats both.
- Exposure: the listener must not become a general server, so it gets the minimal route table, rate limits on 401s, and no directory listing or health page. Bind to private addresses only, never 0.0.0.0, and keep it closed when idle.
- Leaks: offering LAN addresses tells the destination machine about the source's network. That is acceptable between machines the same account owns; the review should confirm the address never goes to Connect's relay logs.
- The macOS firewall prompt on first listen: decide whether to ship it, or document it in the setting's help text.
- Windows and Linux: per-OS firewall behaviour and interface enumeration.

Rejected:
- Plain HTTP on the LAN: the token and the files would travel in the clear.
- mDNS discovery: it advertises the machine to everyone on the network, and the authenticated offer already carries the address.
- Tailscale: it is off on purpose (owner's rule).

Risks: corporate networks with client isolation (the fallback covers them), VPNs that make a "private" address non-local, and machines with several interfaces (offer each one and try them in order with a short connect timeout, 1.5 s).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: The setting is off by default for the first release and turned on after the security review and a week of use → default off (reversible).
- D-02: The certificate is pinned by fingerprint inside the offer, not issued by a local CA → pin (reversible).
- D-03: The connect timeout per LAN address is 1.5 s, inside one total LAN deadline of 5 s to first byte, before falling back → 1.5 s / 5 s (reversible).
- D-04: One certificate per operation, not per listener lifetime (security review P2) → per operation.
### Open
- none

## Tasks

### T-01 Security review of the design
- AC: AC-06 | Files: .specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/reports/security-review.md | Test: test -s .specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/reports/security-review.md

### T-02 LAN listener with a per-lifetime pinned certificate
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/lanListener.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/lanListener.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceService.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer/lanListener

### T-03 Offer carries the LAN address; destination pins, tries it first, falls back to Connect
- AC: AC-01, AC-02, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/folderCopy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceClient.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/destinationService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/twoServer.lan.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer/twoServer.lan

### T-04 Setting and the path line in the copy dialog
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyProgressPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/CopyProgressPanel

### T-06 Firewall check on signed builds per OS
- AC: AC-06 | Files: .specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/reports/firewall.md | Test: test -s .specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/reports/firewall.md

### T-05 Verify and close 1334
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14 | Files: .specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/reports/ | Test: specweave verify 1334
