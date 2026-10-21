# -*- coding: utf-8 -*-
"""Daily Telegram digest for the sales team: new customer sign-ups from the previous day.
Runs as a background thread inside the same process (app.py), no external cron needed."""
import threading
import time
from datetime import datetime, timedelta
import config
import db
import notify
from jalali import jdate

LAST_RUN_FILE = config.INSTANCE / 'digest_last_run.txt'


def _yesterday_customers():
    c = db.connect()
    rows = c.execute(
        "SELECT name, company, city, job, phone FROM users "
        "WHERE role='customer' AND date(created_at)=date('now','-1 day','localtime') "
        "ORDER BY created_at"
    ).fetchall()
    c.close()
    return rows


def _build_message(rows, day_label):
    if not rows:
        return 'اعضای جدید دیروز (%s): هیچ ثبت‌نام جدیدی نداشتیم.' % day_label
    lines = ['🆕 اعضای جدید دیروز (%s) — %d نفر' % (day_label, len(rows)), '']
    for i, r in enumerate(rows, 1):
        parts = [r['name']]
        for f in ('company', 'city', 'job', 'phone'):
            if r[f]:
                parts.append(r[f])
        lines.append('%d. %s' % (i, ' — '.join(parts)))
    lines.append('')
    lines.append('برای پیگیری فروش.')
    return '\n'.join(lines)


def run_once():
    """Build and send the digest for 'yesterday'. Safe to call manually (e.g. from manage.py) too."""
    yesterday = datetime.now() - timedelta(days=1)
    rows = _yesterday_customers()
    text = _build_message(rows, jdate(yesterday))
    try:
        notify.telegram_to(config.TELEGRAM_SALES_CHAT_ID, text)
    except Exception as e:
        with open(config.INSTANCE / 'notifications.log', 'a', encoding='utf-8') as f:
            f.write('%s | digest-error | %s\n' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(e)[:200]))
    LAST_RUN_FILE.write_text(datetime.now().strftime('%Y-%m-%d'), encoding='utf-8')


def _already_ran_today():
    if not LAST_RUN_FILE.exists():
        return False
    return LAST_RUN_FILE.read_text(encoding='utf-8').strip() == datetime.now().strftime('%Y-%m-%d')


def _loop():
    while True:
        try:
            now = datetime.now()
            if now.hour >= config.DIGEST_HOUR and not _already_ran_today():
                run_once()
        except Exception:
            pass
        time.sleep(600)  # check every 10 minutes; cheap and tolerant of process restarts


def start():
    """Call once at app startup. No-op if AKH_DAILY_DIGEST=0 or no bot token is configured."""
    if not config.DAILY_DIGEST:
        return
    threading.Thread(target=_loop, daemon=True).start()
