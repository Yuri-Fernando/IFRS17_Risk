# Alinhamento com IFRS 17 - Insurance Contracts

## Enquadramento Regulatório

Este modelo implementa requisitos do IFRS 17 - Insurance Contracts, padrão contábil internacional para reconhecimento e mensuração de contratos de seguro.

## Definições IFRS 17

### Contrato de Seguro

Contrato em que uma parte (assegurador) assume risco de segurado. O risco deve ser significativo (não trivial).

### Obrigação de Desempenho

Obrigação do assegurador de compensar segurado por evento coberto.

### Risk Adjustment

**Definição IFRS 17.37A**:
> "O ajuste ao risco compensa a entidade por assumir incerteza não-financeira sobre as quantidades, período e incidência de fluxos de caixa futuros."

## Estrutura de Mensuração

### Modelo de Valor Presente Esperado

IFRS 17 exige mensuração de Fulfillment Cash Flows, compostos por:

```
FCF = BEL + RA

BEL = Best Estimate Liability
    = Σ E(CF_t) / (1+r)^t

RA  = Risk Adjustment
    = VaR_α(CF) - E(CF)
```

## Componentes da Provisão

### 1. Best Estimate Liability (BEL)

**Definição**: Valor presente não-viés dos fluxos de caixa futuros

**Componentes**:
- Sinistros esperados
- Benefícios contratuais
- Despesas incorridas
- Cancelamentos esperados

**Cálculo no Modelo**:
```python
BEL = Σ(Prêmios_VP) - Σ(Sinistros_VP) - Σ(Despesas_VP) - Ajuste_Lapse
```

**Propriedade**: BEL não inclui margem (não é conservador)

### 2. Risk Adjustment (RA)

**Definição**: Compensação por incerteza não-financeira

**O que RA NÃO é**:
- Não inclui risco financeiro (taxa de juros)
- Não inclui lucro
- Não é margem de segurança geral

**O que RA É**:
- Compensa variabilidade na frequência/severidade
- Compensa incerteza na duração
- Reflete apetite a risco da entidade

**Metodologia**:
```
RA = VaR_95 - E[Perdas]
```

Percentil de 95% é comum, mas pode variar com apetite a risco.

## Alinhamento com Requisitos IFRS 17

### Requisito 1: Decomposição de Componentes

IFRS 17.85-87 exige divisão entre:
1. **Componente de Risco**: RA
2. **Componente de Confiança**: BEL

**Implementação**:
- Frequência modelada separadamente
- Severidade modelada separadamente
- Simulação integra ambas

### Requisito 2: Estimativa de Fluxos de Caixa

IFRS 17.40-44 define:
- Determinístico (projeções baseadas em dados)
- Probabilidade-ponderado (cenários)

**Implementação**:
- Projeção determinística de médias
- Simulação Monte Carlo para distribuição

### Requisito 3: Apresentação Separada

IFRS 17.80-82 exige apresentação de:
- Valor do Liability
- RA separadamente
- Mudanças período a período

**Documentação**:
Relatórios incluem RA como linha separada da BEL.

### Requisito 4: Consistência Metodológica

IFRS 17.36 exige que metodologia seja:
- Consistente ao longo do tempo
- Documentada
- Reavaliada anualmente

**Implementação**:
- Versionamento de modelo
- Audit trail
- Documentação de metodologia

## Métodos Aceitos pela IFRS 17

### 1. Value at Risk (VaR)

Nosso método principal.

**Vantagens**:
- Amplamente aceito em prática de mercado
- Transparente e comunicável
- Reflete percentil de confiança explícito

**Fórmula**:
```
RA = VaR_α - E[L]
```

### 2. Cost of Capital (CoC)

Método alternativo citado em IFRS 17.

**Fórmula**:
```
RA = Σ Capital_t / (1+i)^t
```

Onde Capital_t é o capital necessário para suportar incerteza.

**Vantagens**:
- Abordagem econômica
- Alinhado com Theory of Ruin

### 3. Conditional Tail Expectation (CTE)

Refinamento de VaR.

**Vantagens**:
- Melhor captura de cauda pesada
- Coerente de risco
- Mais conservador

**Fórmula**:
```
RA = E[L | L > VaR_α] - E[L]
```

## Aplicação Específica - Previdência Privada

### Provisões de Previdência

Para PGBL/VGBL, IFRS 17 se aplica:

1. **Provisão de Benefício a Conceder**: RA para riscos futuros
2. **Provisão de Benefício Concedido**: RA para pensionistas
3. **Provisão de Despesas**: RA para custos administrativos

### Variáveis Críticas - Previdência

Conforme Circular SUSEP 563/21:

| Variável | Tratamento | Impacto |
|----------|-----------|--------|
| Mortalidade | Tábua calibrada | Crítico |
| Lapse | Taxa de cancelamento | Alto |
| Invalidez | Tábua de invalidez | Médio |
| Rentabilidade | Taxa de retorno | Crítico |
| Inflação | Reajuste de benefícios | Alto |

## Conformidade com BRGAAP

Normas contábeis brasileiras (BRGAAP) para seguros:

- Resolução 1 CMN: Diretrizes gerenciais
- Circular SUSEP 563/21: Mensuração de provisões
- Circular SUSEP 564/21: Divulgação IFRS 17

**Nossa Conformidade**:
- Projeção de 30 anos (alinhado com BRGAAP)
- Inclusão de todos os fluxos (prêmios, benefícios, despesas)
- Cálculo de RA separado
- Documentação completa

## Reconciliação com Práticas de Mercado

### Método de Cálculo

Consistente com:
- Normas atuariais ISA (International Actuarial Standards)
- Guidance da IFRS Foundation
- Práticas de bancos brasileiros (Itaú, BB, Caixa)

### Documentação de Conformidade

Este projeto inclui:

1. **methodology.md**: Como RA é calculado
2. **assumptions.md**: Hipóteses assumidas
3. **validation_report.md**: Testes de validação
4. **audit_trail.json**: Log de auditoria

## Períodos de Reavaliação

IFRS 17.73 exige reavaliação:

- **Anual**: Atualizar BEL e RA
- **Por mudança legislativa**: Revisar compliance
- **Por mudança estrutural**: Mercado, economia
- **No mínimo trienal**: Tábuas de mortalidade

## Divulgação (IFRS 17.119-124)

Requisitos de disclosure incluem:

1. **Natureza e efeito** de contratos de seguro
2. **Julgamentos** e incertezas em estimativas
3. **Reconciliação** de mudanças na provisão
4. **Análise de sensibilidade** de RA

---

*Documento de Conformidade IFRS 17 - v1.0*
