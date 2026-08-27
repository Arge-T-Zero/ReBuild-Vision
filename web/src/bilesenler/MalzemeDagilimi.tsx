import type { SinifTanimi } from '../types'

/**
 * Malzeme dağılımı — yatay çubuk grafik.
 *
 * Form seçimi (dataviz): iş, kategoriler arası BÜYÜKLÜK karşılaştırması →
 * ortak taban çizgisine oturan yatay çubuk. Pasta grafiği kullanılmaz;
 * dokuz dilim okunmaz ve açı karşılaştırması uzunluk karşılaştırmasından
 * kötüdür.
 *
 * Renkler `siniflar.json`'dan gelir ve doğrulayıcıdan geçmiştir. Renk TEK
 * BAŞINA anlam taşımaz: her satırda sınıf adı ve sayı yazılıdır — bu aynı
 * zamanda renk körlüğü ayrımının 6–8 bandında olmasını meşru kılan ikincil
 * kodlamadır.
 */
export function MalzemeDagilimi({
  dagilim, siniflar, secili, secildi,
}: {
  dagilim: { sinif: string; adet: number }[]
  siniflar: Map<string, SinifTanimi>
  secili: Set<string>
  secildi: (sinif: string) => void
}) {
  if (dagilim.length === 0) return null

  const enBuyuk = Math.max(...dagilim.map((d) => d.adet))
  const toplam = dagilim.reduce((t, d) => t + d.adet, 0)
  const sirali = [...dagilim].sort((a, b) => b.adet - a.adet)

  return (
    <ul className="space-y-1">
      {sirali.map((d) => {
        const tanim = siniflar.get(d.sinif)
        const acik = secili.size === 0 || secili.has(d.sinif)
        const oran = (d.adet / enBuyuk) * 100
        const yuzde = Math.round((d.adet / toplam) * 100)

        return (
          <li key={d.sinif}>
            <button
              onClick={() => secildi(d.sinif)}
              aria-pressed={secili.has(d.sinif)}
              title={`${tanim?.gorunen_ad ?? d.sinif}: ${d.adet} doğrulanmış tespit (%${yuzde})`}
              className={`w-full text-left px-2 py-1.5 rounded !min-h-0
                transition-colors hover:bg-yuzey-2
                ${acik ? '' : 'opacity-35'}`}
            >
              <span className="flex items-baseline gap-2 mb-1">
                <span aria-hidden className="w-2.5 h-2.5 rounded-[3px] shrink-0
                  translate-y-0.5"
                  style={{ background: tanim?.renk ?? '#6b7280' }} />
                <span className="text-sm grow truncate">
                  {tanim?.gorunen_ad ?? d.sinif}
                </span>
                <span className="text-sm sayisal text-metin-2">{d.adet}</span>
                <span className="text-xs sayisal text-metin-4 w-9 text-right">
                  %{yuzde}
                </span>
              </span>

              {/* İnce çubuk, tabana oturur, veri ucu yuvarlatılmış. */}
              <span className="block h-1.5 rounded-full bg-yuzey-3 overflow-hidden">
                <span
                  className="block h-full rounded-full"
                  style={{
                    width: `${oran}%`,
                    background: tanim?.renk ?? '#6b7280',
                  }}
                />
              </span>
            </button>
          </li>
        )
      })}
    </ul>
  )
}
