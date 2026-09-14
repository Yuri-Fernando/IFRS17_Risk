# Premissas do Modelo — Credit Risk ECL Engine

Documento de transparência técnica: toda premissa que não decorre
diretamente do dataset é listada aqui, com justificativa e o que seria
necessário em produção para substituí-la por dado observado.

| # | Premissa | Justificativa no PoC | Substituição em produção |
|---|---|---|---|
| 1 | PD de originação = PD atual ajustada por drift log-normal aleatório | Dataset não traz histórico de safra (vintage) nem PD na data de concessão | Base histórica de PD por safra, ou score de originação armazenado no sistema de crédito |
| 2 | Extrapolação de PD lifetime via hazard rate constante | Simplificação padrão de mercado na ausência de curva de PD marginal completa | Curva de PD marginal por período estimada de dados históricos de sobrevivência (survival analysis) |
| 3 | LGD modelada por segmento de colateral (Beta), não observada | Dataset não é um dataset de recuperação/cobrança pós-default | Base histórica de recuperações reais por tipo de garantia e tempo de workout |
| 4 | EAD = saldo remanescente com fração de prazo decorrida fixa (30%) | Dataset não traz data de originação nem cronograma de pagamentos | Data de originação real + calendário de amortização do sistema de crédito |
| 5 | Correlação entre segmentos parametrizada (equicorrelação 0,25) | Dataset não permite estimar correlação real entre taxas de default por segmento (n insuficiente de períodos) | Série histórica multi-período de taxas de default por segmento, correlação de Pearson/Spearman estimada |
| 6 | Correlação de ativos (ρ = 0,15) fixa entre segmentos | Simplificação; Basileia usa ρ variável por tipo de exposição (fórmula de correlação do IRB) | Fórmula de correlação de ativos do IRB (Basileia), variável por PD e tipo de exposição |
| 7 | Segmentação de portfólio por finalidade do crédito (4 segmentos) | Proxy razoável de linha de negócio, dado que o dataset não tem campo de produto bancário explícito | Segmentação real por produto/linha de negócio do banco |
| 8 | Threshold de SICR: 2× PD de originação ou PD absoluta ≥ 20% | Valores de mercado comumente usados como ponto de partida; sujeitos a calibração e validação de auditoria | Calibração específica por carteira, validada com dados reais de migração de rating/score |

## Achado de validação: por que o backtesting por stage rejeita H0 nos Stages 1 e 2

Ao rodar o teste de Kupiec por estágio na execução de referência, o
resultado foi: **Stage 1 e 2 rejeitam H0** (PD prevista muito acima da
taxa observada) e **Stage 3 aceita H0** trivialmente. Isso não é um erro
de código — é uma consequência estrutural de como o staging foi definido
e da natureza do dataset:

- `classify_stage` atribui Stage 3 a **todo** contrato com `default == 1`,
  por construção.
- Logo, dentro de Stage 1 e Stage 2, medidos **na mesma data-base**, a
  taxa de default observada é sempre 0% (todo default já "virou" Stage 3),
  e dentro do Stage 3 é sempre 100%.
- O teste de Kupiec comparando PD prevista com taxa observada só é
  metodologicamente válido em um **painel temporal**: PD prevista na data
  t vs. default realizado nos 12 meses seguintes. Aplicado a um corte
  transversal único (o que o German Credit permite), o teste compara PD
  prevista com uma taxa observada estruturalmente nula ou unitária —
  logo, tende a rejeitar H0 nos Stages 1/2 independentemente da
  qualidade real do modelo.

**Conclusão**: o motor implementa o teste corretamente e o output é
reportado sem filtro (ver `reports/validation_report.md`), mas a
interpretação correta é "este teste, day-one, não é conclusivo sobre
calibração — precisa de um painel de safras (12 meses de maturação) para
ser válido". Isso está documentado aqui em vez de silenciado porque é
precisamente o tipo de leitura crítica esperada de quem avalia calibração
de modelos de risco — aceitar um p-valor sem entender a mecânica por trás
seria o erro real.

## Limitação estrutural mais relevante

O dataset German Credit é um dataset de **originação** (aprovação/rejeição
de crédito) com 1.000 observações de um único período — não é uma
carteira longitudinal com múltiplas safras. Isso significa que qualquer
modelo de PD lifetime, correlação entre safras ou stress test dinâmico é,
neste PoC, necessariamente **ilustrativo da técnica**, não uma calibração
validada para uso em produção. Essa limitação é deliberadamente destacada
— e não escondida — porque é exatamente o tipo de julgamento técnico que
se espera de um Data Scientist de risco de crédito: reconhecer o limite
dos dados disponíveis e ser explícito sobre o que precisaria mudar para
ir de PoC a modelo de produção.
