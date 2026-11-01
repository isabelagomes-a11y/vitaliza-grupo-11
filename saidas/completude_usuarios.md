# Completude do usuarios.csv

Base: `dados/brutos/usuarios.csv`, 64948 linhas. Gerado por `src/completude.py usuarios`.

- **Vazios:** nulo, célula vazia ou só com espaços.

| Coluna | Vazios | % vazios | Vazios + sem conteúdo | % | Criticidade |
|---|---|---|---|---|---|
| `user_id` | 0 | 0.0% | 0 | 0.0% | alta |
| `email` | 0 | 0.0% | 0 | 0.0% | média |
| `data_cadastro` | 0 | 0.0% | 0 | 0.0% | alta |
| `data_nascimento` | 3301 | 5.08% | 3301 | 5.08% | alta |
| `sexo` | 3142 | 4.84% | 3142 | 4.84% | alta |
| `cidade` | 0 | 0.0% | 0 | 0.0% | baixa |
| `uf` | 0 | 0.0% | 0 | 0.0% | baixa |
| `cep_prefixo` | 1894 | 2.92% | 1894 | 2.92% | baixa |
| `canal_aquisicao` | 0 | 0.0% | 0 | 0.0% | alta |
| `sistema` | 0 | 0.0% | 0 | 0.0% | baixa |
| `versao_app` | 0 | 0.0% | 0 | 0.0% | baixa |
| `relogio_conectado` | 0 | 0.0% | 0 | 0.0% | média |

## Justificativa

- **`user_id` (alta):** Chave de todos os arquivos; sem ela a conta não se liga a nada.
- **`email` (média):** Canal de e-mail do CRM; sem ele sobram push e WhatsApp, mas a escolha de canal muda.
- **`data_cadastro` (alta):** Tempo de casa, safras e respeito ao corte. Está completa, mas há datas posteriores ao corte (máx. 04/04/2027): qualidade, não completude.
- **`data_nascimento` (alta):** Decisão do grupo: variável de alta importância para a análise. Contas sem ela saem da base master (ver decisoes.md).
- **`sexo` (alta):** Decisão do grupo: variável de alta importância para a análise. Contas sem ela saem da base master (ver decisoes.md). Tem 6 grafias (F, Fem, feminino, M, Masc, masculino): padronização, não falta.
- **`cidade` (baixa):** Descritiva; texto livre com grafias diferentes (SP, Sampa, S. Paulo): padronização, não falta.
- **`uf` (baixa):** Descritiva.
- **`cep_prefixo` (baixa):** cidade e uf estão completas e cobrem a localização.
- **`canal_aquisicao` (alta):** Entra no churn por canal e no CAC; quem vem de influenciador paga R$ 239,90 no primeiro ano. Valor 'interno' (60 contas) não está no dicionário.
- **`sistema` (baixa):** O canal de cobrança, que importa para o churn, vem de assinaturas.csv. Tem 5 grafias (ios, iOS, IOS, android, Android).
- **`versao_app` (baixa):** Só ajuda a investigar problema técnico.
- **`relogio_conectado` (média):** 'nenhum' é categoria válida (sem relógio). Inferível pela origem em atividades.parquet, mas só para quem treinou em 2026.

Critérios de criticidade: **alta**, a falta pode afetar uma decisão de negócio; **média**, dá para inferir, mas a inferência pode levar a uma direção equivocada; **baixa**, dá para seguir com menos detalhe.
