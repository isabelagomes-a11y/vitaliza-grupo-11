# Vitaliza · grupo 11

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

## Unificação dos três trabalhos (07/11/2026)

O grupo fez três trabalhos em paralelo. Eles foram comparados e somados numa solução só:

- **S1** — análise completa (diagnóstico, modelo, uplift da campanha, retorno, briefing da mensagem): `saidas/solucao1/`
- **S2** — Plano de Inteligência de Retenção (deck para o Conselho): `saidas/solucao2/`
- **S3** — este repositório: limpeza, EDA, segmentação e personas (`src/`, `notebooks/`, `saidas/`)

| Onde | O quê |
|---|---|
| `docs/COMPARATIVO.md` | os três trabalhos lado a lado, aderência ao guia e números conferidos |
| `docs/SOLUCAO_UNIFICADA.md` | o melhor de cada um, com a fonte de cada peça |
| `ROADMAP.md` | fases até a semana 5 (15/11) e a semana 10 (20/12), com os critérios de avaliação |
| `ACOMPANHAMENTO.md` | checklist vivo: decisões, donos, status, histórico |
| `src/vitaliza/` | código unificado: base, limpeza, variáveis e segmentos |
| `src/build_eda_unificada.py` | gera `notebooks/eda_unificada.ipynb`, os gráficos e os números |
| `saidas/entrega_semana5/` | **entrega final da semana 5**: relatório de segmentação (5 p.), cartões de persona e mini deck, com as fontes em HTML |
| `src/montar_entrega_semana5.py` | monta a pasta para o Google Drive só com o que vai ser entregue |
| `saidas/solucao3/` | registro da entrega original da S3 (Word, PowerPoint e PDF) |
| `saidas/graficos_unificados/` | os 11 gráficos dos documentos e `numeros.json` |
| `docs/diagramas/` | fluxograma do sistema (`.drawio`, 3 páginas) e imagens PNG |

Para gerar de novo a EDA unificada, na raiz do projeto: `.venv/bin/python src/build_eda_unificada.py` (Windows: `.venv\Scripts\python src\build_eda_unificada.py`).
