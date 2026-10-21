/* Proof-of-work for public forms (no third-party CAPTCHA): find a nonce so that SHA-256(challenge + ":" + nonce) starts with `bits` zero bits. */
const born = new Map(); /* the server rejects tokens younger than 2 s; never submit sooner */
export async function solve(challenge, bits) {
  const wait = () => new Promise(r => setTimeout(r, Math.max(0, 2600 - (performance.now() - (born.get(challenge) || 0)))));
  const enc = new TextEncoder();
  for (let n = 0; n < 4e6; n++) {
    const h = new Uint8Array(await crypto.subtle.digest('SHA-256', enc.encode(challenge + ':' + n)));
    let z = 0; for (const b of h) { if (b === 0) z += 8; else { z += Math.clz32(b) - 24; break; } if (z >= bits) break; }
    if (z >= bits) { await wait(); return String(n); }
  }
  return '';
}
export async function getChallenge() {
  const r = await fetch('/api/pow', { credentials: 'same-origin' }); if (!r.ok) throw new Error('pow'); const j = await r.json(); born.set(j.challenge, performance.now()); return j;
}
