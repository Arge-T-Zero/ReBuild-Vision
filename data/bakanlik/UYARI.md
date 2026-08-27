# ⛔ UYARI — Bu klasör versiyon kontrolüne girmez

Şartname **Madde 9.1**:

> "Verilerin kopyalanması, paylaşılması veya farklı bir platformda
> kullanılması yasaktır."

Şartname **Madde 10.5**:

> "Bakanlık tarafından sağlanan veriler, açık izin olmaksızın üçüncü taraf
> yapay zekâ servislerine veya bulut tabanlı model sağlayıcılarına
> gönderilemez."

## Kurallar

1. Bakanlık tarafından sağlanan veri **yalnızca** bu klasörde tutulur.
2. Bu klasörün içeriği `.gitignore` ile dışlanmıştır. **Asla commit edilmez.**
3. Bu veri hiçbir bulut servisine gönderilmez: Supabase, Google Colab,
   herhangi bir barındırılan model API'si dahil.
4. Model eğitimi bulut ortamında yapılacaksa **yalnızca** kendi ürettiğimiz
   veya açık kaynak veriyle yapılır.
5. Madde 10.6 uyarınca yarışma sonrası silme yükümlülüğü vardır:
   finalist değilse **15 gün**, finalistse **30 gün** içinde.

Silme prosedürü ve veri envanteri: `docs/veri-politikasi.md`
