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

    def _novo(self, tarefa_id, texto, minutos_estimados, gerado_por_ia):
        ordem = 1 + max(
            (p.ordem for p in self.passos if p.tarefa_id == tarefa_id),
            default=0
        )
        passo = SimpleNamespace(
            id=len(self.passos) + 1,
            tarefa_id=tarefa_id,
            texto=texto,
            minutos_estimados=minutos_estimados,
            gerado_por_ia=gerado_por_ia,
            concluido=False,
            substituido=False,
            ordem=ordem
        )
        self.passos.append(passo)
        return passo

    def criar(self, tarefa_id, texto, minutos_estimados=10):
        return self._novo(tarefa_id, texto, minutos_estimados, gerado_por_ia=False)

    def criar_varios(self, tarefa_id, passos, gerado_por_ia=False):
        return [
            self._novo(tarefa_id, p["texto"], p["minutos_estimados"], gerado_por_ia)
            for p in passos
        ]

    def listar_por_tarefa(self, tarefa_id):
        return sorted(
            (p for p in self.passos if p.tarefa_id == tarefa_id),
            key=lambda p: p.ordem
        )

    def buscar_por_id(self, passo_id):
        return next((p for p in self.passos if p.id == passo_id), None)

    def atualizar(self, passo_id, texto, minutos_estimados):
        passo = self.buscar_por_id(passo_id)
        passo.texto = texto
        passo.minutos_estimados = minutos_estimados
        return passo

    def reordenar(self, tarefa_id, ids_em_ordem):
        for ordem, passo_id in enumerate(ids_em_ordem, start=1):
            self.buscar_por_id(passo_id).ordem = ordem
        return [self.buscar_por_id(passo_id) for passo_id in ids_em_ordem]


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


class TestTarefaServiceDesmenuzar(unittest.TestCase):
    """Épica 2 · Desmenuzar (H2.1 a H2.4)."""

    PASSOS_DA_IA = [
        {"texto": "Abrir o documento", "minutos_estimados": 5},
        {"texto": "Escrever a introdução", "minutos_estimados": 20},
        {"texto": "Revisar", "minutos_estimados": 10},
    ]

    def setUp(self):
        self.passos = PassoRepositoryFake()
        self.chamadas_ia = []

        def ia_falsa(titulo):
            self.chamadas_ia.append(titulo)
            return [dict(p) for p in self.PASSOS_DA_IA]

        self.service = TarefaService(
            tarefa_repository=TarefaRepositoryFake([
                SimpleNamespace(id=10, usuario_id=1, titulo="Trabalho final"),
                SimpleNamespace(id=20, usuario_id=1, titulo="Outra tarefa"),
            ]),
            usuario_repository=UsuarioRepositoryFake([1, 2]),
            passo_repository=self.passos,
            gerador_de_passos=ia_falsa,
        )

    def test_ia_cria_passos_com_minutos_marcados_como_da_ia(self):
        criados = self.service.gerar_passos(1, 10)

        self.assertEqual(self.chamadas_ia, ["Trabalho final"])
        self.assertEqual([p.minutos_estimados for p in criados], [5, 20, 10])
        self.assertTrue(all(p.gerado_por_ia for p in criados))
        self.assertEqual([p.ordem for p in criados], [1, 2, 3])

    def test_ia_nao_roda_de_novo_se_a_tarefa_ja_tem_passos(self):
        self.service.gerar_passos(1, 10)

        with self.assertRaises(ValueError):
            self.service.gerar_passos(1, 10)

        self.assertEqual(len(self.chamadas_ia), 1)
        self.assertEqual(len(self.passos.passos), 3)

    def test_falha_da_ia_chega_como_falha_ia(self):
        from core.erros import FalhaIA

        def ia_quebrada(titulo):
            raise FalhaIA("Não foi possível gerar os passos agora.")

        self.service.gerador_de_passos = ia_quebrada

        with self.assertRaises(FalhaIA):
            self.service.gerar_passos(1, 10)

        # H2.4: mesmo assim a pessoa pode escrever os passos.
        passo = self.service.adicionar_passo(1, 10, "Abrir o documento")
        self.assertFalse(passo.gerado_por_ia)

    def test_passo_a_mao_sem_minutos_vale_10(self):
        passo = self.service.adicionar_passo(1, 10, "Abrir o documento")

        self.assertEqual(passo.minutos_estimados, 10)
        self.assertFalse(passo.gerado_por_ia)

    def test_minutos_fora_da_faixa_sao_recusados(self):
        for minutos in (0, -5, 121):
            with self.subTest(minutos=minutos), self.assertRaises(ValueError):
                self.service.adicionar_passo(1, 10, "Abrir", minutos)

        self.assertEqual(self.passos.passos, [])

    def test_passo_longo_demais_e_recusado(self):
        with self.assertRaises(ValueError):
            self.service.adicionar_passo(1, 10, "x" * 256)

    def test_editar_muda_texto_e_minutos(self):
        passo = self.service.gerar_passos(1, 10)[0]

        editado = self.service.editar_passo(1, 10, passo.id, "  Abrir o Word  ", 3)

        self.assertEqual((editado.texto, editado.minutos_estimados), ("Abrir o Word", 3))

    def test_editar_passo_de_outra_tarefa_e_recusado(self):
        passo = self.service.gerar_passos(1, 10)[0]

        with self.assertRaises(ValueError):
            self.service.editar_passo(1, 20, passo.id, "Outro texto", 5)

    def test_reordenar_aplica_a_ordem_recebida(self):
        a, b, c = self.service.gerar_passos(1, 10)

        self.service.reordenar_passos(1, 10, [c.id, a.id, b.id])

        ordem = [p.texto for p in self.passos.listar_por_tarefa(10)]
        self.assertEqual(ordem, ["Revisar", "Abrir o documento", "Escrever a introdução"])

    def test_reordenar_com_passos_faltando_ou_repetidos_e_recusado(self):
        a, b, c = self.service.gerar_passos(1, 10)

        for ids in ([a.id, b.id], [a.id, a.id, b.id], [a.id, b.id, c.id, 999]):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                self.service.reordenar_passos(1, 10, ids)

    def test_passos_substituidos_ficam_fora_da_ordem(self):
        a, b, c = self.service.gerar_passos(1, 10)
        b.substituido = True

        self.service.reordenar_passos(1, 10, [c.id, a.id])

        with self.assertRaises(ValueError):
            self.service.reordenar_passos(1, 10, [c.id, a.id, b.id])


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
