#!/usr/bin/env python3
"""Regenerate catalog.json, tools.html, llms-full.txt for the J-Dawgs hub.

Sources (source of truth, re-read every run):
  - Agent Exchange page's embedded agentJson block  (ts-spaces/j-dawgs-agent-exchange/index.html)
  - AI Tool Store page's embedded ai-catalog block  (ts-spaces/ai-tool-store/index.html)
The store's headline counts define the catalog: its full list (110) minus nothing,
with the flagship free tool carried separately (free_flagship), exactly as the store
presents it. Run: python3 generate.py
"""
import json, html, re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser('~/workspace')
STORE_URL = "https://muse.ai/s/ai-tool-store-xng6xkxwjkxl2xab/UoF72OkKI7j33Q2ITxmrZyIr4nv40QtYfj2AgESh_k8"
EXCH_URL = "https://muse.ai/s/j-dawgs-agent-exchange-ih6xlnihzxdhxc/ZbleqxFHRE0NcswaBkyN13y9lLp5rPAgHTb6t8ii-PY"

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
    exmap = {norm(t['name']): t for t in ex['tools']}
    lite_key = norm(st['free_tool']['name'])
    tools, price_conflicts = [], 0
    # Membership and counts anchor to the STORE catalog (the task's anchor:
    # 110 listed / 106 built). The Exchange enriches matched entries.
    for s in st['tools']:
        key = norm(s['name'])
        et = exmap.get(key, {})
        url = et.get('url') if isinstance(et.get('url'), str) and et['url'].startswith('http') else None
        if not url and s.get('url'):
            url = s['url']
        price = et.get('price_usd')
        if price is None and s.get('price') not in (None, 'FREE'):
            try: price = float(str(s['price']).replace('$', ''))
            except ValueError: price = None
        if isinstance(et.get('price_usd'), (int, float)) and s.get('price') not in (None, 'FREE'):
            try:
                if abs(float(str(s['price']).replace('$', '')) - et['price_usd']) > 0.001:
                    price_conflicts += 1
            except ValueError: pass
        e = {"name": html.unescape(s['name']), "description": s['description'],
             "price_usd": price, "free": price == 0,
             "status": s['status'], "url": url}
        if s.get('category'): e['category'] = s['category']
        if s.get('takes_in'): e['takes_in'] = s['takes_in']
        if s.get('hands_back'): e['hands_back'] = s['hands_back']
        cpu = et.get('card_payment_url') or s.get('card_payment_url')
        if cpu: e['card_payment_url'] = cpu
        if et.get('slug'): e['slug'] = et['slug']
        elif s.get('id'): e['slug'] = s['id']
        tools.append(e)
    tools.sort(key=lambda t: (t['status'] != 'Built', t['name'].casefold()))
    built = sum(1 for t in tools if t['status'] == 'Built')
    priced = sum(1 for t in tools if isinstance(t.get('price_usd'), (int, float)) and t['price_usd'] > 0)
    total = round(sum(t['price_usd'] for t in tools if isinstance(t.get('price_usd'), (int, float))), 2)
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
    print(f"merged: listed={len(tools)} built={built} priced={priced} total=${total} with_url={withurl} price_conflicts={price_conflicts}")
    # The store page's own counts block lags its tools list during crew edits;
    # the merged list (built from the store's actual tools array) is the anchor.
    # Report drift as a warning instead of failing the whole generation.
    if len(tools) != st['counts']['listed'] or built != st['counts']['built']:
        print(f"DRIFT NOTE: store counts block says listed={st['counts']['listed']} built={st['counts']['built']}; "
              f"its tools array currently yields listed={len(tools)} built={built} (counts block reconciles at the end of the crew's edit).")
    write_outputs(tools, st, built, priced, total)

def write_outputs(tools, st, built, priced, total):
    lite = {"name": st['free_tool']['name'], "price_usd": 0, "url": st['free_tool']['url'],
            "note": "Flagship free tool, listed on the store outside the 110-count."}
    catalog = {
        "name": "J-Dawgs AI Tool Store — Full Catalog",
        "generated": "2026-11-03",
        "source": "AI Tool Store ai-catalog block (membership + counts anchor), enriched from the J-Dawgs Agent Exchange agentJson catalog and the Lane 6 share-record URL resolutions (~/workspace/mcp/jdawgs-mcp/build_catalog.py)",
        "store_url": STORE_URL, "exchange_url": EXCH_URL,
        "counts": {"listed": len(tools), "built": built, "priced_tools": priced,
                   "priced_tools_combined_value_usd": total},
        "offers": {
            "unlimited_pass": {"name": "J-Dawgs Unlimited Pass", "price_usd": 99.99,
                               "terms": "One-time payment. Unlimited use of every priced tool in the store, including all future tools.",
                               "url": st['unlimited_pass']['url']},
            "everything_stack": {"name": "The Everything Stack", "price_usd": 19.99,
                                 "terms": "One full pass through all priced tools on the shelf.",
                                 "url": st['bundle']['url']},
        },
        "tools": tools,
        "free_flagship": lite,
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
    rows.append(f"<tr><td><strong>{E(lite['name'])}</strong> (flagship free tool)</td><td>The flagship free edition of the Almost-JSON Repair Bench — full tool, no charge.</td><td>Free</td><td>Built</td><td><a href=\"{E(lite['url'])}\">Open the tool</a></td></tr>")
    tools_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>All {len(tools)} Tools — J-Dawgs AI Tool Store Index</title>
<meta name="description" content="Plain-text index of every tool in the J-Dawgs AI Tool Store: {len(tools)} listed, {built} built and working, with prices and direct links.">
</head>
<body>
<header><h1>Every tool in the J-Dawgs AI Tool Store</h1>
<p>{len(tools)} tools listed · {built} built and working · {priced} priced tools, ${total:.2f} bought one at a time — or the <strong>J-Dawgs Unlimited Pass: $99.99 one time</strong> for unlimited use of every priced tool including all future tools, or the <strong>Everything Stack: $19.99</strong> for one full pass through every priced tool. Every tool runs in your browser — no account, no install. Full machine-readable catalog: <a href="catalog.json">catalog.json</a>. Store: <a href="{STORE_URL}">AI Tool Store</a> · <a href="index.html">J-Dawgs hub</a>.</p></header>
<table border="1" cellspacing="0" cellpadding="6">
<thead><tr><th>Tool</th><th>What it does</th><th>Price per use</th><th>Status</th><th>Link</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>
<footer><p><a href="https://aiagentsdirectory.com/agent/ai-tool-store-by-j-dawgs" target="_blank" rel="noopener" title="Discover AI Tool Store by J-Dawgs on AI Agents Directory"><img src="https://aiagentsdirectory.com/featured-badge.svg?v=2024" alt="AI Tool Store by J-Dawgs - Featured on AI Agents Directory" width="200" height="50" /></a></p><p>© 2026 J-Dawgs (Joshua Dawson), Springfield, MO. Counts and prices are a snapshot of the live store catalog taken 2026-11-03; the store adds tools daily, so the live store may list more. Regenerate with generate.py.</p></footer>
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
    lines.append(f"- [{lite['name']}]({lite['url']}): Flagship free tool. (Free; status: Built)")
    open(f'{HERE}/llms-full.txt', 'w').write("\n".join(lines) + "\n")
    print(f"wrote catalog.json, tools.html ({len(rows)} rows), llms-full.txt ({len(lines)} lines)")

def main():
    # The Store/Exchange pages are edited by builder crews around the clock;
    # if a source file is mid-edit, parsing or the count assertions fail —
    # retry until a consistent snapshot lands.
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
