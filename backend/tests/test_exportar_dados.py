"""Respaldo próprio (scripts/exportar_dados.py), com um SQLite em memória no lugar do MySQL."""
import json
import unittest
from datetime import date, datetime

from sqlalchemy import create_engine

import models  # noqa: F401  (registra as tabelas)
from config.database import Base
from models import FechamentoDia, Passo, Tarefa, Usuario
from scripts.exportar_dados import TABELAS, exportar
from sqlalchemy.orm import Session


class TestExportarDados(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)

        with Session(self.engine) as sessao:
            sessao.add(Usuario(id=1, nome="Ana", email="ana@exemplo.com", senha_hash="hash",
                               papel="usuario", limite_hoje=3, onboarding_concluido=True,
                               criado_em=datetime(2026, 11, 1, 9, 30)))
            sessao.add(Tarefa(id=10, usuario_id=1, titulo="Lavar louça", data_planejada=date(2026, 11, 12),
                              ordem_dia=1, concluida=False, criado_em=datetime(2026, 11, 1, 9, 31)))
            sessao.add(Passo(id=100, tarefa_id=10, texto="Juntar a louça", ordem=1, minutos_estimados=5,
                             gerado_por_ia=True, concluido=True, substituido=False))
            sessao.add(FechamentoDia(id=1, usuario_id=1, data=date(2026, 11, 11)))
            sessao.commit()

    def test_exporta_todas_as_tabelas_em_json(self):
        dados = exportar(self.engine, Base.metadata)

        self.assertEqual(list(dados["tabelas"]), TABELAS)
        self.assertEqual(dados["tabelas"]["usuarios"][0]["email"], "ana@exemplo.com")
        self.assertEqual(dados["tabelas"]["tarefas"][0]["data_planejada"], "2026-11-12")
        self.assertEqual(dados["tabelas"]["passos"][0]["texto"], "Juntar a louça")
        self.assertEqual(dados["tabelas"]["fechamentos_dia"][0]["data"], "2026-11-11")

        # Tudo vira JSON sem erro (datas como texto).
        json.dumps(dados, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
