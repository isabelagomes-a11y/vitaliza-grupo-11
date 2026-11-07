"""Monta a pasta da entrega da semana 5 para o Google Drive, só com o que vai ser entregue.

Uso (na raiz do projeto):  .venv/bin/python src/montar_entrega_semana5.py [pasta_de_destino]
Padrão: ~/Downloads/Vitaliza_G11_Entrega_Semana5. Não copia dados, .venv nem .env.
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DEST = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads" / "Vitaliza_G11_Entrega_Semana5"

if DEST.exists():
    shutil.rmtree(DEST)
(DEST / "EDA" / "codigo").mkdir(parents=True)

ent = RAIZ / "saidas" / "entrega_semana5"
for pdf in sorted(ent.glob("Vitaliza_G11_*.pdf")):
    shutil.copy2(pdf, DEST / pdf.name)
shutil.copy2(RAIZ / "notebooks" / "eda_unificada.ipynb", DEST / "EDA" / "eda_unificada.ipynb")
shutil.copytree(RAIZ / "saidas" / "graficos_unificados", DEST / "EDA" / "graficos")
shutil.copytree(RAIZ / "src" / "vitaliza", DEST / "EDA" / "codigo" / "vitaliza", ignore=shutil.ignore_patterns("__pycache__"))
shutil.copy2(RAIZ / "src" / "build_eda_unificada.py", DEST / "EDA" / "codigo" / "build_eda_unificada.py")
shutil.copy2(RAIZ / "requirements.txt", DEST / "EDA" / "codigo" / "requirements.txt")

(DEST / "LEIA-ME.md").write_text("""# Vitaliza · Grupo 11 · Entrega da semana 5

| Artefato | Arquivo |
|---|---|
| Negócios — Customer Segmentation Report | `Vitaliza_G11_Relatorio_Segmentacao.pdf` (5 páginas) |
| Cartões de persona | `Vitaliza_G11_Cartoes_Persona.pdf` (4 cartões) |
| Tecnologia — mini deck da EDA | `Vitaliza_G11_MiniDeck_EDA.pdf` (5 slides) |
| Tecnologia — EDA (código + visualizações) | `EDA/eda_unificada.ipynb` (notebook executado), `EDA/graficos/` (11 gráficos e `numeros.json`), `EDA/codigo/` (código Python) |

Os dados do case não estão nesta pasta. Para rodar o código: colocar os arquivos do data room em `dados/brutos/`
(ou indicar a pasta na variável `VITALIZA_DADOS`), instalar `EDA/codigo/requirements.txt` e rodar
`python build_eda_unificada.py` a partir da raiz do projeto.
""", encoding="utf-8")

for p in sorted(DEST.rglob("*")):
    if p.is_file():
        print(p.relative_to(DEST))
