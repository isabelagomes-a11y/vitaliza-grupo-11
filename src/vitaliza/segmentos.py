"""Base analítica da semana 5 e os 4 segmentos de momento (+ camada de comportamento).

Base: assinaturas pagas ativas no fim de 31/07/2026. Rótulo: a assinatura terminou até 29/09/2026 (60 dias).
Segmentos: A anual com renovação em até 60 dias · B mensal com até 5 meses · C mensal com 6+ meses ·
D anual com renovação depois de 60 dias. Camada: anual ativo × pouco uso; mensal ar livre × vídeo.
"""
import numpy as np
import pandas as pd

from .base import ativos_em
from .features import POST_RULES

REF = pd.Timestamp("2026-08-01")          # fim do dia 31/07/2026
FIM_JANELA = pd.Timestamp("2026-09-30")   # saídas até 29/09/2026
TAXA = {"app_store": .15, "google_play": .15, "web_cartao": .035, "web_pix": .0099}
PRECO = {"mensal": 39.90, "anual": 299.90 / 12}
NOMES = {
    "A": "A · O anual que esfriou antes de renovar",
    "B": "B · O mensal que ainda está decidindo",
    "C": "C · O mensal fiel que pode escorregar",
    "D": "D · O anual garantido até a renovação",
}


def base_semana5(sp, e, a, X, ref=REF, fim=FIM_JANELA):
    b = ativos_em(sp, ref).sort_values("ini").drop_duplicates("user_id", keep="last").set_index("user_id")
    b["y"] = (b.fim.notna() & (b.fim < fim)).astype(int)

    ee = e[e.ts < ref]
    cob = ee[ee.evento.isin(["assinatura_iniciada", "renovacao"])].groupby("user_id").ts.last()
    b["dias_ate_renovacao"] = ((cob.reindex(b.index) + pd.Timedelta(days=365)) - ref).dt.days
    b["meses_casa"] = (ref - a.groupby("user_id").inicio.min().reindex(b.index)).dt.days / 30.44
    r = ee[ee.evento.isin(["renovacao_automatica_desligada", "renovacao_automatica_religada",
                           "renovacao", "assinatura_iniciada"])].groupby("user_id").evento.last()
    b["renov_desligada"] = r.reindex(b.index).eq("renovacao_automatica_desligada").astype(int)

    # uso: treinos registrados no uso mensal (BI) de maio a julho/2026; mês sem registro = 0
    um = X["uso"][X["uso"].mes.isin(["2026-05", "2026-06", "2026-07"])].copy()
    um["atividades"] = um.atividades.astype(float)
    pm = um.pivot_table(index="user_id", columns="mes", values="atividades", aggfunc="sum").reindex(b.index).fillna(0)
    for m in ("2026-05", "2026-06", "2026-07"):
        if m not in pm.columns:
            pm[m] = 0
    b["treinos_mes"] = pm[["2026-05", "2026-06", "2026-07"]].mean(axis=1)
    ant = pm[["2026-05", "2026-06"]].mean(axis=1)
    b["queda_uso"] = ((pm["2026-07"] < 0.5 * ant) & (ant > 0)).astype(int)
    at = X["at"][(X["at"].inicio >= "2026-05-01") & (X["at"].inicio < ref)]
    b["pct_ar_livre"] = at.tipo.isin(["corrida", "caminhada", "pedal"]).groupby(at.user_id).mean().reindex(b.index).fillna(0)
    b["gps_falha"] = (~at.gps_ok).groupby(at.user_id).sum().reindex(b.index).fillna(0).gt(0).astype(int)

    po = X["po"][(X["po"].ts < ref) & (X["po"].ts >= ref - pd.Timedelta(days=60))]
    b["meta_cumprida"] = po.groupby("user_id").meta_cumprida.any().reindex(b.index).fillna(False).astype(int)
    tk = X["tk"][(X["tk"].ts < ref) & (X["tk"].ts >= ref - pd.Timedelta(days=90))]
    b["chamado_gps"] = tk[tk.tema == "gps"].groupby("user_id").size().reindex(b.index).fillna(0).gt(0).astype(int)
    b["android"] = X["u"].set_index("user_id").sistema.reindex(b.index).eq("android").astype(int)

    b["valor_mes"] = [PRECO[p] * (1 - TAXA.get(c, .15)) for p, c in zip(b.plano, b.canal)]
    b["segmento"] = np.where(b.plano == "anual", np.where(b.dias_ate_renovacao <= 60, "A", "D"),
                             np.where(b.meses_casa < 6, "B", "C"))
    b["camada"] = np.where(b.plano == "anual", np.where(b.treinos_mes < 2, "pouco uso", "ativo"),
                           np.where(b.pct_ar_livre >= 0.5, "ar livre", "vídeo"))
    return b


def acao(seg, camada, renov_desligada):
    """Regra de priorização da semana 5 (decisões do grupo de 07/11/2026)."""
    if seg in ("A", "D") and camada == "pouco uso":
        return "Não contatar"          # D2: contatar o anual que não usa aumenta o desligamento
    if seg == "B":
        return "Imediata"
    if seg == "C":
        return "Imediata no gatilho"
    if seg == "A":
        return "Imediata"
    return "Proteger"
