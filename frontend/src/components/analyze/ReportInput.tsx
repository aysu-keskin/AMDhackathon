import { FileText, Flame, Forklift, Hammer, Loader2, Package, Play, RotateCcw, type LucideIcon } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import type { Sample } from "@/lib/api"
import { fill, useLang } from "@/lib/i18n"
import { cn } from "@/lib/utils"

const SAMPLE_ICON: Record<string, LucideIcon> = { press: Hammer, forklift: Forklift, conveyor: Package, fryer: Flame }

export function ReportInput({ text, onText, samples, busy, online, onAnalyze, onRunSample, onReplay }: {
  text: string
  onText: (text: string) => void
  samples: Sample[]
  busy: boolean
  online: boolean | null
  onAnalyze: () => void
  onRunSample: (sample: Sample) => void
  onReplay: (sample: Sample) => void
}) {
  const { t, lang } = useLang()
  const tooShort = text.trim().length < 20
  return (
    <div className="grid min-w-0 gap-5">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg"><FileText className="size-5 text-muted-foreground" /> {t.reportLabel}</CardTitle>
          <CardDescription>{t.reportHelp}</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-3">
          <Textarea value={text} onChange={(e) => onText(e.target.value)} placeholder={t.reportPlaceholder}
            className="min-h-32 resize-y text-[15px] leading-relaxed" maxLength={4000} />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className={cn("text-xs tabular-nums text-muted-foreground", tooShort && text.length > 0 && "text-amber-700 dark:text-amber-400")}>
              {fill(t.chars, { n: text.length })}{tooShort && text.length > 0 ? ` · ${t.minChars}` : ""}
            </span>
            <Button size="lg" onClick={onAnalyze} disabled={busy || online === false || tooShort}
              className="h-10 gap-2 bg-brand px-5 text-brand-foreground shadow-sm hover:bg-brand/90">
              {busy ? <Loader2 className="animate-spin" /> : <Play />} {t.analyze}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-2.5">
        <p className="text-sm text-muted-foreground"><span className="font-medium text-foreground">{t.samples}</span> · {t.samplesHint}</p>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {samples.map((s) => {
            const Icon = SAMPLE_ICON[s.id] ?? FileText
            return (
              <div key={s.id} className="grid content-between gap-3 rounded-xl border bg-card p-3 transition-colors hover:border-ring/40">
                <button className="grid gap-2 text-left" onClick={() => onText(s.text)}>
                  <span className="flex items-center gap-2">
                    <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-brand/15 text-amber-700 dark:text-brand"><Icon className="size-4" /></span>
                    <span className="text-sm font-medium leading-tight">{s.title[lang]}</span>
                  </span>
                  <span className="line-clamp-2 text-xs text-muted-foreground">{s.text}</span>
                </button>
                <div className="flex gap-1.5">
                  <Button size="sm" className="flex-1" disabled={busy || online === false} onClick={() => onRunSample(s)}>
                    <Play /> {t.runLive}
                  </Button>
                  {s.has_replay && (
                    <Button size="sm" variant="outline" disabled={busy} onClick={() => onReplay(s)}>
                      <RotateCcw /> {t.replay}
                    </Button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
