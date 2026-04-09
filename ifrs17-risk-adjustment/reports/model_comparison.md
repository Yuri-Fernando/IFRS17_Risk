# Comparação de Metodologias de Risk Adjustment

## Visão Geral

IFRS 17 permite múltiplas metodologias para cálculo de Risk Adjustment. Este documento compara as abordagens principais e justifica a escolha.

## 1. Value at Risk (VaR)

### Definição

O percentil de confiança da distribuição de perdas.

```
RA_VaR = VaR_α - E[L]
```

Onde VaR_α é o valor tal que P(L > VaR_α) = 1 - α.

### Vantagens

| Aspecto | Descrição |
|--------|-----------|
| Simplicidade | Fácil de calcular e comunicar |
| Transparência | Percentil é explícito e compreensível |
| Conformidade | Amplamente aceito em IFRS 17 |
| Auditoria | Facilita validação |
| Mercado | Padrão de facto em bancos |

### Desvantagens

| Aspecto | Descrição |
|--------|-----------|
| Cauda | Não captura magnitude além de VaR |
| Coerência | Pode violar subaditividade em alguns casos |
| Percentil | Sensível ao nível de confiança escolhido |
| Discretização | Depende de número de simulações |

### Exemplo Numérico

```
Distribuição de perdas (10.000 simulações):
- Média: R$ 1.000.000
- σ: R$ 500.000
- VaR_95: R$ 1.822.000
- RA = 1.822.000 - 1.000.000 = R$ 822.000
```

### Quando Usar

- Portfólios com distribuição "bem-comportada"
- Quando simplicidade é prioritária
- Comunicação com stakeholders
- Conformidade rápida

## 2. Conditional Tail Expectation (CTE)

### Definição

A média das perdas além do percentil.

```
RA_CTE = E[L | L > VaR_α] - E[L]
```

Também conhecido como Expected Shortfall ou Average Value at Risk.

### Vantagens

| Aspecto | Descrição |
|--------|-----------|
| Cauda | Captura magnitude dos eventos extremos |
| Coerência | Satisfaz axiomas de risco coerente |
| Conservador | Naturalmente mais prudente |
| Resiliência | Menos sensível a outliers |

### Desvantagens

| Aspecto | Descrição |
|--------|-----------|
| Complexidade | Mais difícil de calcular |
| Comunicação | Menos intuitivo |
| Volatilidade | Pequena amostra → estimativa instável |
| Mercado | Menos comum (ainda) |

### Exemplo Numérico

```
Mesma distribuição acima:
- Perdas além de VaR_95: [1.822, 1.850, ..., 2.500]
- Média dessas perdas: R$ 1.950.000
- RA = 1.950.000 - 1.000.000 = R$ 950.000

Diferença vs VaR: +R$ 128.000 (+15.6%)
```

### Quando Usar

- Quando cauda é importante (seguros raros)
- Mercados exigindo rigor estatístico
- Produtos de longa duração
- Reguladores (preferência crescente)

## 3. Cost of Capital (CoC)

### Definição

Capital necessário para suportar incerteza, descontado.

```
RA_CoC = Σ_t [Capital_t / (1+i)^t]

Capital_t = VaR_α(Capital Requirement no ano t)
```

### Vantagens

| Aspecto | Descrição |
|--------|-----------|
| Económico | Reflete custo real de capital |
| Consistente | Alinhado com decisões de alocação |
| Dinâmico | Varia com estrutura de capital |
| Prospectivo | Olha para frente |

### Desvantagens

| Aspecto | Descrição |
|--------|-----------|
| Complexidade | Requer projeção de capital futuro |
| Taxa | Qual taxa de desconto? |
| Parâmetros | Mais assumções necessárias |
| Calibração | Difícil calibrar |

### Fórmula Expandida

```
RA_CoC = Σ_t [MAX(0, VaR_t - BEL_t) × r] / (1+d)^t

Onde:
- VaR_t: Valor em Risco no ano t
- BEL_t: Best Estimate no ano t
- r: Taxa de custo de capital (ex: 12%)
- d: Taxa de desconto (ex: 5%)
```

### Quando Usar

- Decisões de pricing
- Alocação de capital
- Análise de rentabilidade
- Comparação com alternativas

## 4. Comparação Quantitativa

### Cenário Base

```
Portfólio:
- Prêmios anuais: R$ 10.000.000
- Sinistros esperados: R$ 8.000.000
- Despesas: R$ 1.500.000
- Horizonte: 10 anos
```

### Resultados por Método

| Método | RA Anual | RA Total (10 anos) | % de BEL |
|--------|----------|-------------------|----------|
| VaR_95 | R$ 800k | R$ 6.2M | 15% |
| CTE_95 | R$ 950k | R$ 7.4M | 18% |
| CoC_12% | R$ 1.1M | R$ 8.6M | 21% |

**Observação**: CTE e CoC são mais conservadores.

## 5. Matriz de Decisão

| Critério | VaR | CTE | CoC |
|----------|-----|-----|-----|
| Simplicidade | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| Transparência | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Rigor Estatístico | ★★★★☆ | ★★★★★ | ★★★★☆ |
| Conformidade IFRS | ★★★★★ | ★★★★★ | ★★★★★ |
| Facilidade Auditoria | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| Aceitação Mercado | ★★★★★ | ★★★☆☆ | ★★★☆☆ |
| Conservadorismo | ★★★☆☆ | ★★★★☆ | ★★★★☆ |

## 6. Recomendação - Por Caso de Uso

### Caso 1: Seguro Geral Direto
**Recomendação: VaR_95**
- Risco é bem entendido
- Distribuição é regular
- Simplicidade é chave

### Caso 2: Vida Longa / Previdência
**Recomendação: CTE_95**
- Cauda pesada é crítica
- Risco de longevidade é extremo
- Precisão é essencial

### Caso 3: Análise Econômica / Pricing
**Recomendação: CoC_12%**
- Necessário entender custo de capital
- Decisões de negócio
- Retorno on capital

### Caso 4: Portfólio Misto (Recomendado)
**Recomendação: VaR_95 Principal + CTE_95 Stress**
- VaR para conformidade
- CTE para validação
- Comparação enriquece análise

## 7. Nossa Escolha: VaR como Principal

### Justificativa

1. **Conformidade**: Amplamente aceito em IFRS 17
2. **Transparência**: Fácil comunicar com auditores
3. **Praticidade**: Implementação simples
4. **Mercado**: Padrão de facto
5. **Documentação**: Bem estabelecido

### Segurança - CTE em Stress

Complementamos com:
- Cálculo paralelo de CTE (para validação)
- Análise de diferença VaR vs CTE
- Teste de cauda pesada

### Monitoramento

Anualmente:
- Reavaliamos escolha de método
- Comparamos com reguladores
- Ajustamos se necessário

---

*Documento de Comparação Metodológica - v1.0*
