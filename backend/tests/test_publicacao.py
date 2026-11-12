"""Fase 3 · Publicar: limite de tentativas de login e certificado do Aiven numa variável."""
import os
import unittest
from types import SimpleNamespace

from config.database import _gravar_certificado
from core.erros import CredenciaisInvalidas, TentativasDemais
from core.limite_login import LimiteDeTentativas
from core.seguranca import gerar_hash_senha
from services.usuario_service import UsuarioService


class Relogio:
    def __init__(self):
        self.agora = 1000.0

    def __call__(self):
        return self.agora


class UsuarioRepositoryFake:
    def __init__(self):
        self.usuario = SimpleNamespace(id=1, email="ana@exemplo.com",
                                       senha_hash=gerar_hash_senha("segredo1"))

    def buscar_por_email(self, email):
        return self.usuario if email == self.usuario.email else None


class TestLimiteDeLogin(unittest.TestCase):
    def setUp(self):
        self.relogio = Relogio()
        self.limite = LimiteDeTentativas(maximo=5, janela_segundos=900, relogio=self.relogio)
        self.service = UsuarioService(repository=UsuarioRepositoryFake(), limite_login=self.limite)

    def errar(self, vezes, email="ana@exemplo.com"):
        for _ in range(vezes):
            with self.assertRaises(CredenciaisInvalidas):
                self.service.autenticar(email, "errada")

    def test_depois_de_5_erros_nem_a_senha_certa_entra(self):
        self.errar(5)

        with self.assertRaises(TentativasDemais):
            self.service.autenticar("ana@exemplo.com", "segredo1")

    def test_conta_o_email_sem_diferenciar_maiusculas(self):
        self.errar(5, "  ANA@exemplo.com ")

        with self.assertRaises(TentativasDemais):
            self.service.autenticar("ana@exemplo.com", "segredo1")

    def test_libera_depois_da_janela(self):
        self.errar(5)
        self.relogio.agora += 901

        self.assertEqual(self.service.autenticar("ana@exemplo.com", "segredo1").id, 1)

    def test_entrar_com_sucesso_zera_a_contagem(self):
        self.errar(4)
        self.service.autenticar("ana@exemplo.com", "segredo1")
        self.errar(4)

        self.assertEqual(self.service.autenticar("ana@exemplo.com", "segredo1").id, 1)

    def test_email_sem_conta_tambem_e_limitado(self):
        # Mesmo comportamento: não revela quais e-mails existem.
        self.errar(5, "ninguem@exemplo.com")

        with self.assertRaises(TentativasDemais):
            self.service.autenticar("ninguem@exemplo.com", "qualquer")

    def test_um_email_bloqueado_nao_afeta_outro(self):
        self.errar(5, "ninguem@exemplo.com")

        self.assertEqual(self.service.autenticar("ana@exemplo.com", "segredo1").id, 1)


CORPO = "MIIB" + "A" * 120 + "xyz="


class TestCertificadoNaVariavel(unittest.TestCase):
    def ler(self, conteudo):
        caminho = _gravar_certificado(conteudo)
        self.addCleanup(os.remove, caminho)
        with open(caminho, encoding="ascii") as arquivo:
            return arquivo.read()

    def esperado(self):
        linhas = [CORPO[i:i + 64] for i in range(0, len(CORPO), 64)]
        return "-----BEGIN CERTIFICATE-----\n" + "\n".join(linhas) + "\n-----END CERTIFICATE-----\n"

    def test_remonta_o_certificado_mesmo_com_as_linhas_juntas(self):
        formatos = {
            "original": f"-----BEGIN CERTIFICATE-----\n{CORPO[:64]}\n{CORPO[64:]}\n-----END CERTIFICATE-----\n",
            "com espacos": f"-----BEGIN CERTIFICATE----- {CORPO[:64]} {CORPO[64:]} -----END CERTIFICATE-----",
            "com barra n": f"-----BEGIN CERTIFICATE-----\\n{CORPO}\\n-----END CERTIFICATE-----",
        }
        for nome, conteudo in formatos.items():
            with self.subTest(formato=nome):
                self.assertEqual(self.ler(conteudo), self.esperado())

    def test_sem_certificado_avisa(self):
        with self.assertRaises(RuntimeError):
            _gravar_certificado("qualquer coisa")


if __name__ == "__main__":
    unittest.main()
