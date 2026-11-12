from core.seguranca import gerar_token_acesso
from services.usuario_service import UsuarioService


class UsuarioController:
    """Repassa os pedidos da API para o service.

    Os erros sobem como exceções de core/erros.py e viram
    respostas HTTP nos handlers registrados em api_app.py.
    """

    def __init__(self, service=None):
        self.service = service or UsuarioService()

    def listar_perfis(self):
        return self.service.listar_usuarios()

    def buscar_perfil(self, usuario_id):
        return self.service.buscar_usuario(usuario_id)

    def criar_perfil(self, nome, email, senha):
        return self.service.criar_usuario(nome, email, senha)

    def atualizar_perfil(self, usuario_id, nome):
        return self.service.atualizar_usuario(usuario_id, nome)

    def alterar_limite_hoje(self, usuario_id, limite_hoje):
        return self.service.alterar_limite_hoje(usuario_id, limite_hoje)

    def concluir_onboarding(self, usuario_id):
        return self.service.concluir_onboarding(usuario_id)

    def excluir_perfil(self, usuario_id):
        self.service.excluir_usuario(usuario_id)

    def autenticar(self, email, senha):
        usuario = self.service.autenticar(email, senha)
        token, expira_em = gerar_token_acesso(usuario.id, usuario.nome)
        return {
            "usuario": usuario,
            "access_token": token,
            "token_type": "bearer",
            "expires_in": expira_em
        }
