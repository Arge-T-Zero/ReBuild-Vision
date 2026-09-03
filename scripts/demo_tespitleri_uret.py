#!/usr/bin/env python3
"""Demo tespitlerini GERÇEK modelden üretir.

⚠️ NEDEN AYRI BİR BETİK

`scripts/demo_veri.py` 02.09.2026'ya kadar tespit kutularını ve güven
skorlarını ELLE YAZILMIŞ bir listeden alıyordu. Sayılar makul görünüyordu
ama hiçbiri bir modelden gelmiyordu — yani jürinin demo ortamında gördüğü
her kutu uydurmaydı. Ana talimat Bölüm 9.5 sahteliğin gizlenmemesini
istiyor; en iyisi sahteliği hiç üretmemek.

Bu betik gerçek `best.pt` ile çıkarım yapar ve sonucu
`scripts/demo_tespitleri.json` dosyasına yazar. Dosya depoya girer, böylece:

  - demo verisi ağırlık olmadan da kurulabilir (dosya hazır),
  - ama içindeki her kutu ve her güven skoru GERÇEK model çıktısıdır.

Ne gerçek DEĞİLDİR, açıkça: görüntülerin kendisi sentetiktir
(`web/public/gorseller/README.md`) ve doğrulama/ölçüm senaryosu
`demo_veri.py` tarafından üstüne yazılır — sahada gerçek bir uzman ya da
gerçek bir şerit metre yok.

KULLANIM

    # Ağırlığı yerine koyun (Releases → model-v1)
    cp best.pt model-service/agirliklar/

    # Model servisini çalıştırın
    python -m uvicorn app:app --app-dir model-service --port 8091

    # Tespitleri üretin
    MODEL_SERVIS=http://127.0.0.1:8091 python scripts/demo_tespitleri_uret.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

DEPO_KOKU = Path(__file__).resolve().parents[1]
SERVIS = os.getenv("MODEL_SERVIS", "http://127.0.0.1:8091")
CIKTI = DEPO_KOKU / "scripts/demo_tespitleri.json"

# Demo verisinde kullanılan sentetik görüntüler.
GORUNTULER = [
    "ornek-enkaz-1.webp",
    "ornek-enkaz-2.webp",
    "ornek-enkaz-3.webp",
]


def _cokparcali(alan: str, ad: str, icerik: bytes, tur: str) -> tuple[bytes, str]:
    """multipart/form-data gövdesi kurar — ek bağımlılık istemeden."""
    sinir = uuid.uuid4().hex
    govde = (
        f"--{sinir}\r\n"
        f'Content-Disposition: form-data; name="{alan}"; filename="{ad}"\r\n'
        f"Content-Type: {tur}\r\n\r\n"
    ).encode() + icerik + f"\r\n--{sinir}--\r\n".encode()
    return govde, f"multipart/form-data; boundary={sinir}"


def _istek(yol: str, veri: bytes | None = None, tur: str | None = None) -> dict:
    istek = urllib.request.Request(f"{SERVIS}{yol}", data=veri)
    if tur:
        istek.add_header("Content-Type", tur)
    with urllib.request.urlopen(istek, timeout=180) as y:
        return json.loads(y.read())


def main() -> int:
    try:
        saglik = _istek("/health")
    except (urllib.error.URLError, OSError) as e:
        print(f"HATA: model servisine ulaşılamadı ({SERVIS}): {e}", file=sys.stderr)
        print("Servisi çalıştırın: python -m uvicorn app:app "
              "--app-dir model-service --port 8091", file=sys.stderr)
        return 1

    # SAHTE servisle üretmeyi REDDET. Bu betiğin tek varlık sebebi
    # demo kutularının gerçek olması; sahte servisten üretilen bir dosya
    # elle yazılmış listeden daha iyi olmazdı, üstelik gerçek görünürdü.
    if saglik.get("sahte"):
        print("HATA: bağlanılan servis SAHTE. Gerçek ağırlıkla çalıştırın "
              "(model-service/agirliklar/best.pt).", file=sys.stderr)
        return 1
    if not saglik.get("agirlik_yuklendi"):
        print(f"HATA: ağırlık yüklü değil — {saglik.get('hata', '')}", file=sys.stderr)
        return 1

    kayit = {
        "_aciklama": (
            "GERÇEK model çıktısı. Kutular ve güven skorları "
            "model-service/agirliklar/best.pt ile üretilmiştir; elle "
            "yazılmamıştır. Görüntülerin kendisi sentetiktir "
            "(web/public/gorseller/README.md). Yeniden üretmek için: "
            "scripts/demo_tespitleri_uret.py"
        ),
        "model": saglik.get("model"),
        "model_license": saglik.get("model_license"),
        "review_threshold": saglik.get("review_threshold"),
        "goruntuler": [],
    }

    for ad in GORUNTULER:
        yol = DEPO_KOKU / "web/public/gorseller" / ad
        if not yol.is_file():
            print(f"HATA: {yol} yok", file=sys.stderr)
            return 1
        govde, tur = _cokparcali("file", ad, yol.read_bytes(), "image/webp")
        sonuc = _istek("/predict", govde, tur)
        kayit["goruntuler"].append({
            "dosya": ad,
            "genislik": sonuc["image_width"],
            "yukseklik": sonuc["image_height"],
            "tespitler": [
                {
                    "sinif": t["class_name"],
                    "guven": t["confidence"],
                    "bbox": t["bbox"],
                    "bbox_format": t["bbox_format"],
                    "inceleme_gerekli": t["needs_review"],
                }
                for t in sonuc["detections"]
            ],
        })
        print(f"  {ad}: {len(sonuc['detections'])} tespit")

    CIKTI.write_text(
        json.dumps(kayit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    toplam = sum(len(g["tespitler"]) for g in kayit["goruntuler"])
    print(f"\n{CIKTI.relative_to(DEPO_KOKU)} yazıldı — "
          f"{len(kayit['goruntuler'])} görüntü, {toplam} gerçek tespit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
