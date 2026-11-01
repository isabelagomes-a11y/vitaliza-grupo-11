# Completude do onboarding.csv

Base: `dados/brutos/onboarding.csv`, 63929 linhas. Gerado por `src/completude_onboarding.py`.

- **Vazios:** célula vazia ou só com espaços.
- **Sem conteúdo:** "-", ".", "asdf", "kkkk", "nada", "nao sei", "ok", "sla", "x", "😂".
  Critério proposto, ainda não registrado como decisão de limpeza.

| Coluna | Vazios | % vazios | Vazios + sem conteúdo | % | Criticidade |
|---|---|---|---|---|---|
| `onboarding_id` | 0 | 0.0% | 0 | 0.0% | baixa |
| `user_id` | 0 | 0.0% | 0 | 0.0% | alta |
| `respondido_em` | 0 | 0.0% | 0 | 0.0% | média |
| `objetivo_texto` | 5467 | 8.55% | 19235 | 30.09% | média |
| `como_conheceu` | 4586 | 7.17% | 16101 | 25.19% | baixa |
| `nivel` | 4513 | 7.06% | 4513 | 7.06% | média |
| `dias_por_semana` | 6368 | 9.96% | 6368 | 9.96% | média |

## Justificativa

- **`onboarding_id` (baixa):** Identificador da resposta; nenhuma decisão depende dele.
- **`user_id` (alta):** Chave que liga o questionário a assinaturas e treinos; sem ela a linha não serve. Está completa, sem duplicados.
- **`respondido_em` (média):** Garante que só entra informação anterior ao corte (vai de 01/09/2020 a 30/09/2026). Está completa.
- **`objetivo_texto` (média):** Base da extração com IA e da mensagem personalizada. Dá para decidir quem contatar pelo comportamento, mas tratar 'asdf' ou '😂' como objetivo desviaria a extração. Sugestão: marcar como 'não informado', sem imputar.
- **`como_conheceu` (baixa):** usuarios.csv já traz canal_aquisicao, estruturado e atribuído pelo marketing; o texto livre só acrescenta detalhe.
- **`nivel` (média):** Inferível em parte por ritmo e frequência em atividades.parquet, mas nível declarado e real podem divergir; errar muda tom e oferta da mensagem.
- **`dias_por_semana` (média):** A diferença entre intenção e uso real é candidata a sinal de saída; sem a intenção, sobra só o uso. Fora os vazios, tem 23 grafias ('3', '3x', '3 vezes', 'todos'): padronização, não falta.

## Contas sem questionário

1019 das 64948 contas de `usuarios.csv` (1.57%) não têm linha no onboarding. O dicionário não explica por quê. Criticidade baixa por ora; a reavaliar se se concentrarem em pagantes.

Critérios de criticidade: **alta**, a falta pode afetar uma decisão de negócio; **média**, dá para inferir, mas a inferência pode levar a uma direção equivocada; **baixa**, dá para seguir com menos detalhe.
