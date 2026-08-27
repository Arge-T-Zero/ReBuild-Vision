import type { ReactNode } from 'react'

/**
 * Sayfa kabuğu — bütün ekranlar aynı genişlik ve boşluğu paylaşır.
 *
 * Önceden her sayfa kendi genişliğini seçiyordu (kimi 1400px, kimi dar bir
 * sütun) ve uygulama tek bir ürün gibi durmuyordu. Genişlik artık tek
 * yerden gelir.
 *
 * `dar` seçeneği okuma ağırlıklı sayfalar içindir (işlem geçmişi, rol
 * onayları): uzun satır okunmayı zorlaştırır.
 */
export function Sayfa({ children, dar = false }: {
  children: ReactNode
  dar?: boolean
}) {
  return (
    <div className={`mx-auto w-full px-5 sm:px-6 py-6 sm:py-8
      ${dar ? 'max-w-3xl' : 'max-w-[1240px]'}`}>
      {children}
    </div>
  )
}

/** Kartların yan yana dizildiği ızgara. */
export function Izgara({ children, sutun = 3 }: {
  children: ReactNode
  sutun?: 2 | 3
}) {
  return (
    <ul className={`grid gap-4 sm:grid-cols-2
      ${sutun === 3 ? 'xl:grid-cols-3' : ''}`}>
      {children}
    </ul>
  )
}

/**
 * Özet şeridi — sayfanın başındaki sayılar.
 * Küçük ekranda alt alta, geniş ekranda yan yana ve aralarında ayraçla.
 */
export function OzetSerit({ children }: { children: ReactNode }) {
  return (
    <div className="mb-6 grid grid-cols-2 sm:grid-cols-4 rounded-kart
      border border-kenar bg-yuzey overflow-hidden
      divide-x divide-y sm:divide-y-0 divide-kenar">
      {children}
    </div>
  )
}
