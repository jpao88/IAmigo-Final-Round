import unittest

from controllers.usuario_controller import UsuarioController


class UsuarioServiceFake:
    def __init__(self):
        self.usuarios = [
            {"nome": "Ana", "email": "ana@exemplo.com"},
            {"nome": "Leo", "email": "leo@exemplo.com"},
        ]

    def listar_usuarios(self):
        return self.usuarios


class TestUsuarioControllerListarPerfis(unittest.TestCase):
    def setUp(self):
        self.controller = UsuarioController(service=UsuarioServiceFake())

    def test_listar_perfis_retorna_lista_do_service(self):
        resultado = self.controller.listar_perfis()
        self.assertEqual(len(resultado), 2)


if __name__ == "__main__":
    unittest.main()