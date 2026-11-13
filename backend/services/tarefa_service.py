from datetime import date

from repositories.tarefa_repository import TarefaRepository
from repositories.usuario_repository import UsuarioRepository
from repositories.passo_repository import PassoRepository
from core.erros import DadosInvalidos, LimiteHojeAtingido, NaoEncontrado
from core.ia_service import dividir_passo, gerar_passos_tarefa

# Mesmo tamanho da coluna tarefas.titulo.
TAMANHO_MAXIMO_TITULO = 200
# Limite de linhas por envio, para um texto colado sem querer não lotar a Bandeja.
MAXIMO_TAREFAS_POR_VEZ = 50
# Passos: mesmo tamanho da coluna passos.texto; sem minutos, vale 10 (recorrido).
TAMANHO_MAXIMO_PASSO = 255
MINUTOS_PADRAO = 10
MINUTOS_MAXIMO = 120


class TarefaService:
    def __init__(
        self,
        tarefa_repository=None,
        usuario_repository=None,
        passo_repository=None,
        gerador_de_passos=None,
        divisor_de_passo=None,
    ):
        self.tarefa_repository = tarefa_repository or TarefaRepository()
        self.usuario_repository = usuario_repository or UsuarioRepository()
        self.passo_repository = passo_repository or PassoRepository()
        # Nos testes, troca-se a IA por uma função falsa.
        self.gerador_de_passos = gerador_de_passos or gerar_passos_tarefa
        self.divisor_de_passo = divisor_de_passo or dividir_passo

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

    # ---- Hoje (Épica 3 · Planear hoy) ----
    # `data` é a data local da pessoa, enviada pelo front (como na Bandeja).

    def listar_hoje(self, usuario_id, data=None):
        """H3.3: as tarefas do dia, na ordem; a primeira pendente é "Ahora"."""
        self._garantir_usuario(usuario_id)

        return self.tarefa_repository.listar_do_dia(usuario_id, data or date.today())

    def planejar_para_hoje(self, usuario_id, ids, data=None):
        """H3.1 e H3.2: põe uma ou várias tarefas da Bandeja em Hoje, no fim.

        Só contam para o limite as tarefas de hoje ainda não concluídas:
        terminar rápido nunca impede de planejar mais. Entram todas ou nenhuma.
        """
        data = data or date.today()
        usuario = self.usuario_repository.buscar_por_id(usuario_id)

        if usuario is None:
            raise NaoEncontrado("Usuário não encontrado.")

        if not ids or len(ids) != len(set(ids)):
            raise DadosInvalidos("Escolha as tarefas, uma vez cada.")

        tarefas = self.tarefa_repository.listar_por_ids(usuario_id, ids)

        if len(tarefas) != len(ids):
            raise NaoEncontrado("Tarefa não encontrada.")

        if any(tarefa.concluida or tarefa.data_planejada == data for tarefa in tarefas):
            raise DadosInvalidos("Essa tarefa já está em Hoje ou foi concluída.")

        pendentes = self.tarefa_repository.contar_pendentes_do_dia(usuario_id, data)

        if pendentes + len(ids) > usuario.limite_hoje:
            raise LimiteHojeAtingido("Hoje já está cheio.")

        return self.tarefa_repository.planejar(usuario_id, ids, data)

    def reordenar_hoje(self, usuario_id, ids_em_ordem, data=None):
        """H3.4: recebe as tarefas pendentes do dia na ordem nova; a primeira vira "Ahora"."""
        self._garantir_usuario(usuario_id)
        data = data or date.today()

        ids_pendentes = {
            tarefa.id
            for tarefa in self.tarefa_repository.listar_do_dia(usuario_id, data)
            if not tarefa.concluida
        }

        if len(ids_em_ordem) != len(set(ids_em_ordem)) or set(ids_em_ordem) != ids_pendentes:
            raise DadosInvalidos("A nova ordem precisa ter todas as tarefas de hoje, uma vez cada.")

        self.tarefa_repository.reordenar_dia(ids_em_ordem)

    def tirar_de_hoje(self, usuario_id, tarefa_id):
        """Devolve a tarefa à Bandeja, sem data (desfaz um "+ Hoy")."""
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        return self.tarefa_repository.tirar_do_dia(tarefa_id)

    def listar_passos(self, usuario_id, tarefa_id):
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        return self.passo_repository.listar_por_tarefa(tarefa_id)

    def _validar_passo(self, texto, minutos_estimados):
        texto = (texto or "").strip()

        if not texto:
            raise DadosInvalidos("O texto do passo não pode ficar vazio.")

        if len(texto) > TAMANHO_MAXIMO_PASSO:
            raise DadosInvalidos(f"O passo pode ter no máximo {TAMANHO_MAXIMO_PASSO} caracteres.")

        if minutos_estimados is None:
            minutos_estimados = MINUTOS_PADRAO

        if not 1 <= minutos_estimados <= MINUTOS_MAXIMO:
            raise DadosInvalidos(f"Os minutos precisam estar entre 1 e {MINUTOS_MAXIMO}.")

        return texto, minutos_estimados

    def _passos_ativos(self, tarefa_id):
        """Os que aparecem para a pessoa: os substituídos por "Me atasqué" ficam de fora."""
        return [
            passo for passo in self.passo_repository.listar_por_tarefa(tarefa_id)
            if not passo.substituido
        ]

    def gerar_passos(self, usuario_id, tarefa_id, idioma="es"):
        """H2.1: a IA sugere os passos. Só para tarefas ainda sem passos,
        para um toque duplo no botão não duplicar a lista."""
        tarefa = self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        if self._passos_ativos(tarefa_id):
            raise DadosInvalidos("A tarefa já tem passos.")

        passos = self.gerador_de_passos(tarefa.titulo, idioma)

        return self.passo_repository.criar_varios(tarefa_id, passos, gerado_por_ia=True)

    def adicionar_passo(self, usuario_id, tarefa_id, texto, minutos_estimados=None):
        """H2.2 e H2.3: passo escrito pela pessoa, no fim da lista."""
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        texto, minutos_estimados = self._validar_passo(texto, minutos_estimados)

        return self.passo_repository.criar(tarefa_id, texto, minutos_estimados)

    def editar_passo(self, usuario_id, tarefa_id, passo_id, texto, minutos_estimados):
        """H2.2: muda o texto e os minutos de um passo (da IA ou não)."""
        self._obter_passo_da_tarefa(usuario_id, tarefa_id, passo_id)

        texto, minutos_estimados = self._validar_passo(texto, minutos_estimados)

        return self.passo_repository.atualizar(passo_id, texto, minutos_estimados)

    def reordenar_passos(self, usuario_id, tarefa_id, ids_em_ordem):
        """H2.2: recebe todos os passos visíveis da tarefa, na ordem nova."""
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        ids_ativos = {passo.id for passo in self._passos_ativos(tarefa_id)}

        if len(ids_em_ordem) != len(set(ids_em_ordem)) or set(ids_em_ordem) != ids_ativos:
            raise DadosInvalidos("A nova ordem precisa ter todos os passos da tarefa, uma vez cada.")

        return self.passo_repository.reordenar(tarefa_id, ids_em_ordem)

    # ---- Modo foco (Épica 4 · Hacer) ----

    def concluir_passo(self, usuario_id, tarefa_id, passo_id):
        """H4.2: marca o passo; se era o último pendente, a tarefa fica concluída.

        Devolve {"passo": ..., "tarefa_concluida": bool} para o front saber
        se celebra só o passo ou a tarefa inteira.
        """
        passo = self._obter_passo_da_tarefa(usuario_id, tarefa_id, passo_id)

        if passo.substituido:
            raise DadosInvalidos("Esse passo foi dividido.")

        passo = self.passo_repository.concluir(passo_id)

        faltam = [p for p in self._passos_ativos(tarefa_id) if not p.concluido]
        if not faltam:
            self.tarefa_repository.concluir(tarefa_id)

        return {"passo": passo, "tarefa_concluida": not faltam}

    def concluir_tarefa(self, usuario_id, tarefa_id):
        """Tarefa sem passos: no modo foco é um passo só, e "Hecho" a conclui."""
        self._obter_tarefa_do_usuario(usuario_id, tarefa_id)

        if any(not p.concluido for p in self._passos_ativos(tarefa_id)):
            raise DadosInvalidos("A tarefa ainda tem passos pendentes.")

        return self.tarefa_repository.concluir(tarefa_id)

    def dividir_passo(self, usuario_id, tarefa_id, passo_id, idioma="es"):
        """H4.4 "Me atasqué": a IA divide o passo em 2 ou 3 menores, no lugar dele."""
        passo = self._obter_passo_da_tarefa(usuario_id, tarefa_id, passo_id)

        if passo.concluido or passo.substituido:
            raise DadosInvalidos("Esse passo não pode ser dividido.")

        tarefa = self.tarefa_repository.buscar_por_id(tarefa_id)
        novos = self.divisor_de_passo(tarefa.titulo, passo.texto, passo.minutos_estimados, idioma)

        return self.passo_repository.dividir(passo_id, novos)

    def alternar_status_passo(self, usuario_id, tarefa_id, passo_id):
        self._obter_passo_da_tarefa(usuario_id, tarefa_id, passo_id)

        return self.passo_repository.alternar_concluido(passo_id)

    def excluir_passo(self, usuario_id, tarefa_id, passo_id):
        self._obter_passo_da_tarefa(usuario_id, tarefa_id, passo_id)

        self.passo_repository.excluir(passo_id)
