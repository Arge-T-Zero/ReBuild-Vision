export type Rol =
  | 'yonetici' | 'afad' | 'belediye' | 'saha' | 'uzman' | 'yikim' | 'tesis'

export type OnayDurumu = 'beklemede' | 'onaylandi' | 'reddedildi'

/** 'reddet' bilinçli olarak yoktur — docs/karar-kaydi.md K-004 */
export type DogrulamaDurumu =
  | 'beklemede' | 'onaylandi' | 'duzeltildi' | 'belirsiz'

export interface Kullanici {
  id: number
  eposta: string
  ad: string
  rol: Rol | null
  onay_durumu: OnayDurumu
  olusturma_tarihi: string
}

export interface Nokta { enlem: number; boylam: number }

export interface EnkazAlani {
  id: number
  ad: string
  konum: Nokta | null
  sinir: Nokta[] | null
  erisim_durumu: 'acik' | 'kisitli' | 'kapali'
  sorumlu: string | null
  inceleme_tarihi: string | null
  olusturan_id: number
  olusturma_tarihi: string
  goruntu_sayisi: number

  /** Kart özeti — sahayı açmadan durumu görmek için. */
  tespit_sayisi: number
  dogrulanan_sayisi: number
  inceleme_bekleyen: number
  /** Yalnızca DOĞRULANMIŞ kayıtlardan; haritayla aynı kural (Bölüm 1.4). */
  malzeme_dagilimi: { sinif: string; adet: number }[]
}

export interface BBox { x: number; y: number; w: number; h: number }

export interface Tespit {
  id: number
  goruntu_id: number
  sinif: string
  guven_skoru: number
  bbox: BBox | null
  /** Kutunun hangi koordinat uzayında olduğu — ölçekleme buna göre yapılır */
  bbox_format: string
  dogrulama_durumu: DogrulamaDurumu
  dogrulayan_id: number | null
  dogrulama_tarihi: string | null
  duzeltilen_sinif: string | null
  inceleme_gerekli: boolean
  /** Her model çıktısı 'ön tahmin'dir, istisnasız */
  etiket: string
}

export interface Goruntu {
  id: number
  enkaz_alani_id: number
  dosya_yolu: string
  genislik: number | null
  yukseklik: number | null
  cekim_tarihi: string | null
  cihaz: string | null
  yukleyen_id: number
  olusturma_tarihi: string
  tespitler: Tespit[]
}

export interface YuklemeSonucu {
  goruntuler: Goruntu[]
  sahte_model_servisi: boolean
  inceleme_kuyruguna_dusen: number
}

/** Miktar — hesaplanmadıysa hiçbir sayı alanı dolu gelmez */
export interface Miktar {
  tespit_id: number
  hesaplandi: boolean
  aciklama: string | null
  deger_alt: number | null
  deger_ust: number | null
  birim: string | null
  kullanilan_katsayi: number | null
  katsayi_kaynagi: string | null
  yontem: string | null
}

export interface Olcum {
  id: number
  tespit_id: number
  tur: 'alan' | 'hacim' | 'agirlik'
  deger: number
  birim: string
  yontem: string
  giren_id: number
  tarih: string
}

export interface SinifTanimi {
  id: number
  ad: string
  gorunen_ad: string
  cdw_seg: string
  malzeme_mi: boolean
  renk: string
}

export interface SiniflarYaniti {
  surum: string
  kaynak: string
  siniflar: SinifTanimi[]
  kapsanmayan_gruplar: { ad: string; not: string }[]
}

export interface SistemDurumu {
  model_servisi: {
    ulasilabilir: boolean
    sahte: boolean | null
    model?: string
    lisans?: string
    hata?: string
  }
  kapsam_uyarisi: string
  model_metrikleri: string
}

/**
 * Tehlikeli madde kaydı — TEŞHİS DEĞİL.
 * Bu tipte bilinçli olarak olasılık, risk seviyesi veya madde adı yoktur.
 */
export interface TehlikeliKayit {
  id: number
  tespit_id: number
  durum: 'incelemeye_yonlendirildi' | 'lab_sonucu_var'
  lab_sonucu_notu: string | null
  giren_id: number
  tarih: string
}

export interface TehlikeliYanit {
  tespit_id: number
  kayitlar: TehlikeliKayit[]
  /** Kayıt yoksa yokluğun güvenlik anlamına gelmediğini söyleyen metin */
  aciklama: string | null
  /** 'degerlendirilmedi' | 'kayit_var' — asla 'guvenli' değil */
  degerlendirme: string
}

export interface IslemGecmisi {
  id: number
  kayit_tipi: string
  kayit_id: number | null
  islem: string
  eski_deger: Record<string, unknown> | null
  yeni_deger: Record<string, unknown> | null
  kullanici_id: number | null
  tarih: string
}
