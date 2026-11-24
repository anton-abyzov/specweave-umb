# 0880 website evidence and acquisition report

## Delivered

- Homepage preserves SpecWeave continuity positioning and adds a visible hero link plus an explanatory Jev use-case section.
- `/jev` explains a specific EasyChamp read-routing problem, shows three interactive recorded cases from the actual Python replay, and exposes all sanitized records as downloadable JSON.
- Primary result: five additional correct direct reads in 62 authored replay cases. Forty-one live Jev requests; 45/62 to 50/62 correct read-or-fallback decisions. Original broad intent benchmark remains a separate collapsed historical section; figures are explicitly incomparable.
- Selected handler demonstration uses real Gemini and Jev calls plus fixture EasyChamp data. One 1.99s failed listing versus 0.307s direct listing is shown with selection bias, excluded production services, and 4/5 rerun reliability disclosed.
- Premium Kie artwork has responsive 640/960/1600 variants. Art is conceptual; data and evidence remain accessible HTML text.
- Homepage board becomes one column on small phones, two columns on tablet, four on desktop. Body text, supporting labels, code, touch targets, focus outlines, and captions have readable floors. Hero typography fits 320px.
- Jev guide now links the practical evidence and removes universal cost/latency, schema, and calibrated-probability claims.

## Verification

Node 22.20.0, all browser checks explicitly headless, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never. No visible browser or personal browser used.

- Production Docusaurus build passes. Existing blog metadata and stale Browserslist notices remain; no new broken link/anchor warning.
- `npm run lint:docs-refs`: `docs-refs: OK — 154 pages, 11 skills, 81 CLI commands.`
- Headless Playwright: 10 page/viewport combinations, `/` and `/jev` at 320, 375, 390, 768, and 1440. Verifies HTTP success, no horizontal/clipped text overflow, real board interaction, recorded-example switching, keyboard FAQ expansion, image loading, raw evidence endpoint, and no browser runtime errors. Full-page plus viewport screenshots in `artifacts/site/`; results JSON captures run time and target URL.
- Full docs-site Vitest: 6 failed files / 10 failed tests; 33 passed files / 192 passed tests. Identical failures reproduced on unmodified base checkout. Existing unused Hero/HowItWorks text assertions, SVG component mock assumptions in Icon/TrustedBy/Integrations, and Remotion theme-token assertion. No tests weakened or removed. Logs preserved in site-unit.log and site-baseline-unit.log.

## Problems that matter

1. The classifier tax can erase the speed benefit: 12.9 seconds across 41 replay calls for five added routes, requiring over 2.58 seconds avoided per recovered route to break even on total model latency. No broad productivity claim is justified.
2. Three existing regex misroutes remain. Regex-first preserves them. Read-route selection never replaces deterministic authorization.
3. Confidence varies between identical replays: one selected Russian case fell from 0.95 to 0.94 and reverted to fallback. English response templates remain unchanged.
4. Browser delegation failed the real public EasyChamp navigation check twice by selecting done too early; verification rejected it. Website calls this experimental, not a proven speedup.
5. Heuristic secret masking is not a privacy guarantee. API state leaves the machine; explicit opt-in and configured-provider disclosures remain prominent.
6. Production traffic, paid conversion, real user time saved, and retained adoption have not been measured. Integration defaults off; root owns source deploy and release receipts.

## Acquisition and activation

The previous homepage had no Jev entry point. Users could see claims elsewhere but had no short path from use case to inspectable evidence to setup. New path: homepage hero → concrete example → evidence → setup guide.

No existing product-event analytics pattern was found in docs-site/src. Config delegates generic analytics injection to the edge; access to a reporting account was not established. No new tracking vendor or content-collecting beacon was added.

Measure a privacy-respecting funnel before buying traffic: unique /jev visitor → recorded-example interaction → evidence download → setup-guide click → successful doctor call → first accepted bounded decision → second use on a later day. Website click events can carry only event name, route and anonymous session identifier; CLI adoption should require separate telemetry consent and never collect prompts, keys or corpus text. Establish a baseline, then compare weekly cohorts; do not mix documentation visits with activated users.

Recommended first acquisition asset: one annotated actual-handler clip showing the known input, off/on behavior, and raw report link, explicitly labelled controlled demo with fixture data. Pair with the 62-case replay and one failure. Avoid a general speed multiplier or benchmark card alone. Broader rollout should wait for representative opt-in shadow data and a net latency/cost win.

## Release boundary

Site lane supplies committed source, local static build and headless proof. Root integrates and owns public deployment, npm release, installed-version receipt, and manual acceptance before increment closure.
