from datetime import date, timedelta

from core.erros import DadosInvalidos, NaoEncontrado
from repositories.fechamento_repository import FechamentoRepository
from repositories.tarefa_repository import TarefaRepository
from repositories.usuario_repository import UsuarioRepository


class DiaService:
    """Épica 5 · Cerrar el día.

    O dia é o das tarefas planejadas para ele (data_planejada), não o relógio
    do servidor: assim o resumo vale para a data local da pessoa.
    O que ficou pendente usa as rotas de Hoje: "Hacerla mañana" planeja para
    outra data e "Guardarla sin fecha" tira do dia.
    """

    def __init__(self, tarefa_repository=None, usuario_repository=None, fechamento_repository=None):
        self.tarefa_repository = tarefa_repository or TarefaRepository()
        self.usuario_repository = usuario_repository or UsuarioRepository()
        self.fechamento_repository = fechamento_repository or FechamentoRepository()

    def _garantir_usuario(self, usuario_id):
        if self.usuario_repository.buscar_por_id(usuario_id) is None:
            raise NaoEncontrado("Usuário não encontrado.")

    def resumo(self, usuario_id, data):
        """H5.1 e H5.2: o que a pessoa conseguiu no dia e o que ficou para decidir."""
        self._garantir_usuario(usuario_id)

        tarefas = self.tarefa_repository.listar_do_dia(usuario_id, data)
        concluidas = [tarefa for tarefa in tarefas if tarefa.concluida]

        return {
            "data": data,
            "passos_concluidos": sum(
                1
                for tarefa in tarefas
                for passo in tarefa.passos
                if passo.concluido and not passo.substituido
            ),
            "tarefas_concluidas": len(concluidas),
            "concluidas": concluidas,
            "pendentes": [tarefa for tarefa in tarefas if not tarefa.concluida],
            "fechado": self.fechamento_repository.existe(usuario_id, data),
        }

    def fechar(self, usuario_id, data):
        """H5.3: registra o fechamento do dia. Fechar de novo não cria um segundo."""
        self._garantir_usuario(usuario_id)

        # Um dia de folga para os fusos horários; mais que isso ainda não chegou.
        if data > date.today() + timedelta(days=1):
            raise DadosInvalidos("Esse dia ainda não chegou.")

        if not self.fechamento_repository.existe(usuario_id, data):
            self.fechamento_repository.criar(usuario_id, data)

    def dia_pendente(self, usuario_id, hoje):
        """H5.4: o último dia com tarefas em Hoje, se ainda não foi fechado.

        Só olha o mais recente: dias mais antigos já passaram e não voltam a aparecer.
        """
        self._garantir_usuario(usuario_id)

        ultimo = self.tarefa_repository.ultima_data_planejada_antes(usuario_id, hoje)

        if ultimo is None or self.fechamento_repository.existe(usuario_id, ultimo):
            return None

        return ultimo
