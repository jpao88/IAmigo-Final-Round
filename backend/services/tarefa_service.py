from datetime import date

from repositories.tarefa_repository import TarefaRepository
from repositories.usuario_repository import UsuarioRepository
from repositories.passo_repository import PassoRepository
from core.erros import DadosInvalidos, NaoEncontrado
from core.ia_service import gerar_passos_tarefa

# Mesmo tamanho da coluna tarefas.titulo.
TAMANHO_MAXIMO_TITULO = 200
# Limite de linhas por envio, para um texto colado sem querer não lotar a Bandeja.
MAXIMO_TAREFAS_POR_VEZ = 50


class TarefaService:
    def __init__(self, tarefa_repository=None, usuario_repository=None, passo_repository=None):
        self.tarefa_repository = tarefa_repository or TarefaRepository()
        self.usuario_repository = usuario_repository or UsuarioRepository()
        self.passo_repository = passo_repository or PassoRepository()

    def _garantir_usuario(self, usuario_id):
        if self.usuario_repository.buscar_por_id(usuario_id) is None:
            raise NaoEncontrado("Usuário não encontrado.")

    def _obter_tarefa_do_usuario(self, usuario_id, tarefa_id):
        self._garantir_usuario(usuario_id)

        tarefa = self.tarefa_repository.buscar_por_id(tarefa_id)

        if tarefa is None or tarefa.usuario_id != usuario_id:
            raise NaoEncontrado("Tarefa não encontrada.")

        return tarefa

    def _obter_passo_da_tarefa(self, usuario_id, tarefa_id, passo_id):
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        passo = self.passo_repository.buscar_por_id(passo_id)

        if passo is None or passo.tarefa_id != tarefa_id:
            raise NaoEncontrado("Passo não encontrado.")

        return passo

    def _validar_titulo(self, titulo):
        titulo = titulo.strip()

        if not titulo:
            raise DadosInvalidos("O título não pode ficar vazio.")

        return titulo

    def listar_tarefas(self, usuario_id):
        self._garantir_usuario(usuario_id)

        return self.tarefa_repository.listar_por_usuario(usuario_id)

    def listar_bandeja(self, usuario_id, hoje=None):
        """H1.3: tarefas sem data e as de dias passados que não foram concluídas.

        `hoje` é a data local da pessoa, enviada pelo front: o servidor
        pode estar em outro fuso horário.
        """
        self._garantir_usuario(usuario_id)

        return self.tarefa_repository.listar_bandeja(usuario_id, hoje or date.today())

    def buscar_tarefa(self, usuario_id, tarefa_id):
        return self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

    def criar_tarefa(self, usuario_id, titulo):
        self._garantir_usuario(usuario_id)

        titulo = self._validar_titulo(titulo)

        return self.tarefa_repository.criar(usuario_id, titulo)

    def criar_varias(self, usuario_id, titulos):
        """H1.1 e H1.2: cada linha com texto vira uma tarefa na Bandeja; as vazias são ignoradas.

        Valida tudo antes de gravar: ou entram todas, ou nenhuma.
        """
        self._garantir_usuario(usuario_id)

        titulos = [titulo.strip() for titulo in titulos if titulo.strip()]

        if not titulos:
            raise DadosInvalidos("Escreva pelo menos uma tarefa.")

        if len(titulos) > MAXIMO_TAREFAS_POR_VEZ:
            raise DadosInvalidos(f"Envie no máximo {MAXIMO_TAREFAS_POR_VEZ} tarefas por vez.")

        if any(len(titulo) > TAMANHO_MAXIMO_TITULO for titulo in titulos):
            raise DadosInvalidos(f"Cada tarefa pode ter no máximo {TAMANHO_MAXIMO_TITULO} caracteres.")

        return self.tarefa_repository.criar_varias(usuario_id, titulos)

    def alternar_status(self, usuario_id, tarefa_id):
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        return self.tarefa_repository.alternar_concluida(tarefa_id)

    def excluir_tarefa(self, usuario_id, tarefa_id):
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        self.tarefa_repository.excluir(tarefa_id)

    def listar_passos(self, usuario_id, tarefa_id):
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        return self.passo_repository.listar_por_tarefa(tarefa_id)

    def gerar_passos(self, usuario_id, tarefa_id):
        tarefa = self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        textos = gerar_passos_tarefa(tarefa.titulo)

        return self.passo_repository.criar_varios(tarefa_id, textos, gerado_por_ia=True)

    def adicionar_passo(self, usuario_id, tarefa_id, texto):
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        texto = texto.strip()

        if not texto:
            raise DadosInvalidos("O texto do passo não pode ficar vazio.")

        return self.passo_repository.criar(tarefa_id, texto)

    def alternar_status_passo(self, usuario_id, tarefa_id, passo_id):
        self._obter_passo_da_tarefa(usuario_id, tarefa_id, passo_id)

        return self.passo_repository.alternar_concluido(passo_id)

    def excluir_passo(self, usuario_id, tarefa_id, passo_id):
        self._obter_passo_da_tarefa(usuario_id, tarefa_id, passo_id)

        self.passo_repository.excluir(passo_id)
