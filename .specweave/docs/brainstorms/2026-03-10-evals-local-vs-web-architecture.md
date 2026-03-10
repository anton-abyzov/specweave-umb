# Brainstorm: Evals Local vs Web Architecture
**Date**: 2026-03-10 | **Depth**: standard | **Lens**: default | **Status**: complete

## Problem Frame
**Statement**: The vskill web platform has an admin evals editor that duplicates local CLI eval authoring capabilities. evals.json is source code — authoring belongs locally, not on a web form.

| Dimension | Answer |
|-----------|--------|
| Who | Skill authors (own evals), platform (runs benchmarks, shows results) |
| What | evals.json editing on web is redundant — CLI already has full eval system with local UI |
| Where | vskill CLI (`vskill eval`, `vskill studio`) vs vskill-platform (`/admin/evals`) |
| Why | Web-editing source files via GitHub API is a leaky abstraction. Authors should own their evals |
| How | Delete web editor, rely on existing CLI tooling + platform's rescan pipeline |

## Key Discovery
The vskill CLI already has a **production-ready eval system**: `vskill eval init/run/serve/coverage`, a local Skill Studio web UI (`vskill studio`), multi-provider LLM support (Claude CLI, Anthropic API, Ollama), A/B comparison, MCP simulation, and history tracking. The web editor is fully redundant.

## Selected Approach: Author-Owned, Platform-Scanned

### Boundary
| Surface | Responsibility |
|---------|---------------|
| **vskill CLI** | Author evals.json, run/validate locally, push to repo |
| **vskill-platform** | Discover evals.json during repo scan, run server-side benchmarks, display public results |

### Delete from platform
- `/admin/evals` page (web editor)
- `/api/v1/admin/evals/content` (fetch evals.json from GitHub)
- `/api/v1/admin/evals/commit` (commit evals.json to GitHub)
- `/api/v1/admin/evals/skills` (editor skill list)

### Keep on platform
- Queue-based eval workers (read evals.json from repos during scan)
- `/api/v1/admin/eval/trigger` and `/api/v1/admin/eval/purge` (admin API)
- `/api/v1/admin/eval/bulk` (batch enqueue)
- Public eval results pages (`/skills/[owner]/[repo]/[skill]/evals`)

### Keep on CLI (already exists)
- `vskill eval init` — scaffold evals.json with LLM
- `vskill eval run` — execute locally with multi-provider support
- `vskill studio` / `vskill eval serve` — local web UI for authoring
- `vskill eval coverage` — coverage report
- `vskill eval generate-all` — batch scaffold

### Flow
```
Author: vskill studio → edit evals.json → vskill eval run → validate → git push
Platform: rescan repo → detect evals.json → queue eval run → store results → public page
```

## Rationale
- evals.json is source code — belongs in the developer's local workflow
- CLI already has richer tooling than the web editor (A/B comparison, MCP simulation, history, multi-model)
- Platform's value is aggregation + remote execution at scale, not editing JSON files
- No sync protocol needed — git push + platform rescan is the sync mechanism

## Next Steps
- Create increment to delete the admin evals editor from vskill-platform
- Revert the bulk delete feature (0473) since the page is being removed
- Ensure CLI eval tools are documented for skill authors
