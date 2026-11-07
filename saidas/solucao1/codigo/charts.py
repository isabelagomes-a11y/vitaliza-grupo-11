"""Gera os gráficos (SVG) usados nos documentos de análise e de solução."""
import io
import json
import sys

sys.path.insert(0, "src")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from base import *
from features import *

OUT = "outputs/charts/"
import os
os.makedirs(OUT, exist_ok=True)
R = json.load(open("outputs/resultados.json"))

# ---- linguagem visual (tokens) ----
INK, INK2, MUTED, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
MENSAL, ANUAL = "#2a78d6", "#eb6834"          # entidades: plano
ANDROID, IOS = "#1baf7a", "#6250d6"           # entidades: sistema
CRIT, GOOD, WARN, CTX = "#d03b3b", "#0ca30c", "#fab219", "#c3c2b7"   # papéis: problema, ganho, incerteza, contexto

plt.rcParams.update({
    "font.family": ["Helvetica Neue", "Helvetica", "Arial"], "font.size": 9, "text.color": INK,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": .6, "axes.axisbelow": True, "figure.facecolor": "none", "axes.facecolor": "none",
    "lines.linewidth": 2, "svg.fonttype": "none",
})


def save(fig, name):
    fig.savefig(OUT + name + ".svg", bbox_inches="tight", transparent=True)
    plt.close(fig)


def pct(ax, axis="y", dec=0):
    f = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.{dec}f}%".replace(".", ","))
    (ax.yaxis if axis == "y" else ax.xaxis).set_major_formatter(f)


e = load_eventos(); a = load_assinaturas(); sp = spells(e, a); X = load_all()
meses = pd.date_range("2025-01-01", "2026-09-01", freq="MS")
MES = {1:"jan",2:"fev",3:"mar",4:"abr",5:"mai",6:"jun",7:"jul",8:"ago",9:"set",10:"out",11:"nov",12:"dez"}
lab = [f"{MES[m.month]}/{m:%y}" for m in meses]
br = lambda v, d=0: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")

# 1. churn mensal com eventos
ch = churn_mensal(sp, meses)
fig, ax = plt.subplots(figsize=(7.2, 2.6))
cols = [CTX] * 12 + [INK2] * 9
cols[15] = CRIT
ax.bar(range(len(ch)), ch.churn * 100, color=cols, width=.72)
ax.axhline(5.6, color=MUTED, lw=1, ls=(0, (3, 2))); ax.text(-.4, 5.75, "média 2025: 5,6%", color=INK2, fontsize=8)
ax.plot([12 - .4, 20.4], [6.6, 6.6], color=INK, lw=1, ls=(0, (3, 2))); ax.text(11.6, 6.8, "média 2026: 6,6%", color=INK, fontsize=8)
ax.text(15, ch.churn[15] * 100 + .15, "8,1%", ha="center", color=CRIT, fontsize=8, fontweight="bold")
for x, t in [(14, "reajuste\n01/03"), (16.5, "falha GPS\nmai–jun"), (19.3, "campanha\n10/08")]:
    ax.annotate(t, (x, 0.2), xytext=(x, 9.6), ha="center", fontsize=7.5, color=INK2,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=.7, ls=":"))
ax.set_xticks(range(len(ch))); ax.set_xticklabels(lab, rotation=90, fontsize=7.5); ax.set_ylim(0, 10.5); pct(ax)
ax.grid(axis="x", visible=False)
save(fig, "01_churn_mensal")

# 2. churn por plano
rows = []
for m in meses:
    t1 = m + pd.offsets.MonthBegin(1); at = ativos_em(sp, m)
    rows.append(at.assign(l=at.fim.notna() & (at.fim < t1)).groupby("plano").l.mean().rename(m))
cp = pd.DataFrame(rows) * 100
fig, ax = plt.subplots(figsize=(7.2, 2.5))
x = np.arange(len(cp))
ax.axvspan(13.5, 16.5, color=CRIT, alpha=.07, lw=0); ax.text(15, 15.3, "3 meses após o reajuste", ha="center", fontsize=7.5, color=CRIT)
ax.plot(x, cp.mensal, color=MENSAL, marker="o", ms=3.5); ax.plot(x, cp.anual, color=ANUAL, marker="o", ms=3.5)
ax.text(20.4, cp.mensal.iloc[-1], " mensal", color=INK, va="center", fontsize=8.5)
ax.text(20.4, cp.anual.iloc[-1], " anual", color=INK, va="center", fontsize=8.5)
ax.set_xticks(x); ax.set_xticklabels(lab, rotation=90, fontsize=7.5); pct(ax); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(4)); ax.set_ylim(0, 16.5); ax.set_xlim(-.5, 22.3)
ax.grid(axis="x", visible=False)
save(fig, "02_churn_plano")

# 3. decomposição (cascata)
d = R["decomp"]
steps = [("Churn\n2025", 5.62, "base"), ("Mensais\nsaindo mais", d["mensais saindo mais (preço, GPS)"], "up"),
         ("Anuais\nsaindo mais", d["anuais saindo mais (renovações maduras)"], "up"),
         ("Mais anuais\nna base", d["mudança de mix (mais anuais, que saem menos)"], "down"), ("Churn\n2026", 6.62, "base")]
fig, ax = plt.subplots(figsize=(6.4, 2.6)); run = 0
for i, (n, v, k) in enumerate(steps):
    if k == "base":
        ax.bar(i, v, color=INK2, width=.6); ax.text(i, v + .05, f"{v:.1f}%".replace(".", ","), ha="center", fontsize=8.5, fontweight="bold"); run = v
    else:
        b = run if v > 0 else run + v
        ax.bar(i, abs(v), bottom=b, color=CRIT if v > 0 else GOOD, width=.6)
        ax.text(i, run + max(v, 0) + .05, f"{v:+.2f} pp".replace(".", ","), ha="center", fontsize=8.5, color=INK)
        run += v
ax.set_xticks(range(5)); ax.set_xticklabels([s[0] for s in steps], fontsize=8); ax.set_ylim(5, 7.2); pct(ax, dec=1)
ax.grid(axis="x", visible=False)
save(fig, "03_decomposicao")

# 4. Android x iOS
u = X["u"].set_index("user_id"); rows = []
for m in pd.date_range("2026-01-01", "2026-09-01", freq="MS"):
    t1 = m + pd.offsets.MonthBegin(1); at = ativos_em(sp, m).copy(); at["s"] = at.user_id.map(u.sistema)
    rows.append(at.assign(l=at.fim.notna() & (at.fim < t1)).groupby("s").l.mean().rename(m))
cs = pd.DataFrame(rows) * 100
fig, ax = plt.subplots(figsize=(6.4, 2.4)); x = np.arange(len(cs))
ax.axvspan(3.5, 5.5, color=WARN, alpha=.18, lw=0); ax.text(4.5, 9.3, "GPS falhando\nno Android", ha="center", fontsize=7.5, color=INK2)
ax.axvspan(4.5, 6.5, color=CRIT, alpha=.07, lw=0)
ax.plot(x, cs.android, color=ANDROID, marker="o", ms=3.5); ax.plot(x, cs.ios, color=IOS, marker="o", ms=3.5)
ax.text(8.15, cs.android.iloc[-1] + .35, " Android", fontsize=8.5); ax.text(8.15, cs.ios.iloc[-1] - .35, " iOS", fontsize=8.5)
ax.annotate("+2,4 pp", (5.5, 6.3), fontsize=8.5, color=CRIT, fontweight="bold", ha="center")
ax.set_xticks(x); ax.set_xticklabels([MES[m.month] for m in cs.index], fontsize=8); pct(ax); ax.set_ylim(3, 10.3); ax.set_xlim(-.4, 9.3)
ax.grid(axis="x", visible=False)
save(fig, "04_android_ios")

# 5. curva de captura (modelo)
import lightgbm as lgb
TR = ["2026-03-01", "2026-04-01", "2026-05-01", "2026-06-01"]
def build(ref):
    f = snapshot(ref, sp, e, a, X); return f.join(text_features(ref, f, X))
tr = pd.concat([build(r) for r in TR]); te = build("2026-07-31")
cols = [c for c in tr.columns if c not in ("plano", "canal", "y")]
m = lgb.LGBMClassifier(n_estimators=400, learning_rate=.03, num_leaves=31, min_child_samples=100, subsample=.8, subsample_freq=1, colsample_bytree=.8, verbose=-1, random_state=0).fit(tr[cols], tr.y)
p = m.predict_proba(te[cols])[:, 1]
o = np.argsort(-p); cum = np.cumsum(te.y.values[o]) / te.y.sum(); frac = np.arange(1, len(o) + 1) / len(o)
fig, ax = plt.subplots(figsize=(4.6, 3.0))
ax.plot(frac * 100, cum * 100, color=MENSAL); ax.plot([0, 100], [0, 100], color=MUTED, lw=1, ls=(0, (3, 2)))
k = 1500 / 14753; ck = np.interp(k, frac, cum)
ax.scatter([k * 100], [ck * 100], s=40, color=MENSAL, edgecolor=SURF, linewidth=2, zorder=3)
ax.annotate(f"top 1.500 (10% da base)\npega {ck:.0%} das saídas".replace(".", ","), (k * 100, ck * 100), xytext=(22, 50), fontsize=8,
            arrowprops=dict(arrowstyle="-", color=MUTED, lw=.7))
ax.text(60, 52, "ao acaso", color=INK2, fontsize=8, rotation=33)
ax.text(40, 95, "modelo", color=INK, fontsize=8.5)
ax.set_xlabel("% da base contatada, do maior para o menor risco"); ax.set_ylabel("% das saídas alcançadas")
pct(ax); pct(ax, "x"); ax.set_xlim(0, 100); ax.set_ylim(0, 102)
save(fig, "05_captura")

# 6. efeito da campanha (pontos com IC)
cc = pd.DataFrame(R["campanha_celulas"])
sel = [("mensal · ativo", "saiu", "Mensal ativo · saída"), ("anual · ativo", "desligou", "Anual ativo · desligou renovação"),
       ("anual · dorminhoco", "desligou", "Anual dorminhoco · desligou renovação"), ("renovação já desligada", "saiu", "Renovação já desligada · saída")]
msgs = [("desafio", "Desafio"), ("cupom", "Cupom"), ("conteudo", "Conteúdo")]
fig, ax = plt.subplots(figsize=(7.2, 3.1)); yy = 0; ticks = []
for cel, res, nome in sel:
    for j, (mg, mn) in enumerate(msgs):
        r = cc[(cc["célula"] == cel) & (cc.resultado == res) & (cc.mensagem == mg)].iloc[0]
        sig = r["IC high"] < 0 or r["IC low"] > 0
        col = (GOOD if r["Δ pp"] < 0 else CRIT) if sig else CTX
        y = yy - j * .28
        ax.plot([r["IC low"], r["IC high"]], [y, y], color=col, lw=2, solid_capstyle="round")
        ax.scatter(r["Δ pp"], y, s=34, color=col, edgecolor=SURF, linewidth=1.5, zorder=3)
        ax.text(27.5, y, mn, fontsize=7.5, va="center", color=INK2)
    ticks.append((yy - .28, nome)); yy -= 1.25
ax.axvline(0, color=INK2, lw=1)
ax.set_yticks([t[0] for t in ticks]); ax.set_yticklabels([t[1] for t in ticks], fontsize=8.5); ax.tick_params(axis="y", length=0)
ax.set_xlim(-12, 31)
for yb in (-.95, -2.2, -3.45): ax.axhline(yb, color=GRID, lw=.8)
ax.set_xlabel("efeito contra o controle (pp) · ← menos saída   mais saída →")
ax.grid(axis="y", visible=False)
save(fig, "06_campanha")

# 7. estratégias
E = pd.DataFrame(R["estrategias"]).set_index("estrategia")
order = ["Cupom para todos", "Cupom para o top 1.500 de risco", "Não fazer nada", "Desafio para todos", "Regra seletiva por célula"]
vals = E.loc[order, "lucro"] / 1000
fig, ax = plt.subplots(figsize=(6.4, 2.4))
ax.barh(range(5), vals, color=[CRIT if v < 0 else (GOOD if v > 0 else CTX) for v in vals], height=.6)
for i, v in enumerate(vals):
    t = f"{'+' if v > 0 else ('−' if v < 0 else '')}R$ {abs(v):.0f} mil"
    if v < -100: ax.text(v + 8, i, t, va="center", ha="left", fontsize=8.5, color="#ffffff", fontweight="bold")
    else: ax.text(v + (6 if v >= 0 else -6), i, t, va="center", ha="left" if v >= 0 else "right", fontsize=8.5)
ax.set_yticks(range(5)); ax.set_yticklabels(["Cupom para todos", "Cupom para o top 1.500", "Não fazer nada", "Desafio para todos", "Regra seletiva"], fontsize=8.5)
ax.axvline(0, color=INK2, lw=1); ax.set_xlim(-470, 150); ax.tick_params(axis="y", length=0); ax.grid(axis="y", visible=False)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}"))
ax.set_xlabel("lucro líquido incremental por onda (R$ mil)")
save(fig, "07_estrategias")

# 8. alocação da base
segs = [("Desafio · mensal", 6107, MENSAL), ("Desafio · anual", 5492, ANUAL), ("Quietos de propósito", 3154, CTX)]
fig, ax = plt.subplots(figsize=(7.2, .95)); left = 0
for n, v, c in segs:
    ax.barh(0, v - 40, left=left + 20, color=c, height=.55)
    ax.text(left + v / 2, 0, f"{n}\n{v:,}".replace(",", "."), ha="center", va="center", fontsize=8, color="#ffffff" if c != CTX else INK)
    left += v
ax.set_xlim(0, 14753); ax.axis("off")
save(fig, "08_alocacao")

# 9. segmentos
sg = pd.DataFrame(R["segmentos"]).set_index("segmento").sort_values("saída 60d observada (ref. 31/07)")
fig, ax = plt.subplots(figsize=(6.4, 2.4))
v = sg["saída 60d observada (ref. 31/07)"] * 100
ax.barh(range(len(sg)), v, color=[CRIT if x > 20 else (WARN if x > 10 else INK2) for x in v], height=.6)
for i, (x, n) in enumerate(zip(v, sg.n)):
    ax.text(x + .4, i, f"{br(x, 1)}%  ·  {br(n)} pessoas", va="center", fontsize=8)
ax.set_yticks(range(len(sg))); ax.set_yticklabels(sg.index, fontsize=8.5); ax.tick_params(axis="y", length=0)
pct(ax, "x"); ax.set_xlim(0, 34); ax.grid(axis="y", visible=False); ax.set_xlabel("saída nos 60 dias seguintes (referência 31/07)")
save(fig, "09_segmentos")

# 10. valor de texto e imagem (duas comparações, cada uma no seu teste)
fig, ax = plt.subplots(figsize=(5.2, 2.3))
xs = [0, 1, 2.6, 3.6]; vals = [62.6, 66.1, 65.4, 65.0]
ax.bar(xs, vals, color=[CTX, GOOD, CTX, CTX], width=.7)
for x, v in zip(xs, vals):
    ax.text(x, v + .3, f"{v:.1f}%".replace(".", ","), ha="center", fontsize=8.5)
ax.set_xticks(xs); ax.set_xticklabels(["sem texto", "com texto", "sem imagem", "com imagem"], fontsize=8)
ax.text(.5, 68.2, "Texto: +3,5 pp", ha="center", fontsize=8.5, color=INK, fontweight="bold")
ax.text(3.1, 68.2, "Imagem: −0,4 pp", ha="center", fontsize=8.5, color=INK2, fontweight="bold")
ax.set_ylim(55, 70); pct(ax); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5)); ax.set_ylabel("captura no top 1.500"); ax.grid(axis="x", visible=False)
save(fig, "10_texto_imagem")
print("ok", ck)
