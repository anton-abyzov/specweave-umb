# Plan: 0282 - Repository Links on All Skill Surfaces

## Approach

Add repository links to 5 skill surfaces that currently lack them. The `repoUrl` field is already available in `SkillData` and returned by the API, so no backend changes are needed for most surfaces. Each surface needs a small, contextually appropriate repo link added.

## Changes by Surface

### 1. Skills Listing Page (`/skills/page.tsx`)
- Add a small repo link in the metrics row (bottom line of each skill row)
- Format: abbreviated `owner/repo` in teal, with click stopPropagation since the entire row is a link

### 2. Trust Center - Verified Skills Tab (`trust/VerifiedSkillsTab.tsx`)
- Add a "Repo" column to the table between "Skill" and "Author"
- Show abbreviated GitHub link

### 3. Trust Center - Blocked Skills Tab (`trust/BlockedSkillsTab.tsx`)
- The `sourceUrl` field exists but is shown as plain text in "Source Registry" column
- Make it a clickable link

### 4. Homepage Trending Section (`page.tsx`)
- Add a small repo link after the author name in each trending row

### 5. Search Palette (`components/SearchPalette.tsx`)
- Add `repoUrl` to search API response
- Show as small secondary text in results

## Testing

- Update existing tests for VerifiedSkillsTab and BlockedSkillsTab to verify repo links
- Verify search API includes repoUrl in response
