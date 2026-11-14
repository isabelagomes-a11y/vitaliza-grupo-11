"""Gráficos em PNG do relatório e do mini deck da semana 5 (Word e PowerPoint não leem SVG).

Uso (na raiz do projeto, depois de build_eda.py, build_kmeans.py e entrega/dados.py):
    python src/entrega/graficos.py
Lê saidas/graficos/numeros.json, kmeans.json e entrega.json; grava saidas/graficos/png/.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
G = RAIZ / "saidas" / "graficos"
PNG = G / "png"

INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
MENSAL, ANUAL, CTX, CRIT = "#2a78d6", "#eb6834", "#c3c2b7", "#d03b3b"
SEG = {"A": "#eb6834", "B": "#2a78d6", "C": "#1baf7a", "D": "#eda100"}
plt.rcParams.update({
    "font.family": ["Arial"], "font.size": 10, "text.color": INK, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": .7,
    "axes.axisbelow": True, "figure.facecolor": "white", "axes.facecolor": "white", "axes.titlesize": 11,
    "axes.titlelocation": "left", "axes.titlecolor": INK,
})
br = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")


def salvar(fig, nome):
    PNG.mkdir(parents=True, exist_ok=True)
    fig.savefig(PNG / f"{nome}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def plano_tempo_casa(n):
    faixas = list(n["tempo_casa"]["mensal"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    x = np.arange(len(faixas))
    for i, (plano, cor) in enumerate([("mensal", MENSAL), ("anual", ANUAL)]):
        vals = [n["tempo_casa"][plano][f] for f in faixas]
        pos = x + (i - .5) * .38
        ax.bar(pos, vals, .38, color=cor, label=plano, edgecolor="white", linewidth=1.5)
        for p, v in zip(pos, vals):
            ax.text(p, v + .4, f"{br(v)}%", ha="center", fontsize=8.5)
    ax.axhline(100 * n["base_churn"], color=MUTED, ls="--", lw=1)
    ax.text(len(faixas) - .5, 100 * n["base_churn"] + .5, f"base {br(100 * n['base_churn'])}%", ha="right", fontsize=8, color=INK2)
    ax.set_xticks(x, faixas)
    ax.set_xlabel("tempo de casa em 31/07/2026")
    ax.set_ylabel("saída em 60 dias (%)")
    ax.set_ylim(0, 22)
    ax.legend(frameon=False, loc="upper right")
    salvar(fig, "e1_plano_tempo_casa")


def auc(n):
    itens = sorted(n["auc"].items(), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    cores = [ANUAL if k == "renovação desligada" else (CTX if v < .52 else MENSAL) for k, v in itens]
    ax.barh([k for k, _ in itens], [v for _, v in itens], color=cores, height=.65)
    for y, (_, v) in enumerate(itens):
        ax.text(v + .003, y, br(v, 2), va="center", fontsize=8.5)
    ax.axvline(.5, color=MUTED, ls="--", lw=1)
    ax.set_xlim(.45, .74)
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("AUC de cada variável sozinha (0,50 = acaso)")
    salvar(fig, "e2_auc")


def subida_2026(d):
    meses = ["01", "02", "03", "04", "05", "06", "07", "08", "09"]
    rotulos = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set"]
    s = d["serie_plano"]["mensal"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.3), gridspec_kw={"width_ratios": [1.15, 1]})
    for ano, cor, lw in [("2025", CTX, 2), ("2026", MENSAL, 2.4)]:
        a1.plot(rotulos, [s[f"{ano}-{m}"] for m in meses], color=cor, lw=lw, marker="o", markersize=4, label=ano)
    a1.axvspan(1.6, 6.4, color="#2a78d6", alpha=.06)
    a1.annotate("reajuste\n01/03", (2, 15.2), fontsize=8, color=INK2, ha="center")
    a1.text(3, s["2026-04"] + .5, f"{br(s['2026-04'])}%", ha="center", fontsize=8.5, color=MENSAL)
    a1.set_ylim(5, 16.5)
    a1.set_ylabel("churn do mês (%)")
    a1.set_title("Mensal: 2026 contra 2025, mês a mês")
    a1.legend(frameon=False, loc="lower left")
    r = d["renovacoes_anuais"]
    tri = [x["tri"].replace("Q", " T") for x in r]
    a2.bar(tri, [x["pct_primeira"] for x in r], color=[CTX, CTX] + [ANUAL] * (len(r) - 2), width=.65)
    for i, x in enumerate(r):
        a2.text(i, x["pct_primeira"] + 1.5, f"{x['pct_primeira']:.0f}%", ha="center", fontsize=8.5)
    a2.set_ylim(0, 90)
    a2.set_ylabel("% das renovações que são a 1ª")
    a2.set_title("Anual: a safra de 2024 chega à 1ª renovação")
    a2.tick_params(axis="x", labelsize=8.5)
    fig.tight_layout(w_pad=2.5)
    salvar(fig, "e3_subida_2026")


def segmentos(n):
    cam = n["camadas"]
    acao = {(p["segmento"], p["camada"]): p["acao"] for p in n["priorizacao"]}
    fig, ax = plt.subplots(figsize=(8.8, 3.4))
    x = np.arange(len(cam))
    for i, c in enumerate(cam):
        nc = acao[(c["segmento"], c["camada"])] == "Não contatar"
        ax.bar(i, 100 * c["churn"], .7, color=SEG[c["segmento"]], alpha=.45 if nc else 1, edgecolor="white", linewidth=1.5,
               hatch="//" if nc else None)
        ax.text(i, 100 * c["churn"] + 1.2, f"{br(100 * c['churn'])}%", ha="center", fontsize=9)
    ax.axhline(100 * n["base_churn"], color=MUTED, ls="--", lw=1)
    ax.set_xticks(x, [f"{c['segmento']} · {c['camada']}\nn={c['n']:,}".replace(",", ".") for c in cam], fontsize=8.5)
    ax.set_ylabel("saída em 60 dias (%)")
    ax.set_ylim(0, 78)
    ax.text(len(cam) - .5, 74, "hachurado: anual com pouco uso, não contatar (sorteio de agosto)", ha="right", fontsize=8, color=INK2)
    salvar(fig, "e4_segmentos_camadas")


def campanha(n):
    linhas = [("B · saída", "B · mensal novato"), ("C · saída", "C · mensal veterano"), ("A · saída", "A · anual renovando"),
              ("Anual pouco uso (A+D) · desligou", "Anual pouco uso · desligou a renovação")]
    grupos = [("cupom", ANUAL), ("desafio", MENSAL), ("conteudo", "#1baf7a")]
    rotulo = {"cupom": "cupom", "desafio": "desafio", "conteudo": "conteúdo"}
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    for i, (chave, rot) in enumerate(linhas):
        for j, (g, cor) in enumerate(grupos):
            ef, lo, hi = n["campanha"][chave]["efeitos"][g]
            y = i + (j - 1) * .22
            ax.plot([lo, hi], [y, y], color=cor, lw=2.2, alpha=.85)
            ax.plot(ef, y, "o", color=cor, markersize=6, label=rotulo[g] if i == 0 else None)
    ax.axvline(0, color=INK2, lw=1)
    ax.set_yticks(range(len(linhas)), [r for _, r in linhas])
    ax.invert_yaxis()
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("efeito contra o controle, em pontos (intervalo de 95%) · ← retém   piora →")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(.5, 1.13))
    salvar(fig, "e5_campanha")


def kmeans(k):
    comp = k["comparacao"]
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    nomes = [c["esquema"] for c in comp][::-1]
    vals = [c["auc"] for c in comp][::-1]
    ax.barh(nomes, vals, color=[ANUAL, MENSAL, CTX, CTX], height=.6)
    for y, v in enumerate(vals):
        ax.text(v + .004, y, br(v, 3), va="center", fontsize=8.5)
    ax.axvline(.5, color=MUTED, ls="--", lw=1)
    ax.set_xlim(.45, .93)
    ax.grid(axis="x", color=GRID)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("AUC do esquema de grupos (0,50 = acaso)")
    salvar(fig, "e6_kmeans_regra")


def uso(n):
    faixas = list(n["uso"])
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    vals = [n["uso"][f] for f in faixas]
    ax.bar(faixas, vals, color=[ANUAL] + [MENSAL] * (len(faixas) - 1), width=.65)
    for i, v in enumerate(vals):
        ax.text(i, v + .5, f"{br(v)}%", ha="center", fontsize=9)
    ax.axhline(100 * n["base_churn"], color=MUTED, ls="--", lw=1)
    ax.set_xlabel("treinos por mês (mai–jul/2026)")
    ax.set_ylabel("saída em 60 dias (%)")
    ax.set_ylim(0, 26)
    salvar(fig, "e7_uso")


def main():
    n = json.loads((G / "numeros.json").read_text(encoding="utf-8"))
    k = json.loads((G / "kmeans.json").read_text(encoding="utf-8"))
    d = json.loads((G / "entrega.json").read_text(encoding="utf-8"))
    plano_tempo_casa(n), auc(n), subida_2026(d), segmentos(n), campanha(n), kmeans(k), uso(n)
    print("gravados:", sorted(p.name for p in PNG.glob("*.png")))


if __name__ == "__main__":
    main()
