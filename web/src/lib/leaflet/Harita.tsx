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
import { useEffect, useRef, useState } from 'react'
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

  /**
   * Altlık karoları yüklenemedi mi?
   *
   * ⚠️ BU SESSİZ BİR ARIZAYDI. Karolar `tile.openstreetmap.org`'dan
   * gelir; ağ kapalıysa, kurum güvenlik duvarı engelliyorsa ya da jüri
   * sistemi çevrimdışı bir makinede çalıştırıyorsa Leaflet hiçbir şey
   * söylemeden BOŞ GRİ BİR KUTU bırakıyordu. Ekranda ne bir hata, ne bir
   * açıklama vardı — projenin amiral gemisi olan Malzeme Kaynak Haritası
   * "bozuk" görünüyordu, oysa işaretçiler ve saha sınırları çalışıyordu.
   *
   * Ayrım önemli: altlık bir GÖRSEL BAĞLAMDIR, verinin kendisi değil.
   * Yokluğunda gösterilecek şey bir hata ekranı değil, karoların
   * gelmediğini söyleyen ve verinin durduğunu belirten bir nottur.
   */
  const [altlikYok, setAltlikYok] = useState(false)

  useEffect(() => {
    if (!kapsayici.current || harita.current) return

    const h = L.map(kapsayici.current, {
      center: merkez,
      zoom: yakinlik,
      // Klavye ile gezinme açık — erişilebilirlik.
      keyboard: true,
    })

    const karolar = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      // Atıf zorunludur (ODbL 1.0).
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> katkıcıları',
    })

    // Tek bir karo hatası bir aksaklık olabilir; birkaçı ard arda
    // gelirse altlık gerçekten yok demektir. Eşik, ilk ekranda yüklenen
    // karo sayısının altında tutuldu ki durum hızlı anlaşılsın.
    let hataSayisi = 0
    karolar.on('tileerror', () => {
      hataSayisi += 1
      if (hataSayisi >= 3) setAltlikYok(true)
    })
    karolar.on('tileload', () => setAltlikYok(false))
    karolar.addTo(h)

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
    <div className="relative">
      <div
        ref={kapsayici}
        style={{ height: yukseklik }}
        /* `harita-koyu` bileşenin KENDİSİNDE: karo filtresi tek tek
           çağrı yerlerine bırakılırsa unutuluyor — "Yeni alan tanımla"
           formundaki harita koyu temada bembeyaz kalıyordu. Açık temada
           --u-harita-filtre zaten `none`. */
        className="harita-koyu w-full rounded-lg border border-kenar"
        role="application"
        aria-label={etiket}
      />
      {altlikYok && (
        /* Sol üstte Leaflet'in yakınlaştırma denetimi duruyor; bildirim
           tam ekranı kaplarsa onun üzerine biner ve haritayı gerçekten
           kullanılamaz hâle getirir. Sol kenardan denetim genişliği
           kadar boşluk bırakılır. */
        <p role="status"
          className="absolute left-14 right-3 top-3 z-[1000] flex items-start
            gap-2 text-xs leading-relaxed rounded-md px-3 py-2.5
            bg-yuzey-ust border border-uyari/50 text-metin-2 shadow-kart">
          <span aria-hidden className="text-uyari font-bold shrink-0">!</span>
          <span>
            <strong className="text-uyari font-semibold">
              Harita altlığı yüklenemedi.
            </strong>{' '}
            Çevrimdışı olabilirsiniz ya da ağınız OpenStreetMap'e
            erişemiyor. <strong className="text-metin">Saha işaretçileri ve
            sınırlar aşağıda gösterilmeye devam ediyor</strong> — eksik
            olan yalnızca arka plandaki harita görüntüsüdür.
          </span>
        </p>
      )}
    </div>
  )
}

/**
 * Leaflet'in varsayılan işaretçi ikonları paket yolundan gelmez; düzeltir.
 *
 * Halka rengi jetondan gelir: `#0e1116` olarak sabit kodlanmıştı ve açık
 * temada işaretçinin çevresinde neredeyse siyah bir çember bırakıyordu.
 *
 * ⚠️ İşaretçiye ERİŞİLEBİLİR AD vermek çağıranın işidir:
 * `L.marker(..., { title: alanAdi })`. Leaflet işaretçiyi `role="button"`
 * ve `tabindex="0"` ile çizer; ad verilmezse ekran okuyucu yalnızca
 * "düğme" der ve hangi saha olduğunu söylemez (axe-core:
 * `aria-command-name`, serious).
 */
export function isaretciIkonu(renk: string): L.DivIcon {
  return L.divIcon({
    className: '',
    html: `<span style="display:block;width:18px;height:18px;border-radius:50%;
      background:${renk};border:3px solid var(--u-isaretci-halka);
      box-shadow:0 0 0 2px ${renk}"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  })
}
