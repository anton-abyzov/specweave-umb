# Artifact storage and portable documents

## Problem
Artifacts span project files, reports, generated media and provider pages. Storage, retention, sharing and Office compatibility need one evidence-based plan.

## Scope
Research and bounded read-only local inventory. Consolidate 1342, shelf, previews, reports, design systems and machine grants. No implementation, deletion, publication, sync, grants, auth changes or migrations. Remote state remains unknown without authorized studio_file_transfer.

## Acceptance Criteria
- [ ] AC-01: Inventory names measured roots, byte counts, duplication scope and unknown remote state.
- [ ] AC-02: Current primary sources verify Claude changes and distinguish native Office fidelity from previews.
- [ ] AC-03: Plan defines identity, retention, versions, conflicts, availability, revocation and sharing without duplicating existing owners.
- [ ] AC-04: Gemini 4 Neon independently reviews evidence and plan at xhigh effort, with responses recorded.

## Approach
Read existing specs and source, inventory only selected artifact directories without symlinks or databases, research official documentation, record compatibility limits and phased plan, request independent review. No broad suites required for research.

## Decisions
### Asked
- User requested Fable 5.2 research and Neon xhigh review. Fable failed before output; configured fallback authorizes this Codex continuation.
### Defaulted
- Preserve originals; conversion is a derivative until fidelity is demonstrated.
- Research is separate from 1342 implementation ownership.
### Open
- Native Office app round-trip acceptance remains unverified until an authorized isolated fixture run.

## Tasks
### T-01 Consolidate evidence and inventory
- AC: AC-01, AC-02 | Files: reports/inventory.json, reports/research.md | Test: python3 -m json.tool reports/inventory.json
### T-02 Recommend phased plan
- AC: AC-03 | Files: reports/research.md | Test: inspect source links and explicit unknowns
### T-03 Independent review and reconciliation
- AC: AC-04 | Files: reports/neon-review.md, reports/research.md | Test: verify reviewer receipt and respond to each finding

Verify and close 1435 after review and owner acceptance.

## Scoped acceptance and limits
On November 20, 2026, the requester acknowledged receipt and authorized recording acceptance of the research deliverable using the existing independent Neon receipt. This is not self-certification or acceptance of a wider implementation. Neon round 2 returned ship for research at supported high effort (requested xhigh). Its three medium documentation findings were subsequently corrected by the author; those changes are documented in reports/research.md, not claimed as independently re-reviewed. Remote availability, native Office application round-trip fidelity and full live ownership reconciliation remain unverified. No implementation, publication, grants, sync or deletion is accepted by this research receipt. The parent must record delivery because a thread and its descendants cannot record that thread's own delivery.
