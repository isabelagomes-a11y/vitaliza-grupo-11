"""Sinais de assinatura até a data de referência, por assinante.

Uso: python src/variaveis_eventos.py   (depois de src/base_assinantes.py)

Para cada assinante de dados/processados/assinantes_ref.csv, usa só eventos de
dados/processados/eventos_assinatura_limpo.csv até o fim de 31/07/2026 (horário de Brasília):
- veio_de_trial: começou com trial (trial_iniciado antes do início da assinatura);
- renovacoes_ate_ref: quantas renovações já pagou;
- renovacao_desligada_ref: renovação automática desligada na data de referência (último
  desligamento sem religamento depois). É o aviso que a loja manda antes da expiração;
- dias_desde_desligar: dias entre esse desligamento e a data de referência;
- desligou_alguma_vez, religou_alguma_vez;
- carencia_ate_ref: já teve período de carência (cobrança recusada);
- cancelamento_web_ate_ref: cancelou pelo site (o período pago segue até expirar);
- chargeback_reembolso_ate_ref.

Grava dados/processados/variaveis_eventos.csv (uma linha por assinante).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from base_assinantes import DATA_REF

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
PROCESSADOS = RAIZ / "dados" / "processados"


def main():
    base = pd.read_csv(PROCESSADOS / "assinantes_ref.csv", usecols=["user_id", "inicio"], parse_dates=["inicio"])
    ev = pd.read_csv(PROCESSADOS / "eventos_assinatura_limpo.csv", dtype=str, keep_default_na=False,
                     usecols=["user_id", "data_hora_brt", "evento"], parse_dates=["data_hora_brt"])
    ev = ev[ev["user_id"].isin(base["user_id"])]
    total = len(ev)
    ev = ev[ev["data_hora_brt"] <= DATA_REF]
    print(f"eventos dos assinantes: {total} | até {DATA_REF}: {len(ev)} (fora: {total - len(ev)})")

    conta = ev.pivot_table(index="user_id", columns="evento", values="data_hora_brt", aggfunc="count", fill_value=0)
    ultimo = ev.pivot_table(index="user_id", columns="evento", values="data_hora_brt", aggfunc="max")
    primeiro = ev.pivot_table(index="user_id", columns="evento", values="data_hora_brt", aggfunc="min")

    def col(tabela, evento, padrao):
        return tabela[evento] if evento in tabela else pd.Series(padrao, index=tabela.index)

    v = base.set_index("user_id")
    trial = col(primeiro, "trial_iniciado", pd.NaT).reindex(v.index)
    v["veio_de_trial"] = (trial.notna() & (trial <= v["inicio"])).astype(int)
    v["renovacoes_ate_ref"] = col(conta, "renovacao", 0).reindex(v.index).fillna(0).astype(int)
    desl = col(ultimo, "renovacao_automatica_desligada", pd.NaT).reindex(v.index)
    relig = col(ultimo, "renovacao_automatica_religada", pd.NaT).reindex(v.index)
    desligada = desl.notna() & (relig.isna() | (relig < desl))
    v["renovacao_desligada_ref"] = desligada.astype(int)
    v["dias_desde_desligar"] = np.where(desligada, (DATA_REF - desl).dt.days, np.nan)
    v["desligou_alguma_vez"] = desl.notna().astype(int)
    v["religou_alguma_vez"] = relig.notna().astype(int)
    for nome, evento in [("carencia_ate_ref", "periodo_carencia"), ("cancelamento_web_ate_ref", "cancelamento_web")]:
        v[nome] = (col(conta, evento, 0).reindex(v.index).fillna(0) > 0).astype(int)
    cb = col(conta, "chargeback", 0).reindex(v.index).fillna(0) + col(conta, "reembolso", 0).reindex(v.index).fillna(0)
    v["chargeback_reembolso_ate_ref"] = (cb > 0).astype(int)

    v = v.drop(columns="inicio").reset_index()
    assert len(v) == len(base)
    print(f"variáveis de eventos: {len(v)} assinantes (= base)")
    for c in ["veio_de_trial", "renovacao_desligada_ref", "desligou_alguma_vez", "religou_alguma_vez",
              "carencia_ate_ref", "cancelamento_web_ate_ref", "chargeback_reembolso_ate_ref"]:
        print(f"{c}: {int(v[c].sum())}")
    print("renovacoes_ate_ref (mediana, máx):", v["renovacoes_ate_ref"].median(), v["renovacoes_ate_ref"].max(),
          "| dias_desde_desligar (mediana):", v["dias_desde_desligar"].median())

    v.to_csv(PROCESSADOS / "variaveis_eventos.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/variaveis_eventos.csv ({len(v)} linhas, {v.shape[1]} colunas)")


if __name__ == "__main__":
    main()
