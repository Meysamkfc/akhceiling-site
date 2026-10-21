# -*- coding: utf-8 -*-
import hmac
import re
import secrets
import time
from collections import defaultdict, deque
from functools import wraps
from flask import session, request, abort, g, redirect
import config

_FA = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')


def digits(s):
    return (s or '').translate(_FA)


def clean(s, n=200):
    """strip control chars, collapse whitespace, cap length"""
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(s or ''))
    s = re.sub(r'[ \t]+', ' ', s).strip()
    return s[:n]


def clean_multiline(s, n=1500):
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(s or '')).replace('\r', '')
    return s.strip()[:n]


def norm_phone(s):
    """Iranian mobile -> 09xxxxxxxxx ; landline -> 0xxxxxxxxxx ; otherwise None"""
    d = re.sub(r'[\s\-()]', '', digits(s))
    d = re.sub(r'^(\+98|0098)', '0', d)
    if re.fullmatch(r'9\d{9}', d):
        d = '0' + d
    if re.fullmatch(r'09\d{9}', d) or re.fullmatch(r'0[1-8]\d{9}', d):
        return d
    return None


def password_error(p, phone=''):
    from hardening import password_problem
    return password_problem(p, phone)


def _password_error_legacy(p):
    if len(p) < 8:
        return 'رمز عبور باید حداقل ۸ کاراکتر باشد.'
    if not re.search(r'[A-Za-z]', p) or not re.search(r'\d', p):
        return 'رمز عبور باید هم حرف لاتین و هم عدد داشته باشد.'
    if len(p) > 128:
        return 'رمز عبور خیلی طولانی است.'
    return None


def client_ip():
    if config.TRUST_PROXY:
        xf = request.headers.get('X-Forwarded-For', '')
        if xf:
            return xf.split(',')[0].strip()[:45]
    return (request.remote_addr or '')[:45]


# ------------------------------------------------------------------ CSRF
def csrf_token():
    if 'csrf' not in session:
        session['csrf'] = secrets.token_urlsafe(32)
    return session['csrf']


def check_csrf():
    tok = request.form.get('_csrf') or request.headers.get('X-CSRF-Token') or ''
    if not tok or not hmac.compare_digest(tok, session.get('csrf', '')):
        abort(400, 'درخواست نامعتبر است. صفحه را تازه کنید و دوباره تلاش کنید.')


def same_origin_ok():
    """Reject cross-site POSTs (Origin / Fetch-Metadata)."""
    sfs = request.headers.get('Sec-Fetch-Site')
    if sfs and sfs not in ('same-origin', 'none'):
        return False
    origin = request.headers.get('Origin')
    if origin:
        from urllib.parse import urlparse
        if urlparse(origin).netloc != request.host:
            return False
    return True


# ------------------------------------------------------------------ rate limiting (in-memory, per process)
_hits = defaultdict(deque)


def hit(key, limit, window):
    """returns True if the call is allowed, False if the limit is exceeded"""
    now = time.time()
    q = _hits[key]
    while q and q[0] < now - window:
        q.popleft()
    if len(q) >= limit:
        return False
    q.append(now)
    if len(_hits) > 20000:
        for k in [k for k, v in _hits.items() if not v][:5000]:
            _hits.pop(k, None)
    return True


# ------------------------------------------------------------------ auth decorators
def login_required(*roles):
    def deco(fn):
        @wraps(fn)
        def w(*a, **kw):
            u = g.get('user')
            if not u:
                return redirect('/account/login/?next=' + request.path)
            if roles and u['role'] not in roles:
                abort(403)
            return fn(*a, **kw)
        return w
    return deco


STAFF = ('sales', 'admin')


# ------------------------------------------------------------------ failed-login memory (drives the "proof of work after 3 failures" rule)
_fails = defaultdict(deque)


def note_fail(ip):
    q = _fails[ip]
    q.append(time.time())
    while q and q[0] < time.time() - 900:
        q.popleft()


def recent_fails(ip):
    q = _fails.get(ip)
    if not q:
        return 0
    while q and q[0] < time.time() - 900:
        q.popleft()
    return len(q)
