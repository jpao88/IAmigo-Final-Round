"""Idiomas do front (frontend/js/i18n.js): espanhol e português têm as mesmas chaves,
e toda chave usada nas telas existe. Lê os arquivos do front como texto (sem navegador)."""
import re
import unittest
from pathlib import Path

FRONT = Path(__file__).resolve().parents[2] / "frontend" / "js"
CHAVE = re.compile(r'^\s+"([\w.]+)":', re.M)


def dicionario(nome):
    texto = (FRONT / "i18n.js").read_text(encoding="utf-8")
    inicio = texto.index(f"const {nome} = {{")
    fim = texto.index("\n};", inicio)
    return CHAVE.findall(texto[inicio:fim])


class TestTraducoes(unittest.TestCase):
    def test_espanhol_e_portugues_tem_as_mesmas_chaves(self):
        es, pt = dicionario("es"), dicionario("pt")

        self.assertEqual(len(es), len(set(es)), "Chave repetida no espanhol.")
        self.assertEqual(len(pt), len(set(pt)), "Chave repetida no português.")
        self.assertEqual(set(es) - set(pt), set(), "Falta em português.")
        self.assertEqual(set(pt) - set(es), set(), "Falta em espanhol.")

    def test_toda_chave_usada_nas_telas_existe(self):
        existentes = set(dicionario("es"))
        usadas = {}

        for arquivo in [*FRONT.glob("*.js"), *FRONT.glob("telas/*.js")]:
            if arquivo.name == "i18n.js":
                continue
            texto = arquivo.read_text(encoding="utf-8")
            for chave in re.findall(r'\bt\("([\w.]+)"', texto):
                usadas.setdefault(chave, arquivo.name)
            # Chaves guardadas em listas (ex.: as etapas da bienvenida).
            for chave in re.findall(r'"((?:bienvenida|foco|cerrar)\.[\w]+)"', texto):
                usadas.setdefault(chave, arquivo.name)

        faltando = {chave: arquivo for chave, arquivo in usadas.items() if chave not in existentes}
        self.assertEqual(faltando, {})


if __name__ == "__main__":
    unittest.main()
