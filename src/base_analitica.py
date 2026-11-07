"""Base analítica: uma linha por assinante de 31/07/2026 com todas as variáveis.

Uso: python src/base_analitica.py
     (depois de base_assinantes, variaveis_uso, variaveis_eventos, variaveis_valor e limpar_usuarios)

Junta por user_id, partindo de dados/processados/assinantes_ref.csv, e confere que o número
de assinantes não muda em nenhuma junção. Decisões registradas em decisoes.md:
- idade_ref: idade em anos completos na data de referência (31/07/2026); vazia quando falta
  data de nascimento ou a idade sai de 0 a 100;
- dias_semana_pretendidos: dias_por_semana do onboarding como número ("3x", "3 vezes" → 3;
  "todos" → 7); vazio quando não respondeu;
- grupo_campanha: grupo sorteado em 10/08/2026, só como controle (a campanha caiu dentro da
  janela do churn); vazio para quem não foi sorteado.

Grava dados/processados/base_analitica.csv.
"""
import sys
from pathlib import Path

import pandas as pd

from base_assinantes import DATA_REF
from calcular_idade import IDADE_MAX, IDADE_MIN, idade_em

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
PROCESSADOS = RAIZ / "dados" / "processados"

COLUNAS_USUARIO = ["user_id", "canal_aquisicao", "relogio_conectado", "sistema", "uf", "sexo",
                   "data_nascimento", "conta_duplicada"]


def dias_pretendidos(serie):
    texto = serie.str.strip().str.lower()
    numero = texto.str.extract(r"^(\d)\s*(?:x|vezes)?$")[0].astype(float)
    numero[texto == "todos"] = 7
    nao_lido = (texto != "") & numero.isna()
    assert not nao_lido.any(), f"dias_por_semana sem regra: {sorted(texto[nao_lido].unique())}"
    return numero


def juntar(base, outra, nome):
    antes = len(base)
    junta = base.merge(outra, on="user_id", how="left", validate="one_to_one", indicator=True)
    sem = int((junta.pop("_merge") == "left_only").sum())
    assert len(junta) == antes, f"{nome}: a junção mudou o número de assinantes"
    print(f"+ {nome}: {antes} -> {len(junta)} linhas | assinantes sem linha em {nome}: {sem}")
    return junta


def main():
    base = pd.read_csv(PROCESSADOS / "assinantes_ref.csv")
    print(f"assinantes_ref: {len(base)} linhas")
    for nome in ["variaveis_uso", "variaveis_eventos", "variaveis_valor"]:
        base = juntar(base, pd.read_csv(PROCESSADOS / f"{nome}.csv"), nome)

    usuarios = pd.read_csv(PROCESSADOS / "usuarios_limpo.csv", dtype=str, keep_default_na=False,
                           usecols=COLUNAS_USUARIO)
    nasc = pd.to_datetime(usuarios["data_nascimento"].replace("", None), format="%Y-%m-%d")
    idade = idade_em(nasc, DATA_REF.normalize())
    usuarios["idade_ref"] = idade.where(idade.between(IDADE_MIN, IDADE_MAX))
    base = juntar(base, usuarios.drop(columns="data_nascimento"), "usuarios_limpo")
    print(f"  idade_ref vazia: {base['idade_ref'].isna().sum()} | sexo vazio: {(base['sexo'] == '').sum()}")

    onb = pd.read_csv(BRUTOS / "onboarding.csv", dtype=str, keep_default_na=False,
                      usecols=["user_id", "nivel", "dias_por_semana"])
    onb["dias_semana_pretendidos"] = dias_pretendidos(onb.pop("dias_por_semana"))
    base = juntar(base, onb, "onboarding")
    print(f"  dias_semana_pretendidos vazio: {base['dias_semana_pretendidos'].isna().sum()} | "
          f"nivel vazio: {(base['nivel'].fillna('') == '').sum()}")

    camp = pd.read_csv(BRUTOS / "campanha_ago26.csv", dtype=str, keep_default_na=False, usecols=["user_id", "grupo"])
    base = juntar(base, camp.rename(columns={"grupo": "grupo_campanha"}), "campanha_ago26")
    print("  grupo_campanha:", base["grupo_campanha"].fillna("(não sorteado)").value_counts().to_dict())

    base.to_csv(PROCESSADOS / "base_analitica.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/base_analitica.csv ({len(base)} linhas, {base.shape[1]} colunas)")


if __name__ == "__main__":
    main()
