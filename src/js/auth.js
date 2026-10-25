/* Login / registration: solve the proof-of-work in the background and add it to the form (no third-party CAPTCHA). */
import { solve, getChallenge } from './pow.js';

/* registration form: country -> city (Iran = dropdown, other = free text), job dropdown -> "other" free text */
(() => {
  const country = document.getElementById('country'), cityIr = document.getElementById('city_ir'), cityOther = document.getElementById('city_other');
  if (country && cityIr && cityOther) {
    const syncCity = () => {
      const iran = country.value === 'ایران';
      cityIr.hidden = !iran; cityIr.required = iran; cityIr.disabled = !iran;
      const other = !iran || cityIr.value === 'سایر';
      cityOther.hidden = !other; cityOther.disabled = !other;
      if (other) cityOther.focus();
    };
    country.addEventListener('change', syncCity); cityIr.addEventListener('change', syncCity); syncCity();
  }
  const job = document.getElementById('job'), jobOther = document.getElementById('job_other');
  if (job && jobOther) {
    const syncJob = () => { const other = job.value === 'سایر'; jobOther.hidden = !other; jobOther.disabled = !other; if (other) jobOther.focus(); };
    job.addEventListener('change', syncJob); syncJob();
  }
})();
document.querySelectorAll('form[data-pow]').forEach(f => {
  let work = null;
  const start = () => { if (!work) work = getChallenge().then(async c => ({ c, n: await solve(c.challenge, c.bits) })).catch(() => null); };
  f.addEventListener('focusin', start, { once: true });
  f.addEventListener('submit', async e => {
    if (f.dataset.done) return;
    e.preventDefault(); start();
    const btn = f.querySelector('button[type=submit]'); if (btn) btn.disabled = true;
    const w = await work;
    if (w) {
      [['pow_token', w.c.token], ['pow_nonce', w.n]].forEach(([k, v]) => { const i = document.createElement('input'); i.type = 'hidden'; i.name = k; i.value = v; f.appendChild(i); });
    }
    f.dataset.done = '1'; f.submit();
  });
});
