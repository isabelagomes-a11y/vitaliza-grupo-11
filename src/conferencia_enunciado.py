"""Confere a reconstrução das assinaturas (src/vitaliza/base.py) contra os números do enunciado.

Uso: python src/conferencia_enunciado.py   (na raiz do projeto)

Grava saidas/conferencia_enunciado.csv. Se algum número não bater, a coluna diferenca mostra
quanto. É a prova de que a base usada na EDA e na segmentação reproduz a série oficial.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vitaliza.base import CORTE, ativos_em, churn_mensal, load_assinaturas, load_eventos, spells  # noqa: E402
from vitaliza.config import SAIDAS  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main():
    e, a = load_eventos(), load_assinaturas()
    sp = spells(e, a)
    print(f"eventos: {len(e)} | assinaturas: {len(a)} | períodos pagos reconstruídos: {len(sp)}")

    linhas = []

    def add(item, esperado, calculado):
        linhas.append({"item": item, "enunciado": esperado, "reconstruido": calculado})

    m = churn_mensal(sp, pd.period_range("2025-01", "2026-09", freq="M").astype(str)).set_index("mes")
    add("ativos no início de jan/2025", 8540, int(m.loc["2025-01", "ativos_inicio"]))
    add("abril/2026: ativos no início", 14237, int(m.loc["2026-04", "ativos_inicio"]))
    add("abril/2026: perdas", 1154, int(m.loc["2026-04", "perdas"]))
    add("abril/2026: churn %", 8.1, round(100 * m.loc["2026-04", "churn"], 1))
    add("setembro/2026: ativos no início", 14319, int(m.loc["2026-09", "ativos_inicio"]))
    add("setembro/2026: churn %", 5.0, round(100 * m.loc["2026-09", "churn"], 1))
    add("agosto/2026: churn %", 5.9, round(100 * m.loc["2026-08", "churn"], 1))
    add("ativos em 30/09/2026 (fim do dia)", 14753, len(ativos_em(sp, CORTE)))
    add("churn médio mensal 2025 %", 5.6, round(100 * m.loc["2025-01":"2025-12", "churn"].mean(), 1))
    add("churn médio mensal jan-set/2026 %", 6.6, round(100 * m.loc["2026-01":"2026-09", "churn"].mean(), 1))
    add("perdas da série mensal jun-set/2026", 3362, int(m.loc["2026-06":"2026-09", "perdas"].sum()))
    fins = sp["fim"].between("2026-06-01", CORTE, inclusive="left").sum()
    add("fins de assinatura jun-set/2026", 3389, int(fins))
    ativos = ativos_em(sp, CORTE)
    add("plano anual em 30/09 (%)", 57, round(100 * (ativos["plano"] == "anual").mean()))
    for canal, pct in [("app_store", 36.6), ("google_play", 33.6), ("web_cartao", 20.3), ("web_pix", 9.5)]:
        add(f"{canal} em 30/09 (%)", pct, round(100 * (ativos["canal"] == canal).mean(), 1))

    t = pd.DataFrame(linhas)
    t["diferenca"] = (t["reconstruido"] - t["enunciado"]).round(1)
    print(t.to_string(index=False))
    print(f"batem exatamente: {(t['diferenca'] == 0).sum()} de {len(t)}")
    por_fim = sp.loc[sp["fim"].notna(), "fim_evento"].value_counts().to_dict()
    print("como os períodos terminam:", por_fim)
    t.to_csv(SAIDAS / "conferencia_enunciado.csv", index=False, encoding="utf-8")
    print("gravado: saidas/conferencia_enunciado.csv")


if __name__ == "__main__":
    main()
