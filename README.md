# jdawgs-hub

The indexable front door for J-Dawgs. All four businesses live behind muse.ai share
URLs that serve a blank JavaScript app shell to crawlers and AI fetchers, so search
engines and AI crawlers see almost nothing. This folder is the portable,
server-rendered layer that fixes that: plain HTML and text a crawler can read with
zero JavaScript.

## Contents

- `index.html` — the hub: what each business is, prices, and links to all four live pages + the worker signup form.
- `tools.html` — one crawlable row per Tool Store tool (110 listed + the free flagship), with price, status, and a direct link.
- `catalog.json` — the full Tool Store catalog (name, description, price, status, URL, card-payment link) in clean JSON, sourced from the J-Dawgs Agent Exchange catalog and reconciled against the AI Tool Store catalog (110 listed / 106 built / 102 priced / $85.50).
- `llms.txt` / `llms-full.txt` — per the llms.txt convention: the four properties for AI crawlers, plus a full per-tool index.
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

## Links
- Live hub: https://joshuajdawg0350.github.io/jdawgs-hub/
- Work as a Hand (worker signup): https://joshuajdawg0350.github.io/jdawgs-hub/work.html
- Signup form: https://forms.gle/kbYe1Uu8SShwE9kz8
- AI Tool Store: https://muse.ai/s/ai-tool-store-xng6xkxwjkxl2xab/UoF72OkKI7j33Q2ITxmrZyIr4nv40QtYfj2AgESh_k8
- J-Dawgs Trading Post: https://muse.ai/s/selling-website-xij6xkxuxkxy7cxxo/6OdKXk-tcAnCrK8M-DuEiyYuKf0AK24A1EeWn9CrFYI
