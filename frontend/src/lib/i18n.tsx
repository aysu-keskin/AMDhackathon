import { createContext, useContext, useState, type ReactNode } from "react"
import type { Lang } from "./api"

const en = {
  appName: "Incident Coding Assistant",
  tagline: "From a free-text incident report to OSHA codes, similar real cases and a sourced action plan — with a person making the final call.",
  tabAnalyze: "Analyze",
  tabMeasure: "Measurement",
  reportLabel: "Incident report (English)",
  reportPlaceholder: "Describe what happened: task, machine or object, injury…",
  analyze: "Analyze",
  samples: "Sample reports (written by the team)",
  runLive: "Run live",
  replay: "Replay",
  waking: "Connecting to the live server… if it was asleep this takes up to 30 s. Replays work right away.",
  offlineBanner: "Live analysis is offline right now (free hosting). Recorded examples and the measurement page still work — use “Replay”.",
  replayBanner: "Recorded result from {date}. Not a live call — use “Run live” to call AMD Token Factory now.",
  stepCoder: "Coding the report (classifier)",
  stepGemma: "Second opinion — Gemma-4-31B-IT on AMD",
  stepDraft: "Drafting actions — DeepSeek-V4-Flash on AMD",
  stepDraftEvolus: "Drafting actions — our Evolus agent on DeepSeek-V4-Flash (AMD)",
  stepCases: "Searching similar OSHA cases",
  elapsed: "{s} s elapsed — usually 1–2 min",
  elapsedEvolus: "{s} s elapsed — usually 2–3 min: the Evolus agent searches its OSHA library first",
  codesTitle: "OSHA codes",
  event: "Event", source: "Source", nature: "Injury", part: "Body part",
  trusted: "Trusted", approximate: "Approximate", human: "Your decision",
  labelHelp: {
    trusted: "Model is confident and checks agree. Measured ≥ 93% correct on unseen 2025 data.",
    approximate: "Probably right, but check it. Source codes are always shown this way.",
    human: "The system is unsure here. Errors are about 5× more common in this band — please choose.",
  },
  confidence: "confidence",
  gemmaAgrees: "{model} agrees", gemmaPicks: "{model} suggests {code}",
  fallbackBanner: "{measured} is unavailable right now, so {model} gave the second opinion. Its agreement is shown but not measured, so “Trusted” on the event code uses the classifier-only rule (92.8% on 2025).",
  noSecondOpinion: "The second opinion is unavailable right now. “Trusted” on the event code uses the classifier-only rule (92.8% on 2025).",
  chooseCode: "Choose the right code",
  casesTitle: "Similar OSHA cases",
  casesHelp: "Real reports from OSHA's Severe Injury Reports (2024–2025), coded by OSHA.",
  planTitle: "Corrective action draft",
  planHelp: "Each action cites an OSHA standard that may be relevant. Edit, untick or keep — you decide.",
  missingTitle: "Questions that would change the plan",
  filtered: "{n} suggestion(s) removed by the validator",
  types: { engineering: "Engineering", administrative: "Administrative", training: "Training", ppe: "PPE" } as Record<string, string>,
  standardsUsed: "Standards excerpts given to the model (eCFR {date})",
  fromLibrary: "found by the Evolus agent in its library",
  approve: "Approve",
  approveBlocked: "Choose a code for every “Your decision” card first.",
  approved: "Approved by the safety officer",
  downloadJson: "Download JSON",
  print: "Print / save as PDF",
  amdTitle: "What ran on AMD",
  amdHelp: "LLM calls go to AMD Token Factory (AMD-hosted vLLM on AMD GPUs).",
  viaEvolus: "Written by our Evolus agent “Corrective Action Drafter” (workspace DarkSea28) with its library of 36 OSHA sections; the agent's model runs on AMD Token Factory.",
  evolusFallback: "The Evolus agent was unavailable, so this draft was written directly on AMD Token Factory.",
  total: "Total",
  error: "Something went wrong",
  // Measurement page
  mShiftTitle: "OSHA changed its code system on 1 January 2024",
  mShiftText: "The same numbers mean different things before and after. Group 65 did not exist; group 62 vanished overnight. Mixing the two systems silently breaks any model, so we keep them apart.",
  mBaselineTitle: "Classifier accuracy (time split, unseen years)",
  mOldText: "Old system: trained 2015–2021, tested on 2023 manufacturing — reproducing our pre-registered brief.",
  mNewText: "New system (the product): trained on 2024, tested on 2025 manufacturing.",
  mBrief: "Brief", mOurs: "Reproduced", mAccuracy: "Accuracy", mRows: "Test rows",
  mLabelsTitle: "Confidence labels on 2025 (thresholds fixed beforehand)",
  mLabelsText: "Rule: “trusted” where validation accuracy was ≥ 93%; source is never trusted; the least confident 20% go to a person.",
  mShare: "Share", mErrRatio: "Errors in the person band vs the rest",
  mSecondTitle: "Gemma second opinion on event type (500 reports, pre-registered)",
  mStrict: "Pre-registered scoring", mRescored: "After the declared deviation",
  mDeviation: "Gemma often answered “65: Struck by…” instead of “65”. Our strict parser counted these as disagreement and the test failed. We wrote down a parsing fix before re-scoring the same answers, and we show both results. The re-scored result is weaker evidence.",
  mRule: "Rule", mTrustedShare: "Trusted share", mTrustedAcc: "Accuracy when trusted", mPass: "Pass",
  mBaselineOnly: "Classifier only", mRuleB: "Classifier + Gemma agree (in product)", mRuleA: "Rule A",
  mLimitsTitle: "Limits we don't hide",
  mLimits: [
    "Data is from the US and covers severe injuries only; Turkish or Italian factories may differ.",
    "Event type alone missed the 93% target by 0.2 points (92.8%); Gemma's agreement lifts it to 94.4% (re-scored).",
    "Source codes are hard (≈ 63% top-1); the person always chooses them.",
    "Corrective-action drafts are not measured; a validator only blocks unknown standards and legal or medical verdicts.",
  ],
}

type Dict = typeof en

const it: Dict = {
  ...en,
  appName: "Assistente di codifica infortuni",
  tagline: "Da una segnalazione libera a codici OSHA, casi reali simili e un piano d’azione con fonti — la decisione finale resta a una persona.",
  tabAnalyze: "Analisi",
  tabMeasure: "Misurazione",
  reportLabel: "Segnalazione dell’infortunio (in inglese)",
  reportPlaceholder: "Descrivi cosa è successo: attività, macchina o oggetto, lesione…",
  analyze: "Analizza",
  samples: "Segnalazioni di esempio (scritte dal team)",
  runLive: "Esegui dal vivo",
  replay: "Registrazione",
  waking: "Connessione al server dal vivo… se era in pausa servono fino a 30 s. Le registrazioni funzionano subito.",
  offlineBanner: "L’analisi dal vivo è offline in questo momento (hosting gratuito). Gli esempi registrati e la pagina di misurazione funzionano — usa “Registrazione”.",
  replayBanner: "Risultato registrato il {date}. Non è una chiamata dal vivo — usa “Esegui dal vivo” per chiamare ora AMD Token Factory.",
  stepCoder: "Codifica della segnalazione (classificatore)",
  stepGemma: "Secondo parere — Gemma-4-31B-IT su AMD",
  stepDraft: "Bozza delle azioni — DeepSeek-V4-Flash su AMD",
  stepDraftEvolus: "Bozza delle azioni — il nostro agente Evolus su DeepSeek-V4-Flash (AMD)",
  stepCases: "Ricerca di casi OSHA simili",
  elapsed: "{s} s trascorsi — di solito 1–2 min",
  elapsedEvolus: "{s} s trascorsi — di solito 2–3 min: l’agente Evolus consulta prima la sua biblioteca OSHA",
  codesTitle: "Codici OSHA",
  event: "Evento", source: "Fonte", nature: "Lesione", part: "Parte del corpo",
  trusted: "Affidabile", approximate: "Approssimativo", human: "Decidi tu",
  labelHelp: {
    trusted: "Il modello è sicuro e i controlli concordano. Misurato ≥ 93% corretto su dati 2025 mai visti.",
    approximate: "Probabilmente giusto, ma verificalo. I codici della fonte sono sempre mostrati così.",
    human: "Il sistema non è sicuro. Qui gli errori sono circa 5 volte più frequenti — scegli tu.",
  },
  confidence: "confidenza",
  gemmaAgrees: "{model} concorda", gemmaPicks: "{model} suggerisce {code}",
  fallbackBanner: "{measured} non è disponibile in questo momento, quindi il secondo parere è di {model}. Il suo accordo è mostrato ma non misurato, quindi “Affidabile” sul codice evento usa la regola del solo classificatore (92,8% sul 2025).",
  noSecondOpinion: "Il secondo parere non è disponibile in questo momento. “Affidabile” sul codice evento usa la regola del solo classificatore (92,8% sul 2025).",
  chooseCode: "Scegli il codice corretto",
  casesTitle: "Casi OSHA simili",
  casesHelp: "Segnalazioni reali dai Severe Injury Reports dell’OSHA (2024–2025), codificate dall’OSHA.",
  planTitle: "Bozza di azioni correttive",
  planHelp: "Ogni azione cita uno standard OSHA che potrebbe essere pertinente. Modifica, deseleziona o conserva — decidi tu.",
  missingTitle: "Domande che cambierebbero il piano",
  filtered: "{n} suggerimento/i rimosso/i dal validatore",
  types: { engineering: "Ingegneristica", administrative: "Organizzativa", training: "Formazione", ppe: "DPI" },
  standardsUsed: "Estratti degli standard forniti al modello (eCFR {date})",
  fromLibrary: "trovato dall’agente Evolus nella sua biblioteca",
  approve: "Approva",
  approveBlocked: "Prima scegli un codice per ogni scheda “Decidi tu”.",
  approved: "Approvato dal responsabile della sicurezza",
  downloadJson: "Scarica JSON",
  print: "Stampa / salva in PDF",
  amdTitle: "Cosa è stato eseguito su AMD",
  amdHelp: "Le chiamate LLM vanno ad AMD Token Factory (vLLM ospitato da AMD su GPU AMD).",
  viaEvolus: "Scritta dal nostro agente Evolus “Corrective Action Drafter” (workspace DarkSea28) con la sua biblioteca di 36 sezioni OSHA; il modello dell’agente gira su AMD Token Factory.",
  evolusFallback: "L’agente Evolus non era disponibile, quindi questa bozza è stata scritta direttamente su AMD Token Factory.",
  total: "Totale",
  error: "Qualcosa è andato storto",
  mShiftTitle: "L’OSHA ha cambiato il sistema di codifica il 1° gennaio 2024",
  mShiftText: "Gli stessi numeri hanno significati diversi prima e dopo. Il gruppo 65 non esisteva; il gruppo 62 è scomparso dall’oggi al domani. Mescolare i due sistemi rompe silenziosamente ogni modello, quindi li teniamo separati.",
  mBaselineTitle: "Accuratezza del classificatore (divisione temporale, anni mai visti)",
  mOldText: "Sistema vecchio: addestrato 2015–2021, testato sulla manifattura 2023 — riproduce il nostro documento pre-registrato.",
  mNewText: "Sistema nuovo (il prodotto): addestrato sul 2024, testato sulla manifattura 2025.",
  mBrief: "Documento", mOurs: "Riprodotto", mAccuracy: "Accuratezza", mRows: "Righe di test",
  mLabelsTitle: "Etichette di confidenza sul 2025 (soglie fissate prima)",
  mLabelsText: "Regola: “affidabile” dove l’accuratezza di validazione era ≥ 93%; la fonte non è mai affidabile; il 20% meno sicuro va a una persona.",
  mShare: "Quota", mErrRatio: "Errori nella fascia “persona” rispetto al resto",
  mSecondTitle: "Secondo parere di Gemma sul tipo di evento (500 segnalazioni, pre-registrato)",
  mStrict: "Valutazione pre-registrata", mRescored: "Dopo la deviazione dichiarata",
  mDeviation: "Gemma spesso rispondeva “65: Struck by…” invece di “65”. Il nostro parser rigido le contava come disaccordo e il test non è passato. Abbiamo scritto una correzione del parsing prima di rivalutare le stesse risposte e mostriamo entrambi i risultati. Il risultato rivalutato è una prova più debole.",
  mRule: "Regola", mTrustedShare: "Quota affidabile", mTrustedAcc: "Accuratezza se affidabile", mPass: "Superato",
  mBaselineOnly: "Solo classificatore", mRuleB: "Classificatore + Gemma concordano (nel prodotto)", mRuleA: "Regola A",
  mLimitsTitle: "Limiti che non nascondiamo",
  mLimits: [
    "I dati sono statunitensi e coprono solo infortuni gravi; le fabbriche turche o italiane possono essere diverse.",
    "Il solo tipo di evento ha mancato l’obiettivo del 93% di 0,2 punti (92,8%); l’accordo di Gemma lo porta al 94,4% (rivalutato).",
    "I codici della fonte sono difficili (≈ 63% al primo posto); la persona li sceglie sempre.",
    "Le bozze di azioni correttive non sono misurate; un validatore blocca solo standard sconosciuti e giudizi legali o medici.",
  ],
}

const dictionaries: Record<Lang, Dict> = { en, it }

const LangContext = createContext<{ lang: Lang; setLang: (l: Lang) => void; t: Dict }>({
  lang: "en", setLang: () => {}, t: en,
})

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(() => {
    try { return (localStorage.getItem("lang") as Lang) || "en" } catch { return "en" }
  })
  const change = (l: Lang) => {
    setLang(l)
    try { localStorage.setItem("lang", l) } catch { /* private mode */ }
  }
  return <LangContext.Provider value={{ lang, setLang: change, t: dictionaries[lang] }}>{children}</LangContext.Provider>
}

export const useLang = () => useContext(LangContext)

export function fill(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, key) => String(values[key] ?? ""))
}
