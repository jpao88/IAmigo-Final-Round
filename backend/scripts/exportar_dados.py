"""Respaldo próprio: exporta todas as contas, tarefas, passos e fechamentos para um arquivo JSON.

Complementa os backups automáticos do Aiven. O arquivo tem dados pessoais
(nomes, e-mails, hashes de senha): fica FORA do repositório, na pasta
RESPALDOS_DIR do .env ou, sem ela, em ~/IAmigo-respaldos.

Uso, a partir de backend/:
    .venv\\Scripts\\python scripts\\exportar_dados.py
"""
import json
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

# Permite rodar o arquivo diretamente (python scripts/exportar_dados.py).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402

# Na ordem em que dá para restaurar (cada tabela depende só das anteriores).
TABELAS = ["usuarios", "tarefas", "passos", "fechamentos_dia"]


def _valor(valor):
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    if isinstance(valor, Decimal):
        return int(valor) if valor == valor.to_integral_value() else float(valor)
    return valor


def exportar(engine, metadata):
    """Lê as tabelas numa única transação (uma foto consistente) e devolve um dicionário."""
    dados = {"exportado_em": datetime.now().isoformat(timespec="seconds"), "tabelas": {}}

    with engine.connect() as conexao:
        for nome in TABELAS:
            tabela = metadata.tables[nome]
            linhas = conexao.execute(select(tabela).order_by(*tabela.primary_key.columns))
            dados["tabelas"][nome] = [
                {coluna: _valor(valor) for coluna, valor in linha._mapping.items()}
                for linha in linhas
            ]

    return dados


def pasta_de_respaldos():
    pasta = os.getenv("RESPALDOS_DIR") or str(Path.home() / "IAmigo-respaldos")
    return Path(pasta)


def main():
    from config.database import Base, engine
    import models  # noqa: F401  (registra as tabelas em Base.metadata)

    dados = exportar(engine, Base.metadata)

    pasta = pasta_de_respaldos()
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / f"iamigo-{datetime.now():%Y-%m-%d-%H%M}.json"
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"Respaldo guardado en {arquivo}")
    for nome, linhas in dados["tabelas"].items():
        print(f"  {nome}: {len(linhas)}")


if __name__ == "__main__":
    main()
