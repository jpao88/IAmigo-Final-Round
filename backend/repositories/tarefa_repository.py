from datetime import datetime

from sqlalchemy import func, or_, select
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

    def listar_bandeja(self, usuario_id, hoje):
        """Não concluídas, sem data ou com data anterior a `hoje`.

        As mais novas primeiro. As que chegaram juntas (mesmo criado_em)
        ficam na ordem em que a pessoa escreveu as linhas.
        """
        with SessionLocal() as session:
            comando = (
                select(Tarefa)
                .where(
                    Tarefa.usuario_id == usuario_id,
                    Tarefa.concluida.is_(False),
                    or_(Tarefa.data_planejada.is_(None), Tarefa.data_planejada < hoje),
                )
                .order_by(Tarefa.criado_em.desc(), Tarefa.id)
            )
            return list(session.scalars(comando))

    def criar_varias(self, usuario_id, titulos):
        """Grava todas numa única transação: se uma falhar, nenhuma fica salva.

        Todas recebem o mesmo criado_em (relógio do banco): cada INSERT até o
        Aiven leva meio segundo e, sem isso, a ordem da Bandeja se embaralharia.

        Todos os campos são preenchidos aqui, então não é preciso reler cada
        tarefa do banco depois do commit (economiza uma consulta por tarefa).
        """
        with SessionLocal() as session:
            agora = session.scalar(select(func.now()))
            tarefas = [
                Tarefa(
                    usuario_id=usuario_id,
                    titulo=titulo,
                    data_planejada=None,
                    ordem_dia=None,
                    concluida=False,
                    concluida_em=None,
                    criado_em=agora,
                )
                for titulo in titulos
            ]
            session.add_all(tarefas)
            session.commit()

            return tarefas

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
