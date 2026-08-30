import { useState } from 'react'
import { IslemGecmisiListesi } from '../bilesenler/IslemGecmisi'
import { Baslik, Buton, Kart } from '../bilesenler/Temel'
import { Sayfa } from '../bilesenler/Duzen'

/**
 * İşlem geçmişi sayfası — Rapor Bölüm 6, dördüncü yenilikçi yön.
 *
 * "Her kayıt için oluşturan kullanıcı, tarih, doğrulama durumu ve değişiklik
 * geçmişi saklanarak izlenebilirlik sağlanacaktır."
 *
 * Bu bilgi yalnızca veri tabanında durmaz; burada görünür (Bölüm 4.2).
 */

/**
 * Süzgeçler — renkleri listedeki kayıt renkleriyle AYNI.
 *
 * Süzgeç düğmesi nötr griyken, kullanıcı "Tespitler"e basıp listede
 * hangi renklerin kaldığını gözüyle eşleştiremiyordu. Aynı renk her iki
 * yerde de kullanılınca süzgeç aynı zamanda bir RENK ANAHTARI oluyor.
 */
const SUZGECLER: {
  deger: string | undefined; etiket: string; renk?: string
}[] = [
  { deger: undefined, etiket: 'Tümü' },
  { deger: 'tespit', etiket: 'Tespitler', renk: 'var(--u-kayit-tespit)' },
  { deger: 'olcum', etiket: 'Ölçümler', renk: 'var(--u-kayit-olcum)' },
  { deger: 'enkaz_alani', etiket: 'Enkaz alanları', renk: 'var(--u-kayit-alan)' },
  { deger: 'goruntu', etiket: 'Görüntüler', renk: 'var(--u-kayit-goruntu)' },
  { deger: 'kullanici', etiket: 'Kullanıcılar', renk: 'var(--u-kayit-kullanici)' },
]

export function Gecmis() {
  const [suzgec, setSuzgec] = useState<string | undefined>(undefined)

  return (
    <Sayfa dar>
      <Baslik
        ustBaslik="İzlenebilirlik"
        baslik="İşlem geçmişi"
        aciklama="Sistemdeki her yazma işlemi — kim, ne zaman, neyi değiştirdi — otomatik olarak kaydedilir. Kayıtlar silinemez ve düzenlenemez. Renkler kayıt türünü gösterir."
      />

      <div className="flex gap-1.5 flex-wrap mb-5" role="group"
        aria-label="Kayıt türü süzgeci">
        {SUZGECLER.map((s) => (
          <Buton
            key={s.etiket}
            tur={suzgec === s.deger ? 'ikincil' : 'sessiz'}
            className="text-sm"
            aria-pressed={suzgec === s.deger}
            onClick={() => setSuzgec(s.deger)}
            /* Renk noktası yalnızca işarettir; anlamı yanındaki
               etiket taşır (ana talimat Bölüm 9.3). */
            ikon={s.renk
              ? <span aria-hidden className="w-2 h-2 rounded-full shrink-0"
                  style={{ background: s.renk }} />
              : undefined}
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
    </Sayfa>
  )
}
