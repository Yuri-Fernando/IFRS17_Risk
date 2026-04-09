"""
Pipeline Central

Orquestra execução completa do modelo de Risk Adjustment.
Integra todas as etapas: dados → modeling → simulação → cálculo → validação.

Pensado como se fosse rodando em AWS (mas executa localmente).
"""

from src.data.load_data import load_data
from src.data.preprocess import preprocess
from src.actuarial.cashflow_projection import project_cashflows
from src.actuarial.bel_calculation import calculate_bel
from src.modeling.frequency import train_frequency
from src.modeling.severity import train_severity
from src.simulation.monte_carlo import simulate_losses
from src.modeling.risk_adjustment import calculate_risk_adjustment
from src.validation.model_metrics import calculate_all_metrics
from src.validation.distribution_tests import ks_test
from src.governance.audit_log import AuditLog


def run_pipeline(
    data_source: str = 'synthetic',
    n_simulations: int = 10000,
    normalize_data: bool = True,
    ra_method: str = 'var',
    ra_alpha: float = 95,
    verbose: bool = True
) -> dict:
    """
    Pipeline completo de Risk Adjustment.

    Etapas:
    1. Carregamento e preprocessamento
    2. Projeção atuarial (BEL)
    3. Treinamento de modelos (freq + sev)
    4. Simulação Monte Carlo
    5. Cálculo de Risk Adjustment
    6. Validação

    Args:
        data_source: fonte de dados ('synthetic' ou 'csv')
        n_simulations: número de simulações Monte Carlo
        normalize_data: se deve normalizar variáveis
        ra_method: método de RA ('var', 'cte', 'cost_of_capital')
        ra_alpha: percentil para VaR/CTE
        verbose: exibe progresso

    Returns:
        Dicionário com resultado completo
    """

    audit = AuditLog()

    if verbose:
        print("=" * 70)
        print("IFRS 17 Risk Adjustment Engine - Pipeline Execution")
        print("=" * 70)

    # =========================================================================
    # ETAPA 1: Carregamento e Preprocessamento
    # =========================================================================
    if verbose:
        print("\n[1/6] Carregando dados...")

    data = load_data(source=data_source)
    audit.record("Data Loading", details={'records': len(data), 'source': data_source})

    if verbose:
        print(f"  Registros carregados: {len(data)}")
        print(f"  Colunas: {list(data.columns)}")

    # Preprocessamento
    if verbose:
        print("\n[2/6] Preprocessando dados...")

    preprocessed_data, scaler = preprocess(data, normalize=normalize_data)
    audit.record("Data Preprocessing", details={'normalized': normalize_data})

    if verbose:
        print("  Dados processados com sucesso")

    # =========================================================================
    # ETAPA 2: Projeção Atuarial
    # =========================================================================
    if verbose:
        print("\n[3/6] Projetando fluxos atuariais...")

    projections = project_cashflows(preprocessed_data, projection_years=30)
    bel = calculate_bel(projections, discount_rate=0.05)

    audit.record(
        "Actuarial Projection",
        details={
            'projection_years': 30,
            'bel_total': float(bel['total_bel'])
        }
    )

    if verbose:
        print(f"  BEL calculado: ${bel['total_bel']:.2f}")

    # =========================================================================
    # ETAPA 3: Treinamento de Modelos
    # =========================================================================
    if verbose:
        print("\n[4/6] Treinando modelos estatísticos...")

    freq_model = train_frequency(preprocessed_data)
    sev_model = train_severity(preprocessed_data)

    audit.record(
        "Model Training",
        details={
            'freq_distribution': freq_model.distribution,
            'sev_distribution': sev_model.distribution
        }
    )

    if verbose:
        print(f"  Frequência: {freq_model.distribution}")
        print(f"  Severidade: {sev_model.distribution}")

    # =========================================================================
    # ETAPA 4: Simulação Monte Carlo
    # =========================================================================
    if verbose:
        print(f"\n[5/6] Rodando {n_simulations:,} simulações Monte Carlo...")

    losses = simulate_losses(freq_model, sev_model, n_simulations=n_simulations)

    audit.record(
        "Monte Carlo Simulation",
        details={
            'n_simulations': n_simulations,
            'mean_loss': float(losses.mean()),
            'std_loss': float(losses.std())
        }
    )

    if verbose:
        print(f"  Perda média simulada: ${losses.mean():.2f}")
        print(f"  Desvio padrão: ${losses.std():.2f}")

    # =========================================================================
    # ETAPA 5: Cálculo de Risk Adjustment
    # =========================================================================
    if verbose:
        print("\n[6/6] Calculando Risk Adjustment...")

    ra_result = calculate_risk_adjustment(
        losses,
        method=ra_method,
        alpha=ra_alpha,
        include_all_methods=True
    )

    audit.record(
        "Risk Adjustment Calculation",
        details=ra_result
    )

    if verbose:
        print(f"  Método: {ra_result['method_description']}")
        print(f"  Risk Adjustment: ${ra_result['Risk_Adjustment']:.2f}")

    # =========================================================================
    # CONSOLIDAÇÃO FINAL
    # =========================================================================
    # Validação dos modelos
    ks_result = ks_test(losses[losses > 0], distribution='lognormal')

    audit.record(
        "Distribution Testing",
        details=ks_result
    )

    # Resultado final
    result = {
        'status': 'SUCCESS',
        'execution_time': 'completed',
        'data': {
            'records': len(data),
            'features': len(data.columns)
        },
        'actuarial': {
            'bel': float(bel['total_bel']),
            'projection_years': 30
        },
        'models': {
            'frequency': {
                'distribution': freq_model.distribution,
                'parameters': freq_model.params
            },
            'severity': {
                'distribution': sev_model.distribution,
                'parameters': sev_model.params
            }
        },
        'simulation': {
            'n_simulations': n_simulations,
            'mean_loss': float(losses.mean()),
            'std_loss': float(losses.std()),
            'min_loss': float(losses.min()),
            'max_loss': float(losses.max()),
            'percentiles': {
                'p5': float(losses.quantile(0.05)),
                'p50': float(losses.quantile(0.50)),
                'p95': float(losses.quantile(0.95))
            }
        },
        'risk_adjustment': ra_result,
        'validation': ks_result,
        'audit_log': audit.logs
    }

    if verbose:
        print("\n" + "=" * 70)
        print("RESULTADO FINAL")
        print("=" * 70)
        print(f"BEL: ${bel['total_bel']:.2f}")
        print(f"RA ({ra_method.upper()}): ${ra_result['Risk_Adjustment']:.2f}")
        print(f"Provisão Total (IFRS 17): ${bel['total_bel'] + ra_result['Risk_Adjustment']:.2f}")
        print("=" * 70)

    return result
