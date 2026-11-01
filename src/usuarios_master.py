"""Base master de usuários: usuarios.csv sem as contas que não têm data de nascimento ou sexo.

Uso: python src/usuarios_master.py

Lê dados/brutos/usuarios.csv (sem alterar) e grava em dados/processados/:
- usuarios_master.csv: contas com data_nascimento e sexo preenchidos;
- usuarios_removidos.csv: user_id e motivo de cada conta removida.

Decisão registrada em decisoes.md. Não corrige mais nada: grafias de sexo, datas de
cadastro posteriores ao corte e o canal "interno" ficam para decisões próprias.
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
PROCESSADOS = RAIZ / "dados" / "processados"

OBRIGATORIAS = ["data_nascimento", "sexo"]


def main():
    df = pd.read_csv(BRUTOS / "usuarios.csv", dtype=str, keep_default_na=False)
    print(f"usuarios.csv: {len(df)} linhas")

    falta = pd.DataFrame({col: df[col].str.strip() == "" for col in OBRIGATORIAS})
    master = df
    for col in OBRIGATORIAS:
        antes = len(master)
        master = master[~falta.loc[master.index, col]]
        print(f"filtro {col} preenchido: {antes} -> {len(master)} (-{antes - len(master)})")

    removidas = falta.any(axis=1)
    motivo = falta[removidas].apply(lambda r: " e ".join(f"sem {c}" for c in OBRIGATORIAS if r[c]), axis=1)
    removidos = pd.DataFrame({"user_id": df.loc[removidas, "user_id"], "motivo": motivo})
    print(removidos["motivo"].value_counts().to_string())
    assert len(master) + len(removidos) == len(df)

    PROCESSADOS.mkdir(exist_ok=True)
    master.to_csv(PROCESSADOS / "usuarios_master.csv", index=False, encoding="utf-8")
    removidos.to_csv(PROCESSADOS / "usuarios_removidos.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/usuarios_master.csv ({len(master)} linhas) "
          f"e usuarios_removidos.csv ({len(removidos)} linhas)")


if __name__ == "__main__":
    main()
