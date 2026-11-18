// Crée l'agent vocal « régulation » de FORSSUAP 78 chez ElevenLabs, avec les bons réglages.
// Usage :  ELEVENLABS_API_KEY=... npm run creer-agent            (agent privé, via le relais : recommandé)
//          ELEVENLABS_API_KEY=... npm run creer-agent -- --public (agent public, pour un essai rapide sans relais)
// Variables facultatives : ELEVENLABS_VOICE_ID (voix française choisie dans la bibliothèque de voix ElevenLabs),
// ELEVENLABS_ALLOWLIST (agent public : adresses autorisées, séparées par des virgules).
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const apiKey = process.env.ELEVENLABS_API_KEY;
if (!apiKey) {
  console.error("Indiquez la clé : ELEVENLABS_API_KEY=xxxx npm run creer-agent");
  process.exit(1);
}
const isPublic = process.argv.includes("--public");
const client = new ElevenLabsClient({ apiKey });

const agent = await client.conversationalAi.agents.create({
  name: "FORSSUAP 78 - Régulation",
  conversationConfig: {
    agent: {
      firstMessage: "Le SAMU, j’écoute.",
      language: "fr",
      prompt: {
        // Le rôle détaillé et le scénario sont envoyés par FORSSUAP 78 au début de chaque appel.
        prompt: "Tu joues l’ARM du SAMU 78 (CRRA 15) qui prend le bilan des sapeurs-pompiers, et le médecin régulateur en cas de détresse importante, dans un exercice de formation du SDIS 78. Tu parles français, au téléphone, en phrases courtes.",
        llm: "claude-sonnet-5-5",
      },
    },
    // Voix par défaut : « Hugo - Warm and Grounded » (français standard), à ajouter d'abord à « My Voices » ; ELEVENLABS_VOICE_ID pour une autre voix.
    tts: { modelId: "eleven_flash_v2_5", voiceId: process.env.ELEVENLABS_VOICE_ID || "IbbR6Av0dWuQJS0b8JVT" },
    // « patient » : l'agent laisse le temps d'hésiter avant de répondre ; relance après 8 s de silence.
    turn: { turnEagerness: "patient", turnTimeout: 8 },
    // Garde-fou de coût : un appel d'exercice ne dépasse pas 10 minutes.
    conversation: { maxDurationSeconds: 600 },
  },
  platformSettings: {
    // FORSSUAP 78 envoie à chaque appel le rôle, le scénario, le niveau et la première phrase.
    overrides: { conversationConfigOverride: { agent: { firstMessage: true, language: true, prompt: { prompt: true } }, tts: { voiceId: true } } },
    // Agent public : seules l'application publiée et l'application Android (origine « localhost ») peuvent l'appeler.
    auth: isPublic
      ? { enableAuth: false, allowlist: (process.env.ELEVENLABS_ALLOWLIST || "forma-st.github.io,localhost").split(",").map((h) => ({ hostname: h.trim() })) }
      : { enableAuth: true },
    // Garde-fous de coût : 3 appels simultanés au plus, 40 appels par jour au plus.
    callLimits: { agentConcurrencyLimit: 3, dailyLimit: 40, burstingEnabled: false },
  },
});

console.log("\nAgent créé. Identifiant :", agent.agentId);
console.log(isPublic
  ? "Mode public : collez cet identifiant dans FORSSUAP 78 (Réglages > Régulation SAMU simulée > Voix de l'appel)."
  : "Enregistrez-le sur le relais :  npx wrangler secret put ELEVENLABS_AGENT_ID");
console.log("Voix : Hugo (français). Pour en changer : tableau de bord ElevenLabs > Agents > FORSSUAP 78 - Régulation > Voice.\n");
