import { createContext, useContext } from 'react'
import type { ReactNode } from 'react'
import type { SayfaAdi } from './roller'

/**
 * Sayfa geçişi.
 *
 * Boş durumlar bir sonraki adımı göstermek zorundadır (ana talimat
 * Bölüm 9.4) ve o adım çoğu zaman BAŞKA bir sayfadadır: "doğrulanmış
 * kayıt yok" diyen harita, kullanıcıyı inceleme kuyruğuna yollamalı.
 * Bunu her sayfaya tek tek geri çağrı geçirerek yapmak yerine tek
 * bağlamdan veriyoruz.
 */

interface Baglam {
  git: (sayfa: Exclude<SayfaAdi, 'alan'>) => void
  alanaGit: (id: number) => void
  /** Kullanıcının menüsünde o sayfa var mı — yoksa aksiyon gösterilmez. */
  erisilebilir: (sayfa: Exclude<SayfaAdi, 'alan'>) => boolean
}

const Ctx = createContext<Baglam | null>(null)

export function GezinmeSaglayici({ deger, children }: {
  deger: Baglam
  children: ReactNode
}) {
  return <Ctx.Provider value={deger}>{children}</Ctx.Provider>
}

export function useGezinme() {
  const d = useContext(Ctx)
  if (!d) throw new Error('GezinmeSaglayici dışında kullanılamaz')
  return d
}
