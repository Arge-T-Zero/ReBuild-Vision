import { useEffect, useRef, useState } from 'react'
import type { SinifTanimi, Tespit } from '../types'
import { yuzdeMetni } from './GuvenSkoru'

/**
 * Görüntü üzerinde tespit kutuları.
 *
 * KUTU ÖLÇEKLEME: kutuların hangi koordinat uzayında verildiği
 * `bbox_format` alanından okunur (ana talimat Bölüm 4.3 — brief bunu en
 * sık hata kaynağı olarak işaretlemiş). Bilinmeyen bir format gelirse
 * kutu ÇİZİLMEZ ve durum kullanıcıya söylenir; yanlış yerde kutu
 * göstermektense hiç göstermemek doğrudur.
 */
/**
 * Sınıf renginin üzerinde okunacak metin rengi.
 *
 * ⚠️ Etiket metni `#0e1116` olarak SABİT KODLANMIŞTI ve üç sınıf renginde
 * WCAG AA'nın altında kalıyordu (ölçüldü): `yumusak_plastik` 3,82 ·
 * `konteyner` 3,91 · `dolgu_toprak` 4,14. Etiket, kutunun ne olduğunu
 * söyleyen tek yazıdır; okunamıyorsa kutu da anlamsızdır.
 *
 * Sınıf renkleri `siniflar.json`'dan gelir ve DEĞİŞTİRİLEMEZ (index.css
 * içindeki kural). Bu yüzden düzeltme metin tarafında: rengin bağıl
 * parlaklığına göre koyu ya da beyaz seçilir. Ölçüldü: on sınıfın
 * tamamında en düşük oran 4,57.
 */
const ETIKET_KOYU = '#0e1116'
const ETIKET_ACIK = '#ffffff'

function bagilParlaklik(renk: string): number {
  const h = renk.replace('#', '')
  const [r, g, b] = [0, 2, 4].map((i) => {
    const c = parseInt(h.slice(i, i + 2), 16) / 255
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

/** Eşik 0,19: on sınıf rengiyle ölçülerek belirlendi. */
function okunurMetin(renk: string): string {
  return bagilParlaklik(renk) > 0.19 ? ETIKET_KOYU : ETIKET_ACIK
}

export function TespitKutulari({
  gorselUrl, tespitler, goruntuGenislik, goruntuYukseklik, siniflar,
  secili, secildi, vurgulu, vurgulandi,
}: {
  gorselUrl: string
  tespitler: Tespit[]
  goruntuGenislik: number | null
  goruntuYukseklik: number | null
  siniflar: Map<string, SinifTanimi>
  secili?: number | null
  secildi?: (id: number) => void
  /** Listede üzerine gelinen tespit — kutusu öne çıkar. */
  vurgulu?: number | null
  vurgulandi?: (id: number | null) => void
}) {
  const gorselRef = useRef<HTMLImageElement>(null)
  const [olcu, setOlcu] = useState({ g: 0, y: 0 })

  useEffect(() => {
    const el = gorselRef.current
    if (!el) return
    const guncelle = () => setOlcu({ g: el.clientWidth, y: el.clientHeight })
    guncelle()
    const gozlemci = new ResizeObserver(guncelle)
    gozlemci.observe(el)
    return () => gozlemci.disconnect()
  }, [gorselUrl])

  const kaynakG = goruntuGenislik ?? 0
  const kaynakY = goruntuYukseklik ?? 0
  const olceklenebilir = kaynakG > 0 && kaynakY > 0 && olcu.g > 0

  /**
   * Etiketlerin nereye konacağını çakışmadan hesaplar.
   *
   * Birbirine yakın iki kutunun etiketi üst üste biniyordu; ekranda
   * "Dolgu toprak · %76" ile "Beton · %32" iç içe geçiyordu. Sabit bir
   * kural (hep üstte, ya da sıra numarasına göre değiştir) yetmiyor:
   * aynı tarafa düşen iki komşu kutu yine çakışıyor.
   *
   * Burada her etiket için dört aday yer denenir (üst-sol, üst-sağ,
   * alt-sol, alt-sağ) ve önceden yerleştirilmiş etiketlerle KESİŞMEYEN
   * ilk aday seçilir. Hiçbiri uymazsa ilk aday kullanılır — o zaman da
   * vurgulanan etiket zIndex ile öne gelir.
   *
   * Genişlik ölçülmez, TAHMİN EDİLİR: etiket ölçülene kadar çizilemez,
   * çizildikten sonra ölçmek ise düzeni bir kare boyunca titretirdi.
   * Tahmin bilinçli olarak cömerttir; fazladan boşluk bırakmak, çakışan
   * etiketten iyidir.
   */
  const yerlesim = (() => {
    // `solOfset` KUTUYA GÖRE piksel: etiket görüntünün dışına taşmasın
    // diye mutlak konum önce görüntü sınırlarına kırpılır, sonra kutuya
    // göre ofsete çevrilir. Önceden etiket `left:0` / `right:0` ile
    // kutuya yapışıyordu ve sağ kenardaki bir kutunun uzun etiketi
    // görüntüyü aşıyordu: 390 px telefonda sayfa 461 px'e uzayıp YATAY
    // KAYDIRMAYA düşüyordu (ölçüldü).
    const sonuc = new Map<number, { altta: boolean; solOfset: number }>()
    if (!olceklenebilir) return sonuc
    const oran = olcu.g / kaynakG
    // Sabitler tarayıcıda ÖLÇÜLEREK kalibre edildi: gerçek etiket
    // genişlikleri 153/154/180/188/189 px çıktı; sınıf adı uzunluğuna
    // göre regresyon ≈ 7 px/karakter + 118 px sabit (yüzde metni,
    // "ÖN TAHMİN" rozeti, boşluklar ve iç kenar payı).
    const KARAKTER = 7
    const SABIT = 118
    const PAY = 8             // çakışmaya karşı emniyet payı
    const YUKSEKLIK = 22

    const yerlesenler: { x: number; y: number; g: number; y2: number }[] = []
    const kesisiyor = (a: typeof yerlesenler[0]) => yerlesenler.some(
      (v) => a.x < v.x + v.g && v.x < a.x + a.g
        && a.y < v.y2 && v.y < a.y2,
    )

    for (const t of tespitler) {
      if (t.bbox_format !== 'pixel_absolute_original' || !t.bbox) continue
      const ad = siniflar.get(t.duzeltilen_sinif ?? t.sinif)?.gorunen_ad ?? t.sinif
      const g = ad.length * KARAKTER + SABIT + PAY
      const kx = t.bbox.x * oran
      const ky = t.bbox.y * oran
      const kg = t.bbox.w * oran
      const kyuk = t.bbox.h * oran

      const adaylar = [
        { altta: false, sagaYasli: false },
        { altta: false, sagaYasli: true },
        { altta: true, sagaYasli: false },
        { altta: true, sagaYasli: true },
      ].filter((a) => !(!a.altta && ky < YUKSEKLIK + 6))  // üstte yer yoksa ele

      const uygun = adaylar.length > 0 ? adaylar : [{ altta: true, sagaYasli: false }]
      let secim = uygun[0]
      for (const a of uygun) {
        const x = a.sagaYasli ? kx + kg - g : kx
        const y = a.altta ? ky + kyuk + 3 : ky - YUKSEKLIK - 3
        if (!kesisiyor({ x, y, g, y2: y + YUKSEKLIK })) { secim = a; break }
      }
      const hamX = secim.sagaYasli ? kx + kg - g : kx
      // Görüntünün içine kırp; etiket görselden geniş olamaz.
      const x = Math.max(0, Math.min(hamX, Math.max(0, olcu.g - g)))
      const y = secim.altta ? ky + kyuk + 3 : ky - YUKSEKLIK - 3
      yerlesenler.push({ x, y, g, y2: y + YUKSEKLIK })
      sonuc.set(t.id, { altta: secim.altta, solOfset: x - kx })
    }
    return sonuc
  })()

  return (
    <div className="relative inline-block max-w-full">
      <img
        ref={gorselRef}
        src={gorselUrl}
        alt="Enkaz alanı görüntüsü"
        className="max-w-full h-auto rounded-lg block"
      />
      {olceklenebilir && tespitler.map((t) => {
        // Yalnızca orijinal piksel uzayındaki kutular çizilir.
        if (t.bbox_format !== 'pixel_absolute_original' || !t.bbox) return null
        const oran = olcu.g / kaynakG
        const renk = siniflar.get(t.duzeltilen_sinif ?? t.sinif)?.renk ?? '#8593a1'
        const aktif = secili === t.id
        const one = vurgulu === t.id
        // Başka bir kutu vurgulanmışken bu kutu geri çekilir; göz doğrudan
        // listede üzerine gelinen kayda gider.
        const soluk = vurgulu != null && !one && !aktif

        // Yerleşim yukarıda, çakışma kontrolüyle birlikte hesaplandı.
        const { altta, solOfset } = yerlesim.get(t.id)
          ?? { altta: false, solOfset: 0 }
        const etiketRengi = okunurMetin(renk)

        return (
          <button
            key={t.id}
            onClick={() => secildi?.(t.id)}
            onMouseEnter={() => vurgulandi?.(t.id)}
            onMouseLeave={() => vurgulandi?.(null)}
            onFocus={() => vurgulandi?.(t.id)}
            onBlur={() => vurgulandi?.(null)}
            /* Ekran okuyucu HAM sınıf adını ("dolgu_toprak") okuyordu ve
               uzmanın düzeltmesini hiç yansıtmıyordu: kutu görsel olarak
               düzeltilmiş sınıfı gösterirken sesli olarak modelin ilk
               tahminini söylüyordu. */
            aria-label={
              `${siniflar.get(t.duzeltilen_sinif ?? t.sinif)?.gorunen_ad
                ?? (t.duzeltilen_sinif ?? t.sinif)} tespiti`
              + `, model güveni yüzde ${yuzdeMetni(t.guven_skoru)}`
              + (t.duzeltilen_sinif ? ' (uzman düzeltmesi)' : ' (ön tahmin)')
            }
            className="absolute p-0 min-h-0 focus-visible:z-20 transition-opacity"
            style={{
              left: t.bbox.x * oran,
              top: t.bbox.y * oran,
              width: t.bbox.w * oran,
              height: t.bbox.h * oran,
              border: `${aktif || one ? 3 : 2}px ${
                t.inceleme_gerekli ? 'dashed' : 'solid'} ${renk}`,
              background: aktif || one ? `${renk}2e` : 'transparent',
              borderRadius: 3,
              opacity: soluk ? 0.35 : 1,
              zIndex: one ? 10 : aktif ? 5 : 1,
              boxShadow: one ? `0 0 0 2px ${renk}55` : undefined,
            }}
          >
            {/* Yer seçimi `yerlesim` içinde çakışma kontrolüyle yapıldı.
                Vurgulanan etiket zIndex ile öne gelir.

                ⚠️ SOLUK KUTUNUN ETİKETİ ARTIK ÇİZİLMİYOR — ÖNCEDEN
                OKUNAMAZ HÂLDE EKRANDA DURUYORDU.

                `opacity: 0.35` düğmenin tamamına uygulanıyor, yani
                etiketin hem zemini hem yazısı fotoğrafa doğru soluyordu.
                Ölçülen sonuç: `#0e1116` yazı `#3987e5` zeminde 0,35
                opaklıkla `#abacad` / `#bad5f6` olarak render ediliyor ve
                kontrast **1,5**'e düşüyordu (eşik 4,5). Aynı şey dolgu
                toprak etiketinde 1,57, ahşapta 1,45.

                Bu geçici bir durum değildi: `soluk`, listede herhangi bir
                satırın üzerine gelindiği ANDA doğru olur — yani uzmanın
                kuyruk üzerinde çalıştığı sürenin neredeyse tamamında.
                Ekranda okunamayacak kadar soluk ama yer kaplayan dokuz
                etiket duruyordu.

                Doğru davranış, yazıyı soldurmak değil KALDIRMAKTIR:
                geri çekilen tespidin kutusu (konum + sınıf rengi) yerinde
                kalır, etiketi çizilmez. Hiçbir bilgi kaybolmaz — vurgulu
                ve seçili tespitlerin etiketleri tam okunaklı durur, imleç
                çekilince hepsi geri gelir — ve fotoğrafın üstü de
                gerçekten sadeleşir. */}
            {!soluk && <span
              className="absolute px-1.5 py-0.5 rounded text-xs font-semibold
                whitespace-nowrap flex items-center gap-1"
              style={{
                background: renk,
                color: etiketRengi,
                [altta ? 'top' : 'bottom']: 'calc(100% + 3px)',
                left: solOfset,
                zIndex: one ? 12 : aktif ? 6 : 2,
              }}
            >
              {siniflar.get(t.duzeltilen_sinif ?? t.sinif)?.gorunen_ad ?? t.sinif}
              {' · %'}{yuzdeMetni(t.guven_skoru)}
              {/* Her kutuda "ön tahmin", istisnasız (ana talimat Bölüm 1.4).
                  Kutunun kendisi tek başına bakıldığında kesinlik iddia
                  etmemelidir; listedeki rozet burada da bulunmalıdır. */}
              <span
                className="px-1 rounded-[2px] font-medium tracking-wide"
                /* Rozet, etiketin rengini TERSİNE çevirir; oran simetrik
                   olduğu için iki yönde de aynı ve AA'yı geçer. */
                style={{ background: etiketRengi, color: renk, fontSize: 9 }}
              >
                ÖN TAHMİN
              </span>
            </span>}
          </button>
        )
      })}
    </div>
  )
}

/** Çizilemeyen kutular için uyarı — sessizce yutulmaz. */
export function CizilemeyenKutuUyarisi({ tespitler }: { tespitler: Tespit[] }) {
  const cizilemeyen = tespitler.filter(
    (t) => t.bbox_format !== 'pixel_absolute_original' || !t.bbox,
  )
  if (cizilemeyen.length === 0) return null
  return (
    <p className="text-xs text-uyari mt-2">
      {cizilemeyen.length} tespitin kutusu çizilemedi: koordinat biçimi
      tanınmıyor ({[...new Set(cizilemeyen.map((t) => t.bbox_format))].join(', ')}).
      Yanlış konumda kutu göstermemek için çizim yapılmadı.
    </p>
  )
}
