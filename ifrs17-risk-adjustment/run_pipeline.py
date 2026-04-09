#!/usr/bin/env python3
"""
IFRS 17 Risk Adjustment Engine - Main Entry Point

Executa pipeline completo de cálculo de Risk Adjustment.
"""

import sys
import argparse
import json
from pathlib import Path

from src.cloud.pipeline import run_pipeline
from src.governance.model_versioning import ModelVersion, ModelRegistry
from src.governance.audit_log import AuditLog


def main():
    """Executa pipeline com argumentos de linha de comando."""

    parser = argparse.ArgumentParser(
        description="IFRS 17 Risk Adjustment Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python run_pipeline.py --data-source synthetic
  python run_pipeline.py --data-source csv --data-file data/raw/dataset.csv
  python run_pipeline.py --simulations 50000 --ra-method cte
        """
    )

    # Argumentos de dados
    parser.add_argument(
        "--data-source",
        choices=["synthetic", "csv"],
        default="synthetic",
        help="Fonte de dados (padrão: synthetic)"
    )

    parser.add_argument(
        "--data-file",
        type=str,
        default="data/raw/dataset.csv",
        help="Caminho do arquivo CSV (se --data-source csv)"
    )

    # Argumentos de simulação
    parser.add_argument(
        "--simulations",
        type=int,
        default=10000,
        help="Número de simulações Monte Carlo (padrão: 10000)"
    )

    parser.add_argument(
        "--normalize",
        action="store_true",
        default=True,
        help="Normalizar variáveis (padrão: True)"
    )

    # Argumentos de Risk Adjustment
    parser.add_argument(
        "--ra-method",
        choices=["var", "cte", "cost_of_capital"],
        default="var",
        help="Método de cálculo de RA (padrão: var)"
    )

    parser.add_argument(
        "--ra-alpha",
        type=float,
        default=95,
        help="Percentil para VaR/CTE (padrão: 95)"
    )

    # Argumentos de saída
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports/",
        help="Diretório de saída (padrão: reports/)"
    )

    parser.add_argument(
        "--export-json",
        action="store_true",
        help="Exportar resultados em JSON"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Modo verbose (padrão: True)"
    )

    args = parser.parse_args()

    # Cria diretório de output se não existir
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Executa pipeline
    print(f"\nIFRS 17 Risk Adjustment Engine")
    print(f"==============================\n")

    result = run_pipeline(
        data_source=args.data_source,
        n_simulations=args.simulations,
        normalize_data=args.normalize,
        ra_method=args.ra_method,
        ra_alpha=args.ra_alpha,
        verbose=args.verbose
    )

    # Exporta resultados
    if args.export_json:
        output_file = Path(args.output_dir) / "result.json"

        # Converte para JSON-serializable
        json_result = {
            'status': result['status'],
            'data': {
                'records': result['data']['records'],
                'features': result['data']['features']
            },
            'actuarial': {
                'bel': float(result['actuarial']['bel']),
                'projection_years': result['actuarial']['projection_years']
            },
            'models': {
                'frequency': {
                    'distribution': result['models']['frequency']['distribution'],
                },
                'severity': {
                    'distribution': result['models']['severity']['distribution'],
                }
            },
            'simulation': {
                'n_simulations': result['simulation']['n_simulations'],
                'mean_loss': result['simulation']['mean_loss'],
                'std_loss': result['simulation']['std_loss']
            },
            'risk_adjustment': {
                'method': result['risk_adjustment']['method'],
                'risk_adjustment_value': result['risk_adjustment']['Risk_Adjustment']
            }
        }

        with open(output_file, 'w') as f:
            json.dump(json_result, f, indent=2)

        print(f"\nResultados exportados para: {output_file}")

    return result


if __name__ == "__main__":
    main()
