import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { useDurum } from '../durum'
import { SAYFA_ACIKLAMASI, SAYFA_ETIKETI, rolTanimi } from '../roller'
import type { SayfaAdi } from '../roller'
import { Buton } from './Temel'

/**
 * İlk giriş turu — adım adım "burası ne işe yarar".
 *
 * Menüde bir sekmenin ADINI görmek ne yaptığını söylemiyor: "Kuyruk"
 * nedir, oraya niye gidilir, kim gider? Kullanıcı sistemi deneyerek
 * öğrenmek zorunda kalıyordu ve burası bir afet yönetim aracı —
 * deneyerek öğrenmenin maliyeti yüksek.
 *
 * Tur, ilgili menü öğesinin ÜZERİNİ aydınlatır ve yanında tek cümlelik
 * açıklamasını gösterir. Bir liste kartı yerine tur seçilmesinin sebebi:
 * liste "şurada şu var" der ama kullanıcı o şeyin EKRANDA NEREDE
 * olduğunu öğrenmez. Aydınlatma bunu doğrudan gösterir.
 *
 * Hedefler ekran genişliğine göre değişir: masaüstünde üst çubuk, dar
 * ekranda alt çubuk. Bileşen görünür olanı ölçerek bulur — hangisinin
 * açık olduğunu tahmin etmez.
 *
 * Tur YALNIZCA O ROLÜN menüsünü anlatır. Yönetici ekranını hiç
 * göremeyecek bir saha personeline "rol onayları" diye bir yerden söz
 * etmek öğretmek değil, kafa karıştırmaktır.
 *
 * Bir kez bitirilince ya da atlanınca bir daha gösterilmez. Tercih
 * kullanıcı kimliğine göre saklanır: aynı tarayıcıda başka bir hesapla
 * giren kişi turu yeniden görür — o başka bir insandır.
 */

interface Adim {
  /** Aydınlatılacak öğe; yoksa kart ekranın ortasında durur. */
  hedef?: string
  baslik: string
  metin: string
}

const KART_GENISLIK = 340
const PAY = 12

function anahtar(kullaniciId: number) {
  return `rebuild_vision_tanitim_${kullaniciId}`
}

function gorulduMu(kullaniciId: number): boolean {
  try {
    return localStorage.getItem(anahtar(kullaniciId)) === 'bitti'
  } catch {
    // Depolama engelliyse tur her girişte çıkar. Rahatsız edici ama
    // bozuk değil; sessizce çökmesindense görünmesi iyidir.
    return false
  }
}

/**
 * Hedefin ekrandaki yeri.
 *
 * Aynı `data-tanitim` değeri İKİ yerde bulunur (üst çubuk ve alt çubuk);
 * biri `display:none` olduğu için ölçüsü sıfırdır. Görünür olan seçilir.
 */
function hedefKutusu(ad: string): DOMRect | null {
  const adaylar = document.querySelectorAll<HTMLElement>(`[data-tanitim="${ad}"]`)
  for (const el of adaylar) {
    const k = el.getBoundingClientRect()
    if (k.width > 0 && k.height > 0) return k
  }
  return null
}

export function IlkTanitim({ git }: {
  git: (s: Exclude<SayfaAdi, 'alan'>) => void
}) {
  const { kullanici, durum } = useDurum()
  const [acik, setAcik] = useState(
    () => (kullanici ? !gorulduMu(kullanici.id) : false),
  )
  const [sira, setSira] = useState(0)
  const [kutu, setKutu] = useState<DOMRect | null>(null)
  const [kartYuk, setKartYuk] = useState(200)
  const kartRef = useRef<HTMLDivElement>(null)

  const tanim = rolTanimi(kullanici?.rol ?? null)
  const sahteModel = durum?.model_servisi.sahte === true

  const adimlar: Adim[] = [
    {
      baslik: `Hoş geldiniz, ${kullanici?.ad ?? ''}`,
      metin: `Sisteme ${tanim.ad} olarak bağlandınız. ${tanim.gorev} `
        + 'Şimdi kısaca hangi ekranın ne işe yaradığını göstereceğim — '
        + 'birkaç adım sürer.',
    },
    ...tanim.menu.map((s) => ({
      hedef: s,
      baslik: SAYFA_ETIKETI[s],
      metin: SAYFA_ACIKLAMASI[s],
    })),
    ...(sahteModel
      ? [{
          hedef: 'model',
          baslik: 'Sahte model servisi',
          metin: 'Bu rozet, sınıflandırmanın GERÇEK bir modelden değil '
            + 'sahte servisten geldiğini söyler. Model henüz eğitilmedi; '
            + 'sınıf ve güven skorları uydurmadır. Rozet, gerçek model '
            + 'bağlandığında kendiliğinden kaybolur.',
        }]
      : []),
    {
      baslik: 'Son kararı sistem vermez',
      metin: 'Model çıktılarının hepsi "ön tahmin" etiketiyle görünür. '
        + 'Uzman onaylamadan hiçbir kayıt haritaya ya da rapora girmez. '
        + 'Sistem tehlikeli madde teşhisi yapmaz ve yalnızca görünür '
        + 'yüzeyi değerlendirir.',
    },
  ]

  const adim = adimlar[sira]
  const sonMu = sira === adimlar.length - 1

  const bitir = useCallback(() => {
    setAcik(false)
    if (!kullanici) return
    try { localStorage.setItem(anahtar(kullanici.id), 'bitti') } catch { /* yoksay */ }
  }, [kullanici])

  // Hedefin yerini ölç. Pencere boyutu değişince (ya da dönünce) çubuk
  // üstten alta taşınabiliyor; ölçüm tekrarlanmazsa aydınlatma boş bir
  // yeri gösterir.
  useLayoutEffect(() => {
    if (!acik) return
    const olc = () => setKutu(adim?.hedef ? hedefKutusu(adim.hedef) : null)
    olc()
    window.addEventListener('resize', olc)
    window.addEventListener('scroll', olc, true)
    return () => {
      window.removeEventListener('resize', olc)
      window.removeEventListener('scroll', olc, true)
    }
  }, [acik, sira, adim?.hedef])

  useLayoutEffect(() => {
    if (kartRef.current) setKartYuk(kartRef.current.offsetHeight)
  }, [sira, acik])

  // Esc turu atlar; klavye kullanıcısı tuzağa düşmez.
  useEffect(() => {
    if (!acik) return
    const t = (e: KeyboardEvent) => {
      if (e.key === 'Escape') bitir()
      if (e.key === 'ArrowRight' && !sonMu) setSira((n) => n + 1)
      if (e.key === 'ArrowLeft' && sira > 0) setSira((n) => n - 1)
    }
    window.addEventListener('keydown', t)
    return () => window.removeEventListener('keydown', t)
  }, [acik, sonMu, sira, bitir])

  // Kart açılınca odak ona geçer: ekran okuyucu turu duyurur, klavye
  // kullanıcısı doğrudan düğmelere ulaşır.
  useEffect(() => {
    if (acik) kartRef.current?.focus()
  }, [acik, sira])

  if (!acik || !kullanici || !adim) return null

  // Kartın yeri: hedefin altında yer varsa altta, yoksa üstünde.
  // Alt çubuk ekranın dibinde durduğu için mobilde neredeyse her zaman
  // üstte çıkar.
  const gorunumY = window.innerHeight
  const gorunumX = window.innerWidth
  const genislik = Math.min(KART_GENISLIK, gorunumX - PAY * 2)

  let ust: number
  let sol: number
  if (kutu) {
    const altaSigar = kutu.bottom + PAY + kartYuk < gorunumY - PAY
    ust = altaSigar ? kutu.bottom + PAY : kutu.top - kartYuk - PAY
    sol = kutu.left + kutu.width / 2 - genislik / 2
  } else {
    ust = gorunumY / 2 - kartYuk / 2
    sol = gorunumX / 2 - genislik / 2
  }
  ust = Math.max(PAY, Math.min(ust, gorunumY - kartYuk - PAY))
  sol = Math.max(PAY, Math.min(sol, gorunumX - genislik - PAY))

  return (
    <>
      {/* Perde. Aydınlatma, halkanın DIŞINA taşan dev bir gölgeyle
          yapılır: ayrı bir maske katmanı ya da dört ayrı panel
          gerekmez, hedef gerçekten "delik" gibi görünür. */}
      <div
        aria-hidden
        onClick={bitir}
        /* z-index Leaflet'in ÜSTÜNDE olmak zorunda: harita katmanları
           400–700 arasında, harita altlık uyarısı 1000'de duruyor.
           Daha düşük bir değerde harita işaretçileri turun kartını
           deliyordu (ölçüldü: mobilde 4. adımda işaretçi kartın
           üstüne biniyordu). */
        className="fixed inset-0 z-[2000]"
        style={kutu
          ? {
              // Hedefin kendisi perdenin altında kalmaz: tıklama
              // perdeye gider, kullanıcı yanlışlıkla sayfayı
              // değiştirmez.
              background: 'transparent',
              boxShadow: 'none',
            }
          : { background: 'rgba(8, 12, 18, 0.55)' }}
      >
        {kutu && (
          <span
            className="absolute rounded-lg"
            style={{
              left: kutu.left - 4,
              top: kutu.top - 4,
              width: kutu.width + 8,
              height: kutu.height + 8,
              boxShadow: '0 0 0 9999px rgba(8, 12, 18, 0.55), '
                + '0 0 0 2px var(--u-marka)',
            }}
          />
        )}
      </div>

      <div
        ref={kartRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="tanitim-baslik"
        aria-describedby="tanitim-metin"
        tabIndex={-1}
        className="fixed z-[2001] rounded-kart border border-kenar bg-yuzey-ust
          shadow-[var(--u-golge-ust)] p-4 outline-none"
        style={{ left: sol, top: ust, width: genislik }}
      >
        {/* `metin-4` idi: koyu temada `yuzey-ust` üzerinde tam 4,50 ile
            sınırda kalıp AA'yı geçemiyordu (axe: serious). Bir ton
            açıldı — koyu temada 5,01, açık temada 7,37. */}
        <p className="text-xs text-metin-3 sayisal mb-1.5">
          {sira + 1} / {adimlar.length}
        </p>
        <h2 id="tanitim-baslik" className="font-semibold tracking-tight">
          {adim.baslik}
        </h2>
        <p id="tanitim-metin"
          className="text-sm text-metin-2 mt-1.5 leading-relaxed">
          {adim.metin}
        </p>

        <div className="flex items-center justify-between gap-3 mt-4">
          <button onClick={bitir}
            className="text-sm text-metin-3 hover:text-metin transition-colors
              !min-h-0">
            Turu atla
          </button>

          <div className="flex gap-2">
            {sira > 0 && (
              <Buton tur="ikincil" boyut="kucuk"
                onClick={() => setSira((n) => n - 1)}>
                Geri
              </Buton>
            )}
            <Buton
              boyut="kucuk"
              onClick={() => {
                if (sonMu) { bitir(); return }
                // Anlatılan ekrana GİDİLİR: kullanıcı okuduğu yeri aynı
                // anda görür, sonradan menüde arayıp bulmak zorunda
                // kalmaz.
                const sonraki = adimlar[sira + 1]
                if (sonraki?.hedef && sonraki.hedef !== 'model') {
                  git(sonraki.hedef as Exclude<SayfaAdi, 'alan'>)
                }
                setSira((n) => n + 1)
              }}
            >
              {sonMu ? 'Bitir' : 'İleri'}
            </Buton>
          </div>
        </div>
      </div>
    </>
  )
}
