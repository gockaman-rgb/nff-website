#!/usr/bin/env python3
"""Regenere la section HTML rampable des questions du test blanc.

Le quiz de /outils/examen-civique.html est rendu par JavaScript : les
questions vivent dans js/qcm-civique.js et Google n'en voyait rien (314 mots
visibles, position moyenne 71,5). Ce script recopie les questions, leurs
reponses et leurs explications en HTML statique entre les marqueurs
<!-- QCM:START --> et <!-- QCM:END -->, replie dans des <details> pour ne pas
divulgacher le test au lecteur qui fait defiler la page.

Le fichier JS reste la source de verite : relancer ce script apres toute
modification des questions.

    python3 scripts/build_qcm_section.py
"""

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
JS = ROOT / "js" / "qcm-civique.js"
PAGE = ROOT / "outils" / "examen-civique.html"
START, END = "<!-- QCM:START -->", "<!-- QCM:END -->"


def load_questions():
    src = JS.read_text(encoding="utf-8")
    marker = "var DATA = "
    i = src.index(marker) + len(marker)
    data, _ = json.JSONDecoder().raw_decode(src, i)
    return data


def esc(text):
    return html.escape(text, quote=False)


def render(questions):
    out = [
        '    <h2 class="section-title">Les 10 questions, avec les r&eacute;ponses expliqu&eacute;es</h2>',
        '    <p class="section-sub">Chaque question est repli&eacute;e&nbsp;: faites le test d\'abord, '
        "d&eacute;pliez ensuite pour comprendre pourquoi la bonne r&eacute;ponse est la bonne.</p>",
        '    <div class="qcm-answers">',
    ]
    for n, q in enumerate(questions, 1):
        good = q["o"][q["a"]]
        out.append("      <details>")
        out.append(
            f'        <summary><span class="qcm-num">{n}</span> {esc(q["q"])}</summary>'
        )
        out.append('        <ul class="qcm-opts">')
        for j, opt in enumerate(q["o"]):
            mark = ' class="ok"' if j == q["a"] else ""
            out.append(f"          <li{mark}>{esc(opt)}</li>")
        out.append("        </ul>")
        out.append(
            f'        <p class="qcm-good"><strong>R&eacute;ponse&nbsp;: {esc(good)}</strong></p>'
        )
        out.append(f'        <p class="qcm-why">{esc(q["e"])}</p>')
        out.append(f'        <p class="qcm-theme">Th&egrave;me&nbsp;: {esc(q["c"])}</p>')
        out.append("      </details>")
    out.append("    </div>")
    return "\n".join(out)


def build_quiz_schema(questions):
    """Schema.org Quiz : decrit l'exercice sans exposer les bonnes reponses."""
    return {
        "@context": "https://schema.org",
        "@type": "Quiz",
        "name": "Test blanc de l'examen civique de naturalisation",
        "description": (
            "Test blanc gratuit de 10 questions parmi les plus difficiles de l'examen "
            "civique obligatoire pour la naturalisation francaise, avec correction expliquee."
        ),
        "url": "https://naturalisationfrancefacile.fr/outils/examen-civique.html",
        "inLanguage": "fr-FR",
        "isAccessibleForFree": True,
        "educationalLevel": "Examen civique de naturalisation",
        "about": {"@type": "Thing", "name": "Examen civique de naturalisation francaise"},
        "numberOfQuestions": len(questions),
        "hasPart": [
            {
                "@type": "Question",
                "eduQuestionType": "Multiple choice",
                "name": q["q"],
                "acceptedAnswer": {"@type": "Answer", "text": q["o"][q["a"]]},
            }
            for q in questions
        ],
    }


def main():
    questions = load_questions()
    page = PAGE.read_text(encoding="utf-8")

    if START not in page or END not in page:
        sys.exit(f"marqueurs {START} / {END} absents de {PAGE}")

    page = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        START + "\n" + render(questions) + "\n    " + END,
        page,
        flags=re.S,
    )

    schema = (
        '  <script type="application/ld+json">\n  '
        + json.dumps(build_quiz_schema(questions), ensure_ascii=False, indent=2).replace(
            "\n", "\n  "
        )
        + "\n  </script>\n"
    )
    page = re.sub(
        r'  <script type="application/ld\+json">\n  \{\n    "@context": "https://schema\.org",\n    "@type": "Quiz".*?</script>\n',
        schema,
        page,
        flags=re.S,
    )
    if '"@type": "Quiz"' not in page:
        page = page.replace("</head>", schema + "</head>", 1)

    PAGE.write_text(page, encoding="utf-8")

    for block in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', page, re.S
    ):
        json.loads(block)

    print(f"{len(questions)} questions ecrites dans {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
