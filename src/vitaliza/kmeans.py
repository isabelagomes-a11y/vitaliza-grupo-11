"""K-means de apoio à segmentação: avalia o agrupamento e compara com a regra da camada.

A segmentação oficial (segmentos.py) usa regras. Este módulo mostra, com as quatro lentes da aula
(inércia, silhueta, estabilidade e negócio), o que o k-means encontra e por que a regra o substitui.
O agrupamento usa só comportamento e ciclo conhecidos na data de referência; ficam de fora o rótulo `y`,
a renovação desligada (decisão já tomada), o valor e a demografia. A queda de uso (0/1) também fica fora:
como coluna binária ela domina o agrupamento e vira um grupo próprio (ver o notebook).
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, roc_auc_score, silhouette_score

VARIAVEIS = ["log_treinos_mes", "pct_ar_livre", "log_meses_casa", "meses_ate_renovacao", "plano_anual"]


def variaveis(b, com_queda=False):
    """Variáveis do agrupamento a partir da base de segmentos.base_semana5."""
    v = pd.DataFrame(index=b.index)
    v["log_treinos_mes"] = np.log1p(b["treinos_mes"])
    v["pct_ar_livre"] = b["pct_ar_livre"]
    v["log_meses_casa"] = np.log1p(b["meses_casa"].clip(lower=0))
    v["plano_anual"] = (b["plano"] == "anual").astype(int)
    v["meses_ate_renovacao"] = np.where(v["plano_anual"] == 1, (b["dias_ate_renovacao"] / 30).clip(0, 11), 0)
    if com_queda:
        v["queda_uso"] = b["queda_uso"]
        return v[VARIAVEIS + ["queda_uso"]]
    return v[VARIAVEIS]


def avaliar_k(X, ks, semente=42, amostra=6000, n_estab=10):
    """Inércia, silhueta (amostra) e estabilidade (ARI entre ajustes em subamostras de 80%) por k."""
    rng = np.random.default_rng(semente)
    linhas = []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=semente).fit(X)
        idx = rng.choice(len(X), size=min(amostra, len(X)), replace=False)
        aris = []
        for s in range(n_estab):
            sub = rng.choice(len(X), size=int(0.8 * len(X)), replace=False)
            outro = KMeans(n_clusters=k, n_init=5, random_state=semente + 1 + s).fit(X[sub])
            aris.append(adjusted_rand_score(km.labels_, outro.predict(X)))
        linhas.append({"k": k, "inercia": round(km.inertia_), "silhueta": round(silhouette_score(X[idx], km.labels_[idx]), 3),
                       "estabilidade_ari": round(float(np.mean(aris)), 3), "ari_min": round(float(np.min(aris)), 3)})
    return pd.DataFrame(linhas)


def nomear(v, rotulos):
    """Nome de cada cluster pelo perfil médio (plano e treino ao ar livre), não pelo número do cluster."""
    p = v.assign(c=rotulos).groupby("c")[["plano_anual", "pct_ar_livre"]].mean()
    nomes = {c: ("anual" if r.plano_anual >= 0.5 else "mensal") + (" ar livre" if r.pct_ar_livre >= 0.5 else " vídeo")
             for c, r in p.iterrows()}
    return pd.Series(rotulos, index=v.index).map(nomes)


def camada_kmeans(cluster):
    """Camada pelo k-means: o perfil de treino do cluster (ar livre × vídeo)."""
    return cluster.str.split(" ", n=1).str[1]


def auc_grupo(y, grupo):
    """Quanto um esquema de grupos separa o rótulo: AUC usando o churn do próprio grupo como score."""
    return roc_auc_score(y, y.groupby(grupo).transform("mean"))
