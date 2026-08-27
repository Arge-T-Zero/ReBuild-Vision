import { useEffect, useRef, useState } from 'react'
import type { SinifTanimi, Tespit } from '../types'

/**
 * Görüntü üzerinde tespit kutuları.
 *
 * KUTU ÖLÇEKLEME: kutuların hangi koordinat uzayında verildiği
 * `bbox_format` alanından okunur (ana talimat Bölüm 4.3 — brief bunu en
 * sık hata kaynağı olarak işaretlemiş). Bilinmeyen bir format gelirse
 * kutu ÇİZİLMEZ ve durum kullanıcıya söylenir; yanlış yerde kutu
 * göstermektense hiç göstermemek doğrudur.
 */
export function TespitKutulari({
  gorselUrl, tespitler, goruntuGenislik, goruntuYukseklik, siniflar, secili, secildi,
}: {
  gorselUrl: string
  tespitler: Tespit[]
  goruntuGenislik: number | null
  goruntuYukseklik: number | null
  siniflar: Map<string, SinifTanimi>
  secili?: number | null
  secildi?: (id: number) => void
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
        return (
          <button
            key={t.id}
            onClick={() => secildi?.(t.id)}
            aria-label={`${t.sinif} tespiti, güven ${t.guven_skoru}`}
            className="absolute p-0 min-h-0 focus-visible:z-10"
            style={{
              left: t.bbox.x * oran,
              top: t.bbox.y * oran,
              width: t.bbox.w * oran,
              height: t.bbox.h * oran,
              border: `${aktif ? 3 : 2}px ${t.inceleme_gerekli ? 'dashed' : 'solid'} ${renk}`,
              background: aktif ? `${renk}22` : 'transparent',
              borderRadius: 3,
            }}
          >
            <span
              className="absolute -top-6 left-0 px-1.5 py-0.5 rounded text-[11px]
                font-semibold whitespace-nowrap"
              style={{ background: renk, color: '#0e1116' }}
            >
              {siniflar.get(t.duzeltilen_sinif ?? t.sinif)?.gorunen_ad ?? t.sinif}
              {' · '}{t.guven_skoru}
            </span>
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
