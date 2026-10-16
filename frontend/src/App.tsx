import { useState, type ReactNode } from "react"
import { Moon, ShieldCheck, Sun } from "lucide-react"
import { MotionConfig, motion } from "motion/react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { TooltipProvider } from "@/components/ui/tooltip"
import { LangProvider, useLang } from "@/lib/i18n"
import { ThemeProvider, useTheme } from "@/lib/theme"
import { cn } from "@/lib/utils"
import { Analyze } from "@/pages/Analyze"
import { Measurement } from "@/pages/Measurement"

// Each tab's content slides in when it mounts (Radix unmounts the inactive tab).
function TabPanel({ children }: { children: ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, ease: "easeOut" }}>
      {children}
    </motion.div>
  )
}

function TopBar() {
  const { t, lang, setLang } = useLang()
  const { theme, toggle } = useTheme()
  return (
    <header className="sticky top-0 z-40 border-b bg-background/75 backdrop-blur-md print:hidden">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-2.5 sm:px-6">
        <div className="flex min-w-0 items-center gap-2.5">
          <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-brand text-brand-foreground shadow-sm">
            <ShieldCheck className="size-5" />
          </span>
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold leading-tight">{t.appName}</div>
            <div className="hidden gap-1.5 text-[11px] text-muted-foreground sm:flex">
              <span>AMD Token Factory</span><span aria-hidden>·</span><span>Evolus · DarkSea28</span>
            </div>
          </div>
        </div>
        <TabsList className="order-last w-full sm:order-none sm:w-fit">
          <TabsTrigger value="analyze" className="px-3">{t.tabAnalyze}</TabsTrigger>
          <TabsTrigger value="measure" className="px-3">{t.tabMeasure}</TabsTrigger>
        </TabsList>
        <div className="ml-auto flex items-center gap-1">
          <div className="flex rounded-lg bg-muted p-[3px]" role="group" aria-label="Language">
            {(["en", "it"] as const).map((l) => (
              <button key={l} onClick={() => setLang(l)} aria-pressed={lang === l}
                className={cn("h-7 rounded-md px-2.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground",
                  lang === l && "bg-background text-foreground shadow-sm")}>
                {l.toUpperCase()}
              </button>
            ))}
          </div>
          <Button variant="ghost" size="icon" onClick={toggle} aria-label={t.themeToggle} title={t.themeToggle}>
            {theme === "dark" ? <Sun /> : <Moon />}
          </Button>
        </div>
      </div>
    </header>
  )
}

function Shell() {
  const { t } = useLang()
  const [tab, setTab] = useState("analyze")
  return (
    <Tabs value={tab} onValueChange={setTab} className="min-h-screen gap-0">
      <TopBar />
      <main className="mx-auto grid w-full max-w-6xl gap-6 px-4 py-6 sm:px-6 sm:py-8">
        <div className="grid max-w-3xl gap-1.5">
          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{t.appName}</h1>
          <p className="text-sm text-muted-foreground sm:text-base">{t.tagline}</p>
        </div>
        <TabsContent value="analyze"><TabPanel><Analyze /></TabPanel></TabsContent>
        <TabsContent value="measure"><TabPanel><Measurement /></TabPanel></TabsContent>
        <footer className="border-t pt-4 text-xs text-muted-foreground">
          DarkSea28 · AMD Developer Hackathon ACT III · Data: OSHA Severe Injury Reports (U.S. Government work) · MIT
        </footer>
      </main>
    </Tabs>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <LangProvider>
        {/* Honour the system "reduce motion" setting for every animation. */}
        <MotionConfig reducedMotion="user">
          <TooltipProvider><Shell /></TooltipProvider>
        </MotionConfig>
      </LangProvider>
    </ThemeProvider>
  )
}
