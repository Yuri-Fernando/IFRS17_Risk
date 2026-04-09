# Metodologia do Modelo de Risk Adjustment IFRS 17

## Objetivo

Calcular o Ajuste ao Risco (Risk Adjustment - RA) conforme IFRS 17, representando a compensação exigida pela entidade por assumir incerteza não-financeira nos fluxos de caixa de contratos de seguro.

## Definição IFRS 17

Conforme IFRS 17 seção 37A:

> O ajuste ao risco compensa a entidade por assumir incerteza não-financeira sobre as quantidades, período e incidência de fluxos de caixa futuros.

Matematicamente:

```
Provisão = Best Estimate Liability + Risk Adjustment
```

Onde:
- **BEL**: Valor presente esperado dos fluxos de caixa futuros
- **RA**: Compensação pela incerteza

## Metodologia Adotada

### 1. Decomposição Frequência-Severidade

O modelo decompõe a distribuição agregada de perdas em:

- **Frequência (N)**: Número de eventos (sinistros)
  - Distribuição: Poisson ou Binomial Negativa
  - Parâmetro: λ (lambda) - taxa média de eventos

- **Severidade (X)**: Valor de cada evento
  - Distribuição: Lognormal ou Gamma
  - Parâmetros: μ (média) e σ (desvio padrão)

**Agregação**:
```
S = X₁ + X₂ + ... + Xₙ
```

Onde S é a perda total agregada.

### 2. Simulação Monte Carlo

Simula a distribuição empírica de perdas agregadas através de:

```
Para cada cenário i = 1 até n_simulations:
  1. N_i ~ Frequência(parâmetros)
  2. Para j = 1 até N_i:
       X_ij ~ Severidade(parâmetros)
  3. S_i = Σ X_ij
```

Resultado: Array com n_simulations valores de perdas agregadas.

**Propriedades**:
- Captura dependência entre frequência e severidade
- Modela cauda da distribuição realistica
- Fornece distribuição empírica para cálculo de percentis

### 3. Cálculo do Risk Adjustment

#### Método VaR (Value at Risk)

Metodologia principal adotada.

**Fórmula**:
```
RA = VaR_α(S) - E[S]
```

Onde:
- VaR_α = percentil α da distribuição simulada (ex: 95%)
- E[S] = perda esperada (BEL)

**Interpretação**:
- RA representa a compensação pela incerteza
- Diferença entre "pior caso" e "caso médio"
- Maior α → maior RA (mais conservador)

**Vantagens**:
- Simples e transparente
- Fácil comunicação com auditoria
- Aderência às práticas de mercado
- Interpretação intuitiva

#### Método CTE (Conditional Tail Expectation)

Metodologia alternativa, mais conservadora.

**Fórmula**:
```
RA = CTE_α(S) - E[S]
CTE_α = E[S | S > VaR_α]
```

**Diferenças vs VaR**:
- Considera média da cauda, não apenas percentil
- Melhor captura eventos extremos
- Mais conservador (RA maior)
- Mais adequado para cauda pesada

#### Método Cost of Capital

Abordagem econômica alternativa.

**Fórmula**:
```
RA = Capital_Requerido × Taxa_de_Capital
```

Onde:
- Capital_Requerido = quantidade de capital para cobrir incerteza
- Taxa_de_Capital = custo marginal de capital

## Integração com BEL

O cálculo completo segue:

```
Provisão IFRS 17 = BEL + RA

BEL = Σ(t=1 a T) [E(CF_t) × DF_t]

Onde:
- CF_t: Fluxo de caixa esperado no período t
- DF_t: Fator de desconto (taxa de juros)
- T: Horizonte de projeção (30 anos)
```

### Fluxos de Caixa Atuariais

Componentes:
1. **Prêmios**: Receita futura de contratos
2. **Sinistros**: Pagamentos esperados
3. **Benefícios**: Renda vitalícia, aposentadoria
4. **Despesas**: Custos administrativos
5. **Lapse**: Cancelamento de contratos
6. **Mortalidade**: Sobrevivência de segurados

## Variáveis Críticas

Conforme IFRS 17 Art. 2 - Variáveis de Risco:

| Variável | Fonte | Impacto |
|----------|-------|--------|
| Frequência de sinistros | Dados históricos | Alta |
| Severidade de sinistros | Sinistros históricos | Alta |
| Lapse (cancelamento) | Comportamento cliente | Média |
| Mortalidade | Tábuas atuariais | Alta (vida) |
| Volatilidade | Variação periódica | Media |
| Taxa de desconto | Mercado de juros | Crítica |

## Validação do Modelo

### 1. Ajuste Estatístico

- **Teste KS**: Aderência de distribuições
- **AIC/BIC**: Seleção de modelos
- **R²**: Qualidade preditiva

### 2. Backtesting

- Comparar previsões com observado
- Teste Kupiec POF
- Teste Christoffersen

### 3. Teste de Estresse

- Aumentar frequência em 20-50%
- Aumentar severidade em 20-50%
- Aumentar lapse em 30-100%

### 4. Análise de Sensibilidade

- One-way (uma variável por vez)
- Two-way (combinações)
- Tornado (ranking de impacto)

## Propriedades Matemáticas

### Propriedade 1: Monotonicidade

RA é monotônico crescente em α:
```
RA(α₁) < RA(α₂) se α₁ < α₂
```

Mais alta a confiança, maior o RA.

### Propriedade 2: Independência de Escala

Se multiplicar todos os valores por k:
```
RA(k×S) = k × RA(S)
```

### Propriedade 3: Translação

Se adicionar constante c:
```
RA(S + c) = RA(S) + c
```

## Limitações e Ressalvas

1. **Dados Históricos**: Modelo assume que passado prediz futuro
2. **Eventos Extremos**: Pode subestimar cauda muito pesada
3. **Mudança Estrutural**: Não captura quebras estruturais
4. **Correlação**: Assume independência entre freq e sev (melhorável)
5. **Lapse**: Sensível a mudanças econômicas não capturadas

## Alinhamento Regulatório

- IFRS 17: Insurance Contracts Standard
- BRGAAP: Normas contábeis brasileiras
- Circular SUSEP 563/21: Mensuração de provisões
- Resolução 1 CMN: Diretrizes gerenciais

## Recomendações para Auditoria

1. Validar dados de entrada (histórico, completude)
2. Verificar adequação das distribuições escolhidas
3. Testar hipóteses através de backtesting
4. Realizar análise de sensibilidade
5. Documentar mudanças de metodologia
6. Revisar anualmente ou quando há mudanças estruturais

---

*Documento de Metodologia - IFRS 17 Risk Adjustment Engine v1.0*
