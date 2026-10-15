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
    standards: { section: string; topic: string; excerpt: string }[]
    ecfr_date: string
  }
  amd: { endpoint: string; calls: { purpose: string; model: string; seconds: number; error: string | null }[] }
  seconds_total: number
  replay?: boolean
  recorded_at?: string
}

export type Sample = { id: string; title: Bilingual; text: string; has_replay: boolean }

export function pick(value: Bilingual | string | undefined, lang: Lang): string {
  if (!value) return ""
  return typeof value === "string" ? value : value[lang] || value.en
}

async function json<T>(response: Response): Promise<T> {
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`)
  return response.json()
}

export const api = {
  analyze: (text: string) =>
    fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) })
      .then((r) => json<Analysis>(r)),
  samples: () => fetch("/api/samples").then((r) => json<Sample[]>(r)),
  replay: (id: string) => fetch(`/api/replay/${id}`).then((r) => json<Analysis>(r)),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  metrics: () => fetch("/api/metrics").then((r) => json<any>(r)),
}
