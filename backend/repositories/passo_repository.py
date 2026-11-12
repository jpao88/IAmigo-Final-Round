from datetime import datetime

from sqlalchemy import func, select, update

from config.database import SessionLocal
from models.passo import Passo


class PassoRepository:
    """Os passos novos têm todos os campos preenchidos aqui: assim não é preciso
    reler cada um do banco depois do commit (cada ida ao Aiven custa ~0,4 s)."""

    def listar_por_tarefa(self, tarefa_id):
        with SessionLocal() as session:
            comando = (
                select(Passo)
                .where(Passo.tarefa_id == tarefa_id)
                .order_by(Passo.ordem, Passo.id)
            )
            return list(session.scalars(comando))

    def _proxima_ordem(self, session, tarefa_id):
        comando = select(func.max(Passo.ordem)).where(Passo.tarefa_id == tarefa_id)
        return (session.scalar(comando) or 0) + 1

    def _novo(self, tarefa_id, texto, minutos_estimados, ordem, gerado_por_ia):
        return Passo(
            tarefa_id=tarefa_id,
            texto=texto,
            ordem=ordem,
            minutos_estimados=minutos_estimados,
            gerado_por_ia=gerado_por_ia,
            concluido=False,
            concluido_em=None,
            substituido=False,
            passo_origem_id=None,
        )

    def criar(self, tarefa_id, texto, minutos_estimados=10):
        with SessionLocal() as session:
            passo = self._novo(
                tarefa_id, texto, minutos_estimados,
                ordem=self._proxima_ordem(session, tarefa_id),
                gerado_por_ia=False,
            )
            session.add(passo)
            session.commit()
            return passo

    def criar_varios(self, tarefa_id, passos, gerado_por_ia=False):
        """`passos`: [{"texto": ..., "minutos_estimados": ...}], na ordem em que serão feitos."""
        with SessionLocal() as session:
            inicio = self._proxima_ordem(session, tarefa_id)
            novos = [
                self._novo(
                    tarefa_id, passo["texto"], passo["minutos_estimados"],
                    ordem=indice, gerado_por_ia=gerado_por_ia,
                )
                for indice, passo in enumerate(passos, start=inicio)
            ]
            session.add_all(novos)
            session.commit()
            return novos

    def buscar_por_id(self, passo_id):
        with SessionLocal() as session:
            comando = select(Passo).where(Passo.id == passo_id)
            return session.scalar(comando)

    def atualizar(self, passo_id, texto, minutos_estimados):
        with SessionLocal() as session:
            passo = session.get(Passo, passo_id)
            passo.texto = texto
            passo.minutos_estimados = minutos_estimados
            session.commit()
            return passo

    def reordenar(self, tarefa_id, ids_em_ordem):
        """Dá a ordem 1, 2, 3... aos passos, na sequência recebida."""
        with SessionLocal() as session:
            comando = select(Passo).where(
                Passo.tarefa_id == tarefa_id, Passo.id.in_(ids_em_ordem)
            )
            por_id = {passo.id: passo for passo in session.scalars(comando)}

            for ordem, passo_id in enumerate(ids_em_ordem, start=1):
                por_id[passo_id].ordem = ordem

            session.commit()
            return [por_id[passo_id] for passo_id in ids_em_ordem]

    def concluir(self, passo_id):
        """Marca como concluído (sem desfazer se já estava: um toque duplo em "Hecho" não volta atrás)."""
        with SessionLocal() as session:
            passo = session.get(Passo, passo_id)
            if not passo.concluido:
                passo.concluido = True
                passo.concluido_em = datetime.now()
                session.commit()
            return passo

    def dividir(self, passo_id, novos):
        """H4.4: o passo original fica `substituido` (não se apaga) e os novos
        entram no lugar dele, apontando para ele; os seguintes andam para frente."""
        with SessionLocal() as session:
            original = session.get(Passo, passo_id)
            original.substituido = True

            session.execute(
                update(Passo)
                .where(Passo.tarefa_id == original.tarefa_id, Passo.ordem > original.ordem)
                .values(ordem=Passo.ordem + len(novos))
            )

            criados = []
            for deslocamento, novo in enumerate(novos, start=1):
                passo = self._novo(
                    original.tarefa_id, novo["texto"], novo["minutos_estimados"],
                    ordem=original.ordem + deslocamento, gerado_por_ia=True,
                )
                passo.passo_origem_id = original.id
                criados.append(passo)

            session.add_all(criados)
            session.commit()
            return criados

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
