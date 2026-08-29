import type { ReactNode } from 'react'
import type { DogrulamaDurumu } from '../types'
import { Ikon } from './Ikon'

export function Buton({
  children, tur = 'birincil', boyut = 'normal', ikon, ...p
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  tur?: 'birincil' | 'ikincil' | 'sessiz' | 'tehlike'
  boyut?: 'normal' | 'kucuk'
  ikon?: ReactNode
}) {
  const stiller = {
    birincil:
      'bg-marka text-taban font-semibold hover:bg-marka-2 ' +
      'shadow-[0_1px_2px_rgba(0,0,0,0.4)]',
    ikincil:
      'bg-yuzey-3 text-metin border border-kenar-net hover:border-kenar-parlak ' +
      'hover:bg-[#2a3140]',
    sessiz: 'bg-transparent text-metin-2 hover:text-metin hover:bg-yuzey-2',
    tehlike:
      'bg-transparent text-dikkat border border-dikkat/40 hover:bg-dikkat/10',
  }[tur]

  // Küçük boyutta bile dokunma hedefi 32px'in altına inmez; ölçümde
  // 'Çıkış' düğmesi 24px çıkmıştı (WCAG 2.5.5).
  const olcu = boyut === 'kucuk'
    ? 'px-2.5 py-1.5 text-xs min-h-8 gap-1.5'
    : 'px-3.5 py-2 text-sm gap-2'

  return (
    <button
      {...p}
      className={`inline-flex items-center justify-center rounded-md
        transition-colors disabled:opacity-40 disabled:cursor-not-allowed
        ${olcu} ${stiller} ${p.className ?? ''}`}
    >
      {ikon}
      {children}
    </button>
  )
}

export function Alan({ etiket, ipucu, children }: {
  etiket: string; ipucu?: string; children: ReactNode
}) {
  return (
    <label className="block">
      <span className="block text-xs font-medium text-metin-2 mb-1.5
        uppercase tracking-wide">{etiket}</span>
      {children}
      {ipucu && (
        <span className="block text-xs text-metin-4 mt-1.5 leading-relaxed">
          {ipucu}
        </span>
      )}
    </label>
  )
}

export const girdiSinifi =
  'w-full px-3 py-2.5 rounded-md bg-taban border border-kenar text-metin ' +
  'placeholder:text-metin-4 focus:border-marka focus:bg-yuzey ' +
  'transition-colors text-sm'

export function Kart({ children, className = '', vurgulu = false }: {
  children: ReactNode; className?: string; vurgulu?: boolean
}) {
  return (
    <div className={`bg-yuzey rounded-kart border transition-colors
      ${vurgulu ? 'border-marka/60' : 'border-kenar'}
      shadow-[0_1px_3px_rgba(0,0,0,0.35)] ${className}`}>
      {children}
    </div>
  )
}

export function Baslik({ ustBaslik, baslik, aciklama, sag }: {
  ustBaslik?: string; baslik: string; aciklama?: string; sag?: ReactNode
}) {
  return (
    <div className="flex items-start justify-between gap-6 flex-wrap mb-6">
      <div className="min-w-0">
        {ustBaslik && (
          <p className="text-xs font-medium uppercase tracking-wider
            text-metin-4 mb-1.5">{ustBaslik}</p>
        )}
        <h2 className="text-2xl font-semibold tracking-tight break-words">{baslik}</h2>
        {aciklama && (
          <p className="text-sm text-metin-3 mt-1.5 max-w-2xl leading-relaxed">
            {aciklama}
          </p>
        )}
      </div>
      {sag && <div className="shrink-0">{sag}</div>}
    </div>
  )
}

/**
 * Özet sayı — bir bakışta okunan tek değer.
 *
 * dataviz: bu bir grafik değil, "hero number"; tek bir büyüklüğün işi
 * sayıdır. Sayı `sayisal` sınıfıyla hizalı yazılır.
 */
export function OzetSayi({ deger, etiket, alt, ton = 'notr' }: {
  deger: ReactNode
  etiket: string
  alt?: string
  ton?: 'notr' | 'vurgu' | 'uyari'
}) {
  const renk = {
    notr: 'text-metin',
    vurgu: 'text-marka',
    uyari: 'text-uyari',
  }[ton]
  return (
    <div className="px-4 py-3">
      <p className={`text-2xl font-semibold sayisal ${renk}`}>{deger}</p>
      <p className="text-xs text-metin-3 mt-0.5">{etiket}</p>
      {alt && <p className="text-xs text-metin-4 mt-0.5">{alt}</p>}
    </div>
  )
}

/**
 * Boş durum — yönlendirme yapar, sadece "veri yok" demez
 * (ana talimat Bölüm 9.4).
 */
export function BosDurum({ baslik, aciklama, aksiyon, ikon }: {
  baslik: string; aciklama?: string; aksiyon?: ReactNode; ikon?: ReactNode
}) {
  return (
    <div className="text-center py-14 px-6">
      {ikon && (
        <div className="inline-flex items-center justify-center w-11 h-11
          rounded-full bg-yuzey-2 border border-kenar text-metin-4 mb-3">
          {ikon}
        </div>
      )}
      <p className="text-metin font-medium">{baslik}</p>
      {aciklama && (
        <p className="text-metin-3 text-sm mt-2 max-w-md mx-auto leading-relaxed">
          {aciklama}
        </p>
      )}
      {aksiyon && <div className="mt-5 flex justify-center">{aksiyon}</div>}
    </div>
  )
}

export function Hata({ mesaj }: { mesaj: string }) {
  return (
    <p role="alert" className="flex items-start gap-2 text-dikkat text-sm
      bg-dikkat/10 border border-dikkat/30 rounded-md px-3 py-2.5">
      <Ikon.Uyari boyut={16} className="mt-0.5" />
      <span>{mesaj}</span>
    </p>
  )
}

export function Bilgi({ children }: { children: ReactNode }) {
  return (
    <p role="status" className="text-sm bg-marka/10 border border-marka/30
      rounded-md px-3 py-2.5 text-metin-2">
      {children}
    </p>
  )
}

/**
 * Doğrulama durumu rozeti — arayüzün omurgası (ana talimat Bölüm 9.1).
 *
 * Renk TEK BAŞINA anlam taşımaz: her rozette metin etiketi ve ayırt edici
 * bir ikon vardır (Bölüm 9.3). Çerçeve biçimi de duruma göre değişir,
 * böylece gri tonlamada ve renk körlüğünde de ayrışır.
 */
export function DogrulamaRozeti({ durum, boyut = 'normal' }: {
  durum: DogrulamaDurumu; boyut?: 'normal' | 'kucuk'
}) {
  const tanim = {
    beklemede: {
      metin: 'Beklemede',
      sinif: 'border-dashed border-kenar-net text-metin-3',
      ikon: <Ikon.Bekle boyut={12} />,
    },
    onaylandi: {
      metin: 'Onaylandı',
      sinif: 'border-solid border-olumlu/60 text-olumlu bg-olumlu/10',
      ikon: <Ikon.Onayla boyut={12} />,
    },
    duzeltildi: {
      metin: 'Düzeltildi',
      sinif: 'border-solid border-marka/60 text-marka bg-marka/10',
      ikon: <Ikon.Duzelt boyut={12} />,
    },
    belirsiz: {
      metin: 'Belirsiz',
      sinif: 'border-solid border-uyari/60 text-uyari bg-uyari/10',
      ikon: <Ikon.Belirsiz boyut={12} />,
    },
  }[durum]

  return (
    <span className={`inline-flex items-center gap-1 rounded border
      font-medium whitespace-nowrap ${tanim.sinif}
      ${boyut === 'kucuk' ? 'px-1.5 py-0.5 text-[11px]' : 'px-2 py-0.5 text-xs'}`}>
      {tanim.ikon}
      {tanim.metin}
    </span>
  )
}

/**
 * 'Ön tahmin' etiketi — HER model çıktısında görünür, istisnasız
 * (ana talimat Bölüm 1.4).
 */
export function OnTahminEtiketi() {
  return (
    <span className="inline-block px-1.5 py-0.5 rounded bg-yuzey-3
      border border-kenar-net text-[11px] uppercase tracking-wider
      text-metin-3 font-medium whitespace-nowrap">
      ön tahmin
    </span>
  )
}

/** Malzeme sınıfı göstergesi — renk + her zaman metin. */
export function SinifEtiketi({ renk, ad, boyut = 'normal' }: {
  renk: string; ad: string; boyut?: 'normal' | 'kucuk'
}) {
  return (
    <span className="inline-flex items-center gap-2 min-w-0">
      <span aria-hidden className="rounded-[3px] shrink-0"
        style={{
          background: renk,
          width: boyut === 'kucuk' ? 8 : 10,
          height: boyut === 'kucuk' ? 8 : 10,
        }} />
      <span className={`truncate ${boyut === 'kucuk' ? 'text-xs' : ''}`}>
        {ad}
      </span>
    </span>
  )
}

/**
 * Kapsam uyarısı — ana talimat Bölüm 1.3.
 * Sonuç ekranında ve harita lejandında YAZILI olarak bulunur.
 */
export function KapsamUyarisi({ metin }: { metin: string }) {
  return (
    <p className="flex items-start gap-2 text-xs text-metin-3
      border-l-2 border-kenar-net pl-3 py-1 leading-relaxed">
      {metin}
    </p>
  )
}
