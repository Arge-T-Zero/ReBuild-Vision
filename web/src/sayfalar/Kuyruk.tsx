import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import {
  Baslik, BosDurum, Buton, Hata, Kart, OnTahminEtiketi, SinifEtiketi,
  girdiSinifi,
} from '../bilesenler/Temel'
import { Ikon } from '../bilesenler/Ikon'
import { GuvenSkoru } from '../bilesenler/GuvenSkoru'
import { Sayfa } from '../bilesenler/Duzen'
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
    <Sayfa dar>
      <Baslik
        ustBaslik="Doğrulama"
        baslik="Uzman inceleme kuyruğu"
        aciklama="Model güveni düşük olan tespitler bu kuyruğa otomatik olarak alınır; sizin eklemeniz gerekmez."
        sag={kayitlar && kayitlar.length > 0 && (
          <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-md
            bg-uyari/10 border border-uyari/40 text-uyari text-sm font-medium">
            <Ikon.Kuyruk boyut={15} />
            {kayitlar.length} kayıt bekliyor
          </span>
        )}
      />

      {hata && <div className="mb-4"><Hata mesaj={hata} /></div>}

      {kayitlar === null ? (
        <p className="text-metin-3 text-sm">Yükleniyor…</p>
      ) : kayitlar.length === 0 ? (
        <Kart>
          <BosDurum
            ikon={<Ikon.Onayla boyut={20} />}
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
    </Sayfa>
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
        <div className="grow min-w-0">
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="font-medium">
              <SinifEtiketi renk={tanim?.renk ?? '#6b7280'}
                ad={tanim?.gorunen_ad ?? tespit.sinif} />
            </span>
            <OnTahminEtiketi />
          </div>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-xs text-metin-4 uppercase tracking-wide">
              Model güveni
            </span>
            <GuvenSkoru skor={tespit.guven_skoru} incelemeGerekli />
          </div>
          <p className="flex items-center gap-1.5 text-xs text-uyari mt-2">
            <Ikon.Uyari boyut={13} /> Uzman incelemesi gerekli
          </p>
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
          <Buton disabled={bekliyor} onClick={() => karar('onaylandi')}
            ikon={<Ikon.Onayla boyut={15} />}>
            Onayla
          </Buton>
          <Buton tur="ikincil" disabled={bekliyor}
            onClick={() => setDuzeltmeAcik(true)} ikon={<Ikon.Duzelt boyut={15} />}>
            Düzelt
          </Buton>
          <Buton tur="ikincil" disabled={bekliyor} onClick={() => karar('belirsiz')}
            ikon={<Ikon.Belirsiz boyut={15} />}>
            Belirsiz olarak işaretle
          </Buton>
        </div>
      )}

      {hata && <div className="mt-3"><Hata mesaj={hata} /></div>}
    </Kart>
  )
}
