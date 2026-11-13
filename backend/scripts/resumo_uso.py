"""Resumo de uso por pessoa, para acompanhar a prueba de varios días (Fase 3).

Mostra só números, nunca o texto das tarefas: quantas criou, quantos passos
e tarefas concluiu, em quantos dias planejou e fechou o dia, e o último dia ativo.

Uso, a partir de backend/:
    .venv\\Scripts\\python scripts\\resumo_uso.py              (todas as contas)
    .venv\\Scripts\\python scripts\\resumo_uso.py 2026-11-13   (só atividade desde essa data)
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _dia(valor):
    return valor.date() if hasattr(valor, "date") else valor


def resumir(usuarios, tarefas, passos, fechamentos, desde=None):
    """Recebe listas de objetos (do banco ou de teste) e devolve uma linha por pessoa."""
    def conta(dia):
        return dia is not None and (desde is None or _dia(dia) >= desde)

    tarefa_dono = {t.id: t.usuario_id for t in tarefas}
    linhas = []

    for usuario in sorted(usuarios, key=lambda u: u.id):
        minhas = [t for t in tarefas if t.usuario_id == usuario.id]
        meus_passos = [p for p in passos if tarefa_dono.get(p.tarefa_id) == usuario.id]
        meus_fechamentos = [f for f in fechamentos if f.usuario_id == usuario.id]

        datas = (
            [_dia(t.criado_em) for t in minhas if conta(t.criado_em)]
            + [_dia(t.concluida_em) for t in minhas if conta(t.concluida_em)]
            + [_dia(p.concluido_em) for p in meus_passos if conta(p.concluido_em)]
        )

        linhas.append({
            "id": usuario.id,
            "nome": usuario.nome,
            "tarefas_criadas": sum(1 for t in minhas if conta(t.criado_em)),
            "passos_concluidos": sum(1 for p in meus_passos if p.concluido and conta(p.concluido_em)),
            "tarefas_concluidas": sum(1 for t in minhas if t.concluida and conta(t.concluida_em)),
            "dias_com_plano": len({t.data_planejada for t in minhas if conta(t.data_planejada)}),
            "dias_fechados": sum(1 for f in meus_fechamentos if conta(f.data)),
            "ultimo_dia_ativo": max(datas) if datas else None,
        })

    return linhas


def main():
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from config.database import engine
    from models import FechamentoDia, Passo, Tarefa, Usuario

    # Consola do Windows: acentos certos.
    sys.stdout.reconfigure(encoding="utf-8")
    desde = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else None

    with Session(engine) as sessao:
        linhas = resumir(
            list(sessao.scalars(select(Usuario))),
            list(sessao.scalars(select(Tarefa))),
            list(sessao.scalars(select(Passo))),
            list(sessao.scalars(select(FechamentoDia))),
            desde,
        )

    print(f"Uso {'desde ' + desde.isoformat() if desde else 'total'}:")
    print(f"{'id':>3}  {'nombre':<16} {'creadas':>7} {'pasos':>5} {'hechas':>6} {'días plan':>9} {'cerrados':>8}  último día")
    for l in linhas:
        print(
            f"{l['id']:>3}  {l['nome'][:16]:<16} {l['tarefas_criadas']:>7} {l['passos_concluidos']:>5} "
            f"{l['tarefas_concluidas']:>6} {l['dias_com_plano']:>9} {l['dias_fechados']:>8}  "
            f"{l['ultimo_dia_ativo'] or '-'}"
        )


if __name__ == "__main__":
    main()
