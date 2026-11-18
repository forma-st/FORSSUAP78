# FORSSUAP 78 — notes de développement

Application d'évaluation hors ligne (PWA + APK Android) pour le **SDIS 78 – Groupement Formation** :
formation des équipiers SSUAP SPV/SPP, référentiels **RIOFE** du SDIS 78
(référentiel technique : https://spf-editions.fr/sdis-78/sommaire).
Projet indépendant, dérivé de l'app « Eval » (UDPS 28, dépôt forma-st/udps28-eval) : ne rien partager avec elle.

Langue : l'utilisateur travaille en **français** ; interface, PDF, messages de commit en français.

## Architecture
- `src/app.html` : application complète en un seul fichier (JS vanilla). État `S`, actions `A` (`data-act`),
  liaisons `data-bind` / `data-scope`. Données dans localStorage (clé `forssuap78-v1`), audio dans IndexedDB `forssuap78-audio`.
- `build.py` injecte les données (`__LOGO__`, `__MARK__`, `__FORM_FILES__`, `__SCENARIOS__`, `__RIOFE__`)
  et produit `fichier-unique.html` + `docs/app/` (PWA, service worker). Toujours relancer `python3 build.py` après modification.
- `docs/` = GitHub Pages (https://forma-st.github.io/FORSSUAP78/), `docs/FORSSUAP78.apk`, `docs/qr.png`.
- Android : Capacitor 6 dans `mobile/` (appId `fr.sdis78.forssuap`). Build :
  `cd mobile && npx cap sync android && cd android && ./gradlew assembleDebug --no-daemon -q --max-workers=2`
  puis copier `app/build/outputs/apk/debug/app-debug.apk` vers `docs/FORSSUAP78.apk`.
  Il faut un SDK Android (ANDROID_HOME) et JDK 17 ; dl.google.com est autorisé dans l'environnement.
  Incrémenter `versionCode`/`versionName` (mobile/android/app/build.gradle) et `APP_VERSION` (src/app.html). Version actuelle : 1.2.1 (code 5).
- `tools/brand.py` : toutes les images (logo PDF, icônes web, mipmaps, splash) depuis `brand/logo-sdis78-source.png`.
- `vendor/` : jsPDF, SDK Anthropic (bundle esbuild), client ElevenLabs (bundle).
- `relay/` : Cloudflare Worker (relais IA `/v1/messages` + `/eleven/session`), nom `forssuap78-relais`.

## Référentiels RIOFE
- Sources : `modeles/riofe/` (RIOFE_EQ_SPV_SUAP.pdf, RIOFE_EQ_SPV_MODULE_TRANSVERSE.pdf, RIOFE_CHEF_EQUIPE_SPP.pdf), valise pédagogique `modeles/valise/`.
- `tools/riofe.py` extrait contenu + géométrie → `data/riofe.json` et rend les fonds de page `docs/app/forms/riofe-*.png` (200 dpi).
- Cursus : `PS` (Prompt Secours, module transverse, 7 colonnes MSP) et `EQSUAP` (Équipier SUAP, 9 colonnes MSP + compétences transversales).
  Le RIOFE Chef d'équipe SPP n'est **pas** utilisé pour l'instant (décision utilisateur : seule la partie SSUAP équipier SPV).
- Tous les restes PSE / CE / PIC F / PAE FPSE ont été supprimés en v1.2.0 (grilles, exemples, QCM, fiches pédagogiques, fonds de page,
  rendus PDF sur fonds, modèles PDF, outils). Les grilles fournies obsolètes encore stockées sur un appareil sont purgées au chargement
  (sauf si modifiées). L’app Eval PSE (forma-st/udps28-eval) garde les siens : ne rien y toucher depuis ce dépôt.
- Niveaux : A (vert) / ECA (orange) / NA (rouge). Un savoir-agir est validé s'il est observé ≥ 2 fois au niveau minimal requis ;
  un savoir-agir non validé fait échouer son bloc.
- **Autoévaluation accompagnée** : le stagiaire coche d'abord (case hachurée + contour pointillé, `l.self`), puis le formateur valide
  ou corrige (croix, `l.marks`). **Fiche critériée** : seul le formateur coche.
- Code : module RIOFE en tête de `src/app.html` (`RIOFE_COURSES`, `riofeTemplates`, `riofeGrid`) et PDF
  (`drawRiofeSheet`, `riofeSheetPages`, `riofeSommPages`, `riofeAttestPages`, zones `RIOFE_ATTEST` en points).
- Exigence forte : les exports PDF **respectent rigoureusement les documents d'origine** (fond = page d'origine + surimpression mesurée).

## Scénarios MSP
- `tools/scenarios_sdis78.py` → `data/scenarios.json` : 11 scénarios Prompt Secours (`ps-01`…) et 14 Équipier SUAP (`suap-01`…, MSP01–07).
- `observe` = savoirs-agir RIOFE (`c22`…`c32` PS, `c1`…`c15` SUAP) ; `cases` = thèmes en pastilles, propres au cursus (`SC_TAGS`).
- « Évaluer ce cas » crée une fiche MSP (autoévaluation accompagnée) pré-remplie : thème, missions (objectifs), réf. MSP.

## Régulation simulée (SAMU 78 – CRRA 15 : bilan pompier)
- **Pas de CTA-CODIS** (décision utilisateur). Accueil : « Le SAMU, j’écoute. » (`AI_GREETING`, identique au first message de l’agent).
- `callSystem` : l’ARM (PARM) du CRRA 15 prend tout le bilan pompier ; il ne passe le médecin régulateur **qu’en cas de détresse
  importante** (détresse vitale, signes de gravité, traumatisme grave, douleur thoracique, accouchement / nouveau-né, enfant grave,
  plusieurs victimes graves). Appelant = prompt secours seul (PS) ou équipier / chef d’agrès VSAV (EQSUAP, niveau avancé).
- `debriefSystem` : correction du bilan, proposition A / ECA / NA sur C24 (PS) ou C4-C5 (SUAP).
- Agent ElevenLabs « SDIS 78 Régulation 15 » (voix Claire) : `EL_AGENT_DEFAULT='agent_4401m7ptk799fpxvzbprhgfr232b'` (mode « Agent public »).
  Il doit autoriser les surcharges par appel (prompt, first message, language) et être limité à forma-st.github.io et localhost.
- Secret réseau ElevenLabs enregistré sur l’environnement « sdis78 » (hôte api.elevenlabs.io, en-tête xi-api-key), droits ElevenAgents
  en écriture et voix en lecture (lecture / modification de l’agent, jetons, URL signées, liste des voix : OK). Le proxy de la session bloque les
  WebSocket (404) : l’appel vocal ne se teste que dans un vrai navigateur. Agent vérifié le 18/11/2026 : surcharges prompt / first message /
  language autorisées, allowlist forma-st.github.io + localhost, auth désactivée, 600 s max, 3 appels simultanés, 40 / jour,
  voix **Claire - Customer service** `HuLbOdhRlvQQN8oPP0AJ` (française, féminine), modèle eleven_flash_v2_5. L’application ne surcharge pas la voix.

## Règles de sécurité (impératives)
- ElevenLabs : ne jamais ouvrir/afficher un fichier .env ; ne jamais demander ni accepter une clé dans le chat ; jamais de clé dans le code
  (le SDK lit `ELEVENLABS_API_KEY`). Les clés passent par les secrets réseau de l'environnement (formulaire sécurisé).
- Jamais de noms de participants dans les requêtes IA. `.env.local` et le keystore ne sont jamais commités.

## Tests
Serveur local : `cd docs/app && python3 -m http.server 8779`, puis Playwright (Chromium préinstallé).
`window.__app` expose DB, A, buildPdf, formativePages, certPages, riofeAttestPages, riofeSommPages, ensureCert, ensureDays…
Vérifier les PDF en les rendant en PNG (`pdftoppm`) et en contrôlant visuellement le placement.

## Tâches restantes
1. Faire valider les scénarios MSP par l’équipe pédagogique (contenu, adresses, jours) ; tester un appel vocal réel avec l’agent Claire.
2. **Feuille d'émargement** à compléter à l'export — modèle à fournir par l'utilisateur.
3. Diplôme Équipier SUAP (modèle GEEF à fusion) : non implémenté, à voir avec l'utilisateur.
4. Code générique encore présent mais sans usage RIOFE (technicité, fiches de suivi, QCM, certificat / attestation FC génériques) : à garder
   tant que des grilles personnalisées peuvent s’en servir.
