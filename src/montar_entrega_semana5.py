"""Monta a pasta da entrega da semana 5 para o Google Drive, só com o que vai ser entregue.

Uso (na raiz do projeto):  python src/montar_entrega_semana5.py [pasta_de_destino]
Padrão: ~/Downloads/Vitaliza_G10_Entrega_Semana5. Não copia dados, .venv nem .env.
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DEST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads" / "Vitaliza_G10_Entrega_Semana5"

if DEST.exists():
    shutil.rmtree(DEST)
(DEST / "EDA" / "codigo").mkdir(parents=True)

ent = RAIZ / "saidas" / "entrega_semana5"
for pdf in sorted(ent.glob("Vitaliza_G10_*.pdf")):
    shutil.copy2(pdf, DEST / pdf.name)
shutil.copy2(RAIZ / "decisoes.md", DEST / "decisoes.md")
for nb in ("eda.ipynb", "segmentacao_kmeans.ipynb"):
    shutil.copy2(RAIZ / "notebooks" / nb, DEST / "EDA" / nb)
shutil.copytree(RAIZ / "saidas" / "graficos", DEST / "EDA" / "graficos")
shutil.copytree(RAIZ / "src" / "vitaliza", DEST / "EDA" / "codigo" / "vitaliza", ignore=shutil.ignore_patterns("__pycache__"))
for script in ("build_eda.py", "build_kmeans.py", "conferencia_enunciado.py", "completude.py", "completude_config.json"):
    shutil.copy2(RAIZ / "src" / script, DEST / "EDA" / "codigo" / script)
shutil.copy2(RAIZ / "requirements.txt", DEST / "EDA" / "codigo" / "requirements.txt")

(DEST / "LEIA-ME.md").write_text("""# Vitaliza · Grupo 10 · Entrega da semana 5

Igor Moreira · Isabela Gomes · Lucas Murta · Roberto Fernandes Fortes Neto

| Artefato | Arquivo |
|---|---|
| Negócios — Customer Segmentation Report | `Vitaliza_G10_Relatorio_Segmentacao.pdf` (5 páginas) |
| Cartões de persona | `Vitaliza_G10_Cartoes_Persona.pdf` (4 cartões) |
| Tecnologia — apresentação executiva (processo e insights) | `Vitaliza_G10_MiniDeck_EDA.pdf` (capa + 5 slides) |
| Tecnologia — documentação das decisões | `decisoes.md` (cada decisão com motivo, critério, linhas afetadas e onde é aplicada) |
| Tecnologia — EDA (código + visualizações) | `EDA/eda.ipynb` e `EDA/segmentacao_kmeans.ipynb` (executados), `EDA/graficos/`, `EDA/codigo/` |

Repositório: github.com/isabelagomes-a11y/vitaliza-grupo-11 (branch main).
Os dados do case não estão nesta pasta. Para rodar o código: colocar os arquivos do data room em `dados/brutos/`
(ou indicar a pasta na variável `VITALIZA_DADOS`), instalar `EDA/codigo/requirements.txt` e rodar
`python build_eda.py` a partir da raiz do projeto.
""", encoding="utf-8")

for p in sorted(DEST.rglob("*")):
    if p.is_file():
        print(p.relative_to(DEST))
