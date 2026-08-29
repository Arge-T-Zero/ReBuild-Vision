import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import type { IslemGecmisi as Kayit, SinifTanimi } from '../types'
import { BosDurum, Buton } from './Temel'

/**
 * İşlem geçmişi — Rapor Bölüm 6, dördüncü yenilikçi yön.
 *
 * "Kayıtların kim tarafından ve ne zaman doğrulandığı izlenebilecektir."
 *
 * Ana talimat Bölüm 4.2: bu bilgi ARAYÜZDE DE GÖRÜNÜR OLMALIDIR, yalnızca
 * veri tabanında durmamalıdır. Bu bileşen o gerekliliğin karşılığıdır.
 */

const ISLEM_ADI: Record<string, string> = {
  olusturma: 'oluşturdu',
  guncelleme: 'değiştirdi',
  silme: 'sildi',
}

const ALAN_ADI: Record<string, string> = {
  dogrulama_durumu: 'Doğrulama durumu',
  duzeltilen_sinif: 'Düzeltilen sınıf',
  inceleme_gerekli: 'İnceleme gerekli',
  dogrulayan_id: 'Doğrulayan',
  dogrulama_tarihi: 'Doğrulama tarihi',
  sinif: 'Sınıf',
  guven_skoru: 'Güven skoru',
  deger: 'Değer',
  yontem: 'Yöntem',
  ad: 'Ad',
  rol: 'Rol',
  onay_durumu: 'Onay durumu',
  erisim_durumu: 'Erişim durumu',
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
}

const KAYIT_TIPI_ADI: Record<string, string> = {
  tespit: 'Tespit',
  olcum: 'Ölçüm',
  enkaz_alani: 'Enkaz alanı',
  goruntu: 'Görüntü',
  kullanici: 'Kullanıcı',
  miktar_hesabi: 'Miktar hesabı',
  tehlikeli_kayit: 'Tehlikeli madde kaydı',
}

/**
 * Geçmişte gösterilmesi anlamsız olan alanlar.
 *
 * `dogrulayan_id` ve `dogrulama_tarihi` bilinçli olarak gizlenir: kaydın
 * başlık satırı zaten "kim" ve "ne zaman" bilgisini veriyor, tekrar etmek
 * listeyi okunmaz hale getiriyordu.
 */
const GIZLE = new Set([
  'id', 'olusturma_tarihi', 'tarih', 'bbox',
  'dogrulayan_id', 'dogrulama_tarihi', 'giren_id', 'yukleyen_id',
])

const ISO_TARIH = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/

function tarihBicimle(s: string): string {
  const t = new Date(s)
  if (Number.isNaN(t.getTime())) return s
  return t.toLocaleString('tr-TR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function degerBicimle(
  d: unknown, siniflar?: Map<string, SinifTanimi>,
): string {
  if (d === null || d === undefined) return '—'
  if (typeof d === 'boolean') return d ? 'evet' : 'hayır'
  const m = String(d)
  // Ham ISO damgası göstermek yerine okunur tarih yaz.
  if (ISO_TARIH.test(m)) return tarihBicimle(m)
  // Sınıf adları tek kaynaktan gelir: siniflar.json.
  const sinif = siniflar?.get(m)
  if (sinif) return sinif.gorunen_ad
  return DEGER_ADI[m] ?? m
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

  if (hata) return <p className="text-xs text-dikkat">{hata}</p>
  if (kayitlar === null) {
    return <p className="text-xs text-metin-3">Geçmiş yükleniyor…</p>
  }

  if (kayitlar.length === 0) {
    return kompakt
      ? <p className="text-xs text-metin-3">Bu kayıtta henüz değişiklik yok.</p>
      : <BosDurum
          baslik="Henüz işlem kaydı yok"
          aciklama="Bir alan tanımlandığında, görüntü yüklendiğinde, tespit doğrulandığında ya da ölçüm girildiğinde kayıt buraya otomatik düşer. Kayıtlar silinemez ve düzenlenemez." />
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold text-metin-2">{baslik}</h4>
        <Buton tur="sessiz" className="text-xs !min-h-0 !py-1" onClick={yenile}>
          Yenile
        </Buton>
      </div>

      <ol className="space-y-2">
        {kayitlar.map((k) => {
          const degisenler = Object.entries(k.yeni_deger ?? {})
            .filter(([alan]) => !GIZLE.has(alan))
          return (
          <li key={k.id}
            className="text-xs border-l-2 border-kenar-net pl-3 py-0.5">
            <p className="text-metin-2">
              <span className="text-metin">
                {KAYIT_TIPI_ADI[k.kayit_tipi] ?? k.kayit_tipi}
                {k.kayit_id != null && ` #${k.kayit_id}`}
              </span>
              {' '}kaydını{' '}
              <span className="text-metin">
                {k.kullanici_ad
                  ?? (k.kullanici_id != null
                    ? `kullanıcı #${k.kullanici_id}`
                    : 'sistem')}
              </span>
              {' '}{ISLEM_ADI[k.islem] ?? k.islem}
              <span className="text-metin-3"> · {tarihBicimle(k.tarih)}</span>
            </p>

            {k.islem === 'guncelleme' && degisenler.length > 0 && (
              <ul className="mt-1 space-y-0.5">
                {degisenler.map(([alan, yeni]) => (
                  <li key={alan} className="text-metin-3">
                    {ALAN_ADI[alan] ?? alan}:{' '}
                    <s className="text-metin-3">
                      {degerBicimle(k.eski_deger?.[alan], siniflar)}
                    </s>
                    {' → '}
                    <span className="text-metin-2">
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
    </div>
  )
}
