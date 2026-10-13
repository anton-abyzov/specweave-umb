---
id: 0907-m4-portable-continuation-proof
title: M4 portable continuation proof
project: specweave
---

# M4 portable continuation proof

## Problem

The previous destination smoke checks proved independent execution, but did not prove that a coordinator and worker on M1 or M3 can continue an actual M4 discovery with the same code and portable context.

## Scope

In: one bounded native coordinator and worker discovery on M4, followed by one continuation on M1 and one on M3, using this isolated experiment and explicit branch transport. The operator writes only this increment's specification, ledger, handoff and evidence documents. Native coordinator and worker turns inspect code and report evidence without editing files.

Out: product changes, dependency installation, builds, deployments, network product calls, secrets or environment-file reads, credential or billing changes, production data, existing user chats, and changes to another owner's checkout. A successful continuation is not a claim that the complete application runs locally.

## Acceptance Criteria

- [ ] AC-01: An actual M4 coordinator delegates a read-only source discovery to one native worker; the worker and automatically resumed coordinator report the pinned nested commit, a concrete code finding, a fresh marker and a continuation decision in a passed source receipt.
- [ ] AC-02: An actual M1 coordinator and native worker load the transported M4 checkpoint, independently inspect the same nested code commit, preserve its marker and decision, and finish through automatic coordinator continuation with a passed destination receipt.
- [ ] AC-03: An actual M3 coordinator and native worker load the transported M4 checkpoint, independently inspect the same nested code commit, preserve its marker and decision, and finish through automatic coordinator continuation with a passed destination receipt.

## Approach

- Own only this experiment on branch `codex/0907-handoff-specweave`. This fixture does not take over any other increment or active project session.
- Root source baseline: `99e16cf4eba879f1b163b894b37ec4cc3908b677` from `https://github.com/anton-abyzov/specweave-umb.git`. The root HEAD will advance only for experiment documentation; validate that every difference from the baseline stays in this increment. Distinguish the initial source proof HEAD from the later handoff transport commit.
- Nested source: `repositories/anton-abyzov/specweave` at exactly `a7bd43cabd0b241cea9a3c7cd8bc22fbe3ba9c9a` from `https://github.com/anton-abyzov/specweave.git`. It stays detached and unchanged. The nested checkout must exist on each execution host before worker launch.
- Native turns may read the increment, its explicit checkpoint, tracked source, README and package metadata within these two repositories. They may read Git identity and status. They must not read `.env*`, credential files, private session databases or unrelated paths, write files, run project hooks, switch providers, use credits, or broaden permissions.
- Save the M4 discovery receipt before creating a handoff document. The checkpoint must contain the real source finding, marker, decision, exact source paths and commits, remaining tasks and next step. Do not prefill results or fabricate completion.
- Transport only this named feature branch and its committed experiment documents. Never update a shared latest-handoff Git ref. Use the operator's explicit `handoff --no-push` and pickup sequence only after the source proof succeeds.
- Keep secrets, host credentials, native session state and uncommitted owner work outside Git transport. Machine-local paths may differ; repository identity and exact nested commit must match.
- Every receipt has `status`, `host`, `mode`, `key`, `baseline`, `marker`, `decision`, `outcome`, `quiescence` and `temporarySessionRevoked`. The second baseline row identifies the nested repository. Native worker output and automatic coordinator relay are separate evidence.

## Tasks

### T-01 Discover source and checkpoint continuation on M4
- AC: AC-01 | Files: .specweave/increments/0907-m4-portable-continuation-proof/reports/m4-source.json | Test: python3 -c 'import json;from pathlib import Path;d=json.loads(Path('"'"'.specweave/increments/0907-m4-portable-continuation-proof/reports/m4-source.json'"'"').read_text());assert d['"'"'status'"'"']=='"'"'passed'"'"' and d['"'"'host'"'"']=='"'"'m4'"'"' and d['"'"'mode'"'"']=='"'"'source'"'"' and d['"'"'key'"'"']=='"'"'specweave'"'"';assert d['"'"'baseline'"'"'][1]['"'"'sha'"'"']=='"'"'a7bd43cabd0b241cea9a3c7cd8bc22fbe3ba9c9a'"'"';assert d['"'"'marker'"'"'] and d['"'"'decision'"'"'];assert d['"'"'outcome'"'"']['"'"'workerThreadId'"'"'] and d['"'"'outcome'"'"']['"'"'automaticWakeRunId'"'"'] and d['"'"'outcome'"'"']['"'"'workerText'"'"'] and d['"'"'outcome'"'"']['"'"'relayText'"'"'];assert d['"'"'temporarySessionRevoked'"'"'] is True'

### T-02 Continue the M4 discovery on M1
- AC: AC-02 | Files: .specweave/increments/0907-m4-portable-continuation-proof/reports/m1-continuation.json | Test: python3 -c 'import json;from pathlib import Path;d=json.loads(Path('"'"'.specweave/increments/0907-m4-portable-continuation-proof/reports/m1-continuation.json'"'"').read_text());assert d['"'"'status'"'"']=='"'"'passed'"'"' and d['"'"'host'"'"']=='"'"'m1'"'"' and d['"'"'mode'"'"']=='"'"'destination'"'"' and d['"'"'key'"'"']=='"'"'specweave'"'"';assert d['"'"'baseline'"'"'][1]['"'"'sha'"'"']=='"'"'a7bd43cabd0b241cea9a3c7cd8bc22fbe3ba9c9a'"'"';assert d['"'"'marker'"'"'] and d['"'"'decision'"'"'];assert d['"'"'outcome'"'"']['"'"'workerThreadId'"'"'] and d['"'"'outcome'"'"']['"'"'automaticWakeRunId'"'"'] and d['"'"'outcome'"'"']['"'"'workerText'"'"'] and d['"'"'outcome'"'"']['"'"'relayText'"'"'];assert d['"'"'temporarySessionRevoked'"'"'] is True;s=json.loads(Path('"'"'.specweave/increments/0907-m4-portable-continuation-proof/reports/m4-source.json'"'"').read_text());assert d['"'"'marker'"'"']==s['"'"'marker'"'"'] and d['"'"'decision'"'"']==s['"'"'decision'"'"']'

### T-03 Continue the M4 discovery on M3
- AC: AC-03 | Files: .specweave/increments/0907-m4-portable-continuation-proof/reports/m3-continuation.json | Test: python3 -c 'import json;from pathlib import Path;d=json.loads(Path('"'"'.specweave/increments/0907-m4-portable-continuation-proof/reports/m3-continuation.json'"'"').read_text());assert d['"'"'status'"'"']=='"'"'passed'"'"' and d['"'"'host'"'"']=='"'"'m3'"'"' and d['"'"'mode'"'"']=='"'"'destination'"'"' and d['"'"'key'"'"']=='"'"'specweave'"'"';assert d['"'"'baseline'"'"'][1]['"'"'sha'"'"']=='"'"'a7bd43cabd0b241cea9a3c7cd8bc22fbe3ba9c9a'"'"';assert d['"'"'marker'"'"'] and d['"'"'decision'"'"'];assert d['"'"'outcome'"'"']['"'"'workerThreadId'"'"'] and d['"'"'outcome'"'"']['"'"'automaticWakeRunId'"'"'] and d['"'"'outcome'"'"']['"'"'workerText'"'"'] and d['"'"'outcome'"'"']['"'"'relayText'"'"'];assert d['"'"'temporarySessionRevoked'"'"'] is True;s=json.loads(Path('"'"'.specweave/increments/0907-m4-portable-continuation-proof/reports/m4-source.json'"'"').read_text());assert d['"'"'marker'"'"']==s['"'"'marker'"'"'] and d['"'"'decision'"'"']==s['"'"'decision'"'"']'
