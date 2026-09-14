# Relatório de Validação — Credit Risk ECL Engine

> Os números concretos desta execução (Gini, KS, PSI, backtesting) são
> gerados automaticamente a cada `python run_pipeline.py --export-json`
> e ficam disponíveis em `reports/result_final.json`, seção `validation`.
> Este documento descreve **o que** é validado e **como interpretar**
> cada teste — não fixa números, que mudam a cada execução/calibração.

## 1. Poder discriminante (Gini / KS / AUC)

- **Gini** = 2×AUC − 1. Mede a capacidade do modelo de ordenar tomadores
  do mais arriscado ao menos arriscado.
- **KS** (Kolmogorov-Smirnov): distância máxima entre as curvas
  acumuladas de bons e maus pagadores.
- **Gate de qualidade** (`config/model_config.yaml`): Gini mínimo 0,40 e
  KS mínimo 0,30 para o modelo ser considerado apto à produção.

## 2. Calibração

A tabela de calibração (`calibration_table` em
`src/validation/model_validation.py`) agrupa a carteira em decis de PD
prevista e compara com a taxa de default observada em cada decil. Um
modelo bem calibrado tem desvio absoluto baixo em todos os decis — não
apenas boa ordenação (Gini), mas boa **magnitude** de probabilidade, que
é o que realmente importa para o cálculo de ECL (uma soma de PDs, não um
ranking).

## 3. Estabilidade populacional (PSI)

O PSI compara a distribuição de PD do modelo entre o conjunto de treino e
o de teste (proxy, neste PoC, de comparação entre safras/períodos em
produção). Interpretação de mercado:

| PSI | Interpretação |
|---|---|
| < 0,10 | Estável — nenhuma ação necessária |
| 0,10 – 0,25 | Atenção — monitorar próximas safras |
| > 0,25 | Mudança significativa — recalibração recomendada |

## 4. Backtesting (Teste de Kupiec / POF)

Para cada stage, compara-se a PD média prevista com a taxa de default
efetivamente observada, via teste de razão de verossimilhança (Kupiec
Proportion of Failures). H0: a PD prevista é estatisticamente compatível
com a taxa observada. Rejeição de H0 indica necessidade de recalibração
do modelo para aquele stage.

## 5. Comparação de modelos (champion vs. challenger)

Ver `reports/model_comparison.md` — a Regressão Logística é o champion
por interpretabilidade regulatória; o Gradient Boosting serve de
challenger para quantificar o custo de interpretabilidade (diferença de
Gini entre os dois).

## 6. Stress testing

Ver `reports/model_comparison.md`, seção de cenários — sensibilidade da
ECL a choques de PD e LGD downturn.

## 7. Simulação de Monte Carlo com cópula

A qualidade da simulação é verificada por:
- Convergência do VaR/CVaR com o aumento de `n_simulations` (recomenda-se
  rodar com 50.000+ simulações antes de qualquer uso além de PoC).
- Consistência ordinal: VaR 99,9% deve ser sempre ≥ VaR 95% (testado em
  `tests/test_models.py::test_copula_simulation_produces_valid_distribution`).
- O benefício de diversificação reportado deve ser interpretado com
  cautela: reflete a correlação **parametrizada**, não estimada de dados
  reais (ver limitação #5 em `reports/assumptions.md`).
