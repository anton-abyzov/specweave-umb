# 0880 text contrast correction

Source: site worktree, branch codex/0880-site, commit c7713ff4d. Root must run the same test against its integrated build; these local screenshots are not deployment proof.

Changed shared accent from #bd481f to #b1411c. On actual Jev comparison-card background #ecefe3, small 14px/600 text improves from4.384:1 to4.948:1, above required4.5:1. Accent on paper #f6f4ee is5.242:1. Theoretical accent on start background #e8eddf is4.835:1; current start section has no accent text, so this is a palette calculation rather than an observed DOM pair.

The DOM check also exposed four existing 12px board count labels at3.275:1. Changed only their color from #8a8d84 to the existing --soft token. No layout, type size, interaction, or page-content redesign.

Browser verification computes actual rendered foreground/background pairs for every visible text node within main on home and Jev at390/1440. Transparent background layers are composited through ancestors. It applies4.5:1 for normal text and3:1 only for WCAG large text; hidden details are excluded. Current pages have solid backgrounds behind text. This is not a claim about text-over-image or more complex opacity effects in future designs.

Observed pair groups: homepage23 per width; Jev18 per width. Zero failures after the correction. Existing ten responsive checks at320/375/390/768/1440 also pass. Production Docusaurus build passes. Headless:true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never throughout.

Receipts and refreshed screenshots: reports/artifacts/site/contrast.json and results.json; both include test source branch/revision/dirty status plus target URL. New jev-390-comparison.png and jev-1440-comparison.png show the affected cards. Root's final integrated run should replace local branch evidence before claiming deployment.

Latest unrelated documentation CI external Anthropic500 is recorded by root. No links, origins, or failing statuses were skipped or weakened for this contrast change.
