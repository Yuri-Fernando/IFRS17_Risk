# IFRS17_Risk — Modelagem de Risco Atuarial e de Crédito

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-portfólio-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![License](https://img.shields.io/badge/license-portfólio%2Fuso%20livre-lightgrey)

Repositório de portfólio com dois motores de cálculo de risco/provisão
financeira, evoluindo do mesmo núcleo de engenharia (pipeline modular,
governança, validação estatística, auditabilidade) aplicado a domínios
regulatórios diferentes.

---

## 📊 v2 — [credit-risk-ecl-engine](credit-risk-ecl-engine/) *(atual)*

Motor de **Perda Esperada de Crédito (ECL)** para carteiras bancárias,
conforme **IFRS 9** e **Resolução CMN n. 4.966/2021**.

- Modelagem de **PD, LGD e EAD** (champion Regressão Logística vs.
  challenger Gradient Boosting)
- **Staging IFRS 9** (Stage 1/2/3, SICR) e extrapolação de PD lifetime
- Simulação de Monte Carlo com **correlação entre segmentos via cópula
  Gaussiana** (VaR, CVaR, benefício de diversificação)
- Validação: Gini, KS, PSI, calibração, backtesting de Kupiec
- Stress testing com 4 cenários macroeconômicos
- Trilha de auditoria e versionamento de modelo
- Dataset real (**UCI German Credit**, 1.000 contratos) baixado
  automaticamente
- **Notebook executável de ponta a ponta**, com resultados e gráficos
  já salvos: [`credit_risk_ecl_engine.ipynb`](credit-risk-ecl-engine/notebooks/credit_risk_ecl_engine.ipynb)

➡️ Documentação completa em [credit-risk-ecl-engine/README.md](credit-risk-ecl-engine/README.md)

## 🏛️ v1 — [ifrs17-risk-adjustment](ifrs17-risk-adjustment/)

Motor de **Ajuste ao Risco (Risk Adjustment)** para contratos de seguro
e previdência, conforme **IFRS 17**.

- Modelagem de frequência/severidade (Poisson/Binomial Negativa,
  Lognormal/Gamma)
- Simulação de Monte Carlo (10.000+ cenários) e cálculo de VaR/CTE
- Validação atuarial (testes de aderência, backtesting, stress test)

➡️ Documentação completa em [ifrs17-risk-adjustment/README.md](ifrs17-risk-adjustment/README.md)

---

## Por que dois projetos — a evolução v1 → v2

O `credit-risk-ecl-engine` é um **pivô consciente** do
`ifrs17-risk-adjustment`, não um projeto do zero: a mesma arquitetura de
pipeline (dados → modelagem → simulação → validação → governança) foi
migrada de risco atuarial de seguros para **risco de crédito bancário**
— domínio de PD/LGD/EAD e IFRS 9/CMN 4.966.

A v2 também endereça, de forma deliberada, uma lacuna metodológica comum
em modelos de risco desse tipo: PoCs que somam perdas contrato a
contrato assumindo **independência entre inadimplências** subestimam o
risco de cauda de uma carteira real. A v2 resolve isso incorporando
**correlação entre segmentos de risco via cópulas** no motor de
simulação — e documenta, com transparência, cada premissa e limitação
que separa um PoC de um modelo pronto para produção.

Ambos os projetos permanecem no repositório para evidenciar essa
evolução do raciocínio técnico entre os dois domínios.

## Stack

Python 3.10+ · NumPy · Pandas · SciPy · scikit-learn · statsmodels ·
Matplotlib · Jupyter

## Estrutura do repositório

```
IFRS17_Risk/
├── credit-risk-ecl-engine/     # v2 — risco de crédito bancário (IFRS 9 / CMN 4.966)
├── ifrs17-risk-adjustment/     # v1 — risco atuarial de seguros (IFRS 17)
├── main.ipynb                  # notebook exploratório original da v1
└── resumo.md                   # guia de estudo da v1
```
