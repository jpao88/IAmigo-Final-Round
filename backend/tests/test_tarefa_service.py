import unittest
from datetime import date
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


class TarefaRepositoryBandejaFake:
    """Guarda o que o service pediu ao repositório, sem MySQL."""

    def __init__(self):
        self.criadas = []
        self.bandeja_pedida = None

    def criar_varias(self, usuario_id, titulos):
        novas = [
            SimpleNamespace(id=len(self.criadas) + i, usuario_id=usuario_id, titulo=titulo)
            for i, titulo in enumerate(titulos, start=1)
        ]
        self.criadas.extend(novas)
        return novas

    def listar_bandeja(self, usuario_id, hoje):
        self.bandeja_pedida = (usuario_id, hoje)
        return []


class TestTarefaServiceCapturar(unittest.TestCase):
    """Épica 1 · Capturar (H1.1, H1.2, H1.3)."""

    def setUp(self):
        self.tarefas = TarefaRepositoryBandejaFake()
        self.service = TarefaService(
            tarefa_repository=self.tarefas,
            usuario_repository=UsuarioRepositoryFake([1]),
            passo_repository=PassoRepositoryFake()
        )

    def test_cada_linha_vira_uma_tarefa(self):
        criadas = self.service.criar_varias(1, ["Pagar a luz", "Ligar pro dentista"])

        self.assertEqual([t.titulo for t in criadas], ["Pagar a luz", "Ligar pro dentista"])
        self.assertTrue(all(t.usuario_id == 1 for t in criadas))

    def test_linhas_vazias_sao_ignoradas_e_espacos_removidos(self):
        criadas = self.service.criar_varias(1, ["", "  Comprar pão  ", "   ", "Estudar"])

        self.assertEqual([t.titulo for t in criadas], ["Comprar pão", "Estudar"])

    def test_so_linhas_vazias_e_recusado(self):
        with self.assertRaises(ValueError):
            self.service.criar_varias(1, ["", "   "])

        self.assertEqual(self.tarefas.criadas, [])

    def test_uma_linha_longa_demais_impede_todas(self):
        with self.assertRaises(ValueError):
            self.service.criar_varias(1, ["Curta", "x" * 201])

        self.assertEqual(self.tarefas.criadas, [])

    def test_mais_de_50_linhas_e_recusado(self):
        with self.assertRaises(ValueError):
            self.service.criar_varias(1, [f"Tarefa {i}" for i in range(51)])

        self.assertEqual(self.tarefas.criadas, [])

    def test_usuario_inexistente_e_recusado(self):
        with self.assertRaises(ValueError):
            self.service.criar_varias(99, ["Estudar"])

    def test_bandeja_usa_a_data_local_enviada(self):
        self.service.listar_bandeja(1, date(2026, 11, 12))

        self.assertEqual(self.tarefas.bandeja_pedida, (1, date(2026, 11, 12)))

    def test_bandeja_sem_data_usa_hoje_do_servidor(self):
        self.service.listar_bandeja(1)

        self.assertEqual(self.tarefas.bandeja_pedida, (1, date.today()))


if __name__ == "__main__":
    unittest.main()
