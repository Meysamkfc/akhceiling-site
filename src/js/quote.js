import { solve, getChallenge } from './pow.js';
const f = document.getElementById('qf');
if (f) {
  const $ = id => document.getElementById(id);
  const PROD = { grid: 'سقف کاذب شبکه‌ای ۶۰×۶۰', drywall: 'سیستم درای‌وال و سقف گچی', grillium: 'سقف گریلیوم (مشبک)', profiles: 'پروفیل و اتصالات درای‌وال', other: 'سایر / نیاز به راهنمایی' };
  const BLD = { office: 'اداری / تجاری', school: 'آموزشی / دانشگاهی', hospital: 'درمانی / بیمارستانی', hotel: 'هتل / لابی / فرودگاه', home: 'مسکونی', industrial: 'صنعتی / سوله' };
  const q = new URLSearchParams(location.search);
  if (q.get('p') && PROD[q.get('p')]) $('product').value = q.get('p');
  if (q.get('b') && BLD[q.get('b')]) $('building').value = q.get('b');
  if (q.get('area') && /^[\d.]{1,9}$/.test(q.get('area'))) $('area').value = q.get('area');
  if (q.get('note')) $('desc').value = q.get('note').slice(0, 900);
  const digits = s => s.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d)).replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d));
  const phoneOk = s => { const t = s.replace(/[\s-]/g, ''); return /^(\+98|0098|0)?9\d{9}$/.test(t) || /^0\d{10}$/.test(t); };
  const v = id => ($(id).value || '').trim();
  const msg = () => {
    const l = ['درخواست قیمت — صنعت سقف البرز خاورمیانه', 'نام: ' + v('name'), 'تلفن: ' + digits(v('phone'))];
    if (v('company')) l.push('شرکت: ' + v('company')); l.push('شهر پروژه: ' + v('city'));
    if ($('building').value) l.push('نوع ساختمان: ' + BLD[$('building').value]); if ($('product').value) l.push('محصول: ' + PROD[$('product').value]);
    if (v('area')) l.push('متراژ تقریبی: ' + digits(v('area')) + ' متر مربع'); if (v('desc')) l.push('توضیحات: ' + v('desc')); return l.join('\n');
  };
  const validate = () => { let ok = true; const set = (id, m) => { $(id + '-e').textContent = m || ''; if (m) ok = false; };
    set('name', v('name').length < 3 ? 'نام و نام خانوادگی را وارد کنید.' : ''); set('phone', phoneOk(digits(v('phone'))) ? '' : 'شماره تماس معتبر وارد کنید.'); set('city', v('city').length < 2 ? 'شهر پروژه را وارد کنید.' : ''); return ok; };
  const manual = () => { const t = msg(), enc = encodeURIComponent(t); $('wa').href = 'https://wa.me/989124968761?text=' + enc; $('mail').href = 'mailto:info@akhceiling.com?subject=' + encodeURIComponent('درخواست قیمت') + '&body=' + enc; $('preview').textContent = t; $('manual').hidden = false; $('okmsg').hidden = true; };
  // warm up the proof-of-work while the visitor types
  let pow = null; f.addEventListener('focusin', () => { if (!pow) pow = getChallenge().then(async c => ({ c, n: await solve(c.challenge, c.bits) })).catch(() => null); }, { once: true });
  f.addEventListener('submit', async e => {
    e.preventDefault(); if ($('website').value) return; if (!validate()) return;
    const btn = f.querySelector('button[type=submit]'); btn.disabled = true; btn.textContent = 'در حال ثبت…';
    let ok = false, code = '';
    try {
      const t = (await (await fetch('/api/csrf', { credentials: 'same-origin' })).json()).token;
      if (!pow) pow = getChallenge().then(async c => ({ c, n: await solve(c.challenge, c.bits) }));
      const p = await pow; if (!p) throw new Error('pow');
      const r = await fetch('/api/lead', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': t },
        body: JSON.stringify({ source: 'quote', name: v('name'), phone: v('phone'), company: v('company'), city: v('city'), building: $('building').value, product: $('product').value, area: v('area'), desc: v('desc'), website: v('website'), pow_token: p.c.token, pow_nonce: p.n }) });
      const j = await r.json();
      if (r.status === 422) { const er = j.errors || {}; Object.keys(er).forEach(k => { const n = $(k + '-e'); if (n) n.textContent = er[k]; }); btn.disabled = false; btn.textContent = 'ثبت درخواست'; pow = null; return; }
      ok = r.ok && j.ok; code = j.code || '';
    } catch (_) { ok = false; }
    f.hidden = true; $('sent').hidden = false; if (ok) $('trk').textContent = code; else manual();
    $('sent').scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  const cp = $('copy'); if (cp) cp.addEventListener('click', async () => { try { await navigator.clipboard.writeText($('preview').textContent); cp.textContent = 'کپی شد ✓'; } catch (_) { } });
}
