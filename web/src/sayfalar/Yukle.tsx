import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { useDurum } from '../durum'
import { useGezinme } from '../gezinme'
import { Sayfa } from '../bilesenler/Duzen'
import {
  Baslik, Bilgi, BosDurum, Buton, Hata, KapsamUyarisi, Kart,
  OnTahminEtiketi, SinifEtiketi, girdiSinifi,
} from '../bilesenler/Temel'
import { GuvenSkoru } from '../bilesenler/GuvenSkoru'
import { Ikon } from '../bilesenler/Ikon'
import { SahteModelUyarisi } from '../bilesenler/ModelDurumu'
import type { EnkazAlani, YuklemeSonucu } from '../types'
import { sayfaGorevi } from '../roller'

/**
 * Saha personelinin ana ekranı.
 *
 * Saha personelinin tek işi görüntü yüklemek ve ölçüm girmek. Önceden
 * giriş yapınca boş bir alan listesiyle karşılaşıyor, ne yapacağını
 * anlamıyordu. Artık doğrudan çalışma ekranına düşüyor.
 */
export function Yukle() {
  const { kullanici, durum, siniflar } = useDurum()
  const { alanaGit, git, erisilebilir } = useGezinme()
  const [alanlar, setAlanlar] = useState<EnkazAlani[] | null>(null)
  const [seciliAlan, setSeciliAlan] = useState<number | ''>('')
  const [dosyalar, setDosyalar] = useState<File[]>([])
  const [surukleniyor, setSurukleniyor] = useState(false)
  const [yukleniyor, setYukleniyor] = useState(false)
  const [sonuc, setSonuc] = useState<YuklemeSonucu | null>(null)
  const [hata, setHata] = useState('')
  const girdi = useRef<HTMLInputElement>(null)

  useEffect(() => {
    api.alanlar()
      .then((a) => {
        setAlanlar(a)
        if (a.length === 1) setSeciliAlan(a[0].id)
      })
      .catch((h) => setHata(h.message))
  }, [])

  const dosyaEkle = useCallback((liste: FileList | null) => {
    if (!liste) return
    const gorseller = Array.from(liste).filter((d) => d.type.startsWith('image/'))
    if (gorseller.length === 0) {
      setHata('Yalnızca görüntü dosyası yükleyebilirsiniz')
      return
    }
    setHata('')
    setDosyalar((d) => [...d, ...gorseller])
  }, [])

  async function gonder() {
    if (!seciliAlan || dosyalar.length === 0) return
    setHata(''); setYukleniyor(true); setSonuc(null)
    try {
      const s = await api.goruntuYukle(Number(seciliAlan), dosyalar)
      setSonuc(s)
      setDosyalar([])
      if (girdi.current) girdi.current.value = ''
    } catch (h) {
      setHata(h instanceof Error ? h.message : 'Yükleme başarısız')
    } finally {
      setYukleniyor(false)
    }
  }

  const tumTespitler = (sonuc?.goruntuler ?? []).flatMap((g) => g.tespitler)

  return (
    <Sayfa>
      <Baslik
        ustBaslik="Saha çalışması"
        baslik="Görüntü yükle"
        gorev={sayfaGorevi(kullanici?.rol ?? null, 'yukle')}
        aciklama="Yüklediğiniz görüntüler otomatik sınıflandırılır. Model güveni düşük olan tespitler uzman incelemesine kendiliğinden gider."
      />

      {/* Sınıflandırmayı ÜRETEN servisin ne olduğu, yükleme düğmesinin
          hemen üstünde yazar: sonucu sahte bir servisin ürettiğini
          sonradan değil, yüklemeden önce bilmeli. */}
      <div className="mb-4"><SahteModelUyarisi /></div>

      {hata && <div className="mb-4"><Hata mesaj={hata} /></div>}

      {alanlar !== null && alanlar.length === 0 ? (
        <Kart>
          <BosDurum
            ikon={<Ikon.Alan boyut={20} />}
            baslik="Size atanmış bir saha bulunmuyor"
            aciklama="Görüntü yükleyebilmek için önce bir enkaz alanına bağlı olmanız gerekir. Belediye ya da AFAD yetkilisi alanı tanımladıktan sonra burada görünecektir."
            aksiyon={erisilebilir('harita') && (
              <Buton tur="ikincil" onClick={() => git('harita')}
                ikon={<Ikon.Harita boyut={15} />}>
                Malzeme haritasına bak
              </Buton>
            )}
          />
        </Kart>
      ) : (
        <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_320px]">
          <div className="space-y-4">
            <Kart className="p-5">
              <label className="block mb-4">
                <span className="block text-xs font-medium text-metin-2 mb-1.5
                  uppercase tracking-wide">Enkaz alanı</span>
                <select
                  value={seciliAlan}
                  onChange={(e) => setSeciliAlan(e.target.value ? Number(e.target.value) : '')}
                  className={girdiSinifi}
                >
                  <option value="">Alan seçin…</option>
                  {(alanlar ?? []).map((a) => (
                    <option key={a.id} value={a.id}>{a.ad}</option>
                  ))}
                </select>
              </label>

              {/* Sürükle-bırak alanı — büyük dokunma hedefi, eldivenli kullanım */}
              <div
                onDragOver={(e) => { e.preventDefault(); setSurukleniyor(true) }}
                onDragLeave={() => setSurukleniyor(false)}
                onDrop={(e) => {
                  e.preventDefault(); setSurukleniyor(false)
                  dosyaEkle(e.dataTransfer.files)
                }}
                className={`rounded-kart border-2 border-dashed p-8 text-center
                  transition-colors ${surukleniyor
                    ? 'border-marka bg-marka/5'
                    : 'border-kenar-net hover:border-kenar-parlak'}`}
              >
                <div className="inline-flex items-center justify-center w-12 h-12
                  rounded-full bg-yuzey-2 border border-kenar text-metin-3 mb-3">
                  <Ikon.Foto boyut={22} />
                </div>
                <p className="font-medium">Görüntüleri buraya sürükleyin</p>
                <p className="text-sm text-metin-3 mt-1">
                  ya da cihazınızdan seçin — JPEG, PNG veya WebP
                </p>
                <input ref={girdi} type="file" multiple accept="image/*"
                  className="hidden"
                  onChange={(e) => dosyaEkle(e.target.files)} />
                <Buton tur="ikincil" className="mt-4"
                  onClick={() => girdi.current?.click()}
                  ikon={<Ikon.Yukle boyut={15} />}>
                  Dosya seç
                </Buton>
              </div>

              {dosyalar.length > 0 && (
                <div className="mt-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm text-metin-2">
                      <span className="sayisal">{dosyalar.length}</span> görüntü seçildi
                    </p>
                    <button onClick={() => setDosyalar([])}
                      className="text-xs text-metin-3 hover:text-metin !min-h-0">
                      Listeyi temizle
                    </button>
                  </div>
                  <ul className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                    {dosyalar.map((d, i) => (
                      <li key={`${d.name}-${i}`}
                        className="relative aspect-4/3 rounded-md overflow-hidden
                          border border-kenar bg-yuzey-2">
                        <img src={URL.createObjectURL(d)} alt=""
                          className="w-full h-full object-cover" />
                      </li>
                    ))}
                  </ul>

                  <Buton className="mt-4 w-full" disabled={!seciliAlan || yukleniyor}
                    onClick={gonder} ikon={<Ikon.Yukle boyut={15} />}>
                    {yukleniyor
                      ? 'İşleniyor…'
                      : !seciliAlan
                        ? 'Önce bir enkaz alanı seçin'
                        : `${dosyalar.length} görüntüyü yükle ve sınıflandır`}
                  </Buton>
                </div>
              )}
            </Kart>

            {sonuc && (
              <Kart className="p-5">
                <Bilgi>
                  <span className="sayisal">{sonuc.goruntuler.length}</span> görüntü
                  işlendi,{' '}
                  <span className="sayisal">{tumTespitler.length}</span> tespit
                  bulundu.{' '}
                  {sonuc.inceleme_kuyruguna_dusen > 0 ? (
                    <>Düşük güvenli{' '}
                      <strong className="text-metin sayisal">
                        {sonuc.inceleme_kuyruguna_dusen}
                      </strong>{' '}
                      tanesi otomatik olarak uzman incelemesine gitti.</>
                  ) : (
                    <>Uzman incelemesi gerektiren tespit çıkmadı.</>
                  )}
                </Bilgi>

                <ul className="mt-4 space-y-2">
                  {tumTespitler.map((t) => {
                    const tanim = siniflar.get(t.sinif)
                    return (
                      <li key={t.id}
                        className="flex items-center gap-3 flex-wrap px-3 py-2
                          rounded-md border border-kenar">
                        <SinifEtiketi renk={tanim?.renk ?? '#6b7280'}
                          ad={tanim?.gorunen_ad ?? t.sinif} />
                        <GuvenSkoru skor={t.guven_skoru}
                          incelemeGerekli={t.inceleme_gerekli} />
                        {/* ⚠️ BU ETİKET BURADA YOKTU. Kural "istisnasız"
                            diyor; yan paneldeki düzyazı ("sonuçlar ön
                            tahmin olarak listelenir") etiketin yerini
                            tutmaz — kullanıcı bu listenin ekran
                            görüntüsünü paylaştığında düzyazı gitmiş
                            olur, etiket kalır. Mobil aynı listeyi zaten
                            doğru gösteriyordu. */}
                        <OnTahminEtiketi />
                        <span className="grow" />
                        {t.inceleme_gerekli && (
                          <span className="text-xs text-uyari">
                            uzman incelemesine gitti
                          </span>
                        )}
                      </li>
                    )
                  })}
                </ul>

                {seciliAlan && (
                  <Buton tur="ikincil" className="mt-4"
                    onClick={() => alanaGit(Number(seciliAlan))}>
                    Alanı aç ve ölçüm gir
                  </Buton>
                )}
              </Kart>
            )}
          </div>

          {/* Yan panel: ne olacağını önceden anlatır */}
          <div className="space-y-4">
            <Kart className="p-4">
              <h2 className="text-sm font-semibold text-metin-2 mb-3">
                Yükledikten sonra ne olur
              </h2>
              <ol className="space-y-3 text-sm text-metin-3">
                {[
                  'Görüntüler otomatik sınıflandırılır; sonuçlar ön tahmin olarak listelenir.',
                  'Model güveni düşük tespitler uzman kuyruğuna kendiliğinden gider.',
                  'Ölçüm girerseniz miktar belirsizlik aralığıyla hesaplanır.',
                  'Ölçüm girilmezse miktar hesaplanmaz — sistem tahmin uydurmaz.',
                ].map((m, i) => (
                  <li key={i} className="flex gap-2.5">
                    <span aria-hidden className="shrink-0 w-5 h-5 rounded-full
                      bg-yuzey-3 text-metin-3 grid place-items-center
                      text-xs sayisal">{i + 1}</span>
                    <span className="leading-relaxed">{m}</span>
                  </li>
                ))}
              </ol>
            </Kart>

            {durum && (
              <Kart className="p-4">
                <KapsamUyarisi metin={durum.kapsam_uyarisi} />
              </Kart>
            )}
          </div>
        </div>
      )}
    </Sayfa>
  )
}
