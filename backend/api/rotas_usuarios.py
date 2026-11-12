from typing import List

from fastapi import APIRouter, Depends, status

from api.dependencias import exigir_admin, exigir_dono, exigir_dono_ou_admin
from api.schemas import AtualizarUsuario, NovoLimiteHoje, NovoUsuario, Resposta, UsuarioPublico
from controllers.usuario_controller import UsuarioController

router = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"]
)

controller = UsuarioController()


@router.get(
    "",
    response_model=Resposta[List[UsuarioPublico]],
    dependencies=[Depends(exigir_admin)]
)
def listar_usuarios():
    return {
        "dados": controller.listar_perfis()
    }


@router.get(
    "/{usuario_id}",
    response_model=Resposta[UsuarioPublico],
    dependencies=[Depends(exigir_dono_ou_admin)]
)
def buscar_usuario(usuario_id: int):
    return {
        "dados": controller.buscar_perfil(usuario_id)
    }


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Resposta[UsuarioPublico])
def criar_usuario(dados: NovoUsuario):
    usuario = controller.criar_perfil(
        dados.nome,
        dados.email,
        dados.senha
    )

    return {
        "dados": usuario
    }


@router.put(
    "/{usuario_id}",
    response_model=Resposta[UsuarioPublico],
    dependencies=[Depends(exigir_dono_ou_admin)]
)
def atualizar_usuario(usuario_id: int, dados: AtualizarUsuario):
    usuario = controller.atualizar_perfil(usuario_id, dados.nome)

    return {
        "dados": usuario
    }


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(exigir_dono_ou_admin)]
)
def excluir_usuario(usuario_id: int):
    controller.excluir_perfil(usuario_id)


# H3.5: só a própria pessoa muda o seu limite de Hoje.
@router.put(
    "/{usuario_id}/limite-hoje",
    response_model=Resposta[UsuarioPublico],
    dependencies=[Depends(exigir_dono)]
)
def alterar_limite_hoje(usuario_id: int, dados: NovoLimiteHoje):
    return {
        "dados": controller.alterar_limite_hoje(usuario_id, dados.limite_hoje)
    }


# H6.3: terminou a primeira tarefa guiada (ou pulou a guia).
@router.put(
    "/{usuario_id}/onboarding",
    response_model=Resposta[UsuarioPublico],
    dependencies=[Depends(exigir_dono)]
)
def concluir_onboarding(usuario_id: int):
    return {
        "dados": controller.concluir_onboarding(usuario_id)
    }
