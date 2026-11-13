"""Limpeza da resposta da IA (H2.1), sem chamar o Gemini."""
import unittest

from core.ia_service import MAXIMO_PASSOS, MINUTOS_PADRAO, _normalizar


class TestNormalizarPassosDaIA(unittest.TestCase):
    def test_formato_de_saida(self):
        passos = _normalizar([{"texto": "Abrir el libro", "minutos": 5}])

        self.assertEqual(passos, [{"texto": "Abrir el libro", "minutos_estimados": 5}])

    def test_sem_minutos_ou_minutos_invalidos_viram_10(self):
        passos = _normalizar([
            {"texto": "A"},
            {"texto": "B", "minutos": "muito"},
            {"texto": "C", "minutos": 0},
            {"texto": "D", "minutos": 500},
        ])

        self.assertEqual([p["minutos_estimados"] for p in passos], [MINUTOS_PADRAO] * 4)

    def test_textos_vazios_saem_e_numeracao_e_removida(self):
        passos = _normalizar([
            {"texto": "  ", "minutos": 5},
            {"texto": "1. Abrir el libro", "minutos": 5},
            {"texto": "- Leer", "minutos": 5},
        ])

        self.assertEqual([p["texto"] for p in passos], ["Abrir el libro", "Leer"])

    def test_no_maximo_7_passos(self):
        passos = _normalizar([{"texto": f"Paso {i}", "minutos": 5} for i in range(12)])

        self.assertEqual(len(passos), MAXIMO_PASSOS)

    def test_texto_cortado_no_tamanho_da_coluna(self):
        passos = _normalizar([{"texto": "x" * 300, "minutos": 5}])

        self.assertEqual(len(passos[0]["texto"]), 255)



class TestPromptsPorIdioma(unittest.TestCase):
    def test_gerar_em_espanhol_e_em_portugues(self):
        from core.ia_service import montar_prompt_gerar

        self.assertIn('Tarea: "Lavar la ropa"', montar_prompt_gerar("Lavar la ropa", "es"))
        self.assertIn('Tarefa: "Lavar a roupa"', montar_prompt_gerar("Lavar a roupa", "pt"))
        self.assertIn("Divida esta tarefa", montar_prompt_gerar("x", "pt"))

    def test_dividir_leva_os_minutos_e_o_passo(self):
        from core.ia_service import montar_prompt_dividir

        prompt = montar_prompt_dividir("Trabalho final", "Escrever a introdução", 20, "pt")

        self.assertIn("20 minutos", prompt)
        self.assertIn('Passo travado: "Escrever a introdução"', prompt)

    def test_idioma_desconhecido_usa_espanhol(self):
        from core.ia_service import montar_prompt_gerar

        self.assertIn("Divide esta tarea", montar_prompt_gerar("x", "fr"))

    def test_o_service_passa_o_idioma_para_a_ia(self):
        from types import SimpleNamespace
        from services.tarefa_service import TarefaService

        pedidos = []

        class Tarefas:
            def buscar_por_id(self, tarefa_id):
                return SimpleNamespace(id=10, usuario_id=1, titulo="Lavar a roupa")

        class Usuarios:
            def buscar_por_id(self, usuario_id):
                return SimpleNamespace(id=1)

        class Passos:
            def listar_por_tarefa(self, tarefa_id):
                return []

            def criar_varios(self, tarefa_id, passos, gerado_por_ia):
                return passos

        service = TarefaService(
            tarefa_repository=Tarefas(), usuario_repository=Usuarios(), passo_repository=Passos(),
            gerador_de_passos=lambda titulo, idioma: pedidos.append(idioma) or [{"texto": "A", "minutos_estimados": 5}],
        )
        service.gerar_passos(1, 10, "pt")

        self.assertEqual(pedidos, ["pt"])


if __name__ == "__main__":
    unittest.main()
