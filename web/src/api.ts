import type {
  EnkazAlani, Goruntu, IslemGecmisi, Kullanici, Miktar, Olcum,
  SiniflarYaniti, SistemDurumu, Tespit, YuklemeSonucu,
} from './types'

const TABAN = '/api'
const ANAHTAR = 'rebuild_vision_jeton'

export const jetonAl = () => localStorage.getItem(ANAHTAR)
export const jetonYaz = (j: string) => localStorage.setItem(ANAHTAR, j)
export const jetonSil = () => localStorage.removeItem(ANAHTAR)

export class ApiHatasi extends Error {
  durum: number
  constructor(durum: number, mesaj: string) {
    super(mesaj)
    this.durum = durum
  }
}

async function istek<T>(yol: string, secenek: RequestInit = {}): Promise<T> {
  const basliklar = new Headers(secenek.headers)
  const jeton = jetonAl()
  if (jeton) basliklar.set('Authorization', `Bearer ${jeton}`)
  if (secenek.body && !(secenek.body instanceof FormData)) {
    basliklar.set('Content-Type', 'application/json')
  }

  const yanit = await fetch(`${TABAN}${yol}`, { ...secenek, headers: basliklar })

  if (!yanit.ok) {
    let mesaj = `İstek başarısız (${yanit.status})`
    try {
      const govde = await yanit.json()
      if (typeof govde.detail === 'string') mesaj = govde.detail
      else if (Array.isArray(govde.detail)) mesaj = govde.detail[0]?.msg ?? mesaj
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
  olcumler: (tespitId: number) => istek<Olcum[]>(`/olcum/tespit/${tespitId}`),
  olcumEkle: (govde: unknown) =>
    istek<Olcum>('/olcum', { method: 'POST', body: JSON.stringify(govde) }),

  harita: () => istek<{
    kapsam_uyarisi: string
    not: string
    malzeme_dagilimi: { sinif: string; adet: number }[]
  }>('/harita'),

  gecmis: (p: { kayit_tipi?: string; kayit_id?: number; limit?: number } = {}) => {
    const q = new URLSearchParams()
    if (p.kayit_tipi) q.set('kayit_tipi', p.kayit_tipi)
    if (p.kayit_id != null) q.set('kayit_id', String(p.kayit_id))
    if (p.limit) q.set('limit', String(p.limit))
    return istek<IslemGecmisi[]>(`/gecmis?${q}`)
  },

  gorselUrl: (dosyaYolu: string) => `${TABAN}/dosya/${dosyaYolu}`,
}
