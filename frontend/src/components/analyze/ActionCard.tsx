import { Badge } from "@/components/ui/badge"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Textarea } from "@/components/ui/textarea"
import { pick, type Action, type Analysis } from "@/lib/api"
import { useLang } from "@/lib/i18n"
import { cn } from "@/lib/utils"
import { ACTION_TYPE } from "./labels"

type Standard = Analysis["action_plan"]["standards"][number]

export function ActionCard({ action, standard, kept, text, onToggle, onEdit }: {
  action: Action; standard?: Standard; kept: boolean; text: string; onToggle: () => void; onEdit: (v: string) => void
}) {
  const { t, lang } = useLang()
  const style = ACTION_TYPE[action.type] ?? ACTION_TYPE.administrative
  const Icon = style.icon
  return (
    <div className={cn("grid gap-2.5 rounded-xl border border-l-4 bg-card p-3.5 transition-opacity", style.edge, !kept && "opacity-50")}>
      <div className="flex flex-wrap items-center gap-2">
        <input type="checkbox" checked={kept} onChange={onToggle} className="size-4 accent-current" aria-label="keep" />
        <span className={cn("inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium", style.chip)}>
          <Icon className="size-3.5" /> {t.types[action.type] ?? action.type}
        </span>
        <Popover>
          <PopoverTrigger asChild>
            <button className="rounded-md border px-2 py-0.5 font-mono text-xs transition-colors hover:bg-muted" title={t.excerpt}>
              29 CFR {action.standard}
            </button>
          </PopoverTrigger>
          <PopoverContent>
            <div className="grid gap-2">
              <div className="font-medium leading-snug">29 CFR {action.standard}{standard ? ` — ${standard.topic}` : ""}</div>
              {standard?.from_library && <Badge variant="outline" className="whitespace-normal">{t.fromLibrary}</Badge>}
              <span className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">{t.excerpt}</span>
              <p className="max-h-60 overflow-auto whitespace-pre-line text-xs leading-relaxed text-muted-foreground">
                {standard ? `${standard.excerpt}…` : t.noExcerpt}
              </p>
            </div>
          </PopoverContent>
        </Popover>
      </div>
      <Textarea value={text} onChange={(e) => onEdit(e.target.value)} className="min-h-14 text-sm" disabled={!kept} />
      <p className="text-xs text-muted-foreground">{pick(action.why, lang)}</p>
    </div>
  )
}
