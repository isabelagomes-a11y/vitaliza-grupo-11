"""Limpeza do pagamentos.csv: cópias removidas, valor numérico, fuso único e marcações.

Uso: python src/limpar_pagamentos.py   (depois de src/situacao_assinantes.py)

Lê dados/brutos/pagamentos.csv (sem alterar) e grava dados/processados/pagamentos_limpo.csv,
ordenado por user_id e data_hora_brt. Decisões registradas em decisoes.md:
- remove a segunda cópia das cobranças idênticas em tudo menos pagamento_id (fica a de
  menor pagamento_id);
- valor_num: valor como número ("R$ 34,90" e "34.90" viram 34.9); negativos são estornos
  e chargebacks;
- data_hora_brt: horário de Brasília (loja em UTC convertida; site já em Brasília);
- tentativa_sem_recusa: tentativa 2 sem recusa antes (a coluna tentativa não é usada);
- metodo_diverge_canal: meio de pagamento diferente do canal da assinatura;
- preco_antigo_pos_reajuste: mensal cobrado a R$ 34,90 a partir de 01/03/2026.
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
PROCESSADOS = RAIZ / "dados" / "processados"

FUSO = "America/Sao_Paulo"
CORTE = pd.Timestamp("2026-10-01")
REAJUSTE = pd.Timestamp("2026-03-01")
CANAL_DO_METODO = {"app_store": "app_store", "google_play": "google_play",
                   "cartao": "web_cartao", "pix_automatico": "web_pix"}


def main():
    g = pd.read_csv(BRUTOS / "pagamentos.csv", dtype=str, keep_default_na=False)
    n = len(g)
    print(f"pagamentos.csv: {n} linhas")

    sem_id = [c for c in g.columns if c != "pagamento_id"]
    g = g.sort_values("pagamento_id")
    copia = g.duplicated(sem_id, keep="first")
    g = g[~copia]
    print(f"cópias removidas: {copia.sum()} | restam {len(g)}")

    formato_br = g["valor"].str.startswith("R$")
    g["valor_num"] = (g["valor"].str.replace("R$ ", "", regex=False)
                      .str.replace(",", ".", regex=False).astype(float))
    print(f"valor: {formato_br.sum()} no formato 'R$ 0,00' convertidas | valores: {sorted(g['valor_num'].unique())}")

    utc = g["data_hora"].str.endswith("Z")
    loja = g["metodo"].isin(["app_store", "google_play"])
    assert (utc == loja).all(), "fuso não coincide com o meio de pagamento; rever a regra"
    convertidas = pd.to_datetime(g.loc[utc, "data_hora"], format="%Y-%m-%dT%H:%M:%SZ", utc=True)
    convertidas = convertidas.dt.tz_convert(FUSO).dt.tz_localize(None)
    locais = pd.to_datetime(g.loc[~utc, "data_hora"], format="%Y-%m-%d %H:%M:%S")
    g["data_hora_brt"] = pd.concat([convertidas, locais]).reindex(g.index)
    assert (g["data_hora_brt"] < CORTE).all(), "há pagamento depois do corte"
    print(f"fuso: {utc.sum()} de loja convertidas de UTC para Brasília; {(~utc).sum()} do site já em Brasília")

    g = g.sort_values(["user_id", "data_hora_brt"], kind="stable")
    anterior = g.groupby("user_id")["status"].shift(1)
    g["tentativa_sem_recusa"] = ((g["tentativa"] == "2") & (anterior != "recusado")).astype(int)
    periodos = pd.read_csv(PROCESSADOS / "assinaturas_periodos.csv", usecols=["user_id", "canal_cobranca"])
    canal = g["user_id"].map(periodos.set_index("user_id")["canal_cobranca"])
    assert canal.notna().all(), "pagamento de usuário sem assinatura"
    g["metodo_diverge_canal"] = (g["metodo"].map(CANAL_DO_METODO) != canal).astype(int)
    g["preco_antigo_pos_reajuste"] = ((g["valor_num"] == 34.9) & (g["data_hora_brt"] >= REAJUSTE)).astype(int)
    for c in ["tentativa_sem_recusa", "metodo_diverge_canal", "preco_antigo_pos_reajuste"]:
        print(f"{c}: {int(g[c].sum())}")

    assert len(g) == n - copia.sum()
    g.to_csv(PROCESSADOS / "pagamentos_limpo.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/pagamentos_limpo.csv ({len(g)} linhas, {g.shape[1]} colunas)")


if __name__ == "__main__":
    main()
