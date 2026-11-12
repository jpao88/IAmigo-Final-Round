"""Épica 5 · Cerrar el día e H6.3 (guia uma vez só). Sem MySQL."""
import unittest
from datetime import date, timedelta
from types import SimpleNamespace

from core.erros import DadosInvalidos
from services.dia_service import DiaService
from services.usuario_service import UsuarioService

HOJE = date(2026, 11, 12)
ONTEM = date(2026, 11, 11)


class UsuarioRepositoryFake:
    def __init__(self):
        self.usuario = SimpleNamespace(id=1, onboarding_concluido=False)
        self.gravacoes = 0

    def buscar_por_id(self, usuario_id):
        return self.usuario if usuario_id == 1 else None

    def concluir_onboarding(self, usuario_id):
        self.gravacoes += 1
        self.usuario.onboarding_concluido = True
        return self.usuario


class TarefaRepositoryFake:
    def __init__(self, tarefas):
        self.tarefas = tarefas

    def listar_do_dia(self, usuario_id, data):
        return [t for t in self.tarefas if t.usuario_id == usuario_id and t.data_planejada == data]

    def ultima_data_planejada_antes(self, usuario_id, data):
        datas = [
            t.data_planejada for t in self.tarefas
            if t.usuario_id == usuario_id and t.data_planejada and t.data_planejada < data
        ]
        return max(datas, default=None)


class FechamentoRepositoryFake:
    def __init__(self, fechados=()):
        self.fechados = list(fechados)

    def existe(self, usuario_id, data):
        return (usuario_id, data) in self.fechados

    def criar(self, usuario_id, data):
        self.fechados.append((usuario_id, data))


def passo(concluido=False, substituido=False):
    return SimpleNamespace(concluido=concluido, substituido=substituido)


def tarefa(id, data=HOJE, concluida=False, passos=(), usuario_id=1):
    return SimpleNamespace(
        id=id, usuario_id=usuario_id, data_planejada=data, concluida=concluida, passos=list(passos)
    )


class BaseDia(unittest.TestCase):
    def montar(self, tarefas, fechados=()):
        self.fechamentos = FechamentoRepositoryFake(fechados)
        self.service = DiaService(
            tarefa_repository=TarefaRepositoryFake(tarefas),
            usuario_repository=UsuarioRepositoryFake(),
            fechamento_repository=self.fechamentos,
        )


class TestResumo(BaseDia):
    def test_conta_passos_e_tarefas_do_dia(self):
        self.montar([
            tarefa(1, concluida=True, passos=[passo(True), passo(True), passo(substituido=True)]),
            tarefa(2, passos=[passo(True), passo()]),
            tarefa(3, concluida=True),  # sem passos: conta só como tarefa
            tarefa(4, data=ONTEM, concluida=True, passos=[passo(True)]),  # outro dia
        ])

        resumo = self.service.resumo(1, HOJE)

        self.assertEqual(resumo["passos_concluidos"], 3)
        self.assertEqual(resumo["tarefas_concluidas"], 2)
        self.assertEqual([t.id for t in resumo["concluidas"]], [1, 3])
        self.assertEqual([t.id for t in resumo["pendentes"]], [2])
        self.assertFalse(resumo["fechado"])

    def test_dia_sem_nada_feito_nao_quebra(self):
        self.montar([tarefa(1)])

        resumo = self.service.resumo(1, HOJE)

        self.assertEqual((resumo["passos_concluidos"], resumo["tarefas_concluidas"]), (0, 0))


class TestFechar(BaseDia):
    def test_fechar_duas_vezes_registra_um_so(self):
        self.montar([tarefa(1)])

        self.service.fechar(1, HOJE)
        self.service.fechar(1, HOJE)

        self.assertEqual(self.fechamentos.fechados, [(1, HOJE)])
        self.assertTrue(self.service.resumo(1, HOJE)["fechado"])

    def test_nao_fecha_um_dia_que_nao_chegou(self):
        self.montar([])

        with self.assertRaises(DadosInvalidos):
            self.service.fechar(1, date.today() + timedelta(days=5))


class TestDiaPendente(BaseDia):
    def test_ontem_sem_fechar_aparece(self):
        self.montar([tarefa(1, data=ONTEM), tarefa(2)])

        self.assertEqual(self.service.dia_pendente(1, HOJE), ONTEM)

    def test_ontem_fechado_nao_aparece(self):
        self.montar([tarefa(1, data=ONTEM)], fechados=[(1, ONTEM)])

        self.assertIsNone(self.service.dia_pendente(1, HOJE))

    def test_so_o_dia_mais_recente_conta(self):
        # O último dia com plano foi fechado; um mais antigo sem fechar não volta.
        antes = date(2026, 11, 5)
        self.montar([tarefa(1, data=antes), tarefa(2, data=ONTEM)], fechados=[(1, ONTEM)])

        self.assertIsNone(self.service.dia_pendente(1, HOJE))

    def test_sem_dias_planejados(self):
        self.montar([tarefa(1, data=None), tarefa(2)])

        self.assertIsNone(self.service.dia_pendente(1, HOJE))

    def test_dias_de_outra_pessoa_nao_contam(self):
        self.montar([tarefa(1, data=ONTEM, usuario_id=2)])

        self.assertIsNone(self.service.dia_pendente(1, HOJE))


class TestOnboarding(unittest.TestCase):
    def test_conclui_uma_vez(self):
        repositorio = UsuarioRepositoryFake()
        service = UsuarioService(repository=repositorio)

        self.assertTrue(service.concluir_onboarding(1).onboarding_concluido)
        service.concluir_onboarding(1)

        self.assertEqual(repositorio.gravacoes, 1)


if __name__ == "__main__":
    unittest.main()
