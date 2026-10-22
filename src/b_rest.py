# -*- coding: utf-8 -*-
from b_core import *
from b_pages import ALLP

def art_html(blocks):
    out, toc = '', []
    for t, v in blocks:
        if t == 'h2':
            hid = 'h%d' % (len(toc) + 1); toc.append((hid, v)); out += '<h2 id="%s">%s</h2>' % (hid, v)
        elif t == 'p':
            out += '<p>%s</p>' % v
        elif t == 'ul':
            out += '<ul>%s</ul>' % ''.join('<li>%s</li>' % i for i in v)
    return out, toc

def words(blocks):
    n = 0
    for t, v in blocks:
        n += len(re.findall(r'\S+', v if isinstance(v, str) else ' '.join(v)))
    return n

ART_IMG = {'estimate': 'projects/p06.jpg', 'default': 'projects/p01.jpg'}
def art_img(a):
    s = a['slug']
    return 'show/p04.jpg' if ('drywall' in s or 'profile' in s or 'screw' in s) else 'projects/p01.jpg'

def build_articles():
    cards = ''.join('<a class="card hv pc rv" href="/articles/%s/">%s<div class="b"><h3>%s</h3><p>%s</p><span class="link">ادامه مطلب</span></div></a>' % (a['slug'], rimg(art_img(a), a['title'], '(max-width:760px) 100vw, 33vw'), esc(a['title']), esc(a['desc'])) for a in ARTICLES)
    body = (phero('مقالات و آموزش', 'راهنمای انتخاب، اجزای سیستم‌ها و نکات فنی سقف کاذب و درای‌وال؛ همه بر پایه اطلاعات رسمی کاتالوگ شرکت.', [('/', 'خانه'), (None, 'مقالات')]) +
            '<section class="sec"><div class="wrap"><h2 class="sr">فهرست مقالات</h2><div class="grid g3">%s</div></div></section>' % cards + cta())
    page('/articles/', 'مقالات آموزشی سقف کاذب و درای‌وال', 'مقالات تخصصی صنعت سقف البرز خاورمیانه: انتخاب سقف کاذب، اجزای سقف شبکه‌ای، پروفیل‌های درای‌وال، پیچ‌ها، ضخامت ورق و برآورد متریال.', body,
         crumbs=[('/', 'خانه'), ('/articles/', 'مقالات')], priority='0.8', freq='weekly', kind='CollectionPage',
         extra_ld=[{"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + '/articles/%s/' % a['slug'], "name": a['title']} for i, a in enumerate(ARTICLES)]}])
    add_doc('مقالات', 'مقالات آموزشی سقف کاذب درای‌وال', '/articles/', 'صفحه', 'مقاله آموزش')
    for k, a in enumerate(ARTICLES):
        url = SITE + '/articles/%s/' % a['slug']
        content, toc = art_html(a['body'])
        tocbox = '<nav class="tocbox rv" aria-label="فهرست مطالب"><b>در این مقاله</b>%s</nav>' % ''.join('<a href="#%s">%s</a>' % t for t in toc) if len(toc) > 2 else ''
        others = [b for b in ARTICLES if b is not a][:3]
        rel = '<div class="rel rv">%s</div>' % ''.join('<a href="/articles/%s/">%s</a>' % (b['slug'], esc(b['title'])) for b in others)
        prods = '<div class="rel rv">%s</div>' % ''.join('<a href="/products/%s/">%s</a>' % (q['slug'], esc(q['title'])) for q in ALLP[:3])
        body = (phero(a['title'], a['desc'], [('/', 'خانه'), ('/articles/', 'مقالات'), (None, 'مقاله')]) +
                '<section class="sec"><div class="wrap"><article class="art"><p class="note">منتشر شده: %s · زمان مطالعه حدود %s دقیقه</p>%s%s<p class="row x15"><a class="btn" href="/estimate/">برآورد متریال</a><a class="btn line" href="/quote/">درخواست مشاوره و قیمت</a></p><h2>محصولات مرتبط</h2>%s<h2>مقاله‌های بیشتر</h2>%s</article></div></section>' % (FIRST_PUBLISHED, max(1, round(words(a['body']) / 180)), tocbox, content, prods, rel))
        ld = {"@type": "Article", "@id": url + '#article', "headline": a['title'], "description": a['desc'], "inLanguage": "fa-IR", "datePublished": FIRST_PUBLISHED, "dateModified": TODAY, "wordCount": words(a['body']),
              "image": [SITE + rurl(art_img(a), 1600)], "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}, "mainEntityOfPage": {"@id": url + '#webpage'}}
        page('/articles/%s/' % a['slug'], '%s | %s' % (a['title'], NAME), a['desc'], body, extra_ld=[ld], article=True, kind='Article' if False else 'WebPage',
             crumbs=[('/', 'خانه'), ('/articles/', 'مقالات'), ('/articles/%s/' % a['slug'], a['title'])], priority='0.7', images=[SITE + rurl(art_img(a), 1600)])
        add_doc(a['title'], a['desc'] + ' ' + ' '.join(v if isinstance(v, str) else ' '.join(v) for t, v in a['body']), '/articles/%s/' % a['slug'], 'مقاله')

def build_glossary():
    dl = '<dl class="gl">%s</dl>' % ''.join(
        '<div class="glrow rv">%s<div><dt id="t%d">%s</dt><dd>%s</dd></div></div>' % (rimg(GLOSSARY_IMG[i], t, '84px'), i, esc(t), esc(d))
        for i, (t, d) in enumerate(GLOSSARY))
    body = (phero('واژه‌نامه سقف کاذب و درای‌وال', 'معنی اصطلاحات رایج: پروفیل F47، UH36، L25، سپری، تایل مینرال، باکس نور مخفی و بیشتر؛ به زبان ساده.', [('/', 'خانه'), (None, 'واژه‌نامه')]) +
            '<section class="sec"><div class="wrap"><div class="art">%s</div></div></section>' % dl + cta())
    page('/glossary/', 'واژه‌نامه سقف کاذب و درای‌وال | معنی اصطلاحات', 'معنی اصطلاحات سقف کاذب و درای‌وال: درای‌وال، پروفیل F47، UH36، L25، کلیپس، سپری نمایان و پنهان، تایل مینرال، گریلیوم، باکس نور مخفی و گالوانیزه.', body,
         crumbs=[('/', 'خانه'), ('/glossary/', 'واژه‌نامه')], priority='0.7', extra_ld=[{"@type": "DefinedTermSet", "@id": SITE + '/glossary/#terms', "name": "واژه‌نامه سقف کاذب و درای‌وال", "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d, "url": SITE + '/glossary/#t%d' % i} for i, (t, d) in enumerate(GLOSSARY)]}])
    for i, (t, d) in enumerate(GLOSSARY):
        add_doc(t, d, '/glossary/#t%d' % i, 'واژه‌نامه')

def build_faq():
    ask_bot = '<div class="row"><a class="btn" href="/assistant/">پرسیدن از دستیار هوشمند</a></div>'
    body = (phero('پرسش‌های متداول', 'پاسخ کوتاه و دقیق درباره پروفیل‌ها، سقف‌ها، ضخامت و وزن، ارسال و ساعات کاری؛ یا مستقیم از دستیار هوشمند بپرسید.', [('/', 'خانه'), (None, 'پرسش‌های متداول')], ask_bot) +
            '<section class="sec"><div class="wrap x10">%s</div></section>' % faq_html(FAQ_HUB) + cta('پاسخ خود را پیدا نکردید؟', 'از دستیار هوشمند بپرسید یا کارشناس ما با شما تماس می‌گیرد.'))
    page('/faq/', 'پرسش‌های متداول | پروفیل، سقف شبکه‌ای، ارسال', 'پاسخ پرسش‌های پرتکرار: تفاوت F47 و UH36، ضخامت و وزن پروفیل، طول سفارشی، تایل مقاوم رطوبت، ارسال به سراسر کشور و ساعات کاری.', body,
         crumbs=[('/', 'خانه'), ('/faq/', 'پرسش‌های متداول')], priority='0.8', extra_ld=[faq_node(FAQ_HUB, SITE + '/faq/')], kind='FAQPage' if False else 'WebPage')
    for q, a in FAQ_HUB:
        add_doc(q, a, '/faq/', 'پرسش')

def build_search():
    allp = ENTRIES
    links = ''.join('<li><a href="%s">%s</a></li>' % (p, esc(v['title'].split('|')[0].strip())) for p, v in sorted(allp.items()) if p not in ('/404.html', '/search/'))
    body = (phero('جست‌وجو در سایت', 'نام محصول، پروفیل یا موضوع را بنویسید. میان‌بر: Ctrl+K یا «/» در هر صفحه.', [('/', 'خانه'), (None, 'جست‌وجو')]) +
            '<section class="sec"><div class="wrap x10"><form class="form" role="search" action="/search/" method="get"><label for="sq">عبارت جست‌وجو</label><input id="sq" name="q" type="search" autocomplete="off" placeholder="مثلاً: F47 یا وزن بندیل"></form><div id="sr" class="x24" aria-live="polite"></div>'
            '<noscript><h2 class="x24">نقشه سایت</h2><ul class="checks">%s</ul></noscript></div></section>' % links)
    page('/search/', 'جست‌وجو در سایت | %s' % NAME, 'جست‌وجو در محصولات، مقالات، پرسش‌ها و واژه‌نامه صنعت سقف البرز خاورمیانه.', body, noindex=True, scripts=('search.js',))

def build_privacy():
    collect = [('فرم «درخواست قیمت» و «تماس با ما»', 'نام، شماره تماس، شهر، نام شرکت (اختیاری) و توضیحات پروژه.'),
               ('ثبت‌نام در پنل مشتریان', 'نام، ایمیل یا شماره موبایل، رمز عبور (به‌صورت هش‌شده ذخیره می‌شود، نه متن ساده)، شهر، نام شرکت و شغل (اختیاری).'),
               ('ثبت سفارش', 'آدرس تحویل، زمان مورد نیاز، و فایل‌هایی که خودتان برای سفارش بارگذاری می‌کنید (فاکتور یا نقشه).'),
               ('بازدید صفحات سایت', 'فقط تعداد بازدید هر صفحه به‌صورت ناشناس ثبت می‌شود؛ بدون کوکی ردیابی و بدون ذخیره آدرس IP.'),
               ('گزارش امنیتی', 'برای جلوگیری از سوءاستفاده و ورود غیرمجاز، آدرس IP درخواست‌ها و تاریخچه‌ی فعالیت حساب (مثل زمان ورود) نگه‌داری می‌شود.')]
    use = ['پاسخ‌گویی به درخواست قیمت یا مشاوره توسط کارشناس فروش', 'پیگیری و تکمیل سفارش‌های ثبت‌شده', 'جلوگیری از ثبت‌نام و پیام‌های مزاحم و خودکار (ربات‌ها)', 'اطلاع‌رسانی درباره‌ی وضعیت سفارش یا حساب کاربری']
    protect = ['رمز عبور با الگوریتم استاندارد (scrypt) هش می‌شود؛ حتی کارکنان ما هم رمز شما را نمی‌بینند.', 'امکان فعال‌سازی تأیید دومرحله‌ای (2FA) برای حساب کاربری وجود دارد.', 'فایل‌های بارگذاری‌شده پیش از ذخیره بررسی و بازتولید می‌شوند تا فایل مخرب ذخیره نشود.', 'دسترسی به اطلاعات مشتریان فقط برای کارشناسان فروش و مدیر سیستم، آن هم فقط در محدوده‌ی کاری‌شان، امکان‌پذیر است.']
    body = (phero('حریم خصوصی', 'این صفحه دقیقاً توضیح می‌دهد چه اطلاعاتی از شما جمع‌آوری می‌شود، چرا، و چطور محافظت می‌شود.', [('/', 'خانه'), (None, 'حریم خصوصی')]) +
            ('<section class="sec"><div class="wrap"><div class="split"><div>%s<h2>چه اطلاعاتی <em class="o">جمع‌آوری</em> می‌شود؟</h2><p class="lead">فقط همان اطلاعاتی که خودتان در فرم‌ها وارد می‌کنید؛ هیچ داده‌ای بدون اطلاع شما از منبع دیگری گرفته نمی‌شود.</p></div>'
             '<div class="card pad"><ul class="checks x15">%s</ul></div></div></div></section>' % (kicker('01', 'جمع‌آوری'), ''.join('<li><b>%s</b> — %s</li>' % (esc(t), d) for t, d in collect))) +
            ('<section class="sec paper2"><div class="wrap"><div class="split rev"><div>%s<h2>چرا این اطلاعات <em class="o">استفاده</em> می‌شود؟</h2><p class="lead">اطلاعات شما هرگز به شخص ثالث فروخته یا اجاره داده نمی‌شود.</p></div>'
             '<div class="card pad"><ul class="checks x15">%s</ul></div></div></div></section>' % (kicker('02', 'استفاده'), ''.join('<li>%s</li>' % u for u in use))) +
            ('<section class="sec"><div class="wrap"><div class="split"><div>%s<h2>چطور <em class="o">محافظت</em> می‌شود؟</h2></div><div class="card pad"><ul class="checks x15">%s</ul></div></div></div></section>' % (kicker('03', 'امنیت'), ''.join('<li>%s</li>' % p for p in protect))) +
            ('<section class="sec paper2"><div class="wrap x10"><h2>حذف یا اصلاح اطلاعات</h2><p class="lead">هر زمان بخواهید اطلاعات حساب خود را حذف یا اصلاح کنید، یا بدانید چه اطلاعاتی از شما نگه‌داری می‌شود، کافی‌ست با ایمیل <a class="link" href="mailto:%s">%s</a> یا تلفن <a class="num" href="tel:+982188507585">%s</a> با ما تماس بگیرید.</p></div></section>'
             % (EMAIL, EMAIL, PHONE_FA)) + cta('سؤالی درباره حریم خصوصی دارید؟', 'با کارشناسان ما تماس بگیرید.'))
    page('/privacy/', 'حریم خصوصی | %s' % NAME_FULL, 'سیاست حریم خصوصی صنعت سقف البرز خاورمیانه: چه اطلاعاتی جمع‌آوری می‌شود، چرا، و چطور محافظت و نگه‌داری می‌شود.', body,
         crumbs=[('/', 'خانه'), ('/privacy/', 'حریم خصوصی')], priority='0.3')
    add_doc('حریم خصوصی', 'سیاست حریم خصوصی جمع‌آوری اطلاعات امنیت داده مشتریان', '/privacy/', 'صفحه', 'حریم خصوصی')

def build_404():
    body = phero('صفحه پیدا نشد', 'آدرسی که وارد کرده‌اید وجود ندارد یا جابه‌جا شده است. می‌توانید جست‌وجو کنید یا به صفحه‌های اصلی بروید.', [('/', 'خانه'), (None, '۴۰۴')], '<div class="row"><a class="btn" href="/">صفحه اصلی</a><a class="btn line" href="/search/">جست‌وجو</a><a class="btn line" href="/products/">محصولات</a></div>')
    page('/404.html', 'صفحه پیدا نشد', 'صفحه مورد نظر پیدا نشد.', body, noindex=True)

