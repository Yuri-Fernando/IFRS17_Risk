# IFRS 17 Risk Adjustment Engine

### Motor de cálculo de Ajuste ao Risco (Risk Adjustment) para contratos de seguro

## Status

🟢 **Concluído — Versão 1.0**

Projeto de **modelagem atuarial, estatística e simulação de risco** desenvolvido para calcular o **Risk Adjustment (RA)** no contexto do IFRS 17, combinando projeção de fluxos, modelagem de frequência e severidade, Simulação Monte Carlo, métricas de risco e validação estatística.

A implementação possui pipeline modular em Python, notebook principal, testes automatizados, documentação metodológica, rastreabilidade de execuções e componentes de governança.

> **Escopo:** aplicação de pesquisa e portfólio para experimentação quantitativa com conceitos do IFRS 17. Não substitui modelos atuariais, processos de validação ou requisitos regulatórios de uma implementação institucional.

---

# Início Rápido

## 1. Instalar dependências

```bash
cd ifrs17-risk-adjustment
python setup_environment.py
```

Ou instalação manual:

```bash
python -m venv venv
```

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```cmd
venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

---

## 2. Abrir o notebook

```bash
jupyter notebook notebooks/main.ipynb
```

---

## 3. Executar o pipeline

Execute as células do notebook na sequência.

O fluxo calcula:

```text
Fluxos Atuariais
      ↓
BEL
      ↓
Modelagem de Frequência
      ↓
Modelagem de Severidade
      ↓
Monte Carlo
      ↓
Distribuição de Perdas
      ↓
VaR / CTE
      ↓
Risk Adjustment
      ↓
Validação + Auditoria
```

---

# Sobre o Projeto

O IFRS 17 Risk Adjustment Engine implementa um pipeline quantitativo para mensuração do **Ajuste ao Risco (Risk Adjustment)** associado à incerteza não financeira em contratos de seguro.

A estrutura considera:

* **BEL (Best Estimate Liability):** valor presente esperado dos fluxos futuros;
* **RA (Risk Adjustment):** compensação pela incerteza não financeira.

Conceitualmente:

```text
Provisão IFRS 17 = BEL + RA
```

---

# Objetivo

O projeto busca combinar **modelagem atuarial, estatística, simulação e validação** em uma implementação modular para análise de risco.

A arquitetura permite:

* projetar fluxos atuariais;
* modelar frequência e severidade;
* gerar cenários de perdas;
* calcular métricas de risco;
* estimar o Risk Adjustment;
* comparar métodos;
* validar premissas;
* registrar execuções e resultados.

---

# Metodologia

## 1. Projeção Atuarial

A camada atuarial contempla:

* Projeção de fluxos de caixa;
* Cálculo de BEL;
* Modelagem de lapse;
* Modelagem de mortalidade;
* Horizonte de projeção.

---

## 2. Modelagem de Frequência

A frequência representa o número de eventos de perda.

Modelos disponíveis:

* Poisson;
* Binomial Negativa.

```text
N ~ Freq(parameters)
```

---

## 3. Modelagem de Severidade

A severidade representa o valor financeiro de cada evento.

Distribuições disponíveis:

* Lognormal;
* Gamma.

```text
X ~ Severity(parameters)
```

---

## 4. Agregação de Perdas

A perda agregada é calculada como:

```text
S = X₁ + X₂ + ... + Xₙ
```

Cada cenário de Monte Carlo representa uma possível realização da distribuição agregada de perdas.

---

# Simulação Monte Carlo

O motor gera cenários de perda para estimar a distribuição agregada.

Fluxo:

```text
N ~ Frequency
      ↓
Para cada evento:
X ~ Severity
      ↓
S = Σ X
      ↓
Distribuição de Perdas
```

Configuração padrão:

```text
10.000 cenários
```

A quantidade pode ser alterada por argumento.

Exemplo:

```bash
python run_pipeline.py --simulations 50000
```

---

# Risk Adjustment

O projeto suporta diferentes métodos para cálculo do RA.

## VaR

Método padrão:

```text
RA = VaR₉₅ - E[S]
```

## CTE

Método alternativo:

```text
RA = E[S | S > VaR₉₅] - E[S]
```

O pipeline permite comparar os resultados obtidos por diferentes métodos.

---

# Estrutura do Pipeline

```text
Data Source
    ↓
Preprocessing
    ↓
Actuarial Projection
    ↓
Frequency Modeling
    ↓
Severity Modeling
    ↓
Monte Carlo Simulation
    ↓
Risk Metrics
    ↓
Risk Adjustment
    ↓
Validation
    ↓
Governance / Audit
```

---

# Validação

O projeto inclui uma camada dedicada à validação estatística e quantitativa.

## Testes de aderência

* Kolmogorov-Smirnov;
* Shapiro-Wilk;
* Jarque-Bera.

## Backtesting

* Kupiec POF;
* Christoffersen.

## Stress Testing

Avaliação do comportamento do modelo sob alterações dos principais parâmetros.

## Sensibilidade

* One-way;
* Two-way;
* Tornado analysis.

## Convergência

Verificação da estabilidade dos resultados conforme o número de simulações aumenta.

---

# Governança

A camada de governança foi estruturada para facilitar rastreabilidade e auditoria.

Inclui:

* Versionamento do modelo;
* Registro de execução;
* Audit log;
* Configurações versionáveis;
* Quality gates;
* Documentação de hipóteses.

---

# Estrutura do Projeto

```text
ifrs17-risk-adjustment/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── notebooks/
│   └── main.ipynb
│
├── src/
│   ├── data/
│   │   ├── load_data.py
│   │   └── preprocess.py
│   │
│   ├── actuarial/
│   │   ├── cashflow_projection.py
│   │   ├── bel_calculation.py
│   │   ├── lapse_model.py
│   │   └── mortality_model.py
│   │
│   ├── modeling/
│   │   ├── frequency.py
│   │   ├── severity.py
│   │   ├── risk_metrics.py
│   │   └── risk_adjustment.py
│   │
│   ├── simulation/
│   │   └── monte_carlo.py
│   │
│   ├── validation/
│   │   ├── model_metrics.py
│   │   ├── distribution_tests.py
│   │   ├── backtesting.py
│   │   ├── stress_test.py
│   │   └── sensitivity.py
│   │
│   ├── governance/
│   │   ├── model_versioning.py
│   │   └── audit_log.py
│   │
│   └── cloud/
│       ├── pipeline.py
│       └── deploy_local_simulation.py
│
├── config/
│   ├── parameters.yaml
│   └── model_config.yaml
│
├── reports/
│   ├── methodology.md
│   ├── assumptions.md
│   ├── ifrs17_alignment.md
│   ├── validation_report.md
│   ├── model_comparison.md
│   └── audit_trail.md
│
├── docs/
│   ├── business_explanation.md
│   └── glossary.md
│
├── tests/
│
├── requirements.txt
├── run_pipeline.py
├── setup_environment.py
└── README.md
```

---

# Componentes Principais

## Data

### `src/data/load_data.py`

Responsável por:

* carregamento dos dados;
* geração de dados sintéticos;
* preparação das entradas.

### `src/data/preprocess.py`

Responsável por:

* limpeza;
* normalização;
* feature engineering.

---

## Actuarial

### `cashflow_projection.py`

Projeção dos fluxos futuros.

### `bel_calculation.py`

Cálculo do Best Estimate Liability.

### `lapse_model.py`

Modelagem do comportamento de cancelamento.

### `mortality_model.py`

Modelagem de mortalidade.

---

## Modeling

### `frequency.py`

Modelagem de frequência:

* Poisson;
* Binomial Negativa.

### `severity.py`

Modelagem de severidade:

* Lognormal;
* Gamma.

### `risk_metrics.py`

Cálculo de:

* VaR;
* CTE;
* RA.

### `risk_adjustment.py`

Orquestração do cálculo completo do Risk Adjustment.

---

## Simulation

### `monte_carlo.py`

Responsável pela geração dos cenários de perdas agregadas.

---

## Validation

### `model_metrics.py`

Métricas:

* RMSE;
* MAE;
* MAPE;
* R².

### `distribution_tests.py`

Testes:

* KS;
* Shapiro-Wilk;
* Jarque-Bera.

### `backtesting.py`

Métodos:

* Kupiec POF;
* Christoffersen.

### `stress_test.py`

Cenários de estresse.

### `sensitivity.py`

Análises de sensibilidade.

---

## Governance

### `model_versioning.py`

Versionamento das configurações e modelos.

### `audit_log.py`

Registro das execuções e eventos relevantes.

---

## Cloud

### `pipeline.py`

Orquestração do pipeline completo.

### `deploy_local_simulation.py`

Estrutura para simulação de deployment em ambiente AWS.

---

# Como Executar

## Execução básica

```bash
python run_pipeline.py
```

O pipeline utiliza dados sintéticos por padrão e retorna a estimativa do BEL, distribuição de perdas, métricas de risco e Risk Adjustment.

---

## Simulações customizadas

### 50.000 cenários

```bash
python run_pipeline.py --simulations 50000
```

### Utilizar CTE

```bash
python run_pipeline.py --ra-method cte
```

### Exportar JSON

```bash
python run_pipeline.py --export-json
```

### Utilizar dataset local

```bash
python run_pipeline.py \
  --data-source csv \
  --data-file data/raw/seu_dataset.csv
```

---

# Uso via Python

```python
from src.cloud.pipeline import run_pipeline

result = run_pipeline(
    data_source="synthetic",
    n_simulations=10000,
    ra_method="var",
    ra_alpha=95,
    verbose=True
)

print(
    f"BEL: ${result['actuarial']['bel']:.2f}"
)

print(
    f"RA: ${result['risk_adjustment']['Risk_Adjustment']:.2f}"
)
```

---

# Documentação

## Para entendimento do negócio

* [Business Explanation](docs/business_explanation.md)
* [Glossary](docs/glossary.md)

## Para implementação

* [Methodology](reports/methodology.md)
* [Assumptions](reports/assumptions.md)
* [IFRS 17 Alignment](reports/ifrs17_alignment.md)

## Para validação e auditoria

* [Validation Report](reports/validation_report.md)
* [Model Comparison](reports/model_comparison.md)
* [Audit Trail](reports/audit_trail.md)

---

# Exemplo de Saída

O pipeline retorna uma estrutura organizada contendo dados atuariais, modelos, simulação, Risk Adjustment, validação e auditoria:

```python
{
    "status": "SUCCESS",

    "data": {...},

    "actuarial": {
        "bel": 1250000.00,
        "projection_years": 30
    },

    "models": {
        "frequency": {...},
        "severity": {...}
    },

    "simulation": {
        "n_simulations": 10000,
        "mean_loss": 1000000.00,
        "std_loss": 500000.00,
        "percentiles": {...}
    },

    "risk_adjustment": {
        "method": "var",
        "Risk_Adjustment": 185000.00,
        "all_methods_comparison": {...}
    },

    "validation": {...},

    "audit_log": [...]
}
```

> Os valores acima são exemplos de estrutura de retorno e não representam resultados financeiros reais.

---

# Testes

### Executar testes

```bash
pytest tests/
```

### Com cobertura

```bash
pytest --cov=src tests/
```

### Teste específico

```bash
pytest tests/test_models.py::test_frequency
```

---

# Performance

Resultados indicados para o ambiente de execução do projeto:

| Cenário                     | Tempo aproximado |
| --------------------------- | ---------------: |
| 10.000 simulações           |            ~30 s |
| 50.000 simulações           |           ~2 min |
| Memória — 50.000 simulações |            ~1 GB |

Os tempos dependem do ambiente, configuração do modelo e volume de dados processado.

---

# Configuração

## `parameters.yaml`

Controla parâmetros como:

* número de simulações;
* distribuições;
* níveis de confiança;
* parâmetros de execução.

## `model_config.yaml`

Define:

* hipóteses;
* constraints;
* quality gates;
* parâmetros técnicos.

---

# Conformidade e Referências Regulatórias

O projeto foi estruturado em torno de conceitos relacionados a:

* **IFRS 17 — Insurance Contracts**;
* BRGAAP;
* SUSEP;
* BACEN.

> A implementação é uma ferramenta experimental de pesquisa e portfólio. A indicação de alinhamento a uma norma não significa certificação, aprovação regulatória ou conformidade institucional.

---

# O que este projeto demonstra

* Modelagem atuarial;
* Modelagem de frequência e severidade;
* Simulação Monte Carlo;
* Value at Risk;
* Conditional Tail Expectation;
* Risk Adjustment;
* Modelagem estatística;
* Validação estatística;
* Backtesting;
* Stress testing;
* Sensitivity analysis;
* Governança de modelos;
* Audit trail;
* Versionamento;
* Pipeline modular em Python;
* Estruturação de soluções quantitativas.

---

# Limitações Conhecidas

1. O modelo assume independência entre frequência e severidade;
2. Dependências mais complexas podem exigir modelos adicionais, como cópulas;
3. Dados históricos podem não representar mudanças estruturais futuras;
4. Correlações entre diferentes linhas de negócio não são modeladas na versão atual;
5. Tábuas de mortalidade assumem estabilidade;
6. Dados sintéticos podem não representar integralmente características de contratos reais.

---

# Melhorias Futuras

* Integração com PostgreSQL;
* API REST para execução remota;
* Dashboard em Tableau ou Power BI;
* Modelos de cópula;
* Deployment automatizado em AWS;
* Backtesting contínuo;
* Monitoramento de drift;
* Novos modelos de frequência e severidade;
* Cenários macroeconômicos;
* Integração com dados reais;
* Maior automação de governança e auditoria.

---

# Status do Projeto

🟢 **Concluído — v1.0.0**

A versão atual inclui:

* ✅ Pipeline atuarial;
* ✅ Cálculo de BEL;
* ✅ Modelagem de frequência;
* ✅ Modelagem de severidade;
* ✅ Simulação Monte Carlo;
* ✅ Cálculo de VaR;
* ✅ Cálculo de CTE;
* ✅ Risk Adjustment;
* ✅ Validação estatística;
* ✅ Backtesting;
* ✅ Stress testing;
* ✅ Sensibilidade;
* ✅ Governança;
* ✅ Audit trail;
* ✅ Versionamento;
* ✅ Testes automatizados;
* ✅ Notebook principal;
* ✅ Documentação metodológica.

### Evoluções futuras

As melhorias planejadas concentram-se em:

* Novas fontes de dados;
* Modelos de dependência;
* APIs;
* Dashboards;
* Cloud deployment;
* Backtesting contínuo;
* Monitoramento e governança avançados.

---

# Versão

**v1.0.0 — Março de 2026**

---

# Licença

MIT License.

---

# Autor

**Yuri Fernando Dubbern**

AI/ML Engineer · Data Science · Statistical Modeling · Risk Analytics

[LinkedIn](https://www.linkedin.com/in/yuridubbern) · [GitHub](https://github.com/Yuri-Fernando) · [Lattes](http://lattes.cnpq.br/7151392692642166) · [Linktree](https://linktr.ee/yuri.f.dubbern)
