# WebMCP in the wild: October 2026 scan

Generated 2026-10-11 from `2026-10-scan.jsonl` (600 sites). Aggregates: `2026-10-aggregate.json`.

## Method

- `vskill audit-webmcp` (branch `claude/webmcp-audit`, commit 7a8ab0a), headless chrome-headless-shell 153 with `--enable-features=CDPScreenshotNewSurface,WebMCP`, no origin-trial token, concurrency 5, 30 s per site; the 43 sites that hit a timeout or network error were rerun once at 60 s, concurrency 3 (`2026-10-scan-rerun.jsonl`), and the better record kept.
- Homepage only, logged out, default locale. Tools registered later (after login, on product or cart pages, or after interaction) are not seen, so counts are a floor.
- The audit enumerates `document.modelContext` registrations and never calls a tool, clicks or submits.
- With the WebMCP flag on, Chromium exposes `document.modelContext` on every page, so its presence only confirms the scan environment worked. Adoption is measured as registering at least one tool on load.
- The seed list is purposive, not random: most cohorts were chosen because they were already expected to use WebMCP. Rates here describe these cohorts, not the web.
- Write shape, PII and injection checks are heuristics from `src/webmcp/score.ts`; every injection hit is listed below for manual review.

## Headline

Shopify's storefront module registers the same 12 tools on 92 of these sites, so it dominates every tool-level count. The second column removes those platform tools (sites that only have Shopify's tools then count as zero-tool sites).

| Metric | All tools | Excluding Shopify platform tools |
| --- | ---: | ---: |
| Sites in seed list | 600 | 600 |
| Scanned (page loaded) | 597 | 597 |
| Failed to load (ERROR) | 3 (0.5%) | 3 (0.5%) |
| `document.modelContext` exposed (browser flag; environment check, not adoption) | 597 | 597 |
| Registered at least one tool | 188 (31.5% of scanned) | 96 (16.1% of scanned) |
| Tools enumerated | 1657 | 553 |
| Tools per site with tools (mean / median / max) | 8.8 / 12 / 28 | 5.8 / 4 / 28 |
| Write-shaped tools | 416 | 48 |
| ... without `consequentialHint` | 406 (97.6%) | 38 (79.2%) |
| ... marked `readOnlyHint: true` | 4 | 4 |
| Sites with an unhinted write-shaped tool | 119 | 27 |
| Tools with `consequentialHint` | 8 | 8 |
| Tools with `readOnlyHint` | 599 | 231 |
| Tools with `untrustedContentHint` | 911 | 83 |
| Sites with third-party-registered tools | 4 (28 tools) | 3 (16 tools) |
| Tools with PII-shaped params / unexpected (WMCP-004) | 14 / 2 | 14 / 2 |
| Schema findings: missing / invalid JSON / not object / wrong type | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Oversized descriptions (tools / sites) | 563 / 99 | 11 / 7 |
| Sites over the per-page tool guidance | 0 | 0 |
| Tool sites with a Permissions-Policy header | 32 of 188 | 32 of 96 |
| Sites whose Permissions-Policy mentions tools/WebMCP | 7 | 7 |
| Prompt-injection pattern hits (WMCP-001) | 92 | 0 |
| Shopify platform tools (sites / tools) | 92 / 1104 | - |

## By cohort group

| Group | Seed | Scanned | Errors | modelContext | ≥1 tool | Tools | Write-shaped | No consequentialHint | 3rd-party sites | Injection hits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a: Known Good listed | 336 | 336 | 0 | 336 | 37 (11%) | 157 | 21 | 14 (66.7%) | 0 | 1 |
| b: Shopify storefronts | 100 | 100 | 0 | 100 | 91 (91%) | 1092 | 364 | 364 (100%) | 1 | 91 |
| c: Cloudflare/Vercel/OSS adopters | 54 | 52 | 2 | 52 | 24 (46.2%) | 134 | 10 | 10 (100%) | 1 | 0 |
| d: origin trial and showcases | 58 | 58 | 0 | 58 | 36 (62.1%) | 274 | 21 | 18 (85.7%) | 2 | 0 |
| e: control | 52 | 51 | 1 | 51 | 0 (0%) | 0 | 0 | 0 | 0 | 0 |

### By cohort

| Cohort | Seed | Scanned | Errors | ≥1 tool | Tools | Median tools | Write-shaped / unhinted | 3rd-party sites |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a_knowngood | 336 | 336 | 0 | 37 | 157 | 3 | 21 / 14 | 0 |
| b_shopify_cartjs | 75 | 75 | 0 | 68 | 816 | 12 | 272 / 272 | 1 |
| b_shopify_liquid | 25 | 25 | 0 | 23 | 276 | 12 | 92 / 92 | 0 |
| c_cloudflare_bridge | 2 | 2 | 0 | 0 | 0 | - | 0 / 0 | 0 |
| c_cloudflare_property | 3 | 3 | 0 | 2 | 3 | 1.5 | 0 / 0 | 0 |
| c_oss_webmcp_dependent | 48 | 46 | 2 | 22 | 131 | 4 | 10 / 10 | 1 |
| c_vercel_mcp_handler | 1 | 1 | 0 | 0 | 0 | - | 0 / 0 | 0 |
| d_chromelabs_demo | 1 | 1 | 0 | 1 | 1 | 1 | 0 / 0 | 0 |
| d_mcpb_showcase | 3 | 3 | 0 | 2 | 5 | 2.5 | 1 / 1 | 0 |
| d_origin_trial_named | 9 | 9 | 0 | 1 | 1 | 1 | 0 / 0 | 1 |
| d_showcase | 45 | 45 | 0 | 32 | 267 | 6 | 20 / 17 | 1 |
| e_control | 52 | 51 | 1 | 0 | 0 | - | 0 / 0 | 0 |

## Tool count distribution (scanned sites)

| Tools on homepage | Sites |
| --- | ---: |
| 0 | 409 |
| 1 | 13 |
| 2-5 | 56 |
| 6-10 | 13 |
| 11-20 | 102 |
| 21+ | 4 |

## Most common tool names

Count = sites registering a tool with that name.

| Tool | Sites |
| --- | ---: |
| `get_product` | 97 |
| `add_to_cart` | 95 |
| `get_cart` | 93 |
| `browse_store` | 92 |
| `cancel_cart` | 92 |
| `get_ucp_profile` | 92 |
| `manage_orders` | 92 |
| `proceed_to_checkout` | 92 |
| `search_catalog` | 92 |
| `search_shop_policies_and_faqs` | 92 |
| `show_variant` | 92 |
| `update_cart_lines` | 92 |
| `search_products` | 6 |
| `list_packages` | 4 |
| `list_services` | 4 |
| `search_destinations` | 4 |
| `search_site` | 4 |
| `view_destination` | 4 |
| `navigate` | 3 |
| `book_appointment` | 2 |
| `compare_packages` | 2 |
| `get_contact_info` | 2 |
| `get_game_state` | 2 |
| `get_page` | 2 |
| `get_page_context` | 2 |
| `get_pricing` | 2 |
| `navigate_to_page` | 2 |
| `place_order` | 2 |
| `redo` | 2 |
| `redo_edit` | 2 |

## Who registers the tools

Host of the script that called `registerTool`, from the captured stack.

| Script host | Tools |
| --- | ---: |
| 3dstreet.app | 28 |
| webroom.openai.chatgpt.site | 28 |
| fieldwork-beat-machine.openai.chatgpt.site | 26 |
| video-editor.ai-creator.top | 21 |
| alibaba.github.io | 20 |
| www.persona-chat.dev | 17 |
| snugug.github.io | 16 |
| agentive.au | 14 |
| scvd.store | 14 |
| (unknown) | 13 |
| apparel.monster | 13 |
| paperie-webmcp-greeting-cards.openai.chatgpt.site | 13 |
| athleticbrewing.com | 12 |
| brightland.co | 12 |
| casper.com | 12 |
| cdn.shopify.com | 12 |
| colourpop.com | 12 |
| coniuncta.com | 12 |
| fahertybrand.com | 12 |
| feature.com | 12 |
| fellowproducts.com | 12 |
| fentybeauty.com | 12 |
| floydhome.com | 12 |
| girlfriend.com | 12 |
| goli.com | 12 |
| greatjonesgoods.com | 12 |
| hexclad.com | 12 |
| hyperice.com | 12 |
| iliabeauty.com | 12 |
| jeffreestarcosmetics.com | 12 |

## Write-shaped tools and confirmation hints

416 tools look like they change state (checkout, cart edits, send, book, delete...). 406 of them (97.6%) carry no `consequentialHint`, so a browsing agent has no page-supplied signal to ask the user first. By tier: medium 28, high 107, low 281.

Shopify note: 1104 tools on 92 sites are registered by Shopify's own storefront script. They are a platform default; merchants cannot change their names, descriptions or annotations, so any hint gap there is one fix at the platform level, not 92 merchant problems.

### Write-shaped tools marked readOnlyHint: true (WMCP-003)

| Site | Cohort | Tool | Finding |
| --- | --- | --- | --- |
| webmcp-flow.vercel.app | d_showcase | `remove_node` | looks like a write action (remove) but is marked readOnlyHint: true |
| scvd.store | d_showcase | `quote_store_purchase` | looks like a write action (purchase) but is marked readOnlyHint: true |
| gaffer.sh | a_knowngood | `gaffer.signup_url` | looks like a write action (signup) but is marked readOnlyHint: true |
| bui-hinsche.com | a_knowngood | `book_appointment` | looks like a write action (book) but is marked readOnlyHint: true |

## Third-party-registered tools (WMCP-005)

"Third-party" means the script file that called `registerTool` came from a different registrable domain than the page. That includes a brand's own asset CDN on a separate domain and WebMCP helper libraries loaded from public CDNs, not only outside vendors. Review each before drawing conclusions.

| Script host | Tools |
| --- | ---: |
| cdn.shopify.com | 12 |
| cdn.jsdelivr.net | 9 |
| unpkg.com | 6 |
| assets.targetimg1.com | 1 |

| Site | Cohort | Tool | Registered by |
| --- | --- | --- | --- |
| target.com | d_origin_trial_named | `search_products` | https://assets.targetimg1.com/webui/top-of-funnel/_next/static/chunks/pages/_app-6c37e8ef95fed1e9.js |
| emingure.github.io | d_showcase | `add_to_cart` | https://unpkg.com/simple-webmcp@0.3.0/dist/index.js |
| emingure.github.io | d_showcase | `checkout` | https://unpkg.com/simple-webmcp@0.3.0/dist/index.js |
| emingure.github.io | d_showcase | `get_cart` | https://unpkg.com/simple-webmcp@0.3.0/dist/index.js |
| emingure.github.io | d_showcase | `get_product` | https://unpkg.com/simple-webmcp@0.3.0/dist/index.js |
| emingure.github.io | d_showcase | `search_products` | https://unpkg.com/simple-webmcp@0.3.0/dist/index.js |
| emingure.github.io | d_showcase | `update_cart` | https://unpkg.com/simple-webmcp@0.3.0/dist/index.js |
| cotopaxi.com | b_shopify_cartjs | `add_to_cart` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `browse_store` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `cancel_cart` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `get_cart` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `get_product` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `get_ucp_profile` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `manage_orders` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `proceed_to_checkout` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `search_catalog` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `search_shop_policies_and_faqs` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `show_variant` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| cotopaxi.com | b_shopify_cartjs | `update_cart_lines` | https://cdn.shopify.com/shopifycloud/storefront/assets/storefront/webmcp-f427de6a.js |
| agentready.gh.miniasp.com | c_oss_webmcp_dependent | `activate_target` | https://cdn.jsdelivr.net/npm/@willh/agentready@latest/dist/agentready.min.js |
| agentready.gh.miniasp.com | c_oss_webmcp_dependent | `fill_form` | https://cdn.jsdelivr.net/npm/@willh/agentready@latest/dist/agentready.min.js |
| agentready.gh.miniasp.com | c_oss_webmcp_dependent | `find_on_page` | https://cdn.jsdelivr.net/npm/@willh/agentready@latest/dist/agentready.min.js |
| agentready.gh.miniasp.com | c_oss_webmcp_dependent | `get_install_snippet` | https://cdn.jsdelivr.net/npm/@willh/agentready@latest/dist/agentready.min.js |
| agentready.gh.miniasp.com | c_oss_webmcp_dependent | `get_page_context` | https://cdn.jsdelivr.net/npm/@willh/agentready@latest/dist/agentready.min.js |
| agentready.gh.miniasp.com | c_oss_webmcp_dependent | `go_to_section` | https://cdn.jsdelivr.net/npm/@willh/agentready@latest/dist/agentready.min.js |
| agentready.gh.miniasp.com | c_oss_webmcp_dependent | `read_target` | https://cdn.jsdelivr.net/npm/@willh/agentready@latest/dist/agentready.min.js |
| agentready.gh.miniasp.com | c_oss_webmcp_dependent | `set_field` | https://cdn.jsdelivr.net/npm/@willh/agentready@latest/dist/agentready.min.js |
| agentready.gh.miniasp.com | c_oss_webmcp_dependent | `submit_form` | https://cdn.jsdelivr.net/npm/@willh/agentready@latest/dist/agentready.min.js |

## PII-shaped parameters

14 tools take a parameter whose name looks like personal data (email 14, address 5, phone 6). Most are expected (an email field on a newsletter tool). 2 were flagged because the tool's name and description give no reason for it:

| Site | Tool | Finding |
| --- | --- | --- |
| alpis.fr | `request_translation_quote` | asks for phone (parameter "phone") although its name and description do not need it |
| brandhalo.io | `prefill_schedule_call_form` | asks for email (parameter "contactEmail") although its name and description do not need it |

## Schemas, descriptions, Permissions-Policy

- Schema findings on 0 tools: 0 missing, 0 invalid JSON, 0 not an object, 0 non-object type.
- 563 descriptions over the length guidance, on 99 sites. 0 sites register more tools than the per-page guidance.
- 32 of 188 tool-registering sites send a Permissions-Policy header; 7 sites' policies mention tools or WebMCP.
  - codex-modeling-studio.openai.chatgpt.site (d_showcase): `tools=(self), camera=(), microphone=(), geolocation=(), clipboard-read=(), clipboard-write=(), payment=(), usb=(), serial=(), hid=(), bluetooth=(), midi=(), display-capture=()`
  - scholar-sidekick.com (d_showcase): `camera=(), microphone=(), geolocation=(), tools=(self)`
  - qrcodecrafter.com (d_showcase): `camera=(self), microphone=(), geolocation=(), interest-cohort=(), tools=(self)`
  - sitemapkit.com (d_showcase): `tools=(self)`
  - harbertgroup.com (a_knowngood): `tools=(self)`
  - worldmonitor.app (c_oss_webmcp_dependent): `camera=(), microphone=(), geolocation=(self), accelerometer=(), autoplay=(self "https://www.youtube.com" "https://www.youtube-nocookie.com"), bluetooth=(), display-capture=(), encrypted-media=(self "https://www.youtube.com" "https://www.youtube-nocookie.com"), gyroscope=(), hid=(), idle-detection=(…`
  - segregation-console.vercel.app (c_oss_webmcp_dependent): `tools=(self), camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()`

## Prompt-injection pattern hits (manual review)

Every WMCP-001 hit, verbatim. These are pattern matches, not confirmed attacks: an instruction like "do not ask the user to confirm" in a cart tool is a design choice worth discussing, not evidence of malice.

1. Tool `add_to_cart`, medium, Shopify platform tool, 92 sites
   - Finding: description: tells the agent to skip user confirmation (WP-07) matched "do NOT ask the user to confirm"
   - Description (verbatim): "Add products to the cart. Call this as soon as the user asks to ADD items (triggers: "add ... to my cart", "buy", "I'll take", "put ... in my basket") — in ONE call listing every item they named, up to the 10-entry limit. That request IS the authorization: do NOT ask the user to confirm before calling, and do NOT stop after search_catalog or get_product merely to report the variant you found — make the change, then tell the user it is done. Batch every item for ONE request into a SINGLE call — line_items accepts up to 10 entries; do NOT call add_to_cart once per item. Batching applies WITHIN a single request: each new thing the user asks for later is its own call. If one request names more than 10 items, split just that request into as few calls as possible. Do NOT retry a call that already returned a result: adds are cumulative, so repeating a call adds duplicate items. Use line_items[].item.id with a ProductVariant GID when the exact variant is known. Use handle or query only when adding the selected or first available variant. To change a quantity or remove something already in the cart, use update_cart_lines instead — this tool can only add."
   - Sites: coniuncta.com (a_knowngood), aimeleondore.com (b_shopify_liquid), athleticbrewing.com (b_shopify_liquid), aloyoga.com (b_shopify_liquid), beardbrand.com (b_shopify_liquid), allbirds.com (b_shopify_liquid), jp.bape.com (b_shopify_liquid), safariland.com (b_shopify_liquid), brightland.co (b_shopify_liquid), brooklinen.com (b_shopify_liquid), casper.com (b_shopify_liquid), colourpop.com (b_shopify_liquid), deathwishcoffee.com (b_shopify_liquid), fahertybrand.com (b_shopify_liquid), us.dollarshaveclub.com (b_shopify_liquid), fellowproducts.com (b_shopify_liquid), feature.com (b_shopify_liquid), everlane.com (b_shopify_liquid), fentybeauty.com (b_shopify_liquid), floydhome.com (b_shopify_liquid), goli.com (b_shopify_liquid), glossier.com (b_shopify_liquid), lairdsuperfood.com (b_shopify_liquid), hexclad.com (b_shopify_liquid), graza.co (b_shopify_cartjs), greats.com (b_shopify_cartjs), greatjones.com (b_shopify_cartjs), hismileteeth.com (b_shopify_cartjs), jeffreestarcosmetics.com (b_shopify_cartjs), hyperice.com (b_shopify_cartjs), iliabeauty.com (b_shopify_cartjs), kith.com (b_shopify_cartjs), lalo.com (b_shopify_cartjs), jlab.com (b_shopify_cartjs), jbhifi.com.au (b_shopify_cartjs), kosas.com (b_shopify_cartjs), liquiddeath.com (b_shopify_cartjs), kyliecosmetics.com (b_shopify_cartjs), koio.co (b_shopify_cartjs), lskd.co (b_shopify_cartjs), monos.com (b_shopify_cartjs), magicspoon.com (b_shopify_cartjs), morphe.com (b_shopify_cartjs), mvmt.com (b_shopify_cartjs), marinelayer.com (b_shopify_cartjs), negativeunderwear.com (b_shopify_cartjs), mudwtr.com (b_shopify_cartjs), nanit.com (b_shopify_cartjs), nativecos.com (b_shopify_cartjs), oliverpeoples.com (b_shopify_cartjs), nomatic.com (b_shopify_cartjs), naadam.co (b_shopify_cartjs), outdoorvoices.com (b_shopify_cartjs), packershoes.com (b_shopify_cartjs), noahny.com (b_shopify_cartjs), ooni.com (b_shopify_cartjs), parachutehome.com (b_shopify_cartjs), partakefoods.com (b_shopify_cartjs), pacas.com (b_shopify_cartjs), rarebeauty.com (b_shopify_cartjs), pela.earth (b_shopify_cartjs), redbullshopus.com (b_shopify_cartjs), puravidabracelets.com (b_shopify_cartjs), representclo.com (b_shopify_cartjs), ritual.com (b_shopify_cartjs), rothys.com (b_shopify_cartjs), skinnydipped.com (b_shopify_cartjs), sneakerpolitics.com (b_shopify_cartjs), skullcandy.com (b_shopify_cartjs), setactive.co (b_shopify_cartjs), stance.com (b_shopify_cartjs), stanley1913.com (b_shopify_cartjs), supergoop.com (b_shopify_cartjs), stussy.com (b_shopify_cartjs), thursdayboots.com (b_shopify_cartjs), therabody.com (b_shopify_cartjs), taylorstitch.com (b_shopify_cartjs), ugmonk.com (b_shopify_cartjs), tenthousand.cc (b_shopify_cartjs), tentree.com (b_shopify_cartjs), tower28beauty.com (b_shopify_cartjs), undefeated.com (b_shopify_cartjs), tuftandneedle.com (b_shopify_cartjs), trueclassictees.com (b_shopify_cartjs), thesill.com (b_shopify_cartjs), vitalproteins.com (b_shopify_cartjs), hauslabs.com (b_shopify_cartjs), girlfriend.com (b_shopify_cartjs), nobullproject.com (b_shopify_cartjs), cotopaxi.com (b_shopify_cartjs), knix.com (b_shopify_cartjs), lunya.co (b_shopify_cartjs)

## Notable sites

Largest tool surfaces, leaving out the 92 sites whose only tools are the Shopify platform set (12 tools each, scored identically).

| Site | Cohort | Tools | Write-shaped | consequentialHint | 3rd-party | Shopify platform | Verdict | Score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3dstreet.app | c_oss_webmcp_dependent | 28 | 2 | 0 | 0 | 0 | CONCERNS | 78 |
| webroom.openai.chatgpt.site | d_showcase | 28 | 0 | 0 | 0 | 0 | PASS | 100 |
| fieldwork-beat-machine.openai.chatgpt.site | d_showcase | 26 | 0 | 0 | 0 | 0 | PASS | 100 |
| video-editor.ai-creator.top | d_showcase | 21 | 2 | 0 | 0 | 0 | PASS | 84 |
| alibaba.github.io | c_oss_webmcp_dependent | 20 | 1 | 0 | 0 | 0 | CONCERNS | 85 |
| persona-chat.dev | d_showcase | 17 | 2 | 0 | 0 | 0 | CONCERNS | 70 |
| snugug.github.io | d_showcase | 16 | 1 | 0 | 0 | 0 | PASS | 92 |
| agentive.au | a_knowngood | 14 | 2 | 0 | 0 | 0 | PASS | 84 |
| scvd.store | d_showcase | 14 | 2 | 1 | 0 | 0 | CONCERNS | 85 |
| apparel.monster | a_knowngood | 13 | 5 | 7 | 0 | 0 | PASS | 100 |
| paperie-webmcp-greeting-cards.openai.chatgpt.site | d_showcase | 13 | 0 | 0 | 0 | 0 | PASS | 100 |
| jsonstat.com | d_showcase | 12 | 0 | 0 | 0 | 0 | PASS | 100 |
| sundaytable.openai.chatgpt.site | d_showcase | 12 | 2 | 0 | 0 | 0 | PASS | 84 |
| wandernote.openai.chatgpt.site | d_showcase | 11 | 1 | 0 | 0 | 0 | PASS | 92 |
| intlayer.org | d_showcase | 10 | 2 | 0 | 0 | 0 | PASS | 84 |
| margin-local-docs.openai.chatgpt.site | d_showcase | 10 | 0 | 0 | 0 | 0 | PASS | 100 |
| agentready.gh.miniasp.com | c_oss_webmcp_dependent | 9 | 1 | 0 | 9 | 0 | CONCERNS | 76 |
| docyrus.com | a_knowngood | 9 | 1 | 0 | 0 | 0 | PASS | 92 |
| frogman.in | a_knowngood | 9 | 1 | 0 | 0 | 0 | PASS | 92 |
| qrcodecrafter.com | d_showcase | 9 | 0 | 0 | 0 | 0 | PASS | 100 |
| webmcp.corsen.ai | c_oss_webmcp_dependent | 8 | 0 | 0 | 0 | 0 | PASS | 97 |
| ora.ai | c_oss_webmcp_dependent | 7 | 0 | 0 | 0 | 0 | PASS | 100 |
| scholar-sidekick.com | d_showcase | 7 | 0 | 0 | 0 | 0 | PASS | 100 |
| superturbo.app | c_oss_webmcp_dependent | 7 | 0 | 0 | 0 | 0 | PASS | 100 |
| webmcp-flow.vercel.app | d_showcase | 7 | 1 | 0 | 0 | 0 | CONCERNS | 82 |
| emingure.github.io | d_showcase | 6 | 3 | 0 | 6 | 0 | CONCERNS | 63 |
| webmcp.cool | d_showcase | 6 | 1 | 0 | 0 | 0 | PASS | 89 |
| bui-hinsche.com | a_knowngood | 5 | 1 | 0 | 0 | 0 | CONCERNS | 85 |
| crossword-desk-studio.openai.chatgpt.site | d_showcase | 5 | 0 | 0 | 0 | 0 | PASS | 100 |
| eduardocruz.com | a_knowngood | 5 | 1 | 0 | 0 | 0 | PASS | 86 |
| flyingfish.in | a_knowngood | 5 | 0 | 0 | 0 | 0 | PASS | 100 |
| jobspipe.dev | a_knowngood | 5 | 0 | 0 | 0 | 0 | PASS | 100 |
| kuro.tw | c_oss_webmcp_dependent | 5 | 2 | 0 | 0 | 0 | CONCERNS | 82 |
| popularchairs.com | a_knowngood | 5 | 1 | 0 | 0 | 0 | CONCERNS | 85 |
| specification.website | a_knowngood | 5 | 0 | 0 | 0 | 0 | PASS | 100 |
| stacktr.ee | d_showcase | 5 | 2 | 0 | 0 | 0 | PASS | 84 |
| techiewithbeard.com | c_oss_webmcp_dependent | 5 | 0 | 0 | 0 | 0 | PASS | 100 |
| webmcp.oxidt.com | c_oss_webmcp_dependent | 5 | 1 | 0 | 0 | 0 | CONCERNS | 85 |
| webmcpify.at | c_oss_webmcp_dependent | 5 | 0 | 0 | 0 | 0 | PASS | 100 |
| 360automation.ai | a_knowngood | 4 | 0 | 0 | 0 | 0 | PASS | 100 |
| africantechno.com | a_knowngood | 4 | 0 | 0 | 0 | 0 | PASS | 100 |
| andrey-markin.com | c_oss_webmcp_dependent | 4 | 0 | 0 | 0 | 0 | PASS | 100 |
| brandhalo.io | a_knowngood | 4 | 0 | 0 | 0 | 0 | PASS | 100 |
| britecity.com | a_knowngood | 4 | 0 | 0 | 0 | 0 | PASS | 100 |
| business.digital | a_knowngood | 4 | 1 | 0 | 0 | 0 | PASS | 92 |
| gaffer.sh | a_knowngood | 4 | 1 | 0 | 0 | 0 | CONCERNS | 85 |
| gosx3d.m31labs.dev | c_oss_webmcp_dependent | 4 | 0 | 0 | 0 | 0 | PASS | 100 |
| mahinavilla.com | a_knowngood | 4 | 0 | 0 | 0 | 0 | PASS | 100 |
| mentria.ai | c_oss_webmcp_dependent | 4 | 0 | 0 | 0 | 0 | PASS | 100 |
| orchestkit.yonyon.ai | c_oss_webmcp_dependent | 4 | 0 | 0 | 0 | 0 | PASS | 100 |
| webmcp.sh | d_mcpb_showcase | 4 | 1 | 0 | 0 | 0 | CONCERNS | 82 |
| webmcp.today | d_showcase | 4 | 0 | 0 | 0 | 0 | PASS | 100 |
| aaronlynn.com | a_knowngood | 3 | 1 | 0 | 0 | 0 | PASS | 92 |
| agent-ready.dev | d_showcase | 3 | 0 | 0 | 0 | 0 | PASS | 100 |
| ajuda.crmpiperun.com | a_knowngood | 3 | 0 | 0 | 0 | 0 | PASS | 100 |
| crema-and-co-client.fly.dev | d_showcase | 3 | 0 | 0 | 0 | 0 | PASS | 100 |
| docs.customer.io | a_knowngood | 3 | 0 | 0 | 0 | 0 | PASS | 100 |
| esim.edusport.co.za | a_knowngood | 3 | 0 | 0 | 0 | 0 | PASS | 100 |
| esim.thompsonstravel.co.za | a_knowngood | 3 | 0 | 0 | 0 | 0 | PASS | 100 |
| fluxwireless.co | a_knowngood | 3 | 0 | 0 | 0 | 0 | PASS | 100 |

## Errors

| Kind | Sites |
| --- | ---: |
| Timeout | 1 |
| net::ERR_HTTP2_PROTOCOL_ERROR | 1 |
| net::ERR_TIMED_OUT | 1 |

## Observations

- Shopify's storefront module is the largest single source of WebMCP tools in this sample: 1104 of 1657 tools on 92 sites, the same 12 tools and descriptions everywhere. Its `add_to_cart` description tells agents not to ask the user to confirm, and none of its write tools (`add_to_cart`, `update_cart_lines`, `cancel_cart`, `proceed_to_checkout`) set `consequentialHint`. Because merchants cannot edit these, any change belongs with the platform.
- Outside Shopify, 38 of 48 write-shaped tools (79.2%) lack `consequentialHint`; only 8 tools in the whole sample set it.
- Of 336 sites a public directory lists as WebMCP users, 37 (11%) registered a tool on homepage load. The rest may register on other pages, after interaction, behind a bot wall, or no longer use WebMCP.
- The control cohort (51 large sites with no static WebMCP marker) registered 0 tools, so the scan did not produce false adoption.
- No prompt-injection pattern matched outside the Shopify platform description, and no tool had a missing or malformed inputSchema.
- 10 tools were seen only through CDP/`getTools` and not through the `registerTool` hook (registered before the init script, or declared without script); they have no `registeredBy`.

## Audit tool issues found by this run

- WMCP-005 treats `cdn.shopify.com` as third-party. Shopify usually serves its storefront module from the shop's own domain under `/cdn/shopifycloud/`, but on cotopaxi.com it came from `cdn.shopify.com`, so the same 12 platform tools picked up 12 medium findings and the site alone scored FAIL (46) instead of CONCERNS (62). Platform CDNs (Shopify, and brand asset domains like `assets.targetimg1.com` for target.com) need an allowlist or a softer severity.
- Helper libraries loaded from public CDNs (`unpkg.com`, `cdn.jsdelivr.net`) are reported as third-party because the library's file calls `registerTool`. That is accurate about where the code came from, but the page author chose those tools; the finding text could say "registered via a library loaded from ...".
- `documentModelContext` is always true with the WebMCP flag on, so it does not indicate adoption. A field recording whether page script touched `document.modelContext` would be more useful.

## Caveats

- Not a random sample; cohort a comes from a directory that lists sites already flagged as WebMCP users, and the Known Good terms forbid bulk extraction, so the seed list stays internal.
- Homepage-only, logged-out scans undercount tools that appear on product, cart or account pages.
- Bot walls (403/429, challenge pages) can hide a site's tools; those show up as loads with zero tools, not as errors.
- The write-shape classifier is name and description based. It errs toward flagging cart edits (low tier) and checkout (high tier).
