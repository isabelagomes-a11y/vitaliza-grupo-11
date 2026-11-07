"""Base de assinantes na data de referência, com o churn nos 60 dias seguintes.

Uso: python src/base_assinantes.py   (depois de src/situacao_assinantes.py e src/usuarios_master.py)

População: assinaturas pagas ativas no fim de 31/07/2026 (horário de Brasília), sem contas
internas. Uma linha por assinante. Só entram informações conhecidas até a data de
referência, exceto o rótulo:
- churn_60d = 1 se a assinatura expirou nos 60 dias seguintes (até o fim de 29/09/2026);
- tipo_saida e fim só são preenchidos para quem saiu na janela.
Plano na data de referência = plano do último evento com plano até ela.
master_nasc_sexo = "sim" se a conta está em usuarios_master.csv (nascimento e sexo válidos).

Grava dados/processados/assinantes_ref.csv.
"""
import sys
from pathlib import Path

import pandas as pd

from situacao_assinantes import ativos_em

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
PROCESSADOS = RAIZ / "dados" / "processados"

DATA_REF = pd.Timestamp("2026-08-01") - pd.Timedelta(seconds=1)  # fim de 31/07/2026
JANELA_DIAS = 60
FIM_JANELA = DATA_REF + pd.Timedelta(days=JANELA_DIAS)  # fim de 29/09/2026


def main():
    periodos = pd.read_csv(PROCESSADOS / "assinaturas_periodos.csv", parse_dates=["inicio", "fim"])
    print(f"assinaturas_periodos.csv: {len(periodos)} assinaturas "
          f"({periodos['interna'].sum()} internas, fora das contagens)")

    base = ativos_em(periodos, DATA_REF).copy()
    print(f"ativos em {DATA_REF}: {len(base)}")
    assert not base["user_id"].duplicated().any()

    ev = pd.read_csv(PROCESSADOS / "eventos_assinatura_limpo.csv", dtype=str, keep_default_na=False,
                     usecols=["user_id", "data_hora_brt", "plano"], parse_dates=["data_hora_brt"])
    ev = ev[(ev["plano"] != "") & (ev["data_hora_brt"] <= DATA_REF) & ev["user_id"].isin(base["user_id"])]
    plano_ref = ev.groupby("user_id")["plano"].last()
    base["plano_ref"] = base["user_id"].map(plano_ref).fillna(base["plano"])
    print(f"plano na data de referência: {base['user_id'].isin(plano_ref.index).sum()} pelos eventos, "
          f"{(~base['user_id'].isin(plano_ref.index)).sum()} pelo plano da assinatura | "
          f"mudaram de plano depois: {(base['plano_ref'] != base['plano']).sum()}")

    saiu = base["fim"].notna() & (base["fim"] <= FIM_JANELA)
    base["churn_60d"] = saiu.astype(int)
    base.loc[~saiu, ["fim", "tipo_saida"]] = [pd.NaT, ""]
    base["tempo_casa_dias"] = (DATA_REF.normalize() - base["inicio"].dt.normalize()).dt.days
    base["tempo_casa_meses"] = base["tempo_casa_dias"] // 30

    master = pd.read_csv(PROCESSADOS / "usuarios_master.csv", dtype=str, usecols=["user_id"])
    base["master_nasc_sexo"] = base["user_id"].isin(master["user_id"]).map({True: "sim", False: "nao"})

    cols = ["user_id", "plano_ref", "canal_cobranca", "inicio", "tempo_casa_dias", "tempo_casa_meses",
            "churn_60d", "fim", "tipo_saida", "master_nasc_sexo"]
    base = base[cols].rename(columns={"plano_ref": "plano"})

    print(f"churn_60d (até {FIM_JANELA}): {base['churn_60d'].sum()} de {len(base)} "
          f"({100 * base['churn_60d'].mean():.2f}%)")
    print("tipo de saída na janela:", base.loc[base["churn_60d"] == 1, "tipo_saida"].value_counts().to_dict())
    print("master_nasc_sexo:", base["master_nasc_sexo"].value_counts().to_dict())
    print("plano:", base["plano"].value_counts().to_dict(), "| canal:", base["canal_cobranca"].value_counts().to_dict())

    base.to_csv(PROCESSADOS / "assinantes_ref.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/assinantes_ref.csv ({len(base)} linhas, {base.shape[1]} colunas)")


if __name__ == "__main__":
    main()
