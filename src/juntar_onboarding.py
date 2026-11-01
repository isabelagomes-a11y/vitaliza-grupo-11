"""Junta o questionário de entrada à base master de usuários.

Uso: python src/juntar_onboarding.py   (depois de src/usuarios_master.py)

Left join de dados/processados/usuarios_master.csv com dados/brutos/onboarding.csv pelo
user_id: a master manda, nenhuma conta entra ou sai. Os textos vêm como estão no bruto.
Grava dados/processados/usuarios_master_onboarding.csv, com a coluna tem_onboarding.
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
PROCESSADOS = RAIZ / "dados" / "processados"


def main():
    master = pd.read_csv(PROCESSADOS / "usuarios_master.csv", dtype=str, keep_default_na=False)
    onb = pd.read_csv(BRUTOS / "onboarding.csv", dtype=str, keep_default_na=False)
    print(f"master: {len(master)} linhas | onboarding: {len(onb)} linhas")
    assert not onb["user_id"].duplicated().any(), "user_id duplicado no onboarding"
    print(f"onboarding de contas fora da master (ficam de fora): {(~onb['user_id'].isin(master['user_id'])).sum()}")

    base = master.merge(onb, on="user_id", how="left", validate="one_to_one", indicator=True)
    base["tem_onboarding"] = (base.pop("_merge") == "both").map({True: "sim", False: "nao"})
    base = base.fillna("")
    assert len(base) == len(master), "a junção mudou o número de linhas"
    print(f"após left join: {len(base)} linhas")
    print(base["tem_onboarding"].value_counts().to_string())

    base.to_csv(PROCESSADOS / "usuarios_master_onboarding.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/usuarios_master_onboarding.csv ({len(base)} linhas, {base.shape[1]} colunas)")


if __name__ == "__main__":
    main()
