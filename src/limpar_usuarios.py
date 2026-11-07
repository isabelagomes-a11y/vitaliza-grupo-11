"""Limpeza do usuarios.csv: grafias padronizadas, CEP completo e marcações de qualidade.

Uso: python src/limpar_usuarios.py   (depois de src/situacao_assinantes.py)

Lê dados/brutos/usuarios.csv (sem alterar) e grava dados/processados/usuarios_limpo.csv,
com as mesmas linhas. Decisões registradas em decisoes.md:
- sexo: F ou M (vazio continua vazio);
- sistema: ios ou android;
- cidade: nome oficial (36 grafias para 13 cidades; "SP" e "RJ" como cidade viram as capitais);
- cep_prefixo: 3 dígitos, completando o zero à esquerda perdido;
- cadastro_invalido: data_cadastro depois do corte (sim/nao);
- conta_duplicada: mesmo e-mail em mais de uma conta (sim/nao);
- inicio_antes_cadastro: assinatura começa antes do cadastro da conta (sim/nao).
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
PROCESSADOS = RAIZ / "dados" / "processados"

CORTE = pd.Timestamp("2026-10-01")  # primeiro instante depois do corte

SEXO = {"f": "F", "fem": "F", "feminino": "F", "m": "M", "masc": "M", "masculino": "M", "": ""}
SISTEMA = {"ios": "ios", "android": "android"}
CIDADE = {
    "b. horizonte": "Belo Horizonte", "belo horizonte": "Belo Horizonte", "bh": "Belo Horizonte",
    "bsb": "Brasília", "brasilia": "Brasília", "brasília": "Brasília", "brasília - df": "Brasília",
    "florianopolis": "Florianópolis", "florianópolis": "Florianópolis", "floripa": "Florianópolis",
    "rio de janeiro": "Rio de Janeiro", "rio": "Rio de Janeiro", "rj": "Rio de Janeiro",
    "são paulo": "São Paulo", "sao paulo": "São Paulo", "s. paulo": "São Paulo", "sampa": "São Paulo",
    "sp": "São Paulo", "são paulo - sp": "São Paulo",
    "campinas": "Campinas", "curitiba": "Curitiba", "fortaleza": "Fortaleza", "goiânia": "Goiânia",
    "porto alegre": "Porto Alegre", "recife": "Recife", "salvador": "Salvador", "santos": "Santos",
}


def padronizar(df, col, mapa):
    chave = df[col].str.strip().str.lower()
    novo = chave.map(mapa)
    assert novo.notna().all(), f"{col}: valores sem mapeamento {sorted(chave[novo.isna()].unique())}"
    mudou = int((novo != df[col]).sum())
    df[col] = novo
    print(f"{col}: {mudou} linhas alteradas -> {df[col].replace('', '(vazio)').value_counts().to_dict()}")


def main():
    u = pd.read_csv(BRUTOS / "usuarios.csv", dtype=str, keep_default_na=False)
    n = len(u)
    print(f"usuarios.csv: {n} linhas")

    padronizar(u, "sexo", SEXO)
    padronizar(u, "sistema", SISTEMA)
    padronizar(u, "cidade", CIDADE)

    curto = u["cep_prefixo"].str.fullmatch(r"\d{1,2}")
    u.loc[curto, "cep_prefixo"] = u.loc[curto, "cep_prefixo"].str.zfill(3)
    print(f"cep_prefixo: {curto.sum()} completados com zero à esquerda | "
          f"vazios: {(u['cep_prefixo'] == '').sum()} | fora de 3 dígitos: "
          f"{(~u['cep_prefixo'].str.fullmatch(r'\d{3}') & (u['cep_prefixo'] != '')).sum()}")

    cadastro = pd.to_datetime(u["data_cadastro"], format="%Y-%m-%d %H:%M:%S")
    u["cadastro_invalido"] = (cadastro >= CORTE).map({True: "sim", False: "nao"})

    email = u["email"].str.strip().str.lower()
    u["conta_duplicada"] = email.duplicated(keep=False).map({True: "sim", False: "nao"})

    periodos = pd.read_csv(PROCESSADOS / "assinaturas_periodos.csv", usecols=["user_id", "inicio"],
                           parse_dates=["inicio"])
    inicio = u["user_id"].map(periodos.set_index("user_id")["inicio"])
    u["inicio_antes_cadastro"] = (inicio < cadastro.dt.normalize()).map({True: "sim", False: "nao"})

    for col in ["cadastro_invalido", "conta_duplicada", "inicio_antes_cadastro"]:
        print(f"{col}: {u[col].value_counts().to_dict()}")
    assert len(u) == n
    u.to_csv(PROCESSADOS / "usuarios_limpo.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/usuarios_limpo.csv ({len(u)} linhas, {u.shape[1]} colunas)")


if __name__ == "__main__":
    main()
