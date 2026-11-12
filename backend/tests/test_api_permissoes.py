"""Matriz de permissões (H0.4 do backlog) e formatos da API."""
import unittest
from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

import api.rotas_tarefas as rotas_tarefas
import api.rotas_usuarios as rotas_usuarios
from api.dependencias import obter_usuario_autenticado
from api_app import app

DONO = SimpleNamespace(id=1, papel="usuario")
OUTRO = SimpleNamespace(id=2, papel="usuario")
ADMIN = SimpleNamespace(id=9, papel="admin")

USUARIO = SimpleNamespace(
    id=1, nome="Ana", email="ana@exemplo.com", papel="admin",
    senha_hash="pbkdf2_sha256$segredo", limite_hoje=3,
    onboarding_concluido=False, criado_em=datetime(2026, 1, 1)
)
TAREFA = SimpleNamespace(
    id=10, usuario_id=1, titulo="Lavar louça", data_planejada=None,
    ordem_dia=None, concluida=False, concluida_em=None,
    criado_em=datetime(2026, 1, 1)
)
PASSO = SimpleNamespace(
    id=100, tarefa_id=10, texto="Juntar a louça", ordem=1,
    minutos_estimados=10, gerado_por_ia=True, concluido=False,
    concluido_em=None, substituido=False, passo_origem_id=None
)


class ServiceFake:
    """Responde qualquer método com um usuário, uma tarefa, um passo ou listas deles."""

    def __getattr__(self, nome):
        def metodo(*args, **kwargs):
            if nome == "listar_usuarios":
                return [USUARIO]
            if nome == "listar_hoje":
                return [SimpleNamespace(**vars(TAREFA), minutos_restantes=25)]
            if nome in ("listar_tarefas", "listar_bandeja", "criar_varias", "planejar_para_hoje"):
                return [TAREFA]
            if nome == "concluir_passo":
                return {"passo": PASSO, "tarefa_concluida": False}
            if nome in ("listar_passos", "gerar_passos", "reordenar_passos", "dividir_passo"):
                return [PASSO]
            if "passo" in nome:
                return PASSO
            if "usuario" in nome or "limite" in nome:
                return USUARIO
            return TAREFA
        return metodo


class BaseApi(unittest.TestCase):
    def setUp(self):
        self.originais = (
            rotas_tarefas.controller.service,
            rotas_usuarios.controller.service,
        )
        rotas_tarefas.controller.service = ServiceFake()
        rotas_usuarios.controller.service = ServiceFake()
        self.cliente = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()
        (
            rotas_tarefas.controller.service,
            rotas_usuarios.controller.service,
        ) = self.originais

    def como(self, usuario):
        app.dependency_overrides[obter_usuario_autenticado] = lambda: usuario


class TestMatrizDePermissoes(BaseApi):
    CASOS = [
        # (método, rota, corpo, {perfil: status esperado})
        ("get", "/usuarios", None, {"DONO": 403, "OUTRO": 403, "ADMIN": 200}),
        ("get", "/usuarios/1", None, {"DONO": 200, "OUTRO": 403, "ADMIN": 200}),
        ("put", "/usuarios/1", {"nome": "Ana"},
         {"DONO": 200, "OUTRO": 403, "ADMIN": 200}),
        ("get", "/usuarios/1/tarefas", None, {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("patch", "/usuarios/1/tarefas/10", None, {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("get", "/usuarios/1/tarefas/10/passos", None,
         {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("get", "/usuarios/1/tarefas/bandeja?hoje=2026-11-12", None,
         {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("post", "/usuarios/1/tarefas/lote", {"titulos": ["Estudar"]},
         {"DONO": 201, "OUTRO": 403, "ADMIN": 403}),
        ("post", "/usuarios/1/tarefas/10/passos/gerar", None,
         {"DONO": 201, "OUTRO": 403, "ADMIN": 403}),
        ("post", "/usuarios/1/tarefas/10/passos", {"texto": "Abrir"},
         {"DONO": 201, "OUTRO": 403, "ADMIN": 403}),
        ("put", "/usuarios/1/tarefas/10/passos/100", {"texto": "Abrir", "minutos_estimados": 5},
         {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("put", "/usuarios/1/tarefas/10/passos/ordem", {"ids": [100]},
         {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("delete", "/usuarios/1/tarefas/10/passos/100", None,
         {"DONO": 204, "OUTRO": 403, "ADMIN": 403}),
        ("get", "/usuarios/1/tarefas/hoje?data=2026-11-12", None,
         {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("post", "/usuarios/1/tarefas/hoje", {"ids": [10], "data": "2026-11-12"},
         {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("put", "/usuarios/1/tarefas/hoje/ordem", {"ids": [10]},
         {"DONO": 204, "OUTRO": 403, "ADMIN": 403}),
        ("delete", "/usuarios/1/tarefas/10/hoje", None,
         {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("put", "/usuarios/1/limite-hoje", {"limite_hoje": 4},
         {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("post", "/usuarios/1/tarefas/10/passos/100/concluir", None,
         {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
        ("post", "/usuarios/1/tarefas/10/passos/100/dividir", None,
         {"DONO": 201, "OUTRO": 403, "ADMIN": 403}),
        ("post", "/usuarios/1/tarefas/10/concluir", None,
         {"DONO": 200, "OUTRO": 403, "ADMIN": 403}),
    ]

    def test_matriz(self):
        perfis = {"DONO": DONO, "OUTRO": OUTRO, "ADMIN": ADMIN}

        for metodo, rota, corpo, esperado in self.CASOS:
            for perfil, status_esperado in esperado.items():
                with self.subTest(rota=f"{metodo.upper()} {rota}", perfil=perfil):
                    self.como(perfis[perfil])
                    kwargs = {"json": corpo} if corpo is not None else {}
                    resposta = getattr(self.cliente, metodo)(rota, **kwargs)
                    self.assertEqual(resposta.status_code, status_esperado)

    def test_sem_token_recebe_401(self):
        for rota in ("/usuarios", "/usuarios/1", "/usuarios/1/tarefas"):
            with self.subTest(rota=rota):
                self.assertEqual(self.cliente.get(rota).status_code, 401)


class TestFormatos(BaseApi):
    def test_saida_de_usuario_nao_expoe_senha_nem_papel(self):
        self.como(ADMIN)

        dados = self.cliente.get("/usuarios/1").json()["dados"]

        self.assertEqual(
            set(dados),
            {"id", "nome", "email", "limite_hoje", "onboarding_concluido", "criado_em"}
        )

    def test_saida_de_tarefa_tem_os_campos_do_contrato(self):
        self.como(DONO)

        dados = self.cliente.get("/usuarios/1/tarefas").json()["dados"]

        self.assertEqual(dados[0]["titulo"], "Lavar louça")
        self.assertIn("concluida", dados[0])

    def test_titulo_maior_que_a_coluna_e_recusado(self):
        self.como(DONO)

        resposta = self.cliente.post(
            "/usuarios/1/tarefas",
            json={"titulo": "x" * 201}
        )

        self.assertEqual(resposta.status_code, 422)

    def test_bandeja_devolve_lista_de_tarefas(self):
        self.como(DONO)

        dados = self.cliente.get("/usuarios/1/tarefas/bandeja").json()["dados"]

        self.assertEqual(dados[0]["titulo"], "Lavar louça")

    def test_bandeja_com_data_invalida_e_recusada(self):
        self.como(DONO)

        resposta = self.cliente.get("/usuarios/1/tarefas/bandeja?hoje=amanha")

        self.assertEqual(resposta.status_code, 422)


if __name__ == "__main__":
    unittest.main()
