import { useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import { useTema } from '../tema'
import { Alan, Buton, Hata, girdiSinifi } from '../bilesenler/Temel'
import { Ikon } from '../bilesenler/Ikon'
import { SahteModelUyarisi } from '../bilesenler/ModelDurumu'

/**
 * Giriş ve kayıt ekranı.
 *
 * DÜZEN ORTALANMIŞTIR ve her ekran boyutunda AYNIDIR. Önceki düzen ikiye
 * bölünüyordu (solda görsel, sağda form); dar ekranda sol panel tamamen
 * gizlendiği için mobil ile masaüstü başka ürünler gibi duruyordu ve
 * metin fotoğrafın üzerinde kaldığı için okunurluk perdenin gücüne
 * bağlıydı. Kart artık kendi zeminine oturur: kontrast fotoğraftan
 * bağımsız garanti altındadır.
 *
 * İki ekranın GÖRSELİ DE METNİ DE farklıdır. Yalnızca fotoğrafı
 * değiştirip başlığı sabit bırakmak yarım iş olurdu — kullanıcı başka
 * bir yere geldiğini görselden sezip metinden doğrulayamıyordu.
 */

/** Sunucudaki `Field(min_length=8)` ile aynı (api/app/schemas.py). */
const PAROLA_ASGARI = 8

const OZELLIKLER = [
  {
    baslik: 'İnsan denetimli sınıflandırma',
    metin: 'Model çıktıları ön tahmindir; uzman onaylar, düzeltir ya da '
      + 'belirsiz işaretler. İnsanın kararı modelin tahminini geçersiz kılar.',
  },
  {
    baslik: 'Ölçüm yoksa miktar üretilmez',
    metin: 'Sistem dayanağı olmayan tonaj tahmini oluşturmaz. Miktar '
      + 'hesaplandığında tek bir kesin değer değil, belirsizlik aralığı verilir.',
  },
  {
    baslik: 'Her kayıt izlenebilir',
    metin: 'Kimin ne zaman neyi değiştirdiği otomatik kaydedilir. '
      + 'Kayıtlar silinemez ve düzenlenemez.',
  },
]

const KUNYE = 'TEKNOFEST 2026 Sıfır Atık ve Döngüsel Ekonomi Yarışması · '
  + 'Takım Arge-T Zero. Sistem yalnızca görünür yüzeye ilişkin ön '
  + 'değerlendirme yapar ve tehlikeli madde teşhisi yapmaz.'

/**
 * Ekran başına görsel VE metin.
 *
 * Kayıt görseli bilinçli seçildi: ayrıştırılmış malzeme yığınları
 * (ahşap, beton, tuğla, metal) sistemin ne ürettiğini gösteriyor —
 * başvuran kişinin merak ettiği tam olarak budur. Giriş görseli ise
 * ayrıştırılmamış enkazı gösterir: işin başladığı yer.
 *
 * Her iki görsel de depoda hazır ve yapay zekâ ile üretilmiştir
 * (gorseller/README.md); yeni dosya eklenmedi.
 */
const EKRAN = {
  giris: {
    gorsel: '/gorseller/giris-hero.webp',
    baslik: 'Enkaz malzemelerinin görüntü tabanlı ön sınıflandırması ve '
      + 'doğrulanabilir kaynak haritası',
  },
  kayit: {
    gorsel: '/gorseller/ornek-enkaz-3.webp',
    baslik: 'Ayrıştırılan her malzeme, doğrulanmış bir kayda dönüşür',
  },
} as const

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

function Marka() {
  return (
    <span className="flex items-center gap-2.5">
      <span aria-hidden className="w-9 h-9 rounded-lg bg-marka/15
        border border-marka/40 grid place-items-center text-marka shrink-0">
        <img src="/logo-isaret.svg" alt="" aria-hidden width={20} height={20} />
      </span>
      <span className="font-semibold text-lg tracking-tight">ReBuild Vision</span>
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
          biri için konfor değil, gerekliliktir. */}
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

/** Kural göstergesi — renk tek başına anlam taşımaz, ikon da değişir. */
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

export function Giris() {
  const { girisYap, oturumNotu } = useDurum()
  const [kayitModu, setKayitModu] = useState(false)
  const [bilgi, setBilgi] = useState('')

  const ekran = kayitModu ? EKRAN.kayit : EKRAN.giris

  function kipDegistir(kayit: boolean) {
    setKayitModu(kayit)
    setBilgi('')
    window.scrollTo({ top: 0, behavior: 'auto' })
  }

  return (
    <div className="min-h-screen relative">
      {/* Arka plan: İKİ görsel de yüklüdür ve opaklıkla geçiş yapar.
          Tek bir `src` değiştirilseydi yeni dosya inene kadar ekran
          boşalır, geçiş "acayip" görünürdü. Görsel yapay zekâ ile
          üretilmiştir; gerçek bir afet fotoğrafı değildir (Madde 10.7). */}
      <div aria-hidden className="fixed inset-0 overflow-hidden">
        {(['giris', 'kayit'] as const).map((k) => (
          <img
            key={k}
            src={EKRAN[k].gorsel} alt=""
            className="giris-gorsel absolute inset-0 w-full h-full object-cover"
            style={{ opacity: (k === 'kayit') === kayitModu ? 1 : 0 }}
            fetchPriority={k === 'giris' ? 'high' : 'low'}
          />
        ))}
        <div className="giris-perde-tam absolute inset-0" />
      </div>

      <div className="relative min-h-screen flex flex-col items-center
        px-4 py-6 sm:px-6 sm:py-10">
        <div className="w-full max-w-[460px] flex justify-end mb-4">
          <TemaDugmesi />
        </div>

        {/* Kart KENDİ ZEMİNİNE oturur (yarı saydam değil): kontrast
            fotoğraftan bağımsız garanti altındadır. */}
        <main className="w-full max-w-[460px] rounded-kart border border-kenar
          bg-yuzey shadow-[var(--u-golge-ust)] p-6 sm:p-8">
          <Marka />

          {/* `key` ile birlikte içerik her kip değişiminde yeniden
              belirir; ani sıçrama yerine yumuşak geçiş olur. */}
          <div key={kayitModu ? 'kayit' : 'giris'} className="giris-belir">
            {/* Geri bağlantısı BAŞLIĞIN ÜSTÜNDE: aşağıda kalırsa ekranın
                başlığıyla formun başlığı arasına sıkışıyor ve okuma
                sırasını bozuyordu. */}
            {kayitModu && (
              <Buton tur="sessiz" boyut="kucuk" onClick={() => kipDegistir(false)}
                className="mt-4 -ml-2.5" ikon={<Ikon.Geri boyut={14} />}>
                Girişe dön
              </Buton>
            )}

            <h1 className={`text-xl sm:text-[22px] font-semibold tracking-tight
              leading-snug ${kayitModu ? 'mt-3' : 'mt-5'}`}>
              {ekran.baslik}
            </h1>

            <div className="mt-7">
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
            </div>
          </div>

          {/* Sahte model uyarısı her iki ekranda da görünür: demoyu
              izleyen kişi sisteme bakmadan gerçek bir modelin
              çalıştığını sanmamalı (ana talimat Bölüm 9.5). */}
          <div className="mt-6"><SahteModelUyarisi /></div>
        </main>

        {/* Tanıtım YALNIZCA giriş ekranında. Kayıt ekranında yerini üç
            adımlı süreç anlatımı alır; ikisini birden göstermek aynı
            ekranda iki farklı şey öğretmeye çalışmak olurdu. */}
        {!kayitModu && (
          <section aria-label="Sistemin çalışma kuralları"
            className="w-full max-w-[460px] mt-4 rounded-kart border
              border-kenar bg-yuzey p-6 sm:p-8 giris-belir">
            <ul className="space-y-5">
              {OZELLIKLER.map((o) => (
                <li key={o.baslik} className="border-l-2 border-kenar-net pl-4">
                  <p className="font-medium text-metin">{o.baslik}</p>
                  <p className="text-sm text-metin-3 mt-1 leading-relaxed">
                    {o.metin}
                  </p>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* `footer` bilinçli: künye bir yer işaretine ait olmalı.
            Çıplak bir `p` olarak dururken hiçbir yer işaretinin içinde
            değildi (axe: `region`) ve yer işaretlerine göre gezinen bir
            ekran okuyucu kullanıcısı onu atlıyordu. */}
        <footer className="w-full max-w-[460px] mt-4 rounded-kart border
          border-kenar bg-yuzey px-6 py-4">
          <p className="text-xs text-metin-3 leading-relaxed">{KUNYE}</p>
        </footer>
      </div>
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
      <h2 className="text-lg font-semibold tracking-tight">Giriş yap</h2>
      <p className="text-sm text-metin-3 mt-1 mb-6">
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

        {!hata && oturumNotu && (
          <p role="status" className="text-uyari text-sm bg-uyari/10
            border border-uyari/30 rounded-md px-3 py-2.5 leading-relaxed">
            {oturumNotu}
          </p>
        )}

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
 * Parola tekrarı EKLENDİ. Tek alanda yazılan bir parolanın yanlış
 * yazıldığı ancak ilk giriş denemesinde anlaşılıyordu — ve o an hesap
 * çoktan onay kuyruğuna girmiş, yönetici sahibinin giremeyeceği bir
 * hesabı onaylamış oluyordu.
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
      <h2 className="text-lg font-semibold tracking-tight">Hesap oluştur</h2>
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
