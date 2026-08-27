import type { SistemDurumu } from '../types'

/**
 * Sahte model servisi uyarısı — ana talimat Bölüm 9.5.
 *
 * "Arayüzde sahte servis kullanılıyorsa bunu gösteren bir işaret dursun —
 * demo sırasında yanlışlıkla 'gerçek model çalışıyor' izlenimi
 * verilmesin."
 *
 * Bu bant kapatılamaz ve gizlenemez.
 */
export function SahteServisRozeti({ durum }: { durum: SistemDurumu | null }) {
  if (!durum) return null

  if (!durum.model_servisi.ulasilabilir) {
    return (
      <div role="status" className="bg-dikkat text-taban px-4 py-1.5 text-sm font-semibold
        text-center">
        Model servisine ulaşılamıyor — yeni görüntüler işlenemez
      </div>
    )
  }

  if (!durum.model_servisi.sahte) return null

  return (
    <div role="status" className="bg-uyari text-taban px-4 py-1.5 text-sm font-semibold
      text-center">
      SAHTE MODEL SERVİSİ — gösterilen tespitler gerçek bir modelden gelmemektedir
      <span className="font-normal opacity-80"> ({durum.model_servisi.model})</span>
    </div>
  )
}
