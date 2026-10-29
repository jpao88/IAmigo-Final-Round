from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from config.database import SessionLocal
from models.tarefa import Tarefa


class TarefaRepository:
    def listar_por_usuario(self, usuario_id):
        """Devolve as tarefas já com tarefa.passos carregado (1 consulta extra no total)."""
        with SessionLocal() as session:
            comando = (
                select(Tarefa)
                .where(Tarefa.usuario_id == usuario_id)
                .options(selectinload(Tarefa.passos))
                .order_by(Tarefa.id)
            )
            return list(session.scalars(comando))

    def criar(self, usuario_id, titulo):
        with SessionLocal() as session:
            tarefa = Tarefa(
                usuario_id=usuario_id,
                titulo=titulo
            )
            session.add(tarefa)
            session.commit()
            session.refresh(tarefa)
            return tarefa

    def buscar_por_id(self, tarefa_id):
        with SessionLocal() as session:
            comando = select(Tarefa).where(Tarefa.id == tarefa_id)
            return session.scalar(comando)

    def alternar_concluida(self, tarefa_id):
        with SessionLocal() as session:
            comando = select(Tarefa).where(Tarefa.id == tarefa_id)
            tarefa = session.scalar(comando)
            tarefa.concluida = not tarefa.concluida
            tarefa.concluida_em = datetime.now() if tarefa.concluida else None
            session.commit()
            session.refresh(tarefa)
            return tarefa

    def excluir(self, tarefa_id):
        with SessionLocal() as session:
            comando = select(Tarefa).where(Tarefa.id == tarefa_id)
            tarefa = session.scalar(comando)
            session.delete(tarefa)
            session.commit()
