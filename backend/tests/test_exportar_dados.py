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



class TestResumoUso(unittest.TestCase):
    def test_conta_por_pessoa_e_desde_uma_data(self):
        from types import SimpleNamespace as N
        from scripts.resumo_uso import resumir

        usuarios = [N(id=1, nome="Ana"), N(id=2, nome="Bia")]
        tarefas = [
            N(id=10, usuario_id=1, criado_em=datetime(2026, 11, 12, 9), concluida=True,
              concluida_em=datetime(2026, 11, 13, 10), data_planejada=date(2026, 11, 13)),
            N(id=11, usuario_id=1, criado_em=datetime(2026, 11, 10, 9), concluida=False,
              concluida_em=None, data_planejada=None),
            N(id=20, usuario_id=2, criado_em=datetime(2026, 11, 13, 9), concluida=False,
              concluida_em=None, data_planejada=date(2026, 11, 13)),
        ]
        passos = [
            N(tarefa_id=10, concluido=True, concluido_em=datetime(2026, 11, 13, 9, 30)),
            N(tarefa_id=10, concluido=True, concluido_em=datetime(2026, 11, 13, 9, 50)),
            N(tarefa_id=20, concluido=False, concluido_em=None),
        ]
        fechamentos = [N(usuario_id=1, data=date(2026, 11, 13))]

        ana, bia = resumir(usuarios, tarefas, passos, fechamentos)
        self.assertEqual(
            (ana["tarefas_criadas"], ana["passos_concluidos"], ana["tarefas_concluidas"],
             ana["dias_com_plano"], ana["dias_fechados"], ana["ultimo_dia_ativo"]),
            (2, 2, 1, 1, 1, date(2026, 11, 13)),
        )
        self.assertEqual((bia["passos_concluidos"], bia["dias_fechados"]), (0, 0))

        ana_desde = resumir(usuarios, tarefas, passos, fechamentos, desde=date(2026, 11, 12))[0]
        self.assertEqual(ana_desde["tarefas_criadas"], 1)


if __name__ == "__main__":
    unittest.main()
