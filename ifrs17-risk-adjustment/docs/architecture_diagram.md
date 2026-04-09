# Diagrama de Arquitetura

## Pipeline Local (Desenvolvimento)

```
Raw Data (CSV/Synthetic)
    ↓
[load_data.py]
    ↓
DataFrame bruto
    ↓
[preprocess.py]
    ├─ handle_missing_values
    ├─ encode_categorical
    ├─ normalize_numeric
    └─ add_interaction_features
    ↓
Dados processados
    ↓
Paralelo:
├─ [actuarial]
│   ├─ project_cashflows
│   └─ calculate_bel
│
├─ [modeling]
│   ├─ train_frequency
│   └─ train_severity
│
└─ [validation - prévia]
    └─ distribution_tests

    ↓
Modelos treinados + BEL
    ↓
[monte_carlo.py]
simulate_losses(freq_model, sev_model)
    ↓
Array de perdas simuladas (10k scenarios)
    ↓
[risk_metrics.py]
├─ calculate_var
├─ calculate_cte
└─ calculate_cost_of_capital
    ↓
Risk Adjustment calculado
    ↓
[validation - completa]
├─ backtesting
├─ stress_test
└─ sensitivity_analysis
    ↓
[audit_log.py]
Log de auditoria
    ↓
[governance]
Model versioning + export
    ↓
Resultado Final:
├─ BEL: R$ 1.25M
├─ RA: R$ 185k
├─ Provisão: R$ 1.435M
└─ Métricas de validação
```

## Estrutura de Dados (Flow)

```
Input:
  - df_raw: DataFrame (5000 linhas × 8 colunas)
    [claim, claim_amount, age, premium, region, duration, risk_score, lapse]

Output:
  - df_preprocessed: DataFrame normalizado
    [48 features: originais + interações + normalizadas]

Models:
  - freq_model: FrequencyModel(lambda=0.15, distribution='poisson')
  - sev_model: SeverityModel(mu=9.2, sigma=1.5, distribution='lognormal')

Simulation Output:
  - losses: ndarray(10000,) [valores de perdas por cenário]

Final Results:
  - result: dict {
      'BEL': 1250000,
      'RA': 185000,
      'method': 'var',
      'alpha': 95,
      'validation': {...},
      'audit_log': [...]
    }
```

## Dependências Entre Módulos

```
load_data.py
    ↓
preprocess.py
    ├→ frequency.py ←─┐
    ├→ severity.py   │
    └→ .......... monte_carlo.py
                      ↓
                risk_metrics.py
                      ↓
            risk_adjustment.py
                      ↓
        ┌─────────┬───┴────┬──────────┐
        ↓         ↓         ↓          ↓
    backtesting  stress_test sensitivity  model_metrics
        ↓         ↓         ↓          ↓
        └─────────┴─────────┴──────────┘
                      ↓
        [validation_report]
                      ↓
              audit_log.py
                      ↓
            model_versioning.py
                      ↓
              [export JSON]
```

## Stack Técnico

```
Python 3.8+
├── NumPy (operações numéricas)
├── Pandas (manipulação de dados)
├── SciPy (distribuições, testes)
├── Scikit-learn (preprocessamento, GLM)
├── Statsmodels (GLM, testes estatísticos)
├── Matplotlib/Seaborn (visualização)
└── PyYAML (configuração)

Testes:
├── Pytest (framework)
└── Pytest-cov (cobertura)

Desenvolvimento:
├── Jupyter (notebooks)
├── Black (formatação)
├── Flake8 (linting)
└── Sphinx (documentação)
```

## Fluxo de Execução

### Opção 1: Linha de Comando

```bash
$ python run_pipeline.py --simulations 10000 --ra-method var --export-json

Loading data...
Preprocessing...
Training frequency model...
Training severity model...
Running 10000 Monte Carlo simulations...
Calculating Risk Adjustment...
Running validation tests...
[SUCCESS] Results exported to reports/result.json
```

### Opção 2: Jupyter Notebook

```python
from src.cloud.pipeline import run_pipeline

result = run_pipeline(
    data_source='synthetic',
    n_simulations=10000
)

# Acessar resultados
print(f"Provisão: R$ {result['actuarial']['bel'] + result['risk_adjustment']['Risk_Adjustment']:,.0f}")
```

### Opção 3: AWS Lambda

```
Event (S3, CloudWatch)
    ↓
Lambda Handler
    ├─ Load model from Model Registry
    ├─ Load data from S3
    ├─ run_pipeline()
    ├─ Save to RDS
    └─ Return result
```

## Governança e Auditoria

```
Model Version Registry
├─ v1.0.0 (2024-01-01)
│  ├─ parameters.json
│  ├─ metrics.json
│  └─ validation_report.md
├─ v1.0.1 (2024-01-15)
│  ├─ parameters.json
│  ├─ metrics.json
│  └─ validation_report.md
└─ v1.1.0 (2024-02-01)
   ├─ parameters.json
   ├─ metrics.json
   └─ validation_report.md

Audit Log
├─ 2024-01-15 10:30:00 - Model Execution (v1.0.0)
├─ 2024-01-15 11:45:00 - Validation PASSED
├─ 2024-01-15 12:00:00 - Results Exported (JSON)
└─ 2024-01-15 12:05:00 - Parameter Change (alpha: 95→90)
```

## Escalabilidade

### Simulations Scaling

```
n_simulations = 1000
  Time: 3 segundos
  Memory: 50 MB

n_simulations = 10000
  Time: 30 segundos
  Memory: 500 MB

n_simulations = 100000
  Time: 300 segundos
  Memory: 5 GB
  → Batch processing recomendado
```

### Data Scaling

```
records = 1000
  Models: Immediate
  Validation: < 1s

records = 100000
  Models: < 5s
  Validation: < 10s

records = 1000000
  Models: ~ 1 min
  Validation: ~ 2 min
  → Particionamento recomendado
```

---

*Diagramas de Arquitetura - IFRS 17 Risk Adjustment v1.0*
