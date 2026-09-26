#!/usr/bin/env python3
"""Rassemble les donnees de la rubrique /prefectures/ dans data/prefectures/.

Rien n'est invente ici : chaque fichier produit vient d'une source publique,
datee, que les pages citent.

  departements.json  101 departements (INSEE, Code officiel geographique 2025 :
                     nom, article, region, chef-lieu) + leurs 5 communes les
                     plus peuplees (geo.api.gouv.fr, populations INSEE).
  plateformes.json   copie de l'annuaire embarque dans l'app iOS
                     (Resources/plateformes_naturalisation.json) : 41
                     plateformes, adresses et courriels verifies un par un le
                     21/09/2026, avec leur source. C'est LA source des
                     coordonnees : on ne corrige jamais une adresse ici, on la
                     corrige dans l'app puis on relance ce script.
  carte_dgef.json    ce que la carte officielle du ministere de l'Interieur
                     (DGEF, macarte.ign.fr) dit de chaque plateforme : modalite
                     de depot des declarations (mariage), accueil physique,
                     telephone et permanences. Rattache a nos plateformes par
                     les departements cites dans chaque fiche.
  centres.json       centres agrees par France Education international pour
                     l'examen civique et le TCF en France, releves le
                     19/09/2026 pour l'annuaire de delf-tcf-tef.fr (meme
                     editeur), rattaches a leur departement par le code postal.
  carte_paths.json   contours des departements de metropole (Etalab,
                     contours administratifs 2025 simplifies a 1 000 m),
                     re-simplifies et projetes en chemins SVG.

    python3 scripts/refresh_prefectures_data.py

Les chemins vers le depot de l'app et celui de delf-tcf-tef.fr se reglent par
NFF_APP_REPO et DELF_SITE_REPO.
"""

import csv
import io
import json
import math
import os
import pathlib
import re
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "prefectures"
HOME = pathlib.Path.home()
APP_REPO = pathlib.Path(os.environ.get("NFF_APP_REPO", HOME / "Desktop/NaturalisationFranceFacile"))
DELF_REPO = pathlib.Path(os.environ.get("DELF_SITE_REPO", HOME / "Desktop/DELF TCF/site"))

URL_COG = "https://www.insee.fr/fr/statistiques/fichier/8377162/v_departement_2025.csv"
URL_COMMUNES = "https://geo.api.gouv.fr/communes?fields=nom,code,codeDepartement,population&format=json"
URL_REGIONS = "https://geo.api.gouv.fr/regions"
URL_CONTOURS = "https://etalab-datasets.geo.data.gouv.fr/contours-administratifs/2025/geojson/departements-1000m.geojson"
URL_DGEF_API = "https://macarte.ign.fr/api/maps/e6de13433eaeb9e66ef4cf7d2fe9d108/file"
URL_DGEF_MAP = "https://macarte.ign.fr/carte/e33e5b949d3c8ff991adc1c67aa0b28c/Plateformes-Naturalisation"

# 101 departements : metropole (2A/2B au lieu de 20) + 5 DROM. Les collectivites
# d'outre-mer (975, 977, 978, 986-988) n'ont pas de page : depot en ligne impossible,
# donnees a source unique (voir la page d'accueil de la rubrique).
DROM = ["971", "972", "973", "974", "976"]

# Ville où siège chaque plateforme de métropole (pour placer le point sur les cartes).
SIEGES = {
    "prefecture-de-police": ("Paris", "75"), "hauts-de-seine": ("Nanterre", "92"),
    "seine-saint-denis": ("Bobigny", "93"), "val-de-marne": ("Créteil", "94"), "val-doise": ("Cergy", "95"),
    "essonne": ("Évry-Courcouronnes", "91"), "yvelines": ("Saint-Germain-en-Laye", "78"),
    "seine-et-marne": ("Torcy", "77"), "meurthe-et-moselle": ("Nancy", "54"), "marne": ("Reims", "51"),
    "bas-rhin": ("Strasbourg", "67"), "doubs": ("Besançon", "25"), "cote-dor": ("Dijon", "21"),
    "nord": ("Lille", "59"), "oise": ("Beauvais", "60"), "seine-maritime": ("Rouen", "76"),
    "calvados": ("Caen", "14"), "ille-et-vilaine": ("Rennes", "35"), "loire-atlantique": ("Nantes", "44"),
    "indre-et-loire": ("Tours", "37"), "deux-sevres": ("Niort", "79"), "gironde": ("Bordeaux", "33"),
    "haute-vienne": ("Limoges", "87"), "haute-garonne": ("Toulouse", "31"), "herault": ("Montpellier", "34"),
    "puy-de-dome": ("Clermont-Ferrand", "63"), "rhone": ("Lyon", "69"), "isere": ("Grenoble", "38"),
    "bouches-du-rhone": ("Marseille", "13"), "alpes-maritimes": ("Nice", "06"), "haute-corse": ("Bastia", "2B"),
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (nff-website data refresh)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def fold(s):
    """Comparaison insensible aux accents, a la casse et aux apostrophes."""
    s = s.replace("\u2019", "'")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


# ─── departements ────────────────────────────────────────────────────────────
def build_departements():
    cog = list(csv.DictReader(io.StringIO(get(URL_COG).decode("utf-8"))))
    communes = json.loads(get(URL_COMMUNES))
    regions = {r["code"]: r["nom"] for r in json.loads(get(URL_REGIONS))}
    by_code = {c["code"]: c for c in communes}
    by_dep = defaultdict(list)
    for c in communes:
        if c.get("population"):
            by_dep[c["codeDepartement"]].append(c)
    deps = []
    for d in cog:
        top = sorted(by_dep[d["DEP"]], key=lambda c: -c["population"])[:5]
        deps.append({
            "code": d["DEP"],
            "nom": d["LIBELLE"],
            "tncc": int(d["TNCC"]),
            "region": regions.get(d["REG"], d["REG"]),
            "chef_lieu": by_code[d["CHEFLIEU"]]["nom"],
            "villes": [c["nom"] for c in top],
        })
    assert len(deps) == 101, len(deps)
    return {"source": "INSEE, Code officiel géographique 2025 ; geo.api.gouv.fr (populations INSEE)",
            "departements": deps}


# ─── carte officielle DGEF ───────────────────────────────────────────────────
def build_carte_dgef(deps, plateformes):
    raw = json.loads(get(URL_DGEF_API))
    popups = raw["layers"][1]["data"]["popupContent"]
    name_to_code = {fold(d["nom"]): d["code"] for d in deps}
    name_to_code.update({"reunion": "974", "la reunion": "974"})
    code_to_pf = {c: p["id"] for p in plateformes for c in p["departements"]}
    out = {}
    for p in popups:
        desc = p["desc"]
        names = re.findall(r"\*([^*]+)\*", desc.split("\n")[0])
        codes = [name_to_code.get(fold(n)) for n in names]
        pfs = Counter(code_to_pf[c] for c in codes if c in code_to_pf)
        if not pfs:
            continue
        pid = pfs.most_common(1)[0][0]
        f = out.setdefault(pid, {"titres": []})
        if p["titre"] not in f["titres"]:
            f["titres"].append(p["titre"])

        def grab(rx):
            m = re.search(rx, desc, re.I)
            return re.sub(r"\s+", " ", m.group(1)).strip(" .\"*") if m else None

        decl = grab(r"par\s+\**d[ée]claration\**\s*:?\s*([^\n]+(?:\n(?!\s*[>*\-]|\s*-{2,}|Courriel|Site)[^\n]+)?)")
        fields = {
            "accueil": grab(r"Adresse physique[^:]*:\s*([^\n]+)"),
            "adresse_postale": grab(r"Adresse postale\s*:\s*([^\n]+)"),
            "telephone": grab(r"T[ée]l\s*:\s*([^\n(]+)"),
            "permanence": grab(r"permanence t[ée]l[ée]phonique\s*:?\s*([^)\n]+)"),
            "horaires": grab(r"Horaires?[^:\n]*:\s*([^\n]+)"),
            "declaration": decl,
            "texte": desc,
        }
        urls = re.findall(r"https?://[^\s)\]\"]+", decl or "")
        if not urls and decl and decl.rstrip().endswith(":"):
            # « … sur le module dédié à l'adresse suivante : » puis l'URL à la ligne
            m = re.search(r"d[ée]claration[^\n]*:\s*\n\s*(https?://\S+)", desc, re.I)
            urls = [m.group(1)] if m else []
        fields["declaration_url"] = urls[0] if urls else None
        # une plateforme a parfois deux fiches (une par polygone) : on garde les champs renseignés
        for k, v in fields.items():
            if v and not f.get(k):
                f[k] = v
    return {
        "source": URL_DGEF_MAP,
        "api": URL_DGEF_API,
        "note": "Carte interactive publiée par le Webmestre DGEF (ministère de l'Intérieur), liée depuis "
                "immigration.interieur.gouv.fr ; données de la carte mises à jour le 3 octobre 2025.",
        "donnees_du": "2025-10-03",
        "plateformes": out,
    }


# ─── centres d'examen (delf-tcf-tef.fr, liste FEI) ───────────────────────────
def dep_of_cp(cp):
    cp = (cp or "").strip()
    if not re.fullmatch(r"\d{5}", cp):
        return None
    if cp.startswith("97"):
        return cp[:3]
    if cp.startswith("20"):
        return "2A" if cp[:3] in ("200", "201") else "2B"
    return cp[:2]


def build_centres():
    data = DELF_REPO / "_build" / "data"
    out = {"source": "Liste des centres d'examen de France Éducation international, relevée pour "
                     "l'annuaire de delf-tcf-tef.fr", "releve_le": None, "civique": [], "tcf": []}
    for key, fname in (("civique", "civique_france.json"), ("tcf", "tcf_france.json")):
        d = json.load(open(data / fname, encoding="utf-8"))
        out["releve_le"] = d.get("date")
        seen = set()
        for c in d["centres"]:
            dep = dep_of_cp(c.get("cp"))
            if not dep or not c.get("name"):
                continue  # la liste FEI commence par une entrée parasite (le sélecteur de pays)
            k = (c["name"].lower(), c["city"].lower(), c["address"].lower())
            if k in seen:
                continue
            seen.add(k)
            out[key].append({
                "dep": dep, "nom": c["name"].strip(), "adresse": c["address"].strip(),
                "cp": c["cp"], "ville": c["city"].strip(), "tel": c["phone"].strip(),
                "site": c["url"].strip(), "ordinateur": bool(c.get("so")),
            })
    return out


# ─── contours → chemins SVG ──────────────────────────────────────────────────
def dp(points, eps):
    """Douglas-Peucker."""
    if len(points) < 3:
        return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    dx, dy = x2 - x1, y2 - y1
    norm = math.hypot(dx, dy) or 1e-9
    dmax, idx = 0, 0
    for i in range(1, len(points) - 1):
        x, y = points[i]
        d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / norm
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return dp(points[: idx + 1], eps)[:-1] + dp(points[idx:], eps)
    return [points[0], points[-1]]


def dp_ring(ring, eps):
    """Douglas-Peucker sur un anneau ferme : on le coupe au point le plus eloigne du premier."""
    pts = ring[:-1] if ring[0] == ring[-1] else ring
    if len(pts) < 4:
        return []
    far = max(range(len(pts)), key=lambda i: math.hypot(pts[i][0] - pts[0][0], pts[i][1] - pts[0][1]))
    a = dp(pts[: far + 1], eps)
    b = dp(pts[far:] + [pts[0]], eps)
    return a[:-1] + b


def build_paths():
    geo = json.loads(get(URL_CONTOURS))
    lat0 = math.radians(46.6)
    feats = [f for f in geo["features"] if f["properties"]["code"] not in DROM and len(f["properties"]["code"]) <= 2]

    def proj(lon, lat):
        return lon * math.cos(lat0), -lat

    xs, ys = [], []
    for f in feats:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            for ring in poly:
                for lon, lat in ring:
                    x, y = proj(lon, lat)
                    xs.append(x)
                    ys.append(y)
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    W = 1000.0
    k = W / (maxx - minx)
    H = (maxy - miny) * k
    paths, centers = {}, {}
    for f in feats:
        code = f["properties"]["code"]
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        parts, area_best, c_best = [], 0, None
        for poly in polys:
            for ri, ring in enumerate(poly):
                pts = [((proj(lon, lat)[0] - minx) * k, (proj(lon, lat)[1] - miny) * k) for lon, lat in ring]
                simp = dp_ring(pts, 1.1)
                if len(simp) < 4:
                    continue
                # aire (pour placer l'étiquette sur la plus grande partie)
                a = 0.5 * sum(simp[i][0] * simp[i + 1][1] - simp[i + 1][0] * simp[i][1] for i in range(len(simp) - 1))
                if ri == 0 and abs(a) > area_best:
                    area_best = abs(a)
                    c_best = (sum(p[0] for p in simp) / len(simp), sum(p[1] for p in simp) / len(simp))
                ip = [(round(x), round(y)) for x, y in simp]
                d = f"M{ip[0][0]} {ip[0][1]}"
                for (ax, ay), (bx, by) in zip(ip, ip[1:]):
                    if (bx, by) != (ax, ay):
                        d += f"l{bx - ax} {by - ay}"
                parts.append(d + "z")
        paths[code] = "".join(parts)
        centers[code] = [round(c_best[0]), round(c_best[1])] if c_best else None
    sieges = {}
    for pid, (ville, dep) in SIEGES.items():
        q = urllib.parse.urlencode({"nom": ville, "codeDepartement": dep, "fields": "nom,centre", "limit": 5})
        hits = [c for c in json.loads(get("https://geo.api.gouv.fr/communes?" + q)) if fold(c["nom"]) == fold(ville)]
        lon, lat = hits[0]["centre"]["coordinates"]
        x, y = proj(lon, lat)
        sieges[pid] = [round((x - minx) * k), round((y - miny) * k)]
    return {"source": "Etalab, contours administratifs 2025 (départements, 1 000 m), Licence Ouverte 2.0",
            "viewBox": [0, 0, round(W), round(H)], "paths": paths, "centres": centers, "sieges": sieges}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    app_json = APP_REPO / "NaturalisationFranceFacile/Resources/plateformes_naturalisation.json"
    plateformes = json.load(open(app_json, encoding="utf-8"))
    (OUT / "plateformes.json").write_text(json.dumps(plateformes, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    deps = build_departements()
    (OUT / "departements.json").write_text(json.dumps(deps, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    carte = build_carte_dgef(deps["departements"], plateformes["platforms"])
    (OUT / "carte_dgef.json").write_text(json.dumps(carte, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    centres = build_centres()
    (OUT / "centres.json").write_text(json.dumps(centres, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    paths = build_paths()
    (OUT / "carte_paths.json").write_text(json.dumps(paths, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"departements {len(deps['departements'])} · plateformes {len(plateformes['platforms'])} · "
          f"fiches DGEF {len(carte['plateformes'])} · centres civique {len(centres['civique'])} / "
          f"TCF {len(centres['tcf'])} · contours {len(paths['paths'])}")


if __name__ == "__main__":
    main()
