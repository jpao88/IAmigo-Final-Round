from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, status

from api.dependencias import exigir_dono
from api.schemas import DiaPendente, Resposta, ResumoDia
from controllers.dia_controller import DiaController

# Épica 5 · Cerrar el día. As datas são as locais da pessoa, enviadas pelo front.
router = APIRouter(
    prefix="/usuarios/{usuario_id}/dias",
    tags=["dias"],
    dependencies=[Depends(exigir_dono)]
)

controller = DiaController()


# /pendente antes de /{data}.
@router.get("/pendente", response_model=Resposta[DiaPendente])
def dia_pendente(usuario_id: int, hoje: Optional[date] = None):
    return {
        "dados": {"data": controller.dia_pendente(usuario_id, hoje or date.today())}
    }


@router.get("/{data}", response_model=Resposta[ResumoDia])
def resumo_do_dia(usuario_id: int, data: date):
    return {
        "dados": controller.resumo(usuario_id, data)
    }


@router.post("/{data}/fechar", status_code=status.HTTP_204_NO_CONTENT)
def fechar_dia(usuario_id: int, data: date):
    controller.fechar(usuario_id, data)
