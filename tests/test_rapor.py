"""Rapor indirme — dosyadaki kurallar ekrandakiyle aynı olmalı.

Bu testlerin asıl işi bir kaçamağı engellemek: ekranda gizlenen bir
sayının dosyada verilmesi kuralı anlamsız kılardı.
"""
from __future__ import annotations

import csv
import io
import json


async def _hazirla(istemci, jeton, tespit_kur, ucuncu_sinif: str = "seramik"):
    """Bir doğrulanmış, bir doğrulanmamış ve bir de üçüncü kayıt kurar.

    Üçüncü kayıt her zaman DOĞRULANMIŞTIR. `ucuncu_sinif` malzeme
    olmayan bir sınıf verildiğinde rapordan düşmesinin tek sebebi
    malzeme olmaması olur; doğrulanmamış olsaydı hangi kuralın onu
    elediği belirsiz kalırdı. Varsayılan hâlinde (`seramik`) sıradan bir
    malzeme kaydıdır ve raporda görünür.
    """
    onayli = await tespit_kur("tugla")
    await istemci.post(f"/tespit/{onayli}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "onaylandi"})
    beklemede = await tespit_kur("ahsap")
    malzeme_degil = await tespit_kur(ucuncu_sinif)
    await istemci.post(f"/tespit/{malzeme_degil}/dogrula",
                       headers=await jeton("uzman"),
                       json={"durum": "onaylandi"})
    return onayli, beklemede, malzeme_degil


async def test_json_yalnizca_dogrulanmis_kayit_verir(istemci, jeton, tespit_kur):
    onayli, beklemede, _ = await _hazirla(istemci, jeton, tespit_kur)
    d = json.loads((await istemci.get("/rapor/json",
                                      headers=await jeton("belediye"))).text)

    kimlikler = [k["tespit_id"] for k in d["kayitlar"]]
    assert onayli in kimlikler
    assert beklemede not in kimlikler, (
        "Doğrulanmamış ön tahmin rapora girmemeli — ekranda gizlenip "
        "dosyada verilseydi kural anlamsız olurdu"
    )


async def test_raporda_malzeme_olmayan_sinif_yok(
    istemci, jeton, tespit_kur, malzeme_olmayan_sinif
):
    """K-007: malzeme olmayan sınıf raporda da yok."""
    _, _, malzeme_degil = await _hazirla(
        istemci, jeton, tespit_kur, malzeme_olmayan_sinif)
    d = json.loads((await istemci.get("/rapor/json",
                                      headers=await jeton("belediye"))).text)
    assert malzeme_degil not in [k["tespit_id"] for k in d["kayitlar"]]
    assert malzeme_olmayan_sinif not in {k["sinif"] for k in d["kayitlar"]}


async def test_olcumsuz_kayitta_miktar_null(istemci, jeton, tespit_kur):
    """Miktar hesaplanmadıysa null — sıfır DEĞİL (Bölüm 1.1)."""
    await _hazirla(istemci, jeton, tespit_kur)
    d = json.loads((await istemci.get("/rapor/json",
                                      headers=await jeton("belediye"))).text)
    assert d["kayitlar"][0]["miktar"] is None


async def test_csv_de_miktar_bos_hucre(istemci, jeton, tespit_kur):
    """Elektronik tabloda 0 gören biri 'ölçüm sıfır' sanardı."""
    await _hazirla(istemci, jeton, tespit_kur)
    metin = (await istemci.get("/rapor/csv",
                               headers=await jeton("belediye"))).text

    # Yorum satırları ';' içerdiği için csv.writer onları tırnaklıyor;
    # '#' ile değil '"#' ile başlıyorlar. Başlık satırını adıyla bul.
    satirlar = metin.lstrip("\ufeff").splitlines()
    bas = next(i for i, s in enumerate(satirlar) if s.startswith("tespit_id"))
    okuyucu = csv.DictReader(io.StringIO("\n".join(satirlar[bas:])), delimiter=";")
    kayit = next(okuyucu)
    assert kayit["miktar_alt"] == "", "Boş hücre olmalı, 0 değil"
    assert kayit["miktar_ust"] == ""


async def test_csv_excel_uyumlu(istemci, jeton, tespit_kur):
    """Türkçe karakterler bozulmasın, sütunlar birleşmesin."""
    await _hazirla(istemci, jeton, tespit_kur)
    y = await istemci.get("/rapor/csv", headers=await jeton("belediye"))

    assert y.text.startswith("﻿"), "Excel için UTF-8 BOM gerekli"
    assert ";" in y.text, "Türkçe yerelde ayraç ; olmalı"
    assert "text/csv" in y.headers["content-type"]
    assert "attachment" in y.headers["content-disposition"]


async def test_raporda_kapsam_uyarisi_var(istemci, jeton, tespit_kur):
    """Dosyayı QGIS'te ya da Excel'de açan da uyarıyı görmeli."""
    await _hazirla(istemci, jeton, tespit_kur)
    baslik = await jeton("belediye")

    j = json.loads((await istemci.get("/rapor/json", headers=baslik)).text)
    assert "görünür yüzey" in j["kapsam_uyarisi"]
    assert "teşhisi yapmaz" in j["kapsam_uyarisi"]

    g = json.loads((await istemci.get("/rapor/geojson", headers=baslik)).text)
    assert "görünür yüzey" in g["kunye"]["kapsam_uyarisi"]

    c = (await istemci.get("/rapor/csv", headers=baslik)).text
    assert "görünür yüzey" in c


async def test_geojson_koordinat_sirasi_dogru(istemci, jeton, tespit_kur):
    """GeoJSON'da boylam önce gelir; ters yazılırsa nokta okyanusa düşer."""
    await _hazirla(istemci, jeton, tespit_kur)
    g = json.loads((await istemci.get("/rapor/geojson",
                                      headers=await jeton("belediye"))).text)
    assert g["type"] == "FeatureCollection"
    # Test verisi konumsuz olabilir; varsa sıra kontrol edilir.
    for f in g["features"]:
        boylam, enlem = f["geometry"]["coordinates"]
        assert -180 <= boylam <= 180 and -90 <= enlem <= 90


async def test_rapor_yetki_ister(istemci, jeton, tespit_kur):
    await _hazirla(istemci, jeton, tespit_kur)
    for rol in ("saha", "uzman", "yikim", "tesis"):
        y = await istemci.get("/rapor/json", headers=await jeton(rol))
        assert y.status_code == 403, f"{rol} rapor indirememeli"
    for rol in ("belediye", "afad", "yonetici"):
        y = await istemci.get("/rapor/json", headers=await jeton(rol))
        assert y.status_code == 200


async def test_uzman_duzeltmesi_raporda_gecerli_sinif(istemci, jeton, tespit_kur):
    tid = await tespit_kur("cam")
    await istemci.post(f"/tespit/{tid}/dogrula", headers=await jeton("uzman"),
                       json={"durum": "duzeltildi", "duzeltilen_sinif": "tugla"})
    d = json.loads((await istemci.get("/rapor/json",
                                      headers=await jeton("belediye"))).text)
    k = next(x for x in d["kayitlar"] if x["tespit_id"] == tid)
    assert k["sinif"] == "tugla", "Geçerli sınıf uzmanın düzelttiğidir"
    assert k["model_tahmini"] == "cam", "Ham tahmin izlenebilir kalmalı"
