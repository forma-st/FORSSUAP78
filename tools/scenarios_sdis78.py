#!/usr/bin/env python3
"""Scénarios de mises en situation professionnelle (MSP) SDIS 78 → data/scenarios.json

Prompt Secours (cursus PS) d'après le programme de la valise pédagogique,
Équipier SUAP (cursus EQSUAP) d'après le chronogramme du RIOFE (MSP 01 à 07).
`observe` est indexé par les savoir-agir des fiches MSP RIOFE (PS : c22…c32 ; SUAP : c1…c15).
`tpl` indique la fiche proposée : 'auto' (autoévaluation accompagnée) ou 'crit' (évaluation critériée).
"""
import json, os

def R(t, nom, brief, jeu, param, maq=''):
    return {'t': t, 'nom': nom, 'brief': brief, 'jeu': jeu, 'param': param, 'maq': maq}

def sc(cur, id, n, ref, tpl, jour, etape, niveau, titre, theme, missions, lieu, equipe, cases, objectifs, message, contexte, roles,
       evolution, attendus, observe, mat, securite, debrief, duree='15 min + 10 min de débriefing', secouristes=None):
    return {'id': id, 'n': n, 'ref': ref, 'tpl': tpl, 'cur': cur, 'jour': jour, 'etape': etape, 'niveau': niveau, 'titre': titre, 'theme': theme,
            'missions': missions, 'duree': duree, 'lieu': lieu, 'equipe': equipe, 'cases': cases, 'checks': [], 'objectifs': objectifs,
            'message': message, 'contexte': contexte, 'roles': roles,
            'secouristes': secouristes or ('Vous êtes équipier prompt-secours, seul ou en binôme, avec votre sac de premiers secours.' if cur == 'PS'
                                           else 'Vous êtes l’équipage d’un VSAV (chef d’agrès joué par un formateur ou un stagiaire) avec l’ensemble du matériel du véhicule.'),
            'evolution': evolution, 'attendus': attendus, 'observe': observe,
            'mat': {k: mat.get(k, []) for k in ('lieu', 'maq', 'acc', 'sec')}, 'securite': securite, 'debrief': debrief}

PS = 'PS'
SU = 'EQSUAP'
L = []

# ======================================================================== Prompt Secours
L.append(sc(PS, 'ps-oava', 1, 'MSP OAVA', 'auto', 'J1', 'Détresse ventilatoire', 1,
    'Étouffement au restaurant', 'Obstruction grave des voies aériennes chez un adulte',
    'Reconnaître l’obstruction grave, réaliser les gestes de désobstruction, faire alerter, surveiller.',
    'Salle de restaurant : tables, chaises, assiettes', 'Équipier prompt-secours seul, témoins joués par les stagiaires', ['ova'],
    ['Distinguer obstruction partielle et obstruction grave', 'Réaliser claques dans le dos puis compressions abdominales', 'Faire alerter et surveiller après la désobstruction'],
    '« Vous déjeunez au restaurant ; à la table voisine, un homme se lève brusquement en portant les mains à sa gorge. »',
    'M. Durand (52 ans) a avalé un morceau de viande. Il ne peut plus parler ni tousser ; il est rouge puis bleuit.',
    [R('Victime', 'M. Durand, 52 ans', 'Vous vous étouffez avec un morceau de viande. Vous ne pouvez ni parler ni tousser.',
       'Portez les mains à la gorge, restez debout et penché en avant. Le corps étranger sort à la 3e compression abdominale si les gestes sont corrects.',
       ['Ne parle pas, ne tousse pas', 'Agitation, cyanose des lèvres', 'Après désobstruction : FR 22/min, SpO2 94 %, FC 110/min'], 'Fond de teint bleuté sur les lèvres'),
     R('Tiers', 'Épouse de la victime', 'Vous êtes affolée et tapez dans le dos de votre mari sans efficacité.', 'Laissez la place si on vous le demande clairement ; vous pouvez être envoyée alerter.', [])],
    [['Gestes corrects et rapides', 'Désobstruction à la 3e compression abdominale ; la victime respire et tousse.'],
     ['Gestes inefficaces ou tardifs', 'Perte de connaissance au bout de 1 min 30 : arrêt cardiaque, RCP à débuter.']],
    ['Reconnaître l’obstruction grave (ne parle pas, ne tousse pas)', 'Jusqu’à 5 claques dans le dos', 'Jusqu’à 5 compressions abdominales en alternance',
     'Faire alerter les secours', 'Installer et surveiller la victime après la désobstruction'],
    {'c23': 'Écarte les chaises, fait de la place', 'c24': 'Désigne un témoin pour alerter, message complet', 'c25': 'Reconnaît l’obstruction grave',
     'c26': 'Claques dans le dos puis compressions abdominales efficaces', 'c31': 'Surveille la respiration après désobstruction'},
    {'lieu': ['Table et 2 chaises', 'Assiettes, couverts'], 'maq': ['Fond de teint bleuté'], 'acc': ['Mannequin de désobstruction pour la pratique'], 'sec': ['Sac de premiers secours']},
    'Les compressions abdominales et les claques se simulent sur le figurant, se pratiquent réellement sur mannequin uniquement.',
    ['Quels signes vous ont fait dire que l’obstruction était grave ?', 'Que faire si la victime perd connaissance ?']))

L.append(sc(PS, 'ps-hemo', 2, 'MSP hémorragie', 'auto', 'J1', 'Détresse circulatoire', 1,
    'Coupure à l’atelier', 'Hémorragie externe de l’avant-bras',
    'Arrêter l’hémorragie, installer la victime, alerter, surveiller.', 'Atelier : établi, outils sans lame, sol encombré',
    'Équipier prompt-secours seul, collègue de la victime', ['hemo'],
    ['Se protéger et arrêter immédiatement le saignement', 'Allonger la victime et relayer la compression', 'Alerter et surveiller'],
    '« Un agent technique s’est coupé à l’atelier, son collègue vous appelle. »',
    'M. Leroy (45 ans) s’est entaillé l’avant-bras avec une tôle. Le sang coule en continu. Il est debout et pâle.',
    [R('Victime', 'M. Leroy, 45 ans', 'Vous vous êtes coupé, vous tenez votre bras. Vous voulez juste un pansement.',
       'Debout au départ ; vous vous sentez faible au bout de 2 minutes si on ne vous allonge pas.', ['Conscient, anxieux', 'FC 104/min, FR 18/min', 'Pâleur, sueurs'],
       'Plaie de 6 cm à l’avant-bras, faux sang')],
    [['Compression efficace dans la minute', 'Le saignement s’arrête, la victime se calme.'], ['Pas de compression', 'Malaise : la victime s’assoit seule, FC 120/min.']],
    ['Mettre des gants', 'Comprimer immédiatement la plaie', 'Allonger la victime', 'Relayer par un pansement compressif', 'Alerter, couvrir, surveiller'],
    {'c22': 'Gants, éloigne les outils', 'c24': 'Alerte complète et structurée', 'c26': 'Compression immédiate puis pansement compressif',
     'c25': 'Recherche les autres signes de gravité', 'c31': 'Surveille le saignement et l’état de la victime'},
    {'lieu': ['Établi, quelques outils sans lame', 'Bâche au sol'], 'maq': ['Plaie en silicone', 'Faux sang', 'Fond de teint clair'], 'acc': ['Chiffon'], 'sec': ['Gants, pansement compressif, garrot']},
    'Aucun outil tranchant réel. Protéger le sol du faux sang.', ['Pourquoi comprimer avant d’ouvrir le sac ?', 'Quand poser un garrot ?']))

L.append(sc(PS, 'ps-malaise', 3, 'MSP bilans', 'auto', 'J2', 'Bilans, malaise', 2,
    'Malaise au bureau', 'Malaise chez une personne diabétique',
    'Réaliser le bilan complet, installer la victime, transmettre le bilan, surveiller.', 'Bureau : chaise, bureau, sac à main',
    'Équipier prompt-secours, collègue de bureau', ['malaise'],
    ['Réaliser un bilan structuré', 'Recueillir les antécédents et traitements', 'Transmettre un bilan clair, appliquer les consignes'],
    '« Une collègue se sent mal à son bureau. »',
    'Mme Petit (38 ans), diabétique, a sauté le déjeuner. Elle est pâle, en sueur, tremblante et un peu confuse.',
    [R('Victime', 'Mme Petit, 38 ans', 'Vous êtes diabétique sous insuline, vous n’avez pas mangé ce midi.', 'Réponses lentes, un peu confuses. Vous vous améliorez si on vous donne du sucre.',
       ['Consciente, ralentie', 'FC 96/min, FR 16/min, SpO2 98 %', 'Sueurs, tremblements', 'Glycémie si mesurée : 0,45 g/L'], 'Glycérine en vaporisateur pour les sueurs')],
    [['Bilan complet et sucre donné', 'Amélioration en 10 minutes.'], ['Rien n’est fait', 'Aggravation : la victime ne répond plus.']],
    ['Installer en position d’attente adaptée', 'Bilan d’urgence vitale puis complémentaire', 'Rechercher antécédents, traitements, dernier repas',
     'Transmettre le bilan', 'Appliquer les consignes (resucrage si autorisé), surveiller'],
    {'c25': 'Bilan structuré et complet', 'c24': 'Transmission claire', 'c28': 'Prise en charge adaptée du malaise', 'c31': 'Surveillance et réévaluation'},
    {'lieu': ['Bureau, chaise'], 'maq': ['Glycérine (sueurs)'], 'acc': ['Sac à main avec carnet de diabétique et stylo à insuline factice'], 'sec': ['Sac de premiers secours, sucre']},
    'Aucun produit réel à injecter.', ['Quels éléments du bilan vous ont orientés ?', 'Comment avez-vous structuré la transmission ?']))

L.append(sc(PS, 'ps-inconscient', 4, 'MSP inconscient', 'crit', 'J2', 'Victime inconsciente', 2,
    'Personne au sol dans un parc', 'Victime inconsciente qui respire',
    'Apprécier la conscience et la respiration, libérer les voies aériennes, PLS, alerter, surveiller.', 'Extérieur : allée de parc, banc',
    'Équipier prompt-secours seul, témoin', ['pc'],
    ['Reconnaître la perte de connaissance', 'Libérer les voies aériennes et apprécier la respiration', 'Mettre en PLS, alerter, surveiller'],
    '« Un promeneur vous fait signe : une femme est allongée près d’un banc. »',
    'Mme Martin (60 ans) est allongée sur le dos, ne répond pas. Elle respire bruyamment.',
    [R('Victime', 'Mme Martin, 60 ans', 'Vous êtes inconsciente.', 'Restez inerte, respiration bruyante qui devient normale après libération des voies aériennes.', ['Ne répond pas', 'Respire : FR 14/min']),
     R('Tiers', 'Promeneur', 'Vous avez trouvé la dame.', 'Vous pouvez alerter si on vous le demande précisément.', [])],
    [['PLS rapide', 'Respiration régulière, la victime reste stable.'], ['Victime laissée sur le dos', 'Respiration de plus en plus bruyante, vomissements.']],
    ['Vérifier l’absence de danger', 'Apprécier la conscience', 'Libérer les voies aériennes et apprécier la respiration', 'PLS', 'Alerter', 'Surveiller la respiration'],
    {'c23': 'Vérifie l’absence de danger', 'c25': 'Conscience puis respiration', 'c26': 'LVA et PLS correctes', 'c24': 'Alerte', 'c31': 'Surveillance continue'},
    {'lieu': ['Banc'], 'acc': ['Couverture'], 'sec': ['Sac de premiers secours']}, 'Tapis de sol pour le figurant.',
    ['Comment avez-vous apprécié la respiration ?', 'Qu’auriez-vous fait si elle cessait de respirer ?']))

L.append(sc(PS, 'ps-acr', 5, 'MSP ACR adulte', 'crit', 'J3', 'Arrêt cardiaque', 2,
    'Arrêt cardiaque en salle de sport', 'Arrêt cardiaque chez l’adulte, DAE disponible',
    'Reconnaître l’arrêt cardiaque, alerter, RCP, mise en œuvre du DAE, relais des secours.', 'Salle de sport : tapis, haltères',
    'Équipier prompt-secours et un témoin', ['acr'],
    ['Reconnaître l’arrêt cardiaque', 'Alerter et faire apporter le DAE', 'RCP de qualité et DAE sans interruption inutile'],
    '« Un homme vient de s’effondrer près d’un tapis de course. »', 'M. Bernard (58 ans) s’est effondré pendant son entraînement. Il ne répond pas et ne respire pas.',
    [R('Victime', 'Mannequin RCP (M. Bernard, 58 ans)', 'Arrêt cardiaque.', 'Remplacer le figurant par le mannequin dès le début de la RCP.', ['Inconscient', 'Ne respire pas'])],
    [['RCP et DAE dans les 3 minutes', 'Le DAE délivre un choc ; poursuivre la RCP jusqu’au relais.'], ['RCP retardée', 'Le DAE n’indique pas de choc, poursuivre la RCP.']],
    ['Reconnaître l’ACR', 'Alerter, demander le DAE', 'Compressions 100 à 120/min, 5 à 6 cm', 'Mettre en œuvre le DAE', 'Poursuivre jusqu’au relais'],
    {'c26': 'RCP de qualité, DAE', 'c24': 'Alerte précoce', 'c32': 'Relais avec les secours', 'c23': 'Sécurité lors du choc'},
    {'lieu': ['Tapis de sol'], 'acc': ['Mannequin RCP', 'DAE de formation'], 'sec': ['Sac de premiers secours']}, 'DAE de formation uniquement.',
    ['Combien de temps entre l’effondrement et le premier choc ?', 'Comment limiter les interruptions des compressions ?']))

L.append(sc(PS, 'ps-trauma', 6, 'MSP traumatisme', 'crit', 'J3', 'Victime traumatisée', 2,
    'Chute d’échelle dans un jardin', 'Suspicion de traumatisme du rachis',
    'Assurer la sécurité, maintenir la tête, réaliser le bilan, alerter, surveiller.', 'Jardin : échelle couchée au sol',
    'Équipier prompt-secours, conjoint de la victime', ['trauma'],
    ['Suspecter un traumatisme du rachis', 'Maintenir la tête en position neutre', 'Bilan et alerte'],
    '« Un homme est tombé de son échelle en taillant sa haie. »', 'M. Roux (67 ans) est tombé d’environ 2 m. Il est allongé sur le dos et se plaint du cou.',
    [R('Victime', 'M. Roux, 67 ans', 'Vous avez mal au cou, des fourmillements dans les mains.', 'Vous voulez vous relever : n’obéissez que si on vous l’interdit clairement.',
       ['Conscient', 'FC 88/min, FR 18/min', 'Douleur cervicale, fourmillements des mains'])],
    [['Maintien de tête rapide', 'État stable.'], ['Victime mobilisée', 'Aggravation des fourmillements, perte de force dans les bras.']],
    ['Interdire de bouger', 'Maintien de tête', 'Bilan', 'Alerter', 'Couvrir, surveiller'],
    {'c30': 'Maintien de tête en position neutre', 'c25': 'Bilan orienté traumatisme', 'c24': 'Alerte', 'c31': 'Surveillance'},
    {'lieu': ['Échelle', 'Taille-haie factice'], 'sec': ['Sac de premiers secours, couverture']}, 'Échelle couchée au sol, aucune hauteur.',
    ['Quels éléments vous ont fait suspecter une atteinte du rachis ?']))

L.append(sc(PS, 'ps-smv', 7, 'MSP SMV', 'crit', 'J4', 'Situation multi-victimes', 3,
    'Accident entre deux cyclistes', 'Situation à plusieurs victimes',
    'Bilan circonstanciel, priorisation des victimes, alerte, gestes de secours, intégration à l’arrivée des secours.', 'Piste cyclable',
    'Deux équipiers prompt-secours', ['hemo', 'trauma', 'pc'],
    ['Faire un bilan circonstanciel et demander des renforts', 'Prioriser les victimes', 'S’intégrer à l’arrivée des secours'],
    '« Deux cyclistes viennent de se percuter. »', 'Un cycliste saigne abondamment de la jambe, un second est inconscient, un troisième marche et crie.',
    [R('Victime', 'Cycliste 1', 'Plaie de jambe qui saigne abondamment.', 'Pâleur progressive.', ['FC 120/min'], 'Faux sang'),
     R('Victime', 'Cycliste 2', 'Inconscient, respire.', 'Restez inerte.', ['FR 16/min']),
     R('Tiers', 'Cycliste 3', 'Égratignures, très agité.', 'Vous accaparez l’équipier.', [])],
    [['Priorisation correcte', 'Les deux victimes graves sont prises en charge.'], ['Équipier accaparé par le cycliste 3', 'La victime qui saigne s’aggrave.']],
    ['Bilan circonstanciel', 'Demander des renforts', 'Hémorragie : compression', 'Inconscient : PLS', 'Rendre compte à l’arrivée des secours'],
    {'c23': 'Sécurise la zone', 'c24': 'Alerte avec nombre de victimes', 'c26': 'Traite les détresses vitales en priorité', 'c32': 'S’intègre à l’arrivée des secours'},
    {'lieu': ['Vélos'], 'maq': ['Faux sang', 'Égratignures'], 'sec': ['2 sacs de premiers secours']}, 'Vélos couchés au sol.',
    ['Comment avez-vous choisi la première victime ?']))

L.append(sc(PS, 'ps-synthese', 8, 'MSP synthèse', 'crit', 'J4', 'Synthèse', 3,
    'Malaise et chute dans un escalier', 'Synthèse : bilan, malaise et traumatisme',
    'Prendre en charge une victime présentant plusieurs atteintes, transmettre le bilan, s’intégrer dans la chaîne des secours.', 'Escalier d’immeuble',
    'Équipier prompt-secours', ['malaise', 'trauma'],
    ['Mener un bilan complet', 'Prioriser les actions', 'Transmettre et s’intégrer à l’arrivée des secours'],
    '« Une voisine a entendu quelqu’un tomber dans l’escalier. »', 'Mme Lefèvre (74 ans) a fait un malaise et chuté de quelques marches. Douleur au poignet, désorientée.',
    [R('Victime', 'Mme Lefèvre, 74 ans', 'Vous avez eu un étourdissement, vous avez mal au poignet.', 'Un peu désorientée, vous répétez les mêmes questions.',
       ['FC 52/min irrégulier', 'PA 95/60', 'Déformation du poignet'])],
    [['Bilan complet', 'L’équipier détecte le pouls lent et irrégulier et le transmet.'], ['Bilan centré sur le poignet', 'Nouveau malaise.']],
    ['Bilan d’urgence vitale puis complémentaire', 'Immobiliser le poignet', 'Transmettre les anomalies du pouls', 'Surveiller'],
    {'c25': 'Bilan complet', 'c28': 'Malaise pris en compte', 'c30': 'Immobilisation du poignet', 'c32': 'S’intègre à la chaîne des secours'},
    {'lieu': ['Escalier ou marches'], 'maq': ['Déformation du poignet'], 'sec': ['Sac de premiers secours, attelle']}, 'Figurante allongée sur un tapis en bas des marches.',
    ['Quelle était l’information la plus importante à transmettre ?'], duree='20 min + 15 min de débriefing'))

# ======================================================================== Équipier SUAP
L.append(sc(SU, 'su-msp01', 1, 'MSP01', 'auto', 'J1', 'Immobilisation, relevage, brancardage', 1,
    'Chute d’escabeau à domicile', 'Suspicion de traumatisme du rachis, relevage et brancardage',
    'Sécuriser, réaliser le bilan, immobiliser, relever et brancarder la victime jusqu’au VSAV.', 'Domicile : salon encombré, couloir étroit',
    'Équipage VSAV de 3 ou 4', ['trauma'],
    ['Immobiliser le rachis', 'Choisir et réaliser la technique de relevage', 'Brancarder en sécurité jusqu’au VSAV'],
    'Départ VSAV : « Chute d’une personne âgée à domicile, douleur dorsale. »', 'Mme Garnier (78 ans) est tombée de son escabeau en changeant une ampoule. Elle est au sol sur le dos.',
    [R('Victime', 'Mme Garnier, 78 ans', 'Douleur dans le bas du dos.', 'Vous avez peur d’être déplacée, demandez ce qu’on vous fait.', ['Consciente', 'FC 92/min, PA 145/85', 'Douleur lombaire, sensibilité conservée'])],
    [['Immobilisation correcte', 'Douleur stable.'], ['Relevage brutal', 'Douleur intense, angoisse.']],
    ['Maintien de tête', 'Bilan', 'Choix du matériel (cuillère, MID)', 'Relevage commandé', 'Brancardage adapté au couloir'],
    {'c10': 'Immobilisation adaptée', 'c11': 'Relevage commandé et synchronisé', 'c3': 'Se positionne au sein de l’équipe', 'c5': 'Bilan', 'c13': 'Surveillance pendant le brancardage'},
    {'lieu': ['Escabeau', 'Meubles pour encombrer'], 'sec': ['Brancard cuillère, MID, brancard']}, 'Charge réelle : rappel des gestes et postures.',
    ['Pourquoi ce choix de technique de relevage ?'], duree='45 min + 15 min de débriefing'))

L.append(sc(SU, 'su-msp02', 2, 'MSP02', 'auto', 'J2', 'Bilan – MMP', 2,
    'Malaise d’un homme diabétique', 'Bilan complet et transmission au médecin régulateur',
    'Réaliser le bilan, recueillir les éléments, transmettre le bilan pompier au SAMU (15), appliquer les consignes.', 'Domicile : cuisine',
    'Équipage VSAV', ['malaise'],
    ['Bilan structuré', 'Transmission claire au médecin régulateur', 'Application des consignes et surveillance'],
    'Départ VSAV : « Homme de 62 ans, malaise à domicile. »', 'M. Moreau (62 ans), diabétique, est assis dans sa cuisine, en sueur et confus.',
    [R('Victime', 'M. Moreau, 62 ans', 'Diabétique, vous avez fait votre insuline sans manger.', 'Confus, agressif si on insiste.', ['Glycémie 0,40 g/L', 'FC 100/min', 'Sueurs']),
     R('Tiers', 'Épouse', 'Vous donnez le traitement et les antécédents si on vous les demande.', '', [])],
    [['Bilan complet et resucrage', 'Amélioration.'], ['Bilan incomplet', 'Perte de connaissance.']],
    ['Bilan circonstanciel, d’urgence vitale, complémentaire', 'Glycémie', 'Transmission au médecin régulateur', 'Application des consignes'],
    {'c5': 'Bilan complet', 'c4': 'Transmission au médecin régulateur', 'c9': 'Prise en charge du malaise', 'c13': 'Surveillance', 'c14': 'Hygiène lors de la glycémie'},
    {'lieu': ['Table, chaise'], 'acc': ['Lecteur de glycémie de formation'], 'sec': ['Sac VSAV']}, '', ['Votre transmission était-elle complète ?'], duree='30 min + 15 min de débriefing'))

L.append(sc(SU, 'su-msp03', 3, 'MSP03', 'crit', 'J2', 'Extraction de victime ACT', 2,
    'Accident de la circulation, conducteur incarcéré', 'Extraction d’une victime d’un véhicule',
    'Sécuriser, accéder à la victime, bilan, participer à l’extraction avec l’équipe de désincarcération.', 'Véhicule de formation',
    'Équipage VSAV et équipe de désincarcération', ['trauma'],
    ['Sécuriser', 'Maintien de tête et bilan dans le véhicule', 'Extraction coordonnée'],
    'Départ VSAV et FPT : « Accident véhicule léger contre arbre, une personne incarcérée. »', 'Le conducteur (35 ans) est conscient, coincé par le tableau de bord, douleur à la jambe.',
    [R('Victime', 'Conducteur, 35 ans', 'Douleur à la jambe droite, peur.', 'Vous voulez sortir seul.', ['FC 110/min', 'PA 120/80', 'Déformation de la jambe'], 'Déformation de jambe')],
    [['Coordination efficace', 'Extraction dans l’axe.'], ['Défaut de coordination', 'Mobilisation de la tête, douleur cervicale.']],
    ['Sécurisation', 'Maintien de tête', 'Bilan', 'Extraction synchronisée'],
    {'c2': 'Sécurité des intervenants', 'c12': 'Participation à l’extraction', 'c10': 'Immobilisation', 'c3': 'Position dans l’équipe'},
    {'lieu': ['Véhicule de formation'], 'sec': ['Plan dur, collier, MID']}, 'Zone de désincarcération balisée, EPI obligatoires.', ['Comment s’est faite la coordination ?'], duree='45 min + 15 min de débriefing'))

L.append(sc(SU, 'su-msp04', 4, 'MSP04', 'crit', 'J3', 'Nouveau-né à la naissance', 2,
    'Accouchement inopiné à domicile', 'Accouchement et prise en charge du nouveau-né',
    'Évaluer l’imminence, préparer le kit, accompagner la naissance, prendre en charge le nouveau-né et la mère.', 'Domicile : chambre',
    'Équipage VSAV', ['detresse'],
    ['Évaluer l’imminence de l’accouchement', 'Prendre en charge le nouveau-né', 'Surveiller la mère'],
    'Départ VSAV : « Femme enceinte, contractions rapprochées. »', 'Mme Robert (29 ans), 3e grossesse, à terme, a envie de pousser.',
    [R('Victime', 'Mme Robert, 29 ans', 'Vous avez très envie de pousser.', 'Naissance au bout de quelques minutes.', ['Contractions toutes les 2 minutes']),
     R('Victime', 'Nouveau-né (mannequin)', '', 'Respire après séchage et stimulation.', [])],
    [['Prise en charge correcte', 'Nouveau-né rose et tonique.'], ['Nouveau-né non séché', 'Hypothermie, respiration faible.']],
    ['Bilan de la parturiente', 'Transmission au médecin régulateur', 'Préparation du kit', 'Sécher, réchauffer, stimuler', 'Surveiller mère et enfant'],
    {'c8': 'Prise en charge adaptée', 'c4': 'Transmission', 'c13': 'Surveillance', 'c14': 'Hygiène'},
    {'lieu': ['Lit'], 'acc': ['Mannequin d’accouchement', 'Mannequin nouveau-né'], 'sec': ['Kit accouchement']}, '', ['Quels signes annonçaient un accouchement imminent ?']))

L.append(sc(SU, 'su-msp05', 5, 'MSP05', 'crit', 'J3', 'Affections spécifiques', 2,
    'Troubles de la parole chez une personne âgée', 'Suspicion d’accident vasculaire cérébral',
    'Reconnaître les signes d’AVC, noter l’heure de début, transmettre rapidement, surveiller.', 'Domicile : salon',
    'Équipage VSAV', ['malaise'],
    ['Reconnaître un AVC', 'Noter l’heure de début des signes', 'Transmission rapide'],
    'Départ VSAV : « Homme de 70 ans, ne parle plus correctement. »', 'M. Laurent (70 ans) a la bouche déviée et ne bouge plus le bras droit depuis 30 minutes.',
    [R('Victime', 'M. Laurent, 70 ans', 'Vous parlez difficilement.', 'Bras droit sans force.', ['PA 180/100', 'Glycémie 1,10 g/L']),
     R('Tiers', 'Fille de la victime', 'Vous savez que les signes ont commencé à 14 h 10.', '', [])],
    [['Transmission rapide', 'Orientation vers une unité neurovasculaire.'], ['Heure non recherchée', 'Orientation retardée.']],
    ['Bilan', 'Rechercher l’heure de début', 'Glycémie', 'Transmission', 'Surveillance'],
    {'c9': 'Reconnaît l’AVC', 'c5': 'Bilan', 'c4': 'Transmission', 'c13': 'Surveillance'},
    {'lieu': ['Fauteuil'], 'sec': ['Sac VSAV']}, '', ['Pourquoi l’heure de début est-elle essentielle ?']))

L.append(sc(SU, 'su-msp06', 6, 'MSP06', 'crit', 'J4', 'Brûlures', 2,
    'Brûlure dans la cuisine d’un restaurant', 'Brûlure thermique étendue',
    'Refroidir, réaliser le bilan, protéger, transmettre et surveiller pendant le transport.', 'Cuisine de restaurant',
    'Équipage VSAV', ['detresse'],
    ['Refroidir sans provoquer d’hypothermie', 'Évaluer la gravité', 'Transmettre et surveiller'],
    'Départ VSAV : « Cuisinier brûlé par de l’huile. »', 'M. Henry (40 ans) a reçu de l’huile chaude sur l’avant-bras et le thorax.',
    [R('Victime', 'M. Henry, 40 ans', 'Douleur intense.', 'Vous voulez retirer votre tablier collé.', ['FC 115/min', 'Brûlures avant-bras et thorax'], 'Maquillage de brûlures')],
    [['Refroidissement précoce', 'Douleur diminuée.'], ['Refroidissement prolongé à l’eau froide', 'Frissons.']],
    ['Refroidir', 'Évaluer surface et profondeur', 'Protéger', 'Transmettre', 'Surveiller'],
    {'c8': 'Prise en charge de la brûlure', 'c5': 'Bilan', 'c14': 'Hygiène', 'c13': 'Surveillance'},
    {'lieu': ['Plan de travail'], 'maq': ['Brûlures maquillées'], 'sec': ['Pansements pour brûlés, couverture']}, '', ['Comment avez-vous évalué la gravité ?']))

L.append(sc(SU, 'su-msp07', 7, 'MSP07', 'crit', 'J4', 'MSP adaptée aux besoins', 3,
    'Violences intrafamiliales', 'Détecter une situation de violences et adapter sa conduite',
    'Prendre en charge la victime, détecter les signes de violences, adapter sa conduite, rendre compte au chef d’agrès.', 'Domicile',
    'Équipage VSAV', ['trauma'],
    ['Détecter des signes de violences', 'Adapter sa conduite et assurer la sécurité', 'Rendre compte'],
    'Départ VSAV : « Femme tombée dans l’escalier. »', 'Mme Simon (34 ans) présente des ecchymoses d’âges différents ; son conjoint répond à sa place.',
    [R('Victime', 'Mme Simon, 34 ans', 'Vous dites être tombée.', 'Regards inquiets vers votre conjoint.', ['Ecchymoses d’âges différents']),
     R('Tiers', 'Conjoint', 'Vous répondez à la place de votre compagne.', 'Vous devenez agressif si on vous demande de sortir.', [])],
    [['Situation repérée', 'Le chef d’agrès est informé.'], ['Signes ignorés', 'La victime reste au domicile.']],
    ['Bilan', 'Repérer les incohérences', 'Assurer la sécurité de l’équipe', 'Rendre compte au chef d’agrès'],
    {'c6': 'Détecte la situation, adapte sa conduite', 'c2': 'Sécurité', 'c5': 'Bilan', 'c3': 'Rend compte'},
    {'maq': ['Ecchymoses'], 'sec': ['Sac VSAV']}, 'Débriefing attentif : sujet sensible.', ['Quels signes vous ont alertés ?'], duree='30 min + 20 min de débriefing'))

L.append(sc(SU, 'su-msp07b', 8, 'MSP07', 'crit', 'J5', 'MSP adaptée aux besoins', 3,
    'Douleur thoracique au travail', 'Synthèse : détresse circulatoire évolutive',
    'Bilan, transmission au médecin régulateur, collaboration avec l’équipe médicale, surveillance pendant le transport.', 'Bureau',
    'Équipage VSAV, équipe SMUR jouée par un formateur', ['malaise', 'acr'],
    ['Reconnaître une douleur thoracique grave', 'Collaborer avec l’équipe médicale', 'Réagir à l’arrêt cardiaque'],
    'Départ VSAV : « Homme de 55 ans, douleur dans la poitrine. »', 'M. Fontaine (55 ans) a une douleur thoracique serrant depuis 20 minutes, en sueur.',
    [R('Victime', 'M. Fontaine, 55 ans', 'Douleur qui serre la poitrine et irradie dans le bras.', 'Arrêt cardiaque au bout de 10 minutes (passer au mannequin).', ['FC 105/min', 'PA 100/60', 'Sueurs'])],
    [['Transmission rapide et DAE posé', 'Choc délivré, reprise d’activité cardiaque.'], ['DAE non préparé', 'Retard au premier choc.']],
    ['Bilan', 'Transmission', 'Anticiper : DAE prêt', 'RCP', 'Collaboration avec le SMUR'],
    {'c7': 'Prise en charge de la détresse vitale', 'c4': 'Collaboration avec l’équipe médicale', 'c5': 'Bilan', 'c13': 'Surveillance'},
    {'acc': ['Mannequin RCP', 'DAE de formation'], 'sec': ['Sac VSAV, oxygène']}, 'DAE de formation uniquement.', ['Qu’avez-vous anticipé ?'], duree='30 min + 20 min de débriefing'))

# scénarios complémentaires (sujets absents du planning)
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenarios_complements import complements
L += complements({c: max([x['n'] for x in L if x['cur'] == c] or [0]) for c in ('PS', 'EQSUAP')})

root = os.path.join(os.path.dirname(__file__), '..')
with open(os.path.join(root, 'data', 'scenarios.json'), 'w', encoding='utf-8') as f:
    json.dump(L, f, ensure_ascii=False, indent=0)
print('scenarios.json :', len(L), 'scénarios')
