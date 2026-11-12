from sqlalchemy import select

from config.database import SessionLocal
from models.usuario import Usuario


class UsuarioRepository:
    def listar(self):
        with SessionLocal() as session:
            comando = select(Usuario).order_by(Usuario.nome)
            return list(session.scalars(comando))

    def buscar_por_email(self, email):
        with SessionLocal() as session:
            comando = select(Usuario).where(Usuario.email == email)
            return session.scalar(comando)

    def buscar_por_id(self, usuario_id):
        with SessionLocal() as session:
            comando = select(Usuario).where(Usuario.id == usuario_id)
            return session.scalar(comando)

    def criar(self, nome, email, senha_hash):
        with SessionLocal() as session:
            usuario = Usuario(
                nome=nome,
                email=email,
                senha_hash=senha_hash
            )
            session.add(usuario)
            session.commit()
            session.refresh(usuario)
            return usuario

    def atualizar(self, usuario_id, nome):
        with SessionLocal() as session:
            comando = select(Usuario).where(Usuario.id == usuario_id)
            usuario = session.scalar(comando)
            usuario.nome = nome
            session.commit()
            session.refresh(usuario)
            return usuario

    def atualizar_limite_hoje(self, usuario_id, limite_hoje):
        with SessionLocal() as session:
            usuario = session.get(Usuario, usuario_id)
            usuario.limite_hoje = limite_hoje
            session.commit()
            return usuario

    def concluir_onboarding(self, usuario_id):
        with SessionLocal() as session:
            usuario = session.get(Usuario, usuario_id)
            usuario.onboarding_concluido = True
            session.commit()
            return usuario

    def excluir(self, usuario_id):
        with SessionLocal() as session:
            comando = select(Usuario).where(Usuario.id == usuario_id)
            usuario = session.scalar(comando)
            session.delete(usuario)
            session.commit()
