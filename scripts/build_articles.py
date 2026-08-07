#!/usr/bin/env python3
"""Genere les articles de blog a partir du dictionnaire ARTICLES.

Les cinq premiers articles ont ete choisis sur les donnees Search Console
(6 mois au 7 aout 2026), en cherchant les intentions ou le site apparait
deja sans satisfaire personne, ou bien n'apparait pas du tout alors que
l'etape existe dans le parcours.

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

<p>Sur la base du dossier complet et du compte rendu, la pr&eacute;fecture formule un <strong>avis</strong>&nbsp;: favorable, favorable avec r&eacute;serves, ou d&eacute;favorable. Cet avis n'est pas la d&eacute;cision finale, mais il p&egrave;se lourd&nbsp;: le minist&egrave;re suit g&eacute;n&eacute;ralement la recommandation locale.</p>

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
  <li><strong>Favorable</strong> &mdash; il n'y a g&eacute;n&eacute;ralement pas de courrier annon&ccedil;ant &laquo;&nbsp;c'est accept&eacute;&nbsp;&raquo;. Ce que vous verrez, c'est la parution de votre d&eacute;cret. Depuis f&eacute;vrier 2023, l'espace ANEF signale automatiquement cette publication&nbsp;; vous pouvez aussi la v&eacute;rifier dans l'<a href="/outils/decret-naturalisation.html">annuaire des d&eacute;crets publi&eacute;s au Journal officiel</a>. La pr&eacute;fecture vous convoque ensuite &agrave; la <a href="/blog/ceremonie-naturalisation-que-se-passe-t-il.html">c&eacute;r&eacute;monie d'accueil</a>.</li>
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

<p>En pratique, il vous faut n&eacute;anmoins une <strong>preuve</strong> pour engager les d&eacute;marches&nbsp;: l'ampliation de votre d&eacute;cret, remise le plus souvent lors de la c&eacute;r&eacute;monie, ou r&eacute;cup&eacute;rable aupr&egrave;s de votre pr&eacute;fecture.</p>

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

<p>Votre naturalisation ne lui transmet rien automatiquement&nbsp;: l'effet collectif ne concerne que les enfants mineurs. En revanche, elle lui ouvre une voie&nbsp;: la <a href="/blog/naturalisation-par-mariage-2026.html">d&eacute;claration de nationalit&eacute; &agrave; raison du mariage</a>, sous conditions de dur&eacute;e de mariage et de communaut&eacute; de vie. Le niveau B2 et l'examen civique s'appliquent l&agrave; aussi.</p>
""",
    "faq": [
        ("Quelles démarches faire juste après la naturalisation ?",
         "Dans cet ordre : demander votre acte de naissance français au Service central d'état civil de Nantes si vous êtes né à l'étranger, puis la carte nationale d'identité, puis le passeport, puis l'inscription sur les listes électorales. Chaque étape dépend de la précédente : l'acte de naissance conditionne tout le reste."),
        ("Faut-il attendre la cérémonie pour commencer les démarches ?",
         "Non. Le décret prend effet à la date de sa signature : vous êtes français avant la cérémonie. Il vous faut néanmoins une preuve — l'ampliation du décret — que vous récupérez à la cérémonie ou auprès de votre préfecture."),
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
         "Non, l'effet collectif ne concerne que les enfants mineurs. Votre conjoint peut en revanche engager une déclaration de nationalité à raison du mariage, sous conditions de durée de mariage et de communauté de vie — avec, là aussi, le niveau B2 et l'examen civique."),
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
    ],
    "sources": [
        ("https://www.service-public.gouv.fr/particuliers/vosdroits/F2213", "Service-public.gouv.fr &mdash; Naturalisation par d&eacute;cret (F2213)"),
        ("https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070721/LEGISCTA000006149926/", "Code civil &mdash; Acquisition de la nationalit&eacute; fran&ccedil;aise"),
    ],
    "cta": "Pr&eacute;parer mon dossier avec l'app",
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
        "datePublished": TODAY,
        "dateModified": TODAY,
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
  <link rel="stylesheet" href="/css/style.css?v=23" />
{ld(article_ld)}{ld(breadcrumb_ld)}{ld(faq_ld)}</head>
<body>

<nav class="nav">
  <div class="nav-inner">
    <a href="/" class="nav-logo">Naturalisation <span>France Facile</span></a>
    <button class="nav-toggle" aria-label="Menu" onclick="document.querySelector('.nav-links').classList.toggle('open')">&#9776;</button>
    <div class="nav-links">
      <a href="/#fonctionnalites">Fonctionnalit&eacute;s</a>
      <a href="/outils/examen-civique.html">Examen civique</a>
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
  <p class="article-meta" style="text-align:center">Mis &agrave; jour le {TODAY_FR} &middot; {a["tag"]}</p>

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
