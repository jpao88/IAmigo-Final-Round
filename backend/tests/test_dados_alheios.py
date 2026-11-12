"""Fase 3 · Ninguém vê nem muda dados de outra pessoa.

A rota já exige ser o dono do {usuario_id} (test_api_permissoes.py). Aqui se
testa a segunda barreira: dentro da própria rota, trocar o id da tarefa ou do
passo por um alheio é recusado, e nada é gravado. Sem MySQL.
"""
import unittest
from datetime import date
from types import SimpleNamespace

from core.erros import DadosInvalidos, NaoEncontrado
from services.dia_service import DiaService
from services.tarefa_service import TarefaService

HOJE = date(2026, 11, 12)

# Pessoa 1: tarefa 10 com o passo 100. Pessoa 2: tarefa 20 com o passo 200.
TAREFAS = {
    10: SimpleNamespace(id=10, usuario_id=1, titulo="Da pessoa 1", concluida=False,
                        data_planejada=HOJE, passos=[]),
    20: SimpleNamespace(id=20, usuario_id=2, titulo="Da pessoa 2", concluida=False,
                        data_planejada=HOJE, passos=[]),
}
PASSOS = {
    100: SimpleNamespace(id=100, tarefa_id=10, texto="Passo 1", minutos_estimados=10,
                         concluido=False, substituido=False),
    200: SimpleNamespace(id=200, tarefa_id=20, texto="Passo 2", minutos_estimados=10,
                         concluido=False, substituido=False),
}


class SoLeitura:
    """Qualquer método que não seja de leitura falha o teste: não pode haver gravação."""

    def __getattr__(self, nome):
        raise AssertionError(f"Gravou ou leu sem conferir o dono: {type(self).__name__}.{nome}")


class TarefaRepositoryFake(SoLeitura):
    def buscar_por_id(self, tarefa_id):
        return TAREFAS.get(tarefa_id)

    def listar_por_ids(self, usuario_id, ids):
        return [t for t in TAREFAS.values() if t.usuario_id == usuario_id and t.id in ids]

    def listar_do_dia(self, usuario_id, data):
        return [t for t in TAREFAS.values() if t.usuario_id == usuario_id and t.data_planejada == data]

    def ultima_data_planejada_antes(self, usuario_id, data):
        return None


class PassoRepositoryFake(SoLeitura):
    def buscar_por_id(self, passo_id):
        return PASSOS.get(passo_id)

    def listar_por_tarefa(self, tarefa_id):
        return [p for p in PASSOS.values() if p.tarefa_id == tarefa_id]


class UsuarioRepositoryFake:
    def buscar_por_id(self, usuario_id):
        return SimpleNamespace(id=usuario_id, limite_hoje=5) if usuario_id in (1, 2) else None


class FechamentoRepositoryFake(SoLeitura):
    def existe(self, usuario_id, data):
        return False


def ia_proibida(*args):
    raise AssertionError("Chamou a IA com dados de outra pessoa.")


class TestTarefasEPassosAlheios(unittest.TestCase):
    def setUp(self):
        self.service = TarefaService(
            tarefa_repository=TarefaRepositoryFake(),
            usuario_repository=UsuarioRepositoryFake(),
            passo_repository=PassoRepositoryFake(),
            gerador_de_passos=ia_proibida,
            divisor_de_passo=ia_proibida,
        )

    def test_pessoa_2_nao_toca_a_tarefa_da_pessoa_1(self):
        casos = {
            "buscar_tarefa": (2, 10),
            "alternar_status": (2, 10),
            "excluir_tarefa": (2, 10),
            "tirar_de_hoje": (2, 10),
            "concluir_tarefa": (2, 10),
            "listar_passos": (2, 10),
            "gerar_passos": (2, 10),
            "adicionar_passo": (2, 10, "Intruso"),
            "reordenar_passos": (2, 10, [100]),
            "editar_passo": (2, 10, 100, "Intruso", 5),
            "concluir_passo": (2, 10, 100),
            "dividir_passo": (2, 10, 100),
            "alternar_status_passo": (2, 10, 100),
            "excluir_passo": (2, 10, 100),
        }
        for metodo, argumentos in casos.items():
            with self.subTest(metodo=metodo), self.assertRaises(NaoEncontrado):
                getattr(self.service, metodo)(*argumentos)

    def test_passo_alheio_dentro_da_propria_tarefa(self):
        # A pessoa 2 usa a própria tarefa (20) com o passo da pessoa 1 (100).
        casos = {
            "editar_passo": (2, 20, 100, "Intruso", 5),
            "concluir_passo": (2, 20, 100),
            "dividir_passo": (2, 20, 100),
            "alternar_status_passo": (2, 20, 100),
            "excluir_passo": (2, 20, 100),
        }
        for metodo, argumentos in casos.items():
            with self.subTest(metodo=metodo), self.assertRaises(NaoEncontrado):
                getattr(self.service, metodo)(*argumentos)

    def test_hoje_nao_aceita_tarefas_alheias(self):
        with self.assertRaises(NaoEncontrado):
            self.service.planejar_para_hoje(2, [10], HOJE)

        with self.assertRaises(DadosInvalidos):
            self.service.reordenar_hoje(2, [10, 20], HOJE)

    def test_listas_so_trazem_o_proprio(self):
        self.assertEqual([t.id for t in self.service.listar_hoje(2, HOJE)], [20])


class TestDiasAlheios(unittest.TestCase):
    def test_resumo_so_conta_as_proprias_tarefas(self):
        service = DiaService(
            tarefa_repository=TarefaRepositoryFake(),
            usuario_repository=UsuarioRepositoryFake(),
            fechamento_repository=FechamentoRepositoryFake(),
        )

        resumo = service.resumo(2, HOJE)

        self.assertEqual([t.id for t in resumo["pendentes"]], [20])


if __name__ == "__main__":
    unittest.main()
