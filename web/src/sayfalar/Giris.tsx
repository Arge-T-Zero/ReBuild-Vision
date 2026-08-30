import { useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import { useTema } from '../tema'
import { Alan, Buton, Hata, girdiSinifi } from '../bilesenler/Temel'
import { Ikon } from '../bilesenler/Ikon'
import { SahteModelUyarisi } from '../bilesenler/ModelDurumu'

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

const KUNYE = 'TEKNOFEST 2026 Sıfır Atık ve Döngüsel Ekonomi Yarışması · '
  + 'Takım Arge-T Zero. Sistem yalnızca görünür yüzeye ilişkin ön '
  + 'değerlendirme yapar ve tehlikeli madde teşhisi yapmaz.'

/**
 * Giriş ekranındaki tema düğmesi.
 *
 * Tema düğmesi yalnızca giriş YAPTIKTAN sonraki üst çubukta vardı. Oysa
 * temayı en çok isteyecek kişi, ekranı henüz okuyamayan kişidir: güneş
 * altındaki saha personeli ya da gece nöbetindeki uzman. Tercihini
 * yapabilmesi için önce giriş yapması gerekiyordu.
 */
function TemaDugmesi() {
  const { tema, temaDegistir } = useTema()
  return (
    <Buton
      tur="ikincil" boyut="kucuk" onClick={temaDegistir}
      aria-label={tema === 'dark' ? 'Açık temaya geç' : 'Koyu temaya geç'}
      title={tema === 'dark'
        ? 'Açık tema — güneş altında daha okunur'
        : 'Koyu tema — düşük ışıkta daha okunur'}
      ikon={tema === 'dark' ? <Ikon.Gunes boyut={15} /> : <Ikon.Ay boyut={15} />}
    >
      {tema === 'dark' ? 'Açık tema' : 'Koyu tema'}
    </Buton>
  )
}

function Marka({ boyut = 'normal' }: { boyut?: 'normal' | 'buyuk' }) {
  const k = boyut === 'buyuk' ? 36 : 32
  return (
    <span className="flex items-center gap-2.5">
      <span aria-hidden className="rounded-lg bg-marka/15 border border-marka/40
        grid place-items-center text-marka shrink-0"
        style={{ width: k, height: k }}>
        <img src="/logo-isaret.svg" alt="" aria-hidden
          width={boyut === 'buyuk' ? 20 : 18}
          height={boyut === 'buyuk' ? 20 : 18} />
      </span>
      <span className={`font-semibold tracking-tight
        ${boyut === 'buyuk' ? 'text-lg' : ''}`}>ReBuild Vision</span>
    </span>
  )
}

export function Giris() {
  const { girisYap, oturumNotu } = useDurum()
  const [kayitModu, setKayitModu] = useState(false)
  const [eposta, setEposta] = useState('')
  const [parola, setParola] = useState('')
  const [parolaGorunur, setParolaGorunur] = useState(false)
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
      {/* Sol: kimlik ve iddia — arkada saha görüntüsü.
          `aside` bilinçli: içerik bir yer işaretine (landmark) ait olmalı;
          denetimde bu bölüm hiçbir yer işaretinin içinde değildi. */}
      <aside aria-label="Proje tanıtımı"
        className="hidden lg:flex flex-col justify-between p-12 border-r
        border-kenar bg-yuzey relative overflow-hidden">
        {/* Görsel yapay zekâ ile üretilmiştir; gerçek bir afet fotoğrafı
            değildir (Madde 10.7 ile uyumlu, telif sorunu yok). */}
        <img
          src="/gorseller/giris-hero.webp" alt="" aria-hidden
          className="giris-gorsel absolute inset-0 w-full h-full object-cover"
          fetchPriority="high"
        />
        {/* Okunabilirlik perdesi. Gücü temaya göre değişir (index.css):
            koyu temada güçlü, açık temada zayıf — aynı perde açık temada
            fotoğrafı beyaz bir sise çeviriyordu. */}
        <div aria-hidden className="giris-perde absolute inset-0" />

        <Marka boyut="buyuk" />

        <div className="max-w-lg relative">
          <h1 className="text-3xl font-semibold tracking-tight leading-tight">
            Enkaz malzemelerinin görüntü tabanlı ön sınıflandırması ve
            doğrulanabilir kaynak haritası
          </h1>

          <ul className="mt-10 space-y-6">
            {OZELLIKLER.map((o) => (
              <li key={o.baslik} className="border-l-2 border-kenar-net pl-4">
                <p className="font-medium text-metin">{o.baslik}</p>
                {/* Fotoğrafın üzerinde `metin-3` zayıf kalıyordu; bu
                    paragraflar düz zeminde değil görselin üstünde
                    duruyor ve bir ton koyu olmaları gerekiyor. */}
                <p className="text-sm text-metin-2 mt-1 leading-relaxed">
                  {o.metin}
                </p>
              </li>
            ))}
          </ul>
        </div>

        <p className="text-xs text-metin-3 max-w-lg leading-relaxed relative">
          {KUNYE}
        </p>
      </aside>

      {/* Sağ: form — sayfanın ana içeriği */}
      <main className="relative flex flex-col p-6 sm:p-10">
        {/* MOBİL HERO ŞERİDİ.

            Saha görüntüsü yalnızca `lg` ve üzerindeki sol panelde vardı;
            telefonda hiç görünmüyordu. Oysa sahanın asıl aygıtı telefon
            ve görsel, ekranın ne işe yaradığını tek bakışta anlatan
            öğe — metinden önce o okunuyor.

            Şerit tam genişlikte (kenar boşluğundan taşar) ve alt kenarı
            sayfa zeminine erir; üzerinde yalnızca tema düğmesi durur.
            Marka, başlık ve form ŞERİDİN ALTINDA, düz zeminde kalır:
            fotoğrafın üzerine metin ve form girdisi koymak her iki
            temada da okunurluğu kumara çevirirdi.

            640 px'lik küçük sürüm kullanılır — masaüstü sürümü 170 KB,
            bu 102 KB ve telefonda aradaki farkın karşılığı yok. */}
        <div aria-hidden className="lg:hidden absolute inset-x-0 top-0
          h-[190px] sm:h-[240px] overflow-hidden">
          <img
            src="/gorseller/giris-hero-kucuk.webp" alt=""
            className="giris-gorsel w-full h-full object-cover"
            fetchPriority="high" width={640} height={478}
          />
          <div className="giris-perde-mobil absolute inset-0" />
        </div>

        {/* Tema düğmesi her ekran boyutunda, giriş yapmadan erişilebilir.
            Kendi zemini olduğu için fotoğrafın üzerinde de okunur. */}
        <div className="relative flex justify-end mb-6 lg:mb-0">
          <TemaDugmesi />
        </div>

        <div className="relative w-full max-w-sm mx-auto grow flex flex-col
          justify-center pt-[120px] sm:pt-[160px] lg:pt-0">
          {/* Küçük ekranda sol panel gizlendiği için burası BOMBOŞ bir
              ekrandı: ne proje adı, ne ne yaptığı, ne kimin yaptığı
              görünüyordu — üstelik sahanın asıl aygıtı telefon.
              Aşağıdaki blok o boşluğu, masaüstündeki anlatının sıkışmış
              hâliyle doldurur. */}
          <div className="lg:hidden mb-8">
            <Marka />
            <h1 className="text-xl font-semibold tracking-tight leading-snug mt-5">
              Enkaz malzemelerinin görüntü tabanlı ön sınıflandırması ve
              doğrulanabilir kaynak haritası
            </h1>
            <ul className="mt-4 space-y-2">
              {OZELLIKLER.map((o) => (
                <li key={o.baslik}
                  className="flex items-start gap-2 text-sm text-metin-2">
                  <Ikon.Onayla boyut={14}
                    className="text-marka mt-0.5 shrink-0" />
                  {o.baslik}
                </li>
              ))}
            </ul>
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
              {/* Parolayı görebilmek eldivenli parmakla ve güneş altında
                  yazan biri için konfor değil, gerekliliktir: yanlış
                  yazdığını ancak "e-posta veya parola hatalı" cevabından
                  anlıyordu. */}
              <span className="relative block">
                <input value={parola} onChange={(e) => setParola(e.target.value)}
                  type={parolaGorunur ? 'text' : 'password'}
                  className={`${girdiSinifi} pr-12`}
                  autoComplete={kayitModu ? 'new-password' : 'current-password'}
                  required />
                <button type="button" tabIndex={0}
                  onClick={() => setParolaGorunur((g) => !g)}
                  aria-label={parolaGorunur ? 'Parolayı gizle' : 'Parolayı göster'}
                  aria-pressed={parolaGorunur}
                  className="absolute right-1 top-1/2 -translate-y-1/2 px-2.5
                    !min-h-0 h-9 rounded text-metin-3 hover:text-metin
                    hover:bg-yuzey-2 transition-colors"
                >
                  {parolaGorunur
                    ? <Ikon.GozKapali boyut={17} />
                    : <Ikon.Goz boyut={17} />}
                </button>
              </span>
            </Alan>

            {kayitModu && (
              /* Rol seçimi BİLİNÇLİ OLARAK YOK — Brief Bölüm 3 */
              <p className="text-xs text-metin-3 bg-yuzey-2 border border-kenar
                rounded-md px-3 py-2.5 leading-relaxed">
                Rolünüzü kendiniz seçemezsiniz. Kayıt sonrası hesabınız onay
                bekler; yetkiniz yönetici tarafından atanır.
              </p>
            )}

            {/* Oturum kendiliğinden düştüyse nedeni burada söylenir. */}
            {!hata && !kayitModu && oturumNotu && (
              <p role="status" className="text-uyari text-sm bg-uyari/10
                border border-uyari/30 rounded-md px-3 py-2.5 leading-relaxed">
                {oturumNotu}
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

          {/* Sahte model servisi uyarısı giriş ekranında da görünür:
              demoyu izleyen kişi sisteme daha bakmadan gerçek bir modelin
              çalıştığını sanmamalı (ana talimat Bölüm 9.5). */}
          <div className="mt-6"><SahteModelUyarisi /></div>

          {/* Künye küçük ekranda sol panelle birlikte kaybolmuştu. */}
          <p className="lg:hidden text-xs text-metin-4 leading-relaxed mt-6">
            {KUNYE}
          </p>
        </div>
      </main>
    </div>
  )
}
