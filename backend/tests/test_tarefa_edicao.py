"""Mudar o título de uma tarefa (ex.: reescrever em português). Sem MySQL."""
import unittest
from types import SimpleNamespace

from core.erros import DadosInvalidos, NaoEncontrado
from services.tarefa_service import TarefaService


class TarefaRepositoryFake:
    def __init__(self):
        self.tarefa = SimpleNamespace(id=10, usuario_id=1, titulo="Lavar la ropa")

    def buscar_por_id(self, tarefa_id):
        return self.tarefa if tarefa_id == 10 else None

    def renomear(self, tarefa_id, titulo):
        self.tarefa.titulo = titulo
        return self.tarefa


class UsuarioRepositoryFake:
    def buscar_por_id(self, usuario_id):
        return SimpleNamespace(id=usuario_id) if usuario_id in (1, 2) else None


class TestRenomearTarefa(unittest.TestCase):
    def setUp(self):
        self.tarefas = TarefaRepositoryFake()
        self.service = TarefaService(
            tarefa_repository=self.tarefas,
            usuario_repository=UsuarioRepositoryFake(),
            passo_repository=SimpleNamespace(),
            gerador_de_passos=lambda titulo, idioma="es": [],
        )

    def test_muda_o_titulo_sem_espacos_nas_pontas(self):
        tarefa = self.service.renomear_tarefa(1, 10, "  Lavar a roupa ")

        self.assertEqual(tarefa.titulo, "Lavar a roupa")

    def test_titulo_vazio_e_recusado_e_nada_muda(self):
        with self.assertRaises(DadosInvalidos):
            self.service.renomear_tarefa(1, 10, "   ")

        self.assertEqual(self.tarefas.tarefa.titulo, "Lavar la ropa")

    def test_titulo_longo_demais_e_recusado(self):
        with self.assertRaises(DadosInvalidos):
            self.service.renomear_tarefa(1, 10, "x" * 201)

    def test_tarefa_de_outra_pessoa_e_recusada(self):
        with self.assertRaises(NaoEncontrado):
            self.service.renomear_tarefa(2, 10, "Intruso")

        self.assertEqual(self.tarefas.tarefa.titulo, "Lavar la ropa")


if __name__ == "__main__":
    unittest.main()
