import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import {
  Baslik, BosDurum, Buton, Hata, Kart, girdiSinifi,
} from '../bilesenler/Temel'
import { Ikon } from '../bilesenler/Ikon'
import { Sayfa } from '../bilesenler/Duzen'
import type { Kullanici, Rol } from '../types'
import { sayfaGorevi } from '../roller'

/**
 * Rol onay ekranı — kamu sistemi mantığının göstergesi.
 *
 * Brief Bölüm 3: "Kullanıcı kayıt olurken kendi rolünü seçemez."
 * Kayıt sonrası hesap `onay_durumu: beklemede` ile başlar; yetkiyi
 * yönetici verir. Bu, demoda anlatılacak bir ayrıntıdır.
 */

const ROLLER: { deger: Rol; etiket: string; aciklama: string }[] = [
  { deger: 'saha', etiket: 'Saha personeli',
    aciklama: 'Görüntü yükleme, ölçüm girme' },
  { deger: 'uzman', etiket: 'Doğrulayıcı uzman',
    aciklama: 'Onayla / düzelt / belirsiz işaretle' },
  { deger: 'belediye', etiket: 'Belediye yetkilisi',
    aciklama: 'Saha tanımlama, görüntü yükleme, rapor' },
  { deger: 'afad', etiket: 'AFAD yetkilisi',
    aciklama: 'Çok sahalı görünüm, rapor' },
  { deger: 'yikim', etiket: 'Yıkım firması',
    aciklama: 'Yalnızca kendi sahası — salt okunur' },
  { deger: 'tesis', etiket: 'Tesis operatörü',
    aciklama: 'Kendine yönlendirilen kayıtlar — salt okunur' },
  { deger: 'yonetici', etiket: 'Yönetici',
    aciklama: 'Rol atama ve tüm işlemler' },
]

export function Yonetici() {
  const { kullanici } = useDurum()
  const [bekleyenler, setBekleyenler] = useState<Kullanici[] | null>(null)
  const [hata, setHata] = useState('')

  const yenile = useCallback(() => {
    api.bekleyenler().then(setBekleyenler).catch((h) => setHata(h.message))
  }, [])

  useEffect(() => { yenile() }, [yenile])

  return (
    <Sayfa dar>
      <Baslik
        ustBaslik="Yönetim"
        baslik="Rol onayı bekleyen hesaplar"
        gorev={sayfaGorevi(kullanici?.rol ?? null, 'yonetici')}
        aciklama="Kullanıcılar kayıt olurken kendi rollerini seçemez. Yetki bu ekrandan verilir; atama işlem geçmişine kaydedilir."
      />

      {hata && <div className="mb-4"><Hata mesaj={hata} /></div>}

      {bekleyenler === null ? (
        <p className="text-metin-3 text-sm">Yükleniyor…</p>
      ) : bekleyenler.length === 0 ? (
        <Kart>
          <BosDurum
            ikon={<Ikon.Kullanici boyut={20} />}
            baslik="Onay bekleyen hesap yok"
            aciklama="Tüm başvurular karara bağlanmış. Yeni bir kullanıcı kayıt olduğunda burada görünür ve rol atanana kadar giriş yapamaz."
          />
        </Kart>
      ) : (
        <ul className="space-y-3">
          {bekleyenler.map((k) => (
            <li key={k.id}>
              <BekleyenSatir kullanici={k} tamamlandi={yenile} />
            </li>
          ))}
        </ul>
      )}
    </Sayfa>
  )
}

function BekleyenSatir({ kullanici, tamamlandi }: {
  kullanici: Kullanici; tamamlandi: () => void
}) {
  const [rol, setRol] = useState<string>('')
  const [hata, setHata] = useState('')
  const [bekliyor, setBekliyor] = useState(false)

  async function karar(onay: 'onaylandi' | 'reddedildi') {
    if (onay === 'onaylandi' && !rol) {
      setHata('Hesabı onaylamak için bir rol seçilmelidir')
      return
    }
    setHata(''); setBekliyor(true)
    try {
      // Reddedilen hesap için de bir rol alanı gönderilir; hesap
      // onay_durumu=reddedildi olduğu için giriş yapamaz.
      await api.rolAta(kullanici.id, rol || 'tesis', onay)
      tamamlandi()
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'İşlem başarısız')
      setBekliyor(false)
    }
  }

  const secili = ROLLER.find((r) => r.deger === rol)

  return (
    <Kart className="p-4">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="min-w-0">
          <p className="font-medium">{kullanici.ad}</p>
          <p className="text-sm text-metin-3">{kullanici.eposta}</p>
          <p className="text-xs text-metin-3 mt-0.5">
            Kayıt: {new Date(kullanici.olusturma_tarihi).toLocaleString('tr-TR')}
          </p>
        </div>
        <span className="shrink-0 px-2 py-0.5 rounded border border-dashed
          border-kenar-net text-xs text-metin-3">
          Rol atanmadı
        </span>
      </div>

      <div className="mt-4 space-y-3">
        <label className="block">
          <span className="block text-sm font-medium text-metin-2 mb-1.5">
            Atanacak rol
          </span>
          <select value={rol} onChange={(e) => setRol(e.target.value)}
            className={girdiSinifi}>
            <option value="">Rol seçin…</option>
            {ROLLER.map((r) => (
              <option key={r.deger} value={r.deger}>{r.etiket}</option>
            ))}
          </select>
          {secili && (
            <span className="block text-xs text-metin-3 mt-1">
              {secili.aciklama}
            </span>
          )}
        </label>

        {hata && <Hata mesaj={hata} />}

        <div className="flex gap-2 flex-wrap">
          <Buton disabled={bekliyor || !rol} onClick={() => karar('onaylandi')}>
            Rolü ata ve hesabı onayla
          </Buton>
          <Buton tur="ikincil" disabled={bekliyor}
            onClick={() => karar('reddedildi')}>
            Başvuruyu reddet
          </Buton>
        </div>
      </div>
    </Kart>
  )
}
