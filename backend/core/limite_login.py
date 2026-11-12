"""Limite de tentativas de login: impede adivinhar a senha de uma conta testando muitas.

Conta as falhas por e-mail numa janela de tempo. Depois de MAXIMO_FALHAS, o
login daquele e-mail fica recusado até a falha mais antiga sair da janela.
Entrar com sucesso zera a contagem.

Fica na memória do processo: basta para um servidor só (V1). Se a API
rodar em várias instâncias, cada uma conta as suas.
"""
import threading
import time
from collections import defaultdict, deque

from core.erros import TentativasDemais

MAXIMO_FALHAS = 5
JANELA_SEGUNDOS = 15 * 60


class LimiteDeTentativas:
    def __init__(self, maximo=MAXIMO_FALHAS, janela_segundos=JANELA_SEGUNDOS, relogio=time.monotonic):
        self.maximo = maximo
        self.janela = janela_segundos
        self.relogio = relogio
        self._falhas = defaultdict(deque)
        # As rotas síncronas do FastAPI rodam em várias threads.
        self._trava = threading.Lock()

    def _descartar_antigas(self, chave):
        limite = self.relogio() - self.janela
        falhas = self._falhas[chave]
        while falhas and falhas[0] <= limite:
            falhas.popleft()
        if not falhas:
            del self._falhas[chave]

    def verificar(self, chave):
        with self._trava:
            self._descartar_antigas(chave)
            if len(self._falhas.get(chave, ())) >= self.maximo:
                raise TentativasDemais("Muitas tentativas. Tente de novo em alguns minutos.")

    def registrar_falha(self, chave):
        with self._trava:
            self._falhas[chave].append(self.relogio())

    def limpar(self, chave):
        with self._trava:
            self._falhas.pop(chave, None)


# Uma instância para toda a API.
LIMITE_LOGIN = LimiteDeTentativas()
