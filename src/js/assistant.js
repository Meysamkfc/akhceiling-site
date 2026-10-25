/* Smart assistant (no external AI, no data leaves the page until the visitor presses "request a call"):
   - understands area / room / system in free Persian text, computes a material estimate from the catalog,
   - shows a real executed sample, answers technical questions by retrieval over the site's own verified content,
   - otherwise hands over to a human sales expert (lead is scored on the server). */
import { build, search, norm } from './ir.js';
import { estimate, table, num, fa, fmt, digits } from './calc.js';
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
  const SYS_EN = {
    grid: { name: '60×60 grid suspended ceiling', url: '/en/products/grid-ceiling/', text: 'Tiles are removable with easy access to the services above the ceiling; fast to install and needs no painting.' },
    drywall: { name: 'Drywall ceiling system', url: '/en/products/drywall/', text: 'A seamless, joint-free surface with recessed lighting boxes and decorative designs.' }
  };
  const ROOM_NAME_EN = { office: 'Office / commercial', school: 'Educational / university', hospital: 'Medical / hospital', commercial: 'Lobby / hotel', home: 'Residential', industrial: 'Industrial / warehouse' };
  const isEN = document.documentElement.lang === 'en';
  const pick = (room, a) => {
    const S = (s, f, cap, capEN) => ({ s, img: '/assets/r/' + f + '-960.webp', cap: isEN ? capEN : cap });
    if (room === 'home') return a < 40 ? S('drywall', 'show-p04', 'سقف گچی دکوراتیو — هتل آزادی', 'Decorative gypsum ceiling — Hotel Azadi') : S('drywall', 'show-r8', 'سقف گچی با باکس‌های مربعی — رستوران نیاوران', 'Gypsum ceiling with square boxes — Niavaran restaurant');
    if (room === 'office') return a < 30 ? S('drywall', 'show-d2', 'سقف گچی با باکس', 'Gypsum ceiling with a box') : a < 150 ? S('grid', 'show-p01', 'سقف شبکه‌ای — دانشگاه شهرری', 'Grid ceiling — Shahre Rey University') : S('grid', 'show-p06', 'سقف شبکه‌ای — راهرو و فضای بزرگ', 'Grid ceiling — corridor and large space');
    if (room === 'school' || room === 'hospital') return a < 100 ? S('grid', 'show-p01', 'سقف شبکه‌ای — دانشگاه شهرری', 'Grid ceiling — Shahre Rey University') : S('grid', 'show-p07', 'سقف شبکه‌ای — دانشگاه شهید رجایی', 'Grid ceiling — Shahid Rajaei University');
    if (room === 'commercial') return a < 40 ? S('drywall', 'show-p04', 'سقف گچی دکوراتیو — هتل آزادی', 'Decorative gypsum ceiling — Hotel Azadi') : S('grid', 'show-p06', 'سقف شبکه‌ای — راهرو و فضای بزرگ', 'Grid ceiling — corridor and large space');
    return a < 200 ? S('grid', 'show-p12', 'سقف شبکه‌ای — کارخانه سینک اخوان', 'Grid ceiling — Akhavan Sink factory') : S('grid', 'show-p13', 'سقف شبکه‌ای — مجموعه تن‌ماهی ماسی', 'Grid ceiling — Tanmahi Massi complex');
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

  const form = el('form', 'inl'); const input = el('input'); input.placeholder = isEN ? 'Type your question or request…' : 'سؤال یا درخواست خود را بنویسید…'; input.setAttribute('aria-label', isEN ? 'Your message' : 'پیام شما'); input.maxLength = 300; input.autocomplete = 'off';
  const go = el('button', 'btn sm plain', isEN ? 'Send' : 'ارسال'); go.type = 'submit'; form.append(input, go);
  comp.append(form);
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
      return say([P(strong(SYS_EN[sys].name + ' (' + sys + ')'), ' — ', info), P('See the full page: ', link(SYS_EN[sys].name, SYS_EN[sys].url)), P(areaM ? 'For a material estimate or a quote, please use the ' : 'For pricing, please use the ', link('quote request form', '/en/quote/'), ' or call ', strong('+98 21 8850 7585'), '.')]).then(offerContactEN);
    }
    return say([P('Hi! I can give a short answer in English.'), P('AKH manufactures galvanized drywall profiles (F47, UH36, L25) and 60×60cm grid suspended ceilings, shipped nationwide from our Kahrizak factory.'), P('See: ', link('English homepage', '/en/'), ' · ', link('Request a quote', '/en/quote/'), ' · call ', strong('+98 21 8850 7585'), '.')]).then(offerContactEN);
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
    const lang = isEN ? 'en' : 'fa';
    const r = estimate(sys, A, 0, 10, {}, lang);
    const sc = el('div', 'scroll'); sc.appendChild(table(r.rows, lang));
    const msg = isEN
      ? [P(strong(r.title), ' — ', fmt(A, lang), ' m² (perimeter approx. ', fmt(r.P, lang), ' m, 10% waste):'), sc, P('This is just an ', strong('initial estimate'), ' with a standard layout and catalog dimensions; the final amount is confirmed by our technical expert. ', link('Adjust spacing in the full calculator', '/en/estimate/?area=' + A + '&sys=' + sys))]
      : [P(strong(r.title), ' — ', fa(A), ' متر مربع (محیط تقریبی ', fa(r.P), ' متر، پرت ۱۰٪):'), sc, P('این فقط ', strong('تخمین اولیه'), ' با چیدمان استاندارد و ابعاد کاتالوگ است؛ مقدار نهایی با کارشناس. ', link('تنظیم فاصله‌ها در ماشین‌حساب کامل', '/estimate/?area=' + A + '&sys=' + sys))];
    await say(msg, 'bot', 450);
    if (ctx.room) return sampleReply(); return offerContact();
  }
  async function sampleReply() {
    const p = pick(ctx.room, ctx.area || 50), s = isEN ? SYS_EN[p.s] : SYS[p.s], fig = el('figure', 'sample'), im = el('img'); im.src = p.img; im.alt = p.cap; im.width = 960; im.height = 720; im.loading = 'lazy';
    fig.append(im, el('figcaption', '', p.cap + (isEN ? ' — a project built with our materials' : ' — پروژه‌ای که با متریال ما اجرا شده')));
    const roomName = isEN ? ROOM_NAME_EN[ctx.room] : ROOMS[ctx.room][0];
    const areaTxt = isEN ? fmt(ctx.area || 50, 'en') + ' m²' : fa(ctx.area || 50) + ' متر مربع';
    const msg = isEN
      ? [P('For ', strong(roomName), ', about ', strong(areaTxt), ', I’d suggest this example from our completed projects:'), fig, P(strong(s.name), ' — ', s.text, ' ', link('More information', s.url)), P('This is just an example, not a final design or price.')]
      : [P('برای ', strong(roomName), ' حدود ', strong(areaTxt), ' این نمونه از کارهای اجراشده ما را پیشنهاد می‌کنم:'), fig, P(strong(s.name), ' — ', s.text, ' ', link('اطلاعات بیشتر', s.url)), P('این فقط یک نمونه است، نه طرح یا قیمت نهایی.')];
    await say(msg, 'bot', 600);
    ctx.sys = ctx.sys || p.s; return offerContact();
  }
  async function offerContact() {
    if (isEN) { await say([P('For ', strong('accurate pricing and a technical recommendation'), ', a sales expert will contact you.'), btn('Request a call back', () => contactReply())], 'bot', 300); return; }
    await say([P('برای ', strong('قیمت و پیشنهاد فنی دقیق'), '، کارشناس فروش با شما تماس می‌گیرد.'), btn('درخواست تماس کارشناس', () => contactReply())], 'bot', 300);
  }
  const btn = (txt, fn) => { const b = el('button', 'btn sm', txt); b.type = 'button'; b.style.marginTop = '6px'; b.onclick = fn; return b; };
  async function contactReply(pre) {
    const existing = document.getElementById('leadform');
    if (existing) { await say(P(isEN ? 'Our expert can answer this better — please complete the form above so they can reach you.' : 'برای این سؤال هم کارشناس بهتر می‌تواند پاسخ بدهد؛ لطفاً فرم بالا را تکمیل کنید تا باهاتون تماس بگیرد.'), 'bot', 250); existing.scrollIntoView({ block: 'center' }); return; }
    const f = el('form', 'inl col'); f.id = 'leadform'; f.noValidate = true;
    const mk = (n, ph, ac, im) => { const i = el('input'); i.name = n; i.placeholder = ph; i.autocomplete = ac; i.setAttribute('aria-label', ph); if (im) i.inputMode = im; if (n === 'phone') i.dir = 'ltr'; return i; };
    const hp = mk('website', '', 'off'); hp.className = 'hp'; hp.tabIndex = -1; hp.setAttribute('aria-hidden', 'true');
    const er = el('div', 'err'); er.setAttribute('role', 'alert');
    const submitLabel = isEN ? 'Request a call back' : 'ثبت درخواست تماس';
    const sub = el('button', 'btn plain', submitLabel); sub.type = 'submit';
    f.append(mk('name', isEN ? 'Full name' : 'نام و نام خانوادگی', 'name'), mk('phone', isEN ? 'Phone number, e.g. 09123456789' : 'شماره تماس، مثل ۰۹۱۲۳۴۵۶۷۸۹', 'tel', 'tel'), mk('city', isEN ? 'Project city (optional)' : 'شهر پروژه (اختیاری)', 'off'), hp, er, sub);
    pow = pow || getChallenge().then(async c => ({ c, n: await solve(c.challenge, c.bits) })).catch(() => null);
    await say([P((pre ? pre + ' ' : '') + (isEN ? 'Please enter your name and phone number:' : 'لطفاً نام و شماره تماس خود را بنویسید:')), f], 'bot', 350);
    f.name.focus();
    f.addEventListener('submit', async e => {
      e.preventDefault(); er.textContent = '';
      const name = f.name.value.trim(), phone = f.phone.value.trim();
      if (name.length < 3) { er.textContent = isEN ? 'Please enter your full name.' : 'نام و نام خانوادگی را وارد کنید.'; return; }
      const pn = digits(phone).replace(/[\s-]/g, ''); if (!(/^(\+98|0098|0)?9\d{9}$/.test(pn) || /^0\d{10}$/.test(pn))) { er.textContent = isEN ? 'Please enter a valid phone number.' : 'شماره تماس معتبر وارد کنید.'; return; }
      sub.disabled = true; sub.textContent = isEN ? 'Submitting…' : 'در حال ثبت…';
      try {
        const p = await pow; if (!p) throw new Error('pow');
        const sys = SYS[ctx.sys] ? SYS[ctx.sys].name : '';
        const payload = { source: 'assistant', name, phone, city: f.city.value.trim(), website: f.website.value, area: ctx.area || '', room: ctx.room, suggestion: sys, sample: '',
          building: ({ office: 'office', school: 'school', hospital: 'hospital', commercial: 'hotel', home: 'home', industrial: 'industrial' })[ctx.room], product: ctx.sys || '',
          desc: (isEN ? 'Submitted from the smart assistant' : 'ثبت از دستیار هوشمند') + (ctx.room ? (isEN ? ' — use: ' + (ROOM_NAME_EN[ctx.room] || ctx.room) : ' — کاربری: ' + ROOMS[ctx.room][0]) : '') + (ctx.area ? (isEN ? ' — area: ' + ctx.area : ' — متراژ: ' + ctx.area) : '') + (ctx.q ? (isEN ? ' — last message: ' : ' — آخرین پیام: ') + ctx.q.slice(0, 160) : ''), pow_token: p.c.token, pow_nonce: p.n };
        const r = await fetch('/api/lead', { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf }, body: JSON.stringify(payload) });
        const j = await r.json();
        if (r.status === 422) { er.textContent = Object.values(j.errors || {})[0] || (isEN ? 'Please check your details.' : 'اطلاعات را بررسی کنید.'); sub.disabled = false; sub.textContent = submitLabel; pow = null; return; }
        if (!r.ok || !j.ok) throw new Error(j.error || 'x');
        f.replaceWith(el('p', '', name + ' — ' + phone));
        await say(isEN
          ? [P('Submitted ✅ Your tracking number: ', el('b', 'num', j.code)), P('A sales expert will call you during working hours (Sat–Wed 9:00–17:00, Thu 9:00–13:00).')]
          : [P('ثبت شد ✅ شماره پیگیری شما: ', el('b', 'num', j.code)), P('کارشناس فروش در ساعات کاری (شنبه تا چهارشنبه ۹ تا ۱۷، پنجشنبه ۹ تا ۱۳) با شما تماس می‌گیرد.')], 'bot', 500);
      } catch (_) { sub.disabled = false; sub.textContent = submitLabel; pow = null; er.textContent = isEN ? 'The online submission failed. Please call +98 21 8850 7585 or use the "Request a quote" page.' : 'ثبت آنلاین انجام نشد. لطفاً با ۰۲۱-۸۸۵۰۷۵۸۵ تماس بگیرید یا از صفحه «درخواست قیمت» استفاده کنید.'; }
    });
  }

  (async () => {
    const greeting = document.documentElement.lang === 'en' ? "I'm AlborzBot, got a question? I'm here to help." : 'من بات البرز هستم، سؤالی دارید؟ در خدمتم.';
    await say(P(greeting), 'bot', 300);
    const q = new URLSearchParams(location.search), room = q.get('room'), area = parseFloat(q.get('area'));
    if (room && ROOMS[room] && area >= 1) {
      ctx.room = room; ctx.area = area;
      const echo = isEN ? (ROOM_NAME_EN[room] || room) + ', ' + fmt(area, 'en') + ' m²' : ROOMS[room][0] + '، ' + fa(area) + ' متر مربع';
      await say(t(echo), 'me', 0); await sampleReply(); await estimateReply(area, pick(room, area).s === 'grid' ? 'grid' : 'drywall');
    }
  })();
}
