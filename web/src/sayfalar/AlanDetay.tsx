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
import { RaporIndir } from '../bilesenler/RaporIndir'
import { TehlikeliKarti } from '../bilesenler/TehlikeliKarti'
import type { EnkazAlani, Goruntu, Miktar, Olcum, Tespit } from '../types'

const YUKLEYEBILIR = new Set(['yonetici', 'saha', 'belediye'])
// api/app/core/permissions.py RAPOR_ALABILIR ile aynı küme.
const RAPOR_ALABILIR = new Set(['yonetici', 'belediye', 'afad'])
const OLCEBILIR = new Set(['yonetici', 'saha', 'uzman'])

// Tehlikeli madde YÖNLENDİRMESİ — teşhis değil (ana talimat Bölüm 1.2).
// api/app/core/permissions.py ile aynı kümeler.
const YONLENDIREBILIR = new Set(['yonetici', 'saha', 'uzman', 'belediye'])
const LAB_GIREBILIR = new Set(['yonetici', 'uzman'])

export function AlanDetay({ alanId, geri }: { alanId: number; geri: () => void }) {
  const { kullanici, durum, siniflar } = useDurum()
  const [goruntuler, setGoruntuler] = useState<Goruntu[] | null>(null)
  // Alanın TAMAMI tutulur. Önceden yalnızca `ad` alınıyor, gelen kaydın
  // geri kalanı atılıyordu: erişim durumu, sorumlu ve koordinat listedeki
  // kartta görünüp alanın kendi sayfasında kayboluyordu. Bir sahaya
  // gidecek ekibin ilk soracağı şey ("girilebiliyor mu, sorumlusu kim")
  // tam da orada eksikti.
  const [alan, setAlan] = useState<EnkazAlani | null>(null)
  const [seciliTespit, setSeciliTespit] = useState<number | null>(null)
  const [hata, setHata] = useState('')
  const [yukleniyor, setYukleniyor] = useState(false)
  const [sonYukleme, setSonYukleme] = useState<{ kuyruk: number } | null>(null)
  const dosyaGirdi = useRef<HTMLInputElement>(null)

  const yenile = useCallback(() => {
    api.alanGoruntuleri(alanId).then(setGoruntuler).catch((h) => setHata(h.message))
  }, [alanId])

  useEffect(() => {
    api.alan(alanId).then(setAlan).catch(() => {})
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
        baslik={alan?.ad || 'Enkaz alanı'}
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

      {alan && <AlanKunyesi alan={alan} />}

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

      {/* Alan bazlı rapor. API `?alan_id=` destekliyordu ama arayüzde
          hiçbir yerden çağrılmıyordu: rapor yalnızca malzeme haritasından,
          sistemin tamamı için alınabiliyordu. Bir belediye yetkilisinin en
          çok isteyeceği şey ise BU sahanın raporudur. */}
      {RAPOR_ALABILIR.has(kullanici?.rol ?? '') && (
        <Kart className="mb-5 p-4">
          <RaporIndir alanId={alanId} />
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
          {goruntuler.map((g, i) => (
            <GoruntuKarti
              key={g.id} goruntu={g} sira={i + 1} siniflar={siniflar}
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

const ERISIM = {
  acik: { ad: 'Erişim açık', sinif: 'border-olumlu/50 text-olumlu bg-olumlu/10',
    not: 'Sahaya giriş açık.' },
  kisitli: { ad: 'Erişim kısıtlı', sinif: 'border-uyari/50 text-uyari bg-uyari/10',
    not: 'Sahaya giriş kısıtlı; yetkili birimle görüşülmeden gidilmemelidir.' },
  kapali: { ad: 'Erişim kapalı', sinif: 'border-dikkat/50 text-dikkat bg-dikkat/10',
    not: 'Sahaya giriş kapalı.' },
}

/**
 * Alan künyesi — sahanın kimlik bilgisi.
 *
 * Bu bilgi listedeki kartta vardı, alanın KENDİ sayfasında yoktu: sayfa
 * yalnızca adı gösterip doğrudan görüntülere geçiyordu. Sahaya ekip
 * gönderecek bir belediye ya da AFAD yetkilisi için erişim durumu
 * kartta değil, burada gerekiyor.
 *
 * Koordinat `sayisal` sınıfıyla ve tam duyarlıkla yazılır; kırpılmış bir
 * koordinat sahada yanlış yere götürür.
 */
function AlanKunyesi({ alan }: { alan: EnkazAlani }) {
  const e = ERISIM[alan.erisim_durumu]
  return (
    <Kart className="mb-5 p-4">
      <div className="flex flex-wrap items-start gap-x-8 gap-y-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-metin-4 mb-1.5">
            Erişim durumu
          </p>
          <span className={`inline-flex px-2 py-0.5 rounded border text-xs
            font-medium ${e.sinif}`}>{e.ad}</span>
          <p className="text-xs text-metin-3 mt-1.5 max-w-xs leading-relaxed">
            {e.not}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-metin-4 mb-1.5">
            Sorumlu
          </p>
          <p className="text-sm text-metin-2">{alan.sorumlu || '—'}</p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-metin-4 mb-1.5">
            Merkez konum
          </p>
          {alan.konum ? (
            <p className="text-sm text-metin-2 sayisal">
              {alan.konum.enlem.toFixed(5)}, {alan.konum.boylam.toFixed(5)}
            </p>
          ) : (
            /* "0, 0" ya da "—" değil: konumun GİRİLMEDİĞİ yazılır.
               Yokluk, sahanın koordinatsız olduğu anlamına gelmez. */
            <p className="text-sm text-metin-3">Girilmedi</p>
          )}
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-metin-4 mb-1.5">
            Sınır
          </p>
          <p className="text-sm text-metin-2">
            {alan.sinir && alan.sinir.length >= 3
              ? <><span className="sayisal">{alan.sinir.length - 1}</span> köşeli poligon</>
              : <span className="text-metin-3">Çizilmedi</span>}
          </p>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-metin-4 mb-1.5">
            Tanımlanma
          </p>
          <p className="text-sm text-metin-2 sayisal">
            {new Date(alan.olusturma_tarihi).toLocaleDateString('tr-TR')}
          </p>
        </div>
      </div>
    </Kart>
  )
}

function GoruntuKarti({
  goruntu, sira, siniflar, secili, secildi, olcebilir, rol,
}: {
  goruntu: Goruntu
  sira: number
  siniflar: Map<string, { renk: string; gorunen_ad: string; malzeme_mi: boolean }>
  secili: number | null
  secildi: (id: number) => void
  olcebilir: boolean
  rol: string
}) {
  // Listede üzerine gelinen tespitin kutusu görüntüde öne çıkar; ters yönde
  // de çalışır. İki panel arasındaki bağı gözle kurmak zordu.
  const [vurgulu, setVurgulu] = useState<number | null>(null)

  return (
    <Kart className="p-4">
      {/*
        ⚠️ GÖRÜNTÜLERİN KİMLİĞİ YOKTU. Her kart yalnızca "Tespitler"
        yazıyordu; beş görüntülü bir sahada ekran okuyucunun başlık
        listesi "Tespitler, Tespitler, Tespitler…" diye okunuyor ve
        hangi fotoğrafta olunduğu anlaşılamıyordu.

        Aynı yerde bir izlenebilirlik eksiği de vardı: `cekim_tarihi` ve
        `cihaz` API'den geliyor, tipte duruyor ve HİÇBİR EKRANDA
        gösterilmiyordu. Görüntünün ne zaman ve neyle çekildiği, bu
        projede tespitin dayanağının bir parçasıdır — kararı sonradan
        denetleyecek kişinin ilk soracağı şeydir.
      */}
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 mb-3
        pb-3 border-b border-kenar">
        <h2 className="text-sm font-semibold">
          <span className="sayisal">{sira}</span>. görüntü
        </h2>
        <p className="text-xs text-metin-3">
          {goruntu.cekim_tarihi
            ? `Çekim: ${new Date(goruntu.cekim_tarihi).toLocaleString('tr-TR')}`
            : 'Çekim tarihi görüntüde kayıtlı değil'}
          {goruntu.cihaz ? ` · ${goruntu.cihaz}` : ''}
          {' · '}
          Yüklenme: {new Date(goruntu.olusturma_tarihi).toLocaleDateString('tr-TR')}
        </p>
      </div>
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
            vurgulu={vurgulu}
            vurgulandi={setVurgulu}
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
                  vurgulu={vurgulu === t.id}
                  vurgulandi={setVurgulu}
                />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Kart>
  )
}

function TespitSatiri({
  tespit, siniflar, acik, ac, olcebilir, rol, vurgulu, vurgulandi,
}: {
  tespit: Tespit
  siniflar: Map<string, { renk: string; gorunen_ad: string; malzeme_mi: boolean }>
  acik: boolean
  ac: () => void
  olcebilir: boolean
  rol: string
  vurgulu: boolean
  vurgulandi: (id: number | null) => void
}) {
  const [miktar, setMiktar] = useState<Miktar | null>(null)
  const [olcumler, setOlcumler] = useState<Olcum[]>([])
  const [veriHatasi, setVeriHatasi] = useState('')
  // Her yenilemede artar; işlem geçmişi paneli buna bakarak tazelenir.
  // Ölçüm eklendikten sonra panelin eski hâlinde kalması, izlenebilirlik
  // iddiasını ekranda yalanlıyordu.
  const [surum, setSurum] = useState(0)

  const yenile = useCallback(() => {
    setVeriHatasi('')
    // Hatalar YUTULMAZ. Miktar gelmediğinde ekran sessizce boş kalırsa
    // kullanıcı "miktar hesaplanmadı" ile "istek başarısız" arasındaki
    // farkı göremez — bu projede o fark kuralın ta kendisidir.
    Promise.all([
      api.miktar(tespit.id).then(setMiktar),
      api.olcumler(tespit.id).then(setOlcumler),
    ])
      .catch((h) => setVeriHatasi(
        h instanceof Error ? h.message : 'Miktar ve ölçümler alınamadı',
      ))
      .finally(() => setSurum((n) => n + 1))
  }, [tespit.id])

  useEffect(() => { if (acik) yenile() }, [acik, yenile])

  const gosterilenSinif = tespit.duzeltilen_sinif ?? tespit.sinif
  const tanim = siniflar.get(gosterilenSinif)

  return (
    <div
      onMouseEnter={() => vurgulandi(tespit.id)}
      onMouseLeave={() => vurgulandi(null)}
      className={`border rounded-md transition-colors
        ${acik ? 'border-marka' : vurgulu ? 'border-kenar-parlak bg-yuzey-2'
                                          : 'border-kenar'}`}
    >
      <button onClick={ac}
        onFocus={() => vurgulandi(tespit.id)}
        onBlur={() => vurgulandi(null)}
        className="w-full text-left px-3 py-3 flex items-start gap-2.5">
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

      {acik && veriHatasi && (
        <div className="px-3 pb-3">
          <Hata mesaj={veriHatasi} />
          <Buton tur="ikincil" className="mt-2 text-sm" onClick={yenile}>
            Yeniden dene
          </Buton>
        </div>
      )}

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
              tespitId={tespit.id}
              yenilemeAnahtari={surum}
              baslik="Bu tespitin geçmişi" limit={20} kompakt
            />
          </div>
        </div>
      )}
    </div>
  )
}
