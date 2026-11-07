# Solução unificada

> O melhor dos três trabalhos numa solução só. Cada peça indica de onde vem: **[S1]** análise completa (nossa), **[S2]** Plano de Inteligência de Retenção, **[S3]** Relatório de Segmentação + Mini deck.

## A história em uma frase

O churn subiu por três motivos (o preço do mensal, um defeito de GPS e as renovações anuais) **[S1]**. Quem sai se explica pelo **momento do ciclo e pelo uso**, não pela demografia **[S3]**. Por isso a solução contata menos e melhor: age onde o sorteio de agosto mostrou efeito e deixa em paz quem o contato faria sair **[S1, S2]**.

## 1 · Base e dados

| Decisão | Fonte |
|---|---|
| Status de cada assinatura reconstruído pelos eventos, com fusos convertidos para Brasília | S1, S3 |
| Base da semana 5: ativos no **fim de 31/07/2026** (14.032), saída em 60 dias até 29/09 (1.469 · 10,5%) | S3, conferido com o código de S1 |
| Escoragem final: ativos em 30/09/2026 (14.753), risco até 29/11 | S1 |
| Conciliação com 18 números do enunciado | S3 |
| 25 decisões de limpeza documentadas, incluindo **1.941 cobranças duplicadas** | S3 (já incorporado ao código unificado) |
| 60 contas internas fora das contagens | S1, S3 |

## 2 · Por que o churn subiu (diagnóstico)

| Causa | Evidência | Fonte |
|---|---|---|
| Reajuste do mensal (01/03) | +4,7 pp/mês na diferença em diferenças contra o anual; pico de 14,5% em abril | S1, S3 |
| Falha de GPS no Android (mai–jun) | 19% dos treinos sem GPS; 535 e 418 chamados; churn +2,4 pp acima do iOS em jun–jul | S1, S2 |
| Renovações anuais chegando | vencimentos em janeiro 224 → 670; o anual sobe desde jul/25 | S1, S2, S3 |
| Descartados | falha de pagamento (estável), perfil da base, demografia (AUC 0,50) | S1, S3 |

## 3 · Os 4 segmentos (base: fim de 31/07)

Segmentos por **momento** [S3] e enriquecidos com os sinais de [S1]:

| Segmento | Quem | Assinantes | Churn 60 d | % do churn | Sinal extra de S1 |
|---|---|---|---|---|---|
| **A · O anual que esfriou antes de renovar** | anual com renovação nos próximos 60 dias | 1.370 | **45,3%** | 42% | 41% já desligaram a renovação; postou "meta cumprida" → 60% saem |
| **B · O mensal que ainda está decidindo** | mensal com até 5 meses | 2.679 | 18,6% | 34% | "meta cumprida" → **49%** (contra 16%) |
| **C · O mensal fiel que pode escorregar** | mensal com 6 meses ou mais | 3.067 | 11,3% | 24% | "meta cumprida" → **30%** (contra 9,5%); queda de uso → 28,5% |
| **D · O anual garantido até a renovação** | anual com renovação depois de 60 dias | 6.916 | 0,1% | 0,3% | 2.596 com pouco uso: o A dos próximos meses |

Números do código unificado (`src/vitaliza/`, gerados por `src/build_eda_unificada.py`). A Solução 3 tinha 1.362 · 2.651 · 3.095 · 6.924 pessoas, com as mesmas taxas; a diferença (até 30 pessoas) vem de como se conta o tempo de casa e a data da renovação.

**Camada de comportamento:** no anual, ativo × pouco uso (menos de 2 treinos/mês, o gatilho da S3); no mensal, ar livre × vídeo (mais ou menos da metade dos treinos ao ar livre). A S3 usava o k-means para essa camada; a regra é mais simples de explicar e dá a mesma separação (AUC 0,87).

## 4 · Hipóteses de driver por segmento

| Segmento | Driver principal | Evidência | Fonte |
|---|---|---|---|
| A | decide na renovação; o desânimo aparece meses antes, como queda de uso | pouco uso → 54,5% de saída; ativo → 11,1% | S3 |
| B | reavalia o preço a cada cobrança; reajuste de março | pico pós-reajuste; cupom −5,6 pp, desafio −3,9 pp | S1, S3 |
| C | o hábito quebra (queda de uso, meta cumprida, falha de GPS) | queda de uso 28,5% × 9,0%; meta cumprida 30% × 9,5% | S1, S3 |
| D | sem risco agora; o risco se forma pelo não uso até a renovação | 2.870 com pouco uso | S3 |

## 5 · Priorização e ação

| Ordem | Quem | Classificação | Ação | Evidência do sorteio de agosto |
|---|---|---|---|---|
| 1 | **B** | Imediata | desafio por push + e-mail (ar livre: desafio de corrida; vídeo: plano em vídeo); cupom só para quem desligar a renovação | desafio −4,4 pp, cupom −6,6 pp [S1/S3] |
| 2 | **C** com gatilho (queda de uso, meta cumprida, falha de GPS, recusa de cobrança) | Imediata no gatilho | desafio ou plano; na recusa, lembrete para atualizar o pagamento | cupom −4,9 pp, desafio −2,7 pp |
| 3 | **A ativo** | Imediata | plano de treino ou desafio antes do vencimento, sem desconto | no anual ativo, o desafio reduziu o desligamento em 3,8 pp [S1] |
| — | **A** e **D** com pouco uso | **Não contatar** (decisão do grupo, 07/11) | nenhum contato; monitorar e recalcular todo mês | contatar o anual com pouco uso aumentou o desligamento: cupom +5,9 pp, conteúdo +4,7 pp [S1, S2] |
| — | D ativo | Monitoramento | conteúdo leve, sem oferta | — |

Dentro de qualquer segmento, quem tem maior **risco do modelo** sobe na fila dos canais escassos: WhatsApp (1.500/mês) e CS (300/mês) [S1, S3].

## 6 · Modelo preditivo (semana 10)

- Fotos da base no tempo, validação fora do tempo, 4 modelos (logística, árvore, random forest, boosting) [S1].
- Variáveis de momento (dias até a próxima cobrança, renovação desligada) + uso + texto [S1, S3].
- **Sem idade e sexo** como variável ou gatilho (LGPD) [S3]. Decidido em 07/11; retreinado: AUC 0,936 e captura de 66,1%, iguais ao modelo com elas.
- A adicionar para a rubrica: matriz de confusão, escolha de limiar, precisão × recall e análise de erros.

## 7 · Retorno e KPIs (semana 10)

- Só o incremental entra: efeito do sorteio × contatados × valor do assinante retido [S1].
- Referência atual: R$ 93 mil por onda (R$ 49 mil só no mensal), faixa de R$ 69–142 mil [S1]. **Recalcular com os 4 segmentos.**
- Custos: canais, ofertas e IA generativa (tokens) [S1]. A adicionar: infraestrutura e **payback**.
- KPIs: taxa de retenção, uplift contra o controle permanente de 10%, custo por saída evitada, payback [S1, S2].
- Riscos com gatilho e resposta [S2].

## 8 · Mensagem e app (semana 10)

- O LLM recebe segmento, score de risco, ação e sinais extraídos, e escreve o texto; não decide [S1].
- Briefing com tom, ofertas permitidas e proibições; guardrails [S1].
- App em **Marimo**: escolhe um assinante → mostra risco, segmento e ação → chama a API de GenAI → mostra a mensagem [guia].
- Os segmentos de negócio alimentam o briefing de personalização (critério "alinhamento ambidestro" da rubrica).

## 9 · Limitações (unificadas)

- Associação não é causa; só a campanha de agosto mede efeito [S1, S3].
- 67% das saídas sem motivo registrado; a pesquisa de saída tem viés de seleção [S3].
- A campanha de agosto cai dentro da janela de 60 dias [S1, S3].
- Segmentos de momento mudam todo mês e precisam ser recalculados [S3].
- k-means com separação fraca (silhueta 0,18–0,23) [S1, S3].
- O uso mensal diverge do registro de treinos em 13% dos casos [S3].
- Efeito no anual medido por desligamento em 51 dias, não por renovação [S1].
- A extração de texto ainda não foi conferida contra rótulos humanos [S1].
