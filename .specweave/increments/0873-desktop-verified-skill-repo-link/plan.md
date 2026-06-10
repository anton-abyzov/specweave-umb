# Implementation Plan: Desktop verified-skill repository link

## Design

Update the desktop eval-ui `RepoLink` component so it can generate a
verified-skill.com skill detail URL when the caller supplies `skillName`.
`DetailHeader` will pass `skill.skill` to `RepoLink`, which makes the byline's
repo chip open the canonical registry page:

`https://verified-skill.com/skills/{owner}/{repo}/{skill}`

The component will keep `parseOwnerRepo` unchanged for GitHub URL validation and
canonicalization. A small helper will normalize the skill name by trimming
leading/trailing slashes, taking the final path segment when a hierarchical
`owner/repo/skill` value appears, and URL-encoding each verified-skill path
segment.

`SourceFileLink` remains untouched so the source-file chip still opens the
GitHub blob URL.

## Rationale

The existing UI already separates three intents in the byline:

- author profile
- repository identity
- source file

Only the repository identity chip needs to move from GitHub to the public
verified registry page. Keeping the direct file link on GitHub preserves the
debugging path while making the more prominent repository chip land on the
website Anton asked for.

No API or data model change is needed because `repoUrl` and `skill` are already
available in `SkillInfo`.

## Files

- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/RepoLink.tsx`
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx`
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/RepoLink.test.tsx`
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/DetailHeader.source-link.test.tsx`
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/DetailHeader.byline.test.tsx`

## Testing Strategy

Use existing fast Vitest component tests:

- `RepoLink.test.tsx` covers URL generation and validation.
- `DetailHeader.source-link.test.tsx` covers the byline contract and preserves
  source-file GitHub blob behavior.
- `DetailHeader.byline.test.tsx` covers the integrated desktop detail header.

Then run the focused eval-ui test set for these files.
