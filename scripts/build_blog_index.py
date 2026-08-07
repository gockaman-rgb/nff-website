#!/usr/bin/env python3
"""Regenere blog/index.html a partir des articles eux-memes.

L'index etait maintenu a la main et avait derive : 24 valeurs de tag
differentes pour 28 articles, melangeant des sujets (Documents, Delais),
des marqueurs temporels (Nouveau, 2026, Actualite) et des formats (Guide,
Checklist, Pieges) ; sept cartes portaient un liseré rouge sans regle ;
"Nouveau" restait affiche sur des articles d'avril et "Urgent Mai 2026"
sur un evenement passe depuis trois mois.

Ici, titre, description et dates sont lus dans chaque fichier : ils ne
peuvent plus se desynchroniser. Seule la categorie est editoriale, dans
SECTIONS ci-dessous. Le badge "Nouveau" se calcule sur datePublished et
s'eteint donc tout seul.

    python3 scripts/build_blog_index.py
"""

import datetime
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
BASE = "https://naturalisationfrancefacile.fr"
APP = "https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087"

# Date de reference : passee en argument pour rester reproductible.
TODAY = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date(2026, 8, 7)
NEW_DAYS = 30

# Article pilier, mis en avant hors grille.
PILLAR = "guide-complet-naturalisation-2026"

# Les six etapes du parcours. L'ordre des sections est l'ordre reel des
# demarches : c'est aussi celui dans lequel les gens cherchent.
SECTIONS = [
    ("conditions", "1. Suis-je &eacute;ligible&nbsp;?",
     "Les conditions &agrave; remplir avant m&ecirc;me de constituer un dossier.",
     ["conditions-naturalisation-francaise", "ressources-revenus-naturalisation",
      "naturalisation-par-mariage-2026", "naturalisation-2026-nouvelles-regles",
      "pourquoi-devenir-francais-avantages"]),
    ("examens", "2. Les examens",
     "Le niveau B2 en fran&ccedil;ais et l'examen civique, obligatoires depuis 2026.",
     ["atteindre-niveau-b2-naturalisation", "tcf-irn-ou-delf-b2-lequel-choisir",
      "preparation-tcf-delf-naturalisation", "examen-civique-naturalisation-2026",
      "questions-mise-en-situation-examen-civique-naturalisation"]),
    ("dossier", "3. Constituer le dossier",
     "Les pi&egrave;ces &agrave; fournir, le budget &agrave; pr&eacute;voir et les erreurs qui font rejeter.",
     ["documents-naturalisation", "casier-judiciaire-naturalisation",
      "erreurs-dossier-naturalisation", "cout-naturalisation-francaise-2026",
      "hausse-timbre-fiscal-naturalisation-mai-2026"]),
    ("entretien", "4. L'entretien en pr&eacute;fecture",
     "Se pr&eacute;parer &agrave; l'entretien d'assimilation, et savoir ce qui suit.",
     ["entretien-naturalisation-prefectures", "questions-entretien-naturalisation",
      "sentrainer-entretien-naturalisation", "apres-entretien-naturalisation"]),
    ("suivi", "5. Suivre son dossier",
     "Comprendre o&ugrave; en est votre demande, relancer, et contester si besoin.",
     ["suivre-dossier-naturalisation-anef", "statuts-anef-naturalisation",
      "delais-naturalisation-2026", "delais-naturalisation-par-prefecture",
      "relance-naturalisation-que-faire-sans-reponse", "ajournement-vs-refus-naturalisation"]),
    ("apres", "6. Apr&egrave;s l'obtention",
     "Le d&eacute;cret est publi&eacute;&nbsp;: la c&eacute;r&eacute;monie et les d&eacute;marches qui suivent.",
     ["ceremonie-naturalisation-que-se-passe-t-il", "demarches-apres-naturalisation"]),
]

MOIS = ["janvier", "f&eacute;vrier", "mars", "avril", "mai", "juin", "juillet",
        "ao&ucirc;t", "septembre", "octobre", "novembre", "d&eacute;cembre"]


def read_article(slug):
    path = BLOG / f"{slug}.html"
    if not path.exists():
        sys.exit(f"article introuvable : {path}")
    s = path.read_text(encoding="utf-8")
    title = html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1)).strip()
    desc = html.unescape(
        re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
    ).strip()
    pub = mod = None
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        data = json.loads(block)
        for o in data if isinstance(data, list) else [data]:
            if o.get("@type") == "Article":
                pub = o.get("datePublished", "")[:10]
                mod = o.get("dateModified", "")[:10]
    if not pub:
        sys.exit(f"datePublished manquante : {slug}")
    return {
        "slug": slug, "title": title, "desc": desc,
        "pub": datetime.date.fromisoformat(pub),
        "mod": datetime.date.fromisoformat(mod or pub),
    }


def fr_date(d):
    return f"{d.day}&nbsp;{MOIS[d.month - 1]}&nbsp;{d.year}"


def esc(text):
    return html.escape(text, quote=False)


def card(a, section_label):
    is_new = (TODAY - a["pub"]).days <= NEW_DAYS
    cls = "blog-card is-new" if is_new else "blog-card"
    badge = '<span class="blog-card-badge">Nouveau</span>' if is_new else ""
    return f"""      <a href="/blog/{a['slug']}.html" class="{cls}">
        <span class="blog-card-tag">{section_label}</span>{badge}
        <h3>{esc(a['title'])}</h3>
        <p>{esc(a['desc'])}</p>
        <span class="blog-card-meta"><time datetime="{a['mod'].isoformat()}">Mis &agrave; jour le {fr_date(a['mod'])}</time></span>
        <span class="blog-card-link">Lire l'article &rarr;</span>
      </a>"""


def main():
    seen, articles = set(), {}
    for _, _, _, slugs in SECTIONS:
        for slug in slugs:
            if slug in seen:
                sys.exit(f"article classe deux fois : {slug}")
            seen.add(slug)
            articles[slug] = read_article(slug)
    pillar = read_article(PILLAR)

    on_disk = {p.stem for p in BLOG.glob("*.html") if p.stem != "index"}
    missing = on_disk - seen - {PILLAR}
    if missing:
        sys.exit(f"articles non classes dans SECTIONS : {sorted(missing)}")

    # ── sections ──
    body = []
    def strip_num(label):
        return re.sub(r"^[0-9]+\. ", "", label)

    nav = " ".join(
        '<a href="#%s">%s</a>' % (key, strip_num(label)) for key, label, _, _ in SECTIONS
    )
    for key, label, sub, slugs in SECTIONS:
        short = strip_num(label)
        cards = "\n".join(card(articles[s], short) for s in slugs)
        body.append(f"""  <section class="blog-section" id="{key}">
    <h2 class="blog-section-title">{label}</h2>
    <p class="blog-section-sub">{sub}</p>
    <div class="blog-grid">
{cards}
    </div>
  </section>""")

    ordered = [pillar] + [articles[s] for _, _, _, sl in SECTIONS for s in sl]
    blog_ld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "@id": f"{BASE}/blog/#blog",
        "name": "Blog — Naturalisation France Facile",
        "description": "Guides pratiques sur la naturalisation française, étape par étape : conditions, examens, dossier, entretien, suivi et démarches après l'obtention.",
        "url": f"{BASE}/blog/",
        "inLanguage": "fr-FR",
        "publisher": {"@type": "Organization", "name": "Naturalisation France Facile", "url": BASE},
    }
    itemlist_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Tous les guides de naturalisation",
        "numberOfItems": len(ordered),
        "itemListElement": [
            {"@type": "ListItem", "position": i, "url": f"{BASE}/blog/{a['slug']}.html", "name": a["title"]}
            for i, a in enumerate(ordered, 1)
        ],
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog"},
        ],
    }

    def ld(o):
        return ('  <script type="application/ld+json">\n  '
                + json.dumps(o, ensure_ascii=False, indent=2).replace("\n", "\n  ")
                + "\n  </script>\n")

    old = (BLOG / "index.html").read_text(encoding="utf-8")
    head_tail = old[old.index("</head>"):]
    nav_html = head_tail[head_tail.index("<nav class=\"nav\">"):head_tail.index("</nav>") + 6]
    footer_html = head_tail[head_tail.index("<footer class=\"footer\">"):]

    page = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-B5GLCV73F6"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-B5GLCV73F6');</script>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/x-icon" href="/img/favicon.ico" />
  <link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32x32.png" />
  <link rel="icon" type="image/png" sizes="16x16" href="/img/favicon-16x16.png" />
  <link rel="apple-touch-icon" sizes="180x180" href="/img/apple-touch-icon.png" />
  <link rel="manifest" href="/site.webmanifest" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#0a0f2c" media="(prefers-color-scheme: dark)" />
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <title>Blog naturalisation : {len(ordered)} guides &eacute;tape par &eacute;tape</title>
  <meta name="description" content="Conditions, examens, dossier, entretien, suivi et démarches après l'obtention : tous nos guides sur la naturalisation française, classés dans l'ordre du parcours." />
  <link rel="canonical" href="{BASE}/blog/" />
  <meta property="og:title" content="Blog naturalisation&nbsp;: les guides &eacute;tape par &eacute;tape" />
  <meta property="og:description" content="Tous nos guides sur la naturalisation française, classés dans l'ordre réel des démarches." />
  <meta property="og:url" content="{BASE}/blog/" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="fr_FR" />
  <meta property="og:site_name" content="Naturalisation France Facile" />
  <meta property="og:image" content="{BASE}/img/og/default.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{BASE}/img/og/default.png" />
  <link rel="stylesheet" href="/css/style.css?v=21" />
{ld(blog_ld)}{ld(itemlist_ld)}{ld(breadcrumb_ld)}</head>
<body>

{nav_html}

<section class="section" style="padding-top:120px">
  <picture class="blog-hero-flag">
    <source srcset="/img/blog-flag.webp" type="image/webp" />
    <img src="/img/blog-flag.jpg" loading="lazy" decoding="async" alt="Drapeau de la R&eacute;publique fran&ccedil;aise &mdash; Libert&eacute;, &Eacute;galit&eacute;, Fraternit&eacute;" width="880" height="597" />
  </picture>
  <h1 class="section-title">Blog</h1>
  <p class="section-sub">{len(ordered)}&nbsp;guides sur la naturalisation fran&ccedil;aise, class&eacute;s dans l'ordre r&eacute;el des d&eacute;marches.</p>

  <nav class="blog-toc" aria-label="Les &eacute;tapes">{nav}</nav>

  <a href="/blog/{pillar['slug']}.html" class="blog-pillar">
    <span class="blog-card-tag">Commencer ici</span>
    <h2>{esc(pillar['title'])}</h2>
    <p>{esc(pillar['desc'])}</p>
    <span class="blog-card-link">Lire le guide complet &rarr;</span>
  </a>
</section>

{chr(10).join(body)}

<section class="cta-banner">
  <h2>Pr&eacute;parez votre naturalisation, gratuitement</h2>
  <p>Examen civique, TCF&nbsp;IRN et DELF&nbsp;B2, simulation d'entretien, checklist des pi&egrave;ces et suivi du dossier.</p>
  <a class="cta-btn" href="{APP}" target="_blank">T&eacute;l&eacute;charger sur l'App Store</a>
</section>

{footer_html}"""

    (BLOG / "index.html").write_text(page, encoding="utf-8")

    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        json.loads(block)
        assert not re.search(r"&[a-zA-Z]{2,8};", block), "entite HTML dans le JSON-LD"

    news = [a["slug"] for a in ordered if (TODAY - a["pub"]).days <= NEW_DAYS]
    print(f"{len(ordered)} articles · {len(SECTIONS)} sections · pilier : {PILLAR}")
    print(f"badge Nouveau ({NEW_DAYS} jours) : {len(news)} article(s) — {', '.join(news) or 'aucun'}")


if __name__ == "__main__":
    main()
