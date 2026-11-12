"""Épica 3 · Planear hoy (H3.1 a H3.5), sem MySQL."""
import unittest
from datetime import date
from types import SimpleNamespace

from core.erros import LimiteHojeAtingido
from models.passo import Passo
from models.tarefa import Tarefa
from services.tarefa_service import TarefaService
from services.usuario_service import UsuarioService

HOJE = date(2026, 11, 12)
ONTEM = date(2026, 11, 11)


class UsuarioRepositoryFake:
    def __init__(self, limite_hoje=3):
        self.usuario = SimpleNamespace(id=1, limite_hoje=limite_hoje)

    def buscar_por_id(self, usuario_id):
        return self.usuario if usuario_id == 1 else None

    def atualizar_limite_hoje(self, usuario_id, limite_hoje):
        self.usuario.limite_hoje = limite_hoje
        return self.usuario


class TarefaRepositoryHojeFake:
    """Tarefas em memória, com as mesmas regras do repositório real."""

    def __init__(self, tarefas):
        self.tarefas = {t.id: t for t in tarefas}

    def buscar_por_id(self, tarefa_id):
        return self.tarefas.get(tarefa_id)

    def listar_do_dia(self, usuario_id, data):
        do_dia = [t for t in self.tarefas.values() if t.usuario_id == usuario_id and t.data_planejada == data]
        return sorted(do_dia, key=lambda t: (t.ordem_dia, t.id))

    def listar_por_ids(self, usuario_id, ids):
        return [t for t in self.tarefas.values() if t.usuario_id == usuario_id and t.id in ids]

    def contar_pendentes_do_dia(self, usuario_id, data):
        return sum(1 for t in self.listar_do_dia(usuario_id, data) if not t.concluida)

    def planejar(self, usuario_id, ids_em_ordem, data):
        ultima = max((t.ordem_dia for t in self.listar_do_dia(usuario_id, data)), default=0)
        for ordem, tarefa_id in enumerate(ids_em_ordem, start=ultima + 1):
            self.tarefas[tarefa_id].data_planejada = data
            self.tarefas[tarefa_id].ordem_dia = ordem
        return [self.tarefas[i] for i in ids_em_ordem]

    def reordenar_dia(self, ids_em_ordem):
        for ordem, tarefa_id in enumerate(ids_em_ordem, start=1):
            self.tarefas[tarefa_id].ordem_dia = ordem

    def tirar_do_dia(self, tarefa_id):
        self.tarefas[tarefa_id].data_planejada = None
        self.tarefas[tarefa_id].ordem_dia = None
        return self.tarefas[tarefa_id]


def tarefa(id, usuario_id=1, data=None, ordem=None, concluida=False):
    return SimpleNamespace(
        id=id, usuario_id=usuario_id, titulo=f"Tarefa {id}",
        data_planejada=data, ordem_dia=ordem, concluida=concluida,
    )


class BaseHoje(unittest.TestCase):
    def montar(self, tarefas, limite_hoje=3):
        self.tarefas = TarefaRepositoryHojeFake(tarefas)
        self.service = TarefaService(
            tarefa_repository=self.tarefas,
            usuario_repository=UsuarioRepositoryFake(limite_hoje),
            passo_repository=object(),
            gerador_de_passos=lambda titulo: [],
        )

    def ordem_de_hoje(self):
        return [t.id for t in self.tarefas.listar_do_dia(1, HOJE) if not t.concluida]


class TestPlanejarHoje(BaseHoje):
    def test_mais_hoy_poe_a_tarefa_no_fim_do_dia(self):
        self.montar([tarefa(1, data=HOJE, ordem=1), tarefa(2)])

        self.service.planejar_para_hoje(1, [2], HOJE)

        self.assertEqual(self.ordem_de_hoje(), [1, 2])
        self.assertEqual(self.tarefas.tarefas[2].ordem_dia, 2)

    def test_varias_de_uma_vez_na_ordem_escolhida(self):
        self.montar([tarefa(1), tarefa(2), tarefa(3)])

        self.service.planejar_para_hoje(1, [3, 1], HOJE)

        self.assertEqual(self.ordem_de_hoje(), [3, 1])

    def test_limite_atingido_nao_agrega_nenhuma(self):
        self.montar([tarefa(1, data=HOJE, ordem=1), tarefa(2), tarefa(3), tarefa(4)])

        with self.assertRaises(LimiteHojeAtingido):
            self.service.planejar_para_hoje(1, [2, 3, 4], HOJE)

        self.assertEqual(self.ordem_de_hoje(), [1])

    def test_concluidas_de_hoje_nao_contam_para_o_limite(self):
        self.montar([
            tarefa(1, data=HOJE, ordem=1, concluida=True),
            tarefa(2, data=HOJE, ordem=2, concluida=True),
            tarefa(3, data=HOJE, ordem=3, concluida=True),
            tarefa(4),
        ])

        self.service.planejar_para_hoje(1, [4], HOJE)

        self.assertEqual(self.ordem_de_hoje(), [4])

    def test_tarefa_de_ontem_pode_voltar_para_hoje(self):
        self.montar([tarefa(1, data=ONTEM, ordem=1)])

        self.service.planejar_para_hoje(1, [1], HOJE)

        self.assertEqual(self.tarefas.tarefas[1].data_planejada, HOJE)

    def test_tarefa_ja_em_hoje_ou_concluida_e_recusada(self):
        self.montar([tarefa(1, data=HOJE, ordem=1), tarefa(2, concluida=True)])

        for ids in ([1], [2]):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                self.service.planejar_para_hoje(1, ids, HOJE)

    def test_tarefa_de_outra_pessoa_e_recusada(self):
        self.montar([tarefa(1, usuario_id=2)])

        with self.assertRaises(ValueError):
            self.service.planejar_para_hoje(1, [1], HOJE)

        self.assertIsNone(self.tarefas.tarefas[1].data_planejada)

    def test_lista_vazia_ou_repetida_e_recusada(self):
        self.montar([tarefa(1)])

        for ids in ([], [1, 1]):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                self.service.planejar_para_hoje(1, ids, HOJE)


class TestOrdenarETirarDeHoje(BaseHoje):
    def setUp(self):
        self.montar([
            tarefa(1, data=HOJE, ordem=1),
            tarefa(2, data=HOJE, ordem=2),
            tarefa(3, data=HOJE, ordem=3),
            tarefa(4, data=HOJE, ordem=4, concluida=True),
        ])

    def test_reordenar_a_primeira_vira_ahora(self):
        self.service.reordenar_hoje(1, [3, 1, 2], HOJE)

        self.assertEqual(self.ordem_de_hoje(), [3, 1, 2])

    def test_reordenar_precisa_de_todas_as_pendentes(self):
        for ids in ([3, 1], [3, 1, 2, 4], [1, 1, 2, 3]):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                self.service.reordenar_hoje(1, ids, HOJE)

    def test_tirar_de_hoje_volta_para_a_bandeja(self):
        self.service.tirar_de_hoje(1, 2)

        self.assertIsNone(self.tarefas.tarefas[2].data_planejada)
        self.assertEqual(self.ordem_de_hoje(), [1, 3])


class TestLimiteHoje(unittest.TestCase):
    def setUp(self):
        self.usuarios = UsuarioRepositoryFake()
        self.service = UsuarioService(repository=self.usuarios)

    def test_aceita_de_1_a_5(self):
        for limite in (1, 5):
            self.assertEqual(self.service.alterar_limite_hoje(1, limite).limite_hoje, limite)

    def test_recusa_fora_da_faixa(self):
        for limite in (0, 6, -1):
            with self.subTest(limite=limite), self.assertRaises(ValueError):
                self.service.alterar_limite_hoje(1, limite)

        self.assertEqual(self.usuarios.usuario.limite_hoje, 3)


class TestMinutosRestantes(unittest.TestCase):
    """O tempo do dia (H3.3) sai dos passos que ainda faltam."""

    def passo(self, minutos, concluido=False, substituido=False):
        return Passo(minutos_estimados=minutos, concluido=concluido, substituido=substituido)

    def test_soma_so_os_passos_pendentes_e_visiveis(self):
        t = Tarefa(concluida=False)
        t.passos = [self.passo(10), self.passo(5, concluido=True), self.passo(20, substituido=True), self.passo(15)]

        self.assertEqual(t.minutos_restantes, 25)

    def test_sem_passos_vale_10(self):
        t = Tarefa(concluida=False)
        t.passos = []

        self.assertEqual(t.minutos_restantes, 10)

    def test_concluida_sem_passos_vale_0(self):
        t = Tarefa(concluida=True)
        t.passos = []

        self.assertEqual(t.minutos_restantes, 0)


if __name__ == "__main__":
    unittest.main()
