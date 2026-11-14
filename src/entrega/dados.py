"""Números da entrega da semana 5 que não estão em numeros.json: série 2025 × 2026 e renovações do anual.

Uso (na raiz do projeto):  python src/entrega/dados.py
Grava saidas/graficos/entrega.json. Lê os brutos pelo código unificado (src/vitaliza).
"""
import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
from vitaliza.base import churn_mensal, load_assinaturas, load_eventos, spells  # noqa: E402

SAIDA = RAIZ / "saidas" / "graficos" / "entrega.json"


def serie_por_plano(sp):
    """Churn mensal (perdas no mês ÷ ativos no início) por plano, jan/2025 a set/2026."""
    meses = pd.date_range("2025-01-01", "2026-09-01", freq="MS")
    return {p: {m: round(100 * c, 1) for m, c in churn_mensal(sp[sp.plano == p], meses).set_index("mes").churn.items()}
            for p in ("mensal", "anual")}


def renovacoes_anuais(sp, a):
    """Cada aniversário de assinatura anual de 2025 a set/2026: número da renovação e se saiu nela."""
    inicio = a.set_index("user_id").inicio
    linhas = []
    for r in sp[sp.plano == "anual"].itertuples():
        comeco = inicio.get(r.user_id)
        if pd.isna(comeco):
            continue
        for k in range(1, 8):
            aniv = comeco + pd.DateOffset(years=k)
            if aniv >= pd.Timestamp("2026-10-01"):
                break
            if aniv < pd.Timestamp("2025-01-01") or r.ini > aniv:
                continue
            if pd.notna(r.fim) and r.fim < aniv - pd.Timedelta(days=40):
                break
            saiu = bool(pd.notna(r.fim) and r.fim <= aniv + pd.Timedelta(days=5))
            linhas.append((aniv, k, saiu))
            if saiu:
                break
    rv = pd.DataFrame(linhas, columns=["aniv", "k", "saiu"])
    rv["tri"] = rv.aniv.dt.to_period("Q").astype(str)
    rv["primeira"] = rv.k == 1
    t = rv.groupby("tri").agg(renovacoes=("k", "size"), pct_primeira=("primeira", "mean"))
    t["churn_primeira"] = rv[rv.primeira].groupby("tri").saiu.mean()
    t["churn_seguintes"] = rv[~rv.primeira].groupby("tri").saiu.mean()
    t[["pct_primeira", "churn_primeira", "churn_seguintes"]] *= 100
    return t.round(1).reset_index().to_dict("records")


def main():
    e, a = load_eventos(), load_assinaturas()
    sp = spells(e, a)
    dados = {"serie_plano": serie_por_plano(sp), "renovacoes_anuais": renovacoes_anuais(sp, a)}
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(dados["renovacoes_anuais"], ensure_ascii=False))
    print("gravado:", SAIDA.relative_to(RAIZ))


if __name__ == "__main__":
    main()
