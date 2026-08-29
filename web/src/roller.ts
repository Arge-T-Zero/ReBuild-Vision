import type { Rol } from './types'

/**
 * Rol tanımları — her rol farklı bir işe gelir, farklı ekranla karşılanır.
 *
 * Önceden bütün roller aynı ekranı görüyordu; saha personeli giriş yapınca
 * boş bir alan listesi buluyordu, oysa onun tek işi görüntü yüklemek.
 * Ana talimat Bölüm 5'teki yetki tablosu artık gezinmeye de yansıyor.
 *
 * ⚠️ Bu dosya YALNIZCA ARAYÜZ içindir. Yetki kontrolü sunucu tarafında
 * yapılır (`api/app/core/permissions.py`); buradaki gizleme kolaylıktır,
 * güvenlik değildir.
 */

export type SayfaAdi =
  | 'alanlar' | 'alan' | 'kuyruk' | 'harita' | 'gecmis' | 'yonetici' | 'yukle'

export interface RolTanimi {
  ad: string
  /** Giriş yapınca açılan sayfa — rolün asıl işi. */
  anaSayfa: Exclude<SayfaAdi, 'alan'>
  /** Menüde görünecek sayfalar, sırayla. */
  menu: Exclude<SayfaAdi, 'alan'>[]
  /** Ana sayfada gösterilen tek cümlelik yönlendirme. */
  gorev: string
}

export const ROLLER: Record<Rol, RolTanimi> = {
  saha: {
    ad: 'Saha personeli',
    anaSayfa: 'yukle',
    menu: ['yukle', 'alanlar', 'harita'],
    gorev: 'Sahadan görüntü yükleyin ve ölçüm girin.',
  },
  uzman: {
    ad: 'Doğrulayıcı uzman',
    anaSayfa: 'kuyruk',
    menu: ['kuyruk', 'alanlar', 'harita', 'gecmis'],
    gorev: 'Model güveni düşük tespitleri inceleyin ve karara bağlayın.',
  },
  belediye: {
    ad: 'Belediye yetkilisi',
    anaSayfa: 'alanlar',
    menu: ['alanlar', 'harita', 'gecmis'],
    gorev: 'Enkaz alanlarını tanımlayın ve malzeme dağılımını izleyin.',
  },
  afad: {
    ad: 'AFAD yetkilisi',
    anaSayfa: 'harita',
    menu: ['harita', 'alanlar', 'gecmis'],
    gorev: 'Sahaları ve doğrulanmış malzeme dağılımını izleyin.',
  },
  yikim: {
    ad: 'Yıkım firması',
    anaSayfa: 'alanlar',
    menu: ['alanlar', 'harita'],
    gorev: 'Size atanmış sahaları görüntüleyin.',
  },
  tesis: {
    ad: 'Tesis operatörü',
    anaSayfa: 'harita',
    menu: ['harita', 'alanlar'],
    gorev: 'Size yönlendirilen malzeme kayıtlarını görüntüleyin.',
  },
  yonetici: {
    ad: 'Yönetici',
    anaSayfa: 'alanlar',
    menu: ['alanlar', 'kuyruk', 'harita', 'gecmis', 'yonetici'],
    gorev: 'Sistemin tamamına erişiminiz var.',
  },
}

export const SAYFA_ETIKETI: Record<Exclude<SayfaAdi, 'alan'>, string> = {
  yukle: 'Görüntü yükle',
  alanlar: 'Enkaz alanları',
  kuyruk: 'İnceleme kuyruğu',
  harita: 'Malzeme haritası',
  gecmis: 'İşlem geçmişi',
  yonetici: 'Rol onayları',
}

/**
 * Mobil alt gezinme çubuğunun kısa etiketleri.
 *
 * 360 px ekranda beş sekme yan yana durunca sekme başına ~72 px kalıyor;
 * "İnceleme kuyruğu" oraya sığmaz. Kısaltmalar tek başına anlaşılır
 * olacak biçimde seçildi — yanlarındaki ikonla birlikte okunuyorlar.
 */
export const SAYFA_KISA_ETIKET: Record<Exclude<SayfaAdi, 'alan'>, string> = {
  yukle: 'Yükle',
  alanlar: 'Alanlar',
  kuyruk: 'Kuyruk',
  harita: 'Harita',
  gecmis: 'Geçmiş',
  yonetici: 'Roller',
}

/** Rolü olmayan (onay bekleyen) kullanıcı için güvenli varsayılan. */
export const VARSAYILAN: RolTanimi = {
  ad: 'Rol atanmadı',
  anaSayfa: 'alanlar',
  menu: ['alanlar'],
  gorev: 'Hesabınız yönetici onayı bekliyor.',
}

export function rolTanimi(rol: Rol | null): RolTanimi {
  return rol ? ROLLER[rol] : VARSAYILAN
}
