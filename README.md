# IFRS 17 Risk Adjustment Engine

Motor de cálculo de Ajuste ao Risco (Risk Adjustment) conforme norma IFRS 17 - Insurance Contracts.

---

##  COMECE AQUI (3 Passos)

### Passo 1: Instale Dependências (5-10 min, primeira vez apenas)
```bash
cd "g:\...\IR17\ifrs17-risk-adjustment"
python setup_environment.py
```

### Passo 2: Abra Jupyter
```bash
jupyter notebook notebooks/main.ipynb
```

### Passo 3: Execute Todas as Células
No notebook, pressione **Shift + Enter** em cada célula, na ordem.

**Resultado:** Provisão IFRS 17 calculada em 5-10 minutos.

---

**Precisa de mais ajuda?** Veja:
- [GUIA_EXECUCAO.md](GUIA_EXECUCAO.md) - Instruções detalhadas
- [QUICKSTART.md](QUICKSTART.md) - Guia rápido
- [CHECKLIST_PROJETO.md](CHECKLIST_PROJETO.md) - O que foi entregue

---

## Objetivo

Calcular provisões para contratos de seguro e previdência através de modelo atuarial robusto, estatisticamente validado e conforme norma IFRS 17.

A provisão é composta por:
- **BEL** (Best Estimate Liability): Valor presente esperado dos fluxos futuros
- **RA** (Risk Adjustment): Compensação pela incerteza não-financeira

```
Provisão IFRS 17 = BEL + RA
```

## Estrutura do Projeto

```
ifrs17-risk-adjustment/
├── data/                    # Dados brutos, processados, externos
├── notebooks/               # Análise exploratória e desenvolvimento
├── src/                     # Código Python modular
│   ├── data/               # Carregamento e preprocessamento
│   ├── actuarial/          # Projeções atuariais (BEL, lapse, mortalidade)
│   ├── modeling/           # Modelos estatísticos (freq, severity, RA)
│   ├── simulation/         # Monte Carlo
│   ├── validation/         # Testes e validação
│   ├── governance/         # Auditoria e versionamento
│   └── cloud/              # Pipeline e deployment
├── config/                 # Parâmetros e configuração
├── reports/                # Documentação e resultados
├── docs/                   # Guias e explicações
├── tests/                  # Testes unitários
├── requirements.txt        # Dependências Python
└── run_pipeline.py        # Script principal
```

## Instalação

### Pré-requisitos
- Python 3.8+
- pip

### Setup

```bash
# Clonar repositório
git clone <repo-url>
cd ifrs17-risk-adjustment

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Uso

### Execução Básica (Dados Sintéticos)

```bash
python run_pipeline.py
```

Resultado: Provisão IFRS 17 com dados gerados automaticamente.

### Com Argumentos Customizados

```bash
# Aumentar número de simulações
python run_pipeline.py --simulations 50000

# Usar método CTE em vez de VaR
python run_pipeline.py --ra-method cte

# Exportar resultados em JSON
python run_pipeline.py --export-json

# Usar dataset local
python run_pipeline.py --data-source csv --data-file data/raw/seu_dataset.csv
```

### Desde Jupyter

```python
from src.cloud.pipeline import run_pipeline

result = run_pipeline(
    data_source='synthetic',
    n_simulations=10000,
    ra_method='var',
    ra_alpha=95,
    verbose=True
)

print(f"BEL: ${result['actuarial']['bel']:.2f}")
print(f"RA: ${result['risk_adjustment']['Risk_Adjustment']:.2f}")
```

## Documentação

### Para Leitura Inicial
1. **[business_explanation.md](docs/business_explanation.md)** - O que o modelo faz (linguagem leiga)
2. **[glossary.md](docs/glossary.md)** - Termos técnicos explicados

### Para Implementadores
1. **[methodology.md](reports/methodology.md)** - Como o modelo funciona (técnico)
2. **[assumptions.md](reports/assumptions.md)** - Hipóteses atuariais
3. **[ifrs17_alignment.md](reports/ifrs17_alignment.md)** - Conformidade regulatória

### Para Auditores
1. **[validation_report.md](reports/validation_report.md)** - Testes de validação
2. **[model_comparison.md](reports/model_comparison.md)** - Comparação de métodos
3. **[audit_trail.md](reports/audit_trail.md)** - Rastreamento de execuções

## Metodologia

### Decomposição Frequência-Severidade

Modelo decompõe distribuição agregada de perdas em:

1. **Frequência (N)**: Número de eventos
   - Distribuição: Poisson ou Binomial Negativa
   
2. **Severidade (X)**: Valor de cada evento
   - Distribuição: Lognormal ou Gamma

3. **Agregação**: S = X₁ + X₂ + ... + Xₙ

### Simulação Monte Carlo

Para cada cenário:
```
N ~ Freq(params)
Para cada evento: X ~ Sev(params)
S = Σ X
```

Resultado: 10.000 cenários de perda agregada

### Cálculo de Risk Adjustment

**Método VaR** (padrão):
```
RA = VaR₉₅ - E[S]
```

**Método CTE** (alternativo):
```
RA = E[S | S > VaR₉₅] - E[S]
```

## Validação

Modelo passa por rigorosos testes:

- **Testes de aderência**: KS test, Shapiro-Wilk
- **Backtesting**: Kupiec POF, Christoffersen
- **Stress testing**: Variações de parâmetros
- **Sensibilidade**: One-way, two-way, tornado
- **Convergência**: Valida n_simulations suficiente

Ver [validation_report.md](reports/validation_report.md) para detalhes.

## Conformidade Regulatória

- **IFRS 17**: Padrão contábil internacional
- **BRGAAP**: Normas contábeis brasileiras
- **SUSEP**: Circular 563/21 (provisões)
- **BACEN**: Diretrizes BCB

## Componentes Principais

### Data (`src/data/`)
- `load_data.py`: Carregamento de CSV ou geração sintética
- `preprocess.py`: Limpeza, normalização, feature engineering

### Actuarial (`src/actuarial/`)
- `cashflow_projection.py`: Projeção de fluxos
- `bel_calculation.py`: Cálculo de Best Estimate Liability
- `lapse_model.py`: Modelo de cancelamento
- `mortality_model.py`: Modelo de mortalidade

### Modeling (`src/modeling/`)
- `frequency.py`: Modelagem de frequência (Poisson/NB)
- `severity.py`: Modelagem de severidade (Lognormal/Gamma)
- `risk_metrics.py`: Cálculo de VaR, CTE, RA
- `risk_adjustment.py`: Orquestração de RA

### Simulation (`src/simulation/`)
- `monte_carlo.py`: Simulação de perdas agregadas

### Validation (`src/validation/`)
- `model_metrics.py`: RMSE, MAE, MAPE, R²
- `distribution_tests.py`: KS test, Shapiro-Wilk, Jarque-Bera
- `backtesting.py`: Kupiec POF, Christoffersen
- `stress_test.py`: Cenários de estresse
- `sensitivity.py`: Análise de sensibilidade

### Governance (`src/governance/`)
- `model_versioning.py`: Versionamento de modelo
- `audit_log.py`: Log de auditoria

### Cloud (`src/cloud/`)
- `pipeline.py`: Orquestração do pipeline completo
- `deploy_local_simulation.py`: Simulação de deployment AWS

## Configuração

### parameters.yaml
Parâmetros de execução (n_simulations, distribuições, etc)

### model_config.yaml
Configurações técnicas (hipóteses, constraints, quality gates)

## Saída

O pipeline retorna:

```python
{
    'status': 'SUCCESS',
    'data': {...},
    'actuarial': {
        'bel': 1250000.00,
        'projection_years': 30
    },
    'models': {
        'frequency': {...},
        'severity': {...}
    },
    'simulation': {
        'n_simulations': 10000,
        'mean_loss': 1000000.00,
        'std_loss': 500000.00,
        'percentiles': {...}
    },
    'risk_adjustment': {
        'method': 'var',
        'Risk_Adjustment': 185000.00,
        'all_methods_comparison': {...}
    },
    'validation': {...},
    'audit_log': [...]
}
```

## Teste

```bash
# Rodar testes unitários
pytest tests/

# Com cobertura
pytest --cov=src tests/

# Teste específico
pytest tests/test_models.py::test_frequency
```

## Performance

- **10.000 simulações**: ~30 segundos
- **50.000 simulações**: ~2 minutos
- **Memória**: ~1GB para 50k simulações

## Limitações Conhecidas

1. Assume independência entre frequência e severidade (melhorável com copulas)
2. Dados históricos podem não predizer futuro (quebras estruturais)
3. Não captura correlação entre linhas de negócio
4. Tábuas de mortalidade assumem estabilidade

## Roadmap

- [ ] Integração com banco de dados (PostgreSQL)
- [ ] API REST para execução remota
- [ ] Dashboard Tableau/Power BI
- [ ] Modelos de copula para dependência
- [ ] Deployment automático em AWS
- [ ] Backtesting automático contínuo

## Contribuidores

- Risk Modeling Team

## Licença

MIT

## Versão

v1.0.0 - março 2026

---

Para questões técnicas, ver [methodology.md](reports/methodology.md)
Para dúvidas de negócio, ver [business_explanation.md](docs/business_explanation.md)
