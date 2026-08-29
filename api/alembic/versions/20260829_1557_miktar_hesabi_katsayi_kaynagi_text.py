"""miktar_hesabi.katsayi_kaynagi -> Text

Katsayı kaynağı atfı varchar(300)'e sığmıyordu.

Bir katsayının dayanağı, üretilen tonajın tek gerekçesidir. Tam atıf
(kurum + belge + tarih + EPA'nın kendi gösterdiği birincil kaynak) 300
karakteri aşınca kayıt yazılamıyor, miktar hesabı 500 ile düşüyordu.
Uzunluk sınırı yüzünden gerekçeyi kısaltmak izlenebilirliği veri
modeline feda etmek olurdu; sütun genişletildi.

Geri alma güvenli DEĞİLDİR: 300 karakterden uzun mevcut atıflar
kırpılır. Bu yüzden downgrade veri kaybını açıkça bildirir.

Revision ID: 175ce5db0b21
Revises: fc3d51b6229a
Create Date: 2026-08-29 15:57:32.960983
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
import geoalchemy2


revision = '175ce5db0b21'
down_revision = 'fc3d51b6229a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "miktar_hesabi", "katsayi_kaynagi",
        existing_type=sa.String(length=300),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade() -> None:
    # USING ile açık kırpma: veri kaybı sessizce olmaz, burada yazılıdır.
    op.execute(
        "ALTER TABLE miktar_hesabi "
        "ALTER COLUMN katsayi_kaynagi TYPE VARCHAR(300) "
        "USING left(katsayi_kaynagi, 300)"
    )
