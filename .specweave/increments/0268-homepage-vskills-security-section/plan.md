# 0268: Plan — Homepage V-Skills Security Section

## Approach

Add a new React section component to the existing homepage. Follows the established pattern of other sections (ProblemSection, WhatsNewSection, etc.).

## Steps

1. Add new SVG icons to the `Icons` object in `index.tsx` (shield, scan, certificate)
2. Create `VSkillsSection` component with:
   - "Security Alert" badge (red)
   - "36.82%" stat with source
   - Three-tier trust ladder (Scanned/Verified/Certified cards)
   - CTA to docs and verifiedskill.com
3. Add a "Verified Skills" feature card to `FeaturesSection`
4. Update existing "Extensible Skills" card copy
5. Add CSS styles to `index.module.css` for the new section
6. Insert `<VSkillsSection />` in the page layout between Problem and WhatsNew
7. Test responsive layout and dark mode

## Risks

- **Low**: CSS conflicts — mitigated by CSS modules scoping
- **Low**: Page length — new section adds ~1 viewport, acceptable for the value

## Dependencies

- Increment 0267 (optional) — links will work either way, just different paths
