import type {
  EnkazAlani, Goruntu, IslemGecmisi, Kullanici, Miktar, Olcum,
  SiniflarYaniti, SistemDurumu, TehlikeliKayit, TehlikeliYanit, Tespit,
  YuklemeSonucu,
} from './types'

const TABAN = '/api'

/**
 * Pydantic'in İngilizce doğrulama mesajlarını Türkçeleştirir.
 *
 * Tamamen Türkçe bir kamu arayüzünde "String should have at least 8
 * characters" görünmesi kabul edilemez. Sunucu kendi yazdığı mesajları
 * zaten Türkçe döner (`ctx.error`); burada çevrilenler yalnızca
 * Pydantic'in yerleşik kısıt mesajlarıdır.
 */
function turkcelestir(h: {
  type?: string; msg?: string; loc?: (string | number)[]
  ctx?: Record<string, unknown>
} | undefined): string | undefined {
  if (!h) return undefined
  const alan = ALAN_ADLARI[String(h.loc?.[h.loc.length - 1] ?? '')] ?? 'Bu alan'
  const n = h.ctx?.min_length ?? h.ctx?.max_length

  switch (h.type) {
    case 'string_too_short': return `${alan} en az ${n} karakter olmalıdır.`
    case 'string_too_long': return `${alan} en fazla ${n} karakter olabilir.`
    case 'missing': return `${alan} zorunludur.`
    case 'string_pattern_mismatch': return `${alan} geçerli bir biçimde değil.`
    case 'greater_than': return `${alan} ${h.ctx?.gt}'dan büyük olmalıdır.`
    case 'float_parsing':
    case 'int_parsing': return `${alan} sayı olmalıdır.`
    // `value_error`, sunucunun kendi yazdığı (Türkçe) mesajdır; olduğu
    // gibi geçer — yalnızca Pydantic'in eklediği önek atılır.
    default: return h.msg?.replace(/^Value error, /, '')
  }
}

const ALAN_ADLARI: Record<string, string> = {
  parola: 'Parola', eposta: 'E-posta', ad: 'Ad soyad',
  deger: 'Ölçüm değeri', yontem: 'Ölçüm yöntemi', birim: 'Birim',
  sinif: 'Sınıf', durum: 'Durum', not: 'Not',
}
const ANAHTAR = 'rebuild_vision_jeton'

/**
 * Oturum jetonu deposu.
 *
 * ⚠️ BURASI UYGULAMAYI KOMPLE ÇÖKERTİYORDU. Üç işlev de `localStorage`'a
 * KORUMASIZ dokunuyordu. Tarayıcı "tüm site verilerini engelle" ayarındaysa
 * (ya da kurumsal ilke bunu dayatıyorsa) `localStorage.getItem` erişimin
 * kendisinde `SecurityError` atar. `durum.tsx` açılışta `jetonAl()`
 * çağırdığı için hata React ağacının kökünde patlıyor ve ekranda
 * **bomboş beyaz sayfa** kalıyordu: ne giriş formu, ne hata mesajı, ne
 * bir açıklama. Kullanıcının sistemin bozuk olduğunu sanmaktan başka
 * yapabileceği bir şey yoktu.
 *
 * `tema.tsx` aynı riski görüp try/catch kullanıyordu; jeton tarafına
 * uygulanmamıştı.
 *
 * Depolama yoksa jeton BELLEKTE tutulur: kullanıcı yine giriş yapıp
 * çalışabilir, yalnızca sekmeyi kapatınca oturumu düşer. Bu, çalışan bir
 * uygulamayla hiç açılmayan bir uygulama arasındaki farktır.
 */
let bellektekiJeton: string | null = null

export const jetonAl = (): string | null => {
  try {
    return localStorage.getItem(ANAHTAR) ?? bellektekiJeton
  } catch {
    return bellektekiJeton
  }
}

export const jetonYaz = (j: string) => {
  bellektekiJeton = j
  try { localStorage.setItem(ANAHTAR, j) } catch { /* bellekte kalır */ }
}

export const jetonSil = () => {
  bellektekiJeton = null
  try { localStorage.removeItem(ANAHTAR) } catch { /* zaten yazılamamıştı */ }
}

export class ApiHatasi extends Error {
  durum: number
  constructor(durum: number, mesaj: string) {
    super(mesaj)
    this.durum = durum
  }
}

/**
 * Oturumun düştüğünü uygulamaya duyurur.
 *
 * Jeton varken 401 gelmesi tek bir şey demektir: jeton artık geçerli
 * değil. Önceden bu durumda sayfanın ortasına "Jeton geçersiz veya süresi
 * dolmuş" yazılıyor, üst çubukta kullanıcının adı ve bütün menü duruyordu
 * — kullanıcı hâlâ giriş yapmış görünüyor ama hiçbir şey çalışmıyordu.
 * Şimdi jeton silinir ve uygulama giriş ekranına döner.
 */
export const OTURUM_DUSTU = 'rebuild-vision:oturum-dustu'

async function istek<T>(yol: string, secenek: RequestInit = {}): Promise<T> {
  const basliklar = new Headers(secenek.headers)
  const jeton = jetonAl()
  if (jeton) basliklar.set('Authorization', `Bearer ${jeton}`)
  if (secenek.body && !(secenek.body instanceof FormData)) {
    basliklar.set('Content-Type', 'application/json')
  }

  /**
   * ⚠️ `fetch` AĞ HATASINDA yanıt döndürmez, fırlatır — ve fırlattığı
   * `TypeError`ın mesajı tarayıcının kendi dilindedir: "Failed to fetch".
   * Bu dize kullanıcıya olduğu gibi çıkıyordu.
   *
   * Tamamen Türkçe bir kamu arayüzünde İngilizce bir tarayıcı hatası
   * göstermek zaten kabul edilemezdi; üstelik bu, kullanıcının EN SIK
   * göreceği hata: sunucu ücretsiz katmanda uyuduğu için ilk istek
   * düşebiliyor. Yani en olası hata, en anlaşılmaz mesajı veriyordu.
   *
   * Mesaj ne olduğunu VE ne yapılacağını söyler.
   */
  let yanit: Response
  try {
    yanit = await fetch(`${TABAN}${yol}`, { ...secenek, headers: basliklar })
  } catch {
    throw new ApiHatasi(
      0,
      'Sunucuya ulaşılamadı. İnternet bağlantınızı kontrol edip yeniden '
      + 'deneyin. Sunucu uzun süredir kullanılmadıysa ilk istek bir '
      + 'dakikaya kadar sürebilir.',
    )
  }

  // Jeton GÖNDERİLDİĞİ hâlde 401 geldiyse oturum düşmüştür. Jeton
  // gönderilmediğinde gelen 401 (hatalı parolayla giriş denemesi) bu
  // yola girmez — orada silinecek bir oturum yoktur.
  if (yanit.status === 401 && jeton) {
    jetonSil()
    window.dispatchEvent(new CustomEvent(OTURUM_DUSTU))
  }

  if (!yanit.ok) {
    let mesaj = `İstek başarısız (${yanit.status})`
    try {
      const govde = await yanit.json()
      if (typeof govde.detail === 'string') mesaj = govde.detail
      else if (Array.isArray(govde.detail)) {
        mesaj = turkcelestir(govde.detail[0]) ?? mesaj
      }
    } catch { /* gövde JSON değilse varsayılan mesaj kalır */ }
    throw new ApiHatasi(yanit.status, mesaj)
  }
  if (yanit.status === 204) return undefined as T
  return yanit.json() as Promise<T>
}

export const api = {
  durum: () => istek<SistemDurumu>('/sistem/durum'),
  siniflar: () => istek<SiniflarYaniti>('/sistem/siniflar'),

  kayit: (govde: { eposta: string; parola: string; ad: string }) =>
    istek<Kullanici>('/auth/kayit', { method: 'POST', body: JSON.stringify(govde) }),

  giris: (eposta: string, parola: string) =>
    istek<{ jeton: string; kullanici: Kullanici }>('/auth/giris', {
      method: 'POST', body: JSON.stringify({ eposta, parola }),
    }),

  ben: () => istek<Kullanici>('/auth/ben'),
  bekleyenler: () => istek<Kullanici[]>('/auth/bekleyenler'),
  rolAta: (id: number, rol: string, onay_durumu: string) =>
    istek<Kullanici>(`/auth/kullanici/${id}/rol`, {
      method: 'POST', body: JSON.stringify({ rol, onay_durumu }),
    }),

  alanlar: () => istek<EnkazAlani[]>('/enkaz-alani'),
  alan: (id: number) => istek<EnkazAlani>(`/enkaz-alani/${id}`),
  alanOlustur: (govde: unknown) =>
    istek<EnkazAlani>('/enkaz-alani', { method: 'POST', body: JSON.stringify(govde) }),

  alanGoruntuleri: (id: number) => istek<Goruntu[]>(`/goruntu/alan/${id}`),
  goruntuYukle: (alanId: number, dosyalar: File[]) => {
    const veri = new FormData()
    dosyalar.forEach((d) => veri.append('dosyalar', d))
    return istek<YuklemeSonucu>(`/goruntu/yukle/${alanId}`, { method: 'POST', body: veri })
  },

  kuyruk: () => istek<Tespit[]>('/tespit/inceleme-kuyrugu'),
  dogrula: (id: number, durum: string, duzeltilen_sinif?: string) =>
    istek<Tespit>(`/tespit/${id}/dogrula`, {
      method: 'POST', body: JSON.stringify({ durum, duzeltilen_sinif: duzeltilen_sinif ?? null }),
    }),

  miktar: (tespitId: number) => istek<Miktar>(`/miktar/${tespitId}`),

  tehlikeliKayitlar: (tespitId: number) =>
    istek<TehlikeliYanit>(`/tehlikeli/tespit/${tespitId}`),
  tehlikeliYonlendir: (govde: {
    tespit_id: number
    durum: 'incelemeye_yonlendirildi' | 'lab_sonucu_var'
    lab_sonucu_notu?: string
  }) => istek<TehlikeliKayit>('/tehlikeli', {
    method: 'POST', body: JSON.stringify(govde),
  }),

  olcumler: (tespitId: number) => istek<Olcum[]>(`/olcum/tespit/${tespitId}`),
  olcumEkle: (govde: unknown) =>
    istek<Olcum>('/olcum', { method: 'POST', body: JSON.stringify(govde) }),

  harita: () => istek<{
    kapsam_uyarisi: string
    not: string
    malzeme_dagilimi: { sinif: string; adet: number }[]
  }>('/harita'),

  gecmis: (p: {
    kayit_tipi?: string; kayit_id?: number; tespit_id?: number; limit?: number
  } = {}) => {
    const q = new URLSearchParams()
    if (p.kayit_tipi) q.set('kayit_tipi', p.kayit_tipi)
    if (p.kayit_id != null) q.set('kayit_id', String(p.kayit_id))
    // `tespit_id` tespitin BÜTÜN hikâyesini getirir: kendi kaydı artı
    // ölçüm, miktar ve tehlikeli madde kayıtları.
    if (p.tespit_id != null) q.set('tespit_id', String(p.tespit_id))
    if (p.limit) q.set('limit', String(p.limit))
    return istek<IslemGecmisi[]>(`/gecmis?${q}`)
  },

  gorselUrl: (dosyaYolu: string) => `${TABAN}/dosya/${dosyaYolu}`,

  /**
   * Rapor indirir.
   *
   * Jeton `Authorization` başlığında gittiği için düz bir bağlantı
   * kullanılamaz; dosya getirilip tarayıcıya indirtiliyor.
   */
  raporIndir: async (bicim: 'json' | 'geojson' | 'csv', alanId?: number) => {
    const q = alanId != null ? `?alan_id=${alanId}` : ''
    const yanit = await fetch(`${TABAN}/rapor/${bicim}${q}`, {
      headers: { Authorization: `Bearer ${jetonAl()}` },
    })
    if (!yanit.ok) {
      throw new ApiHatasi(yanit.status, 'Rapor indirilemedi')
    }
    const veri = await yanit.blob()
    const adres = URL.createObjectURL(veri)
    const a = document.createElement('a')
    a.href = adres
    // Dosya adı hangi sahanın, hangi günün raporu olduğunu SÖYLEMELİDİR.
    // Adın tamamı sabitti: üç sahanın raporunu indiren bir yetkilinin
    // indirilenler klasöründe "rebuild-vision-rapor(1).csv",
    // "(2).csv" birikiyor ve hangisinin hangisi olduğu kayboluyordu.
    // Tarih ayrıca doğrulanmış kayıt kümesinin ne zamanki hâli olduğunu
    // kaydeder — rapor yarın aynı olmayabilir.
    const gun = new Date().toISOString().slice(0, 10)
    const kapsam = alanId != null ? `alan-${alanId}` : 'tum-sahalar'
    a.download = `rebuild-vision-${kapsam}-${gun}.${bicim}`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(adres)
  },
}
