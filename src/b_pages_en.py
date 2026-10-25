# -*- coding: utf-8 -*-
"""English counterparts of the Persian pages in b_pages.py (Phase 1 of the bilingual rollout).
Numeric / structural data always comes from content_base.py via the shared Persian lists (PROJECTS,
BIG_PROJECTS, MACHINES, PROFILE_TABLE, SCREW_TABLE, ...); only labels and prose are hand-translated here,
positionally paired with their Persian source so the two languages can never drift apart on the numbers."""
from b_core import *
from b_pages import ALLP, SYS_IMG, SYS_IMG_ALT_EN, EN_PRODUCT_NAME, EN_PRODUCT_SHORT, EN_PROJECT_NAMES, EN_PROJECT_SYS, EN_TAGS

_FA_DIGITS = '۰۱۲۳۴۵۶۷۸۹'
def latin(s):
    """Persian/Eastern-Arabic numerals -> Latin digits, same source string, no hand re-typed numbers.
    Also swaps the Persian conjunction embedded in figures like '0.5 و 0.6' (0.5 and 0.6)."""
    s = str(s)
    for i, d in enumerate(_FA_DIGITS):
        s = s.replace(d, str(i))
    return s.replace('٫', '.').replace('٬', ',').replace(' و ', ' and ')

plain = lambda s: s.replace('&amp;', '&')  # EN_PRODUCT_NAME is pre-HTML-escaped for raw use in markup; undo that for <title>/JSON-LD/plain-text contexts

# ============================================================ PRODUCTS (index)
def build_products_en():
    cards = ''
    for p in ALLP:
        tags = EN_TAGS.get(p['slug'], p['tags'])
        cards += ('<a class="card hv pc rv" href="/en/products/%s/">%s<div class="b"><h3>%s</h3><p>%s</p><div class="tags">%s</div></div></a>' %
                  (p['slug'], rimg(SYS_IMG[p['slug']], SYS_IMG_ALT_EN[p['slug']], '(max-width:760px) 100vw, 25vw'), EN_PRODUCT_NAME[p['slug']], EN_PRODUCT_SHORT[p['slug']], ''.join('<span class="tag">%s</span>' % t for t in tags)))
    body = (phero('Products', 'Two false-ceiling and partition systems, plus drywall profiles — all directly manufactured, with transparent technical specifications.', [('/en/', 'Home'), (None, 'Products')],
                  '<div class="row"><a class="btn" href="/en/estimate/">Material estimate</a><a class="btn line" href="/en/quote/">Request a quote</a></div>', lang='en') +
            '<section class="sec"><div class="wrap"><h2 class="sr">Our products</h2><div class="grid g4">%s</div></div></section>' % cards + cta(lang='en'))
    items = [{"@type": "ListItem", "position": i + 1, "url": SITE + '/en/products/%s/' % p['slug'], "name": plain(EN_PRODUCT_NAME[p['slug']])} for i, p in enumerate(ALLP)]
    page('/en/products/', 'Products | Drywall profiles & grid suspended ceilings', 'AKH Ceiling Systems products: the drywall system, 60x60 grid suspended ceilings, and F47, UH36 and L25 profiles, with full technical specifications.', body,
         extra_ld=[{"@type": "ItemList", "@id": SITE + '/en/products/#list', "itemListElement": items}], crumbs=[('/en/', 'Home'), ('/en/products/', 'Products')], priority='0.9', kind='CollectionPage',
         images=[SITE + rurl(SYS_IMG[p['slug']]) for p in ALLP], lang='en')
    add_doc('Products (EN)', 'drywall system 60x60 grid ceiling F47 UH36 L25 profiles', '/en/products/', 'page', 'products english')

# ============================================================ PRODUCT DETAIL
def profiles_table_en():
    names = ['F47', 'UH36', 'L25 angle']
    from content_base import PROFILE_TABLE
    rows = [[names[i]] + [latin(c) for c in row[1:]] for i, row in enumerate(PROFILE_TABLE)]
    return table_html(rows, ['Profile', 'Sheet thickness (mm)', 'Length (m)', 'Per pack', 'Per bundle', 'Approx. bundle weight (kg)']) + \
        '<p class="note">Weights are given for 0.5 mm and 0.6 mm thickness respectively (per the company’s official catalog table).</p>'

def screw_table_en():
    from content_base import SCREW_TABLE
    names = ['TN 2.5 panel screw', 'TN 3.5 panel screw', 'TB 2.5 self-drilling panel screw', 'LN 9 structural screw', 'LB 9.5 self-drilling structural screw']
    rows = [[names[i]] + [latin(c) for c in row[1:]] for i, row in enumerate(SCREW_TABLE)]
    return table_html(rows, ['Screw type', 'Size', 'Per carton', 'Weight (kg)'])

EN_CONTENT = {
    'drywall': dict(
        h1='Drywall system & plaster false ceilings',
        lead='A lightweight structure of galvanized steel profiles and gypsum board fixed with screws; once the joints are taped and finished, it gives a single seamless surface ready for paint or any architectural design.',
        desc="AKH Ceiling Systems' drywall (dry-construction) system and plaster false ceiling: a substructure and load-bearing frame in galvanized F47, UH36 and L25 profiles, gypsum board, connectors and screws, with full technical specifications and custom lengths on request.",
        about=['In this system, a galvanized steel frame (F47, UH36 and L25) is built to the drawing, and gypsum boards are fixed to it with dedicated panel screws. The joints between boards are taped and filled with joint compound, leaving a seamless surface that can be painted or finished with any other coating.',
               'Because the structure is light and the layout is standardised, material quantities can be calculated precisely and waste stays low. The cavity behind the ceiling is also available for services and for thermal or acoustic insulation.'],
        parts=['F47 profile (load-bearing and panel-bearing)', 'UH36 profile', 'L25 angle', 'F47 connector clip', 'F47 longitudinal joint connector (W)', 'HT90 connector and straight bracket', 'Steel double-spring hanger', 'Panel and structural screws, nails and anchors'],
        uses=['Flat ceiling', 'Boxed ceiling with recessed lighting', 'Decorative ceilings with steps and curves', 'Partition walls', 'Wall cladding', 'TV / LCD feature walls'],
        benefits=['Fast, straightforward installation', 'Lightweight structure', 'Precise material take-off and less waste', 'Room for thermal and acoustic insulation', 'Seamless surface ready for paint', 'High design flexibility'],
        boards=[('Standard board', 'For dry, general-purpose spaces'), ('Moisture-resistant board', 'For damp spaces such as bathrooms and kitchens'), ('Fire-resistant board', 'For spaces with fire-rating requirements')],
        faq=[("What's the difference between the F47 and UH36 profiles?", 'F47 is the most widely used drywall profile, serving as both the load-bearing and panel-bearing member. UH36 is a runner-type profile, typically used as a ceiling hanger and sometimes as the framing around recessed-light edges.'),
             ('Should I choose 0.5 mm or 0.6 mm thickness?', 'Both thicknesses are manufactured. The thicker sheet gives more strength and more weight; the right choice depends on height, load and project type. Our technical team can advise on the exact choice.'),
             ('Do you manufacture custom lengths?', 'Yes, custom lengths are available on request. The standard profile length is 4 metres.'),
             ('Do you ship nationwide?', 'Yes, we ship across the whole country. Submit a quote request for lead time and cost.')],
    ),
    'grid-ceiling': dict(
        h1='60x60 grid suspended ceiling',
        lead='A grid of T-shaped bars that carries the ceiling tiles. Fast to install, needs no painting, and gives easy access to everything above the ceiling.',
        desc="AKH Ceiling Systems' 60x60 and 30x60 grid suspended ceiling (Armstrong-style): exposed and concealed T-bar grids, gypsum, aluminum and mineral acoustic tiles, and steel double-spring hangers — suited to restrooms and office areas.",
        about=['This ceiling suits office and commercial buildings, car parks, educational and healthcare facilities, industrial sites, warehouses and halls. Its main advantages are ease of installation, no need for painting, and easy access to the services above.',
               'The frame consists of a wall angle, 3.6 m main T-bars, and 1.2 m and 0.6 m cross T-bars, with 60x60 cm tiles dropped into the resulting grid. Being lightweight also gives this ceiling better seismic safety.'],
        uses=['Office and commercial buildings', 'Educational facilities and universities', 'Healthcare facilities', 'Car parks and industrial spaces', 'Warehouses and halls'],
        benefits=['Easy access to everything above the ceiling', 'Fast installation', 'No painting required', 'Lightweight, with better seismic safety', 'Tile range from gypsum to aluminum and mineral acoustic', 'Exposed or concealed grid options'],
        tiles=[('Gypsum tile', 'Plain, PVC-faced, or PVC-faced with an aluminum backing for buildings at risk of leaks; acoustic perforated versions with regular or random patterns'),
               ('Aluminum tile', 'Plain or perforated in several patterns (centre-punched, fully punched, four-way or unpunched); installed with exposed or concealed grids'),
               ('Mineral acoustic tile', 'Lightweight with high sound absorption; available with square or bevelled edges (MT 100, MT 103 and MT 106 models)')],
        parts=['White L24 wall angle', 'Main, 1.2 m and 0.6 m T-bars (exposed and concealed)', 'Adjustable steel double-spring hanger', 'Hanger wire', 'Concrete and steel nails & anchors', 'Screws and connectors'],
        faq=[('Is an exposed or a concealed grid better?', 'An exposed grid is simpler to install and easier to access; a concealed grid gives a more seamless look. The right choice depends on the tile type and the design.'),
             ('Which tile suits damp spaces like restrooms?', 'For areas exposed to water or high humidity, moisture-resistant tiles such as aluminum, PVC or HPL are recommended. Talk to our team for the exact specification.'),
             ('Which tile is best for sound absorption?', 'Mineral acoustic tiles and perforated acoustic gypsum tiles are designed specifically for sound control.')],
    ),
    'profiles': dict(
        h1='Drywall profiles & connectors',
        lead="Galvanized F47, UH36 and L25 profiles together with clips, connectors and installation screws; with the company's official specification table.",
        desc='F47, UH36 and L25 galvanized profiles — the substructure and load-bearing frame for the drywall system — plus clips, connectors and screws, with a full technical specification table from AKH Ceiling Systems.',
        about=['The galvanized F47, UH36 and L25 profiles form the main frame of the drywall system and the plaster false ceiling. All three are manufactured in 0.5 mm and 0.6 mm sheet thickness, in a standard 4-metre length, and supplied in defined packs and bundles.',
               'Alongside the profiles, we also manufacture and supply clips, connectors, the HT90 piece, brackets, double-spring hangers, and the full range of screws, nails and anchors, so the entire substructure can be sourced from one place.'],
        uses=['Substructure for a seamless plaster ceiling', 'Substructure for partition and cladding walls', 'Boxed ceilings and recessed lighting', 'Setting ceiling level with the wall angle', 'Connecting the frame to the main structure'],
        benefits=['Galvanized and corrosion-resistant', 'Standard 4 m length, custom lengths available', '0.5 mm and 0.6 mm thicknesses', '20- and 24-piece packs plus bundles', 'Manufactured directly at our Kahrizak factory'],
        faq=[("What's the difference between F47 and UH36?", 'F47 is the most widely used drywall profile, used as both the load-bearing and panel-bearing member. UH36 is a runner profile, typically used as a ceiling hanger.'),
             ('0.5 mm or 0.6 mm — which should I choose?', 'Both thicknesses are available; the thicker sheet is stronger and heavier. The right choice depends on your project — ask our technical team.'),
             ('How many pieces are in a pack and a bundle?', 'F47: 20 per pack, 400 per bundle. UH36: 24 per pack, 480 per bundle. L25: 20 per pack, 1000 per bundle.'),
             ('What does a bundle weigh?', 'F47 is about 580 kg (0.5 mm) or 699 kg (0.6 mm); UH36 about 480/576 kg; L25 about 688/820 kg.'),
             ('Do you manufacture custom lengths?', 'Yes — the standard length is 4 metres, and custom lengths are available on request.'),
             ("What's the difference between TN and TB panel screws?", 'TN is self-tapping with a sharp point; TB is self-drilling. Both fix gypsum board to the substructure.')],
    ),
    'accessories': dict(
        h1='Installation accessories for false ceilings & drywall',
        lead='Screws, nails and anchors, joint tape and connectors needed to install both false-ceiling systems — drywall and grid.',
        desc='AKH Ceiling Systems installation accessories: SSB structural and panel screws, concrete and steel nails & anchors, joint tape, W-connectors, HT90 hangers and brackets.',
        about=['Alongside profiles and tiles, every false-ceiling project needs a set of small installation parts: screws to fix boards and the frame, nails and anchors to hang the frame from the structure above, joint tape to make the joints seamless, and connectors to join profiles together.',
               'These parts are normally supplied together with the main order (profiles, tiles or frame) so installation can proceed without interruption.'],
        uses=['Installing drywall ceilings and walls', 'Installing a 60x60 grid ceiling', 'Fixing to concrete or steel structures'],
        benefits=['Supplied together with the main order', 'SSB brand screws (Taiwan), a recognised name', 'Stock available for immediate delivery', 'Suitable for both concrete and steel fixing'],
        faq=[('What brand are the structural and panel screws?', 'SSB, made in Taiwan, available for immediate delivery.'),
             ('What nail do I need for a concrete ceiling?', 'A concrete nail and anchor. For steel structures, use the steel nail and anchor.'),
             ('What is the joint tape used for?', 'To cover and reinforce the joints between gypsum boards, before filling and final paint.')],
    ),
}

HOWTO_EN = {
    'drywall': ('Installing a drywall ceiling (overview)', ['Mark the ceiling level and fix the L25 angle around the perimeter of the wall.', 'Fix hangers to the main structure above and rest the load-bearing profiles on them.',
                'Clip the panel-bearing F47 profiles to the load-bearing profiles.', 'Run services and insulation (if needed) before closing the ceiling.', 'Fix the gypsum boards to the frame with panel screws.',
                'Tape and fill the joints, then apply paint or the final finish.']),
    'grid-ceiling': ('Installing a grid ceiling (overview)', ['Mark the ceiling level and fix the wall angle around the perimeter.', 'Fix double-spring hangers to the main structure at set intervals.',
                     'Rest the main T-bars on the hangers and level them.', 'Clip in the 1.2 m and 0.6 m cross T-bars to complete the 60x60 grid.', 'Drop the tiles into the grid.']),
}
GRID_TILES_EN = [('PVC-coated colour gypsum tile', 'Coloured PVC facing with an aluminum backing, in more than 36 colours and patterns. 595x595 mm, 7 mm thick.'),
                  ('Wicker-pattern PVC gypsum tile', 'White wicker pattern, in standard and moisture/fire-resistant (WFR) versions. 595x595 mm, 7 mm thick.'),
                  ('Plain PVC gypsum tile', 'The plain, always-in-stock pattern from the PVC-faced gypsum tile range.'),
                  ('Regular/irregular perforated tile', 'PVC-faced gypsum tile with regular or irregular perforations, fire- and moisture-resistant; 7 mm and 9 mm thick.'),
                  ('Square-punch tile', 'Tile with a square punch pattern for varied designs.'),
                  ('Mineral acoustic tile', '15 mm thick, in more than 7 patterns, with square or bevelled edges; suited to meeting rooms and auditoriums.'),
                  ('Aluminum tile', 'Electrostatic powder coating, 0.5 and 0.6 mm thick; suited to food industry, laboratory and industrial-kitchen use.'),
                  ('Fully / centre-punched aluminum tile', '595x595 mm, white or silver; 3105 H16 aluminum sheet, 0.6 and 0.7 mm thick.')]
GRID_TBARS_EN = [('Exposed T-bar', '60x60 wide-flange with white baked enamel and standard click fit.'), ('Concealed T-bar', 'White concealed-frame system; includes 3.6 m, 1.2 m and 0.6 m T-bars and the L24 angle.'),
                  ('Three-colour T-bar', '3.6 m, 1.2 m and 0.6 m T-bars and angle, in white, silver and black.')]
CONNECTORS_EN = [('F47 connector clip', 'A galvanized connector that joins the load-bearing profiles to the F47 panel-bearing profile.'), ('F47 longitudinal joint connector (W)', 'Joins two F47 profiles end to end to extend the frame.'),
                  ('HT90 connector', 'Connects the frame profile to the main structure above.'), ('Direct connector (bracket)', 'Connects the hanger to the load-bearing profile frame.'),
                  ('Adjustable double-spring steel hanger', 'The modular grid-ceiling hanger mechanism: two galvanized wires and an adjustable spring for stable, easy height adjustment.')]
PROFILE_ROLES_EN = [('F47', 'The most widely used drywall profile; load-bearing and panel-bearing. Its accuracy directly affects panel fit and clip placement.'),
                     ('UH36', 'A runner-type profile; typically used as a ceiling hanger and sometimes as framing around recessed-light edges and wall cladding.'),
                     ('L25', 'A 25x25 angle; sets the ceiling level and frames boxes and recessed lighting. Other profiles rest on it.')]
NAIL_TYPES_EN = [('Concrete nail & anchor', 'For fixing hangers and angles to a concrete ceiling or wall.'), ('Steel nail & anchor', 'For fixing to steel structures and framework.')]
JOINT_TAPE_DESC_EN = 'Galvanized joint tape (made in Taiwan) for covering and reinforcing gypsum board joints, before filling and final painting.'
SCREW_BRAND_NOTE_EN = 'Structural screws (LN and LB) and panel screws (TN and TB) are SSB brand, made in Taiwan, available for immediate delivery.'
REAL_GALLERY_EN = {'drywall': [('show/d1.jpg', 'Boxed drywall ceiling with recessed lighting — a real installed project')],
                    'grid-ceiling': [('show/g3.jpg', 'Circular grid ceiling with a centre tile and recessed lighting'), ('show/p02.jpg', 'Grid ceiling with perforated tiles in an industrial space'),
                                      ('photos/real-ceiling.jpg', 'The AKH Ceiling Systems team installing the ceiling frame')]}
ABOUT_HEAD_EN = {'drywall': ('Why', 'drywall?'), 'grid-ceiling': ('How a', 'grid ceiling is built'), 'profiles': ('Introducing', 'the profiles &amp; connectors'), 'accessories': ('Where', 'these parts are used')}

def product_ld_en(p, url, d):
    props = []
    if p['slug'] in ('drywall', 'profiles'):
        props = [("Standard length", "4 m"), ("Sheet thickness", "0.5 and 0.6 mm"), ("Material", "Galvanized steel")]
    elif p['slug'] == 'grid-ceiling':
        props = [("Tile size", "60x60 cm"), ("Main T-bar length", "3.6 m"), ("Hanger", "Steel double-spring")]
    return {"@type": "Product", "@id": url + '#product', "name": plain(EN_PRODUCT_NAME[p['slug']]), "description": d, "image": [SITE + rurl(SYS_IMG[p['slug']], 960)], "url": url,
            "brand": {"@type": "Brand", "name": "A.K.H"}, "manufacturer": {"@id": ORG_ID}, "category": "Building materials / suspended ceilings and drywall", "countryOfOrigin": {"@type": "Country", "name": "Iran"},
            "additionalProperty": [{"@type": "PropertyValue", "name": a, "value": b} for a, b in props]}

def build_product_en(p):
    slug = p['slug']; url = SITE + '/en/products/%s/' % slug
    d = EN_CONTENT[slug]; crumbs = [('/en/', 'Home'), ('/en/products/', 'Products'), ('/en/products/%s/' % slug, EN_PRODUCT_NAME[slug])]
    ab = ''.join('<p class="lead x7">%s</p>' % t for t in d['about'])
    lists = ''
    for title, key in (('Uses', 'uses'), ('Benefits', 'benefits'), ('Parts & components', 'parts')):
        if key in d:
            lists += '<div class="card pad rv"><h3>%s</h3><ul class="checks x8">%s</ul></div>' % (title, ''.join('<li>%s</li>' % x for x in d[key]))
    BOARD_IMG = {'Standard board': 'mat/board-normal.jpg', 'Moisture-resistant board': 'mat/board-moisture.jpg', 'Fire-resistant board': 'mat/board-fire.jpg'}
    TILE_FAMILY_IMG = {'Gypsum tile': 'mat/tile-gypsum.jpg', 'Aluminum tile': 'mat/tile-aluminum.jpg', 'Mineral acoustic tile': 'mat/tile-acoustic.jpg'}
    GRID_TILE_IMG = {'PVC-coated colour gypsum tile': 'mat/tile-pvc-color.jpg', 'Wicker-pattern PVC gypsum tile': 'mat/tile-wicker.jpg', 'Plain PVC gypsum tile': 'mat/tile-pvc-plain.jpg',
                      'Regular/irregular perforated tile': 'mat/tile-perforated.jpg', 'Square-punch tile': 'mat/tile-punch-square.jpg', 'Mineral acoustic tile': 'mat/tile-acoustic.jpg',
                      'Aluminum tile': 'mat/tile-aluminum.jpg', 'Fully / centre-punched aluminum tile': 'mat/tile-aluminum.jpg'}
    TBAR_IMG = {'Exposed T-bar': 'mat/tbar-exposed.jpg', 'Concealed T-bar': 'mat/tbar-concealed.jpg', 'Three-colour T-bar': 'mat/tbar-tricolor.jpg'}
    extra = ''
    if slug == 'drywall':
        boards = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(BOARD_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in d['boards'])
        extra = ('<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>Galvanized <em class="o">profile specifications</em></h2></div>%s<p class="x9"><a class="link" href="/en/products/profiles/">Connectors, screws and a breakdown of each profile</a></p></div></section>'
                 '<section class="sec"><div class="wrap">%s<div class="head"><h2>Three types of <em class="o">gypsum board</em></h2></div><div class="grid g3">%s</div></div></section>' % (kicker('02', 'Spec table'), profiles_table_en(), kicker('03', 'Gypsum boards'), boards))
    elif slug == 'grid-ceiling':
        tiles = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(TILE_FAMILY_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in d['tiles'])
        gt = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(GRID_TILE_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in GRID_TILES_EN)
        gb = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(TBAR_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in GRID_TBARS_EN)
        extra = ('<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>Three tile <em class="o">families</em></h2></div><div class="grid g3">%s</div></div></section>'
                 '<section class="sec"><div class="wrap">%s<div class="head"><h2>Detailed <em class="o">tile models</em></h2><p class="lead">Technical specifications for each model; the final choice depends on the space, budget and moisture/acoustic needs — ask our technical team.</p></div><div class="grid g3">%s</div></div></section>'
                 '<section class="sec paper2"><div class="wrap">%s<div class="head"><h2><em class="o">T-bar</em> options</h2></div><div class="grid g3">%s</div></div></section>'
                 % (kicker('02', 'Tiles'), tiles, kicker('03', 'Tile models'), gt, kicker('04', 'T-bars'), gb))
    elif slug == 'profiles':
        PROFILE_IMG = {'F47': 'parts/profile-f47.jpg', 'UH36': 'parts/profile-uh36.jpg', 'L25': 'parts/profile-l25.jpg'}
        roles = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(PROFILE_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in PROFILE_ROLES_EN)
        conn = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(CONNECTORS_IMG[i], a, '(max-width:760px) 50vw, 25vw'), a, b) for i, (a, b) in enumerate(CONNECTORS_EN))
        sc = screw_table_en()
        extra = ('<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>The role of each <em class="o">profile</em></h2></div><div class="grid g3">%s</div><div class="x11">%s</div></div></section>'
                 '<section class="sec"><div class="wrap">%s<div class="head"><h2>Clips &amp; <em class="o">connectors</em></h2></div><div class="grid g3">%s</div></div></section>'
                 '<section class="sec paper2"><div class="wrap">%s<div class="split"><div><div class="head"><h2>Screws, <em class="o">nails &amp; anchors</em></h2><p class="lead">Panel screws (self-tapping TN and self-drilling TB) fix gypsum board to the substructure; structural screws (LN and LB) join the profiles together.</p></div>%s</div><div class="fig rv">%s</div></div></div></section>'
                 % (kicker('02', 'Profiles'), roles, profiles_table_en(), kicker('03', 'Connectors'), conn, kicker('04', 'Screws'), sc, rimg('mat/screws.jpg', 'Panel and structural screws for the drywall system', '(max-width:1100px) 100vw, 45vw')))
    elif slug == 'accessories':
        sc2 = screw_table_en()
        NAIL_IMG = {'Concrete nail & anchor': 'mat/nail-concrete.jpg', 'Steel nail & anchor': 'mat/nail-iron.jpg'}
        nails = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(NAIL_IMG[a], a, '(max-width:760px) 50vw, 25vw'), a, b) for a, b in NAIL_TYPES_EN)
        conn2 = ''.join('<div class="card pad">%s<h3 class="x4">%s</h3><p class="lead">%s</p></div>' % (rimg(CONNECTORS_IMG[i], a, '(max-width:760px) 50vw, 25vw'), a, b) for i, (a, b) in enumerate(CONNECTORS_EN))
        extra = ('<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>Structural &amp; <em class="o">panel screws</em></h2><p class="lead">%s</p></div>%s</div></section>'
                 '<section class="sec"><div class="wrap">%s<div class="head"><h2>Nails &amp; <em class="o">anchors</em></h2></div><div class="grid g3">%s</div></div></section>'
                 '<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>Joint <em class="o">tape</em></h2><p class="lead">%s</p></div></div></section>'
                 '<section class="sec"><div class="wrap">%s<div class="head"><h2>Connectors &amp; <em class="o">hangers</em></h2></div><div class="grid g3">%s</div></div></section>'
                 % (kicker('02', 'Screws'), SCREW_BRAND_NOTE_EN, sc2, kicker('03', 'Nails & anchors'), nails, kicker('04', 'Joint tape'), JOINT_TAPE_DESC_EN, kicker('05', 'Connectors'), conn2))
    howto = ''
    ld_extra = [product_ld_en(p, url, d['desc'])]
    if slug in HOWTO_EN:
        ht, steps = HOWTO_EN[slug]
        howto_num = {'profiles': '05', 'grid-ceiling': '05'}.get(slug, '04')
        howto = ('<section class="sec"><div class="wrap"><div class="split"><div>%s<h2>%s</h2><p class="note">A general overview; actual installation must follow the project drawings and technical instructions.</p></div><ol class="steps2 x12">%s</ol></div></div></section>' %
                 (kicker(howto_num, 'Installation'), ht, ''.join('<li>%s</li>' % s for s in steps)))
        ld_extra.append({"@type": "HowTo", "@id": url + '#howto', "name": ht, "step": [{"@type": "HowToStep", "position": i + 1, "text": s} for i, s in enumerate(steps)]})
    faq = d.get('faq') or []
    faq_sec = ''
    if faq:
        faq_sec = '<section class="sec"><div class="wrap"><div class="split">%s%s</div></div></section>' % ('<div>' + kicker('FAQ', 'Questions') + '<h2>Frequently asked questions</h2></div>', faq_html(faq))
        ld_extra.append(faq_node(faq, url))
    gallery = ''
    rg = REAL_GALLERY_EN.get(slug)
    if rg:
        rg_num, rg_cls = {'drywall': ('05', ' paper2'), 'grid-ceiling': ('06', ' paper2')}[slug]
        gallery += ('<section class="sec%s"><div class="wrap">%s<div class="head"><h2>Real <em class="o">installed examples</em></h2><p class="lead">Real photos of ceilings installed with this system.</p></div><div class="grid g3">%s</div></div></section>' %
                    (rg_cls, kicker(rg_num, 'Case photos'), ''.join('<figure class="card">%s<figcaption class="pad x13">%s</figcaption></figure>' % (rimg(r, t, '(max-width:760px) 100vw, 30vw'), t) for r, t in rg)))
    others = '<div class="rel">%s</div>' % ''.join('<a href="/en/products/%s/">%s</a>' % (q['slug'], EN_PRODUCT_NAME[q['slug']]) for q in ALLP if q['slug'] != slug)
    ah1, ah2 = ABOUT_HEAD_EN.get(slug, ('About', 'this system'))
    main = ('<section class="sec"><div class="wrap"><div class="split"><div>%s<h2>%s <em class="o">%s</em></h2>%s</div><div class="fig rv">%s</div></div></div></section>' % (kicker('01', 'Overview'), ah1, ah2, ab, rimg(SYS_IMG[slug], SYS_IMG_ALT_EN[slug], '(max-width:1100px) 100vw, 45vw')))
    diag = ('<section class="sec sm"><div class="wrap"><div class="dgwrap card pad rv">%s</div></div></section>' % diagram(p['diagram'], lang='en')) if p.get('diagram') else ''
    feats = '<section class="sec sm"><div class="wrap"><div class="grid g3">%s</div></div></section>' % lists
    related = '<section class="sec sm"><div class="wrap"><h2 class="x14">Related products</h2>%s</div></section>' % others
    body = (phero(d['h1'], d['lead'], crumbs, '<div class="row"><a class="btn" href="/en/quote/?p=%s">Request a quote</a><a class="btn line" href="/en/estimate/">Material estimate</a></div>' % slug.replace('-ceiling', ''), lang='en') + main + diag + feats + extra + howto + gallery + faq_sec + related + cta(lang='en'))
    page('/en/products/%s/' % slug, '%s | %s' % (plain(EN_PRODUCT_NAME[slug]), EN_NAME), d['desc'], body, extra_ld=ld_extra, crumbs=crumbs, priority='0.9', images=[SITE + rurl(SYS_IMG[slug])], lang='en')
    add_doc(plain(EN_PRODUCT_NAME[slug]), d['lead'] + ' ' + ' '.join(d['about']), '/en/products/%s/' % slug, 'page', ' '.join(EN_TAGS.get(slug, p['tags'])))
    for q, a in faq:
        add_doc(q, a, '/en/products/%s/' % slug, 'page', plain(EN_PRODUCT_NAME[slug]))

# ============================================================ PROJECTS
EN_BIG_PROJECTS = [('Mahan Park project, Karaj', 'Paydar Haram Pars Co.'), ('Baran 4 project', 'Tadbir Sazeh Barsava'), ('Protocol building', 'Eng. Sadoughi'), ('Akhavan Sink factory', 'Eng. Zolmajnein'),
                    ('Aftab Tower, Mashhad', 'Tadbir Sazeh Co.'), ('Baga building', 'Beh Afra Gostar Arvand Co.'), ('Mahya Protein factory', 'Eng. Bastam'), ('Salarzadeh project', 'Eng. Salarzad'),
                    ('Shahre Rey University', 'Shahre Rey University Engineering Dept.'), ('Orchid Restaurant, Niavaran', 'Eng. Liaghati')]
EN_GALLERY_CAPS = ['Material delivery to the project site', 'Preparing and moving materials', 'Installing the false ceiling', 'Building the ceiling frame', "AKH's own drywall profiles",
                    'The installation team at work', 'Fitting drywall boards', 'Building the ceiling frame', 'Coordinating work on site', 'Moving a drywall board', 'Teamwork at height', 'Installing the ceiling at height']

def build_projects_en():
    from content_base import PROJECTS, BIG_PROJECTS, GALLERY_CAPS
    pl = ''.join('<a href="#p%d"><span class="n">0%d</span><h3>%s</h3><span>%s</span>%s</a>' % (i + 1, i + 1, esc(EN_PROJECT_NAMES[i]), esc(EN_PROJECT_SYS[i]), rimg('projects/' + f, EN_PROJECT_NAMES[i], '130px', '', w=130, h=84)) for i, (f, t, s) in enumerate(PROJECTS))
    big = ''.join('<a class="gi" href="/assets/cards/c%d-big.jpg" data-cap="%s — client: %s — area: %s m²">%s<span>%s<small>%s m²</small></span></a>' % (n, esc(name), esc(emp), latin(ar), rimg('cards/c%d.jpg' % n, '%s, client %s, area %s m²' % (name, emp, latin(ar)), '(max-width:760px) 50vw, 20vw', w=560, h=840), esc(name), latin(ar)) for (n, _, _, ar), (name, emp) in zip(BIG_PROJECTS, EN_BIG_PROJECTS))
    gal = ''.join('<a class="gi" href="/assets/gallery/g%02d.jpg" data-cap="%s">%s<span>%s</span></a>' % (n, c, rimg('gallery/t%02d.jpg' % n, c + ' — Mahan Park project', '(max-width:760px) 50vw, 25vw'), c) for n, c in enumerate(EN_GALLERY_CAPS, 1))
    gal4 = ''.join('<a class="gi" href="/assets/r/projects-%s-1600.webp" data-cap="%s — %s">%s<span>%s<small>%s</small></span></a>' % (f.rsplit('.', 1)[0], esc(EN_PROJECT_NAMES[i]), esc(EN_PROJECT_SYS[i]), rimg('projects/' + f, '%s — %s' % (EN_PROJECT_NAMES[i], EN_PROJECT_SYS[i]), '(max-width:760px) 50vw, 25vw'), esc(EN_PROJECT_NAMES[i]), esc(EN_PROJECT_SYS[i])) for i, (f, t, s) in enumerate(PROJECTS))
    body = (phero('Projects', "A selection of projects built with AKH Ceiling Systems' materials and experience.", [('/en/', 'Home'), (None, 'Projects')], lang='en') +
            '<section class="sec"><div class="wrap">%s<div class="head"><h2>Completed <em class="o">ceilings</em></h2></div><div class="gal" data-lb>%s</div></div></section>' % (kicker('01', 'Gallery'), gal4) +
            '<section class="sec paper2"><div class="wrap">%s<div class="head"><h2>Major projects &amp; <em class="o">installed area</em></h2><p class="lead">A list of flagship projects with client and area, per the company’s official profile.</p></div><div class="bigp" data-lb>%s</div></div></section>' % (kicker('02', 'Flagship projects'), big) +
            '<section class="sec"><div class="wrap">%s<div class="head"><h2>On site at <em class="o">Mahan Park</em></h2><p class="lead">Real photos of our installation team fitting the ceiling and partitions.</p></div><div class="gal" data-lb>%s</div></div></section>' % (kicker('03', 'On site'), gal) + cta('Your project could be next', "Tell us the project type and we'll suggest the best system.", lang='en'))
    items = [{"@type": "ImageObject", "contentUrl": SITE + rurl('projects/' + f, 1600), "name": EN_PROJECT_NAMES[i], "caption": '%s — %s' % (EN_PROJECT_NAMES[i], EN_PROJECT_SYS[i]), "creator": {"@id": ORG_ID}} for i, (f, t, s) in enumerate(PROJECTS)]
    page('/en/projects/', 'Completed Projects | Universities, Hotels, Commercial & Industrial', 'False-ceiling and drywall projects built with AKH Ceiling Systems materials: Hotel Azadi, Shahre Rey University, the Oil Industry University, Telecom, the 73,000 m² Mahan Park project and more.', body,
         extra_ld=[{"@type": "ImageGallery", "@id": SITE + '/en/projects/#gallery', "name": "Completed projects", "associatedMedia": items}], crumbs=[('/en/', 'Home'), ('/en/projects/', 'Projects')], priority='0.8', kind='CollectionPage',
         images=[SITE + rurl('projects/' + f, 1600) for f, t, s in PROJECTS], lang='en', scripts=('gallery.js',))
    add_doc('Projects (EN)', 'completed projects Hotel Azadi Shahre Rey University Mahan Park', '/en/projects/', 'page', 'projects portfolio')

# ============================================================ ABOUT
EN_COMPANY_FACTS = ["Operating since 1983 under the name 'Faegh Rooz', specialising in drywall profiles and false-ceiling/partition framework since 2009",
                     'Production capacity of over 220 tonnes per month, with a distribution network across Iran', 'Exports to neighbouring countries including Afghanistan, Iraq and Armenia',
                     'Grade-A certified member of the Iran Drywall Trade Association', 'Company registration number: 352685']
EN_MACHINES_NAMES = ['F47 profile line', 'U36 profile line', 'L25 profile line', 'T3.6 profile line', 'T1.2 profile line', 'T0.6 profile line', 'L24 profile line',
                      'STUD wall-profile line', 'RUNNER wall-profile line', '60-tonne press', '40-tonne press']

def build_about_en():
    from content_base import MACHINES
    facts_li = ''.join('<li>%s</li>' % f for f in EN_COMPANY_FACTS)
    mach = table_html([[EN_MACHINES_NAMES[i], latin(c), latin(cap).replace('تن', 'tonnes')] for i, (_, c, cap) in enumerate(MACHINES)], ['Machine', 'Count', 'Daily capacity'])
    body = (phero('About Us', '%s — manufacturer of false-ceiling, partition and drywall-system materials.' % EN_NAME, [('/en/', 'Home'), (None, 'About Us')], lang='en') +
            '<section class="sec"><div class="wrap"><div class="split"><div>%s<h2>Four decades working with <em class="o">steel, aluminum and gypsum</em></h2><p class="lead x7">AKH Ceiling Systems has over 40 years of experience in the construction industry, manufacturing false-ceiling materials and drywall systems, and is today one of the established manufacturers in this field in Iran.</p>'
            '<p class="lead">Quality is not a slogan for us; it is controlled from raw-material selection through to the finished product on the line, and profiles are packed in 20-piece bundles ready for loading.</p></div><div class="fig rv">%s</div></div></div></section>' % (kicker('01', 'Our story'), rimg('photos/real-factory.jpg', 'Profiles manufactured at our factory', '(max-width:1100px) 100vw, 45vw')) +
            '<section class="sec paper2"><div class="wrap">%s<div class="split"><div><h2>Production lines &amp; <em class="o">equipment</em></h2><ul class="checks x15">%s</ul></div><div>%s<p class="note">Per the company’s machinery and equipment list.</p></div></div></div></section>' % (kicker('02', 'Production capacity'), facts_li, mach) +
            '<section class="sec"><div class="wrap"><div class="split rev"><div>%s<h2>Packing &amp; <em class="o">nationwide delivery</em></h2><p class="lead">Once manufactured, materials are packed and prepared for shipment to the project; our team stays with you through final delivery.</p></div><div class="fig rv">%s</div></div></div></section>' % (kicker('03', 'Delivery'), rimg('photos/real-delivery.jpg', 'Delivering materials to a project by the AKH Ceiling Systems team', '(max-width:1100px) 100vw, 45vw')) +
            '<section class="sec paper2"><div class="wrap"><div class="split"><div>%s<h2>With our customers &amp; <em class="o">contractors</em></h2><p class="lead">We regularly take part in specialist construction trade shows, to present our products in person and hear what projects need.</p></div><div class="fig rv">%s</div></div></div></section>' % (kicker('04', 'Trade shows'), rimg('photos/real-expo.jpg', 'Our stand at the Midex trade show', '(max-width:1100px) 100vw, 45vw')) + cta(lang='en'))
    page('/en/about/', 'About Us | %s' % EN_NAME, 'AKH Ceiling Systems has over 40 years of experience; production capacity of over 220 tonnes per month, 11 production and press lines, our Kahrizak factory and Tehran head office.', body,
         crumbs=[('/en/', 'Home'), ('/en/about/', 'About Us')], kind='AboutPage', priority='0.7', images=[SITE + rurl('photos/real-factory.jpg')], lang='en')
    add_doc('About Us (EN)', ' '.join(EN_COMPANY_FACTS), '/en/about/', 'page', 'company history production capacity')

# ============================================================ CONTACT
def build_contact_en():
    maps_q = 'Tehran+Beheshti+Ghanbarzadeh+Havizeh+202'
    maps = 'https://www.google.com/maps/search/?api=1&query=' + maps_q
    maps_embed = 'https://maps.google.com/maps?q=' + maps_q + '&output=embed'
    body = (phero('Contact Us', 'Get in touch for technical advice, a quote, or to arrange a factory visit.', [('/en/', 'Home'), (None, 'Contact Us')], lang='en') +
            '<section class="sec"><div class="wrap"><div class="grid g2"><div class="card pad"><h2>Head office</h2><ul class="checks x8"><li>%s</li><li>Phone: <a class="num" href="tel:+982188507585">%s</a> (10 lines)</li><li>Mobile: <a class="num" href="tel:+989124968761">%s</a></li><li>Email: <a class="num" href="mailto:%s">%s</a></li><li>%s</li><li>%s</li></ul><p class="x16"><a class="link" href="%s" rel="noopener">Get directions</a></p></div>'
            '<div class="card pad"><h2>Factory</h2><ul class="checks x8"><li>%s</li><li>Phone: <a class="num" href="tel:+982156548804">%s</a></li></ul><p class="row x16"><a class="btn sm" href="https://t.me/%s" rel="noopener">Telegram</a><a class="btn sm line" href="https://instagram.com/%s" rel="noopener">Instagram</a></p></div></div>'
            '<div class="mapwrap card rv"><iframe src="%s" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Head office map, %s"></iframe></div>'
            '<div class="cta rv x17"><div><h2>Request a quote online</h2><p>Tell us about your project and our team will get in touch.</p></div><div class="row"><a class="btn" href="/en/quote/">Submit a request</a></div></div></div></section>'
            % (ADDR_OFFICE_EN, PHONE, MOBILE, EMAIL, EMAIL, HOURS_EN[0], HOURS_EN[1], maps, ADDR_FACTORY_EN, PHONE_FACTORY, TELEGRAM, INSTAGRAM, maps_embed, esc(EN_NAME)))
    page('/en/contact/', 'Contact Us | %s' % EN_NAME, 'Contact AKH Ceiling Systems: phone +98 21 8850 7585, Tehran head office and Kahrizak factory, business hours and ways to reach us.', body,
         crumbs=[('/en/', 'Home'), ('/en/contact/', 'Contact Us')], kind='ContactPage', priority='0.8', lang='en')
    add_doc('Contact Us (EN)', 'office address ' + ADDR_OFFICE_EN + ' factory ' + ADDR_FACTORY_EN + ' phone ' + PHONE, '/en/contact/', 'page', 'contact address phone hours')

# ============================================================ MEMBERSHIP
def build_membership_en():
    benefits = [('Personal order panel', 'Track every order from submission to delivery, with no phone calls needed.'),
                ('Dedicated invoice space', 'Proforma and final invoices for every order are uploaded to your panel and available to view or download any time.'),
                ('Secure sign-in with two-factor verification', 'Your account is protected by a password and, if you choose, two-factor authentication (2FA).'),
                ('Smart assistant', "Chat with the site's smart assistant any time for material estimates and technical answers."),
                ('Faster submission and tracking', 'Enter your project details once, then submit further requests in a few clicks.')]
    bl = ''.join('<li><b>%s</b> — %s</li>' % (esc(t), d) for t, d in benefits)
    steps = ''.join('<li>%s</li>' % s for s in ('Sign up with your email or mobile number and a password', 'Optionally add your job title (not required)', 'Complete your project details', 'View proforma invoices and invoices in your panel'))
    body = (phero('Customer Panel Membership', 'Sign up for free to the %s customer panel and manage your orders and invoices in one secure, personal space.' % esc(EN_NAME),
                  [('/en/', 'Home'), (None, 'Membership')], '<div class="row"><a class="btn" href="/account/register/">Sign up free</a><a class="btn line" href="/account/login/">Sign in</a></div>', lang='en') +
            ('<section class="sec"><div class="wrap"><div class="card pad rv">%s<h2>Why <em class="o">sign up</em></h2>'
             '<ul class="checks x15">%s</ul><h3 class="x4">How do I get started?</h3><ul class="checks x15">%s</ul>'
             '<a class="btn x4" href="/account/register/">Sign up now</a></div></div></section>'
             % (kicker('01', 'Benefits'), bl, steps)) +
            cta('Ready?', 'Sign up today and submit your first request.', lang='en'))
    page('/en/membership/', 'Customer Panel Membership | %s' % EN_NAME, 'Sign up for free to the AKH Ceiling Systems customer panel to manage your orders and invoices, and chat with the smart assistant.', body,
         crumbs=[('/en/', 'Home'), ('/en/membership/', 'Membership')], kind='WebPage', priority='0.6', lang='en')
    add_doc('Membership (EN)', 'membership benefits personal space invoices order tracking smart assistant', '/en/membership/', 'page', 'membership sign up login invoice')

# ============================================================ QUOTE / ESTIMATE / ASSISTANT
def build_quote_en():
    prods = ''.join('<option value="%s">%s</option>' % (k, v) for k, v in [('', 'Choose one'), ('grid', '60x60 grid false ceiling'), ('drywall', 'Drywall system & plaster ceiling'), ('profiles', 'Drywall profiles & connectors'), ('other', 'Other / need guidance')])
    blds = ''.join('<option value="%s">%s</option>' % (k, v) for k, v in [('', 'Choose one'), ('office', 'Office / commercial'), ('school', 'Educational / university'), ('hospital', 'Healthcare'), ('hotel', 'Hotel / lobby / airport'), ('home', 'Residential'), ('industrial', 'Industrial / warehouse')])
    def fld(i, label, typ='text', req=True, ph='', extra=''):
        return '<div><label for="%s">%s%s</label><input id="%s" name="%s" type="%s"%s placeholder="%s" autocomplete="off" %s><div class="err" id="%s-e" role="alert"></div></div>' % (i, label, ' *' if req else '', i, i, typ, ' required' if req else '', ph, extra, i)
    form = ('<form class="form" id="qf" novalidate aria-label="Quote request form"><div class="two">%s%s</div><div class="two">%s%s</div><div class="two"><div><label for="building">Building type</label><select id="building">%s</select></div><div><label for="product">Product needed</label><select id="product">%s</select></div></div>'
            '<div class="two">%s<div></div></div><div><label for="desc">Notes</label><textarea id="desc" placeholder="Project type, timeline, colour and design preferences…"></textarea></div>'
            '<div class="hp" aria-hidden="true"><label for="website">Website (leave blank)</label><input id="website" name="website" tabindex="-1" autocomplete="off"></div><div><button class="btn" type="submit">Submit request</button></div></form>'
            '<div class="ok" id="sent" hidden><b>Your request has been submitted ✅</b><p id="okmsg">Tracking number: <b class="num" id="trk"></b></p><p>Our sales team will contact you during business hours.</p><div id="manual" hidden><p>Online submission was not possible; please use one of the options below to send your request:</p><pre id="preview" class="x18"></pre>'
            '<div class="row"><a class="btn sm" id="wa" href="#" target="_blank" rel="noopener">Send via WhatsApp</a><a class="btn sm line" id="mail" href="#">Send via email</a><button class="btn sm line" type="button" id="copy">Copy text</button></div></div></div>'
            '<noscript><p class="note">To submit a request, please enable JavaScript or call <a href="tel:+982188507585" class="num">%s</a>.</p></noscript>'
            % (fld('name', 'Full name', ph='e.g. John Smith'), fld('phone', 'Phone number', 'tel', ph='+98 912 345 6789', extra='inputmode=tel dir=ltr'), fld('company', 'Company name', req=False), fld('city', 'Project city'), blds, prods, fld('area', 'Approximate area (m²)', 'text', False, 'e.g. 500', 'inputmode=numeric'), PHONE))
    side = ('<div class="card pad"><h2>Direct contact</h2><ul class="checks x8"><li>Head office: <a class="num" href="tel:+982188507585">%s</a></li><li>Factory: <a class="num" href="tel:+982156548804">%s</a></li><li>%s</li><li>%s</li></ul></div>'
            '<div class="card pad x19"><h2>What happens after you submit?</h2><ul class="checks x8"><li>Our sales team reviews the request.</li><li>They may ask you for a drawing or project photos if needed.</li><li>Price and technical proposal follow once reviewed.</li></ul></div>' % (PHONE, PHONE_FACTORY, HOURS_EN[0], HOURS_EN[1]))
    body = (phero('Request a Quote', 'Enter your project details; our team will contact you with technical advice and pricing.', [('/en/', 'Home'), (None, 'Request a Quote')], lang='en') +
            '<section class="sec"><div class="wrap"><div class="split x20"><div class="formcard">%s</div><div>%s</div></div></div></section>' % (form, side))
    page('/en/quote/', 'Request a Quote | %s' % EN_NAME, 'Request a quote for false-ceiling and drywall materials: tell us about your project and the AKH Ceiling Systems team will contact you.', body,
         crumbs=[('/en/', 'Home'), ('/en/quote/', 'Request a Quote')], scripts=('quote.js',), priority='0.8', lang='en')
    add_doc('Request a Quote (EN)', 'quote request form project details', '/en/quote/', 'page', 'quote request form')

def build_estimate_en():
    def fld(i, label, val, hint='', f=''):
        h = '<div class="note">%s</div>' % hint if hint else ''
        d = ' data-for="%s"' % f if f else ''
        return '<div%s><label for="%s">%s</label><input id="%s" inputmode="decimal" value="%s" autocomplete="off">%s</div>' % (d, i, label, i, val, h)
    form = ('<form class="form" id="ef" novalidate aria-label="Material estimate"><div class="two"><div><label for="sys">Ceiling type</label><select id="sys"><option value="drywall">Drywall ceiling (F47 profile)</option><option value="grid">60x60 grid ceiling</option></select></div>'
            '<div><label for="area">Ceiling area (m²) *</label><input id="area" inputmode="decimal" placeholder="e.g. 120" autocomplete="off"><div class="err" id="area-e" role="alert"></div></div></div>'
            '<div class="two">%s%s</div><div class="two">%s%s</div><div class="two">%s<div></div></div><div><button class="btn" type="submit">Calculate estimate</button></div></form>' %
            (fld('perim', 'Ceiling perimeter (m)', '', 'Leave blank to calculate from the area, assuming a square room.'), fld('waste', 'Waste / extra percentage', '10', 'For cutting and damage; between 0 and 50.'),
             fld('sp', 'F47 panel-bearing spacing (m)', '0.6', '', 'drywall'), fld('cs', 'F47 load-bearing spacing (m)', '1.2', '', 'drywall'), fld('hs', 'Hanger spacing on load-bearing (m)', '1.2', '', 'drywall')))
    res = ('<div id="res" hidden><div class="cta"><div><p>Initial estimate</p><h2 id="sum"></h2></div></div><div class="scroll x21"><table class="tbl"><thead><tr><th>Item</th><th>Quantity</th><th>Unit</th><th>Note</th></tr></thead><tbody id="tb"></tbody></table></div>'
           '<p class="note">This is only an <b>initial estimate</b> based on a standard layout and our catalog dimensions; it does not account for actual room height, openings, decorative ceilings, or screws and nails. Our technical team will confirm the final quantity and price from your drawings.</p>'
           '<p class="row x22"><a class="btn" id="qlink" href="/en/quote/">Send this estimate to our team for a price</a></p></div>')
    body = (phero('Material Estimate', 'Enter the ceiling type and area to see the approximate quantity of profiles, connectors and tiles; then send the estimate to our team for an exact price.', [('/en/', 'Home'), (None, 'Material Estimate')], lang='en') +
            '<section class="sec"><div class="wrap x23"><div class="formcard">%s</div><div class="x24">%s</div></div></section>' % (form, res) + cta(lang='en'))
    steps = ['Choose the ceiling type.', 'Enter the ceiling area in square metres.', 'Adjust the perimeter and profile spacing if needed.', 'See the approximate quantity of each item and send it to our team for an exact price.']
    page('/en/estimate/', 'Material Estimate | Calculate F47 Profile & Tile Quantity', "A material-estimate calculator for drywall and 60x60 grid false ceilings, based on area: approximate quantity of F47 profile, L25 angle, clips, hangers, tiles and T-bars from the company's catalog dimensions.", body,
         crumbs=[('/en/', 'Home'), ('/en/estimate/', 'Material Estimate')], scripts=('estimate.js',), priority='0.9', freq='weekly',
         extra_ld=[{"@type": "WebApplication", "@id": SITE + '/en/estimate/#app', "name": "False-ceiling material estimate calculator", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "inLanguage": "en-US", "isAccessibleForFree": True, "publisher": {"@id": ORG_ID}},
                   {"@type": "HowTo", "@id": SITE + '/en/estimate/#howto', "name": "Estimating false-ceiling materials", "step": [{"@type": "HowToStep", "position": i + 1, "text": s} for i, s in enumerate(steps)]}], lang='en')
    add_doc('Material Estimate (EN)', 'calculator estimate F47 profile L25 angle clips hangers tiles by area', '/en/estimate/', 'page', 'calculate estimate')

def build_assistant_en():
    chat = ('<div class="chat rv"><div class="chat-hd"><img src="/assets/img/emblem.jpg" alt="" width="560" height="260"><div><b>AlborzBot</b><small>Smart assistant for AKH Ceiling Systems — answers come from the company’s own documentation; nothing is sent anywhere until you request a callback</small></div></div>'
            '<div class="msgs" id="msgs" aria-live="polite"></div><div class="composer" id="composer"></div></div>'
            '<noscript><p class="note">To use the assistant, please enable JavaScript or call <a href="tel:+982188507585" class="num">%s</a>.</p></noscript>'
            '<p class="note x25">The assistant does not give a final technical recommendation or price; once you submit a request, our sales team will call you.</p>' % PHONE)
    body = (phero('Smart Assistant', 'Tell us the area and use of the space to see a material estimate and a matching installed example; ask any technical question too. For pricing, our sales team will call you.', [('/en/', 'Home'), (None, 'Smart Assistant')], lang='en') +
            '<section class="sec"><div class="wrap">%s</div></section>' % chat)
    page('/en/assistant/', 'Smart Assistant | Material Estimate & Technical Answers', 'The AKH Ceiling Systems smart assistant: a material estimate from the area you give it, a matching installed example, and answers to technical questions about profiles and ceilings.', body,
         crumbs=[('/en/', 'Home'), ('/en/assistant/', 'Smart Assistant')], scripts=('assistant.js',), priority='0.8', lang='en')
    add_doc('Smart Assistant (EN)', 'chat material estimate sample ceiling technical answer', '/en/assistant/', 'page', 'smart chat')
