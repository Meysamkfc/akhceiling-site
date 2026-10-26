# -*- coding: utf-8 -*-
LEAD_STATUS = [('new', 'جدید'), ('contacted', 'تماس گرفته شد'), ('follow_up', 'نیازمند پیگیری'), ('proforma', 'پیش‌فاکتور ارسال شد'), ('won', 'موفق'), ('lost', 'ناموفق')]
LEAD_STATUS_EN = [('new', 'New'), ('contacted', 'Contacted'), ('follow_up', 'Needs follow-up'), ('proforma', 'Proforma sent'), ('won', 'Won'), ('lost', 'Lost')]
ORDER_STATUS = [('new', 'جدید'), ('reviewing', 'در حال بررسی'), ('proforma_sent', 'پیش‌فاکتور ارسال شد'), ('confirmed', 'تأیید شد'), ('shipped', 'ارسال شد'), ('delivered', 'تحویل شد'), ('canceled', 'لغو شد')]
ORDER_STATUS_EN = [('new', 'New'), ('reviewing', 'Reviewing'), ('proforma_sent', 'Proforma sent'), ('confirmed', 'Confirmed'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('canceled', 'Canceled')]
USER_STATUS = [('pending', 'در انتظار تأیید'), ('active', 'فعال'), ('rejected', 'رد شده'), ('disabled', 'غیرفعال')]
USER_STATUS_EN = [('pending', 'Pending approval'), ('active', 'Active'), ('rejected', 'Rejected'), ('disabled', 'Disabled')]
ROLES = {'customer': 'مشتری', 'sales': 'کارشناس فروش', 'admin': 'مدیر'}
ROLES_EN = {'customer': 'Customer', 'sales': 'Sales', 'admin': 'Admin'}
SOURCES = {'quote': 'فرم درخواست قیمت', 'assistant': 'دستیار هوشمند', 'contact': 'تماس'}
SOURCES_EN = {'quote': 'Quote form', 'assistant': 'Smart assistant', 'contact': 'Contact'}
BUILDINGS = {'office': 'اداری / تجاری', 'school': 'آموزشی / دانشگاهی', 'hospital': 'درمانی / بیمارستانی', 'hotel': 'هتل / لابی / فرودگاه', 'home': 'مسکونی', 'industrial': 'صنعتی / سوله'}
BUILDINGS_EN = {'office': 'Office / commercial', 'school': 'Educational / university', 'hospital': 'Medical / hospital', 'hotel': 'Hotel / lobby / airport', 'home': 'Residential', 'industrial': 'Industrial / warehouse'}
PRODUCTS = {'grid': 'سقف کاذب شبکه‌ای ۶۰×۶۰', 'drywall': 'سیستم درای‌وال و سقف گچی', 'profiles': 'پروفیل و اتصالات درای‌وال', 'other': 'سایر / نیاز به راهنمایی'}
PRODUCTS_EN = {'grid': '60x60 grid suspended ceiling', 'drywall': 'Drywall & plaster ceiling system', 'profiles': 'Drywall profiles & connectors', 'other': 'Other / needs guidance'}
FILE_KINDS = {'invoice': 'فاکتور', 'plan': 'نقشه / تصویر پروژه', 'proforma': 'پیش‌فاکتور', 'other': 'سایر'}
FILE_KINDS_EN = {'invoice': 'Invoice', 'plan': 'Project plan / image', 'proforma': 'Proforma invoice', 'other': 'Other'}
CALL_OUTCOMES = ['پاسخ داد — مایل به ادامه', 'پاسخ نداد', 'مشغول بود — بعداً تماس بگیرید', 'شماره اشتباه', 'قیمت‌گیری کرده — نیاز به پیش‌فاکتور', 'منصرف شد']
CALL_OUTCOMES_EN = ['Answered — wants to continue', 'No answer', 'Busy — call back later', 'Wrong number', 'Got pricing — needs proforma', 'Not interested']

COUNTRIES = ['ایران', 'عراق', 'افغانستان', 'ترکیه', 'امارات متحده عربی', 'عمان', 'قطر', 'کویت', 'عربستان سعودی', 'پاکستان', 'آذربایجان', 'ترکمنستان', 'ارمنستان', 'روسیه', 'سایر']
COUNTRIES_EN = ['Iran', 'Iraq', 'Afghanistan', 'Turkey', 'United Arab Emirates', 'Oman', 'Qatar', 'Kuwait', 'Saudi Arabia', 'Pakistan', 'Azerbaijan', 'Turkmenistan', 'Armenia', 'Russia', 'Other']
CITIES_IRAN = ['تهران', 'مشهد', 'اصفهان', 'کرج', 'شیراز', 'تبریز', 'قم', 'اهواز', 'کرمانشاه', 'ارومیه', 'رشت', 'زاهدان', 'همدان', 'کرمان', 'یزد', 'اردبیل', 'بندرعباس', 'اراک', 'ساری', 'قزوین',
               'زنجان', 'سنندج', 'خرم‌آباد', 'گرگان', 'بوشهر', 'بابل', 'ایلام', 'شهرکرد', 'یاسوج', 'بیرجند', 'سمنان', 'شهریار', 'ورامین', 'پاکدشت', 'سایر']
CITIES_IRAN_EN = ['Tehran', 'Mashhad', 'Isfahan', 'Karaj', 'Shiraz', 'Tabriz', 'Qom', 'Ahvaz', 'Kermanshah', 'Urmia', 'Rasht', 'Zahedan', 'Hamadan', 'Kerman', 'Yazd', 'Ardabil', 'Bandar Abbas', 'Arak', 'Sari', 'Qazvin',
                  'Zanjan', 'Sanandaj', 'Khorramabad', 'Gorgan', 'Bushehr', 'Babol', 'Ilam', 'Shahrekord', 'Yasuj', 'Birjand', 'Semnan', 'Shahriar', 'Varamin', 'Pakdasht', 'Other']
JOBS = ['کناف‌کار', 'پیمانکار', 'مهندس / ناظر', 'معمار', 'تأسیساتچی', 'فروشنده مصالح ساختمانی', 'شرکت', 'سایر']
JOBS_EN = ['Drywall installer', 'Contractor', 'Engineer / Supervisor', 'Architect', 'HVAC/plumbing technician', 'Building-materials dealer', 'Company', 'Other']

LS = dict(LEAD_STATUS)
OS = dict(ORDER_STATUS)
US = dict(USER_STATUS)
LS_EN = dict(LEAD_STATUS_EN)
OS_EN = dict(ORDER_STATUS_EN)
US_EN = dict(USER_STATUS_EN)
PRIORITY_EN = {'hot': 'Hot', 'warm': 'Warm', 'cold': 'Cold'}
