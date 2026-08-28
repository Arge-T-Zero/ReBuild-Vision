import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { api, jetonAl, jetonSil, jetonYaz } from './api'
import type { Kullanici, SinifTanimi, SiniflarYaniti, SistemDurumu } from './types'

interface Baglam {
  kullanici: Kullanici | null
  yukleniyor: boolean
  durum: SistemDurumu | null
  siniflar: Map<string, SinifTanimi>
  siniflarHam: SiniflarYaniti | null
  girisYap: (eposta: string, parola: string) => Promise<void>
  cikisYap: () => void
}

const Ctx = createContext<Baglam | null>(null)

export function DurumSaglayici({ children }: { children: ReactNode }) {
  const [kullanici, setKullanici] = useState<Kullanici | null>(null)
  const [yukleniyor, setYukleniyor] = useState(true)
  const [durum, setDurum] = useState<SistemDurumu | null>(null)
  const [siniflarHam, setSiniflarHam] = useState<SiniflarYaniti | null>(null)

  useEffect(() => {
    // Sistem durumu ve sınıf tanımları arka planda gelir; arayüzü
    // bekletmezler.
    api.durum().then(setDurum).catch(() => setDurum(null))
    api.siniflar().then(setSiniflarHam).catch(() => setSiniflarHam(null))

    // Jeton yoksa oturum sorgusu HİÇ yapılmaz: giriş ekranı anında açılır.
    //
    // Önceden uygulama /auth/ben cevabını bekleyene kadar "Yükleniyor…"
    // gösteriyordu. Sunucu uykudaysa (Render ücretsiz katmanı ilk isteği
    // ~50 sn bekletiyor) kullanıcı ekrana bakıp sistemin bozuk olduğunu
    // sanıyordu — oysa yapması gereken tek şey giriş yapmaktı.
    if (!jetonAl()) {
      setKullanici(null)
      setYukleniyor(false)
      return
    }

    api.ben()
      .then(setKullanici)
      .catch(() => { jetonSil(); setKullanici(null) })
      .finally(() => setYukleniyor(false))
  }, [])

  const girisYap = useCallback(async (eposta: string, parola: string) => {
    const y = await api.giris(eposta, parola)
    jetonYaz(y.jeton)
    setKullanici(y.kullanici)
  }, [])

  const cikisYap = useCallback(() => {
    jetonSil()
    setKullanici(null)
  }, [])

  const siniflar = new Map((siniflarHam?.siniflar ?? []).map((s) => [s.ad, s]))

  return (
    <Ctx.Provider value={{
      kullanici, yukleniyor, durum, siniflar, siniflarHam, girisYap, cikisYap,
    }}>
      {children}
    </Ctx.Provider>
  )
}

export function useDurum() {
  const d = useContext(Ctx)
  if (!d) throw new Error('DurumSaglayici dışında kullanılamaz')
  return d
}
