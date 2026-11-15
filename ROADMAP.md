# Roadmap

> Do que temos hoje (07/11) até as duas entregas do guia: **semana 5 em 15/11** e **semana 10 em 20/12**, sempre até 23:59.
> Formato livre; entrega por link de pasta pública no Google Drive, enviado na Adalove. **A submissão é individual: cada integrante envia o link.**

```
nov  07 ──── 09 ──────────── 15 ║ 16 ─────── 29 ║ 30 ─────────── 13 ║ 14 ─────── 20 dez
     F0      F1 · Semana 5   ⬆  F2 · Modelo     F3 · App Marimo      F4 · Plano + entrega ⬆
     unificar                entrega                                                     entrega
```

## F0 · Unificar (07–09/11)

- [x] Comparar os três trabalhos do grupo e somar o melhor de cada um
- [x] Conferir os números entre os trabalhos
- [x] Decisões: segmentação de momento, anual com pouco uso (não contatar), idade e sexo (fora)
- [ ] Decisão pendente: provedor de IA
- [x] Repositório enxuto: só a entrega e o código que a gera (branch `dev`)

## F1 · Semana 5: Segmentação + EDA (09–15/11) · entrega 15/11

O que o guia pede, e a base de cada peça:

| Artefato | Formato | Audiência | Onde |
|---|---|---|---|
| **Customer Segmentation Report** (negócios) | relatório executivo, 4–6 p. | Camila, Conselho | `saidas/entrega_semana5/` |
| **Cartões de persona** | 1 cartão por segmento, nome no centro, lido em 10 s | Conselho, marketing, retenção | `saidas/entrega_semana5/` |
| **EDA: código + visualizações** (tecnologia) | notebook + código | liderança técnica e produto | `notebooks/eda.ipynb`, `src/`, `saidas/graficos/` |
| **Mini deck analítico** | 3–5 slides, gráfico no centro | liderança técnica e produto | `saidas/entrega_semana5/` |

Tarefas:
- [x] Incorporar a remoção das 1.941 cobranças duplicadas ao código da S1
- [x] Notebook de EDA (carrega, limpa, visualiza, correlações com churn, segmentação)
- [x] Relatório executivo (5 p.)
- [x] 4 cartões de persona
- [x] Mini deck (5 slides)
- [ ] Revisão do grupo (13–14/11)
- [ ] Pasta pública no Drive e link enviado na Adalove por **cada** integrante (até 15/11, 23:59)

## F2 · Modelo preditivo (16–29/11)

- [ ] Ler o feedback da semana 5 (o professor tem até 2 semanas)
- [x] Modelo sem idade e sexo (LGPD): AUC 0,936, captura 66,1% (sem perda)
- [ ] Levar o modelo para `src/vitaliza/model.py`
- [ ] Métricas da rubrica: AUC-ROC, **matriz de confusão**, limiar escolhido pelo custo, **precisão × recall** justificados para retenção
- [ ] Interpretação: importância das variáveis e **análise de erros** (quem o modelo erra e por quê)
- [ ] Modelo salvo para o app (arquivo carregável)
- [ ] Rotulagem manual dos 300 textos e acerto da extração

## F3 · App web preditivo-generativo em Marimo (30/11–13/12)

O guia pede um app que (1) roda o modelo em Python e mostra o risco de um usuário e (2) chama uma API de GenAI para gerar um texto de retenção personalizado.

- [ ] Escolher o provedor (Gemini, GPT ou Claude) e obter a chave
- [ ] Módulos: `data`, `features`, `model`, `decision`, `extractor` (+ cache), `messaging`
- [ ] App Marimo: escolher assinante → risco + segmento + ação → prompt dinâmico (segmento, score, variáveis) → mensagem
- [ ] Guardrails (termos proibidos, tamanho por canal) e registro do custo por chamada
- [ ] Navegável por pessoa não técnica; código documentado
- [ ] Teste com 10 assinantes reais da base, um de cada segmento

## F4 · Plano de Intervenção + entrega final (07–20/12) · entrega 20/12

- [ ] Plano de Intervenção de Risco: segmentos de risco **do modelo**, oferta e comunicação por segmento, testes embutidos
- [ ] ROI: LTV dos clientes em risco, custo da intervenção (canais, ofertas, **tokens e infraestrutura**), conversão esperada pelo sorteio
- [ ] KPIs: retenção, uplift contra controle, custo por saída evitada, **payback**
- [ ] Alinhamento ambidestro: segmentos → briefing da GenAI → app
- [ ] Revisão do grupo (17–18/12)
- [ ] Pasta no Drive atualizada e link na Adalove por cada integrante (até 20/12, 23:59)

## Critérios de avaliação da semana 10 (para conferir antes de entregar)

| Trilha | Critério | Peso | Para ser "excepcional" |
|---|---|---|---|
| Negócios | Segmentação e estratégia de intervenção | 40% | estratégia personalizada por segmento, hipóteses de driver claras, testes embutidos |
| Negócios | ROI da retenção | 40% | modelo financeiro realista, custos de IA (tokens, infra), KPIs (retenção, uplift, payback) |
| Negócios | Alinhamento ambidestro | 20% | segmentos retroalimentam o briefing da GenAI e a leitura do modelo |
| Tecnologia | Modelo preditivo de churn | 40% | importância de variáveis, análise de erros, precisão × recall justificado |
| Tecnologia | Integração preditivo-generativo | 40% | prompt incorpora segmento, score e variáveis do cliente |
| Tecnologia | Adequação ao problema | 20% | código organizado e documentado; app navegável; pensado para escalar |
