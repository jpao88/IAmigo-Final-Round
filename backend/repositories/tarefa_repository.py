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

    # ---- Hoje (Épica 3) ----

    def listar_do_dia(self, usuario_id, data):
        """As tarefas planejadas para `data`, na ordem do dia, com os passos (para os minutos)."""
        with SessionLocal() as session:
            comando = (
                select(Tarefa)
                .where(Tarefa.usuario_id == usuario_id, Tarefa.data_planejada == data)
                .options(selectinload(Tarefa.passos))
                .order_by(Tarefa.ordem_dia, Tarefa.id)
            )
            return list(session.scalars(comando))

    def ultima_data_planejada_antes(self, usuario_id, data):
        """O dia mais recente antes de `data` que teve tarefas em Hoje (ou None)."""
        with SessionLocal() as session:
            comando = select(func.max(Tarefa.data_planejada)).where(
                Tarefa.usuario_id == usuario_id, Tarefa.data_planejada < data
            )
            return session.scalar(comando)

    def listar_por_ids(self, usuario_id, ids):
        with SessionLocal() as session:
            comando = select(Tarefa).where(
                Tarefa.usuario_id == usuario_id, Tarefa.id.in_(ids)
            )
            return list(session.scalars(comando))

    def contar_pendentes_do_dia(self, usuario_id, data):
        with SessionLocal() as session:
            comando = select(func.count()).where(
                Tarefa.usuario_id == usuario_id,
                Tarefa.data_planejada == data,
                Tarefa.concluida.is_(False),
            )
            return session.scalar(comando)

    def planejar(self, usuario_id, ids_em_ordem, data):
        """Põe as tarefas em `data`, depois das que já estão lá, na ordem recebida."""
        with SessionLocal() as session:
            ultima = session.scalar(
                select(func.max(Tarefa.ordem_dia)).where(
                    Tarefa.usuario_id == usuario_id, Tarefa.data_planejada == data
                )
            ) or 0
            por_id = {
                tarefa.id: tarefa
                for tarefa in session.scalars(select(Tarefa).where(Tarefa.id.in_(ids_em_ordem)))
            }

            for ordem, tarefa_id in enumerate(ids_em_ordem, start=ultima + 1):
                por_id[tarefa_id].data_planejada = data
                por_id[tarefa_id].ordem_dia = ordem

            session.commit()
            return [por_id[tarefa_id] for tarefa_id in ids_em_ordem]

    def reordenar_dia(self, ids_em_ordem):
        with SessionLocal() as session:
            por_id = {
                tarefa.id: tarefa
                for tarefa in session.scalars(select(Tarefa).where(Tarefa.id.in_(ids_em_ordem)))
            }

            for ordem, tarefa_id in enumerate(ids_em_ordem, start=1):
                por_id[tarefa_id].ordem_dia = ordem

            session.commit()

    def tirar_do_dia(self, tarefa_id):
        """Volta para a Bandeja: sem data e sem posição."""
        with SessionLocal() as session:
            tarefa = session.get(Tarefa, tarefa_id)
            tarefa.data_planejada = None
            tarefa.ordem_dia = None
            session.commit()
            return tarefa

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

    def concluir(self, tarefa_id):
        """Marca como concluída (sem desfazer se já estava)."""
        with SessionLocal() as session:
            tarefa = session.get(Tarefa, tarefa_id)
            if not tarefa.concluida:
                tarefa.concluida = True
                tarefa.concluida_em = datetime.now()
                session.commit()
            return tarefa

    def renomear(self, tarefa_id, titulo):
        with SessionLocal() as session:
            tarefa = session.get(Tarefa, tarefa_id)
            tarefa.titulo = titulo
            session.commit()
            return tarefa

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
