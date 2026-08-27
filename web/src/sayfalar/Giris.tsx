import { useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import { Alan, Buton, Hata, Kart, girdiSinifi } from '../bilesenler/Temel'

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
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <h1 className="text-2xl font-semibold mb-1">ReBuild Vision</h1>
        <p className="text-metin-3 text-sm mb-6">
          Enkaz malzemelerinin görüntü tabanlı ön sınıflandırması
        </p>

        <Kart className="p-6">
          <form onSubmit={gonder} className="space-y-4">
            {kayitModu && (
              <Alan etiket="Ad soyad">
                <input value={ad} onChange={(e) => setAd(e.target.value)}
                  className={girdiSinifi} autoComplete="name" required />
              </Alan>
            )}
            <Alan etiket="E-posta">
              <input value={eposta} onChange={(e) => setEposta(e.target.value)}
                type="email" className={girdiSinifi} autoComplete="username" required />
            </Alan>
            <Alan etiket="Parola"
              ipucu={kayitModu ? 'En az 8 karakter' : undefined}>
              <input value={parola} onChange={(e) => setParola(e.target.value)}
                type="password" className={girdiSinifi}
                autoComplete={kayitModu ? 'new-password' : 'current-password'} required />
            </Alan>

            {kayitModu && (
              /* Rol seçimi BİLİNÇLİ OLARAK YOK — Brief Bölüm 3 */
              <p className="text-xs text-metin-3 bg-yuzey-2 border border-kenar
                rounded-md px-3 py-2">
                Rolünüzü kendiniz seçemezsiniz. Kayıt sonrası hesabınız onay
                bekler; rolünüz yetkili yönetici tarafından atanır.
              </p>
            )}

            {hata && <Hata mesaj={hata} />}
            {bilgi && (
              <p role="status" className="text-olumlu text-sm bg-olumlu/10
                border border-olumlu/30 rounded-md px-3 py-2">{bilgi}</p>
            )}

            <Buton type="submit" disabled={bekliyor} className="w-full">
              {bekliyor ? 'İşleniyor…' : kayitModu ? 'Kayıt ol' : 'Giriş yap'}
            </Buton>
          </form>

          <div className="mt-4 pt-4 border-t border-kenar">
            <Buton tur="sessiz" className="w-full text-sm"
              onClick={() => { setKayitModu(!kayitModu); setHata(''); setBilgi('') }}>
              {kayitModu ? 'Zaten hesabım var — giriş yap' : 'Hesabım yok — kayıt ol'}
            </Buton>
          </div>
        </Kart>
      </div>
    </div>
  )
}
