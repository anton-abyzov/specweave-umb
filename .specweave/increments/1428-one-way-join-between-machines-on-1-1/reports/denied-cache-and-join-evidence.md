# Denied cache and join evidence

November 20, 2026. Times below are Eastern Standard Time. The 1428 owner implements the cache correction. The 1431 worker owns the independent reproduction and acceptance record.

## Recent device approvals

M5 and m4 each approved a macOS desktop reporting the same label (redacted here as `SYN1…EXT`). Neither host’s inspected records link that label to a fleet environment, an account-join timestamp, the Air ending `68eb`, or an M2 hardware model.

| Host | First seen | App approved | Most recent desktop connection with that label |
| --- | --- | --- | --- |
| M5 | 1:08:58.321 AM | 1:09:35.209 AM | 1:36:50.620 AM |
| m4 | 1:09:48.683 AM | 1:10:00.387 AM | 1:36:50.802 AM |

M5’s running app was 1.0.401. The candidate reported SpecWithCode 1.0.400 to m4. The observations concern local approval records and matching desktop-session labels. They establish neither a hardware match nor what content the device viewed. Neither host had an identifiable worker grant for this label.

The most recent retained account-join notice on m4 names M5, ending `9725`, on November 16, 2026 at 12:46:18.361 AM. The documented Windows join to M5 occurred on November 19, 2026 around 9:54:46 AM. Neither notice identifies the new candidate.

## Directional evidence

| Direction | Agents and resources | App sessions |
| --- | --- | --- |
| m4 → M5 | Ready, full access to all projects. M5 confirms all sign-ins and routine management for m4. m4’s fleet listing advertised ten provider entries. | M5 recorded a desktop session labeled M4MAX. Its approved Mac uses a different label, so the two records could not be matched to one device. |
| M5 → m4 | m4 has an unrevoked full-access policy for M5 covering all projects and sign-ins. | m4 recorded two unexpired desktop sessions matching the M5 label. Latest recorded connection was 1:21:41.313 AM. |
| m4 ↔ Air ending 68eb | m4 → Air reports `needs_grant`. m4 has no incoming worker policy for that environment ID. | No matching named app record on m4. The reverse host’s session state is unknown. |
| Candidate ↔ m4 or M5 | Both hosts lack a verified candidate environment ID for matching worker policies. Candidate provider, model and project visibility is unknown. | Both hosts approved the candidate label and recorded desktop connections under it. Whether either host can open the candidate is unknown. |

Sources on m4 are `/Users/antonabyzov/.specwithcode/m4/studio-fleet-account-joins.json`, `/Users/antonabyzov/.specwithcode/m4/studio-fleet.json`, `/Users/antonabyzov/.specwithcode/m4/userdata/connect-devices.json`, `/Users/antonabyzov/.specwithcode/m4/userdata/work-grants.json`, the fleet listing and label-filtered aggregates returned by the supported database CLI.

Sources on M5 are `/Users/anton/.specwithcode/studio-fleet-account-joins.json`, `/Users/anton/.specwithcode/studio-fleet.json`, `/Users/anton/.specwithcode/userdata/connect-devices.json`, `/Users/anton/.specwithcode/userdata/work-grants.json` and the existing worker’s supported CLI aggregates. [M5 evidence](studio://thread/644195cc-3df8-418f-9708-3cd5ff059725/mcp%3A7f18ce60-092b-4789-aed3-b607c01cb0f7)

## Privacy correction

The previous client displayed cached project and chat data after an explicit authentication refusal. PR 787 invalidates the affected environment’s stored snapshots and warm thread resumes. A confirmed session can fetch fresh projections. Ordinary network loss preserves offline access to the previous authorized view. No test read an actual private chat or started remote work. [PR 787](https://github.com/anton-abyzov/specwithcode/pull/787)

The 1431 worker independently reproduced the defect at `8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8`, then verified its original regression and both scoped tests passed at `0201a11d399ff4eaec9858a770d4f105abb29796`. The package typecheck passed on that implementation. The final test-only change at `9997f601d885968fd8fcb51e0c2ec53dcd127427` uses two distinct RPC sessions with different project titles and chat bodies. The owner’s six suites passed 127 tests on that commit.

The 1431 baseline also records 142 passing existing worker-grant, revocation, registry and visibility tests. Those tests did not detect the cached-window exposure. Live reverse discovery, direct chat reads, fresh-install behavior and behavior after revocation on installed machines remain unverified.

Owner test output is `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-20-1428-denied-cache/final-focused.log`. Independent evidence is in `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1431-verify-joined-machine-resources-and-one-way-project-and-chat-privacy/reports/investigation.md`. The wider 1428 one-way join design and its review and release gates remain open.
