"""Gera 'Vitaliza — Fluxograma do sistema.drawio' (3 páginas)."""
from xml.sax.saxutils import escape

F = "fontFamily=Helvetica;fontColor=#1e293b;"
CARD = "rounded=1;arcSize=14;whiteSpace=wrap;html=1;strokeColor=none;shadow=1;fontSize=12;spacing=8;" + F
ST = {
    "code": CARD + "fillColor=#e0ecff;",
    "llm": CARD + "fillColor=#efe4ff;",
    "human": CARD + "fillColor=#dcfce7;",
    "crm": CARD + "fillColor=#ffedd5;",
    "none": "rounded=1;arcSize=14;whiteSpace=wrap;html=1;fillColor=#f8fafc;strokeColor=#94a3b8;dashed=1;dashPattern=4 4;fontSize=12;fontColor=#64748b;fontFamily=Helvetica;",
    "data": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;size=9;fillColor=#f1f5f9;strokeColor=#cbd5e1;fontSize=11;spacing=4;" + F,
    "dec": "rhombus;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=none;shadow=1;fontSize=11;spacing=10;" + F,
    "doc": "shape=document;whiteSpace=wrap;html=1;boundedLbl=1;size=0.18;fillColor=#ffffff;strokeColor=#cbd5e1;fontSize=11;" + F,
    "start": "rounded=1;arcSize=50;whiteSpace=wrap;html=1;fillColor=#0f172a;strokeColor=none;fontColor=#ffffff;fontSize=12;fontStyle=1;shadow=1;fontFamily=Helvetica;",
    "title": "text;html=1;align=left;verticalAlign=top;fontSize=24;fontStyle=1;" + F,
    "text": "text;html=1;align=left;verticalAlign=top;fontSize=12;whiteSpace=wrap;fontColor=#475569;fontFamily=Helvetica;",
    "note": "rounded=1;arcSize=8;whiteSpace=wrap;html=1;fillColor=#fffbeb;strokeColor=#fcd34d;fontSize=11;align=left;verticalAlign=top;spacing=10;" + F,
    "done": CARD + "fillColor=#dcfce7;align=left;verticalAlign=top;fontSize=11;",
    "pend": CARD + "fillColor=#fef3c7;align=left;verticalAlign=top;fontSize=11;",
    "future": "rounded=1;arcSize=14;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#94a3b8;dashed=1;dashPattern=4 4;align=left;verticalAlign=top;spacing=8;fontSize=11;" + F,
    "gate": "rhombus;whiteSpace=wrap;html=1;fillColor=#0f172a;strokeColor=none;fontColor=#ffffff;fontSize=11;fontStyle=1;spacing=12;shadow=1;fontFamily=Helvetica;",
    "lane": "swimlane;startSize=30;html=1;rounded=1;arcSize=4;fillColor=#f1f5f9;swimlaneFillColor=#ffffff;strokeColor=#e2e8f0;fontSize=12;fontStyle=1;fontColor=#334155;fontFamily=Helvetica;",
    "band": "rounded=0;whiteSpace=wrap;html=1;fillColor=#0f172a;strokeColor=none;",
}
ICON = {"code": "⚙️ ", "llm": "✨ ", "human": "👥 ", "crm": "📨 ", "none": "🚫 ", "data": "🗄️ ", "done": "✅ ", "pend": "⏳ ", "future": "🧪 "}
E = "edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=classic;endFill=1;endSize=7;strokeColor=#94a3b8;strokeWidth=1.6;fontSize=11;fontColor=#475569;fontFamily=Helvetica;labelBackgroundColor=#ffffff;"
ED = E + "dashed=1;dashPattern=6 4;strokeColor=#16a34a;fontColor=#15803d;"


class Page:
    def __init__(self, name):
        self.name, self.cells, self.n = name, [], 2

    def box(self, kind, x, y, w, h, label, extra=""):
        cid = f"c{self.n}"; self.n += 1
        if label and kind in ICON and w > 60:
            label = ICON[kind] + label
        self.cells.append(f'<mxCell id="{cid}" value="{escape(label, {chr(34): "&quot;"})}" style="{ST[kind]}{extra}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def edge(self, a, b, label="", style=E, pts=None, extra=""):
        cid = f"e{self.n}"; self.n += 1
        geo = '<mxGeometry relative="1" as="geometry">'
        if pts:
            geo += '<Array as="points">' + "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts) + "</Array>"
        geo += "</mxGeometry>"
        self.cells.append(f'<mxCell id="{cid}" value="{escape(label)}" style="{style}{extra}" edge="1" parent="1" source="{a}" target="{b}">{geo}</mxCell>')

    def xml(self, pid):
        body = "".join(self.cells)
        return (f'<diagram id="{pid}" name="{escape(self.name)}"><mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" '
                f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="1900" math="0" shadow="0" background="#f8fafc">'
                f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root></mxGraphModel></diagram>')


def legend(p, x, y):
    p.box("text", x, y, 260, 20, "<b>Legenda: quem executa</b>")
    items = [("code", "⚙️ Código (automático)"), ("llm", "✨ LLM (IA generativa)"), ("human", "👥 Pessoas (revisão e aprovação)"),
             ("crm", "📨 Ferramenta de CRM (envio)"), ("dec", "❓ Pergunta da regra"), ("data", "🗄️ Dados guardados"), ("none", "🚫 Sem contato")]
    for i, (k, t) in enumerate(items):
        p.box(k, x, y + 26 + i * 34, 30, 24, "" if k != "dec" else "", "")
        p.box("text", x + 40, y + 28 + i * 34, 220, 22, t)


# =================================================================== página 1: operação
p1 = Page("1 · Como o sistema roda (todo mês)")
p1.box("text", 40, 0, 600, 18, "<b style=\"color:#2563eb;letter-spacing:1px\">VITALIZA · MÓDULO 2 · INTELI</b>")
p1.box("title", 40, 20, 900, 30, "Vitaliza · Sistema de retenção: execução mensal")
p1.box("text", 40, 56, 860, 40, "Entrada: <b>a base inteira de pagantes ativos</b>, todo dia 1. Saída: para cada assinante, o risco, a decisão e a mensagem. A decisão vem de uma <b>tabela de regras aprovada por pessoas</b>; o LLM só extrai campos e escreve o texto.")
legend(p1, 1080, 30)

X, W = 420, 280
s = p1.box("start", X + 40, 110, 200, 56, "Dia 1 do mês")
src = p1.box("data", 80, 190, 240, 90, "<b>Fontes</b><br>app, lojas (Apple/Google), pagamentos, suporte, rede social")
n1 = p1.box("code", X, 200, W, 70, "<b>1 · Dados</b><br>reconstrói o status de cada assinatura pelos eventos, limpa e seleciona os pagantes ativos")
n2 = p1.box("llm", X, 300, W, 70, "<b>2 · Extração</b><br>lê só as frases novas de posts, chamados e questionário e devolve campos: meta cumprida, GPS, lesão…")
cache = p1.box("data", 780, 300, 220, 70, "Cache de frases já extraídas")
n3 = p1.box("code", X, 400, W, 60, "<b>3 · Variáveis</b><br>uso, rede, cobrança, renovação, texto")
n4 = p1.box("code", X, 490, W, 70, "<b>4 · Modelo de risco</b><br>probabilidade de sair em 60 dias (pesos aprendidos dos dados)")
model = p1.box("data", 780, 490, 220, 70, "Modelo treinado<br>(retreino mensal)")
n5 = p1.box("code", X, 590, W, 60, "<b>5 · Decisão</b><br>aplica a tabela de regras a cada pessoa")
rules = p1.box("data", 780, 585, 220, 70, "<b>Tabela de regras</b><br>versão aprovada pelo comitê")

d1 = p1.box("dec", X + 30, 680, 220, 110, "Já desligou a renovação?")
d1b = p1.box("dec", 90, 690, 220, 110, "Está entre os 300 de maior risco?")
cs = p1.box("crm", 90, 850, 220, 60, "Ligação do CS: oferta de pausa de 60 dias (teste)")
lost = p1.box("none", 90, 950, 220, 50, "Não contatar (perdidos)")
d2 = p1.box("dec", X + 30, 830, 220, 120, "Anual com ≤ 1 dia ativo nos últimos 2 meses?")
quiet = p1.box("none", 780, 860, 220, 60, "Não contatar<br>(não perturbe)")
a1 = p1.box("code", X, 990, W, 50, "Ação: <b>desafio</b> por push + e-mail")
d3 = p1.box("dec", X + 30, 1070, 220, 110, "Está entre os 1.500 de maior risco?")
wa = p1.box("code", 780, 1095, 220, 60, "+ WhatsApp (teste)")
ctl = p1.box("code", X, 1220, W, 60, "<b>Sorteia controle de 10%</b><br>que não recebe nada (para medir)")
lista = p1.box("doc", 780, 1230, 220, 70, "Lista do mês<br>(risco + ação por pessoa)")
n6 = p1.box("llm", X, 1320, W, 70, "<b>6 · Mensagem</b><br>escreve o texto de cada pessoa a partir da decisão e dos campos extraídos")
brief = p1.box("data", 780, 1320, 220, 70, "Briefing + guardrails<br>(tom, ofertas, proibições)")
h1 = p1.box("human", X, 1420, W, 60, "Filtro automático + revisão humana de uma amostra")
crm = p1.box("crm", X, 1510, W, 60, "<b>CRM envia</b> push, e-mail e WhatsApp<br>(o LLM não envia nada)")
n7 = p1.box("code", X, 1610, W, 60, "<b>7 · Medição</b> após 60 dias:<br>saída dos contatados × controle")
h2 = p1.box("human", X, 1710, W, 70, "<b>Comitê mensal</b><br>revisa os números, ajusta a regra e aprova a nova versão")

p1.edge(s, n1); p1.edge(src, n1); p1.edge(n1, n2); p1.edge(n2, cache, "", E + "endArrow=none;dashed=1;")
p1.edge(n2, n3); p1.edge(n3, n4); p1.edge(model, n4, "", E + "dashed=1;"); p1.edge(n4, n5); p1.edge(rules, n5, "", E + "dashed=1;")
p1.edge(n5, d1)
p1.edge(d1, d1b, "Sim"); p1.edge(d1b, cs, "Sim"); p1.edge(d1b, lost, "Não", E, [(60, 745), (60, 975)])
p1.edge(d1, d2, "Não"); p1.edge(d2, quiet, "Sim"); p1.edge(d2, a1, "Não"); p1.edge(a1, d3)
p1.edge(d3, wa, "Sim"); p1.edge(d3, ctl, "Não"); p1.edge(wa, ctl, "", E + "exitX=0;exitY=0.5;entryX=1;entryY=0.2;", [(740, 1125), (740, 1232)])
p1.edge(ctl, lista, "", E + "dashed=1;exitX=1;exitY=0.75;entryX=0;entryY=0.5;"); p1.edge(ctl, n6); p1.edge(brief, n6, "", E + "dashed=1;")
p1.edge(n6, h1); p1.edge(h1, crm); p1.edge(cs, crm, "", E + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;", [(345, 880), (345, 1540)]); p1.edge(crm, n7); p1.edge(n7, h2)
p1.edge(h2, rules, "nova versão da regra", ED, [(1060, 1745), (1060, 620)])
p1.edge(h2, model, "retreino", ED, [(1100, 1760), (1100, 525)])
p1.edge(h2, s, "próximo mês", E + "dashed=1;", [(380, 1745), (380, 138)])
p1.box("note", 760, 1420, 260, 170, "<b>Exemplo</b><br>Ana, mensal, treinou 6 dias em setembro, renovação ligada, risco de 38%.<br>→ não desligou · não é anual dorminhoco → <b>desafio</b> · está no top 1.500 → <b>+ WhatsApp</b> · não caiu no controle → o LLM escreve o texto → o CRM envia.")

# =================================================================== página 2: enquadramento
p2 = Page("2 · Como o assinante é enquadrado")
p2.box("text", 40, 4, 600, 18, "<b style=\"color:#2563eb;letter-spacing:1px\">VITALIZA · MÓDULO 2 · INTELI</b>")
p2.box("title", 40, 20, 1000, 30, "Três rótulos por assinante, cada um com uma função")
p2.box("text", 40, 56, 1100, 40, "Não existe um perfil único por semelhança. A ação vem da <b>célula</b> (regras sem pesos); a <b>nota de risco</b> (pesos aprendidos) só prioriza os canais escassos; o <b>segmento</b> (distância) só ajusta o tom da mensagem.")
inp = p2.box("start", 520, 110, 240, 60, "Assinante ativo no dia 1")
c1 = p2.box("code", 60, 220, 340, 230, "<b>Célula de decisão</b><br><i>regras se/então · sem pesos</i><br><br>Perguntas fixas:<br>• plano (mensal/anual)<br>• renovação desligada?<br>• dias ativos nos últimos 2 meses<br><br><b>Define a ação</b>: desafio, nenhum contato ou CS", ";align=left;verticalAlign=top;")
c2 = p2.box("code", 470, 220, 340, 230, "<b>Nota de risco</b><br><i>modelo (gradient boosting) · pesos aprendidos</i><br><br>~50 variáveis (uso, cobrança, rede, texto) combinadas → probabilidade de 0 a 100% de sair em 60 dias.<br><br><b>Prioriza</b> quem recebe WhatsApp (1.500) e CS (300)", ";align=left;verticalAlign=top;")
c3 = p2.box("code", 880, 220, 340, 230, "<b>Segmento</b><br><i>k-means · centro mais próximo · pesos iguais após padronização</i><br><br>Assíduos, Treinam em grupo, Moderados (com e sem rede), Recém-chegados, Renovação desligada.<br><br><b>Ajusta o tom</b> da mensagem e a comunicação interna", ";align=left;verticalAlign=top;")
out = p2.box("code", 470, 510, 340, 70, "<b>Decisão final por pessoa</b><br>ação + canal + prioridade + tom")
llm = p2.box("llm", 470, 630, 340, 60, "LLM escreve o texto (não decide)")
crm2 = p2.box("crm", 470, 740, 340, 50, "CRM envia")
for c in (c1, c2, c3):
    p2.edge(inp, c)
p2.edge(c1, out, "ação", E + "exitX=0.5;exitY=1;entryX=0.2;entryY=0;", [(230, 485), (538, 485)])
p2.edge(c2, out, "prioridade", E + "exitX=0.5;exitY=1;entryX=0.5;entryY=0;")
p2.edge(c3, out, "tom", E + "exitX=0.5;exitY=1;entryX=0.8;entryY=0;", [(1050, 485), (742, 485)]); p2.edge(out, llm); p2.edge(llm, crm2)
p2.box("note", 60, 510, 340, 130, "<b>Por que a ação não vem da IA?</b><br>Ela depende de um efeito causal medido no sorteio de agosto: contatar o anual que não usa triplica o desligamento. Uma tabela é auditável, estável e mensurável contra o controle.")
p2.box("note", 880, 510, 340, 130, "<b>Onde entraria um RAG?</b><br>Só na mensagem, se a biblioteca de briefings, políticas e mensagens aprovadas crescer. Para decidir, não.")

# =================================================================== página 3: construção
p3 = Page("3 · O que nós fazemos para construir")
p3.box("text", 40, 4, 600, 18, "<b style=\"color:#2563eb;letter-spacing:1px\">VITALIZA · MÓDULO 2 · INTELI</b>")
p3.box("title", 40, 20, 1000, 30, "Procedimento de construção do sistema (CRISP-DM)")
p3.box("text", 40, 56, 1200, 40, "Cada fase usa o resultado da anterior. Verde = feito · amarelo = pendente com o grupo · cinza tracejado = execução na empresa.")
p3.box("done", 1080, 20, 26, 20, ""); p3.box("text", 1112, 20, 120, 20, "feito")
p3.box("pend", 1080, 46, 26, 20, ""); p3.box("text", 1112, 46, 160, 20, "pendente (grupo)")
p3.box("future", 1080, 72, 26, 20, ""); p3.box("text", 1112, 72, 160, 20, "piloto (empresa)")

lanes = [("Entender", 120), ("Preparar e medir", 300), ("Explicar e segmentar", 480), ("Prever", 660),
         ("Prescrever", 840), ("Comunicar e pilotar", 1020)]
for name, y in lanes:
    p3.box("lane", 40, y, 1300, 160, name)

W3, H3 = 290, 110
def ph(kind, col, lane_y, txt):
    return p3.box(kind, 60 + col * 320, lane_y + 36, W3, H3, txt)

f1 = ph("done", 0, 120, "<b>1 · Entender o negócio</b><br>Ler o enunciado e o dicionário; fixar premissas (preços, taxas, CAC, tetos do CRM).<br><i>→ resumo do case</i>")
f2 = ph("done", 0, 300, "<b>2 · Qualidade dos dados</b><br>Formatos, grafias, fusos, cortesias.<br><i>→ notebook §1.1</i>")
f3 = ph("done", 1, 300, "<b>3 · Reconstruir a base</b><br>Status por eventos; conciliar com os números do enunciado.<br><i>→ src/base.py · §1.2</i>")
f4 = ph("done", 0, 480, "<b>4 · Diagnóstico</b><br>Decomposição taxa × mix, diferença em diferenças, triangulação do GPS.<br><i>→ notebook §2</i>")
f5 = ph("done", 1, 480, "<b>5 · Segmentação</b><br>k-means com padronização e silhueta.<br><i>→ notebook §3</i>")
f6 = ph("done", 0, 660, "<b>6 · Modelo de risco</b><br>Fotos no tempo, validação fora do tempo, 4 modelos, calibração.<br><i>→ notebook §4</i>")
f7 = ph("done", 1, 660, "<b>7 · Texto e imagem</b><br>Esquema fixo, extração por regras, ablação; imagens descartadas.<br><i>→ notebook §5</i>")
f7b = ph("pend", 2, 660, "<b>7b · Rotular 300 textos à mão</b><br>Medir o acerto da extração.<br><i>→ outputs/amostra_rotulagem.csv</i>")
f7c = ph("pend", 3, 660, "<b>7c · Extração com LLM real</b><br>Trocar as regras pelo LLM; comparar com a rotulagem e medir o custo.")
f8 = ph("done", 0, 840, "<b>8 · Uplift da campanha</b><br>Efeito por célula e mensagem, IC de 95%.<br><i>→ notebook §6</i>")
f9 = ph("done", 1, 840, "<b>9 · Regra e retorno</b><br>Ação de maior lucro por célula; sensibilidade; orçamento.<br><i>→ notebook §7 · lista CSV</i>")
g1 = p3.box("gate", 700, 876, 190, 110, "Grupo revisa e aprova a regra v1")
f10 = ph("pend", 3, 840, "<b>10 · Mensagem com LLM real</b><br>Briefing pronto (§8); falta gerar os textos e revisar uma amostra.")
f11 = ph("done", 0, 1020, "<b>11 · Documentos</b><br>Análise detalhada, solução em uma página, plano v2.")
f12 = ph("future", 1, 1020, "<b>12 · Piloto nov–dez</b><br>Controle de 10%, testes de WhatsApp e CS, retreino mensal.")
g2 = p3.box("gate", 700, 1056, 190, 110, "Semana 10: escalar, ajustar ou parar")

H = E + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
def cross(a, col_a, b, lane_y):
    gy = lane_y + 170
    p3.edge(a, b, "", E + "exitX=0.5;exitY=1;entryX=0.5;entryY=0;", [(60 + col_a * 320 + W3 / 2, gy), (60 + W3 / 2, gy)])
for a, b in [(f2, f3), (f4, f5), (f6, f7), (f7, f7b), (f7b, f7c), (f8, f9), (f9, g1), (g1, f10), (f11, f12), (f12, g2)]:
    p3.edge(a, b, "", H)
cross(f1, 0, f2, 120); cross(f3, 1, f4, 300); cross(f5, 1, f6, 480); cross(f7, 1, f8, 660); cross(f10, 3, f11, 840)
p3.edge(f7c, f6, "realimenta o modelo", ED + "exitX=0.5;exitY=0;entryX=0.5;entryY=0;", [(1065, 689), (205, 689)])

xml = '<mxfile host="app.diagrams.net" type="device">' + p1.xml("p1") + p2.xml("p2") + p3.xml("p3") + "</mxfile>"
open(__import__("pathlib").Path(__file__).with_name("Vitaliza — Fluxograma do sistema.drawio"), "w", encoding="utf-8").write(xml)
print("ok")
