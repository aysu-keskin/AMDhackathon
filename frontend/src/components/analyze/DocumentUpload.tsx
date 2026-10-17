import { useRef, useState } from "react"
import { ExternalLink, FileUp, Loader2, ScanText } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { api, type Extraction } from "@/lib/api"
import { fill, useLang } from "@/lib/i18n"

// Team-written sample forms (backend/core/sample_pdf.py), so anyone can try the extractor without a file.
const SAMPLE_PDFS = [
  { file: "incident-report-en.pdf", label: "EN" },
  { file: "incident-report-it.pdf", label: "IT" },
]
const SHOWN_FIELDS = ["event_date", "injury", "body_part", "equipment", "language"] as const

// Reports often arrive as forms: our Evolus document extractor reads the PDF and fills in the description.
export function DocumentUpload({ disabled, onText }: { disabled: boolean; onText: (text: string) => void }) {
  const { t } = useLang()
  const input = useRef<HTMLInputElement>(null)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<Extraction | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function read(file: Blob) {
    setBusy(true); setResult(null); setError(null)
    try {
      const extraction = await api.extract(file)
      onText(String(extraction.fields.narrative))
      setResult(extraction)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }

  async function readSample(file: string) {
    const response = await fetch(`/samples/${file}`)
    await read(await response.blob())
  }

  return (
    <div className="grid gap-2.5 rounded-xl border border-dashed p-3">
      <div className="flex flex-wrap items-center gap-2">
        <ScanText className="size-4 text-muted-foreground" />
        <span className="text-sm font-medium">{t.docTitle}</span>
        <span className="text-xs text-muted-foreground">{t.docHint}</span>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <input ref={input} type="file" accept="application/pdf" className="hidden"
          onChange={(e) => { const file = e.target.files?.[0]; e.target.value = ""; if (file) read(file) }} />
        <Button size="sm" variant="outline" disabled={disabled || busy} onClick={() => input.current?.click()}>
          <FileUp /> {t.docUpload}
        </Button>
        <span className="text-xs text-muted-foreground">{t.docOr}</span>
        {SAMPLE_PDFS.map((s) => (
          <span key={s.file} className="inline-flex items-center gap-1">
            <Button size="sm" variant="ghost" disabled={disabled || busy} onClick={() => readSample(s.file)}>
              {fill(t.docSample, { lang: s.label })}
            </Button>
            <a href={`/samples/${s.file}`} target="_blank" rel="noreferrer" title={t.docView}
              className="text-muted-foreground hover:text-foreground"><ExternalLink className="size-3.5" /></a>
          </span>
        ))}
      </div>
      {busy && (
        <p className="flex items-center gap-2 text-sm text-muted-foreground"><Loader2 className="size-4 animate-spin" /> {t.docReading}</p>
      )}
      {error && <p className="text-sm text-rose-700 dark:text-rose-300">{t.docError}: {error}</p>}
      {result && (
        <div className="grid gap-2 rounded-lg bg-emerald-50 p-2.5 text-xs text-emerald-900 dark:bg-emerald-500/10 dark:text-emerald-200">
          <span>{fill(t.docDone, { s: result.seconds })}</span>
          <div className="flex flex-wrap gap-1.5">
            {SHOWN_FIELDS.filter((key) => result.fields[key]).map((key) => (
              <Badge key={key} variant="outline" className="h-auto whitespace-normal border-emerald-300 text-emerald-900 dark:border-emerald-700 dark:text-emerald-200">
                {t.docFields[key]}: {String(result.fields[key])}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
