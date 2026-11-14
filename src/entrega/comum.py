"""Dados e textos comuns ao relatório e ao mini deck da semana 5."""
import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
G = RAIZ / "saidas" / "graficos"
PNG = G / "png"
ENTREGA = RAIZ / "saidas" / "entrega_semana5"

GRUPO = "Grupo 10"
INTEGRANTES = ["Igor Moreira", "Isabela Gomes", "Lucas Murta", "Roberto Fernandes Fortes Neto"]
REPO = "github.com/isabelagomes-a11y/vitaliza-grupo-11"


def carregar():
    """numeros.json (build_eda), kmeans.json (build_kmeans), entrega.json (entrega/dados) e a conferência."""
    n = json.loads((G / "numeros.json").read_text(encoding="utf-8"))
    k = json.loads((G / "kmeans.json").read_text(encoding="utf-8"))
    d = json.loads((G / "entrega.json").read_text(encoding="utf-8"))
    with open(RAIZ / "saidas" / "conferencia_enunciado.csv", encoding="utf-8") as f:
        conf = list(csv.DictReader(f))
    n["seg"] = {s["segmento"]: s for s in n["segmentos"]}
    n["cam"] = {(c["segmento"], c["camada"]): c for c in n["camadas"]}
    n["acao"] = {(p["segmento"], p["camada"]): p["acao"] for p in n["priorizacao"]}
    return n, k, d, conf


def br(v, casas=1):
    return f"{v:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def sinal(v, casas=1):
    """Efeito com sinal explícito: +6,2 ou −6,6 (sinal de menos tipográfico)."""
    return ("+" if v > 0 else "−" if v < 0 else "") + br(abs(v), casas)


def numero_br(texto):
    """Número de um CSV ('8540.0', '8.1') no padrão brasileiro ('8.540', '8,1')."""
    v = float(texto)
    return inteiro(v) if v == int(v) else br(v)


def inteiro(v):
    return f"{int(round(v)):,}".replace(",", ".")


def n_decisoes():
    return sum(1 for l in (RAIZ / "decisoes.md").read_text(encoding="utf-8").splitlines() if l.startswith("| 2026-"))
