import { ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { TooltipProvider } from "@/components/ui/tooltip"
import { LangProvider, useLang } from "@/lib/i18n"
import { Analyze } from "@/pages/Analyze"
import { Measurement } from "@/pages/Measurement"

function Shell() {
  const { t, lang, setLang } = useLang()
  return (
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-6 sm:px-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="grid max-w-2xl gap-1">
          <h1 className="flex items-center gap-2 text-2xl font-semibold"><ShieldCheck className="size-6" /> {t.appName}</h1>
          <p className="text-sm text-muted-foreground">{t.tagline}</p>
        </div>
        <div className="flex gap-1 print:hidden" role="group" aria-label="Language">
          {(["en", "it"] as const).map((l) => (
            <Button key={l} size="sm" variant={lang === l ? "default" : "outline"} onClick={() => setLang(l)}>{l.toUpperCase()}</Button>
          ))}
        </div>
      </header>
      <Tabs defaultValue="analyze" className="gap-6">
        <TabsList className="print:hidden">
          <TabsTrigger value="analyze">{t.tabAnalyze}</TabsTrigger>
          <TabsTrigger value="measure">{t.tabMeasure}</TabsTrigger>
        </TabsList>
        <TabsContent value="analyze"><Analyze /></TabsContent>
        <TabsContent value="measure"><Measurement /></TabsContent>
      </Tabs>
      <footer className="text-xs text-muted-foreground">
        DarkSea28 · AMD Developer Hackathon ACT III · Data: OSHA Severe Injury Reports (U.S. Government work) · MIT
      </footer>
    </div>
  )
}

export default function App() {
  return (
    <LangProvider>
      <TooltipProvider><Shell /></TooltipProvider>
    </LangProvider>
  )
}
