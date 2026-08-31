import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { api, jetonAl, jetonSil, jetonYaz, OTURUM_DUSTU } from './api'
import type { Kullanici, SinifTanimi, SiniflarYaniti, SistemDurumu } from './types'

interface Baglam {
  kullanici: Kullanici | null
  yukleniyor: boolean
  /** Oturum kendiliğinden düştüyse giriş ekranında gösterilecek not. */
  oturumNotu: string
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
  const [oturumNotu, setOturumNotu] = useState('')

  // Jeton geçerliliğini yitirdiğinde uygulama giriş ekranına döner ve
  // NEDENİNİ söyler. Sessizce giriş ekranına atmak, kullanıcının az önce
  // yazdığı bir şeyi kaybettiğini anlamamasına yol açardı.
  useEffect(() => {
    const dinleyici = () => {
      setKullanici(null)
      setOturumNotu(
        'Oturumunuz sona erdi. Kaldığınız yerden devam etmek için '
        + 'tekrar giriş yapın.',
      )
    }
    window.addEventListener(OTURUM_DUSTU, dinleyici)
    return () => window.removeEventListener(OTURUM_DUSTU, dinleyici)
  }, [])

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
    setOturumNotu('')
  }, [])

  const cikisYap = useCallback(() => {
    jetonSil()
    setKullanici(null)
    setOturumNotu('')
    // Adres de sıfırlanır: çıkıştan sonra `/alan/3` adresinde kalmak,
    // geri düğmesine basınca kullanıcıyı giremeyeceği bir yola
    // götürüyordu.
    try { window.history.replaceState(null, '', '/') } catch { /* yoksay */ }
  }, [])

  const siniflar = new Map((siniflarHam?.siniflar ?? []).map((s) => [s.ad, s]))

  return (
    <Ctx.Provider value={{
      kullanici, yukleniyor, durum, siniflar, siniflarHam, girisYap, cikisYap,
      oturumNotu,
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
