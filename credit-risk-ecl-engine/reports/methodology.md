# Metodologia — Credit Risk ECL Engine

## 1. Objetivo

Calcular a provisão para perdas esperadas de crédito (**ECL — Expected
Credit Loss**) de uma carteira de empréstimos, em conformidade com a
**IFRS 9** e a **Resolução CMN n. 4.966/2021**, decompondo o cálculo em
seus três componentes clássicos:

```
ECL = PD × LGD × EAD
```

e incorporando dependência entre segmentos de risco via simulação de
Monte Carlo com cópula — o gap mais comumente apontado em PoCs de risco
de crédito que assumem independência entre inadimplências.

## 2. Fonte de dados

Dataset **UCI Statlog German Credit Data** (Hofmann, 1994), 1.000
contratos de crédito ao consumidor, 20 variáveis explicativas e flag de
inadimplência — benchmark acadêmico consolidado para modelos de PD /
credit scoring. Ver `docs/dataset_card.md` para detalhes completos e
limitações de representatividade.

## 3. Pipeline de cálculo

### 3.1 Pré-processamento e segmentação
- Codificação ordinal de variáveis com ordem natural de risco (status da
  conta corrente, poupança, tempo de emprego).
- One-hot encoding das demais variáveis categóricas.
- Segmentação da carteira em 4 macro-segmentos por finalidade do crédito
  (veículos, bens de consumo, PJ capital de giro, pessoal) — necessária
  para a modelagem de correlação (Seção 3.5).

### 3.2 Modelagem de PD (Probability of Default)
Dois modelos são treinados e comparados:

| Modelo | Papel | Racional |
|---|---|---|
| Regressão Logística | Champion (referência regulatória) | Interpretável, coeficientes auditáveis, exigido para explicabilidade em modelos de crédito |
| Gradient Boosting | Challenger | Captura não-linearidades; usado para avaliar ganho de poder discriminante |

O modelo campeão é selecionado pelo maior **Gini** no conjunto de teste
(ver `reports/model_comparison.md`).

### 3.3 Staging IFRS 9 (SICR)
Cada contrato é classificado em Stage 1, 2 ou 3 conforme a deterioração
do risco desde a originação (Significant Increase in Credit Risk):

- **Stage 1**: PD atual < 2× PD de originação **e** PD atual < 20% → ECL 12 meses.
- **Stage 2**: deterioração relativa ou absoluta de risco, sem default → ECL lifetime.
- **Stage 3**: contrato inadimplente (evidência objetiva de perda) → ECL lifetime, PD = 100%.

A PD lifetime é extrapolada da PD 12 meses assumindo hazard rate
constante:

```
PD_lifetime = 1 - (1 - PD_12m) ^ (prazo_meses / 12)
```

### 3.4 LGD e EAD
- **LGD**: modelada por segmento de garantia/colateral (`property`),
  amostrada de uma distribuição Beta calibrada por média e desvio-padrão
  específicos do tipo de garantia (imóvel < seguro/poupança vinculada <
  veículo/outro < sem garantia, em ordem crescente de severidade).
- **EAD**: saldo devedor remanescente (valor do crédito × fração do
  prazo não decorrida), com Credit Conversion Factor aplicável a limites
  não totalmente desembolsados (CCF = 1 neste PoC, produto sem limite
  rotativo).

### 3.5 Correlação entre segmentos — simulação por cópula Gaussiana
Ponto central deste projeto: em vez de somar `PD × LGD × EAD` contrato a
contrato assumindo independência (o que subestima risco de cauda), o
motor de simulação:

1. Sorteia choques sistêmicos correlacionados entre os 4 segmentos via
   cópula Gaussiana, com matriz de correlação parametrizável.
2. Aplica a fórmula de mistura de Vasicek (base do modelo IRB de
   Basileia) para deslocar a PD de cada contrato conforme o choque do
   seu segmento e a correlação de ativos (ρ).
3. Simula o default de cada contrato via Bernoulli(PD ajustada) e agrega
   a perda do cenário.
4. Repete N vezes → distribuição de perda agregada, da qual se extraem
   **VaR** e **CVaR (Expected Shortfall)**.

O "benefício de diversificação" reportado é a diferença entre a soma das
ECLs individuais (hipótese de independência) e a perda esperada simulada
(com correlação) — quantifica o quanto a hipótese de independência
subestimaria ou superestimaria o risco.

### 3.6 Validação
- **Gini / KS / AUC**: poder discriminante do modelo de PD.
- **PSI**: estabilidade da distribuição de PD entre treino e teste.
- **Calibração**: comparação PD prevista vs. taxa de default observada,
  por decil de score.
- **Backtesting (Kupiec/POF)**: teste estatístico formal por stage.

### 3.7 Stress testing
Recalcula a ECL sob 3 choques macroeconômicos (moderado, severo,
extremo), combinando aumento de PD e LGD downturn add-on — ver
`reports/model_comparison.md` para os resultados numéricos gerados na
última execução.

## 4. Rastreabilidade e governança
Cada execução do pipeline gera uma trilha de auditoria completa
(`src/governance/audit_log.py`) e um identificador de versão do modelo
determinístico (`src/governance/model_versioning.py`), permitindo
reconstituir exatamente qual configuração produziu qual número de
provisão — ver `reports/audit_trail.md`.
