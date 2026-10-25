import { estimate, table, num, fmt, digits } from './calc.js';
const $ = id => document.getElementById(id);
const f = $('ef');
if (f) {
  const lang = document.documentElement.lang === 'en' ? 'en' : 'fa';
  const q = new URLSearchParams(location.search);
  if (q.get('area') && /^[\d.]{1,9}$/.test(q.get('area'))) $('area').value = q.get('area');
  if (q.get('sys') === 'grid') $('sys').value = 'grid';
  const sync = () => document.querySelectorAll('[data-for]').forEach(e => { e.hidden = !e.dataset.for.split(' ').includes($('sys').value); });
  $('sys').addEventListener('change', sync); sync();
  const run = () => {
    const A = num($('area').value, 0), err = $('area-e'); err.textContent = '';
    if (!(A >= 1 && A <= 100000)) { err.textContent = lang === 'en' ? 'Enter an area between 1 and 100,000 m².' : 'متراژ را بین ۱ تا ۱۰۰٬۰۰۰ متر مربع وارد کنید.'; return; }
    const s = $('sys').value, r = estimate(s, A, num($('perim').value, 0), Math.min(Math.max(num($('waste').value, 10), 0), 50), { sp: num($('sp').value, .6), cs: num($('cs').value, 1.2), hs: num($('hs').value, 1.2) }, lang);
    const body = $('tb'); body.replaceChildren(); r.rows.forEach(row => { const tr = body.insertRow(); row.forEach((c, i) => { const td = tr.insertCell(); td.textContent = (i === 1 && typeof c === 'number') ? fmt(c, lang) : c; }); });
    $('sum').textContent = lang === 'en'
      ? r.title + ' — ' + fmt(A, lang) + ' m², perimeter ' + fmt(r.P, lang) + ' m, waste ' + fmt(Math.round((r.w - 1) * 100), lang) + '%'
      : r.title + ' — ' + fmt(A, lang) + ' متر مربع، محیط ' + fmt(r.P, lang) + ' متر، پرت ' + fmt(Math.round((r.w - 1) * 100), lang) + '٪';
    const txt = r.rows.map(x => x[0] + ': ' + fmt(x[1], lang) + ' ' + x[2]).join(lang === 'en' ? '; ' : '؛ ');
    const noteLabel = lang === 'en' ? 'Initial estimate from the site — ' : 'برآورد اولیه از سایت — ';
    $('qlink').href = (lang === 'en' ? '/en/quote/' : '/quote/') + '?p=' + (s === 'grid' ? 'grid' : 'drywall') + '&area=' + encodeURIComponent(A) + '&note=' + encodeURIComponent(noteLabel + r.title + ' — ' + txt);
    $('res').hidden = false; $('res').scrollIntoView({ behavior: 'smooth', block: 'start' });
  };
  f.addEventListener('submit', e => { e.preventDefault(); run(); });
  if ($('area').value) run();
}
