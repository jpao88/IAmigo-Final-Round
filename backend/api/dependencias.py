from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from controllers.usuario_controller import UsuarioController
from core.erros import NaoEncontrado
from core.seguranca import validar_token_acesso

bearer = HTTPBearer(auto_error=False)
controller = UsuarioController()


def _nao_autenticado(mensagem):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=mensagem,
        headers={"WWW-Authenticate": "Bearer"}
    )


def obter_usuario_autenticado(
    credenciais: Optional[HTTPAuthorizationCredentials] = Depends(bearer)
):
    if credenciais is None:
        raise _nao_autenticado("Token de acesso ausente.")

    try:
        usuario_id = validar_token_acesso(credenciais.credentials)
        return controller.buscar_perfil(usuario_id)
    except (ValueError, NaoEncontrado):
        raise _nao_autenticado("Token inválido ou expirado.")


def _sem_permissao():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não tem permissão para esta ação."
    )


def exigir_dono(
    usuario_id: int,
    usuario_autenticado=Depends(obter_usuario_autenticado)
):
    """Autorização: só o próprio dono da conta pode continuar (nem o admin)."""
    if usuario_autenticado.id == usuario_id:
        return usuario_autenticado

    raise _sem_permissao()


def exigir_dono_ou_admin(
    usuario_id: int,
    usuario_autenticado=Depends(obter_usuario_autenticado)
):
    """Autorização: só o admin ou o próprio dono da conta podem continuar."""
    if usuario_autenticado.papel == "admin":
        return usuario_autenticado

    if usuario_autenticado.id == usuario_id:
        return usuario_autenticado

    raise _sem_permissao()


def exigir_admin(usuario_autenticado=Depends(obter_usuario_autenticado)):
    """Autorização: só o admin pode continuar."""
    if usuario_autenticado.papel == "admin":
        return usuario_autenticado

    raise _sem_permissao()
