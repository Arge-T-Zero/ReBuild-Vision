import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import type { TehlikeliYanit } from '../types'
import { Alan, Buton, Hata, girdiSinifi } from './Temel'

/**
 * Tehlikeli madde kartı — TEŞHİS DEĞİL, YÖNLENDİRME.
 *
 * Ana talimat Bölüm 1.2 / Rapor 3.5:
 * Bu bileşende bilinçli olarak BULUNMAYAN şeyler:
 *  - Tehlikeli madde tahmini, ikonu, renk kodu veya olasılık değeri
 *  - "Güvenli" / "tehlikesiz" rozeti
 *  - Model çıktısından türetilen herhangi bir uyarı
 *
 * Kayıt bulunmadığında yeşil bir "temiz" göstergesi GÖSTERİLMEZ; bunun
 * yerine yokluğun güvenlik anlamına gelmediği yazıyla söylenir (Rapor 12).
 */
export function TehlikeliKarti({
  tespitId, yonlendirebilir, labGirebilir,
}: {
  tespitId: number
  yonlendirebilir: boolean
  labGirebilir: boolean
}) {
  const [veri, setVeri] = useState<TehlikeliYanit | null>(null)
  const [formAcik, setFormAcik] = useState(false)
  const [not, setNot] = useState('')
  const [hata, setHata] = useState('')
  const [bekliyor, setBekliyor] = useState(false)

  const yenile = useCallback(() => {
    api.tehlikeliKayitlar(tespitId).then(setVeri).catch(() => {})
  }, [tespitId])

  useEffect(() => { yenile() }, [yenile])

  async function yonlendir() {
    setHata(''); setBekliyor(true)
    try {
      await api.tehlikeliYonlendir({
        tespit_id: tespitId, durum: 'incelemeye_yonlendirildi',
      })
      yenile()
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'Kayıt açılamadı')
    } finally {
      setBekliyor(false)
    }
  }

  async function labSonucuKaydet(e: React.FormEvent) {
    e.preventDefault()
    if (!not.trim()) {
      setHata('Laboratuvar sonucu için not zorunludur')
      return
    }
    setHata(''); setBekliyor(true)
    try {
      await api.tehlikeliYonlendir({
        tespit_id: tespitId, durum: 'lab_sonucu_var', lab_sonucu_notu: not,
      })
      setNot(''); setFormAcik(false)
      yenile()
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'Sonuç kaydedilemedi')
    } finally {
      setBekliyor(false)
    }
  }

  if (!veri) return null

  return (
    <div className="border border-kenar rounded-lg p-4 bg-yuzey-2/40">
      <h4 className="text-sm font-semibold text-metin-2 mb-1">
        Tehlikeli madde incelemesi
      </h4>
      <p className="text-xs text-metin-3 mb-3">
        Sistem tehlikeli madde teşhisi yapmaz. Bu bölüm yalnızca uzman ve
        laboratuvar incelemesi kayıtlarını tutar.
      </p>

      {veri.kayitlar.length === 0 ? (
        /* Yeşil "temiz" rozeti YOK — yokluk güvenlik değildir (Rapor 12). */
        <p className="text-xs text-metin-2 border-l-2 border-uyari pl-3 py-1">
          {veri.aciklama}
        </p>
      ) : (
        <ul className="space-y-2">
          {veri.kayitlar.map((k) => (
            <li key={k.id} className="text-xs border-l-2 border-kenar-net pl-3 py-1">
              <p className="text-metin">
                {k.durum === 'incelemeye_yonlendirildi'
                  ? 'Uzman/laboratuvar incelemesine yönlendirildi'
                  : 'Laboratuvar sonucu girildi'}
              </p>
              <p className="text-metin-3 mt-0.5">
                Kullanıcı #{k.giren_id} ·{' '}
                {new Date(k.tarih).toLocaleString('tr-TR')}
              </p>
              {k.lab_sonucu_notu && (
                <p className="text-metin-2 mt-1">{k.lab_sonucu_notu}</p>
              )}
            </li>
          ))}
        </ul>
      )}

      {hata && <div className="mt-3"><Hata mesaj={hata} /></div>}

      <div className="mt-3 flex gap-2 flex-wrap">
        {yonlendirebilir && (
          <Buton tur="ikincil" className="text-sm" disabled={bekliyor}
            onClick={yonlendir}>
            İncelemeye yönlendir
          </Buton>
        )}
        {labGirebilir && !formAcik && (
          <Buton tur="sessiz" className="text-sm"
            onClick={() => setFormAcik(true)}>
            Laboratuvar sonucu gir
          </Buton>
        )}
      </div>

      {formAcik && (
        <form onSubmit={labSonucuKaydet} className="mt-3 space-y-3">
          <Alan etiket="Laboratuvar sonucu"
            ipucu="Sonucu model değil, yetkili uzman girer. Rapor numarası yazın.">
            <textarea value={not} onChange={(e) => setNot(e.target.value)}
              rows={3} className={girdiSinifi}
              placeholder="örn. Numunede asbest tespit edilmedi — rapor no 2026/451" />
          </Alan>
          <div className="flex gap-2">
            <Buton type="submit" disabled={bekliyor}>Sonucu kaydet</Buton>
            <Buton type="button" tur="sessiz"
              onClick={() => { setFormAcik(false); setHata('') }}>
              Vazgeç
            </Buton>
          </div>
        </form>
      )}
    </div>
  )
}
