"""One-off check: can a GitHub runner download the Coffee Board daily report and the Spices Board weekly?"""
import datetime as dt, re, sys, urllib.parse, urllib.request, http.cookiejar, os

os.makedirs("out", exist_ok=True)
jar = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
op.addheaders = [("User-Agent", "Mozilla/5.0 (EndemicGreens price bot; connect@endemicgreens.com)")]

def log(*a): print(*a, flush=True)

# Coffee Board: page has an ASP.NET postback button for the PDF.
try:
    url = "https://coffeeboard.gov.in/Market_Info.aspx"
    html = op.open(url, timeout=60).read().decode("utf-8", "replace")
    log("coffeeboard page bytes", len(html))
    fields = dict(re.findall(r'<input[^>]+name="(__[A-Z]+)"[^>]*value="([^"]*)"', html))
    log("hidden fields", list(fields))
    m = re.search(r"Daily Coffee Market Report.{0,400}?(\w+day,?\s+\w+\s+\d{1,2},\s+\d{4})", html, re.S)
    log("report date on page", m.group(1) if m else None)
    data = {k: v for k, v in fields.items()}
    data["__EVENTTARGET"] = "lbnmarketinfo"
    data["__EVENTARGUMENT"] = ""
    r = op.open(url, urllib.parse.urlencode(data).encode(), timeout=120)
    body = r.read()
    log("coffeeboard postback", r.status, r.headers.get("Content-Type"), r.headers.get("Content-Disposition"), len(body))
    open("out/coffeeboard_daily.pdf" if body[:4] == b"%PDF" else "out/coffeeboard_response.html", "wb").write(body)
except Exception as e:
    log("COFFEEBOARD ERROR", repr(e))

# Spices Board: weekly PDF, Saturdays; try recent dates and both path variants/spellings.
got = False
today = dt.date.today()
for back in range(0, 21):
    d = today - dt.timedelta(days=back)
    ds = d.strftime("%d.%m.%Y")
    for path in ("sites/default/files", "indianspices/sites/default/files"):
        for name in ("SPICE MARKET", "SPICES MARKET", "SPICEMARKET"):
            u = f"https://indianspices.com/{path}/{urllib.parse.quote(ds + ' ' + name + '.pdf')}"
            try:
                r = op.open(u, timeout=60)
                b = r.read()
                if b[:4] == b"%PDF":
                    log("spices weekly found", u, len(b))
                    open("out/spices_weekly.pdf", "wb").write(b)
                    got = True
                    break
            except Exception as e:
                pass
        if got: break
    if got: break
if not got:
    log("SPICES: no weekly PDF found in last 21 days")
