from fastapi import APIRouter

from api.schemas import Login, Resposta, Sessao
from controllers.usuario_controller import UsuarioController

router = APIRouter(
    prefix="/auth",
    tags=["autenticacao"]
)

controller = UsuarioController()


@router.post("/login", response_model=Resposta[Sessao])
def login(dados: Login):
    return {
        "dados": controller.autenticar(dados.nome, dados.senha)
    }
