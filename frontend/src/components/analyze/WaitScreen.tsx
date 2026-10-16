import { useEffect, useState } from "react"
import { BookOpen, Bot, Check, Cpu, Layers, Loader2, Sparkles } from "lucide-react"
import { motion } from "motion/react"
import { Card, CardContent } from "@/components/ui/card"
import { fill, useLang } from "@/lib/i18n"
import { cn } from "@/lib/utils"

// The server answers once, so only the local steps can be marked done; the two AMD calls run in parallel.
// The bar is a time-based estimate (labelled as such), never above 95% until the answer arrives.
export function WaitScreen({ since, evolus }: { since: number; evolus: boolean }) {
  const { t } = useLang()
  const [now, setNow] = useState(Date.now())
  useEffect(() => { const id = setInterval(() => setNow(Date.now()), 500); return () => clearInterval(id) }, [])
  const seconds = Math.round((now - since) / 1000)
  const expected = evolus ? 150 : 90
  const progress = Math.min(95, (seconds / expected) * 100)
  const steps = [
    { label: t.stepCoder, done: seconds >= 1, icon: Layers },
    { label: t.stepCases, done: seconds >= 1, icon: BookOpen },
    { label: t.stepGemma, done: false, icon: Cpu },
    { label: evolus ? t.stepDraftEvolus : t.stepDraft, done: false, icon: evolus ? Bot : Sparkles },
  ]
  return (
    <div className="grid gap-4">
      <Card>
        <CardContent className="grid gap-5 pt-1">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span className="flex items-center gap-2 font-medium"><Loader2 className="size-4 animate-spin" /> {t.analyzingTitle}</span>
            <span className="text-xs tabular-nums text-muted-foreground">{fill(evolus ? t.elapsedEvolus : t.elapsed, { s: seconds })}</span>
          </div>
          <div className="grid gap-1">
            <div className="h-1.5 overflow-hidden rounded-full bg-muted">
              <motion.div className="h-full rounded-full bg-brand" animate={{ width: `${progress}%` }} transition={{ ease: "linear", duration: 0.5 }} />
            </div>
            <span className="text-[11px] text-muted-foreground">{t.estimated}</span>
          </div>
          <ol className="grid gap-3">
            {steps.map((s, i) => (
              <li key={s.label} className="flex items-center gap-3">
                <span className="relative grid size-8 shrink-0 place-items-center rounded-full border bg-background">
                  {s.done ? <Check className="size-4 text-emerald-600" /> : <s.icon className="size-4" />}
                  {!s.done && (
                    <motion.span className="absolute -inset-px rounded-full ring-2 ring-brand"
                      animate={{ opacity: [0.15, 0.9, 0.15], scale: [1, 1.12, 1] }}
                      transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut", delay: i * 0.25 }} />
                  )}
                </span>
                <span className="grid">
                  <span className={cn("text-sm", s.done ? "text-muted-foreground" : "font-medium")}>{s.label}</span>
                  {!s.done && <span className="text-xs text-muted-foreground">{t.stepRunning}</span>}
                </span>
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>
      {/* Where the result will appear. */}
      <div className="grid gap-3 sm:grid-cols-2" aria-hidden>
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="grid gap-2 rounded-xl border bg-card p-4">
            <div className="h-3 w-1/3 animate-pulse rounded bg-muted" />
            <div className="h-4 w-4/5 animate-pulse rounded bg-muted" />
            <div className="h-1.5 w-full animate-pulse rounded bg-muted" />
          </div>
        ))}
      </div>
    </div>
  )
}
