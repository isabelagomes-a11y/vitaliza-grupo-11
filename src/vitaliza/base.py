"""Funções compartilhadas: leitura, limpeza e reconstrução do status de assinatura."""
import numpy as np
import pandas as pd

from .config import DADOS

D = str(DADOS) + "/"
CORTE = pd.Timestamp("2026-10-01")  # fim do dia 30/09/2026 (BRT)


def to_brt(s: pd.Series) -> pd.Series:
    """Datas das lojas vêm em UTC ('Z'); as do site em horário de Brasília."""
    s = s.astype(str)
    z = s.str.endswith("Z")
    t = pd.to_datetime(s.str.replace("Z", "", regex=False).str.replace("T", " ", regex=False))
    return t.where(~z, t - pd.Timedelta(hours=3))


def load_eventos():
    e = pd.read_csv(D + "eventos_assinatura.csv", dtype=str)
    e["ts"] = to_brt(e.data_hora)
    return e.sort_values(["user_id", "ts"], kind="stable").reset_index(drop=True)


def load_assinaturas():
    a = pd.read_csv(D + "assinaturas.csv", dtype=str, parse_dates=["inicio", "data_fim"])
    return a


START = {"assinatura_iniciada", "renovacao", "renovacao_automatica_religada",
         "periodo_carencia", "cancelamento_web"}
END = {"assinatura_expirada", "reembolso"}


def spells(e: pd.DataFrame, a: pd.DataFrame) -> pd.DataFrame:
    """Períodos pagantes por usuário: [ini, fim). fim = NaT se ativo no corte.

    O log começa em 01/07/2024. Quem já pagava antes disso (assinatura com início
    anterior e sem fim antes de 01/07/2024) começa o log como pagante.
    """
    pre = a[(a.inicio < "2024-07-01") & (a.data_fim.isna() | (a.data_fim >= "2024-07-01"))
            & (a.canal_cobranca != "interno")]
    pre_users = set(pre.user_id)
    pre_plano = pre.sort_values("inicio").groupby("user_id").last()[["plano_atual", "canal_cobranca"]]
    rows = []
    ev = e[e.evento.isin(START | END | {"chargeback", "trial_iniciado", "renovacao_automatica_desligada"})]
    for uid, g in ev.groupby("user_id", sort=False):
        paying = uid in pre_users
        ini = pd.Timestamp("2024-07-01") if paying else None
        plano, canal = (pre_plano.loc[uid].tolist() if paying else (None, None))
        for t, evn, pl, ca in zip(g.ts, g.evento, g.plano, g.canal_cobranca):
            if paying and isinstance(pl, str):
                plano = pl  # plano no momento do evento
            if evn in START and evn != "cancelamento_web" or (evn == "cancelamento_web" and paying):
                if not paying:
                    paying, ini = True, t
                    plano = pl if isinstance(pl, str) else plano
                canal = ca
            elif evn in END and paying:
                rows.append((uid, ini, t, plano, canal, evn))
                paying = False
        if paying:
            rows.append((uid, ini, pd.NaT, plano, canal, None))
    # pagantes antigos sem nenhum evento no log
    seen = set(ev.user_id)
    for r in pre[~pre.user_id.isin(seen)].itertuples():
        rows.append((r.user_id, pd.Timestamp("2024-07-01"), r.data_fim, r.plano_atual, r.canal_cobranca, "sem_evento"))
    return pd.DataFrame(rows, columns=["user_id", "ini", "fim", "plano", "canal", "fim_evento"])


def ativos_em(sp: pd.DataFrame, t) -> pd.DataFrame:
    t = pd.Timestamp(t)
    return sp[(sp.ini < t) & (sp.fim.isna() | (sp.fim >= t))]


def churn_mensal(sp: pd.DataFrame, meses) -> pd.DataFrame:
    out = []
    for m in meses:
        t0 = pd.Timestamp(m); t1 = t0 + pd.offsets.MonthBegin(1)
        at = ativos_em(sp, t0)
        perd = at[at.fim.notna() & (at.fim < t1)]
        out.append((t0.strftime("%Y-%m"), len(at), len(perd)))
    df = pd.DataFrame(out, columns=["mes", "ativos_inicio", "perdas"])
    df["churn"] = df.perdas / df.ativos_inicio
    return df
