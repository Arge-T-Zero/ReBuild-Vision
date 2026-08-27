import type { ReactNode } from 'react'
import type { DogrulamaDurumu } from '../types'

export function Buton({
  children, tur = 'birincil', ...p
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  tur?: 'birincil' | 'ikincil' | 'sessiz'
}) {
  const stiller = {
    birincil: 'bg-vurgu text-taban hover:bg-[#6fb5ff] font-semibold',
    ikincil: 'bg-yuzey-2 text-metin border border-kenar-net hover:border-vurgu',
    sessiz: 'bg-transparent text-metin-2 hover:text-metin hover:bg-yuzey-2',
  }[tur]
  return (
    <button
      {...p}
      className={`px-4 py-2.5 rounded-md transition-colors disabled:opacity-40
        disabled:cursor-not-allowed ${stiller} ${p.className ?? ''}`}
    >
      {children}
    </button>
  )
}

export function Alan({ etiket, ipucu, children }: {
  etiket: string; ipucu?: string; children: ReactNode
}) {
  return (
    <label className="block">
      <span className="block text-sm font-medium text-metin-2 mb-1.5">{etiket}</span>
      {children}
      {ipucu && <span className="block text-xs text-metin-3 mt-1">{ipucu}</span>}
    </label>
  )
}

export const girdiSinifi =
  'w-full px-3 py-2.5 rounded-md bg-yuzey-2 border border-kenar text-metin ' +
  'placeholder:text-metin-3 focus:border-vurgu'

export function Kart({ children, className = '' }: {
  children: ReactNode; className?: string
}) {
  return (
    <div className={`bg-yuzey border border-kenar rounded-lg ${className}`}>
      {children}
    </div>
  )
}

/**
 * Boş durum — yönlendirme yapar, sadece "veri yok" demez
 * (ana talimat Bölüm 9.4).
 */
export function BosDurum({ baslik, aciklama, aksiyon }: {
  baslik: string; aciklama?: string; aksiyon?: ReactNode
}) {
  return (
    <div className="text-center py-12 px-6">
      <p className="text-metin font-medium">{baslik}</p>
      {aciklama && <p className="text-metin-3 text-sm mt-1.5 max-w-md mx-auto">{aciklama}</p>}
      {aksiyon && <div className="mt-4 flex justify-center">{aksiyon}</div>}
    </div>
  )
}

export function Hata({ mesaj }: { mesaj: string }) {
  return (
    <p role="alert" className="text-dikkat text-sm bg-dikkat/10 border border-dikkat/30
      rounded-md px-3 py-2">
      {mesaj}
    </p>
  )
}

/**
 * Doğrulama durumu rozeti — arayüzün omurgası (ana talimat Bölüm 9.1).
 *
 * Renk TEK BAŞINA anlam taşımaz: her rozette metin etiketi vardır
 * (Bölüm 9.3). Çerçeve biçimi de duruma göre değişir, böylece renk
 * körlüğünde ve gri tonlamada da ayrışır.
 */
export function DogrulamaRozeti({ durum }: { durum: DogrulamaDurumu }) {
  const tanim: Record<DogrulamaDurumu, { metin: string; sinif: string }> = {
    beklemede: {
      metin: 'Beklemede',
      sinif: 'border-dashed border-kenar-net text-metin-3',
    },
    onaylandi: {
      metin: 'Onaylandı',
      sinif: 'border-solid border-olumlu text-olumlu bg-olumlu/10',
    },
    duzeltildi: {
      metin: 'Düzeltildi',
      sinif: 'border-solid border-vurgu text-vurgu bg-vurgu/10',
    },
    belirsiz: {
      metin: 'Belirsiz',
      sinif: 'border-solid border-uyari text-uyari bg-uyari/10',
    },
  }
  const t = tanim[durum]
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded
      border-2 text-xs font-medium ${t.sinif}`}>
      {durum === 'duzeltildi' && <span aria-hidden>✎</span>}
      {durum === 'belirsiz' && <span aria-hidden>?</span>}
      {durum === 'onaylandi' && <span aria-hidden>✓</span>}
      {t.metin}
    </span>
  )
}

/**
 * 'Ön tahmin' etiketi — HER model çıktısında görünür, istisnasız
 * (ana talimat Bölüm 1.4).
 */
export function OnTahminEtiketi() {
  return (
    <span className="inline-block px-2 py-0.5 rounded bg-yuzey-2 border border-kenar-net
      text-[11px] uppercase tracking-wide text-metin-2 font-medium">
      ön tahmin
    </span>
  )
}

/**
 * Kapsam uyarısı — ana talimat Bölüm 1.3.
 * Sonuç ekranında ve harita lejandında YAZILI olarak bulunur.
 */
export function KapsamUyarisi({ metin }: { metin: string }) {
  return (
    <p className="text-xs text-metin-3 border-l-2 border-kenar-net pl-3 py-1">
      {metin}
    </p>
  )
}
