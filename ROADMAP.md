# ROADMAP — IFRS17_Risk (frente de crédito)

Legenda: ✅ feito · 🟡 parcial · ⏳ planejado

| Item do plano (seção 6) | Estado | Observação |
|---|---|---|
| 6.1 Lifetime PD via survival (KM, Cox, Weibull) × fórmula simples | ✅ | v2.1 |
| 6.2 PIT × TTC | ✅ | Vasicek + satélite macro |
| 6.3 Cenários macro e ECL ponderada | ✅ | pesos 50/20/30 ilustrativos |
| 6.4 LGD: garantia, recuperação, workout, desconto, downturn | ✅ | viés de resolução declarado |
| 6.5 EAD: amortizável, rotativo, CCF | 🟡 | off-balance (garantias prestadas) ⏳ |
| 6.6 Vintage analysis (safra, MOB, default acumulado) | ✅ | |
| 6.7 Matriz de transição (Current→30→60→90→Default, cura) | ✅ | Markov homogêneo; versão dependente de MOB/macro ⏳ |
| 6.8 Validation pack automático | ✅ | |
| 6.9 Model Risk Governance (`docs/model_risk/`) | ✅ | |
| Bayesian PD por segmento | ✅ | |
| Decomposição de variação da ECL | 🟡 | waterfall de drivers numa data; entre duas datas-base ⏳ |
| Random Survival Forest (challenger) | ⏳ | exigiria scikit-survival |
| Monitoramento contínuo automatizado | ⏳ | indicadores já calculados no pipeline |
| ECL consumindo scores/model versions do RiskCredit | ⏳ | P2 do plano (integração de portfólio) |
| Dados reais multi-safra | ⏳ | depende de base pública adequada |
