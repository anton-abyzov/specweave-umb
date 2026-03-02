# Plan — 0405-github-sync-smoke-test

## Approach
Minimal smoke test: create increment, verify GitHub issue creation, complete AC, close increment, verify issue closure.

## Steps
1. Create increment files (metadata.json, spec.md, tasks.md)
2. Trigger sync to create GitHub issue for US-001
3. Mark AC as complete
4. Close increment
5. Verify GitHub issue is closed
