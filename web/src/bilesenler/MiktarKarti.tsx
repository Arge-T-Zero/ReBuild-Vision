import { useState } from 'react'
import { api } from '../api'
import type { Miktar, Olcum } from '../types'
import { Alan, Buton, Hata, girdiSinifi } from './Temel'

/**
 * Miktar kartı — ana talimat Bölüm 1.1'in görsel karşılığı.
 *
 * ÖLÇÜM YOKSA SAYI GÖSTERİLMEZ. Varsayılan değer, "≈0", "hesaplanıyor"
 * veya yer tutucu bir sayı YAZILMAZ. Boşluk bir hata gibi değil, BİLİNÇLİ
 * BİR KARAR gibi görünür: nedeni yazılır ve ölçüm ekleme aksiyonu sunulur.
 *
 * Miktar hesaplandığında TEK BİR KESİN DEĞER değil, belirsizlik aralığı ve
 * kullanılan yöntem birlikte gösterilir (Rapor Bölüm 4).
 *
 * Bu, final demosunun 7. adımıdır.
 */
/**
 * Sayıyı Türkçe biçimde yazar: ondalık ayracı virgül, binlik ayracı nokta.
 *
 * "11.16 ton" bir Türkçe arayüzde on bir bin yüz altmış gibi okunabilir.
 * Miktar bu projenin ana çıktısı olduğu için yanlış okunması pahalıdır.
 * Basamak sayısı KIRPILMAZ — miktar aralığı olduğu gibi gösterilir.
 */
function sayi(d: number | null | undefined): string {
  if (d === null || d === undefined) return '—'
  return d.toLocaleString('tr-TR', { maximumFractionDigits: 3 })
}

export function MiktarKarti({
  miktar, olcumler, olcumEklenebilir, olcumEklendi,
}: {
  miktar: Miktar
  olcumler: Olcum[]
  olcumEklenebilir: boolean
  olcumEklendi: () => void
}) {
  const [formAcik, setFormAcik] = useState(false)

  return (
    <div className="border border-kenar rounded-lg p-4 bg-yuzey-2/40">
      <h3 className="text-sm font-semibold text-metin-2 mb-3">Miktar</h3>

      {miktar.hesaplandi ? (
        <div>
          <p className="text-2xl font-semibold tabular-nums">
            {sayi(miktar.deger_alt)} – {sayi(miktar.deger_ust)}{' '}
            <span className="text-base font-normal text-metin-2">{miktar.birim}</span>
          </p>
          <p className="text-xs text-metin-3 mt-1">belirsizlik aralığı</p>

          <dl className="mt-3 space-y-1.5 text-xs">
            <div>
              <dt className="text-metin-3 inline">Yöntem: </dt>
              <dd className="text-metin-2 inline">{miktar.yontem}</dd>
            </div>
            <div>
              <dt className="text-metin-3 inline">Katsayı kaynağı: </dt>
              <dd className="text-metin-2 inline">{miktar.katsayi_kaynagi}</dd>
            </div>
          </dl>
        </div>
      ) : (
        /* Sayı yok. Yer tutucu da yok. Neden yazılı ve aksiyon sunuluyor. */
        <div>
          <p className="text-metin font-medium">{miktar.aciklama}</p>
          <p className="text-xs text-metin-3 mt-1.5">
            Sistem, dayanağı olmayan bir miktar tahmini üretmez.
          </p>
          {olcumEklenebilir && !formAcik && (
            <Buton tur="ikincil" className="mt-3" onClick={() => setFormAcik(true)}>
              Ölçüm ekle
            </Buton>
          )}
        </div>
      )}

      {olcumler.length > 0 && (
        <div className="mt-4 pt-3 border-t border-kenar">
          <p className="text-xs text-metin-3 mb-1.5">Girilen ölçümler</p>
          <ul className="space-y-1">
            {olcumler.map((o) => (
              <li key={o.id} className="text-xs text-metin-2">
                <span className="tabular-nums font-medium">
                  {sayi(o.deger)} {o.birim}
                </span>
                {' · '}{o.tur}{' · '}{o.yontem}
              </li>
            ))}
          </ul>
        </div>
      )}

      {olcumEklenebilir && (formAcik || (miktar.hesaplandi && olcumler.length > 0)) && (
        <OlcumFormu
          tespitId={miktar.tespit_id}
          acik={formAcik}
          ac={() => setFormAcik(true)}
          eklendi={() => { setFormAcik(false); olcumEklendi() }}
        />
      )}
    </div>
  )
}

function OlcumFormu({ tespitId, acik, ac, eklendi }: {
  tespitId: number; acik: boolean; ac: () => void; eklendi: () => void
}) {
  const [tur, setTur] = useState<'alan' | 'hacim' | 'agirlik'>('agirlik')
  const [deger, setDeger] = useState('')
  const [yontem, setYontem] = useState('')
  const [hata, setHata] = useState('')
  const [bekliyor, setBekliyor] = useState(false)

  const birim = { alan: 'm2', hacim: 'm3', agirlik: 'ton' }[tur]

  if (!acik) {
    return (
      <Buton tur="sessiz" className="mt-3 text-sm" onClick={ac}>
        Yeni ölçüm ekle
      </Buton>
    )
  }

  async function gonder(e: React.FormEvent) {
    e.preventDefault()
    setHata('')
    // Türkçe klavyede ondalık ayracı virgüldür; "12,4" yazan kullanıcı
    // hata yapmıyor. Number('12,4') NaN döndüğü için önceden bu giriş
    // "sıfırdan büyük olmalıdır" hatası alıyordu — değer sıfırdan
    // büyüktü, sorun biçimdi ve mesaj yanlış yeri gösteriyordu.
    const sayi = Number(deger.trim().replace(',', '.'))
    if (!Number.isFinite(sayi) || sayi <= 0) {
      setHata('Ölçüm değeri sıfırdan büyük bir sayı olmalıdır')
      return
    }
    // Sunucudaki üst sınırla aynı (api/app/schemas.py OLCUM_UST_SINIR).
    // Burada da kontrol edilir ki kullanıcı formu göndermeden uyarılsın.
    if (sayi > 100000) {
      setHata(
        `Bu değer tek bir tespit için olağandışı yüksek (${sayi} ${birim}). `
        + 'Girdiğiniz sayıyı kontrol edin.',
      )
      return
    }
    if (!yontem.trim()) {
      setHata('Ölçümün nasıl yapıldığı yazılmalıdır — izlenebilirlik için zorunlu')
      return
    }
    setBekliyor(true)
    try {
      await api.olcumEkle({ tespit_id: tespitId, tur, deger: sayi, birim, yontem })
      setDeger(''); setYontem('')
      eklendi()
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'Ölçüm kaydedilemedi')
    } finally {
      setBekliyor(false)
    }
  }

  return (
    <form onSubmit={gonder} className="mt-4 pt-3 border-t border-kenar space-y-3">
      <Alan etiket="Ölçüm türü">
        <select value={tur} onChange={(e) => setTur(e.target.value as typeof tur)}
          className={girdiSinifi}>
          <option value="agirlik">Ağırlık (ton)</option>
          <option value="hacim">Hacim (m³)</option>
          <option value="alan">Görünür alan (m²)</option>
        </select>
      </Alan>
      <Alan etiket={`Değer (${birim})`}>
        {/* İpucu Türkçe ondalık ayracıyla yazılır. Kod virgülü zaten
            kabul ediyordu ama örnek "12.4" diyerek kullanıcıyı noktaya
            yönlendiriyordu — verilen örnek, kabul edilen biçimle aynı
            olmalı. */}
        <input value={deger} onChange={(e) => setDeger(e.target.value)}
          inputMode="decimal" placeholder="örn. 12,4" className={girdiSinifi} />
      </Alan>
      <Alan etiket="Ölçüm yöntemi"
        ipucu="Kim, neyle, nasıl ölçtü? İşlem geçmişine kaydedilir.">
        <input value={yontem} onChange={(e) => setYontem(e.target.value)}
          placeholder="örn. Saha kantar ölçümü" className={girdiSinifi} />
      </Alan>
      {hata && <Hata mesaj={hata} />}
      <Buton type="submit" disabled={bekliyor}>
        {bekliyor ? 'Kaydediliyor…' : 'Ölçümü kaydet'}
      </Buton>
    </form>
  )
}
