"""Gera e executa notebooks/segmentacao_kmeans.ipynb (apoio à segmentação da semana 5).

Rodar a partir da raiz do repositório:  .venv/bin/python src/build_kmeans.py
(Windows: .venv\\Scripts\\python src\\build_kmeans.py). Saídas: gráficos SVG e kmeans.json em saidas/graficos/.
"""
import os

import nbformat as nbf
from nbclient import NotebookClient

KERNEL = os.environ.get("VITALIZA_KERNEL", "python3")  # no Windows do grupo: VITALIZA_KERNEL=vitaliza

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

md("""
# Vitaliza · K-means de apoio à segmentação (semana 5)

A segmentação oficial usa regras: 4 segmentos de momento (`src/vitaliza/segmentos.py`) e uma camada de
comportamento também por regra (anual: menos de 2 treinos/mês = pouco uso; mensal: ≥ 50% ao ar livre).
Este notebook mostra **por que** a regra substitui o k-means, com as quatro lentes da aula:
inércia, silhueta, estabilidade e negócio.

O agrupamento usa só comportamento e ciclo conhecidos em 31/07/2026. Ficam de fora o rótulo (quem saiu),
a renovação desligada (decisão já tomada), o valor e a demografia.
""")

code("""
import json, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path.cwd().parent / "src"))
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from vitaliza.base import *
from vitaliza.features import load_all
from vitaliza.segmentos import base_semana5
from vitaliza.kmeans import VARIAVEIS, variaveis, avaliar_k, nomear, camada_kmeans, auc_grupo
from vitaliza.config import SAIDAS
G = SAIDAS / "graficos"; G.mkdir(parents=True, exist_ok=True)
K = {}  # números deste notebook

INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
AZUL, LARANJA, CTX = "#2a78d6", "#eb6834", "#c3c2b7"
plt.rcParams.update({"font.family": ["Helvetica Neue", "Helvetica", "Arial"], "font.size": 9, "text.color": INK,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": .6,
    "axes.axisbelow": True, "figure.facecolor": "none", "axes.facecolor": "none", "lines.linewidth": 2, "svg.fonttype": "none"})
br = lambda v, d=2: f"{v:.{d}f}".replace(".", ",")
def save(fig, nome): fig.savefig(G / f"{nome}.svg", bbox_inches="tight", transparent=True); plt.close(fig)

e = load_eventos(); a = load_assinaturas(); sp = spells(e, a); X = load_all()
b = base_semana5(sp, e, a, X)
v = variaveis(b)
print(f"Base: {len(b):,} assinantes no fim de 31/07; {b.y.sum():,} saíram até 29/09 ({b.y.mean():.1%})")
v.describe().round(2)
""")

md("""
## 1 · Quantos grupos: inércia, silhueta e estabilidade

Variáveis padronizadas (média 0, desvio 1). Estabilidade = ARI médio entre o ajuste na base toda e
10 ajustes em subamostras de 80% (1 = os grupos se repetem; 0 = acaso).
""")
code("""
Z = StandardScaler().fit_transform(v)
lentes = avaliar_k(Z, range(3, 8))
K["lentes"] = lentes.to_dict("records")
fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.1))
for ax, col, tit in zip(axs, ["inercia", "silhueta", "estabilidade_ari"], ["Inércia (cotovelo)", "Silhueta", "Estabilidade (ARI)"]):
    ax.plot(lentes.k, lentes[col], color=AZUL, marker="o", markersize=4)
    ax.scatter([4], lentes.loc[lentes.k == 4, col], color=LARANJA, s=40, zorder=3)
    ax.set_title(tit, fontsize=9, loc="left", color=INK); ax.set_xticks(lentes.k)
fig.tight_layout(); save(fig, "12_kmeans_escolha_k")
lentes
""")

md("""
## 2 · Os grupos do k-means (k = 4) e o churn de cada um, medido depois

Antes, o cuidado da aula: **colunas 0/1 dominam o agrupamento**. Com a queda de uso (0/1) entre as variáveis,
um dos quatro grupos vira só "quem teve queda de uso", misturando anual e mensal. Por isso ela fica fora.
""")
code("""
vq = variaveis(b, com_queda=True)
kq = KMeans(n_clusters=4, n_init=20, random_state=42).fit(StandardScaler().fit_transform(vq))
dominio = vq.assign(grupo=kq.labels_).groupby("grupo")[["queda_uso", "plano_anual"]].mean().round(2)
K["com_queda_binaria"] = dominio.reset_index().to_dict("records")
display(dominio.rename(columns={"queda_uso": "% com queda de uso", "plano_anual": "% anual"}))

km = KMeans(n_clusters=4, n_init=20, random_state=42).fit(Z)
b["cluster"] = nomear(v, km.labels_)
perfil = b.groupby("cluster").agg(n=("y", "size"), churn=("y", "mean"), treinos_mes=("treinos_mes", "median"),
                                  ar_livre=("pct_ar_livre", "mean"), meses_casa=("meses_casa", "median"),
                                  renov_desligada=("renov_desligada", "mean")).round(3)
K["clusters"] = perfil.reset_index().to_dict("records")
perfil
""")

md("""
## 3 · Regra × k-means

Quanto cada esquema separa quem sai (AUC usando o churn do próprio grupo como score; 0,50 = acaso)?
A camada do k-means é o perfil de treino do cluster (ar livre × vídeo); a camada oficial é a regra
(anual: pouco uso × ativo; mensal: ar livre × vídeo).
""")
code("""
b["camada_km"] = camada_kmeans(b["cluster"])
esquemas = {
    "k-means sozinho (4 grupos)": b["cluster"],
    "segmentos de momento (regra)": b["segmento"],
    "segmentos + camada do k-means": b["segmento"] + "|" + b["camada_km"],
    "segmentos + camada por regra (oficial)": b["segmento"] + "|" + b["camada"],
}
comp = pd.DataFrame({"esquema": list(esquemas), "grupos": [s.nunique() for s in esquemas.values()],
                     "auc": [round(auc_grupo(b.y, s), 3) for s in esquemas.values()]})
K["comparacao"] = comp.to_dict("records")

mensal = b[b.plano == "mensal"]
K["concordancia_mensal"] = round(float((mensal["camada"] == mensal["camada_km"]).mean()), 3)
lado = lambda col: b.groupby(["segmento", col]).y.agg(n="size", churn="mean").round(3)
K["camada_regra"] = {f"{s}|{c}": r.to_dict() for (s, c), r in lado("camada").iterrows()}
K["camada_kmeans"] = {f"{s}|{c}": r.to_dict() for (s, c), r in lado("camada_km").iterrows()}

fig, ax = plt.subplots(figsize=(6.4, 2.0))
cores = [CTX, CTX, AZUL, LARANJA]
ax.barh(comp.esquema[::-1], comp.auc[::-1], color=cores[::-1], height=.6)
for y, val in enumerate(comp.auc[::-1]):
    ax.text(val + .004, y, br(val), va="center", fontsize=8.5, color=INK)
ax.axvline(.5, color=MUTED, lw=1, ls=(0, (3, 2))); ax.set_xlim(.45, .95); ax.grid(axis="y", visible=False)
ax.set_xlabel("AUC (0,50 = acaso)")
save(fig, "13_kmeans_vs_regra")
print(f"No mensal, a camada da regra e a do k-means coincidem em {K['concordancia_mensal']:.1%} dos assinantes.")
display(comp); display(lado("camada")); lado("camada_km")
""")

md("""
## 4 · Leitura

- **Nenhum k separa bem.** A silhueta fica entre 0,28 e 0,31 de k = 3 a 7: os grupos são cortes úteis, não tipos
  naturais de cliente. E o **k = 4 é instável**: o ARI médio entre subamostras é 0,67 (mínimo 0,55), contra 0,93 em
  k = 3 e 0,99 em k = 7. Um agrupamento que muda conforme a amostra não serve para operar todo mês.
- **O k-means encontra plano × perfil de treino** (anual ou mensal; ar livre ou vídeo). Sozinho, separa pouco o churn
  (AUC 0,61): não enxerga *quando* o anual pode sair, que é uma regra de calendário (a renovação).
- **No mensal, a regra e o k-means dão a mesma camada** (ar livre × vídeo coincidem em 100% dos assinantes de B e C).
- **No anual, o k-means não acha o que importa.** Dentro do A, a camada do k-means separa 40,5% (ar livre) de 50,3%
  (vídeo); a regra de uso separa **68,2% (pouco uso) de 17,8% (ativo)**. O pouco uso não aparece como grupo porque o
  agrupamento é dominado por plano e perfil de treino.
- **Conclusão:** segmentos de momento + camada por regra separam o máximo (AUC 0,867, contra 0,860 com a camada do
  k-means), são estáveis por construção e simples de explicar e recalcular. O k-means fica como evidência de que a
  regra não perde informação e de por que não foi usado na segmentação oficial.
""")

code("""
(G / "kmeans.json").write_text(json.dumps(K, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
print(json.dumps({k: K[k] for k in ["comparacao", "concordancia_mensal"]}, ensure_ascii=False, indent=1, default=float))
""")

nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
NotebookClient(nb, timeout=1800, kernel_name=KERNEL, resources={"metadata": {"path": "notebooks"}}).execute()
nbf.write(nb, "notebooks/segmentacao_kmeans.ipynb")
print("ok: notebooks/segmentacao_kmeans.ipynb")
