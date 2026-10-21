/* Tiny Persian-aware retrieval (BM25-lite) shared by the site search and the assistant. */
const ZW = /[‌‍‎‏]/g;
export function norm(s) {
  return String(s || '').toLowerCase().replace(/ي/g, 'ی').replace(/ك/g, 'ک').replace(/ة/g, 'ه').replace(ZW, ' ')
    .replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d)).replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d))
    .replace(/[^\p{L}\p{N}\s.]/gu, ' ').replace(/\s+/g, ' ').trim();
}
const STOP = new Set('و در به از که را این آن با برای یا هم است هست می چه چی چیه چیست چند چطور چطوره چگونه چقدر چقدره کدام های ها ای یک بر تا اگر آیا من ما شما بود شود کرد کنید کنم'.split(' '));
export function tokens(s) { return norm(s).split(' ').filter(t => t && !STOP.has(t) && (t.length > 1 || /\d/.test(t))); }
const stem = t => t.replace(/(هایی|ها|های|ات|ان)$/,'').replace(/(ی|ه)$/, '');
/* bounded edit distance, for real typos (prefix matching alone misses a transposed/missing/extra letter) */
function editDist(a, b) {
  if (Math.abs(a.length - b.length) > 2) return 99;
  const m = a.length, n = b.length, dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++) for (let j = 1; j <= n; j++)
    dp[i][j] = a[i - 1] === b[j - 1] ? dp[i - 1][j - 1] : 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
  return dp[m][n];
}
export function build(docs) {
  const df = new Map(), idx = docs.map(d => {
    const tf = new Map(), title = new Set(tokens(d.t).map(stem));
    tokens(d.t + ' ' + (d.k || '') + ' ' + d.x).forEach(w => { w = stem(w); tf.set(w, (tf.get(w) || 0) + 1); });
    tf.forEach((_, w) => df.set(w, (df.get(w) || 0) + 1));
    const len = [...tf.values()].reduce((a, b) => a + b, 0);
    return { d, tf, title, len };
  });
  const N = docs.length, avg = idx.reduce((a, b) => a + b.len, 0) / Math.max(1, N);
  return { idx, df, N, avg };
}
export function search(ix, q, limit = 8) {
  const qs = tokens(q).map(stem); if (!qs.length) return [];
  const out = [];
  for (const e of ix.idx) {
    let s = 0, hit = 0;
    for (const w of qs) {
      let f = e.tf.get(w) || 0;
      if (!f) { for (const [k, v] of e.tf) if (k.length > 2 && (k.startsWith(w) || w.startsWith(k)) && Math.abs(k.length - w.length) < 4) { f = v * .5; break; } }
      if (!f && w.length >= 4) { const maxD = w.length >= 7 ? 2 : 1; for (const [k, v] of e.tf) if (k.length >= 4 && editDist(w, k) <= maxD) { f = v * .4; break; } }
      if (!f) continue; hit++;
      const idf = Math.log(1 + (ix.N - (ix.df.get(w) || 0) + .5) / ((ix.df.get(w) || 0) + .5));
      s += idf * (f * 2.2) / (f + 1.2 * (.25 + .75 * e.len / ix.avg));
      if (e.title.has(w)) s += idf * 1.4;
    }
    if (hit) out.push({ d: e.d, s: s * (hit / qs.length), hit });
  }
  return out.sort((a, b) => b.s - a.s).slice(0, limit);
}
