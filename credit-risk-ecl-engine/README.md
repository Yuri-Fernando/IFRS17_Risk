# Credit Risk ECL Engine

### Motor de cálculo de Perda Esperada de Crédito (ECL) para carteiras bancárias

## Status

🟢 **Concluído — Versão 2.0 (v2 do portfólio)**

Projeto de **modelagem de crédito, estatística e simulação de risco**
desenvolvido para calcular a **Perda Esperada de Crédito (ECL)** no
contexto da **IFRS 9** e da **Resolução CMN n. 4.966/2021**, combinando
modelagem de PD/LGD/EAD, staging por estágio de risco, Simulação de
Monte Carlo com correlação via cópulas, métricas de risco e validação
estatística.

A implementação possui pipeline modular em Python, notebook executável
de ponta a ponta (com resultados e gráficos já salvos), testes
automatizados, documentação metodológica, rastreabilidade de execuções
e componentes de governança.

Este projeto é a evolução direta do
[ifrs17-risk-adjustment](../ifrs17-risk-adjustment/) (v1): mesma
arquitetura de pipeline, migrada de risco atuarial de seguros para
risco de crédito bancário.

> **Escopo:** aplicação de pesquisa e portfólio para experimentação
> quantitativa com conceitos de IFRS 9 / gestão de risco de crédito.
> Não substitui modelos de crédito, processos de validação ou
> requisitos regulatórios de uma implementação institucional.

---

# Início Rápido

## 1. Instalar dependências e baixar o dataset

```bash
cd credit-risk-ecl-engine
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

## 2. Abrir o notebook (já vem com resultados e gráficos salvos)

```bash
jupyter notebook notebooks/credit_risk_ecl_engine.ipynb
```

---

## 3. Executar o pipeline

Via notebook (célula a célula) ou direto pela CLI:

```bash
python run_pipeline.py --export-json
```

O fluxo calcula:

```text
Dados (German Credit)
      ↓
Segmentação + Encoding
      ↓
PD (Champion vs. Challenger)
      ↓
Staging IFRS 9 (Stage 1 / 2 / 3)
      ↓
LGD + EAD
      ↓
ECL = PD x LGD x EAD
      ↓
Monte Carlo + Cópula (correlação)
      ↓
VaR / CVaR
      ↓
Validação + Stress Test + Auditoria
```

---

# Sobre o Projeto

O Credit Risk ECL Engine implementa um pipeline quantitativo para
mensuração da **Perda Esperada de Crédito (Expected Credit Loss)**
associada a uma carteira de empréstimos, conforme o modelo de
impairment da IFRS 9 (e sua convergência no Brasil via Resolução CMN
4.966/2021).

A estrutura considera:

* **PD (Probability of Default):** probabilidade de inadimplência;
* **LGD (Loss Given Default):** severidade da perda, líquida de garantias;
* **EAD (Exposure at Default):** exposição no momento do default.

Conceitualmente:

```text
ECL = PD x LGD x EAD
```

---

# Objetivo

O projeto busca combinar **modelagem de crédito, estatística, simulação
e validação** em uma implementação modular, endereçando explicitamente
uma lacuna comum em PoCs de risco de crédito: a ausência de correlação
entre segmentos de risco.

A arquitetura permite:

* segmentar a carteira e codificar atributos de risco;
* modelar PD com dois candidatos (champion/challenger);
* classificar contratos em estágios IFRS 9 (Stage 1/2/3);
* estimar LGD e EAD;
* calcular a ECL contábil por contrato, stage e segmento;
* simular a distribuição de perda agregada com correlação entre segmentos;
* validar o modelo estatisticamente e via backtesting;
* aplicar cenários de stress;
* registrar execuções e resultados.

---

# Metodologia

## 1. Dados e Segmentação

* Dataset real: UCI Statlog German Credit Data (1.000 contratos);
* Segmentação em 4 linhas de negócio (veículos, bens de consumo, PJ capital de giro, pessoal);
* Codificação ordinal (variáveis com ordem natural de risco) e one-hot (demais categóricas).

---

## 2. Modelagem de PD (Probability of Default)

Dois modelos treinados e comparados:

* Regressão Logística — **champion** (interpretável, referência regulatória);
* Gradient Boosting — **challenger** (não-linear, avalia ganho de poder discriminante).

```text
PD_12m = P(default | atributos do contrato)
```

---

## 3. Staging IFRS 9 (SICR)

Classificação em três estágios conforme deterioração do risco desde a originação:

* **Stage 1:** sem aumento significativo de risco → ECL 12 meses;
* **Stage 2:** aumento significativo de risco (SICR), sem default → ECL lifetime;
* **Stage 3:** evidência objetiva de perda (default) → ECL lifetime, PD = 100%.

```text
PD_lifetime = 1 - (1 - PD_12m) ^ (prazo_meses / 12)
```

---

## 4. LGD e EAD

* **LGD:** distribuição Beta calibrada por segmento de colateral/garantia;
* **EAD:** saldo devedor remanescente, com Credit Conversion Factor (CCF).

```text
ECL_contrato = PD_usada x LGD x EAD
```

---

# Simulação Monte Carlo com Cópula

O motor gera cenários de perda correlacionados entre segmentos para
estimar a distribuição agregada — o ponto central deste projeto frente
a modelos que assumem independência entre inadimplências.

Fluxo:

```text
Choque sistêmico correlacionado (cópula Gaussiana)
      ↓
Ajuste de PD por segmento (mistura de Vasicek)
      ↓
Sorteio de default por contrato (Bernoulli)
      ↓
S = Σ (default_j x LGD_j x EAD_j)
      ↓
Distribuição de Perda Agregada
```

Configuração padrão:

```text
10.000 cenários
```

A quantidade e as correlações podem ser alteradas por argumento.

Exemplo:

```bash
python run_pipeline.py --simulations 50000 --correlation 0.35
```

---

# Risk Adjustment de Cauda (VaR / CVaR)

Além da ECL contábil (uma esperança), o motor calcula medidas de risco
de cauda a partir da distribuição simulada:

## VaR (Value at Risk)

```text
VaR_99.9% = quantil 99,9% da distribuição de perda agregada
```

## CVaR / Expected Shortfall

```text
CVaR_99.9% = E[perda | perda >= VaR_99.9%]
```

O motor também reporta o **benefício de diversificação**: a diferença
entre a soma das ECLs individuais (hipótese de independência) e a
perda esperada simulada (com correlação).

---

# Estrutura do Pipeline

```text
Data Source (CSV real ou sintético)
    ↓
Preprocessing + Segmentação
    ↓
PD Modeling (Champion vs. Challenger)
    ↓
Staging IFRS 9
    ↓
LGD + EAD Modeling
    ↓
ECL Calculation
    ↓
Monte Carlo + Cópula (VaR / CVaR)
    ↓
Validation
    ↓
Stress Testing
    ↓
Governance / Audit
```

---

# Validação

O projeto inclui uma camada dedicada à validação estatística e
quantitativa do modelo de PD e da provisão de ECL.

## Poder discriminante

* Gini;
* KS (Kolmogorov-Smirnov);
* AUC.

## Estabilidade

* PSI (Population Stability Index).

## Calibração

* Comparação PD prevista vs. taxa de default observada, por decil.

## Backtesting

* Teste de Kupiec (Proportion of Failures), por stage.

## Stress Testing

Avaliação da sensibilidade da ECL a choques de PD e LGD downturn (4 cenários).

---

# Governança

A camada de governança foi estruturada para facilitar rastreabilidade e auditoria.

Inclui:

* Versionamento do modelo (hash determinístico de parâmetros);
* Registro de execução (audit log);
* Configurações versionáveis (`config/*.yaml`);
* Quality gates (Gini/KS/PSI mínimos);
* Documentação de hipóteses e limitações conhecidas.

---

# Estrutura do Projeto

```text
credit-risk-ecl-engine/
│
├── data/
│   ├── raw/
│   │   └── german_credit.csv
│   ├── processed/
│   └── external/
│
├── notebooks/
│   ├── credit_risk_ecl_engine.ipynb
│   └── 00_quickstart.py
│
├── src/
│   ├── data/
│   │   ├── load_data.py
│   │   └── preprocess.py
│   │
│   ├── modeling/
│   │   ├── pd_model.py
│   │   ├── staging.py
│   │   ├── lgd_model.py
│   │   ├── ead_model.py
│   │   └── ecl_calculation.py
│   │
│   ├── simulation/
│   │   └── copula_simulation.py
│   │
│   ├── validation/
│   │   ├── model_validation.py
│   │   ├── backtesting.py
│   │   └── stress_test.py
│   │
│   ├── governance/
│   │   ├── model_versioning.py
│   │   └── audit_log.py
│   │
│   └── cloud/
│       └── pipeline.py
│
├── config/
│   ├── parameters.yaml
│   └── model_config.yaml
│
├── reports/
│   ├── methodology.md
│   ├── assumptions.md
│   ├── ifrs9_alignment.md
│   ├── validation_report.md
│   ├── model_comparison.md
│   └── audit_trail.md
│
├── docs/
│   ├── business_explanation.md
│   ├── glossary.md
│   ├── dataset_card.md
│   └── architecture_diagram.md
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

* carregamento do dataset real (German Credit);
* geração de carteira sintética (fallback sem internet);
* normalização da convenção de target (`default = 1`).

### `src/data/preprocess.py`

Responsável por:

* segmentação de portfólio (4 linhas de negócio);
* codificação ordinal e one-hot;
* split treino/teste estratificado.

---

## Modeling

### `pd_model.py`

Modelagem de PD:

* Regressão Logística (champion);
* Gradient Boosting (challenger);
* seleção automática por Gini.

### `staging.py`

Staging IFRS 9:

* classificação SICR (Stage 1/2/3);
* extrapolação de PD lifetime.

### `lgd_model.py`

LGD por segmento de colateral (distribuição Beta).

### `ead_model.py`

EAD via saldo remanescente e Credit Conversion Factor.

### `ecl_calculation.py`

Cálculo de:

* ECL por contrato, stage e segmento;
* coverage ratio da carteira.

---

## Simulation

### `copula_simulation.py`

Responsável pela simulação de Monte Carlo com correlação entre
segmentos (cópula Gaussiana + mistura de Vasicek), gerando VaR, CVaR e
benefício de diversificação.

---

## Validation

### `model_validation.py`

Métricas:

* Gini;
* KS;
* PSI;
* Calibração.

### `backtesting.py`

Teste de Kupiec (Proportion of Failures).

### `stress_test.py`

4 cenários de estresse macroeconômico.

---

## Governance

### `model_versioning.py`

Versionamento determinístico (hash) das configurações e modelos.

### `audit_log.py`

Registro das execuções e eventos relevantes.

---

## Cloud

### `pipeline.py`

Orquestração do pipeline completo, ponto único de entrada.

---

# Como Executar

## Execução básica (dataset real)

```bash
python run_pipeline.py
```

## Execução com dataset sintético (sem internet)

```bash
python run_pipeline.py --data-source synthetic
```

## Simulações customizadas

### 50.000 cenários

```bash
python run_pipeline.py --simulations 50000
```

### Correlação entre segmentos customizada

```bash
python run_pipeline.py --correlation 0.35 --asset-correlation 0.20
```

### Exportar JSON

```bash
python run_pipeline.py --export-json
```

---

# Uso via Python

```python
from src.cloud.pipeline import run_pipeline

result = run_pipeline(
    data_source="csv",
    data_path="data/raw/german_credit.csv",
    n_simulations=10000,
    inter_segment_correlation=0.25,
    verbose=True,
)

print(f"ECL: R$ {result['portfolio']['total_ecl']:.2f}")
print(f"VaR 99.9%: R$ {result['monte_carlo']['var']['var_99.9']:.2f}")
```

---

# Documentação

## Para entendimento do negócio

* [Business Explanation](docs/business_explanation.md)
* [Glossary](docs/glossary.md)
* [Dataset Card](docs/dataset_card.md)

## Para implementação

* [Methodology](reports/methodology.md)
* [Assumptions](reports/assumptions.md)
* [IFRS 9 Alignment](reports/ifrs9_alignment.md)
* [Architecture Diagram](docs/architecture_diagram.md)

## Para validação e auditoria

* [Validation Report](reports/validation_report.md)
* [Model Comparison](reports/model_comparison.md)
* [Audit Trail](reports/audit_trail.md)

---

# Exemplo de Saída (execução real, dataset German Credit)

```python
{
    "status": "SUCCESS",
    "pd_models": {
        "logistic_regression": {"gini": 0.617, "ks": 0.531, "auc": 0.809},
        "gradient_boosting": {"gini": 0.595, "ks": 0.486, "auc": 0.797},
        "champion": "logistic_regression"
    },
    "portfolio": {
        "n_contracts": 1000,
        "total_exposure": 2289880.60,
        "total_ecl": 874913.67,
        "coverage_ratio": 0.3821,
        "n_stage1": 245, "n_stage2": 455, "n_stage3": 300
    },
    "monte_carlo": {
        "n_simulations": 10000,
        "expected_loss": 874570.34,
        "var": {"var_95": 956175.22, "var_99.9": 1026556.20},
        "cvar": {"cvar_95": 976174.43, "cvar_99.9": 1037848.15},
        "diversification_benefit": 295.19
    },
    "validation": {"gini": 0.617, "ks": 0.531, "psi": 0.0259, "psi_rating": "estável"},
    "stress_test": [...],
    "audit_log": [...]
}
```

> Valores gerados por execução real do pipeline sobre o dataset German
> Credit — ver `reports/result_final.json` para o resultado completo e
> `reports/model_comparison.md` para a leitura interpretativa.

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
pytest tests/test_models.py::test_copula_simulation_produces_valid_distribution
```

11 testes cobrindo dados, PD, staging, LGD/EAD, ECL, simulação e validação — todos passando.

---

# Performance

Resultados indicados para o ambiente de execução do projeto:

| Cenário                        | Tempo aproximado |
| ------------------------------- | ----------------: |
| Pipeline completo (10.000 sim.) |             ~5-7 s |
| Suíte de testes (11 testes)     |            ~12-20 s |

Os tempos dependem do ambiente, configuração do modelo e volume de dados processado.

---

# Configuração

## `parameters.yaml`

Controla parâmetros como:

* fonte de dados e split treino/teste;
* hiperparâmetros dos modelos de PD;
* thresholds de staging (SICR);
* número de simulações e correlações (cópula);
* cenários de stress test.

## `model_config.yaml`

Define:

* quality gates (Gini/KS/PSI mínimos);
* governança (métrica de seleção de champion, sign-off humano);
* alinhamento regulatório;
* limitações conhecidas do modelo.

---

# Conformidade e Referências Regulatórias

O projeto foi estruturado em torno de conceitos relacionados a:

* **IFRS 9 (IASB) — Financial Instruments, Section 5.5 Impairment**;
* **Resolução CMN n. 4.966/2021**;
* Resolução BCB n. 352/2023;
* Basileia III / IRB (correlação de ativos — Vasicek).

> A implementação é uma ferramenta experimental de pesquisa e
> portfólio. A indicação de alinhamento a uma norma não significa
> certificação, aprovação regulatória ou conformidade institucional.

---

# O que este projeto demonstra

* Modelagem de risco de crédito (PD, LGD, EAD);
* Staging IFRS 9 e cálculo de ECL;
* Modelagem de dependência via cópulas;
* Simulação de Monte Carlo;
* Value at Risk e Conditional Value at Risk;
* Modelagem estatística (champion/challenger);
* Validação estatística (Gini, KS, PSI, calibração);
* Backtesting (Kupiec/POF);
* Stress testing;
* Governança de modelos;
* Audit trail;
* Versionamento;
* Pipeline modular em Python, testado;
* Leitura crítica de limitações metodológicas (documentadas, não ocultadas).

---

# Limitações Conhecidas

1. Dataset é um corte transversal único — sem múltiplas safras (vintages), o que limita a validação de PD lifetime e o backtesting por stage a um exercício ilustrativo;
2. LGD não é observada no dataset — modelada por proxy de colateral;
3. Correlação entre segmentos é parametrizada, não estimada de série histórica real de inadimplência;
4. Taxa de default do dataset (30%) não representa carteiras bancárias reais — leia resultados como demonstração de método, não benchmark de mercado;
5. EAD assume amortização linear e fração de prazo decorrida fixa, por ausência de data de originação real.

Ver detalhamento completo em [reports/assumptions.md](reports/assumptions.md).

---

# Melhorias Futuras

* Estimar correlação de segmentos a partir de dados históricos reais;
* Curva de PD marginal por vintage (survival analysis);
* Modelo de LGD com dados reais de recuperação/cobrança;
* API REST para scoring em tempo real;
* Dashboard executivo (Power BI/Tableau);
* Integração com banco de dados (PostgreSQL) para histórico de execuções;
* Monitoramento de drift contínuo (PSI em produção).

---

# Status do Projeto

🟢 **Concluído — v2.0.0**

A versão atual inclui:

* ✅ Pipeline de dados (real + sintético);
* ✅ Modelagem de PD (champion/challenger);
* ✅ Staging IFRS 9 (Stage 1/2/3);
* ✅ Modelagem de LGD e EAD;
* ✅ Cálculo de ECL;
* ✅ Simulação de Monte Carlo com cópula (correlação);
* ✅ Cálculo de VaR e CVaR;
* ✅ Validação estatística (Gini, KS, PSI, calibração);
* ✅ Backtesting (Kupiec);
* ✅ Stress testing;
* ✅ Governança (audit trail, versionamento);
* ✅ Testes automatizados (11 testes);
* ✅ Notebook executável com resultados salvos;
* ✅ Documentação metodológica completa.

### Evoluções futuras

As melhorias planejadas concentram-se em:

* Dados históricos multi-safra;
* Correlação estimada empiricamente;
* APIs e dashboards;
* Monitoramento contínuo de modelo em produção.

---

# Versão

**v2.0.0 — Setembro de 2026**

---

# Licença

MIT License.

---

# Autor

**Yuri Fernando Dubbern**

AI/ML Engineer · Data Science · Statistical Modeling · Risk Analytics

[LinkedIn](https://www.linkedin.com/in/yuridubbern) · [GitHub](https://github.com/Yuri-Fernando) · [Lattes](http://lattes.cnpq.br/7151392692642166) · [Linktree](https://linktr.ee/yuri.f.dubbern)
