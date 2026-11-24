# Bounded npm credential discovery

User-authorized discovery used the global Obsidian Brain skill’s configured three vault locations and credential folder. Searched `/Users/antonabyzov/Projects` (including EasyChamp and other projects), `~/.npmrc`, `~/.config`, Documents, Desktop, and Downloads. Search emitted filenames only and excluded dependency directories, Git objects, build output, binary files, test fixtures, and agent transcripts. Files over 2 MB were excluded. Desktop/Downloads/config traversal encountered inaccessible paths; this is not an exhaustive scan of every byte on disk.

29 files matched npm token/assignment patterns. Extracted and deduplicated nine plausible npm credentials in memory. Validated each only against the official npm registry’s `https://registry.npmjs.org/-/whoami` endpoint with the credential in the Authorization header. All nine returned HTTP 401; none established an account identity. See `npm-credential-discovery-results.json` for source paths and status only.

Additional old candidates were present in the Obsidian `Developer-Tools/npm/Npm registry backup keys access key token.md` note and `~/.npmrc`; existing master/root npm notes also matched. No token values, snippets, hashes, or credential-bearing logs were printed or saved. No credentials were written to Obsidian, no GitHub Actions secret was changed, and no publication was triggered. Root handles the separately authorized browser token creation fallback.

## Subsequent recovery

This report records the initial read-only search. After the user completed npm login, root created a scoped vskill token, stored it in the requested private Obsidian credential folder, updated the repository secret and published1.1.1 successfully. See npm-publishing-recovery.md and final-report.md; the initial401results remain unchanged.
