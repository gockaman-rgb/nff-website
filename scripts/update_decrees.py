#!/usr/bin/env python3
"""
Auto-refresh the naturalisation-decree directory from the DILA open data.

Source: https://echanges.dila.gouv.fr/OPENDATA/JORF/  (public, no auth)
 - daily increment archives  JORF_YYYYMMDD-HHMMSS.tar.gz  (~250 KB each)
 - each contains text XML with <NATURE>, <TITREFULL>, <ID> (JORFTEXT),
   <DATE_PUBLI> (JO date) and <DATE_TEXTE> (decree date).

State is kept in data/decrees.json ({"last_archive": ..., "decrees": [...]}).
Each run processes only archives newer than last_archive, merges any new
"... portant naturalisation ..." decrees, then regenerates the directory
block (between the DECREES:START / DECREES:END markers) in the page.

Standard library only — runs as-is on GitHub Actions (ubuntu, python3).
"""
import io, json, os, re, sys, tarfile, urllib.request, datetime
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "decrees.json")
PAGE = os.path.join(ROOT, "outils", "decret-naturalisation.html")
INDEX = "https://echanges.dila.gouv.fr/OPENDATA/JORF/"
UA = {"User-Agent": "naturalisationfrancefacile-decret-bot/1.0 (+https://naturalisationfrancefacile.fr)"}
MAX_ARCHIVES_PER_RUN = 90   # safety cap; last_archive advances so the next run continues

FR_MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin",
             "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def fr_date(iso):
    """2026-06-20 -> '20 juin 2026' ; 2026-06-01 -> '1er juin 2026'."""
    y, m, d = iso.split("-")
    di = int(d)
    return f"{'1er' if di == 1 else di} {FR_MONTHS[int(m) - 1]} {y}"


def fetch(url, timeout=180):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def list_archives():
    html = fetch(INDEX).decode("utf-8", "replace")
    return sorted(set(re.findall(r"JORF_\d{8}-\d{6}\.tar\.gz", html)))


def parse_archive(blob):
    found = []
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tar:
        for m in tar.getmembers():
            if not (m.isfile() and m.name.endswith(".xml") and "/texte/version/" in m.name):
                continue
            try:
                root = ET.fromstring(tar.extractfile(m).read())
            except Exception:
                continue

            def t(tag):
                e = root.find(".//" + tag)
                return (e.text or "").strip() if e is not None else ""

            if t("NATURE") != "DECRET":
                continue
            title = t("TITREFULL") or t("TITRE_TXT")
            if "portant naturalisation" not in title.lower():
                continue
            jid, dp, dt = t("ID"), t("DATE_PUBLI"), t("DATE_TEXTE")
            if jid.startswith("JORFTEXT") and re.match(r"\d{4}-\d{2}-\d{2}", dp) and re.match(r"\d{4}-\d{2}-\d{2}", dt):
                found.append({"jorftext_id": jid, "jo_date_iso": dp, "decret_date_iso": dt})
    return found


def regenerate_page(decrees):
    html = open(PAGE, encoding="utf-8").read()
    by_year = {}
    for d in decrees:
        by_year.setdefault(d["jo_date_iso"][:4], []).append(d)
    block_lines = []
    for yr in sorted(by_year, reverse=True):
        block_lines.append(f'    <div class="jo-year">{yr}</div>')
        for d in by_year[yr]:
            block_lines.append(
                f'    <a class="jo-row" href="{d["url"]}" target="_blank" rel="noopener">'
                f'<span class="jo-when"><span class="jo-date">JO du {d["jo_date"]}</span>'
                f'<span class="jo-meta">D&eacute;cret du {d["decret_date"]} &middot; naturalisations</span></span>'
                f'<span class="jo-go">Voir le d&eacute;cret &rarr;</span></a>')
    block = "\n".join(block_lines)
    new_html, n = re.subn(
        r"(<!-- DECREES:START -->).*?(<!-- DECREES:END -->)",
        lambda m: m.group(1) + "\n" + block + "\n    " + m.group(2),
        html, flags=re.S)
    if n != 1:
        sys.exit("ERROR: DECREES:START/END markers not found exactly once in the page")
    today = fr_date(datetime.date.today().isoformat())
    new_html = re.sub(
        r'(<p class="updated-note">)Mis &agrave; jour le[^<]*(</p>)',
        lambda m: f'{m.group(1)}Mis &agrave; jour le {today} &middot; {len(decrees)} d&eacute;crets r&eacute;f&eacute;renc&eacute;s{m.group(2)}',
        new_html, count=1)
    open(PAGE, "w", encoding="utf-8").write(new_html)


def main():
    db = json.load(open(DATA, encoding="utf-8")) if os.path.exists(DATA) else {"last_archive": "", "decrees": []}
    seen = {d["jorftext_id"] for d in db["decrees"]}
    archives = list_archives()
    todo = [a for a in archives if a > db.get("last_archive", "")][:MAX_ARCHIVES_PER_RUN]
    added = 0
    for a in todo:
        try:
            blob = fetch(INDEX + a)
        except Exception as e:
            print(f"skip {a}: {e}")
            continue
        for dec in parse_archive(blob):
            if dec["jorftext_id"] not in seen:
                seen.add(dec["jorftext_id"])
                db["decrees"].append({
                    "jorftext_id": dec["jorftext_id"],
                    "jo_date": fr_date(dec["jo_date_iso"]),
                    "decret_date": fr_date(dec["decret_date_iso"]),
                    "jo_date_iso": dec["jo_date_iso"],
                    "decret_date_iso": dec["decret_date_iso"],
                    "url": "https://www.legifrance.gouv.fr/jorf/id/" + dec["jorftext_id"],
                })
                added += 1
        db["last_archive"] = a
    db["decrees"].sort(key=lambda d: (d["jo_date_iso"], d["decret_date_iso"], d["jorftext_id"]), reverse=True)
    json.dump(db, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    regenerate_page(db["decrees"])
    print(f"processed {len(todo)} archive(s); added {added} new decree(s); total {len(db['decrees'])}; last_archive={db['last_archive']}")


if __name__ == "__main__":
    main()
