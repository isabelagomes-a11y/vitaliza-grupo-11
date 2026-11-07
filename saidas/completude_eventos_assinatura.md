# Completude do eventos_assinatura.csv

Base: `dados/brutos/eventos_assinatura.csv`, 275565 linhas. Gerado por `src/completude.py eventos_assinatura`.

- **Vazios:** nulo, célula vazia ou só com espaços.

| Coluna | Vazios | % vazios | Vazios + sem conteúdo | % | Criticidade |
|---|---|---|---|---|---|
| `user_id` | 0 | 0.0% | 0 | 0.0% | alta |
| `data_hora` | 0 | 0.0% | 0 | 0.0% | alta |
| `evento` | 0 | 0.0% | 0 | 0.0% | alta |
| `plano` | 72873 | 26.44% | 72873 | 26.44% | média |
| `canal_cobranca` | 0 | 0.0% | 0 | 0.0% | alta |
| `detalhe` | 269494 | 97.8% | 269494 | 97.8% | média |

## Justificativa

- **`user_id` (alta):** Sem ele não se liga o evento ao assinante. Completo; não há assinatura_id, então os períodos de assinatura são montados pela sequência de eventos do usuário.
- **`data_hora` (alta):** Define quem estava ativo e quando saiu. Completa; lojas em UTC (186.323) e site em Brasília (89.242), coerente com o canal em 100% das linhas. Converter para Brasília muda o mês de 753 eventos.
- **`evento` (alta):** Define início, renovação e fim da assinatura. Completo; 11 tipos, todos do dicionário.
- **`plano` (média):** Vazio esperado nos trials (66.139 linhas, ainda sem plano). Fora deles, 6.734 desligamentos de renovação sem plano, inferível pelos eventos vizinhos. Eventos pagos completos.
- **`canal_cobranca` (alta):** Decide onde a pessoa cancela (loja ou site) e a receita líquida. Completo; um canal por usuário.
- **`detalhe` (média):** Só existe em assinatura_expirada: 6.071 das 17.830 têm motivo (renovacao_desligada, falha_pagamento, chargeback, reembolso). Separar saída voluntária de falha de cobrança pode ser inferido por periodo_carencia e pagamentos.csv, mas a inferência pode errar.

## Contas sem linha nesta base

12752 das 64948 contas de `usuarios.csv` (19.63%) não têm linha em `eventos_assinatura.csv`. São contas que não testaram nem assinaram desde 01/07/2024, início do histórico. Criticidade baixa: é o esperado num app freemium.

Critérios de criticidade: **alta**, a falta pode afetar uma decisão de negócio; **média**, dá para inferir, mas a inferência pode levar a uma direção equivocada; **baixa**, dá para seguir com menos detalhe.
