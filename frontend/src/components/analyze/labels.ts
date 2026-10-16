import { ClipboardList, GraduationCap, HardHat, Wrench, type LucideIcon } from "lucide-react"
import type { CodeName, Label } from "@/lib/api"

export const CODE_ORDER: CodeName[] = ["event", "nature", "part", "source"]

export const LABEL_STYLE: Record<Label, string> = {
  trusted: "bg-emerald-100 text-emerald-900 dark:bg-emerald-500/15 dark:text-emerald-300",
  approximate: "bg-amber-100 text-amber-900 dark:bg-amber-500/15 dark:text-amber-300",
  human: "bg-rose-100 text-rose-900 dark:bg-rose-500/15 dark:text-rose-300",
}

export const LABEL_FILL: Record<Label, string> = {
  trusted: "bg-emerald-500",
  approximate: "bg-amber-500",
  human: "bg-rose-500",
}

// Hierarchy of controls: each level keeps one colour and icon across the page.
export const ACTION_TYPE: Record<string, { icon: LucideIcon; edge: string; chip: string }> = {
  engineering: { icon: Wrench, edge: "border-l-sky-500", chip: "bg-sky-100 text-sky-900 dark:bg-sky-500/15 dark:text-sky-300" },
  administrative: { icon: ClipboardList, edge: "border-l-violet-500", chip: "bg-violet-100 text-violet-900 dark:bg-violet-500/15 dark:text-violet-300" },
  training: { icon: GraduationCap, edge: "border-l-teal-500", chip: "bg-teal-100 text-teal-900 dark:bg-teal-500/15 dark:text-teal-300" },
  ppe: { icon: HardHat, edge: "border-l-amber-500", chip: "bg-amber-100 text-amber-900 dark:bg-amber-500/15 dark:text-amber-300" },
}
