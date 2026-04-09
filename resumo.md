# Resumo do Projeto: IFRS 17 Risk Adjustment Engine

Este documento serve como um guia de estudos e visão geral técnica do projeto **IFRS 17 Risk Adjustment Engine**. O objetivo é facilitar o entendimento da arquitetura, metodologia e execução do modelo.

---

## 1. Visão Geral (O que é o projeto?)

O projeto é um motor de cálculo atuarial e estatístico para mensuração de provisões técnicas conforme a norma internacional **IFRS 17 (Insurance Contracts)**. 

### O Problema
Empresas de seguro e previdência precisam reservar capital para cobrir compromissos futuros com segurados. A norma IFRS 17 exige que essa reserva seja composta pelo **BEL** (Best Estimate Liability) e pelo **RA** (Risk Adjustment).

### A Solução
Este motor automatiza o cálculo do RA utilizando técnicas avançadas de ciência de dados e atuária:
- **Modelagem de Frequência e Severidade**: Decompõe o risco em "quantas vezes ocorre" e "qual o valor médio".
- **Simulação de Monte Carlo**: Gera milhares de cenários possíveis para capturar a incerteza.
- **Validação Rigorosa**: Testes estatísticos que garantem a conformidade regulatória (IFRS, SUSEP, BRGAAP).

---

## 2. Arquitetura do Projeto

O projeto é altamente modular e segue as melhores práticas de engenharia de software:

- **`notebooks/main.ipynb`**: Orquestrador principal. Ideal para apresentações e análise visual.
- **`src/`**: Núcleo lógico do sistema.
    - `data/`: Carregamento e limpeza de dados (Real vs. Sintético).
    - `actuarial/`: Cálculo de BEL, projeções de 30 anos, modelos de mortalidade e cancelamento (lapse).
    - `modeling/`: Treinamento de distribuições (Poisson, Lognormal, Gamma) e métricas de risco (VaR, CTE).
    - `simulation/`: Motor de Monte Carlo para 10.000+ simulações.
    - `validation/`: Testes de aderência, estresse e backtesting.
    - `governance/`: Trilhas de auditoria e versionamento de modelos.
- **`reports/`**: Documentação técnica detalhada e resultados finais.

---

## 3. Metodologia Estatística

### Fluxo de Cálculo
1. **BEL**: Projeção de fluxos futuros descontados a valor presente.
2. **Decomposição**:
    - **Frequência (N)**: Segue distribuição Poisson ou Binomial Negativa.
    - **Severidade (X)**: Segue distribuição Lognormal ou Gamma.
3. **Agregação**: A perda total agregada $S$ é a soma dos custos de todos os sinistros simulados.
4. **Risk Adjustment (RA)**: Calculado via **VaR** (Value at Risk) ao nível de 95% de confiança.
    - $RA = VaR_{95\%}(S) - E[S]$

---

## 4. Como Estudar este Projeto

Se você quer dominar este projeto, siga esta trilha:

1. **Nível Executivo**: Leia `docs/business_explanation.md` para entender o valor de negócio.
2. **Nível Atuarial**: Estude `reports/methodology.md` e `reports/assumptions.md` para entender as premissas matemáticas.
3. **Nível Técnico/Código**:
    - Execute o `main.ipynb` para ver o pipeline em ação.
    - Explore `src/modeling/risk_adjustment.py` para ver a implementação dos cálculos de risco.
4. **Governança**: Veja como o `src/governance/audit_log.py` captura cada etapa para fins de auditoria.

---

## 5. Resumo das Ferramentas Utilizadas

- **Linguagem**: Python 3.10+
- **Bibliotecas Base**: NumPy, Pandas, SciPy.
- **Modelagem**: Scikit-Learn, Statsmodels.
- **Visualização**: Matplotlib, Seaborn.
- **Documentação**: Markdown, LaTeX (para fórmulas).

---

**Status do Projeto**:  100% Funcional e Documentado  
**Objetivo**: Excelência técnica em conformidade com IFRS 17.
