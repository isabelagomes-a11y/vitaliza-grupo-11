"""Base master de usuários: usuarios.csv sem as contas sem data de nascimento ou sexo
e sem as contas com idade impossível.

Uso: python src/usuarios_master.py   (depois de src/limpar_usuarios.py)

Lê dados/processados/usuarios_limpo.csv (usuarios.csv com grafias padronizadas) e grava
em dados/processados/:
- usuarios_master.csv: contas com data_nascimento e sexo preenchidos e idade entre
  IDADE_MIN e IDADE_MAX anos em DATA_REF (ver calcular_idade.py);
- usuarios_removidos.csv: user_id e motivo de cada conta removida.

Decisões registradas em decisoes.md. As marcações de usuarios_limpo.csv (cadastro inválido,
conta duplicada, início antes do cadastro) seguem como colunas, sem filtrar.
"""
import sys
from pathlib import Path

import pandas as pd

from calcular_idade import DATA_REF, IDADE_MAX, IDADE_MIN, idade_em

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
PROCESSADOS = RAIZ / "dados" / "processados"

OBRIGATORIAS = ["data_nascimento", "sexo"]


def main():
    df = pd.read_csv(PROCESSADOS / "usuarios_limpo.csv", dtype=str, keep_default_na=False)
    print(f"usuarios_limpo.csv: {len(df)} linhas")

    falta = pd.DataFrame({col: df[col].str.strip() == "" for col in OBRIGATORIAS})
    master = df
    for col in OBRIGATORIAS:
        antes = len(master)
        master = master[~falta.loc[master.index, col]]
        print(f"filtro {col} preenchido: {antes} -> {len(master)} (-{antes - len(master)})")

    nasc = pd.to_datetime(master["data_nascimento"].str.strip(), format="%Y-%m-%d", errors="raise")
    idade = idade_em(nasc)
    impossivel = ~idade.between(IDADE_MIN, IDADE_MAX)
    antes = len(master)
    master = master[~impossivel]
    print(f"filtro idade entre {IDADE_MIN} e {IDADE_MAX} em {DATA_REF.date()}: {antes} -> {len(master)} "
          f"(-{antes - len(master)}: {(idade < IDADE_MIN).sum()} abaixo, {(idade > IDADE_MAX).sum()} acima)")

    motivo = falta.apply(lambda r: " e ".join(f"sem {c}" for c in OBRIGATORIAS if r[c]), axis=1)
    motivo.loc[impossivel[impossivel].index] = f"idade fora de {IDADE_MIN} a {IDADE_MAX}"
    removidos = pd.DataFrame({"user_id": df["user_id"], "motivo": motivo})
    removidos = removidos[~removidos["user_id"].isin(master["user_id"])]
    print(removidos["motivo"].value_counts().to_string())
    assert len(master) + len(removidos) == len(df)

    PROCESSADOS.mkdir(exist_ok=True)
    master.to_csv(PROCESSADOS / "usuarios_master.csv", index=False, encoding="utf-8")
    removidos.to_csv(PROCESSADOS / "usuarios_removidos.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/usuarios_master.csv ({len(master)} linhas) "
          f"e usuarios_removidos.csv ({len(removidos)} linhas)")


if __name__ == "__main__":
    main()
