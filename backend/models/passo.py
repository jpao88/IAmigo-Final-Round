from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.database import Base


class Passo(Base):
    __tablename__ = "passos"

    id: Mapped[int] = mapped_column(primary_key=True)
    tarefa_id: Mapped[int] = mapped_column(
        ForeignKey("tarefas.id", ondelete="CASCADE"), nullable=False
    )
    texto: Mapped[str] = mapped_column(String(255), nullable=False)
    ordem: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    minutos_estimados: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=10, server_default="10"
    )
    gerado_por_ia: Mapped[bool] = mapped_column(nullable=False, default=False)
    concluido: Mapped[bool] = mapped_column(nullable=False, default=False)
    concluido_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Passo travado que foi dividido com "Me atasqué": não aparece no modo foco.
    substituido: Mapped[bool] = mapped_column(nullable=False, default=False)
    # Nos passos criados por "Me atasqué", qual era o passo original.
    passo_origem_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("passos.id", ondelete="SET NULL"), nullable=True
    )

    tarefa: Mapped["Tarefa"] = relationship(back_populates="passos")
