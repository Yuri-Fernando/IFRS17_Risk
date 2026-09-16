# Pension Risk Adjustment Engine

### Motor de cálculo de Ajuste ao Risco (Risk Adjustment) multi-produto para Previdência Complementar e Benefícios de Risco, sob IFRS 17

## Status

🟢 **Concluído — Versão 3.0 (v3 do portfólio)**

Este projeto implementa, de ponta a ponta, a metodologia de **Ajuste ao Risco (AR)** que
desenvolvi durante ~4 meses de trabalho como bolsista/estagiário atuarial em previdência
complementar aberta de uma instituição financeira — cobrindo **Peculio, Pensão por Morte,
Renda por Invalidez, Pensão ao Menor e Previdência (Longevidade)**.

O projeto real terminou incompleto (fui desligado antes de fechar o cálculo com a carteira
real). Este repositório reconstrói e **completa** a metodologia com dados 100% sintéticos,
endereçando explicitamente os gaps que ficaram em aberto — ver a seção
[Do projeto real a este projeto](#do-projeto-real-a-este-projeto) e a
[metodologia mestre completa](../itau/METODOLOGIA_MESTRE.md).

Este é o **v3** do repositório de portfólio, evolução direta de:
[`ifrs17-risk-adjustment`](../ifrs17-risk-adjustment/) (v1, motor genérico de AR) →
[`credit-risk-ecl-engine`](../credit-risk-ecl-engine/) (v2, pivô para risco de crédito) →
**este projeto (v3, aplicação real de metodologia atuarial multi-produto de previdência)**.

> **Escopo:** aplicação de pesquisa e portfólio para experimentação quantitativa com
> conceitos de IFRS 17. **Nenhum dado, volume ou resultado numérico de nenhuma carteira
> real é usado** — o portfólio é 100% sintético, gerado por simulação a partir de tábuas
> biométricas paramétricas. Não substitui modelos atuariais de produção, processos de
> validação institucional ou requisitos regulatórios reais.

---

# Do projeto real a este projeto

| No projeto real (banco) | Neste projeto |
|---|---|
| Percentil-alvo nunca formalmente aprovado pela liderança | Sensibilidade calculada para P75/P80/P90, com o P80 como padrão configurável |
| Credibility testing (Bühlmann) formulado, nunca codificado | Implementado em `src/actuarial/credibility.py`, com fator Z por célula |
| Benefício de diversificação entre "caixinhas" nunca implementado (soma simples) | Implementado em `src/risk_adjustment/ar_engine.py::combine_components` |
| Cenário de correlação adversa (longevidade↓ + conversão↑ + resgate↓) apenas descrito qualitativamente | Simulado via cópula Gaussiana em `src/risk_adjustment/correlation.py` |
| CTE mencionado como melhoria, nunca calculado | Calculado em toda simulação de Monte Carlo (`MonteCarloResult.cte()`) |
| Teste de convergência do nº de cenários nunca formalizado | Implementado e documentado (`src/simulation/monte_carlo.py::convergence_test`) |
| Só o componente Peculio avançou com dados reais | Todos os 5 componentes (exceto Resgate, sem dados de lapse) implementados de ponta a ponta |
| Base de Resgate/Lapse nunca disponibilizada | Ainda em aberto — ver [Limitações](#limitações-conhecidas) |
| Rastreabilidade de premissas cobrada informalmente em reunião | Formalizada em `src/governance/audit_trail.py` (`reports/assumptions.md`) |

---

# Início Rápido

## 1. Instalar dependências

```bash
cd pension-risk-adjustment-engine
python setup_environment.py
```

Ou manualmente: `pip install -r requirements.txt`

## 2. Abrir o notebook (já vem com resultados e gráficos salvos)

```bash
jupyter notebook notebooks/pension_risk_adjustment_e2e.ipynb
```

## 3. Executar o pipeline via linha de comando

```bash
python run_pipeline.py
```

## 4. Rodar o dashboard interativo

```bash
streamlit run dashboard/app.py
```

## 5. Rodar os testes

```bash
pytest tests/ -v
```

---

# Metodologia (resumo)

```
Base de Expostos + Base de Sinistros (100% sintéticas)
        │
        ▼  conciliação por célula (idade x sexo x produto x mês)
Série histórica de sinistralidade / A/E ratio
        │
        ▼  credibility testing (Bühlmann) + seleção de distribuição (AIC/BIC/KS)
Simulação de Monte Carlo (10.000 cenários, semente fixa)
        │
        ▼  percentil-alvo (P75/P80/P90) / mediana
Fator de stress
        │
        ▼  aplicado à tábua biométrica
QX_stress = fator x QX_base  →  BEL_stress = VPL(QX_stress)
        │
        ▼
AR = BEL_stress − BEL_base  (por componente/"caixinha")
        │
        ▼  soma com benefício de diversificação
AR total  →  impacto no CSM (CSM cai R$1 para cada R$1 de AR)
```

Documentação completa da lógica, decisões, evolução histórica e referências:
[`../itau/METODOLOGIA_MESTRE.md`](../itau/METODOLOGIA_MESTRE.md) ·
resumo técnico deste projeto: [`reports/methodology.md`](reports/methodology.md).

---

# Resultado de Referência (execução real, seed=42)

> Gerado por execução real do `run_pipeline.py` / notebook sobre um portfólio sintético de
> **60.000 segurados** (2.793.864 linhas de exposição mensal, 8.981 sinistros simulados).
> Ver `reports/results/final_results.json` para o resultado completo.

| Etapa | Resultado |
|---|---|
| Consistência interna (A/E, Peculio) | **99,1%** — dentro da tolerância esperada, confirma que o dataset sintético é internamente coerente com a tábua geradora |
| Distribuição selecionada (sinistralidade) | **Lognormal** (menor AIC) |
| Fator de stress — P75 / P80 / P90 | **1,0219 / 1,0272 / 1,0420** |
| Consistência com benchmark Solvency II | ✅ Direcionalmente consistente (nosso stress de 2,72% a P80 é proporcionalmente menor que o choque de 15% do Solvency II a 99,5%, como esperado) |
| Convergência de Monte Carlo (1k→50k cenários) | ✅ Estável (variação < 1%) |

## AR por componente (P80)

| Produto | BEL base | AR monetário | AR (% do BEL) |
|---|---:|---:|---:|
| Peculio | R$ 2.826.323.926 | R$ 29.715.004 | 1,05% |
| Pensão por Morte | R$ 4.213.515.841 | R$ 44.464.606 | 1,06% |
| Renda por Invalidez | R$ 3.804.735.429 | R$ 33.867.873 | 0,89% |
| Pensão ao Menor | R$ 395.526.369 | R$ 4.177.246 | 1,06% |
| Previdência — Longevidade | R$ 8.864.300.449 | R$ 76.538.737 | 0,86% |
| **Total (soma simples)** | R$ 20.104.402.014 | **R$ 188.763.466** | 0,94% |
| **Total diversificado (−15%)** | — | **R$ 160.448.946** | **0,80%** |

> Impacto no CSM: **-R$ 160.448.946** (cada R$1 de AR reduz o CSM em R$1 — relação estrutural
> do IFRS 17: `CSM = Prêmio − BEL − AR`).

**Todos os valores acima são de um portfólio 100% sintético — não representam, em nenhuma
medida, dados ou resultados de nenhuma carteira real.**

---

# Estrutura do Projeto

```text
pension-risk-adjustment-engine/
│
├── config/
│   └── config.yaml                    parâmetros centrais (percentis, tábuas, seed, correlações)
│
├── data/
│   ├── raw/ processed/ external/      (vazio — dataset é gerado em memória, não persistido em CSV)
│
├── notebooks/
│   ├── pension_risk_adjustment_e2e.ipynb   notebook completo, executado (resultados e gráficos salvos)
│   └── _build_notebook.py                  script que gera o notebook célula a célula (nbformat)
│
├── src/
│   ├── data/
│   │   ├── mortality_tables.py        tábuas biométricas paramétricas (Gompertz-Makeham)
│   │   └── synthetic_portfolio.py     gerador de portfólio + exposição + sinistros sintéticos
│   │
│   ├── actuarial/
│   │   ├── experience_engine.py       A/E ratio, conciliação (oficial/sensibilidade/pendente)
│   │   ├── credibility.py             credibility testing (Bühlmann)
│   │   └── bel_calculator.py          BEL (lump sum, anuidade, capital equivalente)
│   │
│   ├── modeling/
│   │   ├── distribution_fit.py        seleção de distribuição (AIC/BIC/KS)
│   │   └── frequency_severity.py      frequência (Poisson/NegBin) e severidade (Lognormal)
│   │
│   ├── simulation/
│   │   └── monte_carlo.py             simulação, fator de stress, CTE, teste de convergência
│   │
│   ├── risk_adjustment/
│   │   ├── ar_engine.py               AR por componente, diversificação, benchmark Solvency II
│   │   └── correlation.py             cenário de correlação adversa (cópula Gaussiana)
│   │
│   ├── validation/
│   │   └── diagnostics.py             qui-quadrado, autocorrelação, consistência interna
│   │
│   └── governance/
│       └── audit_trail.py             registro de premissas (hipótese/justificativa/limitação/fonte)
│
├── dashboard/
│   └── app.py                         dashboard interativo (Streamlit)
│
├── reports/
│   ├── methodology.md
│   ├── assumptions.md                 gerado automaticamente pelo pipeline
│   └── results/                       final_results.json + gráficos (.png)
│
├── tests/                             23 testes (pytest) — mortalidade, portfólio, Monte Carlo, AR
│
├── requirements.txt
├── run_pipeline.py                    CLI — executa o pipeline completo sem Jupyter
└── setup_environment.py
```

---

# Metodologia — detalhamento

## 1. Portfólio sintético

Gerado por simulação vetorizada (`src/data/synthetic_portfolio.py`): idade, sexo e produto
distribuídos de forma plausível; sinistros sorteados por Bernoulli usando as **próprias
tábuas biométricas do projeto** — o que torna o dataset internamente auditável (o A/E
agregado deve ficar perto de 100%, verificado em `tests/`).

## 2. Tábuas biométricas

Aproximação paramétrica via **lei de Gompertz-Makeham** (`src/data/mortality_tables.py`),
calibrada para reproduzir a forma de uma curva de mortalidade humana plausível — não os
valores exatos das tábuas oficiais brasileiras (BR-EMS, AT-2000, PRSSVBR/SUSEP), que têm
distribuição restrita a seguradoras/IBA/SUSEP.

## 3. A/E Ratio e credibility testing

Conciliação em 3 categorias (oficial / sensibilidade / pendente), replicando a lógica real
de cruzamento entre base de expostos e base de sinistros. Células com pouca exposição têm o
A/E ajustado em direção ao benchmark de mercado via **credibility de Bühlmann**
(`src/actuarial/credibility.py`).

## 4. Seleção de distribuição e Monte Carlo

Gamma, Lognormal e Normal comparadas por AIC/BIC/KS, com razoabilidade teórica do suporte de
cada uma. Simulação de Monte Carlo com semente fixa, tratamento de zeros por Bernoulli
(`p₀` **estimado empiricamente**, não fixado arbitrariamente — correção de uma falha de
rastreabilidade do projeto original), fator de stress = `percentil_alvo / mediana_simulada`,
com **CTE** calculado como validação cruzada e **teste de convergência** do número de cenários.

## 5. AR por componente e diversificação

`QX_stress = fator × QX_base` (ou `÷ fator` para longevidade) → `AR = BEL_stress − BEL_base`,
por produto, com a direção de stress correta para cada tipo de risco. Soma das "caixinhas"
com benefício de diversificação configurável.

## 6. Cenário de correlação adversa

O pior cenário para o AR de um produto de renda vitalícia é a correlação entre
longevidade↓, conversão↑ e resgate↓ simultâneos — simulado via **cópula Gaussiana**
(`src/risk_adjustment/correlation.py`), a mesma técnica usada no projeto irmão v2
(`credit-risk-ecl-engine`) para correlacionar segmentos de risco de crédito.

---

# Testes

```bash
pytest tests/ -v
```

23 testes cobrindo tábuas biométricas, geração do portfólio sintético (incluindo a verificação
de consistência interna A/E ≈ 100%), simulação de Monte Carlo (reprodutibilidade, CTE ≥ VaR,
convergência) e o motor de AR (direção do stress, diversificação, benchmark Solvency II) —
todos passando.

---

# Limitações Conhecidas

1. **Tábuas biométricas são aproximações paramétricas**, não as tábuas oficiais exatas (BR-EMS/AT-2000/PRSSVBR) — válidas para demonstrar a metodologia, não para uso regulatório real.
2. **Componente de Resgate/Lapse não implementado** — a base de dados correspondente nunca foi disponibilizada no projeto real original; a lógica está descrita qualitativamente na metodologia mestre, mas não calibrada com nenhum dado, real ou sintético.
3. **Pensão por Morte, Renda por Invalidez e Pensão ao Menor usam uma simplificação de "capital equivalente"** para o valor pago na entrada do benefício, em vez de modelar o decremento encadeado completo (entrada + sobrevivência subsequente do beneficiário) — ver `reports/methodology.md`.
4. **Benefício de diversificação (15%) é um parâmetro ilustrativo**, não calibrado por matriz de correlação histórica real entre os componentes.
5. **Portfólio sintético não é calibrado a nenhum mercado real específico** — distribuição etária, de produtos e de capital segurado é ilustrativa.

Ver `reports/assumptions.md` para o registro completo de premissas.

---

# Melhorias Futuras

* Modelo de resgate/lapse via ordenação convexa (referência: MDPI/Risks 2023 — *A Model for Risk Adjustment for Surrender Risk in Life Insurance*), citado na metodologia mestre mas nunca implementado;
* Calibração da matriz de correlação/diversificação a partir de dados históricos reais;
* Modelagem completa do decremento encadeado (entrada no benefício + sobrevivência do beneficiário) para os produtos de renda contingente;
* Bootstrap não paramétrico como alternativa ao Monte Carlo paramétrico para amostras pequenas (sugestão registrada em reunião no projeto real, nunca testada);
* API REST para consulta do AR calculado por cenário.

---

# O que este projeto demonstra

* Modelagem atuarial multi-produto (previdência e benefícios de risco) sob IFRS 17;
* Ajuste ao Risco por intervalo de confiança (percentil), calibrado por simulação de Monte Carlo;
* Credibility testing (Bühlmann);
* Seleção de distribuição estatística com critério combinado (AIC/BIC/KS + razoabilidade teórica);
* Modelagem de dependência entre riscos via cópula Gaussiana;
* Value at Risk (percentil) e Conditional Tail Expectation (CTE);
* Teste de convergência de simulação de Monte Carlo;
* Validação estatística (qui-quadrado, autocorrelação, consistência interna do dataset);
* Governança de modelo: registro formal de premissas (hipótese/justificativa/limitação/fonte);
* Pipeline modular em Python, testado (pytest), com notebook, CLI e dashboard interativo;
* Leitura crítica e documentada de limitações metodológicas — inclusive as herdadas de um projeto real que terminou incompleto.

---

# Versão

**v3.0.0 — Setembro de 2026**

---

# Licença

MIT License.

---

# Autor

**Yuri Fernando Dubbern**

AI/ML Engineer · Data Science · Statistical Modeling · Risk Analytics

[LinkedIn](https://www.linkedin.com/in/yuridubbern) · [GitHub](https://github.com/Yuri-Fernando) · [Lattes](http://lattes.cnpq.br/7151392692642166) · [Linktree](https://linktr.ee/yuri.f.dubbern)
