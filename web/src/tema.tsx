import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'

/**
 * Tema — koyu (varsayılan) ve açık.
 *
 * Açık tema süs değil: sistem GÜNEŞ ALTINDA kullanılacağını iddia ediyor
 * (ana talimat Bölüm 9) ve doğrudan güneşte açık zemin koyu zeminden
 * okunaklıdır. Kullanıcı ortama göre seçer.
 *
 * Tercih `localStorage`'da tutulur; `index.html` içindeki küçük betik onu
 * React yüklenmeden uygular, böylece sayfa açılırken yanıp sönme olmaz.
 * Depolama kapalıysa (gizli sekme, katı tarayıcı ayarı) sessizce koyu
 * temada kalır — okuma ve yazma try/catch içindedir.
 */

const ANAHTAR = 'rebuild_vision_tema'

export type Tema = 'dark' | 'light'

interface Baglam {
  tema: Tema
  temaDegistir: () => void
}

const Ctx = createContext<Baglam | null>(null)

function kayitliTema(): Tema {
  try {
    const t = localStorage.getItem(ANAHTAR)
    if (t === 'light' || t === 'dark') return t
  } catch { /* depolama yok */ }
  return 'dark'
}

export function TemaSaglayici({ children }: { children: ReactNode }) {
  const [tema, setTema] = useState<Tema>(kayitliTema)

  useEffect(() => {
    const kok = document.documentElement
    if (tema === 'light') kok.setAttribute('data-theme', 'light')
    else kok.removeAttribute('data-theme')
    try { localStorage.setItem(ANAHTAR, tema) } catch { /* yoksay */ }
  }, [tema])

  const temaDegistir = useCallback(
    () => setTema((t) => (t === 'dark' ? 'light' : 'dark')),
    [],
  )

  return <Ctx.Provider value={{ tema, temaDegistir }}>{children}</Ctx.Provider>
}

export function useTema() {
  const d = useContext(Ctx)
  if (!d) throw new Error('TemaSaglayici dışında kullanılamaz')
  return d
}
