from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, status

from api.dependencias import exigir_dono
from api.schemas import NovaTarefa, NovasTarefas, PassoSaida, Resposta, TarefaSaida
from controllers.tarefa_controller import TarefaController

router = APIRouter(
    prefix="/usuarios/{usuario_id}/tarefas",
    tags=["tarefas"],
    dependencies=[Depends(exigir_dono)]
)

controller = TarefaController()


@router.get("", response_model=Resposta[List[TarefaSaida]])
def listar_tarefas(usuario_id: int):
    return {
        "dados": controller.listar_tarefas(usuario_id)
    }


# Rotas fixas (/bandeja, /lote) antes de /{tarefa_id}, para não serem lidas como um id.
@router.get("/bandeja", response_model=Resposta[List[TarefaSaida]])
def listar_bandeja(usuario_id: int, hoje: Optional[date] = None):
    return {
        "dados": controller.listar_bandeja(usuario_id, hoje)
    }


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
def gerar_passos(usuario_id: int, tarefa_id: int):
    return {
        "dados": controller.gerar_passos(usuario_id, tarefa_id)
    }


@router.patch("/{tarefa_id}/passos/{passo_id}", response_model=Resposta[PassoSaida])
def alternar_status_passo(usuario_id: int, tarefa_id: int, passo_id: int):
    return {
        "dados": controller.alternar_status_passo(usuario_id, tarefa_id, passo_id)
    }


@router.delete("/{tarefa_id}/passos/{passo_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_passo(usuario_id: int, tarefa_id: int, passo_id: int):
    controller.excluir_passo(usuario_id, tarefa_id, passo_id)
