# Cartões de persona · Vitaliza · grupo 11

**De onde vêm os números.** 14.032 assinantes pagantes ativos em 31/07/2026, sem contas internas.
O churn é a saída nos 60 dias seguintes, até 29/09/2026. A média da base é 10,5%, com 1.469 saídas.

- Segmentos: `notebooks/segmentacao.ipynb`.
- EDA: `notebooks/eda_churn.ipynb`.
- Efeito das mensagens: campanha sorteada de 10/08/2026, contra o grupo de controle, com intervalo de 95%.

**Regras de leitura** (aula 4):
- O nome descreve comportamento. Não há fotos nem personagens.
- Idade e sexo só descrevem e não são gatilho de ação. Nos 4 segmentos, a mediana de idade é de 46 a 47 anos e cerca de 50% são mulheres.
- Toda decisão tem gatilho, ação e uma hipótese a testar.
- Nenhuma variável usa informação posterior a 31/07.

---

## A · O anual que esfriou antes de renovar

**1.362 assinantes (10% da base) · churn de 45,3% · 42% de todo o churn · R$ 21,82 por mês líquidos · R$ 161 mil por ano em risco**

| | |
|---|---|
| **Setup** | Assina o plano anual há cerca de 11 meses (mediana) e a renovação vence em até 1 mês. 71% pagam pela loja. Treina pouco: 1,3 vez por mês (mediana), e 27% não treinaram nenhuma vez entre maio e julho. |
| **Conflito** | Quase metade sai na renovação. Dentro do segmento, quem usa pouco (1.073) sai **54,5%**, contra 11,1% de quem segue ativo (289). Metade dos que usam pouco já desligou a renovação, e esses saem 95%. |
| **Resolução** | O anual não sai quando desanima: sai na data da renovação. O desânimo aparece meses antes, como queda de uso, e só vira perda no vencimento. Entre o aviso de renovação desligada e a expiração, a pessoa continua assinante e pode ser alcançada. |
| **Evidência** | 45,3% de churn contra 6,7% no resto da base (+38,6 pontos). 617 das 1.469 saídas. Gêmeo demográfico (mesma idade e sexo, sem o comportamento): 6,7%. O ativo com renovação ligada sai 7,6%. |
| **Decisão** | **Gatilho:** renovação em até 30 dias e menos de 2 treinos por mês, ou renovação desligada. **Ação:** contato antes do vencimento com conteúdo personalizado ou plano de treino. Se a renovação já estiver desligada, oferta de 1 mês grátis no fim do ciclo. **Hipótese a testar:** o contato antes da renovação reduz o churn do grupo com pouco uso em 10 pontos, com grupo de controle sorteado. |
| **Limite** | Na campanha de agosto, nenhuma mensagem reduziu o churn deste segmento: cupom +4,4 pontos (±7,6), desafio +1,9 (±7,4), conteúdo +0,7 (±7,6). Uma oferta genérica pode não funcionar aqui, e um lembrete de que a pessoa paga por algo que não usa pode até acelerar a saída. 70% das saídas não têm motivo registrado. É um segmento de **momento**: muda todo mês, conforme a data de renovação se aproxima. |
| **Prioridade** | **Agir já** no grupo com pouco uso, que concentra 40% do churn da base, mesmo com valor mensal abaixo da média (a renovação vale de R$ 255 a R$ 297 líquidos de uma vez, conforme o canal). Contato leve, sem oferta, para quem segue ativo. |

---

## B · O mensal que ainda está decidindo

**2.651 assinantes (19% da base) · churn de 18,6% · 33% de todo o churn · R$ 35,45 por mês líquidos · R$ 210 mil por ano em risco**

| | |
|---|---|
| **Setup** | Assina o plano mensal há até 5 meses (mediana de 2 meses). Treina bem: 5,7 vezes por mês (mediana), 8 sessões no app por mês. Todos vieram de trial. 27% chegaram por influenciador, contra 15% na base. |
| **Conflito** | Mesmo treinando, sai quase 2 vezes mais que a base. O uso quase não separa quem sai neste segmento: de 17% a 20% em todas as faixas de treino. Quem treina ao ar livre sai mais (21,4%, n = 1.553) do que quem treina em vídeo (14,6%, n = 1.098). |
| **Resolução** | O novato mensal reavalia a assinatura a cada cobrança. Não é falta de uso que o leva a sair, é a pergunta "vale R$ 39,90 este mês?". |
| **Evidência** | 18,6% de churn contra 8,6% no resto (+10 pontos). 492 saídas. Gêmeo demográfico: 8,7%. Na campanha de agosto, o **cupom de 30% por 3 meses** reduziu o churn em **5,6 pontos** (±4,0) e o desafio em 3,9 pontos (±4,0, na fronteira), contra o controle. |
| **Decisão** | **Gatilho:** mensal entre a 1ª e a 5ª cobrança. A prioridade sobe com renovação desligada (4,8% do segmento) ou recusa de cobrança (5,5%). **Ação:** para quem treina ao ar livre, desafio de corrida e convite a treinar com companhia; para quem treina em vídeo, plano de treino em vídeo. O cupom fica reservado a quem desligar a renovação. **Hipótese a testar:** o desafio sem cupom reduz o churn em 4 pontos, a um custo menor que o cupom (R$ 35,91 por pessoa), testado com grupo de controle. |
| **Limite** | O efeito do cupom é medido sobre toda a campanha, e o arquivo de pagamentos não mostra nenhuma cobrança com desconto. Ainda não sabemos se o efeito veio do cupom usado ou só da mensagem. O pico de churn do mensal em abril e maio de 2026 (14,5% e 13,2%) coincide com o reajuste para R$ 39,90: o preço pode pesar, mas o cruzamento não prova causa. 66% das saídas não têm motivo registrado. |
| **Prioridade** | **Agir já.** Maior valor mensal (R$ 35,45), maior receita anual em risco e reação comprovada a uma mensagem. |

---

## C · O mensal fiel que pode escorregar

**3.095 assinantes (22% da base) · churn de 11,4% · 24% de todo o churn · R$ 35,43 por mês líquidos · R$ 151 mil por ano em risco**

| | |
|---|---|
| **Setup** | Assina o plano mensal há 6 meses ou mais (mediana de 13 meses) e treina com regularidade: 6,3 vezes por mês (mediana). Praticamente todos treinaram entre maio e julho. É a maior receita acumulada por pessoa (R$ 462 líquidos desde 07/2024, mediana). |
| **Conflito** | Na média, o risco fica perto da base (11,4% contra 10,5%). Mas, quando o uso cai, o risco triplica: quem treinou em julho menos da metade do que em maio e junho sai **28,5%** (n = 372), contra 9,0%. Quem desligou a renovação sai 97%. Também é o segmento com mais recusas de cobrança: 16,5% já tiveram cobrança recusada. |
| **Resolução** | O veterano não sai por tempo de casa, sai quando o hábito quebra. A queda de uso é o primeiro sinal visível e aparece antes do aviso de renovação desligada. |
| **Evidência** | Com queda de uso, 28,5% contra 9,0%. Gêmeo demográfico: 10,2% (a demografia não explica). Na campanha de agosto, o cupom reduziu o churn em **5,1 pontos** (±2,8) e o desafio em 2,8 pontos (±3,0), contra o controle. |
| **Decisão** | **Gatilho:** queda de treinos (mês atual abaixo da metade da média dos 2 meses anteriores), renovação desligada ou cobrança recusada. **Ação:** mensagem de retomada com desafio ou plano personalizado; na recusa de cobrança, lembrete para atualizar o meio de pagamento. **Hipótese a testar:** agir só com o gatilho, e não no segmento todo, reduz o churn dos acionados em 5 pontos, com custo de contato cerca de 6 vezes menor. |
| **Limite** | É o único segmento fraco em diferenciação: +1,2 ponto contra o resto da base. Ele só faz sentido com gatilho individual. A queda de uso é medida no `uso_mensal`, que diverge do registro de treinos em 13% dos casos. Para a falha de cobrança, o campo `tentativa` não é confiável. |
| **Prioridade** | **Monitorar**, e agir só com gatilho. Em julho, até cerca de 480 pessoas acionariam o gatilho (372 com queda e 111 com renovação desligada, que podem se sobrepor). |

---

## D · O anual garantido até a renovação

**6.924 assinantes (49% da base) · churn de 0,1% · 0,5% do churn · R$ 21,64 por mês líquidos**

| | |
|---|---|
| **Setup** | Assina o plano anual, e a renovação está a 2 meses ou mais. Já pagou o ano, então não pode sair antes do vencimento: o churn é quase zero. 4.054 seguem ativos (8 treinos por mês no grupo do k-means). |
| **Conflito** | Por baixo do 0,1% há um risco escondido: **2.870 usam pouco**, e **1.203 deles já desligaram a renovação**. Essas pessoas são o segmento A dos próximos meses. No A de hoje, quem chega à renovação usando pouco sai 54,5%. |
| **Resolução** | O churn do anual se decide meses antes da renovação. Esperar o vencimento é agir tarde demais. |
| **Evidência** | 0,1% de churn na janela (8 saídas em 6.924). Entre os anuais que já chegaram à renovação, pouco uso significa 54,5% de churn contra 11,1% dos ativos. Na campanha de agosto, nenhuma mensagem mudou nada: −0,1 a 0,0 ponto, porque ninguém sai antes da renovação. |
| **Decisão** | **Gatilho:** anual com pouco uso entre 2 e 6 meses antes da renovação, com prioridade para quem já desligou. **Ação:** reativação sem oferta (plano de treino, desafio, conteúdo). Desconto aqui seria custo sem retorno, porque a pessoa já pagou o ano. **Hipótese a testar:** reativar o uso antes da renovação reduz o churn na renovação em 10 pontos, comparado com um grupo de controle que só recebe contato no vencimento. |
| **Limite** | O efeito só aparece meses depois, na renovação: a janela de 60 dias desta análise não mede isso. A ligação entre reativar o uso e renovar ainda é uma hipótese. Pode ser seleção (quem volta a treinar já ia renovar). |
| **Prioridade** | **Proteger** os ativos, com contato leve. **Monitorar** os que usam pouco e reativá-los antes de virarem A. É o maior estoque de receita futura da base. |

---

## Resumo da priorização preliminar

| Ordem | Quem | Assinantes | Por quê |
|---|---|---|---|
| 1 | A · pouco uso | 1.073 | 40% do churn da base e a renovação vence agora |
| 2 | B · ar livre e vídeo | 2.651 | maior receita em risco e reação comprovada ao cupom e ao desafio |
| 3 | C, só com gatilho | cerca de 480 por mês | o risco triplica quando o uso cai |
| 4 | D · pouco uso (reativar) | 2.870, prioridade para os 1.203 com renovação desligada | o A dos próximos meses |
| — | D e A ativos | 4.343 | proteger com contato leve, sem oferta |

O teto do CRM (1.500 mensagens de WhatsApp e 300 atendimentos por mês) cabe na ordem 1 e no gatilho do C, mas não em todo o B. A divisão entre canais (push, e-mail, WhatsApp e atendimento) e o retorno de cada ação ficam para o plano de intervenção da semana 10.
