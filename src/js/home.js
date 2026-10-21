import { estimate, table, num, fa } from './calc.js';
const $ = id => document.getElementById(id);
/* hero finder -> assistant (prefilled) */
const f = $('finder');
if (f) f.addEventListener('submit', e => {
  e.preventDefault();
  const a = num($('fa').value, 0), room = $('fr').value;
  if (!(a >= 1)) { $('fa').setCustomValidity('متراژ را وارد کنید'); $('fa').reportValidity(); setTimeout(() => $('fa').setCustomValidity(''), 1600); return; }
  location.href = '/assistant/?room=' + encodeURIComponent(room) + '&area=' + encodeURIComponent(a);
});
/* instant estimate */
const m = $('mini');
if (m) m.addEventListener('submit', e => {
  e.preventDefault();
  const A = num($('ma').value, 0), out = $('mout'); out.replaceChildren();
  if (!(A >= 1 && A <= 100000)) { const p = document.createElement('p'); p.className = 'err'; p.textContent = 'متراژ را بین ۱ تا ۱۰۰٬۰۰۰ وارد کنید.'; out.appendChild(p); return; }
  const r = estimate($('ms').value, A, 0, 10);
  const h = document.createElement('p'); h.className = 'lead'; h.textContent = r.title + ' — ' + fa(A) + ' متر مربع (پرت ۱۰٪)'; out.appendChild(h);
  const sc = document.createElement('div'); sc.className = 'scroll'; sc.appendChild(table(r.rows.slice(0, 4))); out.appendChild(sc);
  const a = document.createElement('a'); a.className = 'btn sm'; a.href = '/estimate/?area=' + encodeURIComponent(A) + '&sys=' + encodeURIComponent($('ms').value); a.textContent = 'برآورد کامل و ارسال برای کارشناس'; a.style.marginTop = '14px'; out.appendChild(a);
});
/* lazy-load the 3D hero (three.js) after the page has settled, so it never competes with critical
   render/LCP weight. */
if ($('hero3d')) {
  const startHero3D = () => { import('/assets/js/hero3d.js').catch(() => { }); };
  const idle = cb => (window.requestIdleCallback ? requestIdleCallback(cb, { timeout: 1500 }) : setTimeout(cb, 200));
  if (document.readyState === 'complete') idle(startHero3D); else addEventListener('load', () => idle(startHero3D));
}
