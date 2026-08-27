import { useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import { Harita, isaretciIkonu } from '../lib/leaflet/Harita'
import {
  Alan, Baslik, BosDurum, Buton, Hata, Kart, OzetSayi, girdiSinifi,
} from '../bilesenler/Temel'
import { Ikon } from '../bilesenler/Ikon'
import { Sayfa } from '../bilesenler/Duzen'
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

  const toplamGoruntu = (alanlar ?? []).reduce((t, a) => t + a.goruntu_sayisi, 0)
  const sinirliErisim = (alanlar ?? []).filter(
    (a) => a.erisim_durumu !== 'acik',
  ).length

  return (
    <Sayfa>
      <Baslik
        ustBaslik="Saha yönetimi"
        baslik="Enkaz alanları"
        aciklama="Rolünüzün görebildiği sahalar listelenir. Yetki kontrolü sunucu tarafında yapılır."
        sag={olusturabilir && !formAcik && (
          <Buton onClick={() => setFormAcik(true)} ikon={<Ikon.Alan boyut={15} />}>
            Yeni alan tanımla
          </Buton>
        )}
      />

      {alanlar !== null && alanlar.length > 0 && (
        <Kart className="mb-6 grid grid-cols-2 sm:grid-cols-3 divide-x divide-kenar">
          <OzetSayi deger={alanlar.length} etiket="Görünen enkaz alanı" />
          <OzetSayi deger={toplamGoruntu} etiket="Yüklenen görüntü" />
          <OzetSayi
            deger={sinirliErisim}
            etiket="Erişimi kısıtlı ya da kapalı"
            ton={sinirliErisim > 0 ? 'uyari' : 'notr'}
          />
        </Kart>
      )}

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
            ikon={<Ikon.Alan boyut={20} />}
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
        <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {alanlar.map((a) => (
            <li key={a.id}>
              <Kart className="p-5 h-full flex flex-col">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-medium leading-snug">{a.ad}</h3>
                  <ErisimRozeti durum={a.erisim_durumu} />
                </div>

                <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2 grow">
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-metin-4">
                      Görüntü
                    </dt>
                    <dd className="text-lg font-medium sayisal">
                      {a.goruntu_sayisi}
                    </dd>
                  </div>
                  <div className="min-w-0">
                    <dt className="text-xs uppercase tracking-wide text-metin-4">
                      Sorumlu
                    </dt>
                    <dd className="text-sm text-metin-2 truncate">
                      {a.sorumlu || '—'}
                    </dd>
                  </div>
                  {a.konum && (
                    <div className="col-span-2">
                      <dt className="text-xs uppercase tracking-wide text-metin-4">
                        Konum
                      </dt>
                      <dd className="text-xs text-metin-3 sayisal">
                        {a.konum.enlem.toFixed(4)}, {a.konum.boylam.toFixed(4)}
                        {a.sinir && ` · ${a.sinir.length - 1} köşeli sınır`}
                      </dd>
                    </div>
                  )}
                </dl>

                <Buton tur="ikincil" className="mt-4 w-full"
                  onClick={() => acildi(a.id)}>
                  Alanı aç
                </Buton>
              </Kart>
            </li>
          ))}
        </ul>
      )}
    </Sayfa>
  )
}

function ErisimRozeti({ durum }: { durum: EnkazAlani['erisim_durumu'] }) {
  const t = {
    acik: { m: 'Erişim açık', s: 'border-olumlu/50 text-olumlu bg-olumlu/10' },
    kisitli: { m: 'Kısıtlı', s: 'border-uyari/50 text-uyari bg-uyari/10' },
    kapali: { m: 'Kapalı', s: 'border-dikkat/50 text-dikkat bg-dikkat/10' },
  }[durum]
  return (
    <span className={`shrink-0 px-2 py-0.5 rounded border text-xs
      font-medium whitespace-nowrap ${t.s}`}>
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
          <Harita merkez={[40.9862, 40.5219]} yakinlik={14} yukseklik="320px"
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
