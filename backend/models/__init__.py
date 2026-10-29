# Importa todos os modelos juntos: os relationship() se referem uns aos
# outros pelo nome ("Tarefa", "Passo") e o SQLAlchemy precisa conhecer todos.
from models.usuario import Usuario
from models.tarefa import Tarefa
from models.passo import Passo
from models.fechamento_dia import FechamentoDia

__all__ = ["Usuario", "Tarefa", "Passo", "FechamentoDia"]
