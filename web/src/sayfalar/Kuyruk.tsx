import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import {
  Baslik, BosDurum, Buton, Hata, Kart, OnTahminEtiketi, SinifEtiketi,
  girdiSinifi,
} from '../bilesenler/Temel'
import { Ikon } from '../bilesenler/Ikon'
import { useGezinme } from '../gezinme'
import { GuvenSkoru } from '../bilesenler/GuvenSkoru'
import { Sayfa } from '../bilesenler/Duzen'
import type { Tespit } from '../types'
import { sayfaGorevi } from '../roller'

/**
 * Uzman doğrulama kuyruğu.
 *
 * Düşük güvenli tespitler buraya OTOMATİK düşer — kullanıcının kuyruğa
 * ekleme yapması gerekmez (ana talimat Bölüm 7.3). Final demosunun
 * 4. ve 5. adımı.
 */
const KARAR_METNI: Record<string, string> = {
  onaylandi: 'onaylandı',
  duzeltildi: 'düzeltildi',
  belirsiz: 'belirsiz olarak işaretlendi',
}

export function Kuyruk() {
  const { kullanici, siniflar, siniflarHam } = useDurum()
  const { git, erisilebilir } = useGezinme()
  const [kayitlar, setKayitlar] = useState<Tespit[] | null>(null)
  const [hata, setHata] = useState('')
  // Verilen son karar. Karar verilince satır listeden düşüyor ve ekranda
  // OLAN BİTENE DAİR HİÇBİR İZ KALMIYORDU: uzman "Onayla"ya bastığında
  // kayıt sessizce yok oluyor, kaydın gerçekten işlendiğini mi yoksa
  // uygulamanın mı düştüğünü ayırt edemiyordu. Bu ürünün ana işi insanın
  // kararını kaydetmek; kararın kaydedildiğini söylememek en pahalı
  // yerdeki sessizlikti.
  const [sonKarar, setSonKarar] = useState<string>('')

  const yenile = useCallback(() => {
    // Hata durumunda liste boş diziye çekilir; `null` "yükleniyor"
    // demektir ve hatayla birlikte kalıcı olarak ekranda kalırdı.
    api.kuyruk()
      .then(setKayitlar)
      .catch((h) => { setHata(h.message); setKayitlar([]) })
  }, [])

  useEffect(() => { yenile() }, [yenile])

  return (
    <Sayfa dar>
      <Baslik
        ustBaslik="Doğrulama"
        baslik="Uzman inceleme kuyruğu"
        gorev={sayfaGorevi(kullanici?.rol ?? null, 'kuyruk')}
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

      {/* `role="status"` ile duyurulur: ekran okuyucu kullanan uzman da
          kararının kaydedildiğini duyar. */}
      {sonKarar && (
        <p role="status" className="flex items-start gap-2 text-sm mb-4
          text-olumlu bg-olumlu/10 border border-olumlu/30 rounded-md
          px-3 py-2.5">
          <Ikon.Onayla boyut={16} className="mt-0.5 shrink-0" />
          <span>
            {sonKarar} Karar işlem geçmişine kaydedildi ve geri alınamaz;
            değişiklik gerekirse alan sayfasından yeni bir kayıt açılır.
          </span>
        </p>
      )}

      {kayitlar === null ? (
        <p className="text-metin-3 text-sm">Yükleniyor…</p>
      ) : kayitlar.length === 0 ? (
        <Kart>
          <BosDurum
            ikon={<Ikon.Onayla boyut={20} />}
            baslik="Kuyruk temiz — bekleyen inceleme yok"
            aciklama="Model güveni düşük bir tespit oluştuğunda buraya kendiliğinden düşer; ayrıca bir şey yapmanız gerekmez."
            aksiyon={erisilebilir('alanlar') && (
              <Buton tur="ikincil" onClick={() => git('alanlar')}
                ikon={<Ikon.Alan boyut={15} />}>
                Enkaz alanlarını incele
              </Buton>
            )}
          />
        </Kart>
      ) : (
        <ul className="space-y-3">
          {kayitlar.map((t) => (
            <li key={t.id}>
              <KuyrukSatiri
                tespit={t} siniflar={siniflar}
                secenekler={siniflarHam?.siniflar ?? []}
                tamamlandi={(durum, sinifAdi) => {
                  setSonKarar(
                    `Tespit #${t.id} ${KARAR_METNI[durum] ?? durum}`
                    + (sinifAdi ? ` — sınıf ${sinifAdi} olarak güncellendi.` : '.'),
                  )
                  yenile()
                }}
              />
            </li>
          ))}
        </ul>
      )}
    </Sayfa>
  )
}

/**
 * Tespitin görüntü üzerindeki kırpılmış önizlemesi.
 *
 * Uzman kanıta bakmadan karar veremez. Kırpma, görüntüyü büyütüp
 * `object-position` ile kutunun merkezine kaydırarak yapılır — sunucuda
 * ayrı bir kırpma işi gerektirmez.
 *
 * Ölçekleme `bbox_format` alanına göre yapılır (ana talimat Bölüm 4.3):
 * `pixel_absolute_original` kutu koordinatlarının ORİJİNAL görüntü
 * pikselinde olduğunu söyler. Başka bir biçim gelirse önizleme
 * gösterilmez — yanlış yeri kırpmaktansa hiç göstermemek doğrudur.
 */
function Kanit({ tespit }: { tespit: Tespit }) {
  const { bbox, bbox_format: bicim } = tespit
  const yol = tespit.goruntu_dosya_yolu
  const gen = tespit.goruntu_genislik
  const yuk = tespit.goruntu_yukseklik

  if (!yol) return null

  const kirpilabilir = !!bbox && bicim === 'pixel_absolute_original'
    && !!gen && !!yuk && bbox.w > 0 && bbox.h > 0

  if (!kirpilabilir) {
    // Kutu ölçeklenemiyorsa görüntünün tamamı gösterilir ve bu AÇIKÇA
    // yazılır. Yanlış yeri kırpıp doğruymuş gibi sunmak, uzmanı hatalı
    // karara sürükler.
    return (
      <div className="shrink-0">
        <div className="w-28 h-28 rounded-md overflow-hidden border border-kenar
          bg-yuzey-3">
          <img src={api.gorselUrl(yol)} loading="lazy"
            alt="Tespitin alındığı görüntü"
            className="w-full h-full object-cover" />
        </div>
        <p className="text-[10px] text-metin-4 mt-1 w-28 leading-tight">
          Kutu konumu ölçeklenemedi — görüntünün tamamı
        </p>
      </div>
    )
  }

  // Kutuyu önizlemeye SIĞDIRACAK ölçek. 1.6 çarpanı kutunun çevresinden
  // bir miktar bağlam bırakır: uzman malzemeyi tek başına değil,
  // bulunduğu yerle birlikte görmelidir.
  const P = 112
  const k = P / (Math.max(bbox!.w, bbox!.h) * 1.6)
  const merkezX = (bbox!.x + bbox!.w / 2) * k
  const merkezY = (bbox!.y + bbox!.h / 2) * k

  return (
    <div className="shrink-0">
      <div
        role="img"
        aria-label={`Tespitin görüntü üzerindeki konumu — ${tespit.sinif} ön tahmini`}
        className="rounded-md border border-kenar bg-yuzey-3 relative
          overflow-hidden"
        style={{
          width: P, height: P,
          backgroundImage: `url(${api.gorselUrl(yol)})`,
          backgroundSize: `${gen! * k}px ${yuk! * k}px`,
          backgroundPosition: `${P / 2 - merkezX}px ${P / 2 - merkezY}px`,
          backgroundRepeat: 'no-repeat',
        }}
      >
        {/* Kutunun kendisi de çizilir: uzman modelin TAM olarak nereyi
            işaretlediğini görmeli, yalnızca çevresini değil. */}
        <span
          aria-hidden
          className="absolute border-2 border-uyari/90 rounded-[3px]
            pointer-events-none"
          style={{
            left: P / 2 - (bbox!.w * k) / 2,
            top: P / 2 - (bbox!.h * k) / 2,
            width: bbox!.w * k,
            height: bbox!.h * k,
          }}
        />
      </div>
      <p className="text-[10px] text-metin-4 mt-1 w-28 leading-tight">
        Model kutusu
      </p>
    </div>
  )
}

function KuyrukSatiri({ tespit, siniflar, secenekler, tamamlandi }: {
  tespit: Tespit
  siniflar: Map<string, { gorunen_ad: string; renk: string }>
  secenekler: { ad: string; gorunen_ad: string }[]
  tamamlandi: (durum: string, sinifAdi?: string) => void
}) {
  const [duzeltmeAcik, setDuzeltmeAcik] = useState(false)
  const [yeniSinif, setYeniSinif] = useState('')
  const [hata, setHata] = useState('')
  const [bekliyor, setBekliyor] = useState(false)

  async function karar(durum: string, duzeltilen?: string) {
    setHata(''); setBekliyor(true)
    try {
      await api.dogrula(tespit.id, durum, duzeltilen)
      tamamlandi(
        durum,
        duzeltilen
          ? secenekler.find((o) => o.ad === duzeltilen)?.gorunen_ad ?? duzeltilen
          : undefined,
      )
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'Doğrulama kaydedilemedi')
      setBekliyor(false)
    }
  }

  const tanim = siniflar.get(tespit.sinif)

  return (
    <Kart className="p-4">
      <div className="flex items-start gap-3">
        <Kanit tespit={tespit} />
        <div className="grow min-w-0">
          {/* Hangi sahadaki hangi tespit — iki kayıt birbirinden
              ayırt edilebilmeli. */}
          <p className="text-xs text-metin-4 mb-1.5 truncate">
            Tespit #{tespit.id}
            {tespit.alan_ad && <> · {tespit.alan_ad}</>}
          </p>
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
