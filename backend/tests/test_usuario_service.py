import unittest
from types import SimpleNamespace

from services.usuario_service import UsuarioService


class UsuarioRepositoryFake:
    """Repositório em memória: simula o banco sem precisar do MySQL."""

    def __init__(self):
        self.usuarios = []
        self.proximo_id = 1

    def listar(self):
        return list(self.usuarios)

    def buscar_por_email(self, email):
        for usuario in self.usuarios:
            if usuario.email == email:
                return usuario
        return None

    def buscar_por_id(self, usuario_id):
        for usuario in self.usuarios:
            if usuario.id == usuario_id:
                return usuario
        return None

    def criar(self, nome, email, senha_hash):
        usuario = SimpleNamespace(
            id=self.proximo_id,
            nome=nome,
            email=email,
            senha_hash=senha_hash
        )
        self.proximo_id += 1
        self.usuarios.append(usuario)
        return usuario

    def atualizar(self, usuario_id, nome):
        usuario = self.buscar_por_id(usuario_id)
        usuario.nome = nome
        return usuario


class TestUsuarioServiceCriar(unittest.TestCase):
    def setUp(self):
        self.repository = UsuarioRepositoryFake()
        self.service = UsuarioService(repository=self.repository)

    def test_criar_com_dados_validos(self):
        usuario = self.service.criar_usuario("Ana", "  Ana@Exemplo.com ", "segredo1")

        self.assertEqual(usuario.nome, "Ana")
        self.assertEqual(usuario.email, "ana@exemplo.com")
        self.assertNotEqual(usuario.senha_hash, "segredo1")
        self.assertEqual(len(self.repository.usuarios), 1)

    def test_nome_vazio_e_recusado(self):
        with self.assertRaises(ValueError) as contexto:
            self.service.criar_usuario("   ", "ana@exemplo.com", "segredo1")

        self.assertEqual(str(contexto.exception), "O nome não pode ficar vazio.")
        self.assertEqual(len(self.repository.usuarios), 0)

    def test_nome_curto_e_recusado(self):
        with self.assertRaises(ValueError) as contexto:
            self.service.criar_usuario("Al", "al@exemplo.com", "segredo1")

        self.assertEqual(
            str(contexto.exception),
            "O nome precisa ter pelo menos 3 caracteres."
        )

    def test_email_invalido_e_recusado(self):
        with self.assertRaises(ValueError) as contexto:
            self.service.criar_usuario("Bia", "bia.exemplo.com", "segredo1")

        self.assertEqual(str(contexto.exception), "Informe um e-mail válido.")

    def test_senha_curta_e_recusada(self):
        with self.assertRaises(ValueError) as contexto:
            self.service.criar_usuario("Bia", "bia@exemplo.com", "12345")

        self.assertEqual(
            str(contexto.exception),
            "A senha precisa ter pelo menos 6 caracteres."
        )
        self.assertEqual(len(self.repository.usuarios), 0)

    def test_email_duplicado_e_recusado(self):
        self.service.criar_usuario("Ana", "ana@exemplo.com", "segredo1")

        with self.assertRaises(ValueError) as contexto:
            self.service.criar_usuario("Ana Paula", "ANA@exemplo.com", "segredo2")

        self.assertEqual(
            str(contexto.exception),
            "Já existe uma conta com esse e-mail."
        )
        self.assertEqual(len(self.repository.usuarios), 1)


class TestUsuarioServiceAtualizar(unittest.TestCase):
    def setUp(self):
        self.repository = UsuarioRepositoryFake()
        self.service = UsuarioService(repository=self.repository)

    def test_atualizar_nome(self):
        usuario = self.service.criar_usuario("Ana", "ana@exemplo.com", "segredo1")

        atualizado = self.service.atualizar_usuario(usuario.id, "Ana Paula")

        self.assertEqual(atualizado.nome, "Ana Paula")


class TestUsuarioServiceAutenticar(unittest.TestCase):
    def setUp(self):
        self.repository = UsuarioRepositoryFake()
        self.service = UsuarioService(repository=self.repository)
        self.ana = self.service.criar_usuario("Ana", "ana@exemplo.com", "segredo1")

    def test_login_com_email_e_senha_corretos(self):
        usuario = self.service.autenticar("ana@exemplo.com", "segredo1")

        self.assertEqual(usuario.id, self.ana.id)

    def test_email_ignora_maiusculas_e_espacos(self):
        usuario = self.service.autenticar("  Ana@Exemplo.COM ", "segredo1")

        self.assertEqual(usuario.id, self.ana.id)

    def test_nomes_repetidos_nao_atrapalham_o_login(self):
        outra_ana = self.service.criar_usuario("Ana", "ana.paula@exemplo.com", "segredo2")

        usuario = self.service.autenticar("ana.paula@exemplo.com", "segredo2")

        self.assertEqual(usuario.id, outra_ana.id)

    def test_senha_errada_e_email_inexistente_tem_a_mesma_mensagem(self):
        for email, senha in (
            ("ana@exemplo.com", "errada"),
            ("ninguem@exemplo.com", "segredo1"),
        ):
            with self.subTest(email=email):
                with self.assertRaises(ValueError) as contexto:
                    self.service.autenticar(email, senha)

                self.assertEqual(str(contexto.exception), "E-mail ou senha inválidos.")


if __name__ == "__main__":
    unittest.main()
