# Política de mudança de modelo

| Classe | Exemplos | Exigência |
|---|---|---|
| Material | nova metodologia de PD lifetime, novo satélite macro, mudança de definição de default | validação completa + aprovação antes do uso |
| Moderada | recalibração de parâmetros, novos pesos de cenário, novo segmento de LGD | validação focada + sensibilidade + aprovação |
| Menor | refatoração sem mudança numérica, documentação | testes automatizados verdes + registro no CHANGELOG |

Toda mudança: commit identificado, hash de configuração (`ModelVersion`), trilha de auditoria (`AuditLog`) e comparação antes/depois da ECL (waterfall).
Recalibração **nunca** é disparada automaticamente por drift — drift abre revisão.
