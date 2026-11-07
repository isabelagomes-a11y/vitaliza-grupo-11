"""Períodos pagos de cada assinante e quem estava ativo em cada data.

Uso: python src/situacao_assinantes.py   (depois de src/limpar_eventos.py)

Cada usuário tem no máximo uma assinatura (assinaturas.csv: uma linha por user_id), então
o período pago é um só por usuário:
- início: data do evento assinatura_iniciada; para quem começou antes de 01/07/2024 (início
  do histórico de eventos), a data `inicio` de assinaturas.csv;
- fim: data do evento assinatura_expirada; sem expiração, a assinatura segue ativa no
  corte, mesmo com reembolso ou chargeback (assim estão em assinaturas.csv e na conta de
  fins do enunciado);
- tipo_saida: voluntaria (renovação desligada), falha_pagamento, chargeback_reembolso ou
  nao_informado, a partir de `detalhe` da expiração;
- interna: conta de canal_aquisicao "interno" (e-mail @vitaliza.com.br). Fica no arquivo,
  mas fora das contagens (ativos_em e perdas_no_mes), como nos números do enunciado.
Datas em horário de Brasília (data_hora_brt). Decisões registradas em decisoes.md.

Grava dados/processados/assinaturas_periodos.csv (uma linha por assinatura) e confere a
reconstrução contra assinaturas.csv e contra os números do enunciado, gravando
saidas/conferencia_enunciado.csv.
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
BRUTOS = RAIZ / "dados" / "brutos"
PROCESSADOS = RAIZ / "dados" / "processados"
SAIDAS = RAIZ / "saidas"

INICIO_HISTORICO = pd.Timestamp("2024-07-01")
CORTE = pd.Timestamp("2026-10-01")  # primeiro instante depois do corte

TIPO_SAIDA = {
    "renovacao_desligada": "voluntaria",
    "falha_pagamento": "falha_pagamento",
    "chargeback": "chargeback_reembolso",
    "reembolso": "chargeback_reembolso",
    "": "nao_informado",
}


def ativos_em(periodos, data):
    """Assinaturas pagas ativas no instante `data` (início <= data < fim), sem contas internas."""
    data = pd.Timestamp(data)
    p = periodos[~periodos["interna"]]
    return p[(p["inicio"] <= data) & (p["fim"].isna() | (p["fim"] > data))]


def ativos_no_dia(periodos, dia):
    """Assinaturas pagas ativas em algum momento do dia, sem contas internas."""
    ini = pd.Timestamp(dia)
    p = periodos[~periodos["interna"]]
    return p[(p["inicio"] < ini + pd.Timedelta(days=1)) & (p["fim"].isna() | (p["fim"] >= ini))]


def perdas_no_mes(periodos, mes):
    """Série mensal da empresa: ativos no início do mês e quantos deles terminam no mês."""
    ini = pd.Timestamp(f"{mes}-01")
    fim = ini + pd.offsets.MonthBegin(1)
    base = ativos_em(periodos, ini)
    perdas = base[base["fim"].notna() & (base["fim"] < fim)]
    return len(base), len(perdas)


def montar_periodos():
    ev = pd.read_csv(PROCESSADOS / "eventos_assinatura_limpo.csv", dtype=str, keep_default_na=False,
                     parse_dates=["data_hora_brt"])
    ass = pd.read_csv(BRUTOS / "assinaturas.csv", dtype=str, keep_default_na=False)
    assert not ass["user_id"].duplicated().any(), "mais de uma assinatura por usuário; rever a regra"
    print(f"eventos limpos: {len(ev)} linhas | assinaturas.csv: {len(ass)} assinaturas")

    def primeiro(evento):
        return ev[ev["evento"] == evento].groupby("user_id")["data_hora_brt"].min()

    def ultimo(evento):
        sel = ev[ev["evento"] == evento]
        return sel.groupby("user_id")[["data_hora_brt", "detalhe", "plano"]].last()

    iniciada = primeiro("assinatura_iniciada")
    expirada = ultimo("assinatura_expirada")
    ultimo_plano = ev[ev["plano"] != ""].groupby("user_id")["plano"].last()

    p = ass[["assinatura_id", "user_id", "canal_cobranca", "inicio", "status_atual", "data_fim",
             "motivo_fim", "plano_atual"]].copy()
    p["inicio_retrato"] = pd.to_datetime(p["inicio"], format="%Y-%m-%d")
    p["inicio_evento"] = p["user_id"].map(iniciada)
    p["inicio"] = p["inicio_evento"].fillna(p["inicio_retrato"])
    p["origem_inicio"] = p["inicio_evento"].notna().map({True: "evento", False: "assinaturas.csv"})

    p["fim"] = p["user_id"].map(expirada["data_hora_brt"])
    detalhe = p["user_id"].map(expirada["detalhe"])
    terminou = p["fim"].notna()
    p["origem_fim"] = terminou.map({True: "assinatura_expirada", False: "ativa"})
    p["tipo_saida"] = ""
    p.loc[terminou, "tipo_saida"] = detalhe[terminou].fillna("").map(TIPO_SAIDA)
    p["plano"] = p["user_id"].map(ultimo_plano).fillna(p["plano_atual"])

    usuarios = pd.read_csv(BRUTOS / "usuarios.csv", dtype=str, keep_default_na=False,
                           usecols=["user_id", "canal_aquisicao"])
    internas = set(usuarios.loc[usuarios["canal_aquisicao"] == "interno", "user_id"])
    p["interna"] = p["user_id"].isin(internas)

    print("origem do início:", p["origem_inicio"].value_counts().to_dict())
    print("origem do fim:", p["origem_fim"].value_counts().to_dict())
    print("tipo de saída:", p.loc[terminou, "tipo_saida"].value_counts().to_dict())
    print(f"contas internas: {len(internas)} | com assinatura: {p['interna'].sum()} | "
          f"ativas no corte: {(p['interna'] & ~terminou).sum()}")
    cb_sem_exp = ev[ev["evento"].isin(["reembolso", "chargeback"])]["user_id"].drop_duplicates()
    print(f"reembolso ou chargeback sem expiração (seguem ativas): "
          f"{(~terminou & p['user_id'].isin(cb_sem_exp)).sum()}")

    # Conferência eventos x retrato de 01/10/2026
    antes = p["origem_inicio"] == "assinaturas.csv"
    print(f"sem assinatura_iniciada: {antes.sum()} | delas com início no retrato antes de 01/07/2024: "
          f"{(p.loc[antes, 'inicio_retrato'] < INICIO_HISTORICO).sum()}")
    dif_ini = (p.loc[~antes, "inicio_evento"].dt.normalize() - p.loc[~antes, "inicio_retrato"]).dt.days
    print("início evento - retrato (dias):", dif_ini.value_counts().head(4).to_dict())
    ativa_evento = p["fim"].isna()
    ativa_retrato = p["status_atual"] == "ativa"
    print(f"ativas pelos eventos: {ativa_evento.sum()} | pelo retrato: {ativa_retrato.sum()} | "
          f"divergem: {(ativa_evento != ativa_retrato).sum()}")
    fim_retrato = pd.to_datetime(p["data_fim"].replace("", None), format="%Y-%m-%d")
    dif_fim = (p["fim"].dt.normalize() - fim_retrato).dt.days.dropna()
    print("fim evento - retrato (dias):", dif_fim.value_counts().head(4).to_dict())
    assert (p["fim"].isna() | (p["fim"] >= p["inicio"])).all(), "fim antes do início"

    cols = ["assinatura_id", "user_id", "plano", "canal_cobranca", "inicio", "fim", "origem_inicio",
            "origem_fim", "tipo_saida", "interna"]
    return p[cols]


def conferir(p):
    linhas = []

    def add(item, esperado, calculado):
        linhas.append({"item": item, "enunciado": esperado, "reconstruido": calculado})

    add("ativos no início de jan/2025", 8540, len(ativos_em(p, "2025-01-01")))
    base, perdas = perdas_no_mes(p, "2026-04")
    add("abril/2026: ativos no início", 14237, base)
    add("abril/2026: perdas", 1154, perdas)
    add("abril/2026: churn %", 8.1, round(100 * perdas / base, 1))
    base, perdas = perdas_no_mes(p, "2026-09")
    add("setembro/2026: ativos no início", 14319, base)
    add("setembro/2026: churn %", 5.0, round(100 * perdas / base, 1))
    base, perdas = perdas_no_mes(p, "2026-08")
    add("agosto/2026: churn %", 5.9, round(100 * perdas / base, 1))
    add("ativos em 30/09/2026 (fim do dia)", 14753, len(ativos_em(p, CORTE - pd.Timedelta(seconds=1))))
    add("pagantes em algum momento de 10/08/2026 (campanha)", 14120, len(ativos_no_dia(p, "2026-08-10")))
    meses = pd.period_range("2025-01", "2025-12", freq="M").astype(str)
    taxas = [100 * perdas / base for base, perdas in (perdas_no_mes(p, m) for m in meses)]
    add("churn médio mensal 2025 %", 5.6, round(sum(taxas) / len(taxas), 1))
    meses = pd.period_range("2026-01", "2026-09", freq="M").astype(str)
    taxas = [100 * perdas / base for base, perdas in (perdas_no_mes(p, m) for m in meses)]
    add("churn médio mensal jan-set/2026 %", 6.6, round(sum(taxas) / len(taxas), 1))
    perdas_serie = sum(perdas_no_mes(p, m)[1] for m in ["2026-06", "2026-07", "2026-08", "2026-09"])
    add("perdas da série mensal jun-set/2026", 3362, perdas_serie)
    fins = (~p["interna"] & p["fim"].between("2026-06-01", CORTE, inclusive="left")).sum()
    add("fins de assinatura jun-set/2026", 3389, int(fins))
    ativos = ativos_em(p, CORTE - pd.Timedelta(seconds=1))
    add("plano anual em 30/09 (%)", 57, round(100 * (ativos["plano"] == "anual").mean()))
    for canal, pct in [("app_store", 36.6), ("google_play", 33.6), ("web_cartao", 20.3), ("web_pix", 9.5)]:
        add(f"{canal} em 30/09 (%)", pct, round(100 * (ativos["canal_cobranca"] == canal).mean(), 1))

    tabela = pd.DataFrame(linhas)
    tabela["diferenca"] = tabela["reconstruido"] - tabela["enunciado"]
    return tabela


def main():
    p = montar_periodos()
    PROCESSADOS.mkdir(exist_ok=True)
    p.to_csv(PROCESSADOS / "assinaturas_periodos.csv", index=False, encoding="utf-8")
    print(f"gravado: dados/processados/assinaturas_periodos.csv ({len(p)} linhas)")

    tabela = conferir(p)
    print()
    print(tabela.to_string(index=False))
    SAIDAS.mkdir(exist_ok=True)
    tabela.to_csv(SAIDAS / "conferencia_enunciado.csv", index=False, encoding="utf-8")
    print("gravado: saidas/conferencia_enunciado.csv")


if __name__ == "__main__":
    main()
