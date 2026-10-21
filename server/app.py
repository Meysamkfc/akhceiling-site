# -*- coding: utf-8 -*-
"""AKH server: serves the static site + CRM (leads), customer accounts/orders, and the staff panel."""
import csv
import time
import hashlib
import io
import json
import os
import re
import secrets
from datetime import datetime, timedelta

from flask import (Flask, request, session, g, jsonify, render_template, redirect, abort, send_file,
                   flash, get_flashed_messages, Response)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import safe_join

import config
import db
import digest
import labels as L
import notify as nt
import security as sec
import hardening as hd
from catalog import CATALOG, BY_KEY
from jalali import jdate, jdatetime

app = Flask(__name__, static_folder=None, template_folder='templates')
app.config.update(
    SECRET_KEY=config.SECRET_KEY, SESSION_COOKIE_NAME=('__Host-akh' if config.HTTPS else 'akh_sess'), SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict', SESSION_COOKIE_SECURE=config.HTTPS, SESSION_COOKIE_PATH='/',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=config.SESSION_HOURS),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024, JSON_AS_ASCII=False,
)
app.teardown_appcontext(db.close_db)
app.jinja_env.globals.update(csrf_token=sec.csrf_token)   # visible inside imported macros too
db.init_db()
digest.start()

CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; media-src 'self'; connect-src 'self'; manifest-src 'self'; worker-src 'none'; "
       "frame-src https://maps.google.com https://www.google.com; "
       "object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; require-trusted-types-for 'script'")
if config.HTTPS:
    CSP += '; upgrade-insecure-requests'


# ------------------------------------------------------------------ request lifecycle
@app.before_request
def load_user():
    g.user = None
    uid = session.get('uid')
    if uid:
        u = db.one('SELECT * FROM users WHERE id=?', (uid,))
        fp = hashlib.sha256((request.headers.get('User-Agent', '') + '|akh').encode()).hexdigest()[:16]
        if u and u['status'] in ('active', 'pending') and (u['role'] == 'customer' or u['status'] == 'active') and session.get('fp', fp) == fp:
            g.user = u
            session['fp'] = fp                               # session is bound to the browser that logged in
        else:
            session.clear()


@app.before_request
def enforce_2fa():
    u = g.get('user')
    if config.REQUIRE_2FA and u and u['role'] in sec.STAFF and not u['totp_on'] and request.path.startswith('/admin'):
        return redirect('/account/security/')


@app.after_request
def headers(resp):
    resp.headers['Content-Security-Policy'] = CSP
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    resp.headers['X-Permitted-Cross-Domain-Policies'] = 'none'
    resp.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    resp.headers['Permissions-Policy'] = 'accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=(), interest-cohort=()'
    resp.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    if config.HTTPS:
        resp.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
    if not getattr(g, 'static_page', False):
        resp.headers['Cache-Control'] = 'no-store'
    return resp


@app.context_processor
def ctx():
    return dict(user=g.get('user'), csrf_token=sec.csrf_token, jdate=jdate, jdatetime=jdatetime, L=L, STAFF=sec.STAFF,
                messages=get_flashed_messages(with_categories=True))


def fail(code, msg):
    return render_template('error.html', code=code, msg=msg), code


@app.errorhandler(400)
def e400(e):
    if request.path.startswith('/api/'):
        return jsonify(ok=False, error=getattr(e, 'description', 'bad request')), 400
    return fail(400, getattr(e, 'description', 'درخواست نامعتبر است.'))


@app.errorhandler(403)
def e403(e):
    return fail(403, 'دسترسی به این صفحه برای شما مجاز نیست.')


@app.errorhandler(413)
def e413(e):
    return fail(413, 'حجم فایل‌ها بیش از حد مجاز است.')


@app.errorhandler(429)
def e429(e):
    if request.path.startswith('/api/'):
        return jsonify(ok=False, error='تعداد درخواست‌ها زیاد است؛ کمی بعد دوباره تلاش کنید.'), 429
    return fail(429, 'تعداد درخواست‌ها زیاد است؛ کمی بعد دوباره تلاش کنید.')


@app.errorhandler(404)
def e404(e):
    if request.path.startswith('/api/'):
        return jsonify(ok=False, error='not found'), 404
    p = config.SITE_DIR / '404.html'
    if p.exists():
        g.static_page = False
        return Response(p.read_bytes(), 404, mimetype='text/html')
    return fail(404, 'صفحه پیدا نشد.')


# ------------------------------------------------------------------ public API
BUILD_OK = set(L.BUILDINGS)
PROD_OK = set(L.PRODUCTS)
ROOM_OK = {'office', 'school', 'hospital', 'commercial', 'home', 'industrial'}


def pick_sales():
    rows = db.all_("""SELECT u.id, (SELECT COUNT(*) FROM leads l WHERE l.assigned_to=u.id AND l.status IN ('new','contacted','follow_up')) AS open_n
                      FROM users u WHERE u.role='sales' AND u.status='active' ORDER BY open_n, u.id""")
    return rows[0]['id'] if rows else None


@app.get('/api/pow')
def api_pow():
    """Issues a small proof-of-work challenge (replaces a third-party CAPTCHA; bound to the caller's IP, single use)."""
    if not sec.hit('pow:' + sec.client_ip(), 30, 600):
        abort(429)
    return jsonify(hd.pow_issue(sec.client_ip()))


@app.get('/api/csrf')
def api_csrf():
    return jsonify(token=sec.csrf_token())


@app.post('/api/lead')
def api_lead():
    if not request.is_json:
        abort(400, 'invalid content type')
    if not sec.same_origin_ok():
        abort(403)
    sec.check_csrf()
    ip = sec.client_ip()
    if not sec.hit('lead:' + ip, 6, 3600):
        abort(429)
    d = request.get_json(silent=True) or {}
    if sec.clean(d.get('website')):                        # honeypot: pretend success, store nothing
        return jsonify(ok=True, code='Q-0000')
    if not hd.pow_verify(d.get('pow_token'), d.get('pow_nonce'), ip):
        return jsonify(ok=False, error='تأیید امنیتی انجام نشد؛ صفحه را تازه کنید و دوباره تلاش کنید.'), 400
    name = sec.clean(d.get('name'), 80)
    phone = sec.norm_phone(d.get('phone'))
    city = sec.clean(d.get('city'), 60)
    errors = {}
    if len(name) < 3:
        errors['name'] = 'نام و نام خانوادگی را وارد کنید.'
    if not phone:
        errors['phone'] = 'شماره تماس معتبر وارد کنید.'
    if len(city) < 2:
        errors['city'] = 'شهر را وارد کنید.'
    source = d.get('source') if d.get('source') in L.SOURCES else 'quote'
    if source == 'assistant':                               # the assistant only needs name + phone (+ city optional)
        errors.pop('city', None)
    area = None
    if sec.clean(d.get('area')):
        try:
            area = float(sec.digits(str(d.get('area'))).replace('٫', '.').replace(',', ''))
            if not (0 < area <= 1000000):
                raise ValueError
        except ValueError:
            errors['area'] = 'متراژ معتبر وارد کنید.'
    if errors:
        return jsonify(ok=False, errors=errors), 422
    if not sec.hit('leadphone:' + phone, 4, 600):
        abort(429)
    building = d.get('building') if d.get('building') in BUILD_OK else None
    product = d.get('product') if d.get('product') in PROD_OK else None
    extra = {}
    if source == 'assistant':
        room = d.get('room')
        extra = {'room': room if room in ROOM_OK else '', 'suggestion': sec.clean(d.get('suggestion'), 80), 'sample': sec.clean(d.get('sample'), 40)}
    code = db.next_code('Q')
    assigned = pick_sales()
    lid = db.run("""INSERT INTO leads(code,source,name,phone,company,city,building,product,area,descr,extra,assigned_to,ip)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                 (code, source, name, phone, sec.clean(d.get('company'), 80), city, building, product, area,
                  sec.clean_multiline(d.get('desc'), 1000), json.dumps(extra, ensure_ascii=False), assigned, ip))
    sc, label, why = hd.score_lead(dict(area=area, product=product, phone=phone, city=city, desc=d.get('desc') or '', source=source, company=d.get('company')))
    db.run('UPDATE leads SET score=?, priority=?, why=? WHERE id=?', (sc, label, '، '.join(why), lid))
    PL = {'hot': 'داغ', 'warm': 'گرم', 'cold': 'سرد'}
    nt.notify('درخواست جدید %s [%s]' % (code, PL[label]), '🔔 درخواست جدید %s — اولویت: %s (امتیاز %d)\nمنبع: %s\nنام: %s\nتلفن: %s\nشهر: %s%s%s\n%s/admin/leads/%d' % (
        code, PL[label], sc, L.SOURCES[source], name, phone, city or '—', ('\nمتراژ: %g' % area) if area else '',
        ('\nمحصول: ' + L.PRODUCTS[product]) if product else '', config.BASE_URL, lid))
    return jsonify(ok=True, code=code)


@app.post('/api/hit')
def api_hit():
    """Privacy-friendly page-view counter: only (day, path) counters. No cookie, no IP, no user id is stored."""
    if not sec.same_origin_ok():
        return ('', 204)
    d = request.get_json(silent=True) or {}
    path = str(d.get('p') or '')[:120]
    if not re.fullmatch(r'/[a-z0-9\-/]*', path) or path.startswith(('/account', '/admin', '/api', '/files')):
        return ('', 204)
    target = config.SITE_DIR / path.strip('/') / 'index.html'
    if not target.is_file():
        return ('', 204)
    if not sec.hit('hit:' + sec.client_ip(), 200, 3600):
        return ('', 204)
    day = datetime.now().strftime('%Y-%m-%d')
    db.run('INSERT INTO pageviews(day,path,n) VALUES(?,?,1) ON CONFLICT(day,path) DO UPDATE SET n=n+1', (day, path))
    return ('', 204)


@app.get('/api/catalog')
def api_catalog():
    return jsonify(CATALOG)


# ------------------------------------------------------------------ accounts
def safe_next(n):
    return n if n and re.fullmatch(r'/(account|admin)/[A-Za-z0-9_\-/?=&.]*', n) and '//' not in n else None


@app.route('/account/register/', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect('/account/')
    form, errors = {}, []
    if request.method == 'POST':
        sec.check_csrf()
        if not sec.hit('reg:' + sec.client_ip(), 5, 3600):
            abort(429)
        form = {k: sec.clean(request.form.get(k), 80) for k in ('name', 'company')}
        ident = sec.clean(request.form.get('identifier'), 120)
        form['identifier'] = ident
        form['country'] = sec.clean(request.form.get('country'), 40) or 'ایران'
        city_sel = sec.clean(request.form.get('city_ir'), 60)
        form['city'] = sec.clean(request.form.get('city_other'), 60) if (form['country'] != 'ایران' or city_sel == 'سایر') else city_sel
        job_sel = sec.clean(request.form.get('job'), 60)
        form['job'] = sec.clean(request.form.get('job_other'), 60) if job_sel == 'سایر' else job_sel
        phone = email = None
        if '@' in ident:
            if re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', ident): email = ident.lower()
            else: errors.append('ایمیل معتبر نیست.')
        elif ident:
            phone = sec.norm_phone(ident)
            if not phone: errors.append('ایمیل یا شماره موبایل معتبر وارد کنید (مثل ۰۹۱۲۳۴۵۶۷۸۹).')
        else:
            errors.append('ایمیل یا شماره موبایل را وارد کنید.')
        pw, pw2 = request.form.get('password', ''), request.form.get('password2', '')
        if sec.clean(request.form.get('website')):
            abort(400)
        if not hd.pow_verify(request.form.get('pow_token'), request.form.get('pow_nonce'), sec.client_ip()):
            errors.append('تأیید امنیتی انجام نشد؛ جاوااسکریپت را فعال کنید و دوباره تلاش کنید.')
        if len(form['name']) < 3: errors.append('نام و نام خانوادگی را وارد کنید.')
        if len(form['city']) < 2: errors.append('شهر را وارد کنید.')
        pe = hd.password_problem(pw, phone or '')
        if pe: errors.append(pe)
        elif pw != pw2: errors.append('تکرار رمز عبور یکسان نیست.')
        dup = (phone and db.one('SELECT 1 FROM users WHERE phone=?', (phone,))) or (email and db.one('SELECT 1 FROM users WHERE email=?', (email,)))
        if not errors and dup:
            # do not reveal whether the account exists (account enumeration): same answer, nothing created
            flash('ثبت‌نام انجام شد. پس از تأیید کارشناس فروش حساب شما فعال می‌شود. اگر قبلاً ثبت‌نام کرده‌اید، با همان ایمیل/شماره و رمز خود وارد شوید.', 'ok')
            return redirect('/account/login/')
        if not errors:
            uid = db.run("INSERT INTO users(role,name,company,phone,email,city,job,country,pass_hash,status) VALUES('customer',?,?,?,?,?,?,?,?,'pending')",
                         (form['name'], form['company'], phone, email, form['city'], form['job'], form['country'], generate_password_hash(pw)))
            db.audit(uid, 'register', phone or email, sec.client_ip())
            nt.notify('ثبت‌نام مشتری جدید', '👤 درخواست عضویت جدید\nنام: %s\nشرکت: %s\nایمیل/موبایل: %s\nکشور: %s\nشهر: %s\nشغل: %s\n%s/admin/customers/%d' % (
                form['name'], form['company'] or '—', phone or email, form['country'], form['city'], form['job'] or '—', config.BASE_URL, uid))
            flash('ثبت‌نام انجام شد. پس از تأیید کارشناس فروش، حساب شما فعال می‌شود و می‌توانید وارد شوید.', 'ok')
            return redirect('/account/login/')
    return render_template('account/register.html', form=form, errors=errors, countries=L.COUNTRIES, cities_iran=L.CITIES_IRAN, jobs=L.JOBS)


@app.route('/account/login/', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect('/admin/' if g.user['role'] in sec.STAFF else '/account/')
    error = None
    if request.method == 'POST':
        sec.check_csrf()
        ip = sec.client_ip()
        ident = sec.clean(request.form.get('identifier'), 120)
        phone = sec.norm_phone(ident) if '@' not in ident else None
        email = ident.lower() if '@' in ident else None
        if not sec.hit('login:' + ip, 20, 600):
            abort(429)
        if sec.recent_fails(ip) >= 3 and not hd.pow_verify(request.form.get('pow_token'), request.form.get('pow_nonce'), ip):
            return render_template('account/login.html', error='برای ادامه، تأیید امنیتی لازم است؛ صفحه را تازه کنید و دوباره تلاش کنید.')
        u = db.one('SELECT * FROM users WHERE phone=?', (phone,)) if phone else (db.one('SELECT * FROM users WHERE email=?', (email,)) if email else None)
        pw = request.form.get('password', '')
        now = datetime.now()
        if u and u['locked_until'] and datetime.strptime(u['locked_until'], '%Y-%m-%d %H:%M:%S') > now:
            error = 'به‌دلیل تلاش‌های ناموفق، ورود تا ۱۵ دقیقه مسدود شده است.'
        else:
            ok = check_password_hash(u['pass_hash'], pw) if u else check_password_hash(generate_password_hash('x'), pw)  # constant-ish time
            if not (u and ok):
                if u:
                    f = u['failed'] + 1
                    lock = (now + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S') if f >= 5 else None
                    db.run('UPDATE users SET failed=?, locked_until=? WHERE id=?', (0 if lock else f, lock, u['id']))
                sec.note_fail(ip)
                db.audit(u['id'] if u else None, 'login_failed', ident, ip)
                error = 'ایمیل/شماره موبایل یا رمز عبور درست نیست.'
            elif u['status'] == 'rejected':
                error = 'درخواست عضویت شما تأیید نشد. با کارشناس فروش تماس بگیرید.'
            elif u['status'] == 'disabled':
                error = 'این حساب غیرفعال شده است.'
            else:
                nxt = safe_next(request.args.get('next'))
                if u['totp_on']:
                    session.clear()
                    session['pre'] = [u['id'], int(time.time()), nxt or '']
                    return redirect('/account/2fa/')
                return finish_login(u, nxt)
    return render_template('account/login.html', error=error)


def finish_login(u, nxt=None):
    session.clear()                                           # new session id after login (fixation)
    session['uid'] = u['id']
    session['fp'] = hashlib.sha256((request.headers.get('User-Agent', '') + '|akh').encode()).hexdigest()[:16]
    session.permanent = True
    db.run("UPDATE users SET failed=0, locked_until=NULL, last_login=datetime('now','localtime') WHERE id=?", (u['id'],))
    db.audit(u['id'], 'login', '2fa' if u['totp_on'] else '', sec.client_ip())
    return redirect(nxt or ('/admin/' if u['role'] in sec.STAFF else '/account/'))


@app.route('/account/2fa/', methods=['GET', 'POST'])
def twofa_verify():
    pre = session.get('pre')
    if not pre or time.time() - pre[1] > 300:
        session.clear()
        return redirect('/account/login/')
    u = db.one('SELECT * FROM users WHERE id=?', (pre[0],))
    error = None
    if request.method == 'POST':
        sec.check_csrf()
        if not sec.hit('2fa:%d' % pre[0], 6, 600):
            abort(429)
        if u and u['totp_on'] and hd.totp_verify(u['totp_secret'], request.form.get('code', '')):
            return finish_login(u, pre[2] or None)
        sec.note_fail(sec.client_ip())
        db.audit(pre[0], '2fa_failed', '', sec.client_ip())
        error = 'کد نادرست است.'
    return render_template('account/2fa.html', error=error)


@app.route('/account/forgot/', methods=['GET', 'POST'])
def forgot_start():
    if g.user:
        return redirect('/account/')
    error = None
    if request.method == 'POST':
        sec.check_csrf()
        ip = sec.client_ip()
        if not sec.hit('forgot:' + ip, 10, 600):
            abort(429)
        ident = sec.clean(request.form.get('identifier'), 120)
        phone = sec.norm_phone(ident) if '@' not in ident else None
        email = ident.lower() if '@' in ident else None
        u = db.one('SELECT * FROM users WHERE phone=?', (phone,)) if phone else (db.one('SELECT * FROM users WHERE email=?', (email,)) if email else None)
        # same response whether or not the account exists (no account enumeration)
        session['frg'] = [u['id'] if u else 0, int(time.time())]
        return redirect('/account/forgot/question/')
    return render_template('account/forgot.html', error=error)


@app.route('/account/forgot/question/', methods=['GET', 'POST'])
def forgot_question():
    frg = session.get('frg')
    if not frg or time.time() - frg[1] > 600:
        session.pop('frg', None)
        return redirect('/account/forgot/')
    u = db.one('SELECT * FROM users WHERE id=?', (frg[0],)) if frg[0] else None
    error = None
    if request.method == 'POST':
        sec.check_csrf()
        ip = sec.client_ip()
        if not sec.hit('forgot_q:' + ip, 10, 600):
            abort(429)
        now = datetime.now()
        if u and u['locked_until'] and datetime.strptime(u['locked_until'], '%Y-%m-%d %H:%M:%S') > now:
            error = 'به‌دلیل تلاش‌های ناموفق، این مسیر تا ۱۵ دقیقه مسدود شده است.'
        else:
            answer = sec.clean(request.form.get('job'), 60)
            ok = bool(u and u['job'] and answer == u['job'])
            if not ok:
                if u:
                    f = u['failed'] + 1
                    lock = (now + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S') if f >= 5 else None
                    db.run('UPDATE users SET failed=?, locked_until=? WHERE id=?', (0 if lock else f, lock, u['id']))
                db.audit(u['id'] if u else None, 'forgot_failed', '', ip)
                error = 'پاسخ درست نیست.'
            else:
                session.pop('frg', None)
                session['frg_ok'] = [u['id'], int(time.time())]
                db.run('UPDATE users SET failed=0, locked_until=NULL WHERE id=?', (u['id'],))
                return redirect('/account/forgot/reset/')
    return render_template('account/forgot_question.html', error=error, jobs=L.JOBS)


@app.route('/account/forgot/reset/', methods=['GET', 'POST'])
def forgot_reset():
    ok = session.get('frg_ok')
    if not ok or time.time() - ok[1] > 600:
        session.pop('frg_ok', None)
        return redirect('/account/forgot/')
    errors = []
    if request.method == 'POST':
        sec.check_csrf()
        u = db.one('SELECT * FROM users WHERE id=?', (ok[0],))
        pw, pw2 = request.form.get('password', ''), request.form.get('password2', '')
        pe = hd.password_problem(pw, (u['phone'] if u else '') or '')
        if pe: errors.append(pe)
        elif pw != pw2: errors.append('تکرار رمز عبور یکسان نیست.')
        if not errors and u:
            db.run('UPDATE users SET pass_hash=?, failed=0, locked_until=NULL WHERE id=?', (generate_password_hash(pw), u['id']))
            db.audit(u['id'], 'password_reset', '', sec.client_ip())
            session.pop('frg_ok', None)
            flash('رمز عبور تغییر کرد. با رمز جدید وارد شوید.', 'ok')
            return redirect('/account/login/')
    return render_template('account/forgot_reset.html', errors=errors)


@app.route('/account/security/', methods=['GET', 'POST'])
@sec.login_required()
def security_page():
    u = g.user
    errors, qr, secret = [], None, None
    if request.method == 'POST':
        sec.check_csrf()
        act = request.form.get('action')
        if act == 'enable' and not u['totp_on']:
            sc = session.get('totp_new')
            if sc and hd.totp_verify(sc, request.form.get('code', '')):
                db.run('UPDATE users SET totp_secret=?, totp_on=1 WHERE id=?', (sc, u['id']))
                session.pop('totp_new', None)
                db.audit(u['id'], '2fa_enabled', '', sec.client_ip())
                flash('ورود دومرحله‌ای فعال شد.', 'ok')
                return redirect('/account/security/')
            errors.append('کد درست نیست؛ دوباره از برنامه احراز هویت بخوانید.')
        elif act == 'disable' and u['totp_on']:
            if not check_password_hash(u['pass_hash'], request.form.get('password', '')) or not hd.totp_verify(u['totp_secret'], request.form.get('code', '')):
                errors.append('رمز عبور یا کد درست نیست.')
            elif u['role'] in sec.STAFF and config.REQUIRE_2FA:
                errors.append('برای کارکنان ورود دومرحله‌ای اجباری است.')
            else:
                db.run('UPDATE users SET totp_secret=NULL, totp_on=0 WHERE id=?', (u['id'],))
                db.audit(u['id'], '2fa_disabled', '', sec.client_ip())
                flash('ورود دومرحله‌ای غیرفعال شد.', 'ok')
                return redirect('/account/security/')
    if not u['totp_on']:
        secret = session.get('totp_new') or hd.totp_secret()
        session['totp_new'] = secret
        qr = hd.qr_svg(hd.totp_uri(secret, u['phone'] or u['email'] or ('#%d' % u['id'])))
    return render_template('account/security.html', errors=errors, qr=qr, secret=secret, base=('admin/_layout.html' if u['role'] in sec.STAFF else 'account/_layout.html'))


@app.post('/account/logout/')
def logout():
    sec.check_csrf()
    session.clear()
    return redirect('/')


@app.get('/account/')
@sec.login_required('customer')
def panel():
    uid = g.user['id']
    orders = db.all_('SELECT * FROM orders WHERE customer_id=? ORDER BY id DESC LIMIT 5', (uid,))
    counts = {r['status']: r['n'] for r in db.all_('SELECT status, COUNT(*) n FROM orders WHERE customer_id=? GROUP BY status', (uid,))}
    return render_template('account/panel.html', orders=orders, counts=counts)


@app.route('/account/profile/', methods=['GET', 'POST'])
@sec.login_required('customer')
def profile():
    errors, done = [], False
    if request.method == 'POST':
        sec.check_csrf()
        if request.form.get('action') == 'profile':
            name, company, email, city, job = (sec.clean(request.form.get(k), 80) for k in ('name', 'company', 'email', 'city', 'job'))
            if len(name) < 3: errors.append('نام را وارد کنید.')
            if email and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email): errors.append('ایمیل معتبر نیست.')
            email = email.lower() or None
            if email and not errors and db.one('SELECT 1 FROM users WHERE email=? AND id<>?', (email, g.user['id'])):
                errors.append('این ایمیل قبلاً برای حساب دیگری ثبت شده است.')
            if not errors:
                db.run('UPDATE users SET name=?,company=?,email=?,city=?,job=? WHERE id=?', (name, company, email, city, job, g.user['id']))
                flash('مشخصات ذخیره شد.', 'ok')
                return redirect('/account/profile/')
        elif request.form.get('action') == 'password':
            cur, new = request.form.get('current', ''), request.form.get('password', '')
            if not check_password_hash(g.user['pass_hash'], cur): errors.append('رمز فعلی درست نیست.')
            pe = sec.password_error(new)
            if pe: errors.append(pe)
            elif new != request.form.get('password2', ''): errors.append('تکرار رمز یکسان نیست.')
            if not errors:
                db.run('UPDATE users SET pass_hash=? WHERE id=?', (generate_password_hash(new), g.user['id']))
                db.audit(g.user['id'], 'password_change', '', sec.client_ip())
                flash('رمز عبور تغییر کرد.', 'ok')
                return redirect('/account/profile/')
    return render_template('account/profile.html', errors=errors)


# ------------------------------------------------------------------ customer orders
def save_upload(fs, order_id, user, side, kind):
    """validate + store one uploaded file privately. returns error text or None"""
    if not fs or not fs.filename:
        return None
    name = os.path.basename(fs.filename.replace('\\', '/'))
    ext = os.path.splitext(name)[1].lower()
    if ext not in config.ALLOWED_UPLOADS:
        return 'فرمت فایل مجاز نیست (فقط PDF، JPG و PNG).'
    data = fs.read(config.MAX_UPLOAD_BYTES + 1)
    if len(data) > config.MAX_UPLOAD_BYTES:
        return 'حجم هر فایل حداکثر ۵ مگابایت است.'
    if not data.startswith(config.ALLOWED_UPLOADS[ext]):
        return 'محتوای فایل با فرمت آن هم‌خوانی ندارد.'
    data, bad = hd.sanitize_upload(ext, data)
    if bad:
        return bad
    stored = secrets.token_hex(16) + ext
    (config.UPLOADS / stored).write_bytes(data)
    mime = {'.pdf': 'application/pdf', '.png': 'image/png'}.get(ext, 'image/jpeg')
    db.run('INSERT INTO files(order_id,uploader_id,side,kind,orig_name,stored_name,mime,size) VALUES(?,?,?,?,?,?,?,?)',
           (order_id, user['id'], side, kind, sec.clean(name, 120), stored, mime, len(data)))
    return None


def own_order(code):
    o = db.one('SELECT * FROM orders WHERE code=?', (code,))
    if not o or (g.user['role'] == 'customer' and o['customer_id'] != g.user['id']):
        abort(404)                                                    # 404 (not 403) so order codes can't be probed
    return o


def require_active_customer():
    if g.user['status'] != 'active':
        return render_template('account/pending.html')
    return None


@app.get('/account/orders/')
@sec.login_required('customer')
def orders_list():
    p = require_active_customer()
    if p: return p
    rows = db.all_('SELECT * FROM orders WHERE customer_id=? ORDER BY id DESC', (g.user['id'],))
    return render_template('account/orders.html', orders=rows)


@app.route('/account/orders/new/', methods=['GET', 'POST'])
@sec.login_required('customer')
def order_new():
    p = require_active_customer()
    if p: return p
    errors = []
    if request.method == 'POST':
        sec.check_csrf()
        if not sec.hit('order:%d' % g.user['id'], 15, 3600):
            abort(429)
        keys = request.form.getlist('item_key[]')[:40]
        opts = request.form.getlist('option[]')[:40]
        qtys = request.form.getlist('qty[]')[:40]
        items = []
        for i, k in enumerate(keys):
            k = k.strip()
            if not k:
                continue
            it = BY_KEY.get(k)
            if not it:
                errors.append('یکی از اقلام نامعتبر است.'); continue
            opt = sec.clean(opts[i] if i < len(opts) else '', 80)
            if it['options'] and opt not in it['options']:
                errors.append('گزینه «%s» برای %s معتبر نیست.' % (opt or '—', it['title'])); continue
            if not it['options']:
                opt = ''
            try:
                q = int(sec.digits(qtys[i] if i < len(qtys) else '').replace(',', ''))
                if not (1 <= q <= 1000000): raise ValueError
            except ValueError:
                errors.append('تعداد «%s» معتبر نیست.' % it['title']); continue
            items.append((k, it['title'], opt, q, it['unit']))
        if not items and not errors:
            errors.append('حداقل یک قلم کالا اضافه کنید.')
        city = sec.clean(request.form.get('city'), 60)
        address = sec.clean_multiline(request.form.get('address'), 400)
        if len(city) < 2: errors.append('شهر تحویل را وارد کنید.')
        files = [f for f in request.files.getlist('files') if f and f.filename][:3]
        if not errors:
            code = db.next_code('AKH')
            oid = db.run('INSERT INTO orders(code,customer_id,city,address,desired_date,note,assigned_to) VALUES(?,?,?,?,?,?,?)',
                         (code, g.user['id'], city, address, sec.clean(request.form.get('desired_date'), 40),
                          sec.clean_multiline(request.form.get('note'), 1000), pick_sales()))
            for it in items:
                db.run('INSERT INTO order_items(order_id,item_key,title,option,qty,unit) VALUES(?,?,?,?,?,?)', (oid,) + it)
            ferr = [e for e in (save_upload(f, oid, g.user, 'customer', 'invoice' if request.form.get('file_kind') == 'invoice' else 'plan') for f in files) if e]
            for e in ferr:
                flash(e, 'err')
            nt.notify('سفارش جدید ' + code, '🛒 سفارش جدید %s\nمشتری: %s (%s)\nاقلام: %d\nشهر: %s\n%s/admin/orders/%s' % (
                code, g.user['name'], g.user['phone'] or g.user['email'] or '—', len(items), city, config.BASE_URL, code))
            flash('سفارش شما ثبت شد (کد %s). کارشناس فروش بررسی و با شما تماس می‌گیرد.' % code, 'ok')
            return redirect('/account/orders/%s/' % code)
    return render_template('account/order_new.html', catalog=CATALOG, errors=errors, f=request.form)


@app.get('/account/orders/<code>/')
@sec.login_required('customer')
def order_detail(code):
    o = own_order(code)
    items = db.all_('SELECT * FROM order_items WHERE order_id=?', (o['id'],))
    files = db.all_('SELECT * FROM files WHERE order_id=? ORDER BY id', (o['id'],))
    msgs = db.all_("SELECT n.*, u.name AS uname FROM notes n LEFT JOIN users u ON u.id=n.user_id WHERE n.entity='order' AND n.entity_id=? AND n.kind='public' ORDER BY n.id", (o['id'],))
    return render_template('account/order_detail.html', o=o, items=items, files=files, msgs=msgs)


@app.post('/account/orders/<code>/upload/')
@sec.login_required('customer')
def order_upload(code):
    sec.check_csrf()
    o = own_order(code)
    if not sec.hit('upl:%d' % g.user['id'], 20, 3600):
        abort(429)
    kind = request.form.get('kind') if request.form.get('kind') in ('invoice', 'plan', 'other') else 'invoice'
    n = 0
    for f in [f for f in request.files.getlist('files') if f and f.filename][:3]:
        e = save_upload(f, o['id'], g.user, 'customer', kind)
        flash(e, 'err') if e else None
        n += 0 if e else 1
    if n:
        db.run("UPDATE orders SET updated_at=datetime('now','localtime') WHERE id=?", (o['id'],))
        nt.notify('فایل جدید سفارش ' + code, '📎 مشتری %s برای سفارش %s فایل بارگذاری کرد.\n%s/admin/orders/%s' % (g.user['name'], code, config.BASE_URL, code))
        flash('فایل ارسال شد.', 'ok')
    return redirect('/account/orders/%s/' % code)


@app.get('/files/<int:fid>/')
@sec.login_required()
def file_get(fid):
    f = db.one('SELECT f.*, o.customer_id FROM files f JOIN orders o ON o.id=f.order_id WHERE f.id=?', (fid,))
    if not f:
        abort(404)
    u = g.user
    if u['role'] == 'customer' and f['customer_id'] != u['id']:
        abort(404)
    path = config.UPLOADS / f['stored_name']
    if not path.is_file():
        abort(404)
    resp = send_file(str(path), mimetype=f['mime'], as_attachment=True, download_name=f['orig_name'])
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp


# ------------------------------------------------------------------ staff panel
def log_note(entity, eid, kind, text):
    db.run('INSERT INTO notes(entity,entity_id,user_id,kind,text) VALUES(?,?,?,?,?)', (entity, eid, g.user['id'], kind, text))


@app.get('/admin/')
@sec.login_required(*sec.STAFF)
def admin_home():
    st = {r['status']: r['n'] for r in db.all_('SELECT status, COUNT(*) n FROM leads GROUP BY status')}
    mine = db.one("SELECT COUNT(*) n FROM leads WHERE assigned_to=? AND status IN ('new','contacted','follow_up')", (g.user['id'],))['n']
    pend = db.one("SELECT COUNT(*) n FROM users WHERE role='customer' AND status='pending'")['n']
    on = db.one("SELECT COUNT(*) n FROM orders WHERE status IN ('new','reviewing')")['n']
    recent = db.all_("""SELECT l.*, u.name AS aname FROM leads l LEFT JOIN users u ON u.id=l.assigned_to ORDER BY l.id DESC LIMIT 8""")
    v7 = db.one("SELECT COALESCE(SUM(n),0) n FROM pageviews WHERE day >= date('now','localtime','-6 days')")['n']
    v30 = db.one("SELECT COALESCE(SUM(n),0) n FROM pageviews WHERE day >= date('now','localtime','-29 days')")['n']
    top = db.all_("SELECT path, SUM(n) n FROM pageviews WHERE day >= date('now','localtime','-29 days') GROUP BY path ORDER BY n DESC LIMIT 8")
    return render_template('admin/home.html', st=st, mine=mine, pend=pend, open_orders=on, recent=recent, v7=v7, v30=v30, top=top)


@app.get('/admin/leads/')
@sec.login_required(*sec.STAFF)
def admin_leads():
    status = request.args.get('status', '')
    src = request.args.get('source', '')
    q = sec.clean(request.args.get('q'), 60)
    mine = request.args.get('mine') == '1'
    pri = request.args.get('priority', '')
    sql, args = 'SELECT l.*, u.name AS aname FROM leads l LEFT JOIN users u ON u.id=l.assigned_to WHERE 1=1', []
    if pri in ('hot', 'warm', 'cold'):
        sql += ' AND l.priority=?'
        args.append(pri)
    if status in L.LS: sql += ' AND l.status=?'; args.append(status)
    if src in L.SOURCES: sql += ' AND l.source=?'; args.append(src)
    if mine: sql += ' AND l.assigned_to=?'; args.append(g.user['id'])
    if q:
        sql += ' AND (l.name LIKE ? OR l.phone LIKE ? OR l.code LIKE ? OR l.city LIKE ?)'
        args += ['%' + q + '%'] * 4
    order = 'l.score DESC, l.id DESC' if request.args.get('sort') == 'priority' else 'l.id DESC'
    rows = db.all_(sql + ' ORDER BY ' + order + ' LIMIT 200', args)
    return render_template('admin/leads.html', leads=rows, f=dict(status=status, source=src, q=q, mine=mine, priority=pri, sort=request.args.get('sort', '')))


@app.route('/admin/leads/<int:lid>/', methods=['GET', 'POST'])
@sec.login_required(*sec.STAFF)
def admin_lead(lid):
    lead = db.one('SELECT * FROM leads WHERE id=?', (lid,))
    if not lead:
        abort(404)
    if request.method == 'POST':
        sec.check_csrf()
        act = request.form.get('action')
        if act == 'status' and request.form.get('status') in L.LS:
            db.run("UPDATE leads SET status=?, updated_at=datetime('now','localtime') WHERE id=?", (request.form['status'], lid))
            log_note('lead', lid, 'status', 'وضعیت: ' + L.LS[request.form['status']])
        elif act == 'assign':
            uid = request.form.get('assigned_to', type=int)
            if uid and db.one("SELECT 1 FROM users WHERE id=? AND role IN ('sales','admin') AND status='active'", (uid,)):
                db.run("UPDATE leads SET assigned_to=?, updated_at=datetime('now','localtime') WHERE id=?", (uid, lid))
                log_note('lead', lid, 'status', 'ارجاع به: ' + db.one('SELECT name FROM users WHERE id=?', (uid,))['name'])
        elif act == 'note' and sec.clean_multiline(request.form.get('text'), 800):
            log_note('lead', lid, 'note', sec.clean_multiline(request.form.get('text'), 800))
        elif act == 'call':
            outcome = request.form.get('outcome') if request.form.get('outcome') in L.CALL_OUTCOMES else ''
            txt = '📞 ' + outcome + ((' — ' + sec.clean(request.form.get('text'), 300)) if sec.clean(request.form.get('text')) else '')
            log_note('lead', lid, 'call', txt)
            if lead['status'] == 'new':
                db.run("UPDATE leads SET status='contacted', updated_at=datetime('now','localtime') WHERE id=?", (lid,))
        db.audit(g.user['id'], 'lead_' + str(act), str(lid), sec.client_ip())
        return redirect('/admin/leads/%d/' % lid)
    notes = db.all_("SELECT n.*, u.name AS uname FROM notes n LEFT JOIN users u ON u.id=n.user_id WHERE entity='lead' AND entity_id=? ORDER BY n.id DESC", (lid,))
    staff = db.all_("SELECT id,name FROM users WHERE role IN ('sales','admin') AND status='active' ORDER BY name")
    extra = json.loads(lead['extra'] or '{}')
    return render_template('admin/lead.html', lead=lead, notes=notes, staff=staff, extra=extra)


@app.get('/admin/customers/')
@sec.login_required(*sec.STAFF)
def admin_customers():
    st = request.args.get('status', '')
    sql, args = "SELECT * FROM users WHERE role='customer'", []
    if st in L.US: sql += ' AND status=?'; args.append(st)
    return render_template('admin/customers.html', rows=db.all_(sql + ' ORDER BY (status=\'pending\') DESC, id DESC LIMIT 300', args), st=st)


@app.route('/admin/customers/<int:uid>/', methods=['GET', 'POST'])
@sec.login_required(*sec.STAFF)
def admin_customer(uid):
    c = db.one("SELECT * FROM users WHERE id=? AND role='customer'", (uid,))
    if not c:
        abort(404)
    if request.method == 'POST':
        sec.check_csrf()
        act = request.form.get('action')
        m = {'approve': 'active', 'reject': 'rejected', 'disable': 'disabled', 'enable': 'active'}
        if act in m:
            db.run('UPDATE users SET status=? WHERE id=?', (m[act], uid))
            log_note('customer', uid, 'status', 'وضعیت حساب: ' + L.US[m[act]])
            db.audit(g.user['id'], 'customer_' + act, str(uid), sec.client_ip())
        elif act == 'note' and sec.clean_multiline(request.form.get('text'), 800):
            log_note('customer', uid, 'note', sec.clean_multiline(request.form.get('text'), 800))
        return redirect('/admin/customers/%d/' % uid)
    orders = db.all_('SELECT * FROM orders WHERE customer_id=? ORDER BY id DESC', (uid,))
    notes = db.all_("SELECT n.*, u.name AS uname FROM notes n LEFT JOIN users u ON u.id=n.user_id WHERE entity='customer' AND entity_id=? ORDER BY n.id DESC", (uid,))
    return render_template('admin/customer.html', c=c, orders=orders, notes=notes)


@app.get('/admin/orders/')
@sec.login_required(*sec.STAFF)
def admin_orders():
    st = request.args.get('status', '')
    sql, args = 'SELECT o.*, u.name AS cname, u.company AS ccompany, u.phone AS cphone FROM orders o JOIN users u ON u.id=o.customer_id WHERE 1=1', []
    if st in L.OS: sql += ' AND o.status=?'; args.append(st)
    return render_template('admin/orders.html', rows=db.all_(sql + ' ORDER BY o.id DESC LIMIT 300', args), st=st)


@app.route('/admin/orders/<code>/', methods=['GET', 'POST'])
@sec.login_required(*sec.STAFF)
def admin_order(code):
    o = db.one('SELECT o.*, u.name AS cname, u.company AS ccompany, u.phone AS cphone, u.email AS cemail FROM orders o JOIN users u ON u.id=o.customer_id WHERE o.code=?', (code,))
    if not o:
        abort(404)
    if request.method == 'POST':
        sec.check_csrf()
        act = request.form.get('action')
        if act == 'status' and request.form.get('status') in L.OS:
            db.run("UPDATE orders SET status=?, updated_at=datetime('now','localtime') WHERE id=?", (request.form['status'], o['id']))
            log_note('order', o['id'], 'status', 'وضعیت: ' + L.OS[request.form['status']])
        elif act in ('note', 'public') and sec.clean_multiline(request.form.get('text'), 800):
            log_note('order', o['id'], 'public' if act == 'public' else 'note', sec.clean_multiline(request.form.get('text'), 800))
        elif act == 'file':
            kind = 'proforma' if request.form.get('kind') == 'proforma' else 'other'
            for f in [f for f in request.files.getlist('files') if f and f.filename][:3]:
                e = save_upload(f, o['id'], g.user, 'staff', kind)
                flash(e, 'err') if e else flash('فایل برای مشتری ارسال شد.', 'ok')
            if kind == 'proforma':
                db.run("UPDATE orders SET status='proforma_sent', updated_at=datetime('now','localtime') WHERE id=? AND status IN ('new','reviewing')", (o['id'],))
        db.audit(g.user['id'], 'order_' + str(act), code, sec.client_ip())
        return redirect('/admin/orders/%s/' % code)
    items = db.all_('SELECT * FROM order_items WHERE order_id=?', (o['id'],))
    files = db.all_('SELECT * FROM files WHERE order_id=? ORDER BY id', (o['id'],))
    notes = db.all_("SELECT n.*, u.name AS uname FROM notes n LEFT JOIN users u ON u.id=n.user_id WHERE entity='order' AND entity_id=? ORDER BY n.id DESC", (o['id'],))
    return render_template('admin/order.html', o=o, items=items, files=files, notes=notes)


@app.get('/admin/audit/')
@sec.login_required('admin')
def admin_audit():
    rows = db.all_("SELECT a.*, u.name AS uname FROM audit a LEFT JOIN users u ON u.id=a.user_id ORDER BY a.id DESC LIMIT 300")
    return render_template('admin/audit.html', rows=rows)


@app.route('/admin/users/', methods=['GET', 'POST'])
@sec.login_required('admin')
def admin_users():
    errors = []
    if request.method == 'POST':
        sec.check_csrf()
        act = request.form.get('action')
        if act == 'create':
            name = sec.clean(request.form.get('name'), 80)
            phone = sec.norm_phone(request.form.get('phone'))
            role = request.form.get('role') if request.form.get('role') in ('sales', 'admin') else 'sales'
            pw = request.form.get('password', '')
            if len(name) < 3: errors.append('نام را وارد کنید.')
            if not phone: errors.append('شماره موبایل معتبر نیست.')
            pe = sec.password_error(pw)
            if pe: errors.append(pe)
            if phone and db.one('SELECT 1 FROM users WHERE phone=?', (phone,)): errors.append('این شماره قبلاً ثبت شده است.')
            if not errors:
                db.run("INSERT INTO users(role,name,phone,pass_hash,status) VALUES(?,?,?,?,'active')", (role, name, phone, generate_password_hash(pw)))
                db.audit(g.user['id'], 'user_create', phone, sec.client_ip())
                flash('کاربر ساخته شد.', 'ok')
                return redirect('/admin/users/')
        elif act in ('disable', 'enable'):
            uid = request.form.get('uid', type=int)
            if uid and uid != g.user['id']:
                db.run("UPDATE users SET status=? WHERE id=? AND role IN ('sales','admin')", ('disabled' if act == 'disable' else 'active', uid))
                return redirect('/admin/users/')
    return render_template('admin/users.html', rows=db.all_("SELECT * FROM users WHERE role IN ('sales','admin') ORDER BY id"), errors=errors)


def _csv_safe(v):
    s = '' if v is None else str(v)
    return "'" + s if s[:1] in ('=', '+', '-', '@', '\t', '\r') else s


def _csv(name, header, rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    for r in rows:
        w.writerow([_csv_safe(x) for x in r])
    return Response('﻿' + buf.getvalue(), mimetype='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename=%s' % name})


@app.get('/admin/export/leads.csv')
@sec.login_required(*sec.STAFF)
def export_leads():
    rows = db.all_('SELECT l.*, u.name AS aname FROM leads l LEFT JOIN users u ON u.id=l.assigned_to ORDER BY l.id')
    return _csv('leads.csv', ['کد', 'تاریخ', 'منبع', 'نام', 'تلفن', 'شرکت', 'شهر', 'نوع ساختمان', 'محصول', 'متراژ', 'وضعیت', 'مسئول', 'توضیحات'],
                [(r['code'], jdatetime(r['created_at']), L.SOURCES.get(r['source']), r['name'], r['phone'], r['company'], r['city'], L.BUILDINGS.get(r['building'], ''),
                  L.PRODUCTS.get(r['product'], ''), r['area'], L.LS.get(r['status']), r['aname'], r['descr']) for r in rows])


@app.get('/admin/export/orders.csv')
@sec.login_required(*sec.STAFF)
def export_orders():
    rows = db.all_('SELECT o.*, u.name AS cname, u.company AS cc, u.phone AS cp FROM orders o JOIN users u ON u.id=o.customer_id ORDER BY o.id')
    out = []
    for r in rows:
        items = '؛ '.join('%s%s × %d %s' % (i['title'], (' (' + i['option'] + ')') if i['option'] else '', i['qty'], i['unit'] or '') for i in db.all_('SELECT * FROM order_items WHERE order_id=?', (r['id'],)))
        out.append((r['code'], jdatetime(r['created_at']), r['cname'], r['cc'], r['cp'], r['city'], L.OS.get(r['status']), items))
    return _csv('orders.csv', ['کد', 'تاریخ', 'مشتری', 'شرکت', 'تلفن', 'شهر', 'وضعیت', 'اقلام'], out)


# ------------------------------------------------------------------ static site (everything else)
BLOCKED = {'_headers', '.htaccess', 'nginx.conf.example'}


@app.route('/', defaults={'p': ''})
@app.route('/<path:p>')
def static_site(p):
    if request.method not in ('GET', 'HEAD'):
        abort(405)
    rel = p.strip('/')
    target = safe_join(str(config.SITE_DIR), rel)
    if target is None:
        abort(404)
    if os.path.isdir(target):
        if p and not p.endswith('/'):
            return redirect('/' + p + '/', 301)
        target = os.path.join(target, 'index.html')
    if os.path.basename(target) in BLOCKED or os.path.basename(target).startswith('.') or not os.path.isfile(target):
        abort(404)
    g.static_page = True
    resp = send_file(target, conditional=True)
    if rel.startswith('assets/') and request.args.get('v'):
        resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'      # URL changes whenever the file changes
    elif rel.startswith('assets/'):
        resp.headers['Cache-Control'] = 'public, max-age=3600'                      # images/fonts/frames: 1 hour, then revalidate
    else:
        resp.headers['Cache-Control'] = 'no-cache'
    return resp


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 8790)), debug=False)
