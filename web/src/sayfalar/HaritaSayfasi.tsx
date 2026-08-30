import { useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import { Harita, isaretciIkonu } from '../lib/leaflet/Harita'
import {
  Baslik, BosDurum, Buton, Hata, KapsamUyarisi, Kart, OzetSayi,
} from '../bilesenler/Temel'
import { MalzemeDagilimi } from '../bilesenler/MalzemeDagilimi'
import { Ikon } from '../bilesenler/Ikon'
import { RaporIndir } from '../bilesenler/RaporIndir'
import { useGezinme } from '../gezinme'
import { Sayfa } from '../bilesenler/Duzen'
import type { EnkazAlani } from '../types'
import L from 'leaflet'
import { sayfaGorevi } from '../roller'

/**
 * Malzeme Kaynak Haritası.
 *
 * Yalnızca DOĞRULANMIŞ kayıtlar gösterilir — filtre veri katmanındadır
 * (ana talimat Bölüm 1.4). Lejandda kapsam uyarısı YAZILI olarak bulunur
 * (Bölüm 1.3).
 */
// api/app/core/permissions.py RAPOR_ALABILIR ile aynı küme.
const RAPOR_ALABILIR = new Set(['yonetici', 'belediye', 'afad'])

/**
 * Harita açılır balonunun içeriğini DOM olarak kurar.
 *
 * ⚠️ Leaflet'in `bindPopup` metoduna dize verilirse onu **HTML olarak
 * ayrıştırır**. Alan adı kullanıcı girdisidir; dize olarak geçirmek
 * saklanmış XSS açığıdır. Alan tanımlama yetkisi olan biri adın içine
 * betik koyarsa, haritayı açan HER kullanıcının oturum jetonu çalınabilir.
 *
 * `textContent` ile kurulan bir düğüm bu yolu tamamen kapatır: tarayıcı
 * içeriği metin olarak ele alır, hiçbir kaçış işlemine gerek kalmaz.
 */
function balon(alan: EnkazAlani): HTMLElement {
  const kok = document.createElement('div')

  const ad = document.createElement('strong')
  ad.textContent = alan.ad
  kok.appendChild(ad)

  const alt = document.createElement('div')
  alt.style.marginTop = '2px'
  alt.style.opacity = '0.75'
  alt.textContent = `${alan.goruntu_sayisi} görüntü · ${alan.tespit_sayisi} tespit`
  kok.appendChild(alt)

  // Doğrulanmış malzemeler — haritanın gösterdiği tek şey bu.
  if (alan.malzeme_dagilimi.length > 0) {
    const m = document.createElement('div')
    m.style.marginTop = '4px'
    m.textContent = alan.malzeme_dagilimi
      .map((d) => `${d.sinif} (${d.adet})`).join(', ')
    kok.appendChild(m)
  }

  return kok
}

export function HaritaSayfasi() {
  const { durum, siniflar, siniflarHam, kullanici } = useDurum()
  const { git, erisilebilir } = useGezinme()
  const [alanlar, setAlanlar] = useState<EnkazAlani[]>([])
  const [dagilim, setDagilim] = useState<{ sinif: string; adet: number }[] | null>(null)
  const [not, setNot] = useState('')
  const [hata, setHata] = useState('')
  const [harita, setHarita] = useState<L.Map | null>(null)
  const [katman] = useState(() => L.layerGroup())
  const [seciliSiniflar, setSeciliSiniflar] = useState<Set<string>>(new Set())

  useEffect(() => {
    api.alanlar().then(setAlanlar).catch((h) => setHata(h.message))
    api.harita()
      .then((h) => { setDagilim(h.malzeme_dagilimi); setNot(h.not) })
      .catch((h) => setHata(h.message))
  }, [])

  useEffect(() => {
    if (!harita) return
    katman.addTo(harita)
    return () => { katman.remove() }
  }, [harita, katman])

  useEffect(() => {
    katman.clearLayers()
    const noktalar: [number, number][] = []
    // Malzeme filtresi HARİTAYA da uygulanır. Önceden yalnızca yan
    // paneldeki sayıyı değiştiriyordu; kullanıcı "Metal"e basıp haritanın
    // aynı kaldığını görünce filtrenin çalışmadığını sanıyordu.
    // Seçili malzemelerden en az birini içermeyen saha haritadan düşer.
    const gorunenAlanlar = seciliSiniflar.size === 0
      ? alanlar
      : alanlar.filter((a) => a.malzeme_dagilimi.some(
        (d) => seciliSiniflar.has(d.sinif),
      ))
    gorunenAlanlar.forEach((a) => {
      if (a.sinir && a.sinir.length >= 3) {
        L.polygon(a.sinir.map((n) => [n.enlem, n.boylam] as [number, number]), {
          color: '#4da3ff', weight: 2, fillOpacity: 0.08,
        }).addTo(katman).bindPopup(balon(a))
      }
      if (a.konum) {
        noktalar.push([a.konum.enlem, a.konum.boylam])
        // `title` işaretçinin ERİŞİLEBİLİR ADIDIR. Leaflet işaretçiyi
        // `role="button"` ile çiziyor; adsız kaldığı için ekran okuyucu
        // yalnızca "düğme" diyor, hangi saha olduğunu söylemiyordu.
        L.marker([a.konum.enlem, a.konum.boylam], {
          icon: isaretciIkonu('#4da3ff'),
          title: `${a.ad} — enkaz alanı`,
          alt: `${a.ad} — enkaz alanı`,
        })
          .addTo(katman)
          .bindPopup(balon(a))
      }
    })
    if (noktalar.length > 0 && harita) {
      if (noktalar.length === 1) {
        // Tek nokta için fitBounds dejenere bir sınır üretir ve harita
        // azami yakınlığa gider; kırsal bir alanda ekran boş kalır.
        harita.setView(noktalar[0], 14)
      } else {
        harita.fitBounds(L.latLngBounds(noktalar).pad(0.3), { maxZoom: 15 })
      }
    }
  }, [alanlar, katman, harita, seciliSiniflar])

  const gorunen = (dagilim ?? []).filter(
    (d) => seciliSiniflar.size === 0 || seciliSiniflar.has(d.sinif),
  )

  function filtreDegistir(ad: string) {
    setSeciliSiniflar((s) => {
      const y = new Set(s)
      if (y.has(ad)) y.delete(ad); else y.add(ad)
      return y
    })
  }

  const toplam = (dagilim ?? []).reduce((t, d) => t + d.adet, 0)

  const haritadakiAlanSayisi = seciliSiniflar.size === 0
    ? alanlar.length
    : alanlar.filter((a) => a.malzeme_dagilimi.some(
      (d) => seciliSiniflar.has(d.sinif),
    )).length

  return (
    <Sayfa>
      <Baslik
        ustBaslik="Doğrulanmış kayıtlar"
        baslik="Malzeme Kaynak Haritası"
        gorev={sayfaGorevi(kullanici?.rol ?? null, 'harita')}
        aciklama={not}
      />

      {hata && <div className="mb-4"><Hata mesaj={hata} /></div>}

      {dagilim !== null && dagilim.length > 0 && (
        <Kart className="mb-5 grid grid-cols-3 divide-x divide-kenar">
          <OzetSayi deger={toplam} etiket="Doğrulanmış tespit" />
          <OzetSayi deger={dagilim.length} etiket="Farklı malzeme türü" />
          <OzetSayi deger={alanlar.length} etiket="Enkaz alanı" />
        </Kart>
      )}

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div>
          <Harita merkez={[40.9862, 40.5219]} yakinlik={13} yukseklik="560px"
            hazir={setHarita} etiket="Malzeme kaynak haritası" />
        </div>

        <div className="space-y-4">
          <Kart className="p-4">
            <div className="flex items-baseline justify-between gap-2 mb-3">
              <h2 className="text-sm font-semibold text-metin-2">
                Malzeme dağılımı
              </h2>
              {seciliSiniflar.size > 0 && (
                <button onClick={() => setSeciliSiniflar(new Set())}
                  className="text-xs text-metin-3 hover:text-metin !min-h-0">
                  Filtreyi temizle
                </button>
              )}
            </div>

            {dagilim === null ? (
              <p className="text-sm text-metin-3">Yükleniyor…</p>
            ) : dagilim.length === 0 ? (
              <BosDurum
                ikon={<Ikon.Harita boyut={20} />}
                baslik="Doğrulanmış kayıt yok"
                aciklama="Harita yalnızca uzman tarafından doğrulanmış tespitleri gösterir; doğrulanmamış ön tahminler buraya girmez. Bu boşluk veri olmadığı anlamına gelmez — kayıtlar henüz incelenmemiş olabilir."
                aksiyon={erisilebilir('kuyruk')
                  ? (
                    <Buton tur="ikincil" onClick={() => git('kuyruk')}
                      ikon={<Ikon.Kuyruk boyut={15} />}>
                      İnceleme kuyruğuna git
                    </Buton>
                  )
                  : erisilebilir('alanlar') && (
                    <Buton tur="ikincil" onClick={() => git('alanlar')}
                      ikon={<Ikon.Alan boyut={15} />}>
                      Enkaz alanlarına bak
                    </Buton>
                  )}
              />
            ) : (
              <MalzemeDagilimi
                dagilim={dagilim} siniflar={siniflar}
                secili={seciliSiniflar} secildi={filtreDegistir}
              />
            )}

            {gorunen.length > 0 && (
              <p className="text-xs text-metin-4 mt-3 pt-3 border-t border-kenar">
                Gösterilen: <span className="sayisal text-metin-3">
                  {gorunen.reduce((t, d) => t + d.adet, 0)}
                </span> doğrulanmış tespit
                {seciliSiniflar.size > 0 && (
                  <> · haritada <span className="sayisal text-metin-3">
                    {haritadakiAlanSayisi}
                  </span> saha</>
                )}
              </p>
            )}
          </Kart>

          {/* Kapsam uyarısı lejandda YAZILI (ana talimat Bölüm 1.3) */}
          {RAPOR_ALABILIR.has(kullanici?.rol ?? '') && (
            <Kart className="p-4">
              <RaporIndir />
            </Kart>
          )}

          <Kart className="p-4 space-y-4">
            {durum && <KapsamUyarisi metin={durum.kapsam_uyarisi} />}
            {siniflarHam && siniflarHam.kapsanmayan_gruplar.length > 0 && (
              <div className="text-xs border-l-2 border-uyari/60 pl-3 py-1">
                <p className="text-metin-2 font-medium mb-1.5">
                  Kapsanmayan malzeme grupları
                </p>
                <ul className="space-y-1.5 text-metin-4 leading-relaxed">
                  {siniflarHam.kapsanmayan_gruplar.map((g) => (
                    <li key={g.ad}>
                      <span className="text-metin-3 font-medium">{g.ad}</span>
                      {' — '}{g.not}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Kart>
        </div>
      </div>
    </Sayfa>
  )
}
