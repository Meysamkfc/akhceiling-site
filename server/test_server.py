# -*- coding: utf-8 -*-
"""Security + workflow tests (Flask test client, throw-away database).   python test_server.py"""
import io
import os
import re
import sys
import tempfile

tmp = tempfile.mkdtemp()
os.environ['AKH_DB'] = os.path.join(tmp, 't.db')
os.environ['AKH_SECRET_KEY'] = 'test-secret'

import app as A  # noqa: E402
import db  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402
import security as sec  # noqa: E402

import hashlib  # noqa: E402
import hardening as hd  # noqa: E402
hd.POW_MIN_AGE = 0


def solve_pow(c):
    j = c.get('/api/pow').get_json()
    n = 0
    while True:
        if hd._zero_bits(hashlib.sha256((j['challenge'] + ':' + str(n)).encode()).digest()) >= j['bits']:
            return {'pow_token': j['token'], 'pow_nonce': str(n)}
        n += 1


PASS, FAIL = [], []


def check(name, cond, extra=''):
    (PASS if cond else FAIL).append(name)
    print(('  ok   ' if cond else '  FAIL ') + name + (('  -> ' + str(extra)) if (extra and not cond) else ''))


def token(c):
    return c.get('/api/csrf').get_json()['token']


def form_token(c, url):
    html = c.get(url).get_data(as_text=True)
    m = re.search(r'name="_csrf" value="([^"]+)"', html)
    return m.group(1) if m else ''


def mk_user(role, phone, pw, status='active', name=None):
    with A.app.app_context():
        return db.run('INSERT INTO users(role,name,phone,pass_hash,status) VALUES(?,?,?,?,?)', (role, name or role + phone[-2:], phone, generate_password_hash(pw), status))


def login(c, phone, pw):
    t = form_token(c, '/account/login/')
    return c.post('/account/login/', data=dict({'_csrf': t, 'identifier': phone, 'password': pw}, **solve_pow(c)), follow_redirects=False)


A.app.config['TESTING'] = False
mk_user('admin', '09120000001', 'Admin12345', name='مدیر')
mk_user('sales', '09120000002', 'Sales12345', name='کارشناس')

print('[lead API]')
c = A.app.test_client()
body = {'source': 'quote', 'name': 'علی رضایی', 'phone': '۰۹۱۲۳۴۵۶۷۸۹', 'city': 'تهران', 'area': '۱۲۰', 'product': 'grid', 'building': 'office', 'desc': 'تست'}
r = c.post('/api/lead', json=body)
check('lead without CSRF token is rejected (400)', r.status_code == 400, r.status_code)
t = token(c)
r = c.post('/api/lead', json=body, headers={'X-CSRF-Token': t, 'Origin': 'http://evil.example'})
check('cross-site Origin is rejected (403)', r.status_code == 403, r.status_code)
r = c.post('/api/lead', data='x=1', headers={'X-CSRF-Token': t, 'Content-Type': 'application/x-www-form-urlencoded'})
check('non-JSON content type rejected (400)', r.status_code == 400, r.status_code)
r = c.post('/api/lead', json=dict(body, phone='123', **solve_pow(c)), headers={'X-CSRF-Token': t})
check('invalid phone -> 422 with error', r.status_code == 422 and 'phone' in r.get_json()['errors'], r.get_json())
r = c.post('/api/lead', json=dict(body, **solve_pow(c)), headers={'X-CSRF-Token': t})
j = r.get_json()
check('valid lead stored, code returned', r.status_code == 200 and re.fullmatch(r'Q-\d{4}-\d{4}', j.get('code', '')), j)
with A.app.app_context():
    row = db.one('SELECT * FROM leads WHERE code=?', (j['code'],))
check('phone normalised to ASCII + area parsed', row and row['phone'] == '09123456789' and row['area'] == 120.0, dict(row) if row else None)
check('lead auto-assigned to the sales expert', row and row['assigned_to'] is not None)
before = None
with A.app.app_context():
    before = db.one('SELECT COUNT(*) n FROM leads')['n']
r = c.post('/api/lead', json=dict(body, website='http://spam', **solve_pow(c)), headers={'X-CSRF-Token': t})
with A.app.app_context():
    after = db.one('SELECT COUNT(*) n FROM leads')['n']
check('honeypot: reports ok but stores nothing', r.status_code == 200 and before == after)
sec._hits.clear()
codes = []
for i in range(8):
    codes.append(c.post('/api/lead', json=dict(body, phone='0912000%04d' % (1000 + i), **solve_pow(c)), headers={'X-CSRF-Token': t}).status_code)
check('rate limit kicks in (429) after 6 requests/hour', 429 in codes, codes)
sec._hits.clear()
r = c.post('/api/lead', json=dict(body, name='x<script>alert(1)</script>y', phone='09127654321', source='assistant', room='office', suggestion='سقف', **solve_pow(c)), headers={'X-CSRF-Token': t})
check('assistant lead accepted', r.status_code == 200, r.get_data(as_text=True)[:100])

print('[accounts + registration]')
c1 = A.app.test_client()
t = form_token(c1, '/account/register/')
r = c1.post('/account/register/', data=dict({'_csrf': t, 'name': 'مشتری یک', 'identifier': '09121111111', 'city_ir': 'کرج', 'password': 'abc', 'password2': 'abc'}, **solve_pow(c1)))
check('weak password rejected', 'رمز عبور' in r.get_data(as_text=True) and r.status_code == 200)
r = c1.post('/account/register/', data={'name': 'x', 'identifier': '09121111111', 'password': 'Abcdefg123', 'password2': 'Abcdefg123'})
check('register without CSRF -> 400', r.status_code == 400, r.status_code)
t = form_token(c1, '/account/register/')
r = c1.post('/account/register/', data=dict({'_csrf': t, 'name': '<img src=x onerror=alert(1)> مشتری', 'company': 'شرکت نمونه', 'identifier': '09121111111', 'city_ir': 'کرج', 'job': 'مهندس / ناظر', 'password': 'Abcdefg123', 'password2': 'Abcdefg123'}, **solve_pow(c1)))
check('registration ok -> redirect to login', r.status_code == 302 and '/account/login/' in r.headers['Location'], r.status_code)
t = form_token(c1, '/account/register/')
r = c1.post('/account/register/', data=dict({'_csrf': t, 'name': 'تکراری', 'identifier': '09121111111', 'city_ir': 'کرج', 'password': 'Abcdefg123', 'password2': 'Abcdefg123'}, **solve_pow(c1)))
check('duplicate registration gives the same neutral answer (no account enumeration)', r.status_code == 302 and '/account/login/' in r.headers['Location'])
r = login(c1, '09121111111', 'Abcdefg123')
check('pending customer can log in to a limited panel', r.status_code == 302 and r.headers['Location'].endswith('/account/'), r.headers.get('Location'))
html = c1.get('/account/orders/new/').get_data(as_text=True)
check('pending customer cannot order (sees pending notice)', 'در انتظار تأیید' in html and 'orderform' not in html)

e1 = A.app.test_client()
te = form_token(e1, '/account/register/')
r = e1.post('/account/register/', data=dict({'_csrf': te, 'name': 'مشتری ایمیلی', 'identifier': 'Buyer@Example.com', 'city_ir': 'شیراز', 'job': 'مهندس / ناظر', 'password': 'Abcdefg123', 'password2': 'Abcdefg123'}, **solve_pow(e1)))
check('email-based registration ok -> redirect to login', r.status_code == 302 and '/account/login/' in r.headers['Location'], r.status_code)
with A.app.app_context():
    eu = db.one("SELECT * FROM users WHERE email='buyer@example.com'")
check('email stored lowercase with job saved, no phone required', eu is not None and eu['phone'] is None and eu['job'] == 'مهندس / ناظر', dict(eu) if eu else None)
r = login(e1, 'buyer@example.com', 'Abcdefg123')
check('pending customer can log in with an email identifier', r.status_code == 302 and r.headers['Location'].endswith('/account/'), r.headers.get('Location'))

print('[forgot password]')
with A.app.app_context():
    fuid = db.run("INSERT INTO users(role,name,phone,city,job,pass_hash,status) VALUES('customer','فراموشکار','09129999999','تهران','پیمانکار',?,'active')", (generate_password_hash('OldPass123'),))
cf = A.app.test_client()
check('GET /account/forgot/ -> 200', cf.get('/account/forgot/').status_code == 200)
t = form_token(cf, '/account/forgot/')
r = cf.post('/account/forgot/', data={'_csrf': t, 'identifier': '09129999999'}, follow_redirects=False)
check('forgot step 1 -> redirect to question', r.status_code == 302 and '/account/forgot/question/' in r.headers['Location'])
t = form_token(cf, '/account/forgot/question/')
r = cf.post('/account/forgot/question/', data={'_csrf': t, 'job': 'مهندس / ناظر'}, follow_redirects=False)
check('wrong security answer -> stays on question page', r.status_code == 200 and 'پاسخ درست نیست' in r.get_data(as_text=True))
t = form_token(cf, '/account/forgot/question/')
r = cf.post('/account/forgot/question/', data={'_csrf': t, 'job': 'پیمانکار'}, follow_redirects=False)
check('correct security answer -> redirect to reset', r.status_code == 302 and '/account/forgot/reset/' in r.headers['Location'])
t = form_token(cf, '/account/forgot/reset/')
r = cf.post('/account/forgot/reset/', data={'_csrf': t, 'password': 'NewPass123', 'password2': 'NewPass999'})
check('mismatched new password -> error, no redirect', r.status_code == 200 and 'یکسان' in r.get_data(as_text=True))
t = form_token(cf, '/account/forgot/reset/')
r = cf.post('/account/forgot/reset/', data={'_csrf': t, 'password': 'NewPass123', 'password2': 'NewPass123'}, follow_redirects=False)
check('password reset ok -> redirect to login', r.status_code == 302 and '/account/login/' in r.headers['Location'])
r = login(A.app.test_client(), '09129999999', 'OldPass123')
check('old password no longer works', r.status_code != 302 or not r.headers.get('Location', '').endswith('/account/'))
r = login(A.app.test_client(), '09129999999', 'NewPass123')
check('new password logs in', r.status_code == 302 and r.headers['Location'].endswith('/account/'), r.headers.get('Location'))
cl = A.app.test_client()
tq = form_token(cl, '/account/forgot/')
cl.post('/account/forgot/', data={'_csrf': tq, 'identifier': '09129999999'})
for _ in range(5):
    tq = form_token(cl, '/account/forgot/question/')
    cl.post('/account/forgot/question/', data={'_csrf': tq, 'job': 'معمار'})
tq = form_token(cl, '/account/forgot/question/')
r = cl.post('/account/forgot/question/', data={'_csrf': tq, 'job': 'معمار'})
check('security question locks out after repeated wrong answers', 'مسدود' in r.get_data(as_text=True))

print('[staff panel + approval]')
ca = A.app.test_client()
r = login(ca, '09120000001', 'Admin12345')
check('admin login -> /admin/', r.status_code == 302 and r.headers['Location'].endswith('/admin/'), r.headers.get('Location'))
html = ca.get('/admin/').get_data(as_text=True)
check('dashboard shows pending registration count', 'عضویت در انتظار تأیید' in html)
html = ca.get('/admin/customers/').get_data(as_text=True)
check('stored XSS payload is escaped in the customer list', '<img src=x' not in html and '&lt;img src=x' in html)
with A.app.app_context():
    cust = db.one("SELECT id FROM users WHERE phone='09121111111'")['id']
    lead_id = db.one("SELECT id FROM leads WHERE source='assistant'")['id']
t = form_token(ca, '/admin/customers/%d/' % cust)
r = ca.post('/admin/customers/%d/' % cust, data={'_csrf': t, 'action': 'approve'})
check('admin approves customer', r.status_code == 302)
html = ca.get('/admin/leads/%d/' % lead_id).get_data(as_text=True)
check('lead detail renders, XSS in name escaped', 'x&lt;script&gt;' in html and '<script>alert(1)' not in html)
t = form_token(ca, '/admin/leads/%d/' % lead_id)
ca.post('/admin/leads/%d/' % lead_id, data={'_csrf': t, 'action': 'call', 'outcome': 'پاسخ داد — مایل به ادامه', 'text': 'پیش‌فاکتور بفرستید'})
with A.app.app_context():
    st = db.one('SELECT status FROM leads WHERE id=?', (lead_id,))['status']
check('logging a call moves new lead to "contacted"', st == 'contacted', st)
r = ca.post('/admin/leads/%d/' % lead_id, data={'action': 'status', 'status': 'won'})
check('staff POST without CSRF -> 400', r.status_code == 400)

print('[customer orders + files + isolation]')
r = login(c1, '09121111111', 'Abcdefg123')  # session already logged in -> redirect
c1 = A.app.test_client()
login(c1, '09121111111', 'Abcdefg123')
html = c1.get('/account/orders/new/').get_data(as_text=True)
check('approved customer sees the order form', 'orderform' in html)
t = form_token(c1, '/account/orders/new/')
pdf = (io.BytesIO(b'%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF'), 'فاکتور.pdf')
r = c1.post('/account/orders/new/', data={'_csrf': t, 'item_key[]': ['f47', 'screw'], 'option[]': ['۰٫۶ میلی‌متر', 'پیچ سازه سرمته LB 9.5'], 'qty[]': ['۱۰', '2'], 'city': 'کرج', 'address': 'جاده', 'files': pdf, 'file_kind': 'invoice'},
            content_type='multipart/form-data')
check('order created with file', r.status_code == 302 and '/account/orders/AKH-' in r.headers['Location'], (r.status_code, r.headers.get('Location')))
ocode = r.headers['Location'].rstrip('/').split('/')[-1]
t = form_token(c1, '/account/orders/new/')
r = c1.post('/account/orders/new/', data={'_csrf': t, 'item_key[]': ['hack'], 'option[]': [''], 'qty[]': ['1'], 'city': 'کرج'}, content_type='multipart/form-data')
check('unknown catalog item rejected', r.status_code == 200 and 'نامعتبر' in r.get_data(as_text=True))
r = c1.post('/account/orders/new/', data={'_csrf': t, 'item_key[]': ['f47'], 'option[]': ['۰٫۷ میلی‌متر'], 'qty[]': ['1'], 'city': 'کرج'}, content_type='multipart/form-data')
check('invalid option rejected', r.status_code == 200 and 'معتبر نیست' in r.get_data(as_text=True))
r = c1.post('/account/orders/new/', data={'_csrf': t, 'item_key[]': ['f47'], 'option[]': ['۰٫۵ میلی‌متر'], 'qty[]': ['-5'], 'city': 'کرج'}, content_type='multipart/form-data')
check('negative quantity rejected', r.status_code == 200 and 'معتبر نیست' in r.get_data(as_text=True))
t = form_token(c1, '/account/orders/%s/' % ocode)
for fname, data, why in [('x.exe', b'MZ\x90\x00', 'exe extension'), ('fake.png', b'not a png at all', 'wrong magic bytes'), ('big.pdf', b'%PDF' + b'0' * (config_max := 5 * 1024 * 1024 + 10), 'over 5 MB')]:
    r = c1.post('/account/orders/%s/upload/' % ocode, data={'_csrf': t, 'kind': 'invoice', 'files': (io.BytesIO(data), fname)}, content_type='multipart/form-data', follow_redirects=True)
    check('upload rejected: ' + why, ('فایل ارسال شد' not in r.get_data(as_text=True)))
with A.app.app_context():
    nfiles = db.one('SELECT COUNT(*) n FROM files')['n']
    fid = db.one('SELECT id FROM files')['id']
check('only the valid file is stored', nfiles == 1, nfiles)
r = c1.get('/files/%d/' % fid)
check('owner downloads own file as attachment + nosniff', r.status_code == 200 and 'attachment' in r.headers.get('Content-Disposition', '') and r.headers.get('X-Content-Type-Options') == 'nosniff', r.headers)

# a second customer must not see the first one's data
mk_user('customer', '09122222222', 'Other12345', name='مشتری دو')
c2 = A.app.test_client()
login(c2, '09122222222', 'Other12345')
check("customer B cannot open customer A's order (404)", c2.get('/account/orders/%s/' % ocode).status_code == 404)
check("customer B cannot download customer A's file (404)", c2.get('/files/%d/' % fid).status_code == 404)
check('customer cannot open /admin/ (403)', c1.get('/admin/').status_code == 403)
check('anonymous cannot download files', A.app.test_client().get('/files/%d/' % fid).status_code == 302)

print('[staff handles the order]')
t = form_token(ca, '/admin/orders/%s/' % ocode)
pro = (io.BytesIO(b'%PDF-1.4 proforma\n%%EOF'), 'proforma.pdf')
ca.post('/admin/orders/%s/' % ocode, data={'_csrf': t, 'action': 'file', 'kind': 'proforma', 'files': pro}, content_type='multipart/form-data')
t = form_token(ca, '/admin/orders/%s/' % ocode)
ca.post('/admin/orders/%s/' % ocode, data={'_csrf': t, 'action': 'public', 'text': 'پیش‌فاکتور ارسال شد'})
html = c1.get('/account/orders/%s/' % ocode).get_data(as_text=True)
check('customer sees proforma file + message + new status', 'proforma.pdf' in html and 'پیش‌فاکتور ارسال شد' in html)
t = form_token(ca, '/admin/orders/%s/' % ocode)
ca.post('/admin/orders/%s/' % ocode, data={'_csrf': t, 'action': 'note', 'text': 'یادداشت داخلی محرمانه'})
html = c1.get('/account/orders/%s/' % ocode).get_data(as_text=True)
check('internal notes are NOT visible to the customer', 'یادداشت داخلی محرمانه' not in html)

print('[sales role limits]')
cs = A.app.test_client()
login(cs, '09120000002', 'Sales12345')
check('sales can open leads', cs.get('/admin/leads/').status_code == 200)
check('sales cannot open user management (403)', cs.get('/admin/users/').status_code == 403)
r = ca.get('/admin/export/leads.csv')
check('CSV export works (UTF-8 BOM, attachment)', r.status_code == 200 and r.data.startswith(b'\xef\xbb\xbf') and 'attachment' in r.headers['Content-Disposition'])
with A.app.app_context():
    db.run("UPDATE leads SET name='=HYPERLINK(\"http://x\")' WHERE id=?", (lead_id,))
check('CSV cells starting with = are neutralised', "'=HYPERLINK" in ca.get('/admin/export/leads.csv').get_data(as_text=True))

print('[login hardening]')
cl = A.app.test_client()
for i in range(5):
    login(cl, '09122222222', 'wrong-pass-%d' % i)
r = login(cl, '09122222222', 'Other12345')
check('account locks after 5 failures (correct password refused)', r.status_code == 200 and 'مسدود' in r.get_data(as_text=True))
cn = A.app.test_client()
t = form_token(cn, '/account/login/')
r = cn.post('/account/login/?next=//evil.example/x', data=dict({'_csrf': t, 'identifier': '09120000001', 'password': 'Admin12345'}, **solve_pow(cn)))
check('open redirect via next= is ignored', r.status_code == 302 and 'evil' not in r.headers['Location'], r.headers.get('Location'))
r = cn.post('/account/logout/', data={})
check('logout without CSRF -> 400', r.status_code == 400)

print('[headers + static]')
r = A.app.test_client().get('/account/login/')
check('dynamic page: CSP + no-store + nosniff', "script-src 'self'" in r.headers.get('Content-Security-Policy', '') and r.headers.get('Cache-Control') == 'no-store' and r.headers.get('X-Content-Type-Options') == 'nosniff')
check('no inline script or style attribute in dynamic HTML', not re.search(r'<script(?![^>]*src=)[^>]*>', r.get_data(as_text=True)) and ' style="' not in r.get_data(as_text=True))
r = A.app.test_client().get('/')
check('static page served with CSP', "frame-ancestors 'none'" in r.headers.get('Content-Security-Policy', '') and "require-trusted-types-for 'script'" in r.headers.get('Content-Security-Policy', ''))
for p in ('/.htaccess', '/_headers', '/nginx.conf.example', '/../server/config.py', '/%2e%2e/server/config.py', '/assets/../../server/.env'):
    check('blocked / not served: ' + p, A.app.test_client().get(p).status_code in (404, 400))
check('uploads folder is not web-accessible', A.app.test_client().get('/instance/uploads/').status_code == 404)

print('[anonymous page-view counter]')
ch = A.app.test_client()
for p in ('/products/', '/products/', '/'):
    ch.post('/api/hit', json={'p': p})
for bad in ('/admin/', '/account/login/', '/../etc/passwd', '/nope/', 'products', '/products/<script>'):
    ch.post('/api/hit', json={'p': bad})
ch.post('/api/hit', json={'p': '/products/'}, headers={'Origin': 'http://evil.example'})
with A.app.app_context():
    rows = {r['path']: r['n'] for r in db.all_('SELECT path, SUM(n) n FROM pageviews GROUP BY path')}
check('counts valid public pages only', rows.get('/products/') == 2 and rows.get('/') == 1 and set(rows) <= {'/', '/products/'}, rows)
html = ca.get('/admin/').get_data(as_text=True)
check('dashboard shows visit stats', 'بازدید ۷ روز اخیر' in html and '/products/' in html)


print('[site 2 hardening]')
import time as _t
# proof of work
cp = A.app.test_client()
tp = token(cp)
body2 = {'source': 'quote', 'name': 'علی رضایی', 'phone': '09123450099', 'city': 'تهران', 'area': '600', 'product': 'grid', 'building': 'office', 'desc': 'پروژه اداری بزرگ برای شرکت ما'}
sec._hits.clear()
r = cp.post('/api/lead', json=body2, headers={'X-CSRF-Token': tp})
check('lead without proof-of-work is refused (400)', r.status_code == 400, r.status_code)
w = solve_pow(cp)
r1 = cp.post('/api/lead', json=dict(body2, **w), headers={'X-CSRF-Token': tp})
r2 = cp.post('/api/lead', json=dict(body2, phone='09123450098', **w), headers={'X-CSRF-Token': tp})
check('valid PoW accepted once, reuse of the same token refused', r1.status_code == 200 and r2.status_code == 400, (r1.status_code, r2.status_code))
j = cp.get('/api/pow').get_json()
bad = {'pow_token': j['token'], 'pow_nonce': '1'}
check('wrong nonce refused', cp.post('/api/lead', json=dict(body2, phone='09123450097', **bad), headers={'X-CSRF-Token': tp}).status_code == 400)
hd.POW_MIN_AGE = 5
w2 = solve_pow(cp)
check('a challenge answered instantly (bot speed) is refused', cp.post('/api/lead', json=dict(body2, phone='09123450096', **w2), headers={'X-CSRF-Token': tp}).status_code == 400)
hd.POW_MIN_AGE = 0
tok = cp.get('/api/pow').get_json()['token']
other = A.app.test_client()
check('a token issued to another IP is refused', not hd.pow_verify(tok, '1', '10.9.9.9'))

# lead scoring
with A.app.app_context():
    lead = db.one("SELECT * FROM leads WHERE phone='09123450099'")
check('big project lead is scored hot', lead and lead['priority'] == 'hot' and lead['score'] >= 7, dict(lead) if lead else None)
sc_small = hd.score_lead(dict(area=20, phone='09120000000', source='assistant'))
check('small anonymous lead is not hot', sc_small[1] != 'hot', sc_small)

# TOTP: RFC 6238 vector + full login flow
check('TOTP implementation matches the RFC 6238 test vector', hd._hotp('GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ', 59 // 30) == '287082')
mk_user('sales', '09125557777', 'Sales777Pass', name='کارشناس دو')
cs2 = A.app.test_client()
login(cs2, '09125557777', 'Sales777Pass')
html = cs2.get('/account/security/').get_data(as_text=True)
m = re.search(r'<p class="num"><b>([A-Z2-7]+)</b></p>', html)
check('security page shows a QR code (inline SVG) and the key', '<svg' in html and bool(m))
secret = m.group(1)
t2 = form_token(cs2, '/account/security/')
r = cs2.post('/account/security/', data={'_csrf': t2, 'action': 'enable', 'code': '000000'})
check('2FA enable with a wrong code fails', 'درست نیست' in r.get_data(as_text=True))
t2 = form_token(cs2, '/account/security/')
cs2.post('/account/security/', data={'_csrf': t2, 'action': 'enable', 'code': hd._hotp(secret, int(_t.time() // 30))})
with A.app.app_context():
    on = db.one("SELECT totp_on FROM users WHERE phone='09125557777'")['totp_on']
check('2FA enabled with a correct code', on == 1)
c3 = A.app.test_client()
r = login(c3, '09125557777', 'Sales777Pass')
check('login with password only leads to the 2FA step (no session yet)', r.status_code == 302 and '/account/2fa/' in r.headers['Location'] and c3.get('/admin/').status_code == 302)
t3 = form_token(c3, '/account/2fa/')
r = c3.post('/account/2fa/', data={'_csrf': t3, 'code': '123456'})
check('wrong 2FA code refused', r.status_code == 200 and 'نادرست' in r.get_data(as_text=True))
r = c3.post('/account/2fa/', data={'_csrf': t3, 'code': hd._hotp(secret, int(_t.time() // 30))}, follow_redirects=False)
check('correct 2FA code completes the login', r.status_code == 302 and '/admin/' in r.headers['Location'] and c3.get('/admin/').status_code == 200)
c4 = A.app.test_client(); login(c4, '09125557777', 'Sales777Pass'); t4 = form_token(c4, '/account/2fa/')
res = [c4.post('/account/2fa/', data={'_csrf': t4, 'code': '%06d' % i}).status_code for i in range(8)]
check('2FA guessing is rate limited (429)', 429 in res, res)

# session bound to the browser
cb = A.app.test_client(); login(cb, '09120000001', 'Admin12345')
check('session works with the same User-Agent', cb.get('/admin/').status_code == 200)
cb2 = A.app.test_client(); login(cb2, '09120000001', 'Admin12345')
cb2.get('/admin/')
check('the same cookie with another User-Agent is rejected', cb2.get('/admin/', headers={'User-Agent': 'UA-2-hijacker'}).status_code == 302)

# password policy
check('weak / common passwords are refused', all(hd.password_problem(p, '09121234567') for p in ('password123', 'Abcdefg1', '1234567890', 'Qwerty12345', 'Pass09121234567x')))
check('a good password is accepted', hd.password_problem('Kj7#mQ2xLp9z', '09121234567') is None)

# uploads: active PDF content and polyglot images
cu = A.app.test_client(); login(cu, '09122222222', 'Other12345')
t5 = form_token(cu, '/account/orders/new/')
with A.app.app_context():
    oc = db.one('SELECT code FROM orders ORDER BY id LIMIT 1')['code']
tt = form_token(c1, '/account/orders/%s/' % oc)
js_pdf = (io.BytesIO(b'%PDF-1.4\n1 0 obj<</Type/Action/S/JavaScript/JS(app.alert(1))>>endobj\n%%EOF'), 'evil.pdf')
with A.app.app_context():
    before = db.one('SELECT COUNT(*) n FROM files')['n']
c1.post('/account/orders/%s/upload/' % oc, data={'_csrf': tt, 'kind': 'invoice', 'files': js_pdf}, content_type='multipart/form-data')
from PIL import Image as _I
bio = io.BytesIO(); _I.new('RGB', (40, 30), (200, 100, 50)).save(bio, 'PNG'); png = bio.getvalue() + b'<?php system($_GET[0]); ?>'
tt = form_token(c1, '/account/orders/%s/' % oc)
c1.post('/account/orders/%s/upload/' % oc, data={'_csrf': tt, 'kind': 'plan', 'files': (io.BytesIO(png), 'plan.png')}, content_type='multipart/form-data')
with A.app.app_context():
    after = db.one('SELECT COUNT(*) n FROM files')['n']
    stored = db.one('SELECT stored_name FROM files ORDER BY id DESC LIMIT 1')['stored_name']
data = (A.config.UPLOADS / stored).read_bytes()
check('PDF with JavaScript is refused', after == before + 1)
check('image is re-encoded: appended PHP payload is gone', data.startswith(b'\x89PNG') and b'<?php' not in data)

# headers on dynamic pages
rh = A.app.test_client().get('/account/login/')
check('dynamic pages: Trusted Types, DENY, CORP, COOP', all(k in str(rh.headers) for k in ("require-trusted-types-for 'script'", 'DENY', 'Cross-Origin-Resource-Policy: same-origin', 'Cross-Origin-Opener-Policy: same-origin')))
check('audit log is admin-only', cs2.get('/admin/audit/').status_code == 403 and ca.get('/admin/audit/').status_code in (200, 302))
check('security.txt is served', A.app.test_client().get('/.well-known/security.txt').status_code == 200)

print('[notifications]')
import time
time.sleep(0.5)
log = (A.config.INSTANCE / 'notifications.log')
txt = log.read_text(encoding='utf-8') if log.exists() else ''
check('staff notification lines written (lead/registration/order)', 'درخواست جدید' in txt and 'درخواست عضویت' in txt and 'سفارش جدید' in txt)

print('[daily digest]')
import digest
digest.run_once()
check('daily digest run_once does not crash and marks last-run file', digest.LAST_RUN_FILE.exists())
check('daily digest message handles zero new customers', 'هیچ ثبت‌نام جدیدی' in digest._build_message([], '۱۴۰۵/۰۱/۰۱'))
row = {'name': 'علی رضایی', 'company': 'شرکت نمونه', 'city': 'تهران', 'job': 'مهندس', 'phone': '09120000000'}
msg_one = digest._build_message([row], '۱۴۰۵/۰۱/۰۱')
check('daily digest message lists a new customer with their details', 'علی رضایی' in msg_one and 'شرکت نمونه' in msg_one and '09120000000' in msg_one)

print('\n%d passed, %d failed' % (len(PASS), len(FAIL)))
if FAIL:
    print('FAILED:', FAIL)
    sys.exit(1)
