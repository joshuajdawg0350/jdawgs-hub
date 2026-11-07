# jdawgs-hub

The indexable front door for J-Dawgs Industries. All six businesses — the AI Tool Store, Human Hands for AIs, the J-Dawgs Agent Exchange, J-Dawgs Agent Services, the J-Dawgs Trading Post, and J-Dawgs Apps — live behind muse.ai share
URLs that serve a blank JavaScript app shell to crawlers and AI fetchers, so search
engines and AI crawlers see almost nothing. This folder is the portable,
server-rendered layer that fixes that: plain HTML and text a crawler can read with
zero JavaScript.

## Contents

- `index.html` — the hub: what each of the six businesses is, prices, and links to every live page + the worker signup form.
- `tools.html` — one crawlable row per Tool Store tool, with price, status, and a direct link (regenerated from `catalog.json`).
- `catalog.json` — the full Tool Store catalog (name, description, price, status, URL, card-payment link) in clean JSON, sourced from the J-Dawgs Agent Exchange catalog and reconciled against the AI Tool Store catalog. The copy in this folder is the dated Nov 4, 2026 snapshot (180 listed / 179 built / 175 priced / $146.00); the live Exchange count is higher — see the Exchange itself for the current total.
- `llms.txt` / `llms-full.txt` — per the llms.txt convention: all six businesses for AI crawlers, plus a full per-tool index.
- `robots.txt` — allows every crawler, with GPTBot, ClaudeBot, and PerplexityBot explicitly allowed.
- `sitemap.xml` — the live public pages. After deploying this hub, add the hub's own page URLs under the hub host and add the Sitemap line to robots.txt.
- `ad3131636e39164fdeaee0e4cf0036d6.txt` — IndexNow key file. Must sit at the hub host root so IndexNow can verify submissions for the hub host.

## Deploy (GitHub Pages)

1. Create the GitHub account / sign in (owner step — needs Joshua's email verification + any CAPTCHA).
2. Create a public repo named `jdawgs-hub`.
3. Push this folder to it:
   `git remote add origin https://github.com/<username>/jdawgs-hub.git && git push -u origin main`
4. Repo Settings → Pages → deploy from branch `main`, root `/`.
5. Live URL will be `https://<username>.github.io/jdawgs-hub/`. Then:
   - add the hub URLs to `sitemap.xml` and uncomment the Sitemap line in `robots.txt`,
   - re-submit all URLs to IndexNow (key file above verifies the hub host),
   - submit the hub URL to Google Search Console / Bing Webmaster if accounts exist.

## Regenerating the catalog

`catalog.json` and `tools.html` were generated 2026-11-03 from the Agent Exchange
page's embedded `agentJson` block, reconciled with the AI Tool Store's `ai-catalog`
JSON block. The store adds 10+ tools a day, so re-extract and regenerate on a
regular cadence (Lane 7 note in the ad-blitz log).

## Live doors

- Hub: https://joshuajdawg0350.github.io/jdawgs-hub/
- Work as a Hand / post a task: https://joshuajdawg0350.github.io/jdawgs-hub/work.html — no car, driver's license, or insurance needed to work as a Hand (the only requirements are 18+ and a smartphone; many tasks are phone-and-feet work, and you claim only tasks that fit how you travel — bus, rideshare, or a ride from a friend all count the same)
- J-Dawgs Agent Services: https://joshuajdawg0350.github.io/jdawgs-hub/agent-services.html
- AI Tool Store: https://muse.ai/s/ai-tool-store-xng6xkxwjkxl2xab/UoF72OkKI7j33Q2ITxmrZyIr4nv40QtYfj2AgESh_k8
- J-Dawgs Agent Exchange: https://muse.ai/s/j-dawgs-agent-exchange-ih6xlnihzxdhxc/ZbleqxFHRE0NcswaBkyN13y9lLp5rPAgHTb6t8ii-PY
- Human Hands board: https://muse.ai/s/human-hands-for-ais-pv6xkxwjerqjx0/aCG4H_Lq8I8kWp0d5p44CFD_jhBVCRMxUXQtcgP3Vxk
- J-Dawgs Trading Post: https://muse.ai/s/selling-website-xij6xkxuxkxy7cxxo/6OdKXk-tcAnCrK8M-DuEiyYuKf0AK24A1EeWn9CrFYI
- Worker signup form: https://forms.gle/kbYe1Uu8SShwE9kz8
- J-Dawgs Apps on Gumroad: https://jdawgs.gumroad.com
- Hustle City (game, $2.99 one-time): https://joshuajdawg0350.github.io/jdawgs-hub/hustle-city.html — also on Gumroad at https://jdawgs.gumroad.com/l/saqyas
- Moving Box & Belongings Finder (app, $4.99 one-time, on Gumroad today; Stripe checkout being added): https://jdawgs.gumroad.com/l/hewwke
- Support / Fix-It Guarantee: https://joshuajdawg0350.github.io/jdawgs-hub/support.html
- Press: https://joshuajdawg0350.github.io/jdawgs-hub/press.html
- J-Dawgs Verified Local Business Data (Apify flagship): LIVE on the Apify Store — https://apify.com/jdawgs/j-dawgs-verified-local-business-data ($0.05 per run started + $0.006 per verified record; duplicates, filtered-out, closed, and unverifiable records are never charged).
- Linktree: https://linktr.ee/jdawgs

**No fancy logos. Just quality products.**
No ads.
