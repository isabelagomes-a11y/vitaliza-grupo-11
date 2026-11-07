# Completude do uso_mensal.csv

Base: `dados/brutos/uso_mensal.csv`, 591662 linhas. Gerado por `src/completude.py uso_mensal`.

- **Vazios:** nulo, célula vazia ou só com espaços.

| Coluna | Vazios | % vazios | Vazios + sem conteúdo | % | Criticidade |
|---|---|---|---|---|---|
| `user_id` | 0 | 0.0% | 0 | 0.0% | alta |
| `mes` | 0 | 0.0% | 0 | 0.0% | alta |
| `atividades` | 0 | 0.0% | 0 | 0.0% | alta |
| `atividades_ar_livre` | 0 | 0.0% | 0 | 0.0% | média |
| `atividades_video` | 0 | 0.0% | 0 | 0.0% | média |
| `minutos` | 0 | 0.0% | 0 | 0.0% | média |
| `dias_ativos` | 0 | 0.0% | 0 | 0.0% | média |
| `sessoes_app` | 0 | 0.0% | 0 | 0.0% | alta |

## Justificativa

- **`user_id` (alta):** Chave para ligar o uso ao assinante. Completo; nenhum user_id fora de usuarios.csv; sem duplicado por usuário e mês.
- **`mes` (alta):** Situa o uso no tempo e permite usar só meses anteriores à data de referência. Completo, de 2025-01 a 2026-09. Cobertura muda em jan/2026: em 2025 quase só pagantes; a partir de 2026 também usuários grátis.
- **`atividades` (alta):** Frequência de treino, principal lente de comportamento. Completa e coerente (= ar livre + vídeo). Em 2026 diverge do atividades.parquet em 13% dos usuário-mês (parquet sempre maior).
- **`atividades_ar_livre` (média):** Distingue perfil de treino; o tipo de cada treino de 2026 também está em atividades.parquet.
- **`atividades_video` (média):** Distingue perfil de treino; o tipo de cada treino de 2026 também está em atividades.parquet.
- **`minutos` (média):** Intensidade do uso; recalculável pelo parquet em 2026, mas as fontes divergem. Sem valores impossíveis (20 a 99 min por treino entre p1 e p99).
- **`dias_ativos` (média):** Regularidade do uso; recalculável pelo parquet em 2026. Coerente: nunca maior que os dias do mês nem que o número de treinos.
- **`sessoes_app` (alta):** Única fonte de aberturas do app (engajamento sem treino); nenhuma outra base supre.

## Contas sem linha nesta base

1118 das 64948 contas de `usuarios.csv` (1.72%) não têm linha em `uso_mensal.csv`. Mês sem linha nem sempre é uso zero: de 219 a 379 assinantes de 31/07 não têm linha em maio, junho ou julho, e cerca de 28% deles têm treinos no atividades.parquet nesses meses. Tratados como uso zero com marcação (ver decisoes.md).

Critérios de criticidade: **alta**, a falta pode afetar uma decisão de negócio; **média**, dá para inferir, mas a inferência pode levar a uma direção equivocada; **baixa**, dá para seguir com menos detalhe.
