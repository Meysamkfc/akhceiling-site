# سرور CRM و پنل مشتریان (Flask + SQLite)

اجرا (ویندوز): `run.bat` → http://127.0.0.1:8790
ساخت مدیر اول (حساب پیش‌فرض وجود ندارد):
    .venv\Scripts\python manage.py create-user --role admin --name "نام" --phone 09xxxxxxxxx
افزودن کارشناس فروش: از پنل مدیر ← «کاربران» یا با همان دستور (`--role sales`).
اعلان کارشناسان (تلگرام/ایمیل/پیامک): `.env.example` را به `.env` کپی و پر کنید. بدون آن، اعلان‌ها فقط در `instance/notifications.log` ثبت می‌شوند.
روی هاست واقعی: پشت HTTPS بگذارید و `AKH_HTTPS=1` و (فقط پشت پروکسی خودتان) `AKH_TRUST_PROXY=1` تنظیم کنید.
تست خودکار: `python test_server.py` (۵۷ آزمون امنیت و گردش کار).
پشتیبان‌گیری: پوشه `instance/` (پایگاه‌داده + فایل‌های مشتریان) را کپی کنید.
