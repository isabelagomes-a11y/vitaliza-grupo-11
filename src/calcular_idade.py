"""Calcula a idade a partir de data_nascimento na base master com onboarding.

Uso: python src/calcular_idade.py   (depois de src/juntar_onboarding.py)

Idade em anos completos na data de referência (DATA_REF): quem ainda não fez aniversário
no ano conta um a menos. Mantém data_nascimento e grava a coluna idade em
dados/processados/usuarios_master_onboarding.csv.

Idades impossíveis (< 0 ou > 100) já saem da base em src/usuarios_master.py; aqui o
script só confere que não sobrou nenhuma.
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO = RAIZ / "dados" / "processados" / "usuarios_master_onboarding.csv"

DATA_REF = pd.Timestamp("2026-11-01")
IDADE_MIN, IDADE_MAX = 0, 100


def idade_em(nasc, ref=DATA_REF):
    """Idade em anos completos na data ref; nasc é uma série datetime."""
    ainda_nao_fez = (nasc.dt.month > ref.month) | ((nasc.dt.month == ref.month) & (nasc.dt.day > ref.day))
    return ref.year - nasc.dt.year - ainda_nao_fez.astype(int)


def main():
    base = pd.read_csv(ARQUIVO, dtype=str, keep_default_na=False)
    n = len(base)
    print(f"usuarios_master_onboarding.csv: {n} linhas, {base.shape[1]} colunas")

    nasc = pd.to_datetime(base["data_nascimento"].str.strip(), format="%Y-%m-%d", errors="raise")
    idade = idade_em(nasc)

    base = base.drop(columns="idade", errors="ignore")
    base.insert(base.columns.get_loc("data_nascimento") + 1, "idade", idade)
    assert len(base) == n

    print(f"idade em {DATA_REF.date()}: mín {idade.min()}, mediana {idade.median():.0f}, máx {idade.max()}")
    print(f"impossíveis: < {IDADE_MIN}: {(idade < IDADE_MIN).sum()} | > {IDADE_MAX}: {(idade > IDADE_MAX).sum()}")
    assert idade.between(IDADE_MIN, IDADE_MAX).all(), "há idades impossíveis; rode src/usuarios_master.py"

    base.to_csv(ARQUIVO, index=False, encoding="utf-8")
    print(f"gravado: {ARQUIVO.relative_to(RAIZ).as_posix()} ({len(base)} linhas, {base.shape[1]} colunas)")


if __name__ == "__main__":
    main()
