#!/usr/bin/env python3
"""Genere les articles de blog a partir du dictionnaire ARTICLES.

Les cinq premiers articles ont ete choisis sur les donnees Search Console
(6 mois au 7 aout 2026), en cherchant les intentions ou le site apparait
deja sans satisfaire personne, ou bien n'apparait pas du tout alors que
l'etape existe dans le parcours.

Les cinq suivants (17 septembre 2026) couvrent les voies d'acces a la
nationalite qui exigent aussi le niveau B2, a cote de la declaration par
mariage deja traitee : reintegration, refugies, etudes en France,
dispenses de stage, candidats de plus de 65 ans ; puis "naturalisation
rapide", l'article de methode qui relie les cinq leviers a l'app.

Quatre articles de plus, choisis sur la Search Console (3 mois au 15
septembre 2026) : des requetes ou le site se positionnait deja sans page
dediee ("pourquoi voulez-vous devenir francais" ~300 impressions servies
par l'article "avantages", "avis favorable naturalisation lettre
recommandee", "timbre fiscal 55 EUR naturalisation" 187 impressions sans
clic, "journal officiel naturalisation liste des noms"). Chaque article
porte sa date ("date" / "date_fr"), a defaut TODAY.

Faits verifies (septembre 2026) : l'examen civique ne concerne que les
procedures par decret (service-public F39426) ; les attestations de
comparabilite ENIC-NARIC ne prouvent plus le B2 depuis le 1er janvier
2026 ; la dispense de langue des plus de 60 ans a disparu le 1er avril
2020 (decret 2019-1507).

    python3 scripts/build_articles.py
"""

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
BASE = "https://naturalisationfrancefacile.fr"
APP = "https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087"
TODAY = "2026-08-07"
TODAY_FR = "7 ao&ucirc;t 2026"

APP_SVG = (
    '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">'
    '<path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>'
)
YT_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
TT_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>'


ARTICLES = {
# ═══════════════════════════════════════════════════════════════════════
"casier-judiciaire-naturalisation": {
    "title": "Casier judiciaire et naturalisation : 3 mois ou 6 mois ?",
    "h1": "Casier judiciaire et naturalisation&nbsp;: 3&nbsp;mois, 6&nbsp;mois, ou pas du tout&nbsp;?",
    "desc": "La règle réelle : l'extrait de casier judiciaire étranger n'est exigé que si vous vivez en France depuis moins de 10 ans. Et la règle des 3 mois ne le vise pas.",
    "og": "Casier judiciaire et naturalisation : la vraie r&egrave;gle",
    "tag": "Documents",
    "og_img": "checklist-documents.png",
    "lede": "C'est l'une des questions les plus recherch&eacute;es sur le dossier de naturalisation, et l'une des plus mal expliqu&eacute;es&nbsp;: l'extrait de casier judiciaire &eacute;tranger doit-il dater de moins de 3&nbsp;mois ou de moins de 6&nbsp;mois&nbsp;? La r&eacute;ponse honn&ecirc;te tient en deux points que presque personne ne dit clairement.",
    "body": """
<h2>Le point que tout le monde saute&nbsp;: peut-&ecirc;tre que vous n'en avez pas besoin</h2>

<p>Avant de courir apr&egrave;s un document, v&eacute;rifiez s'il vous est demand&eacute;. La r&egrave;gle officielle est claire&nbsp;: l'extrait de casier judiciaire <strong>&eacute;tranger</strong> n'est exig&eacute; que si vous vivez en France <strong>depuis moins de 10&nbsp;ans</strong>.</p>

<p>Si vous r&eacute;sidez en France depuis 10&nbsp;ans ou plus &agrave; la date de d&eacute;p&ocirc;t, ce document ne fait pas partie des pi&egrave;ces &agrave; fournir. Beaucoup de candidats perdent des semaines et de l'argent &agrave; obtenir un document que leur pr&eacute;fecture ne leur demandera pas.</p>

<div class="callout">
  <p><strong>&Agrave; retenir&nbsp;:</strong> moins de 10&nbsp;ans de r&eacute;sidence en France &rarr; extrait de casier judiciaire &eacute;tranger exig&eacute;. 10&nbsp;ans ou plus &rarr; non exig&eacute;.</p>
</div>

<h2>Et le casier judiciaire fran&ccedil;ais&nbsp;?</h2>

<p>Vous n'avez pas &agrave; le demander. L'administration consulte elle-m&ecirc;me votre <strong>bulletin n&deg;&nbsp;2</strong> du casier judiciaire national dans le cadre de l'instruction. C'est une v&eacute;rification interne, pas une pi&egrave;ce &agrave; joindre &agrave; votre dossier.</p>

<p>Ce que vous devez fournir, c'est le document &eacute;quivalent d&eacute;livr&eacute; par le ou les <strong>pays &eacute;trangers</strong> o&ugrave; vous avez v&eacute;cu &mdash; ou, &agrave; d&eacute;faut, par votre pays de nationalit&eacute;.</p>

<h2>D'o&ugrave; vient la confusion entre 3 et 6&nbsp;mois</h2>

<p>La r&egrave;gle des <strong>3&nbsp;mois</strong> existe bel et bien, mais elle ne vise pas le casier judiciaire&nbsp;: elle concerne les <strong>actes d'&eacute;tat civil fran&ccedil;ais</strong>, qui doivent &ecirc;tre d&eacute;livr&eacute;s depuis moins de trois mois. C'est cette r&egrave;gle que les forums transposent, &agrave; tort, &agrave; l'extrait de casier.</p>

<p>Pour l'extrait de casier judiciaire &eacute;tranger, la r&eacute;glementation exige un document <strong>original</strong>, d&eacute;livr&eacute; par une autorit&eacute; comp&eacute;tente, mais ne fixe pas de dur&eacute;e de validit&eacute; nationale uniforme. En pratique, les pr&eacute;fectures attendent un document <strong>r&eacute;cent</strong>, et la fourchette g&eacute;n&eacute;ralement admise va de 3 &agrave; 6&nbsp;mois selon les d&eacute;partements et selon le d&eacute;lai d'obtention dans votre pays d'origine.</p>

<p>La cons&eacute;quence pratique&nbsp;: <strong>visez moins de 3&nbsp;mois si vous le pouvez</strong>. Un document de moins de 3&nbsp;mois est accept&eacute; partout&nbsp;; un document de 5&nbsp;mois peut passer dans une pr&eacute;fecture et &ecirc;tre refus&eacute; dans une autre. Ne pariez pas sur l'interpr&eacute;tation la plus favorable.</p>

<h2>Quels pays devez-vous couvrir&nbsp;?</h2>

<p>Pas seulement votre pays de naissance. Vous devez fournir un extrait pour <strong>chaque pays o&ugrave; vous avez r&eacute;sid&eacute;</strong> avant votre installation en France. Si vous avez v&eacute;cu au Maroc puis en Espagne avant d'arriver en France il y a six ans, il vous faudra les deux documents.</p>

<p>Si un pays ne d&eacute;livre pas ce type de document, ou si vous ne pouvez pas l'obtenir, fournissez une <strong>attestation motiv&eacute;e</strong> de l'autorit&eacute; consulaire expliquant l'impossibilit&eacute;, plut&ocirc;t que de laisser un vide dans le dossier. Un dossier qui explique une absence est mieux trait&eacute; qu'un dossier incomplet sans commentaire.</p>

<h2>Traduction, l&eacute;galisation, apostille</h2>

<p>Un document r&eacute;dig&eacute; en langue &eacute;trang&egrave;re doit &ecirc;tre accompagn&eacute; d'une <strong>traduction par un traducteur agr&eacute;&eacute;</strong>, habilit&eacute; &agrave; intervenir aupr&egrave;s des autorit&eacute;s judiciaires ou administratives fran&ccedil;aises. C'est l'original de la traduction qui est demand&eacute;, pas une photocopie.</p>

<p>S'y ajoute, selon le pays d'origine, une <strong>l&eacute;galisation</strong> ou une <strong>apostille</strong>. La distinction d&eacute;pend des conventions sign&eacute;es par le pays&nbsp;: l'apostille pour les &Eacute;tats parties &agrave; la convention de La Haye, la l&eacute;galisation consulaire pour les autres. V&eacute;rifiez aupr&egrave;s du consulat concern&eacute; avant de lancer la traduction, car l'apostille se pose sur le document d'origine.</p>

<h2>L'ordre des op&eacute;rations, qui fait gagner des semaines</h2>

<ol>
  <li><strong>V&eacute;rifiez d'abord votre anciennet&eacute; de r&eacute;sidence.</strong> Moins de 10&nbsp;ans en France&nbsp;? Continuez. Sinon, passez &agrave; la pi&egrave;ce suivante de votre dossier.</li>
  <li><strong>Listez tous les pays de r&eacute;sidence</strong> ant&eacute;rieurs, pas seulement celui de votre nationalit&eacute;.</li>
  <li><strong>Renseignez-vous sur le d&eacute;lai d'obtention</strong> dans chacun. Il varie de quelques jours &agrave; plusieurs mois. C'est ce d&eacute;lai qui d&eacute;termine quand lancer la demande.</li>
  <li><strong>Faites apostiller ou l&eacute;galiser</strong> le document d'origine.</li>
  <li><strong>Faites traduire ensuite</strong> par un traducteur agr&eacute;&eacute;.</li>
  <li><strong>D&eacute;posez rapidement.</strong> Le compteur de fra&icirc;cheur court &agrave; partir de la date de d&eacute;livrance, pas de la traduction.</li>
</ol>

<h2>Un ant&eacute;c&eacute;dent judiciaire est-il r&eacute;dhibitoire&nbsp;?</h2>

<p>Pas m&eacute;caniquement. L'administration appr&eacute;cie la nature des faits, leur anciennet&eacute; et leur gravit&eacute;. Une contravention ancienne et une condamnation r&eacute;cente pour des faits graves ne pr&eacute;sentent &eacute;videmment pas le m&ecirc;me poids.</p>

<p>Ce qui, en revanche, nuit &agrave; coup s&ucirc;r&nbsp;: <strong>l'omission</strong>. Une d&eacute;claration incompl&egrave;te d&eacute;couverte en cours d'instruction p&egrave;se plus lourd que le fait lui-m&ecirc;me. Si votre situation est complexe, faites-la examiner par un avocat avant de d&eacute;poser plut&ocirc;t que de tenter votre chance.</p>

<h2>Combien de temps faut-il pour l'obtenir&nbsp;?</h2>

<p>C'est la variable qui d&eacute;termine tout votre calendrier, et elle &eacute;chappe compl&egrave;tement &agrave; l'administration fran&ccedil;aise. Les d&eacute;lais varient &eacute;norm&eacute;ment selon le pays&nbsp;: quelques jours l&agrave; o&ugrave; la demande est enti&egrave;rement d&eacute;mat&eacute;rialis&eacute;e, plusieurs mois l&agrave; o&ugrave; elle suppose un passage physique ou une proc&eacute;dure consulaire.</p>

<p>Trois questions &agrave; poser avant de lancer la d&eacute;marche&nbsp;:</p>

<ul>
  <li><strong>La demande peut-elle se faire &agrave; distance&nbsp;?</strong> Certains pays exigent une pr&eacute;sence sur place ou une procuration notari&eacute;e, ce qui change radicalement le calendrier.</li>
  <li><strong>Le consulat en France peut-il s'en charger&nbsp;?</strong> Beaucoup de consulats transmettent la demande &agrave; leur administration centrale. C'est souvent plus lent, mais cela &eacute;vite un voyage.</li>
  <li><strong>L'apostille se pose-t-elle dans le pays d'origine&nbsp;?</strong> Presque toujours oui &mdash; et c'est une &eacute;tape suppl&eacute;mentaire &agrave; anticiper, pas &agrave; d&eacute;couvrir apr&egrave;s coup.</li>
</ul>

<p>La cons&eacute;quence pratique est contre-intuitive&nbsp;: c'est souvent la pi&egrave;ce qu'il faut demander <strong>en premier</strong>, alors qu'on la traite en dernier parce qu'elle para&icirc;t secondaire.</p>

<h2>Les situations particuli&egrave;res</h2>

<h3>R&eacute;fugi&eacute;s et apatrides</h3>

<p>Si vous &ecirc;tes r&eacute;fugi&eacute; ou apatride, vous ne pouvez pas, par d&eacute;finition, solliciter les autorit&eacute;s du pays que vous avez fui. C'est l'<strong>OFPRA</strong> qui &eacute;tablit les documents tenant lieu d'&eacute;tat civil, et votre statut est pris en compte pour cette pi&egrave;ce comme pour les autres. Ne tentez surtout pas de contacter votre consulat d'origine&nbsp;: cela peut &ecirc;tre interpr&eacute;t&eacute; comme une reprise de contact avec les autorit&eacute;s dont vous demandiez protection.</p>

<h3>Pays sans administration fonctionnelle</h3>

<p>Guerre, effondrement de l'&Eacute;tat civil, archives d&eacute;truites&nbsp;: l'administration fran&ccedil;aise conna&icirc;t ces situations. La bonne r&eacute;ponse n'est jamais de laisser la case vide, mais de <strong>documenter l'impossibilit&eacute;</strong> &mdash; attestation consulaire, courrier de refus, preuve des d&eacute;marches entreprises. Un dossier qui explique une absence se traite&nbsp;; un dossier silencieux repart en demande de compl&eacute;ment.</p>

<h3>Plusieurs pays de r&eacute;sidence</h3>

<p>Une question revient souvent&nbsp;: &agrave; partir de combien de temps un s&eacute;jour compte-t-il comme une r&eacute;sidence&nbsp;? Il n'y a pas de seuil officiel unique. Le crit&egrave;re retenu est celui de la <strong>r&eacute;sidence</strong> et non du passage&nbsp;: des vacances ou une mission de quelques semaines ne cr&eacute;ent pas d'obligation, un s&eacute;jour de plusieurs mois avec adresse et activit&eacute; sur place, oui. Dans le doute, fournissez le document&nbsp;: un extrait de trop ne p&eacute;nalise jamais un dossier.</p>

<h2>Et si le document arrive apr&egrave;s le d&eacute;p&ocirc;t&nbsp;?</h2>

<p>Ce n'est pas ind&eacute;passable, mais cela co&ucirc;te du temps. Deux strat&eacute;gies&nbsp;:</p>

<ol>
  <li><strong>Attendre et d&eacute;poser complet.</strong> Recommand&eacute; dans la plupart des cas&nbsp;: c'est le d&eacute;p&ocirc;t d'un dossier complet qui d&eacute;clenche le r&eacute;c&eacute;piss&eacute; de compl&eacute;tude, lequel fait courir le d&eacute;lai l&eacute;gal d'instruction. Un dossier incomplet ne fait pas d&eacute;marrer le compteur.</li>
  <li><strong>D&eacute;poser en signalant la pi&egrave;ce en cours.</strong> Justifiable si votre certificat de langue ou votre titre de s&eacute;jour approche de sa limite. Joignez la preuve de la d&eacute;marche engag&eacute;e aupr&egrave;s de l'autorit&eacute; &eacute;trang&egrave;re.</li>
</ol>

<p>Dans les deux cas, gardez en t&ecirc;te la <a href="/blog/delais-naturalisation-par-prefecture.html">m&eacute;canique des d&eacute;lais</a>&nbsp;: chaque aller-retour pour une pi&egrave;ce manquante co&ucirc;te plusieurs semaines, entre l'envoi de la demande, votre r&eacute;ponse et le r&eacute;examen.</p>
""",
    "faq": [
        ("L'extrait de casier judiciaire pour la naturalisation doit-il dater de moins de 3 mois ou de 6 mois ?",
         "La réglementation exige un extrait original délivré par une autorité compétente, sans fixer de durée de validité nationale uniforme. La règle des 3 mois que l'on lit partout concerne en réalité les actes d'état civil français. En pratique, les préfectures attendent un document récent, généralement de moins de 3 à 6 mois. Visez moins de 3 mois : ce format est accepté partout."),
        ("Faut-il fournir un casier judiciaire si je vis en France depuis plus de 10 ans ?",
         "Non. L'extrait de casier judiciaire étranger n'est exigé que des personnes qui vivent en France depuis moins de 10 ans. Au-delà, ce document ne fait pas partie des pièces à fournir."),
        ("Dois-je demander mon casier judiciaire français ?",
         "Non. L'administration consulte elle-même votre bulletin n° 2 du casier judiciaire national pendant l'instruction. Vous n'avez pas à le joindre au dossier."),
        ("Combien de pays dois-je couvrir ?",
         "Tous ceux où vous avez résidé avant la France, pas seulement votre pays de nationalité. Si un pays ne délivre pas ce document, joignez une attestation motivée de l'autorité consulaire plutôt que de laisser un vide."),
        ("Faut-il traduire et apostiller l'extrait de casier judiciaire ?",
         "Oui pour la traduction : un document en langue étrangère doit être traduit par un traducteur agréé, et c'est l'original de la traduction qui est demandé. Selon le pays, s'y ajoute une apostille (États parties à la convention de La Haye) ou une légalisation consulaire. Faites apostiller avant de faire traduire."),
        ("Je suis réfugié : comment obtenir un casier judiciaire de mon pays d'origine ?",
         "Vous n'avez pas à le demander, et vous ne devez surtout pas contacter le consulat du pays que vous avez fui : c'est l'OFPRA qui établit les documents tenant lieu d'état civil pour les réfugiés et apatrides. Votre statut est pris en compte pour cette pièce comme pour les autres."),
        ("Mon pays ne délivre pas ce document, que faire ?",
         "Ne laissez pas la case vide : documentez l'impossibilité. Une attestation de l'autorité consulaire, un courrier de refus ou la preuve des démarches entreprises permettent à l'administration de traiter votre dossier. Un dossier qui explique une absence avance ; un dossier silencieux repart en demande de complément."),
        ("Combien de temps prévoir pour obtenir l'extrait ?",
         "Cela dépend entièrement du pays : de quelques jours quand la demande est dématérialisée à plusieurs mois quand elle suppose une présence sur place ou une procédure consulaire, sans compter l'apostille. C'est souvent la pièce à demander en premier, alors qu'on la traite en dernier parce qu'elle paraît secondaire."),
    ],
    "links": [
        ("/blog/documents-naturalisation.html", "La liste compl&egrave;te des documents du dossier"),
        ("/blog/erreurs-dossier-naturalisation.html", "Les erreurs qui font rejeter un dossier"),
        ("/blog/conditions-naturalisation-francaise.html", "Les 7 conditions de la naturalisation"),
        ("/blog/naturalisation-refugie-2026.html", "R&eacute;fugi&eacute;s&nbsp;: l'&eacute;tat civil vient de l'OFPRA, pas du consulat"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation fran&ccedil;aise par d&eacute;cret (F2213)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F34708/1_0_0_1_1_1_0", "Service-public.gouv.fr &mdash; Pi&egrave;ces &agrave; fournir"),
    ],
    "cta": "V&eacute;rifier ma checklist de documents",
},
# ═══════════════════════════════════════════════════════════════════════
"apres-entretien-naturalisation": {
    "title": "Après l'entretien de naturalisation : que se passe-t-il ?",
    "h1": "Apr&egrave;s l'entretien d'assimilation&nbsp;: ce qui se passe vraiment",
    "desc": "Le compte rendu, l'avis du préfet, la transmission au ministère : les étapes après l'entretien, les délais à connaître et ce qu'un silence prolongé signifie.",
    "og": "Apr&egrave;s l'entretien de naturalisation : les &eacute;tapes",
    "tag": "Entretien",
    "og_img": "simulation-entretien.png",
    "lede": "L'entretien est pass&eacute;. Vous &ecirc;tes sorti sans savoir si &ccedil;a s'est bien pass&eacute;, personne ne vous a rien dit, et votre espace en ligne n'a pas boug&eacute; depuis. Voici ce qui se produit r&eacute;ellement derri&egrave;re, dans quel ordre, et &agrave; partir de quand un silence devient anormal.",
    "body": """
<h2>&Eacute;tape 1&nbsp;: le compte rendu d'entretien</h2>

<p>L'agent qui vous a re&ccedil;u r&eacute;dige un compte rendu. Ce document n'est pas une note sur 20&nbsp;: c'est un texte qui d&eacute;crit votre parcours, votre niveau de fran&ccedil;ais tel qu'il s'est manifest&eacute; dans l'&eacute;change, votre connaissance des droits et devoirs, et votre adh&eacute;sion aux principes de la R&eacute;publique.</p>

<p>C'est la pi&egrave;ce la plus subjective de tout votre dossier, et l'une des plus influentes. Vous ne la recevez pas&nbsp;: elle circule en interne.</p>

<h2>&Eacute;tape 2&nbsp;: l'avis du pr&eacute;fet</h2>

<p>Sur la base du dossier complet et du compte rendu, la pr&eacute;fecture formule un <strong>avis</strong>&nbsp;: favorable, favorable avec r&eacute;serves, ou d&eacute;favorable. Cet avis n'est pas la d&eacute;cision finale, mais il p&egrave;se lourd&nbsp;: le minist&egrave;re suit g&eacute;n&eacute;ralement la recommandation locale. Ce qu'il vaut juridiquement, comment on l'apprend et ce qui peut encore bloquer&nbsp;: voir notre guide de l'<a href="/blog/avis-favorable-naturalisation.html">avis favorable</a>.</p>

<p>&Agrave; ce stade, rien ne change dans votre espace en ligne. C'est normal, et c'est la premi&egrave;re source d'angoisse&nbsp;: le dossier avance sans que l'affichage bouge.</p>

<h2>&Eacute;tape 3&nbsp;: la transmission au minist&egrave;re</h2>

<p>Le dossier part ensuite &agrave; la <a href="/glossaire/sdanf.html">SDANF</a>, la sous-direction de l'acc&egrave;s &agrave; la nationalit&eacute; fran&ccedil;aise, bas&eacute;e &agrave; Rez&eacute;. C'est elle qui instruit au niveau national et pr&eacute;pare la d&eacute;cision.</p>

<p>Ce changement de service est invisible c&ocirc;t&eacute; usager. Beaucoup de dossiers restent affich&eacute;s &laquo;&nbsp;en cours d'instruction&nbsp;&raquo; alors qu'ils ont d&eacute;j&agrave; chang&eacute; de main.</p>

<h2>&Eacute;tape 4&nbsp;: la d&eacute;cision, et ses trois issues</h2>

<ul>
  <li><strong>D&eacute;cision favorable</strong> &mdash; votre nom figurera dans un d&eacute;cret. Vous &ecirc;tes fran&ccedil;ais &agrave; la date de signature du d&eacute;cret, avant m&ecirc;me la <a href="/blog/ceremonie-naturalisation-que-se-passe-t-il.html">c&eacute;r&eacute;monie d'accueil</a>.</li>
  <li><strong>Ajournement</strong> &mdash; votre demande est report&eacute;e, avec un d&eacute;lai impos&eacute; avant de pouvoir red&eacute;poser. Ce n'est pas un refus&nbsp;: c'est un &laquo;&nbsp;pas maintenant&nbsp;&raquo;, souvent li&eacute; &agrave; une situation professionnelle ou &agrave; un niveau de langue jug&eacute; encore insuffisant.</li>
  <li><strong>Refus ou irrecevabilit&eacute;</strong> &mdash; la demande est rejet&eacute;e. Vous disposez alors de <strong>2&nbsp;mois</strong> pour former un <a href="/glossaire/rapo.html">RAPO</a>.</li>
</ul>

<h2>Combien de temps faut-il attendre&nbsp;?</h2>

<p>Le d&eacute;lai l&eacute;gal ne court pas depuis l'entretien mais depuis la <strong>d&eacute;livrance du r&eacute;c&eacute;piss&eacute; de compl&eacute;tude</strong>&nbsp;: l'administration dispose de <strong>18&nbsp;mois</strong> pour r&eacute;pondre, ramen&eacute;s &agrave; <strong>12&nbsp;mois</strong> si vous r&eacute;sidez en France depuis plus de dix ans.</p>

<p>En pratique, entre l'entretien et la publication du d&eacute;cret, comptez le plus souvent <strong>plusieurs mois</strong>, avec de forts &eacute;carts d'une pr&eacute;fecture &agrave; l'autre. Notre guide des <a href="/blog/delais-naturalisation-2026.html">d&eacute;lais de naturalisation</a> d&eacute;taille chaque phase.</p>

<h2>&laquo;&nbsp;J'ai l'impression d'avoir rat&eacute; mon entretien&nbsp;&raquo;</h2>

<p>C'est un ressenti tr&egrave;s r&eacute;pandu et il est mauvais conseiller. L'entretien n'est pas un examen&nbsp;: il n'y a pas de seuil de bonnes r&eacute;ponses, et un agent laconique n'est pas un agent d&eacute;favorable. Beaucoup de candidats persuad&eacute;s d'avoir &eacute;chou&eacute; re&ccedil;oivent une d&eacute;cision favorable.</p>

<p>Ce qui p&egrave;se r&eacute;ellement&nbsp;: une <strong>incoh&eacute;rence</strong> entre vos r&eacute;ponses et les pi&egrave;ces du dossier, une <strong>difficult&eacute; manifeste &agrave; soutenir un &eacute;change</strong> en fran&ccedil;ais, ou une r&eacute;ponse qui contredit frontalement les principes r&eacute;publicains. Une date d'histoire oubli&eacute;e ne fait pas &eacute;chouer un dossier.</p>

<h2>Que faire pendant l'attente</h2>

<ol>
  <li><strong>Ne d&eacute;posez pas de nouveau dossier.</strong> Cela n'acc&eacute;l&egrave;re rien et brouille l'instruction.</li>
  <li><strong>Surveillez votre espace en ligne et votre courrier</strong>, y compris les indésirables. Une demande de pi&egrave;ce compl&eacute;mentaire non vue fait perdre des mois.</li>
  <li><strong>Signalez tout changement</strong> d'adresse, de situation familiale ou professionnelle. Un dossier qui ne refl&egrave;te plus votre situation r&eacute;elle est un dossier fragile.</li>
  <li><strong>Ne relancez pas avant le d&eacute;lai l&eacute;gal.</strong> Une relance pr&eacute;matur&eacute;e n'a aucun effet. Pass&eacute; ce d&eacute;lai, en revanche, elle est l&eacute;gitime&nbsp;: voir notre guide <a href="/blog/relance-naturalisation-que-faire-sans-reponse.html">relancer sans r&eacute;ponse</a>.</li>
</ol>

<h2>&Agrave; partir de quand s'inqui&eacute;ter</h2>

<p>Un dossier sans mouvement pendant plusieurs mois est <strong>banal</strong>. Le vrai signal d'alerte, c'est le d&eacute;passement du d&eacute;lai l&eacute;gal &mdash; 18&nbsp;mois, ou 12 selon votre situation &mdash; &agrave; compter du r&eacute;c&eacute;piss&eacute; de compl&eacute;tude. C'est &agrave; ce moment-l&agrave; qu'une relance &eacute;crite, puis un recours, prennent tout leur sens.</p>

<h2>Si votre situation change entre l'entretien et la d&eacute;cision</h2>

<p>C'est le point le plus souvent n&eacute;glig&eacute;, et celui qui co&ucirc;te le plus cher. Votre dossier a &eacute;t&eacute; instruit sur une photographie de votre situation&nbsp;; si elle bouge pendant les mois d'attente, l'administration doit le savoir. Un dossier qui ne refl&egrave;te plus la r&eacute;alit&eacute; au moment de la d&eacute;cision est un dossier fragile.</p>

<ul>
  <li><strong>D&eacute;m&eacute;nagement</strong> &mdash; &agrave; signaler imm&eacute;diatement. C'est la premi&egrave;re cause de courrier jamais re&ccedil;u, et donc de d&eacute;cision notifi&eacute;e dans le vide, d&eacute;lai de recours compris.</li>
  <li><strong>Perte d'emploi</strong> &mdash; &agrave; signaler, m&ecirc;me si l'annonce est inconfortable. Une situation d&eacute;grad&eacute;e d&eacute;couverte par l'administration p&egrave;se plus lourd qu'une situation d&eacute;grad&eacute;e annonc&eacute;e et document&eacute;e. Voir <a href="/blog/ressources-revenus-naturalisation.html">ce que la pr&eacute;fecture regarde en mati&egrave;re de ressources</a>.</li>
  <li><strong>Mariage, divorce, naissance</strong> &mdash; toute modification de l'&eacute;tat civil est &agrave; signaler avec les actes correspondants. Une naissance peut ouvrir l'effet collectif pour l'enfant, encore faut-il qu'il soit connu du dossier.</li>
  <li><strong>Titre de s&eacute;jour qui expire</strong> &mdash; renouvelez-le normalement. Une demande de naturalisation en cours ne vous dispense pas d'&ecirc;tre en s&eacute;jour r&eacute;gulier, et une rupture de r&eacute;gularit&eacute; peut faire basculer le dossier en irrecevabilit&eacute;.</li>
  <li><strong>Condamnation ou proc&eacute;dure en cours</strong> &mdash; l'administration le verra au bulletin n&deg;&nbsp;2. La d&eacute;couvrir par elle-m&ecirc;me est toujours pire que l'apprendre de vous.</li>
</ul>

<h2>Comment chaque d&eacute;cision vous parvient</h2>

<p>Les canaux diff&egrave;rent selon l'issue, et savoir lequel surveiller &eacute;vite bien des angoisses&nbsp;:</p>

<ul>
  <li><strong>Favorable</strong> &mdash; il n'y a g&eacute;n&eacute;ralement pas de courrier annon&ccedil;ant &laquo;&nbsp;c'est accept&eacute;&nbsp;&raquo;. Ce que vous verrez, c'est la parution de votre d&eacute;cret. Depuis f&eacute;vrier 2023, l'espace ANEF signale automatiquement cette publication&nbsp;; vous pouvez aussi la v&eacute;rifier dans l'<a href="/outils/decret-naturalisation.html">annuaire des d&eacute;crets publi&eacute;s au Journal officiel</a> et <a href="/blog/journal-officiel-naturalisation-liste-des-noms.html">t&eacute;l&eacute;charger l'extrait nominatif</a> sur L&eacute;gifrance. La pr&eacute;fecture vous convoque ensuite &agrave; la <a href="/blog/ceremonie-naturalisation-que-se-passe-t-il.html">c&eacute;r&eacute;monie d'accueil</a>.</li>
  <li><strong>Ajournement, refus, irrecevabilit&eacute;</strong> &mdash; ces d&eacute;cisions sont <strong>notifi&eacute;es</strong>, par courrier ou via le t&eacute;l&eacute;service. La date de notification est capitale&nbsp;: c'est elle, et non la date de la d&eacute;cision, qui fait courir vos deux mois de recours. Notez-la d&egrave;s r&eacute;ception.</li>
</ul>

<p>Cette asym&eacute;trie explique un malentendu fr&eacute;quent&nbsp;: l'absence de courrier n'est pas un mauvais signe. Une d&eacute;cision d&eacute;favorable, elle, se manifeste toujours par un &eacute;crit motiv&eacute;.</p>

<h2>Le compte rendu d'entretien&nbsp;: peut-on le consulter&nbsp;?</h2>

<p>Vous ne le recevez pas spontan&eacute;ment. En revanche, en cas de d&eacute;cision d&eacute;favorable, il devient un &eacute;l&eacute;ment utile pour comprendre ce qui a p&eacute;ch&eacute; et construire un <a href="/glossaire/rapo.html">RAPO</a> qui r&eacute;pond aux vrais motifs plut&ocirc;t qu'&agrave; des motifs suppos&eacute;s. Les documents administratifs vous concernant peuvent faire l'objet d'une demande de communication&nbsp;; c'est une d&eacute;marche &agrave; envisager si les motifs notifi&eacute;s vous paraissent flous.</p>

<p>En pratique, la d&eacute;cision motiv&eacute;e que vous recevez suffit le plus souvent&nbsp;: c'est elle qu'il faut r&eacute;futer point par point, pi&egrave;ces &agrave; l'appui.</p>
""",
    "faq": [
        ("Combien de temps entre l'entretien de naturalisation et la réponse ?",
         "Le délai légal court depuis la délivrance du récépissé de complétude, pas depuis l'entretien : l'administration dispose de 18 mois pour répondre, ramenés à 12 mois si vous résidez en France depuis plus de dix ans. En pratique, plusieurs mois s'écoulent entre l'entretien et la publication du décret, avec de forts écarts selon les préfectures."),
        ("Comment savoir si mon entretien d'assimilation s'est bien passé ?",
         "Vous ne le saurez pas sur le moment : l'agent rédige un compte rendu interne que vous ne recevez pas, et un agent peu expansif n'est pas un agent défavorable. Ce qui pèse réellement, ce sont les incohérences entre vos réponses et votre dossier, une difficulté manifeste à soutenir un échange en français, ou une réponse contraire aux principes républicains — pas une date d'histoire oubliée."),
        ("Mon statut en ligne ne bouge pas depuis l'entretien, est-ce mauvais signe ?",
         "Non. Le passage de la préfecture au ministère et l'instruction nationale ne se traduisent pas toujours par un changement de libellé. Un dossier peut rester affiché « en cours d'instruction » pendant des mois tout en avançant."),
        ("Que se passe-t-il si l'avis du préfet est défavorable ?",
         "L'avis du préfet n'est pas la décision finale : c'est le ministère qui décide, même s'il suit généralement la recommandation locale. En cas de refus ou d'ajournement, vous disposez de 2 mois à compter de la notification pour former un RAPO."),
        ("Faut-il relancer la préfecture après l'entretien ?",
         "Pas avant l'expiration du délai légal : une relance prématurée n'a aucun effet. Passé 18 mois (ou 12 selon votre situation) à compter du récépissé de complétude, une relance écrite est légitime et utile."),
        ("Je déménage pendant l'instruction, dois-je le signaler ?",
         "Oui, immédiatement. C'est la première cause de courrier jamais reçu — donc de décision notifiée dans le vide, délai de recours compris. Signalez aussi toute perte d'emploi, tout changement d'état civil et tout renouvellement de titre de séjour : un dossier qui ne reflète plus votre situation réelle au moment de la décision est un dossier fragile."),
        ("Comment vais-je savoir que ma naturalisation est acceptée ?",
         "Il n'y a généralement pas de courrier annonçant l'acceptation : ce que vous verrez, c'est la parution de votre décret. L'espace ANEF signale automatiquement cette publication depuis février 2023. À l'inverse, un ajournement, un refus ou une irrecevabilité sont toujours notifiés par écrit et motivés."),
        ("Mon titre de séjour expire pendant l'instruction, que faire ?",
         "Renouvelez-le normalement. Une demande de naturalisation en cours ne dispense pas d'être en séjour régulier, et une rupture de régularité peut faire basculer le dossier en irrecevabilité."),
    ],
    "links": [
        ("/blog/entretien-naturalisation-prefectures.html", "L'entretien en pr&eacute;fecture&nbsp;: comment il se d&eacute;roule"),
        ("/blog/avis-favorable-naturalisation.html", "Avis favorable&nbsp;: ce que &ccedil;a vaut, et combien de temps avant le d&eacute;cret"),
        ("/blog/suivre-dossier-naturalisation-anef.html", "Suivre son dossier sur l'ANEF"),
        ("/blog/ajournement-vs-refus-naturalisation.html", "Ajournement ou refus&nbsp;: que faire"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret (F2213)"),
        ("https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000699753", "D&eacute;cret n&deg;&nbsp;93-1362 &mdash; proc&eacute;dure de naturalisation"),
    ],
    "cta": "S'entra&icirc;ner &agrave; l'entretien dans l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"delais-naturalisation-par-prefecture": {
    "title": "Délais de naturalisation : pourquoi ça varie par préfecture",
    "h1": "D&eacute;lais de naturalisation par pr&eacute;fecture&nbsp;: d'o&ugrave; viennent les &eacute;carts",
    "desc": "Pourquoi deux dossiers identiques déposés à Paris et en Lozère n'avancent pas au même rythme, et comment situer le vôtre sans se fier aux forums.",
    "og": "Pourquoi les d&eacute;lais varient d'une pr&eacute;fecture &agrave; l'autre",
    "tag": "D&eacute;lais",
    "og_img": "suivi-relance.png",
    "lede": "&laquo;&nbsp;Mon coll&egrave;gue a eu sa r&eacute;ponse en 10&nbsp;mois, moi j'attends depuis deux ans.&nbsp;&raquo; Les &eacute;carts entre pr&eacute;fectures sont r&eacute;els et parfois du simple au double. Voici ce qui les explique, et ce que vous pouvez en faire.",
    "body": """
<h2>Un d&eacute;lai l&eacute;gal identique, des r&eacute;alit&eacute;s tr&egrave;s diff&eacute;rentes</h2>

<p>La loi ne fait pas de diff&eacute;rence selon le d&eacute;partement&nbsp;: l'administration dispose de <strong>18&nbsp;mois</strong> pour r&eacute;pondre &agrave; compter de la d&eacute;livrance du r&eacute;c&eacute;piss&eacute; de compl&eacute;tude, d&eacute;lai ramen&eacute; &agrave; <strong>12&nbsp;mois</strong> si vous r&eacute;sidez en France depuis plus de dix ans.</p>

<p>Ce d&eacute;lai encadre la r&eacute;ponse de l'administration. Il ne dit rien du temps total entre le moment o&ugrave; vous commencez &agrave; rassembler vos pi&egrave;ces et celui o&ugrave; votre nom para&icirc;t au Journal officiel &mdash; qui est ce que les gens comparent entre eux.</p>

<h2>Les quatre facteurs qui creusent l'&eacute;cart</h2>

<h3>1. Le volume de dossiers rapport&eacute; aux effectifs</h3>

<p>C'est le facteur dominant. Une pr&eacute;fecture d'&Icirc;le-de-France traite un nombre de demandes sans commune mesure avec celle d'un d&eacute;partement rural, sans que ses effectifs suivent la m&ecirc;me proportion. La file d'attente est plus longue avant m&ecirc;me que quiconque ouvre votre dossier.</p>

<h3>2. Le d&eacute;lai de convocation &agrave; l'entretien</h3>

<p>Dans certains d&eacute;partements, l'<a href="/blog/entretien-naturalisation-prefectures.html">entretien d'assimilation</a> est fix&eacute; quelques semaines apr&egrave;s le d&eacute;p&ocirc;t&nbsp;; ailleurs, il faut attendre plusieurs mois. Ce cr&eacute;neau est souvent le principal goulot d'&eacute;tranglement, et il d&eacute;pend enti&egrave;rement des capacit&eacute;s locales.</p>

<h3>3. La compl&eacute;tude de votre dossier</h3>

<p>C'est le seul facteur que vous ma&icirc;trisez, et il n'est pas marginal. Chaque demande de pi&egrave;ce compl&eacute;mentaire ajoute un aller-retour de plusieurs semaines&nbsp;: le temps que la demande vous parvienne, que vous obteniez le document, qu'il soit traduit s'il y a lieu, et qu'il soit r&eacute;examin&eacute;. Deux ou trois allers-retours suffisent &agrave; ajouter six mois.</p>

<h3>4. La complexit&eacute; de votre situation</h3>

<p>Un parcours lin&eacute;aire &mdash; m&ecirc;me employeur, m&ecirc;me adresse, un seul pays d'origine &mdash; s'instruit plus vite qu'un dossier avec plusieurs pays de r&eacute;sidence, des p&eacute;riodes &agrave; l'&eacute;tranger ou une situation familiale &agrave; reconstituer.</p>

<h2>Les ordres de grandeur observ&eacute;s</h2>

<p>Aucune administration ne publie de tableau officiel des d&eacute;lais par d&eacute;partement, et il faut se m&eacute;fier des sites qui en affichent un&nbsp;: ces chiffres sont invariablement reconstitu&eacute;s &agrave; partir de t&eacute;moignages. Les tendances g&eacute;n&eacute;ralement constat&eacute;es&nbsp;:</p>

<ul>
  <li><strong>Pr&eacute;fectures les plus rapides</strong> &mdash; environ 8 &agrave; 12&nbsp;mois. Plut&ocirc;t des d&eacute;partements de taille moyenne, peu peupl&eacute;s.</li>
  <li><strong>D&eacute;lai m&eacute;dian</strong> &mdash; environ 12 &agrave; 15&nbsp;mois. La majorit&eacute; des pr&eacute;fectures de m&eacute;tropole.</li>
  <li><strong>Pr&eacute;fectures les plus charg&eacute;es</strong> &mdash; 15 &agrave; 20&nbsp;mois, parfois davantage. Paris et la petite couronne en particulier.</li>
</ul>

<p>Ce sont des ordres de grandeur, pas des engagements. Votre dossier peut sortir du lot dans un sens comme dans l'autre.</p>

<h2>Peut-on choisir sa pr&eacute;fecture&nbsp;?</h2>

<p>Non. La pr&eacute;fecture comp&eacute;tente est celle de votre <strong>r&eacute;sidence habituelle</strong>, et l'administration v&eacute;rifie que le centre de vos int&eacute;r&ecirc;ts s'y trouve r&eacute;ellement. D&eacute;m&eacute;nager pour acc&eacute;l&eacute;rer une demande est une mauvaise id&eacute;e&nbsp;: cela peut au contraire allonger le traitement, le temps que le dossier soit transf&eacute;r&eacute;.</p>

<p>Pr&eacute;cision utile&nbsp;: le service comp&eacute;tent n'est pas toujours la pr&eacute;fecture de votre d&eacute;partement. Les dossiers sont instruits par des <strong>plateformes de naturalisation</strong>, dont beaucoup regroupent plusieurs d&eacute;partements&nbsp;: celle de Toulouse en traite huit. Notre <a href="/prefectures/">annuaire des plateformes par d&eacute;partement</a> donne la v&ocirc;tre, avec ses coordonn&eacute;es v&eacute;rifi&eacute;es.</p>

<p>En revanche, si vous d&eacute;m&eacute;nagez pour de vraies raisons pendant l'instruction, <strong>signalez-le imm&eacute;diatement</strong>. Un changement d'adresse non d&eacute;clar&eacute; est la premi&egrave;re cause de convocation jamais re&ccedil;ue.</p>

<h2>Comment situer votre propre d&eacute;lai</h2>

<ol>
  <li><strong>Notez la date de votre r&eacute;c&eacute;piss&eacute; de compl&eacute;tude.</strong> C'est le seul point de d&eacute;part qui compte juridiquement &mdash; pas la date de cr&eacute;ation du compte, pas celle du d&eacute;p&ocirc;t initial.</li>
  <li><strong>Ajoutez 18&nbsp;mois</strong> (ou 12 si vous r&eacute;sidez en France depuis plus de dix ans). Vous obtenez la date &agrave; partir de laquelle le silence de l'administration devient contestable.</li>
  <li><strong>Ne comparez pas avec les forums.</strong> Les d&eacute;lais qu'on y lit m&eacute;langent des points de d&eacute;part diff&eacute;rents et sur-repr&eacute;sentent les cas extr&ecirc;mes, dans les deux sens.</li>
  <li><strong>Avant cette date&nbsp;: patientez.</strong> Apr&egrave;s&nbsp;: <a href="/blog/relance-naturalisation-que-faire-sans-reponse.html">relancez par &eacute;crit</a>, puis envisagez un recours.</li>
</ol>

<h2>Un exemple chiffr&eacute;</h2>

<p>Prenons un dossier d&eacute;pos&eacute; en ligne le 10&nbsp;mars, avec un r&eacute;c&eacute;piss&eacute; de compl&eacute;tude d&eacute;livr&eacute; le 2&nbsp;juin apr&egrave;s deux demandes de pi&egrave;ces compl&eacute;mentaires, pour une personne install&eacute;e en France depuis sept ans&nbsp;:</p>

<ul>
  <li>Le compteur l&eacute;gal d&eacute;marre le <strong>2&nbsp;juin</strong>, pas le 10&nbsp;mars. Les presque trois mois pass&eacute;s &agrave; compl&eacute;ter le dossier ne comptent pas.</li>
  <li>La personne r&eacute;side en France depuis moins de dix ans&nbsp;: le d&eacute;lai est de <strong>18&nbsp;mois</strong>, soit une &eacute;ch&eacute;ance au <strong>2&nbsp;d&eacute;cembre de l'ann&eacute;e suivante</strong>.</li>
  <li>Avant cette date, le silence de l'administration est parfaitement r&eacute;gulier, quelle que soit la dur&eacute;e d&eacute;j&agrave; &eacute;coul&eacute;e.</li>
</ul>

<p>Ce calcul explique la plupart des &eacute;carts ressentis entre voisins&nbsp;: deux personnes qui &laquo;&nbsp;ont d&eacute;pos&eacute; en m&ecirc;me temps&nbsp;&raquo; peuvent avoir des r&eacute;c&eacute;piss&eacute;s espac&eacute;s de six mois.</p>

<h2>Ce qui remet le compteur en arri&egrave;re</h2>

<p>Trois m&eacute;canismes rallongent le d&eacute;lai r&eacute;el sans que personne ne vous pr&eacute;vienne&nbsp;:</p>

<ol>
  <li><strong>Le dossier incomplet.</strong> Tant que la compl&eacute;tude n'est pas constat&eacute;e, le d&eacute;lai l&eacute;gal ne court pas. C'est la raison la plus fr&eacute;quente d'une attente qui para&icirc;t interminable&nbsp;: elle n'a pas encore commenc&eacute;.</li>
  <li><strong>Les demandes de pi&egrave;ces compl&eacute;mentaires.</strong> Chacune ajoute le temps de l'envoi, le v&ocirc;tre pour obtenir la pi&egrave;ce &mdash; parfois des mois s'il s'agit d'un <a href="/blog/casier-judiciaire-naturalisation.html">document &eacute;tranger &agrave; faire apostiller et traduire</a> &mdash; puis celui du r&eacute;examen.</li>
  <li><strong>Les pi&egrave;ces qui expirent.</strong> Une attestation de langue valable deux ans, un acte d'&eacute;tat civil de moins de trois mois&nbsp;: si l'instruction s'&eacute;ternise, ces documents peuvent devoir &ecirc;tre refaits, et le co&ucirc;t comme le d&eacute;lai repartent.</li>
</ol>

<h2>Ce qui ne sert &agrave; rien</h2>

<p>Autant le dire franchement, parce que ces r&eacute;flexes co&ucirc;tent du temps et de l'&eacute;nergie sans rien produire&nbsp;:</p>

<ul>
  <li><strong>Relancer toutes les deux semaines.</strong> Les relances rapproch&eacute;es ne remontent pas la file&nbsp;: elles ajoutent du courrier &agrave; traiter au service qui instruit votre dossier. Un courrier tous les deux &agrave; trois mois, argument&eacute; et r&eacute;f&eacute;renc&eacute;, p&egrave;se infiniment plus.</li>
  <li><strong>D&eacute;poser un second dossier.</strong> Cela ne cr&eacute;e pas une seconde chance, mais un doublon qui brouille l'instruction du premier.</li>
  <li><strong>Comparer avec les forums.</strong> Les t&eacute;moignages m&eacute;langent des points de d&eacute;part diff&eacute;rents &mdash; cr&eacute;ation de compte, d&eacute;p&ocirc;t, r&eacute;c&eacute;piss&eacute; &mdash; et sur-repr&eacute;sentent les cas extr&ecirc;mes dans les deux sens. On y lit rarement &laquo;&nbsp;tout s'est pass&eacute; normalement&nbsp;&raquo;.</li>
</ul>

<h2>Quand le d&eacute;lai l&eacute;gal est d&eacute;pass&eacute;</h2>

<p>L&agrave;, votre position change compl&egrave;tement. L'absence de r&eacute;ponse au-del&agrave; du d&eacute;lai n'est plus une simple lenteur&nbsp;: elle devient contestable.</p>

<ol>
  <li><strong>Une relance &eacute;crite</strong> au service naturalisations, en lettre recommand&eacute;e avec accus&eacute; de r&eacute;ception, rappelant la date de votre r&eacute;c&eacute;piss&eacute; de compl&eacute;tude et le d&eacute;lai applicable.</li>
  <li><strong>Sans r&eacute;ponse</strong>, la voie contentieuse s'ouvre. Le tribunal administratif de Nantes est comp&eacute;tent pour les affaires de nationalit&eacute;, quel que soit votre lieu de r&eacute;sidence.</li>
</ol>

<p>Notre guide sur <a href="/blog/relance-naturalisation-que-faire-sans-reponse.html">la relance sans r&eacute;ponse</a> d&eacute;taille le contenu et le destinataire de chaque courrier selon l'&eacute;tape.</p>
""",
    "faq": [
        ("Quel est le délai légal de traitement d'une demande de naturalisation ?",
         "L'administration dispose de 18 mois pour répondre à compter de la délivrance du récépissé de complétude, délai ramené à 12 mois si vous résidez en France depuis plus de dix ans. C'est ce récépissé, et non la date de dépôt initial, qui fait courir le compteur."),
        ("Existe-t-il un tableau officiel des délais par préfecture ?",
         "Non. Aucune administration ne publie de délais par département. Les tableaux que l'on trouve en ligne sont reconstitués à partir de témoignages : ils donnent une tendance, pas un engagement."),
        ("Pourquoi ma préfecture est-elle plus lente qu'une autre ?",
         "Principalement à cause du rapport entre le volume de dossiers et les effectifs, et du délai de convocation à l'entretien d'assimilation. S'y ajoutent la complétude de votre dossier — chaque pièce manquante coûte plusieurs semaines — et la complexité de votre parcours."),
        ("Peut-on déposer sa demande dans une autre préfecture pour aller plus vite ?",
         "Non. La préfecture compétente est celle de votre résidence habituelle, et l'administration vérifie que le centre de vos intérêts s'y trouve. Déménager pour accélérer une demande risque au contraire de la ralentir."),
        ("À partir de quand puis-je relancer ?",
         "Une fois le délai légal dépassé, calculé depuis votre récépissé de complétude. Avant cette date, une relance n'a aucun effet sur l'instruction."),
        ("Pourquoi mon voisin a-t-il eu sa réponse avant moi alors qu'on a déposé en même temps ?",
         "Parce que le compteur ne part pas du dépôt mais du récépissé de complétude. Deux personnes qui ont « déposé en même temps » peuvent avoir des récépissés espacés de plusieurs mois si l'une a eu des demandes de pièces complémentaires. S'y ajoute le délai réduit à 12 mois pour qui réside en France depuis plus de dix ans."),
        ("Les relances fréquentes accélèrent-elles le traitement ?",
         "Non. Les relances rapprochées ne remontent pas la file : elles ajoutent du courrier à traiter au service qui instruit votre dossier. Un courrier tous les deux à trois mois, argumenté et référencé, est plus efficace. Déposer un second dossier est également contre-productif : cela crée un doublon qui brouille l'instruction du premier."),
    ],
    "links": [
        ("/prefectures/", "O&ugrave; d&eacute;poser son dossier&nbsp;: la plateforme de chaque d&eacute;partement"),
        ("/blog/delais-naturalisation-2026.html", "Les d&eacute;lais &eacute;tape par &eacute;tape"),
        ("/blog/suivre-dossier-naturalisation-anef.html", "Suivre son dossier sur l'ANEF"),
        ("/blog/relance-naturalisation-que-faire-sans-reponse.html", "Relancer un dossier sans r&eacute;ponse"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret (F2213)"),
        ("https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000699753", "D&eacute;cret n&deg;&nbsp;93-1362"),
    ],
    "cta": "Suivre mes d&eacute;lais dans l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"demarches-apres-naturalisation": {
    "title": "Vous êtes français : les démarches des 6 premiers mois",
    "h1": "Vous &ecirc;tes fran&ccedil;ais&nbsp;: les d&eacute;marches des six premiers mois",
    "desc": "Acte de naissance français, carte d'identité, passeport, listes électorales, double nationalité : l'ordre dans lequel enchaîner, et ce qui bloque si on l'inverse.",
    "og": "Devenir fran&ccedil;ais : et maintenant, quelles d&eacute;marches ?",
    "tag": "Apr&egrave;s l'obtention",
    "og_img": "default.png",
    "lede": "Votre d&eacute;cret est publi&eacute;. Commence alors une s&eacute;rie de d&eacute;marches dont personne ne vous a expliqu&eacute; l'ordre &mdash; et cet ordre compte, parce que chacune d&eacute;pend de la pr&eacute;c&eacute;dente.",
    "body": """
<h2>D'abord&nbsp;: vous &ecirc;tes d&eacute;j&agrave; fran&ccedil;ais</h2>

<p>Vous n'avez pas &agrave; attendre la <a href="/blog/ceremonie-naturalisation-que-se-passe-t-il.html">c&eacute;r&eacute;monie d'accueil</a> pour commencer. Un d&eacute;cret de naturalisation prend effet <strong>&agrave; la date de sa signature</strong> (article 51 du d&eacute;cret n&deg;&nbsp;93-1362). La c&eacute;r&eacute;monie est un moment d'accueil r&eacute;publicain, pas une formalit&eacute; d'acquisition.</p>

<p>En pratique, il vous faut n&eacute;anmoins une <strong>preuve</strong> pour engager les d&eacute;marches&nbsp;: l'extrait nominatif de votre d&eacute;cret, &agrave; t&eacute;l&eacute;charger sur L&eacute;gifrance &agrave; partir de la date de publication communiqu&eacute;e sur votre espace ANEF. Ce PDF porte une signature &eacute;lectronique authentifi&eacute;e et se suffit &agrave; lui-m&ecirc;me, sans copie certifi&eacute;e conforme&nbsp;; notre guide explique <a href="/blog/journal-officiel-naturalisation-liste-des-noms.html">comment le trouver</a>. Avant f&eacute;vrier 2023, l'administration envoyait une ampliation par courrier ou par mail.</p>

<h2>&Eacute;tape 1&nbsp;: l'acte de naissance fran&ccedil;ais</h2>

<p>C'est la pi&egrave;ce ma&icirc;tresse, et la premi&egrave;re &agrave; demander. Si vous &ecirc;tes n&eacute; &agrave; l'&eacute;tranger, c'est le <a href="/glossaire/scec.html">Service central d'&eacute;tat civil</a> (SCEC), &agrave; Nantes, qui &eacute;tablit votre acte de naissance fran&ccedil;ais &agrave; partir de votre d&eacute;cret.</p>

<p>Tout le reste en d&eacute;coule&nbsp;: carte d'identit&eacute;, passeport, inscription &eacute;lectorale. Commencer par autre chose, c'est se heurter &agrave; un guichet qui vous renverra vers le SCEC.</p>

<ul>
  <li>La d&eacute;livrance d'un acte d'&eacute;tat civil est <strong>gratuite</strong>.</li>
  <li>Commandez <strong>plusieurs copies int&eacute;grales</strong> d'un coup&nbsp;: vous en aurez besoin &agrave; plusieurs reprises.</li>
  <li><strong>V&eacute;rifiez l'orthographe</strong> de vos nom et pr&eacute;noms d&egrave;s r&eacute;ception. Une erreur non signal&eacute;e se propage ensuite &agrave; tous vos titres.</li>
</ul>

<h2>&Eacute;tape 2&nbsp;: la carte nationale d'identit&eacute;</h2>

<p>Une fois l'acte de naissance en main, faites votre demande de <strong>CNI</strong> en mairie &eacute;quip&eacute;e d'un dispositif de recueil, apr&egrave;s pr&eacute;-demande en ligne. La premi&egrave;re d&eacute;livrance est gratuite.</p>

<p>C'est le document qui change le quotidien&nbsp;: il remplace le titre de s&eacute;jour dans toutes les situations o&ugrave; l'on vous demandait de justifier votre droit au s&eacute;jour.</p>

<h2>&Eacute;tape 3&nbsp;: le passeport</h2>

<p>M&ecirc;me circuit que la CNI, mais payant. Le passeport fran&ccedil;ais ouvre la libert&eacute; de circulation dans l'Union europ&eacute;enne et la protection consulaire fran&ccedil;aise &agrave; l'&eacute;tranger.</p>

<p>Vous pouvez d&eacute;poser les deux demandes en m&ecirc;me temps si votre mairie le permet&nbsp;: cela &eacute;vite un second rendez-vous et une seconde prise d'empreintes.</p>

<h2>&Eacute;tape 4&nbsp;: l'inscription sur les listes &eacute;lectorales</h2>

<p>Elle n'est pas automatique du seul fait de la naturalisation. Inscrivez-vous en ligne ou en mairie&nbsp;; l'inscription est souvent propos&eacute;e au moment de la demande de CNI.</p>

<p>Attention au calendrier&nbsp;: pour voter &agrave; un scrutin donn&eacute;, il faut &ecirc;tre inscrit avant une date limite, g&eacute;n&eacute;ralement le sixi&egrave;me vendredi pr&eacute;c&eacute;dant le scrutin. Ne remettez pas cette d&eacute;marche &agrave; plus tard&nbsp;: c'est le droit que la plupart des naturalis&eacute;s citent en premier, et celui qu'on oublie le plus souvent d'activer.</p>

<h2>&Eacute;tape 5&nbsp;: et votre nationalit&eacute; d'origine&nbsp;?</h2>

<p>La France <strong>admet la double nationalit&eacute;</strong> et ne vous demande pas de renoncer &agrave; votre nationalit&eacute; d'origine.</p>

<p>Mais c'est votre pays d'origine qui d&eacute;cide de son c&ocirc;t&eacute;. Certains &Eacute;tats ne reconnaissent pas la double nationalit&eacute; et pr&eacute;voient une perte automatique, d'autres exigent une d&eacute;claration. <strong>Renseignez-vous aupr&egrave;s de votre consulat</strong> avant la naturalisation plut&ocirc;t qu'apr&egrave;s&nbsp;: la r&egrave;gle ne d&eacute;pend pas de la France et personne en pr&eacute;fecture ne vous la donnera.</p>

<h2>&Eacute;tape 6&nbsp;: les mises &agrave; jour &agrave; ne pas oublier</h2>

<ul>
  <li><strong>Employeur et service RH</strong> &mdash; votre dossier contient probablement encore une copie de votre titre de s&eacute;jour.</li>
  <li><strong>Caisse d'assurance maladie, banque, organismes sociaux</strong> &mdash; pour &eacute;viter des demandes de justificatifs de s&eacute;jour devenues sans objet.</li>
  <li><strong>Titre de s&eacute;jour</strong> &mdash; il n'a plus lieu d'&ecirc;tre renouvel&eacute;. Ne payez pas une taxe de renouvellement inutile.</li>
</ul>

<h2>Un mot sur la francisation du nom</h2>

<p>Il est possible de demander la <strong>francisation</strong> de son nom ou de ses pr&eacute;noms, mais cette demande se formule <strong>pendant la proc&eacute;dure de naturalisation</strong>, pas apr&egrave;s. Une fois le d&eacute;cret publi&eacute;, il faut passer par une proc&eacute;dure de changement de nom, plus lourde. Si l'orthographe de votre nom vous pose probl&egrave;me au quotidien, c'est avant le d&eacute;p&ocirc;t qu'il faut y penser.</p>

<h2>Vos enfants mineurs&nbsp;: l'effet collectif</h2>

<p>L'<strong>article 22-1 du Code civil</strong> pr&eacute;voit que l'enfant mineur dont l'un des deux parents acquiert la nationalit&eacute; fran&ccedil;aise devient fran&ccedil;ais <em>de plein droit</em>, &agrave; deux conditions cumulatives&nbsp;:</p>

<ol>
  <li>il a la <strong>m&ecirc;me r&eacute;sidence habituelle</strong> que ce parent &mdash; ou r&eacute;side alternativement avec lui en cas de s&eacute;paration ou de divorce&nbsp;;</li>
  <li>son <strong>nom est mentionn&eacute; dans le d&eacute;cret</strong>.</li>
</ol>

<p>Cette seconde condition est celle qui pi&egrave;ge. Un enfant qui remplit parfaitement la condition de r&eacute;sidence mais qui n'a pas &eacute;t&eacute; d&eacute;clar&eacute; au moment du d&eacute;p&ocirc;t ne b&eacute;n&eacute;ficie pas de l'effet collectif. Le rattraper ensuite suppose une d&eacute;marche distincte, bien plus longue.</p>

<p>Une fois le d&eacute;cret paru, <strong>v&eacute;rifiez que chacun de vos enfants y figure</strong>. C'est la mention <a href="/glossaire/nat-eff-rei.html">EFF</a> qui mat&eacute;rialise l'effet collectif. Demandez ensuite leur acte de naissance fran&ccedil;ais au SCEC, comme pour vous.</p>

<h2>Moins de 25&nbsp;ans&nbsp;: une obligation que personne ne vous rappellera</h2>

<p>Si vous acquerez la nationalit&eacute; fran&ccedil;aise avant vos 25&nbsp;ans, vous entrez dans les obligations du service national comme tout Fran&ccedil;ais&nbsp;:</p>

<ul>
  <li><strong>Le recensement citoyen</strong>, &agrave; faire en mairie dans les mois qui suivent l'acquisition.</li>
  <li><strong>La Journ&eacute;e d&eacute;fense et citoyennet&eacute; (JDC)</strong>, &agrave; effectuer <strong>avant vos 25&nbsp;ans</strong>. Vous y &ecirc;tes convoqu&eacute; apr&egrave;s le recensement.</li>
</ul>

<p>Ce n'est pas une formalit&eacute; symbolique&nbsp;: l'<strong>attestation de participation</strong> est exig&eacute;e pour s'inscrire au permis de conduire, au baccalaur&eacute;at et aux concours de la fonction publique avant 25&nbsp;ans. Beaucoup de jeunes naturalis&eacute;s la d&eacute;couvrent le jour o&ugrave; on la leur demande, et se retrouvent bloqu&eacute;s. Apr&egrave;s 25&nbsp;ans, l'attestation n'est plus r&eacute;clam&eacute;e pour ces d&eacute;marches.</p>

<h2>Ce que devient votre titre de s&eacute;jour</h2>

<p>Il n'a plus d'objet. Vous n'avez ni &agrave; le renouveler, ni &agrave; payer la taxe correspondante&nbsp;: c'est une d&eacute;pense inutile que certains continuent d'engager par prudence.</p>

<p>Conservez-le n&eacute;anmoins quelque temps&nbsp;: il porte votre <a href="/glossaire/agdref.html">num&eacute;ro AGDREF</a>, qui peut encore servir &agrave; identifier vos anciens dossiers aupr&egrave;s de l'administration. Pour justifier de votre identit&eacute; et de votre droit au s&eacute;jour, en revanche, c'est d&eacute;sormais votre carte nationale d'identit&eacute; qui fait foi.</p>

<h2>Et votre conjoint &eacute;tranger&nbsp;?</h2>

<p>Votre naturalisation ne lui transmet rien automatiquement&nbsp;: l'effet collectif ne concerne que les enfants mineurs. En revanche, elle lui ouvre une voie&nbsp;: la <a href="/blog/naturalisation-par-mariage-2026.html">d&eacute;claration de nationalit&eacute; &agrave; raison du mariage</a>, sous conditions de dur&eacute;e de mariage et de communaut&eacute; de vie. Le niveau B2 s'applique l&agrave; aussi, mais pas l'examen civique, r&eacute;serv&eacute; aux proc&eacute;dures par d&eacute;cret.</p>
""",
    "faq": [
        ("Quelles démarches faire juste après la naturalisation ?",
         "Dans cet ordre : demander votre acte de naissance français au Service central d'état civil de Nantes si vous êtes né à l'étranger, puis la carte nationale d'identité, puis le passeport, puis l'inscription sur les listes électorales. Chaque étape dépend de la précédente : l'acte de naissance conditionne tout le reste."),
        ("Faut-il attendre la cérémonie pour commencer les démarches ?",
         "Non. Le décret prend effet à la date de sa signature : vous êtes français avant la cérémonie. Il vous faut néanmoins une preuve : l'extrait nominatif de votre décret, à télécharger sur Légifrance (il porte une signature électronique authentifiée), à partir de la date de publication indiquée sur votre espace ANEF."),
        ("La première carte d'identité française est-elle gratuite ?",
         "Oui, la première délivrance d'une carte nationale d'identité est gratuite. Le passeport, lui, est payant."),
        ("Perd-on sa nationalité d'origine en devenant français ?",
         "La France admet la double nationalité et ne vous demande pas d'y renoncer. En revanche, votre pays d'origine peut prévoir une perte automatique ou exiger une déclaration : renseignez-vous auprès de votre consulat, idéalement avant la naturalisation."),
        ("Peut-on franciser son nom après la naturalisation ?",
         "La demande de francisation du nom ou des prénoms se formule pendant la procédure de naturalisation. Après la publication du décret, il faut passer par une procédure de changement de nom, nettement plus lourde."),
        ("Mes enfants mineurs deviennent-ils français en même temps que moi ?",
         "Sous deux conditions cumulatives posées par l'article 22-1 du Code civil : l'enfant doit avoir la même résidence habituelle que vous — ou résider alternativement avec vous en cas de séparation — et son nom doit être mentionné dans le décret. C'est cette seconde condition qui piège : un enfant non déclaré au dépôt ne bénéficie pas de l'effet collectif, et le rattraper ensuite suppose une démarche distincte."),
        ("J'ai moins de 25 ans : ai-je des obligations de service national ?",
         "Oui. Vous devez faire le recensement citoyen en mairie dans les mois qui suivent l'acquisition, puis la Journée défense et citoyenneté avant vos 25 ans. L'attestation de participation est exigée pour s'inscrire au permis de conduire, au baccalauréat et aux concours de la fonction publique avant 25 ans."),
        ("Mon conjoint étranger devient-il français aussi ?",
         "Non, l'effet collectif ne concerne que les enfants mineurs. Votre conjoint peut en revanche engager une déclaration de nationalité à raison du mariage, sous conditions de durée de mariage et de communauté de vie — avec, là aussi, le niveau B2, mais sans examen civique, réservé aux procédures par décret."),
        ("Faut-il renouveler son titre de séjour après la naturalisation ?",
         "Non, il n'a plus d'objet et la taxe de renouvellement serait une dépense inutile. Conservez-le tout de même quelque temps : il porte votre numéro AGDREF, utile pour identifier vos anciens dossiers."),
    ],
    "links": [
        ("/blog/ceremonie-naturalisation-que-se-passe-t-il.html", "La c&eacute;r&eacute;monie d'accueil&nbsp;: convocation et d&eacute;roulement"),
        ("/outils/decret-naturalisation.html", "V&eacute;rifier la publication de mon d&eacute;cret"),
        ("/blog/pourquoi-devenir-francais-avantages.html", "Les avantages concrets de la nationalit&eacute;"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F1051", "Service-public.gouv.fr &mdash; Carte nationale d'identit&eacute;"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F334", "Service-public.gouv.fr &mdash; Double nationalit&eacute; (F334)"),
        ("https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000047096231", "D&eacute;cret n&deg;&nbsp;93-1362, article 51 &mdash; prise d'effet des d&eacute;crets"),
        ("https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006419939", "Code civil, article 22-1 &mdash; effet collectif pour les enfants mineurs"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F871", "Service-public.gouv.fr &mdash; Journ&eacute;e d&eacute;fense et citoyennet&eacute; (F871)"),
    ],
    "cta": "Pr&eacute;parer la suite avec l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"ressources-revenus-naturalisation": {
    "title": "Ressources et naturalisation : ce que la préfecture regarde",
    "h1": "Ressources et naturalisation&nbsp;: ce que la pr&eacute;fecture regarde vraiment",
    "desc": "Il n'existe aucun salaire minimum légal pour être naturalisé. Ce qui compte est la stabilité : CDD, intérim, auto-entrepreneur, chômage, ce que chaque situation implique.",
    "og": "Ressources et naturalisation : la stabilit&eacute; avant le montant",
    "tag": "Conditions",
    "og_img": "default.png",
    "lede": "&laquo;&nbsp;Combien faut-il gagner pour &ecirc;tre naturalis&eacute;&nbsp;?&nbsp;&raquo; La question revient sans cesse, et la r&eacute;ponse d&eacute;&ccedil;oit d'abord&nbsp;: <strong>il n'existe aucun montant l&eacute;gal</strong>. Ce qui se joue est plus subtil, et surtout plus pr&eacute;parable qu'on ne le croit.",
    "body": """
<h2>Aucun seuil, mais une appr&eacute;ciation</h2>

<p>Aucun texte ne fixe de salaire minimum pour obtenir la nationalit&eacute; fran&ccedil;aise. L'administration appr&eacute;cie votre <strong>insertion professionnelle</strong> et le <strong>caract&egrave;re stable et suffisant</strong> de vos ressources, au regard de votre situation d'ensemble.</p>

<p>Cette appr&eacute;ciation est large et elle explique pourquoi deux personnes aux revenus comparables re&ccedil;oivent des d&eacute;cisions diff&eacute;rentes. Ce qui les s&eacute;pare, ce n'est presque jamais le montant&nbsp;: c'est la <strong>trajectoire</strong> que raconte le dossier.</p>

<h2>Ce qui compte&nbsp;: la stabilit&eacute;, pas le montant</h2>

<p>Un salari&eacute; au SMIC en CDI depuis quatre ans pr&eacute;sente un dossier plus solide qu'un cadre bien pay&eacute; qui encha&icirc;ne des missions de trois mois entrecoup&eacute;es de p&eacute;riodes sans activit&eacute;. Les crit&egrave;res qui p&egrave;sent&nbsp;:</p>

<ul>
  <li><strong>La continuit&eacute;</strong> &mdash; des ressources r&eacute;guli&egrave;res sur plusieurs ann&eacute;es, sans trou inexpliqu&eacute;.</li>
  <li><strong>La progression</strong> &mdash; une situation qui s'am&eacute;liore, m&ecirc;me lentement, se lit mieux qu'une situation qui se d&eacute;grade.</li>
  <li><strong>La coh&eacute;rence fiscale</strong> &mdash; des avis d'imposition qui concordent avec les revenus d&eacute;clar&eacute;s, et des imp&ocirc;ts &agrave; jour.</li>
  <li><strong>L'autonomie</strong> &mdash; subvenir &agrave; ses besoins, appr&eacute;ci&eacute;e en tenant compte de la composition du foyer.</li>
</ul>

<h2>Votre situation, cas par cas</h2>

<h3>CDI</h3>
<p>La configuration la plus simple. Joignez le contrat, les bulletins de salaire des derniers mois et les avis d'imposition. Une anciennet&eacute; de plusieurs ann&eacute;es joue nettement en votre faveur.</p>

<h3>CDD et int&eacute;rim</h3>
<p>Ce n'est pas un obstacle en soi, mais il faut <strong>montrer la continuit&eacute;</strong>. Un encha&icirc;nement r&eacute;gulier de contrats chez le m&ecirc;me employeur ou dans le m&ecirc;me secteur se d&eacute;fend tr&egrave;s bien. Joignez l'ensemble des contrats, pas seulement le dernier, et une attestation de votre agence ou employeur si vous en obtenez une.</p>

<h3>Auto-entrepreneur et ind&eacute;pendant</h3>
<p>La difficult&eacute; est que vos revenus ne se lisent pas sur des bulletins de salaire. Compensez par le volume de preuves&nbsp;: avis d'imposition sur plusieurs ann&eacute;es, attestations URSSAF, d&eacute;clarations de chiffre d'affaires, bilans le cas &eacute;ch&eacute;ant. Une activit&eacute; d&eacute;clar&eacute;e depuis longtemps et fiscalement en r&egrave;gle est un bon dossier.</p>

<h3>Ch&ocirc;mage</h3>
<p>&Ecirc;tre au ch&ocirc;mage au moment du d&eacute;p&ocirc;t n'emp&ecirc;che pas de d&eacute;poser, mais c'est un moment d&eacute;favorable si la p&eacute;riode est r&eacute;cente et isol&eacute;e dans un parcours par ailleurs instable. Si votre parcours ant&eacute;rieur est solide et que vous justifiez d'une indemnisation, le dossier reste d&eacute;fendable. Si vous en avez la possibilit&eacute;, <strong>attendre une reprise d'activit&eacute;</strong> est souvent le calcul le plus rationnel&nbsp;: un ajournement co&ucirc;te des ann&eacute;es et un <a href="/blog/cout-naturalisation-francaise-2026.html">timbre fiscal de 255&nbsp;&euro;</a> non remboursable.</p>

<h3>Retraite, &eacute;tudes, parent au foyer</h3>
<p>Ces situations s'appr&eacute;cient diff&eacute;remment&nbsp;: une pension de retraite est une ressource stable par nature&nbsp;; un &eacute;tudiant ou un parent au foyer est examin&eacute; dans le cadre des ressources du foyer. Documentez la situation du foyer dans son ensemble.</p>

<h2>Les prestations sociales sont-elles un probl&egrave;me&nbsp;?</h2>

<p>Percevoir des prestations auxquelles vous avez droit n'est pas une faute et ne disqualifie personne automatiquement. Ce qui est examin&eacute;, c'est la <strong>part</strong> qu'elles repr&eacute;sentent dans vos ressources et leur <strong>caract&egrave;re durable</strong>&nbsp;: un compl&eacute;ment ponctuel ne se lit pas comme une d&eacute;pendance de longue dur&eacute;e sans activit&eacute; par ailleurs.</p>

<h2>Comment pr&eacute;senter votre situation</h2>

<ol>
  <li><strong>Couvrez plusieurs ann&eacute;es</strong>, pas seulement les derniers mois. Trois avis d'imposition racontent une trajectoire&nbsp;; un bulletin de salaire ne raconte rien.</li>
  <li><strong>Expliquez les trous.</strong> Une p&eacute;riode sans revenus qui reste inexpliqu&eacute;e sera interpr&eacute;t&eacute;e&nbsp;; la m&ecirc;me p&eacute;riode document&eacute;e (formation, cong&eacute; parental, maladie) ne pose g&eacute;n&eacute;ralement pas de probl&egrave;me.</li>
  <li><strong>Soyez &agrave; jour fiscalement.</strong> C'est un point v&eacute;rifiable et v&eacute;rifi&eacute;. Un retard d'imposition non r&eacute;gularis&eacute; est un signal n&eacute;gatif imm&eacute;diat.</li>
  <li><strong>Ne surjouez pas.</strong> Des pi&egrave;ces qui embellissent la r&eacute;alit&eacute; se retournent contre vous lors de l'<a href="/blog/entretien-naturalisation-prefectures.html">entretien d'assimilation</a>, o&ugrave; l'on vous demandera de raconter votre parcours.</li>
</ol>

<p>Les ressources jug&eacute;es insuffisantes ou pr&eacute;caires figurent parmi les motifs d'<a href="/blog/ajournement-vs-refus-naturalisation.html">ajournement</a> les plus fr&eacute;quents. La bonne nouvelle, c'est que l'ajournement n'est pas un refus&nbsp;: c'est un report, et le temps impos&eacute; peut &ecirc;tre exactement celui qu'il faut pour consolider une situation.</p>

<h2>Les pi&egrave;ces &agrave; fournir, selon votre situation</h2>

<p>L'erreur la plus courante consiste &agrave; joindre trois bulletins de salaire et &agrave; s'arr&ecirc;ter l&agrave;. Ce que l'administration lit en priorit&eacute;, ce sont les <strong>avis d'imposition</strong>&nbsp;: ils couvrent une ann&eacute;e enti&egrave;re, ils sont infalsifiables et ils racontent une trajectoire.</p>

<ul>
  <li><strong>Salari&eacute;</strong> &mdash; contrat de travail, trois derniers bulletins de salaire, et surtout les <strong>trois derniers avis d'imposition</strong>.</li>
  <li><strong>CDD ou int&eacute;rim</strong> &mdash; l'<em>ensemble</em> des contrats de la p&eacute;riode, pas seulement le dernier, plus les avis d'imposition. Une attestation de l'employeur ou de l'agence sur la r&eacute;gularit&eacute; des missions aide beaucoup.</li>
  <li><strong>Ind&eacute;pendant ou auto-entrepreneur</strong> &mdash; avis d'imposition, attestation de vigilance URSSAF, d&eacute;clarations de chiffre d'affaires, bilans le cas &eacute;ch&eacute;ant, et un extrait d'immatriculation qui montre l'anciennet&eacute; de l'activit&eacute;.</li>
  <li><strong>Retrait&eacute;</strong> &mdash; notification de pension et avis d'imposition. Une pension est une ressource stable par nature&nbsp;: c'est un bon dossier.</li>
  <li><strong>Sans activit&eacute;</strong> &mdash; justificatifs d'indemnisation, et les pi&egrave;ces qui documentent la p&eacute;riode ant&eacute;rieure. C'est ici que la profondeur historique compte le plus.</li>
</ul>

<h2>Les ressources du foyer</h2>

<p>Vous n'&ecirc;tes pas &eacute;valu&eacute; hors sol. L'administration appr&eacute;cie votre autonomie en tenant compte de la composition de votre foyer&nbsp;: un conjoint qui travaille, des charges partag&eacute;es, des enfants &agrave; charge.</p>

<p>Concr&egrave;tement, un revenu modeste dans un foyer &agrave; deux salaires ne se lit pas comme le m&ecirc;me revenu supportant seul quatre personnes. Documentez donc la situation du foyer&nbsp;: avis d'imposition commun, justificatif de la situation du conjoint, composition familiale. Un parent au foyer ou un &eacute;tudiant s'appr&eacute;cie dans ce cadre, pas isol&eacute;ment.</p>

<h2>Revenus per&ccedil;us &agrave; l'&eacute;tranger</h2>

<p>Ils ne sont pas disqualifiants, mais ils appellent une vigilance particuli&egrave;re. Deux points comptent&nbsp;:</p>

<ul>
  <li><strong>Sont-ils d&eacute;clar&eacute;s en France&nbsp;?</strong> C'est la premi&egrave;re chose v&eacute;rifi&eacute;e. Des revenus &eacute;trangers absents de vos avis d'imposition fran&ccedil;ais posent un probl&egrave;me de coh&eacute;rence bien avant de poser un probl&egrave;me de montant.</li>
  <li><strong>Que disent-ils de votre centre d'int&eacute;r&ecirc;ts&nbsp;?</strong> La naturalisation suppose que le centre de vos int&eacute;r&ecirc;ts mat&eacute;riels et familiaux se trouve en France. Une activit&eacute; principale &agrave; l'&eacute;tranger peut &ecirc;tre lue comme un indice contraire &mdash; c'est un enjeu de r&eacute;sidence autant que de ressources.</li>
</ul>

<h2>Quand d&eacute;poser, selon votre situation</h2>

<p>Le choix du moment est la variable la plus sous-estim&eacute;e, alors qu'elle ne co&ucirc;te rien &agrave; ajuster&nbsp;:</p>

<ul>
  <li><strong>Vous venez de signer un CDI</strong> &mdash; laissez passer la p&eacute;riode d'essai. Un contrat confirm&eacute; vaut mieux qu'un contrat r&eacute;cent.</li>
  <li><strong>Vous encha&icirc;nez les CDD</strong> &mdash; attendez d'avoir une s&eacute;quence lisible sur deux &agrave; trois ans plut&ocirc;t que de d&eacute;poser au milieu d'une p&eacute;riode trou&eacute;e.</li>
  <li><strong>Vous venez de lancer une activit&eacute; ind&eacute;pendante</strong> &mdash; attendez d'avoir au moins deux exercices d&eacute;clar&eacute;s. Un premier exercice partiel ne d&eacute;montre rien.</li>
  <li><strong>Vous &ecirc;tes sans emploi</strong> &mdash; si une reprise est envisageable &agrave; court terme, elle change la lecture du dossier. Rappelez-vous que le <a href="/blog/cout-naturalisation-francaise-2026.html">timbre fiscal de 255&nbsp;&euro;</a> n'est pas remboursable, et qu'un ajournement impose souvent deux ans d'attente&nbsp;: d&eacute;poser six mois plus tard co&ucirc;te moins cher que d&eacute;poser trop t&ocirc;t.</li>
</ul>

<p>Ce raisonnement vaut aussi pour les autres conditions&nbsp;: v&eacute;rifiez l'ensemble des <a href="/blog/conditions-naturalisation-francaise.html">crit&egrave;res d'&eacute;ligibilit&eacute;</a> avant d'engager les frais.</p>
""",
    "faq": [
        ("Quel salaire minimum faut-il pour être naturalisé français ?",
         "Aucun texte ne fixe de montant. L'administration apprécie l'insertion professionnelle et le caractère stable et suffisant des ressources au regard de la situation d'ensemble. Un salarié au SMIC en CDI depuis plusieurs années présente souvent un dossier plus solide qu'un revenu élevé mais discontinu."),
        ("Peut-on demander la naturalisation en CDD ou en intérim ?",
         "Oui. Ce n'est pas un obstacle en soi, mais il faut démontrer la continuité : joignez l'ensemble des contrats et non seulement le dernier, et les avis d'imposition sur plusieurs années. Un enchaînement régulier chez le même employeur ou dans le même secteur se défend très bien."),
        ("Être au chômage empêche-t-il d'obtenir la nationalité française ?",
         "Non, mais c'est un moment défavorable pour déposer si la période est récente dans un parcours par ailleurs instable. Si votre trajectoire antérieure est solide, le dossier reste défendable. Quand c'est possible, attendre une reprise d'activité est souvent plus rationnel qu'un ajournement, qui coûte des années et un timbre fiscal non remboursable."),
        ("Toucher le RSA ou des allocations empêche-t-il la naturalisation ?",
         "Percevoir des prestations auxquelles on a droit n'est pas une faute et ne disqualifie pas automatiquement. Ce qui est examiné, c'est la part qu'elles représentent dans vos ressources et leur caractère durable."),
        ("Comment justifier ses revenus quand on est auto-entrepreneur ?",
         "Par le volume de preuves, faute de bulletins de salaire : avis d'imposition sur plusieurs années, attestations URSSAF, déclarations de chiffre d'affaires et bilans le cas échéant. Une activité déclarée de longue date et fiscalement en règle constitue un bon dossier."),
        ("Les revenus de mon conjoint sont-ils pris en compte ?",
         "Oui. L'administration apprécie votre autonomie en tenant compte de la composition du foyer : un revenu modeste dans un foyer à deux salaires ne se lit pas comme le même revenu supportant seul quatre personnes. Documentez la situation du foyer, pas seulement la vôtre."),
        ("Faut-il fournir des bulletins de salaire ou des avis d'imposition ?",
         "Les deux, mais ce sont les avis d'imposition qui pèsent le plus : ils couvrent une année entière et racontent une trajectoire, là où trois bulletins de salaire ne montrent qu'un instantané. Prévoyez les trois derniers."),
        ("Quand vaut-il mieux déposer sa demande ?",
         "Après la période d'essai si vous venez de signer un CDI, après une séquence lisible de deux à trois ans si vous enchaînez les CDD, après au moins deux exercices déclarés si vous êtes indépendant. Le timbre fiscal de 255 € n'est pas remboursable et un ajournement impose souvent deux ans d'attente : déposer six mois plus tard coûte moins cher que déposer trop tôt."),
    ],
    "links": [
        ("/blog/conditions-naturalisation-francaise.html", "Les 7 conditions de la naturalisation"),
        ("/blog/documents-naturalisation.html", "La liste des pi&egrave;ces &agrave; fournir"),
        ("/blog/ajournement-vs-refus-naturalisation.html", "Ajournement ou refus&nbsp;: que faire"),
        ("/blog/naturalisation-apres-etudes-en-france.html", "Jeunes dipl&ocirc;m&eacute;s&nbsp;: ce que la pr&eacute;fecture attend c&ocirc;t&eacute; emploi"),
        ("/blog/naturalisation-refugie-2026.html", "R&eacute;fugi&eacute;s&nbsp;: ressources et prestations sociales"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret (F2213)"),
        ("https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070721/LEGISCTA000006149926/", "Code civil &mdash; Acquisition de la nationalit&eacute; fran&ccedil;aise"),
    ],
    "cta": "Pr&eacute;parer mon dossier avec l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"reintegration-nationalite-francaise-2026": {
    "title": "Réintégration nationalité française : décret ou déclaration ?",
    "h1": "R&eacute;int&eacute;gration dans la nationalit&eacute; fran&ccedil;aise&nbsp;: par d&eacute;cret ou par d&eacute;claration&nbsp;?",
    "desc": "Né en Algérie avant 1962 ou ancien Français ? Par décret, la réintégration exige B2 et examen civique, sans durée de résidence ; par déclaration, ni test ni examen.",
    "og": "R&eacute;int&eacute;gration dans la nationalit&eacute; fran&ccedil;aise&nbsp;: les deux voies",
    "tag": "Conditions",
    "og_img": "default.png",
    "date": "2026-09-17",
    "date_fr": "17 septembre 2026",
    "lede": "Redevenir fran&ccedil;ais n'est pas une naturalisation comme les autres. La loi pr&eacute;voit deux voies, aux exigences tr&egrave;s diff&eacute;rentes&nbsp;: la r&eacute;int&eacute;gration par d&eacute;cret, qui suit les r&egrave;gles de la naturalisation sans la condition de stage, et la r&eacute;int&eacute;gration par d&eacute;claration, r&eacute;serv&eacute;e &agrave; trois cas pr&eacute;cis. Voici comment savoir laquelle vous concerne, ce qu'on vous demandera en 2026, et le pi&egrave;ge du dossier&nbsp;: prouver une nationalit&eacute; perdue il y a parfois soixante ans.",
    "body": """
<h2>R&eacute;int&eacute;gration ou naturalisation&nbsp;: la diff&eacute;rence tient en une phrase</h2>

<p>La naturalisation s'adresse &agrave; un &eacute;tranger qui n'a jamais &eacute;t&eacute; fran&ccedil;ais. La r&eacute;int&eacute;gration s'adresse &agrave; une personne qui <strong>a poss&eacute;d&eacute; la nationalit&eacute; fran&ccedil;aise et l'a perdue</strong>&nbsp;: c'est l'article 24 du Code civil, qui vise &laquo;&nbsp;les personnes qui &eacute;tablissent avoir poss&eacute;d&eacute; la qualit&eacute; de Fran&ccedil;ais&nbsp;&raquo;. Tout le dossier tourne autour de ce verbe, <em>&eacute;tablir</em>.</p>

<p>Elle ne se confond pas non plus avec une nationalit&eacute; &laquo;&nbsp;par filiation&nbsp;&raquo;. Un enfant n&eacute; apr&egrave;s que ses parents ont perdu la nationalit&eacute; fran&ccedil;aise n'a lui-m&ecirc;me jamais &eacute;t&eacute; fran&ccedil;ais&nbsp;: il ne peut pas &ecirc;tre r&eacute;int&eacute;gr&eacute; dans une nationalit&eacute; qu'il n'a pas eue. Pour lui, ce sera la naturalisation par d&eacute;cret ou l'une des autres voies d'acc&egrave;s. La &laquo;&nbsp;r&eacute;int&eacute;gration par filiation&nbsp;&raquo;, souvent recherch&eacute;e, n'existe pas.</p>

<div class="callout">
  <p><strong>&Agrave; retenir&nbsp;:</strong> la r&eacute;int&eacute;gration suppose que <em>vous</em>, personnellement, ayez &eacute;t&eacute; fran&ccedil;ais &agrave; un moment de votre vie. Deux voies existent ensuite&nbsp;: par d&eacute;cret (la r&egrave;gle g&eacute;n&eacute;rale) ou par d&eacute;claration (trois cas de perte pr&eacute;cis).</p>
</div>

<h2>Le cas le plus fr&eacute;quent&nbsp;: &ecirc;tre n&eacute; en Alg&eacute;rie avant l'ind&eacute;pendance</h2>

<p>C'est la situation qui g&eacute;n&egrave;re le plus de demandes, et le plus de confusion. Avant le 3 juillet 1962, l'Alg&eacute;rie &eacute;tait constitu&eacute;e de d&eacute;partements fran&ccedil;ais&nbsp;: les personnes qui y sont n&eacute;es &eacute;taient fran&ccedil;aises. Mais l'ordonnance n&deg;&nbsp;62-825 du 21 juillet 1962 a distingu&eacute; deux cat&eacute;gories.</p>

<ul>
  <li>Les personnes de <strong>statut civil de droit commun</strong> ont conserv&eacute; la nationalit&eacute; fran&ccedil;aise.</li>
  <li>Les personnes de <strong>statut civil de droit local</strong>, c'est-&agrave;-dire l'immense majorit&eacute; de la population, l'ont perdue au 1<sup>er</sup> janvier 1963, sauf si elles ont souscrit en France une <strong>d&eacute;claration recognitive</strong> de nationalit&eacute; fran&ccedil;aise avant le 22 mars 1967.</li>
</ul>

<p>Les enfants n&eacute;s en France avant le 1<sup>er</sup> janvier 1963 de parents de statut local ont suivi la condition de leurs parents&nbsp;: sans d&eacute;claration recognitive, ils ont perdu la nationalit&eacute; fran&ccedil;aise avec eux. Ces personnes, n&eacute;es en Alg&eacute;rie ou en France avant 1963, ont donc bien &laquo;&nbsp;poss&eacute;d&eacute; la qualit&eacute; de Fran&ccedil;ais&nbsp;&raquo;&nbsp;: elles sont &eacute;ligibles &agrave; la r&eacute;int&eacute;gration par d&eacute;cret, &agrave; tout &acirc;ge.</p>

<p>La r&eacute;ponse du minist&egrave;re de l'Int&eacute;rieur publi&eacute;e au Journal officiel le 3 juin 2025 le confirme, en ajoutant une limite&nbsp;: la r&eacute;int&eacute;gration &laquo;&nbsp;est soumise, pour le surplus, aux conditions et aux r&egrave;gles de la naturalisation&nbsp;&raquo;, dont la r&eacute;sidence en France. Une personne n&eacute;e en Alg&eacute;rie avant 1962 qui vit &agrave; l'&eacute;tranger ne peut pas &ecirc;tre r&eacute;int&eacute;gr&eacute;e tant qu'elle n'a pas &eacute;tabli sa r&eacute;sidence en France.</p>

<h3>N&eacute; en France apr&egrave;s 1962 de parents n&eacute;s en Alg&eacute;rie&nbsp;? Vous &ecirc;tes probablement d&eacute;j&agrave; fran&ccedil;ais</h3>

<p>C'est le point que beaucoup de familles ignorent. L'article 19-3 du Code civil rend fran&ccedil;ais l'enfant n&eacute; en France dont un parent y est lui-m&ecirc;me n&eacute;, et l'Alg&eacute;rie d'avant le 3 juillet 1962 compte comme la France. L'enfant n&eacute; en France depuis le 1<sup>er</sup> janvier 1963 d'un parent n&eacute; en Alg&eacute;rie avant l'ind&eacute;pendance est donc fran&ccedil;ais de naissance, quel qu'ait &eacute;t&eacute; le statut de ses parents et m&ecirc;me s'ils ont perdu la nationalit&eacute; fran&ccedil;aise. Inutile de demander une r&eacute;int&eacute;gration ou une naturalisation&nbsp;: la bonne d&eacute;marche est un <a href="/glossaire/cnf.html">certificat de nationalit&eacute; fran&ccedil;aise</a>, d&eacute;livr&eacute; par le tribunal judiciaire.</p>

<h3>Et les autres anciens territoires&nbsp;?</h3>

<p>Le raisonnement vaut, avec des textes propres &agrave; chaque cas, pour les personnes de statut local originaires des anciens territoires d'outre-mer devenus ind&eacute;pendants en 1960 (Afrique subsaharienne, Madagascar)&nbsp;: elles ont perdu la nationalit&eacute; fran&ccedil;aise lorsque la loi du nouvel &Eacute;tat la leur a conf&eacute;r&eacute;e, sauf domicile en France ou d&eacute;claration recognitive. En revanche, le Maroc et la Tunisie &eacute;taient des protectorats&nbsp;: leurs ressortissants n'ont jamais &eacute;t&eacute; fran&ccedil;ais, et la r&eacute;int&eacute;gration ne leur est pas ouverte sur ce fondement.</p>

<h2>Voie n&deg;&nbsp;1&nbsp;: la r&eacute;int&eacute;gration par d&eacute;cret</h2>

<p>L'article 24-1 tient en deux phrases&nbsp;: la r&eacute;int&eacute;gration par d&eacute;cret &laquo;&nbsp;peut &ecirc;tre obtenue &agrave; tout &acirc;ge et sans condition de stage. Elle est soumise, pour le surplus, aux conditions et aux r&egrave;gles de la naturalisation.&nbsp;&raquo;</p>

<p>Concr&egrave;tement, vous &ecirc;tes dispens&eacute; de la <strong>dur&eacute;e de r&eacute;sidence de 5&nbsp;ans</strong> exig&eacute;e pour une naturalisation ordinaire. Tout le reste s'applique, y compris les exigences renforc&eacute;es depuis le 1<sup>er</sup> janvier 2026&nbsp;:</p>

<ul>
  <li><strong>R&eacute;sider en France</strong> au moment de la signature du d&eacute;cret, avec le centre de vos int&eacute;r&ecirc;ts mat&eacute;riels et familiaux en France, et un titre de s&eacute;jour en cours de validit&eacute; (sauf ressortissants europ&eacute;ens et suisses).</li>
  <li><strong>Justifier du niveau B2</strong> de fran&ccedil;ais, &agrave; l'oral et &agrave; l'&eacute;crit, par un dipl&ocirc;me fran&ccedil;ais ou un test (TCF ou TEF de moins de 2&nbsp;ans).</li>
  <li><strong>R&eacute;ussir l'examen civique</strong>&nbsp;: 40&nbsp;questions, 32&nbsp;bonnes r&eacute;ponses exig&eacute;es, dans un centre agr&eacute;&eacute;.</li>
  <li><strong>Passer l'entretien</strong> d'assimilation en pr&eacute;fecture et signer la charte des droits et devoirs du citoyen.</li>
  <li>Disposer de <strong>ressources stables et suffisantes</strong>, appr&eacute;ci&eacute;es sur 5&nbsp;ans, et n'avoir aucune condamnation incompatible (peine ferme de 6&nbsp;mois ou plus, atteinte aux int&eacute;r&ecirc;ts de la Nation).</li>
</ul>

<table class="article-table">
  <thead><tr><th>Crit&egrave;re</th><th>R&eacute;int&eacute;gration par d&eacute;cret</th><th>Naturalisation par d&eacute;cret</th></tr></thead>
  <tbody>
    <tr><td>Dur&eacute;e de r&eacute;sidence (stage)</td><td><em>Aucune</em></td><td>5&nbsp;ans (2&nbsp;ans ou dispense dans certains cas)</td></tr>
    <tr><td>R&eacute;sidence en France au moment du d&eacute;cret</td><td>Oui</td><td>Oui</td></tr>
    <tr><td>Niveau de fran&ccedil;ais</td><td>B2</td><td>B2</td></tr>
    <tr><td>Examen civique</td><td>Oui</td><td>Oui</td></tr>
    <tr><td>Entretien en pr&eacute;fecture</td><td>Oui</td><td>Oui</td></tr>
    <tr><td>Preuve d'une nationalit&eacute; fran&ccedil;aise ant&eacute;rieure</td><td><em>Oui, pi&egrave;ce centrale</em></td><td>Non</td></tr>
    <tr><td>Timbre fiscal</td><td>255&nbsp;&euro;</td><td>255&nbsp;&euro;</td></tr>
    <tr><td>D&eacute;lai l&eacute;gal de r&eacute;ponse</td><td>18&nbsp;mois (12&nbsp;mois apr&egrave;s 10&nbsp;ans de r&eacute;sidence)</td><td>18&nbsp;mois (12&nbsp;mois apr&egrave;s 10&nbsp;ans de r&eacute;sidence)</td></tr>
  </tbody>
</table>

<p>La proc&eacute;dure est celle de la naturalisation&nbsp;: demande en ligne sur le t&eacute;l&eacute;service de l'<a href="/glossaire/anef.html">ANEF</a> (le formulaire s'intitule d'ailleurs &laquo;&nbsp;demande de naturalisation ou de r&eacute;int&eacute;gration&nbsp;&raquo;), ou cerfa n&deg;&nbsp;12753 d&eacute;pos&eacute; &agrave; la plateforme de naturalisation de votre domicile si le d&eacute;p&ocirc;t en ligne est impossible. Le d&eacute;cret est ensuite publi&eacute; au Journal officiel&nbsp;: dans notre <a href="/outils/decret-naturalisation.html">annuaire des d&eacute;crets</a>, les r&eacute;int&eacute;grations portent le code <a href="/glossaire/nat-eff-rei.html">REI</a>.</p>

<h2>Voie n&deg;&nbsp;2&nbsp;: la r&eacute;int&eacute;gration par d&eacute;claration</h2>

<p>L'article 24-2 r&eacute;serve cette voie, beaucoup plus l&eacute;g&egrave;re, &agrave; des situations pr&eacute;cises&nbsp;: vous avez perdu la nationalit&eacute; fran&ccedil;aise <strong>&agrave; la suite d'un mariage avec un &eacute;tranger</strong> (sous l'empire des anciennes lois), <strong>par acquisition volontaire d'une nationalit&eacute; &eacute;trang&egrave;re</strong> alors que vous r&eacute;sidiez &agrave; l'&eacute;tranger, ou &agrave; raison de l'exercice de certains mandats publics.</p>

<p>Les conditions ne portent ni sur la langue ni sur les connaissances civiques&nbsp;: il faut avoir <strong>conserv&eacute; ou acquis des liens manifestes avec la France</strong> (culturels, professionnels, &eacute;conomiques ou familiaux), ne pas faire l'objet d'une expulsion ou d'une interdiction du territoire, &ecirc;tre en s&eacute;jour r&eacute;gulier si vous vivez en France, et ne pas avoir de condamnation incompatible.</p>

<p>La d&eacute;claration se souscrit au <strong>tribunal judiciaire</strong> de votre domicile, ou au consulat si vous vivez &agrave; l'&eacute;tranger. L'administration a <strong>6&nbsp;mois</strong> &agrave; compter du r&eacute;c&eacute;piss&eacute; pour l'enregistrer ou refuser&nbsp;; pass&eacute; ce d&eacute;lai, le silence vaut enregistrement. La nationalit&eacute; prend effet &agrave; la date de souscription, et vos enfants mineurs qui vivent avec vous deviennent fran&ccedil;ais s'ils sont mentionn&eacute;s dans la d&eacute;claration.</p>

<div class="callout">
  <p><strong>Pas de test de langue, pas d'examen civique</strong> pour la r&eacute;int&eacute;gration par d&eacute;claration&nbsp;: ces deux &eacute;preuves ne concernent que les proc&eacute;dures par d&eacute;cret. Mais cette voie n'est ouverte qu'aux cas de perte cit&eacute;s par l'article 24-2. Une perte li&eacute;e &agrave; l'ind&eacute;pendance d'un territoire rel&egrave;ve du d&eacute;cret.</p>
</div>

<h2>Prouver que vous avez &eacute;t&eacute; fran&ccedil;ais&nbsp;: le nerf du dossier</h2>

<p>La pi&egrave;ce qui d&eacute;cide de tout est celle qui &eacute;tablit votre nationalit&eacute; fran&ccedil;aise pass&eacute;e. Selon votre histoire, il s'agira de&nbsp;:</p>

<ul>
  <li>votre <strong>acte de naissance</strong> &eacute;tabli en Alg&eacute;rie avant le 3 juillet 1962, accompagn&eacute; des actes de naissance de vos parents, pour les personnes de statut local&nbsp;;</li>
  <li>un ancien document fran&ccedil;ais &agrave; votre nom&nbsp;: <strong>livret de famille, carte d'identit&eacute;, livret militaire, carte d'&eacute;lecteur</strong> d'avant l'ind&eacute;pendance&nbsp;;</li>
  <li>l'<strong>ampliation d'un d&eacute;cret</strong> de naturalisation ou de r&eacute;int&eacute;gration, une d&eacute;claration de nationalit&eacute; enregistr&eacute;e, un certificat de nationalit&eacute; fran&ccedil;aise ou un jugement, si vous aviez acquis la nationalit&eacute; par ces voies&nbsp;;</li>
  <li>pour la voie par d&eacute;claration, un <strong>certificat des autorit&eacute;s du pays</strong> dont vous avez acquis la nationalit&eacute;, pr&eacute;cisant la date d'acquisition et la loi qui l'a permise.</li>
</ul>

<p>Les actes &eacute;tablis en Alg&eacute;rie avant 1962 s'obtiennent aupr&egrave;s de la commune alg&eacute;rienne de naissance et, selon les cas, aupr&egrave;s des Archives nationales d'outre-mer ou du <a href="/glossaire/scec.html">Service central d'&eacute;tat civil</a> de Nantes. Comptez plusieurs mois&nbsp;: c'est la premi&egrave;re d&eacute;marche &agrave; lancer, avant m&ecirc;me le test de langue. Chaque document &eacute;tranger doit &ecirc;tre traduit par un traducteur agr&eacute;&eacute;, et les actes d'&eacute;tat civil sont fournis en copie int&eacute;grale.</p>

<h2>Le B2 et l'examen civique&nbsp;: ce que 2026 change pour les candidats &agrave; la r&eacute;int&eacute;gration</h2>

<p>Beaucoup de candidats &agrave; la r&eacute;int&eacute;gration ont grandi avec le fran&ccedil;ais, parfois fait toute leur scolarit&eacute; en fran&ccedil;ais. Mais depuis le 1<sup>er</sup> janvier 2026, un dipl&ocirc;me &eacute;tranger, m&ecirc;me obtenu en fran&ccedil;ais, ne prouve plus le niveau&nbsp;: les attestations de comparabilit&eacute; ENIC-NARIC ne sont plus accept&eacute;es. Seuls comptent un <strong>dipl&ocirc;me fran&ccedil;ais</strong> (brevet, CAP, bac, dipl&ocirc;me du sup&eacute;rieur d&eacute;livr&eacute; au nom de l'&Eacute;tat), un <strong>DELF B2 ou DALF</strong>, ou une <strong>attestation TCF ou TEF</strong> de moins de deux ans. Parler fran&ccedil;ais ne suffit pas&nbsp;: il faut le certifier, &agrave; l'&eacute;crit comme &agrave; l'oral.</p>

<p>L'examen civique est la seconde marche. 40&nbsp;questions, 45&nbsp;minutes, 32&nbsp;bonnes r&eacute;ponses exig&eacute;es&nbsp;: le seuil de 80&nbsp;% ne laisse que 8&nbsp;erreurs, et les 12&nbsp;questions de mise en situation surprennent les candidats qui ont r&eacute;vis&eacute; l'histoire mais pas la vie quotidienne (la&iuml;cit&eacute;, &eacute;galit&eacute; femmes-hommes, r&egrave;gles du vivre-ensemble).</p>

<p>L'application <a href="https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087" target="_blank">Naturalisation France Facile</a> a &eacute;t&eacute; con&ccedil;ue pour ces deux &eacute;preuves&nbsp;: plus de 750&nbsp;exercices calibr&eacute;s B2 sur les 4&nbsp;&eacute;preuves du TCF IRN et du DELF B2, avec correction de vos productions &eacute;crites et orales et des examens blancs en conditions r&eacute;elles&nbsp;; 258&nbsp;questions d'examen civique sur les 5&nbsp;th&egrave;mes officiels, 100&nbsp;mises en situation et une explication apr&egrave;s chaque r&eacute;ponse. Le simulateur d'entretien vous pr&eacute;pare ensuite aux questions de la pr&eacute;fecture, et la checklist des pi&egrave;ces vous &eacute;vite d'oublier la preuve de nationalit&eacute; ant&eacute;rieure, absente des listes standard.</p>

<h2>L'ordre des d&eacute;marches qui &eacute;vite de perdre un an</h2>

<ol>
  <li><strong>R&eacute;unissez d'abord la preuve de votre nationalit&eacute; pass&eacute;e.</strong> C'est la pi&egrave;ce la plus longue &agrave; obtenir, et sans elle le dossier est irrecevable.</li>
  <li><strong>Identifiez votre voie.</strong> Perte par mariage, par acquisition volontaire ou par mandat public&nbsp;: d&eacute;claration au tribunal. Tout autre cas, dont l'ind&eacute;pendance d'un territoire&nbsp;: d&eacute;cret.</li>
  <li><strong>Pour le d&eacute;cret, planifiez le B2 et l'examen civique.</strong> Une attestation TCF ou TEF n'est valable que 2&nbsp;ans&nbsp;: passez le test quand le reste du dossier est pr&ecirc;t, pas deux ans avant.</li>
  <li><strong>D&eacute;posez en ligne</strong>, avec le timbre fiscal de 255&nbsp;&euro;, puis suivez l'instruction sur votre espace ANEF.</li>
  <li><strong>Pr&eacute;parez l'entretien.</strong> Pour une r&eacute;int&eacute;gration, l'agent s'int&eacute;ressera &agrave; votre parcours, aux circonstances de la perte et &agrave; vos liens actuels avec la France.</li>
</ol>
""",
    "faq": [
        ("Qu'est-ce que la réintégration dans la nationalité française ?",
         "C'est la procédure qui permet à une personne qui a possédé puis perdu la nationalité française de la retrouver (article 24 du Code civil). Elle se fait par décret, aux conditions de la naturalisation mais sans durée minimale de résidence, ou par déclaration dans trois cas de perte précis : mariage avec un étranger, acquisition volontaire d'une nationalité étrangère, exercice de certains mandats publics."),
        ("Je suis né en Algérie avant 1962 : puis-je être réintégré dans la nationalité française ?",
         "Oui, si vous étiez de statut civil de droit local et avez perdu la nationalité française au 1er janvier 1963 faute de déclaration recognitive : vous avez possédé la qualité de Français. La réintégration par décret est possible à tout âge et sans condition de stage, mais elle exige de résider en France, de justifier du niveau B2 et de réussir l'examen civique."),
        ("Je suis né en France après 1962 de parents nés en Algérie : dois-je demander la réintégration ?",
         "Non. En application de l'article 19-3 du Code civil, l'enfant né en France depuis le 1er janvier 1963 d'un parent né en Algérie avant le 3 juillet 1962 est français de naissance, quel que soit le statut de ses parents. Demandez un certificat de nationalité française au tribunal judiciaire, pas une réintégration."),
        ("Peut-on être réintégré en résidant à l'étranger ?",
         "Par décret, non : la réintégration suit les règles de la naturalisation, qui exigent de résider en France au moment de la signature du décret (réponse ministérielle du 3 juin 2025). Seules quelques situations assimilées à une résidence en France font exception, comme une activité exercée pour le compte de l'État français, la résidence à Monaco ou le service dans l'armée française. La réintégration par déclaration, elle, peut être souscrite au consulat."),
        ("Faut-il passer le test de français et l'examen civique pour être réintégré ?",
         "Pour la réintégration par décret, oui : niveau B2 à l'écrit et à l'oral, et réussite de l'examen civique, comme pour toute naturalisation depuis le 1er janvier 2026. Pour la réintégration par déclaration, non : ni test de langue ni examen civique."),
        ("Combien coûte la réintégration et combien de temps dure-t-elle ?",
         "Par décret : un timbre fiscal de 255 € (127,50 € en Guyane), plus le coût du test de langue et de l'examen civique ; l'administration a 18 mois pour répondre à partir du récépissé, ramenés à 12 mois si vous résidez en France depuis au moins 10 ans, prolongeables une fois de 3 mois. Par déclaration : décision dans les 6 mois du récépissé, le silence valant enregistrement."),
        ("Quelle différence entre réintégration et naturalisation ?",
         "Une seule condition disparaît : la durée minimale de résidence en France, 5 ans en règle générale. Tout le reste est identique : résidence en France, titre de séjour, B2, examen civique, entretien, ressources, moralité. S'y ajoute la preuve que vous avez été français."),
        ("Mes enfants deviennent-ils français avec moi ?",
         "Oui. La réintégration par décret ou par déclaration produit effet à l'égard de vos enfants de moins de 18 ans qui résident habituellement avec vous, à condition qu'ils soient mentionnés dans le décret ou la déclaration (article 24-3 du Code civil)."),
    ],
    "links": [
        ("/blog/conditions-naturalisation-francaise.html", "Les conditions de la naturalisation, auxquelles renvoie la r&eacute;int&eacute;gration"),
        ("/blog/tcf-irn-ou-delf-b2-lequel-choisir.html", "TCF IRN ou DELF B2&nbsp;: lequel choisir pour prouver le B2"),
        ("/blog/examen-civique-naturalisation-2026.html", "L'examen civique&nbsp;: format, seuil et m&eacute;thode"),
        ("/blog/naturalisation-apres-65-ans.html", "Naturalisation apr&egrave;s 65&nbsp;ans&nbsp;: la d&eacute;claration sans test"),
        ("/outils/decret-naturalisation.html", "V&eacute;rifier la publication de votre d&eacute;cret (code REI)"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2214", "Service-public.gouv.fr &mdash; R&eacute;int&eacute;gration dans la nationalit&eacute; fran&ccedil;aise par d&eacute;cret (F2214)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F3071", "Service-public.gouv.fr &mdash; R&eacute;int&eacute;gration par d&eacute;claration (F3071)"),
        ("https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070721/LEGISCTA000006149957/", "Code civil &mdash; Articles 24 &agrave; 24-3 (r&eacute;int&eacute;gration)"),
        ("https://questions.assemblee-nationale.fr/q17/17-2579QE.htm", "Assembl&eacute;e nationale &mdash; R&eacute;ponse minist&eacute;rielle du 3 juin 2025 sur les Alg&eacute;riens n&eacute;s avant le 3 juillet 1962"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F39426", "Service-public.gouv.fr &mdash; Examen civique&nbsp;: proc&eacute;dures concern&eacute;es (F39426)"),
    ],
    "cta": "Pr&eacute;parer le B2 et l'examen civique avec l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"naturalisation-refugie-2026": {
    "title": "Naturalisation d'un réfugié : conditions, B2 et délais (2026)",
    "h1": "Naturalisation des r&eacute;fugi&eacute;s&nbsp;: sans condition de stage, mais pas sans conditions",
    "desc": "Réfugié, vous pouvez déposer sans attendre 5 ans. Mais B2, examen civique et ressources stables restent exigés, et la protection subsidiaire n'a pas cette dispense.",
    "og": "Naturalisation des r&eacute;fugi&eacute;s en 2026&nbsp;: ce qui est vraiment exig&eacute;",
    "tag": "Conditions",
    "og_img": "default.png",
    "date": "2026-09-17",
    "date_fr": "17 septembre 2026",
    "lede": "La Convention de Gen&egrave;ve demande aux &Eacute;tats de faciliter la naturalisation des r&eacute;fugi&eacute;s, et le droit fran&ccedil;ais le fait sur un point pr&eacute;cis&nbsp;: aucune dur&eacute;e minimale de r&eacute;sidence n'est exig&eacute;e. Sur tout le reste, un r&eacute;fugi&eacute; est un candidat comme les autres, et depuis 2026 les autres marches (niveau B2, examen civique, ressources appr&eacute;ci&eacute;es sur cinq ans) sont plus hautes. Voici ce qui vous est demand&eacute;, ce qui ne l'est pas, et l'ordre dans lequel avancer.",
    "body": """
<h2>La dispense de stage&nbsp;: ce qu'elle veut dire, et ce qu'elle ne veut pas dire</h2>

<p>L'article 21-19 du Code civil permet de naturaliser &laquo;&nbsp;sans condition de stage&nbsp;&raquo; l'&eacute;tranger qui a obtenu le statut de r&eacute;fugi&eacute;. Le stage, c'est la dur&eacute;e de r&eacute;sidence habituelle en France exig&eacute;e avant de d&eacute;poser&nbsp;: 5&nbsp;ans en r&egrave;gle g&eacute;n&eacute;rale. Un r&eacute;fugi&eacute; statutaire peut donc, en droit, d&eacute;poser sa demande d&egrave;s la reconnaissance de son statut par l'OFPRA ou la CNDA.</p>

<p>Cette dispense ne supprime rien d'autre. Vous devez toujours <strong>r&eacute;sider en France</strong> au moment du d&eacute;cret et y avoir le centre de vos int&eacute;r&ecirc;ts, d&eacute;tenir un titre de s&eacute;jour valide (la carte de r&eacute;sident d&eacute;livr&eacute;e aux r&eacute;fugi&eacute;s convient), justifier du <strong>niveau B2</strong>, r&eacute;ussir l'<strong>examen civique</strong>, passer l'<strong>entretien</strong> d'assimilation, et disposer de <strong>ressources stables et suffisantes</strong>.</p>

<div class="callout">
  <p><strong>Le vrai calendrier&nbsp;:</strong> la loi permet de d&eacute;poser tout de suite, mais la circulaire du 2 mai 2025 demande aux pr&eacute;fectures d'appr&eacute;cier l'insertion professionnelle <em>sur cinq ans</em>. D&eacute;poser sans emploi stable ni certification B2 conduit presque toujours &agrave; un ajournement. La dispense de stage fait gagner du temps &agrave; ceux qui sont pr&ecirc;ts&nbsp;; elle ne rend pas pr&ecirc;t.</p>
</div>

<h2>R&eacute;fugi&eacute;, protection subsidiaire, apatride&nbsp;: trois r&eacute;gimes diff&eacute;rents</h2>

<table class="article-table">
  <thead><tr><th>Statut</th><th>Dur&eacute;e de r&eacute;sidence exig&eacute;e</th><th>Test de langue B2</th></tr></thead>
  <tbody>
    <tr><td>R&eacute;fugi&eacute; statutaire (OFPRA ou CNDA)</td><td><em>Aucune</em> (art. 21-19)</td><td>Exig&eacute;, sauf apr&egrave;s 70&nbsp;ans et 15&nbsp;ans de r&eacute;sidence</td></tr>
    <tr><td>B&eacute;n&eacute;ficiaire de la protection subsidiaire</td><td>5&nbsp;ans (r&egrave;gle g&eacute;n&eacute;rale)</td><td>Exig&eacute;</td></tr>
    <tr><td>Apatride reconnu par l'OFPRA</td><td>5&nbsp;ans (r&egrave;gle g&eacute;n&eacute;rale)</td><td>Exig&eacute;, sauf apr&egrave;s 70&nbsp;ans et 15&nbsp;ans de r&eacute;sidence</td></tr>
  </tbody>
</table>

<p>Le point qui surprend&nbsp;: la <strong>protection subsidiaire</strong> ne donne pas la dispense de stage. L'article 21-19 ne vise que le statut de r&eacute;fugi&eacute; au sens de la Convention de Gen&egrave;ve. Si vous &ecirc;tes b&eacute;n&eacute;ficiaire de la protection subsidiaire, vous relevez de la r&egrave;gle g&eacute;n&eacute;rale des 5&nbsp;ans de r&eacute;sidence habituelle, sauf si une autre r&eacute;duction s'applique &agrave; vous, par exemple un dipl&ocirc;me du sup&eacute;rieur fran&ccedil;ais obtenu apr&egrave;s deux ans d'&eacute;tudes, qui ram&egrave;ne le stage &agrave; 2&nbsp;ans. Les ann&eacute;es pass&eacute;es en France en s&eacute;jour r&eacute;gulier, y compris pendant la proc&eacute;dure d'asile, comptent en principe dans ce calcul&nbsp;; c'est votre installation durable (logement, travail, famille) que la pr&eacute;fecture regarde.</p>

<h2>Le niveau B2&nbsp;: la marche la plus haute, sans dispense li&eacute;e au statut</h2>

<p>Depuis le 1<sup>er</sup> janvier 2026, tout candidat &agrave; la naturalisation doit justifier d'un niveau B2 &agrave; l'&eacute;crit et &agrave; l'oral. Le statut de r&eacute;fugi&eacute; n'y change rien, et la seule dispense pr&eacute;vue par la loi est &eacute;troite&nbsp;: l'article 21-24-1 en exempte le r&eacute;fugi&eacute; politique ou l'apatride <strong>&acirc;g&eacute; de plus de 70&nbsp;ans</strong> qui r&eacute;side r&eacute;guli&egrave;rement en France <strong>depuis au moins 15&nbsp;ans</strong>. Les conditions sont cumulatives. L'autre dispense concerne un handicap ou un &eacute;tat de sant&eacute; qui rend l'&eacute;valuation impossible, sur certificat m&eacute;dical.</p>

<p>Pour tous les autres, il faut un justificatif&nbsp;: un dipl&ocirc;me fran&ccedil;ais (brevet, CAP, bac, dipl&ocirc;me du sup&eacute;rieur d&eacute;livr&eacute; au nom de l'&Eacute;tat), un DELF B2 ou un DALF, ou une attestation TCF ou TEF de moins de deux ans. Un dipl&ocirc;me obtenu dans le pays d'origine, m&ecirc;me en fran&ccedil;ais, ne prouve plus le niveau depuis 2026.</p>

<p>La difficult&eacute; est concr&egrave;te&nbsp;: les formations linguistiques de l'OFII, dans le cadre du contrat d'int&eacute;gration r&eacute;publicaine, visent le niveau A1 puis A2. Entre A2 et B2, il y a plusieurs centaines d'heures de travail. Notre guide sur <a href="/blog/atteindre-niveau-b2-naturalisation.html">le chemin vers le B2</a> propose un plan de travail r&eacute;aliste, et l'application <a href="https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087" target="_blank">Naturalisation France Facile</a> vous entra&icirc;ne sur les 4&nbsp;&eacute;preuves du TCF IRN et du DELF B2 (compr&eacute;hension orale avec transcription, compr&eacute;hension &eacute;crite, expression &eacute;crite et orale corrig&eacute;es selon les crit&egrave;res officiels), avec des examens blancs pour mesurer o&ugrave; vous en &ecirc;tes avant de payer une inscription.</p>

<h2>L'examen civique&nbsp;: obligatoire, comme pour tout le monde</h2>

<p>Le QCM de 40&nbsp;questions s'impose &agrave; toute demande par d&eacute;cret depuis le 1<sup>er</sup> janvier 2026, sans dispense li&eacute;e au statut de r&eacute;fugi&eacute;&nbsp;; seule une impossibilit&eacute; m&eacute;dicale y &eacute;chappe. Il faut 32&nbsp;bonnes r&eacute;ponses&nbsp;; les questions portent sur l'histoire, les institutions, les droits et devoirs, la place de la France dans le monde et la vie en soci&eacute;t&eacute;. Les 12&nbsp;questions de mise en situation testent des r&eacute;flexes (la&iuml;cit&eacute;, &eacute;galit&eacute;, respect des lois) plut&ocirc;t que des dates. L'app contient 258&nbsp;questions et 100&nbsp;mises en situation avec explication&nbsp;: s'entra&icirc;ner en fran&ccedil;ais tout en r&eacute;visant, les deux pr&eacute;parations se renforcent.</p>

<h2>Le dossier d'un r&eacute;fugi&eacute;&nbsp;: ce qui diff&egrave;re des autres candidats</h2>

<h3>L'&eacute;tat civil vient de l'OFPRA, jamais du consulat</h3>

<p>Ne contactez en aucun cas les autorit&eacute;s du pays que vous avez fui&nbsp;: une d&eacute;marche aupr&egrave;s de votre consulat peut &ecirc;tre interpr&eacute;t&eacute;e comme un acte d'all&eacute;geance et remettre en cause votre protection. C'est l'<strong>OFPRA</strong> qui &eacute;tablit vos actes d'&eacute;tat civil (certificats tenant lieu d'acte de naissance ou de mariage). Ces documents ont valeur d'actes fran&ccedil;ais&nbsp;: demandez-les en ligne sur le site de l'OFPRA suffisamment t&ocirc;t pour qu'ils aient <strong>moins de 3&nbsp;mois</strong> au moment du d&eacute;p&ocirc;t.</p>

<h3>Pas d'extrait de casier judiciaire du pays d'origine</h3>

<p>La r&egrave;gle g&eacute;n&eacute;rale exige un <a href="/blog/casier-judiciaire-naturalisation.html">extrait de casier judiciaire &eacute;tranger</a> des candidats install&eacute;s en France depuis moins de 10&nbsp;ans. Elle ne s'applique pas au pays d'origine du r&eacute;fugi&eacute; ou de l'apatride prot&eacute;g&eacute; par l'OFPRA. Le b&eacute;n&eacute;ficiaire de la protection subsidiaire, lui aussi plac&eacute; sous la protection de l'OFPRA, documente l'impossibilit&eacute; de le demander plut&ocirc;t que de contacter son pays. Si vous avez v&eacute;cu dans un pays tiers avant la France, l'extrait de ce pays reste en revanche demand&eacute;, ou une attestation d'impossibilit&eacute;.</p>

<h3>Le titre de s&eacute;jour et le titre de voyage</h3>

<p>Fournissez votre carte de r&eacute;sident (ou votre carte de s&eacute;jour pluriannuelle, pour la protection subsidiaire) et, comme document d'identit&eacute;, votre titre de voyage pour r&eacute;fugi&eacute;. Le passeport du pays d'origine ne doit pas figurer au dossier.</p>

<h3>Les ressources&nbsp;: le vrai motif d'ajournement</h3>

<p>&laquo;&nbsp;Naturalisation r&eacute;fugi&eacute; sans emploi&nbsp;&raquo; est l'une des recherches les plus fr&eacute;quentes sur le sujet, et la r&eacute;ponse est nette depuis la circulaire du 2 mai 2025&nbsp;: les revenus sont appr&eacute;ci&eacute;s <strong>hors prestations sociales</strong>, et les demandes dont les ressources proviennent majoritairement de ces prestations sont, sauf exception, &eacute;cart&eacute;es. Pour un salari&eacute;, la pr&eacute;fecture attend un CDI de plus d'un an ou une continuit&eacute; de CDD sur 24&nbsp;mois. Une exception explicite&nbsp;: l'insuffisance de ressources qui r&eacute;sulte directement d'une maladie ou d'un handicap ne peut pas vous &ecirc;tre oppos&eacute;e. Notre article sur <a href="/blog/ressources-revenus-naturalisation.html">ce que la pr&eacute;fecture regarde</a> d&eacute;taille chaque situation (CDD, int&eacute;rim, auto-entrepreneur, formation).</p>

<h2>D&eacute;lais, d&eacute;cision et effets sur votre statut</h2>

<p>Le d&eacute;lai l&eacute;gal de r&eacute;ponse est de 18&nbsp;mois &agrave; compter du r&eacute;c&eacute;piss&eacute; de dossier complet, ramen&eacute; &agrave; 12&nbsp;mois si vous r&eacute;sidez habituellement en France depuis au moins 10&nbsp;ans, prolongeable une fois de 3&nbsp;mois. Il n'existe pas de proc&eacute;dure acc&eacute;l&eacute;r&eacute;e propre aux r&eacute;fugi&eacute;s&nbsp;; les d&eacute;lais r&eacute;els varient surtout selon la <a href="/blog/delais-naturalisation-par-prefecture.html">plateforme de naturalisation</a> qui instruit votre dossier.</p>

<p>Le jour o&ugrave; le d&eacute;cret est sign&eacute;, vous &ecirc;tes fran&ccedil;ais, et vos enfants mineurs qui vivent avec vous le deviennent s'ils y sont mentionn&eacute;s. Votre statut de r&eacute;fugi&eacute; prend alors fin&nbsp;: la protection de la France remplace celle de l'OFPRA, vous demandez une carte d'identit&eacute; et un passeport fran&ccedil;ais, et le titre de voyage n'a plus d'objet. Nos <a href="/blog/demarches-apres-naturalisation.html">d&eacute;marches des 6 premiers mois</a> vous guident dans l'ordre.</p>

<h2>Dans quel ordre avancer</h2>

<ol>
  <li><strong>Stabilisez d'abord votre situation professionnelle.</strong> C'est ce qui d&eacute;cide entre d&eacute;cret et ajournement, bien plus que la date du d&eacute;p&ocirc;t.</li>
  <li><strong>Travaillez le B2 en parall&egrave;le</strong>, par paliers (A2, B1, B2)&nbsp;: mesurez votre niveau avec un examen blanc avant de vous inscrire.</li>
  <li><strong>Passez l'examen civique</strong> une fois le vocabulaire en place&nbsp;; l'attestation n'a pas de dur&eacute;e de validit&eacute; limit&eacute;e.</li>
  <li><strong>Commandez vos actes &agrave; l'OFPRA</strong> trois &agrave; quatre semaines avant le d&eacute;p&ocirc;t, pour respecter la r&egrave;gle des 3&nbsp;mois.</li>
  <li><strong>D&eacute;posez en ligne</strong> sur l'ANEF avec le timbre fiscal de 255&nbsp;&euro;, puis pr&eacute;parez l'entretien avec le simulateur.</li>
</ol>
""",
    "faq": [
        ("Un réfugié peut-il demander la naturalisation dès l'obtention de son statut ?",
         "En droit, oui : l'article 21-19 du Code civil dispense les réfugiés statutaires de toute durée minimale de résidence. En pratique, la demande n'aboutit que si les autres conditions sont réunies : titre de séjour valide, niveau B2 certifié, examen civique réussi, ressources stables appréciées sur cinq ans."),
        ("La protection subsidiaire donne-t-elle la même dispense ?",
         "Non. La dispense de stage ne vise que le statut de réfugié. Un bénéficiaire de la protection subsidiaire doit justifier de 5 ans de résidence habituelle en France, sauf autre cause de réduction, par exemple un diplôme du supérieur français obtenu après deux ans d'études, qui ramène la durée à 2 ans."),
        ("Un réfugié est-il dispensé du test de français B2 ?",
         "Seulement s'il remplit des conditions cumulatives : être réfugié politique ou apatride, avoir plus de 70 ans et résider régulièrement en France depuis au moins 15 ans (article 21-24-1). Tous les autres doivent fournir un diplôme français, un DELF B2 ou DALF, ou une attestation TCF/TEF de moins de 2 ans. Un handicap ou un état de santé rendant l'évaluation impossible ouvre aussi une dispense, sur certificat médical."),
        ("Un réfugié doit-il passer l'examen civique ?",
         "Oui. L'examen civique s'applique à toute demande de naturalisation ou de réintégration par décret depuis le 1er janvier 2026, quel que soit le statut du candidat. Seule une impossibilité médicale attestée permet d'en être dispensé."),
        ("Peut-on être naturalisé en étant réfugié sans emploi ?",
         "C'est très difficile depuis la circulaire du 2 mai 2025 : les ressources sont appréciées hors prestations sociales, et les demandes reposant majoritairement sur ces prestations sont en principe écartées ou ajournées. Exception : si l'insuffisance des ressources résulte directement d'une maladie ou d'un handicap, elle ne peut pas vous être opposée."),
        ("Quels documents d'état civil fournir quand on est réfugié ?",
         "Les certificats tenant lieu d'actes d'état civil délivrés par l'OFPRA (naissance, mariage), à demander en ligne et datés de moins de 3 mois au dépôt. Ne contactez jamais les autorités de votre pays d'origine. L'extrait de casier judiciaire de ce pays n'est pas exigé."),
        ("Que devient mon statut de réfugié après la naturalisation ?",
         "Il prend fin : en devenant français, vous bénéficiez de la protection de la France et n'avez plus besoin de celle de l'OFPRA. Vous demandez une carte d'identité et un passeport français ; le titre de voyage pour réfugié n'a plus d'objet."),
        ("Mes enfants deviennent-ils français avec moi ?",
         "Oui, s'ils ont moins de 18 ans, résident habituellement avec vous et sont mentionnés dans le décret. Leur minorité s'apprécie à la date de signature du décret."),
    ],
    "links": [
        ("/blog/ressources-revenus-naturalisation.html", "Ressources et naturalisation&nbsp;: ce que la pr&eacute;fecture regarde"),
        ("/blog/atteindre-niveau-b2-naturalisation.html", "Atteindre le niveau B2&nbsp;: plan de travail A2&rarr;B2"),
        ("/blog/naturalisation-sans-condition-de-stage.html", "Naturalisation sans condition de stage&nbsp;: toutes les dispenses"),
        ("/blog/documents-naturalisation.html", "La liste compl&egrave;te des pi&egrave;ces du dossier"),
        ("/blog/ajournement-vs-refus-naturalisation.html", "Ajournement ou refus&nbsp;: que faire"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret&nbsp;: conditions et pi&egrave;ces (F2213)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F11926", "Service-public.gouv.fr &mdash; Justifier de son niveau de fran&ccedil;ais, dispenses (F11926)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F39426", "Service-public.gouv.fr &mdash; Examen civique (F39426)"),
        ("https://www.legifrance.gouv.fr/circulaire/id/45604", "L&eacute;gifrance &mdash; Circulaire du 2 mai 2025, orientations relatives &agrave; l'acquisition de la nationalit&eacute; fran&ccedil;aise"),
        ("https://www.ofpra.gouv.fr/mes-documents-detat-civil", "OFPRA &mdash; Mes documents d'&eacute;tat civil"),
    ],
    "cta": "Pr&eacute;parer le B2 et l'examen civique avec l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"naturalisation-apres-etudes-en-france": {
    "title": "Naturalisation après des études en France : 2 ans suffisent ?",
    "h1": "Naturalisation apr&egrave;s des &eacute;tudes en France&nbsp;: le stage r&eacute;duit &agrave; 2&nbsp;ans, mode d'emploi",
    "desc": "Un diplôme du supérieur français après 2 ans d'études ramène la résidence exigée à 2 ans. Étudiant, alternant, doctorant, passeport talent : ce que la préfecture attend.",
    "og": "Naturalisation apr&egrave;s des &eacute;tudes en France&nbsp;: le stage r&eacute;duit &agrave; 2&nbsp;ans",
    "tag": "Conditions",
    "og_img": "default.png",
    "date": "2026-09-17",
    "date_fr": "17 septembre 2026",
    "lede": "Vous avez obtenu un dipl&ocirc;me dans une universit&eacute; ou une &eacute;cole fran&ccedil;aise, et vous vous demandez si vous devez attendre cinq ans de r&eacute;sidence avant de demander la nationalit&eacute;. Non&nbsp;: le Code civil ram&egrave;ne cette dur&eacute;e &agrave; deux ans pour les dipl&ocirc;m&eacute;s du sup&eacute;rieur fran&ccedil;ais. Mais entre la lettre de la loi et la d&eacute;cision de la pr&eacute;fecture, il y a l'insertion professionnelle, le niveau de langue, et une circulaire de 2025 qui a durci la lecture de tout cela. Voici ce qui compte vraiment.",
    "body": """
<h2>La r&egrave;gle&nbsp;: deux ans au lieu de cinq</h2>

<p>La naturalisation exige en principe cinq ann&eacute;es de r&eacute;sidence habituelle en France avant le d&eacute;p&ocirc;t de la demande&nbsp;: c'est le &laquo;&nbsp;stage&nbsp;&raquo; de l'article 21-17 du Code civil. L'article 21-18 le r&eacute;duit &agrave; <strong>deux ans</strong> pour &laquo;&nbsp;l'&eacute;tranger qui a accompli avec succ&egrave;s deux ann&eacute;es d'&eacute;tudes sup&eacute;rieures en vue d'acqu&eacute;rir un dipl&ocirc;me d&eacute;livr&eacute; par une universit&eacute; ou un &eacute;tablissement d'enseignement sup&eacute;rieur fran&ccedil;ais&nbsp;&raquo;. Service-public le r&eacute;sume ainsi&nbsp;: avoir obtenu un dipl&ocirc;me d'un &eacute;tablissement d'enseignement sup&eacute;rieur fran&ccedil;ais apr&egrave;s deux ans d'&eacute;tudes.</p>

<p>Trois &eacute;l&eacute;ments doivent donc &ecirc;tre r&eacute;unis&nbsp;:</p>

<ul>
  <li><strong>deux ann&eacute;es d'&eacute;tudes sup&eacute;rieures</strong> accomplies en France, avec succ&egrave;s&nbsp;;</li>
  <li>un <strong>dipl&ocirc;me obtenu</strong>&nbsp;: un cursus interrompu avant le dipl&ocirc;me ne suffit pas&nbsp;;</li>
  <li>un &eacute;tablissement <strong>fran&ccedil;ais</strong>&nbsp;: universit&eacute;, &eacute;cole d'ing&eacute;nieurs ou de commerce, IUT, section de BTS. Un dipl&ocirc;me &eacute;tranger pr&eacute;par&eacute; &agrave; distance depuis la France ne compte pas.</li>
</ul>

<p>Concr&egrave;tement, un master (deux ans), un BTS ou un BUT, une licence ou un dipl&ocirc;me d'ing&eacute;nieur remplissent la condition. Une seule ann&eacute;e en France, m&ecirc;me dipl&ocirc;mante, ne suffit pas&nbsp;: un master 2 obtenu apr&egrave;s un master 1 &agrave; l'&eacute;tranger, par exemple, ne fait qu'une ann&eacute;e d'&eacute;tudes sup&eacute;rieures en France.</p>

<div class="callout">
  <p><strong>Ce que la r&eacute;duction ne change pas&nbsp;:</strong> les deux ans sont une dur&eacute;e de r&eacute;sidence, pas un droit &agrave; la naturalisation. Tout le reste s'applique&nbsp;: titre de s&eacute;jour valide, r&eacute;sidence en France au moment du d&eacute;cret, niveau B2, examen civique, entretien, ressources stables, moralit&eacute;.</p>
</div>

<h2>Les ann&eacute;es d'&eacute;tudes comptent-elles dans la r&eacute;sidence&nbsp;?</h2>

<p>Oui&nbsp;: le stage s'appr&eacute;cie en r&eacute;sidence habituelle, et les ann&eacute;es pass&eacute;es en France sous un titre de s&eacute;jour &eacute;tudiant sont des ann&eacute;es de r&eacute;sidence r&eacute;guli&egrave;re. Un &eacute;tudiant arriv&eacute; pour une licence et rest&eacute; pour un master a souvent d&eacute;j&agrave; cinq ans de pr&eacute;sence&nbsp;; la r&eacute;duction &agrave; deux ans sert surtout &agrave; ceux qui sont arriv&eacute;s directement en master ou en &eacute;cole.</p>

<p>La nuance vient de la notion de <strong>centre des int&eacute;r&ecirc;ts</strong>. La pr&eacute;fecture v&eacute;rifie que votre vie est en France&nbsp;: travail, logement, famille, attaches. Un candidat dont le conjoint et les enfants vivent &agrave; l'&eacute;tranger, ou dont les revenus viennent majoritairement de l'&eacute;tranger, peut se voir refuser la naturalisation m&ecirc;me avec la dur&eacute;e requise&nbsp;: la circulaire du 2 mai 2025 demande explicitement d'&eacute;carter les demandes dont les revenus proviennent majoritairement de l'&eacute;tranger.</p>

<h2>Le point qui d&eacute;cide de tout&nbsp;: l'insertion professionnelle</h2>

<p>C'est le motif d'ajournement le plus fr&eacute;quent pour les jeunes dipl&ocirc;m&eacute;s. La circulaire du 2 mai 2025 demande aux pr&eacute;fets d'appr&eacute;cier l'insertion professionnelle <strong>sur cinq ans</strong> et, pour les salari&eacute;s, d'exiger un <strong>CDI de plus d'un an</strong> &agrave; la date d'examen de la demande, ou une <strong>continuit&eacute; de CDD sur 24&nbsp;mois</strong>. Les revenus sont compar&eacute;s au SMIC, major&eacute; selon la composition du foyer, et appr&eacute;ci&eacute;s hors prestations sociales.</p>

<p>Traduction pratique, situation par situation&nbsp;:</p>

<table class="article-table">
  <thead><tr><th>Situation</th><th>Lecture de la pr&eacute;fecture</th><th>Conseil</th></tr></thead>
  <tbody>
    <tr><td>&Eacute;tudiant encore en cours</td><td>Pas d'insertion professionnelle&nbsp;: ajournement tr&egrave;s probable, sauf profil de haut niveau</td><td>Attendre le dipl&ocirc;me et un premier contrat</td></tr>
    <tr><td>Alternant (apprentissage, professionnalisation)</td><td>Un contrat de travail et des revenus, mais &agrave; dur&eacute;e d&eacute;termin&eacute;e</td><td>D&eacute;poser une fois embauch&eacute; &agrave; l'issue de l'alternance</td></tr>
    <tr><td>Jeune dipl&ocirc;m&eacute; en CDD ou en int&eacute;rim</td><td>Continuit&eacute; exig&eacute;e sur 24&nbsp;mois</td><td>Constituer le dossier, d&eacute;poser au 24<sup>e</sup> mois ou d&egrave;s le CDI</td></tr>
    <tr><td>Salari&eacute; en CDI de plus d'un an</td><td>Situation attendue</td><td>D&eacute;poser d&egrave;s que le B2 et l'examen civique sont acquis</td></tr>
    <tr><td>Doctorant, chercheur, passeport talent</td><td>Profil &laquo;&nbsp;&agrave; potentiel &eacute;lev&eacute;&nbsp;&raquo; explicitement vis&eacute; par la circulaire</td><td>Mettre en avant le parcours&nbsp;: contrat doctoral, publications, projet</td></tr>
    <tr><td>Interne en m&eacute;decine ou en pharmacie</td><td>Salari&eacute; de l'h&ocirc;pital&nbsp;: insertion r&eacute;elle, contrats successifs</td><td>Joindre les contrats et le calendrier de l'internat</td></tr>
  </tbody>
</table>

<p>Pour les doctorants et les titulaires d'un passeport talent, la circulaire ouvre une porte suppl&eacute;mentaire&nbsp;: elle invite les pr&eacute;fectures &agrave; prendre en compte &laquo;&nbsp;les &eacute;tudiants de haut niveau et les professionnels titulaires d'un passeport talent&nbsp;&raquo; susceptibles de contribuer au rayonnement de la France, et rappelle qu'ils peuvent b&eacute;n&eacute;ficier de la r&eacute;duction du stage &agrave; deux ans au titre des <strong>services importants rendus par leurs capacit&eacute;s et talents</strong> (article 21-18, 2&deg;). Ce fondement ne demande pas de dipl&ocirc;me fran&ccedil;ais&nbsp;: il vise le profil.</p>

<h2>Votre dipl&ocirc;me fran&ccedil;ais prouve le niveau B2&nbsp;: pas de TCF &agrave; passer</h2>

<p>C'est l'avantage le plus concret, et le moins connu. Depuis le 1<sup>er</sup> janvier 2026, le niveau B2 se prouve soit par un test (TCF ou TEF de moins de deux ans, 200 &agrave; 300&nbsp;&euro; pour le TCF), soit par un dipl&ocirc;me. L'arr&ecirc;t&eacute; du 22 d&eacute;cembre 2025 accepte notamment <strong>tout dipl&ocirc;me d&eacute;livr&eacute; au nom de l'&Eacute;tat sanctionnant un niveau au moins &eacute;gal au niveau 3 du cadre national des certifications</strong>, et toute certification professionnelle enregistr&eacute;e au RNCP &agrave; partir de ce niveau. Une licence (niveau 6), un master (niveau 7), un doctorat (niveau 8), un BTS ou un BUT (niveau 5), un dipl&ocirc;me d'ing&eacute;nieur ou un baccalaur&eacute;at remplissent largement cette condition.</p>

<p>Deux v&eacute;rifications &agrave; faire avant de compter dessus&nbsp;:</p>

<ul>
  <li>le dipl&ocirc;me doit &ecirc;tre <strong>national</strong> (d&eacute;livr&eacute; au nom de l'&Eacute;tat) ou <strong>enregistr&eacute; au RNCP</strong>&nbsp;: un dipl&ocirc;me d'universit&eacute; (DU), un certificat d'&eacute;cole ou un &laquo;&nbsp;MBA&nbsp;&raquo; non enregistr&eacute; ne suffisent pas, m&ecirc;me prestigieux&nbsp;;</li>
  <li>l'arr&ecirc;t&eacute; ne pose aucune condition sur la langue d'enseignement&nbsp;: c'est le dipl&ocirc;me qui atteste le niveau. Mais si vous avez suivi un cursus enti&egrave;rement en anglais, pr&eacute;parez tout de m&ecirc;me l'entretien en pr&eacute;fecture, qui se d&eacute;roule en fran&ccedil;ais et &eacute;value votre aisance r&eacute;elle.</li>
</ul>

<p>Si votre dipl&ocirc;me n'entre pas dans ces cat&eacute;gories, il vous faudra un DELF B2, un DALF ou une attestation TCF ou TEF. L'application <a href="https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087" target="_blank">Naturalisation France Facile</a> vous entra&icirc;ne sur les quatre &eacute;preuves du TCF IRN et du DELF B2, avec correction de l'expression &eacute;crite et orale selon les crit&egrave;res officiels et des examens blancs complets&nbsp;: de quoi valider le niveau avant de payer une inscription.</p>

<h2>L'examen civique et l'entretien&nbsp;: ce qu'aucun dipl&ocirc;me ne remplace</h2>

<p>Aucun dipl&ocirc;me ne dispense de l'<strong>examen civique</strong>&nbsp;: 40&nbsp;questions, 32&nbsp;bonnes r&eacute;ponses, 45&nbsp;minutes, dans un centre agr&eacute;&eacute;, pour environ 70&nbsp;&euro;. Les dipl&ocirc;m&eacute;s le sous-estiment souvent, puis butent sur les questions de mise en situation et les rep&egrave;res historiques pr&eacute;cis. L'app propose 258&nbsp;questions sur les cinq th&egrave;mes officiels et 100&nbsp;mises en situation, avec une explication &agrave; chaque r&eacute;ponse.</p>

<p>L'<strong>entretien d'assimilation</strong> en pr&eacute;fecture, lui, portera sur votre parcours&nbsp;: pourquoi la France, pourquoi maintenant, quel projet professionnel, quelle vie ici. Un candidat qui explique clairement le lien entre ses &eacute;tudes, son emploi et son installation a un dossier coh&eacute;rent. Le simulateur d'entretien de l'app, avec notation de vos r&eacute;ponses, permet de r&eacute;p&eacute;ter ces questions avant le jour J.</p>

<h2>Le dossier&nbsp;: les pi&egrave;ces propres aux &eacute;tudiants et jeunes dipl&ocirc;m&eacute;s</h2>

<ul>
  <li>le <strong>dipl&ocirc;me</strong> obtenu en France, et les relev&eacute;s de notes attestant les deux ann&eacute;es valid&eacute;es&nbsp;;</li>
  <li>les <strong>titres de s&eacute;jour</strong> successifs, pour &eacute;tablir la continuit&eacute; de r&eacute;sidence&nbsp;: &eacute;tudiant, recherche d'emploi ou cr&eacute;ation d'entreprise, salari&eacute;, passeport talent&nbsp;;</li>
  <li>les avis d'imposition des trois derni&egrave;res ann&eacute;es, m&ecirc;me &laquo;&nbsp;non imposable&nbsp;&raquo;&nbsp;; si vous avez &eacute;t&eacute; pris en charge par vos parents, leur justificatif de ressources&nbsp;;</li>
  <li>pour un &eacute;tudiant boursier, l'attestation de bourse&nbsp;; pour un alternant, le contrat et les bulletins&nbsp;;</li>
  <li>le contrat de travail en cours et les trois derniers bulletins de salaire&nbsp;;</li>
  <li>l'attestation de r&eacute;ussite &agrave; l'examen civique et, si votre dipl&ocirc;me ne prouve pas le B2, l'attestation TCF ou TEF ou le DELF.</li>
</ul>

<p>L'<a href="/blog/casier-judiciaire-naturalisation.html">extrait de casier judiciaire du pays d'origine</a> est demand&eacute; aux candidats install&eacute;s en France depuis moins de dix ans, ce qui est presque toujours le cas des anciens &eacute;tudiants&nbsp;: lancez cette demande en premier, elle peut prendre des mois.</p>

<h2>Calendrier r&eacute;aliste pour un dipl&ocirc;m&eacute;</h2>

<ol>
  <li><strong>Pendant la derni&egrave;re ann&eacute;e d'&eacute;tudes&nbsp;:</strong> passez l'examen civique (l'attestation n'a pas de dur&eacute;e de validit&eacute; limit&eacute;e) et demandez l'extrait de casier judiciaire du pays d'origine.</li>
  <li><strong>Au premier emploi&nbsp;:</strong> r&eacute;unissez les justificatifs de r&eacute;sidence continue et d'imposition.</li>
  <li><strong>Au CDI de plus d'un an, ou &agrave; 24&nbsp;mois de contrats continus&nbsp;:</strong> d&eacute;posez en ligne sur l'ANEF, avec le timbre fiscal de 255&nbsp;&euro;.</li>
  <li><strong>Ensuite&nbsp;:</strong> entretien, puis instruction&nbsp;; le d&eacute;lai l&eacute;gal de r&eacute;ponse est de 18&nbsp;mois &agrave; compter du r&eacute;c&eacute;piss&eacute;.</li>
</ol>
""",
    "faq": [
        ("Peut-on demander la naturalisation après 2 ans d'études en France ?",
         "Oui, si vous avez obtenu un diplôme d'un établissement d'enseignement supérieur français après deux années d'études supérieures accomplies avec succès : l'article 21-18 du Code civil ramène alors la durée de résidence exigée de 5 à 2 ans. Les autres conditions (titre de séjour, B2, examen civique, ressources, moralité) restent entières."),
        ("Un étudiant encore en cours d'études peut-il être naturalisé ?",
         "Rien ne l'interdit, et service-public prévoit même les pièces à fournir dans ce cas (certificat de scolarité, attestation de bourse, prise en charge par les parents). Mais depuis la circulaire du 2 mai 2025, l'insertion professionnelle est appréciée sur cinq ans avec des ressources stables hors prestations : sans emploi, la demande est en général ajournée, sauf profil de haut niveau."),
        ("Les années passées avec un titre de séjour étudiant comptent-elles ?",
         "Oui, ce sont des années de résidence régulière et habituelle en France. La préfecture vérifie toutefois que le centre de vos intérêts est bien en France (travail, logement, famille) et que vos revenus ne viennent pas majoritairement de l'étranger."),
        ("Mon master français me dispense-t-il du TCF ?",
         "Oui. Depuis le 1er janvier 2026, tout diplôme délivré au nom de l'État sanctionnant au moins le niveau 3 du cadre national des certifications, ou toute certification RNCP à partir de ce niveau, justifie le niveau B2 : licence, master, doctorat, BTS, BUT, diplôme d'ingénieur, baccalauréat. Un diplôme d'université (DU) ou un certificat d'école non enregistré au RNCP ne suffit pas."),
        ("Qu'attend la préfecture d'un jeune diplômé côté emploi ?",
         "Pour un salarié, un CDI de plus d'un an à la date d'examen de la demande ou une continuité de CDD sur 24 mois, avec des revenus au moins au niveau du SMIC, majoré selon la composition du foyer et appréciés hors prestations sociales (circulaire du 2 mai 2025)."),
        ("Le passeport talent ou un doctorat aident-ils ?",
         "Oui. La circulaire du 2 mai 2025 invite les préfectures à prendre en compte les étudiants de haut niveau et les titulaires d'un passeport talent, et rappelle qu'ils peuvent bénéficier de la réduction du stage à deux ans au titre des services importants rendus à la France par leurs capacités et talents (article 21-18, 2°), indépendamment d'un diplôme français."),
        ("Un alternant peut-il déposer une demande ?",
         "Il le peut, et son contrat de travail est un vrai atout par rapport à un étudiant sans revenus. Mais un contrat d'apprentissage reste à durée déterminée : le dossier est plus solide une fois l'embauche obtenue à l'issue de l'alternance."),
        ("Faut-il passer l'examen civique même avec un diplôme français ?",
         "Oui. Aucun diplôme ne dispense de l'examen civique, obligatoire pour toute demande de naturalisation depuis le 1er janvier 2026. Seule une impossibilité médicale attestée y échappe."),
    ],
    "links": [
        ("/blog/conditions-naturalisation-francaise.html", "Les 7 conditions de la naturalisation"),
        ("/blog/ressources-revenus-naturalisation.html", "Ressources&nbsp;: CDD, int&eacute;rim, auto-entrepreneur, ce que chaque situation implique"),
        ("/blog/naturalisation-sans-condition-de-stage.html", "Naturalisation sans condition de stage&nbsp;: qui est dispens&eacute; des 5&nbsp;ans"),
        ("/blog/examen-civique-naturalisation-2026.html", "L'examen civique&nbsp;: 40&nbsp;questions, 80&nbsp;% de r&eacute;ussite"),
        ("/blog/ajournement-vs-refus-naturalisation.html", "Ajournement ou refus&nbsp;: que faire"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret&nbsp;: dur&eacute;e de r&eacute;sidence (F2213)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F11926", "Service-public.gouv.fr &mdash; Dipl&ocirc;mes et attestations accept&eacute;s pour justifier du niveau B2 (F11926)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F34746", "Service-public.gouv.fr &mdash; Justificatifs de revenus, cas de l'&eacute;tudiant (F34746)"),
        ("https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000053164463", "L&eacute;gifrance &mdash; Arr&ecirc;t&eacute; du 22 d&eacute;cembre 2025 relatif &agrave; la justification du niveau de ma&icirc;trise du fran&ccedil;ais"),
        ("https://www.legifrance.gouv.fr/circulaire/id/45604", "L&eacute;gifrance &mdash; Circulaire du 2 mai 2025, orientations relatives &agrave; l'acquisition de la nationalit&eacute; fran&ccedil;aise"),
    ],
    "cta": "Valider mon B2 et l'examen civique avec l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"naturalisation-sans-condition-de-stage": {
    "title": "Naturalisation sans condition de stage : qui est dispensé ?",
    "h1": "Naturalisation sans condition de stage&nbsp;: qui est dispens&eacute; des 5&nbsp;ans de r&eacute;sidence&nbsp;?",
    "desc": "Francophones, réfugiés, légionnaires, services exceptionnels : qui est dispensé des 5 ans de résidence, et pourquoi le B2, l'examen civique et l'entretien restent exigés.",
    "og": "Naturalisation sans condition de stage&nbsp;: la liste des dispenses",
    "tag": "Conditions",
    "og_img": "tcf-delf-b2.png",
    "date": "2026-09-17",
    "date_fr": "17 septembre 2026",
    "lede": "&laquo;&nbsp;Sans condition de stage&nbsp;&raquo; est la formule la plus mal comprise du droit de la nationalit&eacute;. Elle ne signifie ni &laquo;&nbsp;naturalisation imm&eacute;diate&nbsp;&raquo;, ni &laquo;&nbsp;sans test de langue&nbsp;&raquo;. Elle supprime une seule des conditions de la naturalisation&nbsp;: la dur&eacute;e minimale de r&eacute;sidence en France, cinq ans en r&egrave;gle g&eacute;n&eacute;rale. Voici qui en b&eacute;n&eacute;ficie, ce que la pr&eacute;fecture continue d'exiger, et pourquoi le niveau B2 est devenu, pour les francophones, la question centrale.",
    "body": """
<h2>Ce qu'est le stage, et ce que la dispense supprime</h2>

<p>Le &laquo;&nbsp;stage&nbsp;&raquo; d&eacute;signe la dur&eacute;e de r&eacute;sidence habituelle en France exig&eacute;e avant le d&eacute;p&ocirc;t d'une demande de naturalisation&nbsp;: cinq ans (article 21-17 du Code civil), ramen&eacute;s &agrave; deux ans dans certains cas (dipl&ocirc;me du sup&eacute;rieur fran&ccedil;ais, capacit&eacute;s et talents, parcours exceptionnel d'int&eacute;gration). Les articles 21-19 et 21-20 en dispensent totalement six cat&eacute;gories de personnes.</p>

<p>La dispense porte uniquement sur cette dur&eacute;e. Elle laisse intactes toutes les autres conditions&nbsp;: <strong>r&eacute;sider en France</strong> au moment de la signature du d&eacute;cret, avec le centre de ses int&eacute;r&ecirc;ts mat&eacute;riels et familiaux, d&eacute;tenir un titre de s&eacute;jour valide, justifier du <strong>niveau B2</strong>, r&eacute;ussir l'<strong>examen civique</strong>, passer l'<strong>entretien</strong> d'assimilation, disposer de ressources stables, et n'avoir ni condamnation incompatible ni s&eacute;jour irr&eacute;gulier pass&eacute;. Et la naturalisation reste une d&eacute;cision discr&eacute;tionnaire&nbsp;: remplir les conditions ne cr&eacute;e pas un droit.</p>

<h2>Qui est dispens&eacute; du stage&nbsp;: la liste compl&egrave;te</h2>

<table class="article-table">
  <thead><tr><th>Situation</th><th>Fondement</th><th>Ce qu'il faut prouver</th></tr></thead>
  <tbody>
    <tr><td>Ressortissant d'un pays dont le fran&ccedil;ais est langue officielle (ou l'une des langues officielles), et dont le fran&ccedil;ais est la langue maternelle</td><td>Art. 21-20</td><td>Nationalit&eacute; et langue maternelle (scolarit&eacute;, milieu familial)</td></tr>
    <tr><td>Ressortissant d'un tel pays, scolaris&eacute; au moins 5&nbsp;ans dans un &eacute;tablissement enseignant en fran&ccedil;ais</td><td>Art. 21-20</td><td>Nationalit&eacute;, certificats de scolarit&eacute;, dipl&ocirc;mes</td></tr>
    <tr><td>R&eacute;fugi&eacute; statutaire (OFPRA ou CNDA)</td><td>Art. 21-19, 5&deg;</td><td>D&eacute;cision de reconnaissance du statut</td></tr>
    <tr><td>Services militaires accomplis dans une unit&eacute; de l'arm&eacute;e fran&ccedil;aise, dont la L&eacute;gion &eacute;trang&egrave;re</td><td>Art. 21-19, 1&deg;</td><td>&Eacute;tat des services, d&eacute;corations, citations</td></tr>
    <tr><td>Engagement volontaire dans les arm&eacute;es fran&ccedil;aises ou alli&eacute;es en temps de guerre</td><td>Art. 21-19, 1&deg;</td><td>&Eacute;tat des services</td></tr>
    <tr><td>Services exceptionnels rendus &agrave; la France, ou naturalisation pr&eacute;sentant un int&eacute;r&ecirc;t exceptionnel</td><td>Art. 21-19, 3&deg;</td><td>Rapport motiv&eacute; du ministre, avis du Conseil d'&Eacute;tat</td></tr>
  </tbody>
</table>

<p>Deux cas particuliers s'y ajoutent, hors proc&eacute;dure ordinaire&nbsp;: le militaire &eacute;tranger <strong>bless&eacute; en op&eacute;ration</strong> peut devenir fran&ccedil;ais &laquo;&nbsp;par le sang vers&eacute;&nbsp;&raquo;, sur proposition du ministre des Arm&eacute;es (article 21-14-1), et le francophone qui contribue &laquo;&nbsp;par son action &eacute;m&eacute;rite au rayonnement de la France&nbsp;&raquo; peut &ecirc;tre naturalis&eacute; sur proposition du ministre des Affaires &eacute;trang&egrave;res (article 21-21).</p>

<h2>Francophones&nbsp;: dispens&eacute;s du stage, pas du test de fran&ccedil;ais</h2>

<p>C'est le paradoxe de 2026. L'article 21-20 vise &laquo;&nbsp;la personne qui appartient &agrave; l'entit&eacute; culturelle et linguistique fran&ccedil;aise&nbsp;&raquo;&nbsp;: S&eacute;n&eacute;galais, Ivoiriens, Camerounais, Maliens, Guin&eacute;ens, Congolais, B&eacute;ninois, Togolais, Burkinab&egrave;, Nig&eacute;riens, Gabonais, Ha&iuml;tiens, Belges, Suisses, Canadiens ou Luxembourgeois, d&egrave;s lors que le fran&ccedil;ais est leur langue maternelle ou qu'ils ont &eacute;t&eacute; scolaris&eacute;s au moins cinq ans en fran&ccedil;ais. Pour eux, aucune dur&eacute;e de r&eacute;sidence n'est exig&eacute;e. Le Maroc, l'Alg&eacute;rie et la Tunisie ne figurent pas dans cette liste&nbsp;: le fran&ccedil;ais n'y est pas langue officielle.</p>

<p>Mais depuis le 1<sup>er</sup> janvier 2026, cette appartenance linguistique ne dispense plus de <strong>prouver</strong> le niveau. Le d&eacute;cret n&deg;&nbsp;2025-648 a relev&eacute; le niveau exig&eacute; &agrave; B2, et l'arr&ecirc;t&eacute; du 22 d&eacute;cembre 2025 a fix&eacute; la liste ferm&eacute;e des justificatifs&nbsp;: dipl&ocirc;me national du brevet, dipl&ocirc;me d&eacute;livr&eacute; au nom de l'&Eacute;tat fran&ccedil;ais d'un niveau au moins &eacute;gal au niveau 3, certification RNCP, dipl&ocirc;me attestant un niveau B2 (DELF B2, DALF), attestation TCF ou TEF de moins de deux ans. Les <strong>attestations de comparabilit&eacute; ENIC-NARIC</strong> pour un dipl&ocirc;me &eacute;tranger obtenu en fran&ccedil;ais, qui servaient jusque-l&agrave;, ne sont plus accept&eacute;es.</p>

<div class="callout">
  <p><strong>Concr&egrave;tement&nbsp;:</strong> un baccalaur&eacute;at, une licence ou un master obtenus &agrave; Dakar, Abidjan ou Yaound&eacute;, en fran&ccedil;ais, ne prouvent plus le B2. Vous parlez fran&ccedil;ais depuis toujours&nbsp;? Il faudra quand m&ecirc;me passer le TCF, le TEF ou le DELF B2, &agrave; moins d'avoir un dipl&ocirc;me fran&ccedil;ais ou un DELF/DALF d&eacute;j&agrave; en poche.</p>
</div>

<p>La bonne nouvelle, c'est que pour un francophone natif, le B2 est un objectif rapide&nbsp;: l'enjeu n'est pas la langue mais le <strong>format</strong> des &eacute;preuves (compr&eacute;hension orale chronom&eacute;tr&eacute;e, expression &eacute;crite norm&eacute;e, temps de parole). Quelques semaines d'entra&icirc;nement cibl&eacute; suffisent souvent. L'application <a href="https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087" target="_blank">Naturalisation France Facile</a> reproduit les quatre &eacute;preuves du TCF IRN et du DELF B2, note vos productions &eacute;crites et orales selon les grilles officielles, et propose des examens blancs pour choisir la certification qui vous convient&nbsp;: le DELF B2, valable &agrave; vie, ou le TCF, plus rapide &agrave; obtenir mais valable deux ans.</p>

<h2>L&eacute;gion &eacute;trang&egrave;re et militaires&nbsp;: ce que la loi dit, et ce que la L&eacute;gion fait</h2>

<p>L'article 21-19 ne fixe aucune dur&eacute;e de service&nbsp;: il dispense du stage l'&eacute;tranger qui a &laquo;&nbsp;effectivement accompli des services militaires dans une unit&eacute; de l'arm&eacute;e fran&ccedil;aise&nbsp;&raquo;. En pratique, la L&eacute;gion &eacute;trang&egrave;re instruit elle-m&ecirc;me les demandes de ses l&eacute;gionnaires et indique qu'un l&eacute;gionnaire peut demander la nationalit&eacute; fran&ccedil;aise &agrave; partir de cinq ans de service, au vu de sa mani&egrave;re de servir et de sa volont&eacute; d'int&eacute;gration&nbsp;; les dossiers passent par le commandement de la L&eacute;gion, &agrave; Aubagne, qui &eacute;met un avis. Le l&eacute;gionnaire bless&eacute; en op&eacute;ration rel&egrave;ve quant &agrave; lui de la voie &laquo;&nbsp;par le sang vers&eacute;&nbsp;&raquo;, sans condition de dur&eacute;e.</p>

<p>Comme pour les autres dispens&eacute;s, le B2, l'examen civique et l'entretien s'appliquent. Les pi&egrave;ces sp&eacute;cifiques sont l'&eacute;tat des services, les d&eacute;corations et les citations.</p>

<h2>Services exceptionnels et int&eacute;r&ecirc;t exceptionnel&nbsp;: une voie rare</h2>

<p>Le 3&deg; de l'article 21-19 vise deux hypoth&egrave;ses&nbsp;: les services exceptionnels rendus &agrave; la France, et la naturalisation qui pr&eacute;sente pour la France un int&eacute;r&ecirc;t exceptionnel. Dans les deux cas, le d&eacute;cret ne peut &ecirc;tre pris qu'apr&egrave;s <strong>avis du Conseil d'&Eacute;tat</strong>, sur rapport motiv&eacute; du ministre comp&eacute;tent. Ce sont les naturalisations de sportifs, de chercheurs ou d'artistes dont parle la presse&nbsp;; elles se comptent en dizaines par an et ne se demandent pas au guichet&nbsp;: elles se proposent. Si votre profil rel&egrave;ve plut&ocirc;t de &laquo;&nbsp;services importants rendus par vos capacit&eacute;s et talents&nbsp;&raquo;, c'est la r&eacute;duction du stage &agrave; deux ans (article 21-18, 2&deg;) qui s'applique, dans la proc&eacute;dure ordinaire.</p>

<h2>Ce que la dispense ne vous &eacute;pargne jamais</h2>

<ul>
  <li><strong>Le B2</strong>, &agrave; l'&eacute;crit et &agrave; l'oral&nbsp;: seuls le r&eacute;fugi&eacute; ou l'apatride de plus de 70&nbsp;ans r&eacute;sidant en France depuis 15&nbsp;ans, et les personnes dont l'&eacute;tat de sant&eacute; rend l'&eacute;valuation impossible, en sont dispens&eacute;s.</li>
  <li><strong>L'examen civique</strong>&nbsp;: 40&nbsp;questions, 32&nbsp;bonnes r&eacute;ponses, dans un centre agr&eacute;&eacute;. Aucune dispense li&eacute;e &agrave; la nationalit&eacute;, &agrave; la langue maternelle ou au statut&nbsp;; seule une impossibilit&eacute; m&eacute;dicale y &eacute;chappe.</li>
  <li><strong>L'entretien d'assimilation</strong>&nbsp;: adh&eacute;sion aux principes de la R&eacute;publique, connaissance des droits et devoirs, coh&eacute;rence du parcours.</li>
  <li><strong>Les ressources stables</strong>, appr&eacute;ci&eacute;es sur cinq ans, hors prestations sociales, et la <strong>r&eacute;sidence effective</strong> en France&nbsp;: un francophone qui vient d'arriver et travaille &agrave; distance pour un employeur &eacute;tranger n'a pas le centre de ses int&eacute;r&ecirc;ts en France.</li>
  <li><strong>La moralit&eacute;</strong>&nbsp;: une peine ferme de 6&nbsp;mois ou plus, une atteinte aux int&eacute;r&ecirc;ts de la Nation ou un s&eacute;jour irr&eacute;gulier pass&eacute; conduisent au rejet.</li>
</ul>

<h2>Comment pr&eacute;parer une demande sans stage</h2>

<ol>
  <li><strong>V&eacute;rifiez le fondement</strong> et r&eacute;unissez sa preuve&nbsp;: scolarit&eacute; en fran&ccedil;ais, statut, &eacute;tat des services.</li>
  <li><strong>V&eacute;rifiez votre justificatif de langue</strong>&nbsp;: dipl&ocirc;me fran&ccedil;ais, DELF ou DALF&nbsp;; sinon, inscrivez-vous au TCF ou au TEF apr&egrave;s quelques examens blancs.</li>
  <li><strong>Passez l'examen civique</strong>&nbsp;; l'attestation n'expire pas.</li>
  <li><strong>Attendez une situation professionnelle stable</strong>&nbsp;: la dispense de stage ne compense pas un CDD de trois mois.</li>
  <li><strong>D&eacute;posez en ligne</strong> sur l'ANEF, avec le timbre fiscal de 255&nbsp;&euro;, puis <a href="/blog/sentrainer-entretien-naturalisation.html">pr&eacute;parez l'entretien</a>.</li>
</ol>
""",
    "faq": [
        ("Que signifie « naturalisation sans condition de stage » ?",
         "Que la durée minimale de résidence en France (5 ans en règle générale, 2 ans dans certains cas) n'est pas exigée. Toutes les autres conditions de la naturalisation s'appliquent : résidence en France au moment du décret, titre de séjour, niveau B2, examen civique, entretien, ressources, moralité."),
        ("Qui est dispensé de la condition de stage ?",
         "Les ressortissants d'un pays dont le français est langue officielle, si le français est leur langue maternelle ou s'ils ont été scolarisés au moins 5 ans en français (article 21-20) ; les réfugiés statutaires ; les personnes ayant accompli des services militaires dans l'armée française ou un engagement volontaire en temps de guerre ; et celles ayant rendu des services exceptionnels à la France (article 21-19)."),
        ("Un francophone doit-il quand même passer le TCF ou le DELF ?",
         "Oui, sauf s'il possède un diplôme français (brevet, CAP, bac, diplôme du supérieur délivré au nom de l'État), un DELF B2 ou un DALF. Depuis le 1er janvier 2026, un diplôme étranger obtenu en français ne prouve plus le niveau : les attestations de comparabilité ENIC-NARIC ne sont plus acceptées."),
        ("Les Marocains, Algériens et Tunisiens bénéficient-ils de la dispense francophone ?",
         "Non : l'article 21-20 vise les ressortissants des États dont le français est langue officielle ou l'une des langues officielles, ce qui n'est pas le cas du Maroc, de l'Algérie ni de la Tunisie. Ils relèvent de la règle générale des 5 ans, sauf autre cause de réduction ou de dispense : études supérieures en France, statut de réfugié, ou réintégration pour les personnes nées en Algérie avant 1962."),
        ("Après combien d'années un légionnaire peut-il demander la nationalité ?",
         "La loi ne fixe pas de durée : l'article 21-19 dispense du stage tout étranger ayant accompli des services militaires dans une unité de l'armée française. La Légion étrangère indique de son côté qu'un légionnaire peut demander la nationalité à partir de cinq ans de service, selon sa manière de servir ; un légionnaire blessé en opération peut l'obtenir sans condition de durée, « par le sang versé »."),
        ("Sans condition de stage, la naturalisation est-elle plus rapide ?",
         "Le dépôt peut se faire plus tôt, mais l'instruction suit le même délai légal : 18 mois à compter du récépissé (12 mois après 10 ans de résidence), prolongeables une fois de 3 mois. Le calendrier réel dépend surtout de votre préparation au B2 et à l'examen civique, et de la stabilité de votre emploi."),
        ("La dispense de stage dispense-t-elle de l'examen civique ?",
         "Non. L'examen civique s'impose à toute demande de naturalisation par décret depuis le 1er janvier 2026, quel que soit le fondement de la demande. Seule une impossibilité médicale attestée y échappe."),
    ],
    "links": [
        ("/blog/naturalisation-refugie-2026.html", "Naturalisation des r&eacute;fugi&eacute;s&nbsp;: ce qui est vraiment exig&eacute;"),
        ("/blog/naturalisation-apres-etudes-en-france.html", "Naturalisation apr&egrave;s des &eacute;tudes en France&nbsp;: le stage r&eacute;duit &agrave; 2&nbsp;ans"),
        ("/blog/reintegration-nationalite-francaise-2026.html", "R&eacute;int&eacute;gration dans la nationalit&eacute; fran&ccedil;aise&nbsp;: d&eacute;cret ou d&eacute;claration"),
        ("/blog/tcf-irn-ou-delf-b2-lequel-choisir.html", "TCF IRN ou DELF B2&nbsp;: lequel choisir"),
        ("/blog/atteindre-niveau-b2-naturalisation.html", "Atteindre le niveau B2&nbsp;: plan de travail"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret&nbsp;: cas sans dur&eacute;e minimale de r&eacute;sidence (F2213)"),
        ("https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070721/LEGISCTA000006149926/", "Code civil &mdash; Articles 21-14-1 &agrave; 21-25-1 (naturalisation, dispenses de stage)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F11926", "Service-public.gouv.fr &mdash; Justifier de son niveau de fran&ccedil;ais (F11926)"),
        ("https://ca.diplomatie.gouv.fr/fr/le-niveau-b2-en-francais-devient-obligatoire-pour-les-demandes-dacquisition-de-la-nationalite", "Consulats de France au Canada &mdash; Niveau B2 et fin des attestations ENIC-NARIC au 1er janvier 2026"),
        ("https://www.legion-recrute.com/fr/questions-frequentes", "L&eacute;gion &eacute;trang&egrave;re &mdash; Questions fr&eacute;quentes (nationalit&eacute; fran&ccedil;aise)"),
    ],
    "cta": "Passer le B2 avec les examens blancs de l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"naturalisation-apres-65-ans": {
    "title": "Naturalisation après 65 ans : test de langue obligatoire ?",
    "h1": "Naturalisation apr&egrave;s 65&nbsp;ans&nbsp;: faut-il passer le test de langue et l'examen civique&nbsp;?",
    "desc": "Par décret, aucune dispense d'âge : B2 et examen civique s'appliquent. Mais avec un enfant ou petit-enfant français et 25 ans en France, une déclaration sans test existe.",
    "og": "Naturalisation apr&egrave;s 65&nbsp;ans&nbsp;: test de langue, ou d&eacute;claration sans test&nbsp;?",
    "tag": "Conditions",
    "og_img": "default.png",
    "date": "2026-09-17",
    "date_fr": "17 septembre 2026",
    "lede": "Jusqu'en 2020, les candidats de plus de 60&nbsp;ans &eacute;taient dispens&eacute;s de justifier de leur niveau de fran&ccedil;ais. Ce n'est plus le cas, et depuis 2026 le niveau exig&eacute; est le B2, avec en plus un examen civique. Pour beaucoup de retrait&eacute;s, la question n'est donc plus &laquo;&nbsp;comment se pr&eacute;parer&nbsp;&raquo; mais &laquo;&nbsp;existe-t-il une autre voie&nbsp;&raquo;. Il en existe une, m&eacute;connue et sans aucun test, r&eacute;serv&eacute;e aux parents et grands-parents de Fran&ccedil;ais install&eacute;s en France depuis 25&nbsp;ans. Voici les deux chemins, et comment choisir.",
    "body": """
<h2>Par d&eacute;cret&nbsp;: aucune dispense li&eacute;e &agrave; l'&acirc;ge, ni pour la langue ni pour l'examen civique</h2>

<p>La naturalisation par d&eacute;cret s'obtient &agrave; tout &acirc;ge, sans limite sup&eacute;rieure. Mais ses conditions ne s'assouplissent pas avec les ann&eacute;es. Le d&eacute;cret du 30 d&eacute;cembre 2019 a supprim&eacute;, &agrave; compter du 1<sup>er</sup> avril 2020, la dispense de justificatif de langue dont b&eacute;n&eacute;ficiaient les plus de 60&nbsp;ans. Depuis le 1<sup>er</sup> janvier 2026, le niveau exig&eacute; est le <strong>B2</strong>, &agrave; l'&eacute;crit comme &agrave; l'oral, et l'<strong>examen civique</strong> (40&nbsp;questions, 32&nbsp;bonnes r&eacute;ponses) s'ajoute &agrave; l'entretien.</p>

<p>Les seules dispenses pr&eacute;vues sont &eacute;troites&nbsp;:</p>

<ul>
  <li><strong>Langue</strong>&nbsp;: le r&eacute;fugi&eacute; politique ou l'apatride de plus de 70&nbsp;ans r&eacute;sidant r&eacute;guli&egrave;rement en France depuis au moins 15&nbsp;ans (article 21-24-1), et les personnes dont un handicap ou l'&eacute;tat de sant&eacute; rend l'&eacute;valuation impossible, sur certificat m&eacute;dical.</li>
  <li><strong>Examen civique</strong>&nbsp;: uniquement l'impossibilit&eacute; m&eacute;dicale attest&eacute;e. Des am&eacute;nagements d'&eacute;preuve (temps suppl&eacute;mentaire, assistance) sont possibles sur certificat m&eacute;dical pr&eacute;cisant les am&eacute;nagements n&eacute;cessaires.</li>
</ul>

<div class="callout">
  <p><strong>Le certificat m&eacute;dical n'est pas un certificat de complaisance&nbsp;:</strong> il doit attester que l'&eacute;tat de sant&eacute; rend toute &eacute;valuation linguistique impossible, et le service instructeur ou le minist&egrave;re peuvent demander une nouvelle expertise m&eacute;dicale. L'&acirc;ge seul n'est pas un motif.</p>
</div>

<h2>Retrait&eacute; et naturalisation&nbsp;: les ressources ne sont pas un obstacle</h2>

<p>La condition d'insertion professionnelle inqui&egrave;te souvent les retrait&eacute;s, &agrave; tort. L'administration appr&eacute;cie les ressources &laquo;&nbsp;selon votre condition&nbsp;&raquo;&nbsp;: une <strong>pension de retraite</strong> stable et suffisante est une ressource au sens de la naturalisation, et service-public pr&eacute;voit les pi&egrave;ces &agrave; fournir dans ce cas (titre de pension, dernier bordereau de versement, avis d'imposition des trois derni&egrave;res ann&eacute;es). Les crit&egrave;res de CDI ou de continuit&eacute; de CDD de la circulaire du 2 mai 2025 visent les salari&eacute;s, pas les retrait&eacute;s.</p>

<p>Deux points restent sensibles&nbsp;: des revenus <strong>majoritairement compos&eacute;s de prestations sociales</strong> sont un motif d'ajournement, sauf si l'insuffisance r&eacute;sulte d'une maladie ou d'un handicap&nbsp;; et des <strong>revenus provenant majoritairement de l'&eacute;tranger</strong> (pension &eacute;trang&egrave;re, biens au pays) peuvent conduire la pr&eacute;fecture &agrave; consid&eacute;rer que le centre de vos int&eacute;r&ecirc;ts n'est pas en France.</p>

<h2>La voie sans test&nbsp;: la d&eacute;claration de l'ascendant d'un Fran&ccedil;ais</h2>

<p>Cr&eacute;&eacute;e par la loi du 7 mars 2016, la d&eacute;claration de nationalit&eacute; de l'article 21-13-1 du Code civil s'adresse &agrave; la personne qui remplit, &agrave; la date de la d&eacute;claration, <strong>trois conditions cumulatives</strong>&nbsp;:</p>

<ol>
  <li>&ecirc;tre &acirc;g&eacute;e de <strong>65&nbsp;ans ou plus</strong>&nbsp;;</li>
  <li>r&eacute;sider en France <strong>de mani&egrave;re r&eacute;guli&egrave;re et habituelle depuis au moins 25&nbsp;ans</strong>&nbsp;;</li>
  <li>&ecirc;tre l'<strong>ascendant direct</strong> d'un ressortissant fran&ccedil;ais&nbsp;: parent, grand-parent ou arri&egrave;re-grand-parent d'un enfant, petit-enfant ou arri&egrave;re-petit-enfant fran&ccedil;ais.</li>
</ol>

<p>Cette proc&eacute;dure est une <strong>d&eacute;claration</strong>, pas une naturalisation&nbsp;: si les conditions sont remplies, l'enregistrement est de droit, sauf opposition du Gouvernement pour indignit&eacute; ou d&eacute;faut d'assimilation. Et surtout, elle &eacute;chappe aux deux &eacute;preuves&nbsp;: <strong>ni test de langue, ni examen civique</strong>. Service-public le dit express&eacute;ment&nbsp;: l'entretien &laquo;&nbsp;ne porte pas sur le niveau de connaissance de la langue fran&ccedil;aise&nbsp;&raquo;, et l'examen civique ne concerne que les proc&eacute;dures par d&eacute;cret.</p>

<table class="article-table">
  <thead><tr><th>Crit&egrave;re</th><th>Naturalisation par d&eacute;cret</th><th>D&eacute;claration &laquo;&nbsp;ascendant de Fran&ccedil;ais&nbsp;&raquo;</th></tr></thead>
  <tbody>
    <tr><td>&Acirc;ge</td><td>18&nbsp;ans et plus</td><td>65&nbsp;ans et plus</td></tr>
    <tr><td>R&eacute;sidence en France</td><td>5&nbsp;ans (r&egrave;gle g&eacute;n&eacute;rale)</td><td>25&nbsp;ans, r&eacute;guli&egrave;re et habituelle</td></tr>
    <tr><td>Lien familial</td><td>Aucun exig&eacute;</td><td>Enfant, petit-enfant ou arri&egrave;re-petit-enfant fran&ccedil;ais</td></tr>
    <tr><td>Test de langue B2</td><td>Oui (dispenses m&eacute;dicales et r&eacute;fugi&eacute;s de plus de 70&nbsp;ans)</td><td><em>Non</em></td></tr>
    <tr><td>Examen civique</td><td>Oui</td><td><em>Non</em></td></tr>
    <tr><td>Entretien</td><td>Oui, assimilation</td><td>Oui, indignit&eacute; et assimilation, hors langue</td></tr>
    <tr><td>Ressources</td><td>Stables et suffisantes</td><td>Pas de condition de ressources</td></tr>
    <tr><td>Nature de la d&eacute;cision</td><td>Discr&eacute;tionnaire (faveur)</td><td>Enregistrement de droit, sauf opposition</td></tr>
    <tr><td>Timbre fiscal</td><td>255&nbsp;&euro;</td><td>255&nbsp;&euro;</td></tr>
    <tr><td>D&eacute;lai</td><td>18&nbsp;mois (12&nbsp;mois apr&egrave;s 10&nbsp;ans de r&eacute;sidence)</td><td>1&nbsp;an pour refuser l'enregistrement (2&nbsp;ans en cas d'opposition)</td></tr>
  </tbody>
</table>

<h3>Le dossier de la d&eacute;claration</h3>

<p>Le formulaire est le <strong>cerfa n&deg;&nbsp;15561</strong>, en deux exemplaires, avec un timbre fiscal de 255&nbsp;&euro; (127,50&nbsp;&euro; en Guyane). Les pi&egrave;ces essentielles&nbsp;: votre acte de naissance, votre titre de s&eacute;jour, l'acte de naissance de moins de 3&nbsp;mois de votre enfant (ou de votre petit-enfant, avec l'acte de naissance du parent interm&eacute;diaire) &eacute;tablissant la filiation, la preuve de la nationalit&eacute; fran&ccedil;aise de ce descendant (acte de naissance mentionnant la nationalit&eacute;, certificat de nationalit&eacute; fran&ccedil;aise, d&eacute;cret ou d&eacute;claration), et surtout des <strong>justificatifs couvrant 25&nbsp;ans de r&eacute;sidence r&eacute;guli&egrave;re</strong>&nbsp;: relev&eacute; de carri&egrave;re, avis d'imposition, anciens titres de s&eacute;jour. Le dossier se d&eacute;pose &agrave; la plateforme de naturalisation de votre domicile, au guichet ou par courrier recommand&eacute; selon les plateformes.</p>

<p>Vous &ecirc;tes ensuite convoqu&eacute; &agrave; un entretien, &agrave; l'issue duquel un r&eacute;c&eacute;piss&eacute; est remis. Le minist&egrave;re a un an pour refuser l'enregistrement (deux ans si une proc&eacute;dure d'opposition est engag&eacute;e)&nbsp;; la nationalit&eacute; prend effet &agrave; la date de souscription de la d&eacute;claration.</p>

<h2>Fr&egrave;re ou s&oelig;ur de Fran&ccedil;ais&nbsp;: l'autre d&eacute;claration sans test</h2>

<p>Pour &ecirc;tre complet&nbsp;: l'article 21-13-2 ouvre une d&eacute;claration similaire au fr&egrave;re ou &agrave; la s&oelig;ur d'un Fran&ccedil;ais n&eacute; en France, &agrave; condition de r&eacute;sider en France depuis l'&acirc;ge de 6&nbsp;ans, d'y avoir suivi sa scolarit&eacute; obligatoire et d'&ecirc;tre en s&eacute;jour r&eacute;gulier. Elle concerne rarement les seniors, mais elle rel&egrave;ve de la m&ecirc;me logique&nbsp;: une d&eacute;claration, sans test de langue ni examen civique.</p>

<h2>Comment choisir entre les deux voies</h2>

<ul>
  <li><strong>Vous avez 65&nbsp;ans, 25&nbsp;ans de r&eacute;sidence r&eacute;guli&egrave;re et un descendant fran&ccedil;ais&nbsp;:</strong> la d&eacute;claration est la voie naturelle. Pas de test, pas d'examen, une d&eacute;cision de droit.</li>
  <li><strong>Il vous manque l'une des trois conditions</strong> (moins de 25&nbsp;ans en France, pas de descendant fran&ccedil;ais, moins de 65&nbsp;ans)&nbsp;: seule la naturalisation par d&eacute;cret est ouverte, avec le B2 et l'examen civique.</li>
  <li><strong>Vous &ecirc;tes &agrave; quelques ann&eacute;es des 25&nbsp;ans&nbsp;:</strong> comparez le temps de pr&eacute;paration du B2 (souvent 6 &agrave; 18&nbsp;mois selon le niveau de d&eacute;part) au temps d'attente&nbsp;; il est parfois plus s&ucirc;r d'attendre la d&eacute;claration.</li>
</ul>

<h2>Pr&eacute;parer le B2 et l'examen civique &agrave; 65&nbsp;ans&nbsp;: r&eacute;aliste&nbsp;?</h2>

<p>Oui, &agrave; condition de s'y prendre m&eacute;thodiquement. Le niveau B2 exige de comprendre un journal radio ou un article de presse, d'&eacute;crire une lettre argument&eacute;e et de tenir une conversation sur un sujet d'actualit&eacute;. Pour quelqu'un qui vit en France depuis vingt ans, l'oral est souvent acquis&nbsp;; c'est l'&eacute;crit et le format des &eacute;preuves qui demandent du travail. Le DELF B2, valable &agrave; vie, est un bon choix quand on n'est pas press&eacute;&nbsp;; le TCF IRN, valable deux ans, quand le dossier est pr&ecirc;t.</p>

<p>L'application <a href="https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087" target="_blank">Naturalisation France Facile</a> permet d'avancer &agrave; son rythme&nbsp;: des exercices de compr&eacute;hension orale avec transcription pour r&eacute;&eacute;couter et lire, des sujets d'expression &eacute;crite corrig&eacute;s avec des r&eacute;ponses mod&egrave;les, des examens blancs pour se situer, et, pour l'examen civique, 258&nbsp;questions et 100&nbsp;mises en situation, chacune expliqu&eacute;e. Le simulateur d'entretien aide enfin &agrave; formuler &agrave; l'oral son parcours, ses attaches en France et ses motivations, des questions que l'agent de pr&eacute;fecture posera quelle que soit la voie choisie.</p>
""",
    "faq": [
        ("Faut-il passer le test de français pour être naturalisé après 60 ou 65 ans ?",
         "Pour une naturalisation par décret, oui : depuis le 1er avril 2020, il n'existe plus de dispense liée à l'âge, et le niveau exigé est le B2 depuis le 1er janvier 2026. Les seules dispenses concernent le réfugié ou l'apatride de plus de 70 ans résidant en France depuis 15 ans, et les personnes dont l'état de santé rend l'évaluation impossible, sur certificat médical."),
        ("Existe-t-il une naturalisation sans test après 65 ans ?",
         "Pas une naturalisation, mais une déclaration de nationalité (article 21-13-1 du Code civil) : à partir de 65 ans, avec 25 ans de résidence régulière et habituelle en France et un enfant, petit-enfant ou arrière-petit-enfant français, vous pouvez devenir français par déclaration, sans test de langue ni examen civique."),
        ("Un retraité sans emploi peut-il être naturalisé ?",
         "Oui. Une pension de retraite stable et suffisante répond à la condition de ressources, appréciée selon votre situation. Les exigences de CDI ou de CDD continus visent les salariés. En revanche, des revenus composés majoritairement de prestations sociales ou provenant majoritairement de l'étranger peuvent être opposés."),
        ("L'examen civique est-il obligatoire à 65 ans ?",
         "Pour une demande par décret, oui, quel que soit l'âge : seule une impossibilité médicale attestée permet d'en être dispensé, et des aménagements sont possibles. Pour la déclaration de l'ascendant d'un Français, non : l'examen civique ne concerne que les procédures par décret."),
        ("Quels documents prouvent 25 ans de résidence en France ?",
         "Tous documents couvrant la période de façon continue : relevé de carrière de la sécurité sociale ou relevé de situation individuelle, avis d'imposition, anciens titres de séjour, quittances. Vous pouvez combiner des documents différents pour couvrir les 25 ans."),
        ("Combien coûte la déclaration de l'ascendant d'un Français et combien de temps prend-elle ?",
         "Un timbre fiscal de 255 € (127,50 € en Guyane), comme pour la naturalisation. Le ministère dispose d'un an à compter du récépissé remis après l'entretien pour refuser l'enregistrement, ou de deux ans si une procédure d'opposition est engagée. La nationalité prend effet à la date de souscription."),
        ("Mon petit-enfant est français mais pas mon enfant : la déclaration est-elle possible ?",
         "Oui : l'article 21-13-1 vise l'ascendant direct d'un ressortissant français, ce qui inclut le grand-parent. Il faudra fournir l'acte de naissance du petit-enfant et celui de son parent (votre enfant) pour établir la chaîne de filiation, ainsi que la preuve de la nationalité française du petit-enfant."),
        ("Peut-on obtenir un aménagement du test de langue pour raison de santé ?",
         "Oui. Sur certificat médical précisant les aménagements nécessaires, vous pouvez bénéficier d'aménagements d'épreuve pour le test de langue comme pour l'examen civique. Si l'état de santé rend toute évaluation impossible, une dispense complète est possible, sur certificat médical, l'administration pouvant demander une nouvelle expertise."),
    ],
    "links": [
        ("/blog/atteindre-niveau-b2-naturalisation.html", "Atteindre le niveau B2&nbsp;: combien de mois pr&eacute;voir"),
        ("/blog/tcf-irn-ou-delf-b2-lequel-choisir.html", "TCF IRN ou DELF B2&nbsp;: lequel choisir"),
        ("/blog/ressources-revenus-naturalisation.html", "Ressources et naturalisation&nbsp;: ce que la pr&eacute;fecture regarde"),
        ("/blog/reintegration-nationalite-francaise-2026.html", "R&eacute;int&eacute;gration dans la nationalit&eacute; fran&ccedil;aise&nbsp;: d&eacute;cret ou d&eacute;claration"),
        ("/blog/documents-naturalisation.html", "La liste compl&egrave;te des pi&egrave;ces du dossier"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F33430", "Service-public.gouv.fr &mdash; D&eacute;claration de nationalit&eacute; de l'ascendant d'un Fran&ccedil;ais (F33430)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F11926", "Service-public.gouv.fr &mdash; Niveau de fran&ccedil;ais exig&eacute;, am&eacute;nagements et dispenses (F11926)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F39426", "Service-public.gouv.fr &mdash; Examen civique&nbsp;: proc&eacute;dures concern&eacute;es (F39426)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F34746", "Service-public.gouv.fr &mdash; Justificatifs de revenus, cas du retrait&eacute; (F34746)"),
        ("https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031713003", "Code civil &mdash; Article 21-13-1"),
        ("https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000039696962", "L&eacute;gifrance &mdash; D&eacute;cret n&deg;&nbsp;2019-1507 du 30 d&eacute;cembre 2019 (fin de la dispense de langue apr&egrave;s 60&nbsp;ans)"),
    ],
    "cta": "Pr&eacute;parer le B2 &agrave; mon rythme avec l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"naturalisation-rapide": {
    "title": "Naturalisation rapide : comment devenir français plus vite",
    "h1": "Naturalisation rapide&nbsp;: comment devenir fran&ccedil;ais plus vite, sans y laisser des mois",
    "desc": "Aucune procédure accélérée n'existe. Mais entre un décret en un an et trois ans d'attente, tout se joue avant le dépôt : bonne voie, B2, examen civique, dossier complet.",
    "og": "Naturalisation rapide&nbsp;: les 5 leviers qui font gagner des mois",
    "tag": "M&eacute;thode",
    "og_img": "suivi-relance.png",
    "date": "2026-09-17",
    "date_fr": "17 septembre 2026",
    "lede": "Tapez &laquo;&nbsp;naturalisation rapide&nbsp;&raquo; et vous trouverez des services payants qui promettent d'acc&eacute;l&eacute;rer votre dossier. Aucun ne le peut&nbsp;: la proc&eacute;dure est gratuite hors timbre fiscal, et personne n'obtient de d&eacute;cision plus vite en payant. Ce qui s&eacute;pare un candidat fran&ccedil;ais en quatorze mois d'un candidat qui attend trois ans, ce n'est pas la chance ni la pr&eacute;fecture. C'est la voie choisie, l'ordre dans lequel il a pr&eacute;par&eacute; le B2, l'examen civique et ses pi&egrave;ces, et un dossier accept&eacute; du premier coup. Voici les cinq leviers qui font r&eacute;ellement gagner des mois, et les fausses bonnes id&eacute;es qui en font perdre.",
    "body": """
<h2>Ce qui est incompressible, et ce qui d&eacute;pend de vous</h2>

<p>La loi fixe un d&eacute;lai maximal de r&eacute;ponse&nbsp;: <strong>18&nbsp;mois</strong> &agrave; compter du r&eacute;c&eacute;piss&eacute; de dossier complet, ramen&eacute;s &agrave; <strong>12&nbsp;mois</strong> si vous r&eacute;sidez habituellement en France depuis au moins 10&nbsp;ans, prolongeables une seule fois de 3&nbsp;mois par d&eacute;cision motiv&eacute;e (article 21-25-1 du Code civil). Dans les faits, il s'&eacute;coule le plus souvent <a href="/blog/delais-naturalisation-2026.html">12 &agrave; 18&nbsp;mois</a> entre le r&eacute;c&eacute;piss&eacute; et la publication du d&eacute;cret, avec de fortes variations <a href="/blog/delais-naturalisation-par-prefecture.html">selon la plateforme</a> qui instruit votre dossier.</p>

<p>Ce chrono-l&agrave;, vous ne le contr&ocirc;lez pas. Mais il ne d&eacute;marre qu'au r&eacute;c&eacute;piss&eacute;, et le r&eacute;c&eacute;piss&eacute; n'est d&eacute;livr&eacute; que lorsque le dossier est <em>complet</em>. Tout ce qui pr&eacute;c&egrave;de, le niveau de langue, l'examen civique, les pi&egrave;ces, le choix de la proc&eacute;dure, est du temps que vous pilotez, et c'est l&agrave; que se creusent les &eacute;carts.</p>

<table class="article-table">
  <thead><tr><th>Phase</th><th>Qui tient le chrono</th><th>Votre marge</th></tr></thead>
  <tbody>
    <tr><td>Choix de la voie, B2, examen civique, pi&egrave;ces</td><td><em>Vous</em></td><td>De 2&nbsp;mois &agrave; plus d'un an selon la m&eacute;thode</td></tr>
    <tr><td>D&eacute;p&ocirc;t et v&eacute;rification de compl&eacute;tude</td><td>Vous et la plateforme</td><td>Un dossier complet &eacute;vite des allers-retours de plusieurs semaines chacun</td></tr>
    <tr><td>Entretien et avis du pr&eacute;fet</td><td>La plateforme</td><td>Un entretien pr&eacute;par&eacute; &eacute;vite l'ajournement, qui co&ucirc;te un &agrave; deux ans</td></tr>
    <tr><td>Instruction au minist&egrave;re, d&eacute;cret</td><td>L'administration</td><td>R&eacute;pondre vite aux demandes, relancer au bon moment</td></tr>
  </tbody>
</table>

<div class="callout">
  <p><strong>La r&egrave;gle d'or&nbsp;:</strong> un mois gagn&eacute; avant le d&eacute;p&ocirc;t vaut un mois gagn&eacute; sur le d&eacute;cret. Un mois perdu en cours d'instruction (pi&egrave;ce manquante, changement non signal&eacute;, ajournement) en co&ucirc;te souvent plusieurs.</p>
</div>

<h2>Levier 1&nbsp;: choisir la voie la plus courte pour votre situation</h2>

<p>La naturalisation par d&eacute;cret n'est pas la seule porte, et rarement la plus rapide. Avant de constituer un dossier, v&eacute;rifiez si une autre proc&eacute;dure vous est ouverte&nbsp;:</p>

<ul>
  <li><strong>Mari&eacute;(e) &agrave; un(e) Fran&ccedil;ais(e) depuis 4&nbsp;ans</strong> (5&nbsp;ans sans r&eacute;sidence continue en France)&nbsp;: la <a href="/blog/naturalisation-par-mariage-2026.html">d&eacute;claration par mariage</a>, enregistr&eacute;e dans un d&eacute;lai d'un an apr&egrave;s l'entretien, sans examen civique.</li>
  <li><strong>65&nbsp;ans, 25&nbsp;ans en France, un enfant ou petit-enfant fran&ccedil;ais</strong>&nbsp;: la <a href="/blog/naturalisation-apres-65-ans.html">d&eacute;claration de l'ascendant d'un Fran&ccedil;ais</a>, un an &eacute;galement, sans test de langue ni examen civique.</li>
  <li><strong>Vous avez d&eacute;j&agrave; &eacute;t&eacute; fran&ccedil;ais</strong>&nbsp;: la <a href="/blog/reintegration-nationalite-francaise-2026.html">r&eacute;int&eacute;gration</a>, sans dur&eacute;e minimale de r&eacute;sidence par d&eacute;cret, et en six mois par d&eacute;claration dans certains cas de perte.</li>
  <li><strong>Dipl&ocirc;me du sup&eacute;rieur fran&ccedil;ais apr&egrave;s deux ans d'&eacute;tudes</strong>&nbsp;: la r&eacute;sidence exig&eacute;e tombe &agrave; <a href="/blog/naturalisation-apres-etudes-en-france.html">2&nbsp;ans</a> au lieu de 5.</li>
  <li><strong>R&eacute;fugi&eacute;, ressortissant d'un pays francophone, ancien militaire</strong>&nbsp;: <a href="/blog/naturalisation-sans-condition-de-stage.html">aucune dur&eacute;e de r&eacute;sidence</a> n'est exig&eacute;e.</li>
  <li><strong>10&nbsp;ans de r&eacute;sidence habituelle</strong>&nbsp;: vous restez dans la proc&eacute;dure ordinaire, mais le d&eacute;lai l&eacute;gal de r&eacute;ponse passe de 18 &agrave; 12&nbsp;mois. Si vous &ecirc;tes &agrave; quelques mois du seuil, attendez-le avant de d&eacute;poser.</li>
</ul>

<p>Les <a href="/blog/conditions-naturalisation-francaise.html">sept conditions de la naturalisation</a> restent la base&nbsp;: la voie la plus rapide est d'abord celle dont vous remplissez d&eacute;j&agrave; toutes les conditions.</p>

<h2>Levier 2&nbsp;: lancer le B2 et l'examen civique en parall&egrave;le, et tout de suite</h2>

<p>C'est le poste o&ugrave; les candidats perdent le plus de temps, parce qu'ils encha&icirc;nent les &eacute;tapes au lieu de les mener de front. Depuis le 1<sup>er</sup> janvier 2026, une demande par d&eacute;cret exige un justificatif de niveau B2 et une attestation de r&eacute;ussite &agrave; l'examen civique. Les deux ont des calendriers diff&eacute;rents&nbsp;:</p>

<table class="article-table">
  <thead><tr><th>&Eacute;preuve</th><th>Trouver une date</th><th>R&eacute;sultats</th><th>Validit&eacute;</th></tr></thead>
  <tbody>
    <tr><td>TCF IRN</td><td>Sessions fr&eacute;quentes, souvent sous 1 &agrave; 3&nbsp;mois</td><td>Environ 4&nbsp;semaines</td><td>2&nbsp;ans</td></tr>
    <tr><td>DELF B2</td><td>2 &agrave; 6 sessions par an selon les centres</td><td>2 &agrave; 3&nbsp;mois</td><td>&Agrave; vie</td></tr>
    <tr><td>Examen civique</td><td>Sessions r&eacute;guli&egrave;res en centre agr&eacute;&eacute;</td><td>Rapides</td><td>Sans limite</td></tr>
  </tbody>
</table>

<p>L'ordre le plus efficace&nbsp;: inscrivez-vous &agrave; l'<strong>examen civique d&egrave;s maintenant</strong>, puisque l'attestation n'expire pas, et r&eacute;servez le <strong>TCF IRN</strong> plut&ocirc;t que le DELF si vous &ecirc;tes press&eacute;&nbsp;: m&ecirc;me niveau exig&eacute;, r&eacute;sultats en quelques semaines au lieu de plusieurs mois. Le DELF garde son int&eacute;r&ecirc;t si vous n'&ecirc;tes pas &agrave; trois mois pr&egrave;s, parce qu'il est valable &agrave; vie. Notre comparatif <a href="/blog/tcf-irn-ou-delf-b2-lequel-choisir.html">TCF IRN ou DELF B2</a> d&eacute;taille les deux formats.</p>

<p>Le vrai risque de temps, c'est l'&eacute;chec&nbsp;: un TCF rat&eacute;, c'est 200 &agrave; 300&nbsp;&euro; et deux &agrave; trois mois de plus pour retrouver une date et un r&eacute;sultat. D'o&ugrave; l'int&eacute;r&ecirc;t de <strong>savoir si vous &ecirc;tes pr&ecirc;t avant de r&eacute;server</strong>. L'application <a href="https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087" target="_blank">Naturalisation France Facile</a> sert exactement &agrave; cela&nbsp;: plus de 750&nbsp;exercices calibr&eacute;s B2 sur les quatre &eacute;preuves du TCF IRN et du DELF B2, la correction de vos productions &eacute;crites et orales selon les grilles officielles, et des examens blancs complets qui vous disent o&ugrave; vous en &ecirc;tes. Pour l'examen civique, ses 258&nbsp;questions sur les cinq th&egrave;mes officiels et ses 100&nbsp;mises en situation, chacune expliqu&eacute;e, vous am&egrave;nent au-dessus des 32&nbsp;bonnes r&eacute;ponses sur 40 avant d'entrer dans la salle. Si votre niveau est encore loin du B2, notre <a href="/blog/atteindre-niveau-b2-naturalisation.html">plan de travail A2&rarr;B2</a> donne les ordres de grandeur en mois.</p>

<h2>Levier 3&nbsp;: un dossier complet du premier coup</h2>

<p>Le r&eacute;c&eacute;piss&eacute;, qui d&eacute;clenche le d&eacute;lai l&eacute;gal, n'est d&eacute;livr&eacute; que lorsque toutes les pi&egrave;ces sont l&agrave;. Un dossier incomplet ne &laquo;&nbsp;prend pas date&nbsp;&raquo;&nbsp;: il attend. Et chaque demande de pi&egrave;ce compl&eacute;mentaire pendant l'instruction co&ucirc;te plusieurs semaines, entre l'envoi de la demande, votre r&eacute;ponse et le r&eacute;examen&nbsp;; pass&eacute; le d&eacute;lai fix&eacute;, le dossier peut m&ecirc;me &ecirc;tre class&eacute; sans suite.</p>

<p>La m&eacute;thode qui &eacute;vite ces allers-retours tient en trois r&egrave;gles&nbsp;:</p>

<ol>
  <li><strong>Commandez d'abord les pi&egrave;ces lentes.</strong> L'<a href="/blog/casier-judiciaire-naturalisation.html">extrait de casier judiciaire &eacute;tranger</a> (exig&eacute; si vous vivez en France depuis moins de 10&nbsp;ans), les actes d'&eacute;tat civil &eacute;trangers &agrave; faire apostiller puis traduire par un traducteur agr&eacute;&eacute;&nbsp;: plusieurs semaines &agrave; plusieurs mois selon le pays.</li>
  <li><strong>Gardez les pi&egrave;ces p&eacute;rissables pour la fin.</strong> Un acte d'&eacute;tat civil fran&ccedil;ais doit avoir moins de 3&nbsp;mois au d&eacute;p&ocirc;t&nbsp;; l'attestation TCF ou TEF, moins de 2&nbsp;ans.</li>
  <li><strong>D&eacute;posez en ligne</strong>, sur le t&eacute;l&eacute;service de l'<a href="/glossaire/anef.html">ANEF</a>, o&ugrave; le <a href="/blog/timbre-fiscal-naturalisation.html">timbre fiscal</a> se paie directement&nbsp;: chaque &eacute;tape vous est notifi&eacute;e par mail, et vous r&eacute;pondez aux demandes depuis votre espace, sans courrier. Pr&eacute;parez en m&ecirc;me temps les originaux, exig&eacute;s &agrave; l'entretien.</li>
</ol>

<p>La <a href="/blog/documents-naturalisation.html">liste compl&egrave;te des pi&egrave;ces</a> d&eacute;pend de votre situation (salari&eacute;, ind&eacute;pendant, &eacute;tudiant, retrait&eacute;, en couple, avec enfants). La checklist de l'app la personnalise et se coche au fur et &agrave; mesure&nbsp;: c'est le moyen le plus simple de v&eacute;rifier, avant de cliquer sur &laquo;&nbsp;envoyer&nbsp;&raquo;, que rien ne manque, y compris les pi&egrave;ces que les listes g&eacute;n&eacute;riques oublient.</p>

<h2>Levier 4&nbsp;: ne pas d&eacute;clencher d'ajournement</h2>

<p>L'<a href="/blog/ajournement-vs-refus-naturalisation.html">ajournement</a> est le pire ennemi d'une naturalisation rapide&nbsp;: la demande est report&eacute;e, un d&eacute;lai vous est impos&eacute;, souvent un &agrave; deux ans, et toute nouvelle demande d&eacute;pos&eacute;e avant son terme est class&eacute;e sans suite. Ses causes sont connues, et la plupart se voient avant le d&eacute;p&ocirc;t&nbsp;:</p>

<ul>
  <li><strong>L'insertion professionnelle.</strong> Depuis la circulaire du 2 mai 2025, la pr&eacute;fecture attend d'un salari&eacute; un CDI de plus d'un an ou une continuit&eacute; de CDD sur 24&nbsp;mois, avec des revenus au moins au niveau du SMIC, hors prestations sociales. D&eacute;poser avec un CDD de six mois pour &laquo;&nbsp;gagner du temps&nbsp;&raquo; revient presque toujours &agrave; en perdre&nbsp;: trois mois d'attente d'un CDI valent mieux qu'un an d'ajournement. Notre guide sur <a href="/blog/ressources-revenus-naturalisation.html">les ressources</a> passe chaque situation en revue.</li>
  <li><strong>Le niveau de fran&ccedil;ais r&eacute;el.</strong> L'attestation ouvre la porte, mais l'entretien se d&eacute;roule en fran&ccedil;ais et l'agent note votre aisance. Un B2 de justesse sur le papier et une conversation laborieuse en pr&eacute;fecture font un compte rendu d&eacute;favorable.</li>
  <li><strong>Les incoh&eacute;rences.</strong> Une adresse, une situation familiale ou professionnelle qui ne correspond plus au dossier, un changement non signal&eacute;&nbsp;: tout ce que l'enqu&ecirc;te d&eacute;couvre p&egrave;se plus lourd que le fait lui-m&ecirc;me.</li>
</ul>

<p>L'<a href="/blog/entretien-naturalisation-prefectures.html">entretien d'assimilation</a> se pr&eacute;pare comme une &eacute;preuve&nbsp;: motivations (voir nos <a href="/blog/pourquoi-voulez-vous-devenir-francais.html">huit exemples de r&eacute;ponses</a> &agrave; &laquo;&nbsp;pourquoi voulez-vous devenir fran&ccedil;ais&nbsp;?&nbsp;&raquo;), parcours, valeurs de la R&eacute;publique, vie quotidienne. Le simulateur d'entretien de l'app vous fait r&eacute;p&eacute;ter les <a href="/blog/questions-entretien-naturalisation.html">questions r&eacute;ellement pos&eacute;es</a> et note vos r&eacute;ponses &agrave; l'oral comme &agrave; l'&eacute;crit&nbsp;; c'est la diff&eacute;rence entre arriver en terrain connu et improviser devant l'agent.</p>

<h2>Levier 5&nbsp;: pendant l'instruction, r&eacute;agir vite et relancer au bon moment</h2>

<p>Une fois le r&eacute;c&eacute;piss&eacute; en main, vous n'acc&eacute;l&eacute;rez plus l'administration, mais vous pouvez &eacute;viter de la ralentir&nbsp;:</p>

<ul>
  <li><strong>R&eacute;pondez dans les d&eacute;lais</strong> &agrave; toute demande de pi&egrave;ce ou de formalit&eacute; notifi&eacute;e sur votre espace ANEF.</li>
  <li><strong>Signalez imm&eacute;diatement tout changement</strong> de situation (adresse, emploi, mariage, naissance), avec justificatifs. Ne d&eacute;m&eacute;nagez pas dans un autre d&eacute;partement pour &laquo;&nbsp;changer de pr&eacute;fecture&nbsp;&raquo;&nbsp;: le dossier est transf&eacute;r&eacute;, et le transfert prend du temps.</li>
  <li><strong>Suivez les statuts</strong> de votre dossier sur l'ANEF et sachez <a href="/blog/statuts-anef-naturalisation.html">ce que chacun signifie</a>&nbsp;: un affichage fig&eacute; n'est pas forc&eacute;ment un dossier bloqu&eacute;.</li>
  <li><strong>Apr&egrave;s l'avis favorable, patientez.</strong> La file d'attente du minist&egrave;re ne se relance pas&nbsp;; notre guide explique <a href="/blog/avis-favorable-naturalisation.html">ce qui se passe entre l'avis favorable et le d&eacute;cret</a>.</li>
  <li><strong>Relancez quand c'est utile, pas avant.</strong> Une relance &agrave; trois mois n'a aucun effet&nbsp;; une lettre recommand&eacute;e argument&eacute;e au d&eacute;passement du d&eacute;lai l&eacute;gal, puis un recours, en ont un. Notre guide <a href="/blog/relance-naturalisation-que-faire-sans-reponse.html">que faire sans r&eacute;ponse</a> donne le calendrier et les mod&egrave;les.</li>
</ul>

<p>Le module de suivi de l'app calcule ces dates &agrave; partir de votre r&eacute;c&eacute;piss&eacute; (12 ou 18&nbsp;mois selon votre anciennet&eacute; de r&eacute;sidence, prolongation comprise) et vous indique quelle relance envoyer, &agrave; qui, et quand.</p>

<h2>Ce qui ne marche pas, et ce qui co&ucirc;te du temps</h2>

<ul>
  <li><strong>Les &laquo;&nbsp;services express&nbsp;&raquo; payants.</strong> Service-public l'&eacute;crit noir sur blanc&nbsp;: hormis le timbre fiscal de 255&nbsp;&euro;, l'acquisition de la nationalit&eacute; est une d&eacute;marche gratuite, et aucun site priv&eacute; ne peut vous obtenir un rendez-vous ou une d&eacute;cision plus vite. Au mieux vous payez pour un formulaire&nbsp;; au pire vous confiez vos documents d'identit&eacute; &agrave; un inconnu.</li>
  <li><strong>D&eacute;poser incomplet &laquo;&nbsp;pour prendre date&nbsp;&raquo;.</strong> Sans r&eacute;c&eacute;piss&eacute;, le d&eacute;lai l&eacute;gal ne court pas.</li>
  <li><strong>D&eacute;m&eacute;nager vers une pr&eacute;fecture r&eacute;put&eacute;e rapide.</strong> Le transfert du dossier annule le gain esp&eacute;r&eacute;, et un d&eacute;m&eacute;nagement de complaisance se voit.</li>
  <li><strong>Choisir le DELF quand on est press&eacute;</strong>, ou passer le TCF sans s'&ecirc;tre test&eacute;&nbsp;: deux &agrave; trois mois de plus dans les deux cas.</li>
  <li><strong>Multiplier les relances pr&eacute;coces.</strong> Elles n'acc&eacute;l&egrave;rent rien et encombrent le service qui instruit votre dossier.</li>
</ul>

<h2>Le calendrier le plus court, concr&egrave;tement</h2>

<ol>
  <li><strong>Mois 0.</strong> V&eacute;rifiez votre voie et vos conditions&nbsp;; commandez le casier judiciaire &eacute;tranger et les actes &agrave; apostiller&nbsp;; commencez l'examen civique dans l'app.</li>
  <li><strong>Mois 1.</strong> Passez l'examen civique. Faites un examen blanc de TCF&nbsp;: si le B2 est l&agrave;, r&eacute;servez une date&nbsp;; sinon, planifiez les semaines de travail n&eacute;cessaires.</li>
  <li><strong>Mois 2 &agrave; 3.</strong> Passez le TCF IRN&nbsp;; r&eacute;unissez les pi&egrave;ces de revenus et de domicile&nbsp;; demandez les actes fran&ccedil;ais de moins de 3&nbsp;mois en dernier.</li>
  <li><strong>Mois 3 &agrave; 4.</strong> R&eacute;sultat du TCF, dossier complet, d&eacute;p&ocirc;t en ligne, r&eacute;c&eacute;piss&eacute;. Le d&eacute;lai l&eacute;gal d&eacute;marre.</li>
  <li><strong>Mois 6 &agrave; 10.</strong> Entretien, pr&eacute;par&eacute; avec le simulateur&nbsp;; originaux en main.</li>
  <li><strong>Mois 12 &agrave; 18 apr&egrave;s le r&eacute;c&eacute;piss&eacute;.</strong> D&eacute;cision, puis publication du d&eacute;cret au Journal officiel&nbsp;; vous &ecirc;tes fran&ccedil;ais &agrave; la date de signature. V&eacute;rifiez votre nom dans notre <a href="/outils/decret-naturalisation.html">annuaire des d&eacute;crets</a>.</li>
</ol>

<p>Compt&eacute; ainsi, un candidat pr&ecirc;t met trois &agrave; quatre mois pour d&eacute;poser un dossier complet, puis entre un an et dix-huit mois pour obtenir son d&eacute;cret. Le m&ecirc;me candidat qui encha&icirc;ne les &eacute;tapes une &agrave; une, rate un TCF, d&eacute;pose incomplet et improvise son entretien peut facilement doubler ce d&eacute;lai. La rapidit&eacute;, en naturalisation, ce n'est pas une astuce&nbsp;: c'est une pr&eacute;paration qui tient dans une seule application, gratuite pour commencer.</p>
""",
    "faq": [
        ("Existe-t-il une procédure de naturalisation accélérée ?",
         "Non. Il n'existe ni procédure express, ni traitement prioritaire payant. Le délai légal de réponse est de 18 mois à compter du récépissé, ramené à 12 mois après 10 ans de résidence habituelle en France, prolongeable une fois de 3 mois. Ce que vous pouvez accélérer, c'est tout ce qui précède le récépissé : choix de la voie, B2, examen civique, constitution du dossier."),
        ("Quel est le délai minimum pour obtenir la nationalité française ?",
         "Pour une naturalisation par décret, comptez le temps de préparation (trois à quatre mois pour un candidat prêt) puis 12 à 18 mois d'instruction à partir du récépissé. Les déclarations sont plus courtes : un an pour la déclaration par mariage ou celle de l'ascendant d'un Français, six mois pour une réintégration par déclaration."),
        ("Quelle est la voie la plus rapide pour devenir français ?",
         "Celle dont vous remplissez déjà toutes les conditions. Marié(e) depuis 4 ans à un(e) Français(e) : la déclaration par mariage, sans examen civique. Ancien Français : la réintégration, sans durée de résidence. Diplômé du supérieur français : résidence réduite à 2 ans. Réfugié ou ressortissant d'un pays francophone : aucune durée de résidence. Et après 10 ans en France, le délai légal passe de 18 à 12 mois."),
        ("TCF IRN ou DELF B2 : lequel choisir quand on est pressé ?",
         "Le TCF IRN : des sessions fréquentes et des résultats en quatre semaines environ, contre deux à trois mois et des sessions rares pour le DELF B2. Le DELF reste préférable si vous n'êtes pas à trois mois près, car il est valable à vie alors que l'attestation TCF expire au bout de 2 ans."),
        ("Un service payant peut-il accélérer ma naturalisation ?",
         "Non. Hormis le timbre fiscal de 255 €, la démarche est gratuite, et aucun intermédiaire ne peut obtenir un rendez-vous ou une décision plus rapide. Service-public met explicitement en garde contre ces sites. Le seul accélérateur légitime est votre préparation : dossier complet, B2 et examen civique acquis, entretien répété."),
        ("Déménager dans une préfecture plus rapide fait-il gagner du temps ?",
         "Non. Votre dossier est instruit par la plateforme de votre domicile ; un déménagement en cours d'instruction entraîne un transfert qui rallonge le traitement. Si vous déménagez pour de vraies raisons, signalez-le immédiatement sur votre espace ANEF."),
        ("Quand passer l'examen civique pour ne pas perdre de temps ?",
         "Tout de suite : les sessions sont régulières, les résultats rapides et l'attestation de réussite n'a pas de durée de validité limitée. Passez-le en parallèle de votre préparation au B2, pas après."),
        ("Que faire si le délai légal est dépassé sans réponse ?",
         "Envoyez une lettre recommandée argumentée rappelant la date du récépissé et le délai légal, puis engagez les recours prévus (gracieux, hiérarchique, Défenseur des droits, tribunal administratif). Relancer avant le terme du délai n'a en revanche aucun effet."),
    ],
    "links": [
        ("/blog/delais-naturalisation-2026.html", "D&eacute;lai de naturalisation 2026&nbsp;: 12 &agrave; 18&nbsp;mois en moyenne"),
        ("/blog/guide-complet-naturalisation-2026.html", "Le guide complet en 8 &eacute;tapes"),
        ("/blog/tcf-irn-ou-delf-b2-lequel-choisir.html", "TCF IRN ou DELF B2&nbsp;: lequel choisir"),
        ("/blog/documents-naturalisation.html", "La liste compl&egrave;te des pi&egrave;ces du dossier"),
        ("/blog/relance-naturalisation-que-faire-sans-reponse.html", "Sans r&eacute;ponse&nbsp;: quand et comment relancer"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret&nbsp;: r&eacute;c&eacute;piss&eacute;, d&eacute;lais de r&eacute;ponse, gratuit&eacute; de la d&eacute;marche (F2213)"),
        ("https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070721/LEGISCTA000006149926/", "Code civil &mdash; Article 21-25-1 (d&eacute;lais de r&eacute;ponse) et articles 21-17 &agrave; 21-20 (dur&eacute;e de r&eacute;sidence)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2726", "Service-public.gouv.fr &mdash; D&eacute;claration de nationalit&eacute; par mariage&nbsp;: d&eacute;lai d'un an (F2726)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F11926", "Service-public.gouv.fr &mdash; Justificatifs de niveau de fran&ccedil;ais et validit&eacute; (F11926)"),
        ("https://www.legifrance.gouv.fr/circulaire/id/45604", "L&eacute;gifrance &mdash; Circulaire du 2 mai 2025 (insertion professionnelle, ressources)"),
    ],
    "cta": "Gagner des mois avec l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"pourquoi-voulez-vous-devenir-francais": {
    "title": "Pourquoi voulez-vous devenir français ? 8 réponses d'entretien",
    "h1": "Pourquoi voulez-vous devenir fran&ccedil;ais&nbsp;? Comment r&eacute;pondre &agrave; l'entretien, avec 8 exemples",
    "desc": "La question ouvre presque tous les entretiens. Ce que l'agent évalue vraiment, les réponses qui desservent, une méthode en trois temps et 8 exemples selon votre parcours.",
    "og": "Pourquoi voulez-vous devenir fran&ccedil;ais&nbsp;? 8 exemples de r&eacute;ponses pour l'entretien",
    "tag": "Entretien",
    "og_img": "simulation-entretien.png",
    "date": "2026-09-17",
    "date_fr": "17 septembre 2026",
    "lede": "&laquo;&nbsp;Pourquoi voulez-vous devenir fran&ccedil;ais&nbsp;?&nbsp;&raquo; C'est la question par laquelle commence la plupart des entretiens d'assimilation, celle que tout le monde a pr&eacute;par&eacute;e, et celle o&ugrave; beaucoup tr&eacute;buchent quand m&ecirc;me&nbsp;: r&eacute;ponse trop courte, trop g&eacute;n&eacute;rale, ou qui sonne comme une formalit&eacute;. Voici ce que l'agent &eacute;value derri&egrave;re cette question, les r&eacute;ponses qui desservent, une m&eacute;thode simple pour construire la v&ocirc;tre, et huit exemples r&eacute;dig&eacute;s pour des parcours diff&eacute;rents, &agrave; adapter &agrave; votre histoire, pas &agrave; r&eacute;citer.",
    "body": """
<h2>Ce que l'agent &eacute;value vraiment derri&egrave;re la question</h2>

<p>L'entretien en pr&eacute;fecture n'est pas un examen de connaissances. Depuis le 1<sup>er</sup> janvier 2026, les connaissances sont v&eacute;rifi&eacute;es par l'<a href="/blog/examen-civique-naturalisation-2026.html">examen civique</a>, et le niveau de fran&ccedil;ais par un test ou un dipl&ocirc;me. La circulaire du 2 mai 2025 demande donc aux pr&eacute;fectures de recentrer l'entretien sur une chose&nbsp;: <strong>votre adh&eacute;sion aux principes et aux valeurs essentiels de la R&eacute;publique</strong>, et l'absence de signaux contraires. Service-public le formule ainsi&nbsp;: l'entretien &laquo;&nbsp;a pour but de v&eacute;rifier votre assimilation &agrave; la communaut&eacute; fran&ccedil;aise, notamment votre adh&eacute;sion aux principes et aux valeurs essentiels de la R&eacute;publique&nbsp;&raquo;, que rappelle la charte des droits et devoirs du citoyen fran&ccedil;ais, sign&eacute;e &agrave; la fin de l'entretien.</p>

<p>La question &laquo;&nbsp;pourquoi voulez-vous devenir fran&ccedil;ais&nbsp;?&nbsp;&raquo; sert &agrave; cela. &Agrave; travers votre r&eacute;ponse, l'agent cherche quatre choses&nbsp;:</p>

<ul>
  <li><strong>La sinc&eacute;rit&eacute; du projet</strong>&nbsp;: vous demandez la nationalit&eacute; pour vous inscrire durablement dans la communaut&eacute; nationale, pas pour un document.</li>
  <li><strong>La coh&eacute;rence avec votre dossier</strong>&nbsp;: ce que vous racontez doit correspondre &agrave; votre parcours, &agrave; vos attaches, &agrave; votre situation professionnelle et familiale telles qu'elles figurent dans les pi&egrave;ces.</li>
  <li><strong>Un rapport personnel aux valeurs</strong>&nbsp;: libert&eacute;, &eacute;galit&eacute; (notamment entre les femmes et les hommes), fraternit&eacute;, la&iuml;cit&eacute;. Non pas r&eacute;cit&eacute;es, mais reli&eacute;es &agrave; votre vie.</li>
  <li><strong>Votre aisance en fran&ccedil;ais</strong>&nbsp;: l'&eacute;change se fait en fran&ccedil;ais, et une r&eacute;ponse fluide, construite, compte autant que son contenu.</li>
</ul>

<div class="callout">
  <p><strong>&Agrave; retenir&nbsp;:</strong> l'agent a votre dossier sous les yeux. Il ne cherche pas des informations, il cherche une personne. La bonne r&eacute;ponse est celle que vous seul pouvez donner.</p>
</div>

<h2>Les cinq r&eacute;ponses qui desservent</h2>

<p>Certaines r&eacute;ponses sont sinc&egrave;res et pourtant contre-productives, parce qu'elles d&eacute;crivent un avantage plut&ocirc;t qu'un engagement.</p>

<ol>
  <li><strong>&laquo;&nbsp;Pour avoir le passeport et voyager plus facilement.&nbsp;&raquo;</strong> C'est vrai pour tout le monde, et c'est pr&eacute;cis&eacute;ment ce qu'on ne veut pas entendre en premier&nbsp;: la nationalit&eacute; r&eacute;duite &agrave; un titre de circulation.</li>
  <li><strong>&laquo;&nbsp;Pour ne plus avoir &agrave; renouveler mon titre de s&eacute;jour.&nbsp;&raquo;</strong> Compr&eacute;hensible, mais c'est une r&eacute;ponse de confort administratif. Elle peut venir en fin de r&eacute;ponse, jamais en ouverture.</li>
  <li><strong>&laquo;&nbsp;Parce que j'y ai droit, j'ai les cinq ans.&nbsp;&raquo;</strong> Remplir les conditions ne cr&eacute;e aucun droit&nbsp;: la naturalisation reste une d&eacute;cision discr&eacute;tionnaire. Cette r&eacute;ponse froisse.</li>
  <li><strong>&laquo;&nbsp;Pour les aides, pour mes enfants, pour les &eacute;tudes.&nbsp;&raquo;</strong> Les droits sociaux ne d&eacute;pendent pas de la nationalit&eacute;, et l'agent le sait. Vous perdez en cr&eacute;dibilit&eacute;.</li>
  <li><strong>Une r&eacute;ponse qui d&eacute;nigre votre pays d'origine.</strong> Vous n'avez pas &agrave; renier d'o&ugrave; vous venez. La France admet la double nationalit&eacute;&nbsp;; ce qui compte, c'est ce qui vous attache ici.</li>
</ol>

<p>S'y ajoutent deux erreurs de forme&nbsp;: la r&eacute;ponse en une phrase (&laquo;&nbsp;parce que j'aime la France&nbsp;&raquo;), qui oblige l'agent &agrave; creuser, et la r&eacute;ponse apprise par c&oelig;ur, reconnaissable au ton, qui fait douter de tout le reste.</p>

<h2>La m&eacute;thode en trois temps</h2>

<p>Une bonne r&eacute;ponse dure trente secondes &agrave; une minute et suit un fil simple&nbsp;: d'o&ugrave; vous venez, ce qui vous retient ici, o&ugrave; vous allez. &Agrave; chaque temps, un fait concret.</p>

<table class="article-table">
  <thead><tr><th>Temps</th><th>Ce que vous dites</th><th>Exemple de fait concret</th></tr></thead>
  <tbody>
    <tr><td>1. Le parcours</td><td>Quand et pourquoi vous &ecirc;tes arriv&eacute;, ce que la France vous a permis de construire</td><td>&laquo;&nbsp;Arriv&eacute; en 2017 pour un master, embauch&eacute; en 2019, en CDI depuis 2021&nbsp;&raquo;</td></tr>
    <tr><td>2. Les attaches</td><td>Ce qui fait que votre vie est ici&nbsp;: famille, travail, amis, engagement, quartier</td><td>&laquo;&nbsp;Mes enfants sont scolaris&eacute;s &agrave; Lyon, je suis b&eacute;n&eacute;vole au club de foot&nbsp;&raquo;</td></tr>
    <tr><td>3. Le projet et les valeurs</td><td>Ce que la nationalit&eacute; change pour vous&nbsp;: participer pleinement, voter, &ecirc;tre citoyen &agrave; part enti&egrave;re</td><td>&laquo;&nbsp;Je veux voter dans la ville o&ugrave; je paie mes imp&ocirc;ts depuis dix ans&nbsp;&raquo;</td></tr>
  </tbody>
</table>

<p>Les valeurs viennent naturellement dans le troisi&egrave;me temps, &agrave; condition de les relier &agrave; quelque chose de v&eacute;cu&nbsp;: la la&iuml;cit&eacute; comme libert&eacute; de conscience que vous appr&eacute;ciez au quotidien, l'&eacute;galit&eacute; entre les femmes et les hommes telle que vous l'appliquez dans votre couple ou au travail, la fraternit&eacute; &agrave; travers un engagement concret. Une phrase suffit&nbsp;; c'est l'exemple qui la rend cr&eacute;dible.</p>

<h2>Huit exemples de r&eacute;ponses, selon votre parcours</h2>

<p>Chaque exemple est &eacute;crit comme on le dirait &agrave; l'oral. Prenez la structure, changez les faits&nbsp;: l'agent doit entendre votre histoire, pas celle-ci.</p>

<h3>1. Arriv&eacute; pour les &eacute;tudes, rest&eacute; pour travailler</h3>

<p>&laquo;&nbsp;Je suis arriv&eacute; en France en 2018 pour un master, et ce qui devait &ecirc;tre deux ann&eacute;es d'&eacute;tudes est devenu ma vie. J'ai &eacute;t&eacute; recrut&eacute; &agrave; la fin de mon stage, je suis en CDI depuis quatre ans dans la m&ecirc;me entreprise, et c'est ici que j'ai construit tout ce qui compte pour moi&nbsp;: mon m&eacute;tier, mes amis, mon appartement. Je paie mes imp&ocirc;ts ici, je suis les d&eacute;bats d'ici, et je me suis rendu compte que je ne pouvais pas voter dans le pays o&ugrave; se d&eacute;cide mon quotidien. Demander la nationalit&eacute;, c'est aller au bout de cette installation&nbsp;: &ecirc;tre un citoyen &agrave; part enti&egrave;re, avec les devoirs qui vont avec.&nbsp;&raquo;</p>

<h3>2. Parent d'enfants n&eacute;s en France</h3>

<p>&laquo;&nbsp;Mes deux enfants sont n&eacute;s &agrave; Nantes, ils sont fran&ccedil;ais, ils grandissent &agrave; l'&eacute;cole de la R&eacute;publique. Je veux &ecirc;tre du m&ecirc;me pays que mes enfants, pas seulement le parent &eacute;tranger qui les accompagne. Ma femme et moi avons fait le choix de les &eacute;lever dans les valeurs qu'on leur enseigne &agrave; l'&eacute;cole&nbsp;: la m&ecirc;me libert&eacute; pour notre fille que pour notre fils, le respect de toutes les croyances et le droit de ne pas croire. Devenir fran&ccedil;ais, c'est rendre officiel un engagement que nous vivons d&eacute;j&agrave; &agrave; la maison.&nbsp;&raquo;</p>

<h3>3. Mari&eacute;(e) &agrave; un(e) Fran&ccedil;ais(e)</h3>

<p>&laquo;&nbsp;J'ai rencontr&eacute; mon mari en 2019 et nous vivons ensemble &agrave; Toulouse depuis. Sa famille est devenue la mienne, nos amis sont ici, notre projet de vie est ici. Je n'ai pas demand&eacute; la nationalit&eacute; tout de suite&nbsp;: je voulais d'abord m'installer professionnellement, am&eacute;liorer mon fran&ccedil;ais, comprendre le pays de l'int&eacute;rieur. Aujourd'hui je me sens chez moi, et je veux participer pleinement &agrave; la vie du pays o&ugrave; nous construisons notre famille, y compris par le vote.&nbsp;&raquo; <em>Pour la d&eacute;claration par mariage, l'entretien se d&eacute;roule avec votre conjoint&nbsp;: la r&eacute;alit&eacute; de votre vie commune est v&eacute;rifi&eacute;e en m&ecirc;me temps que votre assimilation.</em></p>

<h3>4. R&eacute;fugi&eacute;</h3>

<p>&laquo;&nbsp;La France m'a accord&eacute; sa protection en 2019, &agrave; un moment o&ugrave; je n'avais plus de pays. Depuis, j'ai appris la langue, trouv&eacute; un emploi de technicien, et je vis &agrave; Rennes avec ma famille. Je ne demande pas la nationalit&eacute; pour effacer d'o&ugrave; je viens, mais parce que c'est ici que ma vie a pu recommencer, et que je veux y contribuer comme citoyen et non plus comme personne prot&eacute;g&eacute;e. Les libert&eacute;s qui m'ont manqu&eacute; l&agrave;-bas, la libert&eacute; d'opinion, la libert&eacute; de conscience, je sais ce qu'elles valent&nbsp;: ce sont les valeurs que je veux d&eacute;fendre &agrave; mon tour.&nbsp;&raquo;</p>

<h3>5. Salari&eacute; install&eacute; depuis longtemps</h3>

<p>&laquo;&nbsp;Je vis en France depuis douze ans. J'y ai fait toute ma carri&egrave;re, dans la m&ecirc;me entreprise de logistique, o&ugrave; j'encadre aujourd'hui une &eacute;quipe. J'ai longtemps repouss&eacute; la demande parce que je pensais que mon titre de s&eacute;jour suffisait. Puis j'ai compris que je vivais comme un Fran&ccedil;ais sans en avoir les droits ni les devoirs&nbsp;: je ne vote pas, je ne peux pas &ecirc;tre jur&eacute;, je ne suis pas concern&eacute; par les d&eacute;cisions prises en mon nom. Je veux r&eacute;gulariser ce d&eacute;calage, parce que ma vie est ici et qu'elle y restera.&nbsp;&raquo;</p>

<h3>6. Entrepreneur ou ind&eacute;pendant</h3>

<p>&laquo;&nbsp;J'ai cr&eacute;&eacute; mon entreprise &agrave; Marseille en 2020. Elle emploie aujourd'hui trois personnes, toutes recrut&eacute;es localement. J'ai b&eacute;n&eacute;fici&eacute; de ce que la France offre &agrave; ceux qui entreprennent&nbsp;: un cadre stable, des r&egrave;gles claires, un syst&egrave;me qui prot&egrave;ge les salari&eacute;s comme les patrons. Devenir fran&ccedil;ais, c'est reconna&icirc;tre que mon projet est li&eacute; &agrave; ce pays et m'engager &agrave; y participer durablement, comme contribuable, comme employeur et, je l'esp&egrave;re, comme citoyen.&nbsp;&raquo;</p>

<h3>7. Retrait&eacute; ou parent d'un Fran&ccedil;ais majeur</h3>

<p>&laquo;&nbsp;J'ai travaill&eacute; trente ans en France, dans le b&acirc;timent puis comme gardien d'immeuble. Mes enfants sont fran&ccedil;ais, mes petits-enfants aussi. Ma retraite, je la vis ici, dans le quartier o&ugrave; j'habite depuis 1998. Je demande la nationalit&eacute; tard parce que, longtemps, je n'ai pas os&eacute;, et parce que le niveau de fran&ccedil;ais &agrave; l'&eacute;crit m'a fait peur. J'ai travaill&eacute; pour l'obtenir. Je veux finir ma vie dans le pays o&ugrave; je l'ai construite, avec les m&ecirc;mes droits que mes enfants.&nbsp;&raquo;</p>

<h3>8. Francophone arriv&eacute; r&eacute;cemment</h3>

<p>&laquo;&nbsp;Le fran&ccedil;ais est ma langue depuis l'enfance et la culture fran&ccedil;aise fait partie de mon &eacute;ducation&nbsp;; ce n'est pas pour cela que je demande la nationalit&eacute;. Je la demande parce que, depuis mon installation &agrave; Lille en 2023 comme ing&eacute;nieur, j'ai trouv&eacute; un pays o&ugrave; je veux m'engager, pas seulement travailler. Je si&egrave;ge au conseil d'&eacute;cole de mes enfants, je suis adh&eacute;rent d'une association de quartier. Ce que je veux, c'est pouvoir y participer pleinement et durablement, avec la responsabilit&eacute; que cela implique.&nbsp;&raquo;</p>

<h2>Les questions qui suivent, et comment les anticiper</h2>

<p>La question de la motivation appelle presque toujours des relances. Pr&eacute;parez-les avec la m&ecirc;me m&eacute;thode&nbsp;: une r&eacute;ponse courte, un fait concret.</p>

<ul>
  <li><strong>&laquo;&nbsp;Pourquoi maintenant&nbsp;?&nbsp;&raquo;</strong> Un &eacute;l&eacute;ment d&eacute;clencheur honn&ecirc;te&nbsp;: un CDI, une naissance, un ancrage devenu &eacute;vident, le niveau de fran&ccedil;ais enfin atteint.</li>
  <li><strong>&laquo;&nbsp;Que repr&eacute;sente la la&iuml;cit&eacute; pour vous&nbsp;?&nbsp;&raquo;</strong> La libert&eacute; de croire, de ne pas croire, de changer de religion, et la neutralit&eacute; de l'&Eacute;tat&nbsp;; puis un exemple de votre quotidien.</li>
  <li><strong>&laquo;&nbsp;Garderez-vous votre nationalit&eacute; d'origine&nbsp;?&nbsp;&raquo;</strong> La France autorise la double nationalit&eacute;. R&eacute;pondez franchement&nbsp;; expliquez que vos attaches d'origine n'entament pas votre engagement ici.</li>
  <li><strong>&laquo;&nbsp;Que changerait la nationalit&eacute; pour vous&nbsp;?&nbsp;&raquo;</strong> Le vote, l'&eacute;ligibilit&eacute;, la participation &agrave; la d&eacute;fense et aux jurys, l'&eacute;galit&eacute; compl&egrave;te de droits et de devoirs.</li>
  <li><strong>&laquo;&nbsp;Qu'est-ce qui vous manquerait si vous quittiez la France&nbsp;?&nbsp;&raquo;</strong> Une r&eacute;ponse concr&egrave;te et personnelle vaut mieux qu'une liste.</li>
</ul>

<p>Notre article sur <a href="/blog/questions-entretien-naturalisation.html">les questions pos&eacute;es &agrave; l'entretien</a> couvre les autres th&egrave;mes&nbsp;: histoire, institutions, vie quotidienne, situation personnelle.</p>

<h2>Et par &eacute;crit&nbsp;?</h2>

<p>Aucune pi&egrave;ce du dossier ne s'appelle &laquo;&nbsp;lettre de motivation&nbsp;&raquo;. Mais le t&eacute;l&eacute;service de l'ANEF vous permet de compl&eacute;ter votre demande &laquo;&nbsp;avec des informations qui vous semblent avoir un int&eacute;r&ecirc;t particulier&nbsp;&raquo;, et certaines plateformes appr&eacute;cient un texte de quelques lignes sur papier libre&nbsp;: engagement associatif, parcours, projet. Si vous le r&eacute;digez, gardez la m&ecirc;me structure en trois temps, sans d&eacute;passer une page, et surtout sans contradiction avec ce que vous direz &agrave; l'oral&nbsp;: l'agent aura le texte devant lui.</p>

<h2>S'entra&icirc;ner jusqu'&agrave; ce que la r&eacute;ponse soit la v&ocirc;tre</h2>

<p>La diff&eacute;rence entre une r&eacute;ponse pr&eacute;par&eacute;e et une r&eacute;ponse r&eacute;cit&eacute;e, c'est la r&eacute;p&eacute;tition &agrave; voix haute. Dites-la, chronom&eacute;trez-la, reformulez-la sans notes, jusqu'&agrave; ce qu'elle tienne en une minute et qu'elle sonne juste. Puis entra&icirc;nez-vous aux relances.</p>

<p>Le module de simulation d'entretien de l'application <a href="https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087" target="_blank">Naturalisation France Facile</a> a &eacute;t&eacute; construit pour cela&nbsp;: 70&nbsp;questions sur les 8&nbsp;th&egrave;mes de l'entretien, dont la motivation personnelle et le projet de vie, chacune avec une r&eacute;ponse mod&egrave;le et des conseils&nbsp;; 15&nbsp;questions sur <em>votre</em> dossier, pour v&eacute;rifier que votre histoire est coh&eacute;rente d'un bout &agrave; l'autre&nbsp;; et une simulation compl&egrave;te de 100&nbsp;questions encha&icirc;n&eacute;es, o&ugrave; vous r&eacute;pondez &agrave; l'oral ou &agrave; l'&eacute;crit et o&ugrave; l'IA note vos r&eacute;ponses et vous dit quoi am&eacute;liorer. Vous arrivez en pr&eacute;fecture en ayant d&eacute;j&agrave; r&eacute;pondu dix fois &agrave; &laquo;&nbsp;pourquoi voulez-vous devenir fran&ccedil;ais&nbsp;?&nbsp;&raquo;, et en sachant que votre r&eacute;ponse tient.</p>
""",
    "faq": [
        ("Que répondre à « pourquoi voulez-vous devenir français ? » à l'entretien de naturalisation ?",
         "Une réponse personnelle en trois temps : votre parcours en France (quand, pourquoi, ce que vous y avez construit), vos attaches (famille, travail, engagement), puis votre projet et ce que la nationalité change pour vous (voter, être citoyen à part entière), en reliant une ou deux valeurs de la République à un exemple vécu. Trente secondes à une minute, des faits concrets, pas de récitation."),
        ("Quelles réponses faut-il éviter ?",
         "Celles qui réduisent la nationalité à un avantage : le passeport pour voyager, la fin du titre de séjour, « j'y ai droit », les aides ou les études. Évitez aussi de dénigrer votre pays d'origine, la réponse en une phrase, et la réponse apprise par cœur, que l'agent reconnaît au ton."),
        ("L'agent pose-t-il d'autres questions sur la motivation ?",
         "Presque toujours : « pourquoi maintenant ? », « que représente la laïcité pour vous ? », « garderez-vous votre nationalité d'origine ? », « que changerait la nationalité pour vous ? ». Préparez chacune avec une réponse courte et un fait concret."),
        ("Faut-il rédiger une lettre de motivation pour la naturalisation ?",
         "Ce n'est pas une pièce obligatoire. Le téléservice de l'ANEF permet d'ajouter des informations d'intérêt particulier, et un texte court sur papier libre est parfois apprécié. Si vous en écrivez un, gardez la structure en trois temps et assurez-vous qu'il ne contredit pas ce que vous direz à l'oral."),
        ("Peut-on dire qu'on veut garder sa nationalité d'origine ?",
         "Oui. La France admet la double nationalité, et la question est souvent posée pour tester la sincérité. Répondez franchement : vos attaches d'origine ne diminuent pas votre engagement en France, et c'est cet engagement que vous expliquez."),
        ("Que se passe-t-il si l'agent estime que la motivation n'est pas sincère ?",
         "Le compte rendu d'entretien pèse sur l'avis du préfet. Un défaut d'assimilation, dont l'absence d'adhésion aux valeurs de la République, peut conduire à une décision d'irrecevabilité (article 21-24 du Code civil) ; une motivation jugée faible ou incohérente avec le dossier peut alimenter un ajournement. D'où l'importance de préparer une réponse vraie et cohérente."),
        ("Comment s'entraîner à répondre ?",
         "À voix haute, chronométré, sans notes, puis en enchaînant les relances. L'application Naturalisation France Facile propose 70 questions d'entretien avec réponses modèles, 15 questions sur votre propre dossier et une simulation complète de 100 questions, avec une notation de vos réponses orales et écrites par IA."),
    ],
    "links": [
        ("/blog/questions-entretien-naturalisation.html", "Toutes les questions pos&eacute;es &agrave; l'entretien, th&egrave;me par th&egrave;me"),
        ("/blog/sentrainer-entretien-naturalisation.html", "S'entra&icirc;ner &agrave; l'entretien&nbsp;: m&eacute;thode, seul ou en duo"),
        ("/blog/entretien-naturalisation-prefectures.html", "Comment se d&eacute;roule l'entretien en pr&eacute;fecture"),
        ("/blog/apres-entretien-naturalisation.html", "Apr&egrave;s l'entretien&nbsp;: ce qui se passe vraiment"),
        ("/blog/pourquoi-devenir-francais-avantages.html", "Pourquoi devenir fran&ccedil;ais&nbsp;: les avantages r&eacute;els, et les id&eacute;es re&ccedil;ues"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret&nbsp;: l'entretien et la charte des droits et devoirs (F2213)"),
        ("https://www.legifrance.gouv.fr/circulaire/id/45604", "L&eacute;gifrance &mdash; Circulaire du 2 mai 2025&nbsp;: l'entretien recentr&eacute; sur l'adh&eacute;sion aux principes et valeurs de la R&eacute;publique"),
        ("https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070721/LEGISCTA000006149926/", "Code civil &mdash; Article 21-24 (assimilation &agrave; la communaut&eacute; fran&ccedil;aise)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2726", "Service-public.gouv.fr &mdash; D&eacute;claration par mariage&nbsp;: l'entretien avec le conjoint (F2726)"),
    ],
    "cta": "R&eacute;p&eacute;ter l'entretien avec l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"avis-favorable-naturalisation": {
    "title": "Avis favorable naturalisation : que se passe-t-il ensuite ?",
    "h1": "Avis favorable de naturalisation&nbsp;: ce que &ccedil;a veut dire, et combien de temps avant le d&eacute;cret",
    "desc": "L'avis favorable est la proposition du préfet, pas la décision : le ministère contrôle encore avant le décret. Comment on l'apprend, ce qui peut bloquer, les délais.",
    "og": "Avis favorable de naturalisation&nbsp;: et apr&egrave;s&nbsp;?",
    "tag": "Suivi",
    "og_img": "suivi-relance.png",
    "date": "2026-09-17",
    "date_fr": "17 septembre 2026",
    "lede": "L'agent vous l'a dit &agrave; la fin de l'entretien, ou un courrier vous l'a annonc&eacute;, ou vous l'avez d&eacute;duit d'un changement de statut sur l'ANEF&nbsp;: votre dossier a re&ccedil;u un avis favorable. C'est la meilleure nouvelle possible avant le d&eacute;cret, et elle appelle trois questions&nbsp;: qu'est-ce que &ccedil;a vaut juridiquement, que reste-t-il &agrave; franchir, et combien de temps encore&nbsp;? R&eacute;ponses &agrave; partir des textes, d&eacute;cret de 1993 en main.",
    "body": """
<h2>Un avis favorable n'est pas une d&eacute;cision&nbsp;: ce que dit le d&eacute;cret de 1993</h2>

<p>La proc&eacute;dure de naturalisation est r&eacute;gl&eacute;e par le d&eacute;cret n&deg;&nbsp;93-1362 du 30 d&eacute;cembre 1993. Il distingue nettement deux moments.</p>

<p>D'un c&ocirc;t&eacute;, les <strong>d&eacute;cisions d&eacute;favorables</strong>, que le pr&eacute;fet prend lui-m&ecirc;me&nbsp;: irrecevabilit&eacute; (article 43), rejet ou ajournement (article 44). Elles vous sont notifi&eacute;es, avec un d&eacute;lai de deux mois pour former un <a href="/glossaire/rapo.html">recours administratif</a> aupr&egrave;s du ministre.</p>

<p>De l'autre, les cas favorables. L'article 46 est pr&eacute;cis&nbsp;: lorsque le pr&eacute;fet &laquo;&nbsp;estime que la demande est recevable et qu'il y a lieu d'accorder la naturalisation&nbsp;&raquo;, il &laquo;&nbsp;&eacute;met une proposition en ce sens&nbsp;&raquo;, et &laquo;&nbsp;le dossier assorti de cette proposition est transmis au ministre charg&eacute; des naturalisations dans les six mois suivant la d&eacute;livrance du r&eacute;c&eacute;piss&eacute;&nbsp;&raquo;. Le dossier part avec vos pi&egrave;ces, votre bulletin n&deg;&nbsp;2 de casier judiciaire et le r&eacute;sultat de l'enqu&ecirc;te.</p>

<p>Puis l'article 48 rappelle qui d&eacute;cide&nbsp;: &laquo;&nbsp;si le ministre charg&eacute; des naturalisations estime qu'il n'y a pas lieu d'accorder la naturalisation ou la r&eacute;int&eacute;gration sollicit&eacute;e, il prononce le rejet de la demande&nbsp;&raquo;&nbsp;; il peut aussi &laquo;&nbsp;en prononcer l'ajournement&nbsp;&raquo;. Autrement dit, l'avis favorable est une <strong>proposition</strong>. La d&eacute;cision, c'est le d&eacute;cret, sign&eacute; au niveau national apr&egrave;s contr&ocirc;le.</p>

<div class="callout">
  <p><strong>&Agrave; retenir&nbsp;:</strong> avis favorable = la pr&eacute;fecture propose votre naturalisation et transmet le dossier au minist&egrave;re. Vous n'&ecirc;tes pas encore fran&ccedil;ais&nbsp;; vous le devenez &agrave; la date de signature du d&eacute;cret. Mais vous avez franchi l'&eacute;tape qui &eacute;carte le plus de dossiers.</p>
</div>

<h2>Comment on apprend l'avis favorable</h2>

<p>Aucun texte n'oblige la pr&eacute;fecture &agrave; vous notifier sa proposition. Elle vous parvient donc de fa&ccedil;on variable&nbsp;:</p>

<ul>
  <li><strong>&Agrave; la fin de l'entretien</strong>, quand l'agent vous indique qu'il proposera un avis favorable. C'est fr&eacute;quent, mais l'avis d&eacute;finitif suppose la validation de sa hi&eacute;rarchie.</li>
  <li><strong>Par un courrier ou un mail</strong> de la plateforme de naturalisation vous informant que votre dossier a &eacute;t&eacute; transmis au minist&egrave;re avec un avis favorable. Toutes les plateformes ne le font pas.</li>
  <li><strong>Par le statut ANEF.</strong> Le passage de la phase pr&eacute;fectorale (proposition de d&eacute;cision) &agrave; la phase de contr&ocirc;le minist&eacute;riel signale que le dossier a quitt&eacute; la pr&eacute;fecture&nbsp;; notre d&eacute;codage des <a href="/blog/statuts-anef-naturalisation.html">statuts ANEF</a> d&eacute;taille chaque libell&eacute;.</li>
</ul>

<p>Une pr&eacute;cision utile, parce que la question revient sans cesse&nbsp;: une <strong>lettre recommand&eacute;e</strong> ne porte pas un avis, elle porte une <em>d&eacute;cision</em>. Si vous en recevez une pendant l'instruction, c'est le plus souvent la notification d'une d&eacute;cision d&eacute;favorable, avec ses voies et d&eacute;lais de recours&nbsp;; &agrave; l'issue, c'est parfois la notification de votre inscription dans un d&eacute;cret, qui vous parvient sinon par mail sur votre espace personnel. Un avis favorable, lui, ne se notifie pas par recommand&eacute;.</p>

<h2>Ce qui se passe au minist&egrave;re apr&egrave;s l'avis favorable</h2>

<p>Le dossier arrive &agrave; la <a href="/glossaire/sdanf.html">sous-direction de l'acc&egrave;s &agrave; la nationalit&eacute; fran&ccedil;aise</a> (SDANF), &agrave; Rez&eacute; pr&egrave;s de Nantes. Elle ne refait pas l'instruction&nbsp;; elle la <strong>contr&ocirc;le</strong>, et pr&eacute;pare le d&eacute;cret. Dans l'ordre&nbsp;:</p>

<ol>
  <li><strong>File d'attente d'affectation.</strong> Le dossier attend qu'un agent le prenne. C'est, d'apr&egrave;s les retours d'usagers, l'&eacute;tape la plus longue du parcours, et aucune relance ne la raccourcit.</li>
  <li><strong>Contr&ocirc;le minist&eacute;riel.</strong> V&eacute;rification de la recevabilit&eacute; et de l'opportunit&eacute; au regard des orientations nationales (la <a href="/blog/ressources-revenus-naturalisation.html">circulaire du 2 mai 2025</a> sur l'insertion professionnelle et le comportement), relecture de l'enqu&ecirc;te et du casier, &eacute;ventuelle enqu&ecirc;te compl&eacute;mentaire.</li>
  <li><strong>V&eacute;rification de l'&eacute;tat civil</strong> par le <a href="/glossaire/scec.html">Service central d'&eacute;tat civil</a> de Nantes, qui &eacute;tablira votre acte de naissance fran&ccedil;ais. C'est l&agrave; que les incoh&eacute;rences d'orthographe ou de dates entre vos actes se r&egrave;glent, parfois au prix d'une demande de pi&egrave;ce.</li>
  <li><strong>Derni&egrave;res v&eacute;rifications puis insertion dans un d&eacute;cret</strong> collectif, signature, publication au Journal officiel. Vous &ecirc;tes inform&eacute; par mail de votre inscription et de la date de publication&nbsp;; le d&eacute;cret se t&eacute;l&eacute;charge sur L&eacute;gifrance.</li>
</ol>

<h2>Combien de temps entre l'avis favorable et le d&eacute;cret&nbsp;?</h2>

<p>Le cadre l&eacute;gal est celui de toute la proc&eacute;dure&nbsp;: l'administration doit r&eacute;pondre dans les <strong>18&nbsp;mois</strong> suivant le r&eacute;c&eacute;piss&eacute; de dossier complet, <strong>12&nbsp;mois</strong> si vous r&eacute;sidez en France depuis au moins 10&nbsp;ans, avec une prolongation possible de 3&nbsp;mois. Le d&eacute;cret de 1993 ajoute un jalon interne&nbsp;: la pr&eacute;fecture doit transmettre sa proposition dans les <strong>6&nbsp;mois</strong> du r&eacute;c&eacute;piss&eacute;.</p>

<table class="article-table">
  <thead><tr><th>&Eacute;tape</th><th>Rep&egrave;re</th><th>Ce que vous voyez</th></tr></thead>
  <tbody>
    <tr><td>R&eacute;c&eacute;piss&eacute; de dossier complet</td><td>Jour 0&nbsp;: le d&eacute;lai l&eacute;gal d&eacute;marre</td><td>R&eacute;c&eacute;piss&eacute; sur l'ANEF</td></tr>
    <tr><td>Entretien puis proposition du pr&eacute;fet</td><td>Au plus tard 6&nbsp;mois apr&egrave;s le r&eacute;c&eacute;piss&eacute; (article 46)</td><td>Avis favorable oral ou courrier, statut &laquo;&nbsp;proposition&nbsp;&raquo;</td></tr>
    <tr><td>Contr&ocirc;le &agrave; la SDANF</td><td>Souvent la phase la plus longue, plusieurs mois</td><td>Statuts de contr&ocirc;le, parfois fig&eacute;s longtemps</td></tr>
    <tr><td>Insertion dans un d&eacute;cret et publication</td><td>Quelques semaines une fois le dossier valid&eacute;</td><td>Mail d'inscription, date au JO sur votre espace</td></tr>
    <tr><td>R&eacute;ponse au plus tard</td><td>18&nbsp;mois (12 apr&egrave;s 10&nbsp;ans de r&eacute;sidence), +3&nbsp;mois</td><td>Pass&eacute; ce d&eacute;lai&nbsp;: relance puis recours</td></tr>
  </tbody>
</table>

<p>En pratique, comptez le plus souvent <strong>entre trois mois et un an</strong> entre l'avis favorable et la publication, selon la file d'attente du moment. Nos pages sur les <a href="/blog/delais-naturalisation-2026.html">d&eacute;lais de naturalisation</a> et sur les <a href="/blog/delais-naturalisation-par-prefecture.html">&eacute;carts entre plateformes</a> donnent les ordres de grandeur observ&eacute;s.</p>

<h2>Peut-on encore &ecirc;tre refus&eacute; apr&egrave;s un avis favorable&nbsp;?</h2>

<p>Oui, c'est rare mais pr&eacute;vu par les textes, et il vaut mieux savoir ce qui le d&eacute;clenche&nbsp;:</p>

<ul>
  <li><strong>Un &eacute;l&eacute;ment nouveau d&eacute;favorable</strong> apparu pendant le contr&ocirc;le&nbsp;: une condamnation, une proc&eacute;dure p&eacute;nale, un signalement de l'enqu&ecirc;te, un s&eacute;jour irr&eacute;gulier pass&eacute; non d&eacute;clar&eacute;.</li>
  <li><strong>Un changement de situation</strong> qui fragilise une condition&nbsp;: perte d'emploi durable, revenus devenus majoritairement des prestations sociales, d&eacute;part du conjoint et des enfants &agrave; l'&eacute;tranger, ce qui remet en cause le centre de vos int&eacute;r&ecirc;ts en France.</li>
  <li><strong>Une incoh&eacute;rence d'&eacute;tat civil</strong> non r&eacute;solue, qui bloque l'insertion dans le d&eacute;cret tant qu'elle n'est pas lev&eacute;e.</li>
  <li><strong>Une divergence d'appr&eacute;ciation</strong> entre la pr&eacute;fecture et le minist&egrave;re sur l'opportunit&eacute;, au regard des orientations nationales.</li>
</ul>

<p>Et apr&egrave;s la publication, le d&eacute;cret peut encore &ecirc;tre <strong>retir&eacute;</strong> dans les deux ans, sur avis conforme du Conseil d'&Eacute;tat, si l'administration constate que vous ne remplissiez pas les conditions, ou dans les deux ans suivant la d&eacute;couverte d'une fraude. La conclusion pratique tient en une phrase&nbsp;: jusqu'au d&eacute;cret, gardez votre situation stable et <strong>d&eacute;clarez tout changement</strong> (adresse, emploi, situation familiale) sur votre espace ANEF, avec justificatifs. Un changement d&eacute;clar&eacute; s'explique&nbsp;; un changement d&eacute;couvert se paie.</p>

<h2>Avis favorable apr&egrave;s un recours&nbsp;: le cas du recours hi&eacute;rarchique</h2>

<p>Autre situation fr&eacute;quente dans les recherches&nbsp;: vous avez re&ccedil;u un ajournement ou un rejet du pr&eacute;fet, form&eacute; un recours aupr&egrave;s du ministre dans les deux mois, et le minist&egrave;re y a fait droit. Cet &laquo;&nbsp;avis favorable apr&egrave;s recours&nbsp;&raquo; signifie que votre dossier repart vers la naturalisation, sans nouvelle demande ni nouveau timbre&nbsp;: il rejoint le circuit de contr&ocirc;le puis d'insertion dans un d&eacute;cret, avec des d&eacute;lais comparables. Notre guide sur l'<a href="/blog/ajournement-vs-refus-naturalisation.html">ajournement et le refus</a> d&eacute;taille la proc&eacute;dure de recours, et ce qu'un silence de quatre mois du ministre signifie.</p>

<h2>Ce que vous pouvez faire pendant l'attente</h2>

<ul>
  <li><strong>Rien pour acc&eacute;l&eacute;rer</strong>, et c'est frustrant&nbsp;: la file d'attente minist&eacute;rielle ne se relance pas. Une relance avant le terme du d&eacute;lai l&eacute;gal n'a pas d'effet.</li>
  <li><strong>R&eacute;pondre vite</strong> &agrave; toute demande de pi&egrave;ce (souvent de l'&eacute;tat civil) notifi&eacute;e sur l'ANEF&nbsp;; c'est le seul moment o&ugrave; votre r&eacute;activit&eacute; change le calendrier.</li>
  <li><strong>Maintenir votre titre de s&eacute;jour en cours de validit&eacute;</strong> jusqu'au d&eacute;cret&nbsp;: demandez son renouvellement dans les d&eacute;lais habituels, la proc&eacute;dure de naturalisation ne le remplace pas.</li>
  <li><strong>Pr&eacute;parer l'apr&egrave;s</strong>&nbsp;: les actes de naissance &eacute;trangers ne serviront plus, mais vos <a href="/blog/demarches-apres-naturalisation.html">d&eacute;marches des six premiers mois</a> (acte de naissance fran&ccedil;ais, carte d'identit&eacute;, passeport, listes &eacute;lectorales) s'encha&icirc;nent vite apr&egrave;s la publication.</li>
  <li><strong>Relancer au bon moment</strong>&nbsp;: au d&eacute;passement du d&eacute;lai l&eacute;gal, une lettre recommand&eacute;e argument&eacute;e, puis les recours d&eacute;crits dans notre guide <a href="/blog/relance-naturalisation-que-faire-sans-reponse.html">que faire sans r&eacute;ponse</a>.</li>
</ul>

<p>Le module de suivi de l'application <a href="https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087" target="_blank">Naturalisation France Facile</a> calcule vos &eacute;ch&eacute;ances &agrave; partir de la date du r&eacute;c&eacute;piss&eacute;, 12 ou 18&nbsp;mois selon votre anciennet&eacute; de r&eacute;sidence, prolongation comprise, et vous dit quelle relance envoyer, &agrave; qui et quand. Sa checklist pr&eacute;pare d&eacute;j&agrave; les d&eacute;marches d'apr&egrave;s-d&eacute;cret, pour que l'attente serve &agrave; quelque chose.</p>
""",
    "faq": [
        ("Que signifie un avis favorable pour une naturalisation ?",
         "Que le préfet, après l'entretien et l'enquête, estime que votre demande est recevable et qu'il y a lieu d'accorder la naturalisation : il émet une proposition en ce sens et transmet le dossier au ministère chargé des naturalisations (article 46 du décret du 30 décembre 1993). C'est une proposition, pas la décision : celle-ci est le décret, pris au niveau national après contrôle."),
        ("Combien de temps après l'avis favorable arrive le décret ?",
         "Le plus souvent entre trois mois et un an, selon la file d'attente du ministère. Le cadre légal est de 18 mois maximum à compter du récépissé de dossier complet (12 mois après 10 ans de résidence habituelle en France), prolongeables une fois de 3 mois ; la préfecture doit transmettre sa proposition dans les 6 mois du récépissé."),
        ("Comment savoir si j'ai un avis favorable ?",
         "Par l'agent à la fin de l'entretien, par un courrier ou un mail de la plateforme indiquant que le dossier est transmis au ministère avec un avis favorable, ou par le passage de votre dossier en phase de contrôle ministériel sur l'ANEF. Aucun texte n'impose une notification de l'avis."),
        ("Une lettre recommandée annonce-t-elle un avis favorable ?",
         "Non. Une lettre recommandée porte une décision : le plus souvent une décision défavorable pendant l'instruction, avec les délais de recours, ou, à la fin, la notification de votre inscription dans un décret. L'avis favorable, lui, ne se notifie pas par recommandé."),
        ("Peut-on être refusé après un avis favorable ?",
         "Oui, c'est rare mais possible : l'article 48 du décret de 1993 permet au ministre de rejeter ou d'ajourner malgré la proposition du préfet, par exemple si un élément nouveau apparaît (condamnation, séjour irrégulier passé, changement de situation) ou en cas de divergence sur l'opportunité. Après publication, le décret peut encore être retiré dans les deux ans si les conditions n'étaient pas remplies, ou en cas de fraude."),
        ("Que veut dire « avis favorable » après un recours hiérarchique ?",
         "Que le ministre a fait droit à votre recours contre une décision d'ajournement ou de rejet du préfet : votre dossier repart vers la naturalisation, sans nouvelle demande ni nouveau timbre, et rejoint le circuit de contrôle puis d'insertion dans un décret."),
        ("Dois-je renouveler mon titre de séjour après l'avis favorable ?",
         "Oui. Jusqu'à la signature du décret, vous restez soumis au droit au séjour : demandez le renouvellement dans les délais habituels. La procédure de naturalisation ne remplace pas le titre de séjour."),
        ("Faut-il relancer après un avis favorable ?",
         "Pas avant le terme du délai légal : la file d'attente ministérielle ne se relance pas. Répondez vite aux demandes de pièces, déclarez tout changement de situation, et n'engagez une relance écrite puis les recours qu'une fois le délai légal dépassé."),
    ],
    "links": [
        ("/blog/apres-entretien-naturalisation.html", "Apr&egrave;s l'entretien&nbsp;: compte rendu, avis du pr&eacute;fet, transmission"),
        ("/blog/statuts-anef-naturalisation.html", "Statuts ANEF&nbsp;: que signifie chaque libell&eacute;"),
        ("/blog/journal-officiel-naturalisation-liste-des-noms.html", "Trouver son nom dans un d&eacute;cret au Journal officiel"),
        ("/blog/relance-naturalisation-que-faire-sans-reponse.html", "Sans r&eacute;ponse&nbsp;: quand et comment relancer"),
        ("/blog/ajournement-vs-refus-naturalisation.html", "Ajournement ou refus&nbsp;: les recours"),
    ],
    "sources": [
        ("https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000041422414", "L&eacute;gifrance &mdash; D&eacute;cret n&deg;&nbsp;93-1362, article 46 (proposition favorable du pr&eacute;fet, transmission au ministre)"),
        ("https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049147350", "L&eacute;gifrance &mdash; D&eacute;cret n&deg;&nbsp;93-1362, article 44 (rejet et ajournement par le pr&eacute;fet)"),
        ("https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000022414611", "L&eacute;gifrance &mdash; D&eacute;cret n&deg;&nbsp;93-1362, article 48 (d&eacute;cision du ministre)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret&nbsp;: d&eacute;lais de r&eacute;ponse, notification, retrait du d&eacute;cret (F2213)"),
        ("https://www.legifrance.gouv.fr/circulaire/id/45604", "L&eacute;gifrance &mdash; Circulaire du 2 mai 2025, orientations relatives &agrave; l'acquisition de la nationalit&eacute; fran&ccedil;aise"),
    ],
    "cta": "Suivre mes d&eacute;lais et relances dans l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"timbre-fiscal-naturalisation": {
    "title": "Timbre fiscal naturalisation : 255 €, achat en ligne, validité",
    "h1": "Timbre fiscal de naturalisation&nbsp;: 255&nbsp;&euro;, o&ugrave; l'acheter, validit&eacute; et remboursement",
    "desc": "255 € depuis le 1er mai 2026 (127,50 € en Guyane), payable dans la démarche ANEF ou sur timbres.impots.gouv.fr, valable 1 an, remboursable 18 mois. Et le timbre à 55 €.",
    "og": "Timbre fiscal de naturalisation&nbsp;: le mode d'emploi 2026",
    "tag": "Documents",
    "og_img": "checklist-documents.png",
    "date": "2026-09-17",
    "date_fr": "17 septembre 2026",
    "lede": "Le timbre fiscal est la seule d&eacute;pense obligatoire de la demande de nationalit&eacute;, et l'une des rares pi&egrave;ces qui peut faire classer un dossier sans suite si elle manque. Depuis le 1er mai 2026, il co&ucirc;te 255&nbsp;&euro;. Voici, &agrave; partir des pages officielles, comment l'acheter (et depuis quand on peut le payer directement dans la d&eacute;marche en ligne), combien de temps il reste valable, comment se le faire rembourser, et ce qu'il faut faire d'un timbre &agrave; 55&nbsp;&euro; achet&eacute; avant la hausse.",
    "body": """
<h2>Le montant en 2026, et les proc&eacute;dures concern&eacute;es</h2>

<p>Le droit de timbre s'&eacute;l&egrave;ve &agrave; <strong>255&nbsp;&euro;</strong> en m&eacute;tropole et dans les d&eacute;partements d'outre-mer, et &agrave; <strong>127,50&nbsp;&euro;</strong> en Guyane. Il &eacute;tait de 55&nbsp;&euro; jusqu'au 30 avril 2026&nbsp;; notre article sur la <a href="/blog/hausse-timbre-fiscal-naturalisation-mai-2026.html">hausse du 1<sup>er</sup> mai 2026</a> en retrace l'origine.</p>

<p>Service-public liste les d&eacute;marches soumises &agrave; cette taxe&nbsp;: la <strong>naturalisation</strong> par d&eacute;cret, la <strong>r&eacute;int&eacute;gration</strong> dans la nationalit&eacute; fran&ccedil;aise, et les <strong>d&eacute;clarations de nationalit&eacute;</strong> au titre du mariage avec un Fran&ccedil;ais, en tant qu'ascendant d'un Fran&ccedil;ais ou de fr&egrave;re ou s&oelig;ur d'un Fran&ccedil;ais. Le montant est identique pour toutes.</p>

<table class="article-table">
  <thead><tr><th>Proc&eacute;dure</th><th>Montant</th><th>O&ugrave; le payer</th></tr></thead>
  <tbody>
    <tr><td>Naturalisation ou r&eacute;int&eacute;gration par d&eacute;cret (d&eacute;p&ocirc;t en ligne)</td><td>255&nbsp;&euro; (127,50&nbsp;&euro; en Guyane)</td><td>Directement dans la d&eacute;marche en ligne sur l'ANEF</td></tr>
    <tr><td>D&eacute;claration par mariage, ascendant, fr&egrave;re ou s&oelig;ur d'un Fran&ccedil;ais</td><td>255&nbsp;&euro; (127,50&nbsp;&euro; en Guyane)</td><td>timbres.impots.gouv.fr ou bureau de tabac agr&eacute;&eacute;, timbre joint au dossier</td></tr>
    <tr><td>D&eacute;p&ocirc;t papier autoris&eacute; (impossibilit&eacute; de t&eacute;l&eacute;service attest&eacute;e)</td><td>255&nbsp;&euro; (127,50&nbsp;&euro; en Guyane)</td><td>timbres.impots.gouv.fr ou bureau de tabac agr&eacute;&eacute;</td></tr>
    <tr><td>D&eacute;p&ocirc;t &agrave; l'&eacute;tranger, au consulat</td><td>Droits de chancellerie</td><td>Au consulat, lors du d&eacute;p&ocirc;t (esp&egrave;ces, carte ou virement selon le poste)</td></tr>
  </tbody>
</table>

<p>Deux cas particuliers reviennent souvent. Un <strong>couple</strong> qui d&eacute;pose deux demandes paie deux timbres&nbsp;: chaque demande est un dossier. Les <strong>enfants mineurs</strong> inscrits sur la demande d'un parent, eux, ne paient rien&nbsp;: ils deviennent fran&ccedil;ais par effet collectif, sans dossier propre.</p>

<h2>O&ugrave; et comment l'acheter</h2>

<h3>1. Dans la d&eacute;marche en ligne, pour la naturalisation et la r&eacute;int&eacute;gration</h3>

<p>C'est la voie normale depuis la g&eacute;n&eacute;ralisation du t&eacute;l&eacute;service&nbsp;: service-public indique que &laquo;&nbsp;la demande de naturalisation fran&ccedil;aise et la demande de r&eacute;int&eacute;gration par d&eacute;cret se font en ligne&nbsp;&raquo; et que &laquo;&nbsp;vous pouvez payer le timbre fiscal &eacute;lectronique lors de la d&eacute;marche en ligne&nbsp;&raquo;. Le paiement se fait par carte bancaire au moment du d&eacute;p&ocirc;t sur l'<a href="/glossaire/anef.html">ANEF</a>, et le timbre est rattach&eacute; &agrave; votre dossier sans manipulation. Si vous avez d&eacute;j&agrave; un timbre &eacute;lectronique, la d&eacute;marche permet de saisir sa r&eacute;f&eacute;rence.</p>

<h3>2. Sur timbres.impots.gouv.fr, pour les d&eacute;clarations et les d&eacute;p&ocirc;ts papier</h3>

<p>Le site officiel de la Direction g&eacute;n&eacute;rale des finances publiques vend le timbre &laquo;&nbsp;Nationalit&eacute; fran&ccedil;aise&nbsp;&raquo; au montant en vigueur. Apr&egrave;s paiement par carte, vous recevez par mail ou par SMS, au choix, le <strong>timbre &eacute;lectronique</strong> (un identifiant &agrave; 16 chiffres) et le <strong>justificatif de paiement</strong> avec la r&eacute;f&eacute;rence de transaction. Imprimez ou enregistrez les deux&nbsp;: le timbre se joint au dossier, la r&eacute;f&eacute;rence sert en cas de remboursement.</p>

<h3>3. Dans un bureau de tabac agr&eacute;&eacute;</h3>

<p>Les buralistes &eacute;quip&eacute;s de l'application &laquo;&nbsp;Point de vente agr&eacute;&eacute;&nbsp;&raquo; d&eacute;livrent le m&ecirc;me timbre &eacute;lectronique, sur un re&ccedil;u portant l'identifiant. Demandez explicitement un timbre pour une demande de nationalit&eacute; fran&ccedil;aise, au montant en vigueur, et conservez le re&ccedil;u comme un original.</p>

<div class="callout">
  <p><strong>Un seul site officiel&nbsp;:</strong> timbres.impots.gouv.fr, sans frais de service. Les sites qui &laquo;&nbsp;vendent&nbsp;&raquo; le timbre plus cher, ou qui proposent un &laquo;&nbsp;service de d&eacute;p&ocirc;t express&nbsp;&raquo;, n'ont aucune existence administrative&nbsp;: hormis le timbre, la d&eacute;marche est gratuite.</p>
</div>

<h2>Validit&eacute;&nbsp;: un an, et pas plus</h2>

<p>Le timbre &eacute;lectronique est <strong>valable 1&nbsp;an &agrave; partir de sa date d'achat</strong>. Service-public en tire un conseil de bon sens&nbsp;: &laquo;&nbsp;pour &eacute;viter qu'il ne soit plus valide au moment du d&eacute;p&ocirc;t de votre demande, attendez d'avoir fini de pr&eacute;parer votre dossier avant de l'acheter&nbsp;&raquo;. C'est la derni&egrave;re pi&egrave;ce &agrave; acqu&eacute;rir, une fois le B2, l'examen civique, les actes et les traductions r&eacute;unis, et c'est d'ailleurs sa place dans une <a href="/blog/documents-naturalisation.html">checklist de dossier</a> bien ordonn&eacute;e.</p>

<p>Un timbre p&eacute;rim&eacute; n'est pas perdu pour autant, &agrave; condition d'agir dans les temps&nbsp;: voir le remboursement ci-dessous.</p>

<h2>Remboursement&nbsp;: 18&nbsp;mois, en ligne, avec la r&eacute;f&eacute;rence de transaction</h2>

<p>Si vous n'utilisez pas le timbre, vous pouvez en demander le <strong>remboursement en ligne dans les 18&nbsp;mois qui suivent l'achat</strong>, sur le m&ecirc;me site, muni de la r&eacute;f&eacute;rence de la transaction indiqu&eacute;e sur le justificatif. Cela couvre trois situations&nbsp;: vous avez achet&eacute; un timbre puis renonc&eacute; &agrave; d&eacute;poser, vous en avez achet&eacute; deux par erreur, ou le timbre a d&eacute;pass&eacute; sa validit&eacute; d'un an mais reste dans la fen&ecirc;tre de 18&nbsp;mois.</p>

<p>Ce qui n'est jamais rembours&eacute;&nbsp;: un timbre <strong>consomm&eacute; par un d&eacute;p&ocirc;t</strong>. Si votre demande est ensuite ajourn&eacute;e, rejet&eacute;e ou class&eacute;e sans suite, la taxe reste acquise, et une nouvelle demande suppose un nouveau timbre. C'est l'une des raisons de ne d&eacute;poser qu'un dossier complet et solide, sujet de notre article sur la <a href="/blog/naturalisation-rapide.html">naturalisation sans perdre de mois</a>.</p>

<h2>J'ai achet&eacute; un timbre &agrave; 55&nbsp;&euro; avant le 1<sup>er</sup> mai 2026&nbsp;: que faire&nbsp;?</h2>

<p>La taxe due est celle en vigueur <strong>&agrave; la date du d&eacute;p&ocirc;t</strong> de la demande. Un dossier d&eacute;pos&eacute; depuis le 1<sup>er</sup> mai 2026 suppose donc un timbre de 255&nbsp;&euro;, m&ecirc;me si vous aviez achet&eacute; un timbre &agrave; 55&nbsp;&euro; avant la hausse&nbsp;: celui-ci ne couvre plus le montant exig&eacute;. Deux possibilit&eacute;s&nbsp;:</p>

<ol>
  <li><strong>Demander son remboursement</strong> en ligne, dans les 18&nbsp;mois suivant l'achat, puis acheter un timbre de 255&nbsp;&euro;, ou payer directement dans la d&eacute;marche ANEF.</li>
  <li><strong>V&eacute;rifier aupr&egrave;s de votre plateforme</strong> si un compl&eacute;ment est accept&eacute; avant de compter dessus&nbsp;: ne d&eacute;posez pas avec un timbre insuffisant, la pi&egrave;ce serait consid&eacute;r&eacute;e comme manquante.</li>
</ol>

<p>Et si vous avez d&eacute;pos&eacute; <em>avant</em> le 1<sup>er</sup> mai 2026 avec un timbre &agrave; 55&nbsp;&euro;, rien ne change&nbsp;: le tarif applicable &eacute;tait celui du jour du d&eacute;p&ocirc;t.</p>

<h2>Les erreurs qui co&ucirc;tent 255&nbsp;&euro; ou plusieurs semaines</h2>

<ul>
  <li><strong>Acheter trop t&ocirc;t</strong>&nbsp;: un dossier qui prend quatorze mois &agrave; r&eacute;unir rend le timbre caduc. Achetez en dernier.</li>
  <li><strong>Se tromper de timbre</strong>&nbsp;: le timbre &laquo;&nbsp;passeport&nbsp;&raquo; ou &laquo;&nbsp;titre de s&eacute;jour&nbsp;&raquo; n'est pas le timbre &laquo;&nbsp;nationalit&eacute;&nbsp;&raquo;. Sur le site officiel, choisissez la rubrique nationalit&eacute; fran&ccedil;aise.</li>
  <li><strong>Perdre le justificatif</strong>&nbsp;: sans la r&eacute;f&eacute;rence de transaction, pas de remboursement. Conservez le mail ou le SMS et une copie imprim&eacute;e.</li>
  <li><strong>Acheter sur un site interm&eacute;diaire</strong>&nbsp;: au mieux vous payez des frais inutiles, au pire vous laissez vos donn&eacute;es bancaires &agrave; un inconnu.</li>
  <li><strong>Payer deux fois</strong> pour deux demandes rejet&eacute;es&nbsp;: le timbre n'assure rien. Un dossier pr&eacute;par&eacute; (B2 acquis, examen civique r&eacute;ussi, pi&egrave;ces compl&egrave;tes, entretien r&eacute;p&eacute;t&eacute;) co&ucirc;te 255&nbsp;&euro;&nbsp;; un dossier b&acirc;cl&eacute; en co&ucirc;te 510 et une ann&eacute;e.</li>
</ul>

<h2>Le timbre dans le budget total</h2>

<p>Le timbre n'est qu'une partie de la d&eacute;pense&nbsp;: s'y ajoutent le test de langue (200 &agrave; 300&nbsp;&euro; pour le TCF IRN, 100 &agrave; 200&nbsp;&euro; pour le DELF B2, sauf si un dipl&ocirc;me fran&ccedil;ais vous en dispense), l'examen civique (environ 70&nbsp;&euro;), les traductions par un traducteur agr&eacute;&eacute; et les apostilles. Notre article sur le <a href="/blog/cout-naturalisation-francaise-2026.html">co&ucirc;t complet de la naturalisation</a> d&eacute;taille chaque poste et les moyens de r&eacute;duire la facture.</p>

<p>Le poste le plus rentable reste la pr&eacute;paration&nbsp;: r&eacute;ussir le TCF et l'examen civique du premier coup, c'est 300&nbsp;&euro; et trois mois de gagn&eacute;s. L'application <a href="https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087" target="_blank">Naturalisation France Facile</a> vous y entra&icirc;ne (750&nbsp;exercices B2 corrig&eacute;s, 258&nbsp;questions civiques expliqu&eacute;es, examens blancs) et sa checklist de dossier place le timbre exactement o&ugrave; il doit &ecirc;tre&nbsp;: en derni&egrave;re ligne, une fois tout le reste coch&eacute;.</p>
""",
    "faq": [
        ("Combien coûte le timbre fiscal pour la naturalisation en 2026 ?",
         "255 € depuis le 1er mai 2026 (127,50 € en Guyane), contre 55 € auparavant. Le montant est le même pour la naturalisation par décret, la réintégration et les déclarations de nationalité par mariage, ascendant ou frère et sœur d'un Français."),
        ("Où acheter le timbre fiscal de naturalisation ?",
         "Pour une naturalisation ou une réintégration déposée en ligne, vous pouvez le payer directement dans la démarche sur l'ANEF. Sinon, achetez le timbre électronique « Nationalité française » sur timbres.impots.gouv.fr ou dans un bureau de tabac équipé de l'application Point de vente agréé. À l'étranger, la taxe se paie au consulat sous forme de droits de chancellerie."),
        ("Combien de temps le timbre fiscal est-il valable ?",
         "Un an à compter de la date d'achat. Achetez-le en dernier, une fois le dossier prêt, pour éviter qu'il n'expire avant le dépôt."),
        ("Le timbre fiscal est-il remboursable ?",
         "Oui, s'il n'a pas été utilisé : la demande de remboursement se fait en ligne dans les 18 mois suivant l'achat, avec la référence de transaction du justificatif. Un timbre consommé par un dépôt n'est pas remboursé, même si la demande est ensuite ajournée ou rejetée."),
        ("J'ai acheté un timbre à 55 € avant mai 2026 : puis-je l'utiliser ?",
         "Pas pour un dossier déposé depuis le 1er mai 2026 : la taxe due est celle en vigueur à la date du dépôt, soit 255 €. Demandez le remboursement du timbre à 55 € dans les 18 mois suivant son achat et achetez un timbre au nouveau montant, ou payez directement dans la démarche ANEF."),
        ("Faut-il un timbre pour chaque membre de la famille ?",
         "Un timbre par demande : un couple qui dépose deux dossiers paie deux timbres. Les enfants mineurs inscrits sur la demande d'un parent n'en paient pas, ils deviennent français par effet collectif."),
        ("Le timbre est-il exigé pour la déclaration par mariage ?",
         "Oui, 255 € (127,50 € en Guyane), comme pour la naturalisation. Il s'achète sur timbres.impots.gouv.fr ou chez un buraliste agréé et se joint au dossier de déclaration."),
        ("Que se passe-t-il si le timbre manque au dossier ?",
         "Le dossier est incomplet : pas de récépissé, donc pas de départ du délai légal, et une mise en demeure de fournir la pièce dans un délai fixé, faute de quoi la demande peut être classée sans suite."),
    ],
    "links": [
        ("/blog/cout-naturalisation-francaise-2026.html", "Co&ucirc;t de la naturalisation 2026&nbsp;: le budget poste par poste"),
        ("/blog/hausse-timbre-fiscal-naturalisation-mai-2026.html", "La hausse du timbre de 55 &agrave; 255&nbsp;&euro;&nbsp;: pourquoi et depuis quand"),
        ("/blog/documents-naturalisation.html", "La liste compl&egrave;te des pi&egrave;ces du dossier"),
        ("/blog/naturalisation-rapide.html", "Naturalisation rapide&nbsp;: d&eacute;poser un dossier complet du premier coup"),
        ("/glossaire/timbre-fiscal.html", "Timbre fiscal&nbsp;: la d&eacute;finition"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F32952", "Service-public.gouv.fr &mdash; Comment acheter un timbre fiscal pour une demande de nationalit&eacute; fran&ccedil;aise&nbsp;? (F32952)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret&nbsp;: prix de la d&eacute;marche, gratuit&eacute; hors timbre (F2213)"),
        ("https://timbres.impots.gouv.fr/", "Direction g&eacute;n&eacute;rale des finances publiques &mdash; Achat en ligne du timbre fiscal &eacute;lectronique"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F33430", "Service-public.gouv.fr &mdash; D&eacute;claration de l'ascendant d'un Fran&ccedil;ais&nbsp;: timbre de 255&nbsp;&euro; (F33430)"),
    ],
    "cta": "Pr&eacute;parer mon dossier complet avec l'app",
},
# ═══════════════════════════════════════════════════════════════════════
"journal-officiel-naturalisation-liste-des-noms": {
    "title": "Journal officiel naturalisation : trouver la liste des noms",
    "h1": "Journal officiel et naturalisation&nbsp;: comment trouver la liste des noms, et pourquoi Google ne l'affiche pas",
    "desc": "Les noms des naturalisés sont au JO, en accès protégé, non indexé par Google. Où les trouver : espace ANEF, extrait nominatif sur Légifrance, notre annuaire des décrets.",
    "og": "Journal officiel&nbsp;: trouver son nom dans un d&eacute;cret de naturalisation",
    "tag": "Apr&egrave;s l'obtention",
    "og_img": "suivi-relance.png",
    "date": "2026-09-17",
    "date_fr": "17 septembre 2026",
    "lede": "Chaque mois, des milliers de personnes tapent &laquo;&nbsp;journal officiel naturalisation liste des noms&nbsp;&raquo; et tombent sur des pages qui n'affichent aucun nom. Ce n'est pas un bug&nbsp;: la loi interdit que les d&eacute;crets de naturalisation soient index&eacute;s par les moteurs de recherche. Les noms existent pourtant, publi&eacute;s et t&eacute;l&eacute;chargeables gratuitement. Voici o&ugrave; ils sont, comment y acc&eacute;der en trois minutes, ce que contient un d&eacute;cret, et ce qu'il faut penser d'une absence.",
    "body": """
<h2>Pourquoi vous ne trouverez jamais la liste des noms sur Google</h2>

<p>Les d&eacute;crets de naturalisation sont publi&eacute;s au Journal officiel depuis 1924, et les d&eacute;crets r&eacute;cents sont sur L&eacute;gifrance. Mais le Code des relations entre le public et l'administration pose une r&egrave;gle claire (article L. 221-14)&nbsp;: &laquo;&nbsp;certains actes individuels, notamment relatifs &agrave; l'&eacute;tat et &agrave; la nationalit&eacute; des personnes, doivent &ecirc;tre publi&eacute;s dans des conditions garantissant qu'ils ne font pas l'objet d'une indexation par des moteurs de recherche&nbsp;&raquo;. L'article R. 221-15 en dresse la liste, et les d&eacute;crets de naturalisation et de r&eacute;int&eacute;gration y figurent express&eacute;ment.</p>

<p>Concr&egrave;tement, la page L&eacute;gifrance d'un d&eacute;cret de naturalisation affiche son titre, sa date, son num&eacute;ro NOR et la mention <strong>&laquo;&nbsp;acc&egrave;s prot&eacute;g&eacute;&nbsp;&raquo;</strong>. Les noms figurent dans un <strong>extrait nominatif au format PDF</strong>, accessible seulement apr&egrave;s un petit calcul anti-robot. Aucun moteur de recherche ne peut donc lire ni afficher cette liste, et aucun site s&eacute;rieux ne peut la republier. Les sites qui promettent une &laquo;&nbsp;liste des noms 2026 par mois&nbsp;&raquo; ne peuvent, au mieux, que vous renvoyer vers ces extraits.</p>

<div class="callout">
  <p><strong>&Agrave; retenir&nbsp;:</strong> la liste des noms existe, elle est officielle, gratuite et t&eacute;l&eacute;chargeable. Elle est simplement <em>invisible pour Google</em>, par choix du l&eacute;gislateur, pour prot&eacute;ger la vie priv&eacute;e des personnes naturalis&eacute;es.</p>
</div>

<h2>Trois fa&ccedil;ons de savoir si votre nom est dans un d&eacute;cret</h2>

<h3>1. Votre espace personnel ANEF, le plus rapide</h3>

<p>Depuis le 1<sup>er</sup> f&eacute;vrier 2023, service-public l'indique noir sur blanc&nbsp;: &laquo;&nbsp;la date de publication au JO du d&eacute;cret de naturalisation est communiqu&eacute;e sur votre compte personnel&nbsp;&raquo;. Vous recevez aussi un mail vous informant de votre inscription dans le d&eacute;cret, avec la date du d&eacute;cret et sa date de publication. Si vous avez d&eacute;pos&eacute; par courrier sans adresse &eacute;lectronique, l'information vous parvient par courrier. Pour lire les statuts qui pr&eacute;c&egrave;dent ce moment, voyez notre d&eacute;codage des <a href="/blog/statuts-anef-naturalisation.html">statuts ANEF</a>.</p>

<h3>2. Notre annuaire des d&eacute;crets, pour rep&eacute;rer les dates</h3>

<p>Notre <a href="/outils/decret-naturalisation.html">annuaire des d&eacute;crets de naturalisation</a> est mis &agrave; jour automatiquement &agrave; chaque parution, &agrave; partir des donn&eacute;es ouvertes du Journal officiel. Il liste les d&eacute;crets par date, avec le lien direct vers chaque page L&eacute;gifrance. Il ne contient aucun nom, la loi l'interdit&nbsp;; il vous fait gagner l'&eacute;tape la plus fastidieuse, retrouver le bon JO.</p>

<h3>3. L'extrait nominatif sur L&eacute;gifrance, la preuve officielle</h3>

<p>La proc&eacute;dure d&eacute;crite par service-public pour un d&eacute;cret publi&eacute; depuis 2016 tient en quatre gestes&nbsp;:</p>

<ol>
  <li>Sur L&eacute;gifrance, dans l'encart <strong>&laquo;&nbsp;Rechercher un JO&nbsp;&raquo;</strong>, indiquez la date de publication du JO recherch&eacute; (celle de votre espace ANEF, ou celle de notre annuaire).</li>
  <li>Sur la page qui s'affiche, cliquez sur le lien <strong>&laquo;&nbsp;Extrait du Journal officiel contenant les informations nominatives (acc&egrave;s prot&eacute;g&eacute;)&nbsp;&raquo;</strong>.</li>
  <li>R&eacute;solvez le captcha, un petit calcul.</li>
  <li>Cliquez sur <strong>&laquo;&nbsp;T&eacute;l&eacute;charger le document&nbsp;&raquo;</strong>, puis cherchez votre nom dans le PDF (Ctrl+F ou Cmd+F). V&eacute;rifiez aussi votre date et votre lieu de naissance&nbsp;: les homonymes sont fr&eacute;quents.</li>
</ol>

<p>Ce PDF a une <strong>valeur juridique &agrave; lui seul</strong>&nbsp;: il porte une signature &eacute;lectronique authentifi&eacute;e, et service-public pr&eacute;cise qu'&laquo;&nbsp;aucune proc&eacute;dure suppl&eacute;mentaire n'est n&eacute;cessaire&nbsp;&raquo;, pas m&ecirc;me une copie certifi&eacute;e conforme. C'est ce document que vous joindrez &agrave; vos premi&egrave;res d&eacute;marches de Fran&ccedil;ais.</p>

<h2>Ce que contient un d&eacute;cret de naturalisation</h2>

<p>Un d&eacute;cret est collectif&nbsp;: il porte &laquo;&nbsp;naturalisation, r&eacute;int&eacute;gration, francisation de noms et pr&eacute;noms et lib&eacute;ration de l'all&eacute;geance fran&ccedil;aise&nbsp;&raquo;, et regroupe des centaines de personnes. Pour chacune, il indique le nom (le cas &eacute;ch&eacute;ant francis&eacute;), les pr&eacute;noms, la date et le lieu de naissance, et la cat&eacute;gorie&nbsp;: <strong>NAT</strong> pour une naturalisation, <strong>REI</strong> pour une r&eacute;int&eacute;gration, <strong>EFF</strong> pour un enfant mineur devenu fran&ccedil;ais par effet collectif. Notre fiche <a href="/glossaire/nat-eff-rei.html">NAT, EFF, REI</a> d&eacute;taille ces codes.</p>

<p>Le d&eacute;cret <strong>prend effet &agrave; la date de sa signature</strong>&nbsp;: vous &ecirc;tes fran&ccedil;ais &agrave; cette date, avant m&ecirc;me la publication, qui rend la d&eacute;cision opposable et vous permet d'agir (carte d'identit&eacute;, passeport, inscription &eacute;lectorale).</p>

<h2>Le calendrier&nbsp;: quand paraissent les d&eacute;crets</h2>

<p>Il n'y a pas de date fixe. Les d&eacute;crets de naturalisation paraissent en g&eacute;n&eacute;ral <strong>une &agrave; trois fois par mois</strong>, souvent en seconde quinzaine, parfois plusieurs le m&ecirc;me jour. Entre la signature et la publication, comptez de quelques jours &agrave; quelques semaines. Et entre l'<a href="/blog/avis-favorable-naturalisation.html">avis favorable</a> de la pr&eacute;fecture et l'insertion dans un d&eacute;cret, le plus souvent de trois mois &agrave; un an, selon la file d'attente du minist&egrave;re.</p>

<table class="article-table">
  <thead><tr><th>Vous cherchez</th><th>O&ugrave; regarder</th><th>Ce que vous obtenez</th></tr></thead>
  <tbody>
    <tr><td>Savoir si vous &ecirc;tes naturalis&eacute;</td><td>Mail et espace ANEF</td><td>Date du d&eacute;cret et date de publication</td></tr>
    <tr><td>La liste des d&eacute;crets parus (2024, 2025, 2026)</td><td>Notre annuaire des d&eacute;crets</td><td>Dates et liens L&eacute;gifrance, sans noms</td></tr>
    <tr><td>La liste des noms d'un d&eacute;cret</td><td>Extrait nominatif sur L&eacute;gifrance (acc&egrave;s prot&eacute;g&eacute;)</td><td>PDF authentifi&eacute;, &agrave; conserver</td></tr>
    <tr><td>Un d&eacute;cret ant&eacute;rieur &agrave; 2016</td><td>L&eacute;gifrance, &laquo;&nbsp;version papier num&eacute;ris&eacute;e&nbsp;&raquo; du JO</td><td>PDF, authentifi&eacute; pour les JO depuis le 2 juin 2004</td></tr>
    <tr><td>Une naturalisation par mariage ou par d&eacute;claration</td><td>Nulle part au JO</td><td>La preuve est la d&eacute;claration enregistr&eacute;e</td></tr>
  </tbody>
</table>

<h2>Votre nom n'y est pas&nbsp;: ce que cela veut dire</h2>

<ul>
  <li><strong>Vous n'avez pas re&ccedil;u le mail d'inscription.</strong> Alors votre dossier n'est simplement pas encore ins&eacute;r&eacute; dans un d&eacute;cret&nbsp;: les dossiers valid&eacute;s sont r&eacute;partis sur plusieurs d&eacute;crets successifs. Ce n'est pas un refus&nbsp;; un refus ou un ajournement vous serait notifi&eacute;, avec des voies de recours.</li>
  <li><strong>Vous avez re&ccedil;u le mail mais ne trouvez pas votre nom.</strong> V&eacute;rifiez la date exacte du JO (il peut y avoir plusieurs d&eacute;crets ce jour-l&agrave;), cherchez votre nom tel qu'il figure &agrave; l'&eacute;tat civil, et pensez &agrave; la francisation si vous l'avez demand&eacute;e.</li>
  <li><strong>Vous &ecirc;tes pass&eacute; par le mariage ou une d&eacute;claration.</strong> Ces acquisitions ne sont pas publi&eacute;es au JO&nbsp;; votre preuve est l'exemplaire enregistr&eacute; de votre d&eacute;claration.</li>
  <li><strong>Une erreur s'est gliss&eacute;e</strong> dans votre nom, vos pr&eacute;noms ou votre date de naissance&nbsp;: elle n'annule pas la naturalisation. Un t&eacute;l&eacute;service permet de demander la rectification du d&eacute;cret&nbsp;; une erreur d'&eacute;tat civil se signale au <a href="/glossaire/scec.html">Service central d'&eacute;tat civil</a> de Nantes.</li>
</ul>

<p>Si vous avez perdu la notification d'un d&eacute;cret ancien, vous pouvez demander les dates au minist&egrave;re de l'Int&eacute;rieur (sous-direction de l'acc&egrave;s &agrave; la nationalit&eacute; fran&ccedil;aise, &agrave; Rez&eacute;), par courrier ou par mail.</p>

<h2>Et apr&egrave;s la publication</h2>

<p>T&eacute;l&eacute;chargez et conservez l'extrait nominatif&nbsp;: c'est votre premi&egrave;re preuve de nationalit&eacute;. Le <a href="/glossaire/scec.html">SCEC</a> &eacute;tablit ensuite votre acte de naissance fran&ccedil;ais, &agrave; partir duquel s'encha&icirc;nent la carte d'identit&eacute;, le passeport et l'inscription sur les listes &eacute;lectorales&nbsp;; nos <a href="/blog/demarches-apres-naturalisation.html">d&eacute;marches des six premiers mois</a> donnent l'ordre &agrave; respecter. La <a href="/blog/ceremonie-naturalisation-que-se-passe-t-il.html">c&eacute;r&eacute;monie d'accueil</a> vient dans les six mois, sur convocation de la pr&eacute;fecture. Enfin, sachez que le d&eacute;cret peut &ecirc;tre retir&eacute; dans les deux ans suivant sa publication si l'administration constate que les conditions n'&eacute;taient pas remplies, ou en cas de fraude&nbsp;: rien d'inqui&eacute;tant pour un dossier sinc&egrave;re.</p>

<p>Beaucoup de lecteurs de cette page n'en sont pas l&agrave;&nbsp;: ils attendent, et cherchent la liste pour tromper l'attente. Le plus utile, entre-temps, est de suivre les bonnes &eacute;ch&eacute;ances et de pr&eacute;parer la suite. L'application <a href="https://apps.apple.com/fr/app/naturalisation-france-facile/id6761140087" target="_blank">Naturalisation France Facile</a> calcule vos d&eacute;lais &agrave; partir du r&eacute;c&eacute;piss&eacute;, vous indique quand une relance est justifi&eacute;e, et sa checklist pr&eacute;pare d&eacute;j&agrave; les d&eacute;marches d'apr&egrave;s-d&eacute;cret&nbsp;; pour ceux qui n'ont pas encore d&eacute;pos&eacute;, elle r&eacute;unit la pr&eacute;paration du B2, de l'examen civique et de l'entretien, ce qui d&eacute;cide de tout le reste.</p>
""",
    "faq": [
        ("Où trouver la liste des noms des naturalisés au Journal officiel ?",
         "Dans l'extrait nominatif de chaque décret, sur Légifrance : recherchez le JO par sa date de publication, cliquez sur « Extrait du Journal officiel contenant les informations nominatives (accès protégé) », résolvez le calcul anti-robot et téléchargez le PDF. Cette liste n'est pas indexée par les moteurs de recherche, en application de l'article L. 221-14 du Code des relations entre le public et l'administration."),
        ("Pourquoi la liste des noms n'apparaît-elle pas sur Google ?",
         "Parce que la loi impose que les actes individuels relatifs à la nationalité soient publiés dans des conditions garantissant qu'ils ne sont pas indexés par les moteurs de recherche. Les noms sont donc dans un PDF en accès protégé, invisible pour Google et impossible à republier légalement."),
        ("Comment savoir si mon nom est dans un décret de naturalisation ?",
         "Par votre espace personnel ANEF, qui communique depuis le 1er février 2023 la date de publication de votre décret, et par le mail d'inscription que vous recevez après la publication. Vous pouvez ensuite télécharger l'extrait nominatif sur Légifrance et y chercher votre nom, votre date et votre lieu de naissance."),
        ("Le PDF de Légifrance a-t-il une valeur juridique ?",
         "Oui. Pour les décrets publiés depuis 2016, l'extrait nominatif porte une signature électronique authentifiée : aucune procédure supplémentaire ni copie certifiée conforme n'est nécessaire. C'est votre première preuve de nationalité, à conserver."),
        ("Quand sont publiés les décrets de naturalisation ?",
         "Sans date fixe, en général une à trois fois par mois, souvent en seconde quinzaine, parfois plusieurs décrets le même jour. Entre l'avis favorable de la préfecture et l'insertion dans un décret, comptez le plus souvent de trois mois à un an."),
        ("Mon nom n'est pas dans le décret : est-ce un refus ?",
         "Non. Un refus ou un ajournement vous est notifié avec des voies de recours. Si vous n'avez pas reçu de mail d'inscription, votre dossier n'est pas encore inséré dans un décret : les dossiers validés sont répartis sur plusieurs décrets successifs."),
        ("La naturalisation par mariage est-elle publiée au Journal officiel ?",
         "Non. Seules les acquisitions par décret (naturalisation, réintégration, effet collectif) sont publiées. La nationalité acquise par déclaration (mariage, ascendant, frère ou sœur d'un Français) se prouve par l'exemplaire enregistré de la déclaration."),
        ("Il y a une erreur dans mon nom sur le décret : que faire ?",
         "L'erreur n'annule pas la naturalisation. Demandez la rectification du décret via le téléservice dédié (ou par courrier au ministère de l'Intérieur si vous aviez déposé un dossier papier) ; une erreur sur un acte d'état civil se signale au Service central d'état civil de Nantes."),
    ],
    "links": [
        ("/outils/decret-naturalisation.html", "Annuaire des d&eacute;crets de naturalisation au JO, mis &agrave; jour &agrave; chaque parution"),
        ("/blog/avis-favorable-naturalisation.html", "Avis favorable&nbsp;: ce qui se passe avant le d&eacute;cret"),
        ("/blog/demarches-apres-naturalisation.html", "Vous &ecirc;tes fran&ccedil;ais&nbsp;: les d&eacute;marches des 6 premiers mois"),
        ("/blog/ceremonie-naturalisation-que-se-passe-t-il.html", "La c&eacute;r&eacute;monie d'accueil&nbsp;: convocation et d&eacute;roulement"),
        ("/glossaire/nat-eff-rei.html", "NAT, EFF, REI&nbsp;: lire les codes d'un d&eacute;cret"),
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F33626", "Service-public.gouv.fr &mdash; Comment trouver son d&eacute;cret de naturalisation publi&eacute; au Journal officiel&nbsp;? (F33626)"),
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret&nbsp;: inscription dans le d&eacute;cret, effet, rectification, retrait (F2213)"),
        ("https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031677770", "L&eacute;gifrance &mdash; Code des relations entre le public et l'administration, article L. 221-14"),
        ("https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031677698", "L&eacute;gifrance &mdash; CRPA, article R. 221-15 (liste des actes non indexables, dont les d&eacute;crets de naturalisation)"),
        ("https://www.legifrance.gouv.fr/jorf/jo", "L&eacute;gifrance &mdash; Journal officiel&nbsp;: derniers num&eacute;ros et navigation par date"),
    ],
    "cta": "Suivre mon dossier jusqu'au d&eacute;cret avec l'app",
},
}


def clean(text):
    """Entites HTML -> caracteres reels, pour le JSON-LD."""
    return html.unescape(re.sub(r"<[^>]+>", "", text)).replace(" ", " ").strip()


def render(slug, a):
    url = f"{BASE}/blog/{slug}.html"
    article_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "inLanguage": "fr-FR",
        "isAccessibleForFree": True,
        "copyrightYear": 2026,
        "copyrightHolder": {"@type": "Organization", "name": "Naturalisation France Facile", "url": BASE},
        "creditText": "Naturalisation France Facile — naturalisationfrancefacile.fr",
        "license": f"{BASE}/mentions-legales.html",
        "headline": clean(a["h1"]),
        "description": a["desc"],
        "url": url,
        "datePublished": a.get("date", TODAY),
        "dateModified": a.get("date", TODAY),
        "author": {"@type": "Person", "name": "Augusto Grone", "url": f"{BASE}/a-propos.html"},
        "publisher": {"@type": "Organization", "name": "Naturalisation France Facile", "url": BASE},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{BASE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": clean(a["h1"])},
        ],
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": ans}}
            for q, ans in a["faq"]
        ],
    }

    def ld(obj):
        return ('  <script type="application/ld+json">\n  '
                + json.dumps(obj, ensure_ascii=False, indent=2).replace("\n", "\n  ")
                + "\n  </script>\n")

    faq_html = "\n".join(
        f"      <h3>{html.escape(q, quote=False)}</h3>\n      <p>{html.escape(ans, quote=False)}</p>"
        for q, ans in a["faq"]
    )
    links_html = "\n".join(f'        <li><a href="{h}">{t}</a></li>' for h, t in a["links"])
    sources_html = "\n".join(
        f'        <li><a href="{h}" target="_blank" rel="noopener">{t}</a></li>' for h, t in a["sources"]
    )

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
  <title>{a["title"]}</title>
  <meta name="description" content="{a["desc"]}" />
  <link rel="canonical" href="{url}" />
  <meta property="og:title" content="{a["og"]}" />
  <meta property="og:description" content="{a["desc"]}" />
  <meta property="og:url" content="{url}" />
  <meta property="og:type" content="article" />
  <meta property="og:locale" content="fr_FR" />
  <meta property="og:site_name" content="Naturalisation France Facile" />
  <meta property="og:image" content="{BASE}/img/og/{a["og_img"]}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:image" content="{BASE}/img/og/{a["og_img"]}" />
  <link rel="stylesheet" href="/css/style.css?v=24" />
{ld(article_ld)}{ld(breadcrumb_ld)}{ld(faq_ld)}</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="nav-logo">Naturalisation <span>France Facile</span></a>
    <button class="nav-toggle" aria-label="Menu" onclick="document.querySelector('.nav-links').classList.toggle('open')">&#9776;</button>
    <div class="nav-links">
      <a href="/#fonctionnalites">Fonctionnalit&eacute;s</a>
      <a href="/outils/examen-civique.html">Examen civique</a>
      <a href="/prefectures/">Pr&eacute;fectures</a>
      <a href="/outils/">Outils</a>
      <a href="/faq.html">FAQ</a>
      <a href="/glossaire/">Glossaire</a>
      <a href="/blog/">Blog</a>
      <a href="{APP}" class="nav-cta" target="_blank">T&eacute;l&eacute;charger</a>
    </div>
  </div>
</nav>

<article class="section" style="padding-top:120px">
  <p class="article-back"><a href="/blog/">&larr; Retour au blog</a></p>
  <h1 class="section-title">{a["h1"]}</h1>
  <p class="article-meta" style="text-align:center">Mis &agrave; jour le {a.get("date_fr", TODAY_FR)} &middot; {a["tag"]}</p>

  <div class="article-body">
    <p class="article-lede">{a["lede"]}</p>
{a["body"]}
    <h2>Questions fr&eacute;quentes</h2>
{faq_html}

    <h2>Pour aller plus loin</h2>
    <ul>
{links_html}
    </ul>

    <h2>Sources officielles</h2>
    <ul>
{sources_html}
    </ul>
  </div>

  <div style="max-width:680px;margin:36px auto 0;text-align:center">
    <a class="cta-btn" href="{APP}" target="_blank">{APP_SVG} {a["cta"]}</a>
  </div>
</article>

<footer class="footer">
  <div class="footer-links"><a href="/faq.html">FAQ</a><a href="/">Accueil</a><a href="/blog/">Blog</a><a href="/glossaire/">Glossaire</a><a href="/a-propos.html">&Agrave; propos</a><a href="/mentions-legales.html">Mentions l&eacute;gales</a><a href="/politique-confidentialite.html">Confidentialit&eacute;</a><a href="mailto:contact@naturalisationfrancefacile.fr">Contact</a></div>
  <div class="footer-social"><a href="https://www.youtube.com/channel/UCrMQy14hPp2j0xPYn0lLlXQ" target="_blank" rel="noopener" aria-label="YouTube">{YT_SVG}</a><a href="https://www.tiktok.com/@naturalisation.france" target="_blank" rel="noopener" aria-label="TikTok">{TT_SVG}</a></div>
  <p class="footer-sources">Sources officielles&nbsp;: <a href="https://www.service-public.gouv.fr/particuliers/vosdroits/N111" target="_blank" rel="noopener">Service-Public</a> &middot; <a href="https://www.legifrance.gouv.fr" target="_blank" rel="noopener">L&eacute;gifrance</a> &middot; <a href="https://www.interieur.gouv.fr" target="_blank" rel="noopener">Minist&egrave;re de l'Int&eacute;rieur</a> &middot; <a href="https://administration-etrangers-en-france.interieur.gouv.fr" target="_blank" rel="noopener">ANEF</a></p>
  <p class="footer-copy">&copy; 2026 Naturalisation France Facile &middot; Informations &agrave; titre indicatif, sans valeur de conseil juridique &middot; Site ind&eacute;pendant, non affili&eacute; &agrave; l'administration.</p>
</footer>
</body></html>
"""


def main():
    for slug, a in ARTICLES.items():
        page = render(slug, a)
        (BLOG / f"{slug}.html").write_text(page, encoding="utf-8")
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
            json.loads(block)
            assert not re.search(r"&[a-zA-Z]{2,8};", block), f"entite HTML dans le JSON-LD de {slug}"
        body = re.sub(r"<script.*?</script>|<nav.*?</nav>|<footer.*?</footer>", "", page, flags=re.S)
        words = len(re.sub(r"<[^>]+>", " ", body).split())
        assert len(a["title"]) <= 62, f"title trop long ({len(a['title'])}) : {slug}"
        assert 110 <= len(a["desc"]) <= 170, f"description hors bornes ({len(a['desc'])}) : {slug}"
        print(f"  {words:5} mots · T{len(a['title']):3} · D{len(a['desc']):3} · {len(a['faq'])} Q · blog/{slug}.html")
    print(f"{len(ARTICLES)} articles generes")


if __name__ == "__main__":
    main()
