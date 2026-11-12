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


if __name__ == "__main__":
    unittest.main()
