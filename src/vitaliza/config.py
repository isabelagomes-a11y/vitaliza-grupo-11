"""Caminhos da solução unificada. Os dados brutos ficam em dados/brutos/ (fora do Git)."""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]          # raiz do repositório
DADOS = Path(os.environ.get("VITALIZA_DADOS", RAIZ / "dados" / "brutos"))
SAIDAS = RAIZ / "saidas"
