"""Variáveis de uso dos 3 meses antes da data de referência, por assinante.

Uso: python src/variaveis_uso.py   (depois de src/base_assinantes.py)

Para cada assinante de dados/processados/assinantes_ref.csv, soma o uso_mensal de
mai, jun e jul/2026 (os 3 meses completos até 31/07/2026). Só entram meses em que a
pessoa já era assinante (início antes do fim do mês); mês sem linha conta como uso zero
e é contado em meses_sem_linha (decisão em decisoes.md).

Colunas: meses_observados, meses_sem_linha, treinos_3m, treinos_m1 (jul), treinos_m2 (jun),
treinos_m3 (mai), dias_ativos_3m, minutos_3m, sessoes_3m, sessoes_m1, ar_livre_3m,
video_3m, treinos_mes (média por mês observado), sessoes_mes, pct_ar_livre,
queda_treinos (jul abaixo da metade da média de mai–jun, para quem tem os 3 meses).

Grava dados/processados/variaveis_uso.csv (uma linha por assinante).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
PROCESSADOS = RAIZ / "dados" / "processados"

MESES = {"m3": "2026-05", "m2": "2026-06", "m1": "2026-07"}
SOMAS = ["atividades", "dias_ativos", "minutos", "sessoes_app", "atividades_ar_livre", "atividades_video"]


def main():
    base = pd.read_csv(PROCESSADOS / "assinantes_ref.csv", usecols=["user_id", "inicio"], parse_dates=["inicio"])
    uso = pd.read_csv(BRUTOS / "uso_mensal.csv")
    uso = uso[uso["mes"].isin(MESES.values()) & uso["user_id"].isin(base["user_id"])]
    print(f"assinantes: {len(base)} | linhas do uso_mensal em mai–jul/2026 desses assinantes: {len(uso)}")

    grade = base.merge(pd.DataFrame({"chave": list(MESES), "mes": list(MESES.values())}), how="cross")
    fim_mes = pd.to_datetime(grade["mes"] + "-01") + pd.offsets.MonthBegin(1)
    grade = grade[grade["inicio"] < fim_mes]
    print(f"assinante-mês observados (já assinava no mês): {len(grade)}")
    grade = grade.merge(uso, on=["user_id", "mes"], how="left", validate="one_to_one", indicator=True)
    grade["sem_linha"] = grade.pop("_merge") == "left_only"
    grade[SOMAS] = grade[SOMAS].fillna(0)
    print(f"assinante-mês sem linha (contam como zero): {grade['sem_linha'].sum()}")

    v = grade.groupby("user_id").agg(
        meses_observados=("mes", "size"),
        meses_sem_linha=("sem_linha", "sum"),
        treinos_3m=("atividades", "sum"),
        dias_ativos_3m=("dias_ativos", "sum"),
        minutos_3m=("minutos", "sum"),
        sessoes_3m=("sessoes_app", "sum"),
        ar_livre_3m=("atividades_ar_livre", "sum"),
        video_3m=("atividades_video", "sum"),
    )
    por_mes = grade.pivot(index="user_id", columns="chave", values="atividades")
    for chave in ["m1", "m2", "m3"]:
        v[f"treinos_{chave}"] = por_mes[chave]
    v["sessoes_m1"] = grade[grade["chave"] == "m1"].set_index("user_id")["sessoes_app"]
    v["treinos_mes"] = (v["treinos_3m"] / v["meses_observados"]).round(2)
    v["sessoes_mes"] = (v["sessoes_3m"] / v["meses_observados"]).round(2)
    v["pct_ar_livre"] = (v["ar_livre_3m"] / v["treinos_3m"].where(v["treinos_3m"] > 0)).round(3)
    media_antes = (v["treinos_m2"] + v["treinos_m3"]) / 2
    tem_3 = v["meses_observados"] == 3
    v["queda_treinos"] = np.where(tem_3, ((media_antes > 0) & (v["treinos_m1"] < media_antes / 2)).astype(int), np.nan)

    v = base[["user_id"]].merge(v.reset_index(), on="user_id", how="left", validate="one_to_one")
    assert len(v) == len(base), "a junção mudou o número de assinantes"
    print(f"variáveis de uso: {len(v)} assinantes (= base)")
    print("meses_observados:", v["meses_observados"].value_counts().sort_index().to_dict())
    print("meses_sem_linha:", v["meses_sem_linha"].value_counts().sort_index().to_dict())
    print("treinos_3m: zero:", int((v["treinos_3m"] == 0).sum()), "| mediana:", v["treinos_3m"].median(),
          "| queda_treinos=1:", int((v["queda_treinos"] == 1).sum()), "de", int(tem_3.sum()), "com 3 meses")

    v.to_csv(PROCESSADOS / "variaveis_uso.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/variaveis_uso.csv ({len(v)} linhas, {v.shape[1]} colunas)")


if __name__ == "__main__":
    main()
