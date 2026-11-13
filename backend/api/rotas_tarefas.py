from datetime import date
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, status

from api.dependencias import exigir_dono
from api.schemas import (
    ConclusaoPasso, DadosPasso, NovaTarefa, NovasTarefas, OrdemPassos, PassoSaida, Resposta,
    TarefaDoDia, TarefasDoDia, TarefaSaida,
)
from controllers.tarefa_controller import TarefaController

router = APIRouter(
    prefix="/usuarios/{usuario_id}/tarefas",
    tags=["tarefas"],
    dependencies=[Depends(exigir_dono)]
)

controller = TarefaController()

# Idioma dos passos que a IA escreve (o mesmo da interface da pessoa).
Idioma = Literal["es", "pt"]


@router.get("", response_model=Resposta[List[TarefaSaida]])
def listar_tarefas(usuario_id: int):
    return {
        "dados": controller.listar_tarefas(usuario_id)
    }


# Rotas fixas (/bandeja, /hoje, /lote) antes de /{tarefa_id}, para não serem lidas como um id.
@router.get("/bandeja", response_model=Resposta[List[TarefaSaida]])
def listar_bandeja(usuario_id: int, hoje: Optional[date] = None):
    return {
        "dados": controller.listar_bandeja(usuario_id, hoje)
    }


@router.get("/hoje", response_model=Resposta[List[TarefaDoDia]])
def listar_hoje(usuario_id: int, data: Optional[date] = None):
    return {
        "dados": controller.listar_hoje(usuario_id, data)
    }


@router.post("/hoje", response_model=Resposta[List[TarefaSaida]])
def planejar_para_hoje(usuario_id: int, dados: TarefasDoDia):
    return {
        "dados": controller.planejar_para_hoje(usuario_id, dados.ids, dados.data)
    }


@router.put("/hoje/ordem", status_code=status.HTTP_204_NO_CONTENT)
def reordenar_hoje(usuario_id: int, dados: TarefasDoDia):
    controller.reordenar_hoje(usuario_id, dados.ids, dados.data)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Resposta[TarefaSaida])
def criar_tarefa(usuario_id: int, dados: NovaTarefa):
    return {
        "dados": controller.criar_tarefa(usuario_id, dados.titulo)
    }


@router.post("/lote", status_code=status.HTTP_201_CREATED, response_model=Resposta[List[TarefaSaida]])
def criar_varias(usuario_id: int, dados: NovasTarefas):
    return {
        "dados": controller.criar_varias(usuario_id, dados.titulos)
    }


@router.put("/{tarefa_id}", response_model=Resposta[TarefaSaida])
def renomear_tarefa(usuario_id: int, tarefa_id: int, dados: NovaTarefa):
    return {
        "dados": controller.renomear_tarefa(usuario_id, tarefa_id, dados.titulo)
    }


@router.patch("/{tarefa_id}", response_model=Resposta[TarefaSaida])
def alternar_status(usuario_id: int, tarefa_id: int):
    return {
        "dados": controller.alternar_status(usuario_id, tarefa_id)
    }


@router.get("/{tarefa_id}", response_model=Resposta[TarefaSaida])
def buscar_tarefa(usuario_id: int, tarefa_id: int):
    return {
        "dados": controller.buscar_tarefa(usuario_id, tarefa_id)
    }


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_tarefa(usuario_id: int, tarefa_id: int):
    controller.excluir_tarefa(usuario_id, tarefa_id)


# ---- Modo foco (Épica 4) ----

@router.post("/{tarefa_id}/concluir", response_model=Resposta[TarefaSaida])
def concluir_tarefa(usuario_id: int, tarefa_id: int):
    return {
        "dados": controller.concluir_tarefa(usuario_id, tarefa_id)
    }


@router.post("/{tarefa_id}/passos/{passo_id}/concluir", response_model=Resposta[ConclusaoPasso])
def concluir_passo(usuario_id: int, tarefa_id: int, passo_id: int):
    return {
        "dados": controller.concluir_passo(usuario_id, tarefa_id, passo_id)
    }


@router.post(
    "/{tarefa_id}/passos/{passo_id}/dividir",
    status_code=status.HTTP_201_CREATED,
    response_model=Resposta[List[PassoSaida]]
)
def dividir_passo(usuario_id: int, tarefa_id: int, passo_id: int, idioma: Idioma = "es"):
    return {
        "dados": controller.dividir_passo(usuario_id, tarefa_id, passo_id, idioma)
    }


@router.delete("/{tarefa_id}/hoje", response_model=Resposta[TarefaSaida])
def tirar_de_hoje(usuario_id: int, tarefa_id: int):
    return {
        "dados": controller.tirar_de_hoje(usuario_id, tarefa_id)
    }


@router.get("/{tarefa_id}/passos", response_model=Resposta[List[PassoSaida]])
def listar_passos(usuario_id: int, tarefa_id: int):
    return {
        "dados": controller.listar_passos(usuario_id, tarefa_id)
    }


@router.post(
    "/{tarefa_id}/passos/gerar",
    status_code=status.HTTP_201_CREATED,
    response_model=Resposta[List[PassoSaida]]
)
def gerar_passos(usuario_id: int, tarefa_id: int, idioma: Idioma = "es"):
    return {
        "dados": controller.gerar_passos(usuario_id, tarefa_id, idioma)
    }


@router.post(
    "/{tarefa_id}/passos",
    status_code=status.HTTP_201_CREATED,
    response_model=Resposta[PassoSaida]
)
def adicionar_passo(usuario_id: int, tarefa_id: int, dados: DadosPasso):
    return {
        "dados": controller.adicionar_passo(
            usuario_id, tarefa_id, dados.texto, dados.minutos_estimados
        )
    }


# /ordem antes de /{passo_id}, para não ser lida como um id.
@router.put("/{tarefa_id}/passos/ordem", response_model=Resposta[List[PassoSaida]])
def reordenar_passos(usuario_id: int, tarefa_id: int, dados: OrdemPassos):
    return {
        "dados": controller.reordenar_passos(usuario_id, tarefa_id, dados.ids)
    }


@router.put("/{tarefa_id}/passos/{passo_id}", response_model=Resposta[PassoSaida])
def editar_passo(usuario_id: int, tarefa_id: int, passo_id: int, dados: DadosPasso):
    return {
        "dados": controller.editar_passo(
            usuario_id, tarefa_id, passo_id, dados.texto, dados.minutos_estimados
        )
    }


@router.patch("/{tarefa_id}/passos/{passo_id}", response_model=Resposta[PassoSaida])
def alternar_status_passo(usuario_id: int, tarefa_id: int, passo_id: int):
    return {
        "dados": controller.alternar_status_passo(usuario_id, tarefa_id, passo_id)
    }


@router.delete("/{tarefa_id}/passos/{passo_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_passo(usuario_id: int, tarefa_id: int, passo_id: int):
    controller.excluir_passo(usuario_id, tarefa_id, passo_id)
