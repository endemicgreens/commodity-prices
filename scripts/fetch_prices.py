"""Fetch coffee, pepper and cardamom prices from official sources and save them as JSON.

Sources:
  - Coffee Board of India, Daily Coffee Market Report (PDF, via the Market Info page form)
  - Spices Board of India, daily small cardamom e-auction table
  - Spices Board of India, current market price table (black pepper)

Rules: never invent numbers. If a source cannot be read or a value looks wrong,
keep the last good values, mark that section as stale and record the error.
The script exits with status 1 if any section failed, so GitHub flags the run.
"""
import datetime as dt
import html as htmlmod
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
LATEST = os.path.join(DATA, "prices.json")
HISTORY = os.path.join(DATA, "history.json")
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
UA = "Mozilla/5.0 (compatible; EndemicGreensPriceBot/1.0; +https://endemicgreens.com; connect@endemicgreens.com)"

COFFEE_URL = "https://coffeeboard.gov.in/Market_Info.aspx"
CARDAMOM_URL = "https://www.indianspices.com/marketing/price/domestic/daily-price.html"
PEPPER_URL = "https://www.indianspices.com/marketing/price/domestic/current-market-price.html"


class SourceError(Exception):
    pass


def opener():
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", UA)]
    return op


def num(s):
    s = s.replace(",", "").strip()
    if s in ("", "-"):
        return None
    return float(s)


def to_iso(d, fmt):
    return dt.datetime.strptime(d, fmt).date().isoformat()


def check(cond, msg):
    if not cond:
        raise SourceError(msg)


# ---------------------------------------------------------------- coffee
def coffee_text(op=None, pdf_path=None):
    if pdf_path is None:
        op = op or opener()
        page = op.open(COFFEE_URL, timeout=90).read().decode("utf-8", "replace")
        fields = dict(re.findall(r'<input[^>]+name="(__[A-Z]+)"[^>]*value="([^"]*)"', page))
        check("__VIEWSTATE" in fields, "Coffee Board page has no form state")
        fields["__EVENTTARGET"] = "lbnmarketinfo"
        fields["__EVENTARGUMENT"] = ""
        body = op.open(COFFEE_URL, urllib.parse.urlencode(fields).encode(), timeout=120).read()
        check(body[:4] == b"%PDF", "Coffee Board did not return a PDF")
        fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(fd, "wb") as f:
            f.write(body)
    out = subprocess.run(["pdftotext", "-layout", pdf_path, "-"], capture_output=True, check=True)
    return out.stdout.decode("utf-8", "replace")


MONTH_RE = r"([A-Z][a-z]{2})[a-z]*\.?\s*[–-]?\s*'?(\d{4}|\d{2})\b"


def _month(m):
    y = m.group(2)
    return f"{m.group(1)}-{('20' + y) if len(y) == 2 else y}"


def _date_any(s):
    for fmt in ("%d.%m.%Y", "%d-%m-%Y", "%d/%m/%Y", "%d.%m.%y"):
        try:
            return dt.datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            pass
    raise SourceError(f"Unreadable date {s}")


def parse_coffee(t):
    report_date = None
    m = re.search(r"Daily Coffee Market Report,?\s*(?:\w+day)?,?\s*([A-Z][a-z]+),?\s+(\d{1,2}),?\s+(\d{4})", t)
    if m:
        try:
            report_date = dt.datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y").date().isoformat()
        except ValueError:
            report_date = None

    # Raw coffee prices, Karnataka, Rs per 50 kg
    m = re.search(r"Raw\s+Coffee\s+Prices?\s*\(?\s*Karnataka\s*\)?[^\n]{0,30}?as\s+on\s+(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", t, re.I)
    check(m, "Raw coffee price block not found")
    raw_date = _date_any(m.group(1))
    after = t[m.end():].splitlines()
    vals = None
    for line in after[:8]:
        nums = [x for x in re.findall(r"\d[\d,]*", line) if len(x.replace(",", "")) >= 3]
        if len(nums) >= 8:
            vals = [num(x) for x in nums[:8]]
            break
    check(vals, "Raw coffee price numbers not found")
    names = ["arabica_parchment", "arabica_cherry", "robusta_parchment", "robusta_cherry"]
    raw = {}
    for i, n in enumerate(names):
        lo, hi = vals[2 * i], vals[2 * i + 1]
        check(1000 <= lo <= hi <= 100000, f"Raw price out of range for {n}: {lo}-{hi}")
        raw[n] = {"low": lo, "high": hi}

    # Futures (layout varies a little between years)
    fut_date = None
    m = re.search(r"Futures\s+Prices?\s+(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})", t)
    if m:
        fut_date = _date_any(m.group(1))
    arabica, robusta = [], []
    block = t[m.end():m.end() + 3000] if m else t
    for line in block.splitlines():
        ms = list(re.finditer(MONTH_RE, line))
        ms = [x for x in ms if x.group(1) in ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")]
        if len(ms) != 2:
            continue
        left = re.findall(r"\(?(\d[\d,]*\.?\d*)\)?", line[ms[0].end():ms[1].start()])
        right = re.findall(r"\(?(\d[\d,]*\.?\d*)\)?", line[ms[1].end():])
        if len(left) < 2 or len(right) < 3:
            continue
        a = {"month": _month(ms[0]), "us_cents_lb": num(left[0]), "inr_kg": num(left[1])}
        r = {"month": _month(ms[1]), "usd_tonne": num(right[0]), "us_cents_lb": num(right[1]), "inr_kg": num(right[2])}
        if 50 <= a["us_cents_lb"] <= 1500 and 300 <= r["usd_tonne"] <= 20000:
            arabica.append(a)
            robusta.append(r)
    futures = {"as_on": fut_date, "arabica_new_york": arabica, "robusta_europe": robusta} if arabica else None

    fx = None
    i = t.find("Exchange Rate")
    if i >= 0:
        m = re.search(r"^\s{20,}(\d{2,3}\.\d{2})\s*$", t[i:i + 1500], re.M)
        if m and 50 <= float(m.group(1)) <= 200:
            fx = float(m.group(1))

    return {
        "report_date": report_date or raw_date,
        "raw_karnataka": {"as_on": raw_date, "unit": "Rs per 50 kg", "prices": raw},
        "futures": futures,
        "inr_per_usd": fx,
    }


# ---------------------------------------------------------------- spices
def table_rows(html, after_marker=None):
    if after_marker:
        i = html.find(after_marker)
        check(i >= 0, f"'{after_marker}' not found on page")
        html = html[i:]
    j = html.find("<table")
    check(j >= 0, "No table found")
    k = html.find("</table>", j)
    tb = html[j:k]
    rows = []
    for r in re.findall(r"<tr.*?</tr>", tb, re.S):
        cells = [re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
                 for c in re.findall(r"<t[hd].*?</t[hd]>", r, re.S)]
        rows.append(cells)
    return rows


def fetch_html(url, op=None):
    op = op or opener()
    return op.open(url, timeout=90).read().decode("utf-8", "replace")


def parse_cardamom(page):
    rows = table_rows(page, "Daily Auction Price of Small Cardamom")
    auctions = []
    for c in rows:
        if len(c) >= 9 and re.match(r"\d{2}-[A-Z][a-z]{2}-\d{4}$", c[1]):
            a = {"date": to_iso(c[1], "%d-%b-%Y"), "auctioneer": c[2].title(), "lots": num(c[3]),
                 "arrived_kg": num(c[4]), "sold_kg": num(c[5]),
                 "max": num(c[6]), "min": num(c[7]), "avg": num(c[8])}
            check(a["avg"] and 200 <= a["avg"] <= 15000, f"Cardamom average out of range: {a}")
            auctions.append(a)
    check(auctions, "No cardamom auction rows found")
    latest = max(a["date"] for a in auctions)
    auctions = [a for a in auctions if a["date"] == latest]
    sold = sum(a["sold_kg"] or 0 for a in auctions)
    wavg = round(sum((a["avg"] or 0) * (a["sold_kg"] or 0) for a in auctions) / sold, 2) if sold else None
    return {"date": latest, "unit": "Rs per kg", "auctions": auctions, "weighted_average": wavg}


def pepper_rows(page):
    rows = table_rows(page, "Current Market Price of Key Spices")
    out = []
    for c in rows:
        if len(c) >= 9 and c[1].lower() in ("pepper", "black pepper") and re.match(r"\d{2}-[A-Z][a-z]{2}-\d{4}$", c[0]):
            grade = c[4] if c[4] not in ("-", "") else ""
            if c[2].lower() == "cochin" and grade not in ("Garbled", "Ungarbled"):
                continue  # odd one-off rows (e.g. misfiled grades)
            if c[2].lower() == "cochin" and c[5] != "IPSTA":
                continue  # keep one consistent source for Kochi
            p = {"date": to_iso(c[0], "%d-%b-%Y"), "market": c[2].title(), "state": c[3].title(),
                 "grade": grade, "source": c[5], "min": num(c[6]), "max": num(c[7]), "avg": num(c[8])}
            if not p["avg"] and p["min"] and p["max"]:
                p["avg"] = round((p["min"] + p["max"]) / 2, 2)
            check(p["avg"] and 100 <= p["avg"] <= 5000, f"Pepper price out of range: {p}")
            out.append(p)
    return out


def parse_pepper(page):
    out = pepper_rows(page)
    check(out, "No pepper rows found")
    latest = {}
    for p in out:  # latest row for each market and grade
        k = (p["market"], p["grade"])
        if k not in latest or p["date"] > latest[k]["date"]:
            latest[k] = p
    markets = sorted(latest.values(), key=lambda p: (p["market"] != "Cochin", p["market"], p["grade"]))
    return {"date": max(p["date"] for p in markets), "unit": "Rs per kg", "markets": markets}


# ---------------------------------------------------------------- main
SECTIONS = {
    "coffee": {"source": "Coffee Board of India, Daily Coffee Market Report", "url": COFFEE_URL},
    "cardamom": {"source": "Spices Board of India, daily e-auction prices of small cardamom", "url": CARDAMOM_URL},
    "pepper": {"source": "Spices Board of India, current market price of key spices", "url": PEPPER_URL},
}


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def pepper_key(m):
    return (m["market"] + ("_" + m["grade"] if m["grade"] else "")).lower()


def add_pepper_point(series, m):
    rec = next((r for r in series if r["date"] == m["date"]), None)
    if rec is None:
        rec = {"date": m["date"]}
        series.append(rec)
    rec[pepper_key(m)] = m["avg"]


def update_history(hist, name, data):
    series = hist.setdefault(name, [])
    if name == "coffee":
        key = data["raw_karnataka"]["as_on"]
        rec = {"date": key, **{k: v for k, v in data["raw_karnataka"]["prices"].items()},
               "arabica_ny_front": (data["futures"] or {}).get("arabica_new_york", [{}])[0].get("us_cents_lb"),
               "robusta_eu_front": (data["futures"] or {}).get("robusta_europe", [{}])[0].get("usd_tonne")}
    elif name == "cardamom":
        key = data["date"]
        rec = {"date": key, "weighted_average": data["weighted_average"]}
    else:
        for m in data["markets"]:
            add_pepper_point(series, m)
        series.sort(key=lambda r: r["date"])
        del series[:-500]
        return
    series[:] = [r for r in series if r["date"] != key] + [rec]
    series.sort(key=lambda r: r["date"])
    del series[:-500]


def run(fetchers):
    os.makedirs(DATA, exist_ok=True)
    latest = load(LATEST, {"sections": {}})
    hist = load(HISTORY, {})
    now = dt.datetime.now(IST).isoformat(timespec="minutes")
    failed = []
    for name, fn in fetchers.items():
        sec = latest["sections"].get(name, {})
        sec.update(SECTIONS[name])
        try:
            data = fn()
            sec["data"] = data
            sec["status"] = "ok"
            sec["error"] = None
            sec["last_success"] = now
            update_history(hist, name, data)
        except Exception as e:  # keep last good data
            sec["status"] = "stale" if sec.get("data") else "unavailable"
            sec["error"] = f"{type(e).__name__}: {e}"[:300]
            failed.append(name)
            print(f"[{name}] FAILED: {sec['error']}", file=sys.stderr)
        sec["last_checked"] = now
        latest["sections"][name] = sec
    latest["generated"] = now
    latest["note"] = ("Figures are copied from the official sources named in each section, with their dates. "
                      "Endemic Greens does not adjust, average (except the sold-quantity-weighted cardamom figure) or forecast them.")
    with open(LATEST, "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False, indent=1)
    with open(HISTORY, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, separators=(",", ":"))
    for name in fetchers:
        print(name, latest["sections"][name]["status"])
    return failed


def main():
    op = opener()
    failed = run({
        "coffee": lambda: parse_coffee(coffee_text(op)),
        "cardamom": lambda: parse_cardamom(fetch_html(CARDAMOM_URL, op)),
        "pepper": lambda: parse_pepper(fetch_html(PEPPER_URL, op)),
    })
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
