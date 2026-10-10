#!/usr/bin/env python3
"""Genere outils/quelle-voie-nationalite.html depuis l'orienteur de l'app.

Source : data/procedure_advisor.json, copie TELLE QUELLE du fichier de l'app
(NaturalisationFranceFacile/Resources/procedure_advisor.json, depot
gockaman-rgb/naturalisation-france-facile). Quand l'arbre change dans l'app,
recopier le fichier puis relancer ce script : la page ne s'edite jamais a la
main, et le site pose exactement les questions de l'app.

Ce que le script ajoute a l'arbre : la fiche de chaque voie (VOIES), ecrite
d'apres service-public.gouv.fr (fiches F2213, F2214, F2726, F33430, F33800,
F295, F3070, F31919, F3071, F1051, F39426, verifiees en 2025-2026), et les
liens vers les articles du site. Regles de l'orienteur, communes avec l'app :
ne jamais promettre un nombre de questions, ne jamais rendre un verdict
d'ineligibilite (un resultat "not_yet" dit ce qui viendra, pas un refus).

APP_COVERS liste les voies que l'app EN VENTE accompagne : seules leurs
fiches renvoient vers l'App Store. A elargir quand la version qui couvre les
declarations sera en vente.

    python3 scripts/build_voies.py
"""

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TREE = ROOT / "data" / "procedure_advisor.json"
OUT = ROOT / "outils" / "quelle-voie-nationalite.html"
NAV_FROM = ROOT / "blog" / "declaration-nationalite-tribunal-judiciaire.html"
BASE = "https://naturalisationfrancefacile.fr"
URL = f"{BASE}/outils/quelle-voie-nationalite.html"
APP = "https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087"
SP = "https://www.service-public.gouv.fr/particuliers/vosdroits/"
DATE, DATE_FR = "2026-10-10", "10 octobre 2026"
CSS_VERSION = 26

APP_COVERS = {"naturalisation_decret", "reintegration_decret"}

TITLE = "Quelle voie pour devenir français ? Le test d'orientation"
DESC = ("Naturalisation, mariage, ascendant, frère ou sœur, tribunal : répondez à quelques "
        "questions pour savoir quelle voie mène à la nationalité française dans votre cas.")

# Ordre d'affichage des fiches = ordre des cles.
VOIES = {
    "naturalisation_decret": {
        "title": "Naturalisation par décret",
        "who": "Vous vivez en France depuis 5 ans en principe (moins dans certains cas), avec un titre de séjour.",
        "facts": [("Où déposer", "En ligne, sur l'ANEF (au consulat si vous vivez à l'étranger)"),
                  ("Français", "Niveau B2 à l'oral et à l'écrit"),
                  ("Examen civique", "Oui, 32 bonnes réponses sur 40"),
                  ("Entretien", "Oui, à la plateforme de naturalisation"),
                  ("Délai légal", "18 mois après le récépissé, 12 si vous vivez en France depuis 10 ans"),
                  ("Coût", "Timbre fiscal de 255 €")],
        "href": "/blog/conditions-naturalisation-francaise.html", "guide": "Les conditions de la naturalisation",
        "sp": "F2213",
    },
    "reintegration_decret": {
        "title": "Réintégration par décret",
        "who": "Vous avez été français·e et vous avez perdu la nationalité, hors des cas de la réintégration par déclaration.",
        "facts": [("Où déposer", "En ligne, sur l'ANEF"),
                  ("Français", "Niveau B2 à l'oral et à l'écrit"),
                  ("Examen civique", "Oui"),
                  ("Entretien", "Oui"),
                  ("Durée de résidence", "Aucune exigée"),
                  ("Coût", "Timbre fiscal de 255 €")],
        "href": "/blog/reintegration-nationalite-francaise-2026.html", "guide": "Le guide de la réintégration",
        "sp": "F2214",
    },
    "declaration_mariage": {
        "title": "Déclaration par mariage",
        "who": "Marié·e à un·e Français·e depuis 4 ans (5 ans dans certains cas), avec une communauté de vie.",
        "facts": [("Où déposer", "Sur papier, à la plateforme de naturalisation (au consulat si vous vivez à l'étranger)"),
                  ("Français", "Niveau B2 à l'oral et à l'écrit"),
                  ("Examen civique", "Non"),
                  ("Entretien", "Oui, avec votre conjoint·e"),
                  ("Délai légal", "1 an après le récépissé de fin d'entretien, 2 ans en cas d'opposition"),
                  ("Coût", "Timbre fiscal de 255 €")],
        "href": "/blog/naturalisation-par-mariage-2026.html", "guide": "Le guide de la déclaration par mariage",
        "sp": "F2726",
    },
    "declaration_ascendant": {
        "title": "Déclaration de l'ascendant d'un Français",
        "who": "65 ans ou plus, 25 ans de résidence régulière en France, et un enfant ou petit-enfant français.",
        "facts": [("Où déposer", "Sur papier, à la plateforme de naturalisation"),
                  ("Français", "Aucun niveau exigé"),
                  ("Examen civique", "Non"),
                  ("Entretien", "Oui, sans test de langue"),
                  ("Délai légal", "1 an après le récépissé de fin d'entretien, 2 ans en cas d'opposition"),
                  ("Coût", "Timbre fiscal de 255 €")],
        "href": "/blog/declaration-nationalite-ascendant-frere-soeur.html", "guide": "La déclaration pas à pas",
        "sp": "F33430",
    },
    "declaration_fratrie": {
        "title": "Déclaration du frère ou de la sœur d'un Français",
        "who": "18 ans ou plus, en France depuis vos 6 ans, scolarité obligatoire en France, et un frère ou une sœur né en France devenu français.",
        "facts": [("Où déposer", "Sur papier, à la plateforme de naturalisation"),
                  ("Français", "Aucun niveau exigé"),
                  ("Examen civique", "Non"),
                  ("Entretien", "Oui, sans test de langue"),
                  ("Délai légal", "1 an après le récépissé de fin d'entretien, 2 ans en cas d'opposition"),
                  ("Coût", "Timbre fiscal de 255 €")],
        "href": "/blog/declaration-nationalite-ascendant-frere-soeur.html", "guide": "La déclaration pas à pas",
        "sp": "F33800",
    },
    "declaration_mineur_ne_en_france": {
        "title": "Déclaration d'un enfant né en France",
        "who": "Enfant né en France de parents étrangers, de 13 à 17 ans, qui a vécu 5 ans en France depuis ses 8 ans (ou ses 11 ans à partir de 16 ans).",
        "facts": [("Où déposer", "Au tribunal judiciaire du domicile, sur papier libre"),
                  ("Français", "Aucun niveau exigé"),
                  ("Examen civique", "Non"),
                  ("Entretien", "De 13 à 15 ans, l'enfant, pour recueillir son accord"),
                  ("Délai légal", "6 mois après le récépissé"),
                  ("Coût", "Gratuit")],
        "href": "/blog/declaration-nationalite-tribunal-judiciaire.html", "guide": "Les déclarations au tribunal",
        "sp": "F295",
    },
    "declaration_adoption_recueil": {
        "title": "Déclaration de l'enfant adopté ou recueilli",
        "who": "Mineur adopté en adoption simple par un·e Français·e, recueilli et élevé par un·e Français·e depuis 3 ans, ou confié à l'aide sociale à l'enfance depuis 3 ans.",
        "facts": [("Où déposer", "Au tribunal judiciaire du domicile (au consulat à l'étranger)"),
                  ("Français", "Aucun niveau exigé"),
                  ("Examen civique", "Non"),
                  ("Délai légal", "6 mois après le récépissé"),
                  ("Coût", "Gratuit")],
        "href": "/blog/declaration-nationalite-tribunal-judiciaire.html", "guide": "Les déclarations au tribunal",
        "sp": "F3070",
    },
    "declaration_possession_etat": {
        "title": "Déclaration de possession d'état de Français",
        "who": "Vous avez été traité·e comme Français·e (papiers, vote…) pendant les 10 années précédant la déclaration.",
        "facts": [("Où déposer", "Au tribunal judiciaire du domicile"),
                  ("Français", "Aucun niveau exigé"),
                  ("Examen civique", "Non"),
                  ("Délai légal", "6 mois après le récépissé"),
                  ("Coût", "Gratuit")],
        "href": "/blog/declaration-nationalite-tribunal-judiciaire.html", "guide": "Les déclarations au tribunal",
        "sp": "F34717",
    },
    "reintegration_declaration": {
        "title": "Réintégration par déclaration",
        "who": "Nationalité perdue par mariage avec un·e étranger·ère, en prenant volontairement une autre nationalité, ou après un mandat public ; des liens manifestes avec la France.",
        "facts": [("Où déposer", "Au tribunal judiciaire du domicile (au consulat à l'étranger)"),
                  ("Français", "Aucun niveau exigé"),
                  ("Examen civique", "Non"),
                  ("Délai légal", "6 mois après le récépissé")],
        "href": "/blog/reintegration-nationalite-francaise-2026.html", "guide": "Le guide de la réintégration",
        "sp": "F3071",
    },
    "attribution_cnf": {
        "title": "Certificat de nationalité française",
        "who": "Un parent français à votre naissance, une naissance en France d'un parent lui-même né en France, ou 5 ans en France depuis vos 11 ans à votre majorité : vous êtes sans doute déjà français·e.",
        "facts": [("Démarche", "Pas de demande de nationalité : un certificat qui prouve que vous l'êtes déjà"),
                  ("Où demander", "Au tribunal judiciaire du domicile"),
                  ("Coût", "Gratuit")],
        "href": "/glossaire/cnf.html", "guide": "Le certificat de nationalité en détail",
        "sp": "F1051",
    },
}

KIND_LABEL = {
    "pick": "Votre voie",
    "not_yet": "Pas encore, mais votre voie existe",
    "cnf": "Vous êtes peut-être déjà français·e",
}

FAQ = [
    ("Quelles sont les voies pour devenir français ?",
     "Il en existe une dizaine. La plus connue est la naturalisation par décret, mais on devient aussi français "
     "par déclaration : par mariage, comme ascendant, frère ou sœur d'un Français, ou au tribunal pour un enfant "
     "né en France, un enfant adopté ou recueilli, la possession d'état et la réintégration. Certaines personnes "
     "sont déjà françaises sans le savoir : elles ont seulement un certificat de nationalité à demander."),
    ("Quelle différence entre naturalisation et déclaration de nationalité ?",
     "La naturalisation par décret est une faveur : l'administration peut la refuser même si les conditions sont "
     "remplies. La déclaration est un droit : si les conditions sont remplies, elle est enregistrée, et sans refus "
     "dans le délai légal, elle doit l'être."),
    ("Le mariage avec un Français donne-t-il la nationalité ?",
     "Pas automatiquement. Après 4 ans de mariage (5 ans dans certains cas, notamment sans 3 ans de résidence "
     "continue en France depuis le mariage) et avec une communauté de vie, vous pouvez faire une déclaration de "
     "nationalité. Elle exige le niveau B2, mais pas l'examen civique."),
    ("Faut-il passer l'examen civique pour toutes les voies ?",
     "Non. Depuis le 1er janvier 2026, l'examen civique n'est exigé que pour la naturalisation et la réintégration "
     "par décret. Le niveau B2 est exigé pour ces deux voies et pour la déclaration par mariage ; les autres "
     "déclarations ne demandent aucun niveau de langue."),
    ("Né en France, suis-je français ?",
     "Pas forcément. Si l'un de vos parents est lui-même né en France, vous êtes français de naissance. Sinon, vous "
     "le devenez automatiquement à 18 ans si vous résidez en France et y avez vécu 5 ans depuis vos 11 ans ; avant "
     "cet âge, une déclaration au tribunal est possible dès 13 ans."),
    ("Le résultat du test a-t-il une valeur officielle ?",
     "Non. Le test vous oriente vers la voie qui correspond le mieux à votre situation, d'après les fiches de "
     "service-public.fr ; seule l'administration, au vu de votre dossier, se prononce. Vérifiez toujours la fiche "
     "officielle de votre voie avant de déposer."),
]

SOURCES = [
    (SP + "F34717", "Service-public.gouv.fr — Comment obtenir la nationalité française ? (F34717)"),
    (SP + "F2213", "Service-public.gouv.fr — Naturalisation par décret (F2213)"),
    (SP + "F2726", "Service-public.gouv.fr — Déclaration de nationalité par mariage (F2726)"),
    (SP + "F39426", "Service-public.gouv.fr — Examen civique (F39426)"),
    (SP + "F1051", "Service-public.gouv.fr — Certificat de nationalité française (F1051)"),
]


# ─── l'arbre ─────────────────────────────────────────────────────────────────
def load_tree():
    tree = json.loads(TREE.read_text(encoding="utf-8"))
    questions = {q["id"]: q for q in tree["questions"]}
    results = tree["results"]
    results = {r["id"]: r for r in results} if isinstance(results, list) else results
    return tree["start"], questions, results


def check_tree(start, questions, results):
    """Chaque branche mene a une question ou a un resultat connus, sans boucle,
    et chaque resultat nomme une voie decrite ici."""
    assert start in questions, start
    seen_q, seen_r = set(), set()

    def walk(qid, trail):
        assert qid not in trail, f"boucle : {' > '.join(trail + [qid])}"
        seen_q.add(qid)
        for o in questions[qid]["options"]:
            nxt = o["next"]
            if nxt.startswith("result:"):
                rid = nxt[7:]
                assert rid in results, f"résultat inconnu : {rid}"
                seen_r.add(rid)
            else:
                assert nxt in questions, f"question inconnue : {nxt}"
                walk(nxt, trail + [qid])

    walk(start, [])
    assert seen_q == set(questions), f"questions orphelines : {set(questions) - seen_q}"
    assert seen_r == set(results), f"résultats orphelins : {set(results) - seen_r}"
    for r in results.values():
        assert r["kind"] in KIND_LABEL, r["kind"]
        assert r["procedure"] in VOIES, f"voie sans fiche : {r['procedure']}"
        for alt in r.get("alternatives", []):
            assert alt in VOIES, alt
        for alts in r.get("flag_alternatives", {}).values():
            for alt in alts:
                assert alt in VOIES, alt


def depth(start, questions):
    def d(qid):
        return 1 + max((d(o["next"]) for o in questions[qid]["options"]
                        if not o["next"].startswith("result:")), default=0)
    return d(start)


# ─── rendu ───────────────────────────────────────────────────────────────────
def e(s):
    return html.escape(s, quote=False)


def typo(fragment):
    """Espaces insecables de la typographie francaise, hors balises."""
    parts = re.split(r"(<[^>]+>)", fragment)
    for i, p in enumerate(parts):
        if not p.startswith("<"):
            parts[i] = re.sub(r" ([:;?!»])", " \\1", p).replace("« ", "« ")
    return "".join(parts)


def facts_dl(facts):
    return "<dl>" + "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in facts) + "</dl>"


def voie_card(pid, v):
    links = [f'<a href="{v["href"]}">{e(v["guide"])} &rarr;</a>',
             f'<a href="{SP}{v["sp"]}" target="_blank" rel="noopener">Fiche officielle ({v["sp"]})</a>']
    return f"""    <div class="pf-key voie-card" id="voie-{pid.replace('_', '-')}">
      <h3>{e(v["title"])}</h3>
      <p class="voie-who">{e(v["who"])}</p>
      {facts_dl(v["facts"])}
      <p class="voie-links">{' &middot; '.join(links)}</p>
    </div>"""


def tree_outline(start, questions, results):
    """L'arbre en listes imbriquees : lisible sans JavaScript, et par les moteurs."""
    def node(qid):
        q = questions[qid]
        items = []
        for o in q["options"]:
            label = e(o["title"]) + (f' <span class="voie-sub-inline">({e(o["subtitle"])})</span>' if o.get("subtitle") else "")
            nxt = o["next"]
            if nxt.startswith("result:"):
                r = results[nxt[7:]]
                v = VOIES[r["procedure"]]
                items.append(f'<li>{label} &rarr; <a href="#voie-{r["procedure"].replace("_", "-")}">'
                             f'{e(v["title"])}</a>{"" if r["kind"] == "pick" else " (" + e(KIND_LABEL[r["kind"]].lower()) + ")"}</li>')
            else:
                items.append(f"<li>{label}<ul>{node(nxt)}</ul></li>")
        return f'<li><strong>{e(q["question"])}</strong><ul>{"".join(items)}</ul></li>'
    return f'<ul class="voie-tree">{node(start)}</ul>'


def js_payload(start, questions, results):
    tree = {"start": start,
            "questions": [{"id": q["id"], "question": q["question"], "help": q.get("help"),
                           "options": [{"title": o["title"], "subtitle": o.get("subtitle"),
                                        "next": o["next"], "sets": o.get("sets", [])} for o in q["options"]]}
                          for q in questions.values()],
            "results": {rid: {"kind": r["kind"], "procedure": r["procedure"], "reason": r["reason"],
                              "alternatives": r.get("alternatives", []),
                              "flag_alternatives": r.get("flag_alternatives", {}),
                              "flag_reasons": r.get("flag_reasons", {})} for rid, r in results.items()}}
    voies = {pid: {"title": v["title"], "facts": v["facts"], "href": v["href"], "guide": v["guide"],
                   "sp": SP + v["sp"], "app": pid in APP_COVERS} for pid, v in VOIES.items()}
    dump = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    return dump(tree), dump(voies), dump(KIND_LABEL)


SCRIPT = r"""
(function () {
  var T = __TREE__, V = __VOIES__, K = __KINDS__, APP = "__APP__";
  var Q = {}; T.questions.forEach(function (q) { Q[q.id] = q; });
  var path = [];
  function $(id) { return document.getElementById(id); }
  function esc(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : s; return d.innerHTML; }
  function show(id) {
    ['voie-start', 'voie-quiz', 'voie-result'].forEach(function (x) { $(x).style.display = x === id ? '' : 'none'; });
  }
  function ask(qid) {
    var q = Q[qid]; show('voie-quiz');
    $('voie-step').textContent = 'Question ' + (path.length + 1);
    $('voie-question').textContent = q.question;
    var h = $('voie-help'); h.textContent = q.help || ''; h.style.display = q.help ? '' : 'none';
    var box = $('voie-options'); box.innerHTML = '';
    q.options.forEach(function (o) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'qcm-opt';
      b.innerHTML = esc(o.title) + (o.subtitle ? '<span class="voie-sub">' + esc(o.subtitle) + '</span>' : '');
      b.onclick = function () { path.push({ q: qid, sets: o.sets || [] }); go(o.next); };
      box.appendChild(b);
    });
    $('voie-back').disabled = path.length === 0;
    $('voie-question').focus();
  }
  function go(next) { if (next.indexOf('result:') === 0) { result(next.slice(7)); } else { ask(next); } }
  function flags() { var f = {}; path.forEach(function (s) { s.sets.forEach(function (x) { f[x] = true; }); }); return f; }
  function voieLink(pid) { var v = V[pid]; return '<a href="' + v.href + '">' + esc(v.title) + '</a>'; }
  function result(rid) {
    var r = T.results[rid], v = V[r.procedure], f = flags(), out = '';
    out += '<div class="voie-kind">' + esc(K[r.kind]) + '</div>';
    out += '<h3>' + esc(v.title) + '</h3>';
    out += '<p class="voie-reason">' + esc(r.reason) + '</p>';
    out += '<div class="pf-key"><dl>' + v.facts.map(function (x) {
      return '<dt>' + esc(x[0]) + '</dt><dd>' + esc(x[1]) + '</dd>'; }).join('') + '</dl></div>';
    Object.keys(r.flag_reasons).forEach(function (fl) {
      if (!f[fl]) { return; }
      out += '<p class="voie-alt">' + esc(r.flag_reasons[fl]) + ' ' +
        (r.flag_alternatives[fl] || []).map(voieLink).join(', ') + '</p>';
    });
    if (r.alternatives.length) {
      out += '<p class="voie-alt">À comparer aussi : ' + r.alternatives.map(voieLink).join(', ') + '.</p>';
    }
    out += '<p class="voie-links"><a class="qcm-btn primary" href="' + v.href + '">' + esc(v.guide) + ' &rarr;</a> ' +
      '<a class="qcm-btn" href="' + v.sp + '" target="_blank" rel="noopener">Fiche officielle</a></p>';
    if (v.app) {
      out += '<p class="voie-app"><a href="' + APP + '" target="_blank" rel="noopener">Préparer cette demande avec l’app Naturalisation France Facile &rarr;</a></p>';
    }
    out += '<p class="voie-note">Une orientation, pas une décision : seule l’administration, au vu de votre dossier, se prononce.</p>';
    $('voie-resultbody').innerHTML = out;
    show('voie-result');
    $('voie-resultbody').focus();
  }
  $('voie-startbtn').onclick = function () { path = []; ask(T.start); };
  $('voie-back').onclick = function () { var last = path.pop(); if (last) { ask(last.q); } };
  $('voie-restart').onclick = function () { path = []; ask(T.start); };
  $('voie-resultback').onclick = function () { var last = path.pop(); if (last) { ask(last.q); } };
})();
"""


def ld(obj):
    return ('  <script type="application/ld+json">\n  '
            + json.dumps(obj, ensure_ascii=False, indent=2).replace("\n", "\n  ")
            + "\n  </script>\n")


def render(start, questions, results):
    page_ld = {"@context": "https://schema.org", "@type": "WebPage", "inLanguage": "fr-FR",
               "name": TITLE, "description": DESC, "url": URL, "dateModified": DATE,
               "isPartOf": {"@type": "WebSite", "name": "Naturalisation France Facile", "url": BASE}}
    crumbs_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{BASE}/"},
        {"@type": "ListItem", "position": 2, "name": "Outils", "item": f"{BASE}/outils/"},
        {"@type": "ListItem", "position": 3, "name": "Quelle voie pour devenir français ?"}]}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}

    src = NAV_FROM.read_text(encoding="utf-8")
    head_top = src[:src.index("  <title>")]
    nav = re.search(r'<nav class="nav">.*?</nav>', src, re.S).group(0)
    footer = re.search(r'<footer class="footer">.*?</footer>', src, re.S).group(0)

    tree_js, voies_js, kinds_js = js_payload(start, questions, results)
    script = (SCRIPT.replace("__TREE__", tree_js).replace("__VOIES__", voies_js)
              .replace("__KINDS__", kinds_js).replace("__APP__", APP))
    cards = "\n".join(voie_card(pid, v) for pid, v in VOIES.items())
    faq_html = "\n".join(
        f'      <div class="faq-item">\n        <div class="faq-q" onclick="this.parentElement.classList.toggle(\'open\')">{e(q)}</div>\n'
        f'        <div class="faq-a">{e(a)}</div>\n      </div>' for q, a in FAQ)
    sources_html = "\n".join(f'        <li><a href="{h}" target="_blank" rel="noopener">{e(t)}</a></li>' for h, t in SOURCES)

    return f"""{head_top}  <title>{e(TITLE)}</title>
  <meta name="description" content="{e(DESC)}" />
  <link rel="canonical" href="{URL}" />
  <meta property="og:title" content="{e(TITLE)}" />
  <meta property="og:description" content="{e(DESC)}" />
  <meta property="og:url" content="{URL}" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="fr_FR" />
  <meta property="og:site_name" content="Naturalisation France Facile" />
  <meta property="og:image" content="{BASE}/img/og/default.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{BASE}/img/og/default.png" />
  <link rel="stylesheet" href="/css/style.css?v={CSS_VERSION}" />
{ld(page_ld)}{ld(crumbs_ld)}{ld(faq_ld)}</head>
<body>

{nav}

<section class="section" style="padding-top:120px">
  <p class="article-back"><a href="/outils/">&larr; Tous les outils</a></p>
  <h1 class="section-title">Quelle voie pour devenir fran&ccedil;ais&nbsp;?</h1>
  <p class="section-sub">{typo(e("La naturalisation par décret n'est qu'une des voies vers la nationalité française. Mariage, famille, naissance en France, adoption : répondez aux questions, une à la fois, et le test vous indique la vôtre — ou vous dit si vous êtes déjà français·e."))}</p>
  <p class="updated-note" style="text-align:center">Mis &agrave; jour le {DATE_FR} &middot; les m&ecirc;mes questions que l'orienteur de l'app</p>

  <div class="qcm" id="voie">
    <div class="qcm-card" id="voie-start">
      <div class="qcm-q" style="margin-bottom:14px">{typo(e("Trouvons la voie qui correspond à votre situation"))}</div>
      <p class="voie-help" style="margin:0 0 20px">{typo(e("Sans inscription, rien n'est enregistré. Le test s'arrête dès que votre voie est trouvée."))}</p>
      <button class="qcm-btn primary" id="voie-startbtn" type="button">Commencer &rarr;</button>
      <noscript><p class="voie-note">{typo(e("Le test interactif demande JavaScript. Sans lui, l'arbre complet et la fiche de chaque voie sont juste en dessous."))}</p></noscript>
    </div>
    <div class="qcm-card" id="voie-quiz" style="display:none">
      <div class="qcm-bar"><span class="qcm-progress" id="voie-step"></span></div>
      <div class="qcm-q" id="voie-question" tabindex="-1"></div>
      <p class="voie-help" id="voie-help"></p>
      <div id="voie-options"></div>
      <div class="qcm-nav">
        <button class="qcm-btn" id="voie-back" type="button">&larr; Retour</button>
        <button class="qcm-btn" id="voie-restart" type="button">Recommencer</button>
      </div>
    </div>
    <div class="qcm-card voie-result" id="voie-result" style="display:none">
      <div id="voie-resultbody" tabindex="-1"></div>
      <div class="qcm-nav">
        <button class="qcm-btn" id="voie-resultback" type="button">&larr; Modifier ma derni&egrave;re r&eacute;ponse</button>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <h2 class="section-title">Toutes les voies, en un coup d'&oelig;il</h2>
  <p class="section-sub">{typo(e("Où déposer, quel niveau de français, quel examen, quel délai : la fiche de chaque voie, d'après service-public.fr."))}</p>
  <div class="voie-list">
{typo(cards)}
  </div>
</section>

<section class="section">
  <div class="article-body">
    <h2>Le test, question par question</h2>
    <p>{typo(e("Le test suit l'ordre de la fiche officielle « Comment obtenir la nationalité française ? » : d'abord ce qui fait de vous un Français de naissance, puis les déclarations, et la naturalisation en dernier. Voici l'arbre complet."))}</p>
    <details class="voie-details">
      <summary>Voir toutes les questions et leurs r&eacute;ponses</summary>
      {typo(tree_outline(start, questions, results))}
    </details>

    <h2>Questions fr&eacute;quentes</h2>
    <div class="faq-list">
{typo(faq_html)}
    </div>

    <h2>Sources officielles</h2>
    <ul>
{sources_html}
    </ul>
  </div>
</section>

{footer}
<script>{script}</script>
</body></html>
"""


def main():
    start, questions, results = load_tree()
    check_tree(start, questions, results)
    page = render(start, questions, results)
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        json.loads(block)
        assert not re.search(r"&[a-zA-Z]{2,8};", block), "entité HTML dans le JSON-LD"
    assert len(TITLE) <= 62, len(TITLE)
    assert 110 <= len(DESC) <= 170, len(DESC)
    for href in set(re.findall(r'href="(/[^"#?]*)', page)):
        target = ROOT / href.lstrip("/")
        assert target.exists() or (target / "index.html").exists() or target == OUT, href
    OUT.write_text(page, encoding="utf-8")
    words = len(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<nav.*?</nav>|<footer.*?</footer>", "", page, flags=re.S)).split())
    print(f"  {words} mots · {len(questions)} questions (au plus {depth(start, questions)} par parcours) · "
          f"{len(results)} résultats · {len(VOIES)} voies · {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
