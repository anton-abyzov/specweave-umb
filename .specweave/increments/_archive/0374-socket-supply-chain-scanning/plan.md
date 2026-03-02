# Plan — 0374 Socket.dev Supply Chain Scanning

## Implementation Order

1. **T-001 + T-002** (parallel): DCI extractor + Socket client — no dependencies
2. **T-004 + T-005** (parallel): Type extensions — trivial, no dependencies
3. **T-003**: Enrich dependency analyzer — depends on T-002
4. **T-006**: Wire into pipeline — depends on T-001, T-002, T-003, T-004, T-005
5. **T-007 + T-008** (parallel): Tests — depends on T-006

## Key Design Decisions

- Raw fetch over Socket SDK (CF Workers compatibility)
- Layer on existing analyzer, don't replace
- 24h KV cache to minimize API calls
- Graceful degradation: no API key = local-only scoring
- DCI penalty: -5 per flagged package (moderate signal)
