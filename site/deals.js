export function filterDeals(rows, {query, market, category, sort}) {
  const terms = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  const matches = rows.filter(d => (!market || d.market === market) && (!category || d.category === category) && terms.every(term => `${d.title} ${d.category} ${d.source}`.toLowerCase().includes(term)));
  const price = d => Number.isFinite(d.price) && d.currency === market ? d.price : Infinity;
  const time = d => Date.parse(d.published) || 0;
  return matches.sort((a,b) => (sort === 'price' && market ? price(a)-price(b) : sort === 'discount' ? (b.discount || 0)-(a.discount || 0) : 0) || time(b)-time(a));
}
export function safeUrl(value) {
  try { const url = new URL(value); return url.protocol === 'https:' && !url.username && !url.password ? url.href : null; } catch { return null; }
}
