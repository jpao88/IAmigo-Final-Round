from repositories.usuario_repository import UsuarioRepository
from core.erros import CredenciaisInvalidas, DadosInvalidos, NaoEncontrado
from core.seguranca import gerar_hash_senha, verificar_senha


class UsuarioService:
    def __init__(self, repository=None):
        self.repository = repository or UsuarioRepository()

    def _validar_nome(self, nome):
        nome = nome.strip()

        if not nome:
            raise DadosInvalidos("O nome não pode ficar vazio.")

        if len(nome) < 3:
            raise DadosInvalidos("O nome precisa ter pelo menos 3 caracteres.")

        return nome

    def _validar_email(self, email):
        email = email.strip().lower()

        if not email or "@" not in email:
            raise DadosInvalidos("Informe um e-mail válido.")

        return email

    def listar_usuarios(self):
        return self.repository.listar()

    def buscar_usuario(self, usuario_id):
        usuario = self.repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado.")

        return usuario

    def criar_usuario(self, nome, email, senha):
        nome = self._validar_nome(nome)
        email = self._validar_email(email)

        if self.repository.buscar_por_email(email) is not None:
            raise DadosInvalidos("Já existe uma conta com esse e-mail.")

        if len(senha) < 6:
            raise DadosInvalidos("A senha precisa ter pelo menos 6 caracteres.")

        return self.repository.criar(nome, email, gerar_hash_senha(senha))

    def atualizar_usuario(self, usuario_id, nome):
        usuario = self.repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado.")

        nome = self._validar_nome(nome)

        return self.repository.atualizar(usuario_id, nome)

    def alterar_limite_hoje(self, usuario_id, limite_hoje):
        """H3.5: quantas tarefas cabem em Hoje, de 1 a 5."""
        self.buscar_usuario(usuario_id)

        if not 1 <= limite_hoje <= 5:
            raise DadosInvalidos("O limite precisa estar entre 1 e 5.")

        return self.repository.atualizar_limite_hoje(usuario_id, limite_hoje)

    def concluir_onboarding(self, usuario_id):
        """H6.3: a guia do primeiro uso aparece uma vez só."""
        usuario = self.buscar_usuario(usuario_id)

        if usuario.onboarding_concluido:
            return usuario

        return self.repository.concluir_onboarding(usuario_id)

    def excluir_usuario(self, usuario_id):
        usuario = self.repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado.")

        self.repository.excluir(usuario_id)

    def autenticar(self, email, senha):
        # Mesma normalização do cadastro, para "Ana@Exemplo.com " achar "ana@exemplo.com".
        usuario = self.repository.buscar_por_email(email.strip().lower())

        # Mesma mensagem para e-mail inexistente e senha errada:
        # não revela quais e-mails têm conta.
        if usuario is None or not verificar_senha(senha, usuario.senha_hash):
            raise CredenciaisInvalidas("E-mail ou senha inválidos.")

        return usuario
