from datetime import datetime

from sqlalchemy import func, select

from config.database import SessionLocal
from models.passo import Passo


class PassoRepository:
    def listar_por_tarefa(self, tarefa_id):
        with SessionLocal() as session:
            comando = (
                select(Passo)
                .where(Passo.tarefa_id == tarefa_id)
                .order_by(Passo.ordem)
            )
            return list(session.scalars(comando))

    def _proxima_ordem(self, session, tarefa_id):
        comando = select(func.max(Passo.ordem)).where(Passo.tarefa_id == tarefa_id)
        return (session.scalar(comando) or 0) + 1

    def criar(self, tarefa_id, texto):
        with SessionLocal() as session:
            passo = Passo(
                tarefa_id=tarefa_id,
                texto=texto,
                ordem=self._proxima_ordem(session, tarefa_id)
            )
            session.add(passo)
            session.commit()
            session.refresh(passo)
            return passo

    def criar_varios(self, tarefa_id, textos, gerado_por_ia=False):
        with SessionLocal() as session:
            inicio = self._proxima_ordem(session, tarefa_id)
            passos = [
                Passo(
                    tarefa_id=tarefa_id,
                    texto=texto,
                    ordem=indice,
                    gerado_por_ia=gerado_por_ia
                )
                for indice, texto in enumerate(textos, start=inicio)
            ]
            session.add_all(passos)
            session.commit()

            for passo in passos:
                session.refresh(passo)

            return passos

    def buscar_por_id(self, passo_id):
        with SessionLocal() as session:
            comando = select(Passo).where(Passo.id == passo_id)
            return session.scalar(comando)

    def alternar_concluido(self, passo_id):
        with SessionLocal() as session:
            comando = select(Passo).where(Passo.id == passo_id)
            passo = session.scalar(comando)
            passo.concluido = not passo.concluido
            passo.concluido_em = datetime.now() if passo.concluido else None
            session.commit()
            session.refresh(passo)
            return passo

    def excluir(self, passo_id):
        with SessionLocal() as session:
            comando = select(Passo).where(Passo.id == passo_id)
            passo = session.scalar(comando)
            session.delete(passo)
            session.commit()
