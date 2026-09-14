#!/usr/bin/env python
"""Verifica dependências e baixa o dataset German Credit, se ausente."""

from __future__ import annotations

import subprocess
import sys
import urllib.request
from pathlib import Path

DATASET_URL = "https://raw.githubusercontent.com/selva86/datasets/master/GermanCredit.csv"
DATASET_PATH = Path("data/raw/german_credit.csv")


def check_and_install_requirements() -> None:
    print("Verificando dependências (requirements.txt)...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"], check=True)
    print("Dependências OK.")


def download_dataset() -> None:
    if DATASET_PATH.exists():
        print(f"Dataset já presente em {DATASET_PATH}, pulando download.")
        return
    print(f"Baixando dataset German Credit de {DATASET_URL} ...")
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(DATASET_URL, DATASET_PATH)
        print(f"Dataset salvo em {DATASET_PATH}.")
    except Exception as exc:  # noqa: BLE001
        print(f"Falha ao baixar dataset ({exc}). Use --data-source synthetic no run_pipeline.py.")


if __name__ == "__main__":
    check_and_install_requirements()
    download_dataset()
    print("\nSetup concluído. Execute: python run_pipeline.py")
