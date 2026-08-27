import { useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import { Harita, isaretciIkonu } from '../lib/leaflet/Harita'
import { BosDurum, Hata, KapsamUyarisi, Kart } from '../bilesenler/Temel'
import type { EnkazAlani } from '../types'
import L from 'leaflet'

/**
 * Malzeme Kaynak Haritası.
 *
 * Yalnızca DOĞRULANMIŞ kayıtlar gösterilir — filtre veri katmanındadır
 * (ana talimat Bölüm 1.4). Lejandda kapsam uyarısı YAZILI olarak bulunur
 * (Bölüm 1.3).
 */
export function HaritaSayfasi() {
  const { durum, siniflar, siniflarHam } = useDurum()
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
    alanlar.forEach((a) => {
      if (a.sinir && a.sinir.length >= 3) {
        L.polygon(a.sinir.map((n) => [n.enlem, n.boylam] as [number, number]), {
          color: '#4da3ff', weight: 2, fillOpacity: 0.08,
        }).addTo(katman).bindPopup(a.ad)
      }
      if (a.konum) {
        noktalar.push([a.konum.enlem, a.konum.boylam])
        L.marker([a.konum.enlem, a.konum.boylam], { icon: isaretciIkonu('#4da3ff') })
          .addTo(katman)
          .bindPopup(`<strong>${a.ad}</strong><br>${a.goruntu_sayisi} görüntü`)
      }
    })
    if (noktalar.length > 0 && harita) {
      harita.fitBounds(L.latLngBounds(noktalar).pad(0.3))
    }
  }, [alanlar, katman, harita])

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

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h2 className="text-xl font-semibold">Malzeme Kaynak Haritası</h2>
      <p className="text-sm text-metin-3 mt-0.5 mb-4">{not}</p>

      {hata && <div className="mb-4"><Hata mesaj={hata} /></div>}

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_280px]">
        <Harita merkez={[40.9862, 40.5219]} yakinlik={13} yukseklik="520px"
          hazir={setHarita} etiket="Malzeme kaynak haritası" />

        <div className="space-y-4">
          <Kart className="p-4">
            <h3 className="text-sm font-semibold text-metin-2 mb-3">
              Malzeme türü filtresi
            </h3>
            {dagilim === null ? (
              <p className="text-sm text-metin-3">Yükleniyor…</p>
            ) : dagilim.length === 0 ? (
              <BosDurum
                baslik="Doğrulanmış kayıt yok"
                aciklama="Haritada yalnızca uzman tarafından doğrulanmış tespitler gösterilir. Önce inceleme kuyruğundaki kayıtları doğrulayın."
              />
            ) : (
              <ul className="space-y-1.5">
                {dagilim.map((d) => {
                  const t = siniflar.get(d.sinif)
                  const secili = seciliSiniflar.size === 0 || seciliSiniflar.has(d.sinif)
                  return (
                    <li key={d.sinif}>
                      <button onClick={() => filtreDegistir(d.sinif)}
                        aria-pressed={seciliSiniflar.has(d.sinif)}
                        className={`w-full flex items-center gap-2.5 px-2 py-1.5 rounded
                          text-left ${secili ? '' : 'opacity-40'} hover:bg-yuzey-2`}>
                        <span aria-hidden className="w-3 h-3 rounded-sm shrink-0"
                          style={{ background: t?.renk ?? '#8593a1' }} />
                        <span className="grow text-sm">{t?.gorunen_ad ?? d.sinif}</span>
                        <span className="text-sm text-metin-2 tabular-nums">{d.adet}</span>
                      </button>
                    </li>
                  )
                })}
              </ul>
            )}
            {gorunen.length > 0 && (
              <p className="text-xs text-metin-3 mt-3 pt-3 border-t border-kenar">
                Gösterilen: {gorunen.reduce((t, d) => t + d.adet, 0)} doğrulanmış tespit
              </p>
            )}
          </Kart>

          {/* Kapsam uyarısı lejandda YAZILI (ana talimat Bölüm 1.3) */}
          <Kart className="p-4 space-y-3">
            {durum && <KapsamUyarisi metin={durum.kapsam_uyarisi} />}
            {siniflarHam && siniflarHam.kapsanmayan_gruplar.length > 0 && (
              <div className="text-xs text-metin-3 border-l-2 border-uyari pl-3 py-1">
                <p className="text-metin-2 font-medium mb-1">Kapsanmayan malzeme grupları</p>
                {siniflarHam.kapsanmayan_gruplar.map((g) => (
                  <p key={g.ad}>
                    <span className="text-metin-2">{g.ad}</span> — {g.not}
                  </p>
                ))}
              </div>
            )}
          </Kart>
        </div>
      </div>
    </div>
  )
}
