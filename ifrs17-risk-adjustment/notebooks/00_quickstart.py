"""
Quickstart - IFRS 17 Risk Adjustment

Demonstração rápida do pipeline completo.

Este arquivo pode ser usado como:
1. Script Python puro (python notebooks/00_quickstart.py)
2. Notebook Jupyter (convertido com nbconvert)
3. Referência para estrutura do pipeline
"""

# Imports
import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cloud.pipeline import run_pipeline
from src.cloud.deploy_local_simulation import simulate_aws_deployment, estimate_aws_costs


def main():
    """Executa quickstart."""

    print("=" * 70)
    print("IFRS 17 Risk Adjustment Engine - Quickstart")
    print("=" * 70)

    # Executa pipeline com dados sintéticos
    print("\n[1/3] Executando pipeline...")
    result = run_pipeline(
        data_source='synthetic',
        n_simulations=10000,
        ra_method='var',
        ra_alpha=95,
        verbose=True
    )

    # Apresenta resultados
    print("\n[2/3] Resultados:")
    print(f"  BEL (Best Estimate Liability): R$ {result['actuarial']['bel']:,.2f}")
    print(f"  RA (Risk Adjustment): R$ {result['risk_adjustment']['Risk_Adjustment']:,.2f}")
    print(f"  Provisão Total: R$ {result['actuarial']['bel'] + result['risk_adjustment']['Risk_Adjustment']:,.2f}")

    print("\n[3/3] Arquitetura AWS (Simulada):")
    deployment = simulate_aws_deployment()
    costs, total = estimate_aws_costs()

    print(f"\n  Custo estimado mensal: R$ {total:.2f}")

    print("\n" + "=" * 70)
    print("Próximos passos:")
    print("  1. Ver docs/business_explanation.md para entender o modelo")
    print("  2. Ver reports/methodology.md para detalhes técnicos")
    print("  3. Executar: python run_pipeline.py --help para mais opções")
    print("=" * 70)


if __name__ == "__main__":
    main()
