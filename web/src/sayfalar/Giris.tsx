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

/** Sunucudaki `Field(min_length=8)` ile aynı (api/app/schemas.py). */
const PAROLA_ASGARI = 8

/**
 * Giriş ekranındaki tema düğmesi.
 *
 * Tema düğmesi yalnızca giriş YAPTIKTAN sonraki üst çubukta vardı. Oysa
 * temayı en çok isteyecek kişi, ekranı henüz okuyamayan kişidir: güneş
 * altındaki saha personeli ya da gece nöbetindeki uzman.
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

/** Parola alanı — göster/gizle düğmesiyle. */
function ParolaAlani({ deger, degisti, etiket, tamamlama }: {
  deger: string
  degisti: (d: string) => void
  etiket: string
  tamamlama: string
}) {
  const [gorunur, setGorunur] = useState(false)
  return (
    <Alan etiket={etiket}>
      {/* Parolayı görebilmek eldivenli parmakla ve güneş altında yazan
          biri için konfor değil, gerekliliktir: yanlış yazdığını ancak
          "e-posta veya parola hatalı" cevabından anlıyordu. */}
      <span className="relative block">
        <input
          value={deger} onChange={(e) => degisti(e.target.value)}
          type={gorunur ? 'text' : 'password'}
          className={`${girdiSinifi} pr-12`}
          autoComplete={tamamlama} required
        />
        <button type="button"
          onClick={() => setGorunur((g) => !g)}
          aria-label={gorunur ? 'Parolayı gizle' : 'Parolayı göster'}
          aria-pressed={gorunur}
          className="absolute right-1 top-1/2 -translate-y-1/2 px-2.5
            !min-h-0 h-9 rounded text-metin-3 hover:text-metin
            hover:bg-yuzey-2 transition-colors"
        >
          {gorunur ? <Ikon.GozKapali boyut={17} /> : <Ikon.Goz boyut={17} />}
        </button>
      </span>
    </Alan>
  )
}

/**
 * Kural göstergesi — parolanın koşulu sağlayıp sağlamadığını SÖYLER.
 *
 * Renk tek başına anlam taşımaz: ikon da değişir ve metin zaten kuralın
 * kendisidir (ana talimat Bölüm 9.3).
 */
function Kural({ saglandi, children }: {
  saglandi: boolean; children: React.ReactNode
}) {
  return (
    <li className={`flex items-start gap-2 text-xs leading-relaxed
      ${saglandi ? 'text-olumlu' : 'text-metin-3'}`}>
      {saglandi
        ? <Ikon.Onayla boyut={13} className="mt-0.5 shrink-0" />
        : <Ikon.Bekle boyut={13} className="mt-0.5 shrink-0" />}
      <span>{children}</span>
    </li>
  )
}

/** Tanıtım blokları — masaüstünde sol panelde, mobilde formun altında. */
function Ozellikler({ kompakt = false }: { kompakt?: boolean }) {
  return (
    <ul className={kompakt ? 'space-y-4' : 'space-y-6'}>
      {OZELLIKLER.map((o) => (
        <li key={o.baslik} className="border-l-2 border-kenar-net pl-4">
          <p className="font-medium text-metin">{o.baslik}</p>
          {/* Masaüstünde bu paragraflar fotoğrafın ÜZERİNDE duruyor ve
              bir ton koyu olmaları gerekiyor; mobilde düz zeminde. */}
          <p className={`text-sm mt-1 leading-relaxed
            ${kompakt ? 'text-metin-3' : 'text-metin-2'}`}>
            {o.metin}
          </p>
        </li>
      ))}
    </ul>
  )
}

export function Giris() {
  const { girisYap, oturumNotu } = useDurum()
  const [kayitModu, setKayitModu] = useState(false)
  const [bilgi, setBilgi] = useState('')

  function kipDegistir(kayit: boolean) {
    setKayitModu(kayit)
    setBilgi('')
    // Uzun kayıt ekranından kısa giriş ekranına dönerken sayfa ortada
    // kalıyordu; kullanıcı boş bir alana bakıyordu.
    window.scrollTo({ top: 0, behavior: 'auto' })
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-[1.1fr_minmax(0,460px)]">
      {/* Sol: kimlik ve iddia — arkada saha görüntüsü.
          `aside` bilinçli: içerik bir yer işaretine (landmark) ait olmalı. */}
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
        {/* Okunabilirlik perdesi; gücü temaya göre değişir (index.css). */}
        <div aria-hidden className="giris-perde absolute inset-0" />

        <Marka boyut="buyuk" />

        <div className="max-w-lg relative">
          <h1 className="text-3xl font-semibold tracking-tight leading-tight">
            Enkaz malzemelerinin görüntü tabanlı ön sınıflandırması ve
            doğrulanabilir kaynak haritası
          </h1>
          <div className="mt-10"><Ozellikler /></div>
        </div>

        <p className="text-xs text-metin-3 max-w-lg leading-relaxed relative">
          {KUNYE}
        </p>
      </aside>

      {/* Sağ: form — sayfanın ana içeriği */}
      <main className="relative flex flex-col">
        {/* MOBİL HERO ŞERİDİ — saha görüntüsü telefonda da görünür.
            640 px'lik küçük sürüm kullanılır (masaüstü sürümü 170 KB). */}
        <div aria-hidden className="lg:hidden relative h-[200px] sm:h-[240px]
          overflow-hidden shrink-0">
          <img
            src="/gorseller/giris-hero-kucuk.webp" alt=""
            className="giris-gorsel w-full h-full object-cover"
            fetchPriority="high" width={640} height={478}
          />
          <div className="giris-perde-mobil absolute inset-0" />
        </div>

        {/* Şeridin son 40 px'ine binerek içeriği yukarı çeker: fotoğrafla
            metin arasında kopuk bir bant kalmaz. */}
        <div className="relative flex flex-col grow p-6 sm:p-10
          -mt-10 lg:mt-0">
          <div className="flex justify-end mb-6 lg:mb-0">
            <TemaDugmesi />
          </div>

          <div className="w-full max-w-sm mx-auto grow flex flex-col
            justify-center">
            <div className="lg:hidden mb-7">
              <Marka />
              <h1 className="text-xl font-semibold tracking-tight
                leading-snug mt-4">
                Enkaz malzemelerinin görüntü tabanlı ön sınıflandırması ve
                doğrulanabilir kaynak haritası
              </h1>
            </div>

            {kayitModu
              ? <KayitFormu
                  girisEkranina={() => kipDegistir(false)}
                  tamamlandi={(m) => { setBilgi(m); setKayitModu(false) }}
                />
              : <GirisFormu
                  kayitEkranina={() => kipDegistir(true)}
                  bilgi={bilgi}
                  oturumNotu={oturumNotu}
                  girisYap={girisYap}
                />}

            {/* Sahte model uyarısı giriş ekranında da görünür: demoyu
                izleyen kişi sisteme bakmadan gerçek bir modelin
                çalıştığını sanmamalı (ana talimat Bölüm 9.5). */}
            <div className="mt-6"><SahteModelUyarisi /></div>

            {/* TANITIM METNİ FORMUN ALTINDA — bilinçli.

                Masaüstünde anlatı solda, form sağda; ikisi aynı anda
                görünür. Telefonda ise alt alta gelmek zorundalar. Anlatı
                üste konursa her gün giriş yapan saha personeli formu
                görmek için onu her seferinde geçmek zorunda kalır.
                Kimlik (görsel + başlık) üstte kalır, açıklama aşağı
                iner: arayan bulur, aramayan formla karşılaşır. */}
            <div className="lg:hidden mt-8 pt-8 border-t border-kenar">
              <Ozellikler kompakt />
              <p className="text-xs text-metin-4 leading-relaxed mt-7">
                {KUNYE}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function GirisFormu({ kayitEkranina, bilgi, oturumNotu, girisYap }: {
  kayitEkranina: () => void
  bilgi: string
  oturumNotu: string
  girisYap: (e: string, p: string) => Promise<void>
}) {
  const [eposta, setEposta] = useState('')
  const [parola, setParola] = useState('')
  const [hata, setHata] = useState('')
  const [bekliyor, setBekliyor] = useState(false)

  async function gonder(e: React.FormEvent) {
    e.preventDefault()
    setHata(''); setBekliyor(true)
    try {
      await girisYap(eposta, parola)
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'İşlem başarısız')
    } finally {
      setBekliyor(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold tracking-tight">Giriş yap</h2>
      <p className="text-sm text-metin-3 mt-1 mb-7">
        Kurumsal hesabınızla oturum açın.
      </p>

      <form onSubmit={gonder} className="space-y-4">
        <Alan etiket="E-posta">
          <input value={eposta} onChange={(e) => setEposta(e.target.value)}
            type="email" className={girdiSinifi} autoComplete="username"
            placeholder="ad.soyad@kurum.gov.tr" required />
        </Alan>
        <ParolaAlani etiket="Parola" deger={parola} degisti={setParola}
          tamamlama="current-password" />

        {/* Oturum kendiliğinden düştüyse nedeni burada söylenir. */}
        {!hata && oturumNotu && (
          <p role="status" className="text-uyari text-sm bg-uyari/10
            border border-uyari/30 rounded-md px-3 py-2.5 leading-relaxed">
            {oturumNotu}
          </p>
        )}

        {/* Kayıt tamamlandıysa sonucu BURADA görür: kayıt ekranından
            döndüğü için mesaj onu giriş ekranında karşılar. */}
        {bilgi && (
          <p role="status" className="flex items-start gap-2 text-olumlu
            text-sm bg-olumlu/10 border border-olumlu/30 rounded-md
            px-3 py-2.5 leading-relaxed">
            <Ikon.Onayla boyut={16} className="mt-0.5 shrink-0" />
            <span>{bilgi}</span>
          </p>
        )}

        {hata && <Hata mesaj={hata} />}

        <Buton type="submit" disabled={bekliyor} className="w-full">
          {bekliyor ? 'İşleniyor…' : 'Giriş yap'}
        </Buton>
      </form>

      <div className="mt-6 pt-5 border-t border-kenar">
        <p className="text-sm text-metin-3 mb-3">Kurumsal hesabınız yok mu?</p>
        <Buton tur="ikincil" className="w-full" onClick={kayitEkranina}
          ikon={<Ikon.Kullanici boyut={15} />}>
          Hesap oluştur
        </Buton>
      </div>
    </div>
  )
}

/**
 * Kayıt ekranı — giriş formunun bir kipi DEĞİL, kendi ekranı.
 *
 * Önceden aynı forma bir alan eklenip başlığı değişiyordu; kullanıcı
 * nereye geldiğini anlamıyor, kaydın ardından ne olacağını hiç
 * öğrenmiyordu. Burada süreç açıkça yazılı: hesap onay bekler, rolü
 * yönetici atar, onaya kadar giriş yapılamaz.
 *
 * Parola tekrarı EKLENDİ. Tek alanda yazılan bir parolanın yanlış
 * yazıldığı ancak ilk giriş denemesinde anlaşılıyordu — ve o an hesap
 * çoktan onay kuyruğuna girmiş oluyordu.
 */
function KayitFormu({ girisEkranina, tamamlandi }: {
  girisEkranina: () => void
  tamamlandi: (mesaj: string) => void
}) {
  const [ad, setAd] = useState('')
  const [eposta, setEposta] = useState('')
  const [parola, setParola] = useState('')
  const [parolaTekrar, setParolaTekrar] = useState('')
  const [hata, setHata] = useState('')
  const [bekliyor, setBekliyor] = useState(false)

  const uzunlukTamam = parola.length >= PAROLA_ASGARI
  const eslesiyor = parola.length > 0 && parola === parolaTekrar
  const adTamam = ad.trim().length >= 2

  async function gonder(e: React.FormEvent) {
    e.preventDefault()
    // Kontroller sunucudakilerin AYNISI; amaç sunucunun yerine geçmek
    // değil, kullanıcıyı gönderdikten sonra değil önce uyarmak.
    if (!uzunlukTamam) {
      setHata(`Parola en az ${PAROLA_ASGARI} karakter olmalıdır.`)
      return
    }
    if (!eslesiyor) {
      setHata('İki parola aynı değil. Kontrol edip tekrar yazın.')
      return
    }
    setHata(''); setBekliyor(true)
    try {
      await api.kayit({ eposta, parola, ad })
      tamamlandi(
        `${eposta} için kaydınız alındı. Hesabınız yönetici onayı ve rol `
        + 'ataması bekliyor; onaylandıktan sonra buradan giriş yapabilirsiniz.',
      )
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'İşlem başarısız')
    } finally {
      setBekliyor(false)
    }
  }

  return (
    <div>
      <Buton tur="sessiz" boyut="kucuk" onClick={girisEkranina}
        className="mb-4 -ml-2.5" ikon={<Ikon.Geri boyut={14} />}>
        Girişe dön
      </Buton>

      <h2 className="text-xl font-semibold tracking-tight">Hesap oluştur</h2>
      <p className="text-sm text-metin-3 mt-1 mb-6 leading-relaxed">
        Kurumsal e-posta adresinizle başvurun. Hesabınız yönetici onayından
        sonra etkinleşir.
      </p>

      {/* Sürecin tamamı ÖNCEDEN yazılı: kullanıcı formu doldurduktan
          sonra "şimdi ne olacak" diye kalmasın. */}
      <ol className="space-y-2.5 text-sm text-metin-3 mb-7 rounded-kart
        border border-kenar bg-yuzey-2 p-4">
        {[
          'Başvurunuz kaydedilir ve onay kuyruğuna alınır.',
          'Yönetici hesabınızı inceler ve yetkinizi (rolünüzü) atar.',
          'Onaya kadar giriş yapamazsınız; onay sonrası aynı bilgilerle girersiniz.',
        ].map((m, i) => (
          <li key={i} className="flex gap-2.5">
            <span aria-hidden className="shrink-0 w-5 h-5 rounded-full
              bg-yuzey-3 text-metin-3 grid place-items-center
              text-xs sayisal">{i + 1}</span>
            <span className="leading-relaxed">{m}</span>
          </li>
        ))}
      </ol>

      <form onSubmit={gonder} className="space-y-4">
        <Alan etiket="Ad soyad">
          <input value={ad} onChange={(e) => setAd(e.target.value)}
            className={girdiSinifi} autoComplete="name"
            placeholder="Adınız ve soyadınız" required minLength={2} />
        </Alan>

        <Alan etiket="Kurumsal e-posta">
          <input value={eposta} onChange={(e) => setEposta(e.target.value)}
            type="email" className={girdiSinifi} autoComplete="username"
            placeholder="ad.soyad@kurum.gov.tr" required />
        </Alan>

        <ParolaAlani etiket="Parola" deger={parola} degisti={setParola}
          tamamlama="new-password" />

        <ParolaAlani etiket="Parola (tekrar)" deger={parolaTekrar}
          degisti={setParolaTekrar} tamamlama="new-password" />

        {/* Kurallar YAZARKEN güncellenir; kullanıcı gönderip reddedilmeyi
            beklemez. */}
        {(parola.length > 0 || parolaTekrar.length > 0) && (
          <ul className="space-y-1.5" aria-label="Parola kuralları">
            <Kural saglandi={uzunlukTamam}>
              En az {PAROLA_ASGARI} karakter
              {!uzunlukTamam && parola.length > 0 && ` — şu an ${parola.length}`}
            </Kural>
            <Kural saglandi={eslesiyor}>İki parola aynı</Kural>
          </ul>
        )}

        {/* Rol seçimi BİLİNÇLİ OLARAK YOK — Brief Bölüm 3 */}
        <p className="flex items-start gap-2 text-xs text-metin-3 bg-yuzey-2
          border border-kenar rounded-md px-3 py-2.5 leading-relaxed">
          <Ikon.Uyari boyut={14} className="mt-0.5 shrink-0 text-metin-4" />
          <span>
            <strong className="text-metin-2 font-medium">
              Rolünüzü kendiniz seçemezsiniz.
            </strong>{' '}
            Yetki, kamu sistemlerinde olduğu gibi yönetici tarafından atanır
            ve atama işlem geçmişine kaydedilir.
          </span>
        </p>

        {hata && <Hata mesaj={hata} />}

        <Buton type="submit" className="w-full"
          disabled={bekliyor || !adTamam || !uzunlukTamam || !eslesiyor}>
          {bekliyor ? 'Gönderiliyor…' : 'Başvuruyu gönder'}
        </Buton>
      </form>

      <div className="mt-5 pt-5 border-t border-kenar">
        <button
          className="text-sm text-metin-3 hover:text-metin transition-colors
            !min-h-0"
          onClick={girisEkranina}
        >
          Zaten hesabım var — giriş yap
        </button>
      </div>
    </div>
  )
}
