import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import {
  BosDurum, Buton, DogrulamaRozeti, Hata, KapsamUyarisi, Kart, OnTahminEtiketi,
} from '../bilesenler/Temel'
import { CizilemeyenKutuUyarisi, TespitKutulari } from '../bilesenler/TespitKutulari'
import { MiktarKarti } from '../bilesenler/MiktarKarti'
import { IslemGecmisiListesi } from '../bilesenler/IslemGecmisi'
import type { Goruntu, Miktar, Olcum, Tespit } from '../types'

const YUKLEYEBILIR = new Set(['yonetici', 'saha', 'belediye'])
const OLCEBILIR = new Set(['yonetici', 'saha', 'uzman'])

export function AlanDetay({ alanId, geri }: { alanId: number; geri: () => void }) {
  const { kullanici, durum, siniflar } = useDurum()
  const [goruntuler, setGoruntuler] = useState<Goruntu[] | null>(null)
  const [alanAdi, setAlanAdi] = useState('')
  const [seciliTespit, setSeciliTespit] = useState<number | null>(null)
  const [hata, setHata] = useState('')
  const [yukleniyor, setYukleniyor] = useState(false)
  const [sonYukleme, setSonYukleme] = useState<{ kuyruk: number } | null>(null)
  const dosyaGirdi = useRef<HTMLInputElement>(null)

  const yenile = useCallback(() => {
    api.alanGoruntuleri(alanId).then(setGoruntuler).catch((h) => setHata(h.message))
  }, [alanId])

  useEffect(() => {
    api.alan(alanId).then((a) => setAlanAdi(a.ad)).catch(() => {})
    yenile()
  }, [alanId, yenile])

  async function yukle(dosyalar: FileList | null) {
    if (!dosyalar?.length) return
    setHata(''); setYukleniyor(true); setSonYukleme(null)
    try {
      const s = await api.goruntuYukle(alanId, Array.from(dosyalar))
      setSonYukleme({ kuyruk: s.inceleme_kuyruguna_dusen })
      yenile()
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'Yükleme başarısız')
    } finally {
      setYukleniyor(false)
      if (dosyaGirdi.current) dosyaGirdi.current.value = ''
    }
  }

  const yukleyebilir = YUKLEYEBILIR.has(kullanici?.rol ?? '')

  return (
    <div className="max-w-6xl mx-auto p-6">
      <Buton tur="sessiz" onClick={geri} className="mb-4 text-sm">← Alanlara dön</Buton>

      <div className="flex items-start justify-between gap-4 mb-2">
        <h2 className="text-xl font-semibold">{alanAdi || 'Enkaz alanı'}</h2>
        {yukleyebilir && (
          <div>
            <input ref={dosyaGirdi} type="file" multiple accept="image/*"
              onChange={(e) => yukle(e.target.files)} className="hidden"
              id="goruntu-girdi" />
            <Buton onClick={() => dosyaGirdi.current?.click()} disabled={yukleniyor}>
              {yukleniyor ? 'İşleniyor…' : 'Görüntü yükle'}
            </Buton>
          </div>
        )}
      </div>

      {durum && <div className="mb-4"><KapsamUyarisi metin={durum.kapsam_uyarisi} /></div>}

      {hata && <div className="mb-4"><Hata mesaj={hata} /></div>}

      {sonYukleme && (
        <p role="status" className="mb-4 text-sm bg-vurgu/10 border border-vurgu/30
          rounded-md px-3 py-2">
          Yükleme tamamlandı.{' '}
          {sonYukleme.kuyruk > 0 ? (
            <>Düşük güvenli <strong>{sonYukleme.kuyruk}</strong> tespit otomatik
              olarak uzman inceleme kuyruğuna alındı.</>
          ) : (
            <>Uzman incelemesi gerektiren tespit bulunmadı.</>
          )}
        </p>
      )}

      {goruntuler === null ? (
        <p className="text-metin-3 text-sm">Yükleniyor…</p>
      ) : goruntuler.length === 0 ? (
        <Kart>
          <BosDurum
            baslik="Bu alana görüntü yükleyerek başlayın"
            aciklama={yukleyebilir
              ? 'Yüklenen görüntüler otomatik olarak sınıflandırılır ve sonuçlar ön tahmin olarak listelenir.'
              : 'Bu alanda henüz görüntü yok. Görüntü yükleme yetkisi saha personeli ve belediye yetkilisindedir.'}
            aksiyon={yukleyebilir && (
              <Buton onClick={() => dosyaGirdi.current?.click()}>Görüntü yükle</Buton>
            )}
          />
        </Kart>
      ) : (
        <div className="space-y-6">
          {goruntuler.map((g) => (
            <GoruntuKarti
              key={g.id} goruntu={g} siniflar={siniflar}
              secili={seciliTespit} secildi={setSeciliTespit}
              olcebilir={OLCEBILIR.has(kullanici?.rol ?? '')}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function GoruntuKarti({ goruntu, siniflar, secili, secildi, olcebilir }: {
  goruntu: Goruntu
  siniflar: Map<string, { renk: string; gorunen_ad: string; malzeme_mi: boolean }>
  secili: number | null
  secildi: (id: number) => void
  olcebilir: boolean
}) {
  return (
    <Kart className="p-4">
      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div>
          <TespitKutulari
            gorselUrl={api.gorselUrl(goruntu.dosya_yolu)}
            tespitler={goruntu.tespitler}
            goruntuGenislik={goruntu.genislik}
            goruntuYukseklik={goruntu.yukseklik}
            siniflar={siniflar as never}
            secili={secili}
            secildi={secildi}
          />
          <CizilemeyenKutuUyarisi tespitler={goruntu.tespitler} />
        </div>

        <div>
          <h3 className="text-sm font-semibold text-metin-2 mb-3">
            Tespitler ({goruntu.tespitler.length})
          </h3>
          <ul className="space-y-2">
            {goruntu.tespitler.map((t) => (
              <li key={t.id}>
                <TespitSatiri
                  tespit={t} siniflar={siniflar}
                  acik={secili === t.id}
                  ac={() => secildi(t.id)}
                  olcebilir={olcebilir}
                />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Kart>
  )
}

function TespitSatiri({ tespit, siniflar, acik, ac, olcebilir }: {
  tespit: Tespit
  siniflar: Map<string, { renk: string; gorunen_ad: string; malzeme_mi: boolean }>
  acik: boolean
  ac: () => void
  olcebilir: boolean
}) {
  const [miktar, setMiktar] = useState<Miktar | null>(null)
  const [olcumler, setOlcumler] = useState<Olcum[]>([])

  const yenile = useCallback(() => {
    api.miktar(tespit.id).then(setMiktar).catch(() => {})
    api.olcumler(tespit.id).then(setOlcumler).catch(() => {})
  }, [tespit.id])

  useEffect(() => { if (acik) yenile() }, [acik, yenile])

  const gosterilenSinif = tespit.duzeltilen_sinif ?? tespit.sinif
  const tanim = siniflar.get(gosterilenSinif)

  return (
    <div className={`border rounded-md ${acik ? 'border-vurgu' : 'border-kenar'}`}>
      <button onClick={ac} className="w-full text-left px-3 py-2.5 flex items-start gap-2.5">
        <span aria-hidden className="mt-1 w-3 h-3 rounded-sm shrink-0"
          style={{ background: tanim?.renk ?? '#8593a1' }} />
        <span className="grow min-w-0">
          <span className="flex items-center gap-2 flex-wrap">
            <span className="font-medium">{tanim?.gorunen_ad ?? gosterilenSinif}</span>
            {/* Güven skoru sayı olarak, YUVARLANMADAN (Bölüm 9.2) */}
            <span className="text-sm text-metin-2 tabular-nums">{tespit.guven_skoru}</span>
            <OnTahminEtiketi />
            <DogrulamaRozeti durum={tespit.dogrulama_durumu} />
          </span>
          {tespit.duzeltilen_sinif && (
            <span className="block text-xs text-metin-3 mt-1">
              Uzman düzeltmesi: <s>{siniflar.get(tespit.sinif)?.gorunen_ad ?? tespit.sinif}</s>
              {' → '}{tanim?.gorunen_ad ?? tespit.duzeltilen_sinif}
            </span>
          )}
          {tespit.inceleme_gerekli && (
            <span className="block text-xs text-uyari mt-1">Uzman incelemesi gerekli</span>
          )}
          {tanim && !tanim.malzeme_mi && (
            <span className="block text-xs text-metin-3 mt-1">
              Atık malzeme değil — miktar ve haritaya dahil edilmez
            </span>
          )}
        </span>
      </button>

      {acik && miktar && (
        <div className="px-3 pb-3 space-y-3">
          <MiktarKarti
            miktar={miktar} olcumler={olcumler}
            olcumEklenebilir={olcebilir && (tanim?.malzeme_mi ?? true)}
            olcumEklendi={yenile}
          />

          {/* İzlenebilirlik arayüzde de görünür (ana talimat Bölüm 4.2) */}
          <div className="border border-kenar rounded-lg p-4 bg-yuzey-2/40">
            <IslemGecmisiListesi
              kayitTipi="tespit" kayitId={tespit.id}
              baslik="Bu tespitin geçmişi" limit={10} kompakt
            />
          </div>
        </div>
      )}
    </div>
  )
}
