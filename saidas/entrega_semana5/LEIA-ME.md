# Entrega da semana 5 · Grupo 10 · versão final

Igor Moreira · Isabela Gomes · Lucas Murta · Roberto Fernandes Fortes Neto

| O guia pede | Arquivo |
|---|---|
| **Negócios — Customer Segmentation Report** (3–4 segmentos com personas, drivers por segmento, priorização imediata × monitoramento, visualizações da EDA, limitações) | `Vitaliza_G10_Relatorio_Segmentacao.pdf` (5 p.; editável em `.docx`) |
| Cartões de persona (1 por segmento, nome no centro, lidos em 10 s) | `Vitaliza_G10_Cartoes_Persona.pdf` (4 cartões) |
| **Tecnologia — apresentação executiva** (processo analítico e insights) | `Vitaliza_G10_MiniDeck_EDA.pdf` (capa + 5 slides; editável em `.pptx`, com notas do apresentador) |
| **Tecnologia — repositório e documentação** | `notebooks/eda.ipynb`, `notebooks/segmentacao_kmeans.ipynb`, `src/`, `saidas/graficos/` e `decisoes.md` (cada decisão com motivo e onde é aplicada) |

Todos os números vêm do código unificado em `src/vitaliza/`. Para gerar de novo (na raiz do projeto, depois de `src/build_eda.py` e `src/build_kmeans.py`):
`src/entrega/dados.py` → `src/entrega/graficos.py` → `src/entrega/relatorio.py` e `src/entrega/minideck.py`; o PDF sai do Word e do PowerPoint (Salvar como PDF).
`fontes/personas.html` gera o PDF dos cartões (abrir no navegador e imprimir em PDF).

**Para o Google Drive** (pasta pública; cada integrante envia o link na Adalove): rode `src/montar_entrega_semana5.py` na raiz do projeto. Ele monta uma pasta só com os PDFs, a EDA (código, notebooks e gráficos) e o `decisoes.md`, sem dados.
