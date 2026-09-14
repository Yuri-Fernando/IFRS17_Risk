# Trilha de Auditoria — Credit Risk ECL Engine

## Objetivo

Garantir que qualquer número de provisão produzido pelo motor possa ser
**reconstituído integralmente**: quais dados entraram, qual modelo foi
usado, quais parâmetros de simulação e quais resultados de validação
acompanharam aquela execução.

## Como funciona

Toda execução de `run_pipeline()` (`src/cloud/pipeline.py`) instancia um
`AuditLog` (`src/governance/audit_log.py`) que registra, em ordem
cronológica, cada etapa do pipeline com timestamp UTC:

1. `load_data` — fonte e número de registros carregados
2. `preprocess` — número de atributos gerados
3. `train_pd_models` — métricas de cada candidato e modelo campeão escolhido
4. `staging` — distribuição de contratos por stage
5. `lgd_ead` — LGD médio e EAD total
6. `ecl_calculation` — totais de provisão
7. `monte_carlo_copula` — parâmetros de correlação e resultados de VaR/CVaR
8. `validation` — Gini, KS, PSI, resultados de backtesting
9. `stress_test` — resultados dos 4 cenários
10. `pipeline_complete` — tempo total de execução

O log completo é serializado em `reports/result_final.json` (chave
`audit_log`) a cada execução com `--export-json`.

## Versionamento de modelo

`src/governance/model_versioning.py` gera um hash SHA-256 (12
caracteres) determinístico a partir do nome do modelo campeão e dos
parâmetros de execução (fonte de dados, número de simulações, correlações
utilizadas). Duas execuções com os mesmos parâmetros produzem o mesmo
`version_hash` — qualquer mudança de premissa gera um hash diferente,
tornando trivial identificar se um resultado reportado corresponde à
configuração vigente ou a uma versão anterior do modelo.

## Requisito regulatório atendido

Este mecanismo endereça a exigência de rastreabilidade de modelos de
risco prevista na Resolução CMN 4.966/2021 e nas práticas de Model Risk
Management (governança de modelos), permitindo auditoria externa e
interna sem depender de reconstituição manual do histórico de execuções.
