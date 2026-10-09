"""Build the Services branch of the static Digicomplish site.

    python tools/build_services.py

Idempotent. Each run:
  1. rewrites the primary menu on every page (Services mega menu, Industries,
     Insights, About, Careers, "Talk to an Expert" button) and the footer link,
  2. generates /services/, /services/workforce/ and a noindex holding page at
     every Services-branch address that is not built yet,
  3. writes redirect stubs, vercel.json redirects, sitemap.xml and robots.txt,
  4. renders the 1200x630 sharing images.

All copy and structure comes from tools/site_data.py. The closing call to
action is tools/partials/cta.html: edit it once and rebuild to update every page.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import site_data as D  # noqa: E402

ROOT = os.path.normpath(os.path.join(HERE, "..", "site"))
REPO = os.path.normpath(os.path.join(HERE, ".."))
SHELL_SOURCE = "privacy-policy.html"      # any normal inner page works as the shell
ASSET_VERSION = "20261009l"
E = html.escape


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def page_files():
    """Every full page (has the site header), excluding the redirect stubs."""
    out = []
    for dp, dn, fn in os.walk(ROOT):
        if "wp-content" in dp or "wp-includes" in dp:
            continue
        for f in fn:
            if f.endswith(".html") and not f.startswith("_"):
                p = os.path.join(dp, f)
                if 'data-elementor-type="header"' in rd(p):
                    out.append(p)
    return out


def href(pillar_slug, service_slug=None):
    p = next(x for x in D.PILLARS if x["slug"] == pillar_slug)
    if service_slug is None:
        return D.pillar_url(p)
    return D.service_url(p, D.find(service_slug, pillar_slug)[1])


# ------------------------------------------------------------- 1. navigation
def mega_menu():
    cols = []
    for p in D.PILLARS:
        parts = ['<div class="dcs-mcol">',
                 '<a class="dcs-mpillar" href="%s">%s</a>' % (D.pillar_url(p), E(p["name"]))]
        if p["groups"]:
            for g, _ in p["groups"]:
                links = "".join('<a href="%s">%s</a>' % (D.service_url(p, s), E(s["name"]))
                                for s in p["services"] if s["group"] == g)
                parts.append('<div class="dcs-mgroup"><span class="dcs-mlabel">%s</span>%s</div>' % (E(g), links))
        else:
            links = "".join('<a href="%s">%s</a>' % (D.service_url(p, s), E(s["name"])) for s in p["services"])
            parts.append('<div class="dcs-mgroup">%s</div>' % links)
        parts.append("</div>")
        cols.append("".join(parts))
    strip = ('<div class="dcs-mstrip"><a href="%s">How We Engage</a>'
             '<a href="/services/">View all services</a></div>' % D.HOW_WE_ENGAGE["url"])
    return ('<!--dcs-menu--><li class="menu-item menu-item-type-post_type menu-item-object-page '
            'menu-item-has-children dcs-services-item"><a href="/services/" class="elementor-item">Services</a>'
            '<ul class="sub-menu elementor-nav-menu--dropdown digi-mega digi-mega-services">'
            '<li class="digi-mega-li"><div class="dcs-mega">'
            '<div class="dcs-mcols">%s</div>%s</div></li></ul></li><!--/dcs-menu-->' % ("".join(cols), strip))


RE_HOME_LI = re.compile(r'<li class="[^"]*menu-item-home[^"]*"><a href="/index\.html"[^>]*>Home</a></li>\s*')
RE_OLD_SOLUTIONS = re.compile(
    r'<li class="[^"]*menu-item-has-children"><a href="[^"]*" class="elementor-item[^"]*"[^>]*>Solutions</a>\s*'
    r'<ul class="sub-menu[^"]*digi-mega-solutions">.*?</ul>\s*</li>', re.S)
RE_NEW_MENU = re.compile(r'<!--dcs-menu-->.*?<!--/dcs-menu-->', re.S)
RE_INDUSTRIES = re.compile(r'(<li class="[^"]*"><a href=")[^"]*(" class="elementor-item[^"]*">Industries</a>)')

HREF_MAP = {
    "/services.html": "/services/",
    "/talent-fulfillment-solutions.html": "/services/workforce/",
    "/digital-excellence.html": "/services/technology/",
    "/how-to-increase-your-youtube-subscribers.html": "/insights.html",
    "/how-to-get-the-most-out-of-your-press-release.html": "/insights.html",
    "/tips-for-remotely-managing-a-team.html": "/insights.html",
}


def update_nav(s):
    menu = mega_menu()
    s = RE_HOME_LI.sub("", s)
    if RE_NEW_MENU.search(s):
        s = RE_NEW_MENU.sub(lambda m: menu, s)
    else:
        s, n = RE_OLD_SOLUTIONS.subn(lambda m: menu, s)
        if not n and "elementor-nav-menu" in s:
            raise RuntimeError("Solutions menu not found")
    s = RE_INDUSTRIES.sub(r"\g<1>/industries/\g<2>", s)
    # header button: "Contact Us" -> "Talk to an Expert" (header only)
    s = re.sub(r'(<header .*?</header>)',
               lambda m: m.group(1).replace('<span class="elementor-button-text">Contact Us</span>',
                                            '<span class="elementor-button-text">Talk to an Expert</span>'),
               s, flags=re.S)
    for old, new in HREF_MAP.items():
        s = s.replace('href="%s"' % old, 'href="%s"' % new)
    # footer: Services link in the brand column
    if 'class="dc-footer-brand"' in s and '<li><a href="/services/">Services</a></li>' not in s:
        s = s.replace('<ul><li><a href="/about.html">About</a></li>',
                      '<ul><li><a href="/services/">Services</a></li><li><a href="/about.html">About</a></li>', 1)
    s = re.sub(r'digi-brand\.(css|js)\?v=[0-9a-z]+', r'digi-brand.\1?v=' + ASSET_VERSION, s)
    return s


# --------------------------------------------------------------- 2. sections
def link_list(items):
    return '<span class="dcs-links">%s</span>' % '<span class="dcs-dot" aria-hidden="true"> · </span>'.join(
        '<a href="%s">%s</a>' % (href(ps, ss), E(t)) for t, ps, ss in items)


def crumbs(trail):
    bits = []
    for name, url in trail[:-1]:
        bits.append('<a href="%s">%s</a>' % (url, E(name)))
    bits.append('<span aria-current="page">%s</span>' % E(trail[-1][0]))
    return ('<nav class="digi-crumbs dcs-crumbs" aria-label="Breadcrumb">%s</nav>'
            % '<span class="dcs-sep" aria-hidden="true">›</span>'.join(bits))


def hero(trail, h1, sub, intro, audience, briefing_label, fine):
    return f'''
  <section class="digi-hero dcs-hero">
    <div class="digi-wrap dcs-hero-grid">
      <div class="dcs-hero-copy">
        {crumbs(trail)}
        <h1>{E(h1)}</h1>
        <p class="dcs-sub">{E(sub)}</p>
        <p class="dcs-intro">{E(intro)}</p>
        <p class="dcs-aud">{E(audience)}</p>
      </div>
      <div class="dcs-hero-actions">
        <a class="dcs-btn dcs-btn-primary" href="#talk" data-request="expert">Talk to an Expert</a>
        <a class="dcs-btn dcs-btn-outline" href="?request=briefing#talk" data-request="briefing">{E(briefing_label)}</a>
        <p class="dcs-fine">{E(fine)}</p>
      </div>
    </div>
  </section>'''


def glance():
    items = "".join('<li><span class="dcs-num">%s</span> <span class="dcs-lbl">%s</span></li>' % (E(n), E(l))
                    for n, l in D.GLANCE)
    return f'''
  <section class="dcs-glance" aria-labelledby="dcs-glance-h">
    <div class="digi-wrap">
      <h2 id="dcs-glance-h" class="dcs-glance-h">At a glance</h2>
      <ul class="dcs-glance-list">{items}</ul>
    </div>
  </section>'''


def head(id_, title, intro=None, extra=""):
    p = '<p>%s</p>' % E(intro) if intro else ""
    return f'<div class="dcs-head{extra}"><h2 id="{id_}">{E(title)}</h2>{p}</div>'


def section(id_, title, body, intro=None, cls=""):
    return f'''
  <section class="dcs-section{cls}" aria-labelledby="{id_}">
    <div class="digi-wrap">
      {head(id_, title, intro)}
      {body}
    </div>
  </section>'''


def where_to_start(rows, id_):
    cards = "".join('<li class="dcs-path"><h3>%s</h3>%s</li>' % (E(t), link_list(links)) for t, links in rows)
    return section(id_, "Where to start", '<ul class="dcs-paths">%s</ul>' % cards,
                   "Choose the priority closest to your own.")


def steps(rows, id_, intro=None):
    li = "".join('<li class="dcs-step"><span class="dcs-step-n" aria-hidden="true">%d</span>'
                 '<h3><span class="dcs-vh">Step %d: </span>%s</h3><p>%s</p></li>'
                 % (i + 1, i + 1, E(t), E(x)) for i, (t, x) in enumerate(rows))
    return section(id_, "How we work", '<ol class="dcs-steps">%s</ol>' % li, intro, " dcs-tint")


def apart(rows, id_):
    li = "".join('<li class="dcs-apart"><p><strong>%s</strong> %s</p></li>' % (E(a), E(b)) for a, b in rows)
    return section(id_, "What sets our approach apart",
                   '<ul class="dcs-aparts dcs-n%d">%s</ul>' % (len(rows), li))


def insights(id_, intro, posts, view_all):
    if len(posts) < 3:
        return "\n  <!-- Insights section hidden until three articles are published (tools/site_data.py) -->"
    cards = "".join('<li class="dcs-post"><h3><a href="%s">%s</a></h3><p>%s</p></li>'
                    % (p["url"], E(p["title"]), E(p.get("summary", ""))) for p in posts[:3])
    more = '<a class="dcs-link" href="/insights.html">View all insights</a>' if view_all else ""
    return section(id_, "Insights", '<ul class="dcs-posts dcs-swipe">%s</ul>%s' % (cards, more), intro)


def cta(heading, line):
    tpl = rd(os.path.join(HERE, "partials", "cta.html"))
    return (tpl.replace("{{HEADING}}", E(heading)).replace("{{LINE}}", E(line))
               .replace("{{ENDPOINT}}", E(D.FORM_ENDPOINT)))


# -------------------------------------------------------------- page bodies
def services_page():
    practice_cards = []
    for p in D.PILLARS:
        feats = [(p["featured_labels"].get(sl, D.find(sl, p["slug"])[1]["name"]), p["slug"], sl)
                 for sl in p["featured"]]
        practice_cards.append(
            f'<li class="dcs-practice"><h3><a href="{D.pillar_url(p)}">{E(p["name"])}</a></h3>'
            f'<p>{E(p["summary"])}</p>{link_list(feats)}'
            f'<a class="dcs-link" href="{D.pillar_url(p)}">Explore {E(p["name"])}</a></li>')
    eng = "".join('<li class="dcs-eng"><p><strong>%s</strong> %s</p></li>' % (E(a), E(b)) for a, b in D.ENGAGEMENT)
    body = "".join([
        hero([("Home", "/index.html"), ("Services", "/services/")], "Services",
             "Advisory and delivery across workforce, capability centers and technology.",
             "We help leadership teams make the decisions that shape their organization, then deliver the programs that carry those decisions out. One accountable team plans the work and runs it.",
             "Designed for CHROs, COOs, CTOs and the leaders who report to them.",
             "Request a briefing",
             "A briefing is a focused conversation with a senior member of our team, followed by a short written summary of priorities and recommended next steps."),
        glance(),
        section("dcs-practices-h", "Our practices", '<ul class="dcs-practices">%s</ul>' % "".join(practice_cards),
                "Three practices, one method."),
        where_to_start(D.SERVICES_WHERE, "dcs-where-h"),
        steps(D.SERVICES_STEPS, "dcs-how-h", "The same four-stage method applies in every practice."),
        apart(D.SERVICES_APART, "dcs-apart-h"),
        section("dcs-eng-h", "Engagement models",
                '<ul class="dcs-engs">%s</ul><a class="dcs-link" href="%s">See how we engage</a>' % (eng, D.HOW_WE_ENGAGE["url"]),
                "The engagement model follows your requirements and is agreed in writing before work begins."),
        insights("dcs-ins-h", "Perspectives for leadership teams on workforce, capability centers and technology.",
                 D.SERVICES_INSIGHTS, True),
        cta(*D.CTA_SERVICES),
    ])
    return body


def workforce_page():
    p = D.PILLARS[0]
    groups = []
    for g, tagline in p["groups"]:
        cards = "".join(
            f'<li class="dcs-svc"><h4><a href="{D.service_url(p, s)}">{E(s["name"])}</a></h4>'
            f'<p>{E(s["descriptor"])}</p><p class="dcs-receive"><strong>You receive:</strong> {E(s["receive"])}</p></li>'
            for s in p["services"] if s["group"] == g)
        gid = "dcs-g-" + re.sub(r"[^a-z]+", "-", g.lower()).strip("-")
        groups.append(f'<div class="dcs-group"><div class="dcs-group-head"><h3 id="{gid}">{E(g)}</h3>'
                      f'<p>{E(tagline)}</p></div><ul class="dcs-svcs" aria-labelledby="{gid}">{cards}</ul></div>')
    groups.append('<p class="dcs-note">Our work covers technology and IT, engineering, sales and commercial, and '
                  'executive and leadership roles, in every industry. See <a href="/industries/">Industries</a>.</p>')

    measures = "".join("<li>%s</li>" % E(m) for m in D.MEASURES)
    risks = "".join('<li><strong>%s</strong> %s</li>' % (E(a), E(b)) for a, b in D.RISKS)
    scen = "".join(
        f'<li class="dcs-scen"><h4>{E(t)}</h4><dl><dt>Challenge:</dt><dd>{E(c)}</dd>'
        f'<dt>Our approach:</dt><dd>{E(a)}</dd><dt>Outcome for leadership:</dt><dd>{E(o)}</dd></dl></li>'
        for t, c, a, o in D.SCENARIOS)
    gov = f'''<div class="dcs-gov">
        <div class="dcs-gov-box"><h3>Measures we report on.</h3><p>Measures are agreed for each engagement, and definitions are fixed at the start so the numbers mean the same thing to everyone.</p><ul class="dcs-ticks">{measures}</ul></div>
        <div class="dcs-gov-box"><h3>How we manage risk.</h3><ul class="dcs-risks">{risks}</ul></div>
      </div>
      <div class="dcs-scen-head"><h3>Illustrative scenarios.</h3><p>Examples of the work we take on.</p></div>
      <ul class="dcs-scens dcs-swipe">{scen}</ul>
      <a class="dcs-link" href="{D.HOW_WE_ENGAGE["url"]}">Read more on How We Engage</a>'''

    faq = "".join(f'<details class="dcs-faq-item"><summary><h3>{E(q)}</h3></summary><p>{E(a)}</p></details>'
                  for q, a in D.FAQ)

    return "".join([
        hero([("Home", "/index.html"), ("Services", "/services/"), ("Workforce & Talent", "/services/workforce/")],
             "Workforce & Talent",
             "Plan, source and manage the workforce your strategy requires.",
             "We help leadership teams decide what capacity they need, understand the talent market, and run the workforce programs that deliver it.",
             "Designed for CHROs, COOs, CTOs and heads of talent.",
             "Request a workforce briefing",
             "A workforce briefing is a focused conversation with a senior member of our team, followed by a short written summary of priorities and recommended next steps."),
        glance(),
        where_to_start(D.WORKFORCE_WHERE, "dcs-where-h"),
        section("dcs-svcs-h", "Our services", "".join(groups)),
        steps(D.WORKFORCE_STEPS, "dcs-how-h"),
        apart(D.WORKFORCE_APART, "dcs-apart-h"),
        section("dcs-gov-h", "Governance and assurance", gov, cls=" dcs-tint"),
        insights("dcs-ins-h", None, D.WORKFORCE_INSIGHTS, False),
        section("dcs-faq-h", "Frequently asked questions", '<div class="dcs-faq">%s</div>' % faq),
        cta(*D.CTA_WORKFORCE),
    ])


def holding_page(name, trail, back):
    links = "".join('<a class="dcs-link" href="%s">%s</a>' % (u, E(t)) for t, u in back)
    return "".join([
        f'''
  <section class="digi-hero dcs-hero dcs-hero-hold">
    <div class="digi-wrap">
      {crumbs(trail)}
      <h1>{E(name)}</h1>
      <p class="dcs-sub">This page is being prepared.</p>
    </div>
  </section>
  <section class="dcs-section"><div class="digi-wrap dcs-hold-links">{links}</div></section>''',
        cta(*D.CTA_SERVICES),
    ])


# ------------------------------------------------------------------- shell
RE_DROP_HEAD = [
    re.compile(r'<link rel="canonical"[^>]*>\s*'),
    re.compile(r"<link rel='shortlink'[^>]*>\s*"),
    re.compile(r'<link rel="alternate" title="oEmbed[^>]*>\s*'),
    re.compile(r'<link rel="alternate" title="JSON"[^>]*>\s*'),
    re.compile(r'<link rel="EditURI"[^>]*>\s*'),
    re.compile(r'\s*<meta property="(og|article):[^"]*"[^>]*>'),
    re.compile(r'<meta name="description"[^>]*>\s*'),
    re.compile(r'<meta name="twitter:[^"]*"[^>]*>\s*'),
    re.compile(r'<script type="application/ld\+json".*?</script>\s*', re.S),
    re.compile(r'gtag\("set","linker",\{"domains":\["beratung\.vamtam\.com"\]\}\);\n?'),
]


def seo_block(url, title, desc, image, index=True, trail=None):
    abs_url = D.SITE + url
    robots = "index, follow, max-image-preview:large" if index else "noindex, follow"
    out = [f'<meta name="description" content="{E(desc)}" />' if desc else "",
           f'<meta name="robots" content="{robots}" />',
           f'<link rel="canonical" href="{abs_url}" />']
    if index:
        img = D.SITE + image
        out += [f'<meta property="og:locale" content="en_US" />',
                f'<meta property="og:type" content="website" />',
                f'<meta property="og:site_name" content="Digicomplish" />',
                f'<meta property="og:title" content="{E(title)}" />',
                f'<meta property="og:description" content="{E(desc)}" />',
                f'<meta property="og:url" content="{abs_url}" />',
                f'<meta property="og:image" content="{img}" />',
                f'<meta property="og:image:width" content="1200" />',
                f'<meta property="og:image:height" content="630" />',
                f'<meta property="og:image:alt" content="{E(title)}" />',
                f'<meta name="twitter:card" content="summary_large_image" />',
                f'<meta name="twitter:title" content="{E(title)}" />',
                f'<meta name="twitter:description" content="{E(desc)}" />',
                f'<meta name="twitter:image" content="{img}" />']
        graph = [
            {"@type": "Organization", "@id": D.SITE + "/#organization", "name": "Digicomplish",
             "url": D.SITE + "/", "logo": D.SITE + "/wp-content/uploads/2026/02/Digicomplish-Logo.png"},
            {"@type": "WebPage", "@id": abs_url + "#webpage", "url": abs_url, "name": title,
             "description": desc, "inLanguage": "en-US",
             "publisher": {"@id": D.SITE + "/#organization"},
             "breadcrumb": {"@id": abs_url + "#breadcrumb"}},
            {"@type": "BreadcrumbList", "@id": abs_url + "#breadcrumb",
             "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n,
                                  "item": D.SITE + ("/" if u == "/index.html" else u)}
                                 for i, (n, u) in enumerate(trail)]},
        ]
        out.append('<script type="application/ld+json">%s</script>'
                   % json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False))
    return "\n".join(x for x in out if x) + "\n"


def build_page(shell, url, title, desc, body, image="", index=True, trail=None, current=True):
    s = shell
    for rx in RE_DROP_HEAD:
        s = rx.sub("", s)
    s = re.sub(r"<meta name='robots'[^>]*>\s*", "", s)
    s = re.sub(r"<title>.*?</title>", lambda m: "<title>%s</title>\n%s" % (
        E(title), seo_block(url, title, desc, image, index, trail)), s, count=1, flags=re.S)
    # leftover theme-vendor domain (Elementor config URLs) -> same-origin
    s = s.replace("https:\\/\\/beratung.vamtam.com", "").replace("https://beratung.vamtam.com", "")
    # body: not the home page; add skip link
    s = re.sub(r'<body class="([^"]*)"', lambda m: '<body class="%s dcs-page"' % m.group(1).replace("home ", ""), s, count=1)
    s = re.sub(r'(<body[^>]*>)', r'\1\n<a class="dcs-skip" href="#main">Skip to content</a>', s, count=1)
    if current:
        s = s.replace('dcs-services-item"><a href="/services/" class="elementor-item"',
                      'dcs-services-item current-menu-ancestor"><a href="/services/" class="elementor-item elementor-item-active"')
    # no stray "current" marker on other items
    s = s.replace(' current-menu-item', '').replace(' current_page_item', '').replace(' aria-current="page" class="elementor-item"', ' class="elementor-item"')
    a = s.index('<div class="digi-main">')
    b = s.index("</article>")
    s = s[:a] + '<div class="digi-main dcs">' + body + "\n</div>\n</div>\n</div>\n" + s[b:]
    assert "beratung.vamtam.com" not in s, url
    return s


def stub(target):
    t = E(target)
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
            f'<meta http-equiv="refresh" content="0; url={t}"><link rel="canonical" href="{E(D.SITE)}{t}">'
            f'<title>Redirecting…</title><script>location.replace("{t}");</script></head>'
            f'<body>Redirecting to <a href="{t}">{t}</a>…</body></html>')


def path_for(url):
    if url.endswith("/"):
        return os.path.join(ROOT, url.strip("/").replace("/", os.sep), "index.html")
    return os.path.join(ROOT, url.lstrip("/").replace("/", os.sep))


# --------------------------------------------------------------------- run
def main():
    # 1. navigation + footer on every page
    stubs = {path_for(old) for old, _ in D.REDIRECTS}
    partials = [os.path.join(ROOT, f) for f in ("_part-head.html", "_part-foot.html") if os.path.exists(os.path.join(ROOT, f))]
    for p in page_files() + partials:
        if p in stubs:
            continue
        s = rd(p)
        n = update_nav(s)
        if n != s:
            wr(p, n)

    # industries anchor on the home page
    ip = os.path.join(ROOT, "index.html")
    s = rd(ip)
    if 'id="industries"' not in s:
        s = s.replace('class="dc-section alt dc-industry">', 'class="dc-section alt dc-industry" id="industries">', 1)
        wr(ip, s)

    shell = rd(os.path.join(ROOT, SHELL_SOURCE))

    # 2. pages
    wr(path_for("/services/"), build_page(
        shell, "/services/", "Workforce, GCC and Technology Services | Digicomplish",
        "Workforce and talent solutions, Global Capability Centers, and technology and AI services for enterprise leadership teams.",
        services_page(), "/wp-content/uploads/2026/10/og-services.png", True,
        [("Home", "/index.html"), ("Services", "/services/")]))
    wr(path_for("/services/workforce/"), build_page(
        shell, "/services/workforce/", "Workforce Strategy, Talent Intelligence, RPO | Digicomplish",
        "Workforce planning, talent intelligence, RPO and MSP for enterprise leadership teams. Advisory-led, with senior ownership of every engagement.",
        workforce_page(), "/wp-content/uploads/2026/10/og-workforce.png", True,
        [("Home", "/index.html"), ("Services", "/services/"), ("Workforce & Talent", "/services/workforce/")]))

    holds = []
    for p in D.PILLARS:
        if not p["built"]:
            holds.append((D.pillar_url(p), p["name"],
                          [("Home", "/index.html"), ("Services", "/services/"), (p["name"], D.pillar_url(p))],
                          [("View all services", "/services/")]))
        for sv in p["services"]:
            if not sv["built"]:
                holds.append((D.service_url(p, sv), sv["name"],
                              [("Home", "/index.html"), ("Services", "/services/"), (p["name"], D.pillar_url(p)),
                               (sv["name"], D.service_url(p, sv))],
                              [("Explore " + p["name"], D.pillar_url(p)), ("View all services", "/services/")]))
    if not D.HOW_WE_ENGAGE["built"]:
        holds.append((D.HOW_WE_ENGAGE["url"], "How We Engage",
                      [("Home", "/index.html"), ("How We Engage", D.HOW_WE_ENGAGE["url"])],
                      [("View all services", "/services/")]))
    for url, name, trail, back in holds:
        wr(path_for(url), build_page(shell, url, "%s | Digicomplish" % name, "", holding_page(name, trail, back),
                                     index=False, trail=trail))

    # 3. redirects, sitemap, robots
    # Netlify (the live host) resolves /services and /services/ to services.html
    # when that file exists, so a stub there redirects to itself forever. Never
    # leave a "<name>.html" next to a "<name>/" folder; real 301s live in _redirects.
    for old, new in D.REDIRECTS:
        p = path_for(old)
        if old.endswith(".html") and os.path.isdir(p[:-5]):
            if os.path.exists(p):
                os.remove(p)
            continue
        wr(p, stub(new))
    wr(os.path.join(ROOT, "_redirects"),
       "# Generated by tools/build_services.py (Netlify). 301! = redirect even if a file exists.\n"
       + "".join("%s  %s  301!\n" % (o.rstrip("/") if o.endswith("/") else o, n) for o, n in D.REDIRECTS))
    for vj in (os.path.join(REPO, "vercel.json"), os.path.join(ROOT, "vercel.json")):
        cfg = json.loads(rd(vj))
        # "trailingSlash": false would 308 /services/ -> /services and fight the canonical URLs
        cfg.pop("trailingSlash", None)
        cfg["redirects"] = [{"source": o.rstrip("/") if o != "/" else o, "destination": n, "permanent": True}
                            for o, n in D.REDIRECTS]
        cfg["redirects"] += [{"source": o, "destination": n, "permanent": True}
                             for o, n in D.REDIRECTS if o.endswith("/")]
        wr(vj, json.dumps(cfg, indent=2) + "\n")

    urls = ["/", "/services/", "/services/workforce/", "/about.html", "/careers.html", "/contact.html",
            "/insights.html", "/privacy-policy.html", "/terms-of-use.html"]
    wr(os.path.join(ROOT, "sitemap.xml"),
       '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
       + "".join("  <url><loc>%s%s</loc></url>\n" % (D.SITE, u) for u in urls) + "</urlset>\n")
    wr(os.path.join(ROOT, "robots.txt"), "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % D.SITE)

    # 4. sharing images
    try:
        import make_og
        make_og.render(os.path.join(ROOT, "wp-content", "uploads", "2026", "10", "og-services.png"),
                       "Services", "Advisory and delivery across workforce, capability centers and technology.")
        make_og.render(os.path.join(ROOT, "wp-content", "uploads", "2026", "10", "og-workforce.png"),
                       "Workforce & Talent", "Plan, source and manage the workforce your strategy requires.")
    except ImportError as e:
        print("skip OG images:", e)

    print("built: /services/, /services/workforce/, %d holding pages, %d redirects" % (len(holds), len(D.REDIRECTS)))


if __name__ == "__main__":
    main()
