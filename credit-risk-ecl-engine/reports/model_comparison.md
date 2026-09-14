# Comparação de Modelos e Resultados — Execução de Referência

> Gerado a partir de `python run_pipeline.py --export-json` com o dataset
> real German Credit (1.000 contratos). Reproduzível: os `seeds` de cada
> etapa estão fixados no código (ver `config/parameters.yaml`). Números
> completos em `reports/result_final.json`.

## 1. Champion vs. Challenger (PD)

| Modelo | Papel | Gini | KS | AUC |
|---|---|---|---|---|
| Regressão Logística | **Champion** | **0,617** | **0,531** | 0,809 |
| Gradient Boosting | Challenger | 0,595 | 0,486 | 0,797 |

**Decisão**: a Regressão Logística venceu por Gini mesmo sendo o modelo
mais simples — resultado que reforça sua escolha como champion também
sob o critério de interpretabilidade regulatória (não houve trade-off
significativo de performance a compensar pela caixa-preta do GBM). Ambos
superam o gate mínimo de qualidade (Gini ≥ 0,40, KS ≥ 0,30) definido em
`config/model_config.yaml`.

## 2. ECL por Stage IFRS 9

| Stage | Contratos | Exposição (EAD) | PD média | LGD média | ECL | Coverage ratio |
|---|---|---|---|---|---|---|
| 1 (normal) | 245 | R$ 425.092,50 | 10,6% | 45,3% | R$ 21.403,99 | 5,0% |
| 2 (SICR) | 455 | R$ 1.037.781,50 | 61,7% | 50,0% | R$ 393.953,91 | 38,0% |
| 3 (default) | 300 | R$ 827.006,60 | 100,0% | 52,5% | R$ 459.555,77 | 55,6% |
| **Total** | **1.000** | **R$ 2.289.880,60** | — | — | **R$ 874.913,67** | **38,2%** |

O coverage ratio total (38,2%) é elevado frente a carteiras bancárias
reais (tipicamente 2-6%) porque o dataset German Credit tem uma taxa de
"mau pagador" de 30% por desenho amostral — ver limitação em
`docs/dataset_card.md`. Os números devem ser lidos como demonstração
metodológica da mecânica de cálculo, não como benchmark de mercado.

## 3. ECL por segmento (correlação de risco)

| Segmento | Contratos | Exposição | ECL | Coverage ratio |
|---|---|---|---|---|
| Bens de consumo | 485 | R$ 957.709,20 | R$ 342.965,17 | 35,8% |
| Veículos | 337 | R$ 888.916,70 | R$ 332.642,10 | 37,4% |
| Pessoal | 169 | R$ 435.657,60 | R$ 198.067,69 | 45,5% |
| PJ capital de giro | 9 | R$ 7.597,10 | R$ 1.238,71 | 16,3% |

## 4. Simulação de Monte Carlo com cópula (10.000 cenários)

| Métrica | Valor |
|---|---|
| Perda esperada simulada (EL) | R$ 874.570,34 |
| VaR 95% | R$ 956.175,22 |
| VaR 99,9% | R$ 1.026.556,20 |
| CVaR 95% (Expected Shortfall) | R$ 976.174,43 |
| CVaR 99,9% | R$ 1.037.848,15 |
| **Benefício de diversificação** | R$ 295,19 |
| ECL contábil (soma independente) | R$ 874.913,67 |

**Leitura**: a perda esperada simulada (que já incorpora correlação
entre segmentos) praticamente coincide com a ECL contábil somada sob
hipótese de independência (diferença de ~R$ 295, <0,1%) — o que é
esperado, já que a *esperança* da perda agregada é matematicamente
invariante à correlação entre os componentes (correlação afeta a
variância/cauda, não a média). O valor que realmente evidencia o
impacto da correlação é a distância entre VaR 99,9% (R$ 1.026.556) e a
ECL contábil pontual (R$ 874.914) — um **gap de ~17%** que a provisão
contábil, por natureza (baseada em esperança), não captura, mas que é
essencial para dimensionamento de capital econômico e para responder à
pergunta "quanto o banco pode perder num cenário de cauda, dado que os
segmentos não são independentes".

## 5. Validação estatística

| Métrica | Valor | Gate | Status |
|---|---|---|---|
| Gini | 0,617 | ≥ 0,40 | ✅ |
| KS | 0,531 | ≥ 0,30 | ✅ |
| PSI (treino vs. teste) | 0,026 | ≤ 0,25 | ✅ estável |

Backtesting de Kupiec por stage: ver interpretação crítica em
`reports/assumptions.md` (seção "Achado de validação") — os resultados
brutos não são conclusivos sobre calibração num corte transversal único,
e essa limitação é documentada explicitamente em vez de ocultada.

## 6. Stress testing

| Cenário | Multiplicador PD | Add-on LGD | ECL total | Δ vs. base |
|---|---|---|---|---|
| Base | 1,00x | +0pp | R$ 874.913,67 | — |
| Moderado | 1,30x | +5pp | R$ 1.016.529,63 | **+16,2%** |
| Severo | 1,80x | +12pp | R$ 1.225.578,15 | **+40,1%** |
| Extremo | 2,50x | +20pp | R$ 1.409.522,26 | **+61,1%** |

A sensibilidade da provisão a choques de PD/LGD é significativa e
não-linear — informação diretamente utilizável em discussões de apetite
ao risco e dimensionamento de capital de contingência.
