from datetime import date, datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from config.database import Base


class FechamentoDia(Base):
    __tablename__ = "fechamentos_dia"
    __table_args__ = (
        UniqueConstraint("usuario_id", "data", name="uq_fechamento_usuario_data"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    data: Mapped[date] = mapped_column(nullable=False)
    fechado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="fechamentos")
