"""
Testes Unitários - Modelos

Valida funcionamento dos componentes principais do pipeline.
"""

import pytest
import numpy as np
import pandas as pd

from src.data.load_data import generate_synthetic_data
from src.data.preprocess import preprocess
from src.modeling.frequency import train_frequency
from src.modeling.severity import train_severity
from src.simulation.monte_carlo import simulate_losses
from src.modeling.risk_adjustment import calculate_risk_adjustment


class TestDataLoading:
    """Testes de carregamento de dados."""

    def test_generate_synthetic_data(self):
        """Valida geração de dados sintéticos."""
        data = generate_synthetic_data(n_records=1000)

        assert len(data) == 1000
        assert 'claim' in data.columns
        assert 'claim_amount' in data.columns
        assert data['claim'].isin([0, 1]).all()

    def test_data_shapes(self):
        """Valida dimensões do dataset."""
        data = generate_synthetic_data(n_records=500)

        assert data.shape == (500, 9)  # 8 colunas base + risk_score


class TestPreprocessing:
    """Testes de preprocessamento."""

    def test_preprocess_no_missing(self):
        """Valida que não há missing values após preprocess."""
        data = generate_synthetic_data(1000)
        processed, _ = preprocess(data, normalize=True)

        assert processed.isnull().sum().sum() == 0

    def test_normalize_creates_features(self):
        """Valida criação de features de interação."""
        data = generate_synthetic_data(100)
        processed, _ = preprocess(data, normalize=True)

        # Deve ter mais colunas após feature engineering
        assert processed.shape[1] > data.shape[1]


class TestModeling:
    """Testes de modelagem."""

    @pytest.fixture
    def sample_data(self):
        """Dados para teste."""
        return generate_synthetic_data(n_records=1000)

    def test_frequency_model(self, sample_data):
        """Testa treinamento de modelo de frequência."""
        model = train_frequency(sample_data)

        assert model.fitted
        assert model.params is not None
        assert 'lambda' in model.params

    def test_severity_model(self, sample_data):
        """Testa treinamento de modelo de severidade."""
        model = train_severity(sample_data)

        assert model.fitted
        assert model.params is not None
        assert 'mu' in model.params
        assert 'sigma' in model.params

    def test_frequency_prediction(self, sample_data):
        """Testa predição de frequência."""
        model = train_frequency(sample_data)
        pred = model.predict(n_samples=100)

        assert len(pred) == 100
        assert (pred >= 0).all()
        assert isinstance(pred, np.ndarray)

    def test_severity_prediction(self, sample_data):
        """Testa predição de severidade."""
        model = train_severity(sample_data)
        pred = model.predict(n_samples=100)

        assert len(pred) == 100
        assert (pred > 0).all()
        assert isinstance(pred, np.ndarray)


class TestSimulation:
    """Testes de simulação Monte Carlo."""

    @pytest.fixture
    def models(self):
        """Modelos para simulação."""
        data = generate_synthetic_data(n_records=500)
        freq = train_frequency(data)
        sev = train_severity(data)
        return freq, sev

    def test_simulate_losses(self, models):
        """Testa simulação de perdas."""
        freq_model, sev_model = models
        losses = simulate_losses(freq_model, sev_model, n_simulations=1000)

        assert len(losses) == 1000
        assert (losses >= 0).all()
        assert losses.mean() > 0

    def test_simulation_convergence(self, models):
        """Testa convergência da simulação."""
        freq_model, sev_model = models

        loss_100 = simulate_losses(freq_model, sev_model, 100).mean()
        loss_1000 = simulate_losses(freq_model, sev_model, 1000).mean()

        # Médias devem estar próximas (não divergir)
        ratio = abs(loss_1000 - loss_100) / loss_100
        assert ratio < 0.3  # Tolerância de 30%


class TestRiskAdjustment:
    """Testes de cálculo de Risk Adjustment."""

    @pytest.fixture
    def losses(self):
        """Distribuição de perdas simuladas."""
        np.random.seed(42)
        return np.random.lognormal(mean=9, sigma=1.5, size=10000)

    def test_var_method(self, losses):
        """Testa cálculo de VaR."""
        result = calculate_risk_adjustment(losses, method='var', alpha=95)

        assert result['method'] == 'var'
        assert result['Risk_Adjustment'] > 0
        assert isinstance(result['Risk_Adjustment'], float)

    def test_cte_method(self, losses):
        """Testa cálculo de CTE."""
        result = calculate_risk_adjustment(losses, method='cte', alpha=95)

        assert result['method'] == 'cte'
        assert result['Risk_Adjustment'] > 0

    def test_var_is_percentile(self, losses):
        """Valida que VaR é o percentil esperado."""
        result_var = calculate_risk_adjustment(losses, method='var', alpha=95)
        expected_var = np.percentile(losses, 95)

        # VaR = percentil - média
        calculated_ra = expected_var - losses.mean()

        assert abs(result_var['Risk_Adjustment'] - calculated_ra) < 1

    def test_cte_greater_than_var(self, losses):
        """Valida que CTE > VaR (mais conservador)."""
        result_var = calculate_risk_adjustment(losses, method='var', alpha=95)
        result_cte = calculate_risk_adjustment(losses, method='cte', alpha=95)

        assert result_cte['Risk_Adjustment'] > result_var['Risk_Adjustment']

    def test_all_methods_comparison(self, losses):
        """Testa comparação de métodos."""
        result = calculate_risk_adjustment(
            losses,
            method='var',
            include_all_methods=True
        )

        assert 'all_methods_comparison' in result
        assert 'VaR' in result['all_methods_comparison']
        assert 'CTE' in result['all_methods_comparison']


class TestEndToEnd:
    """Testes de pipeline completo."""

    def test_full_pipeline(self):
        """Testa pipeline completo de dados → RA."""
        # Dados
        data = generate_synthetic_data(n_records=500)
        assert len(data) > 0

        # Preprocess
        processed, _ = preprocess(data, normalize=True)
        assert processed.isnull().sum().sum() == 0

        # Modelagem
        freq_model = train_frequency(processed)
        sev_model = train_severity(processed)
        assert freq_model.fitted and sev_model.fitted

        # Simulação
        losses = simulate_losses(freq_model, sev_model, n_simulations=1000)
        assert len(losses) == 1000

        # RA
        result = calculate_risk_adjustment(losses, method='var')
        assert 'Risk_Adjustment' in result
        assert result['Risk_Adjustment'] > 0

        print(f"\nPipeline OK. RA calculado: R$ {result['Risk_Adjustment']:.2f}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
