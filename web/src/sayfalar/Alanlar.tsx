import { useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import { Harita, isaretciIkonu } from '../lib/leaflet/Harita'
import { Alan, BosDurum, Buton, Hata, Kart, girdiSinifi } from '../bilesenler/Temel'
import type { EnkazAlani, Nokta } from '../types'
import L from 'leaflet'

const OLUSTURABILIR = new Set(['yonetici', 'belediye', 'afad'])

export function Alanlar({ acildi }: { acildi: (id: number) => void }) {
  const { kullanici } = useDurum()
  const [alanlar, setAlanlar] = useState<EnkazAlani[] | null>(null)
  const [formAcik, setFormAcik] = useState(false)
  const [hata, setHata] = useState('')

  const yenile = () =>
    api.alanlar().then(setAlanlar).catch((h) => setHata(h.message))

  useEffect(() => { yenile() }, [])

  const olusturabilir = OLUSTURABILIR.has(kullanici?.rol ?? '')

  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6 gap-4">
        <div>
          <h2 className="text-xl font-semibold">Enkaz alanları</h2>
          <p className="text-sm text-metin-3 mt-0.5">
            Rolünüzün görebildiği sahalar listelenir.
          </p>
        </div>
        {olusturabilir && !formAcik && (
          <Buton onClick={() => setFormAcik(true)}>Yeni alan tanımla</Buton>
        )}
      </div>

      {hata && <div className="mb-4"><Hata mesaj={hata} /></div>}

      {formAcik && (
        <AlanFormu
          kapat={() => setFormAcik(false)}
          olusturuldu={() => { setFormAcik(false); yenile() }}
        />
      )}

      {alanlar === null ? (
        <p className="text-metin-3 text-sm">Yükleniyor…</p>
      ) : alanlar.length === 0 ? (
        <Kart>
          <BosDurum
            baslik="Henüz enkaz alanı tanımlanmadı"
            aciklama={olusturabilir
              ? 'Bir alan tanımlayarak başlayın; sonra bu alana görüntü yükleyebilirsiniz.'
              : 'Size atanmış bir saha bulunmuyor. Yetkili birimin alan tanımlaması gerekiyor.'}
            aksiyon={olusturabilir && (
              <Buton onClick={() => setFormAcik(true)}>Yeni alan tanımla</Buton>
            )}
          />
        </Kart>
      ) : (
        <ul className="grid gap-3 sm:grid-cols-2">
          {alanlar.map((a) => (
            <li key={a.id}>
              <Kart className="p-4 h-full flex flex-col">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-medium">{a.ad}</h3>
                  <ErisimRozeti durum={a.erisim_durumu} />
                </div>
                <dl className="text-xs text-metin-3 mt-2 space-y-0.5 grow">
                  {a.sorumlu && <div>Sorumlu: {a.sorumlu}</div>}
                  <div>{a.goruntu_sayisi} görüntü</div>
                  {a.konum && (
                    <div className="tabular-nums">
                      {a.konum.enlem.toFixed(4)}, {a.konum.boylam.toFixed(4)}
                    </div>
                  )}
                </dl>
                <Buton tur="ikincil" className="mt-3 w-full"
                  onClick={() => acildi(a.id)}>
                  Alanı aç
                </Buton>
              </Kart>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function ErisimRozeti({ durum }: { durum: EnkazAlani['erisim_durumu'] }) {
  const t = {
    acik: { m: 'Erişim açık', s: 'border-olumlu text-olumlu' },
    kisitli: { m: 'Erişim kısıtlı', s: 'border-uyari text-uyari' },
    kapali: { m: 'Erişim kapalı', s: 'border-dikkat text-dikkat' },
  }[durum]
  return (
    <span className={`shrink-0 px-2 py-0.5 rounded border text-[11px] ${t.s}`}>
      {t.m}
    </span>
  )
}

function AlanFormu({ kapat, olusturuldu }: {
  kapat: () => void; olusturuldu: () => void
}) {
  const [ad, setAd] = useState('')
  const [sorumlu, setSorumlu] = useState('')
  const [erisim, setErisim] = useState<'acik' | 'kisitli' | 'kapali'>('acik')
  const [konum, setKonum] = useState<Nokta | null>(null)
  const [sinir, setSinir] = useState<Nokta[]>([])
  const [mod, setMod] = useState<'konum' | 'sinir'>('konum')
  const [hata, setHata] = useState('')
  const [bekliyor, setBekliyor] = useState(false)
  const [harita, setHarita] = useState<L.Map | null>(null)
  const [katman] = useState(() => L.layerGroup())

  useEffect(() => {
    if (!harita) return
    katman.addTo(harita)
    return () => { katman.remove() }
  }, [harita, katman])

  useEffect(() => {
    katman.clearLayers()
    if (konum) {
      L.marker([konum.enlem, konum.boylam], { icon: isaretciIkonu('#4da3ff') })
        .addTo(katman)
    }
    if (sinir.length >= 2) {
      L.polygon(sinir.map((n) => [n.enlem, n.boylam] as [number, number]), {
        color: '#ffb020', weight: 2, fillOpacity: 0.12,
      }).addTo(katman)
    }
    sinir.forEach((n) => {
      L.circleMarker([n.enlem, n.boylam], {
        radius: 5, color: '#ffb020', fillColor: '#ffb020', fillOpacity: 1,
      }).addTo(katman)
    })
  }, [konum, sinir, katman])

  function tiklandi(enlem: number, boylam: number) {
    if (mod === 'konum') setKonum({ enlem, boylam })
    else setSinir((s) => [...s, { enlem, boylam }])
  }

  async function gonder(e: React.FormEvent) {
    e.preventDefault()
    setHata('')
    if (sinir.length > 0 && sinir.length < 3) {
      setHata('Sınır poligonu için en az 3 nokta gerekir; ya tamamlayın ya temizleyin')
      return
    }
    setBekliyor(true)
    try {
      await api.alanOlustur({
        ad, sorumlu: sorumlu || null, erisim_durumu: erisim,
        konum, sinir: sinir.length >= 3 ? sinir : null,
      })
      olusturuldu()
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'Alan oluşturulamadı')
    } finally {
      setBekliyor(false)
    }
  }

  return (
    <Kart className="p-5 mb-6">
      <h3 className="font-medium mb-4">Yeni enkaz alanı</h3>
      <form onSubmit={gonder} className="grid gap-4 md:grid-cols-2">
        <div className="space-y-4">
          <Alan etiket="Alan adı">
            <input value={ad} onChange={(e) => setAd(e.target.value)}
              className={girdiSinifi} required minLength={2} />
          </Alan>
          <Alan etiket="Sorumlu" ipucu="İsteğe bağlı">
            <input value={sorumlu} onChange={(e) => setSorumlu(e.target.value)}
              className={girdiSinifi} />
          </Alan>
          <Alan etiket="Erişim durumu">
            <select value={erisim} onChange={(e) => setErisim(e.target.value as typeof erisim)}
              className={girdiSinifi}>
              <option value="acik">Açık</option>
              <option value="kisitli">Kısıtlı</option>
              <option value="kapali">Kapalı</option>
            </select>
          </Alan>
        </div>

        <div className="space-y-2">
          <div className="flex gap-2">
            <Buton type="button" tur={mod === 'konum' ? 'birincil' : 'ikincil'}
              className="text-sm flex-1" onClick={() => setMod('konum')}>
              Konum işaretle
            </Buton>
            <Buton type="button" tur={mod === 'sinir' ? 'birincil' : 'ikincil'}
              className="text-sm flex-1" onClick={() => setMod('sinir')}>
              Sınır çiz ({sinir.length})
            </Buton>
          </div>
          <Harita merkez={[40.9862, 40.5219]} yakinlik={14} yukseklik="300px"
            hazir={setHarita} tiklandi={tiklandi}
            etiket="Enkaz alanı konum ve sınır seçimi" />
          <p className="text-xs text-metin-3">
            {mod === 'konum'
              ? 'Haritaya tıklayarak alanın merkez konumunu işaretleyin.'
              : 'Haritaya sırayla tıklayarak sınır köşelerini ekleyin (en az 3).'}
          </p>
          {sinir.length > 0 && (
            <Buton type="button" tur="sessiz" className="text-sm"
              onClick={() => setSinir([])}>Sınırı temizle</Buton>
          )}
        </div>

        <div className="md:col-span-2 space-y-3">
          {hata && <Hata mesaj={hata} />}
          <div className="flex gap-2">
            <Buton type="submit" disabled={bekliyor}>
              {bekliyor ? 'Kaydediliyor…' : 'Alanı kaydet'}
            </Buton>
            <Buton type="button" tur="sessiz" onClick={kapat}>Vazgeç</Buton>
          </div>
        </div>
      </form>
    </Kart>
  )
}
