import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import {
  Baslik, Bilgi, BosDurum, Buton, DogrulamaRozeti, Hata, KapsamUyarisi, Kart,
  OnTahminEtiketi, OzetSayi, SinifEtiketi,
} from '../bilesenler/Temel'
import { Ikon } from '../bilesenler/Ikon'
import { GuvenSkoru } from '../bilesenler/GuvenSkoru'
import { Sayfa } from '../bilesenler/Duzen'
import { CizilemeyenKutuUyarisi, TespitKutulari } from '../bilesenler/TespitKutulari'
import { MiktarKarti } from '../bilesenler/MiktarKarti'
import { IslemGecmisiListesi } from '../bilesenler/IslemGecmisi'
import { TehlikeliKarti } from '../bilesenler/TehlikeliKarti'
import type { Goruntu, Miktar, Olcum, Tespit } from '../types'

const YUKLEYEBILIR = new Set(['yonetici', 'saha', 'belediye'])
const OLCEBILIR = new Set(['yonetici', 'saha', 'uzman'])

// Tehlikeli madde YÖNLENDİRMESİ — teşhis değil (ana talimat Bölüm 1.2).
// api/app/core/permissions.py ile aynı kümeler.
const YONLENDIREBILIR = new Set(['yonetici', 'saha', 'uzman', 'belediye'])
const LAB_GIREBILIR = new Set(['yonetici', 'uzman'])

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
  const tumTespitler = (goruntuler ?? []).flatMap((g) => g.tespitler)
  const toplamTespit = tumTespitler.length
  const dogrulanan = tumTespitler.filter(
    (t) => t.dogrulama_durumu === 'onaylandi' || t.dogrulama_durumu === 'duzeltildi',
  ).length
  const incelemeBekleyen = tumTespitler.filter((t) => t.inceleme_gerekli).length

  return (
    <Sayfa>
      <Buton tur="sessiz" boyut="kucuk" onClick={geri} className="mb-4"
        ikon={<Ikon.Geri boyut={14} />}>
        Alanlara dön
      </Buton>

      <Baslik
        ustBaslik="Enkaz alanı"
        baslik={alanAdi || 'Enkaz alanı'}
        sag={yukleyebilir && (
          <div>
            <input ref={dosyaGirdi} type="file" multiple accept="image/*"
              onChange={(e) => yukle(e.target.files)} className="hidden"
              id="goruntu-girdi" />
            <Buton onClick={() => dosyaGirdi.current?.click()}
              disabled={yukleniyor} ikon={<Ikon.Yukle boyut={15} />}>
              {yukleniyor ? 'İşleniyor…' : 'Görüntü yükle'}
            </Buton>
          </div>
        )}
      />

      {goruntuler !== null && goruntuler.length > 0 && (
        <Kart className="mb-5 grid grid-cols-2 sm:grid-cols-4 divide-x divide-kenar">
          <OzetSayi deger={goruntuler.length} etiket="Görüntü" />
          <OzetSayi deger={toplamTespit} etiket="Tespit" alt="tümü ön tahmin" />
          <OzetSayi deger={dogrulanan} etiket="Doğrulanmış"
            ton={dogrulanan > 0 ? 'vurgu' : 'notr'} />
          <OzetSayi deger={incelemeBekleyen} etiket="Uzman incelemesi gerekli"
            ton={incelemeBekleyen > 0 ? 'uyari' : 'notr'} />
        </Kart>
      )}

      {durum && <div className="mb-4"><KapsamUyarisi metin={durum.kapsam_uyarisi} /></div>}

      {hata && <div className="mb-4"><Hata mesaj={hata} /></div>}

      {sonYukleme && (
        <div className="mb-4">
          <Bilgi>
            Yükleme tamamlandı.{' '}
            {sonYukleme.kuyruk > 0 ? (
              <>Düşük güvenli <strong className="text-metin">
                {sonYukleme.kuyruk}</strong> tespit otomatik olarak uzman
                inceleme kuyruğuna alındı.</>
            ) : (
              <>Uzman incelemesi gerektiren tespit bulunmadı.</>
            )}
          </Bilgi>
        </div>
      )}

      {goruntuler === null ? (
        <p className="text-metin-3 text-sm">Yükleniyor…</p>
      ) : goruntuler.length === 0 ? (
        <Kart>
          <BosDurum
            ikon={<Ikon.Yukle boyut={20} />}
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
              rol={kullanici?.rol ?? ''}
            />
          ))}
        </div>
      )}
    </Sayfa>
  )
}

function GoruntuKarti({ goruntu, siniflar, secili, secildi, olcebilir, rol }: {
  goruntu: Goruntu
  siniflar: Map<string, { renk: string; gorunen_ad: string; malzeme_mi: boolean }>
  secili: number | null
  secildi: (id: number) => void
  olcebilir: boolean
  rol: string
}) {
  return (
    <Kart className="p-4">
      <div className="grid gap-5 lg:grid-cols-[1.45fr_1fr] items-start">
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

        <div className="lg:sticky lg:top-20">
          <div className="flex items-baseline justify-between mb-3">
            <h3 className="text-sm font-semibold text-metin-2">Tespitler</h3>
            <span className="text-xs text-metin-4">
              <span className="sayisal">{goruntu.tespitler.length}</span> kayıt ·
              hepsi ön tahmin
            </span>
          </div>
          <ul className="space-y-2">
            {goruntu.tespitler.map((t) => (
              <li key={t.id}>
                <TespitSatiri
                  tespit={t} siniflar={siniflar}
                  acik={secili === t.id}
                  ac={() => secildi(t.id)}
                  olcebilir={olcebilir}
                  rol={rol}
                />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Kart>
  )
}

function TespitSatiri({ tespit, siniflar, acik, ac, olcebilir, rol }: {
  tespit: Tespit
  siniflar: Map<string, { renk: string; gorunen_ad: string; malzeme_mi: boolean }>
  acik: boolean
  ac: () => void
  olcebilir: boolean
  rol: string
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
    <div className={`border rounded-md ${acik ? 'border-marka' : 'border-kenar'}`}>
      <button onClick={ac} className="w-full text-left px-3 py-3 flex items-start gap-2.5">
        <span className="grow min-w-0">
          <span className="flex items-center gap-2 flex-wrap">
            <span className="font-medium">
              <SinifEtiketi renk={tanim?.renk ?? '#6b7280'}
                ad={tanim?.gorunen_ad ?? gosterilenSinif} />
            </span>
            {/* Güven skoru yüzde olarak, YUVARLANMADAN (Bölüm 9.2) */}
            <GuvenSkoru skor={tespit.guven_skoru}
              incelemeGerekli={tespit.inceleme_gerekli} boyut="kucuk" />
            <OnTahminEtiketi />
            <DogrulamaRozeti durum={tespit.dogrulama_durumu} boyut="kucuk" />
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

          {/* Teşhis değil, yönlendirme kaydı (ana talimat Bölüm 1.2) */}
          <TehlikeliKarti
            tespitId={tespit.id}
            yonlendirebilir={YONLENDIREBILIR.has(rol)}
            labGirebilir={LAB_GIREBILIR.has(rol)}
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
