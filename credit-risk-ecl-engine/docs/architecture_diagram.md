# Diagrama de Arquitetura — Credit Risk ECL Engine

```mermaid
flowchart TD
    A[data/raw: German Credit CSV] --> B[src/data/load_data.py]
    B --> C[src/data/preprocess.py<br/>segmentação + encoding]
    C --> D1[src/modeling/pd_model.py<br/>Logistic Regression]
    C --> D2[src/modeling/pd_model.py<br/>Gradient Boosting]
    D1 --> E{Champion?<br/>maior Gini}
    D2 --> E
    E --> F[src/modeling/staging.py<br/>Stage 1 / 2 / 3 - SICR]
    F --> G1[src/modeling/lgd_model.py<br/>LGD por colateral - Beta]
    F --> G2[src/modeling/ead_model.py<br/>EAD - saldo remanescente]
    G1 --> H[src/modeling/ecl_calculation.py<br/>ECL = PD x LGD x EAD]
    G2 --> H
    H --> I[src/simulation/copula_simulation.py<br/>Monte Carlo + cópula Gaussiana<br/>VaR / CVaR / diversificação]
    H --> J[src/validation/model_validation.py<br/>Gini, KS, PSI, calibração]
    H --> K[src/validation/backtesting.py<br/>Teste de Kupiec]
    H --> L[src/validation/stress_test.py<br/>4 cenários macro]
    I --> M[src/governance/audit_log.py<br/>trilha de auditoria]
    J --> M
    K --> M
    L --> M
    M --> N[src/governance/model_versioning.py<br/>hash de versão do modelo]
    N --> O[reports/result_final.json<br/>data/processed/portfolio_ecl_scored.csv]

    style E fill:#f2d16d,stroke:#8a6d1a
    style H fill:#7fb3d5,stroke:#2e5f7a
    style I fill:#c39bd3,stroke:#6c3483
    style O fill:#82e0aa,stroke:#1e8449
```

## Camadas do sistema

| Camada | Módulos | Responsabilidade |
|---|---|---|
| **Dados** | `src/data/` | Carga, limpeza, segmentação, encoding |
| **Modelagem** | `src/modeling/` | PD, staging IFRS 9, LGD, EAD, ECL |
| **Simulação** | `src/simulation/` | Monte Carlo com correlação (cópula) |
| **Validação** | `src/validation/` | Métricas estatísticas, backtesting, stress test |
| **Governança** | `src/governance/` | Auditoria, versionamento |
| **Orquestração** | `src/cloud/pipeline.py` | Executa o fluxo completo, ponto único de entrada |

## Fluxo de dados por contrato

```
contrato individual
   → atributos (status, histórico, garantia, valor, prazo, ...)
   → PD 12m (modelo campeão)
   → PD originação (proxy) → comparação → Stage (1/2/3)
   → PD lifetime (se Stage 2/3)
   → LGD (segmento de garantia)
   → EAD (saldo remanescente)
   → ECL do contrato = PD_usada x LGD x EAD
   → soma na carteira → ECL total, por stage, por segmento
   → simulação correlacionada → distribuição de perda agregada → VaR/CVaR
```
