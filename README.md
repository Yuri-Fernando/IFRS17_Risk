# IFRS17_Risk — Modelagem de Risco Atuarial e de Crédito

### Dois motores quantitativos de risco/provisão financeira, evoluindo do mesmo núcleo de engenharia para domínios regulatórios diferentes

## Status

🟢 **v2 em portfólio — Credit Risk ECL Engine** · 🟢 **v1 concluído — IFRS 17 Risk Adjustment Engine**

Repositório de portfólio com pipelines quantitativos modulares em Python
(dados → modelagem → simulação → validação → governança), aplicados a
dois domínios regulatórios: risco de crédito bancário (IFRS 9 /
Resolução CMN 4.966) e risco atuarial de seguros (IFRS 17).

> **Escopo:** aplicações de pesquisa e portfólio para experimentação
> quantitativa. Não substituem modelos de produção, processos de
> validação institucional ou requisitos regulatórios de um banco/seguradora.

---

# Versões

## 📊 v2 — [credit-risk-ecl-engine](credit-risk-ecl-engine/) *(atual)*

Motor de **Perda Esperada de Crédito (ECL)** para carteiras bancárias,
conforme **IFRS 9** e **Resolução CMN n. 4.966/2021**: modelagem de PD,
LGD e EAD; staging IFRS 9 (Stage 1/2/3); simulação de Monte Carlo com
**correlação entre segmentos via cópula Gaussiana** (VaR/CVaR);
validação (Gini, KS, PSI, backtesting de Kupiec); stress testing.
Dataset real (UCI German Credit) baixado e usado de fato — resultados
gerados por execução real, não simulados.

➡️ [README completo](credit-risk-ecl-engine/README.md) · [Notebook executado](credit-risk-ecl-engine/notebooks/credit_risk_ecl_engine.ipynb)

## 🏛️ v1 — [ifrs17-risk-adjustment](ifrs17-risk-adjustment/)

Motor de **Ajuste ao Risco (Risk Adjustment)** para contratos de seguro
e previdência, conforme **IFRS 17**: modelagem de frequência/severidade,
simulação de Monte Carlo, cálculo de VaR/CTE e validação atuarial.

➡️ [README completo](ifrs17-risk-adjustment/README.md)

---

# A evolução v1 → v2

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

---

# O que este repositório demonstra

* Modelagem estatística e atuarial/creditícia (PD, LGD, EAD, frequência, severidade);
* Simulação de Monte Carlo e modelagem de dependência via cópulas;
* Métricas de risco: VaR, CVaR/CTE, ECL, Risk Adjustment;
* Validação estatística: Gini, KS, PSI, testes de aderência, backtesting;
* Stress testing e análise de sensibilidade;
* Governança de modelos: audit trail, versionamento, quality gates;
* Pipelines modulares em Python, testados (pytest) e documentados;
* Alinhamento explícito a normas regulatórias (IFRS 9, IFRS 17, CMN 4.966, SUSEP, BACEN).

---

# Stack

Python 3.10+ · NumPy · Pandas · SciPy · scikit-learn · statsmodels ·
Matplotlib · Jupyter

# Estrutura do Repositório

```text
IFRS17_Risk/
│
├── credit-risk-ecl-engine/     v2 — risco de crédito bancário (IFRS 9 / CMN 4.966)
├── ifrs17-risk-adjustment/     v1 — risco atuarial de seguros (IFRS 17)
├── main.ipynb                  notebook exploratório original da v1
└── resumo.md                   guia de estudo da v1
```

---

# Versão

**v2.0.0 — Setembro de 2026** (credit-risk-ecl-engine) · **v1.0.0 — Março de 2026** (ifrs17-risk-adjustment)

# Licença

MIT License.

# Autor

**Yuri Fernando Dubbern**

AI/ML Engineer · Data Science · Statistical Modeling · Risk Analytics

[LinkedIn](https://www.linkedin.com/in/yuridubbern) · [GitHub](https://github.com/Yuri-Fernando) · [Lattes](http://lattes.cnpq.br/7151392692642166) · [Linktree](https://linktr.ee/yuri.f.dubbern)
