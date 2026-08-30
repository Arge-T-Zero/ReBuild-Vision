import { useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import { Harita, isaretciIkonu } from '../lib/leaflet/Harita'
import {
  Alan, Baslik, BosDurum, Buton, Hata, Kart, OzetSayi, girdiSinifi,
} from '../bilesenler/Temel'
import { Ikon } from '../bilesenler/Ikon'
import { SahaKarti } from '../bilesenler/SahaKarti'
import { Sayfa } from '../bilesenler/Duzen'
import type { EnkazAlani, Nokta } from '../types'
import L from 'leaflet'
import { sayfaGorevi } from '../roller'

const OLUSTURABILIR = new Set(['yonetici', 'belediye', 'afad'])

export function Alanlar({ acildi }: { acildi: (id: number) => void }) {
  const { kullanici, siniflar } = useDurum()
  const [alanlar, setAlanlar] = useState<EnkazAlani[] | null>(null)
  const [formAcik, setFormAcik] = useState(false)
  const [hata, setHata] = useState('')

  // Hata durumunda liste boş diziye çekilir. Önceden `null` kalıyordu ve
  // `null` "yükleniyor" anlamına geldiği için ekranda AYNI ANDA hem
  // "Sunucu hatası" hem "Yükleniyor…" görünüp orada kalıyordu.
  const yenile = () => {
    setHata('')
    return api.alanlar()
      .then(setAlanlar)
      .catch((h) => { setHata(h.message); setAlanlar([]) })
  }

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
        gorev={sayfaGorevi(kullanici?.rol ?? null, 'alanlar')}
        aciklama="Rolünüzün görebildiği sahalar listelenir. Yetki kontrolü sunucu tarafında yapılır."
        sag={olusturabilir && !formAcik && (
          <Buton onClick={() => setFormAcik(true)} ikon={<Ikon.Alan boyut={15} />}>
            Yeni alan tanımla
          </Buton>
        )}
      />

      {alanlar !== null && alanlar.length > 0 && (
        <Kart className="mb-6 grid grid-cols-3 divide-x divide-kenar">
          <OzetSayi deger={alanlar.length} etiket="Görünen enkaz alanı" />
          <OzetSayi deger={toplamGoruntu} etiket="Yüklenen görüntü" />
          <OzetSayi
            deger={sinirliErisim}
            etiket="Erişimi kısıtlı ya da kapalı"
            ton={sinirliErisim > 0 ? 'uyari' : 'notr'}
          />
        </Kart>
      )}

      {hata && (
        <div className="mb-4">
          <Hata mesaj={hata} />
          <Buton tur="ikincil" className="mt-3" onClick={yenile}>
            Yeniden dene
          </Buton>
        </div>
      )}

      {formAcik && (
        <AlanFormu
          kapat={() => setFormAcik(false)}
          olusturuldu={() => { setFormAcik(false); yenile() }}
        />
      )}

      {alanlar === null ? (
        <p className="text-metin-3 text-sm">Yükleniyor…</p>
      ) : hata ? null : alanlar.length === 0 ? (
        <Kart>
          <BosDurum
            ikon={<Ikon.Alan boyut={20} />}
            /* Başlık role göre değişir: alan tanımlayamayan bir rol için
               "henüz tanımlanmadı" YANLIŞTIR — sistemde alan olabilir,
               bu role atanmamıştır. Alt açıklama zaten doğruyu söylüyordu;
               başlık onu yalanlıyordu. */
            baslik={olusturabilir
              ? 'Henüz enkaz alanı tanımlanmadı'
              : 'Size atanmış saha yok'}
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
              <SahaKarti alan={a} siniflar={siniflar} acildi={acildi} />
            </li>
          ))}
        </ul>
      )}
    </Sayfa>
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
      L.marker([konum.enlem, konum.boylam], {
        icon: isaretciIkonu('#4da3ff'),
        title: 'Seçilen merkez konum',
        alt: 'Seçilen merkez konum',
      }).addTo(katman)
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
      <h2 className="font-medium mb-4">Yeni enkaz alanı</h2>
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
