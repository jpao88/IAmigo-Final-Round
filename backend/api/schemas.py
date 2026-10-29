"""Formatos de entrada e saída da API.

Os limites de tamanho (max_length) seguem as colunas de database/schema.sql,
para o FastAPI recusar valores inválidos (422) antes de chegar ao service.

Os modelos de saída são a lista branca do que pode sair da API:
campos que não estão aqui (como senha_hash e papel) nunca são enviados.
"""
from datetime import date, datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Resposta(BaseModel, Generic[T]):
    dados: T


# ---------- Entrada ----------

class Login(BaseModel):
    nome: str
    senha: str


class NovoUsuario(BaseModel):
    nome: str = Field(max_length=100)
    email: str = Field(max_length=255)
    senha: str


class AtualizarUsuario(BaseModel):
    nome: str = Field(max_length=100)


class NovaTarefa(BaseModel):
    titulo: str = Field(max_length=200)


# ---------- Saída ----------

class SaidaORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UsuarioPublico(SaidaORM):
    id: int
    nome: str
    email: str
    limite_hoje: int
    onboarding_concluido: bool
    criado_em: Optional[datetime] = None


class TarefaSaida(SaidaORM):
    id: int
    usuario_id: int
    titulo: str
    data_planejada: Optional[date] = None
    ordem_dia: Optional[int] = None
    concluida: bool
    concluida_em: Optional[datetime] = None
    criado_em: Optional[datetime] = None


class PassoSaida(SaidaORM):
    id: int
    tarefa_id: int
    texto: str
    ordem: int
    minutos_estimados: int
    gerado_por_ia: bool
    concluido: bool
    concluido_em: Optional[datetime] = None
    substituido: bool
    passo_origem_id: Optional[int] = None


class Sessao(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    usuario: UsuarioPublico
