import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import {
  BosDurum, Buton, Hata, Kart, OnTahminEtiketi, girdiSinifi,
} from '../bilesenler/Temel'
import type { Tespit } from '../types'

/**
 * Uzman doğrulama kuyruğu.
 *
 * Düşük güvenli tespitler buraya OTOMATİK düşer — kullanıcının kuyruğa
 * ekleme yapması gerekmez (ana talimat Bölüm 7.3). Final demosunun
 * 4. ve 5. adımı.
 */
export function Kuyruk() {
  const { siniflar, siniflarHam } = useDurum()
  const [kayitlar, setKayitlar] = useState<Tespit[] | null>(null)
  const [hata, setHata] = useState('')

  const yenile = useCallback(() => {
    api.kuyruk().then(setKayitlar).catch((h) => setHata(h.message))
  }, [])

  useEffect(() => { yenile() }, [yenile])

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h2 className="text-xl font-semibold">Uzman inceleme kuyruğu</h2>
      <p className="text-sm text-metin-3 mt-0.5 mb-6">
        Model güveni düşük olan tespitler bu kuyruğa otomatik olarak alınır.
      </p>

      {hata && <div className="mb-4"><Hata mesaj={hata} /></div>}

      {kayitlar === null ? (
        <p className="text-metin-3 text-sm">Yükleniyor…</p>
      ) : kayitlar.length === 0 ? (
        <Kart>
          <BosDurum
            baslik="İnceleme bekleyen tespit yok"
            aciklama="Düşük güvenli bir tespit oluştuğunda burada otomatik olarak görünecektir."
          />
        </Kart>
      ) : (
        <ul className="space-y-3">
          {kayitlar.map((t) => (
            <li key={t.id}>
              <KuyrukSatiri
                tespit={t} siniflar={siniflar}
                secenekler={siniflarHam?.siniflar ?? []}
                tamamlandi={yenile}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function KuyrukSatiri({ tespit, siniflar, secenekler, tamamlandi }: {
  tespit: Tespit
  siniflar: Map<string, { gorunen_ad: string; renk: string }>
  secenekler: { ad: string; gorunen_ad: string }[]
  tamamlandi: () => void
}) {
  const [duzeltmeAcik, setDuzeltmeAcik] = useState(false)
  const [yeniSinif, setYeniSinif] = useState('')
  const [hata, setHata] = useState('')
  const [bekliyor, setBekliyor] = useState(false)

  async function karar(durum: string, duzeltilen?: string) {
    setHata(''); setBekliyor(true)
    try {
      await api.dogrula(tespit.id, durum, duzeltilen)
      tamamlandi()
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'Doğrulama kaydedilemedi')
      setBekliyor(false)
    }
  }

  const tanim = siniflar.get(tespit.sinif)

  return (
    <Kart className="p-4">
      <div className="flex items-start gap-3">
        <span aria-hidden className="mt-1 w-3 h-3 rounded-sm shrink-0"
          style={{ background: tanim?.renk ?? '#8593a1' }} />
        <div className="grow min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium">{tanim?.gorunen_ad ?? tespit.sinif}</span>
            <span className="text-sm text-metin-2 tabular-nums">
              güven {tespit.guven_skoru}
            </span>
            <OnTahminEtiketi />
          </div>
          <p className="text-xs text-uyari mt-1">Uzman incelemesi gerekli</p>
        </div>
      </div>

      {duzeltmeAcik ? (
        <div className="mt-4 space-y-3">
          <select value={yeniSinif} onChange={(e) => setYeniSinif(e.target.value)}
            className={girdiSinifi} aria-label="Doğru malzeme sınıfı">
            <option value="">Doğru sınıfı seçin…</option>
            {secenekler.map((s) => (
              <option key={s.ad} value={s.ad}>{s.gorunen_ad}</option>
            ))}
          </select>
          <div className="flex gap-2">
            <Buton disabled={!yeniSinif || bekliyor}
              onClick={() => karar('duzeltildi', yeniSinif)}>
              Düzeltmeyi kaydet
            </Buton>
            <Buton tur="sessiz" onClick={() => setDuzeltmeAcik(false)}>Vazgeç</Buton>
          </div>
        </div>
      ) : (
        /* Üç aksiyon: onayla, düzelt, belirsiz. 'reddet' YOK (K-004). */
        <div className="mt-4 flex gap-2 flex-wrap">
          <Buton disabled={bekliyor} onClick={() => karar('onaylandi')}>
            Onayla
          </Buton>
          <Buton tur="ikincil" disabled={bekliyor} onClick={() => setDuzeltmeAcik(true)}>
            Düzelt
          </Buton>
          <Buton tur="ikincil" disabled={bekliyor} onClick={() => karar('belirsiz')}>
            Belirsiz olarak işaretle
          </Buton>
        </div>
      )}

      {hata && <div className="mt-3"><Hata mesaj={hata} /></div>}
    </Kart>
  )
}
