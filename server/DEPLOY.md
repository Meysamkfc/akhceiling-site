# راه‌اندازی روی سرور واقعی (Ubuntu VPS) — گام به گام

نیازها: یک VPS (۱ vCPU، ۱ تا ۲ گیگ RAM کافی است)، دامنه‌ای که A-record آن به IP سرور اشاره کند.

```bash
# 1) ساخت کاربر و پوشه
sudo adduser --system --group --home /srv/akh akh
sudo apt update && sudo apt install -y python3-venv nginx certbot python3-certbot-nginx sqlite3 unzip
# 2) آپلود بسته (akhceiling-full.zip) و بازکردن آن
sudo unzip akhceiling-full.zip -d /srv/akh && sudo chown -R akh:akh /srv/akh
# 3) محیط پایتون
cd /srv/akh/server && sudo -u akh python3 -m venv .venv && sudo -u akh .venv/bin/pip install -r requirements.txt
# 4) تنظیمات
sudo -u akh cp .env.example .env && sudo -u akh nano .env
#    AKH_BASE_URL=https://akhceiling.com   AKH_HTTPS=1   AKH_TRUST_PROXY=1
#    TELEGRAM_BOT_TOKEN=...  TELEGRAM_CHAT_ID=...   (همان ربات CRM قبلی)
# 5) ساخت اولین مدیر (حساب پیش‌فرض وجود ندارد)
sudo -u akh .venv/bin/python manage.py create-user --role admin --name "نام شما" --phone 09xxxxxxxxx
# 6) سرویس
sudo cp deploy/akh.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now akh
# 7) nginx + گواهی HTTPS
sudo cp deploy/nginx-akh.conf /etc/nginx/sites-available/akh && sudo ln -s /etc/nginx/sites-available/akh /etc/nginx/sites-enabled/
sudo certbot --nginx -d akhceiling.com -d www.akhceiling.com && sudo nginx -t && sudo systemctl reload nginx
# 8) پشتیبان روزانه
sudo chmod +x deploy/backup.sh && (sudo crontab -l 2>/dev/null; echo "30 2 * * * /srv/akh/server/deploy/backup.sh") | sudo crontab -
```

## بعد از راه‌اندازی — فهرست بررسی
- [ ] `https://دامنه/` باز می‌شود و قفل HTTPS دارد؛ `http://` به https هدایت می‌شود.
- [ ] با حساب مدیر وارد `/account/login/` شوید و یک «کارشناس فروش» بسازید (منوی «کاربران»).
- [ ] یک درخواست آزمایشی از «دستیار هوشمند» ثبت کنید ← پیام تلگرام/ایمیل کارشناس برسد.
- [ ] یک مشتری آزمایشی ثبت‌نام و تأیید کنید و سفارش با فایل PDF بدهید.
- [ ] `https://securityheaders.com` و `https://pagespeed.web.dev` را برای دامنه اجرا کنید.
- [ ] در Google Search Console دامنه را ثبت و `sitemap.xml` را ارسال کنید؛ در Google Business پروفایل شرکت را بسازید.
- [ ] یک‌بار `backup.sh` را دستی اجرا کنید و فایل پشتیبان را روی یک ماشین دیگر هم کپی کنید.

## به‌روزرسانی سایت
محتوا را در `site-src/content.py` ویرایش کنید ← `python build.py` ← پوشه `site/` را جایگزین کنید ← `sudo systemctl restart akh`.
پایگاه‌داده و فایل‌های مشتریان در `server/instance/` است و هنگام به‌روزرسانی نباید پاک شود.
