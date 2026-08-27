import { useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import { Alan, Buton, Hata, girdiSinifi } from '../bilesenler/Temel'
import { Ikon } from '../bilesenler/Ikon'

const OZELLIKLER = [
  {
    baslik: 'İnsan denetimli sınıflandırma',
    metin: 'Model çıktıları ön tahmindir; uzman onaylar, düzeltir ya da ' +
      'belirsiz işaretler. İnsanın kararı modelin tahminini geçersiz kılar.',
  },
  {
    baslik: 'Ölçüm yoksa miktar üretilmez',
    metin: 'Sistem dayanağı olmayan tonaj tahmini oluşturmaz. Miktar ' +
      'hesaplandığında tek bir kesin değer değil, belirsizlik aralığı verilir.',
  },
  {
    baslik: 'Her kayıt izlenebilir',
    metin: 'Kimin ne zaman neyi değiştirdiği otomatik kaydedilir. ' +
      'Kayıtlar silinemez ve düzenlenemez.',
  },
]

export function Giris() {
  const { girisYap } = useDurum()
  const [kayitModu, setKayitModu] = useState(false)
  const [eposta, setEposta] = useState('')
  const [parola, setParola] = useState('')
  const [ad, setAd] = useState('')
  const [hata, setHata] = useState('')
  const [bilgi, setBilgi] = useState('')
  const [bekliyor, setBekliyor] = useState(false)

  async function gonder(e: React.FormEvent) {
    e.preventDefault()
    setHata(''); setBilgi(''); setBekliyor(true)
    try {
      if (kayitModu) {
        await api.kayit({ eposta, parola, ad })
        setBilgi(
          'Kaydınız alındı. Hesabınız yönetici onayı ve rol ataması bekliyor; ' +
          'onaylandıktan sonra giriş yapabilirsiniz.',
        )
        setKayitModu(false)
      } else {
        await girisYap(eposta, parola)
      }
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'İşlem başarısız')
    } finally {
      setBekliyor(false)
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-[1.1fr_minmax(0,460px)]">
      {/* Sol: kimlik ve iddia */}
      <div className="hidden lg:flex flex-col justify-between p-12 border-r
        border-kenar bg-yuzey">
        <span className="flex items-center gap-3">
          <span aria-hidden className="w-9 h-9 rounded-lg bg-marka/15
            border border-marka/40 grid place-items-center text-marka">
            <Ikon.Alan boyut={19} />
          </span>
          <span className="font-semibold text-lg tracking-tight">ReBuild Vision</span>
        </span>

        <div className="max-w-lg">
          <h1 className="text-3xl font-semibold tracking-tight leading-tight">
            Enkaz malzemelerinin görüntü tabanlı ön sınıflandırması ve
            doğrulanabilir kaynak haritası
          </h1>

          <ul className="mt-10 space-y-6">
            {OZELLIKLER.map((o) => (
              <li key={o.baslik} className="border-l-2 border-kenar-net pl-4">
                <p className="font-medium text-metin">{o.baslik}</p>
                <p className="text-sm text-metin-3 mt-1 leading-relaxed">
                  {o.metin}
                </p>
              </li>
            ))}
          </ul>
        </div>

        <p className="text-xs text-metin-4 max-w-lg leading-relaxed">
          TEKNOFEST 2026 Sıfır Atık ve Döngüsel Ekonomi Yarışması ·
          Takım Arge-T Zero. Sistem yalnızca görünür yüzeye ilişkin ön
          değerlendirme yapar ve tehlikeli madde teşhisi yapmaz.
        </p>
      </div>

      {/* Sağ: form */}
      <div className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-sm">
          <div className="lg:hidden mb-8">
            <span className="flex items-center gap-2.5">
              <span aria-hidden className="w-8 h-8 rounded-md bg-marka/15
                border border-marka/40 grid place-items-center text-marka">
                <Ikon.Alan boyut={17} />
              </span>
              <span className="font-semibold tracking-tight">ReBuild Vision</span>
            </span>
          </div>

          <h2 className="text-xl font-semibold tracking-tight">
            {kayitModu ? 'Hesap oluştur' : 'Giriş yap'}
          </h2>
          <p className="text-sm text-metin-3 mt-1 mb-7">
            {kayitModu
              ? 'Kaydınız yönetici onayından sonra etkinleşir.'
              : 'Kurumsal hesabınızla oturum açın.'}
          </p>

          <form onSubmit={gonder} className="space-y-4">
            {kayitModu && (
              <Alan etiket="Ad soyad">
                <input value={ad} onChange={(e) => setAd(e.target.value)}
                  className={girdiSinifi} autoComplete="name" required />
              </Alan>
            )}
            <Alan etiket="E-posta">
              <input value={eposta} onChange={(e) => setEposta(e.target.value)}
                type="email" className={girdiSinifi} autoComplete="username"
                placeholder="ad.soyad@kurum.gov.tr" required />
            </Alan>
            <Alan etiket="Parola"
              ipucu={kayitModu ? 'En az 8 karakter' : undefined}>
              <input value={parola} onChange={(e) => setParola(e.target.value)}
                type="password" className={girdiSinifi}
                autoComplete={kayitModu ? 'new-password' : 'current-password'}
                required />
            </Alan>

            {kayitModu && (
              /* Rol seçimi BİLİNÇLİ OLARAK YOK — Brief Bölüm 3 */
              <p className="text-xs text-metin-3 bg-yuzey-2 border border-kenar
                rounded-md px-3 py-2.5 leading-relaxed">
                Rolünüzü kendiniz seçemezsiniz. Kayıt sonrası hesabınız onay
                bekler; yetkiniz yönetici tarafından atanır.
              </p>
            )}

            {hata && <Hata mesaj={hata} />}
            {bilgi && (
              <p role="status" className="text-olumlu text-sm bg-olumlu/10
                border border-olumlu/30 rounded-md px-3 py-2.5 leading-relaxed">
                {bilgi}
              </p>
            )}

            <Buton type="submit" disabled={bekliyor} className="w-full">
              {bekliyor ? 'İşleniyor…' : kayitModu ? 'Kayıt ol' : 'Giriş yap'}
            </Buton>
          </form>

          <div className="mt-5 pt-5 border-t border-kenar">
            <button
              className="text-sm text-metin-3 hover:text-metin transition-colors
                !min-h-0"
              onClick={() => { setKayitModu(!kayitModu); setHata(''); setBilgi('') }}
            >
              {kayitModu
                ? 'Zaten hesabım var — giriş yap'
                : 'Hesabım yok — kayıt ol'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
