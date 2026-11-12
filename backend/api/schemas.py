"""Formatos de entrada e saída da API.

Os limites de tamanho (max_length) seguem as colunas de database/schema.sql,
para o FastAPI recusar valores inválidos (422) antes de chegar ao service.

Os modelos de saída são a lista branca do que pode sair da API:
campos que não estão aqui (como senha_hash e papel) nunca são enviados.
"""
from datetime import date, datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Resposta(BaseModel, Generic[T]):
    dados: T


# ---------- Entrada ----------

class Login(BaseModel):
    email: str
    senha: str


class NovoUsuario(BaseModel):
    nome: str = Field(max_length=100)
    email: str = Field(max_length=255)
    senha: str


class AtualizarUsuario(BaseModel):
    nome: str = Field(max_length=100)


class NovaTarefa(BaseModel):
    titulo: str = Field(max_length=200)


class NovasTarefas(BaseModel):
    # Uma por linha do campo "¿Qué tienes en la cabeza?". O service limpa e valida cada uma.
    titulos: List[str]


class DadosPasso(BaseModel):
    # O service valida o texto (vazio, 255 caracteres) e os minutos (1 a 120; vazio = 10).
    texto: str
    minutos_estimados: Optional[int] = None


class TarefasDoDia(BaseModel):
    # Para "+ Hoy" (uma) e "Elegir tareas para hoy" (várias), e para a ordem nova.
    ids: List[int]
    data: Optional[date] = None  # data local da pessoa; vazia = hoje do servidor


class NovoLimiteHoje(BaseModel):
    limite_hoje: int


class OrdemPassos(BaseModel):
    # Todos os passos visíveis da tarefa, na ordem nova.
    ids: List[int]


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


class TarefaDoDia(TarefaSaida):
    # Passos visíveis ainda não concluídos; sem passos, 10 (H3.3: tempo total do dia).
    minutos_restantes: int


class ConclusaoPasso(BaseModel):
    # H4.2: tarefa_concluida = era o último passo; o front celebra a tarefa inteira.
    passo: PassoSaida
    tarefa_concluida: bool


class ResumoDia(BaseModel):
    # H5.1: só o que se conseguiu; H5.2: as pendentes, para decidir uma a uma.
    data: date
    passos_concluidos: int
    tarefas_concluidas: int
    concluidas: List[TarefaSaida]
    pendentes: List[TarefaSaida]
    fechado: bool


class DiaPendente(BaseModel):
    # H5.4: o último dia com tarefas que não foi fechado, ou null.
    data: Optional[date]
