# Trilha de Auditoria

Documento que registra todas as execuções do modelo para rastreabilidade e conformidade.

## Estrutura de Registro

Cada execução registra:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "operation": "Model Execution",
  "user": "analyst@bank.com",
  "status": "SUCCESS",
  "details": {
    "model_version": "1.0.0",
    "dataset": "2024_Q1_portafolio",
    "n_simulations": 10000,
    "result": {
      "bel": 1250000,
      "ra": 185000,
      "total_provision": 1435000
    }
  }
}
```

## Informações Capturadas

### Execução
- Data/hora (ISO 8601)
- Versão do modelo
- Dataset utilizado
- Usuário responsável
- Status (SUCCESS/FAILURE/WARNING)

### Dados
- Número de registros
- Período coberto
- Validações aplicadas

### Modelos
- Distribuição de frequência
- Parâmetros de frequência
- Distribuição de severidade
- Parâmetros de severidade

### Resultados
- BEL calculado
- Risk Adjustment
- Provisão Total (IFRS 17)
- Métricas de validação

### Mudanças
- Parâmetros alterados
- Motivo da mudança
- Aprovação (if required)

## Retenção de Registros

- **Mínimo legal**: 7 anos (conforme regulação)
- **Recomendado**: 10 anos (conforme boas práticas)
- **Período de teste**: 30 dias

## Acesso à Trilha

Acesso restrito a:
- Analistas de risco autorizados
- Auditoria interna
- Auditoria externa
- Conformidade

## Relatório de Auditoria Periódico

Gerado mensalmente:
- Número de execuções
- Taxa de sucesso/falha
- Mudanças realizadas
- Desvios de expectativa

---

Documento será preenchido via `src/governance/audit_log.py`
