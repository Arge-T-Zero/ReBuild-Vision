import { Buton, Kart, SinifEtiketi } from './Temel'
import { Ikon } from './Ikon'
import type { EnkazAlani, SinifTanimi } from '../types'

/**
 * Enkaz alanı kartı.
 *
 * Önceden kartta yalnızca ad, sorumlu ve koordinat vardı; sahanın durumu
 * hakkında hiçbir şey söylemiyordu. Artık üç şeyi bir bakışta veriyor:
 * sınırın biçimi, doğrulama ilerlemesi ve malzeme dağılımı.
 *
 * Malzeme dağılımı YALNIZCA doğrulanmış kayıtlardan gelir — haritayla
 * aynı kural (ana talimat Bölüm 1.4). Kart, haritanın bilinçli olarak
 * göstermediği sayıları arka kapıdan göstermez.
 */
export function SahaKarti({ alan, siniflar, acildi }: {
  alan: EnkazAlani
  siniflar: Map<string, SinifTanimi>
  acildi: (id: number) => void
}) {
  const oran = alan.tespit_sayisi > 0
    ? alan.dogrulanan_sayisi / alan.tespit_sayisi
    : 0
  const yuzde = Math.round(oran * 100)

  return (
    <Kart className="p-5 h-full flex flex-col">
      <div className="flex items-start justify-between gap-3">
        <h2 className="font-medium leading-snug break-words">{alan.ad}</h2>
        <ErisimRozeti durum={alan.erisim_durumu} />
      </div>

      <div className="mt-4 flex items-start gap-4">
        <SinirKrokisi alan={alan} />

        <dl className="grid grid-cols-2 gap-x-3 gap-y-2 grow min-w-0">
          <div>
            <dt className="text-xs uppercase tracking-wide text-metin-4">
              Görüntü
            </dt>
            <dd className="text-lg font-medium sayisal">{alan.goruntu_sayisi}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wide text-metin-4">
              Tespit
            </dt>
            <dd className="text-lg font-medium sayisal">{alan.tespit_sayisi}</dd>
          </div>
          <div className="col-span-2 min-w-0">
            <dt className="text-xs uppercase tracking-wide text-metin-4">
              Sorumlu
            </dt>
            <dd className="text-sm text-metin-2 truncate">
              {alan.sorumlu || '—'}
            </dd>
          </div>
        </dl>
      </div>

      {/* Doğrulama ilerlemesi — projenin ayırt edici iddiası */}
      {alan.tespit_sayisi > 0 && (
        <div className="mt-4">
          <div className="flex items-baseline justify-between mb-1.5">
            <span className="text-xs text-metin-3">Uzman doğrulaması</span>
            <span className="text-xs sayisal text-metin-2">
              {alan.dogrulanan_sayisi}/{alan.tespit_sayisi} · %{yuzde}
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-yuzey-3 overflow-hidden">
            <div className="h-full rounded-full bg-marka transition-all"
              style={{ width: `${Math.max(2, yuzde)}%` }} />
          </div>
          {alan.inceleme_bekleyen > 0 && (
            <p className="flex items-center gap-1.5 text-xs text-uyari mt-1.5">
              <Ikon.Uyari boyut={12} />
              <span className="sayisal">{alan.inceleme_bekleyen}</span>
              tespit uzman incelemesi bekliyor
            </p>
          )}
        </div>
      )}

      {/* Malzeme dağılımı — yalnızca doğrulanmış kayıtlar */}
      {alan.malzeme_dagilimi.length > 0 && (
        <div className="mt-4">
          <p className="text-xs text-metin-4 mb-1.5">
            Doğrulanmış malzemeler
          </p>
          <MalzemeCubugu dagilim={alan.malzeme_dagilimi} siniflar={siniflar} />
          <ul className="flex flex-wrap gap-x-3 gap-y-1 mt-2">
            {alan.malzeme_dagilimi.slice(0, 3).map((m) => {
              const t = siniflar.get(m.sinif)
              return (
                <li key={m.sinif} className="text-xs text-metin-3">
                  <SinifEtiketi renk={t?.renk ?? '#6b7280'}
                    ad={`${t?.gorunen_ad ?? m.sinif} ${m.adet}`} boyut="kucuk" />
                </li>
              )
            })}
          </ul>
        </div>
      )}

      <div className="grow" />

      <Buton tur="ikincil" className="mt-4 w-full"
        onClick={() => acildi(alan.id)}>
        Alanı aç
      </Buton>
    </Kart>
  )
}

/**
 * Sınır krokisi — sahanın gerçek poligonunu küçük bir SVG olarak çizer.
 *
 * Kart başına bir harita örneği açmak yerine kroki kullanılıyor: on kart
 * on Leaflet örneği demek olurdu ve sayfa ağırlaşırdı. Kroki gerçek
 * geometriyi gösterir, sıfır maliyetlidir.
 */
function SinirKrokisi({ alan }: { alan: EnkazAlani }) {
  const kenar = 76

  if (!alan.sinir || alan.sinir.length < 3) {
    return (
      <div
        className="shrink-0 rounded-md border border-kenar bg-yuzey-2
          grid place-items-center text-metin-4"
        style={{ width: kenar, height: kenar }}
        title={alan.konum
          ? `${alan.konum.enlem.toFixed(4)}, ${alan.konum.boylam.toFixed(4)}`
          : 'Konum girilmedi'}
      >
        <Ikon.Harita boyut={20} />
      </div>
    )
  }

  const enlemler = alan.sinir.map((n) => n.enlem)
  const boylamlar = alan.sinir.map((n) => n.boylam)
  const eMin = Math.min(...enlemler), eMax = Math.max(...enlemler)
  const bMin = Math.min(...boylamlar), bMax = Math.max(...boylamlar)
  const eAralik = eMax - eMin || 1e-9
  const bAralik = bMax - bMin || 1e-9
  const pay = 8
  const ic = kenar - pay * 2

  // En/boy oranını koru: şekil ezilmesin.
  const olcek = Math.min(ic / bAralik, ic / eAralik)
  const gOfset = (kenar - bAralik * olcek) / 2
  const yOfset = (kenar - eAralik * olcek) / 2

  const noktalar = alan.sinir.map((n) => {
    const x = (n.boylam - bMin) * olcek + gOfset
    // Enlem yukarı doğru artar; SVG'de y aşağı doğru artar.
    const y = kenar - ((n.enlem - eMin) * olcek + yOfset)
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')

  return (
    <svg
      width={kenar} height={kenar} viewBox={`0 0 ${kenar} ${kenar}`}
      className="shrink-0 rounded-md border border-kenar bg-yuzey-2"
      role="img"
      aria-label={`Saha sınırı, ${alan.sinir.length - 1} köşeli`}
    >
      <polygon
        points={noktalar}
        fill="var(--u-marka-zemin)"
        stroke="var(--u-marka)"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      {alan.konum && (
        <circle cx={kenar / 2} cy={kenar / 2} r="2.5"
          fill="var(--u-marka)" />
      )}
    </svg>
  )
}

/** Malzeme dağılımı — tek satırlık yığılmış çubuk. */
function MalzemeCubugu({ dagilim, siniflar }: {
  dagilim: { sinif: string; adet: number }[]
  siniflar: Map<string, SinifTanimi>
}) {
  const toplam = dagilim.reduce((t, d) => t + d.adet, 0)
  if (toplam === 0) return null

  return (
    <div className="flex h-2 rounded-full overflow-hidden gap-0.5"
      role="img"
      aria-label={dagilim
        .map((d) => `${siniflar.get(d.sinif)?.gorunen_ad ?? d.sinif} ${d.adet}`)
        .join(', ')}
    >
      {dagilim.map((d) => (
        <div
          key={d.sinif}
          style={{
            width: `${(d.adet / toplam) * 100}%`,
            background: siniflar.get(d.sinif)?.renk ?? '#6b7280',
          }}
        />
      ))}
    </div>
  )
}

function ErisimRozeti({ durum }: { durum: EnkazAlani['erisim_durumu'] }) {
  const t = {
    acik: { m: 'Erişim açık', s: 'border-olumlu/50 text-olumlu bg-olumlu/10' },
    kisitli: { m: 'Kısıtlı', s: 'border-uyari/50 text-uyari bg-uyari/10' },
    kapali: { m: 'Kapalı', s: 'border-dikkat/50 text-dikkat bg-dikkat/10' },
  }[durum]
  return (
    <span className={`shrink-0 px-2 py-0.5 rounded border text-xs
      font-medium whitespace-nowrap ${t.s}`}>
      {t.m}
    </span>
  )
}
