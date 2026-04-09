# Relatório de Validação do Modelo

## Objetivo

Documentar rigorosamente que modelo está estatisticamente válido e pronto para uso operacional.

## 1. Validação de Distribuições

### Teste KS (Kolmogorov-Smirnov)

Testa se dados seguem distribuição teórica.

**Hipóteses**:
- H0: Dados seguem distribuição
- H1: Dados não seguem distribuição

**Resultado Esperado**: p-value > 0.05 (não rejeita H0)

### Teste Shapiro-Wilk (Normalidade)

Para variáveis normalizadas.

**Resultado Esperado**: p-value > 0.05

### Teste Jarque-Bera

Testa normalidade via assimetria e curtose.

**Métricas**:
- Skewness: próximo a 0 (simétrico)
- Kurtosis: próximo a 0 (normal)

## 2. Validação de Modelos Estatísticos

### AIC / BIC (Seleção de Modelo)

Compara Poisson vs Binomial Negativa.

**Critério**: Menor AIC/BIC é melhor

```
AIC = 2k - 2ln(L)
BIC = k×ln(n) - 2ln(L)

Onde:
k = número de parâmetros
n = número de observações
L = máxima verossimilhança
```

### Índice de Dispersão (Poisson)

```
ID = Variância / Média

Se ID ≈ 1: Poisson é apropriado
Se ID > 1.5: Use Binomial Negativa (overdispersão)
```

## 3. Validação Preditiva

### Métricas de Erro

| Métrica | Fórmula | Interpretação |
|---------|---------|----------------|
| RMSE | √(mean(error²)) | Penaliza erros grandes |
| MAE | mean(\|error\|) | Erro absoluto médio |
| MAPE | mean(\|error\|/y)*100 | Erro em % |
| R² | 1 - SS_res/SS_tot | Variância explicada |

**Critérios de Aceitação**:
- MAPE < 15%: Bom
- MAPE < 20%: Aceitável
- R² > 0.70: Bom

### Teste de Resíduos

Resíduos devem ser:
- Independentes (sem padrão temporal)
- Normalmente distribuídos
- Com média zero
- Homocedasticidade (variância constante)

## 4. Backtesting

### Teste Kupiec POF (Proportion of Failures)

Valida se VaR está bem calibrado.

**Lógica**:
Se VaR_95 for correto, esperamos que perda real > VaR em ~5% das vezes.

**Estatística**:
```
N = número de exceções observado
n = número de observações

Se N/n ≈ 0.05: VaR é adequado
```

### Teste Christoffersen

Combina:
1. Teste de frequência (POF)
2. Teste de independência (série de exceções)

**Conclusão**: "VaR válido" ou "VaR inválido"

## 5. Teste de Estresse

### Cenário 1: Aumento de Frequência

```
Frequência base: 15%
Stress +20%: 18%
Stress +50%: 22.5%

Impacto esperado: RA aumenta proporcionalmente
```

### Cenário 2: Aumento de Severidade

```
Severidade base: μ=9, σ=1.5
Stress +20%: μ=10.8, σ=1.8
Stress +50%: μ=13.5, σ=2.25

Impacto esperado: RA aumenta mais que linearmente
```

### Cenário 3: Aumento de Lapse

```
Lapse base: 8%
Stress +30%: 10.4%
Stress +50%: 12%

Impacto esperado: RA reduz (menos segurados)
```

### Resultado Esperado

Modelo é robusto se:
- Resposta aos stresses é previsível
- Não há comportamento não-linear inesperado
- Impactos são economicamente razoáveis

## 6. Análise de Sensibilidade

### One-Way Sensitivity

Varia um parâmetro, mantém outros fixos.

**Parâmetros Críticos**:
1. Taxa de desconto (±1%)
2. Frequência (×1.2, ×1.5)
3. Severidade (×1.2, ×1.5)
4. Lapse (×1.3, ×1.5)

**Representação**: Tornado Chart

Parâmetros com maior amplitude de impacto são mais críticos.

### Two-Way Sensitivity

Varia dois parâmetros simultaneamente.

**Exemplo**: Freq vs Sev (tabela 10×10)

Identifica se há interações importantes.

## 7. Validação de Suposições

### Independência Freq-Sev

**Teste**: Correlação entre N e X

```
Se corr < 0.1: Independência razoável
Se corr > 0.3: Rever modelo (possível copula)
```

### Estacionariedade

Dados históricos reproduzem padrão?

**Teste**: Comparar períodos diferentes
- 2019-2021
- 2021-2023

Se padrões divergem: hipótese quebrada

### Normatividade de Dados

Dados são reais, livres de erros?

**Checklist**:
- [ ] Sem valores ausentes
- [ ] Sem duplicatas
- [ ] Valores dentro de ranges esperados
- [ ] Sem padrões suspeitos

## 8. Consistência Temporal

### Teste Estatístico

Roda modelo em períodos diferentes. Resultados devem ser:
- Similares (mesma ordem de magnitude)
- Estáveis (sem picos inesperados)
- Consistentes (mesmo padrão)

## 9. Convergência de Monte Carlo

Quanto maior n_simulations, mais estável o resultado.

**Teste**:
```
n=1000:   RA = 850k
n=5000:   RA = 822k
n=10000:  RA = 820k
n=50000:  RA = 819k
```

Se estabiliza: 10k simulações é suficiente

**Critério**: Mudança < 1% entre 10k e 50k = aceito

## 10. Validação Final - Checklist

Modelo está aprovado se:

- [ ] KS test p-value > 0.05 (aderência de distribuição)
- [ ] MAPE < 20% (acurácia preditiva)
- [ ] R² > 0.70 (variância explicada)
- [ ] Backtesting Kupiec válido (VaR calibrado)
- [ ] Stress tests são razoáveis (sem anomalias)
- [ ] Sensibilidade é compreendida (documentada)
- [ ] Convergência MC é atingida (n=10k é suficiente)
- [ ] Dados foram validados (qualidade confirmada)
- [ ] Auditoria interna aprova (documentado)

**Se todos passam**: Modelo pronto para produção

---

*Relatório de Validação - IFRS 17 Risk Adjustment Engine v1.0*
