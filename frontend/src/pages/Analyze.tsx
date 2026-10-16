import { useEffect, useMemo, useState } from "react"
import { AlertTriangle, Check, CheckCircle2, Cpu, Download, Loader2, Play, Printer, RotateCcw } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { api, apiHealth, pick, type Action, type Analysis, type CodeName, type CodeOption, type Label, type Sample } from "@/lib/api"
import { fill, useLang } from "@/lib/i18n"
import { cn } from "@/lib/utils"

const CODE_ORDER: CodeName[] = ["event", "nature", "part", "source"]

const LABEL_STYLE: Record<Label, string> = {
  trusted: "bg-emerald-100 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-200",
  approximate: "bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200",
  human: "bg-rose-100 text-rose-900 dark:bg-rose-950 dark:text-rose-200",
}

export function Analyze() {
  const { t, lang } = useLang()
  const [text, setText] = useState("")
  const [samples, setSamples] = useState<Sample[]>([])
  const [result, setResult] = useState<Analysis | null>(null)
  const [busySince, setBusySince] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [online, setOnline] = useState<boolean | null>(null)
  const [evolus, setEvolus] = useState(false)

  useEffect(() => {
    api.samples().then(setSamples).catch(() => setSamples([]))
    apiHealth().then((h) => { setOnline(h.online); setEvolus(h.evolus) })
  }, [])

  async function run(fn: () => Promise<Analysis>) {
    setError(null); setResult(null); setBusySince(Date.now())
    try { setResult(await fn()) } catch (e) { setError(String(e)) } finally { setBusySince(null) }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
      <div className="grid min-w-0 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>{t.reportLabel}</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4">
            <Textarea value={text} onChange={(e) => setText(e.target.value)} placeholder={t.reportPlaceholder}
              className="min-h-28" maxLength={4000} />
            <div className="flex flex-wrap items-center gap-3">
              <Button disabled={busySince !== null || online === false || text.trim().length < 20} onClick={() => run(() => api.analyze(text))}>
                {busySince ? <Loader2 className="animate-spin" /> : <Play />} {t.analyze}
              </Button>
            </div>
            <div className="grid gap-2">
              <p className="text-sm text-muted-foreground">{t.samples}</p>
              <div className="grid gap-2 sm:grid-cols-2">
                {samples.map((s) => (
                  <div key={s.id} className="flex items-center justify-between gap-2 rounded-lg border p-2 text-sm">
                    <button className="min-w-0 truncate text-left hover:underline" onClick={() => setText(s.text)}>
                      {s.title[lang]}
                    </button>
                    <div className="flex shrink-0 gap-1">
                      <Button size="sm" variant="outline" disabled={busySince !== null || online === false}
                        onClick={() => { setText(s.text); run(() => api.analyze(s.text)) }}>{t.runLive}</Button>
                      {s.has_replay && (
                        <Button size="sm" variant="ghost" disabled={busySince !== null}
                          onClick={() => { setText(s.text); run(() => api.replay(s.id)) }}>
                          <RotateCcw /> {t.replay}
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {online === null && (
          <Alert><Loader2 className="animate-spin" /><AlertDescription>{t.waking}</AlertDescription></Alert>
        )}
        {online === false && (
          <Alert><AlertTriangle /><AlertDescription>{t.offlineBanner}</AlertDescription></Alert>
        )}
        {busySince && <Progress since={busySince} evolus={evolus} />}
        {error && (
          <Alert variant="destructive"><AlertTriangle /><AlertDescription>{t.error}: {error}</AlertDescription></Alert>
        )}
        {result && <Result key={result.recorded_at ?? result.seconds_total} result={result} />}
      </div>
      <aside className="grid content-start gap-6">
        {result ? <AmdPanel result={result} /> : <Intro evolus={evolus} />}
      </aside>
    </div>
  )
}

function Intro({ evolus }: { evolus: boolean }) {
  const { t } = useLang()
  return (
    <Card>
      <CardHeader><CardTitle className="flex items-center gap-2"><Cpu className="size-4" /> {t.amdTitle}</CardTitle></CardHeader>
      <CardContent className="grid gap-2 text-sm text-muted-foreground">
        <p>{t.amdHelp}</p>
        <ul className="grid gap-1">
          <li>• {t.stepGemma}</li>
          <li>• {evolus ? t.stepDraftEvolus : t.stepDraft}</li>
        </ul>
      </CardContent>
    </Card>
  )
}

function Progress({ since, evolus }: { since: number; evolus: boolean }) {
  const { t } = useLang()
  const [now, setNow] = useState(Date.now())
  useEffect(() => { const id = setInterval(() => setNow(Date.now()), 500); return () => clearInterval(id) }, [])
  const seconds = Math.round((now - since) / 1000)
  // The server answers once, so only the local steps can be shown as done; the two AMD calls run in parallel.
  const steps = [
    { label: t.stepCoder, done: seconds >= 1 },
    { label: t.stepCases, done: seconds >= 1 },
    { label: t.stepGemma, done: false },
    { label: evolus ? t.stepDraftEvolus : t.stepDraft, done: false },
  ]
  return (
    <Card>
      <CardContent className="grid gap-3 pt-6">
        {steps.map((s) => (
          <div key={s.label} className="flex items-center gap-3 text-sm">
            {s.done ? <Check className="size-4 text-emerald-600" /> : <Loader2 className="size-4 animate-spin text-muted-foreground" />}
            <span className={cn(!s.done && "font-medium")}>{s.label}</span>
          </div>
        ))}
        <p className="text-xs text-muted-foreground">{fill(evolus ? t.elapsedEvolus : t.elapsed, { s: seconds })}</p>
      </CardContent>
    </Card>
  )
}

function Result({ result }: { result: Analysis }) {
  const { t, lang } = useLang()
  const [choices, setChoices] = useState<Partial<Record<CodeName, string>>>({})
  const [kept, setKept] = useState<boolean[]>(() => result.action_plan.actions.map(() => true))
  const [edits, setEdits] = useState<Record<number, string>>({})
  const [approvedAt, setApprovedAt] = useState<string | null>(null)

  const needsChoice = CODE_ORDER.filter((n) => result.codes[n].label === "human" && !choices[n])
  const finalCodes = useMemo(() => Object.fromEntries(CODE_ORDER.map((n) => {
    const c = result.codes[n]
    const options = [c as CodeOption, ...c.alternatives]
    const chosen = options.find((o) => o.code === choices[n]) ?? c
    return [n, { code: chosen.code, title: chosen.title, label: c.label, changed_by_person: chosen.code !== c.code || c.label === "human" }]
  })), [result, choices])

  function approved() {
    return {
      approved_at: approvedAt, report: result.report, codes: finalCodes,
      actions: result.action_plan.actions
        .map((a, i) => ({ ...a, action: edits[i] ?? pick(a.action, lang), kept: kept[i] }))
        .filter((a) => a.kept),
      source: { replay: !!result.replay, models: result.amd.calls.map((c) => c.model) },
    }
  }

  function download() {
    const blob = new Blob([JSON.stringify(approved(), null, 2)], { type: "application/json" })
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = `incident-${new Date().toISOString().slice(0, 10)}.json`
    link.click()
    URL.revokeObjectURL(link.href)
  }

  return (
    <div className="grid gap-6">
      {result.replay && (
        <Alert><RotateCcw /><AlertDescription>{fill(t.replayBanner, { date: result.recorded_at?.slice(0, 16).replace("T", " ") ?? "" })}</AlertDescription></Alert>
      )}
      {result.second_opinion && !result.second_opinion.measured && (
        <Alert><AlertTriangle /><AlertDescription>
          {result.second_opinion.model
            ? fill(t.fallbackBanner, { measured: result.second_opinion.measured_model, model: result.second_opinion.model })
            : t.noSecondOpinion}
        </AlertDescription></Alert>
      )}

      <section className="grid gap-3">
        <h2 className="text-lg font-semibold">{t.codesTitle}</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {CODE_ORDER.map((name) => (
            <CodeCard key={name} name={name} result={result} choice={choices[name]}
              onChoose={(code) => setChoices((c) => ({ ...c, [name]: code }))} />
          ))}
        </div>
      </section>

      <Card>
        <CardHeader>
          <CardTitle>{t.planTitle}</CardTitle>
          <CardDescription>{t.planHelp}</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          {result.action_plan.missing_info.length > 0 && (
            <div className="rounded-lg bg-muted p-3 text-sm">
              <p className="mb-1 font-medium">{t.missingTitle}</p>
              <ul className="grid gap-1">{result.action_plan.missing_info.map((q, i) => <li key={i}>• {pick(q, lang)}</li>)}</ul>
            </div>
          )}
          {result.action_plan.actions.map((a, i) => (
            <ActionRow key={i} action={a} kept={kept[i]} text={edits[i] ?? pick(a.action, lang)}
              onToggle={() => setKept((k) => k.map((v, j) => (j === i ? !v : v)))}
              onEdit={(v) => setEdits((e) => ({ ...e, [i]: v }))} />
          ))}
          {result.action_plan.rejected.length > 0 && (
            <details className="text-sm text-muted-foreground">
              <summary className="cursor-pointer">{fill(t.filtered, { n: result.action_plan.rejected.length })}</summary>
              <ul className="mt-2 grid gap-1">
                {result.action_plan.rejected.map((a, i) => <li key={i}>• {pick(a.action, lang)} — {a.problems?.join("; ")}</li>)}
              </ul>
            </details>
          )}
          <details className="text-sm text-muted-foreground">
            <summary className="cursor-pointer">{fill(t.standardsUsed, { date: result.action_plan.ecfr_date })}</summary>
            <ul className="mt-2 grid gap-2">
              {result.action_plan.standards.map((s) => <li key={s.section}><b>{s.section}</b> {s.topic}</li>)}
            </ul>
          </details>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 pt-6 print:hidden">
          {approvedAt ? (
            <>
              <Badge className={LABEL_STYLE.trusted}><CheckCircle2 /> {t.approved}</Badge>
              <Button variant="outline" onClick={download}><Download /> {t.downloadJson}</Button>
              <Button variant="outline" onClick={() => window.print()}><Printer /> {t.print}</Button>
            </>
          ) : (
            <>
              <Button disabled={needsChoice.length > 0} onClick={() => setApprovedAt(new Date().toISOString())}>
                <CheckCircle2 /> {t.approve}
              </Button>
              {needsChoice.length > 0 && <span className="text-sm text-muted-foreground">{t.approveBlocked}</span>}
            </>
          )}
        </CardContent>
      </Card>

      <section className="grid gap-3">
        <div>
          <h2 className="text-lg font-semibold">{t.casesTitle}</h2>
          <p className="text-sm text-muted-foreground">{t.casesHelp}</p>
        </div>
        {result.similar_cases.map((c) => (
          <Card key={c.upa} className="py-4">
            <CardContent className="grid gap-2 text-sm">
              <p>{c.narrative}</p>
              <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                <span>{c.month}</span>{c.sector && <span>NAICS {c.sector}</span>}
                <Badge variant="secondary">{c.event}</Badge><Badge variant="secondary">{c.source}</Badge>
                <Badge variant="outline">{c.nature}</Badge><Badge variant="outline">{c.part}</Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  )
}

function CodeCard({ name, result, choice, onChoose }: {
  name: CodeName; result: Analysis; choice?: string; onChoose: (code: string) => void
}) {
  const { t } = useLang()
  const c = result.codes[name]
  const options = [c as CodeOption, ...c.alternatives]
  const shown = options.find((o) => o.code === choice) ?? c
  const llm = c.llm_pick
  // Older recordings predate the second_opinion field; they all came from Gemma.
  const llmModel = result.second_opinion?.model ?? "Gemma"
  return (
    <Card className={cn("gap-3 py-4", c.label === "human" && !choice && "ring-2 ring-rose-300 dark:ring-rose-800")}>
      <CardHeader className="px-4">
        <div className="flex items-center justify-between gap-2">
          <CardDescription>{t[name]}</CardDescription>
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge className={cn("cursor-help", LABEL_STYLE[c.label])}>{t[c.label]}</Badge>
            </TooltipTrigger>
            <TooltipContent className="max-w-64">{t.labelHelp[c.label]}</TooltipContent>
          </Tooltip>
        </div>
        <CardTitle className="text-base leading-snug">
          <span className="font-mono text-muted-foreground">{shown.code}</span> {shown.title.split(";")[0]}
        </CardTitle>
      </CardHeader>
      <CardContent className="grid gap-2 px-4 text-xs text-muted-foreground">
        <span>{Math.round(c.confidence * 100)}% {t.confidence}
          {llm && (name === "event" || name === "source") && <> · {llm === c.code ? fill(t.gemmaAgrees, { model: llmModel }) : fill(t.gemmaPicks, { model: llmModel, code: llm })}</>}
        </span>
        {(c.label !== "trusted") && (
          <Select value={choice ?? (c.label === "human" ? undefined : c.code)} onValueChange={onChoose}>
            <SelectTrigger className="h-8 w-full text-xs"><SelectValue placeholder={t.chooseCode} /></SelectTrigger>
            <SelectContent>
              {options.map((o) => (
                <SelectItem key={o.code} value={o.code} className="text-xs">
                  {o.code} · {o.title.split(";")[0]} ({Math.round(o.confidence * 100)}%)
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </CardContent>
    </Card>
  )
}

function ActionRow({ action, kept, text, onToggle, onEdit }: {
  action: Action; kept: boolean; text: string; onToggle: () => void; onEdit: (v: string) => void
}) {
  const { t, lang } = useLang()
  return (
    <div className={cn("grid gap-2 rounded-lg border p-3", !kept && "opacity-50")}>
      <div className="flex flex-wrap items-center gap-2">
        <input type="checkbox" checked={kept} onChange={onToggle} className="size-4 accent-current" aria-label="keep" />
        <Badge variant="secondary">{t.types[action.type] ?? action.type}</Badge>
        <Badge variant="outline" className="font-mono">29 CFR {action.standard}</Badge>
      </div>
      <Textarea value={text} onChange={(e) => onEdit(e.target.value)} className="min-h-14 text-sm" disabled={!kept} />
      <p className="text-xs text-muted-foreground">{pick(action.why, lang)}</p>
    </div>
  )
}

function AmdPanel({ result }: { result: Analysis }) {
  const { t } = useLang()
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Cpu className="size-4" /> {t.amdTitle}</CardTitle>
        <CardDescription>{t.amdHelp}</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-3 text-sm">
        <code className="rounded bg-muted px-2 py-1 text-xs">{result.amd.endpoint}</code>
        {result.amd.calls.map((c) => (
          <div key={c.purpose} className="grid gap-0.5">
            <span className="font-medium">{c.model}</span>
            <span className="text-xs text-muted-foreground">{c.purpose} · {c.seconds} s{c.error ? ` · ${c.error}` : ""}</span>
            {c.via === "evolus" && (
              <span className="mt-1 rounded-md bg-emerald-50 p-2 text-xs text-emerald-900 dark:bg-emerald-950 dark:text-emerald-200">{t.viaEvolus}</span>
            )}
            {c.via === "token_factory" && c.evolus_error && (
              <span className="mt-1 rounded-md bg-amber-50 p-2 text-xs text-amber-900 dark:bg-amber-950 dark:text-amber-200" title={c.evolus_error}>
                {t.evolusFallback}
              </span>
            )}
          </div>
        ))}
        <span className="text-xs text-muted-foreground">{t.total}: {result.seconds_total} s</span>
      </CardContent>
    </Card>
  )
}
