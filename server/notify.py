# -*- coding: utf-8 -*-
"""Staff notifications. Telegram (same bot as the CRM call-bot), e-mail (SMTP) and SMS (Kavenegar) are optional;
without any channel the message is only written to instance/notifications.log (always)."""
import json
import smtplib
import threading
import urllib.parse
import urllib.request
from datetime import datetime
from email.mime.text import MIMEText
import config

LOG = config.INSTANCE / 'notifications.log'


def _log(text, results):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write('%s | %s | %s\n' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(results, ensure_ascii=False), text.replace('\n', ' ¶ ')))


def telegram_to(chat_id, text):
    """Low-level send to an explicit chat/group id. Used directly by the daily sales digest."""
    if not (config.TELEGRAM_BOT_TOKEN and chat_id):
        return None
    data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text, 'disable_web_page_preview': 'true'}).encode()
    req = urllib.request.Request('https://api.telegram.org/bot%s/sendMessage' % config.TELEGRAM_BOT_TOKEN, data=data)
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status == 200


def _telegram(text):
    return telegram_to(config.TELEGRAM_CHAT_ID, text)


def _email(subject, text):
    if not (config.SMTP_HOST and config.NOTIFY_EMAIL_TO):
        return None
    m = MIMEText(text, 'plain', 'utf-8')
    m['Subject'] = subject
    m['From'] = config.SMTP_USER or 'noreply@localhost'
    m['To'] = config.NOTIFY_EMAIL_TO
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10) as s:
        s.starttls()
        if config.SMTP_USER:
            s.login(config.SMTP_USER, config.SMTP_PASS)
        s.sendmail(m['From'], [x.strip() for x in config.NOTIFY_EMAIL_TO.split(',')], m.as_string())
    return True


def _sms(text):
    if not (config.KAVENEGAR_API_KEY and config.NOTIFY_SMS_TO):
        return None
    url = 'https://api.kavenegar.com/v1/%s/sms/send.json' % config.KAVENEGAR_API_KEY
    data = urllib.parse.urlencode({'receptor': ','.join(config.NOTIFY_SMS_TO), 'message': text[:300]}).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10) as r:
        return r.status == 200


def _webhook(subject, text):
    """Make.com (or any other automation tool) "Custom Webhook" trigger: posts {subject, text, ts} as JSON."""
    if not config.MAKE_WEBHOOK_URL:
        return None
    data = json.dumps({'subject': subject, 'text': text, 'ts': datetime.now().isoformat()}).encode()
    req = urllib.request.Request(config.MAKE_WEBHOOK_URL, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return 200 <= r.status < 300


def _worker(subject, text):
    results = {}
    for name, fn in (('telegram', lambda: _telegram(text)), ('email', lambda: _email(subject, text)), ('sms', lambda: _sms(text)), ('webhook', lambda: _webhook(subject, text))):
        try:
            r = fn()
            if r is not None:
                results[name] = 'ok' if r else 'failed'
        except Exception as e:                                     # a broken channel must never break a customer request
            results[name] = 'error: %s' % str(e)[:80]
    _log(text, results)


def notify(subject, text, wait=False):
    t = threading.Thread(target=_worker, args=(subject, text), daemon=True)
    t.start()
    if wait:
        t.join(15)
