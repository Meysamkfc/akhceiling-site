# -*- coding: utf-8 -*-
from b_core import *

SYS_IMG = {'drywall': 'show/p04.jpg', 'grid-ceiling': 'projects/p01.jpg', 'profiles': 'photos/real-factory.jpg', 'accessories': 'photos/real-install.jpg'}
SYS_IMG_ALT = {'drywall': 'سقف گچی دکوراتیو در پروژه هتل آزادی', 'grid-ceiling': 'سقف شبکه‌ای در دانشگاه شهرری', 'profiles': 'پروفیل‌های گالوانیزه تولیدشده در کارخانه', 'accessories': 'نصب زیرسازی سقف کاذب'}
SYS_IMG_ALT_EN = {'drywall': 'Decorative drywall ceiling at the Hotel Azadi project', 'grid-ceiling': 'Grid ceiling at Shahre Rey University', 'profiles': 'Galvanized profiles manufactured at our factory', 'accessories': 'Installing a false-ceiling frame'}
ALLP = PRODUCTS + [dict(slug='profiles', title=PROFILES['title'], short=PROFILES['short'], tags=['F47', 'UH36', 'L25'], diagram='drywall'),
                    dict(slug='accessories', title=ACCESSORIES['title'], short=ACCESSORIES['short'], tags=['SSB', 'HT90', 'پیچ و میخ'])]

def product_ld(p, url, d):
    props = []
    if p['slug'] in ('drywall', 'profiles'):
        props = [("طول استاندارد", "۴ متر"), ("ضخامت ورق", "۰٫۵ و ۰٫۶ میلی‌متر"), ("جنس", "فولاد گالوانیزه")]
    elif p['slug'] == 'grid-ceiling':
        props = [("ابعاد تایل", "۶۰×۶۰ سانتی‌متر"), ("طول سپری مادر", "۳٫۶ متر"), ("آویز", "فنر دوبل استیل")]
    return {"@type": "Product", "@id": url + '#product', "name": p['title'], "description": d, "image": [SITE + rurl(SYS_IMG[p['slug']], 960)], "url": url,
            "brand": {"@type": "Brand", "name": "A.K.H"}, "manufacturer": {"@id": ORG_ID}, "category": "مصالح ساختمانی / سقف کاذب و درای‌وال", "countryOfOrigin": {"@type": "Country", "name": "Iran"},
            "additionalProperty": [{"@type": "PropertyValue", "name": a, "value": b} for a, b in props]}

# ============================================================ HOME
def build_home():
    img_p = 'projects/p02.jpg'
    base, sw, sh = variants(img_p)
    variants('projects/p02-flat.jpg')  # perspective-corrected crop, used as the 3D hero's centerpiece texture
    finder = ('<form class="finder" id="finder" novalidate aria-label="پیشنهاد سریع سقف"><div><label for="fr">کاربری فضا</label><select id="fr"><option value="office">اداری / تجاری</option><option value="home">مسکونی</option>'
              '<option value="school">آموزشی / دانشگاهی</option><option value="hospital">درمانی</option><option value="commercial">لابی / هتل / رستوران</option><option value="industrial">صنعتی / سوله</option></select></div>'
              '<div><label for="fa">متراژ (متر مربع)</label><input id="fa" inputmode="numeric" placeholder="مثلاً ۸۰" autocomplete="off"></div><button class="btn" type="submit">پیشنهاد هوشمند</button></form>')
    hero = ('<section class="hero" id="hero" aria-label="معرفی"><canvas id="hero3d" aria-hidden="true"></canvas><div class="wrap in">'
            '<h1><span style="display:block;font-size:.4em;font-weight:800;margin-bottom:6px;color:#d6d8f0">%s</span>قدمت، <em class="o">%s</em></h1><p class="lead">%s تولید پروفیل درای‌وال (F47، UH36، L25) و سقف شبکه‌ای ۶۰×۶۰؛ مستقیم از کارخانه کهریزک تا پروژه شما.</p>'
            '<div class="row"><a class="btn" href="/quote/">درخواست قیمت</a><a class="btn line" href="/products/">مشاهده محصولات</a></div>%s</div><span class="scrollcue" aria-hidden="true">اسکرول کنید</span></section>'
            % (esc(NAME_FULL), flip_text('نماد کیفیت', loop=False), FOUNDED_NOTE + ' تجربه.', finder))
    tick = '<div class="ticker" aria-hidden="true"><div>' + ('<span>پروفیل F47</span><span>پروفیل UH36</span><span>نبشی L25</span><span>سقف شبکه‌ای ۶۰×۶۰</span><span>درای‌وال</span><span>تایل آکوستیک</span><span>طول سفارشی</span>' * 4) + '</div></div>'
    pn = ''
    for i, p in enumerate(ALLP):
        pn += ('<a class="pn" href="/products/%s/">%s<span class="idx">0%d</span><div class="t"><small>%s</small><h3>%s</h3><p>%s</p></div></a>' %
               (p['slug'], rimg(SYS_IMG[p['slug']], SYS_IMG_ALT[p['slug']], '(max-width:760px) 100vw, 40vw'), i + 1, ' · '.join(p['tags'][:3]), esc(p['title']), esc(p['short'])))
    s1 = ('<section class="sec"><div class="wrap">%s<div class="head"><h2>دو سیستم سقف، <em class="o">یک تولیدکننده</em></h2><p class="lead">از سقف یکپارچه گچی تا سقف شبکه‌ای قابل‌برداشتن؛ همه با تولید مستقیم و مشخصات فنی شفاف.</p></div>'
          '<div class="panels rv">%s</div></div></section>' % (kicker('01', 'محصولات'), pn))
    nums = [('۲۲۰', '+', 'تن ظرفیت تولید در ماه'), ('۱۱', '', 'خط تولید و پرس'), ('۴۰', '+', 'سال تجربه در صنعت ساختمان'), ('۷۳٬۰۰۰', '', 'متر مربع؛ بزرگ‌ترین پروژه')]
    nb = ''.join('<div class="rv"><b>%s<em>%s</em></b><span>%s</span></div>' % (n, u, t) for n, u, t in nums)
    s2 = '<section class="sec sm paper2"><div class="wrap"><div class="nums">%s</div><p class="note">آمار از رزومه رسمی شرکت</p></div></section>' % nb
    mini = ('<form id="mini" class="form" novalidate aria-label="برآورد سریع"><div class="two"><div><label for="ms">نوع سقف</label><select id="ms"><option value="drywall">سقف گچی درای‌وال</option><option value="grid">سقف شبکه‌ای ۶۰×۶۰</option></select></div>'
            '<div><label for="ma">متراژ (متر مربع)</label><input id="ma" inputmode="numeric" placeholder="مثلاً ۱۲۰" autocomplete="off"></div></div><div><button class="btn" type="submit">محاسبه</button></div><div id="mout" aria-live="polite"></div></form>')
    s3 = ('<section class="sec night"><div class="wrap">%s<div class="split"><div><h2>برآورد متریال <em class="o">در ۱۰ ثانیه</em></h2><p class="lead">متراژ را بدهید؛ تعداد تقریبی شاخه F47، نبشی، کلیپس و صفحه گچی با ابعاد کاتالوگ خودمان محاسبه می‌شود.</p><div class="x1">%s</div></div>'
          '<div class="card pad ink"><h3>دستیار هوشمند</h3><p class="lead x2">کاربری فضا را بگویید تا یک نمونه اجراشده ببینید، یا هر سؤال فنی را بپرسید؛ پاسخ از مستندات خود شرکت می‌آید و برای قیمت کارشناس تماس می‌گیرد.</p>'
          '<ul class="checks x3"><li>«۸۰ متر دفتر اداری» ← نمونه سقف</li><li>«وزن بندیل F47 چقدر است؟» ← پاسخ فنی</li><li>«۱۲۰ متر درای‌وال» ← برآورد متریال</li></ul><a class="btn x4" href="/assistant/">شروع گفت‌وگو</a></div></div></div></section>'
          % (kicker('02', 'ابزارهای هوشمند'), mini))
    vid = ''.join('<figure><video muted loop playsinline preload="none" poster="/assets/video/%s.jpg" data-src="/assets/video/%s.mp4" aria-label="%s"></video><figcaption>%s</figcaption></figure>' % (k, k, a, a) for k, a in [('roll', 'خط رول‌فرمینگ پروفیل'), ('cut', 'برش و پرداخت'), ('pack', 'بسته‌بندی و آماده‌سازی ارسال')])
    s4 = ('<section class="sec" id="factory"><div class="wrap">%s<div class="head"><h2>تولید مستقیم در <em class="o">کارخانه</em></h2><p class="lead">از نوار فولادی گالوانیزه تا پروفیل آماده ارسال؛ مراحل تولید را از نزدیک ببینید.</p></div><div class="fv">%s</div></div></section>' % (kicker('03', 'تولید'), vid))
    rows = ''.join('<a href="/projects/"><span class="n">0%d</span><h3>%s</h3><span>%s</span>%s</a>' % (i + 1, esc(t), esc(s), rimg('projects/' + f, t, '130px', '', w=130, h=84)) for i, (f, t, s) in enumerate(PROJECTS[:6]))
    s5 = ('<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>پروژه‌هایی که با <em class="o">متریال ما</em> اجرا شده‌اند</h2><a class="btn line" href="/projects/">همه پروژه‌ها</a></div><div class="plist rv">%s</div></div></section>' % (kicker('04', 'پروژه‌ها'), rows))
    def step_li(i, t, d):
        if i == 0:
            return ('<li class="rv d0"><h3><a class="link" href="/quote/">%s</a></h3><p>%s</p><a class="num" href="tel:+98%s">یا تماس مستقیم با کارشناس: %s</a></li>'
                    % (t, d, PHONE.replace('-', '').lstrip('0'), PHONE_FA))
        return ('<li class="rv d%d"><button type="button" class="step-click"><h3>%s</h3><p>%s</p></button><span class="step-msg">لطفاً گام ۱ را پر کنید</span></li>'
                % (i % 4, t, d))
    steps = ''.join(step_li(i, t, d) for i, (t, d) in enumerate([('درخواست و مشاوره', 'نوع پروژه و متراژ را بگویید؛ مشاور فنی سیستم مناسب را پیشنهاد می‌دهد.'), ('برآورد و پیش‌فاکتور', 'مقدار متریال برآورد و پیش‌فاکتور برای شما ارسال می‌شود.'), ('تولید در کارخانه', 'پروفیل‌ها در ضخامت و طول مورد نیاز تولید و بسته‌بندی می‌شوند.'), ('ارسال به پروژه', 'متریال به سراسر کشور ارسال می‌شود و مشاوره فنی هنگام اجرا ادامه دارد.')]))
    s6 = '<section class="sec"><div class="wrap">%s<div class="head"><h2>از <em class="o">درخواست</em> تا تحویل در چهار گام</h2></div><ol class="steps">%s</ol></div></section>' % (kicker('05', 'روند سفارش'), steps)
    s7 = ('<section class="sec night"><div class="wrap"><div class="split"><div>%s<h2>کاتالوگ فنی را <em class="o">دانلود</em> کنید</h2><p class="lead">جدول مشخصات پروفیل‌ها، پیچ‌ها، اتصالات و سیستم‌های سقف در یک فایل PDF.</p>'
          '<div class="row x5"><a class="btn" href="/assets/catalog/akh-catalog.pdf" download>دانلود کاتالوگ (PDF)</a><a class="btn line" href="/catalogs/">مشاهده صفحه‌ها</a></div></div>'
          '<div class="stack">%s%s</div></div></div></section>' % (kicker('06', 'کاتالوگ'), rimg('catalog/f47.jpg', 'صفحه کاتالوگ پروفیل F47', '30vw'), rimg('catalog/grid-60x60.jpg', 'صفحه کاتالوگ سقف شبکه‌ای ۶۰×۶۰', '30vw')))
    trust_cards = ''.join('<div class="card pad">%s<b class="x13">%s</b><p class="lead x4">کارفرما: %s</p><p class="note">متراژ اجرا: %s متر مربع</p></div>' % (rimg('cards/c%d.jpg' % n, esc(t), '(max-width:760px) 50vw, 25vw'), esc(t), esc(emp), ar) for n, t, emp, ar in BIG_PROJECTS[:6])
    s8 = ('<section class="sec"><div class="wrap">%s<div class="head"><h2>مشتریانی که به ما <em class="o">اعتماد کرده‌اند</em></h2><p class="lead">فهرستی از پروژه‌های واقعی اجراشده، طبق رزومه رسمی شرکت؛ نه نظرات ساختگی.</p></div>'
          '<div class="grid g3">%s</div></div></section>' % (kicker('07', 'مشتریان'), trust_cards))
    cl = '<section class="sec sm paper2"><div class="wrap"><div class="logos">%s</div></div></section>' % ''.join('<img src="/assets/clients/%s" alt="%s" width="170" height="60" loading="lazy">' % (f, esc(a)) for f, a in CLIENTS)
    body = hero + tick + s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + cl + cta()
    sw_cap = '%s/assets/r/%s-960.webp' % (SITE, base)
    page('/', 'صنعت سقف البرز خاورمیانه | تولیدکننده پروفیل درای‌وال F47 و سقف کاذب', 'تولید مستقیم پروفیل درای‌وال F47، UH36 و L25، سقف کاذب شبکه‌ای ۶۰×۶۰. کارخانه کهریزک، دفتر تهران، ارسال به سراسر کشور. برآورد متریال و دستیار هوشمند.',
         body, home=True, scripts=('home.js',), priority='1.0', freq='weekly', kind='WebPage', images=[SITE + rurl(img_p, 960)])
    add_doc('صفحه اصلی', 'صنعت سقف البرز خاورمیانه تولیدکننده پروفیل درای‌وال و سقف کاذب', '/', 'صفحه', 'خانه معرفی')

# ============================================================ HOME (English)
# English names for PROJECTS, positionally paired so the photo/order stays identical between languages.
EN_PROJECT_NAMES = ['Hotel Azadi', 'Shahre Rey University', 'Shahid Rajaee University', 'Akhavan Sink factory', 'Massi Tuna Fish complex', 'Velenjak commercial project',
                     'Multi-layer circular ceiling', 'Office corridor', 'Boxed ceiling with recessed lighting', 'Retail store ceiling', 'Office space', 'Framework before tile installation', 'Retail corridor', 'Industrial kitchen']
EN_PROJECT_SYS = ['Decorative drywall ceiling', 'Grid ceiling', 'Grid ceiling', 'Grid ceiling', 'Grid and drywall ceiling', 'Acoustic grid ceiling', 'Decorative drywall ceiling', 'Grid ceiling',
                   'Decorative drywall ceiling', 'Decorative drywall ceiling', 'Grid ceiling', 'Grid ceiling', 'Linear aluminum ceiling', 'Linear aluminum ceiling']
EN_TAGS = {'accessories': ['SSB', 'HT90', 'Screws & nails'], 'grid-ceiling': ['Gypsum tile', 'Aluminum', 'Mineral acoustic']}
EN_CLIENTS_ALT = ['Iran Khodro', 'Chitoz', 'Customer', 'KCC Kison', 'Akhavan', 'Kerman Motor']

def build_home_en():
    img_p = 'projects/p02.jpg'
    base, sw, sh = variants(img_p)
    hero = ('<section class="hero" id="hero" aria-label="Introduction"><canvas id="hero3d" aria-hidden="true"></canvas><div class="wrap in">'
            '<h1><span style="display:block;font-size:.4em;font-weight:800;margin-bottom:6px;color:#d6d8f0">%s</span>Heritage, a mark of <em class="o">quality</em></h1>'
            '<p class="lead">Direct manufacturing of drywall profiles (F47, UH36, L25) and 60x60 grid suspended ceilings; straight from our Kahrizak factory to your project. Over 40 years of experience.</p>'
            '<div class="row"><a class="btn" href="/en/quote/">Request a quote</a><a class="btn line" href="/en/products/">View products</a></div></div><span class="scrollcue" aria-hidden="true">Scroll</span></section>'
            % esc(EN_NAME))
    tick = '<div class="ticker" aria-hidden="true"><div>' + ('<span>F47 profile</span><span>UH36 profile</span><span>L25 angle</span><span>60x60 grid ceiling</span><span>Drywall</span><span>Acoustic tile</span><span>Custom length</span>' * 4) + '</div></div>'
    pn = ''
    for i, p in enumerate(ALLP):
        pn += ('<a class="pn" href="/en/products/%s/">%s<span class="idx">0%d</span><div class="t"><small>%s</small><h3>%s</h3><p>%s</p></div></a>' %
               (p['slug'], rimg(SYS_IMG[p['slug']], SYS_IMG_ALT_EN[p['slug']], '(max-width:760px) 100vw, 40vw'), i + 1, ' &middot; '.join(EN_TAGS.get(p['slug'], p['tags'])[:3]), EN_PRODUCT_NAME[p['slug']], EN_PRODUCT_SHORT[p['slug']]))
    s1 = ('<section class="sec"><div class="wrap">%s<div class="head"><h2>Two ceiling systems, <em class="o">one manufacturer</em></h2><p class="lead">From seamless drywall ceilings to removable grid ceilings; all directly manufactured with transparent technical specifications.</p>'
          '<div class="panels rv">%s</div></div></section>' % (kicker('01', 'Products'), pn))
    nums = [('220', '+', 'tonnes of monthly production capacity'), ('11', '', 'production and press lines'), ('40', '+', 'years of experience in construction'), ('73,000', '', 'square metres; our largest project')]
    nb = ''.join('<div class="rv"><b>%s<em>%s</em></b><span>%s</span></div>' % (n, u, t) for n, u, t in nums)
    s2 = '<section class="sec sm paper2"><div class="wrap"><div class="nums">%s</div><p class="note">Figures from the company&rsquo;s official profile</p></div></section>' % nb
    vid = ''.join('<figure><video muted loop playsinline preload="none" poster="/assets/video/%s.jpg" data-src="/assets/video/%s.mp4" aria-label="%s"></video><figcaption>%s</figcaption></figure>' % (k, k, a, a)
                   for k, a in [('roll', 'Profile roll-forming line'), ('cut', 'Cutting and finishing'), ('pack', 'Packing and shipment preparation')])
    s4 = ('<section class="sec" id="factory"><div class="wrap">%s<div class="head"><h2>Manufactured directly at our <em class="o">Kahrizak factory</em></h2><p class="lead">From galvanized steel coil to a profile ready for shipment; see the production process up close.</p></div><div class="fv">%s</div></div></section>'
          % (kicker('02', 'Production'), vid))
    rows = ''.join('<a href="/en/projects/"><span class="n">0%d</span><h3>%s</h3><span>%s</span>%s</a>' % (i + 1, esc(EN_PROJECT_NAMES[i]), esc(EN_PROJECT_SYS[i]), rimg('projects/' + f, EN_PROJECT_NAMES[i], '130px', '', w=130, h=84)) for i, (f, t, s) in enumerate(PROJECTS[:6]))
    s5 = ('<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>Projects built with <em class="o">our materials</em></h2><a class="btn line" href="/en/projects/">All projects</a></div><div class="plist rv">%s</div></div></section>'
          % (kicker('03', 'Projects'), rows))
    def step_li_en(i, t, d):
        if i == 0:
            return ('<li class="rv d0"><h3><a class="link" href="/en/quote/">%s</a></h3><p>%s</p><a class="num" href="tel:+98%s">Or call our team directly: %s</a></li>'
                    % (t, d, PHONE.replace('-', '').lstrip('0'), PHONE))
        return ('<li class="rv d%d"><button type="button" class="step-click"><h3>%s</h3><p>%s</p></button><span class="step-msg">Please fill in step 1 first</span></li>' % (i % 4, t, d))
    steps = ''.join(step_li_en(i, t, d) for i, (t, d) in enumerate([
        ('Request &amp; consultation', 'Tell us the project type and area; our technical advisor suggests the right system.'),
        ('Estimate &amp; proforma invoice', 'The required material is estimated and a proforma invoice is sent to you.'),
        ('Manufactured at the factory', 'Profiles are produced and packed in the thickness and length you need.'),
        ('Shipped to your project', 'Materials are shipped nationwide, with technical support continuing during installation.')]))
    s6 = '<section class="sec"><div class="wrap">%s<div class="head"><h2>From <em class="o">request</em> to delivery in four steps</h2></div><ol class="steps">%s</ol></div></section>' % (kicker('04', 'Order process'), steps)
    s7 = ('<section class="sec night"><div class="wrap"><div class="split"><div>%s<h2>Download our <em class="o">technical catalog</em></h2><p class="lead">A PDF with the full spec table for profiles, screws, connectors and ceiling systems (in Persian).</p>'
          '<div class="row x5"><a class="btn" href="/assets/catalog/akh-catalog.pdf" download>Download catalog (PDF)</a></div></div>'
          '<div class="stack">%s%s</div></div></div></section>' % (kicker('05', 'Catalog'), rimg('catalog/f47.jpg', 'F47 profile catalog page', '30vw'), rimg('catalog/grid-60x60.jpg', '60x60 grid ceiling catalog page', '30vw')))
    cl = '<section class="sec sm paper2"><div class="wrap"><div class="logos">%s</div></div></section>' % ''.join('<img src="/assets/clients/%s" alt="%s" width="170" height="60" loading="lazy">' % (f, esc(EN_CLIENTS_ALT[i])) for i, (f, a) in enumerate(CLIENTS))
    body = hero + tick + s1 + s2 + s4 + s5 + s6 + s7 + cl + cta('Ready to start?', 'Sign up today and submit your first request.', lang='en')
    page('/en/', 'AKH Ceiling Systems | Drywall Profile & Suspended Ceiling Manufacturer', 'Direct manufacturing of F47, UH36 and L25 drywall profiles and 60x60 grid suspended ceilings. Kahrizak factory, Tehran office, nationwide shipping.',
         body, home=True, scripts=('home.js',), priority='0.9', freq='weekly', kind='WebPage', images=[SITE + rurl(img_p, 960)], lang='en')
    add_doc('Homepage (EN)', 'AKH Ceiling Systems drywall profile and suspended ceiling manufacturer', '/en/', 'page', 'home english')

# ============================================================ PRODUCTS
def build_products():
    cards = ''
    for p in ALLP:
        cards += ('<a class="card hv pc rv" href="/products/%s/">%s<div class="b"><h3>%s</h3><p>%s</p><div class="tags">%s</div></div></a>' %
                  (p['slug'], rimg(SYS_IMG[p['slug']], SYS_IMG_ALT[p['slug']], '(max-width:760px) 100vw, 25vw'), esc(p['title']), esc(p['short']), ''.join('<span class="tag">%s</span>' % t for t in p['tags'])))
    body = (phero('محصولات', 'دو سیستم سقف و دیوار کاذب و پروفیل‌های درای‌وال؛ همه با تولید مستقیم و مشخصات فنی شفاف.', [('/', 'خانه'), (None, 'محصولات')],
                  '<div class="row"><a class="btn" href="/estimate/">برآورد متریال</a><a class="btn line" href="/quote/">درخواست قیمت</a></div>') +
            '<section class="sec"><div class="wrap"><h2 class="sr">محصولات ما</h2><div class="grid g4">%s</div></div></section>' % cards + cta())
    items = [{"@type": "ListItem", "position": i + 1, "url": SITE + '/products/%s/' % p['slug'], "name": p['title']} for i, p in enumerate(ALLP)]
    page('/products/', 'محصولات | پروفیل درای‌وال و سقف شبکه‌ای', 'محصولات صنعت سقف البرز خاورمیانه: سیستم درای‌وال، سقف شبکه‌ای ۶۰×۶۰ و پروفیل‌های F47، UH36 و L25 با مشخصات فنی کامل.', body,
         extra_ld=[{"@type": "ItemList", "@id": SITE + '/products/#list', "itemListElement": items}], crumbs=[('/', 'خانه'), ('/products/', 'محصولات')], priority='0.9', kind='CollectionPage', images=[SITE + rurl(SYS_IMG[p['slug']]) for p in ALLP])
    add_doc('محصولات', 'سیستم درای‌وال، سقف شبکه‌ای ۶۰×۶۰، پروفیل F47 UH36 L25', '/products/', 'صفحه', 'محصول')

def profiles_table():
    rows = [[a, b, c, d, e, f] for a, b, c, d, e, f in PROFILE_TABLE]
    return table_html(rows, ['پروفیل', 'ضخامت ورق (mm)', 'طول (m)', 'تعداد در بسته', 'تعداد در بندیل', 'وزن تقریبی بندیل (kg)']) + '<p class="note">وزن‌ها به ترتیب برای ضخامت ۰٫۵ و ۰٫۶ میلی‌متر (طبق جدول رسمی کاتالوگ شرکت).</p>'

HOWTO = {
    'drywall': ('مراحل اجرای سقف گچی درای‌وال (مرور کلی)', ['تراز سقف را علامت بزنید و نبشی L25 را دور تا دور دیوار نصب کنید.', 'آویزها را به سقف اصلی وصل کنید و پروفیل‌های باربر را روی آن‌ها بگذارید.', 'پروفیل‌های F47 پانل‌خور را با کلیپس به باربر متصل کنید.', 'تأسیسات و عایق (در صورت نیاز) را قبل از بستن سقف اجرا کنید.', 'صفحات گچی را با پیچ پانل روی زیرسازی نصب کنید.', 'درزها را با نوار و بتونه ببندید، سپس رنگ یا پوشش نهایی را اجرا کنید.']),
    'grid-ceiling': ('مراحل اجرای سقف شبکه‌ای (مرور کلی)', ['تراز سقف را مشخص و نبشی دیواری را دور تا دور نصب کنید.', 'آویزهای فنر دوبل را در فاصله‌های مشخص به سقف اصلی وصل کنید.', 'سپری‌های مادر را روی آویزها قرار دهید و تراز کنید.', 'سپری‌های ۱۲۰ و ۶۰ را برای ساختن شبکه ۶۰×۶۰ جا بزنید.', 'تایل‌ها را داخل شبکه بگذارید.']),
}

def build_product(p):
    slug = p['slug']; url = SITE + '/products/%s/' % slug
    d = P[slug]; crumbs = [('/', 'خانه'), ('/products/', 'محصولات'), ('/products/%s/' % slug, p['title'])]
    ab = ''.join('<p class="lead x7">%s</p>' % t for t in d['about'])
    lists = ''
    for title, key in (('کاربردها', 'uses'), ('مزیت‌ها', 'benefits'), ('اجزا و متعلقات', 'parts')):
        if key in d:
            lists += '<div class="card pad rv"><h3>%s</h3><ul class="checks x8">%s</ul></div>' % (title, ''.join('<li>%s</li>' % x for x in d[key]))
    BOARD_IMG = {'معمولی': 'mat/board-normal.jpg', 'مقاوم رطوبت': 'mat/board-moisture.jpg', 'مقاوم حریق': 'mat/board-fire.jpg'}
    TILE_FAMILY_IMG = {'تایل گچی': 'mat/tile-gypsum.jpg', 'تایل آلومینیومی': 'mat/tile-aluminum.jpg', 'تایل مینرال آکوستیک': 'mat/tile-acoustic.jpg'}
    GRID_TILE_IMG = {'تایل گچی روکش PVC رنگی': 'mat/tile-pvc-color.jpg', 'تایل گچی روکش PVC طرح حصیری': 'mat/tile-wicker.jpg', 'تایل گچی روکش PVC ساده': 'mat/tile-pvc-plain.jpg',
                      'تایل سوراخ‌دار منظم و نامنظم': 'mat/tile-perforated.jpg', 'تایل پانچ مربعی': 'mat/tile-punch-square.jpg', 'تایل مینرال آکوستیک': 'mat/tile-acoustic.jpg',
                      'تایل آلومینیومی': 'mat/tile-aluminum.jpg', 'تایل آلومینیومی تمام پانچ و وسط پانچ': 'mat/tile-aluminum.jpg'}
    TBAR_IMG = {'سپری نمایان': 'mat/tbar-exposed.jpg', 'سپری پنهان': 'mat/tbar-concealed.jpg', 'سپری سه‌رنگ': 'mat/tbar-tricolor.jpg'}
    extra = ''
    if slug == 'drywall':
        boards = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(BOARD_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in d['boards'])
        extra = ('<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>مشخصات پروفیل‌های <em class="o">گالوانیزه</em></h2></div>%s<p class="x9"><a class="link" href="/products/profiles/">اتصالات، پیچ‌ها و توضیح هر پروفیل</a></p></div></section>'
                 '<section class="sec"><div class="wrap">%s<div class="head"><h2>سه نوع <em class="o">صفحه گچی</em></h2></div><div class="grid g3">%s</div></div></section>' % (kicker('02', 'جدول فنی'), profiles_table(), kicker('03', 'صفحات گچی'), boards))
    elif slug == 'grid-ceiling':
        tiles = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(TILE_FAMILY_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in d['tiles'])
        gt = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(GRID_TILE_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in GRID_TILES)
        gb = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(TBAR_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in GRID_TBARS)
        extra = ('<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>سه خانواده <em class="o">تایل</em></h2></div><div class="grid g3">%s</div></div></section>'
                 '<section class="sec"><div class="wrap">%s<div class="head"><h2>مدل‌های دقیق <em class="o">تایل</em></h2><p class="lead">مشخصات فنی هر مدل؛ انتخاب نهایی با توجه به فضا، بودجه و نیاز رطوبت/آکوستیک با کارشناس فنی.</p></div><div class="grid g3">%s</div></div></section>'
                 '<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>انواع <em class="o">سپری</em></h2></div><div class="grid g3">%s</div></div></section>'
                 % (kicker('02', 'تایل‌ها'), tiles, kicker('03', 'مدل‌های تایل'), gt, kicker('04', 'سپری'), gb))
    elif slug == 'profiles':
        PROFILE_IMG = {'F47': 'parts/profile-f47.jpg', 'UH36': 'parts/profile-uh36.jpg', 'L25': 'parts/profile-l25.jpg'}
        roles = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(PROFILE_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in PROFILE_ROLES)
        conn = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(CONNECTORS_IMG[i], a, '(max-width:760px) 50vw, 25vw'), a, b) for i, (a, b) in enumerate(CONNECTORS))
        sc = table_html([list(r) for r in SCREW_TABLE], ['نوع پیچ', 'سایز', 'تعداد در هر کارتن', 'وزن (kg)'])
        extra = ('<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>نقش هر <em class="o">پروفیل</em></h2></div><div class="grid g3">%s</div><div class="x11">%s</div></div></section>'
                 '<section class="sec"><div class="wrap">%s<div class="head"><h2>بست‌ها و قطعات <em class="o">اتصال</em></h2></div><div class="grid g3">%s</div></div></section>'
                 '<section class="sec paper2"><div class="wrap">%s<div class="split"><div><div class="head"><h2>پیچ و <em class="o">میخ و چاشنی</em></h2><p class="lead">پیچ پانل (TN سرتیز و TB سرمته‌دار) صفحه گچی را به زیرسازی وصل می‌کند؛ پیچ سازه (LN و LB) پروفیل‌ها را به هم متصل می‌کند.</p></div>%s</div><div class="fig rv">%s</div></div></div></section>'
                 % (kicker('02', 'پروفیل‌ها'), roles, profiles_table(), kicker('03', 'اتصالات'), conn, kicker('04', 'پیچ'), sc, rimg('mat/screws.jpg', 'انواع پیچ پانل و پیچ سازه درای‌وال', '(max-width:1100px) 100vw, 45vw')))
    elif slug == 'accessories':
        sc2 = table_html([list(r) for r in SCREW_TABLE], ['نوع پیچ', 'سایز', 'تعداد در هر کارتن', 'وزن (kg)'])
        NAIL_IMG = {'میخ و چاشنی بتن': 'mat/nail-concrete.jpg', 'میخ و چاشنی آهن': 'mat/nail-iron.jpg'}
        nails = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(NAIL_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in NAIL_TYPES)
        conn2 = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(CONNECTORS_IMG[i], a, '(max-width:760px) 50vw, 25vw'), a, b) for i, (a, b) in enumerate(CONNECTORS))
        extra = ('<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>پیچ <em class="o">سازه و پانل</em></h2><p class="lead">%s</p></div>%s</div></section>'
                 '<section class="sec"><div class="wrap">%s<div class="head"><h2>میخ و <em class="o">چاشنی</em></h2></div><div class="grid g3">%s</div></div></section>'
                 '<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>نوار <em class="o">درزگیر</em></h2><p class="lead">%s</p></div></div></section>'
                 '<section class="sec"><div class="wrap">%s<div class="head"><h2>اتصالات و <em class="o">آویز</em></h2></div><div class="grid g3">%s</div></div></section>'
                 % (kicker('02', 'پیچ'), SCREW_BRAND_NOTE, sc2, kicker('03', 'میخ و چاشنی'), nails, kicker('04', 'درزگیر'), JOINT_TAPE_DESC, kicker('05', 'اتصالات'), conn2))
    howto = ''
    ld_extra = [product_ld(p, url, d['desc'])]
    if slug in HOWTO:
        ht, steps = HOWTO[slug]
        howto_num = {'profiles': '05', 'grid-ceiling': '05'}.get(slug, '04')
        howto = ('<section class="sec"><div class="wrap"><div class="split"><div>%s<h2>%s</h2><p class="note">مرور کلی برای آشنایی؛ اجرای واقعی باید طبق نقشه و دستورالعمل فنی انجام شود.</p></div><ol class="steps2 x12">%s</ol></div></div></section>' %
                 (kicker(howto_num, 'اجرا'), ht, ''.join('<li>%s</li>' % s for s in steps)))
        ld_extra.append({"@type": "HowTo", "@id": url + '#howto', "name": ht, "step": [{"@type": "HowToStep", "position": i + 1, "text": s} for i, s in enumerate(steps)]})
    faq = d.get('faq') or []
    faq_sec = ''
    if faq:
        faq_sec = '<section class="sec"><div class="wrap"><div class="split">%s%s</div></div></section>' % ('<div>' + kicker('FAQ', 'پرسش‌ها') + '<h2>پرسش‌های متداول</h2></div>', faq_html(faq))
        ld_extra.append(faq_node(faq, url))
    gallery = ''
    REAL_GALLERY = {'drywall': [('show/d1.jpg', 'سقف گچی باکسی با نورپردازی مخفی — نمونه اجرای واقعی')],
                     'grid-ceiling': [('show/g3.jpg', 'سقف شبکه‌ای دایره‌ای با تایل مرکزی و نور مخفی'), ('show/p02.jpg', 'سقف شبکه‌ای با تایل پرفوریت در فضای صنعتی'), ('photos/real-ceiling.jpg', 'تیم صنعت سقف البرز خاورمیانه در حال نصب زیرسازی سقف')]}
    rg = REAL_GALLERY.get(slug)
    if rg:
        rg_num, rg_cls = {'drywall': ('05', ' paper2'), 'grid-ceiling': ('06', ' paper2')}[slug]
        gallery += ('<section class="sec%s"><div class="wrap">%s<div class="head"><h2>نمونه <em class="o">اجرای واقعی</em></h2><p class="lead">تصاویر واقعی از سقف‌های اجراشده با این سیستم.</p></div><div class="grid g3">%s</div></div></section>' %
                    (rg_cls, kicker(rg_num, 'نمونه کار'), ''.join('<figure class="card">%s<figcaption class="pad x13">%s</figcaption></figure>' % (rimg(r, t, '(max-width:760px) 100vw, 30vw'), t) for r, t in rg)))
    rel_art = [a for a in ARTICLES if any(k in a['title'] + a['desc'] for k in {'drywall': ['درای‌وال', 'F47', 'پروفیل'], 'grid-ceiling': ['شبکه‌ای'], 'profiles': ['پروفیل', 'پیچ'], 'accessories': ['پیچ', 'میخ']}[slug])][:3]
    rel = '<div class="rel">%s</div>' % ''.join('<a href="/articles/%s/">%s</a>' % (a['slug'], esc(a['title'])) for a in rel_art) if rel_art else ''
    others = '<div class="rel">%s</div>' % ''.join('<a href="/products/%s/">%s</a>' % (q['slug'], esc(q['title'])) for q in ALLP if q['slug'] != slug)
    ABOUT_HEAD = {'drywall': ('چرا', 'درای‌وال؟'), 'grid-ceiling': ('ساختار', 'سقف شبکه‌ای'), 'profiles': ('معرفی', 'پروفیل‌ها و اتصالات'), 'accessories': ('کاربرد', 'این ملزومات')}
    ah1, ah2 = ABOUT_HEAD.get(slug, ('درباره', 'این سیستم'))
    main = ('<section class="sec"><div class="wrap"><div class="split"><div>%s<h2>%s <em class="o">%s</em></h2>%s</div><div class="fig rv">%s</div></div></div></section>' % (kicker('01', 'معرفی'), ah1, ah2, ab, rimg(SYS_IMG[slug], SYS_IMG_ALT[slug], '(max-width:1100px) 100vw, 45vw')))
    diag = ('<section class="sec sm"><div class="wrap"><div class="dgwrap card pad rv">%s</div></div></section>' % diagram(p['diagram'])) if p.get('diagram') else ''
    feats = '<section class="sec sm"><div class="wrap"><div class="grid g3">%s</div></div></section>' % lists
    related = '<section class="sec sm"><div class="wrap"><h2 class="x14">ادامه مطالعه</h2>%s%s</div></section>' % (rel, others)
    body = (phero(d['h1'], d['lead'], crumbs, '<div class="row"><a class="btn" href="/quote/?p=%s">درخواست قیمت</a><a class="btn line" href="/estimate/">برآورد متریال</a></div>' % slug.replace('-ceiling', '')) + main + diag + feats + extra + howto + gallery + faq_sec + related + cta())
    page('/products/%s/' % slug, '%s | %s' % (p['title'], NAME), d['desc'], body, extra_ld=ld_extra, crumbs=crumbs, priority='0.9', images=[SITE + rurl(SYS_IMG[slug])])
    doc_text = d['lead'] + ' ' + ' '.join(d['about'])
    if slug == 'grid-ceiling':
        doc_text += ' مدل‌های تایل: ' + '، '.join(a for a, b in GRID_TILES) + '. انواع سپری: ' + '، '.join(a for a, b in GRID_TBARS) + '.'
    add_doc(p['title'], doc_text, '/products/%s/' % slug, 'محصول', ' '.join(p['tags']))
    for q, a in faq:
        add_doc(q, a, '/products/%s/' % slug, 'پرسش', p['title'])

# ============================================================ PROJECTS
def build_projects():
    rows = ''.join('<a href="/assets/projects/%s" class="gi"><span class="sr">%s</span></a>' % (f, t) for f, t, s in PROJECTS[:0])
    pl = ''.join('<a href="#p%d"><span class="n">0%d</span><h3>%s</h3><span>%s</span>%s</a>' % (i + 1, i + 1, esc(t), esc(s), rimg('projects/' + f, t, '130px', '', w=130, h=84)) for i, (f, t, s) in enumerate(PROJECTS))
    big = ''.join('<a class="gi" href="/assets/cards/c%d-big.jpg" data-cap="%s — کارفرما: %s — متراژ: %s متر مربع">%s<span>%s<small>%s متر مربع</small></span></a>' % (n, esc(t), esc(emp), ar, rimg('cards/c%d.jpg' % n, '%s، کارفرما %s، متراژ %s متر مربع' % (t, emp, ar), '(max-width:760px) 50vw, 20vw', w=560, h=840), esc(t), ar) for n, t, emp, ar in BIG_PROJECTS)
    gal = ''.join('<a class="gi" href="/assets/gallery/g%02d.jpg" data-cap="%s">%s<span>%s</span></a>' % (n, c, rimg('gallery/t%02d.jpg' % n, c + ' — پروژه ماهان پارک', '(max-width:760px) 50vw, 25vw'), c) for n, c in enumerate(GALLERY_CAPS, 1))
    gal4 = ''.join('<a class="gi" href="/assets/r/projects-%s-1600.webp" data-cap="%s — %s">%s<span>%s<small>%s</small></span></a>' % (f.rsplit('.', 1)[0], esc(t), esc(s), rimg('projects/' + f, '%s — %s' % (t, s), '(max-width:760px) 50vw, 25vw'), esc(t), esc(s)) for f, t, s in PROJECTS)
    body = (phero('پروژه‌ها', 'نمونه‌ای از پروژه‌هایی که با متریال و تجربه صنعت سقف البرز خاورمیانه اجرا شده‌اند.', [('/', 'خانه'), (None, 'پروژه‌ها')]) +
            '<section class="sec"><div class="wrap">%s<div class="head"><h2>سقف‌های <em class="o">اجراشده</em></h2></div><div class="gal" data-lb>%s</div></div></section>' % (kicker('01', 'گالری'), gal4) +
            '<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>پروژه‌های بزرگ و <em class="o">متراژ اجرا</em></h2><p class="lead">فهرست پروژه‌های شاخص با کارفرما و متراژ، طبق رزومه رسمی شرکت.</p></div><div class="bigp" data-lb>%s</div></div></section>' % (kicker('02', 'پروژه‌های شاخص'), big) +
            '<section class="sec"><div class="wrap">%s<div class="head"><h2>اجرا در پروژه <em class="o">ماهان پارک</em></h2><p class="lead">تصاویر واقعی از تیم اجرایی ما هنگام نصب سقف و دیوار کاذب.</p></div><div class="gal" data-lb>%s</div></div></section>' % (kicker('03', 'کارگاه'), gal) + cta('پروژه شما بعدی است', 'نوع پروژه را بگویید تا بهترین سیستم را پیشنهاد دهیم.'))
    items = [{"@type": "ImageObject", "contentUrl": SITE + rurl('projects/' + f, 1600), "name": t, "caption": '%s — %s' % (t, s), "creator": {"@id": ORG_ID}} for f, t, s in PROJECTS]
    page('/projects/', 'پروژه‌های اجراشده | دانشگاه، هتل، مراکز تجاری و صنعتی', 'پروژه‌های سقف کاذب و درای‌وال با متریال صنعت سقف البرز خاورمیانه: هتل آزادی، دانشگاه شهرری، دانشگاه صنعت نفت، مخابرات، ماهان پارک ۷۳٬۰۰۰ متر مربع و بیشتر.', body,
         extra_ld=[{"@type": "ImageGallery", "@id": SITE + '/projects/#gallery', "name": "پروژه‌های اجراشده", "associatedMedia": items}], crumbs=[('/', 'خانه'), ('/projects/', 'پروژه‌ها')], priority='0.8', kind='CollectionPage', images=[SITE + rurl('projects/' + f, 1600) for f, t, s in PROJECTS])
    add_doc('پروژه‌ها', 'پروژه‌های اجراشده هتل آزادی دانشگاه شهرری شهید رجایی صنعت نفت مخابرات ماهان پارک باران تشریفات', '/projects/', 'صفحه', 'پروژه نمونه کار')

# ============================================================ CATALOGS
def build_catalogs():
    items = ''.join('<a class="card hv pc rv" href="/assets/catalog/%s-big.jpg" target="_blank" rel="noopener">%s<div class="b"><h3>%s</h3><p>%s</p><span class="link">مشاهده صفحه</span></div></a>' % (s, rimg('catalog/%s.jpg' % s, 'صفحه کاتالوگ: ' + t, '(max-width:760px) 100vw, 25vw'), t, d) for s, t, d in CATALOGS)
    body = (phero('کاتالوگ‌ها', 'صفحه‌های کاتالوگ رسمی شرکت؛ هر صفحه را ببینید یا کل کاتالوگ را به‌صورت PDF دانلود کنید.', [('/', 'خانه'), (None, 'کاتالوگ‌ها')], '<div class="row"><a class="btn" href="/assets/catalog/akh-catalog.pdf" download>دانلود کل کاتالوگ (PDF)</a></div>') +
            '<section class="sec"><div class="wrap"><h2 class="sr">صفحه‌های کاتالوگ</h2><div class="grid g3">%s</div></div></section>' % items + cta())
    page('/catalogs/', 'کاتالوگ محصولات | دانلود PDF پروفیل و سقف کاذب', 'کاتالوگ رسمی صنعت سقف البرز خاورمیانه: پروفیل F47، UH36، L25، پیچ و اتصالات، سقف‌های دکوراتیو و سقف شبکه‌ای ۶۰×۶۰. دانلود رایگان PDF.', body,
         crumbs=[('/', 'خانه'), ('/catalogs/', 'کاتالوگ‌ها')], priority='0.7', images=[SITE + rurl('catalog/%s.jpg' % s) for s, t, d in CATALOGS],
         extra_ld=[{"@type": "DataDownload", "name": "کاتالوگ محصولات", "encodingFormat": "application/pdf", "contentUrl": SITE + '/assets/catalog/akh-catalog.pdf', "publisher": {"@id": ORG_ID}}])
    add_doc('کاتالوگ‌ها', 'دانلود کاتالوگ PDF پروفیل F47 UH36 L25 پیچ اتصالات', '/catalogs/', 'صفحه', 'کاتالوگ دانلود')

# ============================================================ ABOUT / CONTACT
def build_about():
    facts_li = ''.join('<li>%s</li>' % f for f in COMPANY_FACTS)
    mach = table_html([list(m) for m in MACHINES], ['دستگاه', 'تعداد', 'ظرفیت روزانه'])
    body = (phero('درباره ما', '%s؛ تولیدکننده متریال سقف و دیوار کاذب و سیستم‌های درای‌وال.' % NAME_FULL, [('/', 'خانه'), (None, 'درباره ما')]) +
            '<section class="sec"><div class="wrap"><div class="split"><div>%s<h2>چهار دهه کار با <em class="o">فولاد، آلومینیوم و گچ</em></h2><p class="lead x7">شرکت صنعت سقف البرز خاورمیانه با بیش از ۴۰ سال تجربه در صنعت ساختمان، تولید متریال‌های سقف کاذب و سیستم‌های درای‌وال را دنبال می‌کند و امروز یکی از تولیدکنندگان باسابقه این حوزه در کشور است.</p>'
            '<p class="lead">کیفیت برای ما یک شعار نیست؛ از انتخاب مواد اولیه تا محصول نهایی در خط تولید کنترل می‌شود و پروفیل‌ها در بسته‌های ۲۰ شاخه‌ای آماده بارگیری می‌شوند.</p></div><div class="fig rv">%s</div></div></div></section>' % (kicker('01', 'داستان ما'), rimg('photos/real-factory.jpg', 'پروفیل‌های تولیدشده در کارخانه', '(max-width:1100px) 100vw, 45vw')) +
            '<section class="sec paper2"><div class="wrap">%s<div class="split"><div><h2>خط‌های تولید و <em class="o">تجهیزات</em></h2><ul class="checks x15">%s</ul></div><div>%s<p class="note">طبق فهرست ماشین‌آلات و تجهیزات شرکت.</p></div></div></div></section>' % (kicker('02', 'توان تولید'), facts_li, mach) +
            '<section class="sec"><div class="wrap"><div class="split rev"><div>%s<h2>بسته‌بندی و <em class="o">ارسال به سراسر کشور</em></h2><p class="lead">مصالح پس از تولید بسته‌بندی و برای ارسال به پروژه آماده می‌شوند؛ تیم ما تا تحویل نهایی در کنار شماست.</p></div><div class="fig rv">%s</div></div></div></section>' % (kicker('03', 'ارسال'), rimg('photos/real-delivery.jpg', 'تحویل مصالح به پروژه توسط تیم صنعت سقف البرز خاورمیانه', '(max-width:1100px) 100vw, 45vw')) +
            '<section class="sec paper2"><div class="wrap"><div class="split"><div>%s<h2>در کنار مشتریان و <em class="o">پیمانکاران</em></h2><p class="lead">ما به‌طور مستمر در نمایشگاه‌های تخصصی ساختمان حضور داریم تا محصولات را از نزدیک معرفی کنیم و نیاز پروژه‌ها را بشنویم.</p></div><div class="fig rv">%s</div></div></div></section>' % (kicker('04', 'نمایشگاه'), rimg('photos/real-expo.jpg', 'غرفه شرکت در نمایشگاه میدکس', '(max-width:1100px) 100vw, 45vw')) + cta())
    page('/about/', 'درباره ما | %s' % NAME_FULL, 'صنعت سقف البرز خاورمیانه با بیش از ۴۰ سال تجربه؛ ظرفیت تولید بیش از ۲۲۰ تن در ماه، ۱۱ خط تولید و پرس، کارخانه کهریزک و دفتر مرکزی تهران.', body,
         crumbs=[('/', 'خانه'), ('/about/', 'درباره ما')], kind='AboutPage', priority='0.7', images=[SITE + rurl('photos/real-factory.jpg')])
    add_doc('درباره ما', ' '.join(COMPANY_FACTS), '/about/', 'صفحه', 'شرکت تاریخچه ظرفیت تولید ماشین‌آلات')

def build_contact():
    maps_q = 'Tehran+Beheshti+Ghanbarzadeh+Havizeh+202'
    maps = 'https://www.google.com/maps/search/?api=1&query=' + maps_q
    maps_embed = 'https://maps.google.com/maps?q=' + maps_q + '&output=embed'
    body = (phero('تماس با ما', 'برای مشاوره فنی، درخواست قیمت یا بازدید کارخانه با ما در ارتباط باشید.', [('/', 'خانه'), (None, 'تماس با ما')]) +
            '<section class="sec"><div class="wrap"><div class="grid g2"><div class="card pad"><h2>دفتر مرکزی</h2><ul class="checks x8"><li>%s</li><li>تلفن: <a class="num" href="tel:+982188507585">%s</a> (۱۰ خط)</li><li>موبایل: <a class="num" href="tel:+989124968761">%s</a></li><li>ایمیل: <a class="num" href="mailto:%s">%s</a></li><li>%s</li><li>%s</li></ul><p class="x16"><a class="link" href="%s" rel="noopener">مسیریابی در نقشه</a></p></div>'
            '<div class="card pad"><h2>کارخانه</h2><ul class="checks x8"><li>%s</li><li>تلفن: <a class="num" href="tel:+982156548804">%s</a></li></ul><p class="row x16"><a class="btn sm" href="https://t.me/%s" rel="noopener">تلگرام</a><a class="btn sm line" href="https://instagram.com/%s" rel="noopener">اینستاگرام</a></p></div></div>'
            '<div class="mapwrap card rv"><iframe src="%s" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="نقشه دفتر مرکزی %s"></iframe></div>'
            '<div class="cta rv x17"><div><h2>درخواست قیمت آنلاین</h2><p>مشخصات پروژه را بنویسید تا کارشناسان با شما تماس بگیرند.</p></div><div class="row"><a class="btn" href="/quote/">ثبت درخواست</a></div></div></div></section>'
            % (ADDR_OFFICE, PHONE_FA, MOBILE_FA, EMAIL, EMAIL, HOURS[0], HOURS[1], maps, ADDR_FACTORY, PHONE_FACTORY_FA, TELEGRAM, INSTAGRAM, maps_embed, esc(NAME_FULL)))
    page('/contact/', 'تماس با ما | %s' % NAME_FULL, 'تماس با صنعت سقف البرز خاورمیانه: تلفن ۰۲۱-۸۸۵۰۷۵۸۵، دفتر مرکزی تهران و کارخانه کهریزک، ساعات کاری و راه‌های ارتباطی.', body,
         crumbs=[('/', 'خانه'), ('/contact/', 'تماس با ما')], kind='ContactPage', priority='0.8')
    add_doc('تماس با ما', 'آدرس دفتر ' + ADDR_OFFICE + ' کارخانه ' + ADDR_FACTORY + ' تلفن ' + PHONE + ' ' + HOURS[0], '/contact/', 'صفحه', 'تماس آدرس تلفن ساعت کاری')

# ============================================================ MEMBERSHIP
def build_membership():
    benefits = [('پنل شخصی سفارش‌ها', 'وضعیت هر سفارش را از ثبت تا ارسال دنبال کنید؛ بدون نیاز به تماس تلفنی.'),
                ('فضای اختصاصی فاکتورها', 'پیش‌فاکتور و فاکتور هر سفارش در پنل شما بارگذاری می‌شود و هر زمان قابل مشاهده و دانلود است.'),
                ('ورود امن با تأیید دومرحله‌ای', 'حساب شما با رمز عبور و در صورت تمایل تأیید دومرحله‌ای (2FA) محافظت می‌شود.'),
                ('دستیار هوشمند', 'برای برآورد متریال و پاسخ به سؤالات فنی، هر زمان با دستیار هوشمند سایت گفت‌وگو کنید.'),
                ('ثبت و پیگیری سریع‌تر', 'با ثبت یک‌بار اطلاعات پروژه، درخواست‌های بعدی را با چند کلیک ارسال کنید.')]
    bl = ''.join('<li><b>%s</b> — %s</li>' % (esc(t), d) for t, d in benefits)
    steps = ''.join('<li>%s</li>' % s for s in ('ثبت‌نام با ایمیل یا شماره موبایل و یک رمز عبور', 'در صورت تمایل، شغل یا سمت خود را هم وارد کنید (اختیاری)', 'تکمیل اطلاعات پروژه', 'مشاهده پیش‌فاکتور و فاکتورها در پنل'))
    body = (phero('عضویت در پنل مشتریان', 'با عضویت رایگان در پنل مشتریان %s، سفارش‌ها و فاکتورهای خود را در یک فضای شخصی و امن مدیریت کنید.' % esc(NAME_FULL),
                  [('/', 'خانه'), (None, 'عضویت')], '<div class="row"><a class="btn" href="/account/register/">ثبت‌نام رایگان</a><a class="btn line" href="/account/login/">ورود به حساب</a></div>') +
            ('<section class="sec"><div class="wrap"><div class="card pad rv">%s<h2>علت <em class="o">عضویت</em></h2>'
             '<ul class="checks x15">%s</ul><h3 class="x4">چگونه شروع کنم؟</h3><ul class="checks x15">%s</ul>'
             '<a class="btn x4" href="/account/register/">همین حالا ثبت‌نام کنید</a></div></div></section>'
             % (kicker('01', 'مزایا'), bl, steps)) +
            cta('آماده‌اید؟', 'همین حالا عضو شوید و اولین درخواست خود را ثبت کنید.'))
    page('/membership/', 'عضویت در پنل مشتریان | %s' % NAME_FULL, 'با عضویت رایگان در پنل مشتریان صنعت سقف البرز خاورمیانه، سفارش‌ها و فاکتورهای خود را مدیریت کنید و با دستیار هوشمند سایت در ارتباط باشید.', body,
         crumbs=[('/', 'خانه'), ('/membership/', 'عضویت')], kind='WebPage', priority='0.6')
    add_doc('عضویت در پنل مشتریان', 'مزایای عضویت فضای شخصی فاکتورها پیگیری سفارش دستیار هوشمند', '/membership/', 'صفحه', 'عضویت ثبت نام ورود فاکتور')

# ============================================================ QUOTE / ESTIMATE / ASSISTANT
def build_quote():
    prods = ''.join('<option value="%s">%s</option>' % (k, v) for k, v in [('', 'انتخاب کنید'), ('grid', 'سقف کاذب شبکه‌ای ۶۰×۶۰'), ('drywall', 'سیستم درای‌وال و سقف گچی'), ('profiles', 'پروفیل و اتصالات درای‌وال'), ('other', 'سایر / نیاز به راهنمایی')])
    blds = ''.join('<option value="%s">%s</option>' % (k, v) for k, v in [('', 'انتخاب کنید'), ('office', 'اداری / تجاری'), ('school', 'آموزشی / دانشگاهی'), ('hospital', 'درمانی / بیمارستانی'), ('hotel', 'هتل / لابی / فرودگاه'), ('home', 'مسکونی'), ('industrial', 'صنعتی / سوله')])
    def fld(i, label, typ='text', req=True, ph='', extra=''):
        return '<div><label for="%s">%s%s</label><input id="%s" name="%s" type="%s"%s placeholder="%s" autocomplete="off" %s><div class="err" id="%s-e" role="alert"></div></div>' % (i, label, ' *' if req else '', i, i, typ, ' required' if req else '', ph, extra, i)
    form = ('<form class="form" id="qf" novalidate aria-label="فرم درخواست قیمت"><div class="two">%s%s</div><div class="two">%s%s</div><div class="two"><div><label for="building">نوع ساختمان</label><select id="building">%s</select></div><div><label for="product">محصول مورد نیاز</label><select id="product">%s</select></div></div>'
            '<div class="two">%s<div></div></div><div><label for="desc">توضیحات</label><textarea id="desc" placeholder="نوع پروژه، زمان اجرا، رنگ و طرح مدنظر…"></textarea></div>'
            '<div class="hp" aria-hidden="true"><label for="website">وب‌سایت (خالی بگذارید)</label><input id="website" name="website" tabindex="-1" autocomplete="off"></div><div><button class="btn" type="submit">ثبت درخواست</button></div></form>'
            '<div class="ok" id="sent" hidden><b>درخواست شما ثبت شد ✅</b><p id="okmsg">شماره پیگیری: <b class="num" id="trk"></b></p><p>کارشناس فروش در ساعات کاری با شما تماس می‌گیرد.</p><div id="manual" hidden><p>ثبت آنلاین ممکن نشد؛ برای ارسال درخواست یکی از راه‌های زیر را بزنید:</p><pre id="preview" class="x18"></pre>'
            '<div class="row"><a class="btn sm" id="wa" href="#" target="_blank" rel="noopener">ارسال در واتساپ</a><a class="btn sm line" id="mail" href="#">ارسال ایمیل</a><button class="btn sm line" type="button" id="copy">کپی متن</button></div></div></div>'
            '<noscript><p class="note">برای ارسال درخواست، جاوااسکریپت را فعال کنید یا با <a href="tel:+982188507585" class="num">%s</a> تماس بگیرید.</p></noscript>'
            % (fld('name', 'نام و نام خانوادگی', ph='مثلاً علی رضایی'), fld('phone', 'شماره تماس', 'tel', ph='۰۹۱۲۳۴۵۶۷۸۹', extra='inputmode=tel dir=ltr'), fld('company', 'نام شرکت', req=False), fld('city', 'شهر پروژه'), blds, prods, fld('area', 'متراژ تقریبی (متر مربع)', 'text', False, 'مثلاً ۵۰۰', 'inputmode=numeric'), PHONE_FA))
    side = ('<div class="card pad"><h2>تماس مستقیم</h2><ul class="checks x8"><li>دفتر مرکزی: <a class="num" href="tel:+982188507585">%s</a></li><li>کارخانه: <a class="num" href="tel:+982156548804">%s</a></li><li>%s</li><li>%s</li></ul></div>'
            '<div class="card pad x19"><h2>بعد از ثبت چه می‌شود؟</h2><ul class="checks x8"><li>کارشناس فروش درخواست را بررسی می‌کند.</li><li>در صورت نیاز نقشه یا تصویر پروژه را از شما می‌گیرد.</li><li>قیمت و پیشنهاد فنی پس از تأیید کارشناس اعلام می‌شود.</li></ul></div>' % (PHONE_FA, PHONE_FACTORY_FA, HOURS[0], HOURS[1]))
    body = (phero('درخواست قیمت', 'مشخصات پروژه را وارد کنید؛ کارشناسان ما برای ارائه پیشنهاد فنی و قیمت با شما تماس می‌گیرند.', [('/', 'خانه'), (None, 'درخواست قیمت')]) +
            '<section class="sec"><div class="wrap"><div class="split x20"><div class="formcard">%s</div><div>%s</div></div></div></section>' % (form, side))
    page('/quote/', 'درخواست قیمت و مشاوره | %s' % NAME, 'درخواست قیمت سقف کاذب و درای‌وال: مشخصات پروژه را بنویسید تا کارشناسان صنعت سقف البرز خاورمیانه با شما تماس بگیرند.', body, crumbs=[('/', 'خانه'), ('/quote/', 'درخواست قیمت')], scripts=('quote.js',), priority='0.8')

def build_estimate():
    def fld(i, label, val, hint='', f=''):
        h = '<div class="note">%s</div>' % hint if hint else ''
        d = ' data-for="%s"' % f if f else ''
        return '<div%s><label for="%s">%s</label><input id="%s" inputmode="decimal" value="%s" autocomplete="off">%s</div>' % (d, i, label, i, val, h)
    form = ('<form class="form" id="ef" novalidate aria-label="برآورد متریال"><div class="two"><div><label for="sys">نوع سقف</label><select id="sys"><option value="drywall">سقف گچی درای‌وال (پروفیل F47)</option><option value="grid">سقف شبکه‌ای ۶۰×۶۰</option></select></div>'
            '<div><label for="area">متراژ سقف (متر مربع) *</label><input id="area" inputmode="decimal" placeholder="مثلاً ۱۲۰" autocomplete="off"><div class="err" id="area-e" role="alert"></div></div></div>'
            '<div class="two">%s%s</div><div class="two">%s%s</div><div class="two">%s<div></div></div><div><button class="btn" type="submit">محاسبه برآورد</button></div></form>' %
            (fld('perim', 'محیط سقف (متر)', '', 'اگر خالی بماند از روی متراژ (مربع‌شکل) حساب می‌شود.'), fld('waste', 'درصد پرت و اضافه', '۱۰', 'برای برش و خرابی؛ بین ۰ تا ۵۰.'),
             fld('sp', 'فاصله F47 پانل‌خور (متر)', '۰٫۶', '', 'drywall'), fld('cs', 'فاصله F47 باربر (متر)', '۱٫۲', '', 'drywall'), fld('hs', 'فاصله آویزها روی باربر (متر)', '۱٫۲', '', 'drywall')))
    res = ('<div id="res" hidden><div class="cta"><div><p>برآورد اولیه</p><h2 id="sum"></h2></div></div><div class="scroll x21"><table class="tbl"><thead><tr><th>قلم</th><th>مقدار</th><th>واحد</th><th>توضیح</th></tr></thead><tbody id="tb"></tbody></table></div>'
           '<p class="note">این فقط یک <b>تخمین اولیه</b> بر اساس چیدمان استاندارد و ابعاد کاتالوگ شرکت است؛ فضای واقعی، ارتفاع، بازشوها، سقف‌های دکوراتیو و پیچ و میخ و چاشنی در آن لحاظ نشده است. مقدار نهایی و قیمت را کارشناس فنی پس از بررسی نقشه اعلام می‌کند.</p>'
           '<p class="row x22"><a class="btn" id="qlink" href="/quote/">ارسال این برآورد برای کارشناس و دریافت قیمت</a></p></div>')
    body = (phero('برآورد متریال', 'متراژ و نوع سقف را بنویسید تا تعداد تقریبی پروفیل، اتصالات و تایل را ببینید؛ سپس برای قیمت دقیق، برآورد را برای کارشناس بفرستید.', [('/', 'خانه'), (None, 'برآورد متریال')]) +
            '<section class="sec"><div class="wrap x23"><div class="formcard">%s</div><div class="x24">%s</div></div></section>' % (form, res) + cta())
    steps = ['نوع سقف را انتخاب کنید.', 'متراژ سقف را به متر مربع وارد کنید.', 'در صورت نیاز محیط و فاصله پروفیل‌ها را تغییر دهید.', 'تعداد تقریبی هر قلم را ببینید و برای قیمت دقیق آن را برای کارشناس بفرستید.']
    page('/estimate/', 'برآورد متریال سقف کاذب | محاسبه تعداد پروفیل F47 و تایل', 'ماشین‌حساب برآورد متریال سقف گچی درای‌وال و سقف شبکه‌ای ۶۰×۶۰ بر اساس متراژ: تعداد شاخه F47، نبشی L25، کلیپس، آویز، تایل و سپری با ابعاد کاتالوگ شرکت.', body,
         crumbs=[('/', 'خانه'), ('/estimate/', 'برآورد متریال')], scripts=('estimate.js',), priority='0.9', freq='weekly',
         extra_ld=[{"@type": "WebApplication", "@id": SITE + '/estimate/#app', "name": "ماشین‌حساب برآورد متریال سقف", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "fa-IR", "isAccessibleForFree": True, "publisher": {"@id": ORG_ID}},
                   {"@type": "HowTo", "@id": SITE + '/estimate/#howto', "name": "برآورد متریال سقف کاذب", "step": [{"@type": "HowToStep", "position": i + 1, "text": s} for i, s in enumerate(steps)]}])
    add_doc('برآورد متریال', 'ماشین‌حساب برآورد تعداد پروفیل F47 نبشی L25 کلیپس آویز تایل بر اساس متراژ', '/estimate/', 'صفحه', 'محاسبه متراژ برآورد')

def build_assistant():
    for f in ('show/d2.jpg', 'show/p01.jpg', 'show/p06.jpg', 'show/p07.jpg', 'show/p12.jpg', 'show/p13.jpg', 'show/r8.jpg'):
        variants(f)  # sample photos the assistant.js pick() function references by constructed URL, not via rimg()
    chat = ('<div class="chat rv"><div class="chat-hd"><img src="/assets/img/emblem.jpg" alt="" width="560" height="260"><div><b>البرزبات</b><small>دستیار هوشمند صنعت سقف البرز خاورمیانه — پاسخ از مستندات خود شرکت، بدون ارسال اطلاعات تا زمان درخواست تماس</small></div></div>'
            '<div class="msgs" id="msgs" aria-live="polite"></div><div class="composer" id="composer"></div></div>'
            '<noscript><p class="note">برای استفاده از دستیار، جاوااسکریپت را فعال کنید یا با <a href="tel:+982188507585" class="num">%s</a> تماس بگیرید.</p></noscript>'
            '<p class="note x25">دستیار پیشنهاد فنی یا قیمت نهایی نمی‌دهد؛ پس از ثبت درخواست، کارشناس فروش با شما تماس می‌گیرد.</p>' % PHONE_FA)
    body = (phero('دستیار هوشمند', 'متراژ و کاربری فضا را بگویید تا برآورد متریال و یک نمونه سقف ببینید؛ سؤال فنی هم بپرسید. برای قیمت، کارشناس فروش تماس می‌گیرد.', [('/', 'خانه'), (None, 'دستیار هوشمند')]) +
            '<section class="sec"><div class="wrap">%s</div></section>' % chat)
    page('/assistant/', 'دستیار هوشمند | برآورد متریال و پاسخ فنی', 'دستیار هوشمند صنعت سقف البرز خاورمیانه: برآورد متریال از روی متراژ، نمونه سقف اجراشده برای فضای شما و پاسخ پرسش‌های فنی درباره پروفیل‌ها و سقف‌ها.', body,
         crumbs=[('/', 'خانه'), ('/assistant/', 'دستیار هوشمند')], scripts=('assistant.js',), priority='0.8')
    add_doc('دستیار هوشمند', 'گفت‌وگو برآورد متریال نمونه سقف پاسخ فنی', '/assistant/', 'صفحه', 'چت هوشمند')
