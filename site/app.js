import {filterDeals, safeUrl} from './deals.js';
const [search, market, category, sort, status, results] = ['search','market','category','sort','status','results'].map(id => document.getElementById(id));
const option = sort.querySelector('[value="price"]');
const make = (tag,text,cls) => { const e = document.createElement(tag); if (text != null) e.textContent = text; if (cls) e.className = cls; return e; };
let snapshot;
function draw() {
  option.disabled = !market.value;
  if (option.disabled && sort.value === 'price') sort.value = 'newest';
  if (!snapshot) return;
  const rows = filterDeals(snapshot.deals,{query:search.value,market:market.value,category:category.value,sort:sort.value});
  const stamp = new Date(snapshot.updated);
  const unavailable = snapshot.unavailable?.length ? ` · Unavailable feeds: ${snapshot.unavailable.join(', ')}` : '';
  status.textContent = `${rows.length ? `${rows.length} ${rows.length === 1 ? 'deal' : 'deals'}` : 'No matching deals'} · Snapshot: ${stamp.toLocaleString()}${unavailable}`;
  results.replaceChildren(...rows.map(d => {
    const card = make('article',null,'card');
    const money = Number.isFinite(d.price) ? `$${d.price.toFixed(2)} ${d.currency === 'CA' ? 'CAD' : 'USD'}${d.inferred ? ' (inferred)' : ''}` : 'Check listing for price';
    const link = make('a','View deal'); link.href = d.url; link.setAttribute('aria-label',`View deal: ${d.title}`);
    card.append(make('p',`${d.category} · ${d.market === 'CA' ? 'Canada' : 'US'} feed`,'note'),make('h2',d.title),make('p',money,'price'),make('p',`${d.source}${d.discount ? ` · ${d.discount}% off stated reference price` : ''}`,'note'),link);
    return card;
  }));
}
for (const el of [search,market,category,sort]) el.addEventListener(el === search ? 'input' : 'change',draw);
draw();
try {
  const res = await fetch('./deals.json',{cache:'no-cache'});
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const doc = await res.json();
  doc.deals = doc.deals.filter(d => typeof d.title === 'string' && safeUrl(d.url));
  for (const name of [...new Set(doc.deals.map(d => d.category))].sort()) category.add(new Option(name,name));
  snapshot = doc;
  draw();
} catch { status.textContent = 'No deal snapshot could be loaded. Try refreshing later.'; }
