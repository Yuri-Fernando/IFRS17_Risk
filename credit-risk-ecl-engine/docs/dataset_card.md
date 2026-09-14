# Dataset Card — German Credit Data

## Origem

- **Nome**: Statlog (German Credit Data)
- **Autor**: Prof. Dr. Hans Hofmann, Universität Hamburg (1994)
- **Repositório oficial**: UCI Machine Learning Repository — https://archive.ics.uci.edu/dataset/144
- **Espelho usado no download automatizado** (colunas nomeadas, mesmo
  conteúdo): https://raw.githubusercontent.com/selva86/datasets/master/GermanCredit.csv
- **Licença**: domínio público / uso acadêmico livre (UCI ML Repository)

## Estrutura

- 1.000 contratos de crédito ao consumidor concedidos por um banco alemão
- 20 variáveis explicativas (status de conta corrente, histórico de
  crédito, finalidade, valor, poupança, tempo de emprego, idade, tipo de
  garantia, etc.)
- 1 variável-alvo: qualidade de crédito (bom/mau pagador)
- Taxa de "mau pagador" na amostra original: 30% (300/1.000) — taxa
  elevada por desenho amostral (dataset balanceado para fins didáticos,
  não representa a taxa de inadimplência real de um banco, tipicamente
  de 1 dígito percentual)

## Convenção de target usada neste projeto

O dataset original usa `credit_risk = 1` para bom pagador. Neste projeto,
invertemos a convenção para `default = 1` (inadimplente), que é o padrão
de mercado em modelagem de PD/ECL — ver `src/data/load_data.py`.

## Por que este dataset para um PoC de risco de crédito bancário

- É um benchmark acadêmico amplamente reconhecido, com estrutura de
  dados equivalente à de um dataset real de originação de crédito
  (variáveis demográficas, financeiras e de garantia).
- Permite demonstrar a técnica completa (PD, staging, LGD por colateral,
  EAD, ECL, correlação, validação, backtesting) sem depender de dados
  proprietários de instituição financeira.
- É citado com frequência em literatura de credit scoring e machine
  learning aplicado a crédito, facilitando comparação com benchmarks
  publicados.

## Limitações conhecidas (ver também `reports/assumptions.md`)

1. **Amostra de corte transversal única** — não há múltiplas safras
   (vintages), o que limita a validação de PD lifetime e de correlação
   temporal entre segmentos a um exercício ilustrativo.
2. **Taxa de default de 30%** não é representativa de carteiras bancárias
   reais (tipicamente 1-5%); métricas absolutas de provisão devem ser
   lidas como demonstração metodológica, não como benchmark de mercado.
3. **Ausência de dados de recuperação pós-default** — LGD é estimada por
   proxy de colateral, não observada diretamente.
4. **Sem data de originação real** — EAD e o "tempo decorrido" do
   contrato são aproximados.
5. **Variáveis codificadas para o contexto alemão dos anos 1990** (ex.:
   valores em Deutsche Mark) — tratadas neste projeto como valores
   monetários genéricos, sem conversão cambial ou correção temporal.

## Fallback sintético

O pipeline também oferece geração de uma carteira sintética
(`--data-source synthetic`) com a mesma estrutura de colunas, útil para
execução sem dependência de internet ou para testes de sensibilidade a
diferentes distribuições de risco.
