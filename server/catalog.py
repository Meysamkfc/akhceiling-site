# -*- coding: utf-8 -*-
"""Orderable items (no prices on purpose). Specs come from the AKH printed catalog."""

THICK = ['۰٫۵ میلی‌متر', '۰٫۶ میلی‌متر']

CATALOG = [
    dict(group='پروفیل درای‌وال', items=[
        dict(key='f47', title='پروفیل F47', unit='بسته (۲۰ شاخه)', options=THICK),
        dict(key='uh36', title='پروفیل UH36', unit='بسته (۲۴ شاخه)', options=THICK),
        dict(key='l25', title='نبشی L25', unit='بسته (۲۰ شاخه)', options=THICK),
    ]),
    dict(group='اتصالات و پیچ', items=[
        dict(key='clip-f47', title='بست اتصال F47 (کلیپس)', unit='عدد', options=[]),
        dict(key='w-f47', title='بست اتصال طولی F47 (W)', unit='عدد', options=[]),
        dict(key='ht90', title='قطعه اتصال HT90', unit='عدد', options=[]),
        dict(key='bracket', title='قطعه اتصال مستقیم (براکت)', unit='عدد', options=[]),
        dict(key='hanger-spring', title='آویز فنر دوبل استیل', unit='عدد', options=[]),
        dict(key='screw', title='پیچ', unit='کارتن', options=['پیچ پانل TN 2.5 (۳٫۵×۲۵)', 'پیچ پانل TN 3.5 (۳٫۵×۳۵)', 'پیچ پانل سرمته TB 2.5', 'پیچ سازه به سازه LN 9', 'پیچ سازه سرمته LB 9.5']),
    ]),
    dict(group='سقف شبکه‌ای ۶۰×۶۰', items=[
        dict(key='tile-gypsum', title='تایل گچی', unit='متر مربع', options=['ساده', 'رویه PVC', 'آکوستیک سوراخ‌دار']),
        dict(key='tile-alu', title='تایل آلومینیومی', unit='متر مربع', options=['ساده', 'پانچ‌شده']),
        dict(key='tile-mineral', title='تایل مینرال آکوستیک', unit='متر مربع', options=['MT 100', 'MT 103', 'MT 106']),
        dict(key='tee', title='سپری (مادر / ۱۲۰ / ۶۰)', unit='شاخه', options=['سپری مادر ۳٫۶ متر', 'سپری ۱۲۰', 'سپری ۶۰']),
        dict(key='angle-l24', title='نبشی L24 سفید', unit='شاخه', options=[]),
    ]),
    dict(group='سقف گریلیوم', items=[
        dict(key='grillium', title='سقف کاذب گریلیوم', unit='متر مربع', options=['چشمه ۵×۵ سانتی‌متر', 'چشمه ۱۰×۱۰ سانتی‌متر']),
    ]),
    dict(group='سایر', items=[
        dict(key='other', title='سایر (در توضیحات بنویسید)', unit='مورد', options=[]),
    ]),
]

BY_KEY = {i['key']: i for g in CATALOG for i in g['items']}
