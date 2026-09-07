import { useDurum } from '../durum'
import { Ikon } from './Ikon'

/**
 * Model servisinin durumu — arayüzün en kritik dürüstlük göstergesi.
 *
 * ⚠️ BU BİLEŞEN BİR EKSİĞİ KAPATIR. README şunu taahhüt ediyordu:
 *
 *   "Sahte servis etkinken arayüzde kalıcı bir 'SAHTE MODEL SERVİSİ'
 *    rozeti gösterilir — demo sırasında yanlışlıkla 'gerçek model
 *    çalışıyor' izlenimi verilmez."
 *
 * Rozet arayüzde HİÇ YOKTU. `/sistem/durum` uç noktası `sahte` alanını
 * dönüyor, `types.ts` onu tiplemiş, `durum.tsx` çekiyordu — ve hiçbir
 * bileşen okumuyordu. Yani sistem sahte model servisiyle çalışırken
 * ekranda bunu söyleyen tek bir işaret bile yoktu.
 *
 * Bu, projenin kendi kuralının (ana talimat Bölüm 9.5: "sahtelik hiçbir
 * yerde gizlenmez") ekranda çiğnenmesiydi ve en pahalı yerde bulunurdu:
 * demoyu izleyen bir jüri üyesinin gerçek bir modelin çalıştığını
 * sanması, sonradan öğrenmesinden çok daha kötüdür.
 *
 * Rozet İKİ yerde durur: üst çubukta (her ekranda, kalıcı) ve giriş
 * ekranında (sisteme girmeden önce).
 *
 * ÜÇ DURUM VARDIR, İKİ DEĞİL — 06.09.2026'da eklendi:
 *
 *   1. `ulasilabilir && sahte`        → SAHTE MODEL SERVİSİ (turuncu)
 *   2. `!ulasilabilir && hiz_siniri`  → MODEL MEŞGUL (turuncu, geçici)
 *   3. `!ulasilabilir`                → MODEL YOK (kırmızı)
 *
 * İkinci durum, canlıda çalışan bir model servisi için kırmızı "MODEL
 * YOK" gösterildiği fark edilince ayrıldı: Render ücretsiz katmanı
 * `/health` çağrılarını hız sınırına (HTTP 429) takıyordu. "Meşgul" ile
 * "yok" aynı şey değildir; ama ikinci durumda "her şey yolunda" da
 * denmez — sahte/gerçek ayrımı da o an okunamadığı için metin bunu
 * açıkça söyler (ana talimat Bölüm 9.5).
 */

/** Üst çubuktaki kalıcı rozet. */
export function ModelRozeti() {
  const { durum } = useDurum()
  if (!durum) return null

  const { ulasilabilir, sahte, hiz_siniri } = durum.model_servisi

  // ⚠️ HIZ SINIRI "MODEL YOK" DEĞİLDİR.
  //
  // 06.09.2026'da canlıda bu rozet kırmızı "MODEL YOK" diyordu; model
  // servisi ise çalışıyor, `/health` doğrudan çağrıldığında
  // `agirlik_yuklendi: true` dönüyordu. Sebep Render ücretsiz katmanının
  // hız sınırıydı (HTTP 429). "Meşgul" ile "yok"u aynı göstermek yanlış
  // beyandır ve jüriye sistemin çalışmadığını söyler.
  //
  // Bu dal ONU DA GİZLEMEZ: rozet hâlâ görünür ve durumun OKUNAMADIĞINI
  // söyler — "her şey yolunda" demez, çünkü sahte/gerçek ayrımı da şu an
  // bilinmiyor (ana talimat Bölüm 9.5).
  if (!ulasilabilir && hiz_siniri) {
    return (
      <span
        title={'Model servisi hız sınırına takıldı (HTTP 429). Servis '
          + 'büyük olasılıkla çalışıyor ama durumu şu an okunamıyor; '
          + 'sahte mi gerçek mi olduğu da bilinmiyor. Birkaç saniye '
          + 'sonra sayfayı yenileyin.'}
        className="inline-flex items-center gap-1.5 px-2 py-1 rounded
          border border-uyari/50 bg-uyari/10 text-uyari
          text-[10px] font-semibold uppercase tracking-wider whitespace-nowrap"
      >
        <Ikon.Bekle boyut={13} />
        <span className="sr-only">
          Model servisi meşgul (hız sınırı) — durumu şu an okunamıyor
        </span>
        <span aria-hidden className="hidden sm:inline">Model meşgul</span>
      </span>
    )
  }

  // Servise ulaşılamıyorsa bu da söylenir: görüntü yükleme çalışmayacak
  // ve kullanıcı nedenini yükleme anında değil, ŞİMDİ bilmelidir.
  if (!ulasilabilir) {
    return (
      <span
        title={durum.model_servisi.hata
          ?? 'Model servisine ulaşılamıyor; görüntü yükleme çalışmaz.'}
        className="inline-flex items-center gap-1.5 px-2 py-1 rounded
          border border-dikkat/50 bg-dikkat/10 text-dikkat
          text-[10px] font-semibold uppercase tracking-wider whitespace-nowrap"
      >
        <Ikon.Baglanti boyut={13} />
        {/* 360 px'te üst çubuk rozet + tema + kullanıcı + çıkış'ı yan yana
            taşıyamıyor ve yatay kaydırmaya düşüyordu. Dar ekranda rozet
            ikona iner; anlamı `sr-only` metinle korunur, açıklamanın
            tamamı zaten yükleme ekranında yazılı duruyor. */}
        <span className="sr-only">
          Model servisine ulaşılamıyor — görüntü yükleme sınıflandırma üretemez
        </span>
        <span aria-hidden className="hidden sm:inline">Model yok</span>
      </span>
    )
  }

  if (!sahte) return null

  return (
    <span
      title={'Çıkarım sahte model servisinden geliyor. Sınıf, güven skoru '
        + 've kutular UYDURMADIR; gerçek bir modelin çıktısı değildir.'}
      className="inline-flex items-center gap-1.5 px-2 py-1 rounded
        border border-uyari/60 bg-uyari/10 text-uyari
        text-[10px] font-semibold uppercase tracking-wider whitespace-nowrap"
    >
      <Ikon.Sahte boyut={13} />
      <span className="sr-only">
        Sahte model servisi etkin — çıktılar uydurmadır
      </span>
      {/* Rozet kısa tutulur: üst çubukta beş sekmeli yönetici menüsüyle
          yan yana duruyor ve uzun bir metin menüyü kırpıyordu. Cümlenin
          tamamı `title` ve `sr-only` metninde, açıklaması ise yükleme ve
          giriş ekranlarında tam hâliyle duruyor. */}
      <span aria-hidden className="hidden sm:inline">Sahte model</span>
    </span>
  )
}

/**
 * Giriş ekranındaki ve yükleme ekranındaki açıklamalı uyarı.
 *
 * Rozet dar bir yerde tek kelimeyle uyarır; burada uyarının NE ANLAMA
 * GELDİĞİ yazılıdır — rozetin üzerine gelemeyen dokunmatik kullanıcı
 * için de.
 */
export function SahteModelUyarisi() {
  const { durum } = useDurum()
  if (!durum) return null

  const { ulasilabilir, sahte, model, hata, hiz_siniri, durum_kodu }
    = durum.model_servisi
  const olculdu = !durum.model_metrikleri.startsWith('henüz ölçülmedi')

  // Hız sınırı: servis meşgul, YOK DEĞİL. Ayrı bir metin, ayrı bir renk.
  // Ne "model yok" denir ne de "her şey yolunda" — durum okunamıyor ve
  // bu açıkça yazılır.
  if (!ulasilabilir && hiz_siniri) {
    return (
      <p role="status" className="flex items-start gap-2 text-xs text-uyari
        bg-uyari/10 border border-uyari/30 rounded-md px-3 py-2.5
        leading-relaxed">
        <Ikon.Bekle boyut={15} className="mt-px shrink-0" />
        <span>
          <strong className="font-semibold">
            Model servisi şu an yoğun{durum_kodu ? ` (HTTP ${durum_kodu})` : ''}.
          </strong>{' '}
          Bu <strong className="font-semibold">modelin olmadığı anlamına
          gelmez</strong>; ücretsiz barındırma katmanının hız sınırıdır.
          Servisin durumu — sahte mi gerçek mi çalıştığı dahil — şu an
          okunamıyor. Birkaç saniye sonra sayfayı yenileyin.
          {hata && <span className="block text-metin-3 mt-0.5">{hata}</span>}
        </span>
      </p>
    )
  }

  if (!ulasilabilir) {
    return (
      <p role="status" className="flex items-start gap-2 text-xs text-dikkat
        bg-dikkat/10 border border-dikkat/30 rounded-md px-3 py-2.5
        leading-relaxed">
        <Ikon.Baglanti boyut={15} className="mt-px shrink-0" />
        <span>
          <strong className="font-semibold">Model servisine ulaşılamıyor.</strong>{' '}
          Görüntü yükleme şu an sınıflandırma üretemez.
          {hata && <span className="block text-metin-3 mt-0.5">{hata}</span>}
        </span>
      </p>
    )
  }

  if (!sahte) return null

  return (
    <p role="status" className="flex items-start gap-2 text-xs text-uyari
      bg-uyari/10 border border-uyari/30 rounded-md px-3 py-2.5
      leading-relaxed">
      <Ikon.Sahte boyut={15} className="mt-px shrink-0" />
      <span>
        <strong className="font-semibold uppercase tracking-wide">
          Sahte model servisi
        </strong>{' '}
        etkin{model ? ` (${model})` : ''}. Sınıf, güven skoru ve kutular
        <strong className="font-semibold"> uydurmadır</strong>; gerçek bir
        modelin çıktısı değildir.
        {/* Model VAR ve ÖLÇÜLDÜ. Bunu söylememek, sahteliği gizlemenin
            tersi bir hata olurdu: okuyan kişi "ortada model yok" sanır.
            Sayı buradan uydurulmaz — sunucunun kendi ölçüm özeti
            (`/sistem/durum` → model_metrikleri) olduğu gibi basılır,
            altbilgideki sayıyla aynı kaynaktan gelir. */}
        <span className="block mt-1 text-metin-2">
          Sahte olan <strong className="font-semibold">servis</strong>, model
          değil
          {/* Metrik özeti sunucudan gelir. Ölçüm dosyası o ortamda yoksa
              özet "henüz ölçülmedi…" döner; o durumda "ölçüldü" DEMEYİZ,
              yoksa bant kendi kendini yalanlar. */}
          {olculdu
            ? <>: model eğitildi ve ölçüldü ({durum.model_metrikleri})</>
            : <> — model eğitildi; bu ortamda ölçüm özeti okunamıyor</>}
          . Bu ortam gerçek modeli çalıştırmıyor; çalıştırma adımları
          teslim paketindeki <code>docs/kurulum.md</code> içindedir.
        </span>
      </span>
    </p>
  )
}
