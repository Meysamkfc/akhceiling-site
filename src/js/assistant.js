/* Smart assistant (no external AI, no data leaves the page until the visitor presses "request a call"):
   - understands area / room / system in free Persian text, computes a material estimate from the catalog,
   - shows a real executed sample, answers technical questions by retrieval over the site's own verified content,
   - otherwise hands over to a human sales expert (lead is scored on the server). */
import { build, search, norm } from './ir.js';
import { estimate, table, num, fa, digits } from './calc.js';
import { solve, getChallenge } from './pow.js';

const msgs = document.getElementById('msgs'), comp = document.getElementById('composer');
if (msgs) {
  const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
  const link = (t, h) => { const a = el('a', '', t); a.href = h; return a; };
  const scroll = () => { msgs.scrollTop = msgs.scrollHeight; };
  const ROOMS = { office: ['اداری / تجاری', 'اداری|دفتر|شرکت|تجاری|فروشگاه|مغازه|پاساژ|مرکز خرید'], school: ['آموزشی / دانشگاهی', 'مدرسه|دانشگاه|کلاس|آموزش|دانشکده'], hospital: ['درمانی / بیمارستانی', 'بیمارستان|درمانگاه|کلینیک|مطب|درمان'],
    commercial: ['لابی / هتل', 'لابی|هتل|رستوران|ورودی|فرودگاه|ترمینال'], home: ['مسکونی', 'مسکونی|خانه|آپارتمان|ویلا|منزل|اتاق خواب|پذیرایی|آشپزخانه'], industrial: ['صنعتی / سوله', 'کارخانه|سوله|انبار|صنعتی|پارکینگ|سالن'] };
  const roomOf = t => { for (const k in ROOMS) if (new RegExp(ROOMS[k][1]).test(t)) return k; return ''; };
  const sysOf = t => /شبکه|۶۰|60|تایل|سپری|مینرال/.test(t) ? 'grid' : /درای|گچی|f47|uh36|l25|کناف|باکس|نور مخفی|پروفیل/.test(t) ? 'drywall' : '';
  const areaOf = t => { const m = t.match(/(\d+(?:\.\d+)?)\s*(?:متر\s*مربع|مترمربع|متر|m2|m²)/); if (m) return parseFloat(m[1]); const n = t.match(/(^|\s)(\d{2,6})(\s|$)/); return n ? parseFloat(n[2]) : 0; };
  const SYS = {
    grid: { name: 'سقف کاذب شبکه‌ای ۶۰×۶۰', url: '/products/grid-ceiling/', text: 'تایل‌ها قابل برداشتن‌اند و دسترسی به تأسیسات ساده است؛ اجرا سریع و بدون نیاز به رنگ است.' },
    drywall: { name: 'سقف گچی درای‌وال', url: '/products/drywall/', text: 'سطحی یکپارچه و بدون درز با امکان باکس، نور مخفی و طرح‌های دکوراتیو.' }
  };
  const pick = (room, a) => {
    const S = (s, f, cap) => ({ s, img: '/assets/r/' + f + '-960.webp', cap });
    if (room === 'home') return a < 40 ? S('drywall', 'show-p04', 'سقف گچی دکوراتیو — هتل آزادی') : S('drywall', 'show-r8', 'سقف گچی با باکس‌های مربعی — رستوران نیاوران');
    if (room === 'office') return a < 30 ? S('drywall', 'show-d2', 'سقف گچی با باکس') : a < 150 ? S('grid', 'show-p01', 'سقف شبکه‌ای — دانشگاه شهرری') : S('grid', 'show-p06', 'سقف شبکه‌ای — راهرو و فضای بزرگ');
    if (room === 'school' || room === 'hospital') return a < 100 ? S('grid', 'show-p01', 'سقف شبکه‌ای — دانشگاه شهرری') : S('grid', 'show-p07', 'سقف شبکه‌ای — دانشگاه شهید رجایی');
    if (room === 'commercial') return a < 40 ? S('drywall', 'show-p04', 'سقف گچی دکوراتیو — هتل آزادی') : S('grid', 'show-p06', 'سقف شبکه‌ای — راهرو و فضای بزرگ');
    return a < 200 ? S('grid', 'show-p12', 'سقف شبکه‌ای — کارخانه سینک اخوان') : S('grid', 'show-p13', 'سقف شبکه‌ای — مجموعه تن‌ماهی ماسی');
  };

  const ctx = { room: '', area: 0, sys: '', q: '' };
  let ix = null, csrf = '', pow = null;
  const load = fetch('/assets/data/search.json').then(r => r.json()).then(d => { ix = build(d.filter(x => ['پرسش', 'واژه‌نامه', 'محصول', 'مقاله'].includes(x.g))); }).catch(() => { });
  fetch('/api/csrf', { credentials: 'same-origin' }).then(r => r.json()).then(j => { csrf = j.token; }).catch(() => { });

  const say = (nodes, who = 'bot', delay = 380) => new Promise(res => {
    const b = el('div', 'b ' + who);
    if (who === 'bot' && delay) { const d = el('span', 'dots'); d.append(el('i'), el('i'), el('i')); b.appendChild(d); msgs.appendChild(b); scroll(); setTimeout(() => { b.replaceChildren(...[].concat(nodes)); scroll(); res(b); }, delay); }
    else { b.replaceChildren(...[].concat(nodes)); msgs.appendChild(b); scroll(); res(b); }
  });
  const t = s => document.createTextNode(s);
  const P = (...c) => { const p = el('p'); c.forEach(x => p.append(typeof x === 'string' ? t(x) : x)); return p; };
  const strong = s => el('strong', '', s);

  const quickBar = () => {
    const wrap = el('div'), q = el('div', 'quick');
    [['برآورد متریال برای متراژ من', 'مثلاً ۱۲۰ متر درای‌وال'], ['یک نمونه سقف برای فضای من', 'کاربری و متراژ را بگویم'], ['تفاوت F47 و UH36 چیست؟', 'تفاوت F47 و UH36 چیست؟'], ['ضخامت و وزن پروفیل‌ها', 'وزن بندیل F47 چقدر است؟'], ['تماس با کارشناس فروش', 'تماس با کارشناس']].forEach(([l, ph]) => {
      const b = el('button', '', l); b.type = 'button'; b.onclick = () => { input.value = l === 'برآورد متریال برای متراژ من' ? '' : ph; if (l.startsWith('برآورد')) { input.placeholder = ph; input.focus(); say(P('متراژ و نوع سقف را بنویسید؛ مثلاً «۱۲۰ متر سقف درای‌وال» یا «۸۰ متر سقف شبکه‌ای ۶۰×۶۰».')); } else if (l.startsWith('یک نمونه')) { input.value = ''; input.focus(); say(P('کاربری فضا و متراژ را بنویسید؛ مثلاً «دفتر اداری ۸۰ متر».')); } else send(); }; q.appendChild(b);
    });
    wrap.appendChild(q); return wrap;
  };
  const form = el('form', 'inl'); const input = el('input'); input.placeholder = 'سؤال یا درخواست خود را بنویسید…'; input.setAttribute('aria-label', 'پیام شما'); input.maxLength = 300; input.autocomplete = 'off';
  const go = el('button', 'btn sm plain', 'ارسال'); go.type = 'submit'; form.append(input, go);
  comp.append(quickBar(), form);
  form.addEventListener('submit', e => { e.preventDefault(); send(); });

  async function send() {
    const raw = input.value.trim(); if (!raw) return; input.value = '';
    await say(t(raw), 'me', 0); await respond(raw);
  }
  const isEnglish = s => { const letters = s.replace(/[^A-Za-z؀-ۿ]/g, ''); if (!letters) return false; const latin = (letters.match(/[A-Za-z]/g) || []).length; return latin / letters.length > 0.6; };
  async function respondEN(raw) {
    const t2 = raw.toLowerCase();
    const sys = /grid|60x60|tile|t-?bar/.test(t2) ? 'grid' : /f47|uh36|l25|drywall|profile|stud|track/.test(t2) ? 'drywall' : '';
    const areaM = t2.match(/(\d+(?:\.\d+)?)\s*(?:sq\s*m|sqm|m2|m²|square met(?:er|re)s?)/);
    if (sys) {
      const info = sys === 'grid' ? 'Removable 60×60cm grid ceiling tiles with easy access to the services above the ceiling.' : 'Seamless drywall ceiling system built from galvanized F47, UH36 and L25 profiles.';
      return say([P(strong(SYS[sys].name + ' (' + sys + ')'), ' — ', info), P('See the full page (in Persian — your browser can translate it): ', link(SYS[sys].name, SYS[sys].url)), P(areaM ? 'For a material estimate or a quote, please use the ' : 'For pricing, please use the ', link('quote request form', '/quote/'), ' or call ', strong('+98 21 8850 7585'), '.')]).then(offerContactEN);
    }
    return say([P('Hi! I can give a short answer in English, but full technical detail is only in Persian on this site (your browser can translate those pages).'), P('AKH manufactures galvanized drywall profiles (F47, UH36, L25) and 60×60cm grid suspended ceilings, shipped nationwide from our Kahrizak factory.'), P('See: ', link('English homepage', '/en/'), ' · ', link('Request a quote', '/quote/'), ' · call ', strong('+98 21 8850 7585'), '.')]).then(offerContactEN);
  }
  function offerContactEN() {
    const b = el('div', 'offer'); const btn = el('button', 'btn sm', 'Request a call back'); btn.type = 'button'; btn.onclick = () => contactReply('A sales expert will confirm pricing and technical details.'); b.appendChild(btn);
    msgs.appendChild(b); scroll();
  }
  async function respond(raw) {
    if (isEnglish(raw)) return respondEN(raw);
    const n = norm(raw); ctx.q = raw;
    const area = areaOf(n) || 0, room = roomOf(n), sys = sysOf(n);
    if (area) ctx.area = area; if (room) ctx.room = room; if (sys) ctx.sys = sys;
    const wantsEstimate = /برآورد|محاسبه|چند شاخه|چقدر پروفیل|چقدر متریال|چه مقدار|تعداد|متریال|پروفیل لازم|لازم دارم|نیاز دارم|لازمه|حساب/.test(n);
    const wantsContact = /تماس|کارشناس|قیمت|سفارش|خرید|استعلام|پیش فاکتور|پیشفاکتور|شماره/.test(n);
    if (area && (wantsEstimate || sys)) return estimateReply(area, sys || 'drywall');
    if ((area && ctx.room) || (room && ctx.area)) return sampleReply();
    if (wantsContact && !/وزن|ضخامت|طول|چیست|چه تفاوت/.test(n)) return contactReply('کارشناس فروش قیمت و پیشنهاد فنی را اعلام می‌کند.');
    await load; const r = ix ? search(ix, raw, 3) : [];
    if (r.length && r[0].s > 6) {
      const d = r[0].d, body = [P(d.x)];
      if (d.u) { const s = el('span', 'src'); s.append(t('منبع: '), link(d.t, d.u)); body.push(s); }
      if (r[1] && r[1].s > r[0].s * .7) { const s2 = el('span', 'src'); s2.append(t('مرتبط: '), link(r[1].d.t, r[1].d.u)); body.push(s2); }
      await say(body); return offerContact();
    }
    if (area || room) return say(P('برای پیشنهاد دقیق‌تر هم کاربری و هم متراژ فضا را بگویید؛ مثلاً «دفتر اداری ۸۰ متر».'));
    return contactReply('پاسخ دقیق این پرسش را کارشناس فنی می‌دهد.');
  }
  async function estimateReply(A, sys) {
    const r = estimate(sys, A, 0, 10);
    const sc = el('div', 'scroll'); sc.appendChild(table(r.rows));
    await say([P(strong(r.title), ' — ', fa(A), ' متر مربع (محیط تقریبی ', fa(r.P), ' متر، پرت ۱۰٪):'), sc, P('این فقط ', strong('تخمین اولیه'), ' با چیدمان استاندارد و ابعاد کاتالوگ است؛ مقدار نهایی با کارشناس. ', link('تنظیم فاصله‌ها در ماشین‌حساب کامل', '/estimate/?area=' + A + '&sys=' + sys))], 'bot', 450);
    if (ctx.room) return sampleReply(); return offerContact();
  }
  async function sampleReply() {
    const p = pick(ctx.room, ctx.area || 50), s = SYS[p.s], fig = el('figure', 'sample'), im = el('img'); im.src = p.img; im.alt = p.cap; im.width = 960; im.height = 720; im.loading = 'lazy';
    fig.append(im, el('figcaption', '', p.cap + ' — پروژه‌ای که با متریال ما اجرا شده'));
    await say([P('برای ', strong(ROOMS[ctx.room][0]), ' حدود ', strong(fa(ctx.area || 50) + ' متر مربع'), ' این نمونه از کارهای اجراشده ما را پیشنهاد می‌کنم:'), fig, P(strong(s.name), ' — ', s.text, ' ', link('اطلاعات بیشتر', s.url)), P('این فقط یک نمونه است، نه طرح یا قیمت نهایی.')], 'bot', 600);
    ctx.sys = ctx.sys || p.s; return offerContact();
  }
  async function offerContact() { await say([P('برای ', strong('قیمت و پیشنهاد فنی دقیق'), '، کارشناس فروش با شما تماس می‌گیرد.'), btn('درخواست تماس کارشناس', () => contactReply())], 'bot', 300); }
  const btn = (txt, fn) => { const b = el('button', 'btn sm', txt); b.type = 'button'; b.style.marginTop = '6px'; b.onclick = fn; return b; };
  async function contactReply(pre) {
    const existing = document.getElementById('leadform');
    if (existing) { await say(P('برای این سؤال هم کارشناس بهتر می‌تواند پاسخ بدهد؛ لطفاً فرم بالا را تکمیل کنید تا باهاتون تماس بگیرد.'), 'bot', 250); existing.scrollIntoView({ block: 'center' }); return; }
    const f = el('form', 'inl col'); f.id = 'leadform'; f.noValidate = true;
    const mk = (n, ph, ac, im) => { const i = el('input'); i.name = n; i.placeholder = ph; i.autocomplete = ac; i.setAttribute('aria-label', ph); if (im) i.inputMode = im; if (n === 'phone') i.dir = 'ltr'; return i; };
    const hp = mk('website', '', 'off'); hp.className = 'hp'; hp.tabIndex = -1; hp.setAttribute('aria-hidden', 'true');
    const er = el('div', 'err'); er.setAttribute('role', 'alert'); const sub = el('button', 'btn plain', 'ثبت درخواست تماس'); sub.type = 'submit';
    f.append(mk('name', 'نام و نام خانوادگی', 'name'), mk('phone', 'شماره تماس، مثل ۰۹۱۲۳۴۵۶۷۸۹', 'tel', 'tel'), mk('city', 'شهر پروژه (اختیاری)', 'off'), hp, er, sub);
    pow = pow || getChallenge().then(async c => ({ c, n: await solve(c.challenge, c.bits) })).catch(() => null);
    await say([P((pre ? pre + ' ' : '') + 'لطفاً نام و شماره تماس خود را بنویسید:'), f], 'bot', 350);
    f.name.focus();
    f.addEventListener('submit', async e => {
      e.preventDefault(); er.textContent = '';
      const name = f.name.value.trim(), phone = f.phone.value.trim();
      if (name.length < 3) { er.textContent = 'نام و نام خانوادگی را وارد کنید.'; return; }
      const pn = digits(phone).replace(/[\s-]/g, ''); if (!(/^(\+98|0098|0)?9\d{9}$/.test(pn) || /^0\d{10}$/.test(pn))) { er.textContent = 'شماره تماس معتبر وارد کنید.'; return; }
      sub.disabled = true; sub.textContent = 'در حال ثبت…';
      try {
        const p = await pow; if (!p) throw new Error('pow');
        const sys = SYS[ctx.sys] ? SYS[ctx.sys].name : '';
        const payload = { source: 'assistant', name, phone, city: f.city.value.trim(), website: f.website.value, area: ctx.area || '', room: ctx.room, suggestion: sys, sample: '',
          building: ({ office: 'office', school: 'school', hospital: 'hospital', commercial: 'hotel', home: 'home', industrial: 'industrial' })[ctx.room], product: ctx.sys || '',
          desc: 'ثبت از دستیار هوشمند' + (ctx.room ? ' — کاربری: ' + ROOMS[ctx.room][0] : '') + (ctx.area ? ' — متراژ: ' + ctx.area : '') + (ctx.q ? ' — آخرین پیام: ' + ctx.q.slice(0, 160) : ''), pow_token: p.c.token, pow_nonce: p.n };
        const r = await fetch('/api/lead', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf }, body: JSON.stringify(payload) });
        const j = await r.json();
        if (r.status === 422) { er.textContent = Object.values(j.errors || {})[0] || 'اطلاعات را بررسی کنید.'; sub.disabled = false; sub.textContent = 'ثبت درخواست تماس'; pow = null; return; }
        if (!r.ok || !j.ok) throw new Error(j.error || 'x');
        f.replaceWith(el('p', '', name + ' — ' + phone));
        await say([P('ثبت شد ✅ شماره پیگیری شما: ', el('b', 'num', j.code)), P('کارشناس فروش در ساعات کاری (شنبه تا چهارشنبه ۹ تا ۱۷، پنجشنبه ۹ تا ۱۳) با شما تماس می‌گیرد.')], 'bot', 500);
      } catch (_) { sub.disabled = false; sub.textContent = 'ثبت درخواست تماس'; pow = null; er.textContent = 'ثبت آنلاین انجام نشد. لطفاً با ۰۲۱-۸۸۵۰۷۵۸۵ تماس بگیرید یا از صفحه «درخواست قیمت» استفاده کنید.'; }
    });
  }

  (async () => {
    await say([P('سلام 👋 من ', strong('البرزبات'), ' هستم، دستیار هوشمند صنعت سقف البرز خاورمیانه.'), P('می‌توانم ', strong('برآورد متریال'), ' بدهم، ', strong('نمونه سقف'), ' نشان بدهم یا ', strong('سؤال فنی'), ' شما را درباره پروفیل‌ها و سقف‌ها جواب بدهم. به زبان خودتان بنویسید.')], 'bot', 300);
    const q = new URLSearchParams(location.search), room = q.get('room'), area = parseFloat(q.get('area'));
    if (room && ROOMS[room] && area >= 1) { ctx.room = room; ctx.area = area; await say(t(ROOMS[room][0] + '، ' + fa(area) + ' متر مربع'), 'me', 0); await sampleReply(); await estimateReply(area, pick(room, area).s === 'grid' ? 'grid' : 'drywall'); }
  })();
}
