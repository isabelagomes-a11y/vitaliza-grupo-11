# Acompanhamento

> Atualize a cada avanço: marque o status, preencha o dono e registre no histórico.
> **Status:** ✅ feito · 🟡 em andamento · ⬜ a fazer · 🔒 bloqueado

## Painel

| Entrega | Prazo | Status | Progresso |
|---|---|---|---|
| F0 · Unificação | 09/11 | 🟡 | ▓▓▓▓▓▓▓▓░░ 4/5 |
| **Semana 5 · Segmentação + EDA** | **15/11** | 🟡 revisão do grupo | ▓▓▓▓▓▓▓░░░ 5/7 |
| F2 · Modelo preditivo | 29/11 | 🟡 | ▓▓▓▓░░░░░░ 2/6 |
| F3 · App Marimo | 13/12 | ⬜ | ░░░░░░░░░░ 0/6 |
| **Semana 10 · Plano + App** | **20/12** | ⬜ | ░░░░░░░░░░ 0/6 |

## Decisões pendentes do grupo

| # | Decisão | Proposta | Prazo | Status |
|---|---|---|---|---|
| D4 | Provedor de GenAI (Gemini, GPT, Claude) + chave | — | 29/11 | ⬜ |
| D5 | Dono de cada artefato | preencher a coluna "Dono" abaixo | 09/11 | ⬜ |

## Semana 5 · entrega 15/11

| # | Item | Onde | Dono | Status |
|---|---|---|---|---|
| 1 | Remover as 1.941 cobranças duplicadas | `src/vitaliza/features.py` (S3: `src/limpar_pagamentos.py`) | | ✅ |
| 2 | Notebook de EDA unificado + 11 gráficos | `notebooks/eda_unificada.ipynb` · `saidas/graficos_unificados/` | | ✅ |
| 3 | Customer Segmentation Report (5 p.) | `saidas/entrega_semana5_unificada/` | | ✅ |
| 4 | 4 cartões de persona | `saidas/entrega_semana5_unificada/` | | ✅ |
| 5 | Mini deck analítico (5 slides) | `saidas/entrega_semana5_unificada/` | | ✅ |
| 6 | Revisão do grupo | — | todos | ⬜ |
| 7 | Pasta pública no Drive + link na Adalove (cada um) | — | todos | ⬜ |

## Modelo preditivo · até 29/11

| # | Item | Base | Dono | Status |
|---|---|---|---|---|
| 1 | Fotos no tempo, validação fora do tempo, 4 modelos | S1 | | ✅ |
| 2 | Retirar idade e sexo; retreinar (AUC 0,936, captura 66,1%) | D3 | | ✅ |
| 3 | Levar o modelo para `vitaliza/model.py` (treinar, salvar, carregar) | S1 | | ⬜ |
| 4 | Matriz de confusão, limiar e precisão × recall | rubrica | | ⬜ |
| 5 | Importância de variáveis e análise de erros | S1 (parcial) | | 🟡 |
| 6 | Rotular 300 textos e medir o acerto da extração | `saidas/solucao1/amostra_rotulagem.csv` | | ⬜ |

## App Marimo · até 13/12

| # | Item | Base | Dono | Status |
|---|---|---|---|---|
| 1 | Módulos `base`, `features`, `segmentos` | `src/vitaliza/` | | ✅ |
| 2 | Módulos `model`, `decision` | S1 | | ⬜ |
| 3 | `extractor` + cache por frase | S1 (regras) | | 🟡 |
| 4 | `messaging`: briefing, prompt dinâmico, guardrails | S1 (briefing) | | 🟡 |
| 5 | Chamada real à API de GenAI + custo por chamada | D4 | | 🔒 |
| 6 | Interface Marimo navegável + teste com 1 assinante de cada segmento | — | | ⬜ |

## Semana 10 · entrega 20/12

| # | Item | Base | Dono | Status |
|---|---|---|---|---|
| 1 | Plano de Intervenção por segmento, com testes embutidos | S1 + S2 + S3 | | ⬜ |
| 2 | ROI recalculado com os 4 segmentos, custo de IA e infra | S1 | | ⬜ |
| 3 | KPIs: retenção, uplift, custo por saída evitada, payback | S1 + S2 | | ⬜ |
| 4 | Riscos × gatilho × resposta | S2 | | ⬜ |
| 5 | Revisão do grupo | — | todos | ⬜ |
| 6 | Pasta no Drive atualizada + link na Adalove (cada um) | — | todos | ⬜ |

## Decisões tomadas

| Data | # | Decisão | Motivo |
|---|---|---|---|
| 07/11 | — | Base da semana 5 = ativos no fim de 31/07 (14.032) | convenção da S3, reproduzida pelo código unificado |
| 07/11 | D1 | Segmentação oficial: 4 segmentos de momento (S3) + camada de comportamento + sinais de texto (S1) | o guia pede 3–4 segmentos; separa mais (AUC 0,87) |
| 07/11 | D2 | **Anual com pouco uso (A e D): não contatar**, nem em teste | no sorteio, o contato aumentou o desligamento (cupom +5,9 pp, conteúdo +4,7 pp) |
| 07/11 | D3 | **Idade e sexo fora** do modelo e dos gatilhos | LGPD; não separam (AUC 0,50); retirar não muda o modelo |
| 07/11 | — | Camada de comportamento por regra (< 2 treinos/mês; % ao ar livre) em vez do k-means | mais simples de explicar; mesma separação |
| 07/11 | — | A decisão é uma regra; a IA só extrai e escreve | efeito medido no sorteio; auditável |
| 07/11 | — | Imagens (heatmaps) fora do modelo | não melhoram a captura (−0,4 pp) |

## Histórico

| Data | O que mudou |
|---|---|
| 07/11/2026 | Diretório unificado criado com as 3 soluções, comparativo, solução unificada, roadmap e acompanhamento. Números da S3 conferidos com o código da S1. |
| 07/11/2026 | Decisões D1–D3 tomadas. Código unificado em `src/vitaliza/` (com as duplicadas removidas). Artefatos da semana 5 gerados: relatório (5 p.), cartões de persona (4), mini deck (5 slides), EDA (notebook + 11 gráficos). Modelo retreinado sem idade e sexo. |
| 07/11/2026 | Tudo levado para o repositório do grupo, branch `dev`, num commit só. |
