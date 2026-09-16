#!/usr/bin/env python
"""Verifica/instala dependências. Não há dataset externo a baixar — o
portfólio é 100% sintético e gerado em tempo de execução (src/data/synthetic_portfolio.py)."""

from __future__ import annotations

import subprocess
import sys


def check_and_install_requirements() -> None:
    print("Verificando dependências (requirements.txt)...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"], check=True)
    print("Dependências OK.")


if __name__ == "__main__":
    check_and_install_requirements()
    print("\nSetup concluído. Execute:")
    print("  python run_pipeline.py                          (pipeline via linha de comando)")
    print("  jupyter notebook notebooks/pension_risk_adjustment_e2e.ipynb   (notebook completo)")
    print("  streamlit run dashboard/app.py                   (dashboard interativo)")
