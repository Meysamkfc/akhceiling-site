/* Shared UI: header, menu, reveal, counters, lightbox, lazy video, search palette, anonymous page counter.
   Written without innerHTML so it works under CSP "require-trusted-types-for 'script'". */
import { build, search, norm } from './ir.js';
import Lenis from 'lenis';
const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };

/* gentle, native-feeling inertia scroll; off entirely under prefers-reduced-motion. the mobile nav
   overlay, lightbox and search palette all freeze page scroll while open (see their `lock(true/false)`
   calls below) — Lenis needs to be told to stop/start alongside body.style.overflow, not just have
   the CSS fought over it, and a refcount keeps two overlays opening at once from unlocking too early. */
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
let lenis = null;
if (!reduceMotion) {
  lenis = new Lenis({ duration: 1.0, easing: t => 1 - Math.pow(1 - t, 3), smoothWheel: true, syncTouch: false });
  const raf = time => { lenis.raf(time); requestAnimationFrame(raf); };
  requestAnimationFrame(raf);
}
let lockCount = 0;
const lock = on => {
  lockCount = Math.max(0, lockCount + (on ? 1 : -1));
  document.body.style.overflow = lockCount > 0 ? 'hidden' : '';
  if (lenis) lockCount > 0 ? lenis.stop() : lenis.start();
};

/* header: transparent over the hero, solid after scrolling */
const hdr = $('.hdr');
if (hdr && !document.body.classList.contains('inner')) {
  const on = () => hdr.classList.toggle('solid', scrollY > 40);
  addEventListener('scroll', on, { passive: true }); on();
}
/* mobile menu */
const bg = $('#burger'), nav = $('#nav');
if (bg && nav) {
  const set = o => { nav.classList.toggle('open', o); bg.setAttribute('aria-expanded', String(o)); bg.querySelector('.lbl').textContent = o ? 'بستن' : 'منو'; lock(o); if (o) hdr.classList.add('solid'); else if (!document.body.classList.contains('inner') && scrollY <= 40) hdr.classList.remove('solid'); };
  bg.addEventListener('click', () => set(!nav.classList.contains('open')));
  nav.addEventListener('click', e => { if (e.target.closest('a')) set(false); });
  addEventListener('keydown', e => { if (e.key === 'Escape') set(false); });
}
/* admin panel: collapsible sidebar on mobile */
const sideTgl = $('#sideTgl'), side = $('#adminSide');
if (sideTgl && side) {
  sideTgl.addEventListener('click', () => {
    const open = side.classList.toggle('open');
    sideTgl.setAttribute('aria-expanded', String(open));
  });
}
/* floating assistant chat widget: open in place instead of navigating to /assistant/ */
const fabTip = $('#fabTip');
if (fabTip) {
  let dismissed = false;
  try { dismissed = localStorage.getItem('akh_fabtip_dismissed') === '1'; } catch (e) {}
  if (dismissed) fabTip.hidden = true;
  const tipMin = $('#fabTipMin'), tipClose = $('#fabTipClose'), tipHd = $('.tip-hd', fabTip), tipBody = $('p', fabTip);
  if (tipClose) tipClose.addEventListener('click', e => {
    e.stopPropagation(); fabTip.hidden = true;
    try { localStorage.setItem('akh_fabtip_dismissed', '1'); } catch (e2) {}
  });
  if (tipMin) tipMin.addEventListener('click', e => { e.stopPropagation(); fabTip.classList.toggle('minimized'); });
  if (tipHd) tipHd.addEventListener('click', () => { if (fabTip.classList.contains('minimized')) fabTip.classList.remove('minimized'); });
  if (tipBody) tipBody.addEventListener('click', () => { fabTip.hidden = true; $('#fabChat')?.click(); });
}
const fabChat = $('#fabChat'), chatWidget = $('#chatWidget');
if (fabChat && chatWidget) {
  let loaded = false;
  const openWidget = () => {
    chatWidget.hidden = false;
    fabChat.setAttribute('aria-expanded', 'true');
    if (fabTip) fabTip.hidden = true;
    if (!loaded) { loaded = true; import('/assets/js/assistant.js').catch(() => {}); }
  };
  const closeWidget = () => { chatWidget.hidden = true; chatWidget.classList.remove('minimized'); fabChat.setAttribute('aria-expanded', 'false'); };
  fabChat.addEventListener('click', e => { e.preventDefault(); chatWidget.hidden ? openWidget() : closeWidget(); });
  const x = $('#chatWidgetClose'); if (x) x.addEventListener('click', closeWidget);
  const mn = $('#chatWidgetMin'), hd = $('#chatWidgetHd');
  if (mn) mn.addEventListener('click', e => { e.stopPropagation(); chatWidget.classList.toggle('minimized'); });
  if (hd) hd.addEventListener('click', () => { if (chatWidget.classList.contains('minimized')) chatWidget.classList.remove('minimized'); });
  addEventListener('keydown', e => { if (e.key === 'Escape' && !chatWidget.hidden) closeWidget(); });
}
/* "روند سفارش" steps 2-4: clicking shows "fill step 1 first" instead of doing nothing silently */
$$('.step-click').forEach(b => {
  const msg = b.nextElementSibling;
  b.addEventListener('click', () => {
    msg.classList.add('show');
    clearTimeout(b._t);
    b._t = setTimeout(() => msg.classList.remove('show'), 2500);
  });
});
/* reveal + counters */
const rv = $$('.rv');
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .12 });
  rv.forEach(x => io.observe(x));
} else rv.forEach(x => x.classList.add('in'));
/* safety net for crawlers / very fast scrolling: nothing stays invisible */
setTimeout(() => rv.forEach(x => x.classList.add('in')), 6000);
const fa = n => Number(n).toLocaleString('fa-IR');
const co = new IntersectionObserver(es => es.forEach(e => {
  if (!e.isIntersecting) return; co.unobserve(e.target);
  const t = +e.target.dataset.count; let s = null;
  const step = ts => { s = s || ts; const p = Math.min((ts - s) / 1500, 1); e.target.firstChild.nodeValue = fa(Math.round(t * (1 - Math.pow(1 - p, 3)))); if (p < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
}), { threshold: .5 });
$$('[data-count]').forEach(x => co.observe(x));
/* lightbox */
const lb = $('#lb');
if (lb) {
  const im = $('#lbi'), cp = $('#lbc'); let items = [], i = 0, last = null;
  const show = n => { i = (n + items.length) % items.length; im.src = items[i].href; im.alt = items[i].dataset.cap || ''; cp.textContent = items[i].dataset.cap || ''; };
  const open = (list, n) => { items = list; last = document.activeElement; show(n); lb.hidden = false; lock(true); $('.x', lb).focus(); };
  const close = () => { lb.hidden = true; lock(false); im.removeAttribute('src'); last && last.focus(); };
  $$('[data-lb]').forEach(box => { const list = $$('a.gi', box); list.forEach((a, n) => a.addEventListener('click', e => { e.preventDefault(); open(list, n); })); });
  $('.x', lb).onclick = close; $('.n', lb).onclick = () => show(i + 1); $('.p', lb).onclick = () => show(i - 1);
  lb.addEventListener('click', e => { if (e.target === lb) close(); });
  addEventListener('keydown', e => { if (lb.hidden) return; if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') show(i + 1); if (e.key === 'ArrowRight') show(i - 1); });
}
/* factory videos: load and play only while visible */
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches, vs = $$('video[data-src]');
if (vs.length) {
  if (calm) vs.forEach(v => v.controls = true);
  const vo = new IntersectionObserver(es => es.forEach(e => { const v = e.target; if (e.isIntersecting) { if (!v.src) { v.src = v.dataset.src; v.load(); } if (!calm) v.play().catch(() => { }); } else v.pause(); }), { threshold: .35 });
  vs.forEach(v => vo.observe(v));
}
/* search palette (Ctrl+K or "/") */
const pal = $('#pal');
if (pal) {
  const inp = $('input', pal), res = $('.pres', pal); let ix = null, loading = null, sel = -1, shown = [];
  const load = () => loading || (loading = fetch('/assets/data/search.json').then(r => r.json()).then(d => { ix = build(d); }));
  const paint = list => {
    res.replaceChildren(); shown = list; sel = -1;
    if (!list.length) { res.appendChild(el('div', 'em', inp.value.trim() ? 'نتیجه‌ای پیدا نشد. می‌توانید از «دستیار هوشمند» بپرسید.' : 'نام محصول، پروفیل یا موضوع را بنویسید؛ مثلاً «F47» یا «سقف شبکه‌ای».')); return; }
    list.forEach(r => { const a = el('a'); a.href = r.d.u; a.appendChild(el('b', '', r.d.t)); a.appendChild(el('small', '', r.d.g + ' — ' + r.d.x.slice(0, 90))); res.appendChild(a); });
  };
  const run = async () => { await load(); paint(search(ix, inp.value, 8)); };
  const open = () => { pal.hidden = false; lock(true); inp.value = ''; paint([]); inp.focus(); load(); };
  const close = () => { pal.hidden = true; lock(false); };
  $$('[data-search]').forEach(b => b.addEventListener('click', open));
  addEventListener('keydown', e => {
    const typing = /INPUT|TEXTAREA|SELECT/.test((document.activeElement || {}).tagName || '');
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); pal.hidden ? open() : close(); }
    else if (e.key === '/' && !typing && pal.hidden) { e.preventDefault(); open(); }
    else if (!pal.hidden) {
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); const as = $$('a', res); if (!as.length) return; sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + as.length) % as.length; as.forEach((a, k) => a.classList.toggle('on', k === sel)); as[sel].scrollIntoView({ block: 'nearest' }); }
      if (e.key === 'Enter' && sel >= 0) { e.preventDefault(); location.href = shown[sel].d.u; }
    }
  });
  inp.addEventListener('input', run);
  pal.addEventListener('click', e => { if (e.target === pal) close(); });
}
/* anonymous page-view counter (only with the CRM server; honours Do-Not-Track; no cookies, no IP stored) */
try {
  if (navigator.doNotTrack !== '1' && navigator.sendBeacon && /^https?:/.test(location.protocol) && !/^\/(account|admin|api|files)/.test(location.pathname))
    navigator.sendBeacon('/api/hit', new Blob([JSON.stringify({ p: location.pathname })], { type: 'application/json' }));
} catch (e) { }
