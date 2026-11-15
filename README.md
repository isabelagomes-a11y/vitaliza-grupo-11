# Vitaliza · grupo 10

Projeto do MBA Inteli (Aula 2) sobre o case Vitaliza, um app de assinatura para quem treina.
O grupo analisa a saída de assinantes: quem sai, por quê e em quem vale a pena agir.

As regras de trabalho do grupo (e do agente) estão em [AGENTS.md](AGENTS.md).

## Pastas

- `docs/`: enunciado do case, dicionário de dados e premissas.
- `dados/brutos/`: arquivos originais do data room, somente leitura. Não vão para o GitHub.
- `dados/processados/`: tabelas intermediárias geradas pelas análises. Não vão para o GitHub.
- `notebooks/`: notebooks Jupyter de análise.
- `src/`: código Python reutilizável.
- `saidas/`: resultados (tabelas, gráficos, relatórios).

## Arquivos

- `AGENTS.md`: regras do projeto, lidas pelo agente no início de cada conversa.
- `CLAUDE.md`: aponta o Claude Code para o AGENTS.md.
- `decisoes.md`: registro de todas as decisões de limpeza de dados.
- `.gitignore`: mantém dados, ambiente Python e `.env` fora do GitHub.

## Entrega da semana 5

| Onde | O quê |
|---|---|
| `saidas/entrega_semana5/` | **entrega final** (Grupo 10: Igor Moreira, Isabela Gomes, Lucas Murta, Roberto Fernandes Fortes Neto): relatório de segmentação (5 p.) e mini deck (capa + 5 slides) em PDF, Word e PowerPoint; cartões de persona em PDF, com a fonte em HTML |
| `src/entrega/` | gera o relatório e o mini deck a partir dos números do código (`dados.py` → `graficos.py` → `relatorio.py`, `minideck.py`) |
| `notebooks/eda.ipynb` | EDA executada (carga, limpeza, padrões, correlações, segmentação) |
| `saidas/graficos/` | os 11 gráficos dos documentos e `numeros.json`; 12 e 13 e `kmeans.json` vêm do notebook do k-means |
| `src/vitaliza/` | código: leitura, limpeza, status de cada assinatura, variáveis e segmentos |
| `src/build_eda.py` | gera o notebook, os gráficos e os números |
| `src/montar_entrega_semana5.py` | monta a pasta para o Google Drive só com o que vai ser entregue |
| `notebooks/segmentacao_kmeans.ipynb` · `src/build_kmeans.py` | k-means avaliado nas quatro lentes e comparado com a camada por regra (por que a regra foi escolhida) |
| `src/conferencia_enunciado.py` | confere a reconstrução das assinaturas contra o enunciado (`saidas/conferencia_enunciado.csv`, 17 de 17) |
| `src/completude.py` · `.claude/skills/avaliar-completude/` | completude e criticidade de cada base (`saidas/completude_*`) |
| tag `pipeline-s3` | scripts originais de limpeza e os notebooks de EDA e segmentação anteriores à unificação |
| `ROADMAP.md` · `ACOMPANHAMENTO.md` | caminho até 15/11 e 20/12; decisões e status |

Na raiz do projeto: `.venv/bin/python src/build_eda.py` (Windows: `.venv\Scripts\python src\build_eda.py`).
