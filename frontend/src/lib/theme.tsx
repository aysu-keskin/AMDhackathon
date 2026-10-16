import { createContext, useContext, useEffect, useState, type ReactNode } from "react"

type Theme = "light" | "dark"

// index.html sets the class before React loads (no flash); this keeps it in sync afterwards.
function initialTheme(): Theme {
  try {
    const saved = localStorage.getItem("theme")
    if (saved === "light" || saved === "dark") return saved
  } catch { /* private mode */ }
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light"
}

const ThemeContext = createContext<{ theme: Theme; toggle: () => void }>({ theme: "light", toggle: () => {} })

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(initialTheme)
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark")
  }, [theme])
  const toggle = () => setTheme((current) => {
    const next = current === "dark" ? "light" : "dark"
    try { localStorage.setItem("theme", next) } catch { /* private mode */ }
    return next
  })
  return <ThemeContext.Provider value={{ theme, toggle }}>{children}</ThemeContext.Provider>
}

export const useTheme = () => useContext(ThemeContext)
