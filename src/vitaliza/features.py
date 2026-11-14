"""Variáveis por assinante numa data de referência (sem olhar para depois dela)."""
import re
import unicodedata

import numpy as np
import pandas as pd

from .base import D, ativos_em


def nz(s):
    """minúsculas, sem acento: deixa as regras de texto robustas a digitação."""
    if not isinstance(s, str):
        return ""
    return unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()


# ---------- extração de texto (regras; mesmo esquema que o prompt do LLM devolve) ----------
POST_RULES = {
    "meta_cumprida": r"missao cumprida|valeu cada treino|agora e descansar|medalha no peito|completei|terminei|concluida|feita .*que dia|chorei na chegada|tava pront",
    "meta_futura": r"contagem regressiva|faltam poucas semanas|me inscrevi|inscricao feita|oficial|foco total|bora que|daqui \d+ semanas|agora e planilha|preciso entrar em forma",
    "vida_mudou": r"trabalho novo|emprego novo|mudanca de cidade|nova cidade|nasceu|virei p|intercambio|viajando a trabalho|sem tempo|fase pesada|semanas puxadas|fechamento de ano|promocao no trabalho|mal durmo|vida nova",
    "lesao": r"lesao|doendo|machuquei|fisio mandou|repouso|vou ter que dar uma pausa",
    "bug_app": r"gps|nao marcou|bug|nao salvou|zerad|nao gravou|app marcou|perdi o registro",
    "intencao_sair": r"cancelei|nao renovei|so com o relogio|pausa nos treinos e no app|dar um tempo do app|ultimo mes aqui|fora do pais",
}

TICKET_RULES = [  # ordem importa: primeira regra que casa define o tema
    ("gps", r"gps|percurso|distancia zerad|nao grava|rota"),
    ("sincronizacao", r"garmin|apple watch|apple health|sincroniz|relogio"),
    ("cancelar", r"cancelar|reembolso|nao uso mais|quero sair"),
    ("cobranca", r"cobr|recusad|pix|cartao|duas vezes|fatura|renovar"),
    ("conta", r"senha|login|e-mail|email|entrar|conta"),
]

ONB_RULES = [
    ("evento_com_data", r"formatura|casamento|viagem|verao|ferias|festa|prova|maratona|\d+ ?k\b|reveillon|mochilao"),
    ("saude", r"colesterol|pressao|medic|costas|sedentari|disposicao|saude|diabet|ansiedade|dormir"),
    ("social", r"galera|junto|grupo|companhia|amig|pessoal|namorad|marido|esposa|turma"),
    ("estetica", r"peso|barriga|forma|kg|secar|emagrec|definir"),
    ("performance", r"correr|pace|pedal|forca|melhorar|evoluir|tempo|km"),
]
JUNK = {"", "nada", ".", "x", "sla", "kkkk", "asdf", "nao sei", "ok", "-", "😂"}


def classify_ticket(t):
    t = nz(t)
    for k, r in TICKET_RULES:
        if re.search(r, t):
            return k
    return "outro"


def classify_objetivo(t):
    if not isinstance(t, str) or nz(t).strip() in JUNK or t.strip() in JUNK:
        return "vazio"
    t = nz(t)
    for k, r in ONB_RULES:
        if re.search(r, t):
            return k
    return "outro"


def parse_dias(s):
    if not isinstance(s, str):
        return np.nan
    if "todo" in s:
        return 7
    m = re.search(r"\d", s)
    return float(m.group()) if m else np.nan


# ---------- carga e limpeza (uma vez) ----------
def load_all():
    from .base import to_brt
    u = pd.read_csv(D + "usuarios.csv", dtype=str)
    u["sistema"] = u.sistema.str.lower()
    u["sexo"] = u.sexo.str[0].str.upper()  # F/Fem/feminino -> F ; M/Masc/masculino -> M
    u["data_nascimento"] = pd.to_datetime(u.data_nascimento, errors="coerce")
    u["data_cadastro"] = pd.to_datetime(u.data_cadastro)

    uso = pd.read_csv(D + "uso_mensal.csv", dtype={"user_id": str, "mes": str})

    at = pd.read_parquet(D + "atividades.parquet")
    at["inicio"] = pd.to_datetime(at.inicio)
    at["tipo"] = at.tipo.replace({"run": "corrida", "walk": "caminhada", "strength": "forca", "ride": "pedal"})
    at["com"] = at.treino_com.fillna("").ne("")

    am = pd.read_csv(D + "amizades.csv", dtype=str, parse_dates=["desde"])

    pg = pd.read_csv(D + "pagamentos.csv", dtype=str)
    pg["valor"] = (pg.valor.str.replace("R$ ", "", regex=False).str.replace(",", ".", regex=False).astype(float))
    pg["ts"] = to_brt(pg.data_hora)
    # 1.941 cobranças repetidas: mesmo usuário, horário, valor, status e tentativa; só o pagamento_id muda
    pg = pg.drop_duplicates(["user_id", "data_hora", "valor", "status", "tentativa"])

    po = pd.read_csv(D + "feed_posts.csv", dtype=str)
    po["ts"] = pd.to_datetime(po.data_hora)
    t = po.texto.map(nz)
    for k, r in POST_RULES.items():
        po[k] = t.str.contains(r)

    tk = pd.read_csv(D + "tickets_suporte.csv", dtype=str)
    tk["ts"] = pd.to_datetime(tk.aberto_em)
    tk["tema"] = tk.texto_cliente.map(classify_ticket)

    ob = pd.read_csv(D + "onboarding.csv", dtype=str)
    ob["objetivo_cat"] = ob.objetivo_texto.map(classify_objetivo)
    ob["dias_meta"] = ob.dias_por_semana.map(parse_dias)

    return dict(u=u, uso=uso, at=at, am=am, pg=pg, po=po, tk=tk, ob=ob)


def snapshot(ref, sp, e, a, X, horizon=60):
    """Uma linha por pagante ativo em `ref`, com variáveis até `ref` e o rótulo dos `horizon` dias seguintes."""
    ref = pd.Timestamp(ref)
    base = ativos_em(sp, ref).sort_values("ini").drop_duplicates("user_id", keep="last").copy()
    base["y"] = (base.fim.notna() & (base.fim < ref + pd.Timedelta(days=horizon))).astype(int)
    f = base[["user_id", "plano", "canal", "y"]].set_index("user_id")

    ee = e[e.ts < ref]
    # renovação automática: último sinal antes da data
    r = ee[ee.evento.isin(["renovacao_automatica_desligada", "renovacao_automatica_religada",
                           "renovacao", "assinatura_iniciada"])].groupby("user_id").agg(ult=("evento", "last"), ts=("ts", "last"))
    f["renov_desligada"] = r.ult.reindex(f.index).eq("renovacao_automatica_desligada").astype(int)
    f["dias_desde_desligou"] = np.where(f.renov_desligada == 1, (ref - r.ts.reindex(f.index)).dt.days, -1)
    # próxima cobrança: última cobrança + ciclo do plano
    cob = ee[ee.evento.isin(["assinatura_iniciada", "renovacao"])].groupby("user_id").ts.last()
    ciclo = np.where(f.plano == "anual", 365, 30)
    prox = cob.reindex(f.index) + pd.to_timedelta(ciclo, unit="D")
    f["dias_ate_cobranca"] = (prox - ref).dt.days.clip(-30, 400).fillna(-1)
    f["cobranca_na_janela"] = ((f.dias_ate_cobranca >= 0) & (f.dias_ate_cobranca < horizon)).astype(int)
    f["carencia_60d"] = ee[(ee.evento == "periodo_carencia") & (ee.ts >= ref - pd.Timedelta(days=60))].groupby("user_id").size().reindex(f.index).fillna(0)
    ini = a.groupby("user_id").inicio.min()
    f["tempo_casa_d"] = (ref - ini.reindex(f.index)).dt.days
    f["mensal_preco_novo"] = ((f.plano == "mensal") & (ref >= pd.Timestamp("2026-03-01"))).astype(int)

    pg = X["pg"][X["pg"].ts < ref]
    f["recusas_90d"] = pg[(pg.status == "recusado") & (pg.ts >= ref - pd.Timedelta(days=90))].groupby("user_id").size().reindex(f.index).fillna(0)
    f["pagou_cupom"] = pg[pg.valor == 239.90].groupby("user_id").size().reindex(f.index).fillna(0).gt(0).astype(int)

    # uso mensal: 3 meses completos antes da data
    meses = [(ref - pd.offsets.MonthBegin(k)).strftime("%Y-%m") for k in (1, 2, 3)]
    um = X["uso"][X["uso"].mes.isin(meses)].pivot_table(index="user_id", columns="mes", values=["dias_ativos", "sessoes_app", "minutos"], aggfunc="sum")
    for k, m in enumerate(meses, 1):
        for v in ("dias_ativos", "sessoes_app", "minutos"):
            f[f"{v}_m{k}"] = um[(v, m)].reindex(f.index).fillna(0) if (v, m) in um.columns else 0
    f["tend_dias"] = f.dias_ativos_m1 - f.dias_ativos_m3

    # treinos (2026): últimos 30/90 dias
    at = X["at"][(X["at"].inicio < ref) & (X["at"].inicio >= ref - pd.Timedelta(days=90))]
    g90 = at.groupby("user_id")
    a30 = at[at.inicio >= ref - pd.Timedelta(days=30)].groupby("user_id")
    f["treinos_30d"] = a30.size().reindex(f.index).fillna(0)
    f["treinos_90d"] = g90.size().reindex(f.index).fillna(0)
    f["dias_desde_treino"] = (ref - g90.inicio.max().reindex(f.index)).dt.days.fillna(91)
    f["gps_falha_90d"] = (at.assign(x=~at.gps_ok).groupby("user_id").x.sum()).reindex(f.index).fillna(0)
    f["treino_junto_90d"] = g90.com.sum().reindex(f.index).fillna(0)
    f["ar_livre_share"] = at.tipo.isin(["corrida", "caminhada", "pedal"]).groupby(at.user_id).mean().reindex(f.index).fillna(0)

    u = X["u"].set_index("user_id")
    f["android"] = u.sistema.reindex(f.index).eq("android").astype(int)
    f["relogio"] = u.relogio_conectado.reindex(f.index).ne("nenhum").astype(int)
    f["idade"] = ((ref - u.data_nascimento.reindex(f.index)).dt.days / 365.25).clip(14, 90)
    f["mulher"] = u.sexo.reindex(f.index).eq("F").astype(int)
    for c in ["influenciador", "meta_ads", "indicacao", "google_ads", "parceria_corporativa"]:
        f[f"aq_{c}"] = u.canal_aquisicao.reindex(f.index).eq(c).astype(int)

    am = X["am"][X["am"].desde < ref]
    f["seguidores"] = am.groupby("seguido_id").size().reindex(f.index).fillna(0)
    f["seguindo"] = am.groupby("seguidor_id").size().reindex(f.index).fillna(0)

    f["mensal"] = (f.plano == "mensal").astype(int)
    f["loja"] = f.canal.isin(["app_store", "google_play"]).astype(int)
    return f


def text_features(ref, f, X, days=60):
    """Variáveis vindas de texto: posts, chamados e questionário de entrada."""
    ref = pd.Timestamp(ref)
    g = pd.DataFrame(index=f.index)
    po = X["po"][(X["po"].ts < ref) & (X["po"].ts >= ref - pd.Timedelta(days=days))]
    gp = po.groupby("user_id")
    g["posts_60d"] = gp.size().reindex(g.index).fillna(0)
    for k in POST_RULES:
        g[f"post_{k}"] = gp[k].any().reindex(g.index).fillna(False).astype(int)
    tk = X["tk"][(X["tk"].ts < ref) & (X["tk"].ts >= ref - pd.Timedelta(days=90))]
    for k in ["gps", "sincronizacao", "cancelar", "cobranca", "conta"]:
        g[f"ticket_{k}"] = tk[tk.tema == k].groupby("user_id").size().reindex(g.index).fillna(0)
    g["ticket_aberto"] = tk[tk.status != "resolvido"].groupby("user_id").size().reindex(g.index).fillna(0)
    ob = X["ob"].drop_duplicates("user_id").set_index("user_id")
    for k in ["evento_com_data", "saude", "social", "estetica", "vazio"]:
        g[f"obj_{k}"] = ob.objetivo_cat.reindex(g.index).eq(k).astype(int)
    g["dias_meta"] = ob.dias_meta.reindex(g.index)
    return g


# ---------- imagem: contagem de pixels nos mapas de calor ----------
def _is_route(arr):
    """Rota = tons laranja/vermelho/amarelo forte; o fundo usa 6 cores fixas claras."""
    r, g, b = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    return (r > 200) & (r - b > 90) & (g < 215)


def heatmap_features(folder):
    from pathlib import Path
    from PIL import Image
    rows = []
    for p in Path(folder).glob("*.png"):
        arr = np.asarray(Image.open(p).convert("RGB"))
        route = _is_route(arr)
        n = route.sum()
        park = (np.abs(arr - [197, 226, 175]).sum(-1) < 20)
        water = (np.abs(arr - [170, 207, 230]).sum(-1) < 20)
        beach = (np.abs(arr - [250, 236, 190]).sum(-1) < 12)
        # vizinhança 5x5 da rota: em que tipo de lugar a pessoa treina
        from scipy.ndimage import binary_dilation
        near = binary_dilation(route, iterations=3) & ~route
        tot = max(near.sum(), 1)
        intens = (255 - arr[..., 1][route]).mean() if n else 0  # verde baixo = cor mais quente = mais passagens
        rows.append((p.stem, n, intens, (park & near).sum() / tot, (water & near).sum() / tot, (beach & near).sum() / tot))
    return pd.DataFrame(rows, columns=["user_id", "hm_px", "hm_intens", "hm_parque", "hm_agua", "hm_praia"]).set_index("user_id")
