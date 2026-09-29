# CHANGELOG — IFRS17_Risk

Documento mestre de histórico do repositório. Formato [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) + SemVer por motor.

## [credit-risk-ecl-engine 2.1.0] — 2026-09-28 — Lifetime PD & Forward-Looking

Origem: plano de evolução do portfólio financeiro (seção 6), itens P0 "survival/lifetime PD + macro scenarios +
vintage/migration + validation pack" e P1 "PIT/TTC, downturn LGD, CCF/EAD avançado, Model Risk Governance, Bayesian PD".

### Added
- `src/data/panel.py` — painel sintético mensal (8.000 contratos, 54 meses, safras, DPD com cura, pré-pagamento,
  recessão sintética, workouts de recuperação).
- `src/modeling/survival/` — Kaplan-Meier, incidência cumulativa (risco competitivo), Cox PH, Weibull AFT, term structure.
- `src/modeling/vintage_migration.py` — vintage, atraso por mês, matriz de migração, lifetime PD por Markov.
- `src/modeling/macro_pit.py` — Vasicek PIT/TTC, satélite macro, cenários base/upside/downside.
- `src/modeling/lgd_ead_advanced.py` — LGD de workout, downturn, CCF, EAD amortizável.
- `src/modeling/bayesian_pd.py` — PD Beta-Binomial com shrinkage.
- `src/modeling/lifetime_ecl.py` — ECL lifetime com staging (30 DPD + SICR), cenários ponderados e waterfall.
- `src/validation/validation_pack.py` + `reports/lifetime/validation_pack.md` (gerado).
- `run_lifetime_pipeline.py`, `tests/test_lifetime.py` (12 testes; suíte do motor: 23).
- `credit-risk-ecl-engine/docs/model_risk/` — model card, inventário, políticas de validação/mudança/monitoramento, limitações.

### Não alterado
- Pipeline original (`run_pipeline.py`, German Credit) e seus resultados em `reports/result_final.json`.

## [pension-risk-adjustment-engine 3.0.0] — 2026-09
- Motor de Ajuste ao Risco multi-produto (IFRS 17) — ver README da v3.

## [credit-risk-ecl-engine 2.0.0] — 2026-09
- Motor de ECL (IFRS 9 / CMN 4.966) com PD/LGD/EAD, staging, cópula, VaR/CVaR, validação e stress.

## [ifrs17-risk-adjustment 1.0.0] — 2026-03
- Motor de Risk Adjustment (IFRS 17): frequência/severidade, Monte Carlo, VaR/CTE.
