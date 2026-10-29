"""Erros de domínio do sistema.

Os services lançam estes erros e cada camada decide como mostrá-los:
a API os transforma em status HTTP (api_app.py).

Herdam de ValueError/RuntimeError para que os testes possam capturá-los
com assertRaises(ValueError).
"""


class NaoEncontrado(ValueError):
    """O registro pedido não existe ou não pertence ao usuário."""


class DadosInvalidos(ValueError):
    """Os dados recebidos não respeitam uma regra de negócio."""


class CredenciaisInvalidas(ValueError):
    """E-mail ou senha não conferem."""


class FalhaIA(RuntimeError):
    """O serviço de IA não está configurado ou não respondeu."""
