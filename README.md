# IFRS17_Risk — Modelagem de Risco Atuarial e de Crédito

### Três motores quantitativos de risco/provisão financeira, evoluindo do mesmo núcleo de engenharia para domínios regulatórios diferentes

## Status

🟢 **v3 em portfólio — Pension Risk Adjustment Engine** · 🟢 **v2 concluído — Credit Risk ECL Engine** · 🟢 **v1 concluído — IFRS 17 Risk Adjustment Engine**

Repositório de portfólio com pipelines quantitativos modulares em Python
(dados → modelagem → simulação → validação → governança), aplicados a
dois domínios regulatórios: risco atuarial de seguros/previdência (IFRS 17)
e risco de crédito bancário (IFRS 9 / Resolução CMN 4.966).

> **Escopo:** aplicações de pesquisa e portfólio para experimentação
> quantitativa. Não substituem modelos de produção, processos de
> validação institucional ou requisitos regulatórios de um banco/seguradora.

---

# Versões

## 🏦 v3 — [pension-risk-adjustment-engine](pension-risk-adjustment-engine/) *(atual)*

Motor de **Ajuste ao Risco (AR) multi-produto** para Previdência
Complementar e Benefícios de Risco (Peculio, Pensão por Morte, Renda por
Invalidez, Pensão ao Menor, Longevidade), sob **IFRS 17**. Reconstrói e
**completa** a metodologia real desenvolvida em ~4 meses de trabalho
como bolsista/estagiário atuarial em uma instituição financeira —
credibility testing (Bühlmann), simulação de Monte Carlo com CTE e
teste de convergência, benefício de diversificação entre riscos, e
cenário de correlação adversa (longevidade × conversão × resgate) via
cópula Gaussiana. Dataset 100% sintético e internamente auditável
(A/E ≈ 100% contra a própria tábua geradora) — nenhum dado real de
nenhuma carteira é usado. Resultados gerados por execução real.

➡️ [README completo](pension-risk-adjustment-engine/README.md) · [Notebook executado](pension-risk-adjustment-engine/notebooks/pension_risk_adjustment_e2e.ipynb)

## 📊 v2 — [credit-risk-ecl-engine](credit-risk-ecl-engine/)

Motor de **Perda Esperada de Crédito (ECL)** para carteiras bancárias,
conforme **IFRS 9** e **Resolução CMN n. 4.966/2021**: modelagem de PD,
LGD e EAD; staging IFRS 9 (Stage 1/2/3); simulação de Monte Carlo com
**correlação entre segmentos via cópula Gaussiana** (VaR/CVaR);
validação (Gini, KS, PSI, backtesting de Kupiec); stress testing.
Dataset real (UCI German Credit) baixado e usado de fato — resultados
gerados por execução real, não simulados.

🆕 **Novo — extensão v2.1 Lifetime PD & Forward-Looking (set/2026):** survival
analysis (Kaplan-Meier, Cox PH, Weibull AFT, risco competitivo) substituindo
a extrapolação de hazard constante, vintage e matriz de migração
(Corrente→30→60→Default com cura), PIT × TTC via satélite macro e cenários
base/upside/downside com ECL ponderada, LGD de workout com downturn, CCF do
rotativo, PD bayesiana por segmento, waterfall de drivers da ECL e
*validation pack* automático + documentação de Model Risk Management — sobre
um painel sintético mensal com verdade conhecida (o German Credit não tem
originação nem histórico).

➡️ [README completo](credit-risk-ecl-engine/README.md) · [Notebook executado](credit-risk-ecl-engine/notebooks/credit_risk_ecl_engine.ipynb) · [Validation pack](credit-risk-ecl-engine/reports/lifetime/validation_pack.md)

## 🏛️ v1 — [ifrs17-risk-adjustment](ifrs17-risk-adjustment/)

Motor de **Ajuste ao Risco (Risk Adjustment)** para contratos de seguro
e previdência, conforme **IFRS 17**: modelagem de frequência/severidade,
simulação de Monte Carlo, cálculo de VaR/CTE e validação atuarial.

➡️ [README completo](ifrs17-risk-adjustment/README.md)

---

# A evolução v1 → v2 → v3

O `credit-risk-ecl-engine` (v2) é um **pivô consciente** do
`ifrs17-risk-adjustment` (v1), não um projeto do zero: a mesma
arquitetura de pipeline (dados → modelagem → simulação → validação →
governança) foi migrada de risco atuarial de seguros para **risco de
crédito bancário** — domínio de PD/LGD/EAD e IFRS 9/CMN 4.966. A v2
também endereça, de forma deliberada, uma lacuna metodológica comum em
modelos desse tipo: PoCs que somam perdas assumindo **independência
entre inadimplências** subestimam o risco de cauda de uma carteira
real — resolvida incorporando **correlação entre segmentos via
cópulas** no motor de simulação.

O `pension-risk-adjustment-engine` (v3) fecha um ciclo diferente: durante
o trabalho real de ~4 meses em uma instituição financeira que deu origem
a este projeto, o próprio `ifrs17-risk-adjustment` (v1) foi usado como
referência técnica para justificar escolhas metodológicas no banco
(comparação VaR vs. CTE vs. Custo de Capital, teste de convergência,
fixação de semente). A v3 devolve esse aprendizado ao portfólio,
implementando a metodologia real multi-produto — com as melhorias que
não puderam ser concluídas no projeto original (credibility testing,
diversificação entre riscos, correlação adversa via cópula) — e
reaproveitando a técnica de cópulas já validada na v2.

Os três projetos permanecem no repositório para evidenciar essa
evolução do raciocínio técnico entre os domínios.

---

# O que este repositório demonstra

* Modelagem estatística e atuarial/creditícia (PD, LGD, EAD, frequência, severidade, credibility testing);
* Simulação de Monte Carlo e modelagem de dependência via cópulas;
* Métricas de risco: VaR, CVaR/CTE, ECL, Risk Adjustment;
* Validação estatística: Gini, KS, PSI, testes de aderência, backtesting, consistência interna de dataset sintético;
* Stress testing e análise de sensibilidade;
* Survival analysis (Kaplan-Meier, Cox, Weibull), vintage analysis, matriz de migração e PIT/TTC com cenários macro ponderados (IFRS 9 forward-looking);
* Governança de modelos: audit trail, registro formal de premissas, versionamento, quality gates;
* Pipelines modulares em Python, testados (pytest) e documentados, com notebook, CLI e dashboard interativo;
* Alinhamento explícito a normas regulatórias (IFRS 9, IFRS 17, CMN 4.966, SUSEP, BACEN);
* Reconstrução documentada e honesta de metodologia real de projeto profissional, com dados sintéticos e transparência total sobre limitações.

---

# Stack

Python 3.10+ · NumPy · Pandas · SciPy · scikit-learn · statsmodels ·
Matplotlib · Streamlit · Jupyter

# Estrutura do Repositório

```text
IFRS17_Risk/
│
├── pension-risk-adjustment-engine/   v3 — AR multi-produto de previdência (IFRS 17)
├── credit-risk-ecl-engine/           v2 — risco de crédito bancário (IFRS 9 / CMN 4.966)
├── ifrs17-risk-adjustment/           v1 — risco atuarial de seguros (IFRS 17)
├── main.ipynb                        notebook exploratório original da v1
└── resumo.md                         guia de estudo da v1
```

---

# Versão

**v3.0.0 — Setembro de 2026** (pension-risk-adjustment-engine) · **v2.1.0 — Setembro de 2026** (credit-risk-ecl-engine: lifetime PD & forward-looking) · **v2.0.0 — Setembro de 2026** (credit-risk-ecl-engine) · **v1.0.0 — Março de 2026** (ifrs17-risk-adjustment)

# Licença

MIT License.

# Autor

**Yuri Fernando Dubbern**

AI/ML Engineer · Data Science · Statistical Modeling · Risk Analytics

[LinkedIn](https://www.linkedin.com/in/yuridubbern) · [GitHub](https://github.com/Yuri-Fernando) · [Lattes](http://lattes.cnpq.br/7151392692642166) · [Linktree](https://linktr.ee/yuri.f.dubbern)
