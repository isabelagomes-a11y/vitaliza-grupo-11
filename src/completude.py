"""Completude de uma base estruturada: percentual de faltantes por coluna e criticidade.

Uso: python src/completude.py <base>        (ex.: onboarding, assinaturas, atividades)

Lê só dados/brutos/<arquivo da base> (sem alterar) e, se a base tem user_id, o user_id de
usuarios.csv para contar contas ausentes. Grava saidas/completude_<base>.csv e .md.

Dois números por coluna:
- vazios: nulo, célula vazia ou só com espaços;
- vazios + sem conteúdo: soma as respostas que não dizem nada, se houver uma lista
  aprovada para a base em src/completude_config.json. Não altera nenhum dado.

A criticidade (alta, média, baixa) e o motivo de cada coluna vêm da mesma configuração;
colunas sem criticidade aprovada saem como "a definir".
"""
import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
SAIDAS = RAIZ / "saidas"
CONFIG = Path(__file__).resolve().parent / "completude_config.json"

# Candidatos a "sem conteúdo": valores curtos e repetidos em colunas com muitos valores distintos.
CANDIDATO_MAX_CHARS = 7
CANDIDATO_MIN_PCT = 0.5
CANDIDATO_MIN_DISTINTOS = 50


def ler_base(arquivo):
    caminho = BRUTOS / arquivo
    if caminho.suffix == ".parquet":
        return pd.read_parquet(caminho)
    return pd.read_csv(caminho, dtype=str, keep_default_na=False)


def texto(serie):
    return serie.astype("string").fillna("").str.strip()


def candidatos_sem_conteudo(df):
    n = len(df)
    achados = {}
    for col in df.columns:
        s = texto(df[col])
        if s.nunique() < CANDIDATO_MIN_DISTINTOS:
            continue
        vc = s[s != ""].str.lower().value_counts()
        vc = vc[(vc.index.str.len() <= CANDIDATO_MAX_CHARS) & (100 * vc / n >= CANDIDATO_MIN_PCT)]
        if len(vc):
            achados[col] = vc
    return achados


def main():
    if len(sys.argv) != 2:
        sys.exit("uso: python src/completude.py <base>")
    base = sys.argv[1]
    config = json.loads(CONFIG.read_text(encoding="utf-8")).get(base, {})
    arquivo = config.get("arquivo")
    if arquivo is None:
        achados = sorted(BRUTOS.glob(f"{base}.*"))
        if len(achados) != 1:
            sys.exit(f"base '{base}' não encontrada em dados/brutos/ (ou ambígua): {achados}")
        arquivo = achados[0].name
    sem_conteudo_lista = set(config.get("sem_conteudo", []))
    criticidade = config.get("criticidade", {})

    df = ler_base(arquivo)
    n = len(df)
    print(f"{arquivo}: {n} linhas, {df.shape[1]} colunas")

    linhas = []
    for col in df.columns:
        s = texto(df[col])
        vazios = int((s == "").sum())
        sem_conteudo = int(s.str.lower().isin(sem_conteudo_lista).sum())
        total = vazios + sem_conteudo
        crit, motivo = criticidade.get(col, ["a definir", ""])
        linhas.append({
            "coluna": col,
            "vazios": vazios,
            "pct_vazios": round(100 * vazios / n, 2),
            "sem_conteudo": sem_conteudo,
            "vazios_mais_sem_conteudo": total,
            "pct_vazios_mais_sem_conteudo": round(100 * total / n, 2),
            "criticidade": crit,
            "motivo": motivo,
        })
    tabela = pd.DataFrame(linhas)
    print(tabela.drop(columns="motivo").to_string(index=False))

    candidatos = candidatos_sem_conteudo(df)
    if candidatos:
        print(f"\ncandidatos a 'sem conteúdo' (até {CANDIDATO_MAX_CHARS} caracteres, >= {CANDIDATO_MIN_PCT}% das linhas):")
        for col, vc in candidatos.items():
            novos = vc[~vc.index.isin(sem_conteudo_lista)]
            print(f"  {col}: " + ", ".join(f"{v!r} ({c})" for v, c in vc.items())
                  + (f"  | fora da lista aprovada: {list(novos.index)}" if len(novos) else ""))

    contas = None
    if "user_id" in df.columns and arquivo != "usuarios.csv":
        usuarios = pd.read_csv(BRUTOS / "usuarios.csv", usecols=["user_id"], dtype=str)
        ausentes = int((~usuarios["user_id"].isin(df["user_id"])).sum())
        contas = (len(usuarios), ausentes, round(100 * ausentes / len(usuarios), 2))
        print(f"usuarios.csv: {contas[0]} contas; sem linha em {arquivo}: {ausentes} ({contas[2]}%)")

    SAIDAS.mkdir(exist_ok=True)
    tabela.to_csv(SAIDAS / f"completude_{base}.csv", index=False, encoding="utf-8")

    md = [
        f"# Completude do {arquivo}",
        "",
        f"Base: `dados/brutos/{arquivo}`, {n} linhas. Gerado por `src/completude.py {base}`.",
        "",
        "- **Vazios:** nulo, célula vazia ou só com espaços.",
    ]
    if sem_conteudo_lista:
        md += ["- **Sem conteúdo:** " + ", ".join(f'"{v}"' for v in sorted(sem_conteudo_lista)) + ".",
               "  Critério proposto, ainda não registrado como decisão de limpeza."]
    md += [
        "",
        "| Coluna | Vazios | % vazios | Vazios + sem conteúdo | % | Criticidade |",
        "|---|---|---|---|---|---|",
    ]
    for r in linhas:
        md.append(f"| `{r['coluna']}` | {r['vazios']} | {r['pct_vazios']}% | "
                  f"{r['vazios_mais_sem_conteudo']} | {r['pct_vazios_mais_sem_conteudo']}% | {r['criticidade']} |")
    md += ["", "## Justificativa", ""]
    md += [f"- **`{r['coluna']}` ({r['criticidade']}):** {r['motivo'] or 'a definir.'}" for r in linhas]
    if contas:
        md += [
            "",
            "## Contas sem linha nesta base",
            "",
            f"{contas[1]} das {contas[0]} contas de `usuarios.csv` ({contas[2]}%) não têm linha em `{arquivo}`. "
            + config.get("nota_contas", "A avaliar."),
        ]
    md += [
        "",
        "Critérios de criticidade: **alta**, a falta pode afetar uma decisão de negócio; **média**, dá para inferir, "
        "mas a inferência pode levar a uma direção equivocada; **baixa**, dá para seguir com menos detalhe.",
        "",
    ]
    (SAIDAS / f"completude_{base}.md").write_text("\n".join(md), encoding="utf-8")
    print(f"gravado: saidas/completude_{base}.csv e saidas/completude_{base}.md")


if __name__ == "__main__":
    main()
