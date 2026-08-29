import { Suspense, lazy, useEffect, useState } from 'react'
import { DurumSaglayici, useDurum } from './durum'
import { TemaSaglayici, useTema } from './tema'
import { GezinmeSaglayici } from './gezinme'
import { Buton } from './bilesenler/Temel'
import { Ikon } from './bilesenler/Ikon'
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

const SAYFA_IKONU: Record<Exclude<SayfaAdi, 'alan'>, React.ReactNode> = {
  yukle: <Ikon.Yukle />,
  alanlar: <Ikon.Alan />,
  kuyruk: <Ikon.Kuyruk />,
  harita: <Ikon.Harita />,
  gecmis: <Ikon.Gecmis />,
  yonetici: <Ikon.Kullanici />,
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
      <span className="sr-only sm:not-sr-only">
        {tema === 'dark' ? 'Açık' : 'Koyu'}
      </span>
    </Buton>
  )
}

function Kabuk() {
  const { kullanici, yukleniyor, durum, cikisYap } = useDurum()
  const tanim = rolTanimi(kullanici?.rol ?? null)
  const [konum, setKonum] = useState<Konum>({ ad: tanim.anaSayfa })

  // Rol belli olduğunda o rolün ana sayfasına git: saha personeli doğrudan
  // görüntü yükleme ekranına, uzman inceleme kuyruğuna düşer.
  useEffect(() => {
    if (kullanici) setKonum({ ad: rolTanimi(kullanici.rol).anaSayfa })
  }, [kullanici?.id, kullanici?.rol])

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
    git: (s: Exclude<SayfaAdi, 'alan'>) => setKonum({ ad: s }),
    alanaGit: (id: number) => setKonum({ ad: 'alan', id }),
    // Menüsünde olmayan bir sayfaya yönlendirmek anlamsız olurdu.
    erisilebilir: (s: Exclude<SayfaAdi, 'alan'>) => tanim.menu.includes(s),
  }

  return (
    <GezinmeSaglayici deger={gezinme}>
    <div className="min-h-screen flex flex-col">
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
          <nav className="hidden sm:flex gap-0.5 grow overflow-x-auto"
            aria-label="Ana gezinme">
            {tanim.menu.map((s) => (
              <button
                key={s}
                aria-current={konum.ad === s ? 'page' : undefined}
                onClick={() => setKonum({ ad: s })}
                className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md
                  text-sm whitespace-nowrap transition-colors !min-h-0
                  ${aktif(s)
                    ? 'bg-yuzey-3 text-metin'
                    : 'text-metin-3 hover:text-metin hover:bg-yuzey-2'}`}
              >
                {SAYFA_IKONU[s]}
                {SAYFA_ETIKETI[s]}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-2 shrink-0">
            <TemaDugmesi />
            <span className="text-right leading-tight hidden md:block">
              <span className="block text-sm text-metin-2">{kullanici.ad}</span>
              <span className="block text-xs text-metin-4">{tanim.ad}</span>
            </span>
            <Buton tur="sessiz" boyut="kucuk" onClick={cikisYap}
              ikon={<Ikon.Cikis boyut={14} />}>
              <span className="sr-only sm:not-sr-only">Çıkış</span>
            </Buton>
          </div>
        </div>
      </header>

      {/* Mobil alt gezinme — bütün sekmeler aynı anda görünür ve başparmak
          erişimindedir. Sekme sayısı en fazla beştir (yönetici rolü). */}
      <nav aria-label="Ana gezinme"
        className="sm:hidden fixed bottom-0 inset-x-0 z-30 bg-yuzey
          border-t border-kenar pb-[env(safe-area-inset-bottom)]">
        <ul className="grid" style={{
          gridTemplateColumns: `repeat(${tanim.menu.length}, minmax(0, 1fr))`,
        }}>
          {tanim.menu.map((s) => (
            <li key={s}>
              <button
                aria-current={konum.ad === s ? 'page' : undefined}
                onClick={() => setKonum({ ad: s })}
                className={`w-full flex flex-col items-center justify-center
                  gap-1 py-2 text-[11px] leading-none transition-colors
                  ${aktif(s)
                    ? 'text-marka'
                    : 'text-metin-3 hover:text-metin'}`}
              >
                {SAYFA_IKONU[s]}
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
      <main className="grow pb-20 sm:pb-0">
        <Suspense fallback={
          <div className="p-10 text-center text-metin-3 text-sm">Yükleniyor…</div>
        }>
        {konum.ad === 'yukle' && <Yukle />}
        {konum.ad === 'alanlar' && (
          <Alanlar acildi={(id) => setKonum({ ad: 'alan', id })} />
        )}
        {konum.ad === 'alan' && (
          <AlanDetay alanId={konum.id}
            geri={() => setKonum({ ad: tanim.anaSayfa })} />
        )}
        {konum.ad === 'kuyruk' && <Kuyruk />}
        {konum.ad === 'harita' && <HaritaSayfasi />}
        {konum.ad === 'gecmis' && <Gecmis />}
        {konum.ad === 'yonetici' && <Yonetici />}
        </Suspense>
      </main>

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
