"""Roller ve yetkiler — tek tanım yeri.

Kaynak: ana talimat Bölüm 5 (rapor Bölüm 6'daki altı rol).
Yetki kontrolü API katmanında yapılır; arayüzde gizleme yeterli değildir.
"""
from __future__ import annotations

import enum


class Rol(str, enum.Enum):
    YONETICI = "yonetici"      # rol atar, onaylar (sistem yöneticisi)
    AFAD = "afad"              # çok sahalı görünüm
    BELEDIYE = "belediye"      # kendi ilçesi/sahaları
    SAHA = "saha"              # kendi sahası
    UZMAN = "uzman"            # atandığı sahalar — doğrulama
    YIKIM = "yikim"            # yalnızca kendi sahası, salt okunur
    TESIS = "tesis"            # kendine yönlendirilen kayıtlar, salt okunur


class OnayDurumu(str, enum.Enum):
    BEKLEMEDE = "beklemede"
    ONAYLANDI = "onaylandi"
    REDDEDILDI = "reddedildi"


# Ana talimat Bölüm 5'teki yetki tablosunun kod karşılığı.
SAHA_OLUSTURABILIR = {Rol.YONETICI, Rol.BELEDIYE, Rol.AFAD}
GORUNTU_YUKLEYEBILIR = {Rol.YONETICI, Rol.SAHA, Rol.BELEDIYE}
OLCUM_GIREBILIR = {Rol.YONETICI, Rol.SAHA, Rol.UZMAN}
DOGRULAYABILIR = {Rol.YONETICI, Rol.UZMAN}
RAPOR_ALABILIR = {Rol.YONETICI, Rol.BELEDIYE, Rol.AFAD}
ROL_ATAYABILIR = {Rol.YONETICI}

# Tehlikeli madde YÖNLENDİRMESİ — teşhis değil (ana talimat Bölüm 1.2).
# Sahada şüphe uyandıran bir durumu gören herkes incelemeye yönlendirebilir.
INCELEMEYE_YONLENDIREBILIR = {Rol.YONETICI, Rol.SAHA, Rol.UZMAN, Rol.BELEDIYE}

# Laboratuvar sonucunu YALNIZCA insan girer ve yalnızca yetkili uzman.
# Model bu alana asla yazmaz.
LAB_SONUCU_GIREBILIR = {Rol.YONETICI, Rol.UZMAN}

# Yalnızca görüntüleme yapabilen roller — hiçbir yazma işlemi yapamazlar.
SALT_OKUNUR = {Rol.YIKIM, Rol.TESIS}

# Bütün sahaları görebilen roller. Diğerleri yalnızca ilişkili oldukları
# sahaları görür (bkz. api/app/services/queries.py).
TUM_SAHALARI_GORUR = {Rol.YONETICI, Rol.AFAD}
