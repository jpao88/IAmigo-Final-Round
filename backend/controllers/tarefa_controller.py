from services.tarefa_service import TarefaService


class TarefaController:
    """Repassa os pedidos da API para o service.

    Os erros sobem como exceções de core/erros.py e viram
    respostas HTTP nos handlers registrados em api_app.py.
    """

    def __init__(self, service=None):
        self.service = service or TarefaService()

    def listar_tarefas(self, usuario_id):
        return self.service.listar_tarefas(usuario_id)

    def listar_bandeja(self, usuario_id, hoje=None):
        return self.service.listar_bandeja(usuario_id, hoje)

    def buscar_tarefa(self, usuario_id, tarefa_id):
        return self.service.buscar_tarefa(usuario_id, tarefa_id)

    def criar_tarefa(self, usuario_id, titulo):
        return self.service.criar_tarefa(usuario_id, titulo)

    def criar_varias(self, usuario_id, titulos):
        return self.service.criar_varias(usuario_id, titulos)

    def alternar_status(self, usuario_id, tarefa_id):
        return self.service.alternar_status(usuario_id, tarefa_id)

    def excluir_tarefa(self, usuario_id, tarefa_id):
        self.service.excluir_tarefa(usuario_id, tarefa_id)

    def listar_hoje(self, usuario_id, data=None):
        return self.service.listar_hoje(usuario_id, data)

    def planejar_para_hoje(self, usuario_id, ids, data=None):
        return self.service.planejar_para_hoje(usuario_id, ids, data)

    def reordenar_hoje(self, usuario_id, ids_em_ordem, data=None):
        self.service.reordenar_hoje(usuario_id, ids_em_ordem, data)

    def tirar_de_hoje(self, usuario_id, tarefa_id):
        return self.service.tirar_de_hoje(usuario_id, tarefa_id)

    def listar_passos(self, usuario_id, tarefa_id):
        return self.service.listar_passos(usuario_id, tarefa_id)

    def gerar_passos(self, usuario_id, tarefa_id):
        return self.service.gerar_passos(usuario_id, tarefa_id)

    def adicionar_passo(self, usuario_id, tarefa_id, texto, minutos_estimados=None):
        return self.service.adicionar_passo(usuario_id, tarefa_id, texto, minutos_estimados)

    def editar_passo(self, usuario_id, tarefa_id, passo_id, texto, minutos_estimados):
        return self.service.editar_passo(usuario_id, tarefa_id, passo_id, texto, minutos_estimados)

    def reordenar_passos(self, usuario_id, tarefa_id, ids_em_ordem):
        return self.service.reordenar_passos(usuario_id, tarefa_id, ids_em_ordem)

    def alternar_status_passo(self, usuario_id, tarefa_id, passo_id):
        return self.service.alternar_status_passo(usuario_id, tarefa_id, passo_id)

    def excluir_passo(self, usuario_id, tarefa_id, passo_id):
        self.service.excluir_passo(usuario_id, tarefa_id, passo_id)
