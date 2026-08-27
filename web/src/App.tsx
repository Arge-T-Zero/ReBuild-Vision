import { useState } from 'react'
import { DurumSaglayici, useDurum } from './durum'
import { SahteServisRozeti } from './bilesenler/SahteServisRozeti'
import { Buton } from './bilesenler/Temel'
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

  if (!kullanici) {
    return (
      <>
        <SahteServisRozeti durum={durum} />
        <Giris />
      </>
    )
  }

  const sekmeler: { ad: Sayfa['ad']; etiket: string; gorunur: boolean }[] = [
    { ad: 'alanlar', etiket: 'Enkaz alanları', gorunur: true },
    {
      ad: 'kuyruk',
      etiket: 'İnceleme kuyruğu',
      gorunur: DOGRULAYABILIR.has(kullanici.rol ?? ''),
    },
    { ad: 'harita', etiket: 'Malzeme haritası', gorunur: true },
    { ad: 'gecmis', etiket: 'İşlem geçmişi', gorunur: true },
    {
      ad: 'yonetici',
      etiket: 'Rol onayları',
      gorunur: kullanici.rol === 'yonetici',
    },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <SahteServisRozeti durum={durum} />

      <header className="border-b border-kenar bg-yuzey">
        <div className="max-w-6xl mx-auto px-6 py-3 flex items-center gap-6 flex-wrap">
          <span className="font-semibold">ReBuild Vision</span>

          <nav className="flex gap-1 grow" aria-label="Ana gezinme">
            {sekmeler.filter((s) => s.gorunur).map((s) => (
              <Buton
                key={s.ad}
                tur={sayfa.ad === s.ad || (s.ad === 'alanlar' && sayfa.ad === 'alan')
                  ? 'ikincil' : 'sessiz'}
                className="text-sm"
                aria-current={sayfa.ad === s.ad ? 'page' : undefined}
                onClick={() => setSayfa({ ad: s.ad } as Sayfa)}
              >
                {s.etiket}
              </Buton>
            ))}
          </nav>

          <div className="flex items-center gap-3 text-sm">
            <span className="text-metin-2">
              {kullanici.ad}
              <span className="text-metin-3"> · {ROL_ADI[kullanici.rol ?? ''] ?? 'Rol atanmadı'}</span>
            </span>
            <Buton tur="sessiz" className="text-sm" onClick={cikisYap}>Çıkış</Buton>
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

      <footer className="border-t border-kenar py-3 px-6">
        <p className="max-w-6xl mx-auto text-xs text-metin-3">
          Model çıktıları ön tahmindir. Nihai operasyon kararı yetkili kurum ve
          uzmanlar tarafından verilir. Sistem tehlikeli madde teşhisi yapmaz.
          {durum && ` Model metrikleri: ${durum.model_metrikleri}`}
        </p>
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
