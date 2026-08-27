/**
 * Güven skoru göstergesi.
 *
 * Ana talimat Bölüm 9.2: "Güven skoru gizlenmez. Sayı olarak gösterilir,
 * YUVARLANMAZ."
 *
 * Ondalık (0.78) yerine yüzde (%78) gösteriyoruz çünkü yüzde okunması daha
 * kolay — ama dönüşüm KAYIPSIZDIR: 0.785 → %78,5 olur, %79 değil. Modelin
 * verdiği hassasiyet neyse ekranda o kalır.
 *
 * Çubuk ikincil kodlamadır; sayı her zaman yanında durur, çubuk tek başına
 * bilgi taşımaz.
 */

/** 0.785 → "78,5" · 0.78 → "78" — yuvarlama yok, gereksiz sıfır yok. */
export function yuzdeMetni(skor: number): string {
  const y = skor * 100
  // Kayan nokta artıklarını temizle (0.78*100 = 78.00000000000001)
  const temiz = Math.round(y * 1e6) / 1e6
  return temiz.toLocaleString('tr-TR', { maximumFractionDigits: 4 })
}

export function GuvenSkoru({
  skor, incelemeGerekli = false, cubuk = true, boyut = 'normal',
}: {
  skor: number
  incelemeGerekli?: boolean
  cubuk?: boolean
  boyut?: 'normal' | 'kucuk'
}) {
  const renk = incelemeGerekli ? 'bg-uyari' : 'bg-marka'
  const metinRenk = incelemeGerekli ? 'text-uyari' : 'text-metin-2'

  return (
    <span className="inline-flex items-center gap-2 shrink-0">
      <span className={`sayisal ${metinRenk}
        ${boyut === 'kucuk' ? 'text-xs' : 'text-sm'}`}>
        %{yuzdeMetni(skor)}
      </span>
      {cubuk && (
        <span
          className={`rounded-full bg-yuzey-3 overflow-hidden
            ${boyut === 'kucuk' ? 'h-1 w-10' : 'h-1.5 w-14'}`}
          role="img"
          aria-label={`Model güveni yüzde ${yuzdeMetni(skor)}`}
        >
          <span className={`block h-full rounded-full ${renk}`}
            style={{ width: `${Math.max(2, skor * 100)}%` }} />
        </span>
      )}
    </span>
  )
}
