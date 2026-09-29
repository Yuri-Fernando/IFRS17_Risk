# Model Card — Credit Risk ECL Engine (v2 + extensão lifetime v2.1)

| Campo | Conteúdo |
|---|---|
| Finalidade | Estimar Perda Esperada de Crédito (IFRS 9 / CMN 4.966) em PoC de portfólio |
| Componentes | PD 12m (logística/GBM, German Credit) · PD lifetime (Kaplan-Meier por rating, Markov para contratos em atraso) · satélite macro PIT/TTC · LGD de workout (garantia/LTV, downturn) · EAD (Price; rotativo com CCF) · ECL por cenário e ponderada · cópula (VaR/CVaR) |
| Dados | German Credit (real, 1.000 contratos) para PD 12m; painel sintético mensal (8.000 contratos, 54 meses, `src/data/panel.py`, seed 2026) para lifetime/macro/LGD/CCF |
| Saídas | `reports/result_final.json` (v2) · `reports/lifetime/summary.json`, `validation_pack.md` (v2.1) |
| Métricas-chave (v2.1) | Gini 0,557 (PD na originação × default 12m); 1 de 5 ratings fora do IC de Jeffreys (C, subestima); 3 de 10 safras em vermelho no backtesting (safras expostas à recessão) |
| Usos permitidos | Demonstração técnica, ensino, base de discussão metodológica |
| Usos proibidos | Provisão contábil real, decisão de crédito, reporte regulatório |
| Dono | Autor do repositório (portfólio) |
| Status | Validado tecnicamente — **aprovação pendente** (ver `model_inventory.md`) |

Limitações: ver [`limitations.md`](limitations.md).
