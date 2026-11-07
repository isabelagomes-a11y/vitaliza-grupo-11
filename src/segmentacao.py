"""Variáveis e funções da segmentação com k-means (usadas por notebooks/segmentacao.ipynb).

O agrupamento usa só comportamento e ciclo, conhecidos em 31/07/2026. Ficam de fora, de
propósito: churn_60d (o agrupamento não pode ver quem saiu), renovação desligada e
cancelamento pelo site (decisão já tomada; entram na priorização), valor mensal (eixo de
valor da matriz valor × risco) e demografia (só descreve).
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from base_assinantes import DATA_REF

VARIAVEIS = ["log_treinos_mes", "tendencia_uso", "pct_ar_livre_k", "log_tempo_casa", "meses_ate_renovacao", "plano_anual"]


def meses_ate_renovacao(inicio, plano):
    """Meses inteiros até o próximo aniversário da assinatura anual; 0 no mensal."""
    ref = DATA_REF.normalize()

    def aniversario(anos_depois):
        return pd.to_datetime({"year": ref.year + anos_depois, "month": inicio.dt.month,
                               "day": inicio.dt.day.clip(upper=28)})

    proximo = aniversario(0).where(aniversario(0) > ref, aniversario(1))
    meses = ((proximo - ref).dt.days // 30).clip(0, 11)
    return np.where(plano == "anual", meses, 0)


def preparar(base):
    """Acrescenta as variáveis do agrupamento à base analítica."""
    b = base.copy()
    b["log_treinos_mes"] = np.log1p(b["treinos_mes"])
    antes = (b["treinos_m2"] + b["treinos_m3"]) / 2
    tendencia = np.where(antes > 0, b["treinos_m1"] / antes, np.where(b["treinos_m1"] > 0, 2.0, 1.0))
    b["tendencia_uso"] = np.where(b["meses_observados"] == 3, np.clip(tendencia, 0, 2), 1.0)
    b["pct_ar_livre_k"] = b["pct_ar_livre"].fillna(0.5)
    b["log_tempo_casa"] = np.log1p(b["tempo_casa_meses"])
    b["meses_ate_renovacao"] = meses_ate_renovacao(b["inicio"], b["plano"])
    b["plano_anual"] = (b["plano"] == "anual").astype(int)
    return b


def matriz(b):
    escala = StandardScaler().fit(b[VARIAVEIS])
    return escala.transform(b[VARIAVEIS]), escala


def avaliar_k(X, ks, semente=42, amostra_silhueta=6000, n_estabilidade=10):
    """Inércia, silhueta e estabilidade (ARI entre ajustes em subamostras de 80%) para cada k."""
    rng = np.random.default_rng(semente)
    linhas = []
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=semente).fit(X)
        idx = rng.choice(len(X), size=min(amostra_silhueta, len(X)), replace=False)
        sil = silhouette_score(X[idx], km.labels_[idx])
        aris = []
        for s in range(n_estabilidade):
            sub = rng.choice(len(X), size=int(0.8 * len(X)), replace=False)
            outro = KMeans(n_clusters=k, n_init=5, random_state=semente + 1 + s).fit(X[sub])
            aris.append(adjusted_rand_score(km.labels_, outro.predict(X)))
        linhas.append({"k": k, "inercia": round(km.inertia_, 0), "silhueta": round(sil, 3),
                       "estabilidade_ari": round(float(np.mean(aris)), 3), "ari_min": round(float(np.min(aris)), 3)})
    return pd.DataFrame(linhas)


def ajustar(X, k, semente=42):
    return KMeans(n_clusters=k, n_init=20, random_state=semente).fit(X)


SEGMENTOS = ["A · Anual na porta da renovação", "B · Mensal novato", "C · Mensal veterano",
             "D · Anual com renovação distante"]


def segmento(b):
    """Segmento final: regras de momento (plano, renovação na janela, tempo de casa)."""
    anual = b["plano"] == "anual"
    condicoes = [anual & (b["meses_ate_renovacao"] <= 1), anual, b["tempo_casa_meses"] <= 5]
    escolhas = [SEGMENTOS[0], SEGMENTOS[3], SEGMENTOS[1]]
    return pd.Series(np.select(condicoes, escolhas, default=SEGMENTOS[2]), index=b.index)


def nomear_clusters(b, rotulos):
    """Dá nome de comportamento a cada cluster do k-means a partir do perfil (não do número)."""
    p = b.assign(c=rotulos).groupby("c").agg(anual=("plano_anual", "mean"), treinos=("treinos_mes", "median"),
                                             ar_livre=("pct_ar_livre_k", "mean"))
    nomes = {}
    anuais = p[p["anual"] >= 0.5].sort_values("treinos")
    mensais = p[p["anual"] < 0.5].sort_values("ar_livre")
    for i, c in enumerate(anuais.index):
        nomes[c] = "anual pouco uso" if i == 0 and len(anuais) > 1 else "anual ativo"
    for i, c in enumerate(mensais.index):
        nomes[c] = "mensal vídeo" if i == 0 and len(mensais) > 1 else "mensal ar livre"
    return pd.Series(rotulos, index=b.index).map(nomes)


def camada_comportamento(b, cluster_nome):
    """Camada de comportamento dentro do segmento: no anual, pouco uso x ativo; no mensal, ar livre x vídeo."""
    anual = b["plano"] == "anual"
    pouco = cluster_nome == "anual pouco uso"
    # mensal que caiu num cluster de anual: decide pelo perfil de treino
    video = (cluster_nome == "mensal vídeo") | (cluster_nome.str.startswith("anual") & (b["pct_ar_livre_k"] < 0.5))
    return np.where(anual, np.where(pouco, "pouco uso", "ativo"), np.where(video, "vídeo", "ar livre"))


def gemeo_demografico(b, grupo, alvo):
    """Churn que o segmento teria se se comportasse como o resto da base com a mesma idade e sexo."""
    perfil_demo = pd.cut(b["idade_ref"], [0, 35, 45, 55, 100]).astype(str) + "|" + b["sexo"].fillna("")
    dentro = b[grupo] == alvo
    taxa_fora = b[~dentro].groupby(perfil_demo[~dentro])["churn_60d"].mean()
    pesos = perfil_demo[dentro].value_counts(normalize=True)
    return float((pesos * taxa_fora.reindex(pesos.index)).sum() / pesos[taxa_fora.reindex(pesos.index).notna()].sum())


def perfil(b, grupo):
    """Tamanho, churn, cobertura e médias de cada grupo."""
    total_saidas = b["churn_60d"].sum()
    p = b.groupby(grupo).agg(
        n=("user_id", "size"), churn=("churn_60d", "mean"), saidas=("churn_60d", "sum"),
        pct_mensal=("plano_anual", lambda s: 1 - s.mean()), tempo_casa_mediana=("tempo_casa_meses", "median"),
        meses_ate_renovacao=("meses_ate_renovacao", "mean"), treinos_mes=("treinos_mes", "median"),
        tendencia_uso=("tendencia_uso", "mean"), pct_ar_livre=("pct_ar_livre", "mean"),
        sessoes_mes=("sessoes_mes", "median"), renovacao_desligada=("renovacao_desligada_ref", "mean"),
        valor_mensal=("valor_mensal_liquido", "mean"), idade=("idade_ref", "median"))
    p["pct_base"] = p["n"] / len(b)
    p["pct_do_churn"] = p["saidas"] / total_saidas
    resto = [(b.loc[b[grupo] != g, "churn_60d"].mean()) for g in p.index]
    p["churn_resto"] = resto
    p["diferenca_pp"] = 100 * (p["churn"] - p["churn_resto"])
    return p
