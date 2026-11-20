import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

SOURCES = (
    ('RedFlagDeals', 'CA', 'https://forums.redflagdeals.com/feed/forum/9'),
    ('Slickdeals', 'US', 'https://slickdeals.net/newsearch.php?mode=frontpage&searcharea=deals&searchin=first&rss=1'),
)
CATEGORIES = (
    ('Gaming', r'ps5|playstation|xbox|nintendo|steam deck|gaming headset|game controller'),
    ('Audio', r'headphones?|earbuds?|speakers?|soundbars?|headsets?|microphones?'),
    ('Computers', r'laptops?|chromebooks?|monitors?|ssds?|nvme|graphics cards?|geforce|radeon|keyboards?|mice|mini pcs?|routers?'),
    ('Mobile', r'iphones?|ipads?|tablets?|smartphones?|smartwatches?|pixel \d+|galaxy [as]\d+'),
    ('TV & Home Theater', r'tvs?|televisions?|projectors?|roku|chromecast|streaming sticks?'),
    ('Accessories', r'chargers?|power banks?|usb hubs?|webcams?|docking stations?|dash cams?'),
)
MONEY = r'(?:(CA|US)\s*)?\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)(?![\d.,])'
REFERENCE = re.compile(r'\b(?:was|regular price|list price)\s*:?\s*' + MONEY, re.I)


def prices(title, market):
    hits = list(re.finditer(MONEY, title, re.I))
    ref = REFERENCE.search(title)
    if not hits or len(hits) > 2 or (len(hits) == 2 and (not ref or hits[1].start() < ref.start())):
        return None, market, True, None
    first = hits[0]
    code = first[1].upper() if first[1] else market
    if (ref and ref.start() <= first.start()) or re.search(r'\b(?:save|off|coupon|shipping|gift card)\s*(?::\s*)?$', title[:first.start()], re.I) or re.match(r'\s*(?:off\b|/)', title[first.end():], re.I):
        return None, code, not first[1], None
    value = float(first[2].replace(',', ''))
    if not 0 < value < 100000:
        return None, code, not first[1], None
    old = float(ref[2].replace(',', '')) if ref and (ref[1].upper() if ref[1] else market) == code else 0
    return value, code, not first[1], round(100 * (1 - value / old)) if value < old else None


def date_for(text):
    try:
        date = datetime.fromisoformat(text.replace('Z', '+00:00'))
    except ValueError:
        try:
            date = parsedate_to_datetime(text)
        except (ValueError, TypeError, OverflowError):
            return None
    return date.replace(tzinfo=timezone.utc) if date.tzinfo is None else date.astimezone(timezone.utc)


def fetch(source, market, address, now):
    req = Request(address, headers={'User-Agent': 'ElectronicsDeals Feed Reader/1.0', 'Accept': 'application/rss+xml, application/atom+xml, application/xml'})
    with urlopen(req, timeout=20) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError('Feed too large')
    root = ET.fromstring(raw)
    for node in root.iter():
        node.tag = node.tag.rsplit('}', 1)[-1]
    if root.tag not in {'rss', 'RDF', 'feed'}:
        raise ValueError('Not an RSS or Atom feed')
    rows = []
    for item in (root.findall('.//item') + root.findall('./entry'))[:100]:
        title = ' '.join((item.findtext('title') or '').split())
        category = next((name for name, pattern in CATEGORIES if re.search(r'\b(?:' + pattern + r')\b', title, re.I)), None)
        if not category:
            continue
        link = next((node for node in item.findall('link') if node.get('rel', 'alternate') == 'alternate'), None)
        href = (link.get('href') or link.text or '').strip() if link is not None else ''
        if not href:
            continue
        url = urljoin(address, href)
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            continue
        date = date_for(item.findtext('pubDate') or item.findtext('published') or item.findtext('updated') or '')
        if date and date < now - timedelta(days=7):
            continue
        price, currency, inferred, discount = prices(title, market)
        rows.append(dict(title=title, category=category, source=source, market=market, url=url, price=price, currency=currency, inferred=inferred, discount=discount, published=date.isoformat() if date else None))
    return rows


def main():
    now = datetime.now(timezone.utc)
    unavailable, rows = [], {}
    for source, market, address in SOURCES:
        try:
            for deal in fetch(source, market, address, now):
                rows.setdefault((market, deal['url']), deal)
        except Exception as error:
            print(f'{source}: {error}')
            unavailable.append(source)
    if len(unavailable) == len(SOURCES):
        raise SystemExit('No feeds could be refreshed; refusing to deploy an empty replacement.')
    path = Path(__file__).resolve().parents[1] / 'site' / 'deals.json'
    path.write_text(json.dumps(dict(updated=now.isoformat(), unavailable=unavailable, deals=list(rows.values())), ensure_ascii=False), encoding='utf-8')
    print(f'Wrote {len(rows)} electronics deals')


if __name__ == '__main__':
    main()
