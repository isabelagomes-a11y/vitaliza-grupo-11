# Registro de decisões

| Data | Arquivo | Problema | Decisão | Critério | Linhas afetadas | Quem |
|------|---------|----------|---------|----------|-----------------|------|
| 2026-11-01 | usuarios.csv | Contas sem `data_nascimento` (5,08%) ou sem `sexo` (4,84%) | **Remover** da base master `dados/processados/usuarios_master.csv`, que passa a ser a base chave do projeto. Motivo: data de nascimento e sexo são consideradas variáveis de alta importância para a análise (criticidade alta). IDs removidos e motivo em `dados/processados/usuarios_removidos.csv`; script `src/usuarios_master.py`. Risco aceito: as contas removidas ficam fora da contagem de pagantes e do churn, que podem não bater com o enunciado | Célula vazia ou só com espaços em `data_nascimento` ou em `sexo` | 6.285 de 64.948 (9,68%): 3.143 só sem nascimento, 2.984 só sem sexo, 158 sem os dois. Restam 58.663 | grupo 11 |
