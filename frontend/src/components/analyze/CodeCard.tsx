import { CheckCircle2, CircleHelp, UserRound } from "lucide-react"
import { motion } from "motion/react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import type { Analysis, CodeName, CodeOption, Label } from "@/lib/api"
import { fill, useLang } from "@/lib/i18n"
import { cn } from "@/lib/utils"
import { LABEL_FILL, LABEL_STYLE } from "./labels"

const LABEL_ICON: Record<Label, typeof CheckCircle2> = { trusted: CheckCircle2, approximate: CircleHelp, human: UserRound }

export function CodeCard({ name, result, choice, onChoose }: {
  name: CodeName; result: Analysis; choice?: string; onChoose: (code: string) => void
}) {
  const { t } = useLang()
  const c = result.codes[name]
  const options = [c as CodeOption, ...c.alternatives]
  const shown = options.find((o) => o.code === choice) ?? c
  const llm = c.llm_pick
  // Older recordings predate the second_opinion field; they all came from Gemma.
  const llmModel = result.second_opinion?.model ?? "Gemma"
  const waiting = c.label === "human" && !choice
  const Icon = LABEL_ICON[c.label]
  const confidence = Math.round(c.confidence * 100)
  return (
    <Card className="relative gap-3 py-4">
      {waiting && (
        // A soft pulse on the cards that need the officer's decision.
        <motion.span aria-hidden className="pointer-events-none absolute inset-0 rounded-xl ring-2 ring-rose-400 dark:ring-rose-500"
          animate={{ opacity: [0.25, 0.95, 0.25] }} transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }} />
      )}
      <CardHeader className="px-4">
        <div className="flex items-center justify-between gap-2">
          <CardDescription className="font-medium uppercase tracking-wide text-[11px]">{t[name]}</CardDescription>
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge className={cn("cursor-help gap-1", LABEL_STYLE[c.label])}><Icon /> {t[c.label]}</Badge>
            </TooltipTrigger>
            <TooltipContent className="max-w-64">{t.labelHelp[c.label]}</TooltipContent>
          </Tooltip>
        </div>
        <CardTitle className="text-base leading-snug">
          <span className="font-mono text-muted-foreground">{shown.code}</span> {shown.title.split(";")[0]}
        </CardTitle>
      </CardHeader>
      <CardContent className="grid gap-2.5 px-4 text-xs text-muted-foreground">
        <div className="grid gap-1">
          <div className="flex items-center justify-between">
            <span>{t.confidence}</span><span className="tabular-nums font-medium text-foreground">{confidence}%</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-muted">
            <div className={cn("h-full rounded-full", LABEL_FILL[c.label])} style={{ width: `${confidence}%` }} />
          </div>
        </div>
        {llm && (name === "event" || name === "source") && (
          <span>{llm === c.code ? fill(t.gemmaAgrees, { model: llmModel }) : fill(t.gemmaPicks, { model: llmModel, code: llm })}</span>
        )}
        {c.label !== "trusted" && (
          <Select value={choice ?? (c.label === "human" ? undefined : c.code)} onValueChange={onChoose}>
            <SelectTrigger className={cn("h-8 w-full text-xs", waiting && "border-rose-400")}><SelectValue placeholder={t.chooseCode} /></SelectTrigger>
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
