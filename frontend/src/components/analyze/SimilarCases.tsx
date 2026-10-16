import { useState } from "react"
import { ChevronDown } from "lucide-react"
import { AnimatePresence, motion } from "motion/react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import type { SimilarCase } from "@/lib/api"
import { fill, useLang } from "@/lib/i18n"
import { cn } from "@/lib/utils"

const FIRST = 2

export function SimilarCases({ cases }: { cases: SimilarCase[] }) {
  const { t } = useLang()
  const [open, setOpen] = useState(false)
  const shown = open ? cases : cases.slice(0, FIRST)
  return (
    <div className="grid gap-3">
      <AnimatePresence initial={false}>
        {shown.map((c) => (
          <motion.article key={c.upa} layout initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="grid gap-2.5 rounded-xl border bg-card p-4">
            <p className="text-sm leading-relaxed">{c.narrative}</p>
            <div className="flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
              <span className="tabular-nums">{c.month}</span>
              {c.sector && <><span aria-hidden>·</span><span>NAICS {c.sector}</span></>}
              <Badge variant="secondary" className="ml-1">{c.event}</Badge>
              <Badge variant="outline">{c.source}</Badge>
            </div>
            <p className="text-xs text-muted-foreground">{t.nature}: {c.nature} · {t.part}: {c.part}</p>
          </motion.article>
        ))}
      </AnimatePresence>
      {cases.length > FIRST && (
        <Button variant="ghost" size="sm" className="w-fit" onClick={() => setOpen((v) => !v)}>
          <ChevronDown className={cn("transition-transform", open && "rotate-180")} />
          {open ? t.showLess : fill(t.showMore, { n: cases.length - FIRST })}
        </Button>
      )}
    </div>
  )
}
