import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from update_deals import SOURCES, fetch

FEEDS = (*SOURCES,
    ('Newegg', 'US', 'https://www.newegg.com/d/Product/RSS?Submit=RSSDailyDeals'),
    ('9to5Toys', 'US', 'https://9to5toys.com/feed/'),
)
MERCHANTS = {
    'Amazon': (r'amazon(?:\.ca|\.com)?', ('amazon.ca', 'amazon.com')),
    'Best Buy': (r'best\s*buy(?:\.ca|\.com)?', ('bestbuy.ca', 'bestbuy.com')),
    'Walmart': (r'walmart(?:\.ca|\.com)?', ('walmart.ca', 'walmart.com')),
    'Newegg': (r'newegg(?:\.ca|\.com)?', ('newegg.ca', 'newegg.com')),
    'Canada Computers': (r'canada\s+computers', ('canadacomputers.com',)),
    'Memory Express': (r'memory\s+express', ('memoryexpress.com',)),
    'Costco': (r'costco(?:\.ca|\.com)?', ('costco.ca', 'costco.com')),
    'Staples': (r'staples(?:\.ca|\.com)?', ('staples.ca', 'staples.com')),
    'B&H Photo': (r'b&h(?:\s+photo)?', ('bhphotovideo.com',)),
    'Target': (r'target(?:\.com)?', ('target.com',)),
}


def merchant_for(deal):
    host = urlsplit(deal['url']).hostname or ''
    for name, (_, domains) in MERCHANTS.items():
        if any(host == domain or host.endswith('.' + domain) for domain in domains):
            return name
    matches = [name for name, (pattern, _) in MERCHANTS.items() if re.search(r'(?<!\w)(?:' + pattern + r')(?!\w)', deal['title'], re.I)]
    return matches[0] if len(matches) == 1 else None


def main():
    now = datetime.now(timezone.utc)
    unavailable, rows = [], {}
    for source, market, address in FEEDS:
        try:
            deals = fetch(source, market, address, now)
        except Exception as error:
            unavailable.append(source)
            print(f'{source}: {error}')
            continue
        print(f'{source}: {len(deals)} matching electronics items')
        for deal in deals:
            deal['retailer'] = merchant_for(deal)
            if source == '9to5Toys' and re.search(r'\b(?:roundup|lineup|from|up to|all live)\b', deal['title'], re.I):
                deal.update(price=None, discount=None)
            rows.setdefault((market, deal['url']), deal)
    if not rows:
        raise SystemExit('No electronics deals returned; keeping any previous deployment in place.')
    output = Path(__file__).resolve().parents[1] / 'site' / 'deals.json'
    output.write_text(json.dumps(dict(updated=now.isoformat(), unavailable=unavailable, deals=list(rows.values())), ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    main()
