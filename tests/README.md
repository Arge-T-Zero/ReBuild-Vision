# Testler

**Şartname/kalite kapısı:** ana talimat Bölüm 13 — her push öncesi testler
geçmelidir.

## Çalıştırma

```bash
api/.venv/bin/pip install -r api/requirements-dev.txt
api/.venv/bin/python -m pytest
```

Yalnızca ihlal edilemez kuralları sınamak için:

```bash
api/.venv/bin/python -m pytest -m kural
```

## Test veri tabanı

Testler **ayrı** bir veri tabanında çalışır: `rebuild_vision_test`.
Geliştirme veri tabanına (`rebuild_vision`) dokunulmaz.

Şema `metadata.create_all` ile değil, **gerçek Alembic göçüyle** kurulur.
Böylece göç dosyası da her çalıştırmada sınanmış olur — göç bozulursa
testler kırmızıya döner.

Her testten önce tablolar `TRUNCATE ... RESTART IDENTITY CASCADE` ile
boşaltılır.

> Bağlantı havuzu olarak `NullPool` kullanılır. Havuzlanmış bağlantılar
> testler arasında farklı asyncio olay döngülerine takılır ve
> "attached to a different loop" hatası verir.

## Neyi koruyorlar

Testlerin asıl işi, **Bölüm 1'deki dört ihlal edilemez kuralın sessizce
bozulmasını engellemektir.**

| Dosya | Ne korur |
|---|---|
| `test_kural_1_olcum_yoksa_miktar_yok.py` | Ölçüm yoksa sayı üretilmez; miktar aralık olarak gelir; tek değerli miktar veri tabanınca reddedilir |
| `test_kural_2_tehlikeli_madde.py` | Teşhis yapılmaz; `'guvenli'` yazılamaz; şemada olasılık/risk alanı yok; yanıtlarda "güvenli" geçmez |
| `test_kural_3_ve_4_kapsam_ve_on_tahmin.py` | Kapsam uyarısı yanıtlarda var; her çıktıda "ön tahmin"; doğrulanmamış ve belirsiz kayıtlar hesaba girmez; uzman düzeltmesi modeli geçersiz kılar; "reddet" yok |
| `test_yetki_ve_roller.py` | Yedi rolün yetkileri; kayıtta rol yükseltilemez; onaysız hesap giremez; salt okunur roller yazamaz |
| `test_izlenebilirlik.py` | İşlem geçmişi otomatik dolar; `kayit_id` boş kalmaz; eski/yeni değer saklanır; parola özeti sızmaz |
| `test_bbox_format.py` | `bbox_format` boş geçilemez; güven skoru aralığı zorlanır |
| `test_sinif_tanimlari.py` | `siniflar.json` tutarlılığı; `konteyner` malzeme değil; kapsanmayan gruplar beyan edilmiş; doğrulanmamış katsayı kullanılmaz |

## Regresyon testleri

Bazı testler geçmişte **gerçekten yaşanmış** hataları korur:

- `test_olusturma_kaydinda_kayit_id_dolu` — olay dinleyicisi `before_flush`
  kullandığında yeni kayıtların `id` değeri henüz atanmamış oluyor ve
  denetim kaydı satıra bağlanamıyordu.
- `test_uzman_duzeltmesi_model_tahminini_gecersiz_kilar` — harita ve miktar
  hesapları modelin ham tahminini kullanıyordu; uzmanın düzeltmesi
  yansımıyordu.

## Yeni kural eklenirse

Bölüm 1'e dokunan her değişiklik **önce burada bir testle** ifade edilir.
Kural yalnızca kodda duruyorsa, bir sonraki değişiklikte sessizce
kaybolabilir.
