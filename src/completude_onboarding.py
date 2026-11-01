"""Completude do onboarding.csv: percentual de faltantes por coluna e criticidade.

Lê dados/brutos/onboarding.csv (sem alterar) e usuarios.csv (só user_id, para contar
contas sem questionário). Grava saidas/completude_onboarding.csv e .md.

Dois números por coluna:
- vazios: célula vazia ou só com espaços;
- vazios + sem conteúdo: soma as respostas que não dizem nada (SEM_CONTEUDO).
  Esse critério ainda não foi aprovado como decisão de limpeza; não altera nenhum dado.
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
SAIDAS = RAIZ / "saidas"

SEM_CONTEUDO = {"nada", "😂", ".", "x", "sla", "kkkk", "asdf", "nao sei", "ok", "-"}

CRITICIDADE = {
    "onboarding_id": ("baixa", "Identificador da resposta; nenhuma decisão depende dele."),
    "user_id": ("alta", "Chave que liga o questionário a assinaturas e treinos; sem ela a linha não serve. Está completa, sem duplicados."),
    "respondido_em": ("média", "Garante que só entra informação anterior ao corte (vai de 01/09/2020 a 30/09/2026). Está completa."),
    "objetivo_texto": ("média", "Base da extração com IA e da mensagem personalizada. Dá para decidir quem contatar pelo comportamento, mas tratar 'asdf' ou '😂' como objetivo desviaria a extração. Sugestão: marcar como 'não informado', sem imputar."),
    "como_conheceu": ("baixa", "usuarios.csv já traz canal_aquisicao, estruturado e atribuído pelo marketing; o texto livre só acrescenta detalhe."),
    "nivel": ("média", "Inferível em parte por ritmo e frequência em atividades.parquet, mas nível declarado e real podem divergir; errar muda tom e oferta da mensagem."),
    "dias_por_semana": ("média", "A diferença entre intenção e uso real é candidata a sinal de saída; sem a intenção, sobra só o uso. Fora os vazios, tem 23 grafias ('3', '3x', '3 vezes', 'todos'): padronização, não falta."),
}


def main():
    df = pd.read_csv(BRUTOS / "onboarding.csv", dtype=str, keep_default_na=False)
    n = len(df)
    print(f"onboarding.csv: {n} linhas, {df.shape[1]} colunas")

    linhas = []
    for col in df.columns:
        s = df[col].str.strip()
        vazios = int((s == "").sum())
        sem_conteudo = int(s.str.lower().isin(SEM_CONTEUDO).sum())
        total = vazios + sem_conteudo
        crit, motivo = CRITICIDADE[col]
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

    usuarios = pd.read_csv(BRUTOS / "usuarios.csv", usecols=["user_id"], dtype=str)
    sem_onb = int((~usuarios["user_id"].isin(df["user_id"])).sum())
    pct_sem_onb = round(100 * sem_onb / len(usuarios), 2)
    print(f"usuarios.csv: {len(usuarios)} contas; sem questionário: {sem_onb} ({pct_sem_onb}%)")

    SAIDAS.mkdir(exist_ok=True)
    tabela.to_csv(SAIDAS / "completude_onboarding.csv", index=False, encoding="utf-8")

    md = [
        "# Completude do onboarding.csv",
        "",
        f"Base: `dados/brutos/onboarding.csv`, {n} linhas. Gerado por `src/completude_onboarding.py`.",
        "",
        "- **Vazios:** célula vazia ou só com espaços.",
        "- **Sem conteúdo:** " + ", ".join(f'"{v}"' for v in sorted(SEM_CONTEUDO)) + ".",
        "  Critério proposto, ainda não registrado como decisão de limpeza.",
        "",
        "| Coluna | Vazios | % vazios | Vazios + sem conteúdo | % | Criticidade |",
        "|---|---|---|---|---|---|",
    ]
    for r in linhas:
        md.append(f"| `{r['coluna']}` | {r['vazios']} | {r['pct_vazios']}% | "
                  f"{r['vazios_mais_sem_conteudo']} | {r['pct_vazios_mais_sem_conteudo']}% | {r['criticidade']} |")
    md += ["", "## Justificativa", ""]
    md += [f"- **`{r['coluna']}` ({r['criticidade']}):** {r['motivo']}" for r in linhas]
    md += [
        "",
        "## Contas sem questionário",
        "",
        f"{sem_onb} das {len(usuarios)} contas de `usuarios.csv` ({pct_sem_onb}%) não têm linha no onboarding. "
        "O dicionário não explica por quê. Criticidade baixa por ora; a reavaliar se se concentrarem em pagantes.",
        "",
        "Critérios de criticidade: **alta**, a falta pode afetar uma decisão de negócio; **média**, dá para inferir, "
        "mas a inferência pode levar a uma direção equivocada; **baixa**, dá para seguir com menos detalhe.",
        "",
    ]
    (SAIDAS / "completude_onboarding.md").write_text("\n".join(md), encoding="utf-8")
    print("gravado: saidas/completude_onboarding.csv e saidas/completude_onboarding.md")


if __name__ == "__main__":
    main()
