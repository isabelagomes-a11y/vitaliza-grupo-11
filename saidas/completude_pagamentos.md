# Completude do pagamentos.csv

Base: `dados/brutos/pagamentos.csv`, 165548 linhas. Gerado por `src/completude.py pagamentos`.

- **Vazios:** nulo, célula vazia ou só com espaços.

| Coluna | Vazios | % vazios | Vazios + sem conteúdo | % | Criticidade |
|---|---|---|---|---|---|
| `pagamento_id` | 0 | 0.0% | 0 | 0.0% | baixa |
| `user_id` | 0 | 0.0% | 0 | 0.0% | alta |
| `data_hora` | 0 | 0.0% | 0 | 0.0% | alta |
| `valor` | 0 | 0.0% | 0 | 0.0% | alta |
| `metodo` | 0 | 0.0% | 0 | 0.0% | média |
| `status` | 0 | 0.0% | 0 | 0.0% | alta |
| `tentativa` | 0 | 0.0% | 0 | 0.0% | média |

## Justificativa

- **`pagamento_id` (baixa):** Só identifica a linha; foi pelos IDs consecutivos que se viu que 1.941 cobranças estavam duplicadas.
- **`user_id` (alta):** Liga a cobrança ao assinante. Completo; todos os usuários têm assinatura.
- **`data_hora` (alta):** Situa a cobrança no tempo e permite usar só pagamentos até a data de referência. Lojas em UTC, site em Brasília (como nos eventos).
- **`valor` (alta):** É o valor do assinante (receita). Dois formatos ('34.90' e 'R$ 34,90', este só no site até 30/06/2025); negativos são estornos e chargebacks.
- **`metodo` (média):** O canal também está em assinaturas.csv; diverge em 48 assinantes (Pix com uma cobrança no cartão).
- **`status` (alta):** Separa cobrança aprovada, recusada, estornada e chargeback; base para identificar saída por falha de cobrança.
- **`tentativa` (média):** Não se comporta como no dicionário: das tentativas 2, só 54 vêm depois de uma recusa. Não usada; a falha de cobrança é vista pelo status e pelo período de carência.

## Contas sem linha nesta base

33166 das 64948 contas de `usuarios.csv` (51.07%) não têm linha em `pagamentos.csv`. São contas que nunca pagaram desde 07/2024 (grátis ou só trial). Criticidade baixa: é o esperado num app freemium.

Critérios de criticidade: **alta**, a falta pode afetar uma decisão de negócio; **média**, dá para inferir, mas a inferência pode levar a uma direção equivocada; **baixa**, dá para seguir com menos detalhe.
