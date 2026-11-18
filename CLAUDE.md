# FORSSUAP 78 — notes de développement

Application d'évaluation hors ligne (PWA + APK Android) pour le **SDIS 78 – Groupement Formation** :
formation des équipiers SSUAP SPV/SPP, référentiels **RIOFE** du SDIS 78
(référentiel technique : https://spf-editions.fr/sdis-78/sommaire).
Projet indépendant, dérivé de l'app « Eval » (UDPS 28, dépôt forma-st/udps28-eval) : ne rien partager avec elle.

Langue : l'utilisateur travaille en **français** ; interface, PDF, messages de commit en français.

## Architecture
- `src/app.html` : application complète en un seul fichier (JS vanilla). État `S`, actions `A` (`data-act`),
  liaisons `data-bind` / `data-scope`. Données dans localStorage (clé `forssuap78-v1`), audio dans IndexedDB `forssuap78-audio`.
- `build.py` injecte les données (`__LOGO__`, `__MARK__`, `__QCM__`, `__FICHES__`, `__FORM_FILES__`, `__SCENARIOS__`, `__RIOFE__`, `__FORMATION__`)
  et produit `fichier-unique.html` + `docs/app/` (PWA, service worker). Toujours relancer `python3 build.py` après modification.
- `docs/` = GitHub Pages (https://forma-st.github.io/FORSSUAP78/), `docs/FORSSUAP78.apk`, `docs/qr.png`.
- Android : Capacitor 6 dans `mobile/` (appId `fr.sdis78.forssuap`). Build :
  `cd mobile && npx cap sync android && cd android && ./gradlew assembleDebug --no-daemon -q --max-workers=2`
  puis copier `app/build/outputs/apk/debug/app-debug.apk` vers `docs/FORSSUAP78.apk`.
  Il faut un SDK Android (ANDROID_HOME) et JDK 17 ; dl.google.com est autorisé dans l'environnement.
  Incrémenter `versionCode`/`versionName` (mobile/android/app/build.gradle) et `APP_VERSION` (src/app.html). Version actuelle : 1.2.0 (code 4).
- `tools/brand.py` : toutes les images (logo PDF, icônes web, mipmaps, splash) depuis `brand/logo-sdis78-source.png`.
- `vendor/` : jsPDF, SDK Anthropic (bundle esbuild), client ElevenLabs (bundle).
- `relay/` : Cloudflare Worker (relais IA `/v1/messages` + `/eleven/session`), nom `forssuap78-relais`.

## Deux espaces (écran d'accueil `home`)
- **Espace administratif** (`S.space='admin'`, onglets Formations / Grilles / Réglages) : formations, participants, présence,
  fiches MSP, grilles sommatives, attestations.
- **Espace formation** (`S.space='form'`, onglets Planning / Séquences / Scénarios MSP) : vues `planning`, `modules`, `module`, `present`
  (diaporama plein écran : flèches, balayage, notes formateur) et `scenarios`. Le planning se cale sur les journées d'une formation choisie
  (`S.fsid`) ; « Évaluer » sur une MSP ouvre la fiche MSP pré-remplie (thème, missions, réf.) dans cette formation.
- Données : `tools/formation.py` → `data/formation.json` (plannings PS d'après le programme de la valise, SUAP d'après le chronogramme RIOFE p. 16 ;
  modules séquences/APP avec fiche + diapositives ; seule la séquence 1 est reprise d'un document fourni, les autres sont marquées « à valider »).
  `tools/scenarios_sdis78.py` → `data/scenarios.json` (16 scénarios MSP, `observe` indexé par les savoir-agir RIOFE, `tpl` auto/crit).

## Référentiels RIOFE
- Sources : `modeles/riofe/` (RIOFE_EQ_SPV_SUAP.pdf, RIOFE_EQ_SPV_MODULE_TRANSVERSE.pdf, RIOFE_CHEF_EQUIPE_SPP.pdf), valise pédagogique `modeles/valise/`.
- `tools/riofe.py` extrait contenu + géométrie → `data/riofe.json` et rend les fonds de page `docs/app/forms/riofe-*.png` (200 dpi).
- Cursus : `PS` (Prompt Secours, module transverse, 7 colonnes MSP) et `EQSUAP` (Équipier SUAP, 9 colonnes MSP + compétences transversales).
  Le RIOFE Chef d'équipe SPP n'est **pas** utilisé pour l'instant (décision utilisateur : seule la partie SSUAP équipier SPV).
- Les anciennes grilles PSE ont été supprimées (`builtinTemplatesPSE`, `seedSamplesPSE` sont des restes inactifs, nettoyables).
- Niveaux : A (vert) / ECA (orange) / NA (rouge). Un savoir-agir est validé s'il est observé ≥ 2 fois au niveau minimal requis ;
  un savoir-agir non validé fait échouer son bloc.
- **Autoévaluation accompagnée** : le stagiaire coche d'abord (case hachurée + contour pointillé, `l.self`), puis le formateur valide
  ou corrige (croix, `l.marks`). **Fiche critériée** : seul le formateur coche.
- Code : module RIOFE en tête de `src/app.html` (`RIOFE_COURSES`, `riofeTemplates`, `riofeGrid`) et PDF
  (`drawRiofeSheet`, `riofeSheetPages`, `riofeSommPages`, `riofeAttestPages`, zones `RIOFE_ATTEST` en points).
- Exigence forte : les exports PDF **respectent rigoureusement les documents d'origine** (fond = page d'origine + surimpression mesurée).

## Règles de sécurité (impératives)
- ElevenLabs : ne jamais ouvrir/afficher un fichier .env ; ne jamais demander ni accepter une clé dans le chat ; jamais de clé dans le code
  (le SDK lit `ELEVENLABS_API_KEY`). Les clés passent par les secrets réseau de l'environnement (formulaire sécurisé).
  L'environnement sdis78 n'a **pas encore** de secret ElevenLabs ni d'agent dédié (`EL_AGENT_DEFAULT=''`).
- Jamais de noms de participants dans les requêtes IA. `.env.local` et le keystore ne sont jamais commités.

## Tests
Serveur local : `cd docs/app && python3 -m http.server 8779`, puis Playwright (Chromium préinstallé).
`window.__app` expose DB, A, buildPdf, formativePages, certPages, riofeAttestPages, riofeSommPages, ensureCert, ensureDays…
Vérifier les PDF en les rendant en PNG (`pdftoppm`) et en contrôlant visuellement le placement.

## Tâches restantes
1. Faire relire et compléter par l'équipe pédagogique les modules et scénarios (fiches séquences fournies au fur et à mesure).
2. **Régulation adaptée SDIS** : simulation d'appel CTA-CODIS / CRRA 15, chef d'agrès VSAV ; agent ElevenLabs dédié FORSSUAP
   (nécessite le secret ElevenLabs sur cet environnement, via le formulaire sécurisé) puis renseigner `EL_AGENT_DEFAULT`.
3. **Feuille d'émargement** à compléter à l'export — modèle à fournir par l'utilisateur.
4. Diplôme Équipier SUAP (modèle GEEF à fusion) : non implémenté, à voir avec l'utilisateur.
5. Nettoyage des restes PSE (fonds `docs/app/forms` PSE, QCM PSE, fiches pédagogiques PSE) si l'utilisateur le confirme.
