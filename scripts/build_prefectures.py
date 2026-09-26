#!/usr/bin/env python3
"""Genere la rubrique /prefectures/ : ou deposer son dossier de naturalisation.

    python3 scripts/build_prefectures.py

Produit :
  prefectures/index.html        l'accueil : recherche par departement, code
                                postal ou ville, carte des plateformes, tableau
                                des 101 departements.
  prefectures/<dep>-<code>.html une page par departement (101) : la plateforme
                                qui instruit, ses coordonnees verifiees, le
                                depot (decret et mariage), les etapes, les
                                pieces, les centres d'examen civique et TCF du
                                departement, les delais, l'app.
  prefectures/carte.svg         les contours (une <g id="fr"> de <path
                                id="d-XX">) que les mini-cartes des pages
                                reutilisent par <use>.
  sitemap.xml                   les 102 URL sont remplacees a chaque passage.

NE PAS EDITER LE HTML GENERE A LA MAIN : il est ecrase a chaque passage.
Les coordonnees viennent de data/prefectures/plateformes.json, copie de
l'annuaire verifie de l'app iOS : une correction se fait dans l'app, puis
`python3 scripts/refresh_prefectures_data.py`, puis ce script. Ce qui est
editorial (ville de la plateforme, modalites des declarations tirees de la
carte du ministere, mises en garde) est dans PLATEFORMES ci-dessous.
"""

import html
import json
import pathlib
import re
import unicodedata
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "prefectures"
OUT = ROOT / "prefectures"
BASE = "https://naturalisationfrancefacile.fr"
APP = "https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087"
DELF = "https://delf-tcf-tef.fr"
ANEF = "https://administration-etrangers-en-france.interieur.gouv.fr/particuliers/"
CCC_FORM = "https://contacts-demarches.interieur.gouv.fr"
CARTE_DGEF = "https://macarte.ign.fr/carte/e33e5b949d3c8ff991adc1c67aa0b28c/Plateformes-Naturalisation"
SP_DECRET = "https://www.service-public.gouv.fr/particuliers/vosdroits/F2213"
SP_MARIAGE = "https://www.service-public.gouv.fr/particuliers/vosdroits/F2726"
SP_CEREMONIE = "https://www.service-public.gouv.fr/particuliers/vosdroits/F15868"
LF_DELAIS = "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070721/LEGISCTA000006165459"
LF_CEREMONIE = "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070721/LEGISCTA000006165461"
TODAY = "2026-09-26"
TODAY_FR = "26 septembre 2026"
CSS_V = 25

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]


def date_fr(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{'1er' if d == 1 else d} {MOIS[m - 1]} {y}"


# ─── données ─────────────────────────────────────────────────────────────────
def load(name):
    return json.load(open(DATA / name, encoding="utf-8"))


DEPS = load("departements.json")["departements"]
DEP = {d["code"]: d for d in DEPS}
PF_JSON = load("plateformes.json")
VERIFIE = date_fr(PF_JSON["checkedOn"])                   # 21 septembre 2026
DGEF = load("carte_dgef.json")
DGEF_DU = date_fr(DGEF["donnees_du"])                     # 3 octobre 2025
CENTRES = load("centres.json")
CENTRES_DU = date_fr(CENTRES["releve_le"])                # 19 septembre 2026
CARTE = load("carte_paths.json")

POST = ("par courrier recommandé avec avis de réception", None)

# Ce que l'annuaire de l'app ne dit pas : la ville, la façon de nommer l'hôte, la
# modalité de dépôt des déclarations (carte du ministère, données du 3 octobre 2025,
# ou site de la préfecture quand il est plus récent), l'accueil, les permanences et
# les mises en garde. Chaque valeur est tirée d'une source citée sur la page.
PLATEFORMES = {
    "prefecture-de-police": dict(
        ville="Paris", hote="la préfecture de police", titre="préfecture de police",
        decl=POST,
        notes=["À Paris, les naturalisations ne relèvent pas d'une préfecture de département mais de la "
               "<strong>préfecture de police</strong> (direction de la police générale, 1er bureau)."]),
    "hauts-de-seine": dict(
        ville="Nanterre", hote="la préfecture des Hauts-de-Seine", titre="préfecture de Nanterre",
        decl=("au guichet, sur rendez-vous pris sur le site de la préfecture",
              "https://www.hauts-de-seine.gouv.fr/Demarches-administratives/Etrangers-en-France/NATURALISATION"),
        accueil="167 avenue Joliot-Curie, Nanterre"),
    "seine-saint-denis": dict(
        ville="Bobigny", hote="la préfecture de la Seine-Saint-Denis", titre="préfecture de Bobigny",
        decl=("uniquement sur rendez-vous, à prendre en ligne sur le site de la préfecture",
              "https://www.seine-saint-denis.gouv.fr/Prendre-un-rendez-vous"),
        accueil="1 esplanade Jean-Moulin, Bobigny", tel="01 84 21 27 60",
        notes=["La préfecture publie <strong>deux adresses distinctes</strong> : "
               "celle ci-dessus pour les demandes par décret, et "
               "<a href=\"mailto:pref-naturalisations-declaration@seine-saint-denis.gouv.fr\">"
               "pref-naturalisations-declaration@seine-saint-denis.gouv.fr</a> pour les déclarations "
               "(mariage). Écrire à la mauvaise boîte retarde la réponse."]),
    "val-de-marne": dict(
        ville="Créteil", hote="la préfecture du Val-de-Marne", titre="préfecture de Créteil",
        decl=("sur rendez-vous, à prendre en ligne sur le site de la préfecture",
              "https://www.val-de-marne.gouv.fr/booking/create/4963"),
        accueil="21-29 avenue du Général-de-Gaulle, Créteil"),
    "val-doise": dict(
        ville="Cergy", hote="la préfecture du Val-d'Oise", titre="préfecture de Cergy",
        decl=POST, accueil="5 avenue Bernard-Hirsch, Cergy", tel="01 34 20 95 95",
        horaires="accueil du service des naturalisations de 9 h à 12 h et de 13 h 15 à 16 h",
        email_note="Adresse publiée sur l'ancien domaine « .pref.gouv.fr » (fiche de l'annuaire officiel "
                   "mise à jour en août 2024) : vérifiez-la sur le site de la préfecture avant un envoi important."),
    "essonne": dict(
        ville="Évry-Courcouronnes", court="Évry", hote="la préfecture de l'Essonne", titre="préfecture d'Évry",
        decl=("sur rendez-vous, à prendre en ligne sur le site de la préfecture",
              "https://www.essonne.gouv.fr/booking/create/23014/"),
        accueil="boulevard de France, Évry-Courcouronnes"),
    "yvelines": dict(
        ville="Saint-Germain-en-Laye", hote="la sous-préfecture de Saint-Germain-en-Laye",
        titre="plateforme de Saint-Germain",
        decl=("sur rendez-vous, à prendre sur le site de la préfecture des Yvelines", "https://www.yvelines.gouv.fr/"),
        accueil="1 rue du Panorama, Saint-Germain-en-Laye", tel="01 30 61 34 00",
        permanence="du lundi au vendredi, de 14 h à 16 h",
        notes=["La plateforme des Yvelines <strong>n'est pas à Versailles</strong> : elle est installée à la "
               "sous-préfecture de Saint-Germain-en-Laye."]),
    "seine-et-marne": dict(
        ville="Torcy", hote="la sous-préfecture de Torcy", titre="sous-préfecture de Torcy",
        decl=("sur rendez-vous, à prendre en ligne sur le site de la préfecture",
              "https://www.seine-et-marne.gouv.fr/booking/create/48803"),
        accueil="7 rue Gérard-Philipe, Torcy",
        notes=["Les naturalisations de Seine-et-Marne ne sont pas instruites à Melun, siège de la préfecture, "
               "mais à la <strong>sous-préfecture de Torcy</strong>."]),
    "meurthe-et-moselle": dict(
        ville="Nancy", hote="la préfecture de Meurthe-et-Moselle", exreg="Lorraine", decl=POST,
        accueil="6 rue Sainte-Catherine, Nancy", tel="03 83 34 22 13",
        permanence="lundi, mardi et jeudi, de 8 h 30 à 11 h 30"),
    "marne": dict(
        ville="Reims", hote="la sous-préfecture de Reims", exreg="Champagne-Ardenne", decl=POST,
        accueil="place Royale, Reims",
        notes=["La plateforme est installée à la <strong>sous-préfecture de Reims</strong>, et non à la "
               "préfecture de la Marne, à Châlons-en-Champagne."]),
    "bas-rhin": dict(
        ville="Strasbourg", hote="la préfecture du Bas-Rhin", exreg="Alsace", decl=POST,
        accueil="5 place de la République, Strasbourg",
        notes=["Attention à l'orthographe du courriel : <strong>pref-naturalisation@</strong>, au singulier, "
               "sans « s »."]),
    "doubs": dict(
        ville="Besançon", hote="la préfecture du Doubs", exreg="Franche-Comté", decl=POST,
        accueil="3 avenue de la Gare-d'Eau, Besançon"),
    "cote-dor": dict(
        ville="Dijon", hote="la préfecture de la Côte-d'Or", exreg="Bourgogne", decl=POST,
        notes=["La plateforme a changé d'adresse postale : l'annuaire officiel (mise à jour du 9 juin 2026) "
               "donne le 53 rue de la Préfecture, alors que la carte du ministère affiche encore l'ancienne "
               "Cité Dampierre. C'est la nouvelle adresse qui figure ci-dessus."]),
    "nord": dict(
        ville="Lille", hote="la préfecture du Nord", exreg="Nord-Pas-de-Calais", decl=POST,
        accueil="12 rue Jean-sans-Peur, Lille",
        delai_officiel=("« les procédures de naturalisation durent entre 3 et 4 ans »",
                        "https://www.nord.gouv.fr/Demarches/Naturalisation-dans-le-Nord"),
        notes=["La préfecture du Nord ne publie pas de courriel pour sa plateforme : les demandes de pièces "
               "passent par votre espace ANEF, et elle précise qu'il n'est pas nécessaire de la solliciter "
               "pendant l'instruction pour connaître l'avancement du dossier."]),
    "oise": dict(
        ville="Beauvais", hote="la préfecture de l'Oise", exreg="Picardie", decl=POST,
        accueil="Espace Europe, 2 avenue de l'Europe, Beauvais", tel="03 44 06 10 84",
        permanence="lundi et jeudi, de 14 h à 16 h",
        notes=["Le courriel de la plateforme n'a pas le préfixe « pref- » habituel : "
               "<strong>naturalisations@oise.gouv.fr</strong>."]),
    "seine-maritime": dict(
        ville="Rouen", hote="la préfecture de la Seine-Maritime", exreg="Haute-Normandie", decl=POST,
        accueil="7 place de la Madeleine, Rouen"),
    "calvados": dict(
        ville="Caen", hote="la préfecture du Calvados", exreg="Basse-Normandie", decl=POST,
        accueil="rue Daniel-Huet, Caen", tel="02 31 30 64 00"),
    "ille-et-vilaine": dict(
        ville="Rennes", hote="la préfecture d'Ille-et-Vilaine", exreg="Bretagne", decl=POST,
        accueil="3 avenue de la Préfecture, Rennes",
        notes=["La Loire-Atlantique n'en fait pas partie : elle relève de la plateforme de Nantes."]),
    "loire-atlantique": dict(
        ville="Nantes", hote="la préfecture de la Loire-Atlantique", exreg="Pays de la Loire", decl=POST,
        accueil="6 quai Ceineray, Nantes",
        notes=["Ne confondez pas la plateforme de Nantes avec la SDANF, le service du ministère installé à "
               "Rezé, à côté de Nantes : la plateforme instruit votre dossier, la SDANF décide ensuite, pour "
               "toute la France."]),
    "indre-et-loire": dict(
        ville="Tours", hote="la préfecture d'Indre-et-Loire", exreg="Centre-Val de Loire", decl=POST,
        accueil="15 rue Bernard-Palissy, Tours"),
    "deux-sevres": dict(
        ville="Niort", hote="la préfecture des Deux-Sèvres", exreg="Poitou-Charentes", decl=POST,
        accueil="4 rue Duguesclin, Niort"),
    "gironde": dict(
        ville="Bordeaux", hote="la préfecture de la Gironde", exreg="Aquitaine", decl=POST,
        accueil="rue Claude-Bonnier, Bordeaux"),
    "haute-vienne": dict(
        ville="Limoges", hote="la préfecture de la Haute-Vienne", exreg="Limousin", decl=POST,
        accueil="12 rue des Combes, Limoges", tel="05 55 44 18 00", permanence="mardi et vendredi, de 9 h à 12 h"),
    "haute-garonne": dict(
        ville="Toulouse", hote="la préfecture de la Haute-Garonne", exreg="Midi-Pyrénées",
        decl=("par courrier, à une adresse distincte : préfecture de la Haute-Garonne, DMI-Naturalisations, "
              "1 place Saint-Étienne, 31038 Toulouse Cedex 9", None),
        accueil="1 rue Sainte-Anne, Toulouse"),
    "herault": dict(
        ville="Montpellier", hote="la préfecture de l'Hérault", exreg="Languedoc-Roussillon",
        decl=("uniquement au guichet de la préfecture de l'Hérault, sur rendez-vous (rubrique « Prendre "
              "rendez-vous » du site de la préfecture)", "https://www.herault.gouv.fr/"),
        accueil="place des Martyrs-de-la-Résistance, Montpellier",
        email_note="Ce courriel figure sur la fiche de la plateforme dans l'annuaire officiel (2024) et sur la "
                   "carte du ministère, mais la fiche plus récente de la direction des étrangers (juillet 2026) "
                   "ne propose plus qu'un formulaire de contact. En cas de doute, passez par votre espace ANEF."),
    "puy-de-dome": dict(
        ville="Clermont-Ferrand", hote="la préfecture du Puy-de-Dôme", exreg="Auvergne", decl=POST,
        tel="04 73 98 61 61", permanence="mardi de 14 h à 16 h, jeudi de 9 h à 12 h"),
    "rhone": dict(
        ville="Lyon", hote="la préfecture du Rhône",
        decl=("selon les modalités publiées sur le site de la préfecture du Rhône",
              "https://www.rhone.gouv.fr/Demarches-administratives/Nationalite-francaise"),
        accueil="97 rue Molière, Lyon 3e", tel="04 72 61 61 61",
        notes=["Attention à l'orthographe du courriel : <strong>pref-naturalisation@</strong>, au singulier."]),
    "isere": dict(
        ville="Grenoble", hote="la préfecture de l'Isère",
        decl=("par la démarche en ligne décrite sur le site de la préfecture de l'Isère, qui remplace l'envoi "
              "papier", "https://www.isere.gouv.fr/Demarches-administratives/Immigration-Naturalisation/"
                        "Naturalisation-francaise"),
        accueil="12 place de Verdun, Grenoble",
        notes=["Faute de courriel, le ministère propose aussi un formulaire pour les questions sur un dossier : "
               f"<a href=\"{CCC_FORM}\" rel=\"noopener\">contacts-demarches.interieur.gouv.fr</a>."]),
    "bouches-du-rhone": dict(
        ville="Marseille", hote="la préfecture des Bouches-du-Rhône", decl=POST,
        accueil="66 B rue Saint-Sébastien, Marseille 6e", tel="04 84 35 40 00"),
    "alpes-maritimes": dict(
        ville="Nice", hote="la préfecture des Alpes-Maritimes", decl=POST,
        accueil="CADAM, 147 boulevard du Mercantour, Nice"),
    "haute-corse": dict(
        ville="Bastia", hote="la préfecture de la Haute-Corse", exreg="Corse", decl=POST,
        notes=["Une seule plateforme pour toute l'île : les habitants de Corse-du-Sud, Ajaccio compris, "
               "relèvent de Bastia."]),
    "guadeloupe": dict(
        ville="Pointe-à-Pitre", hote="la sous-préfecture de Pointe-à-Pitre", titre="plateforme de Pointe-à-Pitre",
        decl=("sur rendez-vous (lundi, mardi et jeudi, de 8 h 30 à 11 h 30) ou par courrier recommandé : la "
              "carte du ministère indique les deux, renseignez-vous avant d'envoyer", None),
        tel="05 90 82 68 68",
        notes=["L'adresse postale ci-dessus vient de la carte du ministère ; une autre adresse circule "
               "(rue de la Ville-d'Orly) : vérifiez-la auprès de la sous-préfecture avant un envoi recommandé."]),
    "martinique": dict(
        ville="Fort-de-France", hote="la préfecture de la Martinique", decl=POST,
        accueil="rue Louis-Blanc, Fort-de-France", tel="05 96 39 36 00",
        permanence="lundi, mardi et jeudi, de 14 h 30 à 16 h"),
    "guyane": dict(
        ville="Cayenne", hote="la préfecture de la Guyane", titre="dépôt papier à Cayenne",
        decl=("au guichet de la préfecture, sur rendez-vous", "https://www.guyane.gouv.fr/booking/create/18974"),
        accueil="rue Fiedmond, Cayenne", papier=True,
        notes=["La carte du ministère donne pour code postal « 9307 », manifestement tronqué : nous l'avons "
               "complété en 97307. Confirmez-le auprès de la préfecture avant un envoi recommandé."]),
    "reunion": dict(
        ville="Saint-Denis", hote="la préfecture de La Réunion",
        decl=("sur rendez-vous, à prendre sur rdv-prefecture.interieur.gouv.fr (démarche indiquée sur le site "
              "de la préfecture)", "https://www.reunion.gouv.fr/Demarches/Naturalisation"),
        accueil="6 rue des Messageries, Saint-Denis", tel="02 62 40 77 77",
        permanence="tous les jours sauf le jeudi, de 13 h 45 à 15 h 15",
        decl_src="du site de la préfecture de La Réunion, consulté le 21 septembre 2026"),
    "mayotte": dict(
        ville="Mamoudzou", hote="la préfecture de Mayotte", decl=POST,
        accueil="avenue de la Préfecture, Mamoudzou", tel="02 69 63 50 00", horaires="accueil sur rendez-vous"),
}

TCF_VILLES = {"Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Lille", "Nantes", "Nice",
              "Montpellier", "Strasbourg", "Rennes"}   # pages /centres/tcf-<ville>/ de delf-tcf-tef.fr


# ─── français ────────────────────────────────────────────────────────────────
DANS = {"07": "en Ardèche", "09": "en Ariège", "12": "en Aveyron", "38": "en Isère", "91": "en Essonne",
        "23": "dans la Creuse", "26": "dans la Drôme", "42": "dans la Loire", "50": "dans la Manche",
        "51": "dans la Marne", "55": "dans la Meuse", "58": "dans la Nièvre", "72": "dans la Sarthe",
        "80": "dans la Somme", "86": "dans la Vienne", "75": "à Paris", "976": "à Mayotte",
        "974": "à La Réunion"}
CHEF_LIEU = {"95": "Cergy"}   # la préfecture est à Cergy (chef-lieu de droit : Pontoise)


def forms(d):
    n, t, c = d["nom"], d["tncc"], d["code"]
    if t == 2:
        le, du, dans = f"le {n}", f"du {n}", f"dans le {n}"
    elif t == 3:
        le, du, dans = f"la {n}", f"de la {n}", f"en {n}"
    elif t == 4:
        le, du, dans = f"les {n}", f"des {n}", f"dans les {n}"
    elif t == 5:
        le, du, dans = f"l'{n}", f"de l'{n}", f"dans l'{n}"
    elif t == 1:
        le, du, dans = n, f"d'{n}", f"en {n}"
    else:
        le, du, dans = n, f"de {n}", f"en {n}"
    dans = DANS.get(c, dans)
    return {"le": le, "Le": le[0].upper() + le[1:], "du": du, "dans": dans, "Dans": dans[0].upper() + dans[1:],
            "nom": n, "code": c, "label": f"{n} ({c})", "chef": CHEF_LIEU.get(c, d["chef_lieu"])}


def de_v(v):
    if v.startswith("Le "):
        return "du " + v[3:]
    if v.startswith("Les "):
        return "des " + v[4:]
    return ("d'" if re.match(r"[AEIOUYÉÈÊÂÎ]", v) else "de ") + v


def a_v(v):
    if v.startswith("Le "):
        return "au " + v[3:]
    if v.startswith("Les "):
        return "aux " + v[4:]
    return "à " + v


def hote_a(p):
    """« la préfecture de la Haute-Garonne, à Toulouse » ; sans redite quand l'hôte porte déjà le nom de la ville."""
    return p["hote"] if p["ville"] in p["hote"] else f"{p['hote']}, {a_v(p['ville'])}"


def et(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " et " + items[-1]


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def esc(s):
    return html.escape(s or "", quote=True)


def clean_city(city):   # même règle que delf-tcf-tef.fr (_build/make_centres.py) pour tomber sur ses ancres
    c = re.sub(r"\s*\(.*?\)\s*", "", city)
    c = re.sub(r"\s+cedex.*$", "", c, flags=re.I).strip()
    return c.title() if c.isupper() else c


def page_url(d):
    return f"/prefectures/{slug(d['nom'])}-{d['code'].lower()}.html"


def typo(fragment):
    """Espaces insécables de la typographie française, dans le texte seulement (pas dans les balises)."""
    parts = re.split(r"(<[^>]+>)", fragment)
    for i, p in enumerate(parts):
        if p.startswith("<"):
            continue
        p = re.sub(r" ([:;?!»])", " \\1", p)
        p = p.replace("« ", "« ")
        parts[i] = p
    return "".join(parts)


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).replace(" ", " ").strip()


# ─── plateformes ─────────────────────────────────────────────────────────────
PF = {}
for p in PF_JSON["platforms"]:
    deps = [c for c in p["departements"] if c in DEP]
    if not deps:
        continue   # collectivités d'outre-mer : pas de page (voir l'accueil)
    PF[p["id"]] = {**p, **PLATEFORMES[p["id"]], "deps": deps}

HOST = {"prefecture-de-police": "75", "hauts-de-seine": "92", "seine-saint-denis": "93", "val-de-marne": "94",
        "val-doise": "95", "essonne": "91", "yvelines": "78", "seine-et-marne": "77", "meurthe-et-moselle": "54",
        "marne": "51", "bas-rhin": "67", "doubs": "25", "cote-dor": "21", "nord": "59", "oise": "60",
        "seine-maritime": "76", "calvados": "14", "ille-et-vilaine": "35", "loire-atlantique": "44",
        "indre-et-loire": "37", "deux-sevres": "79", "gironde": "33", "haute-vienne": "87", "haute-garonne": "31",
        "herault": "34", "puy-de-dome": "63", "rhone": "69", "isere": "38", "bouches-du-rhone": "13",
        "alpes-maritimes": "06", "haute-corse": "2B", "guadeloupe": "971", "martinique": "972", "guyane": "973",
        "reunion": "974", "mayotte": "976"}
for pid, p in PF.items():
    p["host"] = HOST[pid]
    assert p["host"] in p["deps"], pid
    p["court"] = p.get("court", p["ville"])

PF_OF = {}
for pid, p in PF.items():
    for c in p["deps"]:
        assert c not in PF_OF, c
        PF_OF[c] = pid
assert set(PF_OF) == set(DEP), set(DEP) ^ set(PF_OF)


def order_deps(codes):
    return sorted(codes, key=lambda c: (len(c) > 2, c.replace("2A", "20A").replace("2B", "20B")))


# ─── centres d'examen ────────────────────────────────────────────────────────
CIV, TCF = defaultdict(list), defaultdict(list)
for c in CENTRES["civique"]:
    CIV[c["dep"]].append(c)
for c in CENTRES["tcf"]:
    TCF[c["dep"]].append(c)


def centre_card(c, kind):
    ville = clean_city(c["ville"])
    lines = [f"<h4>{esc(c['nom'])}</h4>",
             f"<p>{esc(' '.join(x for x in [c['adresse'], c['cp'], ville] if x))}</p>"]
    contact = []
    if c["tel"]:
        tel = re.sub(r"[^\d+]", "", c["tel"])
        contact.append(f'<a href="tel:{esc(tel)}">{esc(c["tel"])}</a>')
    if c["site"]:
        u = c["site"] if c["site"].startswith("http") else "http://" + c["site"]
        if "…" in u:   # la liste FEI tronque les longues adresses : on garde la racine du site
            u = re.match(r"https?://[^/]+", u).group(0) + "/"
        host = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
        contact.append(f'<a href="{esc(u)}" rel="noopener nofollow">{esc(host)}</a>')
    if contact:
        lines.append("<p>" + " · ".join(contact) + "</p>")
    if kind == "tcf":
        lines.append('<p><span class="pf-tag">' + ("sur ordinateur" if c["ordinateur"] else "sur papier") + "</span></p>")
    return '<div class="pf-centre">' + "".join(lines) + "</div>"


def centres_html(codes, kind):
    src = CIV if kind == "civique" else TCF
    cs = [c for code in codes for c in src.get(code, [])]
    cs.sort(key=lambda c: (clean_city(c["ville"]), c["nom"]))
    return cs, '<div class="pf-centres">' + "\n".join(centre_card(c, kind) for c in cs) + "</div>"


# ─── mini-carte ──────────────────────────────────────────────────────────────
VB = CARTE["viewBox"]


def bbox(code):
    xs, ys = [], []
    for m in re.finditer(r"M(-?\d+) (-?\d+)((?:l-?\d+ -?\d+)*)z", CARTE["paths"][code]):
        x, y = int(m.group(1)), int(m.group(2))
        xs.append(x)
        ys.append(y)
        for dx, dy in re.findall(r"l(-?\d+) (-?\d+)", m.group(3)):
            x += int(dx)
            y += int(dy)
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def mini_map(d, p):
    codes = [c for c in p["deps"] if c in CARTE["paths"]]
    if d["code"] not in CARTE["paths"]:
        return ""
    boxes = [bbox(c) for c in codes]
    x0, y0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    x1, y1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    side = max(x1 - x0, (y1 - y0) * 1.25, 70) * 1.5     # du contexte autour, et un zoom lisible en Île-de-France
    vw, vh = side, side / 1.25
    vx, vy = (x0 + x1 - vw) / 2, (y0 + y1 - vh) / 2
    sx, sy = CARTE["sieges"][p["id"]]
    f = forms(d)
    uses = "".join(f'<use href="/prefectures/carte.svg#d-{c}" class="grp"/>' for c in codes if c != d["code"])
    r = max(2.5, round(vw / 75, 1))
    if len(codes) == 1:
        cap = f"{f['Le']} (en rouge) ; le point marque {p['ville']}, où siège la plateforme"
    else:
        cap = (f"{f['Le']} (en rouge) et, en bleu, les autres départements de la plateforme ; le point marque "
               f"{p['ville']}, où elle siège")
    return (f'<figure class="pf-map pf-map-mini"><svg viewBox="{vx:.0f} {vy:.0f} {vw:.0f} {vh:.0f}" role="img" '
            f'aria-label="{esc(cap)}"><use href="/prefectures/carte.svg#fr" class="base"/>{uses}'
            f'<use href="/prefectures/carte.svg#d-{d["code"]}" class="me"/>'
            f'<circle cx="{sx}" cy="{sy}" r="{r}" class="dot"/></svg>'
            f'<figcaption>{cap}.</figcaption></figure>')


# ─── gabarit commun ──────────────────────────────────────────────────────────
APP_SVG = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.71 19.5c-.83 '
           '1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 '
           '12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 '
           '1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 '
           '2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>')
YT_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
TT_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>'


def ld(obj):
    s = json.dumps(obj, ensure_ascii=False, indent=2)
    assert not re.search(r"&[a-zA-Z]{2,8};", s), "entité HTML dans le JSON-LD"
    return '  <script type="application/ld+json">\n  ' + s.replace("\n", "\n  ") + "\n  </script>\n"


def shell(url, title, desc, og_title, body, lds, extra_head=""):
    return f"""<!DOCTYPE html>
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
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{BASE}{url}" />
  <meta property="og:title" content="{esc(og_title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{BASE}{url}" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="fr_FR" />
  <meta property="og:site_name" content="Naturalisation France Facile" />
  <meta property="og:image" content="{BASE}/img/og/prefectures.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{BASE}/img/og/prefectures.png" />
  <link rel="stylesheet" href="/css/style.css?v={CSS_V}" />
{extra_head}{''.join(ld(o) for o in lds)}</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="nav-logo">Naturalisation <span>France Facile</span></a>
    <button class="nav-toggle" aria-label="Menu" onclick="document.querySelector('.nav-links').classList.toggle('open')">&#9776;</button>
    <div class="nav-links">
      <a href="/#fonctionnalites">Fonctionnalités</a>
      <a href="/outils/examen-civique.html">Examen civique</a>
      <a href="/prefectures/">Préfectures</a>
      <a href="/outils/">Outils</a>
      <a href="/faq.html">FAQ</a>
      <a href="/glossaire/">Glossaire</a>
      <a href="/blog/">Blog</a>
      <a href="{APP}" class="nav-cta" target="_blank">Télécharger</a>
    </div>
  </div>
</nav>

{body}

<footer class="footer">
  <div class="footer-links"><a href="/faq.html">FAQ</a><a href="/">Accueil</a><a href="/prefectures/">Préfectures</a><a href="/blog/">Blog</a><a href="/glossaire/">Glossaire</a><a href="/a-propos.html">À propos</a><a href="/mentions-legales.html">Mentions légales</a><a href="/politique-confidentialite.html">Confidentialité</a><a href="mailto:contact@naturalisationfrancefacile.fr">Contact</a></div>
  <div class="footer-social"><a href="https://www.youtube.com/channel/UCrMQy14hPp2j0xPYn0lLlXQ" target="_blank" rel="noopener" aria-label="YouTube">{YT_SVG}</a><a href="https://www.tiktok.com/@naturalisation.france" target="_blank" rel="noopener" aria-label="TikTok">{TT_SVG}</a></div>
  <p class="footer-sources">Sources officielles : <a href="https://www.service-public.gouv.fr/particuliers/vosdroits/N111" target="_blank" rel="noopener">Service-Public</a> · <a href="https://www.legifrance.gouv.fr" target="_blank" rel="noopener">Légifrance</a> · <a href="https://www.interieur.gouv.fr" target="_blank" rel="noopener">Ministère de l'Intérieur</a> · <a href="https://administration-etrangers-en-france.interieur.gouv.fr" target="_blank" rel="noopener">ANEF</a></p>
  <p class="footer-copy">© 2026 Naturalisation France Facile · Informations à titre indicatif, sans valeur de conseil juridique · Site indépendant, non affilié à l'administration.</p>
</footer>
</body></html>
"""


def app_block(d, p):
    """L'encart « l'app vous accompagne », personnalisé pour le département."""
    f = forms(d)
    v = p["ville"]
    if p["email"] and p["contactChannel"] == "email":
        coord = "son adresse postale et son courriel"
    else:
        coord = "son adresse postale, et vous indique le bon canal puisqu'elle ne publie pas de courriel"
    items = [
        ("Votre plateforme, déjà dans l'app",
         f"Choisissez {f['le']} ({f['code']}) dans votre profil : l'app retrouve la plateforme {de_v(v)} "
         f"et reprend {coord} dans vos courriers, avec la source officielle et la date de vérification."),
        ("Vos délais, calculés pour vous",
         "Entrez la date de votre récépissé : l'app calcule l'échéance légale de 18 mois (12 après 10 ans en "
         "France) et vous prévient quand une relance devient utile."),
        ("Le bon courrier au bon moment",
         "Relance, lettre recommandée, recours : des modèles pré-remplis avec vos informations et l'adresse de "
         "votre plateforme."),
        ("L'entretien, répété avant le jour J",
         "Un simulateur d'entretien d'assimilation qui écoute vos réponses et les note par IA, comme face à "
         "l'agent de la plateforme."),
        ("Examen civique et niveau B2",
         "258 questions d'examen civique et plus de 750 exercices TCF IRN et DELF B2 pour arriver au dépôt "
         "avec les deux attestations."),
        ("Les pièces, sans en oublier",
         "La checklist des justificatifs, à cocher au fur et à mesure que vous les réunissez."),
    ]
    lis = "\n".join(f"<li><strong>{t}</strong> {x}</li>" for t, x in items)
    return f"""
<section class="pf-app" id="app" aria-labelledby="app-titre">
  <div class="pf-app-txt">
    <p class="pf-app-kicker">L'application Naturalisation France Facile</p>
    <h2 id="app-titre">Préparer votre dossier {f['dans']}, étape par étape</h2>
    <ul>
{lis}
    </ul>
    <a class="cta-btn" href="{APP}" target="_blank" rel="noopener">{APP_SVG} Télécharger gratuitement</a>
    <p class="pf-app-small">Gratuit sur l'App Store · iPhone et iPad, iOS 17+ · abonnement facultatif</p>
  </div>
  <div class="pf-app-shots" aria-hidden="true">
    <img src="/img/app/suivi-dossier.webp" alt="" width="220" height="449" loading="lazy" />
    <img src="/img/app/entretien-ia.webp" alt="" width="220" height="449" loading="lazy" />
  </div>
</section>
"""


def postal_parts(addr):
    lines = [l.strip() for l in addr.split("\n") if l.strip()]
    m = re.match(r"(\d{5})\s+(.*)", lines[-1])
    return {"@type": "PostalAddress", "streetAddress": ", ".join(lines[1:-1]) or lines[0],
            "postalCode": m.group(1), "addressLocality": re.sub(r"\s+Cedex.*$", "", m.group(2), flags=re.I),
            "addressCountry": "FR"}


def contact_rows(p):
    rows = []
    rows.append(("Adresse postale", f"<address>{esc(p['postalAddress'])}</address>"))
    if p.get("accueil"):
        rows.append(("Accueil du public", esc(p["accueil"])))
    if p["email"] and p["contactChannel"] == "email":
        v = (f'<a href="mailto:{esc(p["email"])}" class="pf-mail">{esc(p["email"])}</a>'
             f' <button type="button" class="pf-copy" data-copy="{esc(p["email"])}">Copier</button>')
        if p.get("email_note"):
            v += f'<br><span class="pf-caveat">{esc(p["email_note"])}</span>'
        rows.append(("Courriel", v))
    elif p.get("papier"):
        rows.append(("Contact", f'Prise de rendez-vous sur <a href="{esc(p["decl"][1])}" rel="noopener">le site de la préfecture</a> ; '
                                "aucun courriel vérifié n'est publié."))
    else:
        rows.append(("Courriel", "Aucun courriel publié : écrivez depuis votre "
                                 f'<a href="{ANEF}" rel="noopener">espace ANEF</a>, ou appelez le Centre de contact '
                                 "citoyens au 0806 001 620 (du lundi au vendredi, 9 h – 17 h)."))
    if p.get("tel"):
        t = esc(p["tel"])
        v = f'<a href="tel:{re.sub(r"[^0-9+]", "", p["tel"])}">{t}</a>'
        if p.get("permanence"):
            v += f" — permanence {esc(p['permanence'])}"
        rows.append(("Téléphone", v))
    if p.get("horaires"):
        rows.append(("Horaires", esc(p["horaires"][0].upper() + p["horaires"][1:])))
    return rows


def platform_card(d, p):
    f = forms(d)
    n = len(p["deps"])
    deps_links = []
    for c in order_deps(p["deps"]):
        dd = DEP[c]
        lab = f"{dd['nom']} ({c})"
        deps_links.append(f"<strong>{lab}</strong>" if c == d["code"] else f'<a href="{page_url(dd)}">{lab}</a>')
    rows = [("Départements", ", ".join(deps_links) if n > 1 else f"{f['label']} uniquement")] + contact_rows(p)
    rows_html = "\n".join(f'<div class="pf-row"><div class="k">{k}</div><div class="v">{v}</div></div>' for k, v in rows)
    host_line = hote_a(p)[0].upper() + hote_a(p)[1:]
    if p["id"] in ("guyane", "guadeloupe"):
        foot = (f"Coordonnées relevées le {VERIFIE} sur la <a href=\"{CARTE_DGEF}\" rel=\"noopener\">carte des "
                "plateformes du ministère de l'Intérieur</a>, sans seconde source officielle pour les confirmer : "
                "vérifiez-les auprès de la préfecture avant un envoi.")
    else:
        foot = (f"Coordonnées relevées le {VERIFIE} sur <a href=\"{esc(p['sourceURL'])}\" rel=\"noopener\">la source "
                f"officielle</a> et recoupées avec la <a href=\"{CARTE_DGEF}\" rel=\"noopener\">carte des plateformes "
                "du ministère de l'Intérieur</a>.")
    return f"""<div class="pf-card">
  <div class="pf-card-head">
    <p class="k">Plateforme de naturalisation{' · ' + str(n) + ' départements' if n > 1 else ''}</p>
    <h3>{esc(p['platformLabel'] or p['name'])}</h3>
    <p>{esc(host_line)}</p>
  </div>
  <div class="pf-rows">
{rows_html}
  </div>
  <p class="pf-card-foot">{foot} Ce site n'est pas la préfecture : n'y envoyez aucun document.</p>
</div>"""


# ─── page département ────────────────────────────────────────────────────────
def page_departement(d):
    f = forms(d)
    pid = PF_OF[d["code"]]
    p = PF[pid]
    v, n = p["ville"], len(p["deps"])
    host = d["code"] == p["host"]
    multi = n > 1
    papier = p.get("papier")
    url = page_url(d)
    autres = [DEP[c] for c in order_deps(p["deps"]) if c != d["code"]]
    liste_deps = et(forms(DEP[c])["le"] for c in order_deps(p["deps"]))
    villes = [x for x in d["villes"] if x != v][:3] if d["code"] != "75" else []

    # — titres —
    if papier:
        h1 = f"Naturalisation {f['dans']} ({f['code']}) : où déposer votre dossier papier"
    elif not host:
        h1 = f"Naturalisation {f['dans']} ({f['code']}) : votre dossier est instruit {a_v(v)}"
    elif multi:
        h1 = f"Naturalisation {f['dans']} ({f['code']}) : la plateforme {de_v(v)} et ses {n} départements"
    else:
        h1 = f"Naturalisation {f['dans']} ({f['code']}) : où déposer votre dossier"
    cands = []
    if p.get("titre") and host:
        cands.append(f"Naturalisation {f['nom']} ({f['code']}) : {p['titre']}")
    if host and not multi:
        cands.append(f"Naturalisation {f['nom']} ({f['code']}) : préfecture {de_v(v)}")
    if not host:
        cands.append(f"Naturalisation {f['nom']} ({f['code']}) : dossier instruit {a_v(p['court'])}")
    cands += [f"Naturalisation {f['nom']} ({f['code']}) : plateforme {de_v(p['court'])}",
              f"Naturalisation {f['nom']} ({f['code']}) : où déposer son dossier",
              f"Naturalisation {f['nom']} ({f['code']}) : où déposer"]
    title = next(t for t in cands if len(t) <= 62)
    dcands = [
        f"{f['Dans']}, la demande de naturalisation se dépose sur l'ANEF puis est instruite {a_v(v)} : "
        f"adresse et contact de la plateforme, entretien, documents, délais.",
        f"{f['Dans']}, la naturalisation se dépose sur l'ANEF et s'instruit {a_v(p['court'])} : "
        f"adresse de la plateforme, entretien, documents, délais.",
        f"Naturalisation {f['dans']} : dépôt sur l'ANEF, plateforme {de_v(p['court'])}, contact, entretien, délais.",
    ]
    if papier:
        dcands = ["En Guyane, la naturalisation ne se dépose pas en ligne : dossier papier au guichet de la "
                  "préfecture, à Cayenne, sur rendez-vous. Pièces et délais."]
    desc = next(x for x in dcands if len(x) <= 158)

    # — chapô —
    if papier:
        lede = ("En Guyane, la demande de naturalisation <strong>ne se dépose pas en ligne</strong> : le dossier "
                "papier se remet au guichet de la préfecture de la Guyane, à Cayenne, sur rendez-vous. C'est la "
                "plateforme de naturalisation de la préfecture qui l'instruit et qui vous convoque ensuite à "
                "l'entretien d'assimilation.")
    elif host:
        lede = (f"{f['Dans']}, la demande de naturalisation par décret <strong>se dépose en ligne, sur l'ANEF</strong>, "
                f"sans rendez-vous. Elle est ensuite instruite par la plateforme de naturalisation de {hote_a(p)}")
        lede += (f", qui traite aussi les dossiers {et(forms(a)['du'] for a in autres)}. " if multi else ". ")
        lede += "C'est elle qui vérifie votre dossier, vous délivre le récépissé et vous convoque à l'entretien."
    else:
        lede = (f"{f['Dans']}, la demande de naturalisation par décret <strong>se dépose en ligne, sur l'ANEF</strong>, "
                f"sans rendez-vous. Elle n'est pas instruite à la préfecture {de_v(f['chef'])} : c'est la "
                f"plateforme de naturalisation de {p['hote']}"
                + (f", <strong>{a_v(v)}</strong>" if v not in p["hote"] else "")
                + f", qui traite les dossiers de {n} départements, dont {f['le']}. C'est elle qui vous convoquera à "
                  f"l'entretien.")
    if villes:
        lede_villes = (f"Que vous habitiez {a_v(villes[0])}"
                       + (f", {a_v(villes[1])}" if len(villes) > 2 else "")
                       + (f" ou {a_v(villes[-1])}" if len(villes) > 1 else "")
                       + f", c'est la même plateforme{'' if host else ', ' + a_v(v)}.")
    else:
        lede_villes = ""

    # — l'essentiel —
    if p["email"] and p["contactChannel"] == "email":
        contact_ess = f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>'
    elif papier:
        contact_ess = "au guichet, sur rendez-vous"
    else:
        contact_ess = "pas de courriel publié : votre espace ANEF"
    ceremonie = ("la préfecture de police" if d["code"] == "75"
                 else f"la préfecture {f['du']}, {a_v(f['chef'])}")
    ess = [
        ("Dépôt", "dossier papier, au guichet de la préfecture, sur rendez-vous" if papier
         else f'en ligne, sur <a href="{ANEF}" rel="noopener">l\'ANEF</a>, sans rendez-vous'),
        ("Instruction", (f"plateforme de naturalisation de {p['hote']}" if v in p["hote"]
                         else f"plateforme {de_v(v)} ({p['hote']})") + (f", pour {n} départements" if multi else "")),
        ("Contact", contact_ess),
        ("Entretien", f"convocation par la plateforme {de_v(v)}"),
        ("Par mariage", p["decl"][0]),
        ("Cérémonie", f"organisée par {ceremonie}, une fois le décret publié"),
        ("Depuis 2026", "niveau B2 et examen civique réussi, à joindre au dossier"),
    ]
    ess_html = "\n".join(f"<dt>{k}</dt><dd>{x}</dd>" for k, x in ess)

    # — tuiles —
    civ, civ_html = centres_html([d["code"]], "civique")
    tcf, tcf_html = centres_html([d["code"]], "tcf")
    tiles = [(p["court"], "siège de la plateforme qui instruit votre dossier" if not host else "siège de votre plateforme de naturalisation")]
    tiles.append((str(len(civ)) if civ else "Aucun",
                  f"centre{'s' if len(civ) > 1 else ''} d'examen civique {f['dans']}" if civ
                  else f"centre d'examen civique listé {f['dans']}"))
    tiles.append((str(len(tcf)) if tcf else "Aucun",
                  f"centre{'s' if len(tcf) > 1 else ''} TCF {f['dans']}" if tcf else f"centre TCF listé {f['dans']}"))
    tiles.append(("18 mois", "délai légal de réponse, 12 si vous vivez en France depuis 10 ans"))
    tiles_html = "\n".join(f'<div class="pf-stat"><div class="num">{esc(a)}</div><div class="lbl">{b}</div></div>' for a, b in tiles)

    # — notes de la plateforme —
    notes = "".join(f'<p class="pf-note">{x}</p>' for x in p.get("notes", []))
    pourquoi = ""
    if not host:
        pourquoi = (f"<p><strong>Pourquoi pas la préfecture {de_v(f['chef'])} ?</strong> Les demandes de naturalisation "
                    f"sont regroupées par plateformes, qui instruisent chacune les dossiers de plusieurs départements. "
                    f"La préfecture {f['du']} n'instruit donc pas votre demande ; c'est elle, en revanche, qui "
                    f"organisera votre cérémonie d'accueil dans la citoyenneté française.</p>")

    # — dépôt —
    if papier:
        depot = f"""
<h3>Par décret : un dossier papier, au guichet</h3>
<p>La Guyane fait partie des rares territoires où le téléservice de l'ANEF n'est pas ouvert à la naturalisation :
le dossier (formulaire cerfa n° 12753 et pièces justificatives) se dépose <strong>au guichet de la préfecture de la Guyane</strong>,
sur rendez-vous pris <a href="{esc(p['decl'][1])}" rel="noopener">sur le site de la préfecture</a>. Les légionnaires
en activité suivent une procédure à part. Le timbre fiscal y est de <strong>127,50 €</strong> au lieu de 255 €.</p>
<h3>Par mariage : la déclaration de nationalité</h3>
<p>La déclaration de nationalité par mariage se dépose elle aussi au guichet, sur rendez-vous. Vous et votre conjoint
êtes ensuite convoqués ensemble à un entretien, à l'issue duquel un récépissé vous est remis.</p>"""
    else:
        decl_txt, decl_url = p["decl"]
        pan = ("de la préfecture de police" if d["code"] == "75"
               else f"de la préfecture {f['du']} ou d'une sous-préfecture")
        decl_link = f' (<a href="{esc(decl_url)}" rel="noopener">voir la page</a>)' if decl_url else ""
        depot = f"""
<h3>Par décret : en ligne, sur l'ANEF</h3>
<p>La naturalisation et la réintégration par décret se demandent sur le téléservice de l'ANEF
(<a href="{ANEF}" rel="noopener">administration-etrangers-en-france.interieur.gouv.fr</a>). Il n'y a pas de rendez-vous à prendre
pour déposer, et le dossier ne se remet pas au guichet{' de la préfecture ' + de_v(f['chef']) if not host else ''} :
le téléservice transmet votre demande à la plateforme compétente pour votre adresse,
{'celle ' + de_v(v) if not host else 'ici celle ' + de_v(v)}. À chaque étape du traitement, vous recevez un courriel.</p>
<h3>Si le dépôt en ligne est impossible</h3>
<p>Vous pouvez alors envoyer votre demande par courrier à la plateforme {de_v(v)} (formulaire cerfa n° 12753 en deux
exemplaires), à condition de joindre la preuve de l'impossibilité : un courriel du Centre de contact citoyens de l'ANTS,
ou un document de la préfecture ou de la sous-préfecture. Ajoutez une enveloppe timbrée à votre adresse et une lettre
suivie de 500 g vierge.</p>
<h3>Par mariage : la déclaration de nationalité</h3>
<p>La déclaration de nationalité par mariage ne passe pas par le même circuit. Pour la plateforme {de_v(v)}, elle se
dépose <strong>{decl_txt}</strong>{decl_link}. Cette modalité vient {p.get('decl_src', 'de la carte du ministère (données du ' + DGEF_DU + ')')} :
vérifiez-la sur le site de la préfecture avant d'envoyer. Vous et votre conjoint êtes ensuite convoqués ensemble à un
entretien, à l'issue duquel un récépissé vous est remis.</p>
<h3>Qui peut vous aider à déposer</h3>
<p>Le <strong>Centre de contact citoyens</strong> de l'ANTS répond sur le dépôt en ligne et le suivi du dossier au
<strong>0806 001 620</strong> (appel non surtaxé, du lundi au vendredi, de 9 h à 17 h). Pour être accompagné sur un
ordinateur, adressez-vous au point d'accueil numérique {pan}.</p>"""
    depot += ("\n<p class=\"pf-note\">Méfiez-vous des sites qui vendent un « rendez-vous naturalisation » : hormis le "
              "timbre fiscal, la démarche est gratuite, et le dépôt par décret se fait en ligne, sans rendez-vous.</p>"
              if not papier else "")

    # — étapes —
    who_pf = f"Plateforme {de_v(v)}"
    etapes = [
        ("you", "Vous", "Dépôt de la demande" if not papier else "Dépôt du dossier papier",
         "En ligne sur l'ANEF, avec le timbre fiscal de 255 €." if not papier
         else "Au guichet de la préfecture, sur rendez-vous, avec le timbre fiscal de 127,50 €."),
        ("pf", who_pf, "Examen des pièces",
         "La plateforme vérifie le dossier et peut demander des pièces complémentaires, dans un délai qu'elle fixe : "
         "sans réponse, la demande peut être classée sans suite."),
        ("pf", who_pf, "Récépissé de complétude",
         "Délivré quand toutes les pièces sont réunies. C'est lui qui fait courir le délai légal de réponse."),
        ("pf", who_pf, "Entretien d'assimilation",
         "Sur convocation. Apportez les originaux de vos documents : ils vous seront demandés."),
        ("pf", "Préfet", "Avis sur la demande",
         "La plateforme transmet le dossier au ministère avec la proposition du préfet."),
        ("min", "Ministère (SDANF, Rezé)", "Contrôles et décision",
         "La sous-direction de l'accès à la nationalité française décide pour toute la France."),
        ("jo", "Journal officiel", "Publication du décret",
         "Vous êtes prévenu par courriel ; le décret prend effet à la date de sa signature."),
        ("pref", "Préfecture de police" if d["code"] == "75" else f"Préfecture {f['du']}", "Cérémonie d'accueil",
         "Organisée pour les habitants du département, en principe dans les six mois."),
    ]
    etapes_html = "\n".join(
        f'<li><span class="pf-who pf-who-{c}">{w}</span><b>{t}</b><span>{x}</span></li>' for c, w, t, x in etapes)

    # — documents —
    timbre = "127,50 € en Guyane" if papier else "255 €"
    docs = [
        f"le timbre fiscal de {timbre} ;",
        "la copie recto verso de votre titre de séjour en cours de validité (sauf ressortissants UE, EEE et suisses) ;",
        "un document officiel d'identité (passeport ou titre de séjour) ;",
        "les justificatifs de votre état civil et de votre nationalité : actes en copie intégrale, traduits par un "
        "traducteur agréé ;",
        "les justificatifs de domicile, de ressources et d'impôts ;",
        "le diplôme ou l'attestation qui prouve votre niveau B2 en français ;",
        "l'attestation de réussite à l'examen civique ;",
        "selon votre situation : pièces sur votre couple, un divorce ou un veuvage, vos enfants mineurs ;",
        "si vous vivez en France depuis moins de 10 ans, l'extrait de casier judiciaire du ou des pays où vous avez "
        "vécu (sauf, pour le pays d'origine, réfugiés et apatrides protégés par l'Ofpra).",
    ]
    docs_html = "\n".join(f"<li>{x}</li>" for x in docs)

    # — examens —
    link_civ = f"{DELF}/centres/examen-civique-france/"
    link_tcf = f"{DELF}/centres/tcf-france/"
    if civ:
        villes_civ = sorted({clean_city(c["ville"]) for c in civ})
        link_civ += "#" + slug(villes_civ[0])
        civ_block = (f"<p>France Éducation international (FEI) liste <strong>{len(civ)} centre{'s' if len(civ) > 1 else ''} "
                     f"agréé{'s' if len(civ) > 1 else ''} {f['dans']}</strong> pour l'examen civique "
                     f"({et(villes_civ)}), selon sa liste du {CENTRES_DU} :</p>\n{civ_html}")
    else:
        sib = [c for a in autres for c in CIV.get(a["code"], [])]
        civ_block = (f"<p>Aucun centre agréé par France Éducation international (FEI) n'est listé {f['dans']} "
                     f"au {CENTRES_DU}.</p>")
        if sib:
            _, sib_html = centres_html([a["code"] for a in autres], "civique")
            civ_block += (f"<p>Dans les autres départements de la plateforme {de_v(v)}, {len(sib)} centres "
                          f"l'organisent :</p>\n{sib_html}")
    if tcf:
        villes_tcf = sorted({clean_city(c["ville"]) for c in tcf})
        city_page = next((x for x in villes_tcf if x in TCF_VILLES), None)
        link_tcf = f"{DELF}/centres/tcf-{slug(city_page)}/" if city_page else link_tcf + "#" + slug(villes_tcf[0])
        tcf_block = (f"<p>Pour le niveau B2, {len(tcf)} centre{'s' if len(tcf) > 1 else ''} "
                     f"{'font' if len(tcf) > 1 else 'fait'} passer le TCF {f['dans']} ({et(villes_tcf)}). La liste de "
                     f"FEI ne précise pas la déclinaison : vérifiez que le centre propose bien le <strong>TCF IRN</strong>, "
                     f"celui de la naturalisation.</p>\n{tcf_html}")
    else:
        sib = [c for a in autres for c in TCF.get(a["code"], [])]
        tcf_block = f"<p>Aucun centre TCF n'est listé {f['dans']} au {CENTRES_DU}.</p>"
        if sib:
            _, sib_html = centres_html([a["code"] for a in autres], "tcf")
            tcf_block += (f"<p>Dans les autres départements de la plateforme {de_v(v)}, {len(sib)} centres le "
                          f"proposent (vérifiez la déclinaison TCF IRN) :</p>\n{sib_html}")

    # — délais —
    delai_officiel = ""
    if p.get("delai_officiel"):
        q, u = p["delai_officiel"]
        delai_officiel = (f"<p class=\"pf-note\">Exception notable : la préfecture du Nord, qui instruit aussi les dossiers "
                          f"du Pas-de-Calais, écrit sur <a href=\"{u}\" rel=\"noopener\">sa page naturalisation</a> "
                          f"qu'en l'état actuel de ses délais, {q}. C'est une durée totale observée, bien au-delà du "
                          f"délai légal : d'où l'importance de dater précisément votre récépissé.</p>")

    # — voisins —
    if multi:
        voisins_titre = f"Les autres départements de la plateforme {de_v(v)}"
        voisins = autres
    elif d["code"] in ("971", "972", "973", "974", "976"):
        voisins_titre = "Les autres départements d'outre-mer"
        voisins = [DEP[c] for c in ("971", "972", "973", "974", "976") if c != d["code"]]
    else:
        voisins_titre = f"Les autres plateformes de la région {d['region']}"
        voisins = [DEP[c] for c in order_deps(DEP) if DEP[c]["region"] == d["region"] and c != d["code"]]
    chips = "\n".join(f'<a href="{page_url(x)}">{x["nom"]} ({x["code"]})</a>' for x in voisins)

    # — FAQ —
    email_txt = (f"par courriel à {p['email']}" if p["email"] and p["contactChannel"] == "email"
                 else "depuis votre espace ANEF (elle ne publie pas de courriel)")
    if papier:
        q1 = ("Où déposer son dossier de naturalisation en Guyane ?",
              "Au guichet de la préfecture de la Guyane, à Cayenne, sur rendez-vous pris sur le site de la préfecture : "
              "en Guyane, le dépôt en ligne sur l'ANEF n'est pas ouvert à la naturalisation. Le timbre fiscal y est de "
              "127,50 €.")
    else:
        q1 = (f"Où déposer son dossier de naturalisation {f['dans']} ?",
              f"En ligne, sur le téléservice de l'ANEF, sans rendez-vous. Le dossier est ensuite instruit par la "
              f"plateforme de naturalisation de {hote_a(p)}"
              + (f", compétente pour {n} départements : {liste_deps}." if multi else "."))
    faq = [q1]
    if not host:
        faq.append((f"Quelle préfecture traite les naturalisations {f['du']} ?",
                    f"Pas la préfecture {de_v(f['chef'])} : les dossiers {f['du']} sont instruits par la plateforme "
                    f"de {hote_a(p)}. La préfecture {f['du']} organise en revanche la cérémonie "
                    f"d'accueil dans la citoyenneté française."))
    else:
        adr = p["postalAddress"].replace("\n", ", ")
        faq.append((f"Quelle est l'adresse de la plateforme de naturalisation {de_v(v)} ?",
                    f"Adresse postale : {adr}. Coordonnées relevées le {VERIFIE} sur les sources officielles ; "
                    f"vérifiez-les avant un envoi recommandé."))
    if papier:
        rdv = "Oui : en Guyane, le dossier papier se dépose au guichet de la préfecture, sur rendez-vous."
    else:
        rdv = ("Non pour une demande par décret : elle se dépose en ligne, sans rendez-vous, et c'est la plateforme "
               "qui vous convoque ensuite à l'entretien. Pour une déclaration par mariage, en revanche, le dépôt se "
               f"fait {p['decl'][0]}.")
    faq.append((f"Faut-il prendre rendez-vous en préfecture pour une naturalisation {f['dans']} ?", rdv))
    if papier:
        contact_faq = ("Par la prise de rendez-vous sur le site de la préfecture de la Guyane : aucun courriel de la "
                       "plateforme n'a pu être vérifié sur une page officielle.")
    else:
        contact_faq = (f"Écrivez-lui {email_txt}, en rappelant votre numéro de dossier ANEF. Le Centre de contact "
                       f"citoyens (0806 001 620) répond aussi sur le dépôt en ligne et le suivi.")
    faq.append((f"Comment contacter la plateforme de naturalisation {de_v(v)} ?", contact_faq))
    faq.append((f"Combien de temps dure une naturalisation {f['dans']} ?",
                "Aucune statistique officielle n'est publiée par plateforme. La loi fixe un délai de réponse de "
                "18 mois à compter du récépissé de complétude, 12 mois si vous résidez en France depuis au moins "
                "10 ans, prolongeable une fois de 3 mois par décision motivée."
                + (" La préfecture du Nord indique toutefois que les procédures durent entre 3 et 4 ans en l'état "
                   "de ses délais." if p.get("delai_officiel") else "")))
    faq.append((f"Où a lieu la cérémonie de naturalisation {f['dans']} ?",
                ("À Paris, c'est le préfet de police qui l'organise" if d["code"] == "75" else
                 f"Elle est organisée par le préfet {f['du']}")
                + ", pour les habitants du département, en principe dans les six mois qui suivent la publication du "
                  "décret. Le maire peut être autorisé à l'organiser dans sa commune."))
    faq_html = "\n".join(f'<details class="pf-faq"><summary>{typo(esc(q))}</summary><p>{typo(esc(a))}</p></details>'
                         for q, a in faq)

    # — JSON-LD —
    office = {"@type": "GovernmentOffice", "name": f"{p['platformLabel'] or p['name']} ({p['name']})",
              "address": postal_parts(p["postalAddress"]),
              "areaServed": [{"@type": "AdministrativeArea", "name": f"{DEP[c]['nom']} ({c})"} for c in order_deps(p["deps"])],
              "parentOrganization": {"@type": "GovernmentOrganization", "name": "Ministère de l'Intérieur"}}
    if p["email"] and p["contactChannel"] == "email":
        office["email"] = p["email"]
    lds = [
        {"@context": "https://schema.org", "@type": "WebPage", "name": plain(h1), "headline": plain(h1),
         "description": desc, "url": BASE + url, "inLanguage": "fr-FR", "datePublished": TODAY,
         "dateModified": TODAY, "isAccessibleForFree": True,
         "author": {"@type": "Person", "name": "Augusto Grone", "url": f"{BASE}/a-propos.html"},
         "publisher": {"@type": "Organization", "name": "Naturalisation France Facile", "url": BASE},
         "isPartOf": {"@type": "CollectionPage", "name": "Où déposer son dossier de naturalisation",
                      "url": f"{BASE}/prefectures/"},
         "about": office},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Où déposer son dossier", "item": f"{BASE}/prefectures/"},
            {"@type": "ListItem", "position": 3, "name": f["label"]}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
    ]

    body = f"""<main class="pf">
<header class="pf-hero">
  <div class="pf-in">
    <nav class="pf-crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a><span>›</span><a href="/prefectures/">Où déposer son dossier</a><span>›</span><span>{f['label']}</span></nav>
    <p class="pf-eyebrow">{d['region']} · département {f['code']}</p>
    <h1>{typo(h1)}</h1>
    <p class="pf-meta">Par <a href="/a-propos.html">Augusto Grone</a> · mis à jour le {TODAY_FR} · coordonnées officielles vérifiées le {VERIFIE}</p>
    <p class="pf-lede">{typo(lede)}{(' ' + typo(lede_villes)) if lede_villes else ''}</p>
    <div class="pf-jump"><a href="#plateforme">La plateforme</a><a href="#depot">Déposer</a><a href="#etapes">Les étapes</a><a href="#documents">Documents</a><a href="#examens">Examens</a><a href="#delais">Délais</a></div>
  </div>
</header>

<div class="pf-in pf-body">
<section class="pf-key" aria-labelledby="essentiel">
  <h2 id="essentiel">L'essentiel</h2>
  <dl>
{typo(ess_html)}
  </dl>
</section>

<div class="pf-stats">
{typo(tiles_html)}
</div>

<h2 id="plateforme">{typo(f"La plateforme qui instruit les dossiers {f['du']}")}</h2>
{typo(platform_card(d, p))}
{typo(notes)}
{typo(pourquoi)}
{mini_map(d, p)}

<h2 id="depot">{typo(f"Où et comment déposer votre dossier {f['dans']}")}</h2>
{typo(depot)}

<h2 id="etapes">Du dépôt au décret : qui fait quoi</h2>
<ol class="pf-steps">
{typo(etapes_html)}
</ol>

<h2 id="documents">{typo(f"Documents à fournir pour une naturalisation {f['dans']}")}</h2>
<p>{typo(f"La liste des pièces est fixée au niveau national : elle est la même {f['dans']} qu'ailleurs. Le téléservice de l'ANEF vous la présente selon votre situation, et la plateforme {de_v(v)} peut vous demander des pièces complémentaires pendant l'instruction. Pour une demande par décret, préparez :")}</p>
<ul class="pf-docs">
{typo(docs_html)}
</ul>
<p>{typo("Gardez les originaux : ils vous seront demandés à l'entretien. Le détail pièce par pièce, avec les pièges à éviter, est dans notre <a href=\"/blog/documents-naturalisation.html\">guide des documents de naturalisation</a>.")}</p>

<h2 id="examens">{typo(f"Examen civique et test de français {f['dans']}")}</h2>
<p>{typo("Depuis le 1er janvier 2026, une demande par décret doit contenir un justificatif du niveau B2 en français et l'attestation de réussite à l'examen civique (40 questions, 32 bonnes réponses exigées). Les deux se passent donc <strong>avant</strong> le dépôt : réservez tôt.")}</p>
<h3>L'examen civique</h3>
{typo(civ_block)}
<p class="pf-more">{typo(f"Adresses complètes, courriels et autres villes : <a href=\"{link_civ}\" rel=\"noopener\">annuaire des centres d'examen civique</a> sur delf-tcf-tef.fr. L'examen est aussi organisé par la CCI Paris Île-de-France, dans ses propres centres.")}</p>
<h3>Le test de français (niveau B2)</h3>
{typo(tcf_block)}
<p class="pf-more">{typo(f"Prix, dates et inscription : <a href=\"{link_tcf}\" rel=\"noopener\">les centres TCF</a> sur delf-tcf-tef.fr. Un diplôme DELF B2 prouve aussi le niveau, et sans limite de durée : <a href=\"/blog/tcf-irn-ou-delf-b2-lequel-choisir.html\">TCF IRN ou DELF B2, lequel choisir</a>.")}</p>

<h2 id="delais">{typo(f"Délais de naturalisation {f['dans']}")}</h2>
<p>{typo(f"Aucune administration ne publie de délai par plateforme, et les chiffres des forums mélangent des points de départ différents. Ce qui est fixé, c'est le délai légal : l'administration a <strong>18 mois</strong> pour répondre à compter de la remise du récépissé de complétude, <strong>12 mois</strong> si vous résidez habituellement en France depuis au moins 10 ans à cette date. Il peut être prolongé une fois de 3 mois, par une décision motivée.")}</p>
{typo(delai_officiel)}
<p>{typo("Le compteur part du récépissé, pas du jour du dépôt : chaque demande de pièce complémentaire le repousse. Au-delà du délai, relancez par écrit ; les recours se forment auprès du ministère, puis du tribunal administratif de Nantes, quel que soit votre département. Voir <a href=\"/blog/delais-naturalisation-2026.html\">les délais de naturalisation en 2026</a> et <a href=\"/blog/relance-naturalisation-que-faire-sans-reponse.html\">que faire sans réponse</a>.")}</p>

{typo(app_block(d, p))}

<h2 id="voisins">{typo(voisins_titre)}</h2>
<div class="pf-chips">
{chips}
<a href="/prefectures/" class="all">Tous les départements</a>
</div>

<h2 id="faq">Questions fréquentes</h2>
{faq_html}

<h2 id="sources">Sources</h2>
<ul class="pf-sources">
<li><a href="{CARTE_DGEF}" rel="noopener">Carte des plateformes de naturalisation</a>, ministère de l'Intérieur (DGEF), données du {DGEF_DU}.</li>
<li><a href="{esc(p['sourceURL'])}" rel="noopener">Fiche de la plateforme</a>, relevée le {VERIFIE}.</li>
<li><a href="{SP_DECRET}" rel="noopener">Naturalisation française par décret</a> et <a href="{SP_MARIAGE}" rel="noopener">déclaration par mariage</a>, Service-Public.fr.</li>
<li><a href="{LF_DELAIS}" rel="noopener">Code civil, art. 21-25-1</a> (délais) et <a href="{LF_CEREMONIE}" rel="noopener">art. 21-28</a> (cérémonie), Légifrance.</li>
<li>Centres d'examen : liste de France Éducation international relevée le {CENTRES_DU} (<a href="{DELF}/centres/" rel="noopener">annuaire de delf-tcf-tef.fr</a>).</li>
</ul>
<p class="pf-disclaimer">Site indépendant, non affilié à l'administration. Les coordonnées changent : en cas de doute, la page de la préfecture fait foi.</p>
</div>
</main>
<script>document.addEventListener('click',function(e){{var b=e.target.closest('.pf-copy');if(!b)return;navigator.clipboard&&navigator.clipboard.writeText(b.dataset.copy).then(function(){{b.textContent='Copié';setTimeout(function(){{b.textContent='Copier'}},1600)}})}});</script>"""
    og = f"Naturalisation {f['dans']} ({f['code']}) : où déposer votre dossier"
    return url, shell(url, title, desc, og, body, lds), title, desc


# ─── carte (fichier partagé + carte de l'accueil) ────────────────────────────
def adjacency():
    cells = {}
    for code, d in CARTE["paths"].items():
        pts = set()
        for m in re.finditer(r"M(-?\d+) (-?\d+)((?:l-?\d+ -?\d+)*)z", d):
            x, y = int(m.group(1)), int(m.group(2))
            pts.add((x // 3, y // 3))
            for dx, dy in re.findall(r"l(-?\d+) (-?\d+)", m.group(3)):
                x += int(dx)
                y += int(dy)
                pts.add((x // 3, y // 3))
        cells[code] = pts
    adj = defaultdict(set)
    codes = list(cells)
    for i, a in enumerate(codes):
        for b in codes[i + 1:]:
            if cells[a] & cells[b]:
                adj[a].add(b)
                adj[b].add(a)
    return adj


def platform_colors():
    adj = adjacency()
    padj = defaultdict(set)
    for a, bs in adj.items():
        for b in bs:
            if PF_OF[a] != PF_OF[b]:
                padj[PF_OF[a]].add(PF_OF[b])
    color = {}
    for pid in sorted(PF, key=lambda x: -len(padj[x])):
        used = {color[q] for q in padj[pid] if q in color}
        color[pid] = next(k for k in range(8) if k not in used)
    return color


def write_carte_svg():
    paths = "\n".join(f'<path id="d-{c}" d="{d}"/>' for c, d in CARTE["paths"].items())
    OUT.joinpath("carte.svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(map(str, VB))}">\n'
        f"<!-- Départements de métropole, d'après Etalab (contours administratifs 2025, Licence Ouverte 2.0) -->\n"
        f'<g id="fr">\n{paths}\n</g>\n</svg>\n', encoding="utf-8")


def hub_map(colors):
    out = []
    for c, d in CARTE["paths"].items():
        dep = DEP[c]
        p = PF[PF_OF[c]]
        t = f"{dep['nom']} ({c}) → plateforme {de_v(p['ville'])}"
        out.append(f'<a href="{page_url(dep)}" aria-label="{esc(t)}"><path d="{d}" class="c{colors[PF_OF[c]]}">'
                   f"<title>{esc(t)}</title></path></a>")
    dots = []
    for pid, (x, y) in CARTE["sieges"].items():
        dots.append(f'<circle cx="{x}" cy="{y}" r="6" class="dot"><title>Plateforme {esc(de_v(PF[pid]["ville"]))}</title></circle>')
    return (f'<svg viewBox="{" ".join(map(str, VB))}" role="img" aria-label="Carte des plateformes de naturalisation '
            f'de métropole : une couleur par plateforme, un point au siège de chacune">'
            + "".join(out) + "".join(dots) + "</svg>")


IDF = ["75", "77", "78", "91", "92", "93", "94", "95"]


def idf_inset(colors):
    """Encart zoomé : les huit plateformes d'Île-de-France sont illisibles à l'échelle de la France."""
    boxes = [bbox(c) for c in IDF]
    x0, y0 = min(b[0] for b in boxes) - 6, min(b[1] for b in boxes) - 6
    x1, y1 = max(b[2] for b in boxes) + 6, max(b[3] for b in boxes) + 6
    out, labels = [], []
    for c in IDF:
        dep = DEP[c]
        p = PF[PF_OF[c]]
        t = f"{dep['nom']} ({c}) → plateforme {de_v(p['ville'])}"
        out.append(f'<a href="{page_url(dep)}" aria-label="{esc(t)}"><path d="{CARTE["paths"][c]}" class="c{colors[PF_OF[c]]}">'
                   f"<title>{esc(t)}</title></path></a>")
        bx = bbox(c)
        lx, ly = (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2
        if c == "92":
            lx -= 2
        labels.append(f'<text x="{lx:.0f}" y="{ly + 2:.0f}" class="lbl{" sm" if c in ("75", "92", "93", "94") else ""}">{c}</text>')
    return (f'<svg viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" role="img" aria-label="Zoom sur l\'Île-de-France : '
            f'une plateforme par département">' + "".join(out) + "".join(labels) + "</svg>")


# ─── accueil de la rubrique ──────────────────────────────────────────────────
def page_hub():
    url = "/prefectures/"
    colors = platform_colors()
    n_pf = len(PF)
    n_mail = sum(1 for p in PF.values() if p["email"] and p["contactChannel"] == "email")
    title = "Plateforme de naturalisation par département : où déposer"
    desc = ("Où déposer son dossier de naturalisation ? Sur l'ANEF, puis la plateforme de votre département : "
            "adresse, courriel, rendez-vous, carte des 101 départements.")
    h1 = "Où déposer son dossier de naturalisation ? La plateforme de chaque département"

    # recherche
    idx = [{"c": d["code"], "n": d["nom"], "u": page_url(d), "p": PF[PF_OF[d["code"]]]["ville"],
            "v": d["villes"], "h": forms(d)["chef"]} for d in DEPS]
    idx_json = json.dumps(idx, ensure_ascii=False, separators=(",", ":"))

    # plateformes par région
    by_region = defaultdict(list)
    for pid, p in PF.items():
        by_region[DEP[p["host"]]["region"]].append(p)
    regions = sorted(by_region, key=lambda r: (r in ("Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte"),
                                               r != "Île-de-France", r))
    blocks = []
    for r in regions:
        cards = []
        for p in sorted(by_region[r], key=lambda p: p["ville"]):
            chips = "".join(f'<a href="{page_url(DEP[c])}">{DEP[c]["nom"]} <span>{c}</span></a>'
                            for c in order_deps(p["deps"]))
            contact = (f'<a href="mailto:{esc(p["email"])}">{esc(p["email"])}</a>' if p["email"] and p["contactChannel"] == "email"
                       else ("dépôt papier au guichet" if p.get("papier") else "pas de courriel : espace ANEF"))
            cards.append(f"""<div class="pf-pcard"><p class="pf-pcard-k"><span class="sw c{colors.get(p['id'], 0)}"></span>{len(p['deps'])} département{'s' if len(p['deps']) > 1 else ''}</p>
<h3><a href="{page_url(DEP[p['host']])}">Plateforme {de_v(p['ville'])}</a></h3>
<p class="pf-pcard-h">{esc(p['hote'][0].upper() + p['hote'][1:])}</p>
<div class="pf-pcard-deps">{chips}</div>
<p class="pf-pcard-c">{contact}</p></div>""")
        blocks.append(f'<h3 class="pf-region">{r}</h3>\n<div class="pf-pgrid">\n' + "\n".join(cards) + "\n</div>")

    # tableau des 101 départements
    rows = []
    for d in DEPS:
        p = PF[PF_OF[d["code"]]]
        rows.append(f'<tr><td>{d["code"]}</td><td><a href="{page_url(d)}">{d["nom"]}</a></td>'
                    f'<td>{esc(p["ville"])}</td><td>{"en ligne (ANEF)" if not p.get("papier") else "papier, au guichet"}</td></tr>')

    faq = [
        ("Où déposer son dossier de naturalisation ?",
         "Une demande de naturalisation par décret se dépose en ligne, sur le téléservice de l'ANEF, sans rendez-vous, "
         "sauf en Guyane et dans les collectivités d'outre-mer, où le dossier reste papier. Elle est ensuite instruite "
         f"par l'une des {n_pf} plateformes de naturalisation, selon le département où vous habitez."),
        ("Qu'est-ce qu'une plateforme de naturalisation ?",
         "C'est le service de préfecture qui instruit les demandes d'accès à la nationalité française pour un ou "
         "plusieurs départements : il vérifie le dossier, délivre le récépissé, conduit l'entretien d'assimilation "
         "et transmet la demande au ministère avec l'avis du préfet."),
        ("Ma préfecture est-elle ma plateforme de naturalisation ?",
         "Pas forcément. En Île-de-France, chaque département a la sienne (à Saint-Germain-en-Laye pour les Yvelines, "
         "à Torcy pour la Seine-et-Marne) ; ailleurs, une plateforme regroupe souvent plusieurs départements, jusqu'à "
         "huit pour celle de Toulouse. Votre préfecture organise en revanche la cérémonie de naturalisation."),
        ("Peut-on déposer son dossier dans une autre préfecture pour aller plus vite ?",
         "Non. La plateforme compétente est celle de votre domicile, et un déménagement en cours d'instruction "
         "entraîne un transfert du dossier qui rallonge le traitement. Signalez tout changement d'adresse."),
        ("Où envoyer une déclaration de nationalité par mariage ?",
         "À la plateforme de votre domicile, mais pas par l'ANEF : selon les plateformes, au guichet sur rendez-vous "
         "ou par courrier recommandé avec avis de réception. Chaque page département précise la modalité."),
        ("Faut-il un rendez-vous pour déposer une demande de naturalisation ?",
         "Non pour une demande par décret, déposée en ligne. Méfiez-vous des sites qui vendent des rendez-vous : "
         "hormis le timbre fiscal de 255 €, la démarche est gratuite."),
    ]
    faq_html = "\n".join(f'<details class="pf-faq"><summary>{typo(esc(q))}</summary><p>{typo(esc(a))}</p></details>'
                         for q, a in faq)
    lds = [
        {"@context": "https://schema.org", "@type": "CollectionPage", "name": h1, "description": desc,
         "url": BASE + url, "inLanguage": "fr-FR", "datePublished": TODAY, "dateModified": TODAY,
         "author": {"@type": "Person", "name": "Augusto Grone", "url": f"{BASE}/a-propos.html"},
         "publisher": {"@type": "Organization", "name": "Naturalisation France Facile", "url": BASE},
         "mainEntity": {"@type": "ItemList", "numberOfItems": len(DEPS), "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "name": f"Naturalisation {forms(d)['dans']} ({d['code']})",
              "url": BASE + page_url(d)} for i, d in enumerate(DEPS)]}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Où déposer son dossier"}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
    ]
    app = app_block_hub()
    body = f"""<main class="pf">
<header class="pf-hero pf-hero-hub">
  <div class="pf-in">
    <nav class="pf-crumbs" aria-label="Fil d'Ariane"><a href="/">Accueil</a><span>›</span><span>Où déposer son dossier</span></nav>
    <p class="pf-eyebrow">Annuaire des plateformes · {len(DEPS)} départements</p>
    <h1>{typo(h1)}</h1>
    <p class="pf-meta">Par <a href="/a-propos.html">Augusto Grone</a> · mis à jour le {TODAY_FR} · coordonnées officielles vérifiées le {VERIFIE}</p>
    <p class="pf-lede">{typo(f"La demande de naturalisation par décret <strong>se dépose en ligne, sur l'ANEF</strong>, où que vous habitiez (sauf en Guyane et dans les collectivités d'outre-mer). Elle est ensuite instruite non par « votre préfecture », mais par l'une des <strong>{n_pf} plateformes de naturalisation</strong> de métropole et des départements d'outre-mer, selon votre département. Trouvez la vôtre :")}</p>
    <form class="pf-finder" role="search" onsubmit="return false">
      <label for="pf-q" class="pf-sr">Votre département, son numéro, votre code postal ou votre ville</label>
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 2a8 8 0 0 1 6.32 12.9l5.39 5.4-1.41 1.4-5.4-5.39A8 8 0 1 1 10 2zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12z"/></svg>
      <input id="pf-q" type="search" autocomplete="off" placeholder="Ex. : 93, Tarn, 31000, Brest" />
      <div id="pf-res" class="pf-res" aria-live="polite"></div>
    </form>
  </div>
</header>

<div class="pf-in pf-body pf-body-wide">
<div class="pf-stats">
<div class="pf-stat"><div class="num">{len(DEPS)}</div><div class="lbl">départements, une page chacun</div></div>
<div class="pf-stat"><div class="num">{n_pf}</div><div class="lbl">plateformes en métropole et outre-mer</div></div>
<div class="pf-stat"><div class="num">{n_mail}</div><div class="lbl">courriels officiels vérifiés un par un</div></div>
<div class="pf-stat"><div class="num">{VERIFIE.rsplit(' ', 1)[0]}</div><div class="lbl">date de la dernière vérification</div></div>
</div>

<h2 id="carte">La carte des plateformes</h2>
<p>{typo("Chaque couleur correspond à une plateforme, le point marque la ville où elle siège. Touchez un département pour ouvrir sa page : adresse, courriel, modalités de dépôt, centres d'examen.")}</p>
<figure class="pf-map pf-map-hub">{hub_map(colors)}</figure>
<figure class="pf-map pf-map-idf">{idf_inset(colors)}<figcaption>Île-de-France : chaque département a sa propre plateforme.</figcaption></figure>

<h2 id="qui">{typo("ANEF, plateforme, préfecture, ministère : qui fait quoi ?")}</h2>
<div class="pf-roles">
<div><b>L'ANEF</b><p>{typo("Le téléservice du ministère de l'Intérieur. Vous y déposez la demande, recevez les demandes de pièces et suivez l'avancement.")}</p></div>
<div><b>La plateforme</b><p>{typo("Le service de préfecture compétent pour votre département : examen du dossier, récépissé, entretien d'assimilation, avis du préfet.")}</p></div>
<div><b>Le ministère</b><p>{typo("La SDANF, à Rezé, contrôle le dossier et décide pour toute la France ; le décret paraît au Journal officiel.")}</p></div>
<div><b>Votre préfecture</b><p>{typo("Celle de votre département organise la cérémonie d'accueil dans la citoyenneté française, en principe dans les six mois.")}</p></div>
</div>

<h2 id="plateformes">Les {n_pf} plateformes, région par région</h2>
{chr(10).join(blocks)}

<h2 id="departements">Les {len(DEPS)} départements</h2>
<div class="pf-tablewrap"><table class="article-table pf-table">
<thead><tr><th>N°</th><th>Département</th><th>Plateforme</th><th>Dépôt par décret</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table></div>

<h2 id="com">{typo("Saint-Barthélemy, Saint-Martin, Saint-Pierre-et-Miquelon, Wallis-et-Futuna, Polynésie, Nouvelle-Calédonie")}</h2>
<p>{typo(f"Les habitants de ces collectivités ne peuvent pas utiliser le téléservice de l'ANEF : le dossier se dépose sur papier auprès de la préfecture ou du haut-commissariat, selon les modalités indiquées sur la <a href=\"{CARTE_DGEF}\" rel=\"noopener\">carte officielle des plateformes</a>. Nous n'avons pas pu recouper leurs coordonnées sur une seconde source officielle : elles ne sont donc pas reprises ici.")}</p>

{typo(app)}

<h2 id="faq">Questions fréquentes</h2>
{faq_html}

<h2 id="sources">Sources et méthode</h2>
<p>{typo(f"Les {n_pf} plateformes et leurs départements viennent de la <a href=\"{CARTE_DGEF}\" rel=\"noopener\">carte interactive du ministère de l'Intérieur</a> (DGEF), à laquelle renvoie la page officielle des procédures d'accès à la nationalité : il n'existe pas d'arrêté qui publie cette liste. Chaque adresse et chaque courriel ont été recoupés le {VERIFIE} avec l'annuaire officiel de l'administration (lannuaire.service-public.gouv.fr) et, en cas de divergence, avec le site de la préfecture. Quand deux sources officielles se contredisent, la page le signale au lieu de trancher en silence ; un courriel que nous n'avons pas pu vérifier n'est pas publié. Procédure : <a href=\"{SP_DECRET}\" rel=\"noopener\">Service-Public.fr</a> ; départements et villes : INSEE ; centres d'examen : liste de France Éducation international du {CENTRES_DU}.")}</p>
<p class="pf-disclaimer">Site indépendant, non affilié à l'administration. Les coordonnées changent : en cas de doute, la page de la préfecture fait foi.</p>
</div>
</main>
<script>
(function(){{var D={idx_json};
function n(s){{return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().replace(/[’']/g,' ').replace(/[^a-z0-9]+/g,' ').trim()}}
function cp(q){{if(/^97\\d{{3}}$/.test(q))return q.slice(0,3);if(/^20\\d{{3}}$/.test(q))return +q.slice(0,3)<202?'2A':'2B';return q.slice(0,2)}}
function find(raw){{var q=n(raw);if(!q)return[];var c=q.replace(/\\s/g,'').toUpperCase();
if(/^\\d{{5}}$/.test(c)){{var k=cp(c);return D.filter(function(d){{return d.c===k}}).map(function(d){{return[d,'code postal '+c]}})}}
if(/^\\d$/.test(c))c='0'+c;
if(/^(\\d{{2,3}}|2A|2B)$/.test(c))return D.filter(function(d){{return d.c===c}}).map(function(d){{return[d,'']}});
var r=[];D.forEach(function(d){{var nn=n(d.n),s=0,via='';if(nn===q)s=100;else if(nn.indexOf(q)===0)s=80;else if(q.length>2&&nn.indexOf(q)>-1)s=60;
if(s<90)d.v.concat([d.h]).forEach(function(v){{var nv=n(v);if(nv===q&&s<90){{s=90;via=v}}else if(q.length>3&&nv.indexOf(q)===0&&s<70){{s=70;via=v}}}});
if(s)r.push([d,via,s])}});return r.sort(function(a,b){{return b[2]-a[2]}}).slice(0,6)}}
var i=document.getElementById('pf-q'),o=document.getElementById('pf-res');
function show(){{var r=find(i.value);if(!i.value.trim()){{o.innerHTML='';return}}
if(!r.length){{o.innerHTML='<p class="pf-res-none">Aucun département trouvé. Essayez le numéro (93), le nom (Tarn) ou le code postal (31000).</p>';return}}
o.innerHTML=r.map(function(x){{var d=x[0];return '<a class="pf-hit" href="'+d.u+'"><span class="pf-hit-n">'+d.n+' <em>'+d.c+'</em></span><span class="pf-hit-p">'+(x[1]?x[1]+' · ':'')+'plateforme '+(/^[AEIOUYÉÈ]/.test(d.p)?'d\\u2019':'de ')+d.p+'</span></a>'}}).join('')}}
i.addEventListener('input',show);i.form.addEventListener('submit',function(){{var a=o.querySelector('a');if(a)location.href=a.href}});
}})();
</script>"""
    return url, shell(url, title, desc, h1, body, lds), title, desc


def app_block_hub():
    items = [
        ("Votre plateforme, déjà dans l'app",
         "Choisissez votre département : l'app retrouve la bonne plateforme et reprend ses coordonnées vérifiées "
         "dans vos courriers, avec la source et la date de vérification."),
        ("Vos délais, calculés pour vous",
         "À partir de la date de votre récépissé : l'échéance légale de 18 ou 12 mois, et le moment où une relance "
         "devient utile."),
        ("L'entretien, répété avant le jour J",
         "Un simulateur d'entretien d'assimilation qui écoute vos réponses et les note par IA."),
        ("Examen civique et niveau B2",
         "258 questions d'examen civique et plus de 750 exercices TCF IRN et DELF B2."),
    ]
    lis = "\n".join(f"<li><strong>{t}</strong> {x}</li>" for t, x in items)
    return f"""
<section class="pf-app" id="app" aria-labelledby="app-titre">
  <div class="pf-app-txt">
    <p class="pf-app-kicker">L'application Naturalisation France Facile</p>
    <h2 id="app-titre">Du dépôt au décret, sans perdre le fil</h2>
    <ul>
{lis}
    </ul>
    <a class="cta-btn" href="{APP}" target="_blank" rel="noopener">{APP_SVG} Télécharger gratuitement</a>
    <p class="pf-app-small">Gratuit sur l'App Store · iPhone et iPad, iOS 17+ · abonnement facultatif</p>
  </div>
  <div class="pf-app-shots" aria-hidden="true">
    <img src="/img/app/suivi-dossier.webp" alt="" width="220" height="449" loading="lazy" />
    <img src="/img/app/entretien-ia.webp" alt="" width="220" height="449" loading="lazy" />
  </div>
</section>
"""


# ─── sitemap et contrôles ────────────────────────────────────────────────────
def update_sitemap(urls):
    sm = ROOT / "sitemap.xml"
    s = sm.read_text(encoding="utf-8")
    s = re.sub(r"\s*<url>\s*<loc>https://naturalisationfrancefacile\.fr/prefectures/[^<]*</loc>.*?</url>", "", s, flags=re.S)
    block = "".join(
        f"\n  <url>\n    <loc>{BASE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>monthly</changefreq>\n"
        f"    <priority>{'0.9' if u == '/prefectures/' else '0.7'}</priority>\n  </url>" for u in urls)
    s = s.replace("\n</urlset>", block + "\n</urlset>")
    sm.write_text(s, encoding="utf-8")


def check(pages):
    words = []
    for url, page, title, desc in pages:
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
            json.loads(block)
        for href in re.findall(r'href="(/[^"#?]*)', page):
            target = ROOT / href.lstrip("/")
            if href.endswith("/"):
                target = target / "index.html"
            assert target.exists() or href.startswith("/prefectures/"), (url, href)
            if href.startswith("/prefectures/") and href != "/prefectures/" and not href.endswith(".svg"):
                assert (OUT / href.split("/")[-1]).exists() or any(u == href for u, *_ in pages), (url, href)
        assert len(title) <= 62, (url, len(title), title)
        assert 100 <= len(desc) <= 160, (url, len(desc), desc)
        text = re.sub(r"<script.*?</script>|<nav.*?</nav>|<footer.*?</footer>|<[^>]+>", " ", page, flags=re.S)
        words.append((len(text.split()), url))
    words.sort()
    print(f"  mots : min {words[0][0]} ({words[0][1]}) · max {words[-1][0]} ({words[-1][1]})")


def main():
    OUT.mkdir(exist_ok=True)
    write_carte_svg()
    pages = [page_hub()] + [page_departement(d) for d in DEPS]
    urls = [u for u, *_ in pages]
    assert len(set(urls)) == len(urls)
    for url, page, *_ in pages:
        name = "index.html" if url == "/prefectures/" else url.split("/")[-1]
        (OUT / name).write_text(page, encoding="utf-8")
    check(pages)
    update_sitemap(urls)
    print(f"{len(pages)} pages générées dans prefectures/ ({len(PF)} plateformes)")


if __name__ == "__main__":
    main()
