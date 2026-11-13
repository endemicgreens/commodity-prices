"""One-off probe (13 Nov 2026): can a GitHub runner read official areca (adike) price sources, and in what shape?
Prints status, final URL, title, table text and useful links for each candidate. Reads only; writes nothing."""
import html, http.cookiejar, re, sys, urllib.parse, urllib.request

UA = "Mozilla/5.0 (compatible; EndemicGreensPriceBot/1.0; +https://endemicgreens.com; connect@endemicgreens.com)"
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
op.addheaders = [("User-Agent", UA), ("Accept-Language", "en-IN,en;q=0.8")]

def get(url, data=None, show_tables=True, links=None, limit=6000):
    print("\n" + "=" * 100 + "\nURL " + url, flush=True)
    try:
        r = op.open(url, data, timeout=60)
        raw = r.read()
        body = raw.decode("utf-8", "replace")
        print("STATUS", r.status, "FINAL", r.geturl(), "BYTES", len(raw), "TYPE", r.headers.get("content-type"))
    except Exception as e:
        print("ERROR", type(e).__name__, e)
        try:
            print("BODY", e.read()[:800].decode("utf-8", "replace"))
        except Exception:
            pass
        return ""
    t = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    print("TITLE", html.unescape(t.group(1)).strip()[:200] if t else None)
    if body.lstrip().startswith("{") or body.lstrip().startswith("["):
        print("JSON", body[:1500])
        return body
    if show_tables:
        tables = re.findall(r"<table.*?</table>", body, re.S | re.I)
        print("TABLES", len(tables))
        for i, tb in enumerate(tables[:6]):
            rows = re.findall(r"<tr.*?</tr>", tb, re.S | re.I)
            print(f"-- table {i}: {len(rows)} rows")
            for row in rows[:45]:
                cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S | re.I)]
                if any(cells):
                    print("   | " + " | ".join(cells)[:300])
    if links:
        hrefs = sorted(set(html.unescape(h) for h in re.findall(r'href=["\']([^"\']+)["\']', body, re.I)))
        hit = [h for h in hrefs if re.search(links, h, re.I)]
        print("LINKS", len(hrefs), "matching", len(hit))
        for h in hit[:60]:
            print("   ", h)
    if not show_tables and not links:
        txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", body, flags=re.S | re.I)))
        print("TEXT", txt[:limit])
    return body

# 1. Krishi Marata Vahini (Karnataka State Agricultural Marketing Board), old and new addresses
home = get("https://www.krishimaratavahini.kar.nic.in/", show_tables=False, links=r"Rep|Price|Comm|Daily|Market|aspx")
q = urllib.parse.urlencode({"CommCode": "140", "CommName": "Arecanut / ಅಡಿಕೆ", "Date": "12/11/2026", "Rep": "Com", "VarCode": "1", "VarName": "Red / ಕೆಂಪು"})
rep = get("https://www.krishimaratavahini.kar.nic.in/MainPage/DailyMrktPriceRep2.aspx?" + q, links=r"CommCode=140|VarCode|Rep=")
# follow other arecanut variety links found on the report page, for the same date
seen = set()
for h in re.findall(r'href=["\']([^"\']*CommCode=140[^"\']*)["\']', rep or "", re.I):
    h = html.unescape(h)
    v = re.search(r"VarCode=(\d+)", h)
    if not v or v.group(1) in seen or v.group(1) == "1":
        continue
    seen.add(v.group(1))
    if len(seen) > 14:
        break
    get(urllib.parse.urljoin("https://www.krishimaratavahini.kar.nic.in/MainPage/", h))
# market-wise report for a Malnad market if such links exist
for h in re.findall(r'href=["\']([^"\']*Rep=Mkt[^"\']*)["\']', rep or "", re.I)[:3]:
    get(urllib.parse.urljoin("https://www.krishimaratavahini.kar.nic.in/MainPage/", html.unescape(h)))
get("https://krama.karnataka.gov.in/", show_tables=False, links=r"Rep|Price|Comm|Daily|Market|report")

# 2. Agmarknet (Directorate of Marketing and Inspection): new portal, and the old report address
ag = get("https://agmarknet.gov.in/", show_tables=False, links=r"price|report|api|commodity|\.js")
for src in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', ag or "", re.I)[:4]:
    js = get(urllib.parse.urljoin("https://agmarknet.gov.in/", src), show_tables=False, links=None, limit=0)
    found = sorted(set(re.findall(r'["\'`](https?://[^"\'`\s]{6,120}|/api/[^"\'`\s]{2,120}|/v\d/[^"\'`\s]{2,120})["\'`]', js or "")))
    print("JS URLS", len(found))
    for f in found[:80]:
        print("   ", f)
get("https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity=140&Tx_State=KK&Tx_District=0&Tx_Market=0&DateFrom=12-Nov-2026&DateTo=12-Nov-2026&Fr_Date=12-Nov-2026&To_Date=12-Nov-2026&Tx_Trend=0&Tx_CommodityHead=Arecanut(Betelnut/Supari)&Tx_StateHead=Karnataka&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--")

# 3. data.gov.in Agmarknet APIs, without a key (only to see whether each resource exists)
for rid in ["9ef84268-d588-465a-a308-a864a43d0070", "35985678-0d79-46b4-9ed6-6f13308a1d24"]:
    get(f"https://api.data.gov.in/resource/{rid}?format=json&limit=1", show_tables=False)
print("\nDONE")
