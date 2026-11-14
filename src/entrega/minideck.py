"""Mini deck da semana 5 (apresentação executiva para Tecnologia): capa + 5 slides, em .pptx.

Uso (na raiz do projeto, depois de entrega/graficos.py):  python src/entrega/minideck.py
Grava saidas/entrega_semana5/Vitaliza_G10_MiniDeck_EDA.pptx. O PDF sai pelo PowerPoint (Salvar como PDF).
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import ENTREGA, GRUPO, INTEGRANTES, PNG, REPO, br, carregar, inteiro, n_decisoes  # noqa: E402

SAIDA = ENTREGA / "Vitaliza_G10_MiniDeck_EDA.pptx"
ESCURO, TINTA, TINTA_2 = RGBColor(0x2E, 0x2E, 0x2B), RGBColor(0x0B, 0x0B, 0x0B), RGBColor(0x52, 0x51, 0x4E)
CLARO, BRANCO, CARTAO = RGBColor(0xC3, 0xC2, 0xB7), RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0xF3, 0xF2, 0xEE)
LARANJA, AZUL, VERDE, AMARELO = RGBColor(0xEB, 0x68, 0x34), RGBColor(0x2A, 0x78, 0xD6), RGBColor(0x1B, 0xAF, 0x7A), RGBColor(0xED, 0xA1, 0x00)
ROSA, AZUL_CLARO = RGBColor(0xFC, 0xE4, 0xD9), RGBColor(0xDD, 0xE9, 0xF8)
TITULO, CORPO = "Cambria", "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
VAZIO = prs.slide_layouts[6]


def texto(s, x, y, w, h, linhas, tam=14, cor=TINTA, negrito=False, fonte=CORPO, alinhar=PP_ALIGN.LEFT,
          ancora=MSO_ANCHOR.TOP, espaco=6):
    caixa = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = caixa.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = ancora
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    for i, linha in enumerate([linhas] if isinstance(linhas, str) else linhas):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.alignment = alinhar
        par.space_after = Pt(espaco)
        for conteudo, opc in (linha if isinstance(linha, list) else [(linha, {})]):
            r = par.add_run()
            r.text = conteudo
            r.font.name = opc.get("fonte", fonte)
            r.font.size = Pt(opc.get("tam", tam))
            r.font.bold = opc.get("negrito", negrito)
            r.font.color.rgb = opc.get("cor", cor)
    return caixa


def caixa(s, x, y, w, h, cor):
    f = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    f.fill.solid()
    f.fill.fore_color.rgb = cor
    f.line.fill.background()
    f.shadow.inherit = False
    f.adjustments[0] = 0.07
    return f


def cabecalho(s, titulo, sub, n):
    texto(s, 0.6, 0.4, 12.1, 0.8, titulo, tam=30, negrito=True, fonte=TITULO)
    texto(s, 0.6, 1.12, 12.1, 0.4, sub, tam=14, cor=TINTA_2)
    texto(s, 0.6, 7.05, 10, 0.3, f"Vitaliza · {GRUPO} · EDA e segmentação (semana 5) · base: 14.032 assinantes ativos em 31/07/2026",
          tam=10, cor=TINTA_2)
    texto(s, 12.2, 7.05, 0.55, 0.3, str(n), tam=10, cor=TINTA_2, alinhar=PP_ALIGN.RIGHT)


def figura(s, nome, x, y, w=None, h=None):
    kw = {"width": Inches(w)} if w else {"height": Inches(h)}
    s.shapes.add_picture(str(PNG / f"{nome}.png"), Inches(x), Inches(y), **kw)


def destaque(s, x, y, w, h, fundo, cor, numero, frase):
    caixa(s, x, y, w, h, fundo)
    texto(s, x + 0.22, y + 0.15, w - 0.44, h - 0.3, [[(numero, {"tam": 28, "negrito": True, "cor": cor, "fonte": TITULO})], frase],
          tam=13, cor=TINTA)


def main():
    n, k, d, conf = carregar()
    seg, cam = n["seg"], n["cam"]
    batem = sum(1 for c in conf if float(c["diferenca"]) == 0)
    s_m = d["serie_plano"]["mensal"]
    camp = n["campanha"]

    # ---------------------------------------------------------------- capa
    s = prs.slides.add_slide(VAZIO)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = ESCURO
    texto(s, 0.8, 0.95, 11.7, 0.4, f"VITALIZA · MÓDULO 2 · SEMANA 5 · {GRUPO.upper()}", tam=13, cor=CLARO, negrito=True)
    texto(s, 0.8, 1.45, 11.7, 1.6, "O que separa quem sai da Vitaliza", tam=46, negrito=True, cor=BRANCO, fonte=TITULO)
    texto(s, 0.8, 2.55, 11.7, 0.6, "Apresentação executiva: processo analítico e insights da análise exploratória e da segmentação",
          tam=17, cor=CLARO)
    for i, (valor, rot, cor) in enumerate([("14.032", "assinantes ativos em 31/07/2026", BRANCO),
                                           (f"{br(100 * n['base_churn'])}%", f"saíram em 60 dias ({inteiro(n['base_saidas'])})", LARANJA),
                                           ("4", "segmentos de momento, com camada de comportamento", RGBColor(0x86, 0xB6, 0xEF))]):
        texto(s, 0.8 + i * 3.9, 3.75, 3.6, 0.9, valor, tam=44, negrito=True, cor=cor, fonte=TITULO)
        texto(s, 0.8 + i * 3.9, 4.65, 3.5, 0.6, rot, tam=13, cor=CLARO)
    texto(s, 0.8, 5.75, 11.7, 0.45, " · ".join(INTEGRANTES), tam=16, cor=BRANCO, negrito=True)
    texto(s, 0.8, 6.25, 11.7, 0.4, f"Repositório: {REPO} · código em src/vitaliza/ · decisões em decisoes.md", tam=12, cor=CLARO)
    s.notes_slide.notes_text_frame.text = (
        "Entrega parcial de Tecnologia: análise exploratória e segmentos, com perfil, tamanho e saída de cada um. "
        "As três peças: repositório (código versionado), documentação (decisões e motivo em decisoes.md) e esta apresentação.")

    # ---------------------------------------------------------------- 1. processo e decisões
    s = prs.slides.add_slide(VAZIO)
    cabecalho(s, "Processo analítico: do data room aos segmentos",
              f"Cada etapa está no repositório; cada decisão de limpeza e de método está em decisoes.md ({n_decisoes()} decisões, com motivo)", 1)
    etapas = [
        ("1 · Qualidade", "completude e criticidade das 5 bases usadas", "src/completude.py"),
        ("2 · Limpeza", f"fuso UTC → Brasília (68% dos eventos); {inteiro(n['cobrancas_duplicadas'])} cobranças duplicadas fora; 60 contas internas fora",
         "src/vitaliza/base.py · features.py"),
        ("3 · Base", f"32.643 assinaturas → 14.032 ativas em 31/07 → {inteiro(n['base_saidas'])} saídas em 60 dias; {batem} de {len(conf)} números do enunciado batem",
         "conferencia_enunciado.py"),
        ("4 · EDA", "série 2025–2026; 15 variáveis medidas por AUC; campanha por segmento", "notebooks/eda.ipynb"),
        ("5 · Segmentação", "k-means avaliado em 4 lentes contra regras de momento; fica a regra", "segmentacao_kmeans.ipynb"),
    ]
    larg, x0 = 2.38, 0.6
    for i, (tit, desc, onde) in enumerate(etapas):
        x = x0 + i * (larg + 0.1)
        caixa(s, x, 1.75, larg, 2.35, ROSA if i == 4 else CARTAO)
        texto(s, x + 0.16, 1.9, larg - 0.32, 2.1, [[(tit, {"negrito": True, "tam": 15, "fonte": TITULO})], desc,
                                                   [(onde, {"tam": 10.5, "cor": TINTA_2})]], tam=12)
    texto(s, 0.6, 4.35, 12.1, 0.35, "Decisões que mudaram o resultado", tam=16, negrito=True, fonte=TITULO)
    decisoes = [
        ("Base = ativos em 31/07; saída em 60 dias", "mesmo horizonte do modelo da semana 10; nenhuma variável usa dado posterior"),
        ("Idade e sexo fora de qualquer gatilho", "não separam quem sai (AUC 0,50) e não podem decidir oferta (LGPD, art. 6º, IX)"),
        ("Camada por regra, não por k-means", f"k = 4 instável (ARI {br(k['lentes'][1]['estabilidade_ari'], 2)}); regra separa mais (AUC {br(k['comparacao'][3]['auc'], 3)} × {br(k['comparacao'][2]['auc'], 3)})"),
        ("Anual com pouco uso: não contatar", "no sorteio de agosto, o contato aumentou o desligamento da renovação (cupom +5,9 pp)"),
    ]
    for i, (dec, motivo) in enumerate(decisoes):
        col, lin = i % 2, i // 2
        x, y = 0.6 + col * 6.1, 4.85 + lin * 1.0
        texto(s, x, y, 5.9, 0.95, [[(dec, {"negrito": True})], [(motivo, {"cor": TINTA_2, "tam": 13})]], tam=14, espaco=2)
    s.notes_slide.notes_text_frame.text = (
        "O professor pediu repositório, documentação das decisões com motivo e a apresentação do processo e dos insights. "
        "A conferência com o enunciado (17 de 17) prova que a base reconstruída reproduz a série oficial antes de qualquer análise.")

    # ---------------------------------------------------------------- 2. o que separa quem sai
    s = prs.slides.add_slide(VAZIO)
    cabecalho(s, "Momento e uso separam quem sai; demografia não",
              "Saída em 60 dias por plano e tempo de casa; ao lado, quanto cada variável separa sozinha (AUC)", 2)
    figura(s, "e1_plano_tempo_casa", 0.6, 1.7, w=7.7)
    a = n["auc"]
    destaque(s, 8.65, 1.75, 4.1, 1.55, ROSA, LARANJA, br(a["renovação desligada"], 2),
             f"renovação desligada: {br(n['renov_desl_churn'])}% saem e são {br(100 * n['renov_desl_share_saidas'], 0)}% das saídas. É decisão já tomada: prioriza, não segmenta")
    destaque(s, 8.65, 3.45, 4.1, 1.55, AZUL_CLARO, AZUL, f"{br(a['treinos/mês'], 2)}–{br(a['dias desde o último treino'], 2)}",
             f"uso: quem não treinou sai {br(n['uso']['0'])}%, contra {br(n['uso']['8+'])}% de quem treina 8 ou mais vezes por mês")
    destaque(s, 8.65, 5.15, 4.1, 1.55, CARTAO, TINTA_2, f"{br(a['mulher'], 2)}–{br(a['idade'], 2)}",
             "idade e sexo: não separam quem sai. No anual, o risco está na data de renovação, não no tempo de casa")
    s.notes_slide.notes_text_frame.text = (
        "Mensal: o risco cai com o tempo de casa. Anual: quase ninguém sai até 5 meses e o pico é em 6-11 meses, quando a renovação "
        "cai na janela. Por isso o segmento do anual usa os dias até a renovação, não o tempo de casa.")

    # ---------------------------------------------------------------- 3. subida de 2026
    s = prs.slides.add_slide(VAZIO)
    cabecalho(s, "2026: reajuste no mensal e 1ª renovação no anual",
              "Churn do mês = perdas no mês ÷ ativos no início do mês. Cruzamento aponta suspeitos, não prova causa", 3)
    figura(s, "e3_subida_2026", 0.6, 1.7, w=8.3)
    dif = [s_m[f"2026-{m}"] - s_m[f"2025-{m}"] for m in ("03", "04", "05", "06", "07")]
    r = d["renovacoes_anuais"]
    destaque(s, 9.2, 1.75, 3.55, 2.45, AZUL_CLARO, AZUL, f"+{br(min(dif))} a +{br(max(dif))} pp",
             f"no mensal de mar a jul/2026 contra 2025, logo após o reajuste (abril: {br(s_m['2026-04'])}% × {br(s_m['2025-04'])}%). Janeiro alto nos dois anos é sazonal")
    destaque(s, 9.2, 4.4, 3.55, 2.45, ROSA, LARANJA, "1 em 4 → 2 em 3",
             f"renovações do anual que são a 1ª, a partir de jul/2025. Na 1ª saem {br(min(x['churn_primeira'] for x in r[2:]), 0)}–{br(max(x['churn_primeira'] for x in r[2:]), 0)}%; nas seguintes, {br(min(x['churn_seguintes'] for x in r[2:]), 0)}–{br(max(x['churn_seguintes'] for x in r[2:]), 0)}%")
    s.notes_slide.notes_text_frame.text = (
        "Revisa a hipótese do reajuste: jan/2026 alto não indica que a subida começou antes, porque jan/2025 também foi alto. "
        f"Comparando o mensal com o anual (que não teve reajuste), a diferença atribui cerca de {br(n['did_preco'])} pp ao preço "
        "entre março e maio. No anual a subida é de composição: a safra de 2024 chegou à 1ª renovação, quando mais gente desiste.")

    # ---------------------------------------------------------------- 4. segmentos
    s = prs.slides.add_slide(VAZIO)
    cabecalho(s, "Quatro segmentos de momento, com perfil, tamanho e saída",
              "Regra: plano × dias até a renovação × tempo de casa; camada: anual ativo × pouco uso, mensal ar livre × vídeo", 4)
    figura(s, "e4_segmentos_camadas", 0.6, 1.65, w=7.8)
    linhas = [("Segmento", "n (% base)", "Saída", "% das saídas")]
    nomes = {"A": "A · anual renova em ≤ 60 dias", "B": "B · mensal até 5 meses", "C": "C · mensal 6+ meses", "D": "D · anual renova depois"}
    for sg in "ABCD":
        x = seg[sg]
        linhas.append((nomes[sg], f"{inteiro(x['n'])} ({br(100 * x['n'] / n['base_n'], 0)}%)", f"{br(100 * x['churn'])}%",
                       f"{br(100 * x['pct_saidas'], 0)}%"))
    tab = s.shapes.add_table(5, 4, Inches(8.6), Inches(1.75), Inches(4.15), Inches(2.3)).table
    for j, w in enumerate([1.85, 0.95, 0.65, 0.7]):
        tab.columns[j].width = Inches(w)
    for i, lin in enumerate(linhas):
        for j, v in enumerate(lin):
            c = tab.cell(i, j)
            c.text = v
            rr = c.text_frame.paragraphs[0].runs[0]
            rr.font.size, rr.font.name, rr.font.bold = Pt(11), CORPO, i == 0
            rr.font.color.rgb = BRANCO if i == 0 else TINTA
            c.fill.solid()
            c.fill.fore_color.rgb = ESCURO if i == 0 else (CARTAO if i % 2 else BRANCO)
            c.margin_left = c.margin_right = Inches(0.06)
    texto(s, 8.6, 4.35, 4.15, 2.5, [
        [("Perfil: ", {"negrito": True}), (f"A tem mediana de {br(11.7)} meses de casa e 1,3 treino/mês; B, {br(2.7)} meses; "
                                            f"C, {br(13.3)} meses e 6,3 treinos/mês.", {})],
        [("Dentro do A: ", {"negrito": True}), (f"pouco uso sai {br(100 * cam[('A', 'pouco uso')]['churn'])}%; ativo, {br(100 * cam[('A', 'ativo')]['churn'])}%.", {})],
        [("Por que regra: ", {"negrito": True}), (f"o k-means sozinho separa pouco (AUC {br(k['comparacao'][0]['auc'], 2)}) e não acha o pouco uso do anual.", {})],
    ], tam=13)
    s.notes_slide.notes_text_frame.text = (
        "Os segmentos mudam todo mês no anual (dependem da data de renovação). O D tem churn quase zero porque o anual não sai antes "
        f"da renovação, mas {inteiro(cam[('D', 'pouco uso')]['n'])} usam pouco: são o A dos próximos meses.")

    # ---------------------------------------------------------------- 5. campanha e onde agir
    s = prs.slides.add_slide(VAZIO)
    cabecalho(s, "Cupom retém o mensal; contatar o anual parado piora",
              "Sorteio de 10/08/2026 com grupo de controle: o único resultado causal da análise. Ao lado, a prioridade de ação", 5)
    figura(s, "e5_campanha", 0.6, 1.65, w=7.6)
    ef = lambda chave, g: camp[chave]["efeitos"][g][0]
    acoes = [(AZUL, "Imediata", f"B · mensal novato ({inteiro(seg['B']['n'])}): desafio ou plano; cupom (−{br(-ef('B · saída', 'cupom'))} pp) se desligar"),
             (LARANJA, "Imediata", f"A · ativo ({inteiro(cam[('A', 'ativo')]['n'])}): plano de treino antes do vencimento"),
             (VERDE, "No gatilho", f"C · queda de uso: risco vai de {br(n['queda_uso']['0']['C'])}% para {br(n['queda_uso']['1']['C'])}%"),
             (TINTA_2, "Não contatar", f"anual com pouco uso ({inteiro(cam[('A', 'pouco uso')]['n'] + cam[('D', 'pouco uso')]['n'])}): monitorar e testar outra abordagem")]
    for i, (cor, rot, desc) in enumerate(acoes):
        y = 1.8 + i * 1.05
        c = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(8.55), Inches(y + 0.08), Inches(0.3), Inches(0.3))
        c.fill.solid()
        c.fill.fore_color.rgb = cor
        c.line.fill.background()
        texto(s, 9.0, y, 3.75, 0.95, [[(rot + ": ", {"negrito": True}), (desc, {})]], tam=13)
    caixa(s, 8.55, 6.05, 4.2, 0.82, CARTAO)
    texto(s, 8.72, 6.12, 3.9, 0.7, [[("Limites: ", {"negrito": True}),
                                     ("associação não é causa fora do sorteio; 67% das saídas sem motivo; a campanha caiu dentro da janela.", {})]],
          tam=11, cor=TINTA_2)
    s.notes_slide.notes_text_frame.text = (
        f"No mensal o cupom reduziu a saída em {br(-ef('B · saída', 'cupom'))} pp no B e {br(-ef('C · saída', 'cupom'))} pp no C; o desafio vai "
        "na mesma direção sem custo de desconto. No anual que renova (A) nenhuma mensagem reteve, e no anual com pouco uso o contato "
        f"aumentou o desligamento da renovação (cupom +{br(ef('Anual pouco uso (A+D) · desligou', 'cupom'))} pp, conteúdo "
        f"+{br(ef('Anual pouco uso (A+D) · desligou', 'conteudo'))} pp, intervalos sem o zero). Por isso a decisão de não contatar.")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    prs.save(SAIDA)
    print("gravado:", SAIDA.name)


if __name__ == "__main__":
    main()
