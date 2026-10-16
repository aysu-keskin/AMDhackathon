import { Bot, Cpu, Timer } from "lucide-react"
import { motion } from "motion/react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { Analysis } from "@/lib/api"
import { useLang } from "@/lib/i18n"
import { cn } from "@/lib/utils"

export function AmdIntro({ evolus }: { evolus: boolean }) {
  const { t } = useLang()
  return (
    <Card>
      <CardHeader><CardTitle className="flex items-center gap-2"><Cpu className="size-4" /> {t.amdTitle}</CardTitle></CardHeader>
      <CardContent className="grid gap-3 text-sm text-muted-foreground">
        <p>{t.amdHelp}</p>
        <ul className="grid gap-2">
          <li className="flex gap-2"><Cpu className="mt-0.5 size-4 shrink-0" /> {t.stepGemma}</li>
          <li className="flex gap-2"><Bot className="mt-0.5 size-4 shrink-0" /> {evolus ? t.stepDraftEvolus : t.stepDraft}</li>
        </ul>
        {evolus && <Badge className="bg-emerald-600 text-white"><Bot /> Evolus · DarkSea28</Badge>}
      </CardContent>
    </Card>
  )
}

// Both calls start together; each bar is that call's duration on the same time scale.
export function AmdPanel({ result }: { result: Analysis }) {
  const { t } = useLang()
  const calls = result.amd.calls
  const scale = Math.max(result.seconds_total, ...calls.map((c) => c.seconds), 1)
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Cpu className="size-4" /> {t.amdTitle}</CardTitle>
        <CardDescription>{t.amdHelp}</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-4 text-sm">
        <code className="w-fit rounded-md bg-muted px-2 py-1 text-xs">{result.amd.endpoint}</code>
        {calls.map((c, i) => (
          <div key={c.purpose} className="grid gap-1.5">
            <div className="flex items-baseline justify-between gap-2">
              <span className="font-medium leading-tight">{c.model}</span>
              <span className="shrink-0 text-xs tabular-nums text-muted-foreground">{c.seconds} s</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-muted">
              <motion.div className={cn("h-full rounded-full", c.via === "evolus" ? "bg-emerald-500" : "bg-primary/70")}
                initial={{ width: 0 }} animate={{ width: `${(c.seconds / scale) * 100}%` }}
                transition={{ duration: 0.9, ease: "easeOut", delay: i * 0.15 }} />
            </div>
            <span className="text-xs text-muted-foreground">{c.purpose}{c.error ? ` · ${c.error}` : ""}</span>
            {c.via === "evolus" && (
              <div className="grid gap-1.5 rounded-lg bg-emerald-50 p-2.5 text-xs text-emerald-900 dark:bg-emerald-500/10 dark:text-emerald-200">
                <Badge className="bg-emerald-600 text-white"><Bot /> Evolus · DarkSea28</Badge>
                <span>{t.viaEvolus}</span>
              </div>
            )}
            {c.via === "token_factory" && c.evolus_error && (
              <span className="rounded-lg bg-amber-50 p-2.5 text-xs text-amber-900 dark:bg-amber-500/10 dark:text-amber-200" title={c.evolus_error}>
                {t.evolusFallback}
              </span>
            )}
          </div>
        ))}
        <p className="text-[11px] text-muted-foreground">{t.parallel}</p>
        <div className="flex items-center gap-1.5 border-t pt-3 text-xs text-muted-foreground">
          <Timer className="size-3.5" /> {t.total}: <span className="tabular-nums font-medium text-foreground">{result.seconds_total} s</span>
        </div>
      </CardContent>
    </Card>
  )
}
