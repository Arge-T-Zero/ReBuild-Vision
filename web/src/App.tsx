import { useState } from 'react'
import { DurumSaglayici, useDurum } from './durum'
import { Buton } from './bilesenler/Temel'
import { Ikon } from './bilesenler/Ikon'
import { Giris } from './sayfalar/Giris'
import { Alanlar } from './sayfalar/Alanlar'
import { AlanDetay } from './sayfalar/AlanDetay'
import { Kuyruk } from './sayfalar/Kuyruk'
import { HaritaSayfasi } from './sayfalar/HaritaSayfasi'
import { Gecmis } from './sayfalar/Gecmis'
import { Yonetici } from './sayfalar/Yonetici'

type Sayfa =
  | { ad: 'alanlar' }
  | { ad: 'alan'; id: number }
  | { ad: 'kuyruk' }
  | { ad: 'harita' }
  | { ad: 'gecmis' }
  | { ad: 'yonetici' }

const ROL_ADI: Record<string, string> = {
  yonetici: 'Yönetici',
  afad: 'AFAD yetkilisi',
  belediye: 'Belediye yetkilisi',
  saha: 'Saha personeli',
  uzman: 'Doğrulayıcı uzman',
  yikim: 'Yıkım firması',
  tesis: 'Tesis operatörü',
}

const DOGRULAYABILIR = new Set(['yonetici', 'uzman'])

function Kabuk() {
  const { kullanici, yukleniyor, durum, cikisYap } = useDurum()
  const [sayfa, setSayfa] = useState<Sayfa>({ ad: 'alanlar' })

  if (yukleniyor) {
    return (
      <div className="min-h-screen flex items-center justify-center text-metin-3">
        Yükleniyor…
      </div>
    )
  }

  if (!kullanici) return <Giris />

  const sekmeler = [
    { ad: 'alanlar', etiket: 'Enkaz alanları', ikon: <Ikon.Alan />, gorunur: true },
    {
      ad: 'kuyruk', etiket: 'İnceleme kuyruğu', ikon: <Ikon.Kuyruk />,
      gorunur: DOGRULAYABILIR.has(kullanici.rol ?? ''),
    },
    { ad: 'harita', etiket: 'Malzeme haritası', ikon: <Ikon.Harita />, gorunur: true },
    { ad: 'gecmis', etiket: 'İşlem geçmişi', ikon: <Ikon.Gecmis />, gorunur: true },
    {
      ad: 'yonetici', etiket: 'Rol onayları', ikon: <Ikon.Kullanici />,
      gorunur: kullanici.rol === 'yonetici',
    },
  ] as const

  const aktif = (ad: string) =>
    sayfa.ad === ad || (ad === 'alanlar' && sayfa.ad === 'alan')

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-kenar bg-yuzey/95 backdrop-blur
        sticky top-0 z-20">
        <div className="max-w-[1400px] mx-auto px-6 h-14 flex items-center gap-8">
          <span className="flex items-center gap-2.5 shrink-0">
            <span aria-hidden className="w-7 h-7 rounded-md bg-vurgu/15
              border border-vurgu/40 grid place-items-center text-vurgu">
              <Ikon.Alan boyut={15} />
            </span>
            <span className="font-semibold tracking-tight">ReBuild Vision</span>
          </span>

          <nav className="flex gap-0.5 grow overflow-x-auto" aria-label="Ana gezinme">
            {sekmeler.filter((s) => s.gorunur).map((s) => (
              <button
                key={s.ad}
                aria-current={sayfa.ad === s.ad ? 'page' : undefined}
                onClick={() => setSayfa({ ad: s.ad } as Sayfa)}
                className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md
                  text-sm whitespace-nowrap transition-colors !min-h-0
                  ${aktif(s.ad)
                    ? 'bg-yuzey-3 text-metin'
                    : 'text-metin-3 hover:text-metin hover:bg-yuzey-2'}`}
              >
                {s.ikon}
                {s.etiket}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-3 shrink-0">
            <span className="text-right leading-tight hidden sm:block">
              <span className="block text-sm text-metin-2">{kullanici.ad}</span>
              <span className="block text-xs text-metin-4">
                {ROL_ADI[kullanici.rol ?? ''] ?? 'Rol atanmadı'}
              </span>
            </span>
            <Buton tur="sessiz" boyut="kucuk" onClick={cikisYap}
              ikon={<Ikon.Cikis boyut={14} />}>
              Çıkış
            </Buton>
          </div>
        </div>
      </header>

      <main className="grow">
        {sayfa.ad === 'alanlar' && (
          <Alanlar acildi={(id) => setSayfa({ ad: 'alan', id })} />
        )}
        {sayfa.ad === 'alan' && (
          <AlanDetay alanId={sayfa.id} geri={() => setSayfa({ ad: 'alanlar' })} />
        )}
        {sayfa.ad === 'kuyruk' && <Kuyruk />}
        {sayfa.ad === 'harita' && <HaritaSayfasi />}
        {sayfa.ad === 'gecmis' && <Gecmis />}
        {sayfa.ad === 'yonetici' && <Yonetici />}
      </main>

      <footer className="border-t border-kenar mt-10">
        <div className="max-w-[1400px] mx-auto px-6 py-4">
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
  )
}

export default function App() {
  return (
    <DurumSaglayici>
      <Kabuk />
    </DurumSaglayici>
  )
}
