# Explicação do Modelo (Para Não-Técnicos)

## O que é este modelo?

Este é um modelo matemático que calcula quanto de dinheiro um banco deve "guardar" hoje para cobrir riscos futuros em contratos de seguro.

## Por que precisamos?

A norma contábil IFRS 17 exige que bancos e seguradoras reportem provisões (reservas) baseadas em:
1. O valor esperado das perdas
2. Um "extra" para cobrir incerteza

## Analogia Simples

Imagine uma corretora de seguros com 10.000 apólices:

- Cada apólice deve gerar ~1 sinistro a cada 7 anos
- Quando há sinistro, valor é em torno de R$ 1.000, mas pode variar bastante
- Alguns anos terão 10 sinistros, outros terão 200

A pergunta é: **Quanto o banco precisa reservar hoje?**

### Resposta em 3 Partes

1. **Best Estimate**: Valor esperado (provável)
   - "Baseado em histórico, esperamos perder R$ 1.5M/ano"

2. **Risk Adjustment**: Compensação pela incerteza
   - "Mas pode ser R$ 2M em ano ruim"
   - "Então guardamos R$ 500k extra para estar seguro"

3. **Total de Provisão** = R$ 1.5M + R$ 500k = R$ 2.0M

## Como o Modelo Funciona

### Etapa 1: Análise de Histórico

Olha para dados passados:
- Quantos sinistros por mês?
- Qual o valor médio?
- Qual a variação?

### Etapa 2: Modelagem Estatística

Escolhe distribuições matemáticas que descrevem bem os dados:
- **Frequência**: Quantas vezes acontece (modelo Poisson)
- **Severidade**: Quanto custa cada uma (modelo Lognormal)

### Etapa 3: Simulação

Simula 10.000 cenários futuros:
- "E se este ano tivermos 150 sinistros?"
- "E se a inflação disparar e cada sinistro custar mais?"
- "Qual será a perda total?"

Result: 10.000 cenários de perda total

### Etapa 4: Risk Adjustment

Olha os 10.000 cenários:
- Cenário melhor: R$ 500k de perda
- Cenário médio: R$ 1.5M de perda
- Cenário pior (95º percentil): R$ 2.0M de perda

**Risk Adjustment = R$ 2.0M - R$ 1.5M = R$ 500k**

## Validação: "Será que o Modelo Está Correto?"

Fazemos testes para verificar:

### Teste 1: Aderência Estatística
Verificamos se as distribuições escolhidas descrevem bem os dados.
(Resultado: sim, passamos)

### Teste 2: Backtesting
Vemos o modelo previu bem no passado?
(Resultado: acurou dentro de 15%, aceitável)

### Teste 3: Estresse
"E se tudo piorar?" Aumentamos frequência +50%, severidade +50%
(Resultado: modelo responde como esperado)

### Teste 4: Sensibilidade
"Qual parâmetro mais afeta o resultado?"
(Resultado: Taxa de desconto é o mais crítico)

## Transparência e Auditoria

Todo cálculo é **rastreável**:
- Data exata do cálculo
- Versão do modelo
- Dataset usado
- Quem executou
- Todos os resultados intermediários

Isso permite auditores (internos e externos) verificarem se está correto.

## Conformidade Regulatória

Este modelo segue:
- IFRS 17 (padrão contábil internacional)
- Normas brasileiras (SUSEP, BACEN)
- Boas práticas de mercado

## Exemplos de Uso

### Exemplo 1: Portfólio de Seguros Gerais
```
Prêmios anuais: R$ 100M
Sinistros esperados: R$ 70M
Despesas: R$ 15M
BEL: R$ 15M (margem esperada)
RA: R$ 3M (incerteza)
Provisão Total: R$ 18M
```

### Exemplo 2: Previdência
```
Benefícios futuros: R$ 500M (valor presente)
RA para risco longevidade: R$ 50M
RA para risco lapse: R$ 30M
Provisão Total: R$ 580M
```

## Mudanças Periódicas

O modelo é revisado:
- **Anualmente**: Com novos dados
- **Quando há lei nova**: Ajusta conformidade
- **Se mercado muda**: Recalibra parâmetros

Qualquer mudança é documentada e aprovada.

## Perguntas Frequentes

**P: Pode o modelo errar?**
R: Sim, como todo modelo matemático. Por isso fazemos muitos testes antes de usar.

**P: Por que não simplificar?**
R: Porque precisamos estar bem calibrados. Reguladores e auditores exigem rigor.

**P: O resultado é determinístico?**
R: Não, ele pode variar conforme dados novos chegam. Por isso revisamos anualmente.

**P: Quem aprova o resultado?**
R: Auditoria Interna, Risco e Conformidade revisam antes de publicar.

---

*Para técnicos, veja methodology.md e assumptions.md*
