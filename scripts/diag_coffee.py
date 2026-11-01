"""One-off: save the text of one Coffee Board report per month, to adapt the reader to older layouts."""
import os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_prices as fp
import backfill as bf

op = fp.opener()
base = "https://coffeeboard.gov.in/Market_Info_Archives.aspx"
month_url = "https://coffeeboard.gov.in/Archives_Month.aspx"
out = []
for y, m in [(2025, 11), (2026, 2), (2026, 6), (2026, 9)]:
    page = op.open(base, timeout=90).read().decode("utf-8", "replace")
    html = bf.post(op, base, bf.form_fields(page), f"GridView1$ctl{m + 1:02d}$LinkButton{y}").read().decode("utf-8", "replace")
    days = re.findall(r"__doPostBack\(&#39;(DataList1\$ctl\d+\$LinkButton1)&#39;,&#39;&#39;\)\"[^>]*>\s*(\d{4},\w{3},\d{2})", html)
    tgt, label = days[len(days) // 2]
    body = bf.post(op, month_url, bf.form_fields(html), tgt).read()
    fd, path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(fd, "wb") as f:
        f.write(body)
    t = fp.coffee_text(pdf_path=path)
    out.append(f"===== {label} =====\n{t[:6000]}")
open(os.path.join(fp.DATA, "diag_coffee.txt"), "w", encoding="utf-8").write("\n".join(out))
