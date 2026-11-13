"""Épica 4 · Hacer (modo foco): concluir passos e tarefas, e "Me atasqué". Sem MySQL nem Gemini."""
import unittest
from types import SimpleNamespace

from core.erros import FalhaIA
from services.tarefa_service import TarefaService


class UsuarioRepositoryFake:
    def buscar_por_id(self, usuario_id):
        return SimpleNamespace(id=usuario_id) if usuario_id in (1, 2) else None


class TarefaRepositoryFake:
    def __init__(self, tarefas):
        self.tarefas = {t.id: t for t in tarefas}

    def buscar_por_id(self, tarefa_id):
        return self.tarefas.get(tarefa_id)

    def concluir(self, tarefa_id):
        self.tarefas[tarefa_id].concluida = True
        return self.tarefas[tarefa_id]


class PassoRepositoryFake:
    """Passos em memória, com as mesmas regras do repositório real."""

    def __init__(self, passos):
        self.passos = passos

    def listar_por_tarefa(self, tarefa_id):
        return sorted((p for p in self.passos if p.tarefa_id == tarefa_id), key=lambda p: p.ordem)

    def buscar_por_id(self, passo_id):
        return next((p for p in self.passos if p.id == passo_id), None)

    def concluir(self, passo_id):
        passo = self.buscar_por_id(passo_id)
        passo.concluido = True
        return passo

    def dividir(self, passo_id, novos):
        original = self.buscar_por_id(passo_id)
        original.substituido = True

        for existente in self.passos:
            if existente.tarefa_id == original.tarefa_id and existente.ordem > original.ordem:
                existente.ordem += len(novos)

        criados = [
            passo(
                id=100 + i, tarefa_id=original.tarefa_id, ordem=original.ordem + i,
                texto=novo["texto"], minutos=novo["minutos_estimados"],
                gerado_por_ia=True, passo_origem_id=original.id,
            )
            for i, novo in enumerate(novos, start=1)
        ]
        self.passos.extend(criados)
        return criados


def passo(id, tarefa_id=10, ordem=1, texto="Passo", minutos=10, concluido=False,
          substituido=False, gerado_por_ia=False, passo_origem_id=None):
    return SimpleNamespace(
        id=id, tarefa_id=tarefa_id, ordem=ordem, texto=texto, minutos_estimados=minutos,
        concluido=concluido, substituido=substituido, gerado_por_ia=gerado_por_ia,
        passo_origem_id=passo_origem_id,
    )


class BaseFoco(unittest.TestCase):
    def montar(self, passos, divisor=None):
        self.tarefas = TarefaRepositoryFake([
            SimpleNamespace(id=10, usuario_id=1, titulo="Trabalho final", concluida=False),
            SimpleNamespace(id=20, usuario_id=1, titulo="Sem passos", concluida=False),
        ])
        self.passos = PassoRepositoryFake(passos)
        self.chamadas_divisor = []

        def divisor_falso(titulo, texto, minutos, idioma="es"):
            self.chamadas_divisor.append((titulo, texto, minutos))
            return [
                {"texto": "Abrir o arquivo", "minutos_estimados": 2},
                {"texto": "Escrever uma frase", "minutos_estimados": 8},
            ]

        self.service = TarefaService(
            tarefa_repository=self.tarefas,
            usuario_repository=UsuarioRepositoryFake(),
            passo_repository=self.passos,
            gerador_de_passos=lambda titulo, idioma="es": [],
            divisor_de_passo=divisor or divisor_falso,
        )

    def textos_visiveis(self):
        return [p.texto for p in self.passos.listar_por_tarefa(10) if not p.substituido]


class TestConcluir(BaseFoco):
    def test_concluir_passo_que_nao_e_o_ultimo(self):
        self.montar([passo(1, ordem=1), passo(2, ordem=2)])

        resultado = self.service.concluir_passo(1, 10, 1)

        self.assertTrue(resultado["passo"].concluido)
        self.assertFalse(resultado["tarefa_concluida"])
        self.assertFalse(self.tarefas.tarefas[10].concluida)

    def test_ultimo_passo_conclui_a_tarefa(self):
        self.montar([passo(1, ordem=1, concluido=True), passo(2, ordem=2)])

        resultado = self.service.concluir_passo(1, 10, 2)

        self.assertTrue(resultado["tarefa_concluida"])
        self.assertTrue(self.tarefas.tarefas[10].concluida)

    def test_passos_substituidos_nao_seguram_a_tarefa(self):
        self.montar([passo(1, ordem=1, substituido=True), passo(2, ordem=2)])

        self.assertTrue(self.service.concluir_passo(1, 10, 2)["tarefa_concluida"])

    def test_toque_duplo_em_hecho_nao_desmarca(self):
        self.montar([passo(1, ordem=1), passo(2, ordem=2)])

        self.service.concluir_passo(1, 10, 1)
        self.service.concluir_passo(1, 10, 1)

        self.assertTrue(self.passos.buscar_por_id(1).concluido)

    def test_passo_substituido_nao_se_conclui(self):
        self.montar([passo(1, substituido=True)])

        with self.assertRaises(ValueError):
            self.service.concluir_passo(1, 10, 1)

    def test_passo_de_outra_pessoa_e_recusado(self):
        self.montar([passo(1)])

        with self.assertRaises(ValueError):
            self.service.concluir_passo(2, 10, 1)

        self.assertFalse(self.passos.buscar_por_id(1).concluido)

    def test_tarefa_sem_passos_se_conclui_direto(self):
        self.montar([])

        self.assertTrue(self.service.concluir_tarefa(1, 20).concluida)

    def test_tarefa_com_passos_pendentes_nao_se_conclui_direto(self):
        self.montar([passo(1)])

        with self.assertRaises(ValueError):
            self.service.concluir_tarefa(1, 10)


class TestMeAtasque(BaseFoco):
    def test_divide_no_lugar_do_original(self):
        self.montar([
            passo(1, ordem=1, texto="Ler"),
            passo(2, ordem=2, texto="Escrever a introdução", minutos=20),
            passo(3, ordem=3, texto="Revisar"),
        ])

        novos = self.service.dividir_passo(1, 10, 2)

        self.assertEqual(self.chamadas_divisor, [("Trabalho final", "Escrever a introdução", 20)])
        self.assertEqual(
            self.textos_visiveis(),
            ["Ler", "Abrir o arquivo", "Escrever uma frase", "Revisar"],
        )
        self.assertTrue(self.passos.buscar_por_id(2).substituido)
        self.assertTrue(all(p.passo_origem_id == 2 and p.gerado_por_ia for p in novos))

    def test_passo_concluido_ou_ja_dividido_nao_se_divide(self):
        self.montar([passo(1, concluido=True), passo(2, ordem=2, substituido=True)])

        for passo_id in (1, 2):
            with self.subTest(passo_id=passo_id), self.assertRaises(ValueError):
                self.service.dividir_passo(1, 10, passo_id)

        self.assertEqual(self.chamadas_divisor, [])

    def test_falha_da_ia_deixa_o_passo_como_estava(self):
        def divisor_quebrado(titulo, texto, minutos, idioma="es"):
            raise FalhaIA("Não foi possível dividir o passo agora.")

        self.montar([passo(1, texto="Escrever")], divisor=divisor_quebrado)

        with self.assertRaises(FalhaIA):
            self.service.dividir_passo(1, 10, 1)

        self.assertFalse(self.passos.buscar_por_id(1).substituido)
        self.assertEqual(self.textos_visiveis(), ["Escrever"])


if __name__ == "__main__":
    unittest.main()
