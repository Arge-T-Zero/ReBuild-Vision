/**
 * Leaflet için ince React sarmalayıcısı.
 *
 * `react-leaflet` BİLİNÇLİ OLARAK KULLANILMIYOR: lisansı `Hippocratic-2.1`,
 * OSI onaylı bir açık kaynak lisansı değil ve kullanım kısıtı içeriyor.
 * Şartname Madde 5.5 ürünün Kuruma bedelsiz ve koşulsuz devrini istiyor;
 * kullanım kısıtı taşıyan bir bileşen bu devri kirletir.
 * Bkz. docs/karar-kaydi.md K-002.
 *
 * Bunun yerine `leaflet` (BSD-2-Clause) doğrudan kullanılıyor.
 */
import { useEffect, useRef } from 'react'
import L from 'leaflet'

export interface HaritaOzellikleri {
  merkez: [number, number]
  yakinlik?: number
  yukseklik?: string
  /** Harita hazır olduğunda bir kez çağrılır. */
  hazir?: (harita: L.Map) => void
  /** Haritaya tıklandığında çağrılır. */
  tiklandi?: (enlem: number, boylam: number) => void
  etiket: string
}

export function Harita({
  merkez, yakinlik = 15, yukseklik = '420px', hazir, tiklandi, etiket,
}: HaritaOzellikleri) {
  const kapsayici = useRef<HTMLDivElement>(null)
  const harita = useRef<L.Map | null>(null)
  const tiklamaRef = useRef(tiklandi)
  tiklamaRef.current = tiklandi

  useEffect(() => {
    if (!kapsayici.current || harita.current) return

    const h = L.map(kapsayici.current, {
      center: merkez,
      zoom: yakinlik,
      // Klavye ile gezinme açık — erişilebilirlik.
      keyboard: true,
    })

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      // Atıf zorunludur (ODbL 1.0).
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> katkıcıları',
    }).addTo(h)

    h.on('click', (e: L.LeafletMouseEvent) => {
      tiklamaRef.current?.(e.latlng.lat, e.latlng.lng)
    })

    harita.current = h
    hazir?.(h)

    return () => {
      h.remove()
      harita.current = null
    }
    // Harita bir kez kurulur; merkez/yakınlık değişimi ayrı ele alınır.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    harita.current?.setView(merkez, yakinlik)
  }, [merkez[0], merkez[1], yakinlik])

  return (
    <div
      ref={kapsayici}
      style={{ height: yukseklik }}
      className="w-full rounded-lg border border-kenar"
      role="application"
      aria-label={etiket}
    />
  )
}

/** Leaflet'in varsayılan işaretçi ikonları paket yolundan gelmez; düzeltir. */
export function isaretciIkonu(renk: string): L.DivIcon {
  return L.divIcon({
    className: '',
    html: `<span style="display:block;width:18px;height:18px;border-radius:50%;
      background:${renk};border:3px solid #0e1116;box-shadow:0 0 0 2px ${renk}"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  })
}
