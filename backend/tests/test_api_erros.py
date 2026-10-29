import unittest
from types import SimpleNamespace

from fastapi.testclient import TestClient

import api.rotas_auth as rotas_auth
import api.rotas_tarefas as rotas_tarefas
import api.rotas_usuarios as rotas_usuarios
from api.dependencias import exigir_dono
from api_app import app
from core.erros import CredenciaisInvalidas, DadosInvalidos, FalhaIA, NaoEncontrado


class ServiceQueFalha:
    """Service falso: qualquer método chamado lança o erro configurado."""

    def __init__(self, erro):
        self.erro = erro

    def __getattr__(self, nome):
        def metodo(*args, **kwargs):
            raise self.erro
        return metodo


class TestTraducaoDeErrosParaHttp(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides[exigir_dono] = (
            lambda: SimpleNamespace(id=1, papel="usuario")
        )
        self.services_originais = (
            rotas_tarefas.controller.service,
            rotas_usuarios.controller.service,
            rotas_auth.controller.service,
        )
        self.cliente = TestClient(app, raise_server_exceptions=False)

    def tearDown(self):
        app.dependency_overrides.clear()
        (
            rotas_tarefas.controller.service,
            rotas_usuarios.controller.service,
            rotas_auth.controller.service,
        ) = self.services_originais

    def _falhar_com(self, erro):
        for modulo in (rotas_tarefas, rotas_usuarios, rotas_auth):
            modulo.controller.service = ServiceQueFalha(erro)

    def test_nao_encontrado_vira_404(self):
        self._falhar_com(NaoEncontrado("Tarefa não encontrada."))

        resposta = self.cliente.get("/usuarios/1/tarefas/99")

        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(resposta.json(), {"detail": "Tarefa não encontrada."})

    def test_dados_invalidos_vira_422(self):
        self._falhar_com(DadosInvalidos("O título não pode ficar vazio."))

        resposta = self.cliente.post(
            "/usuarios/1/tarefas",
            json={"titulo": " "}
        )

        self.assertEqual(resposta.status_code, 422)
        self.assertEqual(resposta.json()["detail"], "O título não pode ficar vazio.")

    def test_falha_ia_vira_503(self):
        self._falhar_com(FalhaIA("Não foi possível gerar os passos agora."))

        resposta = self.cliente.post("/usuarios/1/tarefas/1/passos/gerar")

        self.assertEqual(resposta.status_code, 503)

    def test_credenciais_invalidas_vira_401(self):
        self._falhar_com(CredenciaisInvalidas("Nome ou senha inválidos."))

        resposta = self.cliente.post(
            "/auth/login", json={"nome": "Ana", "senha": "errada"}
        )

        self.assertEqual(resposta.status_code, 401)
        self.assertEqual(resposta.json()["detail"], "Nome ou senha inválidos.")

    def test_erro_inesperado_vira_500_sem_detalhes_internos(self):
        self._falhar_com(ConnectionError("senha do banco: 1234"))

        resposta = self.cliente.get("/usuarios/1/tarefas")

        self.assertEqual(resposta.status_code, 500)
        self.assertEqual(
            resposta.json(), {"detail": "Não foi possível concluir a operação."}
        )


if __name__ == "__main__":
    unittest.main()
