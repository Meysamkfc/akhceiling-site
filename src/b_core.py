# -*- coding: utf-8 -*-
"""Core helpers for site 2: paths, responsive images, JSON-LD, page template, header/footer."""
import os, re, json, shutil, html, datetime, hashlib, math
from PIL import Image
from content2 import *          # noqa

esc = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'site')
A = os.path.join(HERE, 'assets')
TODAY = datetime.date.today().isoformat()
FIRST_PUBLISHED = '2026-10-17'
PAGES = []            # (path, priority, changefreq, [images])
SEARCH = []           # search / assistant knowledge docs
ENTRIES = {}          # path -> dict(title, desc)

NAME_ADDR = dict(streetAddress='خیابان بهشتی، خیابان قنبرزاده، نبش هویزه، پلاک ۲۰۲', addressLocality='تهران', addressCountry='IR')

# ------------------------------------------------------------------ responsive images
WIDTHS = (480, 960, 1600)
_done = {}
def variants(rel):
    """create webp variants of assets/<rel> in site/assets/r/ and return (base, srcW, srcH)"""
    if rel in _done:
        return _done[rel]
    src = os.path.join(A, rel)
    im = Image.open(src).convert('RGB')
    w, h = im.size
    base = rel.rsplit('.', 1)[0].replace('/', '-')
    os.makedirs(os.path.join(OUT, 'assets', 'r'), exist_ok=True)
    for tw in WIDTHS:
        nw = min(tw, w)
        if nw < tw and tw != WIDTHS[0] and any(min(x, w) == nw for x in WIDTHS if x < tw):
            # source narrower than this step: reuse the previous size under this name
            nw = min(tw, w)
        out = os.path.join(OUT, 'assets', 'r', '%s-%d.webp' % (base, tw))
        r = im if nw == w else im.resize((nw, int(h * nw / w)), Image.LANCZOS)
        r.save(out, 'WEBP', quality=80, method=4)
    _done[rel] = (base, w, h)
    return _done[rel]

def rimg(rel, alt, sizes='100vw', cls='', eager=False, w=None, h=None):
    base, sw, sh = variants(rel)
    avail = sorted({min(x, sw) for x in WIDTHS})
    srcset = ', '.join('/assets/r/%s-%d.webp %dw' % (base, tw, min(tw, sw)) for tw in WIDTHS if not (tw > avail[0] and min(tw, sw) == min(WIDTHS[WIDTHS.index(tw) - 1], sw)))
    wd, ht = (w, h) if w and h else (min(960, sw), int(sh * min(960, sw) / sw))
    return ('<img src="/assets/r/%s-960.webp" srcset="%s" sizes="%s" alt="%s" width="%d" height="%d"%s%s>' %
            (base, srcset, sizes, esc(alt), wd, ht, (' class="%s"' % cls) if cls else '', ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'))

def rurl(rel, w=960):
    base, sw, sh = variants(rel)
    return '/assets/r/%s-%d.webp' % (base, w)

# ------------------------------------------------------------------ JSON-LD
ORG_ID = SITE + '/#org'
def org_node():
    return {"@type": ["Organization", "LocalBusiness"], "@id": ORG_ID, "name": NAME_FULL, "alternateName": ["AKH Ceiling Systems", "A.K.H", "صنعت سقف البرز"],
            "url": SITE + '/', "logo": {"@type": "ImageObject", "url": SITE + '/assets/img/emblem.jpg', "width": 560, "height": 260}, "image": SITE + '/assets/og/home.jpg',
            "description": "تولیدکننده پروفیل درای‌وال (F47، UH36، L25) و سقف کاذب شبکه‌ای ۶۰×۶۰؛ کارخانه کهریزک و دفتر مرکزی تهران، ارسال به سراسر کشور.",
            "telephone": "+982188507585", "email": EMAIL, "priceRange": "$$", "address": dict(NAME_ADDR, **{"@type": "PostalAddress"}),
            "areaServed": {"@type": "Country", "name": "Iran"}, "knowsAbout": ["Drywall profiles", "Suspended ceilings", "Metal stud framing"],
            "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday"], "opens": "09:00", "closes": "17:00"},
                                          {"@type": "OpeningHoursSpecification", "dayOfWeek": "Thursday", "opens": "09:00", "closes": "13:00"}],
            "contactPoint": [{"@type": "ContactPoint", "telephone": "+982188507585", "contactType": "sales", "areaServed": "IR", "availableLanguage": ["fa"]},
                             {"@type": "ContactPoint", "telephone": "+982156548804", "contactType": "customer service", "areaServed": "IR", "availableLanguage": ["fa"]}],
            "sameAs": ["https://t.me/" + TELEGRAM, "https://instagram.com/" + INSTAGRAM]}

def website_node():
    return {"@type": "WebSite", "@id": SITE + '/#website', "url": SITE + '/', "name": NAME_FULL, "inLanguage": "fa-IR", "publisher": {"@id": ORG_ID},
            "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": SITE + '/search/?q={search_term_string}'}, "query-input": "required name=search_term_string"}}

def crumbs_node(items, url):
    return {"@type": "BreadcrumbList", "@id": url + '#breadcrumb', "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (u, n) in enumerate(items)]}

def faq_node(items, url):
    return {"@type": "FAQPage", "@id": url + '#faq', "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

# ------------------------------------------------------------------ icons / diagrams
def icon(name):
    d = {
        'search': '<circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M16.5 16.5L21 21" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>',
        'phone': '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>',
        'user': '<circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4 21c1-4 4-6 8-6s7 2 8 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
        'menu': '<path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>',
        'bot': '<rect x="5" y="9" width="14" height="11" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 9V5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="3.3" r="1.5" fill="currentColor"/><circle cx="9" cy="14.5" r="1.3" fill="currentColor"/><circle cx="15" cy="14.5" r="1.3" fill="currentColor"/><path d="M9 18h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
        'mail': '<rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4 7l8 6 8-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
        'telegram': '<path d="M20.5 4L3 11.2l5 1.8m12.5-9L17 20l-6.5-5m10-11L10.5 13" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>',
        'instagram': '<rect x="4" y="4" width="16" height="16" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="3.6" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17" cy="7" r="1" fill="currentColor"/>',
    }[name]
    return '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">%s</svg>' % d

def diagram(kind, lang='fa'):
    slab = '<rect x="10" y="6" width="380" height="14" fill="#d8daec"/>'
    if kind == 'drywall':
        body = (slab + '<g stroke="#15173f" stroke-width="3" fill="none"><path class="dgline" pathLength="1" d="M70 20v46"/><path class="dgline" pathLength="1" d="M200 20v46"/><path class="dgline" pathLength="1" d="M330 20v46"/></g><rect x="30" y="66" width="340" height="9" fill="#2e3192"/>'
                '<g fill="#f6821f"><rect x="52" y="75" width="12" height="11"/><rect x="132" y="75" width="12" height="11"/><rect x="212" y="75" width="12" height="11"/><rect x="292" y="75" width="12" height="11"/><rect x="352" y="75" width="12" height="11"/></g>'
                '<rect x="20" y="86" width="360" height="9" fill="#23266e"/><rect x="10" y="100" width="380" height="16" fill="#ffffff" stroke="#15173f" stroke-width="2.5"/>'
                '<text x="200" y="148" text-anchor="middle" font-size="15" font-weight="700" fill="#5c5f82">F47 · UH36 · L25</text>')
    elif kind == 'grid':
        z = 'M70 20l-6 5 12 6-12 6 12 6-12 6 12 6-6 5'
        body = (slab + ''.join('<path class="dgline" pathLength="1" d="%s" transform="translate(%d,0)" fill="none" stroke="#15173f" stroke-width="3"/>' % (z, x) for x in (0, 130, 260)) +
                '<rect x="20" y="74" width="360" height="7" fill="#2e3192"/><g fill="#ffffff" stroke="#15173f" stroke-width="2"><rect x="14" y="96" width="82" height="18"/><rect x="102" y="96" width="82" height="18"/><rect x="190" y="96" width="82" height="18"/><rect x="278" y="96" width="82" height="18"/></g>'
                '<g fill="#f6821f"><rect x="96" y="92" width="6" height="26"/><rect x="184" y="92" width="6" height="26"/><rect x="272" y="92" width="6" height="26"/></g>'
                '<text x="200" y="148" text-anchor="middle" font-size="15" font-weight="700" fill="#5c5f82">60 × 60</text>')
    else:
        body = slab
    label = 'Schematic ceiling cross-section' if lang == 'en' else 'تصویر شماتیک مقطع سقف'
    return '<svg viewBox="0 0 400 160" role="img" aria-label="%s" class="dg">%s</svg>' % (label, body)

def flip_text(text, duration=2.2, delay=0, loop=False, separator=' ', together=False, cls=''):
    """3D card-flip reveal, one flip unit per WORD (precomputed at build time, no client JS needed).
    Stagger timing ported from VengeanceUI's flip-text component (MIT, github.com/Ashutoshx7/VengeanceUI),
    which flips per character — that breaks Persian/Arabic script (isolates letters, so they lose their
    joined shape, and reverses the visual order), so here the flip unit is the whole word instead."""
    words = [w for w in text.split(separator) if w]
    total = len(words)
    it = 'infinite' if loop else '1'
    out = []
    for wi, word in enumerate(words):
        d = delay if together or total <= 1 else math.sin((wi / total) * (math.pi / 2)) * (duration * 0.25) + delay
        out.append('<span class="flip-char" data-char="%s" style="--flip-duration:%ss;--flip-delay:%.4fs;--flip-iteration:%s">%s</span>' % (esc(word), duration, d, it, esc(word)))
        if wi < total - 1:
            out.append('&nbsp;')
    return '<span class="flip-text-wrap%s" style="perspective:1000px">%s</span>' % (' ' + cls if cls else '', ''.join(out))

# ------------------------------------------------------------------ layout
NAV = [('/products/', 'محصولات', 'products'), ('/projects/', 'پروژه‌ها', None), ('/estimate/', 'برآورد متریال', None), ('/assistant/', 'دستیار هوشمند', None),
       ('/articles/', 'منابع', 'res'), ('/about/', 'درباره ما', None)]
# EN_NAME is the brand name already established in the site's own schema.org alternateName.
EN_NAME = 'AKH Ceiling Systems'
EN_PRODUCT_NAME = {'drywall': 'Drywall &amp; plaster ceiling system', 'grid-ceiling': '60x60 grid suspended ceiling', 'profiles': 'Drywall profiles &amp; connectors', 'accessories': 'Installation accessories'}
EN_PRODUCT_SHORT = {'drywall': 'A seamless, joint-free ceiling with recessed lighting boxes and partition walls', 'grid-ceiling': 'Removable tiles with easy access to services above the ceiling',
                    'profiles': 'F47, UH36, L25, clips, screws and connectors with a full spec table',
                    'accessories': 'Screws, nails, joint tape and connectors for every ceiling system'}
EN_NAV = [('/en/products/', 'Products', None), ('/en/projects/', 'Projects', None), ('/en/estimate/', 'Material Estimate', None), ('/en/assistant/', 'Smart Assistant', None),
          ('/en/articles/', 'Resources', 'res'), ('/en/about/', 'About Us', None)]

# every Persian page that has a real, built English counterpart (and back).
LANG_PAIRS = [
    ('/', '/en/'), ('/products/', '/en/products/'),
    ('/products/drywall/', '/en/products/drywall/'), ('/products/grid-ceiling/', '/en/products/grid-ceiling/'),
    ('/products/profiles/', '/en/products/profiles/'), ('/products/accessories/', '/en/products/accessories/'),
    ('/projects/', '/en/projects/'), ('/about/', '/en/about/'), ('/contact/', '/en/contact/'),
    ('/quote/', '/en/quote/'), ('/estimate/', '/en/estimate/'), ('/assistant/', '/en/assistant/'), ('/membership/', '/en/membership/'),
    # Phase 2: articles, FAQ, glossary, catalogs, privacy. (search and 404 intentionally stay Persian-only, noindex anyway.)
    ('/articles/', '/en/articles/'), ('/faq/', '/en/faq/'), ('/glossary/', '/en/glossary/'),
    ('/catalogs/', '/en/catalogs/'), ('/privacy/', '/en/privacy/'),
] + [('/articles/%s/' % a['slug'], '/en/articles/%s/' % a['slug']) for a in ARTICLES]
FA2EN = dict(LANG_PAIRS)
EN2FA = {v: k for k, v in LANG_PAIRS}

def lang_switch(path, lang):
    """the opposite-language equivalent of this path, if one exists."""
    if lang == 'fa':
        t = FA2EN.get(path)
        return (t, 'EN') if t else None
    if lang == 'en':
        t = EN2FA.get(path)
        return (t, 'فارسی') if t else None
    return None

def topbar(lang='fa'):
    tel = 'tel:+98' + PHONE.replace('-', '').lstrip('0')
    if lang == 'en':
        return ('<div class="topbar"><div class="wrap in"><div class="tb-c"><a href="%s">%s</a><a href="mailto:%s">%s</a></div>'
                '<div class="tb-s"><a href="https://t.me/%s" aria-label="Telegram" rel="noopener">%s</a><a href="https://instagram.com/%s" aria-label="Instagram" rel="noopener">%s</a></div></div></div>'
                % (tel, PHONE, EMAIL, EMAIL, TELEGRAM, icon('telegram'), INSTAGRAM, icon('instagram')))
    return ('<div class="topbar"><div class="wrap in"><div class="tb-c"><a href="%s">%s</a><a href="mailto:%s">%s</a></div>'
            '<div class="tb-s"><a href="https://t.me/%s" aria-label="تلگرام" rel="noopener">%s</a><a href="https://instagram.com/%s" aria-label="اینستاگرام" rel="noopener">%s</a></div></div></div>'
            % (tel, PHONE_FA, EMAIL, EMAIL, TELEGRAM, icon('telegram'), INSTAGRAM, icon('instagram')))

def header(path, dynamic=False, lang='fa'):
    if lang == 'en':
        li = ''
        for href, label, sub in EN_NAV:
            cur = ' aria-current="page"' if (path == href or (sub != 'res' and path.startswith(href))) else ''
            if sub == 'res':
                subs = '<a href="/en/articles/">Articles &amp; guides</a><a href="/en/faq/">FAQ</a><a href="/en/catalogs/">Catalogs (PDF)</a>'
                li += '<li><a href="%s"%s>%s ▾</a><div class="sub">%s</div></li>' % (href, cur if path.startswith(('/en/articles', '/en/faq', '/en/catalogs')) else '', label, subs)
            else:
                li += '<li><a href="%s"%s>%s</a></li>' % (href, cur, label)
        if dynamic:
            acct = '{% if user %}<a class="ibtn hide-m" aria-label="My account" href="{{ \"/admin/\" if user.role != \"customer\" else \"/account/\" }}">' + icon('user') + '<span class="lbl">My account</span></a>{% else %}<a class="ibtn hide-m" aria-label="Sign in / Membership" href="/account/login/?lang=en">' + icon('user') + '<span class="lbl">Sign in</span></a>{% endif %}'
            mobile_acct_en = ('<li class="nav-ex">{% if user %}<a href="{{ \"/admin/\" if user.role != \"customer\" else \"/account/\" }}">My account</a>'
                               '{% else %}<a href="/account/login/?lang=en">Sign in / Membership</a>{% endif %}</li>')
        else:
            acct = '<a class="ibtn hide-m" aria-label="Membership and customer panel" href="/en/membership/">' + icon('user') + '<span class="lbl">Sign in</span></a>'
            mobile_acct_en = '<li class="nav-ex"><a href="/en/membership/">Sign in / Membership</a></li>'
        if dynamic:
            signup_cta = '{% if user %}<a class="ibtn fill signup-cta" href="{{ \"/admin/\" if user.role != \"customer\" else \"/account/\" }}" aria-label="My account">' + icon('user') + '<span class="lbl">My account</span></a>{% else %}<a class="ibtn fill signup-cta" href="/account/register/?lang=en" aria-label="Sign up">' + icon('user') + '<span class="lbl">Sign up</span></a>{% endif %}'
        else:
            signup_cta = '<a class="ibtn fill signup-cta" href="/account/register/?lang=en" aria-label="Sign up">' + icon('user') + '<span class="lbl">Sign up</span></a>'
        phoned = '<a class="ibtn fill call-cta" href="/en/contact/" aria-label="Contact us">%s<span class="lbl">Contact</span></a>' % icon('phone') + signup_cta
        sw = lang_switch(path, lang)
        swlink = '<a class="ibtn hide-m" href="%s">%s</a>' % sw if sw else ''
        li += ('<li class="nav-ex nav-ex-first"><button type="button" data-search>Search the site</button></li>'
               + mobile_acct_en
               + ('<li class="nav-ex"><a href="%s">%s</a></li>' % sw if sw else ''))
        return (topbar(lang) + '<header class="hdr" id="hdr"><div class="wrap in"><a class="brand" href="/en/"><img src="/assets/img/emblem.jpg" alt="%s logo" width="560" height="260"><span>%s</span></a>'
                '<ul class="nav" id="nav">%s</ul><div class="tools">'
                '<button class="ibtn hide-m" type="button" data-search aria-label="Search the site">%s<span class="lbl">Search</span><span class="kbd">Ctrl K</span></button>%s%s%s'
                '<button class="ibtn burger" id="burger" type="button" aria-expanded="false" aria-controls="nav">%s<span class="lbl">Menu</span></button></div></div></header>'
                % (esc(EN_NAME), esc(EN_NAME), li, icon('search'), acct, phoned, swlink, icon('menu')))
    li = ''
    for href, label, sub in NAV:
        cur = ' aria-current="page"' if (path == href or (href != '/' and path.startswith(href) and sub != 'res')) else ''
        if sub == 'products':
            subs = ''.join('<a href="/products/%s/">%s</a>' % (p['slug'], esc(p['title'])) for p in PRODUCTS) + '<a href="/products/profiles/">%s</a>' % PROFILES['title']
            li += '<li><a href="%s"%s>%s ▾</a><div class="sub">%s</div></li>' % (href, cur, label, subs)
        elif sub == 'res':
            subs = ('<a href="/articles/">مقالات آموزشی</a><a href="/faq/">پرسش‌های متداول</a><a href="/catalogs/">کاتالوگ‌ها (PDF)</a>')
            li += '<li><a href="%s"%s>%s ▾</a><div class="sub">%s</div></li>' % (href, cur if path.startswith(('/articles', '/faq', '/catalogs')) else '', label, subs)
        else:
            li += '<li><a href="%s"%s>%s</a></li>' % (href, cur, label)
    if dynamic:
        acct = '{% if user %}<a class="ibtn hide-m" aria-label="پنل من" href="{{ \"/admin/\" if user.role != \"customer\" else \"/account/\" }}">' + icon('user') + '<span class="lbl">پنل من</span></a>{% else %}<a class="ibtn hide-m" aria-label="ورود / عضویت" href="/account/login/">' + icon('user') + '<span class="lbl">ورود</span></a>{% endif %}'
        mobile_acct = ('<li class="nav-ex">{% if user %}<a href="{{ \"/admin/\" if user.role != \"customer\" else \"/account/\" }}">پنل من</a>'
                       '{% else %}<a href="/account/login/">ورود / عضویت</a>{% endif %}</li>')
    else:
        acct = '<a class="ibtn hide-m" aria-label="عضویت و پنل مشتریان" href="/membership/">' + icon('user') + '<span class="lbl">ورود / عضویت</span></a>'
        mobile_acct = '<li class="nav-ex"><a href="/membership/">ورود / عضویت</a></li>'
    if dynamic:
        signup_cta = '{% if user %}<a class="ibtn fill signup-cta" href="{{ \"/admin/\" if user.role != \"customer\" else \"/account/\" }}" aria-label="پنل من">' + icon('user') + '<span class="lbl">پنل من</span></a>{% else %}<a class="ibtn fill signup-cta" href="/account/register/" aria-label="ثبت‌نام">' + icon('user') + '<span class="lbl">ثبت‌نام</span></a>{% endif %}'
    else:
        signup_cta = '<a class="ibtn fill signup-cta" href="/account/register/" aria-label="ثبت‌نام">' + icon('user') + '<span class="lbl">ثبت‌نام</span></a>'
    phoned = '<a class="ibtn fill call-cta" href="/contact/" aria-label="تماس با ما">%s<span class="lbl">تماس</span></a>' % icon('phone') + signup_cta
    sw = lang_switch(path, lang)
    swlink = '<a class="ibtn hide-m" href="%s">%s</a>' % sw if sw else ''
    li += ('<li class="nav-ex nav-ex-first"><button type="button" data-search>جست‌وجو در سایت</button></li>'
           + mobile_acct
           + ('<li class="nav-ex"><a href="%s">%s</a></li>' % sw if sw else ''))
    return (topbar(lang) + '<header class="hdr" id="hdr"><div class="wrap in"><a class="brand" href="/"><img src="/assets/img/emblem.jpg" alt="نشان %s" width="560" height="260"><span>%s</span></a>'
            '<ul class="nav" id="nav">%s</ul><div class="tools">'
            '<button class="ibtn hide-m" type="button" data-search aria-label="جست‌وجو در سایت">%s<span class="lbl">جست‌وجو</span><span class="kbd">Ctrl K</span></button>%s%s%s'
            '<button class="ibtn burger" id="burger" type="button" aria-expanded="false" aria-controls="nav">%s<span class="lbl">منو</span></button></div></div></header>'
            % (esc(NAME), esc(NAME_FULL), li, icon('search'), acct, phoned, swlink, icon('menu')))

def palette(lang='fa'):
    if lang == 'en':
        return ('<div class="pal" id="pal" hidden role="dialog" aria-modal="true" aria-label="Search"><div class="pbox"><input type="search" placeholder="Search the site: F47, grid ceiling, panel screw…" aria-label="Search query" autocomplete="off">'
                '<div class="pres" role="listbox"></div><div class="pfoot"><span>↑↓ Move</span><span>Enter Open</span><span>Esc Close</span></div></div></div>')
    return ('<div class="pal" id="pal" hidden role="dialog" aria-modal="true" aria-label="جست‌وجو"><div class="pbox"><input type="search" placeholder="جست‌وجو در سایت: F47، سقف شبکه‌ای، پیچ پانل…" aria-label="عبارت جست‌وجو" autocomplete="off">'
            '<div class="pres" role="listbox"></div><div class="pfoot"><span>↑↓ حرکت</span><span>Enter باز کردن</span><span>Esc بستن</span></div></div></div>')

MASCOT_IMG = '<img src="/assets/img/alborzbot-mascot.png" alt="" width="377" height="539">'

def assistant_fab(lang='fa'):
    name = 'AlborzBot' if lang == 'en' else 'البرزبات'
    min_label = 'Minimize' if lang == 'en' else 'کوچک‌کردن'
    close_label = 'Close' if lang == 'en' else 'بستن'
    wave = '<span class="wave-hand" aria-hidden="true">&#x1F44B;</span>'
    greet = ('Hi, I&rsquo;m AlborzBot, your smart expert, %s if you have a question, ask right now.' % wave if lang == 'en'
             else 'سلام، من البرزبات، کارشناس هوشمند، %s اگر سؤالی دارید همین حالا بپرسید.' % wave)
    tip = ('<div class="fab-tip" id="fabTip"><div class="tip-hd"><span class="tip-ic">%s</span><b>%s</b>'
           '<button type="button" class="tip-min" id="fabTipMin" aria-label="%s">&#x2212;</button><button type="button" class="tip-x" id="fabTipClose" aria-label="%s">&#x2715;</button></div>'
           '<p>%s</p></div>' % (MASCOT_IMG, name, min_label, close_label, greet))
    if lang == 'en':
        return tip + '<a class="fab" id="fabChat" href="/en/assistant/" aria-label="Chat with the smart assistant" aria-expanded="false" aria-controls="chatWidget">%s</a>' % MASCOT_IMG
    return tip + ('<a class="fab" id="fabChat" href="/assistant/" aria-label="گفت‌وگو با دستیار هوشمند" aria-expanded="false" aria-controls="chatWidget">%s</a>' % MASCOT_IMG)

def assistant_widget(lang='fa'):
    close_label = 'Close' if lang == 'en' else 'بستن'
    min_label = 'Minimize' if lang == 'en' else 'کوچک‌کردن'
    name = 'AlborzBot' if lang == 'en' else 'البرزبات'
    return ('<div class="chat-widget" id="chatWidget" role="dialog" aria-modal="false" aria-label="%s" hidden>'
            '<div class="chat-hd" id="chatWidgetHd"><span class="cw-ic">%s</span><b>%s</b>'
            '<button type="button" class="cw-min" id="chatWidgetMin" aria-label="%s">&#x2212;</button><button type="button" class="cw-x" id="chatWidgetClose" aria-label="%s">&#x2715;</button></div>'
            '<div class="msgs" id="msgs" aria-live="polite"></div><div class="composer" id="composer"></div></div>'
            % (name, MASCOT_IMG, name, min_label, close_label))

def lightbox(lang='fa'):
    if lang == 'en':
        return ('<div class="lb" id="lb" hidden role="dialog" aria-modal="true" aria-label="Image viewer"><button class="x" aria-label="Close">✕</button><button class="n" aria-label="Next image">‹</button>'
                '<button class="p" aria-label="Previous image">›</button><figure><img id="lbi" alt=""><figcaption id="lbc"></figcaption></figure></div>')
    return ('<div class="lb" id="lb" hidden role="dialog" aria-modal="true" aria-label="نمایش عکس"><button class="x" aria-label="بستن">✕</button><button class="n" aria-label="عکس بعدی">‹</button>'
            '<button class="p" aria-label="عکس قبلی">›</button><figure><img id="lbi" alt=""><figcaption id="lbc"></figcaption></figure></div>')

ADDR_OFFICE_EN = 'No. 202, corner of Havizeh St. &amp; Ghanbarzadeh St., Beheshti St., Tehran, Iran'
ADDR_FACTORY_EN = 'No. 4, Aftabgardan Alley, Keshavarz St., Hamzeh-abad St., Shoorabad 60m St., Kahrizak, Iran'
HOURS_EN = ['Saturday–Wednesday: 9:00 AM – 5:00 PM', 'Thursday: 9:00 AM – 1:00 PM']

def footer(lang='fa'):
    if lang == 'en':
        prod_en = ''.join('<li><a href="/en/products/%s/">%s</a></li>' % (p['slug'], EN_PRODUCT_NAME[p['slug']]) for p in PRODUCTS) + '<li><a href="/en/products/profiles/">%s</a></li>' % EN_PRODUCT_NAME['profiles']
        return ('<footer class="ft"><div class="wrap"><p class="big">Profiles, ceilings and partitions; <em class="o">from factory to site</em></p><div class="cols">'
                '<div><h2>%s</h2><p class="slogan">Heritage, a mark of quality</p><p>Manufacturer of drywall and suspended-ceiling materials, with a factory in Kahrizak and nationwide delivery.</p></div>'
                '<div><h2>Products</h2><ul>%s</ul></div>'
                '<div><h2>Quick links</h2><ul><li><a href="/en/estimate/">Material estimate</a></li><li><a href="/en/assistant/">Smart assistant</a></li><li><a href="/en/quote/">Request a quote</a></li><li><a href="/en/catalogs/">Catalogs</a></li><li><a href="/en/projects/">Projects</a></li><li><a href="/en/faq/">FAQ</a></li><li><a href="/en/articles/">Articles</a></li><li><a href="/en/membership/">Customer sign-in</a></li></ul></div>'
                '<div><h2>Contact</h2><ul><li>Head office: <a class="num" href="tel:+982188507585">%s</a></li><li>Factory: <a class="num" href="tel:+982156548804">%s</a></li><li>%s</li><li><a class="num" href="mailto:%s">%s</a></li><li>%s<br>%s</li></ul></div></div>'
                '<div class="copy"><span>© %s — All rights reserved.</span><span><a href="/en/privacy/">Privacy</a> · <a href="https://t.me/%s" rel="noopener">Telegram</a> · <a href="https://instagram.com/%s" rel="noopener">Instagram</a></span></div></div></footer>'
                % (EN_NAME, prod_en, PHONE, PHONE_FACTORY, ADDR_OFFICE_EN, EMAIL, EMAIL, HOURS_EN[0], HOURS_EN[1], EN_NAME, TELEGRAM, INSTAGRAM))
    prod = ''.join('<li><a href="/products/%s/">%s</a></li>' % (p['slug'], esc(p['title'])) for p in PRODUCTS) + '<li><a href="/products/profiles/">%s</a></li>' % PROFILES['title']
    return ('<footer class="ft"><div class="wrap"><p class="big">پروفیل، سقف و دیوار کاذب؛ <em class="o">از کارخانه تا اجرا</em></p><div class="cols">'
            '<div><h2>%s</h2><p class="slogan">قدمت، نماد کیفیت</p><p>تولیدکننده متریال سقف و دیوار کاذب و سیستم درای‌وال با کارخانه در کهریزک و ارسال به سراسر کشور.</p></div>'
            '<div><h2>محصولات</h2><ul>%s</ul></div>'
            '<div><h2>دسترسی سریع</h2><ul><li><a href="/estimate/">برآورد متریال</a></li><li><a href="/assistant/">دستیار هوشمند</a></li><li><a href="/quote/">درخواست قیمت</a></li><li><a href="/catalogs/">کاتالوگ‌ها</a></li><li><a href="/projects/">پروژه‌ها</a></li><li><a href="/faq/">پرسش‌های متداول</a></li><li><a href="/articles/">مقالات</a></li><li><a href="/account/login/">ورود مشتریان</a></li></ul></div>'
            '<div><h2>تماس</h2><ul><li>دفتر مرکزی: <a class="num" href="tel:+982188507585">%s</a> (۱۰ خط)</li><li>کارخانه: <a class="num" href="tel:+982156548804">%s</a></li><li>%s</li><li><a class="num" href="mailto:%s">%s</a></li><li>%s<br>%s</li></ul></div></div>'
            '<div class="copy"><span>© %s — همه حقوق محفوظ است.</span><span><a href="/privacy/">حریم خصوصی</a> · <a href="https://t.me/%s" rel="noopener">تلگرام</a> · <a href="https://instagram.com/%s" rel="noopener">اینستاگرام</a> · <a href="/.well-known/security.txt">امنیت</a></span></div></div></footer>'
            % (NAME_FULL, prod, PHONE_FA, PHONE_FACTORY_FA, ADDR_OFFICE, EMAIL, EMAIL, HOURS[0], HOURS[1], NAME_FULL, TELEGRAM, INSTAGRAM))

# ------------------------------------------------------------------ page template (SEO + security)
OGMAP = {}
def og_for(path):
    return '/assets/og/%s.jpg' % OGMAP.get(path, 'home')

def page(path, title, desc, body, extra_ld=None, home=False, scripts=(), modules=(), og=None, images=None, noindex=False, article=False, kind='WebPage', preload=None, priority='0.7', freq='monthly', crumbs=None, lang='fa'):
    url = SITE + path
    og_url = SITE + (og or og_for(path))
    ld = [org_node(), website_node()]
    wp = {"@type": kind, "@id": url + '#webpage', "url": url, "name": title, "description": desc, "inLanguage": ("en-US" if lang == 'en' else "fa-IR"), "isPartOf": {"@id": SITE + '/#website'}, "about": {"@id": ORG_ID},
          "primaryImageOfPage": {"@type": "ImageObject", "url": og_url, "width": 1200, "height": 630}, "datePublished": FIRST_PUBLISHED, "dateModified": TODAY}
    if crumbs:
        ld.append(crumbs_node(crumbs, url)); wp['breadcrumb'] = {"@id": url + '#breadcrumb'}
    ld.append(wp)
    ld += (extra_ld or [])
    jl = '<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@graph": ld}, ensure_ascii=False, separators=(',', ':'))
    robots = 'noindex,nofollow' if noindex else 'index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1'
    js = ''.join('<script src="/assets/js/%s" defer></script>' % s for s in scripts)
    gsv = '<meta name="google-site-verification" content="%s">' % esc(GOOGLE_SITE_VERIFICATION) if GOOGLE_SITE_VERIFICATION else ''
    pre = ''
    if preload:
        pre = '<link rel="preload" as="image" href="%s" imagesrcset="%s" imagesizes="100vw" fetchpriority="high">' % preload
    if lang == 'en':
        fa_eq = EN2FA.get(path, '/')
        alt_tags = ('<link rel="alternate" hreflang="en" href="%s"><link rel="alternate" hreflang="fa-IR" href="%s%s"><link rel="alternate" hreflang="x-default" href="%s%s">' % (url, SITE, fa_eq, SITE, fa_eq))
    else:
        en_eq = FA2EN.get(path)
        if en_eq:
            alt_tags = ('<link rel="alternate" hreflang="fa-IR" href="%s"><link rel="alternate" hreflang="en" href="%s%s"><link rel="alternate" hreflang="x-default" href="%s">' % (url, SITE, en_eq, url))
        else:
            alt_tags = ('<link rel="alternate" hreflang="fa-IR" href="%s"><link rel="alternate" hreflang="x-default" href="%s">' % (url, url))
    skip = 'Skip to content' if lang == 'en' else 'پرش به محتوا'
    brand_name = EN_NAME if lang == 'en' else NAME_FULL
    rss_title = 'Articles' if lang == 'en' else ('مقالات ' + esc(NAME))
    doc = f'''<!doctype html>
<html lang="{'en' if lang == 'en' else 'fa'}" dir="{'ltr' if lang == 'en' else 'rtl'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
{alt_tags}
<meta name="theme-color" content="#15173f"><meta name="color-scheme" content="light"><meta name="format-detection" content="telephone=no">
<meta name="referrer" content="strict-origin-when-cross-origin"><meta name="author" content="{esc(brand_name)}">
{gsv}
<meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:locale" content="{'en_US' if lang == 'en' else 'fa_IR'}"><meta property="og:site_name" content="{esc(brand_name)}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{og_url}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{esc(title)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{og_url}">
<link rel="icon" href="/assets/img/favicon.png" sizes="64x64"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png"><link rel="manifest" href="/manifest.webmanifest">
<link rel="alternate" type="application/rss+xml" title="{rss_title}" href="/rss.xml">
<link rel="preload" href="/assets/fonts/vazirmatn-arabic.woff2" as="font" type="font/woff2" crossorigin>
{pre}
<link rel="stylesheet" href="/assets/css/site2.css">
<script src="/assets/js/flag.js"></script>
{jl}
</head>
<body class="{'home' if home else 'inner'}">
<a class="skip" href="#main">{skip}</a>
{header(path, lang=lang)}
<main id="main">
{body}
</main>
{footer(lang=lang)}
{'' if path in ('/assistant/', '/en/assistant/') else assistant_fab(lang=lang) + assistant_widget(lang=lang)}
{palette(lang=lang)}
{lightbox(lang=lang)}
<script type="module" src="/assets/js/main.js"></script>
{js}
</body></html>'''
    fp = os.path.join(OUT, path.strip('/'), 'index.html') if path != '/404.html' else os.path.join(OUT, '404.html')
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w', encoding='utf-8').write(inline_to_classes(apply_xsty(doc)))
    ENTRIES[path] = dict(title=title, desc=desc)
    if not noindex:
        PAGES.append((path, priority, freq, images or []))

# hand-written utility tokens used in b_pages (x1..x25) -> real CSS declarations
XSTY = {'x1': 'margin-top:28px', 'x2': 'margin:10px 0 18px', 'x3': 'margin-bottom:24px', 'x4': 'margin-top:4px', 'x5': 'margin-top:26px', 'x6': 'margin-top:22px', 'x7': 'margin-bottom:14px',
        'x8': 'margin-top:12px', 'x9': 'margin-top:24px', 'x10': 'max-width:780px', 'x11': 'margin-top:34px', 'x12': 'margin:0', 'x13': 'font-weight:800;font-size:15px', 'x14': 'margin-bottom:22px',
        'x15': 'margin-top:14px', 'x16': 'margin-top:18px', 'x17': 'margin-top:34px', 'x18': 'white-space:pre-wrap;background:#fff;border:1px solid var(--ink);padding:12px;font-family:inherit', 'x19': 'margin-top:18px',
        'x20': 'align-items:start', 'x21': 'margin-top:18px', 'x22': 'margin-top:14px', 'x23': 'max-width:880px', 'x24': 'margin-top:26px', 'x25': 'text-align:center'}
def apply_xsty(doc):
    def fix(m):
        t = m.group(0); toks = m.group(1).split(); keep = [k for k in toks if k not in XSTY]; st = ';'.join(XSTY[k] for k in toks if k in XSTY)
        if not st: return t
        t = t.replace('class="%s"' % m.group(1), ('class="%s"' % ' '.join(keep)) if keep else '', 1)
        return re.sub(r'^<(\w+)', lambda mm: '<%s style="%s"' % (mm.group(1), st), t, 1)
    return re.sub(r'<[a-zA-Z][^>]*\sclass="([^"]*x\d{1,2}[^"]*)"[^>]*>', fix, doc)

# inline style attributes are not allowed by the CSP: convert them to generated utility classes
_STYLES = {}
def inline_to_classes(doc):
    def tag(m):
        t = m.group(0)
        sm = re.search(r'\sstyle="([^"]*)"', t)
        if not sm:
            return t
        css = sm.group(1).strip().rstrip(';')
        cls = _STYLES.setdefault(css, 'u' + str(len(_STYLES) + 1))
        t = t.replace(sm.group(0), '', 1)
        cm = re.search(r'\sclass="([^"]*)"', t)
        if cm:
            return t.replace(cm.group(0), ' class="' + cm.group(1) + ' ' + cls + '"', 1)
        return re.sub(r'^<(\w+)', lambda mm: '<' + mm.group(1) + ' class="' + cls + '"', t, 1)
    return re.sub(r'<[a-zA-Z][^>]*\sstyle="[^"]*"[^>]*>', tag, doc)

def phero(h1, lead, crumbs, actions='', lang='fa'):
    cr = ''.join(('<span><a href="%s">%s</a></span>' % (u, n)) if u else '<span>%s</span>' % n for u, n in crumbs)
    label = 'Breadcrumb' if lang == 'en' else 'مسیر'
    return '<section class="phero"><div class="wrap"><nav class="crumbs" aria-label="%s">%s</nav><h1>%s</h1><p class="lead">%s</p>%s</div></section>' % (label, cr, h1, lead, actions)

def cta(title=None, text=None, lang='fa'):
    if lang == 'en':
        title = title or 'Get a quote for your project'
        text = text or 'Tell us the area and project type; our team will contact you.'
        labels = ('Request a quote', 'Chat with the assistant')
        quote_url, assistant_url = '/en/quote/', '/en/assistant/'
    else:
        title = title or 'برای پروژه خود قیمت بگیرید'
        text = text or 'متراژ و نوع پروژه را بنویسید؛ کارشناسان ما با شما تماس می‌گیرند.'
        labels = ('درخواست قیمت', 'گفت‌وگو با دستیار')
        quote_url, assistant_url = '/quote/', '/assistant/'
    return ('<section class="sec sm"><div class="wrap"><div class="cta rv"><div><h2>%s</h2><p>%s</p></div><div class="row"><a class="btn" href="%s">%s</a>'
            '<a class="btn line" href="%s">%s</a></div></div></div></section>' % (title, text, quote_url, labels[0], assistant_url, labels[1]))

def kicker(n, text):
    return '<div class="kicker"><b>%s</b>%s</div>' % (n, text)

def table_html(rows, head):
    return ('<div class="scroll"><table class="tbl"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' %
            (''.join('<th>%s</th>' % h for h in head), ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r) for r in rows)))

def faq_html(items):
    return '<div class="faq">%s</div>' % ''.join('<details><summary>%s</summary><div>%s</div></details>' % (esc(q), esc(a)) for q, a in items)

def add_doc(title, text, url, group, keywords=''):
    SEARCH.append(dict(t=title, x=re.sub(r'\s+', ' ', text).strip(), u=url, g=group, k=keywords))
