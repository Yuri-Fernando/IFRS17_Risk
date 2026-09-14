# O que este projeto faz (em linguagem de negócio)

## O problema

Todo banco que empresta dinheiro sabe que uma parte dos tomadores não vai
pagar. A norma contábil **IFRS 9** (e, no Brasil, a **Resolução CMN
4.966/2021**) obriga o banco a reservar, no seu balanço, o valor que
espera perder com essa inadimplência — **antes** dela acontecer. Essa
reserva se chama **ECL (Expected Credit Loss)**, ou Perda Esperada.

Calcular esse número certo importa por três motivos:
1. **Regulatório**: provisão insuficiente é não-conformidade contábil e
   pode gerar sanção do BACEN/CVM.
2. **Financeiro**: provisão excessiva trava capital que poderia estar
   gerando receita; provisão insuficiente expõe o banco a perdas não
   antecipadas.
3. **Estratégico**: entender onde a carteira concentra risco orienta
   decisões de política de crédito, precificação e apetite ao risco —
   exatamente o tipo de "estudo estratégico para redução e otimização do
   custo de crédito" esperado de um Data Scientist de risco.

## Como o modelo resolve isso

A perda esperada de cada contrato de crédito é decomposta em três
perguntas:

| Pergunta | Componente | Exemplo |
|---|---|---|
| Qual a chance desse cliente não pagar? | **PD** (Probability of Default) | 5% ao ano |
| Se ele não pagar, quanto eu recupero? | **LGD** (Loss Given Default) | Recupero 60% via garantia → perco 40% |
| Quanto eu tenho exposto quando ele não paga? | **EAD** (Exposure at Default) | R$ 10.000 de saldo devedor |

Perda esperada do contrato = PD × LGD × EAD.

Somando isso para toda a carteira, chegamos ao valor da provisão. Mas há
um detalhe importante: **inadimplências não são independentes entre si**.
Numa crise, o desemprego sobe e vários segmentos de clientes ficam
inadimplentes ao mesmo tempo. Ignorar essa correlação é um erro comum e é
justamente o gap que este projeto resolve, simulando milhares de
cenários econômicos correlacionados (via cópulas) para capturar não só a
perda média esperada, mas também o **risco de cauda** — quanto o banco
poderia perder num cenário realmente ruim (VaR / CVaR).

## O que o motor entrega

1. **Provisão contábil (ECL)** segmentada pelos 3 estágios da IFRS 9 —
   quanto está "normal" (Stage 1), quanto já deteriorou mas não default
   ainda (Stage 2) e quanto já é prejuízo reconhecido (Stage 3).
2. **Medidas de risco de cauda** (VaR 99,9%, CVaR) — usadas para
   dimensionar capital econômico, além da provisão contábil.
3. **Testes de estresse**: "se o desemprego subir e a inadimplência
   aumentar 80%, quanto a provisão sobe?" — resposta imediata, com número.
4. **Validação estatística formal**: o modelo é auditável — qualquer
   analista, auditor ou regulador pode verificar se a PD prevista bate
   com a taxa de default real observada.

## Para quem serve este projeto (contexto de portfólio)

Este PoC foi desenhado para demonstrar competências diretamente
alinhadas a uma posição de Data Scientist em Gerenciamento de Riscos
Financeiros / Risco de Crédito em banco: modelagem de PD/LGD/EAD,
metodologias de perda esperada, staging IFRS 9, validação e backtesting
de modelos regulatórios, e a capacidade de identificar e endereçar
lacunas metodológicas (correlação entre riscos) de forma proativa — não
apenas executar um cálculo, mas justificar cada premissa como faria uma
área de Modelagem/Validação de um banco.
