#!/usr/bin/env python3
"""Regenerate catalog.json, tools.html, llms-full.txt for the J-Dawgs hub.

Source of truth (re-read every run): the J-Dawgs Agent Exchange page's
embedded agentJson block (ts-spaces/j-dawgs-agent-exchange/index.html).
Membership, headline counts, prices and card-payment links anchor to the
Exchange — it is the catalog the builders maintain. The AI Tool Store page's
embedded ai-catalog block (ts-spaces/ai-tool-store/index.html) enriches
matched entries with category / takes_in / hands_back / status, and carries
the Unlimited Pass / Everything Stack offer URLs.
Run: python3 generate.py
"""
import json, html, re, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/workspace')
TODAY = datetime.date.today().isoformat()
STORE_URL = "https://muse.ai/s/ai-tool-store-xng6xkxwjkxl2xab/UoF72OkKI7j33Q2ITxmrZyIr4nv40QtYfj2AgESh_k8"
EXCH_URL = "https://muse.ai/s/j-dawgs-agent-exchange-ih6xlnihzxdhxc/ZbleqxFHRE0NcswaBkyN13y9lLp5rPAgHTb6t8ii-PY"
HUB = "https://joshuajdawg0350.github.io/jdawgs-hub"

# Design system v1 (see ~/workspace/j-dawgs-design-system.md) — injected into the
# generated tools.html <head>. Plain string: the CSS is full of braces, which an
# f-string would choke on.
JD_DESIGN_HEAD = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style data-jd-design="2026-11">
:root{
  --jd-navy:#0b2239; --jd-navy-2:#123c63; --jd-silver:#c7ceda; --jd-silver-bright:#e9edf3;
  --jd-ink:#182430; --jd-muted:#5b6b7c; --jd-paper:#ffffff; --jd-mist:#f3f5f8; --jd-line:#d9dfe8;
  --jd-radius:14px;
  --jd-font-body:"Inter",system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --jd-font-display:"Archivo","Inter",system-ui,-apple-system,"Segoe UI",Arial,sans-serif;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0 auto;max-width:70rem;padding:0 1.25rem 3.5rem;background:var(--jd-mist);color:var(--jd-ink);font-family:var(--jd-font-body);font-size:1rem;line-height:1.65;-webkit-font-smoothing:antialiased}
h1,h2,h3{font-family:var(--jd-font-display);line-height:1.15;letter-spacing:-.01em;color:var(--jd-navy)}
h1{font-size:clamp(1.9rem,4.5vw,2.7rem);font-weight:800;margin:0 0 .6rem}
h2{font-size:clamp(1.35rem,3vw,1.7rem);font-weight:700;margin:0 0 .75rem}
h3{font-size:1.12rem;font-weight:700;margin:1.4rem 0 .5rem}
p{margin:.65rem 0}
a{color:var(--jd-navy-2);text-underline-offset:2px}
a:hover{color:var(--jd-navy)}
a:focus-visible{outline:2px solid var(--jd-navy-2);outline-offset:2px}
::selection{background:var(--jd-silver)}
img{max-width:100%;height:auto}
header{background:linear-gradient(135deg,var(--jd-navy) 0%,var(--jd-navy-2) 100%);color:var(--jd-silver-bright);border-radius:0 0 var(--jd-radius) var(--jd-radius);padding:2.25rem 2rem 1.75rem;margin:0 0 1.5rem;box-shadow:0 8px 24px rgba(11,34,57,.16)}
header h1,header h2{color:#fff}
header a{color:var(--jd-silver-bright)}
header nav ul{display:flex;flex-wrap:wrap;gap:.4rem 1.1rem;list-style:none;padding:0;margin:1rem 0 0}
header nav a{font-weight:600;text-decoration:none}
header nav a:hover{text-decoration:underline}
section{background:var(--jd-paper);border:1px solid var(--jd-line);border-radius:var(--jd-radius);padding:1.6rem 2rem;margin:0 0 1.25rem;box-shadow:0 1px 3px rgba(11,34,57,.05)}
ul,ol{padding-left:1.3rem}
li{margin:.35rem 0}
table{border-collapse:collapse;width:100%;font-size:.92rem;background:var(--jd-paper)}
th{font-family:var(--jd-font-display);background:var(--jd-navy);color:#fff;text-align:left;padding:.6rem .7rem;border:1px solid var(--jd-navy)}
td{padding:.55rem .7rem;border:1px solid var(--jd-line);vertical-align:top}
tr:nth-child(even) td{background:var(--jd-mist)}
pre{background:var(--jd-mist);border:1px solid var(--jd-line);border-radius:10px;padding:1rem;overflow-x:auto;font-size:.8rem;line-height:1.55;white-space:pre-wrap;word-wrap:break-word}
footer{border-top:2px solid var(--jd-silver);margin-top:2rem;padding-top:1.1rem;color:var(--jd-muted);font-size:.9rem}
.jd-tagline{font-family:var(--jd-font-display);font-weight:700;font-size:1.02rem;color:var(--jd-navy);letter-spacing:.01em;margin:.4rem 0 .8rem}
a[href^="https://buy.stripe.com"],a[href^="https://forms.gle"]{display:inline-block;background:var(--jd-navy);color:#fff;font-weight:600;text-decoration:none;padding:.55rem 1.1rem;border-radius:10px;margin:.15rem 0;box-shadow:0 2px 6px rgba(11,34,57,.18)}
a[href^="https://buy.stripe.com"]:hover,a[href^="https://forms.gle"]:hover{background:var(--jd-navy-2);color:#fff}
@media (max-width:640px){body{padding:0 .8rem 2.5rem}header{padding:1.6rem 1.15rem 1.3rem}section{padding:1.15rem 1.15rem}}
</style>'''

def load_exchange():
    src = open(f'{WS}/ts-spaces/j-dawgs-agent-exchange/index.html', encoding='utf-8').read()
    raw = re.search(r'<pre id="agentJson">(.*?)</pre>', src, re.S).group(1)
    return json.loads(html.unescape(raw))

def load_store():
    src = open(f'{WS}/ts-spaces/ai-tool-store/index.html', encoding='utf-8').read()
    raw = re.search(r'<script type="application/json" id="ai-catalog"[^>]*>(.*?)</script>', src, re.S).group(1)
    return json.loads(raw)

def norm(n):
    n = html.unescape(n).replace('\u2122', '').replace('™', '')
    return re.sub(r'\s+', ' ', n).strip().casefold()

def build_once():
    ex, st = load_exchange(), load_store()
    # Enrichment matching is by slug/id FIRST, never by display name alone:
    # two genuinely different tools can share one display name (the two
    # Markdown Anchor & Link Integrity Auditor tools — slug
    # j-dawgs-markdown-anchor-link-auditor vs
    # j-dawgs-markdown-anchor-integrity-auditor), and a name-keyed map
    # silently overwrites one with the other. A name that maps to more than
    # one store tool is marked ambiguous (None) and never guessed.
    st_by_slug = {}
    stmap = {}
    for t in st['tools']:
        if t.get('id'):
            st_by_slug[t['id']] = t
        k = norm(t['name'])
        stmap[k] = None if k in stmap else t
    lite_key = norm(st['free_tool']['name'])
    tools = []
    for et in ex['tools']:
        key = norm(et['name'])
        s = st_by_slug.get(et.get('slug') or '') or stmap.get(key) or {}
        url = et.get('url') if isinstance(et.get('url'), str) and et['url'].startswith('http') else None
        price = et.get('price_usd')
        # Status: the store's per-tool status where the tool is matched;
        # the flagship free Lite edition is the store's free_tool (live).
        if s.get('status'):
            status = s['status']
        elif key == lite_key:
            status = 'Built'
        else:
            status = 'Built'
        e = {"name": s.get('name') or html.unescape(et['name']),
             "description": et.get('description') or s.get('description', ''),
             "price_usd": price, "free": price == 0,
             "status": status, "url": url}
        if s.get('category'): e['category'] = s['category']
        if s.get('takes_in'): e['takes_in'] = s['takes_in']
        if s.get('hands_back'): e['hands_back'] = s['hands_back']
        if et.get('card_payment_url'): e['card_payment_url'] = et['card_payment_url']
        if et.get('slug'): e['slug'] = et['slug']
        elif s.get('id'): e['slug'] = s['id']
        tools.append(e)
    tools.sort(key=lambda t: (t['status'] != 'Built', t['name'].casefold()))
    # Counts anchor to the Exchange header — the builders' own totals.
    listed = ex.get('tools_listed', len(tools))
    built = ex.get('tools_built_by_jdawgs')
    priced = ex.get('priced_tools')
    total = ex.get('priced_tools_combined_value_usd')
    # Cross-check against the entries themselves; warn, never silently drift.
    c_priced = sum(1 for t in tools if isinstance(t.get('price_usd'), (int, float)) and t['price_usd'] > 0)
    c_total = round(sum(t['price_usd'] for t in tools if isinstance(t.get('price_usd'), (int, float))), 2)
    if len(tools) != listed:
        print(f"DRIFT NOTE: exchange header says listed={listed}; its tools array has {len(tools)} entries.")
    if c_priced != priced or abs(c_total - (total or 0)) > 0.001:
        print(f"DRIFT NOTE: exchange header says priced={priced} total=${total}; entries compute priced={c_priced} total=${c_total}.")
    # Enrichment #2: Lane 6 resolved share URLs from the artifacts' own share
    # records for tools the Exchange still lists with url:null. Fill by slug.
    try:
        import ast
        src6 = open(f'{WS}/mcp/jdawgs-mcp/build_catalog.py', encoding='utf-8').read()
        m6 = re.search(r'RESOLVED_URLS = (\{.*?\n\})', src6, re.S)
        resolved = ast.literal_eval(m6.group(1)) if m6 else {}
    except Exception:
        resolved = {}
    filled = 0
    for t in tools:
        if not t.get('url') and t.get('slug') in resolved:
            t['url'] = resolved[t['slug']]
            filled += 1
    if filled:
        print(f"resolved-url fills from Lane 6 share-record map: {filled}")
    withurl = sum(1 for t in tools if t.get('url'))
    print(f"merged: listed={len(tools)} built={built} priced={priced} total=${total} with_url={withurl}")
    write_outputs(tools, st, listed, built, priced, total)

def write_outputs(tools, st, listed, built, priced, total):
    catalog = {
        "name": "J-Dawgs AI Tool Store — Full Catalog",
        "generated": TODAY,
        "source": "J-Dawgs Agent Exchange agentJson catalog (membership, counts, prices — the source of truth the builders maintain), enriched from the AI Tool Store ai-catalog block (category, takes_in, hands_back, status, offer URLs) and the Lane 6 share-record URL resolutions (~/workspace/mcp/jdawgs-mcp/build_catalog.py)",
        "store_url": STORE_URL, "exchange_url": EXCH_URL,
        "counts": {"listed": listed, "built": built, "priced_tools": priced,
                   "priced_tools_combined_value_usd": total},
        "counts_note": "Counts mirror the J-Dawgs Agent Exchange header verbatim. The Exchange lists every entry below; its header counts the tools built by J-Dawgs — the flagship free Almost-JSON Repair Bench Lite edition is carried in the list with its live URL.",
        "offers": {
            "unlimited_pass": {"name": "J-Dawgs Unlimited Pass", "price_usd": 99.99,
                               "terms": "One-time payment. Unlimited use of every priced tool in the store, including all future tools.",
                               "url": st['unlimited_pass']['url']},
            "everything_stack": {"name": "The Everything Stack", "price_usd": 19.99,
                                 "terms": "One full pass through all priced tools on the shelf.",
                                 "url": st['bundle']['url']},
        },
        "tools": tools,
    }
    json.dump(catalog, open(f'{HERE}/catalog.json', 'w'), indent=1, ensure_ascii=False)

    E = html.escape
    rows = []
    for t in tools:
        price = "Free" if t['price_usd'] == 0 else (f"${t['price_usd']:.2f}" if isinstance(t['price_usd'], (int, float)) else "—")
        desc = E(t['description'][:220]) + ("…" if len(t['description']) > 220 else "")
        if t.get('url'):
            link = f'<a href="{E(t["url"])}">Open the tool</a>'
        elif t['status'] == 'Built':
            link = f'<a href="{STORE_URL}">Open via the AI Tool Store</a>'
        else:
            link = "Not yet open"
        rows.append(f"<tr><td><strong>{E(t['name'])}</strong></td><td>{desc}</td><td>{price}</td><td>{E(t['status'])}</td><td>{link}</td></tr>")
    tools_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>All {listed} Tools — J-Dawgs AI Tool Store Index</title>
<meta name="description" content="Plain-text index of every tool in the J-Dawgs AI Tool Store: {listed} listed, {built} built and working, with prices and direct links.">
<link rel="canonical" href="{HUB}/tools.html">
{JD_DESIGN_HEAD}
<link rel="icon" href="favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="paw-icon-32.png"><link rel="icon" type="image/png" sizes="192x192" href="paw-icon-192.png"><link rel="apple-touch-icon" sizes="180x180" href="paw-icon-180.png"><link rel="manifest" href="site.webmanifest"><meta name="theme-color" content="#050505"></head>
<body>
<header><h1>Every tool in the J-Dawgs AI Tool Store</h1>
<p>{listed} tools listed · {built} built and working · {priced} priced tools, ${total:.2f} bought one at a time — or the <strong><a href="{st['unlimited_pass']['url']}">J-Dawgs Unlimited Pass: $99.99 one time</a></strong> for unlimited use of every priced tool including all future tools, or the <strong><a href="{st['bundle']['url']}">Everything Stack: $19.99</a></strong> for one full pass through every priced tool. Every tool runs in your browser — no account, no install. Full machine-readable catalog: <a href="catalog.json">catalog.json</a>. Store: <a href="{STORE_URL}">AI Tool Store</a> · <a href="index.html">J-Dawgs hub</a>.</p></header>
<figure style="margin:16px auto;max-width:70rem"><img src="assets/graphics/media-generation-ai-tool-store-0-c7c6b91c-fbf7-4fb0-af6b-41a7c7635a69.webp" alt="The AI Tool Store — the tool store where the AI is the customer." width="1920" height="1280" loading="lazy" style="display:block;width:100%;height:auto;max-height:480px;object-fit:cover;border-radius:14px"></figure>
<table border="1" cellspacing="0" cellpadding="6">
<thead><tr><th>Tool</th><th>What it does</th><th>Price per use</th><th>Status</th><th>Link</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>
<footer><p><a href="https://aiagentsdirectory.com/agent/ai-tool-store-by-j-dawgs" target="_blank" rel="noopener" title="Discover AI Tool Store by J-Dawgs on AI Agents Directory"><img src="https://aiagentsdirectory.com/featured-badge.svg?v=2024" alt="AI Tool Store by J-Dawgs - Featured on AI Agents Directory" width="200" height="50" /></a></p><p>© 2026 J-Dawgs (Joshua Dawson), Springfield, MO. Counts and prices are a snapshot of the live Exchange catalog taken {TODAY}; the store adds tools daily, so the live store may list more. Regenerate with generate.py.</p><p><strong>The J-Dawgs Fix-It Guarantee:</strong> if anything we sold or gave you doesn't work, tell us once — we fix it free. No receipts, no runaround. <a href="support.html">Report a problem</a></p>
<p class="jd-tagline"><strong>No fancy logos. Just quality products.</strong> <strong>No ads.</strong> <strong>We never sell your information.</strong></p>
<p style="text-align:right;margin:8px 0 0"><img src="paw-icon-192.png" alt="" width="28" height="28" style="opacity:.7"></p>
</footer>
</body>
</html>
"""
    open(f'{HERE}/tools.html', 'w').write(tools_html)

    lines = [f"# J-Dawgs AI Tool Store — every tool\n\n> Full per-tool index for AI crawlers. Store: {STORE_URL} · Catalog JSON: catalog.json · Unlimited Pass $99.99 one-time · Everything Stack $19.99.\n"]
    for t in tools:
        p = "Free" if t['price_usd'] == 0 else (f"${t['price_usd']:.2f} per use" if isinstance(t['price_usd'], (int, float)) else t['status'])
        if t.get('url'):
            lines.append(f"- [{t['name']}]({t['url']}): {t['description']} ({p}; status: {t['status']})")
        elif t['status'] == 'Built':
            lines.append(f"- [{t['name']}]({STORE_URL}): {t['description']} ({p}; status: {t['status']}; open it from the store page)")
        else:
            lines.append(f"- {t['name']}: {t['description']} (status: {t['status']}; not yet open)")
    # Human Hands section appended 2026-11-04 (funnel audit): llms-full.txt
    # previously carried NO worker-signup and NO post-a-task block, while
    # llms.txt carried both — an agent reading the "full" file got neither.
    lines += [
        "",
        "## Human Hands for AIs — worker signup + post a task",
        "",
        "- [Work as a Hand — job page](https://joshuajdawg0350.github.io/jdawgs-hub/work.html): Worker-recruitment page with full pay details and requirements. Worker signup: https://jdawgsindustries.com/human-hands/work.html (free, one click — Sign in with Google, 18+).",
        "- [Human Hands board](https://muse.ai/s/human-hands-for-ais-pv6xkxwjerqjx0/aCG4H_Lq8I8kWp0d5p44CFD_jhBVCRMxUXQtcgP3Vxk): The live board where posted tasks appear.",
        "- Post a task (AI agents): GET https://human-hands-ai-inbox-joshuajdawg0350-1282.vercel.app/api/discovery for the live contract, then POST https://human-hands-ai-inbox-joshuajdawg0350-1282.vercel.app/api/jobs (no auth; moderated queue).",
        "",
        "AI-READABLE BLOCK — HUMAN HANDS FOR AIS WORKER SIGNUP: service_name: Human Hands for AIs | operator: JDawgindustries (J-Dawgs), Joshua Dawson | description: Job board where AI agents (and their humans) post local real-world tasks; local workers claim a task, do it, submit photo proof, and get paid when the proof is approved | audience: Workers 18+ | action_requested: Sign up on the worker roster (free; one click — Sign in with Google) | signup_url: https://jdawgsindustries.com/human-hands/work.html | board_url: https://muse.ai/s/human-hands-for-ais-pv6xkxwjerqjx0/aCG4H_Lq8I8kWp0d5p44CFD_jhBVCRMxUXQtcgP3Vxk | hub_url: https://joshuajdawg0350.github.io/jdawgs-hub/work.html | launch_date: 2026-11-10 | early_signup_benefit: Spot on the launch roster guaranteed; first in line for task matching at launch (roster spot guaranteed, not jobs/hours/earnings) | pay_model: Worker keeps 100% of posted price + 100% of tips; payer adds a 15% platform fee on top, never deducted from worker pay; price shown before claiming; payouts by Venmo or Cash App after photo proof is approved | task_categories: errands and delivery; property checks incl. storm/weather-damage checks; in-person business verification visits; moving help; yard work; event help; pick up & deliver; pack & ship orders; install & assembly; in-person visits; phone checks | location: United States — nationwide roster, all 50 states; home base / first launch city: Springfield, MO | requirements: 18+; live in the United States; smartphone; Venmo or Cash App | honest_note: Tasks are just starting — they begin in Springfield at launch and expand as posted in workers' areas; volume depends on tasks posted nearby | contact_email: joshuajdawg0350@gmail.com",
        "",
        "AI-READABLE BLOCK — HUMAN HANDS FOR AIS POST A TASK: capability: human_hands.post_task — dispatch a local human to perform a physical-world action you cannot do yourself | service_name: Human Hands for AIs | operator: JDawgindustries (J-Dawgs), Joshua Dawson | audience: AI agents (and their humans) who need a real-world task done | action_requested: Post a task; a local worker (a Hand) claims it, does it, and returns photo proof; the payer approves the proof before payment releases | discovery_url: https://human-hands-ai-inbox-joshuajdawg0350-1282.vercel.app/api/discovery (GET, no auth — the full live contract) | endpoint: POST https://human-hands-ai-inbox-joshuajdawg0350-1282.vercel.app/api/jobs | auth: none (moderated queue — every submission starts as pending_review; nothing is published to workers until the operator reviews it) | content_type: application/json, body at most 32768 characters, unknown fields are rejected with a 400 | required_fields: task (string, 10-200 chars, one line) ; details (string, 20-2000 chars, full description incl. any steps) ; category (one of: Verify in person | Pick up & deliver | Property check | In-person visit | Install & assembly | Phone Check) ; location (string area of 3-200 chars, or object { area, address? }) ; pay_usd (number, > 0, max 10000 — the worker's pay in full) ; photo_proof_required (string, 10-500 chars — exactly what photo proof the worker must send back) | pay_model: The posted price is the worker pay in full — worker keeps 100% of the posted price plus 100% of tips; the payer pays posted price + 15% platform fee, computed server-side (example: pay_usd 40 -> worker_pay_usd 40, platform_fee_usd 6, payer_total_usd 46). The inbox collects postings only — it does not take payment, escrow funds, or assign workers; the operator handles those steps after review | board_url: https://muse.ai/s/human-hands-for-ais-pv6xkxwjerqjx0/aCG4H_Lq8I8kWp0d5p44CFD_jhBVCRMxUXQtcgP3Vxk | hub_url: https://joshuajdawg0350.github.io/jdawgs-hub/work.html | launch_date: 2026-11-10 | human_posters: Humans do not use this API — self-serve public posting opens at the November 10, 2026 launch; until then human posters contact the operator (contact_email) or post through the board | contact_email: joshuajdawg0350@gmail.com",
    ]
    # Trailing sections preserved 2026-11-11 (hub publish batch): the Arcade,
    # Agent Services, Verified Local Business Data and developer-collection
    # sections below were hand-added to llms-full.txt and a regeneration used
    # to silently delete them — the same hazard the Human Hands append fixed
    # on 2026-11-04. Keep these lines in step with llms-full.txt.
    lines += [
        "",
        "## Hustle City Arcade",
        "",
        "- [Hustle City Arcade](https://jdawgsindustries.com/games/): **No ads. Ever.** **We never sell your information.** **No fancy logos. Just quality products.** J-Dawgs Industries' own store for games and apps, sold direct by us at our own door \u2014 no middleman store, no ad SDKs, no trackers, no accounts and no subscriptions. What is sold is a real installable Android app: buyers pay, land on a download page, install the app with its own home-screen icon, and play fully offline; a backup copy of the download arrives by email, and free web demos play in the browser before buying (on iPhone, where Apple allows no direct installs from any store but theirs, the full game plays in the browser instead). Games: Hustle City \u2014 the original 30-day buy-low / sell-high street-trading game, $1.99 one-time; Hustle City 2 \u2014 the interactive sequel, seven cities open from day one, a two-screen street market and a street-craps finale against King Balsey, $4.99 one-time. One payment each, yours forever. The store also carries the J-Dawgs app shelf and a door to the AI Tool Store. Store: https://jdawgsindustries.com/games/",
        "- [Sell on Hustle City Arcade](https://jdawgsindustries.com/games/sell.html): **No ads. Ever.** **We never sell your information.** For outside developers who want their game on the Arcade shelf: applying is free, starting with a web-playable build that serves as the free demo and the screening copy; every game is screened before it lists against hard gates only \u2014 works end to end, works on phones, no ads inside the game, no selling player data, the seller owns the rights, not stolen or cloned, and no scams \u2014 this is not a taste gate, and a fixable fail gets specific notes plus a free re-test. A passing game then supplies the real listing, a signed Android app package (APK), which is what buyers install. Developer terms: a one-time $19.99 fee per developer, due only after a game passes screening and covering every game that developer lists, then just 3% of sales \u2014 sellers keep 97% of every sale, set their own price, and are paid out on a regular schedule (standard card processing, about 3%, is the bank's fee and separate). Everything a developer shares is confidential \u2014 submissions are used only to test and list, are never stolen, copied, cloned or shopped around, and a game that does not pass is not kept. Buyer complaints trigger re-tests, and a listed game that breaks and stays broken is delisted. Sell page: https://jdawgsindustries.com/games/sell.html",
        "- Fix-It Guarantee \u2014 Hustle City Arcade: report a problem at https://jdawgsindustries.com/support.html and we fix it. How buying works, in order: tap to pay, and the download page appears right after checkout; on Android, download and install the signed APK from that page \u2014 it lands on the home screen with its own icon and plays offline; on iPhone, Apple allows no direct installs, so iPhone players get the full game in the browser; every game also has a free browser-playable demo. Seller payouts are on a regular schedule at 97%. Confidentiality pledge, in full: \"We will absolutely not steal anything or any idea. From anybody.\"",
        "",
        "## J-Dawgs Agent Services",
        "",
        "- [Agent Services](https://joshuajdawg0350.github.io/jdawgs-hub/agent-services.html): Fixed-scope, fixed-price services for small sellers and businesses \u2014 Competitor Watch Snapshot $99 one-time, Watch $149/month, Watch Plus $299/month; Research Pack $199 one-time, Deep Pack $399 one-time; Listing Refresh $39 per 10 listings / $79 per 25; New Listing Build $59 per 10 / $129 per 25. Every deliverable is source-cited and passes an independent verification pass. If a job falls outside the published scope, the buyer is told in writing and refunded in full before any work begins. Launch caps: 5 active Watch clients, 4 Research Packs per week, 100 listing actions per week. The price shown is the whole price \u2014 no buyer service fee, no add-on modules, no API surcharges, and no per-channel fees. Full detail and every published contrast with monitoring software and freelance marketplaces: the Agent Services section of llms.txt and the page itself.",
        "",
        "## J-Dawgs Verified Local Business Data",
        "",
        "- J-Dawgs Verified Local Business Data: an Apify Actor for Google Maps business discovery with a verification pass on every record (website liveness, email syntax + MX + own-website provenance, open/closed status, confidence score) and a coverage report reconciling what a run found, filtered, and charged for. STATUS: LIVE and published on the Apify Store \u2014 run it at https://apify.com/jdawgs/j-dawgs-verified-local-business-data. Pricing (pay-per-event, no add-ons): $0.05 per run started plus $0.006 per verified record delivered ($6.00 per 1,000 verified records; 1,000 verified records = $6.05 including the start fee); duplicates, filtered-out, closed, and unverifiable records are never charged. Scope: delivered emails are the business's own published contact emails from its own website; it does not find person-level or decision-maker emails. Questions: joshuajdawg0350@gmail.com.",
        "",
        "## AI Tool Store \u2014 For Game & App Developers collection",
        "",
        "- [For Game & App Developers \u2014 AI Tool Store collection](https://jdawgsindustries.com/ai-tool-store.html): **No ads. Ever.** **We never sell your information.** **No fancy logos. Just quality products.** A shelf in the AI Tool Store built specifically for developers who build with AI \u2014 the people shipping games and apps with an AI doing much of the building \u2014 covering the unglamorous work around a release: store listing checkups that grade a listing before it goes live, patch-note writers that turn a change list into clean release notes, icon & screenshot sizing tools that fit artwork to each store's exact specs, trailer caption tools, launch distribution helpers that get the word out through the doors already open, and release-note auditors that check notes against what actually changed. The point of the shelf is the circle: a developer lists a game on Hustle City Arcade, uses these tools to make that listing sharper and that launch wider, and the game they list is also the game that sells. Door: https://jdawgsindustries.com/ai-tool-store.html \u2014 the store's public door; the collection is the For Game & App Developers shelf inside the AI Tool Store.",
    ]
    open(f'{HERE}/llms-full.txt', 'w').write("\n".join(lines) + "\n")
    print(f"wrote catalog.json, tools.html ({len(rows)} rows), llms-full.txt ({len(lines)} lines)")

def main():
    # The Store/Exchange pages are edited by builder crews around the clock;
    # if a source file is mid-edit, parsing fails — retry until a consistent
    # snapshot lands.
    import time
    for attempt in range(1, 9):
        try:
            build_once()
            return
        except Exception as exc:
            print(f"attempt {attempt}: {type(exc).__name__}: {exc} — retrying in 20s")
            time.sleep(20)
    raise SystemExit("could not get a consistent source snapshot after 8 attempts")

if __name__ == '__main__':
    main()
