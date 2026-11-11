"""Gera e executa notebooks/eda.ipynb (EDA da semana 5).

Rodar a partir da raiz do repositório:  .venv/bin/python src/build_eda.py
Saídas: gráficos SVG e numeros.json em saidas/graficos/.
"""
import nbformat as nbf
from nbclient import NotebookClient

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

md("""
# Vitaliza · EDA (semana 5)

Carrega, limpa e visualiza o data room; mostra padrões e correlações com o churn; sustenta a segmentação
e gera todos os gráficos do relatório e do mini deck.

**Base:** assinaturas pagas ativas no fim de 31/07/2026. **Rótulo:** saiu até 29/09/2026 (60 dias).
Decisões do grupo de 07/11: anual com pouco uso não é contatado; idade e sexo não entram como variável nem gatilho.
""")

code("""
import json, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path.cwd().parent / "src"))
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score
from vitaliza.base import *
from vitaliza.features import *
from vitaliza.segmentos import *
from vitaliza.config import SAIDAS
OUT = G = SAIDAS / "graficos"; G.mkdir(parents=True, exist_ok=True)
N = {}  # números usados no relatório

INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
MENSAL, ANUAL, ANDROID, IOS = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6"
CRIT, GOOD, WARN, CTX = "#d03b3b", "#0ca30c", "#fab219", "#c3c2b7"
SEG = {"A": ANUAL, "B": MENSAL, "C": "#1baf7a", "D": "#eda100"}
plt.rcParams.update({"font.family": ["Helvetica Neue", "Helvetica", "Arial"], "font.size": 9, "text.color": INK,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": .6,
    "axes.axisbelow": True, "figure.facecolor": "none", "axes.facecolor": "none", "lines.linewidth": 2, "svg.fonttype": "none"})
br = lambda v, d=1: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
pctfmt = lambda ax, axis="y": (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
def save(fig, nome): fig.savefig(G / f"{nome}.svg", bbox_inches="tight", transparent=True); plt.close(fig)
""")

md("## 1 · Carga, limpeza e conciliação")
code("""
e = load_eventos(); a = load_assinaturas(); sp = spells(e, a); X = load_all()
pg_raw = pd.read_csv(D + "pagamentos.csv", dtype=str)
N["cobrancas_duplicadas"] = int(pg_raw.duplicated(["user_id", "data_hora", "valor", "status", "tentativa"]).sum())
N["eventos_utc"] = float(e.data_hora.str.endswith("Z").mean())
ch = churn_mensal(sp, pd.date_range("2025-01-01", "2026-09-01", freq="MS"))
conc = pd.DataFrame({
    "enunciado": ["14.753", "8.540", "1.154 · 8,1%", "14.319", "5,6% · 6,6%"],
    "reconstruído": [f"{len(ativos_em(sp, CORTE)):,}".replace(",", "."), f"{ch.ativos_inicio[0]:,}".replace(",", "."),
                     f"{ch.set_index('mes').loc['2026-04','perdas']:,} · {br(ch.set_index('mes').loc['2026-04','churn']*100)}%".replace(",", ".", 1),
                     f"{ch.set_index('mes').loc['2026-09','ativos_inicio']:,}".replace(",", "."),
                     f"{br(ch[ch.mes<'2026'].churn.mean()*100)}% · {br(ch[ch.mes>='2026'].churn.mean()*100)}%"]},
    index=["Ativos em 30/09/2026", "Ativos no início de jan/2025", "Abril/2026: perdas · churn", "Ativos no início de set/2026", "Churn médio 2025 · jan–set/2026"])
print(N); conc
""")

code("""
b = base_semana5(sp, e, a, X)
N["base_n"] = len(b); N["base_saidas"] = int(b.y.sum()); N["base_churn"] = float(b.y.mean())
print(f"Base: {len(b):,} assinantes no fim de 31/07; {b.y.sum():,} saíram até 29/09 ({b.y.mean():.1%})")
""")

md("## 2 · Churn mensal e por que subiu em 2026")
code("""
fig, ax = plt.subplots(figsize=(7.2, 2.4))
cols = [CTX] * 12 + [INK2] * 9; cols[15] = CRIT
ax.bar(range(len(ch)), ch.churn * 100, color=cols, width=.72)
ax.axhline(5.6, color=MUTED, lw=1, ls=(0, (3, 2))); ax.text(-.4, 5.75, "média 2025: 5,6%", fontsize=8, color=INK2)
ax.plot([11.6, 20.4], [6.6, 6.6], color=INK, lw=1, ls=(0, (3, 2))); ax.text(11.6, 8.9, "média 2026: 6,6% (tracejado)", fontsize=8)
ax.text(15, ch.churn[15] * 100 + .15, "8,1%", ha="center", color=CRIT, fontsize=8, fontweight="bold")
MES = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}
ax.set_xticks(range(len(ch))); ax.set_xticklabels([f"{MES[int(m[5:])]}/{m[2:4]}" for m in ch.mes], rotation=90, fontsize=7.5)
ax.set_ylim(0, 9.5); pctfmt(ax); ax.grid(axis="x", visible=False); save(fig, "01_churn_mensal")

rows = []
for m in pd.date_range("2025-01-01", "2026-09-01", freq="MS"):
    t1 = m + pd.offsets.MonthBegin(1); at = ativos_em(sp, m)
    rows.append(at.assign(l=at.fim.notna() & (at.fim < t1)).groupby("plano").l.agg(["mean", "size"]).stack().rename(m))
cp = pd.DataFrame(rows); taxa = cp.xs("mean", axis=1, level=1); peso = cp.xs("size", axis=1, level=1); peso = peso.div(peso.sum(1), axis=0)
c25, c26 = taxa.loc[:"2025-12"].mean(), taxa.loc["2026-01":].mean(); s25, s26 = peso.loc[:"2025-12"].mean(), peso.loc["2026-01":].mean()
dec = {"mensal": s25["mensal"] * (c26["mensal"] - c25["mensal"]) * 100, "anual": s25["anual"] * (c26["anual"] - c25["anual"]) * 100,
       "mix": ((s26 - s25) * c26).sum() * 100}
pre, pos = taxa.loc["2025-09":"2026-02"].mean(), taxa.loc["2026-03":"2026-05"].mean()
N["decomp"] = dec; N["did_preco"] = float(((pos["mensal"] - pre["mensal"]) - (pos["anual"] - pre["anual"])) * 100)
N["pico_mensal_abr"] = float(taxa.loc["2026-04-01", "mensal"])
steps = [("Churn\\n2025", 5.62, "b"), ("Mensais\\nsaindo mais", dec["mensal"], ""), ("Anuais\\nsaindo mais", dec["anual"], ""),
         ("Mais anuais\\nna base", dec["mix"], ""), ("Churn\\n2026", 6.62, "b")]
fig, ax = plt.subplots(figsize=(5.6, 2.5)); run = 0
for i, (n, v, k) in enumerate(steps):
    if k == "b":
        ax.bar(i, v, color=INK2, width=.6); ax.text(i, v + .04, f"{br(v)}%", ha="center", fontsize=8.5, fontweight="bold"); run = v
    else:
        ax.bar(i, abs(v), bottom=run if v > 0 else run + v, color=CRIT if v > 0 else GOOD, width=.6)
        ax.text(i, run + max(v, 0) + .04, f"{v:+.2f} pp".replace(".", ","), ha="center", fontsize=8.5); run += v
ax.set_xticks(range(5)); ax.set_xticklabels([s[0] for s in steps], fontsize=8); ax.set_ylim(5, 7.1)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.1f}%".replace(".", ","))); ax.grid(axis="x", visible=False)
save(fig, "02_decomposicao")

u = X["u"].set_index("user_id"); rows = []
for m in pd.date_range("2026-01-01", "2026-09-01", freq="MS"):
    t1 = m + pd.offsets.MonthBegin(1); at = ativos_em(sp, m).copy(); at["s"] = at.user_id.map(u.sistema)
    rows.append(at.assign(l=at.fim.notna() & (at.fim < t1)).groupby("s").l.mean().rename(m))
cs = pd.DataFrame(rows) * 100; N["android_gap_junjul"] = float((cs.android - cs.ios).loc["2026-06":"2026-07"].mean())
fig, ax = plt.subplots(figsize=(5.6, 2.3)); x = np.arange(len(cs))
ax.axvspan(3.5, 5.5, color=WARN, alpha=.18, lw=0); ax.text(4.5, 9.2, "GPS falhando\\nno Android", ha="center", fontsize=7.5, color=INK2)
ax.plot(x, cs.android, color=ANDROID, marker="o", ms=3.5); ax.plot(x, cs.ios, color=IOS, marker="o", ms=3.5)
ax.text(8.15, cs.android.iloc[-1] + .35, " Android", fontsize=8.5); ax.text(8.15, cs.ios.iloc[-1] - .35, " iOS", fontsize=8.5)
ax.text(5.5, 6.3, "+2,4 pp", fontsize=8.5, color=CRIT, fontweight="bold", ha="center")
ax.set_xticks(x); ax.set_xticklabels([MES[m.month] for m in cs.index], fontsize=8); pctfmt(ax); ax.set_ylim(3, 10.2); ax.set_xlim(-.4, 9.4)
ax.grid(axis="x", visible=False); save(fig, "03_android_ios")
N
""")

md("## 3 · O que separa quem sai")
code("""
# churn por plano e tempo de casa
fx = pd.cut(np.floor(b.meses_casa), [-1, 1, 5, 11, 23, 1e9], labels=["0–1 mês", "2–5 meses", "6–11 meses", "12–23 meses", "24+ meses"])
tc = b.groupby([fx, "plano"]).y.mean().unstack() * 100
fig, ax = plt.subplots(figsize=(6.2, 2.6)); xx = np.arange(len(tc))
for j, (pl, cor) in enumerate([("mensal", MENSAL), ("anual", ANUAL)]):
    ax.bar(xx + (j - .5) * .38, tc[pl], width=.36, color=cor, label=pl)
    for xi, v in zip(xx, tc[pl]): ax.text(xi + (j - .5) * .38, v + .4, f"{br(v)}%", ha="center", fontsize=7.5)
ax.axhline(b.y.mean() * 100, color=MUTED, lw=1, ls=(0, (3, 2)))
ax.set_xticks(xx); ax.set_xticklabels(tc.index, fontsize=8); pctfmt(ax); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5)); ax.legend(frameon=False, fontsize=8); ax.grid(axis="x", visible=False)
ax.set_ylabel("saída em 60 dias"); save(fig, "04_plano_tempo_casa")
N["tempo_casa"] = tc.round(1).to_dict()

# churn por uso
fu = pd.cut(b.treinos_mes, [-.1, 0, 2, 4, 8, 1e9], labels=["0", "até 2", "2–4", "4–8", "8+"])
uu = b.groupby(fu).y.agg(["mean", "size"]); N["uso"] = (uu["mean"] * 100).round(1).to_dict()
fig, ax = plt.subplots(figsize=(4.4, 2.4))
ax.bar(range(len(uu)), uu["mean"] * 100, color=[CRIT] + [INK2] * 3 + [GOOD], width=.6)
for i, v in enumerate(uu["mean"] * 100): ax.text(i, v + .4, f"{br(v)}%", ha="center", fontsize=8)
ax.set_xticks(range(len(uu))); ax.set_xticklabels(uu.index); ax.set_xlabel("treinos por mês (mai–jul)"); pctfmt(ax); ax.grid(axis="x", visible=False)
save(fig, "05_uso")

# renovação desligada
rd = b.groupby("renov_desligada").y.mean() * 100
N["renov_desl_churn"] = float(rd[1]); N["renov_ligada_churn"] = float(rd[0]); N["renov_desl_share_saidas"] = float(b[b.y == 1].renov_desligada.mean())

# AUC de cada variável sozinha
f = snapshot(REF, sp, e, a, X); f = f.join(text_features(REF, f, X))
f = f.join(b[["treinos_mes", "queda_uso", "meses_casa"]])
cand = {"renovação desligada": "renov_desligada", "treinos/mês": "treinos_mes", "dias ativos (julho)": "dias_ativos_m1",
        "sessões no app (julho)": "sessoes_app_m1", "dias desde o último treino": "dias_desde_treino", "queda de uso": "queda_uso",
        "post de meta cumprida": "post_meta_cumprida", "plano mensal": "mensal", "tempo de casa": "meses_casa",
        "chamado de GPS": "ticket_gps", "seguidores": "seguidores", "relógio conectado": "relogio", "Android": "android",
        "idade": "idade", "mulher": "mulher"}
auc = {}
for nome, c in cand.items():
    v = f[c].fillna(f[c].median()); s = roc_auc_score(f.y, v); auc[nome] = max(s, 1 - s)
auc = pd.Series(auc).sort_values(); N["auc"] = auc.round(3).to_dict()
fig, ax = plt.subplots(figsize=(5.6, 3.2))
cor = [CTX if k in ("idade", "mulher") else (CRIT if k == "renovação desligada" else INK2) for k in auc.index]
ax.barh(range(len(auc)), auc, color=cor, height=.6); ax.axvline(.5, color=MUTED, lw=1, ls=(0, (3, 2)))
for i, v in enumerate(auc): ax.text(v + .003, i, br(v, 2), va="center", fontsize=7.5)
ax.set_yticks(range(len(auc))); ax.set_yticklabels(auc.index, fontsize=8); ax.set_xlim(.45, .75); ax.tick_params(axis="y", length=0)
ax.set_xlabel("AUC da variável sozinha (0,50 = acaso)"); ax.grid(axis="y", visible=False); save(fig, "06_auc_variaveis")
auc.round(3)
""")

md("## 4 · Segmentos de momento + camada de comportamento, com sinais de texto")
code("""
order = ["A", "B", "C", "D"]
sg = b.groupby("segmento").agg(n=("y", "size"), churn=("y", "mean"), saidas=("y", "sum"), valor=("valor_mes", "mean"),
                               treinos=("treinos_mes", "mean"), meses=("meses_casa", "median"),
                               renov_desl=("renov_desligada", "mean"), loja=("canal", lambda s: s.isin(["app_store", "google_play"]).mean()))
sg["pct_saidas"] = sg.saidas / b.y.sum()
sg["receita_risco_ano"] = b.assign(r=b.valor_mes * 12 * b.y).groupby("segmento").r.sum()
sg["resto_churn"] = [b[b.segmento != s].y.mean() for s in sg.index]
N["segmentos"] = sg.round(4).reset_index().to_dict("records")

fig, ax = plt.subplots(figsize=(6.2, 2.5))
ax.bar(range(4), sg.loc[order, "churn"] * 100, color=[SEG[s] for s in order], width=.6)
for i, s in enumerate(order):
    ax.text(i, sg.loc[s, "churn"] * 100 + 1, f"{br(sg.loc[s,'churn']*100)}%", ha="center", fontsize=9, fontweight="bold")
    ax.text(i, sg.loc[s, "churn"] * 100 + 5.5, f"{sg.loc[s,'pct_saidas']:.0%} das saídas", ha="center", fontsize=7.5, color=INK2)
ax.axhline(b.y.mean() * 100, color=MUTED, lw=1, ls=(0, (3, 2))); ax.text(3.45, b.y.mean() * 100 + .6, f"base {br(b.y.mean()*100)}%", fontsize=7.5, color=INK2, ha="right")
ax.set_xticks(range(4)); ax.set_xticklabels([f"{s}\\n{sg.loc[s,'n']:,} pessoas".replace(",", ".") for s in order], fontsize=8)
pctfmt(ax); ax.set_ylim(0, 58); ax.grid(axis="x", visible=False); save(fig, "07_segmentos")

cam = b.groupby(["segmento", "camada"]).agg(n=("y", "size"), churn=("y", "mean"), valor=("valor_mes", "mean"), renov=("renov_desligada", "mean"))
N["camadas"] = cam.round(4).reset_index().to_dict("records")
fig, ax = plt.subplots(figsize=(6.6, 2.6)); labels = []; i = 0
for s in order:
    for c in cam.loc[s].index:
        v = cam.loc[(s, c), "churn"] * 100
        nc = (s in ("A", "D") and c == "pouco uso")
        ax.bar(i, v, color=SEG[s], width=.7, alpha=.45 if nc else 1, hatch="///" if nc else None, edgecolor="white" if nc else None)
        ax.text(i, v + 1, f"{br(v)}%", ha="center", fontsize=7.5); labels.append(f"{s} · {c}\\nn={cam.loc[(s,c),'n']:,}".replace(",", ".")); i += 1
ax.set_xticks(range(i)); ax.set_xticklabels(labels, fontsize=7); pctfmt(ax); ax.set_ylim(0, 80); ax.grid(axis="x", visible=False)
save(fig, "08_camadas")

sig = b.groupby(["segmento", "meta_cumprida"]).y.mean().unstack() * 100
sig2 = b.groupby(["segmento", "queda_uso"]).y.mean().unstack() * 100
N["meta_cumprida"] = sig.round(1).to_dict(); N["queda_uso"] = sig2.round(1).to_dict()
N["meta_share"] = b.groupby("segmento").meta_cumprida.mean().round(3).to_dict()
fig, ax = plt.subplots(figsize=(5.6, 2.4)); xx = np.arange(3)
for j, (k, lab, cor) in enumerate([(0, "não postou", CTX), (1, "postou \\"meta cumprida\\"", CRIT)]):
    vals = sig.loc[["A", "B", "C"], k]; ax.bar(xx + (j - .5) * .38, vals, width=.36, color=cor, label=lab)
    for xi, v in zip(xx, vals): ax.text(xi + (j - .5) * .38, v + 1, f"{br(v,0)}%", ha="center", fontsize=8)
ax.set_xticks(xx); ax.set_xticklabels(["A", "B", "C"]); pctfmt(ax); ax.legend(frameon=False, fontsize=8); ax.set_ylim(0, 72); ax.grid(axis="x", visible=False)
save(fig, "09_meta_cumprida")
sg.loc[order].round(3)
""")

md("## 5 · Campanha de agosto por segmento (o que o sorteio mostra)")
code("""
T0 = pd.Timestamp("2026-08-10 10:00")
bc = base_semana5(sp, e, a, X, ref=T0, fim=CORTE)
camp = pd.read_csv(D + "campanha_ago26.csv", dtype=str).set_index("user_id").join(bc[["segmento", "camada", "plano"]], how="inner")
spu = sp.sort_values("ini").drop_duplicates("user_id", keep="last").set_index("user_id")
camp["saiu"] = (spu.fim.reindex(camp.index).notna() & (spu.fim.reindex(camp.index) < CORTE)).astype(int)
ra = e[(e.evento == "renovacao_automatica_desligada") & (e.ts >= T0)].user_id.unique()
camp["desligou"] = camp.index.isin(ra).astype(int)
def efeito(d, y):
    k = d[d.grupo == "controle"][y]; r = {}
    for g in ["desafio", "cupom", "conteudo"]:
        t = d[d.grupo == g][y]; dd = t.mean() - k.mean(); se = np.sqrt(t.var() / len(t) + k.var() / len(k))
        r[g] = (dd * 100, (dd - 1.96 * se) * 100, (dd + 1.96 * se) * 100)
    return r, k.mean() * 100
grupos = [("B · saída", camp.segmento == "B", "saiu"), ("C · saída", camp.segmento == "C", "saiu"),
          ("A · saída", camp.segmento == "A", "saiu"),
          ("Anual pouco uso (A+D) · desligou", (camp.plano == "anual") & (camp.camada == "pouco uso"), "desligou")]
res = {nome: efeito(camp[m], y) for nome, m, y in grupos}
N["campanha"] = {k: {"efeitos": {g: [round(x, 2) for x in v] for g, v in r.items()}, "controle": round(c, 1)} for k, (r, c) in res.items()}
fig, ax = plt.subplots(figsize=(6.8, 2.9)); yy = 0; ticks = []
for nome, (r, _) in res.items():
    for j, (g, gl) in enumerate([("desafio", "Desafio"), ("cupom", "Cupom"), ("conteudo", "Conteúdo")]):
        d, lo, hi = r[g]; sig_ = hi < 0 or lo > 0; cor = (GOOD if d < 0 else CRIT) if sig_ else CTX; y = yy - j * .28
        ax.plot([lo, hi], [y, y], color=cor, lw=2, solid_capstyle="round"); ax.scatter(d, y, s=30, color=cor, zorder=3, edgecolor="white")
        ax.text(31, y, gl, fontsize=7, va="center", color=INK2)
    ticks.append((yy - .28, nome)); yy -= 1.2
ax.axvline(0, color=INK2, lw=1); ax.set_yticks([t[0] for t in ticks]); ax.set_yticklabels([t[1] for t in ticks], fontsize=8)
ax.tick_params(axis="y", length=0); ax.set_xlim(-16, 35); ax.grid(axis="y", visible=False)
ax.set_xlabel("efeito contra o controle (pp) · ← menos   mais →"); save(fig, "10_campanha")
N["campanha"]
""")

md("## 6 · Priorização: valor × risco, com as decisões do grupo")
code("""
cam2 = cam.reset_index(); cam2["acao"] = [acao(s, c, 0) for s, c in zip(cam2.segmento, cam2.camada)]
N["priorizacao"] = cam2.round(4).to_dict("records")
fig, ax = plt.subplots(figsize=(6.4, 3.4))
for r in cam2.itertuples():
    nc = r.acao == "Não contatar"
    ax.scatter(r.churn * 100, r.valor, s=r.n / 12, color=SEG[r.segmento], alpha=.35 if nc else .9, edgecolor=INK2 if nc else "white",
               linewidth=1, linestyle="--" if nc else "-", zorder=3)
    off = {("B", "ar livre"): (10, -3), ("B", "vídeo"): (-8, 12), ("C", "ar livre"): (-4, -16), ("C", "vídeo"): (-70, 12),
           ("D", "ativo"): (8, 8), ("D", "pouco uso"): (8, -16), ("A", "ativo"): (8, -3), ("A", "pouco uso"): (-150, 10)}[(r.segmento, r.camada)]
    ax.annotate(f"{r.segmento} · {r.camada}" + (" · não contatar" if nc else ""), (r.churn * 100, r.valor), xytext=off,
                textcoords="offset points", fontsize=7.5, color=INK2 if nc else INK)
ax.axvline(b.y.mean() * 100, color=MUTED, lw=1, ls=(0, (3, 2))); ax.axhline(b.valor_mes.mean(), color=MUTED, lw=1, ls=(0, (3, 2)))
ax.set_xlabel("risco: saída em 60 dias"); ax.set_ylabel("valor: R$ líquidos por mês"); pctfmt(ax, "x"); ax.set_xlim(-4, 85); ax.set_ylim(18, 40)
for x_, y_, t in [(0, 39, "Proteger"), (60, 39, "Priorizar"), (0, 18, "Manter"), (60, 18, "Monitorar")]:
    ax.text(x_, y_, t, fontsize=8, color=MUTED, fontweight="bold")
save(fig, "11_valor_risco")
cam2
""")

code("""
json.dump(N, open(OUT / "numeros.json", "w"), ensure_ascii=False, indent=1, default=float)
print("ok:", sorted(p.name for p in G.glob("*.svg")))
""")

nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": "notebooks"}}).execute()
nbf.write(nb, "notebooks/eda.ipynb")
print("notebook ok")
