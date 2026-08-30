import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'

/**
 * Tema — açık (VARSAYILAN) ve koyu.
 *
 * VARSAYILAN AÇIK OLMALIDIR. Sistem GÜNEŞ ALTINDA kullanılacağını iddia
 * ediyor (ana talimat Bölüm 9) ve doğrudan güneşte açık zemin koyu
 * zeminden okunaklıdır. Kullanıcıyı önce okuyamayacağı bir ekranla
 * karşılayıp temayı bulmasını beklemek, iddianın tersini yapmaktı.
 * Koyu tema kapalı alan ve gece için bir adım uzakta duruyor.
 *
 * Tercih `localStorage`'da tutulur; `index.html` içindeki küçük betik onu
 * React yüklenmeden uygular, böylece sayfa açılırken yanıp sönme olmaz.
 * Depolama kapalıysa (gizli sekme, katı tarayıcı ayarı) sessizce açık
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
  return 'light'
}

export function TemaSaglayici({ children }: { children: ReactNode }) {
  const [tema, setTema] = useState<Tema>(kayitliTema)

  useEffect(() => {
    const kok = document.documentElement
    // Öznitelik her iki yönde de AÇIKÇA yazılır. Varsayılan artık açık
    // olduğu için "özniteliği kaldır = koyu" varsayımı tersine dönerdi;
    // iki değeri de yazmak bu tuzağı büsbütün kaldırır.
    kok.setAttribute('data-theme', tema)
    // Tarayıcı çubuğu sayfa zeminiyle aynı renge gelsin — mobilde koyu
    // temada beyaz bir şerit kalıyordu.
    document.querySelector('meta[name="theme-color"]')
      ?.setAttribute('content', tema === 'dark' ? '#000000' : '#f5f6f3')
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
