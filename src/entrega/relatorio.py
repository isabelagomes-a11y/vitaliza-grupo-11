"""Customer Segmentation Report da semana 5 em .docx (números da base unificada de src/vitaliza).

Uso (na raiz do projeto, depois de entrega/graficos.py):  python src/entrega/relatorio.py
Grava saidas/entrega_semana5/Vitaliza_G10_Relatorio_Segmentacao.docx. O PDF sai pelo Word (Salvar como PDF).
"""
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import ENTREGA, GRUPO, INTEGRANTES, PNG, REPO, br, carregar, inteiro, n_decisoes, numero_br, sinal  # noqa: E402

SAIDA = ENTREGA / "Vitaliza_G10_Relatorio_Segmentacao.docx"
TINTA, TINTA_2, BRANCO = RGBColor(0x0B, 0x0B, 0x0B), RGBColor(0x52, 0x51, 0x4E), RGBColor(0xFF, 0xFF, 0xFF)
COR = {"A": "EB6834", "B": "2A78D6", "C": "1BAF7A", "D": "EDA100"}
FUNDO = "F3F2EE"

doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
sec.left_margin = sec.right_margin = Cm(2.0)
sec.top_margin = sec.bottom_margin = Cm(1.7)
normal = doc.styles["Normal"]
normal.font.name, normal.font.size, normal.font.color.rgb = "Calibri", Pt(10.5), TINTA
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
normal.paragraph_format.space_after, normal.paragraph_format.line_spacing = Pt(4), 1.1
for nome, tam, antes in [("Heading 1", 15, 12), ("Heading 2", 12, 8), ("Title", 22, 0)]:
    st = doc.styles[nome]
    st.font.name, st.font.size, st.font.bold, st.font.color.rgb = "Calibri", Pt(tam), True, TINTA
    st.element.rPr.rFonts.set(qn("w:asciiTheme"), "")
    st.paragraph_format.space_before, st.paragraph_format.space_after = Pt(antes), Pt(4)
    st.paragraph_format.keep_with_next = True


def sombrear(celula, cor):
    shd = OxmlElement("w:shd")
    for k, v in [("w:val", "clear"), ("w:color", "auto"), ("w:fill", cor)]:
        shd.set(qn(k), v)
    celula._tc.get_or_add_tcPr().append(shd)


def margens(tabela, cm=0.12):
    mar = OxmlElement("w:tblCellMar")
    for lado in ["top", "bottom", "left", "right"]:
        el = OxmlElement(f"w:{lado}")
        el.set(qn("w:w"), str(int(cm * 567)))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tabela._tbl.tblPr.append(mar)


def sem_bordas(tabela):
    b = OxmlElement("w:tblBorders")
    for lado in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        el = OxmlElement(f"w:{lado}")
        el.set(qn("w:val"), "nil")
        b.append(el)
    tabela._tbl.tblPr.append(b)


def p(texto="", negrito=None, tam=None, cor=None, italico=False, depois=None, centro=False):
    par = doc.add_paragraph()
    if negrito:
        r = par.add_run(negrito)
        r.bold = True
        if tam:
            r.font.size = Pt(tam)
    r = par.add_run(texto)
    r.italic = italico
    if tam:
        r.font.size = Pt(tam)
    if cor:
        r.font.color.rgb = cor
    if depois is not None:
        par.paragraph_format.space_after = Pt(depois)
    if centro:
        par.alignment = 1
    return par


def bullet(texto, negrito=None):
    par = doc.add_paragraph(style="List Bullet")
    if negrito:
        par.add_run(negrito).bold = True
    par.add_run(texto)
    par.paragraph_format.space_after = Pt(2)


def tabela(cab, linhas, larguras, tam=9):
    t = doc.add_table(rows=1, cols=len(cab))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    margens(t, 0.1)
    for i, txt in enumerate(cab):
        c = t.rows[0].cells[i]
        r = c.paragraphs[0].add_run(txt)
        r.bold, r.font.size, r.font.color.rgb = True, Pt(tam), BRANCO
        sombrear(c, "2E2E2B")
    for linha in linhas:
        cells = t.add_row().cells
        for i, txt in enumerate(linha):
            r = cells[i].paragraphs[0].add_run(txt[0] if isinstance(txt, tuple) else str(txt))
            r.bold = isinstance(txt, tuple)
            r.font.size = Pt(tam)
            cells[i].paragraphs[0].paragraph_format.space_after = Pt(0)
    for linha in t.rows:
        for i, w in enumerate(larguras):
            linha.cells[i].width = Cm(w)


def figura(nome, largura, legenda):
    doc.add_picture(str(PNG / f"{nome}.png"), width=Cm(largura))
    doc.paragraphs[-1].alignment = 1
    p(legenda, tam=8.5, cor=TINTA_2, italico=True, depois=6, centro=True)


def lado_a_lado(a, b, leg_a, leg_b, larg=8.3):
    t = doc.add_table(rows=2, cols=2)
    sem_bordas(t)
    for i, (arq, leg) in enumerate([(a, leg_a), (b, leg_b)]):
        c = t.rows[0].cells[i]
        c.paragraphs[0].add_run().add_picture(str(PNG / f"{arq}.png"), width=Cm(larg))
        c.paragraphs[0].alignment = 1
        r = t.rows[1].cells[i].paragraphs[0].add_run(leg)
        r.italic, r.font.size, r.font.color.rgb = True, Pt(8.5), TINTA_2
        t.rows[1].cells[i].paragraphs[0].alignment = 1
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def cartao(cor, titulo, numeros, campos):
    t = doc.add_table(rows=1 + len(campos), cols=2)
    sem_bordas(t)
    margens(t, 0.16)
    cab = t.rows[0].cells[0].merge(t.rows[0].cells[1])
    sombrear(cab, cor)
    texto_cab = TINTA if cor == COR["D"] else BRANCO
    r = cab.paragraphs[0].add_run(titulo)
    r.bold, r.font.size, r.font.color.rgb = True, Pt(12.5), texto_cab
    r = cab.add_paragraph().add_run(numeros)
    r.font.size, r.font.color.rgb = Pt(9.5), texto_cab
    for i, (rot, txt) in enumerate(campos, start=1):
        a, b = t.rows[i].cells
        sombrear(a, FUNDO)
        sombrear(b, FUNDO if rot in ("Evidência", "Decisão", "Limite") else "FFFFFF")
        ra = a.paragraphs[0].add_run(rot)
        ra.bold, ra.font.size = True, Pt(9.5)
        b.paragraphs[0].add_run(txt).font.size = Pt(9.5)
        a.paragraphs[0].paragraph_format.space_after = b.paragraphs[0].paragraph_format.space_after = Pt(0)
    for k, linha in enumerate(t.rows):
        linha.cells[0].width, linha.cells[1].width = Cm(2.6), Cm(14.4)
        linha._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        if k < len(t.rows) - 1:
            for c in linha.cells:
                for par in c.paragraphs:
                    par.paragraph_format.keep_with_next = True
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def main():
    n, k, d, conf = carregar()
    seg, cam, camp = n["seg"], n["cam"], n["campanha"]
    pc = lambda v: f"{br(100 * v)}%"
    ef = lambda chave, g: camp[chave]["efeitos"][g]
    s_m = d["serie_plano"]["mensal"]
    dif = [s_m[f"2026-{m}"] - s_m[f"2025-{m}"] for m in ("03", "04", "05", "06", "07")]
    rv = d["renovacoes_anuais"][2:]
    c1 = (min(x["churn_primeira"] for x in rv), max(x["churn_primeira"] for x in rv))
    c2 = (min(x["churn_seguintes"] for x in rv), max(x["churn_seguintes"] for x in rv))
    pouco_anual = cam[("A", "pouco uso")]["n"] + cam[("D", "pouco uso")]["n"]
    batem = sum(1 for c in conf if float(c["diferenca"]) == 0)

    # ---------------------------------------------------------------- capa e resumo
    doc.add_paragraph(style="Title").add_run("Quem sai da Vitaliza, quando e por onde agir")
    p(f"Customer Segmentation Report · Módulo 2, semana 5 · {GRUPO} · novembro de 2026", tam=10, cor=TINTA_2, depois=1)
    p(" · ".join(INTEGRANTES), tam=10, depois=10)

    doc.add_heading("Resumo executivo", level=1)
    p(f"A Vitaliza perde em média {pc(n['base_churn'])} dos assinantes a cada 60 dias, mas essa média esconde grupos que vão "
      f"de 0,1% a {pc(cam[('A', 'pouco uso')]['churn'])}. Analisamos os 14.032 assinantes pagantes ativos em 31/07/2026 e quem "
      f"saiu até 29/09/2026 ({inteiro(n['base_saidas'])} saídas). A base reconstruída reproduz os números oficiais da empresa (seção 1).")
    p("Quatro segmentos explicam o churn pelo momento do ciclo e pelo comportamento de uso, não pela demografia:", depois=2)
    for sg, nome, desc in [
        ("A", "A · O anual que esfriou antes de renovar:",
         f" anual com renovação nos próximos 60 dias. {br(100 * seg['A']['n'] / n['base_n'], 0)}% da base, {pc(seg['A']['churn'])} de churn, "
         f"{br(100 * seg['A']['pct_saidas'], 0)}% de todo o churn. Quem usa pouco sai {pc(cam[('A', 'pouco uso')]['churn'])}."),
        ("B", "B · O mensal que ainda está decidindo:",
         f" mensal com até 5 meses. {br(100 * seg['B']['n'] / n['base_n'], 0)}% da base, {pc(seg['B']['churn'])} de churn, "
         f"{br(100 * seg['B']['pct_saidas'], 0)}% do churn, maior receita em risco (R$ {inteiro(seg['B']['receita_risco_ano'] / 1000)} mil/ano)."),
        ("C", "C · O mensal fiel que pode escorregar:",
         f" mensal com 6 meses ou mais. {br(100 * seg['C']['n'] / n['base_n'], 0)}% da base, {pc(seg['C']['churn'])} de churn; "
         f"com queda de uso, {br(n['queda_uso']['1']['C'])}%."),
        ("D", "D · O anual garantido até a renovação:",
         f" anual com renovação depois de 60 dias. {br(100 * seg['D']['n'] / n['base_n'], 0)}% da base, 0,1% de churn agora, mas "
         f"{inteiro(cam[('D', 'pouco uso')]['n'])} usam pouco: são o A dos próximos meses."),
    ]:
        bullet(desc, nome)
    p(f"A subida do churn em 2026 tem dois suspeitos: no mensal, o churn ficou de {br(min(dif))} a {br(max(dif))} pontos acima de 2025 "
      f"entre março e julho, logo após o reajuste; no anual, a safra de 2024 chegou à 1ª renovação a partir de jul/2025, e nela sai "
      f"cerca de metade dos assinantes (nas seguintes, um terço). São associações, não prova de causa.")
    p(f"Prioridade preliminar: agir já no B e no A ativo; agir no C quando o uso cai; não contatar o anual com pouco uso "
      f"({inteiro(pouco_anual)} assinantes). A campanha sorteada de agosto mostra que o cupom reduziu o churn do mensal "
      f"({sinal(ef('B · saída', 'cupom')[0])} pontos no B e {sinal(ef('C · saída', 'cupom')[0])} no C, contra o controle) e que, no anual "
      f"com pouco uso, o contato aumentou o desligamento da renovação: a oferta precisa ser diferente por segmento.", depois=2)

    # ---------------------------------------------------------------- 1. base e método
    doc.add_heading("1. Base e método", level=1)
    p("População: assinaturas pagas ativas no fim de 31/07/2026, sem as 60 contas internas da empresa. Rótulo: a assinatura "
      "terminou nos 60 dias seguintes, o mesmo horizonte que o modelo da semana 10 vai prever. Toda variável usa só informação "
      "até 31/07/2026. Código em src/vitaliza/ (leitura, limpeza, status de cada assinatura, variáveis e segmentos).")
    linhas = [(c["item"], numero_br(c["enunciado"]), numero_br(c["reconstruido"])) for c in conf
              if c["item"] in {"ativos no início de jan/2025", "abril/2026: perdas", "setembro/2026: ativos no início",
                               "ativos em 30/09/2026 (fim do dia)", "churn médio mensal jan-set/2026 %", "fins de assinatura jun-set/2026"}]
    tabela(["Conferência com o enunciado", "Enunciado", "Reconstruído"], linhas, [9.5, 3.7, 3.8])
    p(f"{batem} de {len(conf)} números batem exatamente (saidas/conferencia_enunciado.csv).", tam=8.5, cor=TINTA_2, italico=True, depois=6)
    p(f"Principais decisões de limpeza ({n_decisoes()} em decisoes.md, cada uma com motivo, critério e linhas afetadas): datas das "
      f"lojas convertidas de UTC para horário de Brasília; {inteiro(n['cobrancas_duplicadas'])} cobranças duplicadas removidas; "
      "grafias padronizadas; valores em dois formatos convertidos; meses sem registro de uso contados como zero; idade e sexo fora "
      "de qualquer variável de decisão (não separam quem sai e não podem ser gatilho, LGPD art. 6º, IX).")

    # ---------------------------------------------------------------- 2. EDA
    doc.add_heading("2. O que a análise exploratória mostrou", level=1)
    lado_a_lado("e1_plano_tempo_casa", "e7_uso",
                "Fig. 1. No mensal o risco cai com o tempo de casa; no anual ele aparece quando a renovação cai na janela (6–11 meses).",
                f"Fig. 2. Quem não treinou sai {br(n['uso']['0'])}%, contra {br(n['uso']['8+'])}% de quem treina 8+ vezes por mês.")
    figura("e3_subida_2026", 15.5, f"Fig. 3. Mensal: de março a julho/2026, {br(min(dif))} a {br(max(dif))} pontos acima de 2025, logo após o "
                                   "reajuste; janeiro alto nos dois anos é sazonal. Anual: desde jul/2025, 2 em cada 3 renovações são a 1ª.")
    tabela(["Hipótese", "Resultado", "Veredito"], [
        ("Mensal sai mais que anual", "14,7% × 7,5%; o mensal é 41% da base e 57% do churn", ("sobreviveu",)),
        ("Pouco tempo de casa sai mais", "mensal 18–19% até 5 meses; no anual o risco é a data de renovação", ("sobreviveu no mensal",)),
        ("Uso baixo e queda de uso antecedem a saída", f"0 treino {br(n['uso']['0'])}%; queda de uso 17,3% × 9,0%", ("sobreviveu",)),
        ("Renovação desligada é o sinal mais forte", f"{br(n['renov_desl_churn'])}% × {br(n['renov_ligada_churn'])}%; AUC {br(n['auc']['renovação desligada'], 2)} (a maior)",
         ("sobreviveu; usar para priorizar",)),
        ("Reajuste de mar/2026 explica a subida de 2026",
         f"mensal: mar–jul/2026 de {br(min(dif))} a {br(max(dif))} pp acima de 2025 (abril {br(s_m['2026-04'])}% × {br(s_m['2025-04'])}%); "
         f"janeiro alto nos dois anos é sazonal. Anual: desde jul/2025, 60–77% das renovações são a 1ª (eram ~25%); na 1ª saem "
         f"{br(c1[0], 0)}–{br(c1[1], 0)}%, nas seguintes {br(c2[0], 0)}–{br(c2[1], 0)}%",
         ("confirmado no mensal; no anual é a 1ª renovação",)),
        ("Pagar no site (cartão) sai mais", "11,9% × 9,7–10,4%; mensal no cartão 18,1%", ("fraca",)),
        ("Idade e sexo separam quem sai", f"AUC {br(n['auc']['mulher'], 2)}–{br(n['auc']['idade'], 2)}", ("caiu",)),
    ], [5.2, 8.6, 3.2], tam=8.5)
    p("Cruzamento aponta suspeitos, não prova causa. A EDA completa, com a decomposição da subida e os sinais de texto, está em "
      "notebooks/eda.ipynb.", tam=8.5, cor=TINTA_2, italico=True)

    # ---------------------------------------------------------------- 3. segmentação
    doc.add_heading("3. Como chegamos aos segmentos", level=1)
    lentes = {x["k"]: x for x in k["lentes"]}
    p(f"Rodamos o k-means em cinco variáveis de comportamento e ciclo (treinos por mês, % ao ar livre, tempo de casa, meses até "
      f"a renovação e plano), padronizadas e sem o churn, e o avaliamos pelas quatro lentes da aula. A separação é fraca (silhueta "
      f"{br(min(x['silhueta'] for x in k['lentes']), 2)}–{br(max(x['silhueta'] for x in k['lentes']), 2)}) e o k = 4 é instável entre "
      f"amostras (ARI {br(lentes[4]['estabilidade_ari'], 2)}). O k-means agrupa por plano e perfil de treino, separa pouco o churn "
      f"(AUC {br(k['comparacao'][0]['auc'], 2)}) e não enxerga quando o anual pode sair. Regras de momento (plano × dias até a "
      f"renovação × tempo de casa) separam muito mais (AUC {br(k['comparacao'][1]['auc'], 2)}). A camada de comportamento também "
      f"ficou por regra: no mensal ela coincide com a do k-means (ar livre × vídeo); no anual, só a regra de uso acha quem sai "
      f"(pouco uso {pc(cam[('A', 'pouco uso')]['churn'])} × ativo {pc(cam[('A', 'ativo')]['churn'])} no A). Resultado: AUC "
      f"{br(k['comparacao'][3]['auc'], 3)}, contra {br(k['comparacao'][2]['auc'], 3)} com a camada do k-means "
      f"(notebooks/segmentacao_kmeans.ipynb).")
    lado_a_lado("e6_kmeans_regra", "e4_segmentos_camadas", "Fig. 4. Quanto cada esquema de grupos separa quem sai.",
                "Fig. 5. Saída por segmento e camada; hachurado, o anual com pouco uso que não será contatado.")

    # ---------------------------------------------------------------- 4. personas
    doc.add_heading("4. Personas", level=1)
    p("Cada persona nasce de um segmento validado. O nome descreve comportamento; idade e sexo só descrevem e não são gatilho "
      "de ação. Toda decisão tem gatilho, ação e uma hipótese a testar com grupo de controle. Os cartões de leitura rápida estão "
      "em Vitaliza_G10_Cartoes_Persona.pdf.", depois=6)
    a_cup = ef("A · saída", "cupom")
    deslig = ef("Anual pouco uso (A+D) · desligou", "cupom"), ef("Anual pouco uso (A+D) · desligou", "conteudo")
    cartao(COR["A"], "A · O anual que esfriou antes de renovar",
           f"{inteiro(seg['A']['n'])} assinantes ({br(100 * seg['A']['n'] / n['base_n'], 0)}%) · churn {pc(seg['A']['churn'])} · "
           f"{br(100 * seg['A']['pct_saidas'], 0)}% do churn · R$ {br(seg['A']['valor'], 2)}/mês líquidos · R$ {inteiro(seg['A']['receita_risco_ano'] / 1000)} mil/ano em risco", [
               ("Setup", f"Plano anual há ~{br(11.7, 0)} meses; a renovação vence nos próximos 60 dias. {br(100 * seg['A']['loja'], 0)}% pagam pela loja. Treina 1,3 vez por mês (mediana)."),
               ("Conflito", f"Quem usa pouco ({inteiro(cam[('A', 'pouco uso')]['n'])}) sai {pc(cam[('A', 'pouco uso')]['churn'])}; quem segue ativo ({inteiro(cam[('A', 'ativo')]['n'])}), {pc(cam[('A', 'ativo')]['churn'])}. {br(100 * cam[('A', 'pouco uso')]['renov'], 0)}% dos que usam pouco já desligaram a renovação."),
               ("Resolução", "O anual não sai quando desanima: sai no vencimento. O desânimo aparece meses antes, como queda de uso."),
               ("Evidência", f"{pc(seg['A']['churn'])} contra {pc(seg['A']['resto_churn'])} no resto da base; {inteiro(seg['A']['saidas'])} das {inteiro(n['base_saidas'])} saídas. Com queda de uso, {br(n['queda_uso']['1']['A'])}%."),
               ("Decisão", f"Ativo: plano de treino antes do vencimento (hipótese: −5 pp, a testar com controle). Pouco uso: não contatar. No sorteio, o contato aumentou o desligamento da renovação do anual com pouco uso (cupom +{br(deslig[0][0])} pp, conteúdo +{br(deslig[1][0])} pp, intervalos sem o zero)."),
               ("Limite", f"No A, nenhuma mensagem reduziu a saída (cupom {sinal(a_cup[0])} pp, intervalo de {sinal(a_cup[1])} a {sinal(a_cup[2])}). A maioria das saídas da base não tem motivo registrado (67%). Segmento de momento: muda todo mês."),
           ])
    b_cup, b_des = ef("B · saída", "cupom"), ef("B · saída", "desafio")
    cartao(COR["B"], "B · O mensal que ainda está decidindo",
           f"{inteiro(seg['B']['n'])} assinantes ({br(100 * seg['B']['n'] / n['base_n'], 0)}%) · churn {pc(seg['B']['churn'])} · "
           f"{br(100 * seg['B']['pct_saidas'], 0)}% do churn · R$ {br(seg['B']['valor'], 2)}/mês líquidos · R$ {inteiro(seg['B']['receita_risco_ano'] / 1000)} mil/ano em risco", [
               ("Setup", "Plano mensal há até 5 meses (mediana de 2,7). Treina 4 vezes por mês (mediana)."),
               ("Conflito", f"Sai quase 2 vezes mais que a base. Ar livre sai {pc(cam[('B', 'ar livre')]['churn'])}; vídeo, {pc(cam[('B', 'vídeo')]['churn'])}. Quem postou meta cumprida sai {br(n['meta_cumprida']['1']['B'])}%, contra {br(n['meta_cumprida']['0']['B'])}%."),
               ("Resolução", "O novato mensal reavalia a assinatura a cada cobrança; quem cumpre a meta que o trouxe tende a sair."),
               ("Evidência", f"{pc(seg['B']['churn'])} contra {pc(seg['B']['resto_churn'])} no resto. Na campanha, cupom {sinal(b_cup[0])} pp ({sinal(b_cup[1])} a {sinal(b_cup[2])}) e desafio {sinal(b_des[0])} pp, contra o controle."),
               ("Decisão", "Gatilho: 1ª a 5ª cobrança, ou meta cumprida. Ação: desafio de corrida para quem treina ao ar livre, plano em vídeo para os demais; cupom só para quem desligar a renovação. Hipótese: o desafio sem cupom reduz 4 pp a custo menor que o cupom (R$ 35,91), com controle."),
               ("Limite", "Nenhuma cobrança com desconto aparece nos pagamentos: não se sabe se o efeito veio do cupom usado ou da mensagem. O pico de abr–mai coincide com o reajuste, mas não prova causa."),
           ])
    c_cup = ef("C · saída", "cupom")
    cartao(COR["C"], "C · O mensal fiel que pode escorregar",
           f"{inteiro(seg['C']['n'])} assinantes ({br(100 * seg['C']['n'] / n['base_n'], 0)}%) · churn {pc(seg['C']['churn'])} · "
           f"{br(100 * seg['C']['pct_saidas'], 0)}% do churn · R$ {br(seg['C']['valor'], 2)}/mês líquidos · R$ {inteiro(seg['C']['receita_risco_ano'] / 1000)} mil/ano em risco", [
               ("Setup", "Plano mensal há 6 meses ou mais (mediana de 13,3). Treina 6,3 vezes por mês (mediana)."),
               ("Conflito", f"Na média, perto da base. Com queda de uso em julho sai {br(n['queda_uso']['1']['C'])}%, contra {br(n['queda_uso']['0']['C'])}%."),
               ("Resolução", "O veterano não sai por tempo de casa: sai quando o hábito quebra. A queda de uso aparece antes do aviso de renovação desligada."),
               ("Evidência", f"{br(n['queda_uso']['1']['C'])}% × {br(n['queda_uso']['0']['C'])}% com e sem queda. Na campanha, cupom {sinal(c_cup[0])} pp ({sinal(c_cup[1])} a {sinal(c_cup[2])})."),
               ("Decisão", "Gatilho: queda de treinos (mês abaixo da metade da média dos 2 anteriores), renovação desligada ou cobrança recusada. Ação: retomada com desafio ou plano. Hipótese: agir só no gatilho reduz 5 pp nos acionados com custo bem menor que contatar o segmento todo."),
               ("Limite", f"Diferença pequena contra o resto da base ({pc(seg['C']['churn'])} × {pc(seg['C']['resto_churn'])}): só faz sentido com gatilho individual."),
           ])
    cartao(COR["D"], "D · O anual garantido até a renovação",
           f"{inteiro(seg['D']['n'])} assinantes ({br(100 * seg['D']['n'] / n['base_n'], 0)}%) · churn 0,1% · "
           f"{br(100 * seg['D']['pct_saidas'], 1)}% do churn · R$ {br(seg['D']['valor'], 2)}/mês líquidos", [
               ("Setup", f"Plano anual com renovação depois de 60 dias: já pagou o ano e não pode sair antes do vencimento. {inteiro(cam[('D', 'ativo')]['n'])} seguem ativos."),
               ("Conflito", f"{inteiro(cam[('D', 'pouco uso')]['n'])} usam pouco e {br(100 * cam[('D', 'pouco uso')]['renov'], 0)}% deles já desligaram a renovação. Quando chegam à renovação usando pouco, saem {pc(cam[('A', 'pouco uso')]['churn'])} (A)."),
               ("Resolução", "O churn do anual se decide meses antes da renovação."),
               ("Evidência", f"{inteiro(seg['D']['saidas'])} saídas na janela. Na renovação, pouco uso = {pc(cam[('A', 'pouco uso')]['churn'])} contra {pc(cam[('A', 'ativo')]['churn'])} dos ativos."),
               ("Decisão", "Ativo: proteger, sem oferta. Pouco uso: não contatar agora (o contato aumentou o desligamento no sorteio); monitorar todo mês e testar, com controle, uma abordagem diferente antes da renovação."),
               ("Limite", "O efeito de qualquer ação só aparece na renovação, fora da janela de 60 dias."),
           ])

    # ---------------------------------------------------------------- 5. priorização
    doc.add_heading("5. Priorização preliminar", level=1)
    figura("e5_campanha", 13.5, "Fig. 6. Efeito de cada mensagem da campanha sorteada de agosto, contra o controle (intervalo de 95%).")
    rot = {"Imediata": "Imediata", "Imediata no gatilho": "Imediata no gatilho", "Proteger": "Proteger", "Não contatar": "Não contatar"}
    tabela(["Segmento · camada", "Assinantes", "Saída", "R$/mês", "Ação"],
           [(f"{p_['segmento']} · {p_['camada']}", inteiro(p_["n"]), pc(p_["churn"]), br(p_["valor"], 2), (rot[p_["acao"]],))
            for p_ in n["priorizacao"]], [4.2, 2.4, 2.2, 2.2, 6.0], tam=8.5)
    p("Dentro de qualquer segmento contatado, quem já desligou a renovação sobe para o topo da fila. O teto do CRM (1.500 WhatsApp "
      "e 300 atendimentos por mês) não cobre todo o B; a divisão por canal e o ROI ficam para o plano de intervenção da semana 10.",
      depois=4)

    # ---------------------------------------------------------------- 6. limitações
    doc.add_heading("6. Limitações da análise", level=1)
    for neg, txt in [
        ("Associação, não causa. ", "Só a campanha sorteada de agosto mede efeito; os demais efeitos de ação são hipóteses a testar."),
        ("Motivo da saída. ", "67% das saídas não têm motivo registrado; a pesquisa de saída só alcança quem paga pelo site e responde (~10%, viés de seleção)."),
        ("Campanha dentro da janela. ", "O cupom reduziu a saída dos grupos tratados; o churn medido fica um pouco abaixo do que seria sem campanha."),
        ("Segmentos de momento. ", "No anual o segmento depende da data de renovação e muda todo mês; precisa ser recalculado mensalmente."),
        ("Separação fraca. ", "Silhueta abaixo de 0,32 em qualquer k: os grupos são cortes úteis, não tipos naturais de cliente."),
        ("Dados de uso. ", "O uso mensal diverge do registro de treinos em parte dos meses, e meses sem registro foram tratados como zero."),
        ("Dados de entrada. ", "Cadastro e onboarding descrevem a entrada, não o momento da decisão; idades impossíveis foram limitadas a 14–90 anos e só descrevem."),
    ]:
        bullet(txt, neg)

    doc.add_heading("Anexo · Como reproduzir", level=2)
    p(f"Repositório {REPO}, branch main. Os dados brutos não vão para o Git. Na raiz do projeto: src/build_eda.py (EDA, gráficos e "
      "números), src/build_kmeans.py (k-means de apoio), src/conferencia_enunciado.py (conferência), src/completude.py <base> "
      "(qualidade) e, para estes documentos, src/entrega/dados.py, graficos.py, relatorio.py e minideck.py. Todas as "
      f"{n_decisoes()} decisões estão em decisoes.md, com motivo, critério, linhas afetadas e onde cada uma é aplicada no código.",
      tam=9.5)

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    doc.save(SAIDA)
    print("gravado:", SAIDA.name)


if __name__ == "__main__":
    main()
