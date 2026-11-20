# Electronics Deals

A standalone, key-free electronics deal finder. Search titles and recognized retailer names; filter by feed market or category; sort by newest, stated discount, or price within one market.

## Publish

Set Settings → Pages → Build and deployment → Source to GitHub Actions. Then run Actions → Refresh and publish deals → Run workflow. It also runs every three hours and on pushes to `main`.

## Preview locally

```sh
python3 scripts/refresh.py
python3 -m http.server 8000 --directory site
```

Open http://localhost:8000. The generated snapshot is not committed.

## Sources and modules

- `scripts/refresh.py` assembles the feeds and recognizes merchant names in titles or link domains. Add future feeds in `FEEDS`.
- `scripts/update_deals.py` implements RSS/Atom parsing, category tagging and title-based pricing.
- `site/deals.js` handles filtering and ranking, and `site/app.js` renders each snapshot.

Canada currently relies on RedFlagDeals. The US sources are Slickdeals, Newegg's official Daily Deals RSS, and 9to5Toys. Merchant recognition is not a direct integration with every recognized store: editorial and community links may go to a deal post instead of a product page. Source counts appear in the build log, and unavailable feeds appear on the site. When no electronics deals are collected, the workflow does not publish an empty replacement. Prices and discounts are as stated in the feeds, not independently verified; confirm shipping, currency and stock on the listing.
