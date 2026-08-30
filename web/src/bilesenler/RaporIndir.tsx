import { useState } from 'react'
import { api } from '../api'
import { Buton, Hata } from './Temel'
import { Ikon } from './Ikon'

/**
 * Rapor indirme.
 *
 * Dosyaya giden veri ekrandakiyle AYNI kuralları taşır: yalnızca
 * doğrulanmış kayıtlar, uzman düzeltmesi geçerli sınıf, malzeme olmayan
 * sınıflar hariç, hesaplanmamış miktar boş. Ekranda gizlenip dosyada
 * verilseydi kural anlamsız olurdu.
 */
const BICIMLER = [
  { anahtar: 'csv' as const, ad: 'CSV',
    aciklama: 'Excel · Türkçe ayraç ve UTF-8' },
  { anahtar: 'geojson' as const, ad: 'GeoJSON',
    aciklama: 'QGIS ve harita araçları' },
  { anahtar: 'json' as const, ad: 'JSON',
    aciklama: 'Tam kayıt, sistem entegrasyonu' },
]

export function RaporIndir({ alanId }: { alanId?: number }) {
  const [bekleyen, setBekleyen] = useState<string | null>(null)
  const [hata, setHata] = useState('')

  async function indir(bicim: 'json' | 'geojson' | 'csv') {
    setHata(''); setBekleyen(bicim)
    try {
      await api.raporIndir(bicim, alanId)
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'Rapor indirilemedi')
    } finally {
      setBekleyen(null)
    }
  }

  return (
    <div>
      <h2 className="text-sm font-semibold text-metin-2 mb-1">Rapor indir</h2>
      <p className="text-xs text-metin-4 mb-3 leading-relaxed">
        Yalnızca doğrulanmış kayıtlar dışa aktarılır. Ölçüm girilmemiş
        tespitlerde miktar alanı{' '}
        <strong className="text-metin-3">boş kalır</strong> — sıfır değil.
      </p>

      <ul className="space-y-1.5">
        {BICIMLER.map((b) => (
          <li key={b.anahtar}>
            <Buton
              tur="ikincil" className="w-full justify-start"
              disabled={bekleyen !== null}
              onClick={() => indir(b.anahtar)}
              ikon={<Ikon.Yukle boyut={15} className="rotate-180" />}
            >
              <span className="text-left">
                <span className="block">
                  {bekleyen === b.anahtar ? 'Hazırlanıyor…' : b.ad}
                </span>
                <span className="block text-xs text-metin-4 font-normal">
                  {b.aciklama}
                </span>
              </span>
            </Buton>
          </li>
        ))}
      </ul>

      {hata && <div className="mt-3"><Hata mesaj={hata} /></div>}
    </div>
  )
}
