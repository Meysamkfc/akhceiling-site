/* Material estimator. All lengths / pack sizes are from the AKH catalog (F47 & L25: 4 m, 20 per pack; main tee 3.6 m). */
export const fa = n => Number(n).toLocaleString('fa-IR');
export const enNum = n => Number(n).toLocaleString('en-US');
export const fmt = (n, lang = 'fa') => lang === 'en' ? enNum(n) : fa(n);
export const digits = s => String(s).replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d)).replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/٫/g, '.').replace(/[,،]/g, '');
export const num = (v, def) => { const x = parseFloat(digits(v)); return isFinite(x) && x > 0 ? x : def; };
export function drywall(A, P, w, o = {}, lang = 'fa') {
  const sp = o.sp || .6, cs = o.cs || 1.2, hs = o.hs || 1.2, f = n => fmt(n, lang);
  const f47 = A / sp + A / cs;
  if (lang === 'en') return [
    ['F47 profile', Math.ceil(f47 * w / 4), '4m lengths', f(Math.ceil(f47 * w / 4 / 20)) + ' packs (20/pack)'],
    ['L25 angle (perimeter)', Math.ceil(P * w / 4), '4m lengths', f(Math.ceil(P * w / 4 / 20)) + ' packs (20/pack)'],
    ['F47 clip connector', Math.ceil(A / (sp * cs) * w), 'pcs', ''],
    ['Hanger & HT90/bracket connector', Math.ceil(A / (cs * hs) * w), 'pcs', ''],
    ['Gypsum board', Math.ceil(A * w), 'm²', 'equal to ceiling area + waste']
  ];
  return [
    ['پروفیل F47', Math.ceil(f47 * w / 4), 'شاخه ۴ متری', fa(Math.ceil(f47 * w / 4 / 20)) + ' بسته (۲۰ شاخه‌ای)'],
    ['نبشی L25 (دور تا دور)', Math.ceil(P * w / 4), 'شاخه ۴ متری', fa(Math.ceil(P * w / 4 / 20)) + ' بسته (۲۰ شاخه‌ای)'],
    ['بست اتصال F47 (کلیپس)', Math.ceil(A / (sp * cs) * w), 'عدد', ''],
    ['آویز و قطعه اتصال (HT90 / براکت)', Math.ceil(A / (cs * hs) * w), 'عدد', ''],
    ['صفحه گچی', Math.ceil(A * w), 'متر مربع', 'برابر سطح سقف + پرت']
  ];
}
export function grid(A, P, w, lang = 'fa') {
  if (lang === 'en') return [
    ['60×60 tile', Math.ceil(A / .36 * w), 'pcs', ''],
    ['Main tee (3.6 m)', Math.ceil(A / 1.2 / 3.6 * w), 'lengths', ''],
    ['120cm cross tee', Math.ceil(A / (1.2 * .6) * w), 'lengths', ''],
    ['60cm cross tee', Math.ceil(A / (1.2 * 1.2) * w), 'lengths', ''],
    ['L24 wall angle', Math.ceil(P * w), 'linear m', 'length per piece not specified in catalog'],
    ['Double-spring steel hanger', Math.ceil(A / (1.2 * 1.2) * w), 'pcs', '']
  ];
  return [
    ['تایل ۶۰×۶۰', Math.ceil(A / .36 * w), 'عدد', ''],
    ['سپری مادر (۳٫۶ متر)', Math.ceil(A / 1.2 / 3.6 * w), 'شاخه', ''],
    ['سپری ۱۲۰ سانتی‌متری', Math.ceil(A / (1.2 * .6) * w), 'شاخه', ''],
    ['سپری ۶۰ سانتی‌متری', Math.ceil(A / (1.2 * 1.2) * w), 'شاخه', ''],
    ['نبشی دیواری L24', Math.ceil(P * w), 'متر طول', 'طول شاخه در کاتالوگ ذکر نشده'],
    ['آویز فنر دوبل استیل', Math.ceil(A / (1.2 * 1.2) * w), 'عدد', '']
  ];
}
export const TITLES = { drywall: 'سقف گچی درای‌وال', grid: 'سقف شبکه‌ای ۶۰×۶۰' };
export const TITLES_EN = { drywall: 'Drywall ceiling system', grid: '60×60 grid ceiling' };
export const perimeterOf = A => Math.round(4 * Math.sqrt(A));
export function estimate(sys, A, P, wastePct = 10, o = {}, lang = 'fa') {
  const w = 1 + Math.min(Math.max(wastePct, 0), 50) / 100, p = P || perimeterOf(A);
  const titles = lang === 'en' ? TITLES_EN : TITLES;
  return { rows: (sys === 'grid' ? grid(A, p, w, lang) : drywall(A, p, w, o, lang)), P: p, w, title: titles[sys] || titles.drywall };
}
export function table(rows, lang = 'fa') {
  const t = document.createElement('table'); t.className = 'tbl';
  const heads = lang === 'en' ? ['Item', 'Qty', 'Unit', 'Note'] : ['قلم', 'مقدار', 'واحد', 'توضیح'];
  const h = t.createTHead().insertRow(); heads.forEach(x => { const th = document.createElement('th'); th.textContent = x; h.appendChild(th); });
  const b = t.createTBody();
  rows.forEach(r => { const tr = b.insertRow(); r.forEach((c, i) => { const td = tr.insertCell(); td.textContent = (i === 1 && typeof c === 'number') ? fmt(c, lang) : c; }); });
  return t;
}
