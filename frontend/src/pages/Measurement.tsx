import { useEffect, useState } from "react"
import { Check, X } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { api, type CodeName } from "@/lib/api"
import { useLang } from "@/lib/i18n"

const BRIEF: Record<CodeName, number> = { event: 0.842, source: 0.6625, nature: 0.926, part: 0.8875 }
const CODES: CodeName[] = ["event", "nature", "part", "source"]
const pct = (x: number | null | undefined, digits = 1) => (x == null ? "—" : `${(x * 100).toFixed(digits)}%`)

export function Measurement() {
  const { t } = useLang()
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [m, setM] = useState<any>(null)
  useEffect(() => { api.metrics().then(setM).catch(() => setM(false)) }, [])
  if (m === null) return <p className="text-muted-foreground">…</p>
  if (m === false) return <p className="text-destructive">{t.error}</p>

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader><CardTitle>{t.mShiftTitle}</CardTitle><CardDescription>{t.mShiftText}</CardDescription></CardHeader>
        <CardContent><ShiftChart series={m.code_shift.series} groups={m.code_shift.groups} /></CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>{t.mBaselineTitle}</CardTitle><CardDescription>{t.mOldText}</CardDescription></CardHeader>
        <CardContent className="grid gap-6">
          <Table>
            <TableHeader><TableRow><TableHead /><TableHead className="text-right">{t.mBrief}</TableHead>
              <TableHead className="text-right">{t.mOurs}</TableHead><TableHead className="text-right">{t.mRows}</TableHead></TableRow></TableHeader>
            <TableBody>
              {CODES.map((c) => (
                <TableRow key={c}><TableCell>{t[c]}</TableCell><TableCell className="text-right tabular-nums">{pct(BRIEF[c])}</TableCell>
                  <TableCell className="text-right tabular-nums font-medium">{pct(m.old_reproduction[c].accuracy)}</TableCell>
                  <TableCell className="text-right tabular-nums">{m.old_reproduction[c].test_rows.toLocaleString("en-US")}</TableCell></TableRow>
              ))}
            </TableBody>
          </Table>
          <p className="text-sm text-muted-foreground">{t.mNewText}</p>
          <Table>
            <TableHeader><TableRow><TableHead /><TableHead className="text-right">{t.mAccuracy}</TableHead>
              <TableHead className="text-right">{t.mRows}</TableHead></TableRow></TableHeader>
            <TableBody>
              {CODES.map((c) => (
                <TableRow key={c}><TableCell>{t[c]}</TableCell>
                  <TableCell className="text-right tabular-nums font-medium">{pct(m.new_accuracy[c].accuracy)}</TableCell>
                  <TableCell className="text-right tabular-nums">{m.new_accuracy[c].test_rows.toLocaleString("en-US")}</TableCell></TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>{t.mLabelsTitle}</CardTitle><CardDescription>{t.mLabelsText}</CardDescription></CardHeader>
        <CardContent>
          <Table>
            <TableHeader><TableRow><TableHead />
              <TableHead className="text-right">{t.trusted}</TableHead><TableHead className="text-right">{t.mTrustedAcc}</TableHead>
              <TableHead className="text-right">{t.human}</TableHead><TableHead className="text-right">{t.mErrRatio}</TableHead></TableRow></TableHeader>
            <TableBody>
              {CODES.map((c) => {
                const row = m.confidence_test.test[c]
                const trusted = row.labels.trusted
                return (
                  <TableRow key={c}><TableCell>{t[c]}</TableCell>
                    <TableCell className="text-right tabular-nums">{pct(trusted.share, 0)}</TableCell>
                    <TableCell className="text-right tabular-nums font-medium">
                      {trusted.accuracy == null ? "—" : <>{pct(trusted.accuracy)} <span className="text-xs text-muted-foreground">({pct(trusted.accuracy_95ci[0])}–{pct(trusted.accuracy_95ci[1])})</span></>}
                    </TableCell>
                    <TableCell className="text-right tabular-nums">{pct(row.labels.human.share, 0)}</TableCell>
                    <TableCell className="text-right tabular-nums">{row.human_vs_rest_error_ratio}×</TableCell></TableRow>
                )
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>{t.mSecondTitle}</CardTitle><CardDescription>{t.mDeviation}</CardDescription></CardHeader>
        <CardContent className="grid gap-6 md:grid-cols-2">
          {(["strict", "rescored"] as const).map((kind) => {
            const e = m.second_opinion[kind].event
            const rows = [["baseline_only", t.mBaselineOnly], ["rule_a", t.mRuleA], ["rule_b", t.mRuleB]] as const
            return (
              <div key={kind} className="grid min-w-0 content-start gap-2">
                <Badge variant={kind === "strict" ? "outline" : "secondary"} className="w-fit">{kind === "strict" ? t.mStrict : t.mRescored}</Badge>
                <Table>
                  <TableHeader><TableRow><TableHead>{t.mRule}</TableHead><TableHead className="text-right">{t.mTrustedShare}</TableHead>
                    <TableHead className="text-right">{t.mTrustedAcc}</TableHead><TableHead className="text-right">{t.mPass}</TableHead></TableRow></TableHeader>
                  <TableBody>
                    {rows.map(([key, label]) => (
                      <TableRow key={key}>
                        <TableCell className="whitespace-normal">{label}</TableCell>
                        <TableCell className="text-right tabular-nums">{pct(e[key].trusted.share, 0)}</TableCell>
                        <TableCell className="text-right tabular-nums">{pct(e[key].trusted.accuracy)}</TableCell>
                        <TableCell className="text-right">{e[key].passes ? <Check className="ml-auto size-4 text-emerald-600" /> : <X className="ml-auto size-4 text-rose-600" />}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )
          })}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>{t.mLimitsTitle}</CardTitle></CardHeader>
        <CardContent><ul className="grid gap-2 text-sm">{t.mLimits.map((l) => <li key={l}>• {l}</li>)}</ul></CardContent>
      </Card>
    </div>
  )
}

const LINE_COLORS: Record<string, string> = { "62": "var(--chart-1)", "42": "var(--chart-2)", "65": "var(--chart-4)", "41": "var(--chart-5)" }

function ShiftChart({ series, groups }: { series: Record<string, number | string>[]; groups: Record<string, string> }) {
  const W = 640, H = 220, P = { l: 36, r: 12, t: 12, b: 28 }
  const keys = Object.keys(groups)
  const max = Math.max(0.3, ...series.flatMap((s) => keys.map((k) => Number(s[k]))))
  const x = (i: number) => P.l + (i * (W - P.l - P.r)) / (series.length - 1)
  const y = (v: number) => P.t + (1 - v / max) * (H - P.t - P.b)
  const switchIndex = series.findIndex((s) => s.month === "2024-01")
  return (
    <div className="grid gap-3">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Monthly share of four OSHA event groups, 2023-2024">
        {[0, 0.1, 0.2, 0.3].filter((v) => v <= max).map((v) => (
          <g key={v}>
            <line x1={P.l} x2={W - P.r} y1={y(v)} y2={y(v)} stroke="var(--border)" />
            <text x={P.l - 6} y={y(v) + 4} textAnchor="end" fontSize="10" fill="var(--muted-foreground)">{v * 100}%</text>
          </g>
        ))}
        <line x1={x(switchIndex)} x2={x(switchIndex)} y1={P.t} y2={H - P.b} stroke="var(--destructive)" strokeDasharray="4 4" />
        <text x={x(switchIndex) + 4} y={P.t + 10} fontSize="10" fill="var(--destructive)">2024-01</text>
        {series.map((s, i) => (i % 6 === 0 ? <text key={i} x={x(i)} y={H - 8} fontSize="10" textAnchor="middle" fill="var(--muted-foreground)">{String(s.month)}</text> : null))}
        {keys.map((k) => (
          <polyline key={k} fill="none" stroke={LINE_COLORS[k]} strokeWidth="2.2" strokeLinejoin="round"
            points={series.map((s, i) => `${x(i)},${y(Number(s[k]))}`).join(" ")} />
        ))}
      </svg>
      <div className="flex flex-wrap gap-4 text-xs">
        {keys.map((k) => (
          <span key={k} className="inline-flex items-center gap-1.5">
            <i className="inline-block h-0.5 w-4" style={{ background: LINE_COLORS[k] }} /> <b className="font-mono">{k}</b> {groups[k]}
          </span>
        ))}
      </div>
    </div>
  )
}
