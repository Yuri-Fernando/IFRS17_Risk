# Validation Pack — Credit Risk ECL Engine · extensão lifetime/forward-looking

Gerado automaticamente por `run_lifetime_pipeline.py` em 2026-09-29T00:45:07.806492+00:00. **Dados sintéticos** (`src/data/panel.py`) — valida o software e o método, não uma carteira real.

## 1. Inventário e status
| model | owner | tier | status | last_validation |
|---|---|---|---|---|
| PD lifetime (KM por rating + Markov p/ atraso) | autor (portfólio) | alto (provisão) | validado tecnicamente — aprovação pendente | 2026-09-29 |
| Satélite macro (probit DR ~ desemprego + PIB) | autor | alto | exploratório — série curta (≤54 meses) | idem |
| LGD workout (garantia/LTV, downturn) | autor | médio | validado tecnicamente — viés de resolução declarado | idem |
| CCF rotativo | autor | médio | validado tecnicamente | idem |

## 2. Discriminação (PD 12m na originação × default em 12 meses)
| auc | gini | ks | n |
|---|---|---|---|
| 0.7785 | 0.5570 | 0.4414 | 7226 |

## 3. Calibração por rating (binomial exato, IC de Jeffreys 95%)
| grade | n | defaults | predicted_pd | observed_dr | jeffreys_low | jeffreys_high | binomial_p | result |
|---|---|---|---|---|---|---|---|---|
| A | 1773 | 22 | 0.0095 | 0.0124 | 0.0080 | 0.0184 | 0.2186 | ok |
| B | 2167 | 56 | 0.0232 | 0.0258 | 0.0198 | 0.0332 | 0.3912 | ok |
| C | 1826 | 107 | 0.0443 | 0.0586 | 0.0485 | 0.0701 | 0.0044 | subestima |
| D | 919 | 95 | 0.0912 | 0.1034 | 0.0849 | 0.1243 | 0.2071 | ok |
| E | 541 | 93 | 0.1807 | 0.1719 | 0.1419 | 0.2054 | 0.6548 | ok |

## 4. Estabilidade
PSI do mix de rating (safras 2022 × 2023): **0.0022**

## 5. Backtesting por safra (semáforo: verde 0,8–1,25 · âmbar 0,6–1,6 · vermelho fora)
| cohort | n | observed | predicted | ratio_obs_pred | traffic_light |
|---|---|---|---|---|---|
| 2022Q1 | 684 | 0.0263 | 0.0287 | 0.9174 | green |
| 2022Q2 | 682 | 0.0132 | 0.0277 | 0.4768 | red |
| 2022Q3 | 712 | 0.0169 | 0.0249 | 0.6775 | amber |
| 2022Q4 | 699 | 0.0229 | 0.0257 | 0.8892 | green |
| 2023Q1 | 718 | 0.0348 | 0.0235 | 1.4825 | amber |
| 2023Q2 | 743 | 0.0283 | 0.0269 | 1.0517 | green |
| 2023Q3 | 726 | 0.0730 | 0.0293 | 2.4943 | red |
| 2023Q4 | 755 | 0.0940 | 0.0453 | 2.0762 | red |
| 2024Q1 | 753 | 0.1116 | 0.0849 | 1.3146 | amber |
| 2024Q2 | 754 | 0.0849 | 0.1315 | 0.6454 | amber |

## 6. Benchmarking de lifetime PD (carteira, meses desde a originação)
| months | kaplan_meier | cif_competing_risk | cox_ph | weibull_aft | markov_chain | simple_formula_v2 |
|---|---|---|---|---|---|---|
| 12 | 0.0500 | 0.0466 | 0.0436 | 0.0439 | 0.0484 | 0.0500 |
| 24 | 0.1274 | 0.1125 | 0.1211 | 0.1114 | 0.0950 | 0.0976 |
| 36 | 0.1865 | 0.1491 | 0.1818 | 0.1842 | 0.1304 | 0.1427 |
| 48 | 0.2077 | 0.1584 | 0.2049 | 0.2555 | 0.1573 | 0.1857 |

## 7. Sensibilidade da ECL
| parameter | value | ecl_weighted |
|---|---|---|
| peso downside | 0.2000 | 2437053.5668 |
| peso downside | 0.3000 | 2508536.2628 |
| peso downside | 0.4000 | 2580018.9588 |
| peso downside | 0.5000 | 2651501.6549 |
| rho (correlação de ativos) | 0.0800 | 2536106.5278 |
| rho (correlação de ativos) | 0.1200 | 2508536.2628 |
| rho (correlação de ativos) | 0.2000 | 2454412.2017 |

## 8. Limitações
- Painel 100% sintético: valida software e método, não uma carteira real.
- Série macro curta (54 meses, 1 recessão): satélite com poucos graus de liberdade.
- KM trata pré-pagamento como censura (PD 'na ausência de saída'); a incidência cumulativa com risco competitivo é reportada ao lado.
- Cauda da hazard além do MOB observado extrapolada pela média dos últimos 12 meses.
- Workouts abertos excluídos da LGD (viés de resolução).
- Vida comportamental do rotativo fixada em 36 meses (premissa).
- Sem calibração regulatória; cenários e pesos ilustrativos.

## 9. Conclusão do validador (automática — requer revisão humana)
Discriminação Gini=0.557. Calibração: 1 de 5 ratings fora do IC de Jeffreys. Backtesting por safra: 3 safra(s) em vermelho. Status sugerido: **aprovado com ressalvas** para uso em PoC; requer revisão humana.
