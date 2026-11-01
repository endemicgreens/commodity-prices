"""One-off: load about a year of history into data/history.json.

Coffee: Coffee Board market-report archive (month page -> day page -> PDF).
Pepper: Spices Board current-market-price table filtered by date.
Cardamom: Spices Board small-cardamom auction table, page by page.
Days that cannot be read are skipped and listed in data/backfill_log.txt.
"""
import datetime as dt
import os
import re
import sys
import tempfile
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_prices as fp  # noqa: E402

START = dt.date.today() - dt.timedelta(days=380)
LOG = []
SAMPLES = [0]


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def form_fields(html):
    return dict(re.findall(r'<input[^>]+name="(__[A-Z]+)"[^>]*value="([^"]*)"', html))


def post(op, url, fields, target):
    data = dict(fields)
    data["__EVENTTARGET"] = target
    data["__EVENTARGUMENT"] = ""
    return op.open(url, urllib.parse.urlencode(data).encode(), timeout=120)


def coffee(hist):
    op = fp.opener()
    base = "https://coffeeboard.gov.in/Market_Info_Archives.aspx"
    month_url = "https://coffeeboard.gov.in/Archives_Month.aspx"
    d = dt.date(START.year, START.month, 1)
    today = dt.date.today()
    n_ok = 0
    while d <= today:
        try:
            page = op.open(base, timeout=90).read().decode("utf-8", "replace")
            target = f"GridView1$ctl{d.month + 1:02d}$LinkButton{d.year}"
            check_html = post(op, base, form_fields(page), target).read().decode("utf-8", "replace")
            days = re.findall(r"__doPostBack\(&#39;(DataList1\$ctl\d+\$LinkButton1)&#39;,&#39;&#39;\)\"[^>]*>\s*(\d{4},\w{3},\d{2})", check_html)
            if not days:
                days = re.findall(r"__doPostBack\('(DataList1\$ctl\d+\$LinkButton1)',''\)\"[^>]*>\s*(\d{4},\w{3},\d{2})", check_html)
            log("coffee month", d.strftime("%Y-%m"), "days", len(days))
            fields = form_fields(check_html)
            for tgt, label in days:
                try:
                    r = post(op, month_url, fields, tgt)
                    body = r.read()
                    if body[:4] != b"%PDF":
                        log("  no pdf", label)
                        continue
                    fd, path = tempfile.mkstemp(suffix=".pdf")
                    with os.fdopen(fd, "wb") as f:
                        f.write(body)
                    data = fp.parse_coffee(fp.coffee_text(pdf_path=path))
                    os.remove(path)
                    fp.update_history(hist, "coffee", data)
                    n_ok += 1
                except Exception as e:
                    log("  skip", label, type(e).__name__, str(e)[:120])
                    if SAMPLES[0] < 3:
                        SAMPLES[0] += 1
                        try:
                            log("SAMPLE TEXT", label, fp.coffee_text(pdf_path=path)[:5000])
                        except Exception:
                            pass
                time.sleep(0.5)
        except Exception as e:
            log("coffee month failed", d, type(e).__name__, str(e)[:150])
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    log("coffee reports read:", n_ok)


def pepper(hist):
    q = urllib.parse.urlencode({"dateFrom": START.isoformat(), "dateTo": dt.date.today().isoformat()})
    page = fp.fetch_html(fp.PEPPER_URL + "?" + q)
    rows = fp.pepper_rows(page)
    series = hist.setdefault("pepper", [])
    for m in rows:
        fp.add_pepper_point(series, m)
    series.sort(key=lambda r: r["date"])
    log("pepper rows:", len(rows), "dates:", len(series))


def cardamom(hist):
    url = "https://www.indianspices.com/marketing/price/domestic/daily-price-small.html"
    by_date = {}
    for page_no in range(1, 200):
        try:
            page = fp.fetch_html(url + (f"?page={page_no}" if page_no > 1 else ""))
            rows = [[re.sub(r"\s+", " ", fp.htmlmod.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
                     for c in re.findall(r"<t[hd].*?</t[hd]>", r, re.S)]
                    for r in re.findall(r"<tr.*?</tr>", page, re.S)]
        except Exception as e:
            log("cardamom page failed", page_no, type(e).__name__, str(e)[:120])
            continue
        dates = []
        for c in rows:
            if len(c) >= 9 and re.match(r"\d{2}-[A-Z][a-z]{2}-\d{4}$", c[1]):
                day = fp.to_iso(c[1], "%d-%b-%Y")
                dates.append(day)
                sold, avg = fp.num(c[5]) or 0, fp.num(c[8])
                if avg and 200 <= avg <= 15000:
                    by_date.setdefault(day, []).append((sold, avg))
        if not dates or min(dates) < START.isoformat():
            break
        time.sleep(0.5)
    series = hist.setdefault("cardamom", [])
    have = {r["date"] for r in series}
    for day, xs in by_date.items():
        if day < START.isoformat() or day in have:
            continue
        sold = sum(s for s, _ in xs)
        w = round(sum(s * a for s, a in xs) / sold, 2) if sold else round(sum(a for _, a in xs) / len(xs), 2)
        series.append({"date": day, "weighted_average": w})
    series.sort(key=lambda r: r["date"])
    log("cardamom dates:", len(series), "pages read:", page_no)


def merge(path):
    """Merge a backfill file into the current history (newer job data wins on the same date)."""
    import json
    new = fp.load(path, {})
    hist = fp.load(fp.HISTORY, {})
    for k, series in new.items():
        cur = {r["date"]: r for r in hist.get(k, [])}
        for r in series:
            if r["date"] in cur:
                merged = dict(r)
                merged.update(cur[r["date"]])
                cur[r["date"]] = merged
            else:
                cur[r["date"]] = r
        hist[k] = sorted(cur.values(), key=lambda r: r["date"])[-500:]
    with open(fp.HISTORY, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, separators=(",", ":"))
    print({k: len(v) for k, v in hist.items()})


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--merge":
        return merge(sys.argv[2])
    hist = {}
    for name, fn in (("pepper", pepper), ("cardamom", cardamom), ("coffee", coffee)):
        try:
            fn(hist)
        except Exception as e:
            log(name, "FAILED", type(e).__name__, str(e)[:200])
    for k in hist:
        hist[k] = hist[k][-500:]
    import json
    with open(os.path.join(fp.DATA, "history_backfill.json"), "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(fp.DATA, "backfill_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
