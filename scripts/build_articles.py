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
