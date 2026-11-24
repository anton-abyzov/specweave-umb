DESIGN CHANGES FIRST
Verdict: fix first

# Security design review: 1390 T-17, round 2

Reviewer context: fresh session, GPT-6.2 Astra. Reviewed umbrella commit: `02958bc51f9760b03573dbdccc5a90aa8d7ff505`. This is a design decision, not a finding of a deployed compromise. Hold T-17 listener code, not the Sync dialog or the Phase 2 release.

Design section and line citations refer to `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1334-direct-lan-path-for-copy-to-another-machine-with-connect-fallback/spec.md` at that commit.

## Disposition of round 1 findings

1. **Closed in design: peer identity and freshness.** Authenticated control binds the two peers, copy scope, target and generation. Mutual TLS requires possession of the recipient's generation key as well as the scoped token. Persisting the generation before use and retiring old sockets prevents an old offer from restoring access (lines 113–123, 145–177, 384–402).
2. **Closed in design: credentials and refusal on fallback.** The connector checks the exact source pin before sending HTTP and verifies `hello` on each connection. A transport failure can switch once to the independently authorized Connect offer. A denial is persisted before teardown and enforced on Connect even if its response was lost (lines 198–215, 223–259).
3. **Partly closed: source selection is closed; destination confinement is not.** Only three read routes are exposed. Selection is fixed on the control path, chunks are served by index and secrets stay on Connect. Manifest validation and private staging protect received data up to final apply (lines 262–303). The remaining issue is below.
4. **Closed in design: listener exposure and resource use.** Authorization precedes body reads. Both peers must opt in; interface eligibility, handshake and socket limits, decoded-data and disk budgets, independent deadlines and closure of accepted sockets are specified (lines 181–194, 316–376, 384–404).

## Rulings on the three requested points

1. **D-09: insufficient as written.** For reviewed Sync trees that may contain writable descendants, specify OS-enforced, handle-relative confinement or an equivalent guarantee before listener code. A narrower design can instead refuse affected writes unless it establishes exclusive control of the entire relevant path for the duration of apply. The helper need not already exist for the next design review; the enforceable rule must.
2. **No source-to-destination control route: Connect is acceptable.** Without that route, make no LAN offer and bind no listener. Use the existing Connect copy only if independently authorized and available; otherwise stop. Missing LAN capability is not authorization, and it is not a reason to retry a refused operation (S-1; lines 239–259, 441).
3. **Relay records: test-relay proof is an acceptable implementation gate.** AC-14 and S-10 specify the required result. A request-body schema cannot prove what a relay records. Require evidence from the test relay before enablement; no live relay inspection is needed for this design verdict (lines 408–422, 442).

## Blocking findings

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 3 | 🟠 HIGH | 1334 design, S-6 / D-09 | 305–312, 440, 457 | Final write is not bound to the reviewed directory | 9/10 |

**Failure:** An existing Sync target and its parent can satisfy the ownership rule while a traversable directory deeper in the reviewed tree permits changes by another local principal. Checking the identity of each directory does not establish exclusive control of its entries. A final mutation can therefore resolve outside the approved target between checks. A later stop or Undo cannot meet AC-26's requirement that outside files remain untouched. This does not depend on compromising the app's user or obtaining a paired key.

**Evidence:** `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode/apps/server/src/fleet/folderTransfer/apply.ts:203–228,250–269,474–501` separates directory checks from pathname-based mutations. The amendment adds checks around the batch but does not bind the mutation itself to the verified directory.

**Required change:** Amend S-6 and D-09 to confine final mutations to the approved tree, or refuse before mutation wherever confinement cannot be established. Apply the same rule after fallback: switching transport does not change filesystem authority. No change to source routes or to the two approved operations is needed.

## Implementation gates

- On the production transport, prove pin-before-HTTP, recipient key possession, generation isolation and active-socket revocation. Prove a lost refusal response and a restart cannot resume a refused copy on either transport.
- On the destination, prove invalid manifests leave the target untouched and out-of-scope requests yield no data. After S-6 is amended, cover an existing reviewed tree with a writable descendant; verify outside files remain unchanged, not merely that the copy reports failure.
- Supply the specified per-OS interface, resource-bound and teardown evidence, and test-relay records showing no LAN block or credential in recorded output. Keep enablement separate from this design review.

## Follow-up

Document which dialog paths have authenticated machine-to-machine control when the implementation is traced. This is coverage information, not a reason to broaden LAN. R-01 through R-03 remain for Anton; this review makes no acceptance decision.
