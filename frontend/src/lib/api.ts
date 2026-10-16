export type Lang = "en" | "it"
export type Bilingual = { en: string; it: string }
export type Label = "trusted" | "approximate" | "human"

export type CodeOption = { code: string; title: string; confidence: number }
export type CodeResult = CodeOption & { label: Label; alternatives: CodeOption[]; llm_pick: string | null }
export type CodeName = "event" | "source" | "nature" | "part"

export type SimilarCase = {
  upa: number; month: string; sector: string | null; narrative: string
  event: string; source: string; nature: string; part: string
}

export type Action = {
  type: string; standard: string
  action: Bilingual | string; why: Bilingual | string
  problems?: string[]
}

export type Analysis = {
  report: string
  codes: Record<CodeName, CodeResult>
  similar_cases: SimilarCase[]
  action_plan: {
    missing_info: (Bilingual | string)[]
    actions: Action[]
    rejected: Action[]
    // from_library: a section the Evolus agent found in its library and cited (not in the prompt's excerpts)
    standards: { section: string; topic: string; excerpt: string; from_library?: boolean }[]
    ecfr_date: string
  }
  second_opinion?: { model: string | null; measured_model: string; measured: boolean }
  // via/evolus_error/evolus are missing in recordings made before the Evolus agent was added.
  amd: {
    endpoint: string
    evolus?: boolean
    calls: {
      purpose: string; model: string; seconds: number; error: string | null
      via?: "evolus" | "token_factory"; evolus_error?: string | null
    }[]
  }
  seconds_total: number
  replay?: boolean
  recorded_at?: string
}

export type Sample = { id: string; title: Bilingual; text: string; has_replay: boolean }

export function pick(value: Bilingual | string | undefined, lang: Lang): string {
  if (!value) return ""
  return typeof value === "string" ? value : value[lang] || value.en
}

// Production: the API lives on another host (VITE_API_URL). Development: Vite proxies /api.
const API = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "")

async function json<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`)
  return response.json()
}

// Bundled copies (public/data, made by backend/core/export_static.py) keep the UI useful when the API is offline.
const bundled = <T,>(file: string) => fetch(`/data/${file}`).then((r) => json<T>(r))

async function withFallback<T>(live: () => Promise<T>, offline: () => Promise<T>): Promise<T> {
  try { return await live() } catch { return offline() }
}

export type Health = { online: boolean; evolus: boolean }

export async function apiHealth(): Promise<Health> {
  try {
    // Railway "serverless" sleeps when idle; waking up and loading the models takes up to ~30 s.
    const r = await fetch(`${API}/api/health`, { signal: AbortSignal.timeout(45000) })
    const body = r.ok ? await r.json() : {}
    return { online: body.ok === true, evolus: body.evolus === true }
  } catch { return { online: false, evolus: false } }
}

export const api = {
  analyze: (text: string) =>
    fetch(`${API}/api/analyze`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) })
      .then((r) => json<Analysis>(r)),
  samples: () => withFallback(
    () => fetch(`${API}/api/samples`).then((r) => json<Sample[]>(r)),
    () => bundled<Sample[]>("samples.json")),
  replay: (id: string) => withFallback(
    () => fetch(`${API}/api/replay/${id}`).then((r) => json<Analysis>(r)),
    () => bundled<Record<string, Analysis>>("replay.json").then((all) => all[id])),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  metrics: () => withFallback(() => fetch(`${API}/api/metrics`).then((r) => json<any>(r)), () => bundled<any>("metrics.json")),
}
