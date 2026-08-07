#!/usr/bin/env python3
"""Regenere le corps des fiches du glossaire.

Les 13 fiches faisaient 76 a 182 mots : Google les explorait et decidait
qu'elles n'apportaient rien (10 sur 13 n'ont eu aucune impression en trois
mois). Ce script reecrit le bloc <main> de chaque fiche a partir du
dictionnaire TERMS ci-dessous, avec une structure constante :

    Definition / Ou vous le rencontrez / Ce qu'il faut faire /
    Erreurs frequentes / Questions frequentes (FAQPage) / Termes lies

Seul le <main> est remplace : head, nav, banniere et footer des fichiers
existants sont conserves tels quels.

    python3 scripts/build_glossaire.py
"""

import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GLOSSAIRE = ROOT / "glossaire"

# Chaque entree : sigle developpe, definition, rencontres, actions,
# erreurs, faq (question -> reponse), liens internes, termes lies.
TERMS = {
    "anef": {
        "long": "Administration Num&eacute;rique des &Eacute;trangers en France",
        "def": [
            "L'ANEF est le portail en ligne du minist&egrave;re de l'Int&eacute;rieur par lequel passent d&eacute;sormais la quasi-totalit&eacute; des d&eacute;marches des &eacute;trangers en France, dont la demande de naturalisation. Elle a remplac&eacute; les guichets physiques de pr&eacute;fecture pour le d&eacute;p&ocirc;t et le suivi des dossiers.",
            "Concr&egrave;tement, c'est l&agrave; que vous cr&eacute;ez votre compte, t&eacute;l&eacute;versez vos pi&egrave;ces justificatives, suivez l'avancement de votre demande et recevez les d&eacute;cisions de l'administration.",
        ],
        "where": [
            "Au moment du d&eacute;p&ocirc;t : tout le dossier de naturalisation se constitue en ligne, pi&egrave;ce par pi&egrave;ce.",
            "Pendant l'instruction : la rubrique &laquo;&nbsp;Mon dossier&nbsp;&raquo; affiche un statut qui &eacute;volue &agrave; chaque &eacute;tape.",
            "Pour les demandes de compl&eacute;ment : la pr&eacute;fecture y d&eacute;pose ses demandes de pi&egrave;ces, avec un d&eacute;lai de r&eacute;ponse.",
            "&Agrave; la fin : depuis le 1<sup>er</sup>&nbsp;f&eacute;vrier 2023, l'ANEF signale la publication de votre d&eacute;cret au Journal officiel. C'est la seule notification automatique officielle qui existe.",
        ],
        "do": [
            "Consultez votre espace au moins une fois par mois, m&ecirc;me sans notification : les e-mails d'alerte finissent parfois en spam.",
            "Gardez l'adresse e-mail de votre compte accessible pendant toute la proc&eacute;dure &mdash; elle sert &agrave; la r&eacute;initialisation du mot de passe et aux notifications.",
            "Signalez tout changement d'adresse postale : c'est la premi&egrave;re cause de convocation jamais re&ccedil;ue.",
        ],
        "errors": [
            "Croire qu'un statut fig&eacute; signifie un dossier bloqu&eacute;. Un dossier peut rester des mois sur le m&ecirc;me libell&eacute; pendant l'enqu&ecirc;te administrative, sans que rien n'aille mal.",
            "Cr&eacute;er un deuxi&egrave;me compte apr&egrave;s avoir perdu ses identifiants : cela cr&eacute;e des doublons difficiles &agrave; d&eacute;m&ecirc;ler. Passez par la r&eacute;cup&eacute;ration de compte.",
            "T&eacute;l&eacute;verser des scans illisibles ou partiels : c'est le motif de demande de compl&eacute;ment le plus fr&eacute;quent, et chaque aller-retour co&ucirc;te des semaines.",
        ],
        "faq": [
            ("L'ANEF pr&eacute;vient-elle quand le d&eacute;cret est publi&eacute; ?",
             "Oui. Depuis le 1er f&eacute;vrier 2023, l'espace &laquo; Mon dossier &raquo; signale la publication de votre d&eacute;cret de naturalisation au Journal officiel. C'est la seule notification automatique officielle."),
            ("Que faire si mon statut ANEF ne bouge plus depuis des mois ?",
             "C'est fr&eacute;quent et rarement inqui&eacute;tant : l'enqu&ecirc;te administrative et le passage d'un service &agrave; l'autre ne changent pas toujours le libell&eacute; affich&eacute;. Si le d&eacute;lai l&eacute;gal d'instruction est d&eacute;pass&eacute;, vous pouvez relancer la pr&eacute;fecture par &eacute;crit."),
            ("Peut-on encore d&eacute;poser un dossier papier ?",
             "Non, sauf exceptions pr&eacute;vues par l'administration. La demande de naturalisation par d&eacute;cret se d&eacute;pose via l'ANEF."),
        ],
        "links": [("/blog/suivre-dossier-naturalisation-anef.html", "Suivre son dossier sur l'ANEF, statut par statut"),
                  ("/blog/statuts-anef-naturalisation.html", "Que signifie chaque statut ANEF")],
        "related": ["sdanf", "agdref", "jorf"],
    },
    "rapo": {
        "long": "Recours Administratif Pr&eacute;alable Obligatoire",
        "def": [
            "Le RAPO est le recours que vous devez adresser au ministre charg&eacute; des naturalisations avant de pouvoir saisir le juge, pour contester un refus, un ajournement ou une irrecevabilit&eacute;. Il est pr&eacute;vu par l'<strong>article 45 du d&eacute;cret n&deg;&nbsp;93-1362</strong>.",
            "Sa particularit&eacute; tient dans son nom : il est <em>pr&eacute;alable</em> et <em>obligatoire</em>. Saisir directement le tribunal administratif sans avoir fait de RAPO rend votre requ&ecirc;te irrecevable, quel que soit le bien-fond&eacute; de vos arguments.",
        ],
        "where": [
            "Apr&egrave;s la notification d'une d&eacute;cision d&eacute;favorable : refus, ajournement avec d&eacute;lai impos&eacute;, ou irrecevabilit&eacute;.",
            "Le d&eacute;lai est de <strong>deux mois &agrave; compter de la notification</strong>. Pass&eacute; ce d&eacute;lai, la d&eacute;cision devient d&eacute;finitive.",
            "Le recours s'adresse au ministre charg&eacute; des naturalisations, <strong>&agrave; l'exclusion de tout autre recours administratif</strong> : il n'y a pas de recours gracieux distinct &agrave; tenter en parall&egrave;le.",
        ],
        "do": [
            "Notez la date exacte de notification : c'est elle qui fait courir les deux mois, pas la date de la d&eacute;cision.",
            "Exposez les <strong>motifs</strong> pour lesquels vous demandez le r&eacute;examen : le texte l'exige. R&eacute;pondez point par point aux motifs de la d&eacute;cision, pi&egrave;ces &agrave; l'appui.",
            "Vous pouvez vous faire <strong>assister ou repr&eacute;senter par toute personne de votre choix</strong> &mdash; ce n'est pas r&eacute;serv&eacute; aux avocats.",
            "Depuis le d&eacute;cret n&deg;&nbsp;2025-648 du 15&nbsp;juillet 2025, le RAPO se d&eacute;pose via le t&eacute;l&eacute;service utilis&eacute; pour la demande initiale.",
        ],
        "errors": [
            "Attendre la r&eacute;ponse ind&eacute;finiment. Le <strong>silence du ministre pendant plus de quatre mois vaut rejet</strong> : c'est &agrave; partir de ce rejet implicite que court votre d&eacute;lai pour saisir le tribunal administratif.",
            "Envoyer un courrier qui conteste la d&eacute;cision sans exposer de motifs ni produire de pi&egrave;ces nouvelles : le r&eacute;examen n'aura aucune raison d'aboutir.",
            "Laisser passer les deux mois en pr&eacute;parant un dossier parfait. Un RAPO d&eacute;pos&eacute; dans les d&eacute;lais, m&ecirc;me perfectible, vaut mieux qu'un dossier irr&eacute;prochable hors d&eacute;lai.",
        ],
        "faq": [
            ("Le RAPO est-il obligatoire avant le tribunal administratif ?",
             "Oui. L'article 45 du d&eacute;cret n&deg; 93-1362 en fait un pr&eacute;alable obligatoire au recours contentieux, &agrave; peine d'irrecevabilit&eacute; de ce dernier."),
            ("Combien de temps le ministre a-t-il pour r&eacute;pondre ?",
             "Le silence gard&eacute; pendant plus de quatre mois vaut d&eacute;cision de rejet. Vous pouvez alors saisir le tribunal administratif."),
            ("Faut-il un avocat pour faire un RAPO ?",
             "Non. Le texte pr&eacute;voit que le demandeur peut &ecirc;tre assist&eacute; ou repr&eacute;sent&eacute; par toute personne de son choix. Un avocat reste utile si les motifs de refus sont juridiquement complexes."),
        ],
        "links": [("/blog/ajournement-vs-refus-naturalisation.html", "Ajournement, refus, irrecevabilit&eacute; : que faire"),
                  ("/blog/relance-naturalisation-que-faire-sans-reponse.html", "Relancer un dossier sans r&eacute;ponse")],
        "related": ["sdanf", "anef"],
    },
    "sdanf": {
        "long": "Sous-Direction de l'Acc&egrave;s &agrave; la Nationalit&eacute; Fran&ccedil;aise",
        "def": [
            "La SDANF est le service du minist&egrave;re de l'Int&eacute;rieur qui instruit les demandes de naturalisation au niveau national, apr&egrave;s le travail de la pr&eacute;fecture. C'est elle qui pr&eacute;pare la d&eacute;cision finale et les d&eacute;crets soumis &agrave; signature.",
            "Elle est bas&eacute;e &agrave; <strong>Rez&eacute;</strong>, en Loire-Atlantique, et <strong>ne re&ccedil;oit pas de public</strong> : aucun d&eacute;placement sur place n'est possible.",
        ],
        "where": [
            "Apr&egrave;s l'instruction en pr&eacute;fecture : votre dossier lui est transmis avec l'avis du pr&eacute;fet.",
            "Sur les courriers de d&eacute;cision : refus, ajournement et irrecevabilit&eacute; portent son en-t&ecirc;te.",
            "Dans le circuit du RAPO : c'est &agrave; ce niveau qu'est instruit le recours adress&eacute; au ministre.",
        ],
        "do": [
            "&Eacute;crivez &agrave; la SDANF uniquement pour ce qui rel&egrave;ve d'elle : tant que votre dossier est en pr&eacute;fecture, c'est la pr&eacute;fecture qui r&eacute;pond. &Eacute;crire aux deux en m&ecirc;me temps n'acc&eacute;l&egrave;re rien.",
            "Rappelez toujours votre num&eacute;ro de dossier et votre num&eacute;ro AGDREF dans vos courriers : sans eux, votre demande ne peut pas &ecirc;tre rattach&eacute;e &agrave; un dossier.",
            "Le service &eacute;tant &agrave; Rez&eacute; et ne recevant pas de public, tout passe par &eacute;crit ou par le t&eacute;l&eacute;service. Privil&eacute;giez la lettre recommand&eacute;e avec accus&eacute; de r&eacute;ception lorsqu'un d&eacute;lai court.",
        ],
        "errors": [
            "Se d&eacute;placer &agrave; Rez&eacute; : le service ne re&ccedil;oit pas de public, aucun guichet n'y est ouvert.",
            "Relancer la SDANF alors que le dossier n'a pas encore quitt&eacute; la pr&eacute;fecture : la relance n'aboutira nulle part et vous fait perdre du temps.",
            "Multiplier les relances rapproch&eacute;es. Un courrier tous les deux &agrave; trois mois, argument&eacute; et r&eacute;f&eacute;renc&eacute;, p&egrave;se plus que dix e-mails.",
        ],
        "faq": [
            ("O&ugrave; se trouve la SDANF ?",
             "&Agrave; Rez&eacute;, en Loire-Atlantique. Le service ne re&ccedil;oit pas de public : les &eacute;changes se font par courrier ou par le t&eacute;l&eacute;service."),
            ("Quelle diff&eacute;rence entre la pr&eacute;fecture et la SDANF ?",
             "La pr&eacute;fecture re&ccedil;oit votre dossier, m&egrave;ne l'entretien d'assimilation et donne un avis. La SDANF instruit ensuite au niveau national et pr&eacute;pare la d&eacute;cision. Tant que le dossier est en pr&eacute;fecture, c'est &agrave; elle qu'il faut &eacute;crire."),
            ("&Agrave; quel moment mon dossier arrive-t-il &agrave; la SDANF ?",
             "Apr&egrave;s l'instruction locale et l'entretien d'assimilation, quand la pr&eacute;fecture transmet le dossier avec l'avis du pr&eacute;fet. Ce passage n'est pas toujours refl&eacute;t&eacute; par un changement de statut visible dans votre espace en ligne."),
        ],
        "links": [("/blog/delais-naturalisation-2026.html", "Les d&eacute;lais &eacute;tape par &eacute;tape"),
                  ("/blog/relance-naturalisation-que-faire-sans-reponse.html", "&Agrave; qui &eacute;crire, et quand")],
        "related": ["rapo", "anef", "scec"],
    },
    "tcf-irn": {
        "long": "Test de Connaissance du Fran&ccedil;ais &mdash; Int&eacute;gration, R&eacute;sidence, Nationalit&eacute;",
        "def": [
            "Le TCF IRN est le test de fran&ccedil;ais con&ccedil;u sp&eacute;cifiquement pour les d&eacute;marches d'int&eacute;gration, de titre de s&eacute;jour et de nationalit&eacute;. C'est la voie la plus utilis&eacute;e pour prouver son niveau dans un dossier de naturalisation.",
            "Il &eacute;value quatre comp&eacute;tences : compr&eacute;hension orale, compr&eacute;hension &eacute;crite, expression orale et expression &eacute;crite. Depuis le 1<sup>er</sup>&nbsp;janvier 2026, le niveau exig&eacute; pour la naturalisation est le <strong>B2</strong>.",
        ],
        "where": [
            "Au moment de constituer le dossier : l'attestation fait partie des pi&egrave;ces obligatoires.",
            "Dans les centres agr&eacute;&eacute;s : le test se passe uniquement dans un centre habilit&eacute;, sur inscription.",
        ],
        "do": [
            "V&eacute;rifiez la <strong>validit&eacute; de deux ans</strong> avant de d&eacute;poser : une attestation p&eacute;rim&eacute;e au moment du d&eacute;p&ocirc;t rend le dossier incomplet.",
            "Comparez les tarifs entre centres de votre r&eacute;gion : ils varient sensiblement pour un test identique.",
            "Pr&eacute;voyez le d&eacute;lai de r&eacute;sultat (environ quatre semaines) dans votre calendrier de d&eacute;p&ocirc;t.",
        ],
        "errors": [
            "Confondre le TCF IRN avec les autres versions du TCF : seule la version IRN est adapt&eacute;e &agrave; ces d&eacute;marches.",
            "Passer le test trop t&ocirc;t. Deux ans de validit&eacute; peuvent expirer pendant la constitution d'un dossier qui prend des mois.",
            "N&eacute;gliger l'expression &eacute;crite. C'est l'&eacute;preuve o&ugrave; l'&eacute;cart entre B1 et B2 se creuse le plus, et celle qui fait le plus souvent manquer le niveau.",
        ],
        "faq": [
            ("Quelle est la diff&eacute;rence entre le TCF IRN et le DELF B2 ?",
             "Le TCF IRN est un test dont l'attestation vaut deux ans ; le DELF B2 est un dipl&ocirc;me valable &agrave; vie. Le DELF co&ucirc;te g&eacute;n&eacute;ralement moins cher mais s'organise &agrave; dates fixes."),
            ("Le TCF IRN est-il valable combien de temps ?",
             "Deux ans. C'est la date de d&eacute;p&ocirc;t du dossier qui compte, pas la date de la d&eacute;cision."),
            ("Peut-on repasser le TCF IRN si le niveau B2 n'est pas atteint ?",
             "Oui, il n'y a pas de limite au nombre de tentatives. Chaque passage est payant, d'o&ugrave; l'int&eacute;r&ecirc;t de se situer avec un test blanc avant de s'inscrire."),
        ],
        "links": [("/blog/tcf-irn-ou-delf-b2-lequel-choisir.html", "TCF IRN ou DELF B2 : lequel choisir"),
                  ("/blog/preparation-tcf-delf-naturalisation.html", "Pr&eacute;parer le TCF IRN ou le DELF B2"),
                  ("https://delf-tcf-tef.fr/tcf-irn/", "S'entra&icirc;ner au TCF IRN sur delf-tcf-tef.fr, notre site d&eacute;di&eacute; aux examens")],
        "related": ["delf-b2", "examen-civique"],
    },
    "delf-b2": {
        "long": "Dipl&ocirc;me d'&Eacute;tudes en Langue Fran&ccedil;aise &mdash; niveau B2",
        "def": [
            "Le DELF B2 est un dipl&ocirc;me officiel d&eacute;livr&eacute; par le minist&egrave;re de l'&Eacute;ducation nationale, qui atteste d'un niveau B2 en fran&ccedil;ais. Contrairement au TCF, ce n'est pas un test dont l'attestation expire : le dipl&ocirc;me est <strong>valable &agrave; vie</strong>.",
            "Depuis le 1<sup>er</sup>&nbsp;janvier 2026, le B2 est le niveau exig&eacute; pour la naturalisation. Le DELF B2 satisfait donc directement &agrave; cette condition.",
        ],
        "where": [
            "Dans les pi&egrave;ces justificatives du dossier, en alternative au TCF IRN.",
            "Dans les centres agr&eacute;&eacute;s (Alliances fran&ccedil;aises, Instituts fran&ccedil;ais, centres de FLE), &agrave; des sessions organis&eacute;es &agrave; dates fixes.",
        ],
        "do": [
            "V&eacute;rifiez le calendrier des sessions t&ocirc;t : contrairement au TCF, on ne passe pas le DELF quand on veut, les sessions sont group&eacute;es sur quelques dates par an.",
            "Conservez le dipl&ocirc;me original : il n'expire jamais et vous resservira pour d'autres d&eacute;marches.",
            "Si vous &ecirc;tes press&eacute;, comparez avec le TCF IRN : il se passe plus souvent, m&ecirc;me s'il co&ucirc;te g&eacute;n&eacute;ralement plus cher et n'est valable que deux ans.",
        ],
        "errors": [
            "Croire qu'un DELF B1 suffit encore. Le seuil est pass&eacute; de B1 &agrave; B2 au 1<sup>er</sup>&nbsp;janvier 2026.",
            "Attendre le dernier moment : entre l'inscription, la session et la d&eacute;livrance du dipl&ocirc;me, comptez plusieurs mois.",
        ],
        "faq": [
            ("Le DELF B2 expire-t-il ?",
             "Non. C'est un dipl&ocirc;me, sa validit&eacute; est illimit&eacute;e, contrairement &agrave; l'attestation du TCF qui vaut deux ans."),
            ("Un dipl&ocirc;me fran&ccedil;ais dispense-t-il du DELF ?",
             "Un dipl&ocirc;me d&eacute;livr&eacute; en France attestant d'un niveau suffisant peut &ecirc;tre accept&eacute; en lieu et place du test. V&eacute;rifiez la liste des justificatifs admis avant de payer un examen."),
            ("Le DALF C1 ou C2 est-il accept&eacute; &agrave; la place du DELF B2 ?",
             "Oui : un dipl&ocirc;me d'un niveau sup&eacute;rieur atteste a fortiori du niveau B2 exig&eacute;."),
        ],
        "links": [("/blog/atteindre-niveau-b2-naturalisation.html", "Atteindre le niveau B2"),
                  ("/blog/tcf-irn-ou-delf-b2-lequel-choisir.html", "TCF IRN ou DELF B2"),
                  ("https://delf-tcf-tef.fr/delf-b2/", "Pr&eacute;parer le DELF B2 sur delf-tcf-tef.fr, notre site d&eacute;di&eacute; aux examens")],
        "related": ["tcf-irn", "examen-civique"],
    },
    "timbre-fiscal": {
        "long": "Timbre fiscal de naturalisation (droit de sceau)",
        "def": [
            "Le timbre fiscal est la taxe que vous devez acquitter pour d&eacute;poser une demande de nationalit&eacute; fran&ccedil;aise. Il s'ach&egrave;te sous forme &eacute;lectronique et son identifiant se joint au dossier.",
            "Depuis le <strong>1<sup>er</sup>&nbsp;mai 2026</strong>, son montant est de <strong>255&nbsp;&euro;</strong> en m&eacute;tropole, contre 55&nbsp;&euro; auparavant. En Guyane, le tarif est de 127,50&nbsp;&euro;.",
        ],
        "where": [
            "Au moment du d&eacute;p&ocirc;t : sans identifiant de timbre, la demande ne peut pas &ecirc;tre enregistr&eacute;e.",
            "Pour toutes les proc&eacute;dures : naturalisation par d&eacute;cret, r&eacute;int&eacute;gration, et d&eacute;claration &agrave; raison du mariage.",
        ],
        "do": [
            "Achetez-le en ligne sur le site officiel des timbres fiscaux, ou dans un bureau de tabac agr&eacute;&eacute;. L'achat en ligne vous donne imm&eacute;diatement l'identifiant &agrave; reporter dans le dossier.",
            "N'achetez le timbre qu'une fois votre dossier complet : il n'est <strong>pas remboursable</strong> en cas de refus.",
            "Conservez le justificatif d'achat : un timbre &eacute;lectronique n'expire pas, il reste utilisable m&ecirc;me achet&eacute; longtemps &agrave; l'avance.",
        ],
        "errors": [
            "Oublier qu'il faut <strong>un timbre par demandeur majeur</strong>. Un couple qui d&eacute;pose deux demandes paie 510&nbsp;&euro;.",
            "Compter sur un remboursement en cas de refus ou d'ajournement : il n'y en a pas.",
        ],
        "faq": [
            ("Combien co&ucirc;te le timbre fiscal de naturalisation en 2026 ?",
             "255 &euro; en m&eacute;tropole depuis le 1er mai 2026, contre 55 &euro; auparavant. En Guyane, le tarif est de 127,50 &euro;."),
            ("Le timbre fiscal est-il remboursable si ma demande est refus&eacute;e ?",
             "Non. Le timbre n'est jamais rembours&eacute;, quelle que soit l'issue de la demande."),
            ("Un timbre achet&eacute; avant la hausse reste-t-il valable ?",
             "Oui. C'est la date d'achat qui compte : un timbre achet&eacute; &agrave; 55 &euro; avant le 1er mai 2026 reste utilisable."),
        ],
        "links": [("/blog/hausse-timbre-fiscal-naturalisation-mai-2026.html", "La hausse du timbre fiscal en d&eacute;tail"),
                  ("/blog/cout-naturalisation-francaise-2026.html", "Le budget complet d'une naturalisation")],
        "related": ["anef", "scec"],
    },
    "agdref": {
        "long": "Application de Gestion des Dossiers des Ressortissants &Eacute;trangers en France",
        "def": [
            "AGDREF est le fichier national qui recense les ressortissants &eacute;trangers titulaires d'un titre de s&eacute;jour. &Agrave; chaque personne enregistr&eacute;e correspond un <strong>num&eacute;ro AGDREF</strong>, aussi appel&eacute; num&eacute;ro &eacute;tranger.",
            "Ce num&eacute;ro est votre identifiant aupr&egrave;s de l'administration des &eacute;trangers : il vous suit d'un titre de s&eacute;jour &agrave; l'autre et jusqu'&agrave; votre demande de naturalisation.",
        ],
        "where": [
            "Sur votre titre de s&eacute;jour, o&ugrave; il figure de mani&egrave;re visible.",
            "Dans votre espace ANEF : il sert &agrave; rattacher votre compte &agrave; votre dossier administratif.",
            "Dans tous vos &eacute;changes &eacute;crits avec la pr&eacute;fecture ou la SDANF.",
        ],
        "do": [
            "Notez-le quelque part d'accessible : vous en aurez besoin &agrave; chaque d&eacute;marche, et le retrouver suppose d'avoir son titre de s&eacute;jour sous la main.",
            "Reprenez-le exactement, sans espace ni caract&egrave;re ajout&eacute;, dans les formulaires en ligne : une saisie approximative emp&ecirc;che le rattachement au bon dossier.",
            "Mentionnez-le en en-t&ecirc;te de tous vos courriers &agrave; la pr&eacute;fecture ou &agrave; la SDANF, avec votre num&eacute;ro de dossier.",
        ],
        "errors": [
            "Le confondre avec le num&eacute;ro de visa ou le num&eacute;ro de dossier ANEF : ce sont trois identifiants diff&eacute;rents.",
            "En cr&eacute;er un nouveau en changeant de titre : le num&eacute;ro AGDREF reste le m&ecirc;me tout au long de votre parcours.",
        ],
        "faq": [
            ("O&ugrave; trouver son num&eacute;ro AGDREF ?",
             "Sur votre titre de s&eacute;jour. Il appara&icirc;t aussi dans votre espace ANEF et sur les courriers de la pr&eacute;fecture."),
            ("Le num&eacute;ro AGDREF change-t-il quand on renouvelle son titre ?",
             "Non, il reste le m&ecirc;me : c'est un identifiant unique attach&eacute; &agrave; votre dossier, qui vous suit d'un titre &agrave; l'autre."),
            ("Que devient le num&eacute;ro AGDREF apr&egrave;s la naturalisation ?",
             "Il cesse d'&ecirc;tre utile : une fois fran&ccedil;ais, vous n'&ecirc;tes plus suivi comme ressortissant &eacute;tranger. Vos d&eacute;marches d'identit&eacute; s'appuient d&eacute;sormais sur votre acte de naissance fran&ccedil;ais."),
        ],
        "links": [("/blog/suivre-dossier-naturalisation-anef.html", "Suivre son dossier sur l'ANEF"),
                  ("/blog/documents-naturalisation.html", "La liste des pi&egrave;ces &agrave; fournir"),
                  ("/blog/casier-judiciaire-naturalisation.html", "Casier judiciaire : qui doit le fournir")],
        "related": ["anef", "sdanf"],
    },
    "scec": {
        "long": "Service Central d'&Eacute;tat Civil",
        "def": [
            "Le SCEC, bas&eacute; &agrave; Nantes, tient l'&eacute;tat civil des Fran&ccedil;ais n&eacute;s &agrave; l'&eacute;tranger &mdash; ce qui inclut les personnes naturalis&eacute;es n&eacute;es hors de France.",
            "C'est lui qui &eacute;tablit votre <strong>acte de naissance fran&ccedil;ais</strong> apr&egrave;s la naturalisation. Ce document devient ensuite la base de toutes vos d&eacute;marches d'identit&eacute;.",
        ],
        "where": [
            "Apr&egrave;s la publication du d&eacute;cret : le SCEC dresse votre acte de naissance fran&ccedil;ais.",
            "&Agrave; chaque demande de carte d'identit&eacute; ou de passeport, si vous &ecirc;tes n&eacute; &agrave; l'&eacute;tranger.",
        ],
        "do": [
            "Demandez votre acte de naissance fran&ccedil;ais d&egrave;s que votre d&eacute;cret est publi&eacute; : la carte d'identit&eacute; et le passeport en d&eacute;pendent.",
            "La demande se fait en ligne et gratuitement ; commandez plusieurs copies int&eacute;grales d'un coup, vous en aurez besoin &agrave; plusieurs reprises.",
            "V&eacute;rifiez l'orthographe de vos nom et pr&eacute;noms sur l'acte d&egrave;s r&eacute;ception : une erreur non signal&eacute;e se propage ensuite &agrave; tous vos titres.",
            "Si vous avez demand&eacute; une francisation de nom ou de pr&eacute;nom, c'est cette version francis&eacute;e qui figurera sur l'acte.",
        ],
        "errors": [
            "Continuer &agrave; produire l'acte de naissance de votre pays d'origine : apr&egrave;s naturalisation, c'est l'acte fran&ccedil;ais &eacute;tabli par le SCEC qui fait foi.",
            "Attendre la c&eacute;r&eacute;monie pour la demander : vous pouvez engager la d&eacute;marche d&egrave;s la publication du d&eacute;cret.",
        ],
        "faq": [
            ("Qui &eacute;tablit l'acte de naissance fran&ccedil;ais apr&egrave;s une naturalisation ?",
             "Le Service central d'&eacute;tat civil, &agrave; Nantes, pour toutes les personnes n&eacute;es &agrave; l'&eacute;tranger."),
            ("La demande d'acte de naissance est-elle payante ?",
             "Non, la d&eacute;livrance d'un acte d'&eacute;tat civil est gratuite."),
            ("Combien de temps faut-il pour recevoir son acte de naissance fran&ccedil;ais ?",
             "Le SCEC doit d'abord &eacute;tablir votre acte &agrave; partir du d&eacute;cret, ce qui prend g&eacute;n&eacute;ralement quelques semaines apr&egrave;s la publication. Les copies demand&eacute;es ensuite arrivent plus vite."),
        ],
        "links": [("/blog/demarches-apres-naturalisation.html", "Les d&eacute;marches des six premiers mois"),
                  ("/blog/ceremonie-naturalisation-que-se-passe-t-il.html", "Apr&egrave;s la c&eacute;r&eacute;monie"),
                  ("/glossaire/cnf.html", "Le certificat de nationalit&eacute; fran&ccedil;aise")],
        "related": ["cnf", "jorf"],
    },
    "jorf": {
        "long": "Journal Officiel de la R&eacute;publique Fran&ccedil;aise",
        "def": [
            "Le Journal officiel est la publication dans laquelle para&icirc;t l'ensemble des textes officiels fran&ccedil;ais, dont les d&eacute;crets de naturalisation.",
            "La parution de votre d&eacute;cret au JORF rend la d&eacute;cision opposable aux tiers. Attention toutefois : ce n'est pas la publication qui vous rend fran&ccedil;ais, mais la <strong>signature du d&eacute;cret</strong> (article 51 du d&eacute;cret n&deg;&nbsp;93-1362).",
        ],
        "where": [
            "&Agrave; la toute fin du parcours, lorsque votre d&eacute;cret de naturalisation est publi&eacute;.",
            "Sur L&eacute;gifrance, o&ugrave; chaque d&eacute;cret est consultable par sa date et son num&eacute;ro JORFTEXT.",
        ],
        "do": [
            "Rep&eacute;rez la date de publication : elle fait courir le d&eacute;lai de six mois dans lequel la pr&eacute;fecture doit organiser votre c&eacute;r&eacute;monie.",
            "Les listes nominatives annex&eacute;es aux d&eacute;crets sont en acc&egrave;s prot&eacute;g&eacute; : c'est voulu par la loi, et aucun site ne devrait les republier.",
        ],
        "errors": [
            "Chercher son nom dans un moteur de recherche : les listes de noms sont d&eacute;lib&eacute;r&eacute;ment exclues de l'indexation.",
            "Confondre la date de signature du d&eacute;cret et sa date de publication : ce sont deux dates diff&eacute;rentes, et c'est la premi&egrave;re qui fait de vous un Fran&ccedil;ais.",
        ],
        "faq": [
            ("Comment savoir si mon d&eacute;cret est paru au Journal officiel ?",
             "Votre espace ANEF le signale automatiquement depuis f&eacute;vrier 2023. Vous pouvez aussi consulter l'annuaire des d&eacute;crets publi&eacute;s et ouvrir le texte officiel sur L&eacute;gifrance."),
            ("Pourquoi les noms ne sont-ils pas consultables librement ?",
             "Les listes nominatives des d&eacute;crets de naturalisation sont en acc&egrave;s prot&eacute;g&eacute; sur L&eacute;gifrance : la r&eacute;glementation limite d&eacute;lib&eacute;r&eacute;ment leur d&eacute;couvrabilit&eacute; par les moteurs de recherche."),
        ],
        "links": [("/outils/decret-naturalisation.html", "L'annuaire des d&eacute;crets publi&eacute;s au JO"),
                  ("/blog/ceremonie-naturalisation-que-se-passe-t-il.html", "Ce qui suit la publication")],
        "related": ["nat-eff-rei", "anef"],
    },
    "nat-eff-rei": {
        "long": "Cat&eacute;gories des d&eacute;crets de nationalit&eacute;",
        "def": [
            "NAT, EFF et REI sont les codes qui distinguent les cat&eacute;gories de d&eacute;cisions dans les d&eacute;crets de nationalit&eacute; publi&eacute;s au Journal officiel.",
            "<strong>NAT</strong> d&eacute;signe les naturalisations, <strong>EFF</strong> les effets collectifs qui &eacute;tendent la nationalit&eacute; aux enfants mineurs du naturalis&eacute;, et <strong>REI</strong> les r&eacute;int&eacute;grations de personnes ayant perdu la nationalit&eacute; fran&ccedil;aise.",
        ],
        "where": [
            "Dans l'intitul&eacute; et les annexes des d&eacute;crets publi&eacute;s au JORF.",
            "Dans les r&eacute;f&eacute;rences que l'administration vous communique.",
        ],
        "do": [
            "Si vous avez des enfants mineurs r&eacute;sidant avec vous, v&eacute;rifiez d&egrave;s le d&eacute;p&ocirc;t qu'ils sont bien mentionn&eacute;s dans votre demande : c'est ce qui d&eacute;clenche l'effet collectif.",
            "Joignez leurs actes de naissance et les justificatifs de r&eacute;sidence commune : l'effet collectif suppose que l'enfant r&eacute;side habituellement avec vous.",
            "Une fois le d&eacute;cret publi&eacute;, v&eacute;rifiez que la mention EFF appara&icirc;t bien pour chacun d'eux.",
        ],
        "errors": [
            "Supposer qu'un enfant mineur devient automatiquement fran&ccedil;ais : l'effet collectif suppose des conditions, notamment que l'enfant soit mentionn&eacute; dans le d&eacute;cret.",
            "Oublier un enfant lors du d&eacute;p&ocirc;t. Le rattraper apr&egrave;s la publication du d&eacute;cret suppose une d&eacute;marche distincte, bien plus longue.",
            "Confondre REI et NAT : la r&eacute;int&eacute;gration s'adresse &agrave; d'anciens Fran&ccedil;ais, pas &agrave; des primo-demandeurs.",
        ],
        "faq": [
            ("Que signifient NAT, EFF et REI dans un d&eacute;cret ?",
             "NAT d&eacute;signe une naturalisation, EFF l'effet collectif qui &eacute;tend la nationalit&eacute; aux enfants mineurs, et REI une r&eacute;int&eacute;gration dans la nationalit&eacute; fran&ccedil;aise."),
            ("Mes enfants sont-ils naturalis&eacute;s en m&ecirc;me temps que moi ?",
             "Sous conditions, oui, par effet collectif &mdash; &agrave; condition qu'ils soient mineurs, qu'ils r&eacute;sident avec vous et qu'ils soient mentionn&eacute;s dans le d&eacute;cret."),
        ],
        "links": [("/outils/decret-naturalisation.html", "L'annuaire des d&eacute;crets"),
                  ("/blog/guide-complet-naturalisation-2026.html", "Le guide complet de la naturalisation")],
        "related": ["jorf", "cnf"],
    },
    "cnf": {
        "long": "Certificat de Nationalit&eacute; Fran&ccedil;aise",
        "def": [
            "Le CNF est le document qui prouve la nationalit&eacute; fran&ccedil;aise d'une personne. Il est d&eacute;livr&eacute; par le directeur des services de greffe du tribunal judiciaire.",
            "Il concerne surtout les personnes fran&ccedil;aises par filiation ou par naissance en France, dont la nationalit&eacute; n'est &eacute;tablie par aucun d&eacute;cret. Une personne naturalis&eacute;e, elle, dispose de l'ampliation de son d&eacute;cret.",
        ],
        "where": [
            "Lorsqu'une administration demande une preuve de nationalit&eacute; que votre &eacute;tat civil ne suffit pas &agrave; &eacute;tablir.",
            "Pour un enfant devenu fran&ccedil;ais &agrave; sa majorit&eacute; au titre de l'article 21-7 du Code civil.",
        ],
        "do": [
            "Rassemblez les actes d'&eacute;tat civil de plusieurs g&eacute;n&eacute;rations : c'est la partie longue de la demande, et celle qui bloque le plus souvent.",
            "Si vous &ecirc;tes naturalis&eacute; par d&eacute;cret, conservez plut&ocirc;t pr&eacute;cieusement votre ampliation : elle joue ce r&ocirc;le de preuve.",
            "Anticipez : un CNF est souvent r&eacute;clam&eacute; au pire moment, quand un titre arrive &agrave; expiration.",
        ],
        "errors": [
            "Demander un CNF alors qu'on a &eacute;t&eacute; naturalis&eacute; par d&eacute;cret : dans ce cas, c'est l'ampliation du d&eacute;cret qui fait preuve.",
        ],
        "faq": [
            ("Qui d&eacute;livre le certificat de nationalit&eacute; fran&ccedil;aise ?",
             "Le directeur des services de greffe du tribunal judiciaire comp&eacute;tent."),
            ("Un naturalis&eacute; a-t-il besoin d'un CNF ?",
             "En principe non : l'ampliation du d&eacute;cret de naturalisation constitue la preuve de la nationalit&eacute;. Le CNF concerne surtout les personnes fran&ccedil;aises par filiation ou par naissance en France."),
            ("Le certificat de nationalit&eacute; fran&ccedil;aise a-t-il une dur&eacute;e de validit&eacute; ?",
             "Le CNF n'a pas de date d'expiration, mais certaines administrations en r&eacute;clament un &eacute;tabli r&eacute;cemment. Conservez l'original et faites-en des copies."),
        ],
        "links": [("/glossaire/scec.html", "Le Service central d'&eacute;tat civil"),
                  ("/blog/guide-complet-naturalisation-2026.html", "Le guide complet")],
        "related": ["scec", "nat-eff-rei"],
    },
    "entretien-assimilation": {
        "long": "Entretien d'assimilation en pr&eacute;fecture",
        "def": [
            "L'entretien d'assimilation est le rendez-vous individuel men&eacute; en pr&eacute;fecture pendant l'instruction de votre demande. Il sert &agrave; v&eacute;rifier votre assimilation &agrave; la communaut&eacute; fran&ccedil;aise : votre ma&icirc;trise du fran&ccedil;ais en situation, votre connaissance des droits et devoirs, et votre adh&eacute;sion aux principes de la R&eacute;publique.",
            "L'agent r&eacute;dige ensuite un compte rendu qui p&egrave;se lourd dans l'avis transmis au minist&egrave;re.",
        ],
        "where": [
            "Pendant l'instruction du dossier en pr&eacute;fecture, sur convocation.",
            "En pr&eacute;sentiel, dans les locaux de la pr&eacute;fecture ou de la sous-pr&eacute;fecture.",
        ],
        "do": [
            "Pr&eacute;parez votre <strong>parcours personnel</strong> : dates d'arriv&eacute;e, &eacute;tapes professionnelles, attaches en France. Les incoh&eacute;rences de dates sont mal per&ccedil;ues.",
            "R&eacute;visez les fondamentaux : institutions, symboles, la&iuml;cit&eacute;, droits et devoirs.",
            "Apportez les originaux des pi&egrave;ces de votre dossier : on vous les demande souvent.",
        ],
        "errors": [
            "R&eacute;citer des r&eacute;ponses apprises par c&oelig;ur : l'entretien &eacute;value aussi votre aisance r&eacute;elle en fran&ccedil;ais.",
            "N&eacute;gliger les questions sur son propre parcours, qui sont pourtant les plus fr&eacute;quentes.",
        ],
        "faq": [
            ("L'entretien d'assimilation est-il &eacute;liminatoire ?",
             "Il n'y a pas de note, mais le compte rendu de l'agent p&egrave;se fortement dans l'avis transmis au minist&egrave;re. Un entretien qui r&eacute;v&egrave;le une ma&icirc;trise insuffisante du fran&ccedil;ais ou une m&eacute;connaissance des principes r&eacute;publicains peut conduire &agrave; un ajournement."),
            ("Quelles questions sont pos&eacute;es &agrave; l'entretien ?",
             "Des questions sur votre parcours personnel et professionnel, sur les institutions et les symboles de la R&eacute;publique, sur la la&iuml;cit&eacute;, et des mises en situation du quotidien."),
        ],
        "links": [("/blog/entretien-naturalisation-prefectures.html", "L'entretien en pr&eacute;fecture"),
                  ("/blog/apres-entretien-naturalisation.html", "Ce qui se passe apr&egrave;s l'entretien"),
                  ("/blog/questions-entretien-naturalisation.html", "Les questions r&eacute;ellement pos&eacute;es"),
                  ("/blog/sentrainer-entretien-naturalisation.html", "S'entra&icirc;ner &agrave; l'entretien")],
        "related": ["examen-civique", "tcf-irn"],
    },
    "examen-civique": {
        "long": "Examen civique de naturalisation",
        "def": [
            "L'examen civique est l'&eacute;preuve &eacute;crite, sous forme de QCM, qui v&eacute;rifie votre connaissance de l'histoire, de la culture, des institutions et des valeurs de la France. Il est <strong>obligatoire depuis le 1<sup>er</sup>&nbsp;janvier 2026</strong> pour la plupart des candidats &agrave; la naturalisation.",
            "Le format&nbsp;: <strong>40 questions en 45 minutes</strong>, avec <strong>32 bonnes r&eacute;ponses sur 40</strong> requises, soit 80&nbsp;%.",
        ],
        "where": [
            "En amont du d&eacute;p&ocirc;t : l'attestation de r&eacute;ussite fait partie des pi&egrave;ces du dossier.",
            "Dans un centre agr&eacute;&eacute;, sur inscription.",
        ],
        "do": [
            "Travaillez les cinq th&eacute;matiques du programme : valeurs et principes, institutions, droits et devoirs, histoire et culture, vie en soci&eacute;t&eacute;.",
            "Ne n&eacute;gligez pas les <strong>mises en situation</strong> : elles ne demandent pas une date mais ce que dit le droit dans une sc&egrave;ne concr&egrave;te. C'est la partie o&ugrave; les candidats perdent le plus de points.",
            "Faites un test blanc pour vous situer avant de vous inscrire.",
        ],
        "errors": [
            "R&eacute;viser uniquement des dates : une bonne moiti&eacute; des points se joue sur la compr&eacute;hension des principes, pas sur la m&eacute;morisation.",
            "Sous-estimer le seuil : 80&nbsp;% laisse une marge de huit erreurs seulement.",
        ],
        "faq": [
            ("Combien de questions comporte l'examen civique ?",
             "40 questions &agrave; traiter en 45 minutes, avec 32 bonnes r&eacute;ponses sur 40 requises (80 %)."),
            ("L'examen civique est-il obligatoire pour tout le monde ?",
             "Il est obligatoire depuis le 1er janvier 2026 pour la plupart des candidats &agrave; la naturalisation. Certaines situations particuli&egrave;res peuvent ouvrir droit &agrave; une dispense."),
        ],
        "links": [("/outils/examen-civique.html", "Faire le test blanc gratuit"),
                  ("/blog/examen-civique-naturalisation-2026.html", "Le guide de l'examen civique 2026"),
                  ("/blog/questions-mise-en-situation-examen-civique-naturalisation.html", "Les questions de mise en situation")],
        "related": ["entretien-assimilation", "tcf-irn"],
    },
}

NAMES = {
    "anef": "ANEF", "rapo": "RAPO", "sdanf": "SDANF", "tcf-irn": "TCF IRN",
    "delf-b2": "DELF B2", "timbre-fiscal": "Timbre fiscal", "agdref": "AGDREF",
    "scec": "SCEC", "jorf": "JORF", "nat-eff-rei": "NAT &middot; EFF &middot; REI",
    "cnf": "CNF", "entretien-assimilation": "Entretien d'assimilation",
    "examen-civique": "Examen civique",
}


def strip_tags(text):
    return re.sub(r"<[^>]+>", "", text)


def render_main(slug, t):
    name = NAMES[slug]
    parts = [
        '<main class="section"><div class="legal" style="max-width:720px">',
        '  <p class="article-back"><a href="/glossaire/">&larr; Glossaire</a></p>',
        f'  <h1 style="margin-bottom:4px">{name}</h1>',
        f'  <p style="color:var(--text-secondary);font-size:16px;margin-bottom:28px"><strong>{t["long"]}</strong></p>',
        "  <h2>D&eacute;finition</h2>",
    ]
    parts += [f"  <p>{p}</p>" for p in t["def"]]

    parts.append("  <h2>O&ugrave; vous le rencontrez</h2>")
    parts.append("  <ul>")
    parts += [f"    <li>{i}</li>" for i in t["where"]]
    parts.append("  </ul>")

    parts.append("  <h2>Ce qu'il faut faire</h2>")
    parts.append("  <ul>")
    parts += [f"    <li>{i}</li>" for i in t["do"]]
    parts.append("  </ul>")

    parts.append("  <h2>Erreurs fr&eacute;quentes</h2>")
    parts.append("  <ul>")
    parts += [f"    <li>{i}</li>" for i in t["errors"]]
    parts.append("  </ul>")

    parts.append("  <h2>Questions fr&eacute;quentes</h2>")
    for q, a in t["faq"]:
        parts.append(f"  <h3>{q}</h3>")
        parts.append(f"  <p>{a}</p>")

    parts.append("  <h2>Pour aller plus loin</h2>")
    parts.append("  <ul>")
    parts += [
        f'    <li><a href="{href}"{" target=_BLANK_ rel=_NOOPENER_" if href.startswith("http") else ""}>{label}</a></li>'.replace(
            '_BLANK_', '"_blank"').replace('_NOOPENER_', '"noopener"').replace('target= ', 'target=')
        for href, label in t["links"]
    ]
    parts.append("  </ul>")

    related = " ".join(
        f'<a href="/glossaire/{r}.html">{NAMES[r]}</a>' for r in t["related"]
    )
    parts.append("  <h2>Termes li&eacute;s</h2>")
    parts.append(
        f'  <p class="module-related" style="justify-content:flex-start">{related}</p>'
    )
    parts.append("</div></main>")
    return "\n".join(parts)


def render_faq_schema(slug, t):
    """FAQPage : le JSON-LD n'est pas decode par le parseur HTML, les entites
    doivent donc etre resolues ici sous peine d'afficher "fran&ccedil;aise"
    tel quel dans les rich results."""
    def clean(text):
        return html.unescape(strip_tags(text)).replace("\u00a0", " ")

    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": clean(q),
                "acceptedAnswer": {"@type": "Answer", "text": clean(a)},
            }
            for q, a in t["faq"]
        ],
    }


def main():
    total = 0
    for slug, t in TERMS.items():
        path = GLOSSAIRE / f"{slug}.html"
        if not path.exists():
            sys.exit(f"fiche absente : {path}")
        page = path.read_text(encoding="utf-8")

        page = re.sub(r"<main class=\"section\">.*?</main>", render_main(slug, t), page, flags=re.S)

        schema = (
            '  <script type="application/ld+json">'
            + json.dumps(render_faq_schema(slug, t), ensure_ascii=False)
            + "</script>\n"
        )
        page = re.sub(
            r'  <script type="application/ld\+json">\{"@context": "https://schema\.org", "@type": "FAQPage".*?</script>\n',
            "",
            page,
            flags=re.S,
        )
        page = page.replace("</head>", schema + "</head>", 1)

        path.write_text(page, encoding="utf-8")

        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
            json.loads(block)

        body = re.sub(r"<script.*?</script>|<nav.*?</nav>|<footer.*?</footer>", "", page, flags=re.S)
        words = len(re.sub(r"<[^>]+>", " ", body).split())
        total += 1
        print(f"  {words:4} mots  glossaire/{slug}.html")

    print(f"{total} fiches regenerees")


if __name__ == "__main__":
    main()
