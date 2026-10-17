import { useEffect, useState } from "react"
import { AlertTriangle, Loader2 } from "lucide-react"
import { AnimatePresence, motion } from "motion/react"
import { AmdIntro } from "@/components/analyze/AmdPanel"
import { ReportInput } from "@/components/analyze/ReportInput"
import { Result } from "@/components/analyze/Result"
import { WaitScreen } from "@/components/analyze/WaitScreen"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { api, apiHealth, type Analysis, type Sample } from "@/lib/api"
import { useLang } from "@/lib/i18n"

export function Analyze() {
  const { t } = useLang()
  const [text, setText] = useState("")
  const [samples, setSamples] = useState<Sample[]>([])
  const [result, setResult] = useState<Analysis | null>(null)
  const [busySince, setBusySince] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [online, setOnline] = useState<boolean | null>(null)
  const [evolus, setEvolus] = useState(false)
  const [extractor, setExtractor] = useState(false)

  useEffect(() => {
    api.samples().then(setSamples).catch(() => setSamples([]))
    apiHealth().then((h) => { setOnline(h.online); setEvolus(h.evolus); setExtractor(h.extractor) })
  }, [])

  // Bring the progress card, then the result, into view (the input card can push them below the fold).
  useEffect(() => {
    if (busySince) document.getElementById("wait")?.scrollIntoView({ behavior: "smooth", block: "center" })
  }, [busySince])
  useEffect(() => {
    if (result) document.getElementById("result-top")?.scrollIntoView({ behavior: "smooth", block: "start" })
  }, [result])

  async function run(fn: () => Promise<Analysis>) {
    setError(null); setResult(null); setBusySince(Date.now())
    try { setResult(await fn()) } catch (e) { setError(String(e)) } finally { setBusySince(null) }
  }

  return (
    <div className="grid gap-6">
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-start">
        <ReportInput text={text} onText={setText} samples={samples} busy={busySince !== null} online={online} extractor={extractor}
          onAnalyze={() => run(() => api.analyze(text))}
          onRunSample={(s) => { setText(s.text); run(() => api.analyze(s.text)) }}
          onReplay={(s) => { setText(s.text); run(() => api.replay(s.id)) }} />
        <AmdIntro evolus={evolus} />
      </div>

      {online === null && (
        <Alert><Loader2 className="animate-spin" /><AlertDescription>{t.waking}</AlertDescription></Alert>
      )}
      {online === false && (
        <Alert><AlertTriangle /><AlertDescription>{t.offlineBanner}</AlertDescription></Alert>
      )}
      <AnimatePresence>
        {busySince && (
          <motion.div key="wait" id="wait" className="scroll-mt-24" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.25 }}>
            <WaitScreen since={busySince} evolus={evolus} />
          </motion.div>
        )}
      </AnimatePresence>
      {error && (
        <Alert variant="destructive"><AlertTriangle /><AlertDescription>{t.error}: {error}</AlertDescription></Alert>
      )}
      {result && <Result key={result.recorded_at ?? result.seconds_total} result={result} />}
    </div>
  )
}
