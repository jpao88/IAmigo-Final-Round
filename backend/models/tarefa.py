from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from config.database import Base


class Tarefa(Base):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    # Vazia: a tarefa está na Bandeja. Com data: está em Hoje desse dia.
    data_planejada: Mapped[Optional[date]] = mapped_column(nullable=True)
    # Posição em Hoje; a 1 é "Agora".
    ordem_dia: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    concluida: Mapped[bool] = mapped_column(nullable=False, default=False)
    concluida_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, server_default=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="tarefas")

    # passive_deletes: quem apaga os passos é o ON DELETE CASCADE do banco.
    passos: Mapped[List["Passo"]] = relationship(
        back_populates="tarefa",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Passo.ordem",
    )
