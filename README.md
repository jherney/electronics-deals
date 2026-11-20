# Electronics Deals

A standalone site for browsing community-posted electronics sales. Search by keyword, filter by category or feed market, and sort by newest, biggest explicitly stated discount, or lowest price within one market. No paid API keys or third-party Python packages are required.

## Publish

In this repository, select **Settings → Pages → Build and deployment → Source → GitHub Actions**. Then open **Actions → Refresh and publish deals → Run workflow**. The workflow builds and publishes a fresh snapshot on pushes to `main`, every three hours when GitHub runs the schedule, and on demand. The deployed path is shown in the workflow's deployment result.

## Preview locally

```sh
python3 scripts/update_deals.py
python3 -m http.server 8000 --directory site
```

Open `http://localhost:8000`. The generated snapshot is intentionally ignored by Git.

## Modules and limitations

- `scripts/update_deals.py`: source configuration, RSS/Atom parsing, categorization and price extraction. Add feed adapters in `SOURCES` and category patterns in `CATEGORIES`.
- `site/deals.js`: filtering, ranking and link validation.
- `site/app.js`: snapshot loading and browser rendering.
- `site/index.html` and `site/styles.css`: layout and responsive presentation.

Canada uses RedFlagDeals; US uses Slickdeals. The page reports unavailable feeds. If both feeds fail, the workflow does not replace the previous deployment. Unmarked dollar currencies are inferred from the feed; price sorting does not compare CAD with USD. A discount is relative to a reference price stated in the title, not an independently verified historical low. Coverage depends on feed availability, and the site does not verify inventory, shipping or seller claims.
