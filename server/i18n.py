# -*- coding: utf-8 -*-
"""Tiny bilingual (fa/en) dictionary for the staff admin panel. Not used on the public marketing site,
which has its own fuller fa/en build (see src/b_pages.py build_home vs build_home_en)."""

UI = {
    'nav_dashboard': ('داشبورد', 'Dashboard'),
    'nav_leads': ('درخواست‌ها و سرنخ‌ها', 'Leads'),
    'nav_my_leads': ('سرنخ‌های من', 'My leads'),
    'nav_customers': ('مشتریان', 'Customers'),
    'nav_orders': ('سفارش‌ها', 'Orders'),
    'nav_users': ('کاربران و کارشناسان', 'Staff users'),
    'nav_2fa': ('ورود دومرحله‌ای', 'Two-factor login'),
    'nav_audit': ('گزارش امنیتی', 'Security log'),
    'nav_export_leads': ('خروجی اکسل سرنخ‌ها', 'Export leads (CSV)'),
    'nav_export_orders': ('خروجی اکسل سفارش‌ها', 'Export orders (CSV)'),
    'logout': ('خروج', 'Log out'),
    'lang_switch': ('EN', 'فارسی'),

    'dash_title': ('داشبورد', 'Dashboard'),
    'dash_new_leads': ('سرنخ جدید', 'New leads'),
    'dash_my_open': ('سرنخ‌های باز من', 'My open leads'),
    'dash_pending_members': ('عضویت در انتظار تأیید', 'Pending memberships'),
    'dash_pending_orders': ('سفارش در انتظار بررسی', 'Orders awaiting review'),
    'dash_traffic': ('بازدید سایت', 'Site traffic'),
    'dash_7d': ('بازدید ۷ روز اخیر', 'Visits, last 7 days'),
    'dash_30d': ('بازدید ۳۰ روز اخیر', 'Visits, last 30 days'),
    'dash_page': ('صفحه', 'Page'),
    'dash_views30': ('بازدید ۳۰ روز', '30-day views'),
    'dash_anon_note': ('شمارنده ناشناس است: فقط تعداد بازدید هر صفحه ثبت می‌شود، بدون کوکی و بدون IP.', 'Anonymous counter: only a per-page visit count is stored, no cookies, no IP.'),
    'dash_recent': ('آخرین درخواست‌ها', 'Recent leads'),
    'dash_none_yet': ('هنوز درخواستی ثبت نشده است.', 'No leads yet.'),

    'leads_title': ('درخواست‌ها و سرنخ‌ها', 'Leads'),
    'col_code': ('کد', 'Code'),
    'col_name': ('نام', 'Name'),
    'col_phone': ('تلفن', 'Phone'),
    'col_city': ('شهر', 'City'),
    'col_source': ('منبع', 'Source'),
    'col_status': ('وضعیت', 'Status'),
    'col_priority': ('اولویت', 'Priority'),
    'col_assigned': ('مسئول', 'Assigned to'),
    'col_date': ('تاریخ', 'Date'),
    'col_action': ('عملیات', 'Action'),
    'filter_all': ('همه', 'All'),
    'filter_mine_only': ('فقط سرنخ‌های من', 'My leads only'),
    'btn_filter': ('اعمال فیلتر', 'Apply filter'),
    'view': ('مشاهده', 'View'),

    'lead_title': ('جزئیات سرنخ', 'Lead details'),
    'lead_contact_info': ('اطلاعات تماس', 'Contact info'),
    'lead_change_status': ('تغییر وضعیت', 'Change status'),
    'lead_assign_to': ('ارجاع به', 'Assign to'),
    'lead_add_note': ('یادداشت جدید', 'Add note'),
    'lead_log_call': ('ثبت تماس', 'Log a call'),
    'lead_notes_history': ('یادداشت‌ها و تاریخچه', 'Notes & history'),
    'btn_save': ('ثبت', 'Save'),
    'btn_submit': ('ارسال', 'Submit'),

    'customers_title': ('مشتریان', 'Customers'),
    'col_company': ('شرکت', 'Company'),
    'col_job': ('شغل', 'Job'),
    'col_joined': ('تاریخ عضویت', 'Joined'),
    'col_job': ('شغل', 'Job'),
    'approve': ('تأیید', 'Approve'),
    'reject': ('رد', 'Reject'),

    'orders_title': ('سفارش‌ها', 'Orders'),
    'col_order_code': ('کد سفارش', 'Order code'),
    'col_customer': ('مشتری', 'Customer'),
    'col_total': ('مبلغ', 'Total'),

    'users_title': ('کاربران و کارشناسان', 'Staff users'),
    'users_new': ('کارشناس جدید', 'New staff member'),
    'col_role': ('نقش', 'Role'),
    'role_sales': ('کارشناس فروش', 'Sales'),
    'role_admin': ('مدیر', 'Admin'),
    'enable': ('فعال‌سازی', 'Enable'),
    'disable': ('غیرفعال‌سازی', 'Disable'),
    'create_user': ('ساخت کاربر', 'Create user'),

    'audit_title': ('گزارش امنیتی', 'Security log'),
    'col_time': ('زمان', 'Time'),
    'col_user': ('کاربر', 'User'),
    'col_event': ('رویداد', 'Event'),
    'col_ip': ('IP', 'IP'),

    'nav_home': ('خانه', 'Home'),
    'nav_crumb_label': ('مسیر', 'Breadcrumb'),

    'security_title': ('ورود دومرحله‌ای (۲FA)', 'Two-factor login (2FA)'),
    'login_title': ('ورود به حساب', 'Sign in'),
    'login_identifier': ('ایمیل یا شماره موبایل', 'Email or mobile number'),
    'login_password': ('رمز عبور', 'Password'),
    'login_btn': ('ورود', 'Sign in'),

    'login_err_pow': ('برای ادامه، تأیید امنیتی لازم است؛ صفحه را تازه کنید و دوباره تلاش کنید.', 'Please refresh the page and try again to complete the security check.'),
    'login_err_locked': ('به‌دلیل تلاش‌های ناموفق، ورود تا ۱۵ دقیقه مسدود شده است.', 'Too many failed attempts; sign-in is locked for 15 minutes.'),
    'login_err_bad_creds': ('ایمیل/شماره موبایل یا رمز عبور درست نیست.', 'Incorrect email/mobile number or password.'),
    'login_err_rejected': ('درخواست عضویت شما تأیید نشد. با کارشناس فروش تماس بگیرید.', 'Your membership request was not approved. Please contact our sales team.'),
    'login_err_disabled': ('این حساب غیرفعال شده است.', 'This account has been disabled.'),

    'register_title': ('ثبت‌نام مشتریان', 'Customer sign-up'),
    'register_intro': ('عضویت مخصوص مشتریان ثابت است. بعد از ثبت‌نام، کارشناس فروش درخواست شما را بررسی و حساب را فعال می‌کند؛ سپس می‌توانید سفارش ثبت کنید و فاکتور ارسال کنید.',
                        'Membership is for regular customers. After you sign up, our sales team will review your request and activate your account; you can then place orders and receive invoices.'),
    'register_name': ('نام و نام خانوادگی', 'Full name'),
    'register_identifier': ('ایمیل یا شماره موبایل', 'Email or mobile number'),
    'register_identifier_note': ('اگر شماره موبایل وارد می‌کنید، با 0 شروع کنید.', 'If entering a mobile number, start it with 0.'),
    'register_company': ('نام شرکت', 'Company name'),
    'register_company_ph': ('مثلاً: شرکت ساختمانی ایران‌سازه', 'e.g. Iran-Sazeh Construction Co.'),
    'register_country': ('کشور', 'Country'),
    'register_city': ('شهر', 'City'),
    'register_city_ph': ('نام شهر', 'City name'),
    'register_job': ('شغل', 'Occupation'),
    'register_job_ph': ('شغل خود را بنویسید', 'Enter your occupation'),
    'register_password': ('رمز عبور', 'Password'),
    'register_password2': ('تکرار رمز', 'Confirm password'),
    'register_password_note': ('رمز عبور حداقل ۱۰ کاراکتر، شامل حرف لاتین و عدد و غیرقابل‌حدس باشد.', 'Password: at least 10 characters, including a letter and a number, and not easily guessable.'),
    'register_btn': ('ثبت‌نام', 'Sign up'),
    'register_already': ('قبلاً ثبت‌نام کرده‌اید؟', 'Already signed up?'),
    'register_login_link': ('ورود', 'Sign in'),

    'reg_err_email_invalid': ('ایمیل معتبر نیست.', 'Enter a valid email address.'),
    'reg_err_phone_invalid': ('ایمیل یا شماره موبایل معتبر وارد کنید (مثل ۰۹۱۲۳۴۵۶۷۸۹).', 'Enter a valid email or mobile number (e.g. 09123456789).'),
    'reg_err_identifier_required': ('ایمیل یا شماره موبایل را وارد کنید.', 'Enter an email or mobile number.'),
    'reg_err_pow': ('تأیید امنیتی انجام نشد؛ جاوااسکریپت را فعال کنید و دوباره تلاش کنید.', 'Security check failed; please enable JavaScript and try again.'),
    'reg_err_name_required': ('نام و نام خانوادگی را وارد کنید.', 'Enter your full name.'),
    'reg_err_city_required': ('شهر را وارد کنید.', 'Enter your city.'),
    'reg_err_password_mismatch': ('تکرار رمز عبور یکسان نیست.', 'Password confirmation does not match.'),
    'reg_ok_duplicate': ('ثبت‌نام انجام شد. پس از تأیید کارشناس فروش حساب شما فعال می‌شود. اگر قبلاً ثبت‌نام کرده‌اید، با همان ایمیل/شماره و رمز خود وارد شوید.',
                          'Sign-up received. Your account will be activated once our sales team reviews it. If you already have an account, sign in with the same email/number and password.'),
    'reg_ok_created': ('ثبت‌نام انجام شد. پس از تأیید کارشناس فروش، حساب شما فعال می‌شود و می‌توانید وارد شوید.',
                        'Sign-up received. Your account will be activated once our sales team reviews it, and you will then be able to sign in.'),
}

PASSWORD_ERRORS = {
    'رمز عبور باید حداقل ۱۰ کاراکتر باشد.': 'Password must be at least 10 characters.',
    'رمز عبور خیلی طولانی است.': 'Password is too long.',
    'رمز عبور باید هم حرف لاتین و هم عدد داشته باشد.': 'Password must include both a letter and a number.',
    'این رمز عبور رایج و قابل حدس است؛ رمز دیگری انتخاب کنید.': 'This password is too common/guessable; please choose another one.',
    'رمز عبور نباید شامل شماره موبایل باشد.': 'Password must not contain your mobile number.',
}


def t(key, lang='fa'):
    pair = UI.get(key)
    if not pair:
        return key
    return pair[1] if lang == 'en' else pair[0]


def tp(msg, lang='fa'):
    """translate a message returned by hardening.password_problem(), if a known one"""
    if lang == 'en' and msg in PASSWORD_ERRORS:
        return PASSWORD_ERRORS[msg]
    return msg
