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

/**
 * Tercih anahtarı — ESKİSİNDEN FARKLI OLMAK ZORUNDA.
 *
 * ⚠️ Eski sürüm `rebuild_vision_tema` anahtarına her açılışta yürürlükteki
 * temayı YAZIYORDU; kullanıcı hiçbir şey seçmemiş olsa bile. Varsayılan o
 * dönemde koyu olduğu için, siteyi bir kez açmış HERKESİN tarayıcısında
 * `"dark"` yazılı kaldı — bir tercih olarak değil, yan etki olarak.
 *
 * O anahtarı okumaya devam etseydik, varsayılanı açık yapmak eski
 * ziyaretçiler için hiçbir şey değiştirmezdi: sistemi daha önce açmış olan
 * jüri üyesi de dâhil herkes yine koyu ekranla karşılaşırdı. Yani
 * düzeltme, tam da düzeltmesi gereken kişilerde çalışmazdı.
 *
 * Yeni anahtar YALNIZCA kullanıcı düğmeye bastığında yazılır (aşağıya
 * bakınız). Böylece içindeki değer her zaman gerçek bir tercihtir; eski
 * anahtar ise okunmaz ve temizlenir.
 */
const ANAHTAR = 'rebuild_vision_tema_secim'
const ESKI_ANAHTAR = 'rebuild_vision_tema'

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

  // Eski anahtar bir tercih taşımıyor, yalnızca eski varsayılanın izini
  // taşıyor. Bırakılırsa hiçbir işe yaramadan tarayıcıda durur.
  useEffect(() => {
    try { localStorage.removeItem(ESKI_ANAHTAR) } catch { /* yoksay */ }
  }, [])

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
  }, [tema])

  // Yazma İŞTE BURADA, açılış etkisinde değil. Depoya yalnızca kullanıcı
  // düğmeye bastığında dokunulur; böylece kayıtlı değer "varsayılan
  // buydu" değil, "kullanıcı bunu seçti" anlamına gelir. Eski sürümün
  // hatası tam olarak bu ayrımı yapmamasıydı.
  const temaDegistir = useCallback(() => {
    setTema((t) => {
      const yeni: Tema = t === 'dark' ? 'light' : 'dark'
      try { localStorage.setItem(ANAHTAR, yeni) } catch { /* yoksay */ }
      return yeni
    })
  }, [])

  return <Ctx.Provider value={{ tema, temaDegistir }}>{children}</Ctx.Provider>
}

export function useTema() {
  const d = useContext(Ctx)
  if (!d) throw new Error('TemaSaglayici dışında kullanılamaz')
  return d
}
