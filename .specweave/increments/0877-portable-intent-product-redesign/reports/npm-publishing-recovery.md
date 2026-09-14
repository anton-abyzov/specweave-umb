# npm publishing recovery — 2026-09-14

The user explicitly authorized searching existing credentials, using Chrome to create a replacement if necessary, and storing any new key as plaintext through Obsidian Brain. Initial discovery found nine invalid candidates. The user completed npm account login before creation.

Created one granular token named `vskill-release-0877-2026-09-14`, owned by `aabyzov`. Scope: vskill package only; read/write publishing and staging; no organization access; CI 2FA bypass; expiry2026-12-13. Verified identity with the official npm registry and passed the value to `gh secret set NPM_TOKEN --repo anton-abyzov/vskill` through stdin. Values stayed out of command arguments, logs and source repositories.

Requested plaintext note (mode0600): `/Users/antonabyzov/Projects/Obsidian/personal-docs/003 Resources/Technical Knowledge/Credentials-Secrets-Passwords/Developer-Tools/npm/vskill npm publishing token 2026-09-14.md`. The existing master npm publishing note and new note are linked. Obsidian's `!cred` routing log contains filename/destination only. Credential content was not ingested into wiki pages. No vault git operations were performed.

vskill release workflow34814057433 attempt2 succeeded, publishing npm1.1.1 and its GitHub release. Registry integrity and publication timestamp are in published-packages.json. SpecWeave2.1.0 separately published through trusted OIDC in workflow34816047820; no new SpecWeave token was created.

The authorized Chrome token tab was closed after validation/storage. Automated product tests and screenshots remained headless throughout. No secret value is contained in this report.
