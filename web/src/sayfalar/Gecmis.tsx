import { useState } from 'react'
import { IslemGecmisiListesi } from '../bilesenler/IslemGecmisi'
import { Buton, Kart } from '../bilesenler/Temel'

/**
 * İşlem geçmişi sayfası — Rapor Bölüm 6, dördüncü yenilikçi yön.
 *
 * "Her kayıt için oluşturan kullanıcı, tarih, doğrulama durumu ve değişiklik
 * geçmişi saklanarak izlenebilirlik sağlanacaktır."
 *
 * Bu bilgi yalnızca veri tabanında durmaz; burada görünür (Bölüm 4.2).
 */

const SUZGECLER: { deger: string | undefined; etiket: string }[] = [
  { deger: undefined, etiket: 'Tümü' },
  { deger: 'tespit', etiket: 'Tespitler' },
  { deger: 'olcum', etiket: 'Ölçümler' },
  { deger: 'enkaz_alani', etiket: 'Enkaz alanları' },
  { deger: 'goruntu', etiket: 'Görüntüler' },
  { deger: 'kullanici', etiket: 'Kullanıcılar' },
]

export function Gecmis() {
  const [suzgec, setSuzgec] = useState<string | undefined>(undefined)

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h2 className="text-xl font-semibold">İşlem geçmişi</h2>
      <p className="text-sm text-metin-3 mt-0.5 mb-5">
        Sistemdeki her yazma işlemi — kim, ne zaman, neyi değiştirdi —
        otomatik olarak kaydedilir. Kayıtlar silinemez ve düzenlenemez.
      </p>

      <div className="flex gap-1.5 flex-wrap mb-5" role="group"
        aria-label="Kayıt türü süzgeci">
        {SUZGECLER.map((s) => (
          <Buton
            key={s.etiket}
            tur={suzgec === s.deger ? 'ikincil' : 'sessiz'}
            className="text-sm"
            aria-pressed={suzgec === s.deger}
            onClick={() => setSuzgec(s.deger)}
          >
            {s.etiket}
          </Buton>
        ))}
      </div>

      <Kart className="p-5">
        <IslemGecmisiListesi
          kayitTipi={suzgec}
          baslik={SUZGECLER.find((s) => s.deger === suzgec)?.etiket ?? 'Tümü'}
          limit={100}
        />
      </Kart>

      <p className="text-xs text-metin-3 mt-4 border-l-2 border-kenar-net pl-3 py-1">
        Parola özetleri ve konum geometrileri bu kayıtlara yazılmaz.
      </p>
    </div>
  )
}
