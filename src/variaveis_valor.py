"""Variáveis de valor até a data de referência, por assinante.

Uso: python src/variaveis_valor.py   (depois de src/limpar_pagamentos.py e src/base_assinantes.py)

Para cada assinante de dados/processados/assinantes_ref.csv, usa só cobranças de
dados/processados/pagamentos_limpo.csv até o fim de 31/07/2026. Receita líquida desconta a
taxa do meio de pagamento (premissas do enunciado: loja 15%, cartão 3,5%, Pix 0,99%):
- valor_mensal_liquido: última cobrança aprovada até a data, líquida, por mês (anual ÷ 12).
  É o quanto o assinante deixa por mês hoje; base do indicador de valor dos segmentos;
- receita_liquida_ate_ref / receita_bruta_ate_ref: soma desde 07/2024 (início do histórico),
  já descontados estornos e chargebacks. Para quem assina desde antes, fica truncada;
- cobrancas_aprovadas_ate_ref, recusas_ate_ref, estorno_chargeback_ate_ref;
- cupom_influenciador: primeira anuidade a R$ 239,90.

Grava dados/processados/variaveis_valor.csv (uma linha por assinante).
"""
import sys
from pathlib import Path

import pandas as pd

from base_assinantes import DATA_REF

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
PROCESSADOS = RAIZ / "dados" / "processados"

TAXA = {"app_store": 0.15, "google_play": 0.15, "cartao": 0.035, "pix_automatico": 0.0099}
ANUAIS = {299.9, 239.9}


def main():
    base = pd.read_csv(PROCESSADOS / "assinantes_ref.csv", usecols=["user_id", "plano"])
    g = pd.read_csv(PROCESSADOS / "pagamentos_limpo.csv",
                    usecols=["user_id", "data_hora_brt", "valor_num", "metodo", "status"],
                    parse_dates=["data_hora_brt"])
    g = g[g["user_id"].isin(base["user_id"])]
    total = len(g)
    g = g[g["data_hora_brt"] <= DATA_REF]
    print(f"cobranças dos assinantes: {total} | até {DATA_REF}: {len(g)} (fora: {total - len(g)})")

    g["liquido"] = (g["valor_num"] * (1 - g["metodo"].map(TAXA))).round(2)
    efetiva = g["status"].isin(["aprovado", "estornado", "chargeback"])
    aprovada = g["status"] == "aprovado"

    v = pd.DataFrame(index=pd.Index(base["user_id"], name="user_id"))
    v["cobrancas_aprovadas_ate_ref"] = g[aprovada].groupby("user_id").size()
    v["receita_bruta_ate_ref"] = g[efetiva].groupby("user_id")["valor_num"].sum().round(2)
    v["receita_liquida_ate_ref"] = g[efetiva].groupby("user_id")["liquido"].sum().round(2)
    v["recusas_ate_ref"] = g[g["status"] == "recusado"].groupby("user_id").size()
    v["estorno_chargeback_ate_ref"] = (g[g["status"].isin(["estornado", "chargeback"])]
                                       .groupby("user_id").size() > 0).astype(int)
    ultima = g[aprovada].groupby("user_id")[["valor_num", "liquido"]].last()
    meses = ultima["valor_num"].isin(ANUAIS).map({True: 12, False: 1})
    v["valor_mensal_liquido"] = (ultima["liquido"] / meses).round(2)
    v["cupom_influenciador"] = (g[aprovada & (g["valor_num"] == 239.9)].groupby("user_id").size() > 0).astype(int)
    contagens = ["cobrancas_aprovadas_ate_ref", "recusas_ate_ref", "estorno_chargeback_ate_ref", "cupom_influenciador"]
    v[contagens] = v[contagens].fillna(0).astype(int)
    v[["receita_bruta_ate_ref", "receita_liquida_ate_ref"]] = v[["receita_bruta_ate_ref", "receita_liquida_ate_ref"]].fillna(0)
    v = v.reset_index()

    assert len(v) == len(base)
    sem_cobranca = v["valor_mensal_liquido"].isna()
    print(f"variáveis de valor: {len(v)} assinantes (= base) | sem cobrança aprovada até a data: {sem_cobranca.sum()}")
    print("valor_mensal_liquido:", v["valor_mensal_liquido"].value_counts().head(8).to_dict())
    print(f"receita líquida até a data (soma): R$ {v['receita_liquida_ate_ref'].sum():,.2f} | "
          f"recusas: {int((v['recusas_ate_ref'] > 0).sum())} assinantes | "
          f"estorno/chargeback: {int(v['estorno_chargeback_ate_ref'].sum())} | "
          f"cupom influenciador: {int(v['cupom_influenciador'].sum())}")

    v.to_csv(PROCESSADOS / "variaveis_valor.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/variaveis_valor.csv ({len(v)} linhas, {v.shape[1]} colunas)")


if __name__ == "__main__":
    main()
