# -*- coding: utf-8 -*-
"""English counterparts of the Persian pages in b_rest.py (Phase 2 of the bilingual rollout).
Same rule as b_pages_en.py: structural/numeric data stays sourced from content_base.py / content2.py;
only labels and prose are hand-translated here, positionally paired with their Persian source."""
from b_core import *
from b_pages import ALLP
from b_rest import art_html, words, art_img

# ============================================================ ARTICLES
EN_ARTICLES = {
    'choosing-false-ceiling': dict(
        title='Choosing a False Ceiling: Which System Suits Your Project?',
        desc='Comparing grid and drywall ceilings, and the criteria for choosing based on building type, access to services, humidity and appearance.',
        body=[('h2', 'Start with what the project needs'),
              ('p', "Choosing a false ceiling isn't just about looks. Three questions help: What type of building is it? Do you need frequent access to the services above the ceiling? Is the environment damp or dry?"),
              ('h2', 'Comparing the two systems'),
              ('ul', ['60x60 grid ceiling: the best option when easy access to services matters; tiles can simply be lifted out. Installation is fast and needs no paint.',
                      'Drywall & plaster ceiling: suited to a seamless, joint-free surface, boxed sections, recessed lighting and decorative designs.']),
              ('h2', 'A few practical tips'),
              ('ul', ['In damp environments, use moisture-resistant materials such as aluminum tiles or moisture-resistant gypsum board.',
                      'If sound absorption matters, consider acoustic tiles.',
                      "Before buying, review the area and services drawing with a technical expert."]),
              ('p', "You can chat with the site's “Smart Assistant” to see an example suited to your space. The final recommendation should be confirmed by a technical expert.")]),
    'grid-ceiling-parts': dict(
        title='The Parts of a 60x60 Grid False Ceiling',
        desc='Wall angle, main tee, 120 and 60 cross tees, double-spring hangers and tile types — what each part of a grid ceiling does.',
        body=[('h2', 'The frame'),
              ('ul', ['Wall angle: levels and defines the edge of the ceiling.',
                      'Main tee (3.6 m): the primary bar, hung from the structure above.',
                      '120 and 60 cross tees: the secondary bars that complete the 60x60 grid.']),
              ('h2', 'The hanger'),
              ('p', 'The steel double-spring hanger is made from two galvanized wires and an adjustable spring, making it simple and stable to adjust the ceiling height.'),
              ('h2', 'The tiles'),
              ('ul', ['Gypsum tile: plain, PVC-faced, or acoustic perforated.',
                      'Aluminum tile: plain or punched, installed with an exposed or concealed grid.',
                      'Mineral acoustic tile: lightweight, with high sound absorption.']),
              ('p', 'Installing tiles is simple, and they can be lifted out to access the services above.')]),
    'drywall-profiles': dict(
        title='Drywall Profiles: What Are F47, UH36 and L25 Used For?',
        desc='An introduction to how the F47, UH36 and L25 profiles are used in drywall ceilings and walls, and notes on choosing 0.5mm or 0.6mm thickness.',
        body=[('h2', 'F47'),
              ('p', 'The most widely used drywall profile, used as both the load-bearing and panel-bearing member. Because panels and clips sit directly on it, manufacturing accuracy matters a great deal.'),
              ('h2', 'UH36'),
              ('p', 'A runner-type profile, typically used as a ceiling hanger, and in some cases as framing around recessed-light edges or cladding walls.'),
              ('h2', 'L25'),
              ('p', 'A 25x25 angle used to set the ceiling level and to frame boxes and recessed lighting.'),
              ('h2', '0.5mm or 0.6mm thickness'),
              ('p', "All three profiles are manufactured in two thicknesses. The thicker sheet gives more strength, and the bundle weighs more; the right choice depends on the project's height and load."),
              ('p', 'The full specification table (length, pieces per pack and bundle, weight) is on the “Profiles & Connectors” page.')]),
    'estimate-drywall-materials': dict(
        title='How Is Drywall Ceiling Material Estimated?',
        desc='A simple method for calculating the number of F47 profiles, L25 angles, clips and hangers for a drywall ceiling, based on area, profile spacing and waste percentage.',
        body=[('h2', 'The basic calculation'),
              ('p', 'Estimating materials means converting the ceiling area into profile lengths. Each F47 profile is 4 metres long and comes in packs of 20, so you just need the total length required, divided by 4.'),
              ('h2', 'Steps'),
              ('ul', ['Panel-bearing F47: at 60cm spacing, about 1.67 m of profile is needed per square metre (1 divided by 0.6).',
                      'Load-bearing F47: at 120cm spacing, about 0.83 m per square metre.',
                      'L25 angle: the ceiling perimeter divided by 4 (around the full wall).',
                      'Clips: one at every point where a panel-bearing and load-bearing profile cross — i.e. area divided by the product of the two spacings.',
                      'Hangers: based on hanger spacing along the load-bearing profile; e.g. one hanger every 120cm.',
                      "Waste: a few percent is usually added for cutting and breakage (the site's calculator defaults to 10%, and it's adjustable)."]),
              ('h2', 'Limitations'),
              ('p', "This method is an initial estimate. Ceiling height, openings, decorative ceilings, boxes, recessed lighting, and screws, nails and anchors aren't included. Our technical team determines the final quantity from the drawings."),
              ('p', 'For a quick calculation, use the site’s “Material Estimate” page.')]),
    'panel-screws-tn-tb': dict(
        title='TN & TB Panel Screws and LN & LB Structural Screws: Differences & Uses',
        desc='An introduction to drywall-system screws: self-tapping (TN) and self-drilling (TB) panel screws, structural screws (LN and LB), and nails & anchors, with the size and weight of each carton.',
        body=[('h2', 'Panel screws'),
              ('p', "Panel screws fix gypsum board to the substructure. Their design lets them drive in easily without tearing the board's paper facing, and the head doesn't raise a bump on the panel after filling. There are two types: self-tapping (TN) and self-drilling (TB)."),
              ('ul', ['TN 2.5 — 3.5×25 — 15 kg per carton.', 'TN 3.5 — 3.5×35 — 11 kg per carton.', 'TB 2.5 — self-drilling panel screw — 3.5-20×25 — 16 kg per carton.']),
              ('h2', 'Structural screws'),
              ('p', 'These screws join profiles to one another and to connectors, and come in self-tapping (LN) and self-drilling (LB) types.'),
              ('ul', ['LN 9 — 3.5×9 — 19 kg per carton.', 'LB 9.5 — 3.5-20×9.5 — 19 kg per carton.']),
              ('h2', 'Nails & anchors'),
              ('p', 'Used to fix the load-bearing component to the main structure above, or to fix the level frame to a wall or floor.'),
              ('p', 'The full table is on the “Profiles & Connectors” page.')]),
    'profile-thickness-05-06': dict(
        title='0.5mm or 0.6mm Thickness for F47, UH36 and L25 Profiles?',
        desc='The bundle-weight difference between F47, UH36 and L25 profiles at 0.5mm and 0.6mm thickness, and notes on choosing based on your project’s needs.',
        body=[('h2', 'Both thicknesses are manufactured'),
              ('p', 'F47, UH36 and L25 profiles are all available in two sheet thicknesses — 0.5mm and 0.6mm — with a standard 4-metre length.'),
              ('h2', 'The weight difference'),
              ('ul', ['F47 (400-piece bundle): about 580 kg at 0.5mm, 699 kg at 0.6mm.', 'UH36 (480-piece bundle): about 480 and 576 kg.', 'L25 (1000-piece bundle): about 688 and 820 kg.']),
              ('p', "So the 0.6mm thickness is roughly 20% heavier — meaning more steel in every piece."),
              ('h2', 'How to choose'),
              ('p', "The choice depends on ceiling height, covering weight, hanger spacing and project requirements, and the final call rests with the project's technical advisor."),
              ('p', 'Submit a “Request a Quote” for your project so our technical team can recommend the best thickness.')]),
    'false-ceiling-in-iran-buyers-guide': dict(
        title='Buying False-Ceiling Materials From a Manufacturer: What to Ask',
        desc='What to ask when buying profiles and false-ceiling materials: sheet thickness, length, packaging, weight, shipping and technical advice.',
        body=[('h2', 'Why buy from the manufacturer?'),
              ('p', 'Buying directly from the factory means clear, verifiable specifications, the option of custom lengths, and technical support during installation.'),
              ('h2', 'Questions to ask'),
              ('ul', ["What's the sheet thickness (0.5 or 0.6mm), and is it marked on the pack?", 'What length are the pieces, and are custom lengths possible?',
                      'How many pieces per pack and bundle, and roughly what weight?', 'Is the profile galvanized?', 'How is it packaged, and is it shipped to the project site?',
                      'Is technical advice and a material estimate provided?']),
              ('p', "To get started, enter your project's area on the “Material Estimate” page and send the result to our team.")]),
}

def build_articles_en():
    cards = ''.join('<a class="card hv pc rv" href="/en/articles/%s/">%s<div class="b"><h3>%s</h3><p>%s</p><span class="link">Read more</span></div></a>'
                     % (a['slug'], rimg(art_img(a), EN_ARTICLES[a['slug']]['title'], '(max-width:760px) 100vw, 33vw'), esc(EN_ARTICLES[a['slug']]['title']), esc(EN_ARTICLES[a['slug']]['desc'])) for a in ARTICLES)
    body = (phero('Articles & Guides', "Full documentation and step-by-step guidance on choosing, system components and technical notes for false ceilings and drywall — all based on the company's own catalog.",
                  [('/en/', 'Home'), (None, 'Articles')], lang='en') +
            '<section class="sec"><div class="wrap"><h2 class="sr">Article index</h2><div class="grid g3">%s</div></div></section>' % cards + cta(lang='en'))
    page('/en/articles/', 'Articles & Guides on False Ceilings and Drywall', 'AKH Ceiling Systems articles: choosing a false ceiling, grid-ceiling components, drywall profiles, screws, sheet thickness and material estimation.', body,
         crumbs=[('/en/', 'Home'), ('/en/articles/', 'Articles')], priority='0.8', freq='weekly', kind='CollectionPage',
         extra_ld=[{"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + '/en/articles/%s/' % a['slug'], "name": EN_ARTICLES[a['slug']]['title']} for i, a in enumerate(ARTICLES)]}], lang='en')
    add_doc('Articles (EN)', 'articles guides false ceiling drywall', '/en/articles/', 'page', 'article guide english')
    for a in ARTICLES:
        ea = EN_ARTICLES[a['slug']]
        url = SITE + '/en/articles/%s/' % a['slug']
        content, toc = art_html(ea['body'])
        tocbox = '<nav class="tocbox rv" aria-label="Table of contents"><b>In this article</b>%s</nav>' % ''.join('<a href="#%s">%s</a>' % t for t in toc) if len(toc) > 2 else ''
        others = [b for b in ARTICLES if b is not a][:3]
        rel = '<div class="rel rv">%s</div>' % ''.join('<a href="/en/articles/%s/">%s</a>' % (b['slug'], esc(EN_ARTICLES[b['slug']]['title'])) for b in others)
        prods = '<div class="rel rv">%s</div>' % ''.join('<a href="/en/products/%s/">%s</a>' % (q['slug'], EN_PRODUCT_NAME[q['slug']]) for q in ALLP[:3])
        body = (phero(ea['title'], ea['desc'], [('/en/', 'Home'), ('/en/articles/', 'Articles'), (None, 'Article')], lang='en') +
                '<section class="sec"><div class="wrap"><article class="art"><p class="note">Published: %s · about %s min read</p>%s%s<p class="row x15"><a class="btn" href="/en/estimate/">Material estimate</a><a class="btn line" href="/en/quote/">Request advice &amp; a quote</a></p><h2>Related products</h2>%s<h2>More articles</h2>%s</article></div></section>'
                % (FIRST_PUBLISHED, max(1, round(words(ea['body']) / 180)), tocbox, content, prods, rel))
        ld = {"@type": "Article", "@id": url + '#article', "headline": ea['title'], "description": ea['desc'], "inLanguage": "en-US", "datePublished": FIRST_PUBLISHED, "dateModified": TODAY, "wordCount": words(ea['body']),
              "image": [SITE + rurl(art_img(a), 1600)], "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}, "mainEntityOfPage": {"@id": url + '#webpage'}}
        page('/en/articles/%s/' % a['slug'], '%s | %s' % (ea['title'], EN_NAME), ea['desc'], body, extra_ld=[ld], article=True, kind='WebPage',
             crumbs=[('/en/', 'Home'), ('/en/articles/', 'Articles'), ('/en/articles/%s/' % a['slug'], ea['title'])], priority='0.7', images=[SITE + rurl(art_img(a), 1600)], lang='en')
        add_doc(ea['title'], ea['desc'] + ' ' + ' '.join(v if isinstance(v, str) else ' '.join(v) for t, v in ea['body']), '/en/articles/%s/' % a['slug'], 'page', 'article english')

# ============================================================ GLOSSARY
GLOSSARY_EN = [
    ('Drywall', 'A dry-construction system in which gypsum boards are fixed with screws to a lightweight metal frame; walls and ceilings go up fast and precisely, without wet materials like plaster.'),
    ('False ceiling', "A ceiling built at a distance below the building's actual ceiling, with the space above used for services and insulation."),
    ('F47 profile', 'The most widely used galvanized profile in the drywall system, serving as both the load-bearing and panel-bearing member. Its standard length is 4 metres.'),
    ('UH36 profile', 'A runner-type profile; typically used as a ceiling hanger and sometimes as framing around recessed-light edges and wall cladding.'),
    ('L25 angle', 'A 25×25 angle profile used to set the ceiling level and to frame boxes and recessed lighting.'),
    ('F47 clip', 'A galvanized connector that joins the load-bearing profiles to the F47 panel-bearing profile.'),
    ('Panel screw (TN / TB)', 'A screw for fixing gypsum board to the substructure; self-tapping (TN) and self-drilling (TB) types.'),
    ('60x60 grid ceiling', 'A false ceiling made of a grid of T-shaped bars, with 60×60 cm tiles resting on it; the tiles can be lifted out for access to services.'),
    ('Exposed / concealed T-bar', 'Two ways of installing a grid ceiling: with an exposed T-bar the bar edge is visible, while a concealed T-bar is covered by the tile.'),
    ('Mineral acoustic tile', 'A lightweight grid-ceiling tile with high sound absorption.'),
    ('Grillium (linear) ceiling', 'An open-mesh false ceiling made of aluminum profiles with a 5×5 or 10×10 cm cell, used for an open, modern look in commercial spaces.'),
    ('Recessed-light box', 'A recess or frame in a gypsum ceiling where a light source is hidden, creating indirect lighting.'),
    ('Galvanized', 'Steel protected with a zinc coating to resist corrosion — the material used for drywall profiles.'),
    ('Bundle', 'The bulk packaging unit for profiles; for example, each F47 bundle contains 400 pieces.'),
    ('Double-spring hanger', 'A grid-ceiling hanger system with two galvanized wires and an adjustable spring, for easy, stable height adjustment.'),
    ('Jointing / taping', 'Filling the joint between gypsum boards with tape and joint compound to create a single, seamless surface.'),
]

def build_glossary_en():
    dl = '<dl class="gl">%s</dl>' % ''.join(
        '<div class="glrow rv">%s<div><dt id="t%d">%s</dt><dd>%s</dd></div></div>' % (rimg(GLOSSARY_IMG[i], t, '84px'), i, esc(t), esc(d))
        for i, (t, d) in enumerate(GLOSSARY_EN))
    body = (phero('False Ceiling & Drywall Glossary', 'Plain-language definitions of common terms: F47, UH36, L25 profiles, T-bars, mineral tile, recessed-light boxes and more.', [('/en/', 'Home'), (None, 'Glossary')], lang='en') +
            '<section class="sec"><div class="wrap"><div class="art">%s</div></div></section>' % dl + cta(lang='en'))
    page('/en/glossary/', 'False Ceiling & Drywall Glossary | Term Definitions', 'Definitions of false-ceiling and drywall terms: drywall, F47, UH36, L25 profiles, clips, exposed and concealed T-bars, mineral tile, grillium ceilings, recessed-light boxes and galvanizing.', body,
         crumbs=[('/en/', 'Home'), ('/en/glossary/', 'Glossary')], priority='0.7', extra_ld=[{"@type": "DefinedTermSet", "@id": SITE + '/en/glossary/#terms', "name": "False ceiling and drywall glossary", "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t, "description": d, "url": SITE + '/en/glossary/#t%d' % i} for i, (t, d) in enumerate(GLOSSARY_EN)]}], lang='en')
    for i, (t, d) in enumerate(GLOSSARY_EN):
        add_doc(t, d, '/en/glossary/#t%d' % i, 'page', 'glossary english')

# ============================================================ FAQ
FAQ_HUB_EN = [
    ("What's the difference between F47 and UH36 profiles?", 'F47 is the most widely used drywall profile and serves as both the load-bearing and panel-bearing member. UH36 is a runner-type profile, typically used as a ceiling hanger and sometimes as framing around recessed-light edges.'),
    ("What's the standard profile length?", 'The standard length for F47, UH36 and L25 is 4 metres, and custom lengths are also available on request.'),
    ('What thicknesses are the profiles manufactured in?', 'All three profiles are manufactured in two sheet thicknesses: 0.5mm and 0.6mm.'),
    ('How many pieces are in each pack and bundle?', 'F47: 20 per pack, 400 per bundle. UH36: 24 per pack, 480 per bundle. L25: 20 per pack, 1000 per bundle.'),
    ('What does a profile bundle weigh, approximately?', 'F47 is about 580 kg (0.5mm) or 699 kg (0.6mm); UH36 about 480 and 576 kg; L25 about 688 and 820 kg.'),
    ('What spaces suit a 60x60 grid ceiling?', 'Office and commercial buildings, car parks, educational, healthcare and industrial facilities, and warehouses and halls — because it gives easy access to services and installs quickly.'),
    ('Which tile suits a damp space?', 'Moisture-resistant tiles such as aluminum, PVC or HPL are recommended; talk to our team for the exact specification.'),
    ("What's the difference between TN and TB panel screws?", 'TN is self-tapping and TB is self-drilling; both fix gypsum board to the substructure.'),
    ('Do you manufacture custom lengths?', 'Yes, custom lengths are available on request.'),
    ('Do you ship nationwide?', 'Yes, we ship across the whole country. Submit a quote request for lead time and cost.'),
    ('Where are your factory and office?', 'Head office: No. 202, corner of Havizeh St. & Ghanbarzadeh St., Beheshti St., Tehran. Factory: Shoorabad 60m St., Kahrizak.'),
    ('What are your business hours?', 'Saturday to Wednesday 9:00–17:00, and Thursday 9:00–13:00.'),
    ('Where can I get pricing?', 'Prices aren’t shown on the site. Submit a request on the “Request a Quote” page or ask the smart assistant, and our sales team will call you.'),
    ("What's the monthly production capacity?", 'Per our official company profile, production capacity is over 220 tonnes per month.'),
    ('Do you only sell materials, or do you also install?', 'For larger projects, our installation team also fits ceilings and partitions; contact our sales team to arrange the details.'),
    ('Do you export?', 'Yes — per our official company profile, we have exported to neighbouring countries including Afghanistan, Iraq and Armenia.'),
    ('Do you hold any certification or standard?', 'The company is a Grade-A certified member of the Iran Drywall Trade Association.'),
    ('Can I visit the factory?', 'The factory is in Kahrizak; you can arrange a visit with our sales team.'),
    ("What's the minimum order quantity?", 'The minimum order varies by item; contact our sales team for the exact figure for each product.'),
    ('Do you issue an official invoice?', 'For an official invoice and the financial details of your order, coordinate with our sales team.'),
    ('Can I get a sample before buying?', 'To receive a product sample, please coordinate with our sales team.'),
]

def build_faq_en():
    ask_bot = '<div class="row"><a class="btn" href="/en/assistant/">Ask the smart assistant</a></div>'
    body = (phero('Frequently Asked Questions', 'Short, accurate answers about profiles, ceilings, thickness and weight, shipping and business hours — or ask the smart assistant directly.', [('/en/', 'Home'), (None, 'FAQ')], ask_bot, lang='en') +
            '<section class="sec"><div class="wrap x10">%s</div></section>' % faq_html(FAQ_HUB_EN) + cta("Didn't find your answer?", 'Ask the smart assistant, or our team will call you.', lang='en'))
    page('/en/faq/', 'FAQ | Profiles, Grid Ceilings, Shipping', "Answers to common questions: the difference between F47 and UH36, profile thickness and weight, custom lengths, moisture-resistant tiles, nationwide shipping and business hours.", body,
         crumbs=[('/en/', 'Home'), ('/en/faq/', 'FAQ')], priority='0.8', extra_ld=[faq_node(FAQ_HUB_EN, SITE + '/en/faq/')], kind='WebPage', lang='en')
    for q, a in FAQ_HUB_EN:
        add_doc(q, a, '/en/faq/', 'page', 'faq english')

# ============================================================ CATALOGS
CATALOGS_EN = [
    ('f47', 'F47 Profile', 'Specifications and spec table for the most widely used drywall profile'),
    ('uh36', 'UH36 Profile', 'Runner-type framing; ceiling hanger and recessed lighting'),
    ('l25', 'L25 Angle', 'Ceiling level, boxed sections and recessed lighting'),
    ('connectors', 'Clips & Connectors', 'Clip, longitudinal joint connector, HT90, bracket and double-spring hanger'),
    ('runner-stud', 'Runner & Stud (Wall Framing)', 'Drywall partition framing; available in 50, 70 and 100 widths'),
    ('grid-60x60', '60x60 False Ceiling System', 'Grid ceiling, tile types and colour range'),
]

def build_catalogs_en():
    items = ''.join('<a class="card hv pc rv" href="/assets/catalog/%s-big.jpg" target="_blank" rel="noopener">%s<div class="b"><h3>%s</h3><p>%s</p><span class="link">View page</span></div></a>'
                     % (s, rimg('catalog/%s.jpg' % s, 'Catalog page: ' + t, '(max-width:760px) 100vw, 25vw'), t, d) for s, t, d in CATALOGS_EN)
    body = (phero('Catalogs', "The company's official catalog pages (in Persian); view each page here, or download the full catalog as a PDF.", [('/en/', 'Home'), (None, 'Catalogs')],
                  '<div class="row"><a class="btn" href="/assets/catalog/akh-catalog.pdf" download>Download full catalog (PDF)</a></div>', lang='en') +
            '<section class="sec"><div class="wrap"><h2 class="sr">Catalog pages</h2><div class="grid g3">%s</div></div></section>' % items + cta(lang='en'))
    page('/en/catalogs/', 'Product Catalogs | Download Profile & False Ceiling PDF', 'AKH Ceiling Systems official catalog: F47, UH36, L25 profiles, screws and connectors, decorative ceilings and the 60x60 grid ceiling. Free PDF download.', body,
         crumbs=[('/en/', 'Home'), ('/en/catalogs/', 'Catalogs')], priority='0.7', images=[SITE + rurl('catalog/%s.jpg' % s) for s, t, d in CATALOGS_EN],
         extra_ld=[{"@type": "DataDownload", "name": "Product catalog", "encodingFormat": "application/pdf", "contentUrl": SITE + '/assets/catalog/akh-catalog.pdf', "publisher": {"@id": ORG_ID}}], lang='en')
    add_doc('Catalogs (EN)', 'download catalog PDF F47 UH36 L25 screws connectors', '/en/catalogs/', 'page', 'catalog download english')

# ============================================================ PRIVACY
def build_privacy_en():
    collect = [('The "Request a Quote" and "Contact Us" forms', 'Name, phone number, city, company name (optional) and project description.'),
               ('Signing up for the customer panel', 'Name, email or mobile number, password (stored hashed, never as plain text), city, company name and job title (optional).'),
               ('Placing an order', 'Delivery address, required timing, and any files you upload for the order yourself (invoice or drawing).'),
               ('Visiting site pages', 'Only an anonymous page-view count is recorded; no tracking cookies and no IP address is stored.'),
               ('Security log', 'To prevent misuse and unauthorized access, request IP addresses and account activity history (such as sign-in times) are kept.')]
    use = ['Responding to quote or advisory requests through our sales team', 'Following up and completing submitted orders',
           'Preventing automated sign-ups and spam messages (bots)', 'Notifying you about the status of your order or account']
    protect = ["Passwords are hashed with a standard algorithm (scrypt); even our own staff can't see your password.", 'Two-factor authentication (2FA) can be enabled for your account.',
               'Uploaded files are checked and re-encoded before storage, so a malicious file is never stored.', "Access to customer data is limited to sales staff and the system administrator, strictly within their own role."]
    body = (phero('Privacy Policy', 'This page explains exactly what information we collect from you, why, and how it is protected.', [('/en/', 'Home'), (None, 'Privacy')], lang='en') +
            ('<section class="sec"><div class="wrap"><div class="split"><div>%s<h2>What information do we <em class="o">collect</em>?</h2><p class="lead">Only what you enter in our forms yourself; nothing is obtained from another source without your knowledge.</p></div>'
             '<div class="card pad"><ul class="checks x15">%s</ul></div></div></div></section>' % (kicker('01', 'Collection'), ''.join('<li><b>%s</b> — %s</li>' % (esc(t), d) for t, d in collect))) +
            ('<section class="sec paper2"><div class="wrap"><div class="split rev"><div>%s<h2>Why is this information <em class="o">used</em>?</h2><p class="lead">Your information is never sold or rented to a third party.</p></div>'
             '<div class="card pad"><ul class="checks x15">%s</ul></div></div></div></section>' % (kicker('02', 'Use'), ''.join('<li>%s</li>' % u for u in use))) +
            ('<section class="sec"><div class="wrap"><div class="split"><div>%s<h2>How is it <em class="o">protected</em>?</h2></div><div class="card pad"><ul class="checks x15">%s</ul></div></div></div></section>' % (kicker('03', 'Security'), ''.join('<li>%s</li>' % p for p in protect))) +
            ('<section class="sec paper2"><div class="wrap x10"><h2>Deleting or correcting your information</h2><p class="lead">Any time you want to delete or correct your account information, or find out what we hold about you, just email <a class="link" href="mailto:%s">%s</a> or call <a class="num" href="tel:+982188507585">%s</a>.</p></div></section>'
             % (EMAIL, EMAIL, PHONE)) + cta('Questions about privacy?', 'Get in touch with our team.', lang='en'))
    page('/en/privacy/', 'Privacy Policy | %s' % EN_NAME, 'AKH Ceiling Systems privacy policy: what information is collected, why, and how it is protected and retained.', body,
         crumbs=[('/en/', 'Home'), ('/en/privacy/', 'Privacy')], priority='0.3', lang='en')
    add_doc('Privacy (EN)', 'privacy policy data collection security customer information', '/en/privacy/', 'page', 'privacy english')
