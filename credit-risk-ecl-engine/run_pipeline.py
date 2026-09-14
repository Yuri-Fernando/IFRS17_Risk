#!/usr/bin/env python
"""
CLI de execução do Credit Risk ECL Engine.

Exemplos:
    python run_pipeline.py
    python run_pipeline.py --data-source synthetic
    python run_pipeline.py --simulations 50000 --correlation 0.35
    python run_pipeline.py --export-json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Garante saída UTF-8 no console do Windows (evita UnicodeEncodeError com
# caracteres como →, ² usados nos logs do pipeline).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.cloud.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Credit Risk ECL Engine — IFRS 9 / CMN 4.966")
    parser.add_argument("--data-source", choices=["csv", "synthetic"], default="csv")
    parser.add_argument("--data-file", default="data/raw/german_credit.csv")
    parser.add_argument("--simulations", type=int, default=10000)
    parser.add_argument("--correlation", type=float, default=0.25, help="Correlação entre segmentos (cópula)")
    parser.add_argument("--asset-correlation", type=float, default=0.15, help="Correlação de ativos (Vasicek)")
    parser.add_argument("--export-json", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    result = run_pipeline(
        data_source=args.data_source,
        data_path=args.data_file if args.data_source == "csv" else None,
        n_simulations=args.simulations,
        inter_segment_correlation=args.correlation,
        asset_correlation=args.asset_correlation,
        verbose=not args.quiet,
    )

    df_ecl = result.pop("df_ecl", None)

    print("\n" + "=" * 70)
    print("RESULTADO — CREDIT RISK ECL ENGINE")
    print("=" * 70)
    print(f"Modelo campeão : {result['pd_models']['champion']}")
    print(f"Gini / KS      : {result['validation']['gini']:.3f} / {result['validation']['ks']:.3f}")
    print(f"Exposição total: R$ {result['portfolio']['total_exposure']:,.2f}")
    print(f"ECL total      : R$ {result['portfolio']['total_ecl']:,.2f}")
    print(f"Coverage ratio : {result['portfolio']['coverage_ratio']:.2%}")
    print(f"VaR 99.9%      : R$ {result['monte_carlo']['var'].get('var_99.9', 0):,.2f}")
    print(f"Benef. diversif: R$ {result['monte_carlo']['diversification_benefit']:,.2f}")
    print(f"Tempo execução : {result['elapsed_seconds']}s")
    print("=" * 70)

    Path("reports").mkdir(exist_ok=True)
    if args.export_json:
        export_path = Path("reports/result_final.json")
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\nResultado exportado em: {export_path}")

    if df_ecl is not None:
        Path("data/processed").mkdir(parents=True, exist_ok=True)
        df_ecl.to_csv("data/processed/portfolio_ecl_scored.csv", index=False)
        print("Carteira detalhada (por contrato) salva em: data/processed/portfolio_ecl_scored.csv")


if __name__ == "__main__":
    main()
