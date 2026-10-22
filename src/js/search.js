import { build, search } from './ir.js';
const inp = document.getElementById('sq'), out = document.getElementById('sr');
if (inp && out) {
  const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
  let ix = null;
  const ready = fetch('/assets/data/search.json').then(r => r.json()).then(d => { ix = build(d); });
  const run = async () => {
    await ready; out.replaceChildren(); const q = inp.value.trim(); if (!q) return;
    const r = search(ix, q, 20);
    if (!r.length) {
      const latin = (q.match(/[A-Za-z]/g) || []).length / Math.max(1, q.replace(/[^A-Za-z؀-ۿ]/g, '').length);
      out.appendChild(el('p', 'lead', 'نتیجه‌ای پیدا نشد. از «دستیار هوشمند» بپرسید یا با ۰۲۱-۸۸۵۰۷۵۸۵ تماس بگیرید.'));
      if (latin > 0.6) { const a = el('a', 'card pad', ''); a.href = '/en/'; a.style.display = 'block'; a.style.marginTop = '8px'; a.textContent = 'English homepage →'; out.appendChild(a); }
      return;
    }
    r.forEach(x => { const a = el('a', 'card pad'); a.href = x.d.u; a.style.display = 'block'; a.style.marginBottom = '12px'; a.appendChild(el('h3', '', x.d.t)); a.appendChild(el('p', '', x.d.x.slice(0, 160) + '…')); a.appendChild(el('small', '', x.d.g)); out.appendChild(a); });
  };
  const q0 = new URLSearchParams(location.search).get('q'); if (q0) { inp.value = q0; run(); }
  inp.addEventListener('input', run);
  inp.form.addEventListener('submit', e => { e.preventDefault(); run(); });
}
