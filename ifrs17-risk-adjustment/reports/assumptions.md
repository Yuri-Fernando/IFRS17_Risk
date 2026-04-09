# Hipóteses e Pressupostos do Modelo

## Hipóteses Atuariais Básicas

### 1. Frequência de Sinistros

**Distribuição**: Poisson ou Binomial Negativa
**Parâmetro**: λ (taxa média)

**Hipóteses**:
- Sinistros ocorrem independentemente
- Taxa constante ao longo do período
- Eventos raros (baixa probabilidade individual)

**Justificativa**:
- Poisson é apropriado para baixas probabilidades
- Binomial Negativa captura overdispersão (variação maior que esperado)

**Limitações**:
- Assume independência (pode não valer em pandemia, desastres)
- Taxa constante (não captura tendência)

### 2. Severidade de Sinistros

**Distribuição**: Lognormal ou Gamma
**Parâmetros**: μ (média) e σ (desvio padrão)

**Hipóteses**:
- Severidade é sempre positiva
- Distribuição tem cauda longa (perdas extremas possíveis)
- Variabilidade proporcional ao valor

**Justificativa Lognormal**:
- Produto de múltiplos fatores → Log-Normal (teorema central do limite em log)
- Modelagem natural para severidade
- Cauda direita realista

**Justificativa Gamma**:
- Alternativa mais flexível
- Melhor para severidades com menos extremos
- Parâmetros mais interpretáveis (shape e scale)

### 3. Independência Freq-Sev

**Hipótese**: Número de sinistros é independente do valor de cada sinistro.

**Justificativa**:
- Geralmente válido para portfólios diversificados
- Simplifica computação

**Limitações**:
- Pode não valer em eventos catastróficos (freq ↑ sev ↓)
- Poderia ser melhorado com copulas

## Hipóteses Atuariais - Previdência

### 4. Mortalidade

**Modelo**: Lei de Gompertz ou Makeham
**Parâmetros**: Calibrados para população brasileira

**Fórmula**:
```
q_x = a × exp(b × x)
```

**Hipóteses**:
- Mortalidade aumenta exponencialmente com idade
- Diferenciais por gênero (homem > mulher)
- Tábua de mortalidade estável

**Limitações**:
- Não captura mudanças seculares (melhoria em mortalidade)
- Assume independência entre vidas

### 5. Lapse (Cancelamento de Contrato)

**Modelo**: Logístico ou Gompertz modificado
**Padrão**: Anti-seleção no início, estabilização depois, novo pico no final

**Hipóteses**:
- Taxa de cancelamento varia com duração e idade
- Sensível a mudanças econômicas
- Previsível a partir de características

**Limitações**:
- Mudanças de taxa podem causar picos inesperados
- Comportamento do cliente pode mudar

### 6. Benefícios Futuros

**Hipótese**: Benefício segue tabela contratual
**Ajustes**: Aplicados por inflação de salários/índices

**Limitações**:
- Assume cumprimento de contratos
- Não captura novas oportunidades de conversão

## Hipóteses Econômicas

### 7. Taxa de Desconto

**Valor Base**: 5.0% ao ano
**Curva**: Ligeiramente ascendente por prazo

**Hipóteses**:
- Curva estável ao longo do período de projeção
- Reflete custo de oportunidade do capital
- Mesma taxa para todos os fluxos

**Justificativa**:
- Baseada em taxa média histórica de títulos
- Inclui prêmio de risco apropriado

**Limitações**:
- Taxa está em movimento constante
- Não captura risco de taxa de juros

### 8. Inflação

**Valor Base**: 2.0% ao ano
**Aplicação**: Prêmios e despesas

**Hipóteses**:
- Inflação constante ao longo do período
- Mesma para todos os componentes

**Limitações**:
- Inflação real varia por componente
- Não captura ciclos inflacionários

## Hipóteses sobre Dados

### 9. Qualidade de Dados

**Assumido**:
- Dados completos e sem erros
- Representativos da população
- Classificação consistente

**Verificação**:
- Checagem de valores ausentes
- Validação de ranges
- Análise de outliers

### 10. Estacionariedade

**Hipótese**: Padrões históricos repetem-se no futuro

**Riscos**:
- Mudanças estruturais (legislação, economia)
- Eventos extremos não previstos
- Comportamento cliente pode mudar

## Sensibilidades Críticas

### Parâmetros de Alta Sensibilidade

| Parâmetro | Impacto | Recomendação |
|-----------|--------|--------------|
| Taxa de desconto | Crítica | Validar com BCRI |
| Frequência sinistro | Crítica | Backtesting anual |
| Severidade sinistro | Crítica | Monitorar inflação |
| Taxa de lapse | Alta | Revisar anualmente |
| Tábua mortalidade | Média | Atualizar periodicamente |

### Stress Testing Recomendado

1. Desconto: ±1% (4-6%)
2. Frequência: ×1.2, ×1.5
3. Severidade: ×1.2, ×1.5
4. Lapse: ×1.3, ×1.5

## Documentação de Mudanças

Qualquer mudança nas hipóteses deve ser:

1. Documentada com justificativa
2. Testada através de backtesting
3. Aprovada pela governança
4. Comunicada a auditoria interna/externa

---

*Documento de Hipóteses - IFRS 17 Risk Adjustment Engine v1.0*
