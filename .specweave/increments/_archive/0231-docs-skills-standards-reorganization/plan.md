# Plan: Skills Documentation Reorganization

## Approach

Reorganize the `docs/skills/` directory into a two-pillar hub structure by creating subdirectories for each standard with hub index pages, moving related guides into the appropriate pillar, and updating the sidebar and redirects.

## Directory Structure (Target)

```
docs/skills/
├── index.md                              # Main Skills hub (already exists, update)
├── extensible/
│   ├── index.md                          # NEW: Extensible Skills pillar hub
│   ├── extensible-skills.md              # MOVED from skills/extensible-skills.md
│   ├── claude-skills-deep-dive.md        # MOVED from guides/claude-skills-deep-dive.md
│   ├── self-improving-skills.md          # MOVED from guides/self-improving-skills.md
│   └── skill-development-guidelines.md   # MOVED from skills/skill-development-guidelines.md
├── verified/
│   ├── index.md                          # NEW: Verified Skills pillar hub
│   ├── verified-skills.md               # MOVED from skills/verified-skills.md
│   ├── secure-skill-factory-standard.md  # MOVED from skills/secure-skill-factory-standard.md
│   └── skills-ecosystem-security.md      # MOVED from skills/skills-ecosystem-security.md
├── skill-discovery-evaluation.md         # STAYS (ecosystem-level, not pillar-specific)
├── skill-contradiction-resolution.md     # STAYS (ecosystem-level, not pillar-specific)
```

## Implementation Steps

1. Create `extensible/` and `verified/` subdirectories
2. Move files into the pillar subdirectories
3. Create hub index pages for each pillar
4. Update the main `skills/index.md` to reference pillar hubs
5. Update `sidebars.ts` with new doc IDs
6. Add redirects in `docusaurus.config.ts` for moved pages
7. Update cross-references in moved files (See Also sections)

## Risk Mitigation

- All moves preserve original content — no content deletion
- Redirects ensure old URLs still work
- Cross-references updated to prevent broken links
