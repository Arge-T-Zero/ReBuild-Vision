"""demo_damgasi — demo verisinin sürüm damgası

Canlı ortamda demo verisi 30.08.2026'da bir kez kuruldu ve bir daha hiç
yenilenmedi: `scripts/demo_veri.py` ilk demo sahasını görünce "zaten var"
deyip dönüyordu. Sınıf listesi 02.09'da 10'dan 5'e inince canlı veri
tabanında artık üretilemeyecek sınıflar (`sert_plastik`, `karton`,
`konteyner`, `alcipan`, `dolgu_toprak`) kaldı.

Bu tablo o erken dönüşü SÜRÜME BAĞLAR: kurulan senaryonun parmak izi
burada durur. Parmak izi aynıysa hiçbir şeye dokunulmaz; değiştiyse
yalnızca sentetik demo kayıtları temizlenip yeniden kurulur.

Tek satırlıdır (id = 1). Tabloyu geri almak veri kaybı DEĞİLDİR: damga
yoksa demo verisi bir kez yeniden kurulur, o kadar.

Revision ID: 4b1a7c0d9e22
Revises: 175ce5db0b21
Create Date: 2026-09-06 15:00:00.000000
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = '4b1a7c0d9e22'
down_revision = '175ce5db0b21'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "demo_damgasi",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("damga", sa.String(length=64), nullable=False),
        sa.Column("senaryo_surumu", sa.String(length=20), nullable=False),
        sa.Column("siniflar_surumu", sa.String(length=20), nullable=False),
        sa.Column("siniflar", sa.Text(), nullable=False),
        sa.Column("tarih", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        # Tek satır: demo verisi tek bir sürümle kuruludur, ikinci bir
        # damga satırı "hangisi geçerli?" sorusunu doğurur.
        sa.CheckConstraint("id = 1", name="ck_demo_damgasi_tek_satir"),
    )


def downgrade() -> None:
    op.drop_table("demo_damgasi")
