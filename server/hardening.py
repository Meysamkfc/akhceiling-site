# -*- coding: utf-8 -*-
"""Extra security + intelligence for site 2: proof-of-work for public forms, TOTP 2FA (RFC 6238), upload sanitising,
password policy and rule-based lead scoring. Standard library + Pillow + segno only."""
import base64
import hashlib
import hmac
import io
import re
import secrets
import struct
import time
import urllib.parse

import config

# ------------------------------------------------------------------ proof-of-work (replaces a third-party CAPTCHA)
POW_BITS = 15
POW_MIN_AGE, POW_MAX_AGE = 2, 900
_used = {}


def _sig(payload, ip):
    return hmac.new(config.SECRET_KEY.encode(), (payload + '|' + ip).encode(), hashlib.sha256).hexdigest()[:32]


def pow_issue(ip):
    payload = '%d.%s.%d' % (int(time.time()), secrets.token_hex(8), POW_BITS)
    token = payload + '.' + _sig(payload, ip)
    return dict(challenge=token, token=token, bits=POW_BITS)


def _zero_bits(digest):
    z = 0
    for b in digest:
        if b == 0:
            z += 8
        else:
            z += 8 - b.bit_length()
            break
    return z


def pow_verify(token, nonce, ip):
    """True when the token was issued to this IP, is neither too fresh (bot) nor too old, was not used before, and the work is valid."""
    try:
        ts, rnd, bits, sig = str(token).split('.')
        payload = '%s.%s.%s' % (ts, rnd, bits)
        if not hmac.compare_digest(sig, _sig(payload, ip)):
            return False
        age = time.time() - int(ts)
        if not (POW_MIN_AGE <= age <= POW_MAX_AGE) or int(bits) < POW_BITS:
            return False
        now = time.time()
        for k in [k for k, v in _used.items() if v < now]:
            _used.pop(k, None)
        if token in _used:
            return False
        nonce = str(nonce)
        if not re.fullmatch(r'\d{1,9}', nonce):
            return False
        if _zero_bits(hashlib.sha256((token + ':' + nonce).encode()).digest()) < int(bits):
            return False
        _used[token] = now + POW_MAX_AGE
        return True
    except Exception:
        return False


# ------------------------------------------------------------------ TOTP (Google Authenticator / any RFC 6238 app)
def totp_secret():
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip('=')


def _hotp(secret, counter):
    key = base64.b32decode(secret + '=' * (-len(secret) % 8))
    h = hmac.new(key, struct.pack('>Q', counter), hashlib.sha1).digest()
    o = h[-1] & 15
    return '%06d' % ((struct.unpack('>I', h[o:o + 4])[0] & 0x7fffffff) % 1000000)


def totp_verify(secret, code, window=1):
    code = re.sub(r'\D', '', str(code))[:6]
    if len(code) != 6:
        return False
    c = int(time.time() // 30)
    return any(hmac.compare_digest(_hotp(secret, c + i), code) for i in range(-window, window + 1))


def totp_uri(secret, label):
    return 'otpauth://totp/%s?secret=%s&issuer=%s&digits=6&period=30' % (urllib.parse.quote('AKH:' + label), secret, 'AKH')


def qr_svg(text):
    import segno
    return segno.make(text, error='m').svg_inline(scale=5, dark='#12141c', light='#ffffff', border=2, omitsize=False)


# ------------------------------------------------------------------ passwords
COMMON = set('''123456 1234567 12345678 123456789 1234567890 0123456789 password password1 password123 qwerty qwerty123 qwertyuiop 111111 000000 abc123 abcd1234 admin admin123 admin1234 letmein welcome iloveyou 1q2w3e4r
1qaz2wsx 123123 654321 987654321 asdfghjkl zxcvbnm monkey dragon football master login passw0rd pass1234 test1234 changeme akh akh1234 akhceiling'''.split())


def password_problem(pw, phone=''):
    if len(pw) < 10:
        return 'رمز عبور باید حداقل ۱۰ کاراکتر باشد.'
    if len(pw) > 128:
        return 'رمز عبور خیلی طولانی است.'
    if not re.search(r'[A-Za-z]', pw) or not re.search(r'\d', pw):
        return 'رمز عبور باید هم حرف لاتین و هم عدد داشته باشد.'
    low = pw.lower()
    if low in COMMON or re.fullmatch(r'(.)\1+', pw) or any(c in low for c in ('password', 'qwerty', '123456')):
        return 'این رمز عبور رایج و قابل حدس است؛ رمز دیگری انتخاب کنید.'
    digits = re.sub(r'\D', '', phone or '')
    if digits and (digits[-8:] in pw or digits[-9:] in pw):
        return 'رمز عبور نباید شامل شماره موبایل باشد.'
    return None


# ------------------------------------------------------------------ uploads
BAD_PDF = (b'/JavaScript', b'/JS', b'/Launch', b'/OpenAction', b'/AA', b'/EmbeddedFile', b'/RichMedia', b'/XFA', b'/SubmitForm', b'/ImportData')


def sanitize_upload(ext, data):
    """returns (clean_bytes, error). Images are decoded and re-encoded (drops EXIF/GPS and any appended payload); PDFs are rejected if active content is present."""
    if ext == '.pdf':
        if not data.startswith(b'%PDF-') or b'%%EOF' not in data[-2048:]:
            return None, 'فایل PDF معتبر نیست.'
        if any(t in data for t in BAD_PDF):
            return None, 'این PDF شامل محتوای فعال (اسکریپت یا فایل پیوست) است و پذیرفته نمی‌شود.'
        return data, None
    from PIL import Image
    try:
        im = Image.open(io.BytesIO(data))
        im.verify()
        im = Image.open(io.BytesIO(data))
        if im.width * im.height > 60_000_000:
            return None, 'ابعاد تصویر بیش از حد بزرگ است.'
        im.load()
    except Exception:
        return None, 'تصویر معتبر نیست.'
    out = io.BytesIO()
    if ext == '.png':
        im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB').save(out, 'PNG', optimize=True)
    else:
        im.convert('RGB').save(out, 'JPEG', quality=88, optimize=True)
    return out.getvalue(), None


# ------------------------------------------------------------------ lead scoring (rule based, transparent)
BIZ = ('پروژه', 'پیمانکار', 'هتل', 'بیمارستان', 'دانشگاه', 'مجتمع', 'برج', 'کارخانه', 'سوله', 'مدرسه', 'فروشگاه', 'شرکت', 'مناقصه', 'تعداد', 'عمده')


def score_lead(d):
    """d: dict(area, product, phone, city, desc, source, company). returns (score, label, reasons)."""
    s, why = 0, []
    a = d.get('area') or 0
    if a >= 1000: s += 4; why.append('متراژ ≥ ۱۰۰۰')
    elif a >= 300: s += 3; why.append('متراژ ≥ ۳۰۰')
    elif a >= 100: s += 2; why.append('متراژ ≥ ۱۰۰')
    elif a > 0: s += 1; why.append('متراژ اعلام شده')
    if d.get('product'): s += 1; why.append('محصول مشخص')
    if str(d.get('phone', '')).startswith('09'): s += 1; why.append('موبایل')
    if d.get('city'): s += 1; why.append('شهر مشخص')
    if d.get('company'): s += 1; why.append('نام شرکت')
    text = d.get('desc') or ''
    if len(text) > 60: s += 1; why.append('توضیحات کامل')
    if any(k in text for k in BIZ): s += 1; why.append('پروژه‌ای/سازمانی')
    if d.get('source') == 'quote': s += 1; why.append('فرم قیمت')
    label = 'hot' if s >= 7 else 'warm' if s >= 4 else 'cold'
    return s, label, why
