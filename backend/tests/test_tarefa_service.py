import unittest
from types import SimpleNamespace

from services.tarefa_service import TarefaService


class UsuarioRepositoryFake:
    def __init__(self, ids):
        self.ids = set(ids)

    def buscar_por_id(self, usuario_id):
        if usuario_id in self.ids:
            return SimpleNamespace(id=usuario_id)
        return None


class TarefaRepositoryFake:
    def __init__(self, tarefas):
        self.tarefas = {t.id: t for t in tarefas}

    def buscar_por_id(self, tarefa_id):
        return self.tarefas.get(tarefa_id)


class PassoRepositoryFake:
    """Repositório em memória: simula o banco sem precisar do MySQL."""

    def __init__(self):
        self.passos = []

    def criar(self, tarefa_id, texto):
        ordem = 1 + max(
            (p.ordem for p in self.passos if p.tarefa_id == tarefa_id),
            default=0
        )
        passo = SimpleNamespace(
            id=len(self.passos) + 1,
            tarefa_id=tarefa_id,
            texto=texto,
            concluido=False,
            ordem=ordem
        )
        self.passos.append(passo)
        return passo


class TestTarefaServiceAdicionarPasso(unittest.TestCase):
    def setUp(self):
        self.passos = PassoRepositoryFake()
        self.service = TarefaService(
            tarefa_repository=TarefaRepositoryFake([
                SimpleNamespace(id=10, usuario_id=1, titulo="Estudar")
            ]),
            usuario_repository=UsuarioRepositoryFake([1, 2]),
            passo_repository=self.passos
        )

    def test_adiciona_passo_na_proxima_ordem(self):
        self.service.adicionar_passo(1, 10, "Abrir o livro")
        passo = self.service.adicionar_passo(1, 10, "  Ler o capítulo  ")

        self.assertEqual(passo.texto, "Ler o capítulo")
        self.assertEqual(passo.ordem, 2)

    def test_texto_vazio_e_recusado(self):
        with self.assertRaises(ValueError):
            self.service.adicionar_passo(1, 10, "   ")

        self.assertEqual(self.passos.passos, [])

    def test_tarefa_de_outro_usuario_e_recusada(self):
        with self.assertRaises(ValueError) as contexto:
            self.service.adicionar_passo(2, 10, "Abrir o livro")

        self.assertEqual(str(contexto.exception), "Tarefa não encontrada.")
        self.assertEqual(self.passos.passos, [])


if __name__ == "__main__":
    unittest.main()
