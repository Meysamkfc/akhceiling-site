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

    'security_title': ('ورود دومرحله‌ای (۲FA)', 'Two-factor login (2FA)'),
    'login_title': ('ورود به حساب', 'Sign in'),
    'login_identifier': ('ایمیل یا شماره موبایل', 'Email or mobile number'),
    'login_password': ('رمز عبور', 'Password'),
    'login_btn': ('ورود', 'Sign in'),
}


def t(key, lang='fa'):
    pair = UI.get(key)
    if not pair:
        return key
    return pair[1] if lang == 'en' else pair[0]
