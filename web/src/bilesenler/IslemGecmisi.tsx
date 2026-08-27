import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import type { IslemGecmisi as Kayit } from '../types'
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

function degerBicimle(d: unknown): string {
  if (d === null || d === undefined) return '—'
  if (typeof d === 'boolean') return d ? 'evet' : 'hayır'
  const m = String(d)
  // Ham ISO damgası göstermek yerine okunur tarih yaz.
  return ISO_TARIH.test(m) ? tarihBicimle(m) : m
}

export function IslemGecmisiListesi({
  kayitTipi, kayitId, baslik = 'İşlem geçmişi', limit = 20, kompakt = false,
}: {
  kayitTipi?: string
  kayitId?: number
  baslik?: string
  limit?: number
  kompakt?: boolean
}) {
  const [kayitlar, setKayitlar] = useState<Kayit[] | null>(null)
  const [hata, setHata] = useState('')

  const yenile = useCallback(() => {
    api.gecmis({ kayit_tipi: kayitTipi, kayit_id: kayitId, limit })
      .then(setKayitlar)
      .catch((h) => setHata(h.message))
  }, [kayitTipi, kayitId, limit])

  useEffect(() => { yenile() }, [yenile])

  if (hata) return <p className="text-xs text-dikkat">{hata}</p>
  if (kayitlar === null) {
    return <p className="text-xs text-metin-3">Geçmiş yükleniyor…</p>
  }

  if (kayitlar.length === 0) {
    return kompakt
      ? <p className="text-xs text-metin-3">Bu kayıtta henüz değişiklik yok.</p>
      : <BosDurum baslik="Henüz işlem kaydı yok"
          aciklama="Sistemdeki her yazma işlemi burada görünür." />
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
                {k.kullanici_id != null ? `kullanıcı #${k.kullanici_id}` : 'sistem'}
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
                      {degerBicimle(k.eski_deger?.[alan])}
                    </s>
                    {' → '}
                    <span className="text-metin-2">{degerBicimle(yeni)}</span>
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
