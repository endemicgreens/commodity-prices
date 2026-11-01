# commodity-prices

Daily coffee, pepper and cardamom prices copied from official sources (Coffee Board of India, Spices Board of India) for endemicgreens.com.

- `scripts/fetch_prices.py` reads the sources. If a source cannot be read, it keeps the last good figures and marks them stale.
- `.github/workflows/prices.yml` runs at 09:00 and 18:00 IST, saves `data/` and publishes it with GitHub Pages.
- Published data: `prices.json` (latest) and `history.json` (one record per report date).
