# Independent review — model identity and cost honesty

Verdict: ship. Root reviewer did not author2dc01995c. Reviewed model extraction, exact-price matching, mixed-session handling, nullable aggregate propagation, model tables/charts and Overview rendering. No confirmed blocking regression found.

Unknown or mixed-model sessions now remain unpriced. Opus5 is no longer renamed to Opus4.6, and unknown models no longer borrow Sonnet prices. The raw model IDs remain available. If any session is unpriced, total estimated value and savings are unknown; the known subset is separately labeled. All prices are explicitly labeled legacy2026-03 API estimates, not bills or subscription spend.

Reviewed230 focused tests, main build/client TypeScript pass, seven headless end-to-end assertions, and actual rendered cost/expanded-session screenshots. Root visually confirmed that unknown rows and mixed-model totals are not presented as zero. Scope remains local Claude Code usage logs; this does not add Codex billing or a controlled harness-quality benchmark.
