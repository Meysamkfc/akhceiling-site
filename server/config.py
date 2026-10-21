# -*- coding: utf-8 -*-
"""Server configuration. Secrets come from environment variables or server/.env (never hard-coded)."""
import os
import secrets
from pathlib import Path

BASE = Path(__file__).resolve().parent
INSTANCE = BASE / 'instance'
UPLOADS = INSTANCE / 'uploads'
SITE_DIR = Path(os.environ.get('AKH_SITE_DIR', BASE.parent / 'site'))
for p in (INSTANCE, UPLOADS):
    p.mkdir(parents=True, exist_ok=True)


def _load_env():
    f = BASE / '.env'
    if not f.exists():
        return
    for line in f.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()


def _secret():
    s = os.environ.get('AKH_SECRET_KEY')
    if s:
        return s
    f = INSTANCE / 'secret.key'
    if not f.exists():
        f.write_text(secrets.token_hex(32))
    return f.read_text().strip()


SECRET_KEY = _secret()
HTTPS = os.environ.get('AKH_HTTPS', '0') == '1'            # set to 1 behind HTTPS (marks cookies Secure)
TRUST_PROXY = os.environ.get('AKH_TRUST_PROXY', '0') == '1'  # set to 1 only behind your own reverse proxy
BASE_URL = os.environ.get('AKH_BASE_URL', 'http://localhost:8800').rstrip('/')
DB_PATH = Path(os.environ.get('AKH_DB', INSTANCE / 'akh.db'))

# notification channels (all optional)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
TELEGRAM_SALES_CHAT_ID = os.environ.get('TELEGRAM_SALES_CHAT_ID', '').strip() or TELEGRAM_CHAT_ID  # daily new-customer digest group; falls back to TELEGRAM_CHAT_ID
DAILY_DIGEST = os.environ.get('AKH_DAILY_DIGEST', '1') == '1'       # 1 = send yesterday's new-customer digest to sales every morning
DIGEST_HOUR = int(os.environ.get('AKH_DIGEST_HOUR', '9') or 9)      # local hour to send it
SMTP_HOST = os.environ.get('SMTP_HOST', '').strip()
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587') or 587)
SMTP_USER = os.environ.get('SMTP_USER', '').strip()
SMTP_PASS = os.environ.get('SMTP_PASS', '').strip()
NOTIFY_EMAIL_TO = os.environ.get('NOTIFY_EMAIL_TO', '').strip()
KAVENEGAR_API_KEY = os.environ.get('KAVENEGAR_API_KEY', '').strip()
NOTIFY_SMS_TO = [x.strip() for x in os.environ.get('NOTIFY_SMS_TO', '').split(',') if x.strip()]
MAKE_WEBHOOK_URL = os.environ.get('MAKE_WEBHOOK_URL', '').strip()  # Make.com "Custom Webhook" trigger URL

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_UPLOADS = {'.pdf': b'%PDF', '.jpg': b'\xff\xd8\xff', '.jpeg': b'\xff\xd8\xff', '.png': b'\x89PNG'}
SESSION_HOURS = 8
REQUIRE_2FA = os.environ.get('AKH_REQUIRE_2FA', '0') == '1'     # 1 = staff must enable 2FA before using the panel
