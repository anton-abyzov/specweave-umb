# Direct LAN path for Copy to another machine, with Connect fallback

## Problem

"Copy to another machine" always moves files through SpecWithCode Connect, even when both Macs sit on the same network. The destination pulls from the source's Connect address. Every byte goes out through the source's internet upload, across the Cloudflare edge and back down to the destination. On November 14, 2026, Anton copied specweave (122,249 files, 7.5 GB) from m4 to m5 in the same house. The transfer was capped by m4's upload speed: about 10 minutes at 100 Mbit/s, against well under a minute over a gigabit LAN. Each request also paid a round trip to Cloudflare.

The destination client already supports a second address for the same source (`fallbackBaseUrl` in `apps/server/src/fleet/folderTransfer/sourceClient.ts`). It moves on a network error or a 5xx, and only after `/.well-known/studio/environment` confirms the machine. `checkSourceUrl` only accepts Connect and `*.ts.net` names, and nothing offers a LAN address.

## Scope

In:
- The source offers one or more LAN addresses for a copy: a private IPv4 or IPv6 address and port, plus the SHA-256 hash of a certificate generated for that generation of the copy. The offer travels on the machine-to-machine control channel and is bound to the recipient, the operation and a generation (S-1).
- The destination tries the LAN address first. It pins the certificate by its hash, proves its own one-time key, and confirms the source and the operation. An unreachable address, a wrong pin or a wrong identity switches the copy once to Connect, and the rest of the copy stays there. A denial stops the copy on both paths (S-4).
- A listener on the source that serves only three read routes of one copy over mutual TLS (S-5). It is bound to eligible private addresses, opens for one generation of one operation, and closes with it, accepted sockets included (S-9).
- A setting on each machine, off by default, "Copy over the local network when both machines are on it", plus a line in the copy dialog saying which path the copy took. Both machines must have it on (S-7).
- A security review before building, and an adversarial review of the result.

Out:
- A LAN path for anything other than the measured Sync copy and Add's whole-folder copy: threads, file transfer, Git fetch, extras, secret files and Connect traffic.
- NAT traversal, relays or peer-to-peer outside one network.
- mDNS/Bonjour browsing. The address travels inside the authenticated offer instead.

## Acceptance Criteria

- [ ] AC-01: With both machines on one network and the setting on at both, a measured Sync ("Compare all files…") or a whole-folder Add pulls its manifest and chunks from the source's LAN address, and the dialog says "Over your local network". No other copy gets a LAN path, and every other step of these two stays on Connect (S-5).
- [ ] AC-02: When the LAN address does not answer, presents a different certificate, or fails the `hello` identity check, the copy switches once to Connect without failing, and the dialog says "Over SpecWithCode Connect". A denial (revoked grant, refused approval, changed scope, failed Connect identity check) stops the copy on both paths (S-4).
- [ ] AC-03: The LAN listener finishes a TLS handshake only with the recipient certificate bound to its operation generation (S-2). After that it serves only the three routes in S-5, with that generation's LAN token, checked before a body is read. A peer without the recipient key gets a failed handshake and no HTTP response. The listener and its accepted sockets close when the generation ends (S-9).
- [ ] AC-04: Each operation generation gets its own source key and certificate (IP SANs only, `CA: false`, `serverAuth`) and its own recipient key and certificate (`CA: false`, `clientAuth`), generated in memory and never written to disk or logged. Only the SHA-256 hashes of the DER certificates cross the wire, inside the `lan` block, on the already-authenticated machine-to-machine control channel (S-1).
- [ ] AC-05: An older destination does not answer `lanCheck`, so no listener is bound and the copy runs over Connect. An older source never asks.
- [ ] AC-06: Each security review is recorded in reports/. The setting cannot be turned on until the design review says DESIGN OK, an implementation review confirms that findings 1 to 4 of the November 19, 2026 review are fixed in code, and AC-34 and AC-35 are met (S-11). Findings 1 to 4 are fixed, never accepted.
- [ ] AC-07: A real-socket test puts an impostor at the offered address with a different self-signed certificate and the correct environment id; it receives no HTTP byte and no token, and the copy completes over Connect.
- [ ] AC-08: A certificate whose DER hash differs from the pin is refused before any HTTP byte is sent, on every connection, retries and keepalive reconnects included, tested through the production fetch stack, not an injected mock.
- [ ] AC-09: A generation's listener closes when its operation is terminal, after 15 minutes without an authenticated request, after 2 hours at most, and on a network change. After sleep, wake or an address change it stays closed; a LAN path returns only through a new generation offered on the control channel (S-9).
- [ ] AC-10: Port scans and unauthenticated probes get only a TLS handshake that fails: no HTTP response, no environment endpoint, no identifying header or certificate subject. An authenticated request for anything off the allow list gets a fixed 401 or 404. Bodies over 128 KiB are refused while streaming, and a flood from one address does not block the valid peer at another (S-8).
- [ ] AC-11: Killing, blackholing or trickling the LAN path at any point, mid-manifest or mid-chunk, latches the operation to Connect within the S-8 deadlines (5 s for connection setup, 15 s without body progress), across client restarts and keepalives, and the dialog reports a mixed path.
- [ ] AC-12: Address admission refuses `172.15.x`, `172.32.x`, `100.64.x`, `169.254.x`, `fe80::` with a zone id, `::ffff:192.168.0.1`, global IPv6 and any hostname, on both machines; each offered address sits on a physical, directly attached interface (S-7) and is bound on its own socket with an OS-assigned port, never a wildcard.
- [ ] AC-13: Secret files never travel the LAN path in this release. The secret routes answer 404 on the LAN listener and stay on Connect with the same per-file approval and recipient sealing. A LAN failure before or during the secret step sends no secret to any LAN peer, and the secret step completes on Connect.
- [ ] AC-14: The `lan` block, its addresses, hashes and LAN token appear in no log, error text, crash report or telemetry on either machine, in the browser, or in Connect relay records. Keys, token and addresses live in memory only; the 0600 destination record keeps the generation number, the path latch and the bytes per path, and is removed with the copy (S-10). The destination's setting must be on too.
- [ ] AC-15: The destination refuses a `lan` block whose `scopeSha256`, `targetSha256` or `bindingSha256` it cannot recompute from its own record, or whose source, destination, operation or purpose differs, and opens no connection for it (S-1).
- [ ] AC-16: A `lanCheck` at or below the highest generation seen, and a `lanOffer` for any other generation, are refused, also after either machine restarts. A superseded generation's listener, token and keys read no data, and a terminal operation never gets a listener again (S-1).
- [ ] AC-17: On a real socket, a client with the right LAN token but no certificate, another certificate, or the right certificate without its key fails the TLS handshake. It gets no HTTP response, and the source reads no request byte from it (S-2).
- [ ] AC-18: With two copies running at once, the token and recipient certificate of one read nothing from the other's listener (S-2).
- [ ] AC-19: Only the control channel creates or renews a LAN offer. No LAN route and no LAN response can create, renew or extend an offer, generation, token, address or deadline, and the browser-relayed `FolderCopyOffer` never carries the `lan` block (S-1).
- [ ] AC-20: Every LAN connection goes through the one LAN connector: TLS 1.3, ALPN `swc-folder-lan/1`, no resumption or 0-RTT, no redirects, no proxy settings, no plaintext, no environment probe, a pool of at most 4 connections owned by one operation generation. The first request on each connection is `hello`, and it must match the environment, operation, generation and binding (S-3).
- [ ] AC-21: Each row of the S-4 decision table is tested on real sockets. Unreachable, wrong pin and wrong identity switch once to Connect. Revoked, refused, changed scope and a failed Connect identity check stop the copy, and it does not continue on Connect. Each denial is saved on the operation record before the generation's sockets close, so a destination that sees only a reset is stopped by its first Connect request.
- [ ] AC-22: The switch to Connect is saved in the destination record before the first Connect request. The Connect address and credentials come only from the original offer's record, never from a LAN response. Unverified partial data is discarded, and after a wrong pin or wrong identity a staged chunk is kept only if the manifest fetched over Connect names its hash (S-4).
- [ ] AC-23: The LAN listener serves `GET hello`, `GET manifest` and `POST chunks` for its own operation and nothing else. Every other method and route, including `POST manifest`, `validate`, `stat`, `refresh`, `ancestry`, `secrets`, `secret`, `release` and `commit`, answers 404 before a body is read and changes nothing (S-5).
- [ ] AC-24: A selection outside the frozen ceiling is refused on the control path and stops the copy. On the LAN a chunk hash outside the operation's manifest returns no bytes, and no request field is resolved as a source path (S-5).
- [ ] AC-25: A manifest with an absolute path, a parent escape, a Windows reserved or stream name, an alias under the destination volume's rules, or sizes over the staging limit is refused before any chunk is requested, and nothing is written outside staging. Before any final write, every folder from the approved target down to the written entry must pass the exclusive-control rule of S-6; a write that fails it is refused before anything is changed, with a reason that names the folder. Gate: in an existing reviewed tree with a group-writable or other-owned folder below the target, that write is refused and files outside the target are byte-for-byte unchanged, over the LAN and over Connect (S-6).
- [ ] AC-26: No final write happens through a folder that another local user could change: the exclusive-control rule of S-6 holds for the whole chain before each write and is checked again after it, and a change found afterwards stops the copy and is reported. A link, junction, other reparse point or different folder on the chain refuses the write, and every file outside the approved folder is untouched. The rule belongs to apply and is the same over the LAN and over Connect; a switch of transport never widens what apply may write. Root and the app's own user are outside this promise. Add still requires a missing or empty target, and Sync still writes only what was reviewed (S-6).
- [ ] AC-27: The source opens no body reader until the method, route, operation, LAN token, generation and grant have passed, and an unauthenticated connection never moves the idle timer (S-2, S-8).
- [ ] AC-28: Every source limit in S-8 is enforced and tested at one past its value: generations, addresses, handshakes, failed handshakes, sockets, concurrent reads, header and body sizes, and each deadline.
- [ ] AC-29: Every destination limit in S-8 is enforced with streamed, counted reads. A source that sends an oversized or highly compressed manifest or chunk batch is cut off at the limit, memory stays bounded, and the copy switches to Connect.
- [ ] AC-30: With the setting off on either machine no key is made, no socket is listening, no `lanCheck` is sent or answered with data, and no `lan` block exists. A change to off ends live generations (S-7, S-9).
- [ ] AC-31: Only physical, directly attached interfaces are used, checked on both machines. An ambiguous interface, a route through a tunnel, a failed bind or a refused firewall prompt means no LAN path and a completed copy over Connect. The app changes no firewall rule and maps no port (S-7).
- [ ] AC-32: On rotation, cancellation, revocation, unpairing, grant withdrawal, a terminal state, opt-out or a network change, the generation's listeners and every accepted socket are closed within 1 second, a response in flight is cut, and the keys and token are dropped (S-9).
- [ ] AC-33: The 15 minute authenticated-idle limit and the 2 hour absolute limit end a generation whatever the transfer grant's own lifetime is. After a wake nothing is served until a new generation arrives on the control channel (S-8, S-9).
- [ ] AC-34: AC-12 and AC-30 to AC-33 are verified on macOS, Windows and Linux separately, on signed builds, with the evidence in reports/. The setting cannot be turned on for an OS without its evidence.
- [ ] AC-35: The setting's help text states risks R-01 to R-03. The setting cannot be turned on until Anton's acceptance of each is recorded in reports/. Refusing a firewall prompt changes no firewall policy and blocks no authorized Connect copy.
- [ ] AC-36: AC-07, AC-08, AC-11, AC-13, AC-17 and AC-21 run on the production transport with real sockets, and AC-11, AC-13 and AC-16 also across a restart of each machine, the secret step included. A mock result does not count for any of them.

## Approach

Files, in order:
1. `packages/contracts/src/folderCopy.ts`: a `FolderCopyLanOffer` schema for the `lan` block in S-1, carried by the `lanCheck` and `lanOffer` control-channel calls. `FolderCopyOffer` itself does not change.
2. `apps/server/src/fleet/folderTransfer/lanListener.ts` (new): a TLS server bound to the private interface addresses (RFC 1918, RFC 4193 and link-local excluded by default). It has a self-signed ECDSA P-256 certificate generated in memory for each operation generation, requires the recipient certificate (S-2), serves only the three routes in S-5 through its own route table, never `handleSourceRequest` as a whole, and opens and closes with one generation (S-9).
3. `apps/server/src/fleet/folderTransfer/sourceService.ts`: after the offer is approved, runs the `lanCheck` and `lanOffer` exchange of S-1 when both settings are on.
4. `apps/server/src/fleet/folderTransfer/sourceClient.ts`: `checkSourceUrl` stays Connect-only. Every LAN request, retries included, goes through the one LAN connector of S-3, which compares the certificate's DER SHA-256 with the pin on `secureConnect` and destroys the socket before any HTTP byte. Never `connect.checkServerIdentity` with undici: it does not pin (security review, P0). No environment probe on LAN: the pinned handshake, then the authenticated `hello`, which checks `environmentId`, `operationId`, `generation` and `bindingSha256`. The LAN address is never a `baseUrl` or `fallbackBaseUrl`; `wrong_machine` is fatal only on Connect.
5. `apps/server/src/fleet/folderTransfer/destinationService.ts`: the S-8 deadlines for the LAN attempt, through the body as well as setup; the S-4 table decides between a switch and a stop. A switch, pin change mid-transfer included, latches the operation to Connect in its record before the first Connect request, so resume, retry and keepalive never re-probe. Records the bytes served per path for the label.
7. The listener does not reuse `folderTransferRoute.ts`'s adapter, because that reads a body before the token is checked. It authorizes from headers first (S-2), honours the update hold, applies the S-8 budgets and deadlines, and sends no `Server` or CORS headers. It binds only eligible RFC 1918 and RFC 4193 addresses (S-7), one socket each, and runs in the signed server process.
6. `apps/web`: the setting and the path line in the dialog's progress panel.

Security review topics (T-01):
- The transfer token must never reach an unpinned peer. The environment check and every request go over the pinned TLS connection, and the token is sent only after the pin matches.
- An attacker on the same network could answer at the offered address with another certificate, or replay an old offer. A fresh certificate per operation generation defeats the first. It does not order offers or prove who the recipient is, so the generation rule (S-1) and the recipient's proof of possession (S-2) cover the replay.
- Exposure: the listener must not become a general server, so it gets the minimal route table, rate limits on 401s, and no directory listing or health page. Bind to private addresses only, never 0.0.0.0, and keep it closed when idle.
- Leaks: offering LAN addresses tells the destination machine about the source's network. That is acceptable between machines the same account owns; the review should confirm the address never goes to Connect's relay logs.
- The macOS firewall prompt on first listen: decide whether to ship it, or document it in the setting's help text.
- Windows and Linux: per-OS firewall behaviour and interface enumeration.

Rejected:
- Plain HTTP on the LAN: the token and the files would travel in the clear.
- mDNS discovery: it advertises the machine to everyone on the network, and the authenticated offer already carries the address.
- Tailscale: it is off on purpose (owner's rule).

Risks: corporate networks with client isolation (the fallback covers them), VPNs that make a "private" address non-local, and machines with several interfaces (offer each one and try them in order with a short connect timeout, 1.5 s).

## Security amendments (November 19, 2026)

This section answers the security review of November 19, 2026: `.specweave/increments/1390-sync-projects-across-machines-and-hand-off-work/reports/reviews/security-review-lan-listener-1.md`. Its verdict was DESIGN CHANGES FIRST, with four findings. The text above was edited in place to agree with this section. If any line still disagrees, this section wins.

No listener code is written until a second review of this section says DESIGN OK.

Words used here:
- Source: the machine that holds the files. Destination: the machine that pulls them.
- Control channel: the machine-to-machine call the copy already uses (`studio_folder_copy_receive`, proxied over Connect and checked against the caller's machine grant). It is authenticated on both ends today: the destination serves it only to a paired machine whose work grant covers the project and is not revoked, under the team rules, and only for an operation whose recorded source is the calling machine. `lanCheck` and `lanOffer` need exactly that grant, the one `start` needs. They do not need the full-access grant that secrets need. Reaching a private address proves none of this.
- Operation: one copy, with its existing operation id.
- Generation: one LAN attempt for an operation. It has its own keys, token, listener and lifetime.
- LAN purposes: `sync-measured` (the measured copy behind "Compare all files…") and `add-whole-folder` (Add's whole-folder copy). No other copy gets a LAN path.

### Finding to design map

| Review finding | Design | Acceptance criteria |
|---|---|---|
| 1. Bind the offer; recipient proof of possession; reject old offers | S-1, S-2, S-9 | AC-04, AC-15, AC-16, AC-17, AC-18, AC-19, AC-32 |
| 2. Pin before HTTP; one connector; unreachable versus denied | S-3, S-4 | AC-02, AC-07, AC-08, AC-11, AC-20, AC-21, AC-22, AC-36 |
| 3. Two copy operations only; frozen scope; destination confinement | S-5, S-6 | AC-01, AC-13, AC-23, AC-24, AC-25, AC-26 |
| 4. Authorize before a body; budgets; interfaces; sockets; both opt in | S-2, S-7, S-8, S-9 | AC-03, AC-09, AC-10, AC-12, AC-27, AC-28, AC-29, AC-30, AC-31, AC-32, AC-33, AC-34 |
| Residual risks | Accepted risks | AC-14, AC-35 |

### S-1 The LAN offer: who creates it, what it binds, generations

Only the control channel creates or renews a LAN offer. Nothing received over the LAN can create, renew or extend an offer, a generation, a token, an address or a deadline.

The `lan` block is not part of `FolderCopyOffer`. The browser relays that offer, so the browser never sees a LAN address, pin or token. The block travels in the body of two control-channel calls, never in a URL, a header or a query string.

The exchange, after the normal offer, grant check and local approvals have passed:

1. The source checks its own setting, the purpose and its interfaces (S-7). It raises the operation's generation counter by one and saves it before sending anything.
2. Source to destination, `lanCheck`: `{ operationId, generation, purpose, candidates: [{ host }] }`. At most 4 candidates. No port, because nothing is bound yet.
3. The destination checks its own setting, that the operation exists in its own record with the same source and purpose, that it is not terminal and not latched to Connect, and that `generation` is higher than any it has seen. It saves the new highest generation. It creates the recipient key and certificate in memory. It answers `{ generation, recipientCertificateSha256, targetSha256, usable: [index] }`. `usable` lists the candidates that are directly attached for it (S-7). If any check fails it answers `{ lan: null }` and creates nothing.
4. The source creates its key and certificate in memory, binds one socket per usable address (S-7), mints the LAN token and sends `lanOffer` with the block below.
5. The destination accepts the block only if `generation` equals the highest it has seen, the recipient key for that generation is still in memory, and every bound field matches its own record. Then it connects (S-3).

The `lan` block, version 1:

| Field | Type | Meaning |
|---|---|---|
| `version` | `1` | Wire version. Any other value is ignored and the copy uses Connect. |
| `generation` | integer, 1 to 2^31 | The generation this block belongs to. |
| `purpose` | `sync-measured` or `add-whole-folder` | The approved copy operation. |
| `expiresAt` | epoch milliseconds | At most 2 hours after the listener was bound. |
| `addresses` | 1 to 4 of `{ host, port }` | IP literals admitted by AC-12, each with its OS-assigned port. |
| `sourceCertificateSha256` | 64 lowercase hex | SHA-256 of the source certificate's DER bytes. |
| `recipientCertificateSha256` | 64 lowercase hex | SHA-256 of the recipient certificate's DER bytes, echoed from step 3. |
| `scopeSha256` | 64 lowercase hex | Hash of the frozen source scope (below). |
| `targetSha256` | 64 lowercase hex | Hash of the frozen destination target, echoed from step 3. |
| `lanToken` | `swclan_` plus 32 random bytes, base64url | Bearer for this generation on the LAN only. |
| `bindingSha256` | 64 lowercase hex | Hash over all bound fields (below). |

Only certificate hashes cross the wire. This settles the "certificate and fingerprint" wording: the hash is the one wire format, and no certificate body is sent.

Hashes are SHA-256 over a domain tag, then the fields in the order given. Each field is written as its UTF-8 byte length (4 bytes, big-endian) followed by its bytes, so no path or name can run into the next field.

- `scopeSha256`: tag `swc-folder-lan-scope-v1`, then `sourceProjectId`, `copyRoot` (the canonical source root), `projectRelativePath`, `mode`, and the selection ceiling as a sorted, comma-joined list of file classes. The ceiling never contains `secret`.
- `targetSha256`: tag `swc-folder-lan-target-v1`, then the destination's canonical target path and the target kind (`empty` for Add, `reviewed` for Sync). The destination computes it. The source carries it without reading it.
- `bindingSha256`: tag `swc-folder-lan-binding-v1`, then `sourceEnvironmentId`, `destinationEnvironmentId`, `operationId`, `purpose`, `scopeSha256`, `targetSha256`, `generation`, `expiresAt`, `sourceCertificateSha256`, `recipientCertificateSha256`.

The destination recomputes all three from its own record and refuses a block that differs, without connecting. The control channel is the authentication. The hashes make the offer, the TLS session and the `hello` answer agree on one operation and one generation.

Generation rules:
- The counter only goes up. Both machines save it in the operation's record before they use it, so a restart cannot bring an old number back.
- The destination refuses `lanCheck` with a generation at or below its highest, and `lanOffer` for any generation but its highest. A delayed, once-valid offer is dead for good.
- A new generation ends the one before it on both machines: listener, accepted sockets, keys and token (S-9).
- One key pair per side per operation generation. Never per listener lifetime, never shared between copies. This replaces the older wording.
- A terminal operation never gets a new generation. An operation latched to Connect never gets one either.
- At most 6 generations per operation per hour.

The LAN token is separate from the copy's transfer token. The transfer token is never sent on the LAN. The LAN token works only on its generation's listener, and only inside a TLS session that proved the recipient key (S-2). The source keeps only its SHA-256, in memory. Revoking the transfer grant ends the generation too.

### S-2 Recipient proof of possession

The proof is mutual TLS with a one-time client certificate.

- The destination creates an ECDSA P-256 key and a self-signed certificate for the generation, in memory. Only the certificate's hash leaves the machine, in the `lanCheck` answer on the control channel.
- The source listener requires a client certificate. It compares the SHA-256 of the presented DER bytes with `recipientCertificateSha256` for its generation, in constant time. A mismatch destroys the socket. No HTTP response is written.
- TLS 1.3 only. The handshake's CertificateVerify proves the client holds the private key, and the signature covers this handshake's transcript. A recorded handshake cannot be replayed. A copied certificate without its key fails.
- Session tickets, resumption and 0-RTT are off on both ends. Every connection does a full handshake and both pin checks.
- ALPN is `swc-folder-lan/1` on both ends. A connection that does not negotiate it is closed.

What this gives:
- Bound to operation and generation: the key exists for one generation of one operation, and each listener serves one generation.
- Bound to the connection: the proof is the TLS handshake itself.
- Checked before any body: it finishes before the first HTTP byte is read.
- Key delivery: only on the control channel.

A LAN token without the recipient key cannot finish a handshake. A recipient key without the LAN token gets a 401. A token or certificate from another copy fails on both counts, because each copy has its own listener, port, keys and token.

Both certificates carry the fixed subject `CN=swc-folder-lan`, no machine name, no account, a random serial, and a life of the generation plus 5 minutes each side. The source certificate has `CA: false`, `serverAuth` and IP SANs for its offered addresses. The recipient certificate has `CA: false`, `clientAuth` and no SAN.

Order of checks on the source, for every accepted socket:

1. Accept. The remote address must be inside the listening interface's own on-link prefix, and the connection budgets (S-8) must allow it. Otherwise the socket is destroyed.
2. TLS 1.3 handshake with the recipient certificate check. Deadline 5 s.
3. Request line and headers. At most 8 KiB, within 2 s.
4. Authorization from headers only, in this order, each with one fixed answer, after which the socket is closed:
   - The method and route are not on the allow list (S-5), or the operation id in the path is not this listener's: 404 `not_found`.
   - The LAN token is missing or wrong: 401 `unauthorized`.
   - The operation carries a recorded denial (S-4): 403 with `revoked`, `refused` or `scope_changed`.
   - A generation that is no longer current never answers. Its sockets are already destroyed (S-9), so a stale generation cannot be mistaken for a denial.
5. Only now is a body reader opened. At most 128 KiB, within 10 s.
6. The response is served under the read budgets and stall deadline (S-8).

Only step 4 passing counts as authenticated use. Nothing before it moves the idle timer.

### S-3 The LAN connector and the pin check order

The destination has one LAN connector. Every LAN byte goes through it: the first request, retries, keepalive reconnects. No other code path may open a socket to a private address for a copy. `checkSourceUrl` stays as it is for Connect; the LAN connector does not use base URLs or the client's fallback list.

Order, for every new connection:

1. Take the address from the accepted `lan` block only. Apply AC-12 and the interface rules (S-7).
2. TCP connect from the eligible local address. 1.5 s per address, tried in the offered order.
3. TLS 1.3 handshake, presenting the recipient certificate, ALPN `swc-folder-lan/1`.
4. On handshake completion, hash the server certificate's DER bytes and compare with `sourceCertificateSha256` in constant time. On a mismatch destroy the socket. No HTTP byte has been written. Chain validation is not used and not needed: the exact pin is the trust.
5. Only then hand the socket to the HTTP client.
6. The first request on every connection is `GET hello` with the LAN token. The answer must name the same `environmentId`, `operationId`, `generation` and `bindingSha256`. Anything else is "wrong identity" (S-4).
7. Then `GET manifest` and `POST chunks`.

Connection setup, steps 2 to 6 across all addresses, has one deadline of 5 s.

Connector rules:
- No plaintext. No redirects: any 3xx is an error. No proxy: `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY` and system proxy settings are ignored.
- No `/.well-known/studio/environment` probe on the LAN. Identity is the pin, then `hello`.
- One connection pool per operation generation, at most 4 connections. It is never shared with another operation or with Connect. It is destroyed on latch, on a new generation and on a terminal state.
- Never `connect.checkServerIdentity` with undici, as before: it does not pin.
- An impostor that completes a TLS handshake sees the recipient's one-time certificate before the pin check closes the socket. That certificate names nothing and grants nothing without its key. The impostor receives no HTTP byte and no token.

### S-4 Fallback decision table

Two outcomes exist besides success.

- Switch once: the operation moves to Connect and stays there. The destination saves the latch in its record before it sends the first Connect request. It never tries the LAN again for that operation, across retries, keepalives and restarts.
- Stop: the copy ends with the reason. It does not continue on any path.

One rule sorts every case: an authenticated answer about authorization stops the copy. Everything else switches once.

A denial never depends on the LAN delivering it. Every denial is first saved on the source's operation record as a revoked transfer grant with its reason: `revoked` (grant revoked or withdrawn, machines unpaired), `refused` (an approval refused or withdrawn) or `scope_changed` (the frozen scope or the source root's identity changed). Only after that save does the source end the generation (S-9). Connect reads the same record. So a destination that sees only a reset switches to Connect, gets the denial on its first request there, and stops. The LAN's own 403 is a faster way to the same end, not the only one.

| What the destination sees on the LAN | Class | Action |
|---|---|---|
| No route, connection refused, connect timeout, 5 s setup deadline passed | Unreachable | Switch once |
| Reset, TLS alert, handshake failure, wrong ALPN | Unreachable | Switch once |
| No body progress for 15 s, or a request's total deadline passed | Unreachable | Switch once |
| Server certificate hash differs from the pin | Wrong pin | Switch once. No HTTP byte was sent |
| `hello` names another environment, operation, generation or binding | Wrong identity | Switch once |
| Generation superseded or expired, listener gone | Unreachable | Use the newer accepted generation if one exists and the operation is not latched. Otherwise switch once |
| Destination restarted and the recipient key is lost after a block was accepted | Unreachable | Switch once |
| Authenticated 403 `revoked` | Denied | Stop |
| Authenticated 403 `refused` (an approval was refused or withdrawn) | Denied | Stop |
| Authenticated 403 `scope_changed` | Denied | Stop |
| Any other authenticated 401 or 403 | Denied | Stop |
| Reset or closed socket because the source ended the generation on a denial | Unreachable | Switch once; Connect then answers the recorded denial and the copy stops |
| Authenticated 400, 404, 413, 429, 5xx, 503 `service_updating`, any 3xx | Not about authorization | Switch once |
| A response over a size limit (S-8), a bad frame, a chunk whose hash is wrong | Not about authorization | Switch once |
| Anything not listed | Default | Switch once |

| What the destination sees on Connect, after a switch or from the start | Action |
|---|---|
| Connect identity check fails (`wrong_machine`) | Stop, as today |
| Transfer grant revoked for any reason, including the recorded `refused` and `scope_changed`, or expired | Stop. The revoked-grant refusal exists today; the `refused` and `scope_changed` reasons are written by this design |
| Network error or 5xx | Retry on Connect by today's rules. Never back to the LAN |

Rules that go with the table:
- "Authenticated" means the answer arrived inside a session that passed both pin checks and `hello`. A 401 on any other connection is not a denial; it is unreachable.
- The Connect address and the transfer token come only from the destination's record of the original offer. Nothing in a LAN response is ever used as an address, a credential or a deadline.
- Connect authorizes on its own. A copy revoked while on the LAN is refused on Connect as well, so a switch can never revive it.
- On a switch, unverified data is thrown away: a manifest that was not fully received and validated, and any partial chunk batch. Chunks already staged stay only because each one matched its SHA-256. After a "wrong pin" or "wrong identity" switch the destination fetches the manifest again over Connect and keeps a staged chunk only if that manifest names its hash.
- Content checks, the review step, Undo and recipient sealing of secrets are the same on both paths.
- The dialog reports a mixed path after a switch.

### S-5 What the LAN listener serves

The LAN listener does not mount `handleSourceRequest` or the `folderTransferRoute.ts` adapter. It has its own route table with three entries, all for the listener's one operation:

| Method and route | Body | Answer |
|---|---|---|
| `GET /api/folder-transfer/v1/{operationId}/hello` | none | Environment id, operation id, generation, `bindingSha256`, batch limit |
| `GET /api/folder-transfer/v1/{operationId}/manifest` | none | The manifest the control path built for this operation, or 202 with progress |
| `POST /api/folder-transfer/v1/{operationId}/chunks` | Up to 1,024 SHA-256 hashes, optional `encodings` | Chunk frames, as today |

Everything else answers 404 before a body is read and changes nothing: `POST manifest`, `validate`, `stat`, `refresh`, `ancestry`, `secrets`, `secret`, `release`, `commit`, and any other method or path. Those stay on Connect, with link, apply, approvals and Undo.

Source-side scope:
- The source freezes the root, the project path, the mode and the selection ceiling when the offer is approved. `scopeSha256` carries them.
- The selection is chosen with `POST manifest` on Connect. A selection outside the ceiling is refused there and the copy stops as "changed scope".
- The LAN serves only indexed content: the one manifest of this operation, and chunks whose hashes that manifest names. A hash outside it gets the existing "unknown" frame with no bytes.
- No LAN request carries a path. No field of a LAN request is ever resolved as a source path.
- If the source root's identity or the frozen scope changes during the copy, the source first records the `scope_changed` denial on the operation, which Connect enforces too, and then ends the generation (S-4).

Secrets never travel the LAN in this release. The secret list and secret files stay on Connect with today's per-file approval and recipient sealing. A LAN failure cannot affect the secret step, because that step never uses the LAN.

### S-6 Destination path confinement

TLS proves who sent the manifest. It does not make the manifest's paths safe. These rules are transport-independent: they live in apply (`apply.ts`) and bind every final write, whether the bytes came over the LAN or over Connect. Switching transport never widens filesystem authority. Amended after the second security review (November 19, 2026), which found the earlier ownership check on the target and its parent too weak.

Manifest validation, before any chunk is requested. One bad entry refuses the whole manifest:

| Rule | Status |
|---|---|
| Relative path, `/` separated, at most 4,096 characters, no empty, `.` or `..` part, no leading `/` | Exists (`isSafeRelativePath`) |
| No control characters | Exists |
| On Windows: no `\` and no `:` (drive letters, UNC, alternate data streams) | Exists |
| On Windows: no reserved device name (`CON`, `PRN`, `AUX`, `NUL`, `COM1` to `COM9`, `LPT1` to `LPT9`, with or without an extension), no part ending in a dot or a space | New |
| No part longer than 255 bytes in UTF-8 | New |
| No two entries that land on one file under the destination volume's rules (case folding and Unicode normalization), and no entry that is both a file and a folder of another entry | Required before the first chunk request; uses the existing alias key in `paths.ts` |
| Declared sizes are whole numbers, and their sum is within the staging limit fixed at approval (S-8) | New |
| A link entry is written as a link, never followed, and its target text passes the same path rules or it is refused | Existing link checks kept |

Staging:
- Chunks are written under a private staging root (mode 0700) inside the operation's own folder, never under the target.
- Staging holds no links. Files are opened with no-follow, and each parent's real path must stay inside the staging root. This exists and stays.
- A file is complete only when its size and every chunk hash match the manifest.

Final writes:
- The destination freezes the target when the copy is approved: the canonical path, the kind (`empty` or `reviewed`) and, once the folder exists, its directory identity (device and inode, or the volume serial and file id on Windows). `targetSha256` carries the path and kind into the offer.
- Exclusive-control rule. Before any final mutation (create, write, rename, delete, mode change), apply reads with `lstat`, never following a link, every folder on the chain from the approved target root down to the folder that holds the written entry. Each one must be:
  - a real folder: not a symbolic link, not a junction, not any other reparse point;
  - owned by the app's user;
  - not writable by group or others (no `g+w`, no `o+w`);
  - free of any ACL entry that grants another principal write, append, delete or delete-child access. On Windows this reads the DACL: only the user, SYSTEM and Administrators may hold such rights. If the ACL cannot be read, the folder fails.
- The approved root must itself be anchored: each of its ancestors is owned by the app's user or by root (SYSTEM or Administrators on Windows) and is not writable by anyone else. One exception: a sticky folder (such as `/tmp`) may be writable by others only if the sticky folder itself is owned by root or the app's user, and the next part is an existing folder owned by the app's user. A sticky folder owned by anyone else never qualifies, because its owner can rename entries in it. Otherwise another user could swap the root, and the copy is refused before it starts.
- Why this is enough: with the rule holding on the whole chain, no principal other than the app's user and root can add, rename or replace an entry in any folder on it. So nobody else can redirect a pathname between the check and the write. The check establishes exclusive control; it does not merely look at identities.
- Refusal comes first. The chain is checked for every entry before the first final mutation. An entry whose chain fails is refused, nothing in or below the failing folder is changed, and the result names the folder and the reason (not owned by you, writable by group, writable by others, another user's ACL entry, a link or reparse point). Entries whose chains pass are applied.
- Check again after. After each write apply repeats the chain check and compares each folder's identity (device and inode, or volume serial and file id) with the one read before. Any change stops the copy and is reported with the folder and what the batch wrote, so Undo can remove it.
- The final entry itself is never opened through a link. A file is put in place by a rename onto its name; an existing link at that name is replaced as a name, not followed.
- Folders that apply creates are made with mode 0700, owned by the app's user, and get their final mode only when the copy commits.
- Threat model: other local users and their processes. Root, Administrators acting as such, and processes running as the app's own user are out of scope. They hold the app's write access already and need no race.
- A handle-relative native helper would make the same guarantee without refusing shared folders. It is not required for this design and can replace the refusal later, under its own review.
- Cost, stated plainly: a reviewed Sync into a tree with a group-writable or other-owned folder no longer writes into that folder, on either transport. The person sees which folder and why.
- Implementation gate (security review 3): on LAN, direct Connect and a forced LAN-to-Connect fallback, an unsafe descendant or an ancestor sticky folder owned by another user is named and refused before the affected mutation, outside files stay byte-for-byte unchanged, and a privately owned tree still copies as the positive control. The rule applies to every final mutation in a batch, covers a missing target on Add, effective ACLs including the right to change permissions, and links or reparse points on each supported OS.
- Renames go from staging to a path built only from the approved folder and validated parts.
- Add still requires a missing or empty target and never writes into `~/.ssh`, app state or the other refused folders. Sync still writes only what the person reviewed. Both rules are enforced in apply, on both paths.

### S-7 Interface binding and both-peer opt-in

Opt-in:
- Each machine has its own setting, off by default. The source opts in by sending `lanCheck`. The destination opts in by answering it. Both happen on the control channel.
- If either setting is off: no key is made, no socket is bound, no `lan` block exists. Off means no bind and no LAN offer.
- If there is no control route to the destination, there is no LAN path.

An address is eligible only if all of these hold, on the machine that owns it:
- It is an IP literal that AC-12 admits: RFC 1918 IPv4 or fc00::/7 IPv6. No hostname.
- Its interface is up, not loopback, and physical: Ethernet or Wi-Fi hardware. Tunnel, VPN, bridge, virtual, container, hotspot-sharing and peer-to-peer interfaces (`utun`, `tun`, `tap`, `wg`, `bridge`, `docker`, `veth`, `vmnet`, `awdl`, `llw`, WSL and Hyper-V adapters) are never eligible.
- The interface type comes from the OS, not from the name alone: the hardware port list on macOS, `IfType` and the hardware flag on Windows, a real device behind `/sys/class/net/{name}/device` on Linux.

Directly attached:
- The destination marks a candidate usable only if the candidate is inside the on-link prefix of one of its own eligible interfaces, and its routing table sends that address out of that same interface. A private address reached through a VPN or a default route is not local and is not usable.
- The destination connects from that interface's address.
- The source accepts a socket only if the remote address is inside the listening interface's on-link prefix.

Binding:
- One socket per usable address. Never a wildcard address.
- The port is assigned by the OS (bind to port 0), unprivileged, new for every generation.
- No discovery, no mDNS, no UPnP or NAT-PMP, no port mapping.
- The app never adds, changes or removes a firewall rule and never asks for elevation to do so.
- If the interface picture is ambiguous (the type cannot be read, the route check fails, two interfaces claim the prefix) or the bind fails, there is no LAN offer. A refused OS firewall prompt shows up as an unreachable address and the copy runs on Connect.

### S-8 Budgets and deadlines

Source listener:

| Budget | Limit |
|---|---|
| Live LAN generations on one source | 4 in total, 2 per destination machine |
| New generations | 6 per operation per hour |
| Addresses per offer | 4 |
| TLS handshakes in progress | 2 per remote address, 16 in total; when full the oldest unfinished one is dropped |
| Failed handshakes | 10 per remote address per minute, then that address is dropped at accept for 60 s |
| Authenticated sockets per operation | 4 |
| Concurrent chunk reads | 4 per operation, 8 in total |
| Handshake deadline | 5 s |
| Header size and deadline | 8 KiB, 2 s |
| Request body size and deadline | 128 KiB streamed cap, 10 s |
| Response stall | Closed when the peer takes less than 64 KiB in 30 s |
| Idle keepalive socket | Closed after 60 s |
| Authenticated idle, whole generation | 15 minutes |
| Absolute life, whole generation | 2 hours |

Failure counts are kept per remote address. A flood from one address cannot use up another address's allowance, and cannot touch the authenticated peer's sockets, which are counted separately. An unauthenticated request never moves the idle timer. Exhausting a LAN budget costs speed only: the copy continues on Connect.

Destination client:

| Budget | Limit |
|---|---|
| Connect per address | 1.5 s |
| Connection setup, all addresses, to an authenticated `hello` | 5 s |
| Response headers | 10 s (`GET manifest` may answer 202 and is polled) |
| Body progress | At least 256 KiB every 15 s, or the body ends |
| Whole request | 10 minutes for the manifest, 5 minutes for a chunk batch |
| Connections | 4 per operation |
| Chunk batch | 65 MiB on the wire and 65 MiB expanded (64 MiB of data plus framing) |
| Manifest | 256 MiB on the wire, 2 GiB expanded, 2,000,000 entries, 64 KiB per line |
| `hello` and 202 answers | 16 KiB |
| Staging disk | The total size fixed at approval (the scan total the person saw in the dialog, saved in the destination record) plus 5 percent, and at least 1 GiB must stay free on the volume. A manifest that declares more is refused. The manifest never sets its own limit |

Destination reads are streamed and counted. A body is cut off at its limit. The manifest is inflated and parsed line by line, never as one buffer. Memory stays bounded however small the wire bytes are. Crossing a limit is a switch to Connect (S-4), where the same limits apply.

The 15 minute and 2 hour limits belong to the generation. They do not depend on the transfer grant's 24 hour idle and 7 day limits, and a live grant never extends them.

For scale: the copy that started this work had 122,249 files in 7.5 GB. Every limit above admits it with room.

### S-9 Lifetime and closing

A generation ends, on both machines, when any of these happens:
- The operation reaches a terminal state, or is cancelled.
- The transfer grant is revoked or withdrawn, or an approval is withdrawn.
- The machines are unpaired, or the machine grant is withdrawn.
- A newer generation starts (rotation).
- Either machine turns the setting off.
- The destination latches the operation to Connect.
- 15 minutes pass without an authenticated request, or 2 hours pass since the bind.
- An address, interface or route changes, or the machine sleeps or wakes.
- The server process shuts down.

When the cause is a denial, the source saves the denial on the operation record first (S-4), then ends the generation.

Ending a generation means all of this, within 1 second:
- Stop listening on every socket of that generation.
- Destroy every accepted socket, including ones mid-response. Closing the listener alone is not enough.
- Destroy the destination's connection pool.
- Drop the keys and the LAN token from memory.
- Refuse the generation number for good.

After a sleep, a wake or a network change nothing rebinds by itself. A LAN path returns only through a new generation on the control channel, and only if the operation has not latched. This replaces the older "rebinds with a fresh offer" wording.

### S-10 Storage, logs and what others see

- Keys, the LAN token and the offered addresses live in memory only.
- The destination's 0600 record stores the highest generation, the path latch with its reason class, and the bytes received per path. The source's record stores the generation counter. Both are removed with the record.
- The `lan` block, the `lanCheck` body, LAN addresses, ports, certificate hashes and the LAN token appear in no log, error text, crash report or telemetry on either machine. Errors name the class from S-4, never the address.
- The browser never receives the block. The dialog gets the path label and byte counts only.
- Requirement: Connect relay records must never contain the block. It is carried only in a request body, never in a URL, header or query. Whether the relay records bodies has not been checked for this design. The implementation review must show, on a test relay, that no relay record holds any part of the block; until then this line is unproven and the setting stays off.
- The `lan` block alone grants nothing. Without the recipient key, which never leaves the destination's memory, the token cannot be used.

### S-11 Turning the setting on

The setting stays off by default and hidden behind the review gate until all of these are recorded:

1. A design review of this section with the verdict DESIGN OK.
2. An implementation review that confirms findings 1 to 4 are fixed in code, with the real-socket tests of AC-36.
3. The per-OS evidence of AC-34.
4. Anton's acceptance of each accepted risk below (AC-35).

A week of use is not evidence and is not a gate.

### Accepted risks

These are the residual risks the review named as eligible for acceptance. Anton accepted all three on November 19, 2026 (`reports/lan-risk-acceptance.md`). The setting is still off by default and stays off until the other S-11 gates are met. None of these replaces a fix for findings 1 to 4.

- R-01: An opted-in destination learns the source's offered private addresses. Status: accepted by Anton on November 19, 2026. Setting: off by default.
- R-02: Local observers on the network can see a temporary TLS endpoint and how much traffic it carries. Status: accepted by Anton on November 19, 2026. Setting: off by default.
- R-03: An OS firewall prompt or client isolation on the network can prevent the LAN path. The copy then runs on Connect at Connect speed. Refusing the prompt changes no firewall policy and blocks no authorized Connect copy. Status: accepted by Anton on November 19, 2026. Setting: off by default.

The setting's help text states all three in plain words.

### For the next review to confirm

These belong to findings 1 to 4. They are not accepted risks.

- Check-then-write in apply (S-6). The second review found the first answer too weak. S-6 now requires exclusive control of the whole chain before each write and refuses the write otherwise (D-09). The next review confirms or overrules this.
- Control route (S-1). Accepted by the second review: without a source-to-destination control route there is no LAN offer and no listener, and the copy uses Connect only if Connect authorizes it. Follow-up note: when the implementation is traced, document which dialog paths (measured Sync, dialog-run Add, agent-run Add) have authenticated machine-to-machine control. This is coverage information, not a reason to widen the LAN path.
- Relay records (S-10). Accepted by the second review as an implementation gate: test-relay records must show no part of the block or any credential before the setting is turned on.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: The setting is off by default and is turned on only through the S-11 gate; a week of use is not evidence (amended November 19, 2026) → default off (reversible).
- D-02: The certificate is pinned by fingerprint inside the offer, not issued by a local CA → pin (reversible).
- D-03: The connect timeout per LAN address is 1.5 s, inside one setup deadline of 5 s to an authenticated `hello`; after that the body must make progress every 15 s (amended November 19, 2026, S-8) → 1.5 s / 5 s / 15 s (reversible).
- D-04: One key and certificate per side per operation generation, never per listener lifetime (amended November 19, 2026, S-1) → per operation generation.
- D-05: Recipient proof of possession is mutual TLS 1.3 with a one-time client certificate, not a signed header (S-2) → mutual TLS (reversible before listener code).
- D-06: Secret files stay on Connect in this release (S-5, AC-13) → Connect only (reversible).
- D-07: The LAN serves three read routes; selection, refresh, stat, ancestry, commit and release stay on Connect (S-5) → three routes (reversible).
- D-08: The numeric budgets and deadlines are the S-8 tables → as listed (reversible).
- D-09: Final writes are confined by the exclusive-control rule in apply: every folder from the approved target down to the written entry is owned by the app's user, not writable by group or others, with no ACL write for another principal, and no link or reparse point; otherwise that write is refused before anything changes. The rule is the same over the LAN and over Connect. A native handle-relative helper is not required (amended November 19, 2026 after the second security review, S-6) → refuse without exclusive control (the next review confirms or overrules).
### Open
- none. One point waits for the next review (D-09); see "For the next review to confirm" in the security amendments.

## Tasks

### T-01 Security review of the design
- AC: AC-06 | Files: .specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/reports/security-review.md | Test: test -s .specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/reports/security-review.md

### T-02 LAN listener with a pinned certificate per operation generation
- AC: AC-03, AC-04, AC-09, AC-10, AC-12, AC-16, AC-17, AC-18, AC-23, AC-24, AC-27, AC-28, AC-30, AC-31, AC-32, AC-33 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/lanListener.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/lanListener.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/transferGrant.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer/lanListener

### T-03 Offer carries the LAN address; destination pins, tries it first, falls back to Connect
- AC: AC-01, AC-02, AC-05, AC-07, AC-08, AC-11, AC-13, AC-14, AC-15, AC-19, AC-20, AC-21, AC-22, AC-25, AC-26, AC-29, AC-36 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/folderCopy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/sourceClient.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/destinationService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/twoServer.lan.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/lanConnector.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/agentCopy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/apply.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/paths.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/manifest.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/pullWorker.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer/twoServer.lan

### T-04 Setting and the path line in the copy dialog
- AC: AC-01, AC-02, AC-35 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyProgressPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/CopyProgressPanel

### T-06 Firewall check on signed builds per OS
- AC: AC-06, AC-34 | Files: .specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/reports/firewall.md | Test: test -s .specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/reports/firewall.md

### T-05 Verify and close 1334
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17, AC-18, AC-19, AC-20, AC-21, AC-22, AC-23, AC-24, AC-25, AC-26, AC-27, AC-28, AC-29, AC-30, AC-31, AC-32, AC-33, AC-34, AC-35, AC-36 | Files: .specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/reports/ | Test: specweave verify 1334
