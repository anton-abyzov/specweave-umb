DESIGN CHANGES FIRST
Verdict: fix first

# Security design review: 1390 T-17, LAN transport for Sync and Add

Reviewer context: fresh session, GPT-6.2 Astra. Reviewed design commit: `c368e2409cad8746105d73cbe9b7df4760195576`, in `/Users/antonabyzov/Projects/github/specweave-umb`. Application baseline: `8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8`, in `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`. The LAN listener is proposed, not deployed at this baseline. Findings describe failures the design permits, not observed compromises.

**Decision:** Amend the design for findings 1–4 before writing listener code. Keep the setting off until implementation evidence is reviewed and each finding is fixed or explicitly accepted with a reason. This does not block the Sync dialog or the Phase 2 release. Recording this review is not approval to enable the setting.

Design citations below refer to `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/spec.md`. The scope restriction is `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1390-sync-projects-across-machines-and-hand-off-work/spec.md:881–885`. Code citations are Git paths relative to the application baseline above.

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 1 | 🟠 HIGH | 1334 design | 27–28, 52–53, 74, 83 | A server pin does not bind the requester or establish offer freshness | 9/10 |
| 2 | 🟠 HIGH | 1334 design | 26, 31–32, 35–37, 43–47 | Generic retry can send a credential before peer verification or weaken fallback | 10/10 |
| 3 | 🟠 HIGH | 1334 design | 25–27, 37, 44–45 | Common transfer routes have more authority than the two approved copy operations | 9/10 |
| 4 | 🟡 MEDIUM | 1334 design | 27, 33–36, 48, 54–57, 64, 73 | Reusing the outer adapter permits pre-authentication body work; response and lifetime limits are incomplete | 10/10 |

## 1. Authenticate both ends and reject superseded offers (AC-03, AC-04, AC-09)

**Failure:** Pinning authenticates the source to the destination. It says nothing about who presents a live copy token to the source. A party that obtains that token can act as the recipient without possessing the paired machine's key. A delayed, once-valid offer can also replace a newer token before transfer begins. A new certificate blocks impersonation with the wrong key; it does not order authenticated offers.

**Evidence:** The current grant uses a random bearer, stores its hash and checks operation, expiry and revocation. The source checks the original offer scope on renewal. The destination permits a changed token before transfer. Connect pairing and machine work grants are separate checks; neither is implied by reaching a private IP. See `apps/server/src/fleet/folderTransfer/transferGrant.ts:37–55,80–112`, `apps/server/src/fleet/folderTransfer/sourceService.ts:425–455,648–665`, `apps/server/src/fleet/folderTransfer/destinationService.ts:402–426`, `apps/server/src/auth/PairingGrantStore.ts:629–701` and `apps/server/src/mcp/workGrantAccess.ts:103–139`.

**Required change:** Only the existing authenticated control channel may create or renew an offer, after the normal grant and local approvals. Bind it to source, destination, operation, authorized scope, purpose, expiry, generation and certificate pin. Require recipient proof of possession bound to that operation on LAN, in addition to the scoped bearer. Reject superseded generations durably; bind each listener, pooled connection and token to one operation and generation. Revoke active sockets on rotation, cancellation, unpairing or grant withdrawal. Resolve the conflicting per-listener/per-operation wording in favor of one key per operation generation. Acceptance: an old offer, a bearer without its recipient proof, or a token for another simultaneous copy cannot read data or reopen a terminal listener.

## 2. Authenticate before HTTP and separate reachability failure from denial (AC-02, AC-05, AC-07, AC-08, AC-11, AC-13)

**Failure:** The existing client trusts its primary base URL for sending requests; `hello` checks identity after receiving a response. Making a private IP an ordinary base URL could disclose the bearer to an impostor before that check. Conversely, treating every LAN denial as a transport failure could resume a revoked copy on Connect. A timeout only to first byte cannot bound a stalled transfer body.

**Evidence:** `apps/server/src/fleet/folderTransfer/sourceClient.ts:42–57,90–113,128–198,212–232`, `apps/server/src/fleet/folderTransfer/destinationService.ts:345–364,872–882` and `packages/contracts/src/folderCopy.ts:218–240`. AC-04 calls for both certificate and fingerprint; the proposed wire schema carries only a fingerprint. Existing redirect and origin restrictions should stay.

**Required change:** Define one wire format and one LAN-only TLS connector. Match the exact DER certificate hash from the authenticated offer before writing any HTTP bytes on every connection, including retries, secrets and keepalives. No redirects, plaintext, public environment probe or shared cross-operation connection. Then require authenticated `hello` to match both source and operation. An unreachable endpoint, wrong LAN pin or wrong LAN identity may switch once to the independently authenticated Connect peer from the original control channel. Never take fallback addresses or credentials from LAN responses. Persist the switch before resuming; discard partial unverified data and preserve content checks and recipient sealing. A revoked grant, refused approval, changed scope or failed Connect identity check stops the operation. Set bounded progress deadlines through the body as well as connection setup. Require AC-07/08 on the production transport and AC-11 across restart, including the secret step; do not infer these results from a mock.

## 3. Preserve source selection and destination confinement (AC-01, AC-03, AC-13; T-17 scope)

**Failure:** A paired peer is not authorized to read every file. The ordinary source limits chunks to its manifest, but the first manifest request selects file classes; the common router also has secret and state-changing routes. Mounting it wholesale would let a valid recipient request more than the user selected or exercise control operations over a data socket. On the other side, TLS authenticates the sender, not its filenames: a malicious manifest or a target directory replaced by a link after preflight must not redirect a write outside the approved target.

**Evidence:** `apps/server/src/fleet/folderTransfer/sourceRoutes.ts:39–105,128–151`, `apps/server/src/fleet/folderTransfer/sourceService.ts:685–712,1064–1086,1300–1325,1363–1381`, `apps/server/src/fleet/folderTransfer/agentCopy.ts:130–161,213–231`, `apps/server/src/fleet/folderTransfer/pullWorker.ts:87–100,263–275` and `apps/server/src/fleet/folderTransfer/apply.ts:246–269`. Existing scope, manifest-membership, chunk-integrity and link checks are safeguards to preserve, not evidence that a new transport may bypass them.

**Required change:** Limit LAN to measured Sync and whole-folder Add. Freeze the authorized source root, selection ceiling and destination in the offer. Allow only the minimum read methods; leave approvals, link, apply, commit and release on the existing control path. Serve indexed, selected content only; never resolve a requester-supplied source path. Keep secrets on Connect unless the same per-file approval and recipient sealing are enforced on both paths. At the destination, validate manifest paths under destination OS semantics, reject absolute/parent escapes, ambiguous aliases and link/reparse-point traversal. Stage under a private root, verify sizes and hashes, and anchor final writes/renames to the approved directory identity without following substituted links. Preserve empty-target Add and reviewed-target Sync through apply. Acceptance: an out-of-scope read returns no bytes; an invalid manifest or changed target leaves all outside files untouched.

## 4. Bound listener exposure and resource use (AC-03, AC-09, AC-10, AC-11, AC-12, AC-14)

**Failure:** The outer HTTP adapter consumes request bodies before the inner router checks the token. Its streamed 4 MiB limit bounds one body, not simultaneous readers or TLS handshakes. On the receiving side, the client buffers responses and the manifest decoder inflates before parsing. A paired but malicious sender can consume memory disproportionate to wire size. Closing a listening socket alone also leaves established connections alive.

**Evidence:** `apps/server/src/fleet/folderTransferRoute.ts:24–59`, `apps/server/src/fleet/folderTransfer/sourceRoutes.ts:39–67`, `apps/server/src/fleet/folderTransfer/sourceClient.ts:272–294,363`, `apps/server/src/fleet/folderTransfer/manifest.ts:1126–1131` and `apps/server/src/fleet/folderTransfer/wire.ts:14–23,70–73`.

**Required change:** Authorize headers before opening a body reader. Specify numeric per-peer and global budgets for offers, addresses, handshakes, sockets and concurrent reads, plus handshake, header and body deadlines. Retain the streamed request limit and bound wire bytes, expanded bytes, manifest entries and staging disk per operation. An unauthenticated request cannot refresh the idle timer or exhaust another peer's authentication allowance.

Require opt-in by both peers through the control channel. Bind separately to eligible directly attached RFC 1918/ULA physical-interface literals on OS-assigned unprivileged ports. Apply the AC-12 exclusions on both ends; a private address alone is not evidence that its route is local. No wildcard, tunnel, discovery, automatic firewall rule or broader retry. Ambiguous interface or firewall refusal means Connect. On opt-out, cancellation/revocation, terminal state or network change, close listeners **and accepted sockets**; enforce the 15-minute authenticated-idle and two-hour absolute limits independently of token lifetime. Wake requires a fresh authenticated offer. Off means no bind and no LAN offer. Verify these properties separately on each supported OS before enablement.

## Residual risks eligible for explicit acceptance

With the setting off by default and the controls above in place, the owner may accept that an opted-in destination learns offered private addresses, that local observers can see a temporary TLS endpoint and traffic volume, and that an OS firewall prompt or client isolation can prevent acceleration. Document these in the setting. Refusal must not change firewall policy or prevent an otherwise authorized Connect copy. Exclude the LAN block and credentials from logs, errors, crash reports and telemetry, including relay-side records; retain LAN metadata only as permitted by AC-14. These are residual tradeoffs, not acceptance of findings 1–4. A week of use is not evidence that the controls work.

Evidence boundary: static design review only. No listener, scan, live database access or runtime test. No implementation AC marked verified.
