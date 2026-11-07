# Comparativo dos três trabalhos

> Os três trabalhos lado a lado: o que cada um tem, o que o guia pede e com o que ficamos.
> Números conferidos em 07/11/2026 com o código da Solução 1 sobre o mesmo data room.

## Os três trabalhos

| | **Solução 1 — Análise completa (nossa)** | **Solução 2 — Plano de Inteligência de Retenção** | **Solução 3 — Relatório de Segmentação + Mini deck EDA** |
|---|---|---|---|
| Arquivos | análise detalhada (19 p.), solução em 1 página (2 p.), plano v2 (11 slides), fluxograma (3 p.), notebook + código | 1 deck (6 slides) | relatório executivo (6 p.) + mini deck (6 slides) |
| Foco | o case inteiro: medir → explicar → prever → decidir → retorno → mensagem | recomendação ao Conselho | **semana 5**: EDA + segmentação + personas |
| Base de análise | corte 30/09 (escoragem) e fotos de mar–jul para o modelo | corte 30/09 | ativos no **fim de 31/07** (14.032) e saídas até 29/09 (1.469 · 10,5%) |
| Código | `saidas/solucao1/` (registro) → evoluiu para `src/vitaliza/` | não entregue | `src/`, `notebooks/`, `decisoes.md` deste repositório |

## Aderência ao guia de entregáveis

✅ atende · 🟡 atende em parte · ⬜ não tem

| O que o guia pede | Sol. 1 | Sol. 2 | Sol. 3 |
|---|---|---|---|
| **Semana 5 · Negócios: Customer Segmentation Report** (relatório executivo, 4–6 p.) | 🟡 tem tudo, mas em 19 p. e com 6 grupos | ⬜ | ✅ 6 p. |
| 3–4 segmentos com cartões de persona | 🟡 6 segmentos, sem cartão | ⬜ | ✅ 4 segmentos, personas completas |
| Hipóteses de drivers de churn por segmento | 🟡 por causa, não por segmento | 🟡 | ✅ |
| Priorização preliminar (imediata × monitoramento) | ⬜ | ⬜ | ✅ |
| Visualizações da EDA | ✅ | 🟡 | ✅ |
| Seção de limitações | ✅ | 🟡 (riscos) | ✅ |
| **Semana 5 · Tecnologia: EDA (código + visualizações)** | ✅ notebook | ⬜ | ✅ scripts + notebooks (repo) |
| Mini deck analítico (3–5 slides, gráfico no centro) | ⬜ | ⬜ | ✅ 5 slides + capa |
| Cartão de persona (1 cartão, nome no centro, lido em 10 s) | ⬜ | ⬜ | 🟡 personas em texto, não em cartão |
| **Semana 10 · Negócios: Plano de Intervenção (ROI)** | ✅ regra + ROI + sensibilidade + custo de IA | 🟡 ROI com contas que não fecham | ⬜ (fica para a semana 10) |
| KPIs (retenção, uplift, payback) | 🟡 sem payback | 🟡 | ⬜ |
| **Semana 10 · Tecnologia: App web preditivo-generativo (Marimo + API GenAI)** | ⬜ só o briefing e a lógica | ⬜ | ⬜ |
| Modelo com matriz de confusão e precisão × recall | 🟡 AUC e captura; sem matriz | ⬜ | ⬜ |

## Tema a tema

| Tema | Sol. 1 | Sol. 2 | Sol. 3 | **Fica com** |
|---|---|---|---|---|
| Conciliação com o enunciado | 7 números, todos batem | — | 18 números, 17 batem | **Sol. 3** (mais ampla) |
| Limpeza de dados | fuso, formatos, grafias, cortesias | — | 25 decisões documentadas; **1.941 cobranças duplicadas removidas**; 753 eventos mudam de mês com o fuso | **Sol. 3**. A Sol. 1 não removeu as duplicadas (só procurou linhas idênticas) e precisa incorporar |
| Hipóteses da EDA | causas da subida (preço, GPS, renovações) | as mesmas 3 | 12 hipóteses com critério de refutação; AUC de cada variável sozinha | **Sol. 3** para a EDA; **Sol. 1** para a subida de 2026 |
| Por que o churn subiu | decomposição (+0,87 mensal, +0,37 anual, −0,25 mix) e diferença em diferenças do preço (+4,7 pp/mês) | 3 choques (sazonalidade, preço, GPS) | reajuste "em parte" (jan/26 já alto; anual sobe desde jul/25) | **Sol. 1**, com a ressalva da Sol. 3 |
| Falha de GPS no Android | 19% dos treinos sem GPS em mai–jun; +2,4 pp de churn | +2,4 pp; chamados 15× | não analisada | **Sol. 1** |
| Segmentação | k-means, 6 grupos (silhueta 0,18) | — | **regras de momento** (plano × renovação × tempo de casa) + camada k-means; AUC 0,87 | **Sol. 3**: 4 segmentos, como pede o guia, e separa muito mais |
| Personas | — | — | Setup · Conflito · Resolução · Evidência · Decisão · Limite; "gêmeo demográfico" | **Sol. 3** |
| Sinais de texto | "meta cumprida" (posts), GPS escondido em "cobrança" (chamados) | "meta cumprida": 40% × 18% | não usou (fica para a semana 10) | **Sol. 1**, para enriquecer as personas |
| Modelo preditivo | 4 modelos, validação fora do tempo, AUC 0,94, captura de 66% no top 1.500 | AUC 0,66–0,70 | AUC por variável; segmentação com AUC 0,87 | **Sol. 1** |
| Demografia | usa idade e sexo como variáveis | — | não separa (AUC 0,50) e **não deve ser gatilho (LGPD, art. 6º, IX)** | **Sol. 3**: tirar idade e sexo do modelo |
| Campanha de agosto | uplift por célula, com IC; "não perturbe" medido | dorminhoco anual ×3 | efeito por segmento (cupom −5,6 no B, −5,1 no C, nada no anual) | **Sol. 1 + Sol. 3** (conferem entre si) |
| Regra de decisão e retorno | R$ 93 mil por onda (R$ 49 mil só mensal), faixa R$ 69–142 mil, custo de IA, sensibilidade | R$ 84 mil/mês, com contas que não fecham | prioridade imediata × monitoramento; ROI fica para a semana 10 | **Sol. 1** para a conta; **Sol. 3** para a priorização |
| Riscos, gatilhos, plano de 10 semanas | sim | **tabela de risco × gatilho × resposta; pedido ao Conselho** | limitações | **Sol. 2** para a forma; **Sol. 1** para os números |
| Mensagem / GenAI | briefing, guardrails, prompt | — | — | **Sol. 1** |
| Fluxo do sistema | fluxograma de 3 páginas | — | — | **Sol. 1** |
| Comunicação | semiótica de cores, trilha de raciocínio | deck executivo elegante | relatório e deck no formato do guia | **Sol. 3** para o formato; **Sol. 1** para a semiótica |

## Números: onde batem e onde divergem

| Número | Sol. 1 | Sol. 2 | Sol. 3 | Conferido | Usar |
|---|---|---|---|---|---|
| Ativos em 30/09/2026 | 14.753 | 14.753 | 14.753 | ✅ | 14.753 |
| Churn médio 2025 · 2026 | 5,6% · 6,6% | 5,6% · 6,6% | 5,6% · 6,6% | ✅ | igual |
| Base da semana 5 | 14.049 (início de 31/07) | — | 14.032 (fim de 31/07) | ✅ o código da Sol. 1 dá **14.032 e 1.469** com o corte no fim do dia | **fim de 31/07** |
| Churn 60 d por segmento | — | — | A 45,3% · B 18,6% · C 11,4% · D 0,1% | ✅ 45,3% · 18,6% · 11,3% · 0,1% (tamanhos diferem em até 30 pessoas) | Sol. 3 |
| Cupom × controle (todos) | −1,9 pp | — | −1,9 pp | ✅ | −1,9 pp |
| Cupom × controle por segmento | — | — | B −5,6 · C −5,1 · A +4,4 | ✅ B −6,6 · C −4,9 · A +6,2 (dentro do IC) | Sol. 3 |
| Reajuste | +4,7 pp/mês (DiD); +8,8 pp em 90 d | ≈ +5 pp em 90 d | pico de 14,5% em abril no mensal | 🟡 medidas diferentes do mesmo efeito | Sol. 1, citando o pico |
| "Meta cumprida" | 19,5% × 9,5% (31/07); B 49% × 16%; C 30% × 9,5% | 40% × 18% | — | 🟡 o 40% da Sol. 2 não foi reproduzido | **Sol. 1** |
| Dorminhoco anual contatado | desligamento 8% → ~25% | saída 11,5% → 34,6% | "lembrar que paga sem usar pode acelerar a saída" | 🟡 mesma direção; definições diferentes | Sol. 1 |
| AUC do modelo | 0,92–0,94 | 0,66–0,70 | 0,87 (segmentação) | — | Sol. 1 (a diferença vem de usar a data da próxima cobrança) |
| Retorno | R$ 93 mil por onda | R$ 84 mil/mês | — | ⚠️ a Sol. 2 tem contas internas que não fecham | Sol. 1 |

## O melhor de cada um

**Solução 1 — Análise completa (nossa)**
- Base reconstruída e o código que reproduz tudo.
- Diagnóstico da subida: decomposição, diferença em diferenças e triangulação do GPS.
- Modelo com validação fora do tempo (AUC 0,94; 66% das saídas no top 1.500).
- Uplift da campanha por célula e a regra "não perturbe".
- Conta de retorno com custo de IA e sensibilidade.
- Sinais de texto ("meta cumprida", GPS escondido em "cobrança").
- Briefing da mensagem, fluxograma do sistema, semiótica visual.

**Solução 2 — Plano de Inteligência de Retenção**
- Narrativa executiva para o Conselho ("contatar menos, reter mais").
- Tabela de riscos × gatilho × resposta e o pedido explícito de decisões.
- Comparação com o Strava (personalização como aposta competitiva).

**Solução 3 — Relatório de Segmentação + Mini deck**
- Formato exato do guia para a semana 5.
- Segmentação por **momento do ciclo** (4 segmentos) + camada de comportamento.
- Personas com Setup, Conflito, Resolução, Evidência, Decisão e Limite.
- Priorização imediata × monitoramento; matriz valor × risco.
- 25 decisões de limpeza documentadas, incluindo as cobranças duplicadas.
- Cuidado com a LGPD (demografia não é gatilho).

## Conflito resolvido

**O anual com pouco uso: contatar ou não?**
- A **Sol. 3** prioriza o *A · pouco uso* como ação imediata e propõe reativar o *D · pouco uso* antes da renovação, sem oferta.
- A **Sol. 1** e a **Sol. 2** mostram, pelo sorteio de agosto, que contatar o anual que não usa **aumenta** o desligamento (8% → ~25%). A própria Sol. 3 registra que no A "nenhuma mensagem funcionou".
- **Decisão do grupo (07/11/2026): não contatar.** O anual com pouco uso (A e D) não recebe nenhum contato; é monitorado e recalculado todo mês. Conferido no sorteio: cupom +5,9 pp e conteúdo +4,7 pp de desligamento contra 6,3% no controle.

## Lacunas que nenhum dos três cobre

- App web preditivo-generativo (Marimo + API de GenAI), entregável da semana 10.
- Chamada real a uma API de GenAI, com custo por token medido.
- Matriz de confusão, escolha de limiar e precisão × recall (critério da rubrica).
- Payback da campanha.
- Cartão de persona no formato de 1 página, lido em 10 segundos.
