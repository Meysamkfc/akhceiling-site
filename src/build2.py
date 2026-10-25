# -*- coding: utf-8 -*-
"""Site 2 builder:  python build2.py   ->  ../site/   (static, strict CSP, SRI, cache-busted assets) + ../server/templates/_base.html"""
import subprocess, base64, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from b_core import *
import b_core
from b_pages import *
import b_pages, b_rest, b_pages_en
from PIL import ImageDraw

def clean_out():
    os.makedirs(OUT, exist_ok=True)
    for n in os.listdir(OUT):
        p = os.path.join(OUT, n)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

def copy_static():
    def cp(rel, dst=None, only=None):
        s = os.path.join(A, rel); d = os.path.join(OUT, 'assets', dst or rel)
        if not os.path.exists(s):
            return
        os.makedirs(os.path.dirname(d) if os.path.isfile(s) else d, exist_ok=True)
        if os.path.isfile(s):
            shutil.copy(s, d)
        else:
            for f in os.listdir(s):
                if only and not only(f):
                    continue
                shutil.copy(os.path.join(s, f), os.path.join(d, f)) if os.path.isfile(os.path.join(s, f)) else None
    cp('fonts'); cp('clients'); cp('video'); cp('img', only=lambda f: f in ('emblem.jpg', 'noise.webp'))
    cp('catalog', only=lambda f: f.endswith('-big.jpg') or f.endswith('.pdf'))
    cp('gallery', only=lambda f: f.startswith('g'))
    cp('cards', only=lambda f: f.endswith('-big.jpg'))
    # icons
    im = Image.open(os.path.join(A, 'img', 'emblem.jpg')).convert('RGB'); s = max(im.size)
    sq = Image.new('RGB', (s, s), 'white'); sq.paste(im, ((s - im.width) // 2, (s - im.height) // 2))
    d = os.path.join(OUT, 'assets', 'img'); os.makedirs(d, exist_ok=True)
    for n, sz in (('favicon.png', 64), ('apple-touch-icon.png', 180), ('icon-192.png', 192), ('icon-512.png', 512)):
        sq.resize((sz, sz), Image.LANCZOS).save(os.path.join(d, n))

OGSRC = {'home': 'show/p04.jpg', 'products': 'projects/p01.jpg', 'projects': 'projects/p07.jpg', 'estimate': 'projects/p01.jpg', 'about': 'photos/real-factory.jpg', 'contact': 'photos/real-expo.jpg',
         'drywall': 'show/p04.jpg', 'grid': 'projects/p01.jpg', 'profiles': 'photos/real-factory.jpg', 'accessories': 'photos/real-install.jpg',
         'articles': 'projects/p06.jpg', 'assistant': 'show/r8.jpg', 'catalogs': 'catalog/f47.jpg'}
def make_og():
    os.makedirs(os.path.join(OUT, 'assets', 'og'), exist_ok=True)
    emb = Image.open(os.path.join(A, 'img', 'emblem.jpg')).convert('RGB'); emb.thumbnail((360, 170))
    for name, rel in OGSRC.items():
        im = Image.open(os.path.join(A, rel)).convert('RGB'); w, h = im.size; r = 1200 / 630
        if w / h > r: nw = int(h * r); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else: nh = int(w / r); y0 = int((h - nh) * .4); im = im.crop((0, y0, w, y0 + nh))
        im = im.resize((1200, 630), Image.LANCZOS)
        ov = Image.new('RGB', (1200, 630), (21, 23, 63)); im = Image.blend(im, ov, .22)
        card = Image.new('RGB', (emb.width + 36, emb.height + 28), 'white'); card.paste(emb, (18, 14)); im.paste(card, (1200 - card.width - 40, 40))
        bar = Image.new('RGB', (1200, 10), (246, 130, 31)); im.paste(bar, (0, 620))
        im.save(os.path.join(OUT, 'assets', 'og', name + '.jpg'), quality=84, optimize=True, progressive=True)
    for p in ('/', ):
        OGMAP[p] = 'home'
    for pth, n in (('/products/', 'products'), ('/projects/', 'projects'), ('/estimate/', 'estimate'), ('/about/', 'about'), ('/contact/', 'contact'), ('/assistant/', 'assistant'), ('/catalogs/', 'catalogs'),
                   ('/articles/', 'articles'), ('/quote/', 'home'), ('/faq/', 'home'), ('/membership/', 'about')):
        OGMAP[pth] = n
    for p in ALLP:
        OGMAP['/products/%s/' % p['slug']] = {'drywall': 'drywall', 'grid-ceiling': 'grid', 'profiles': 'profiles', 'accessories': 'accessories'}[p['slug']]
    for a in ARTICLES:
        OGMAP['/articles/%s/' % a['slug']] = 'articles'

def bundle_js():
    od = os.path.join(OUT, 'assets', 'js'); os.makedirs(od, exist_ok=True)
    esb = os.path.join(ROOT, 'tools', 'node_modules', '.bin', 'esbuild.cmd' if os.name == 'nt' else 'esbuild')
    jd = os.path.join(HERE, 'js')
    ents = {'main.js': 'main.js', 'home.js': 'home.js', 'estimate.js': 'estimate.js', 'quote.js': 'quote.js', 'assistant.js': 'assistant.js', 'order.js': 'order.js', 'search.js': 'search.js', 'auth.js': 'auth.js', 'hero3d.js': 'hero3d.src.js'}
    # hero3d.js and assistant.js are loaded at runtime via dynamic import() (see home.js and the floating
    # chat widget in main.js), which needs a real ES module output; every other entry is a plain
    # <script type="module" src=...> in the HTML, so IIFE is fine for those.
    for out, src in ents.items():
        fmt = 'esm' if out in ('hero3d.js', 'assistant.js') else 'iife'
        r = subprocess.run([esb, os.path.join(jd, src), '--bundle', '--minify', '--format=' + fmt, '--target=es2019', '--legal-comments=none', '--outfile=' + os.path.join(od, out), '--log-level=error', '--resolve-extensions=.js,.mjs', '--alias:three=' + os.path.join(ROOT, 'tools', 'node_modules', 'three', 'build', 'three.module.js')], capture_output=True, text=True, cwd=os.path.join(ROOT, 'tools'))
        if r.returncode:
            print('esbuild failed:', src, r.stderr[:500]); sys.exit(1)
    shutil.copy(os.path.join(jd, 'flag.js'), os.path.join(od, 'flag.js'))

def build_css():
    od = os.path.join(OUT, 'assets', 'css'); os.makedirs(od, exist_ok=True)
    ff = ("@font-face{font-family:Vazirmatn;font-style:normal;font-weight:300 900;font-display:swap;src:url(/assets/fonts/vazirmatn-arabic.woff2) format('woff2');unicode-range:U+0600-06FF,U+0750-077F,U+0870-088E,U+0890-0891,U+0898-08E1,U+08E3-08FF,U+200C-200E,U+2010-2011,U+204F,U+2E41,U+FB50-FDFF,U+FE70-FE74,U+FE76-FEFC}\n"
          "@font-face{font-family:Vazirmatn;font-style:normal;font-weight:300 900;font-display:swap;src:url(/assets/fonts/vazirmatn-latin.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}\n")
    css = ff + open(os.path.join(HERE, 'css', 'site2.css'), encoding='utf-8').read()
    util = '\n/* generated utilities */\n' + ''.join('.%s{%s}\n' % (c, k) for k, c in b_core._STYLES.items())
    css = minify_css(css + util)
    open(os.path.join(od, 'site2.css'), 'w', encoding='utf-8').write(css)

def minify_css(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S); s = re.sub(r'\s+', ' ', s); s = re.sub(r'\s*([{};:,>])\s*', r'\1', s); return s.replace(';}', '}')

def data_files():
    d = os.path.join(OUT, 'assets', 'data'); os.makedirs(d, exist_ok=True)
    json.dump(SEARCH, open(os.path.join(d, 'search.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

CSP = ("default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; font-src 'self'; media-src 'self'; connect-src 'self'; manifest-src 'self'; worker-src 'none'; "
       "frame-src https://maps.google.com https://www.google.com; "
       "object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; require-trusted-types-for 'script'; upgrade-insecure-requests")
HEADERS = {'Content-Security-Policy': CSP, 'Strict-Transport-Security': 'max-age=63072000; includeSubDomains; preload', 'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY',
           'Referrer-Policy': 'strict-origin-when-cross-origin', 'Permissions-Policy': 'accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=(), interest-cohort=()',
           'Cross-Origin-Opener-Policy': 'same-origin', 'Cross-Origin-Resource-Policy': 'same-origin', 'X-Permitted-Cross-Domain-Policies': 'none', 'X-DNS-Prefetch-Control': 'off'}

def seo_files():
    pages = sorted(PAGES, key=lambda x: (-float(x[1]), x[0]))
    ns = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"'
    urls = ''.join('<url><loc>%s%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority>%s</url>' % (SITE, p, TODAY, f, pr, ''.join('<image:image><image:loc>%s</image:loc></image:image>' % i for i in list(dict.fromkeys(imgs))[:20])) for p, pr, f, imgs in pages)
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset %s>%s</urlset>' % (ns, urls))
    NL = chr(10)
    # explicit allows for AI answer-engine / assistant crawlers (GEO/AEO): ChatGPT, Google AI, Perplexity,
    # Claude and Common Crawl (used by most LLM training sets) are welcomed in addition to the default '*' rule.
    ai_bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'Google-Extended', 'PerplexityBot', 'Perplexity-User',
               'ClaudeBot', 'Claude-User', 'Claude-SearchBot', 'anthropic-ai', 'CCBot', 'Applebot-Extended',
               'MistralAI-User', 'DeepSeekBot', 'xAI-Bot', 'cohere-ai', 'meta-externalagent']
    ai_rules = []
    for b in ai_bots:
        ai_rules += ['User-agent: ' + b, 'Allow: /', '']
    open(os.path.join(OUT, 'robots.txt'), 'w').write(NL.join(['User-agent: *', 'Allow: /', 'Disallow: /account/', 'Disallow: /admin/', 'Disallow: /api/', 'Disallow: /files/', 'Disallow: /search/', ''] +
                                                             ai_rules + ['Sitemap: ' + SITE + '/sitemap.xml', '']))
    items = ''.join('<item><title>%s</title><link>%s/articles/%s/</link><guid isPermaLink="true">%s/articles/%s/</guid><pubDate>Sat, 17 Oct 2026 08:00:00 +0000</pubDate><description>%s</description></item>' % (esc(a['title']), SITE, a['slug'], SITE, a['slug'], esc(a['desc'])) for a in ARTICLES)
    open(os.path.join(OUT, 'rss.xml'), 'w', encoding='utf-8').write('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>مقالات %s</title><link>%s/articles/</link><description>مقالات آموزشی سقف کاذب و درای‌وال</description><language>fa-IR</language>%s</channel></rss>' % (esc(NAME), SITE, items))
    open(os.path.join(OUT, 'manifest.webmanifest'), 'w', encoding='utf-8').write(json.dumps({"name": NAME_FULL, "short_name": "AKH", "lang": "fa", "dir": "rtl", "start_url": "/", "display": "standalone", "background_color": "#f4f5fb", "theme_color": "#15173f",
                                                                                          "icons": [{"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}, ensure_ascii=False))
    llms = ['# ' + NAME_FULL, '', '> تولیدکننده پروفیل درای‌وال (F47، UH36، L25) و سقف کاذب شبکه‌ای ۶۰×۶۰. کارخانه کهریزک، دفتر مرکزی تهران، ارسال به سراسر کشور. تلفن ' + PHONE + '.', '', '## صفحه‌های اصلی'] + \
           ['- [%s](%s%s): %s' % (v['title'].split('|')[0].strip(), SITE, p, v['desc']) for p, v in sorted(ENTRIES.items()) if p not in ('/404.html', '/search/') and not p.startswith('/articles/')] + ['', '## مقالات'] + \
           ['- [%s](%s/articles/%s/): %s' % (a['title'], SITE, a['slug'], a['desc']) for a in ARTICLES]
    open(os.path.join(OUT, 'llms.txt'), 'w', encoding='utf-8').write(NL.join(llms) + NL)
    os.makedirs(os.path.join(OUT, '.well-known'), exist_ok=True)
    open(os.path.join(OUT, '.well-known', 'security.txt'), 'w', encoding='utf-8').write(NL.join(['Contact: mailto:' + EMAIL, 'Expires: 2027-10-17T00:00:00.000Z', 'Preferred-Languages: fa, en', 'Canonical: ' + SITE + '/.well-known/security.txt', 'Policy: ' + SITE + '/contact/', '']))
    open(os.path.join(OUT, 'humans.txt'), 'w', encoding='utf-8').write('Company: %s\nContact: %s\nTechnology: static HTML, Flask, WebGL (Three.js)\n' % (NAME_FULL, EMAIL))
    open(os.path.join(OUT, '_headers'), 'w').write('/*\n' + ''.join('  %s: %s\n' % kv for kv in HEADERS.items()) + '/assets/*\n  Cache-Control: public, max-age=3600\n/assets/css/*\n  Cache-Control: public, max-age=31536000, immutable\n/assets/js/*\n  Cache-Control: public, max-age=31536000, immutable\n')
    # Netlify/Cloudflare Pages compress and cache automatically from the rules above; Apache and nginx need it spelled out.
    COMPRESS_TYPES = ('text/html text/css text/plain text/xml application/xml application/xhtml+xml application/rss+xml '
                       'application/javascript application/x-javascript application/json image/svg+xml font/ttf font/otf application/vnd.ms-fontobject')
    ht = ('<IfModule mod_headers.c>\n' + ''.join('  Header always set %s "%s"\n' % kv for kv in HEADERS.items()) + '  <FilesMatch "\\.(css|js)$">\n    Header set Cache-Control "public, max-age=31536000, immutable"\n  </FilesMatch>\n</IfModule>\n'
          '<IfModule mod_deflate.c>\n  AddOutputFilterByType DEFLATE %s\n</IfModule>\n' % COMPRESS_TYPES +
          '<IfModule mod_brotli.c>\n  AddOutputFilterByType BROTLI_COMPRESS %s\n</IfModule>\n' % COMPRESS_TYPES +
          '<IfModule mod_expires.c>\n  ExpiresActive On\n  ExpiresByType text/css "access plus 1 year"\n  ExpiresByType application/javascript "access plus 1 year"\n  ExpiresByType image/webp "access plus 1 hour"\n  ExpiresDefault "access plus 1 hour"\n</IfModule>\n'
          'ErrorDocument 404 /404.html\nOptions -Indexes\n')
    open(os.path.join(OUT, '.htaccess'), 'w').write(ht)
    ng = ('# add inside http { } (once per server, not per site) - gzip the compressible, text-based response types\n'
          'gzip on;\ngzip_vary on;\ngzip_comp_level 6;\ngzip_min_length 256;\ngzip_proxied any;\n'
          'gzip_types %s;\n'
          '# brotli needs the ngx_brotli module (not built into stock nginx); uncomment if it is installed\n'
          '# brotli on; brotli_comp_level 5; brotli_types %s;\n\n'
          '# add inside server { }\n' % (COMPRESS_TYPES, COMPRESS_TYPES) +
          ''.join('add_header %s "%s" always;\n' % kv for kv in HEADERS.items()) +
          'error_page 404 /404.html;\n'
          '# css/js filenames are content-hashed (?v=hash) on every deploy, so they can be cached for a year without going stale\n'
          'location /assets/css/ { expires 1y; add_header Cache-Control "public, immutable" always; }\n'
          'location /assets/js/ { expires 1y; add_header Cache-Control "public, immutable" always; }\n'
          '# images/fonts/etc. are not content-hashed, so a short cache keeps replaced files from sticking around\n'
          'location /assets/ { expires 1h; }\n')
    open(os.path.join(OUT, 'nginx.conf.example'), 'w').write(ng)

def export_jinja_base():
    h = header('', dynamic=True)
    doc = ('<!doctype html><html lang="@@L@@" dir="@@D@@"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>@@T@@ | ' + NAME_FULL + '</title><meta name="robots" content="noindex,nofollow">'
           '<link rel="icon" href="/assets/img/favicon.png" sizes="64x64"><link rel="preload" href="/assets/fonts/vazirmatn-arabic.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/assets/css/site2.css"><script src="/assets/js/flag.js"></script></head>'
           '<body class="inner app"><a class="skip" href="#main">پرش به محتوا</a>' + h + '<main id="main">@@C@@</main>' + footer() + palette() + lightbox() + '<script type="module" src="/assets/js/main.js"></script>@@S@@</body></html>')
    doc = inline_to_classes(apply_xsty(doc)).replace('@@T@@', '{% block title %}{{ title|default("پنل") }}{% endblock %}').replace('@@C@@', '{% block content %}{% endblock %}').replace('@@S@@', '{% block scripts %}{% endblock %}')
    doc = doc.replace('@@L@@', "{{ 'en' if admin_lang=='en' else 'fa' }}").replace('@@D@@', "{{ 'ltr' if admin_lang=='en' else 'rtl' }}")
    tdir = os.path.join(ROOT, 'server', 'templates'); os.makedirs(tdir, exist_ok=True)
    open(os.path.join(tdir, '_base.html'), 'w', encoding='utf-8').write(doc)

def patch_dynamic_js_refs():
    """hero3d.js (from home.js) and assistant.js (from main.js, the floating chat widget) are lazy-loaded at
    runtime via dynamic import(), not a <script> tag in the HTML, so finalize()'s regex-based cache-busting
    never sees them. Patch the literal paths here, before finalize() hashes the *importing* file for its own
    <script> tag's ?v=/SRI — otherwise that SRI would go stale the moment this edits that file's bytes."""
    for host, dep in (('home.js', 'hero3d.js'), ('main.js', 'assistant.js')):
        hp = os.path.join(OUT, 'assets', 'js', host)
        dp = os.path.join(OUT, 'assets', 'js', dep)
        if not os.path.exists(hp) or not os.path.exists(dp):
            continue
        v = hashlib.md5(open(dp, 'rb').read()).hexdigest()[:10]
        s = open(hp, encoding='utf-8').read()
        s2 = s.replace('/assets/js/%s' % dep, '/assets/js/%s?v=%s' % (dep, v))
        if s2 != s:
            open(hp, 'w', encoding='utf-8').write(s2)

def finalize():
    """cache-busting (?v=hash) + Subresource Integrity on every first-party script / stylesheet"""
    def digest(rel):
        return open(os.path.join(OUT, rel.lstrip('/')), 'rb').read()
    def v(rel): return hashlib.md5(digest(rel)).hexdigest()[:10]
    def sri(rel): return 'sha384-' + base64.b64encode(hashlib.sha384(digest(rel)).digest()).decode()
    # also matches a tag already stamped by a previous build (?v=... + integrity=...), so re-running finalize()
    # always refreshes stale hashes instead of only stamping bare tags once and leaving old hashes forever.
    pat_s = re.compile(r'<script( type="module")? src="(/assets/js/[\w.\-]+\.js)(?:\?v=[0-9a-f]+)?"(?: integrity="sha384-[^"]*" crossorigin="anonymous")?( defer)?></script>')
    pat_c = re.compile(r'<link rel="stylesheet" href="(/assets/css/[\w.\-]+\.css)(?:\?v=[0-9a-f]+)?"(?: integrity="sha384-[^"]*" crossorigin="anonymous")?>')
    def fix(s):
        s = pat_s.sub(lambda m: '<script%s src="%s?v=%s" integrity="%s" crossorigin="anonymous"%s></script>' % (m.group(1) or '', m.group(2), v(m.group(2)), sri(m.group(2)), m.group(3) or ''), s)
        s = pat_c.sub(lambda m: '<link rel="stylesheet" href="%s?v=%s" integrity="%s" crossorigin="anonymous">' % (m.group(1), v(m.group(1)), sri(m.group(1))), s)
        return s
    targets = [os.path.join(dp, f) for dp, dn, fn in os.walk(OUT) for f in fn if f.endswith('.html')] + [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.join(ROOT, 'server', 'templates')) for f in fn if f.endswith('.html')]
    for p in targets:
        s = open(p, encoding='utf-8').read(); s2 = fix(s)
        if s2 != s: open(p, 'w', encoding='utf-8').write(s2)

if __name__ == '__main__':
    clean_out(); make_og()
    b_pages.build_home(); b_pages.build_home_en(); b_pages.build_products(); b_pages_en.build_products_en()
    for p in ALLP: b_pages.build_product(p)
    for p in ALLP: b_pages_en.build_product_en(p)
    b_pages.build_projects(); b_pages_en.build_projects_en()
    b_pages.build_catalogs()
    b_pages.build_about(); b_pages_en.build_about_en()
    b_pages.build_contact(); b_pages_en.build_contact_en()
    b_pages.build_membership(); b_pages_en.build_membership_en()
    b_pages.build_quote(); b_pages_en.build_quote_en()
    b_pages.build_estimate(); b_pages_en.build_estimate_en()
    b_pages.build_assistant(); b_pages_en.build_assistant_en()
    b_rest.build_articles(); b_rest.build_faq(); b_rest.build_privacy(); b_rest.build_404(); b_rest.build_search()
    copy_static(); bundle_js(); patch_dynamic_js_refs(); build_css(); data_files(); seo_files(); export_jinja_base(); finalize()
    print('pages:', len(PAGES), '| search docs:', len(SEARCH), '->', OUT)
