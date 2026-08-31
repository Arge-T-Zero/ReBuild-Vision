import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import type { IslemGecmisi as Kayit, SinifTanimi } from '../types'
import { BosDurum, Buton, Hata } from './Temel'
import { Ikon } from './Ikon'

/**
 * İşlem geçmişi — Rapor Bölüm 6, dördüncü yenilikçi yön.
 *
 * "Kayıtların kim tarafından ve ne zaman doğrulandığı izlenebilecektir."
 *
 * Ana talimat Bölüm 4.2: bu bilgi ARAYÜZDE DE GÖRÜNÜR OLMALIDIR, yalnızca
 * veri tabanında durmamalıdır.
 *
 * Liste TÜRE GÖRE RENKLENDİRİLİR. Sebebi süs değil: karışık bir akışta
 * "hangi kayıt neydi" ancak satırı okuyarak anlaşılıyordu ve elli satırlık
 * bir geçmişte göz hiçbir şey ayırt edemiyordu. Renk, listeyi taramayı
 * mümkün kılar.
 *
 * ⚠️ Renk TEK BAŞINA anlam taşımaz (ana talimat Bölüm 9.3): her satırda
 * türün ADI yazılı ve ayırt edici bir ikon vardır. Gri tonlamada ve renk
 * körlüğünde de okunur.
 *
 * Kayıt tipi renkleri malzeme sınıfı renklerinden ve durum renklerinden
 * (onaylandı/uyarı/hata) BİLİNÇLİ OLARAK ayrıdır — aynı ekranda üç ayrı
 * renk dili varsa hiçbiri okunmaz.
 */

const ALAN_ADI: Record<string, string> = {
  dogrulama_durumu: 'Doğrulama durumu',
  duzeltilen_sinif: 'Düzeltilen sınıf',
  inceleme_gerekli: 'İnceleme gerekli',
  dogrulayan_id: 'Doğrulayan',
  dogrulama_tarihi: 'Doğrulama tarihi',
  sinif: 'Sınıf',
  guven_skoru: 'Güven skoru',
  deger: 'Değer',
  birim: 'Birim',
  tur: 'Ölçüm türü',
  yontem: 'Yöntem',
  ad: 'Ad',
  rol: 'Rol',
  onay_durumu: 'Onay durumu',
  erisim_durumu: 'Erişim durumu',
  sorumlu: 'Sorumlu',
  eposta: 'E-posta',
  durum: 'Durum',
  lab_sonucu_notu: 'Laboratuvar notu',
}

/**
 * Ham veri tabanı değerlerinin okunur karşılıkları.
 *
 * Sayfanın vaadi "kim, ne zaman, NEYİ değiştirdi". Ekranda `duzeltildi`,
 * `onaylandi` gibi Türkçe karakterleri düşmüş ham enum değerleri
 * göstermek bu vaadi yarım bırakıyordu. Sınıf adları burada YOKTUR —
 * onlar `siniflar` tanımından (`gorunen_ad`) gelir, tek kaynak orasıdır.
 */
const DEGER_ADI: Record<string, string> = {
  beklemede: 'Beklemede',
  onaylandi: 'Onaylandı',
  duzeltildi: 'Düzeltildi',
  belirsiz: 'Belirsiz',
  reddedildi: 'Reddedildi',
  acik: 'Açık',
  kisitli: 'Kısıtlı',
  kapali: 'Kapalı',
  incelemeye_yonlendirildi: 'İncelemeye yönlendirildi',
  lab_sonucu_var: 'Laboratuvar sonucu var',
  yonetici: 'Yönetici',
  saha: 'Saha personeli',
  uzman: 'Doğrulayıcı uzman',
  belediye: 'Belediye yetkilisi',
  afad: 'AFAD yetkilisi',
  yikim: 'Yıkım firması',
  tesis: 'Geri kazanım tesisi',
  agirlik: 'Ağırlık',
  hacim: 'Hacim',
  alan: 'Görünür alan',
}

interface TipTanimi {
  ad: string
  renk: string
  ikon: (p: { boyut: number; className?: string }) => React.ReactElement
}

const TIP: Record<string, TipTanimi> = {
  tespit: { ad: 'Tespit', renk: 'var(--u-kayit-tespit)', ikon: Ikon.Kuyruk },
  olcum: { ad: 'Ölçüm', renk: 'var(--u-kayit-olcum)', ikon: Ikon.Terazi },
  enkaz_alani: { ad: 'Enkaz alanı', renk: 'var(--u-kayit-alan)', ikon: Ikon.Alan },
  goruntu: { ad: 'Görüntü', renk: 'var(--u-kayit-goruntu)', ikon: Ikon.Foto },
  kullanici: { ad: 'Kullanıcı', renk: 'var(--u-kayit-kullanici)', ikon: Ikon.Kullanici },
  miktar_hesabi: { ad: 'Miktar hesabı', renk: 'var(--u-kayit-miktar)', ikon: Ikon.Grafik },
  tehlikeli_kayit: { ad: 'Tehlikeli madde', renk: 'var(--u-kayit-tehlikeli)', ikon: Ikon.Lab },
}

const BILINMEYEN: TipTanimi = {
  ad: 'Kayıt', renk: 'var(--u-metin-3)', ikon: Ikon.Gecmis,
}

/**
 * Gösterilmesi anlamsız olan alanlar.
 *
 * `dogrulayan_id` ve `dogrulama_tarihi` bilinçli gizlenir: satırın kendisi
 * zaten "kim" ve "ne zaman" bilgisini veriyor, tekrarı listeyi okunmaz
 * hâle getiriyordu.
 */
const GIZLE = new Set([
  'id', 'olusturma_tarihi', 'tarih', 'bbox',
  'dogrulayan_id', 'dogrulama_tarihi', 'giren_id', 'yukleyen_id',
])

const ISO_TARIH = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/

function saatBicimle(s: string): string {
  const t = new Date(s)
  if (Number.isNaN(t.getTime())) return s
  return t.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
}

function tarihBicimle(s: string): string {
  const t = new Date(s)
  if (Number.isNaN(t.getTime())) return s
  return t.toLocaleString('tr-TR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

/**
 * Gün başlığı — "Bugün", "Dün" ya da tam tarih.
 *
 * Elli satırın her birinde tam tarih tekrarlanınca göz saatleri
 * karşılaştıramıyordu. Tarih gün başlığına çıkarıldı; satırlarda yalnızca
 * saat kalır.
 */
function gunEtiketi(s: string): string {
  const t = new Date(s)
  if (Number.isNaN(t.getTime())) return s
  const bugun = new Date()
  const gun = (d: Date) => `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`
  if (gun(t) === gun(bugun)) return 'Bugün'
  const dun = new Date(bugun)
  dun.setDate(bugun.getDate() - 1)
  if (gun(t) === gun(dun)) return 'Dün'
  return t.toLocaleDateString('tr-TR', {
    day: '2-digit', month: 'long', year: 'numeric',
  })
}

function degerBicimle(d: unknown, siniflar?: Map<string, SinifTanimi>): string {
  if (d === null || d === undefined) return '—'
  if (typeof d === 'boolean') return d ? 'evet' : 'hayır'
  const m = String(d)
  if (ISO_TARIH.test(m)) return tarihBicimle(m)
  // Sınıf adları tek kaynaktan gelir: siniflar.json.
  const sinif = siniflar?.get(m)
  if (sinif) return sinif.gorunen_ad
  return DEGER_ADI[m] ?? m
}

/**
 * Satırın cümlesi — "kim ne yaptı".
 *
 * Önceki metin her kayıt için aynı kalıbı kuruyordu: "X kaydını Y
 * değiştirdi". Teknik olarak doğru ama HİÇBİR ŞEY anlatmıyordu — bir
 * tespitin doğrulanmasıyla bir kullanıcıya rol atanması aynı cümleyle
 * çıkıyordu. Fiil artık yapılan işi söyler.
 */
function cumle(k: Kayit): string {
  const kim = k.kullanici_ad
    ?? (k.kullanici_id != null ? `Kullanıcı #${k.kullanici_id}` : 'Sistem')
  const yeni = k.yeni_deger ?? {}

  if (k.islem === 'olusturma') {
    switch (k.kayit_tipi) {
      case 'enkaz_alani': return `${kim} bu enkaz alanını tanımladı.`
      case 'goruntu': return `${kim} bu görüntüyü yükledi.`
      case 'olcum': return `${kim} saha ölçümü girdi.`
      // Tespiti İNSAN oluşturmaz, model üretir. "X oluşturdu" demek
      // tespiti insanın kararıymış gibi gösteriyordu — projenin en
      // temel ayrımını (ön tahmin ≠ karar) geçmişte siliyordu.
      case 'tespit': return `${kim} görüntüyü yükledi; model bu tespiti üretti.`
      // Kayıt olan kişi henüz oturum açmış değildir; `kullanici_id`
      // boştur ve "Sistem oluşturdu" demek yanıltıcıydı.
      case 'kullanici':
        return k.kullanici_id == null
          ? 'Yeni hesap başvurusu alındı; yönetici onayı bekliyor.'
          : `${kim} hesap oluşturdu.`
      case 'miktar_hesabi': return 'Ölçüme dayanarak miktar hesaplandı.'
      case 'tehlikeli_kayit':
        return `${kim} kaydı uzman/laboratuvar incelemesine yönlendirdi.`
      default: return `${kim} kaydı oluşturdu.`
    }
  }

  if (k.islem === 'guncelleme') {
    if (k.kayit_tipi === 'tespit' && 'dogrulama_durumu' in yeni) {
      const d = String(yeni.dogrulama_durumu)
      if (d === 'onaylandi') return `${kim} tespiti onayladı.`
      if (d === 'duzeltildi') return `${kim} tespitin sınıfını düzeltti.`
      if (d === 'belirsiz') return `${kim} tespiti belirsiz olarak işaretledi.`
    }
    if (k.kayit_tipi === 'kullanici' && 'rol' in yeni) {
      return `${kim} bu hesaba rol atadı.`
    }
    return `${kim} kaydı değiştirdi.`
  }

  if (k.islem === 'silme') return `${kim} kaydı sildi.`
  return `${kim} ${k.islem} işlemi yaptı.`
}

export function IslemGecmisiListesi({
  kayitTipi, kayitId, tespitId, baslik = 'İşlem geçmişi', limit = 20,
  kompakt = false, yenilemeAnahtari = 0,
}: {
  kayitTipi?: string
  kayitId?: number
  /** Tespitin bütün hikâyesi: ölçüm ve tehlikeli madde kayıtları dahil. */
  tespitId?: number
  baslik?: string
  limit?: number
  kompakt?: boolean
  /** Değeri değişince liste yeniden çekilir (ölçüm eklendikten sonra). */
  yenilemeAnahtari?: number
}) {
  const { siniflar } = useDurum()
  const [kayitlar, setKayitlar] = useState<Kayit[] | null>(null)
  const [hata, setHata] = useState('')

  const yenile = useCallback(() => {
    setHata('')
    api.gecmis({
      kayit_tipi: kayitTipi, kayit_id: kayitId, tespit_id: tespitId, limit,
    })
      .then(setKayitlar)
      .catch((h) => { setHata(h.message); setKayitlar([]) })
    // `yenilemeAnahtari` bilinçli bağımlılık: ölçüm ya da tehlikeli madde
    // kaydı eklendikten sonra panel kendiliğinden tazelensin.
  }, [kayitTipi, kayitId, tespitId, limit, yenilemeAnahtari])

  useEffect(() => { yenile() }, [yenile])

  // Hata çıplak bir `p` idi: `role="alert"` taşımadığı için ekran
  // okuyucuya DUYURULMUYORDU ve yeniden deneme yolu da yoktu.
  // Uygulamanın geri kalanıyla aynı bileşen kullanılır.
  if (hata) {
    return (
      <div>
        <Hata mesaj={hata} />
        <Buton tur="ikincil" boyut="kucuk" className="mt-2.5" onClick={yenile}>
          Yeniden dene
        </Buton>
      </div>
    )
  }
  if (kayitlar === null) {
    return <p className="text-xs text-metin-3">Geçmiş yükleniyor…</p>
  }

  if (kayitlar.length === 0) {
    return kompakt
      ? <p className="text-xs text-metin-3">Bu kayıtta henüz değişiklik yok.</p>
      : <BosDurum
          ikon={<Ikon.Gecmis boyut={20} />}
          baslik="Henüz işlem kaydı yok"
          aciklama="Bir alan tanımlandığında, görüntü yüklendiğinde, tespit doğrulandığında ya da ölçüm girildiğinde kayıt buraya otomatik düşer. Kayıtlar silinemez ve düzenlenemez." />
  }

  // Kompakt kullanım bir kartın içindedir (sayfa h1 → kart h2 → burası
  // h3); tam sayfa kullanımında doğrudan h1'in altındadır.
  const Duzey = kompakt ? 'h3' : 'h2'
  // Gün başlığı liste başlığının BİR ALTINDA olmalı; sabit `h4` yazınca
  // tam sayfa kullanımında h2'den h4'e atlıyordu (axe: `heading-order`).
  const GunDuzeyi = kompakt ? 'h4' : 'h3'

  // Güne göre grupla. Kayıtlar sunucudan yeniden eskiye gelir; sıra
  // korunur.
  const gruplar: { gun: string; satirlar: Kayit[] }[] = []
  for (const k of kayitlar) {
    const g = gunEtiketi(k.tarih)
    const son = gruplar[gruplar.length - 1]
    if (son && son.gun === g) son.satirlar.push(k)
    else gruplar.push({ gun: g, satirlar: [k] })
  }

  return (
    <div>
      <div className="flex items-center justify-between gap-3 mb-3">
        <Duzey className="text-sm font-semibold text-metin-2">
          {baslik}
          <span className="text-metin-3 font-normal">
            {' · '}<span className="sayisal">{kayitlar.length}</span> kayıt
          </span>
        </Duzey>
        <Buton tur="sessiz" boyut="kucuk" onClick={yenile}>Yenile</Buton>
      </div>

      {gruplar.map((grup) => (
        <section key={grup.gun} className="mb-4 last:mb-0">
          <GunDuzeyi className="text-[11px] font-medium uppercase
            tracking-wider text-metin-4 mb-2">{grup.gun}</GunDuzeyi>

          <ol className="space-y-1.5">
            {grup.satirlar.map((k) => {
              const tip = TIP[k.kayit_tipi] ?? BILINMEYEN
              const Simge = tip.ikon
              const degisenler = Object.entries(k.yeni_deger ?? {})
                .filter(([alan]) => !GIZLE.has(alan))

              return (
                <li key={k.id}
                  /* Sol kenar rengi türü söyler; renk tek başına
                     bırakılmaz, yanında ikon ve tür adı durur. */
                  className="rounded-md border border-kenar bg-yuzey-2/50
                    pl-3 pr-3 py-2 border-l-[3px]"
                  style={{ borderLeftColor: tip.renk }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <span className="flex items-center gap-1.5 min-w-0">
                      <span aria-hidden style={{ color: tip.renk }}
                        className="shrink-0">
                        <Simge boyut={13} />
                      </span>
                      <span className="text-xs font-medium truncate"
                        style={{ color: tip.renk }}>
                        {tip.ad}
                      </span>
                      {k.kayit_id != null && (
                        <span className="text-xs text-metin-4 sayisal shrink-0">
                          #{k.kayit_id}
                        </span>
                      )}
                    </span>
                    <time dateTime={k.tarih}
                      className="text-xs text-metin-4 sayisal shrink-0"
                      title={tarihBicimle(k.tarih)}>
                      {saatBicimle(k.tarih)}
                    </time>
                  </div>

                  <p className="text-xs text-metin-2 mt-1 leading-relaxed">
                    {cumle(k)}
                  </p>

                  {k.islem === 'guncelleme' && degisenler.length > 0 && (
                    <ul className="mt-1.5 space-y-1">
                      {degisenler.map(([alan, yeni]) => (
                        <li key={alan}
                          className="text-xs text-metin-3 flex flex-wrap
                            items-baseline gap-x-1.5">
                          <span className="text-metin-4">
                            {ALAN_ADI[alan] ?? alan}
                          </span>
                          <s>{degerBicimle(k.eski_deger?.[alan], siniflar)}</s>
                          <span aria-hidden>→</span>
                          <span className="text-metin-2 font-medium">
                            {degerBicimle(yeni, siniflar)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </li>
              )
            })}
          </ol>
        </section>
      ))}
    </div>
  )
}
