import { Suspense, lazy, useCallback, useEffect, useRef, useState } from 'react'
import { DurumSaglayici, useDurum } from './durum'
import { TemaSaglayici, useTema } from './tema'
import { GezinmeSaglayici } from './gezinme'
import { Buton } from './bilesenler/Temel'
import { Ikon } from './bilesenler/Ikon'
import { ModelRozeti } from './bilesenler/ModelDurumu'
import { IlkTanitim } from './bilesenler/IlkTanitim'
import { SAYFA_ETIKETI, SAYFA_KISA_ETIKET, rolTanimi } from './roller'
import type { SayfaAdi } from './roller'
import { Giris } from './sayfalar/Giris'
import { Yukle } from './sayfalar/Yukle'
const Alanlar = lazy(() =>
  import('./sayfalar/Alanlar').then((m) => ({ default: m.Alanlar })))
import { AlanDetay } from './sayfalar/AlanDetay'
import { Kuyruk } from './sayfalar/Kuyruk'
// Harita sayfaları Leaflet'i yükler (~150 KB). Giriş ekranında ve
// çoğu sayfada gerekmediği için ayrı parçaya alındı.
const HaritaSayfasi = lazy(() =>
  import('./sayfalar/HaritaSayfasi').then((m) => ({ default: m.HaritaSayfasi })))
import { Gecmis } from './sayfalar/Gecmis'
import { Yonetici } from './sayfalar/Yonetici'

type Konum = { ad: Exclude<SayfaAdi, 'alan'> } | { ad: 'alan'; id: number }

/**
 * ADRES YÖNLENDİRMESİ.
 *
 * ⚠️ Uygulamanın hiç adresi yoktu: bütün ekranlar `/` üzerinde duruyor,
 * gezinme yalnızca React durumunda tutuluyordu. Üç sonucu vardı ve
 * üçü de bir kamu aracı için ağırdır:
 *
 *  1. TARAYICI GERİ DÜĞMESİ KULLANICIYI UYGULAMADAN ATIYORDU. Ölçüldü:
 *     alan detayındayken geri → `about:blank`. Telefonda geri hareketi
 *     ana gezinme yöntemidir; saha personeli bir kez kaydırınca
 *     uygulamadan çıkıyordu.
 *  2. Bir sahanın bağlantısı PAYLAŞILAMIYORDU. "Şu sahaya bak" demek
 *     kurumlar arası çalışmanın en sık ihtiyacı; adres hep aynıydı.
 *  3. Sayfa yenilenince kullanıcı bulunduğu yeri kaybediyordu.
 *
 * Yönlendirme için kütüphane EKLENMEDİ: History API doğrudan
 * kullanılıyor. Yeni bir bağımlılık, projenin lisans denetiminden
 * geçmesi gereken bir kalem daha demek olurdu (docs/lisans-analizi.md).
 *
 * Derin bağlantı üretimde `vercel.json` içindeki yeniden yazma kuralıyla
 * çalışır (`/((?!api/).*) → /index.html`).
 */
const YOL: Record<Exclude<SayfaAdi, 'alan'>, string> = {
  yukle: '/yukle',
  alanlar: '/alanlar',
  kuyruk: '/kuyruk',
  harita: '/harita',
  gecmis: '/gecmis',
  yonetici: '/roller',
}

function konumYolu(k: Konum): string {
  return k.ad === 'alan' ? `/alan/${k.id}` : YOL[k.ad]
}

/**
 * Adresten konum. Rolün menüsünde olmayan bir sayfaya derin bağlantı
 * gelirse ana sayfaya düşer — adres çubuğuna yazılan bir yol, sunucudaki
 * yetki kontrolünün yerine geçmez ama arayüzde de boş ekran açmamalı.
 */
function yolKonumu(yol: string, menu: Exclude<SayfaAdi, 'alan'>[],
  anaSayfa: Exclude<SayfaAdi, 'alan'>): Konum {
  const alan = yol.match(/^\/alan\/(\d+)$/)
  if (alan) return { ad: 'alan', id: Number(alan[1]) }
  const giris = (Object.keys(YOL) as Exclude<SayfaAdi, 'alan'>[])
    .find((s) => YOL[s] === yol)
  if (giris && menu.includes(giris)) return { ad: giris }
  return { ad: anaSayfa }
}

// Üst çubuk (masaüstü) ve alt çubuk (dar ekran) aynı ikonları FARKLI
// boyutta kullanır: dokunmatikte simge parmakla hedeflenir, imleçle
// değil. Alt çubukta 22 px, üstte 18 px.
const SAYFA_IKON_BILESENI: Record<
  Exclude<SayfaAdi, 'alan'>, (p: { boyut: number }) => React.ReactElement
> = {
  yukle: Ikon.Yukle,
  alanlar: Ikon.Alan,
  kuyruk: Ikon.Kuyruk,
  harita: Ikon.Harita,
  gecmis: Ikon.Gecmis,
  yonetici: Ikon.Kullanici,
}

function sayfaIkonu(s: Exclude<SayfaAdi, 'alan'>, boyut: number) {
  const B = SAYFA_IKON_BILESENI[s]
  return <B boyut={boyut} />
}

function TemaDugmesi() {
  const { tema, temaDegistir } = useTema()
  return (
    <Buton
      tur="sessiz" boyut="kucuk" onClick={temaDegistir}
      aria-label={tema === 'dark' ? 'Açık temaya geç' : 'Koyu temaya geç'}
      title={tema === 'dark'
        ? 'Açık tema — güneş altında daha okunur'
        : 'Koyu tema — düşük ışıkta daha okunur'}
      ikon={tema === 'dark' ? <Ikon.Gunes boyut={15} /> : <Ikon.Ay boyut={15} />}
    >
      {/* Etiket yalnızca geniş ekranda; dar masaüstünde bu iki kelime,
          menünün son sekmesinin sığmasına engel oluyordu. */}
      <span className="sr-only xl:not-sr-only">
        {tema === 'dark' ? 'Açık' : 'Koyu'}
      </span>
    </Buton>
  )
}

function Kabuk() {
  const { kullanici, yukleniyor, durum, cikisYap } = useDurum()
  const tanim = rolTanimi(kullanici?.rol ?? null)
  const [konum, setKonumIc] = useState<Konum>({ ad: tanim.anaSayfa })
  const menuRef = useRef<HTMLElement>(null)
  // Açılıştaki adres. Kullanıcı bilgisi sonradan geldiği için derin
  // bağlantı ancak rol belli olunca çözülebilir; o ana kadar saklanır.
  const ilkYol = useRef(window.location.pathname)

  const konumaGit = useCallback((k: Konum, degistir = false) => {
    setKonumIc(k)
    const yol = konumYolu(k)
    if (window.location.pathname === yol) return
    if (degistir) window.history.replaceState(null, '', yol)
    else window.history.pushState(null, '', yol)
  }, [])

  // Geri/ileri düğmesi. Adres değişince ekran onu izler.
  useEffect(() => {
    const t = rolTanimi(kullanici?.rol ?? null)
    const dinleyici = () => setKonumIc(
      yolKonumu(window.location.pathname, t.menu, t.anaSayfa),
    )
    window.addEventListener('popstate', dinleyici)
    return () => window.removeEventListener('popstate', dinleyici)
  }, [kullanici?.rol])

  // Sekme başlığı ekranı söyler. Tek bir "ReBuild Vision" başlığı,
  // birden çok sekme açan bir kullanıcıya hangisinin ne olduğunu
  // söylemiyordu.
  useEffect(() => {
    const ad = konum.ad === 'alan' ? 'Enkaz alanı' : SAYFA_ETIKETI[konum.ad]
    document.title = kullanici
      ? `${ad} · ReBuild Vision`
      : 'Giriş · ReBuild Vision'
  }, [konum, kullanici])

  // Menü gerçekten taşıyor mu? Taşıyorsa sağ kenara soluklaşma konur.
  // Sabit bir soluklaşma, her şey sığdığında da son sekmeyi
  // soluklaştırırdı; ölçmeden karar verilemez.
  useEffect(() => {
    const el = menuRef.current
    if (!el) return
    const olc = () => el.setAttribute(
      'data-kayar', el.scrollWidth > el.clientWidth + 1 ? 'evet' : 'hayir',
    )
    olc()
    const g = new ResizeObserver(olc)
    g.observe(el)
    return () => g.disconnect()
  }, [tanim.menu.length])

  // Rol belli olduğunda: derin bağlantı varsa ORAYA, yoksa o rolün ana
  // sayfasına. Saha personeli doğrudan görüntü yükleme ekranına, uzman
  // inceleme kuyruğuna düşer.
  useEffect(() => {
    if (!kullanici) return
    const t = rolTanimi(kullanici.rol)
    konumaGit(yolKonumu(ilkYol.current, t.menu, t.anaSayfa), true)
    // Bir kez çözüldükten sonra rol değişimi ana sayfaya götürsün.
    ilkYol.current = '/'
  }, [kullanici?.id, kullanici?.rol, konumaGit])

  if (yukleniyor) {
    return (
      <div className="min-h-screen grid place-items-center text-metin-3">
        Yükleniyor…
      </div>
    )
  }

  if (!kullanici) return <Giris />

  const aktif = (ad: string) =>
    konum.ad === ad || (ad === 'alanlar' && konum.ad === 'alan')

  const gezinme = {
    git: (s: Exclude<SayfaAdi, 'alan'>) => konumaGit({ ad: s }),
    alanaGit: (id: number) => konumaGit({ ad: 'alan', id }),
    // Menüsünde olmayan bir sayfaya yönlendirmek anlamsız olurdu.
    erisilebilir: (s: Exclude<SayfaAdi, 'alan'>) => tanim.menu.includes(s),
  }

  return (
    <GezinmeSaglayici deger={gezinme}>
    <div className="min-h-screen flex flex-col">
      {/* Klavye kullanıcısı her sayfada beş sekmelik menüyü geçmek zorunda
          kalıyordu; bu bağlantı odaklanınca görünür olur ve doğrudan
          içeriğe atlar. */}
      <a href="#icerik"
        className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2
          focus:z-50 focus:px-4 focus:py-2 focus:rounded-md focus:bg-marka
          focus:text-taban focus:font-semibold">
        İçeriğe geç
      </a>

      <header className="border-b border-kenar bg-yuzey sticky top-0 z-20">
        <div className="max-w-[1240px] mx-auto px-5 sm:px-6 h-14
          flex items-center gap-4 sm:gap-8">
          <span className="flex items-center gap-2.5 shrink-0">
            <span aria-hidden className="w-7 h-7 rounded-md bg-marka/15
              border border-marka/40 grid place-items-center text-marka">
              <img src="/logo-isaret.svg" alt="" aria-hidden width={16} height={16} />
            </span>
            <span className="font-semibold tracking-tight hidden sm:inline">
              ReBuild Vision
            </span>
          </span>

          {/* Üst menü yalnızca sm ve üzerinde. 360 px'te beş sekme bu
              çubuğa sığmıyor, yatay kaydırmaya düşüyor ve kaydırılabildiğine
              dair hiçbir ipucu olmadığı için sekmelerin çoğu görünmez
              kalıyordu. Mobilde yerini alttaki sabit çubuk alır. */}
          {/* ÜST MENÜ YALNIZCA lg VE ÜZERİNDE.

              Eşik `sm` (640 px) idi ve o aralıkta menü ÇALIŞMIYORDU:
              768 px'te dört sekmelik 610 px'lik içeriğe 177 px yer
              kalıyor, sekmeler sessizce kırpılıyor ve kaydırılabildiğine
              dair hiçbir ipucu bulunmuyordu — yani bir tablet
              kullanıcısı menünün çoğunu hiç göremiyordu. Eşik
              ölçülerek `lg`ye çekildi; altında yerini alttaki sabit
              çubuk alır (o çubuk zaten kısa etiketlerle tasarlanmıştı).

              Etiket KISA addır ("Kuyruk"), tam ad değil. Kapsayıcı
              1240 px'te sınırlı; içine marka, beş sekme, model rozeti,
              tema, kullanıcı ve çıkış giriyor. Tam adlarla beş sekme
              737 px istiyor, eldeki yer 614 px — yani tam ad hiçbir
              ekran genişliğinde sığmıyor, çünkü sınır ekran değil
              kapsayıcı. Kısa etiketler alt çubuk için zaten "ikonuyla
              birlikte tek başına anlaşılır" olacak biçimde seçilmişti.
              Tam ad `aria-label` ve `title` ile korunur. */}
          <nav ref={menuRef}
            className="menu-kayan hidden lg:flex gap-0.5 grow min-w-0
            overflow-x-auto" aria-label="Ana gezinme">
            {tanim.menu.map((s) => (
              <button
                key={s}
                aria-current={konum.ad === s ? 'page' : undefined}
                aria-label={SAYFA_ETIKETI[s]}
                title={SAYFA_ETIKETI[s]}
                /* İlk giriş turu hedefi. Aynı değer alt çubukta da var;
                   tur, görünür olanı ÖLÇEREK seçer. */
                data-tanitim={s}
                onClick={() => konumaGit({ ad: s })}
                /* Sekmeler büyütüldü: 14 px yazı + 16 px ikon bir kamu
                   aracı için küçüktü, tıklama hedefi de dardı. */
                className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-md
                  text-[15px] whitespace-nowrap transition-colors !min-h-0
                  ${aktif(s)
                    ? 'bg-yuzey-3 text-metin font-medium'
                    : 'text-metin-3 hover:text-metin hover:bg-yuzey-2'}`}
              >
                {sayfaIkonu(s, 18)}
                <span aria-hidden>{SAYFA_KISA_ETIKET[s]}</span>
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-2 shrink-0">
            {/* Sahte model servisi rozeti — kalıcı ve her ekranda
                (README taahhüdü, ana talimat Bölüm 9.5). */}
            <ModelRozeti />
            <TemaDugmesi />
            {/* Menü mobilde alttaki çubuğa taşındığı için üst çubukta yer
                açıldı: kullanıcı artık hangi hesapla ve hangi rolle
                bağlı olduğunu her ekran boyutunda görüyor. */}
            <span className="text-right leading-tight min-w-0">
              <span className="block text-sm text-metin-2 truncate max-w-[6.5rem]
                sm:max-w-[8rem] xl:max-w-[10rem]">{kullanici.ad}</span>
              <span className="block text-xs text-metin-4 truncate max-w-[6.5rem]
                sm:max-w-[8rem] xl:max-w-[10rem]">{tanim.ad}</span>
            </span>
            <Buton tur="sessiz" boyut="kucuk" onClick={cikisYap}
              ikon={<Ikon.Cikis boyut={14} />}>
              <span className="sr-only xl:not-sr-only">Çıkış</span>
            </Buton>
          </div>
        </div>
      </header>

      {/* Dar ekran gezinmesi — bütün sekmeler aynı anda görünür ve
          başparmak erişimindedir. Sekme sayısı en fazla beştir (yönetici
          rolü). Telefonun yanında tabletler ve dar dizüstü ekranlar da
          buraya düşer: üst çubuk lg'nin altında sekmeleri taşıyamıyor. */}
      <nav aria-label="Ana gezinme"
        className="lg:hidden fixed bottom-0 inset-x-0 z-30 bg-yuzey
          border-t border-kenar pb-[env(safe-area-inset-bottom)]">
        <ul className="grid" style={{
          gridTemplateColumns: `repeat(${tanim.menu.length}, minmax(0, 1fr))`,
        }}>
          {tanim.menu.map((s) => (
            <li key={s}>
              {/* Dokunma hedefi büyütüldü: simge 16 → 22 px, yükseklik
                  ~48 → ~58 px. Eldivenli parmakla ve sallanan bir araçta
                  kullanılacak; WCAG 2.5.5'in 44 px asgarisi burada
                  taban, hedef değil. */}
              <button
                aria-current={konum.ad === s ? 'page' : undefined}
                data-tanitim={s}
                onClick={() => konumaGit({ ad: s })}
                className={`w-full flex flex-col items-center justify-center
                  gap-1.5 py-2.5 text-xs leading-none transition-colors
                  ${aktif(s)
                    ? 'text-marka font-medium'
                    : 'text-metin-3 hover:text-metin'}`}
              >
                {sayfaIkonu(s, 22)}
                <span className="truncate max-w-full px-0.5">
                  {SAYFA_KISA_ETIKET[s]}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Alt çubuk sabit konumlu; içeriğin son satırı altında kalmasın diye
          mobilde çubuk yüksekliği kadar boşluk bırakılır. */}
      <main id="icerik" className="grow pb-20 lg:pb-0">
        <Suspense fallback={
          <div className="p-10 text-center text-metin-3 text-sm">Yükleniyor…</div>
        }>
        {konum.ad === 'yukle' && <Yukle />}
        {konum.ad === 'alanlar' && (
          <Alanlar acildi={(id) => konumaGit({ ad: 'alan', id })} />
        )}
        {konum.ad === 'alan' && (
          <AlanDetay alanId={konum.id}
            geri={() => konumaGit({ ad: tanim.anaSayfa })} />
        )}
        {konum.ad === 'kuyruk' && <Kuyruk />}
        {konum.ad === 'harita' && <HaritaSayfasi />}
        {konum.ad === 'gecmis' && <Gecmis />}
        {konum.ad === 'yonetici' && <Yonetici />}
        </Suspense>
      </main>

      {/* Tur SAYFA İÇERİĞİNİN DIŞINDA durur: menü öğelerini aydınlatıyor
          ve adım değiştikçe sayfa da değişiyor; bir sayfanın içine
          konsaydı her geçişte yeniden kurulup baştan başlardı. */}
      <IlkTanitim git={gezinme.git} />

      <footer className="border-t border-kenar mt-10">
        <div className="max-w-[1240px] mx-auto px-5 sm:px-6 py-4">
          <p className="text-xs text-metin-4 leading-relaxed max-w-4xl">
            Model çıktıları <strong className="text-metin-3">ön tahmindir</strong>;
            nihai operasyon kararı yetkili kurum ve uzmanlar tarafından verilir.
            Sistem tehlikeli madde teşhisi yapmaz ve yalnızca görünür yüzeyi
            değerlendirir.
            {durum && <> Model metrikleri: {durum.model_metrikleri}.</>}
          </p>
        </div>
      </footer>
    </div>
    </GezinmeSaglayici>
  )
}

export default function App() {
  return (
    <TemaSaglayici>
      <DurumSaglayici>
        <Kabuk />
      </DurumSaglayici>
    </TemaSaglayici>
  )
}
