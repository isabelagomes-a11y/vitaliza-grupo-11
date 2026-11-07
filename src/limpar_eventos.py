"""Limpeza do eventos_assinatura.csv: fuso único e marcação do plano ausente.

Uso: python src/limpar_eventos.py

Lê dados/brutos/eventos_assinatura.csv (sem alterar) e grava
dados/processados/eventos_assinatura_limpo.csv, ordenado por user_id e data_hora_brt.
Decisões registradas em decisoes.md:
- data_hora_brt: data/hora em horário de Brasília. As lojas gravam em UTC (terminado em
  "Z") e são convertidas; o site já grava em Brasília e fica como está. data_hora original
  é mantida.
- plano_ausente: "trial" quando o plano falta num evento de trial (esperado, ainda não há
  plano), "sem_plano" nos demais eventos sem plano, vazio quando há plano. Não imputa.
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
PROCESSADOS = RAIZ / "dados" / "processados"

FUSO = "America/Sao_Paulo"
CORTE = pd.Timestamp("2026-10-01")  # primeiro instante depois do corte de 30/09/2026
EVENTOS_TRIAL = {"trial_iniciado", "trial_expirado"}


def main():
    ev = pd.read_csv(BRUTOS / "eventos_assinatura.csv", dtype=str, keep_default_na=False)
    n = len(ev)
    print(f"eventos_assinatura.csv: {n} linhas")

    utc = ev["data_hora"].str.endswith("Z")
    loja = ~ev["canal_cobranca"].str.startswith("web")
    assert (utc == loja).all(), "fuso não coincide com o canal; rever a regra"
    convertidas = pd.to_datetime(ev.loc[utc, "data_hora"], format="%Y-%m-%dT%H:%M:%SZ", utc=True)
    convertidas = convertidas.dt.tz_convert(FUSO).dt.tz_localize(None)
    locais = pd.to_datetime(ev.loc[~utc, "data_hora"], format="%Y-%m-%d %H:%M:%S")
    ev["data_hora_brt"] = pd.concat([convertidas, locais]).sort_index()
    mes_utc = ev.loc[utc, "data_hora"].str[:7]
    mudou_mes = int((mes_utc != ev.loc[utc, "data_hora_brt"].dt.strftime("%Y-%m")).sum())
    print(f"fuso: {utc.sum()} linhas de loja convertidas de UTC para Brasília "
          f"({mudou_mes} mudam de mês); {(~utc).sum()} do site já em Brasília")
    assert (ev["data_hora_brt"] < CORTE).all(), "há evento depois do corte"

    sem_plano = ev["plano"].str.strip() == ""
    trial = ev["evento"].isin(EVENTOS_TRIAL)
    ev["plano_ausente"] = ""
    ev.loc[sem_plano & trial, "plano_ausente"] = "trial"
    ev.loc[sem_plano & ~trial, "plano_ausente"] = "sem_plano"
    print("plano_ausente:", ev["plano_ausente"].replace("", "(tem plano)").value_counts().to_dict())

    ev = ev.sort_values(["user_id", "data_hora_brt"], kind="stable")
    assert len(ev) == n
    PROCESSADOS.mkdir(exist_ok=True)
    ev.to_csv(PROCESSADOS / "eventos_assinatura_limpo.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/eventos_assinatura_limpo.csv ({len(ev)} linhas, {ev.shape[1]} colunas)")


if __name__ == "__main__":
    main()
