from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config.database import SessionLocal
from models.fechamento_dia import FechamentoDia


class FechamentoRepository:
    def existe(self, usuario_id, data):
        with SessionLocal() as session:
            comando = select(FechamentoDia.id).where(
                FechamentoDia.usuario_id == usuario_id, FechamentoDia.data == data
            )
            return session.scalar(comando) is not None

    def criar(self, usuario_id, data):
        """Registra o fechamento. Se o dia já estava fechado (ex.: dois toques
        quase juntos), a chave única do banco impede o segundo e nada muda."""
        with SessionLocal() as session:
            session.add(FechamentoDia(usuario_id=usuario_id, data=data))
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
