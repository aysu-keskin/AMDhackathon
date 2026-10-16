import { useMemo, useState, type ReactNode } from "react"
import { AlertTriangle, CheckCircle2, Download, Printer, RotateCcw } from "lucide-react"
import { motion } from "motion/react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { pick, type Analysis, type CodeName, type CodeOption } from "@/lib/api"
import { fill, useLang } from "@/lib/i18n"
import { cn } from "@/lib/utils"
import { ActionCard } from "./ActionCard"
import { AmdPanel } from "./AmdPanel"
import { CodeCard } from "./CodeCard"
import { CODE_ORDER, LABEL_FILL, LABEL_STYLE } from "./labels"
import { SimilarCases } from "./SimilarCases"

function Section({ id, n, title, help, children }: { id: string; n: number; title: string; help?: string; children: ReactNode }) {
  return (
    <section id={id} className="grid scroll-mt-24 gap-3">
      <div className="grid gap-0.5">
        <h2 className="flex items-center gap-2 text-lg font-semibold">
          <span className="grid size-6 place-items-center rounded-full bg-primary text-xs text-primary-foreground">{n}</span> {title}
        </h2>
        {help && <p className="text-sm text-muted-foreground">{help}</p>}
      </div>
      {children}
    </section>
  )
}

export function Result({ result }: { result: Analysis }) {
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
  const keptCount = kept.filter(Boolean).length
  const total = result.action_plan.actions.length
  const viaEvolus = result.amd.calls.some((c) => c.via === "evolus")
  const standards = Object.fromEntries(result.action_plan.standards.map((s) => [s.section, s]))

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
    <motion.div id="result-top" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, ease: "easeOut" }}
      className="grid scroll-mt-20 gap-6 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-start">
      <div className="grid min-w-0 gap-8">
        {(result.replay || (result.second_opinion && !result.second_opinion.measured)) && (
          <div className="grid gap-3">
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
          </div>
        )}

        <Section id="codes" n={1} title={t.codesTitle}>
          <div className="grid gap-3 sm:grid-cols-2">
            {CODE_ORDER.map((name) => (
              <CodeCard key={name} name={name} result={result} choice={choices[name]}
                onChoose={(code) => setChoices((c) => ({ ...c, [name]: code }))} />
            ))}
          </div>
        </Section>

        <Section id="plan" n={2} title={t.planTitle} help={t.planHelp}>
          {result.action_plan.missing_info.length > 0 && (
            <div className="rounded-xl border border-dashed bg-muted/50 p-3.5 text-sm">
              <p className="mb-1.5 font-medium">{t.missingTitle}</p>
              <ul className="grid gap-1 text-muted-foreground">{result.action_plan.missing_info.map((q, i) => <li key={i}>• {pick(q, lang)}</li>)}</ul>
            </div>
          )}
          <div className="grid gap-3">
            {result.action_plan.actions.map((a, i) => (
              <ActionCard key={i} action={a} standard={standards[a.standard]} kept={kept[i]} text={edits[i] ?? pick(a.action, lang)}
                onToggle={() => setKept((k) => k.map((v, j) => (j === i ? !v : v)))}
                onEdit={(v) => setEdits((e) => ({ ...e, [i]: v }))} />
            ))}
          </div>
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
              {result.action_plan.standards.map((s) => (
                <li key={s.section}>
                  <b>{s.section}</b> {s.topic}
                  {s.from_library && <Badge variant="outline" className="ml-2 align-middle">{t.fromLibrary}</Badge>}
                </li>
              ))}
            </ul>
          </details>
        </Section>

        <Section id="cases" n={3} title={t.casesTitle} help={t.casesHelp}>
          <SimilarCases cases={result.similar_cases} />
        </Section>

        {/* Stays at the bottom of the screen while the results are in view. */}
        <div className="sticky bottom-3 z-30 print:hidden">
          <div className="flex flex-wrap items-center gap-3 rounded-xl border bg-background/85 p-3 shadow-lg backdrop-blur-md">
            {approvedAt ? (
              <>
                <Badge className={LABEL_STYLE.trusted}><CheckCircle2 /> {t.approved}</Badge>
                <div className="ml-auto flex flex-wrap gap-2">
                  <Button variant="outline" onClick={download}><Download /> {t.downloadJson}</Button>
                  <Button variant="outline" onClick={() => window.print()}><Printer /> {t.print}</Button>
                </div>
              </>
            ) : (
              <>
                <span className={cn("text-sm", needsChoice.length ? "text-rose-700 dark:text-rose-300" : "text-muted-foreground")}>
                  {needsChoice.length ? fill(t.chooseFirst, { n: needsChoice.length }) : fill(t.keptOf, { kept: keptCount, total })}
                </span>
                <Button className="ml-auto bg-brand text-brand-foreground hover:bg-brand/90" disabled={needsChoice.length > 0}
                  onClick={() => setApprovedAt(new Date().toISOString())}>
                  <CheckCircle2 /> {t.approve}
                </Button>
              </>
            )}
          </div>
        </div>
      </div>

      <aside className="order-first grid gap-4 lg:sticky lg:top-20 lg:order-none print:hidden">
        <Card size="sm">
          <CardHeader><CardTitle>{t.summaryTitle}</CardTitle></CardHeader>
          <CardContent className="grid gap-3">
            <ul className="grid gap-2.5">
              {CODE_ORDER.map((n) => {
                const code = finalCodes[n]
                const pending = result.codes[n].label === "human" && !choices[n]
                return (
                  <li key={n} className="flex items-start gap-2.5">
                    <span className={cn("mt-1.5 size-2 shrink-0 rounded-full", pending ? "animate-pulse bg-rose-500" : LABEL_FILL[result.codes[n].label])} />
                    <a href="#codes" className="min-w-0 hover:underline">
                      <span className="block text-[11px] uppercase tracking-wide text-muted-foreground">{t[n]}</span>
                      <span className="block truncate"><b className="font-mono">{code.code}</b> {code.title.split(";")[0]}</span>
                    </a>
                  </li>
                )
              })}
            </ul>
            <div className="grid gap-1 border-t pt-3 text-xs text-muted-foreground">
              <span>{fill(t.keptOf, { kept: keptCount, total })}</span>
              <span>{t.draftBy}: <span className="font-medium text-foreground">{viaEvolus ? t.draftEvolus : t.draftDirect}</span></span>
            </div>
            <nav className="flex flex-wrap gap-1.5 border-t pt-3">
              {([["codes", t.navCodes], ["plan", t.navPlan], ["cases", t.navCases]] as const).map(([id, label], i) => (
                <a key={id} href={`#${id}`} className="rounded-md border px-2 py-1 text-xs transition-colors hover:bg-muted">{i + 1}. {label}</a>
              ))}
            </nav>
          </CardContent>
        </Card>
        <AmdPanel result={result} />
      </aside>
    </motion.div>
  )
}
