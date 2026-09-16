# Metodologia Mestre — Ajuste ao Risco (AR) sob IFRS 17 para Previdência e Benefícios de Risco

> **Documento de registro técnico.** Consolida a metodologia atuarial desenvolvida ao longo de ~4 meses de trabalho (bolsa/estágio atuarial em instituição financeira, previdência complementar aberta), cobrindo produtos de Previdência (longevidade, resgate) e Benefícios de Risco (Peculio, Pensão por Morte, Renda por Invalidez, Pensão ao Menor).
>
> **O que este documento contém:** lógica, fórmulas, decisões metodológicas, evolução do raciocínio, arquitetura técnica, gaps em aberto e referências externas.
> **O que este documento NÃO contém, por decisão deliberada:** números, volumes, valores monetários ou resultados numéricos específicos da carteira real da instituição (expostos, sinistros, capital segurado, percentuais de A/E, fatores de stress calculados etc.). Esses dados são confidenciais e não são reproduzidos aqui nem em nenhum artefato público. A pessoa responsável pelo estudo é identificada como "Yuri" (autor); demais colegas são referidos apenas pelo papel funcional (orientador, atuária de dados, área de modelagem etc.), nunca por nome.
>
> **Uso pretendido:** este documento é a base para reconstruir e completar a metodologia em um projeto de portfólio público, usando dados sintéticos/públicos (tábuas oficiais BR-EMS, AT-2000, PRSSVBR, SUSEP) em vez dos dados reais da carteira.

---

## Changelog deste documento

| Versão | Data | Mudança |
|---|---|---|
| 1.0 | 2026-09-16 | Criação. Consolidação de todo o material das reuniões R4–R15, estudos metodológicos (v1/v2), memorando técnico R8 e apresentações HTML em um único documento mestre. |

---

## 1. Contexto e Objetivo

Yuri atuou como bolsista/estagiário atuarial na área de Previdência de uma instituição financeira, com a missão de desenvolver a metodologia e a implementação do **Ajuste ao Risco (AR / Risk Adjustment)** sob o **IFRS 17**, aplicável a:

- **Previdência Complementar Aberta** (produto de referência: FGBPJ — plano gerador de benefício, tradicional): risco de **longevidade** (fase de renda) e **resgate/lapse** (fase de acumulação).
- **Benefícios de Risco** (produtos sem acumulação de saldo, prêmio mensal contra evento):
  - **Peculio** — pagamento único (*lump sum*) ao beneficiário em caso de morte do segurado;
  - **Pensão por Morte** — renda mensal contínua ao beneficiário após óbito do segurado;
  - **Renda por Invalidez (PMBC)** — renda mensal ao próprio segurado em caso de invalidez;
  - **Pensão ao Menor** — variante da pensão por morte, paga a dependente menor até a maioridade.

O trabalho terminou de forma incompleta: Yuri foi desligado antes de formalizar a metodologia final e rodar o cálculo com a carteira completa. Este documento reconstitui, de forma coerente e rastreável, tudo que foi desenvolvido — para ser completado como projeto de portfólio.

### 1.1 O problema de fundo (IFRS 17 §37)

> *"O Ajuste ao Risco é a compensação que a entidade requer por suportar a incerteza sobre o valor e o prazo dos fluxos de caixa decorrentes de risco não financeiro."*

O passivo de um contrato de seguro/previdência sob IFRS 17 se decompõe em três blocos:

```
Passivo Total = BEL + AR + CSM
```

- **BEL (Best Estimate Liabilities):** valor presente dos fluxos futuros pela melhor estimativa das premissas (tábua de mortalidade base, resgate histórico, conversão em renda).
- **AR (Ajuste ao Risco):** colchão adicional pela incerteza biométrica e comportamental — o objeto deste estudo.
- **CSM (Contractual Service Margin):** lucro futuro ainda não reconhecido.

**A relação crítica AR ↔ CSM:** na mensuração inicial de um contrato lucrativo, `CSM₀ = Prêmio₀ − BEL₀ − AR₀`. Logo, **todo aumento no AR reduz o CSM na mesma proporção**, diminuindo a margem futura reconhecida no P&L ao longo de toda a vida do contrato. Se a mudança de AR afeta serviço futuro, absorve no CSM (sem impacto imediato no resultado); se afeta serviço passado ou torna o contrato oneroso (BEL + AR > Prêmio), vai direto ao P&L como perda no exercício. Por isso a calibração do AR não é um exercício estatístico neutro — é uma decisão de política de reconhecimento de resultado, e precisa de embasamento rigoroso e auditável.

A norma **não prescreve uma técnica específica**, mas exige:
1. Maximizar o uso de informação observável;
2. Divulgar obrigatoriamente o **nível de confiança equivalente**, mesmo que a técnica usada não seja diretamente um intervalo de confiança;
3. Refletir o benefício de diversificação entre riscos do portfólio.

---

## 2. Linha do Tempo — Evolução da Metodologia

A metodologia não nasceu pronta; evoluiu por atrito construtivo entre a proposta conceitual de Yuri e as exigências de rastreabilidade da equipe de dados/atuária e do orientador. Esta seção documenta essa evolução, reunião a reunião, sem números de carteira — só decisões e mudanças de rumo.

### Fase 1 — Formulação conceitual (reuniões iniciais)

- Estrutura do passivo IFRS 17 apresentada e validada: BEL + AR + CSM.
- Primeira proposta de metodologia: **Intervalo de Confiança (percentil)**, não Custo do Capital — decisão fundamentada em benchmarking internacional (ver seção 7) e na simplicidade de comunicação para um público não estritamente atuarial.
- Percentil-alvo inicial proposto: faixa 75%–90% (não 99,5% do padrão Solvency II — destruiria o CSM ao ser conservador demais para um produto de longa duração).
- Abordagem inicial: A/E ratio por célula (idade × sexo × ano) → percentil da distribuição dos desvios → fator de stress → `qx_stress = fator × qx_base` → `AR = VPL(stress) − VPL(BEL)`.
- Definição das "caixinhas": um componente de risco por vez (mortalidade/Peculio, longevidade, invalidez, resgate), somados de forma simples numa primeira fase (sem desconto de correlação/diversificação).
- Levantado o **gap de escala**: uma planilha de referência da atuária de dados continha a lógica completa de BEL/AR/CSM, mas validada para apenas 1 segurado. A base real da carteira tem milhões de segurados, exigindo migração das fórmulas de Excel para módulos Python vetorizados (pandas/numpy) rodando sobre a infraestrutura AWS (Athena + S3).
- Identificado passo faltante: **credibility testing** — antes de calibrar o A/E por célula, verificar se cada célula tem exposição suficiente (regra de bolso usada: milhares de expostos). Se não, aplicar **credibility de Bühlmann**: `fator = Z × A/E_interno + (1−Z) × A/E_mercado`, onde Z cresce com o volume de expostos da célula.

### Fase 2 — Explicação de produto e ampliação de escopo (reunião de alinhamento operacional)

- O orientador explicou em detalhe a diferença entre **Previdência "planejada"** (acumulação de saldo) e **Benefícios de Risco** (prêmio mensal contra evento, sem acumulação): Renda por Invalidez, Pensão por Morte, Peculio, Pensão ao Menor.
- Provisões técnicas relevantes mapeadas: PPNG (prêmios não ganhos), PSL (sinistros a liquidar/avisados), IBNR (sinistros ocorridos e não reportados), PMBC (provisão matemática de benefícios concedidos, ex.: invalidez em fase de renda).
- **Decisão de escopo:** o Peculio entra no estudo — e de forma particular, porque **já possui um percentual de AR aplicado hoje**; o trabalho ali não é calcular do zero, é *auditar/recalibrar* o percentual vigente.
- Dinâmica de trabalho definida pela equipe de dados: o fluxo é *Yuri define a variável necessária → equipe aponta onde encontrar na AWS → Yuri acessa e modela* (não o inverso — a equipe não entrega dados sem saber exatamente o que serão usados para calcular).
- Ferramentas discutidas em ordem crescente de complexidade: AWS Glue (exploração ponto-e-clique) → VS Code + boto3/Athena (scripts repetíveis, preferência de Yuri) → SageMaker (reservado para caso surgisse necessidade de ML, o que nunca se confirmou necessário nesta fase).

### Fase 3 — Reorientação metodológica (checkpoint com o orientador principal)

Após um hiato de reuniões, o orientador principal reorientou a abordagem operacional (mantendo a lógica conceitual de percentil), com um framework mais direto, partindo da **sinistralidade** em vez de partir só do A/E:

```
Passo 1 — Definir os riscos não financeiros relevantes (morte, invalidez, lapse, longevidade)
Passo 2 — Sinistralidade = volume de sinistros / prêmio, no componente mais simples primeiro
Passo 3 — Calcular a média histórica dessa sinistralidade → alimenta a projeção (BEL)
Passo 4 — Medir a incerteza em torno dessa média → essa incerteza é o Ajuste ao Risco
Passo 5 — Identificar a distribuição estatística dos dados (teste de aderência)
Passo 6 — Com a distribuição confirmada, aplicar intervalo de confiança (percentil) → AR
```

Ponto de atenção explícito do orientador: uma área parceira dentro da mesma instituição já havia desenvolvido um estudo similar (reamostragem + N simulações) — o trabalho de Yuri deveria **complementar**, não duplicar esse esforço.

Também nesta fase foi enfatizada, de forma recorrente, a exigência de **rastreabilidade de toda escolha metodológica** (percentil, janela histórica, distribuição escolhida) com **fonte documentada** — motivada pelo fato de que o resultado seria escrutinado por múltiplas camadas dentro do banco (auditoria interna, auditoria externa, área de modelagem estatística).

O orientador também deu um retorno de postura de trabalho, além do técnico: a expectativa era que Yuri chegasse às reuniões com iniciativa própria — leituras adicionais, testes alternativos não solicitados, dúvidas técnicas próprias já parcialmente investigadas — não apenas executando literalmente o que fora pedido na reunião anterior.

### Fase 4 — Início do trabalho por componente: Peculio primeiro (dados reais)

- **Decisão de sequenciamento confirmada:** Mortalidade/Peculio → Longevidade → Invalidez → Resgate. Peculio priorizado porque é o único componente onde o valor do sinistro (pagamento único) já vem completo na base de dados, sem necessidade de cálculo intermediário de valor presente de renda (diferente de Pensão, Invalidez e Pensão ao Menor, que pagam renda mensal e exigem VPL da anuidade).
- Estrutura de dados esclarecida: existem duas bases relacionadas por uma chave composta (produto + plano + tipo de cobertura + competência/mês):
  - **Base de Expostos (Acessórios):** carteira ativa — denominador do A/E e da sinistralidade (exposição, prêmio/contribuição, capital segurado).
  - **Base de Sinistros/Concedidos:** eventos pagos — numerador do A/E (mortes, valor pago, data de ocorrência vs. data de aviso — este lag é a base do cálculo de IBNR).
  - Uma terceira base de **Resgates/Lapse** foi identificada como necessária mas nunca chegou a ser disponibilizada — permanece como gap até o desligamento de Yuri.
- Identificado campo de papel contratual (titular vs. cônjuge/beneficiário vs. filho/segundo beneficiário) — para cálculo de morte no componente de risco, usar apenas o registro do titular.
- Regra de ouro para lidar com bloqueio de dados: **construir o pipeline inteiro com a tábua de mortalidade oficial (mortes esperadas) enquanto se aguarda a base de sinistros reais**, e trocar apenas o input quando os dados reais chegarem. Isso evita ociosidade e já entrega o esqueleto de cálculo testado, incluindo o próprio A/E (observado/tábua) como subproduto natural desse processo.
- Correção de rota identificada via revisão própria (auto-QA antes de levar à equipe): a célula de risco padrão precisa ser **idade × sexo × período**, não apenas idade × período — o campo sexo tinha sido omitido na primeira formulação do pipeline. Também corrigida a granularidade temporal de anual para **mensal**, pois a série anual não teria pontos suficientes para ajustar/testar uma distribuição estatística com robustez.

### Fase 5 — Apresentação de resultados e crise de rastreabilidade (reuniões de validação)

Esta foi a fase mais rica em aprendizado de processo, não só de conteúdo técnico. Yuri apresentou um pipeline funcional com resultados (A/E ratio, seleção de distribuição por AIC/BIC/teste de aderência, simulação de Monte Carlo, percentil de stress) — mas a equipe de dados/atuária **interrompeu a apresentação** porque não conseguia validar nenhum número sem ver o cálculo explícito.

Pontos de fricção documentados, todos relevantes como lição de processo:

1. **"Não conseguimos avaliar nada que você fez."** — resultados numéricos (ex.: uma sinistralidade percentual) apresentados sem mostrar numerador, denominador e filtros aplicados são, do ponto de vista de validação atuarial, **inúteis** — mesmo que o cálculo esteja correto.
2. **Confusão de unidades/labels** — uma métrica de exposição mensal vs. anual foi rotulada de forma trocada/ambígua, gerando desconfiança sobre todo o restante do pipeline até ser esclarecida.
3. **Premissas implícitas não documentadas como premissas** — um parâmetro de probabilidade de "mês sem sinistro" havia sido definido por decisão própria de Yuri (não extraído estatisticamente da base), mas isso não estava explícito; a equipe exigiu que toda constante decidida (e não calculada) fosse rotulada explicitamente como **premissa**, com a justificativa ao lado.
4. **"De onde vem esse número?" como pergunta padrão** — todo valor agregado (ex.: total de eventos esperados pela tábua) precisa estar imediatamente rastreável à fórmula e às colunas de origem, célula por célula.
5. **Reprodutibilidade da simulação** — a semente (seed) do gerador de números aleatórios da simulação Monte Carlo precisa estar **fixada explicitamente no código** (não deixada no default da linguagem), sob risco de o mesmo pipeline gerar resultados diferentes a cada execução — inaceitável para um número que será auditado.
6. **Ambiguidade entre indicadores paralelos** — o A/E ratio (desvio histórico observado vs. esperado pela tábua, olhando para o passado) e o fator de stress derivado da simulação de Monte Carlo (incerteza futura em torno da média simulada) são **duas métricas com propósitos diferentes que saem da mesma base** — a confusão entre os dois consumiu tempo de reunião até ficar claro que não há dependência direta entre eles (são paralelos, não sequenciais).
7. **Exigência de formato "Excel item a item, fórmulas visíveis, com coluna de observação ao lado de cada cálculo"** — a equipe explicitou que o objetivo não é apenas comunicar um resultado, mas produzir um artefato que **outra pessoa consiga operar e auditar** sem depender do autor original — um requisito de governança de modelo, não apenas de apresentação.

**Lição de processo consolidada:** em modelagem atuarial regulatória, a *transparência do caminho do cálculo* é tão importante quanto a correção do resultado final. Um pipeline correto, mas opaco, é considerado não entregável.

### Fase 6 — Consolidação técnica final documentada (reunião mais densa e mais madura do projeto)

Nesta fase o pipeline do componente Peculio chegou à sua forma mais completa e mais bem defendida tecnicamente, incorporando todas as correções cobradas na fase anterior:

- Base de expostos e base de sinistros com filtros de janela temporal e faixa etária plausível (18 a 120 anos) plenamente documentados, com contagem de registros removidos e o motivo de cada remoção.
- **Metodologia de conciliação (matching) entre bases de exposição e sinistro formalizada em três categorias**, por ordem decrescente de confiança:
  - **Oficial:** chave (produto, plano, tipo de cobertura, competência) encontrada exatamente no mesmo mês da ocorrência do evento;
  - **Sensibilidade (lag 1 mês):** a mesma chave só é encontrada na exposição do mês imediatamente anterior — tratado como cenário de sensibilidade, com transparência de que é uma categoria com mais subjetividade envolvida;
  - **Sem cruzamento (pendente):** nenhuma correspondência encontrada — permanece fora do numerador até investigação adicional.
- A/E ratio formalizado com múltiplos cenários de composição do numerador (só oficial / oficial + sensibilidade / total), deixando explícito o intervalo de incerteza associado à própria qualidade da conciliação — não apenas um número único de A/E.
- **Simulação de Monte Carlo totalmente especificada e documentada:**
  - Distribuição escolhida para a sinistralidade mensal agregada: **Gamma**, ajustada por máxima verossimilhança aos dados históricos (função `scipy.stats.gamma.fit`), selecionada por menor AIC frente a Lognormal e Normal, com teste de aderência Kolmogorov-Smirnov como validação cruzada;
  - Tratamento de meses com sinistralidade zero: variável indicadora **Bernoulli** com probabilidade `p₀` — definida explicitamente como **premissa do analista** (não extraída diretamente da base), documentada como tal;
  - Para cada cenário simulado: gera-se uma série de N meses (igual ao tamanho da janela histórica disponível) — cada mês é zero com probabilidade `p₀`, ou um valor amostrado da Gamma ajustada caso contrário — calcula-se a média dos N meses do cenário, e essa média é armazenada;
  - Repetição do processo por um número de cenários estatisticamente padrão (ordem de grandeza de dezena de milhar), com **semente fixada** para reprodutibilidade (ex.: `np.random.seed(42)`, verificado e travado antes do loop de simulação);
  - Resultado: uma distribuição empírica de milhares de médias simuladas de sinistralidade mensal.
  - **Cálculo do fator de stress:**
    ```
    P50 = mediana (ou percentil 50) das médias simuladas
    P_alvo = percentil escolhido (ex.: P75, P80, P90) das médias simuladas

    AR (em pontos percentuais) = P_alvo − P50
    Fator de stress (multiplicativo) = P_alvo / P50
    ```
  - **Aplicação do fator de stress ao cálculo atuarial (uma única vez, não 10.000 vezes):**
    ```
    QX_stress = fator_de_stress × QX_base (tábua oficial)
    BEL_base   = calculado com QX_base
    BEL_stress = calculado com QX_stress
    AR monetário = BEL_stress − BEL_base
    ```
  - Frequência e severidade também decompostas separadamente como visão complementar: frequência mensal de sinistros modelada por **Binomial Negativa** (superior a Poisson por acomodar melhor a sobre-dispersão observada na série), severidade individual por sinistro modelada por **Lognormal**.
- **Fundamentação externa do percentil e do fator de stress resultante:** o fator de stress obtido via P80 foi posicionado explicitamente contra o benchmark do módulo de mortalidade do Solvency II europeu (EIOPA Standard Formula, choque padrão de mortalidade a um nível de confiança de 99,5% a 1 ano) — o argumento de defesa, generalizável a qualquer calibração futura, é: *um percentil de confiança menor que 99,5% deve, por construção, produzir um fator de stress proporcionalmente menor que o benchmark de Solvency II; se o resultado obtido for coerente com essa relação (menor fator, para um percentil menor), a calibração não está fora da realidade do mercado.* Essa lógica de "consistência direcional com benchmark regulatório de referência" é reutilizável para validar qualquer percentil-alvo escolhido, independentemente do valor numérico específico.

### Fase 7 — Uso do próprio projeto de portfólio como referência técnica

Em determinado ponto do trabalho, Yuri usou seu próprio projeto de portfólio pessoal (motor de Ajuste ao Risco IFRS 17 já publicado, com Monte Carlo de frequência × severidade, VaR/CTE e validação estatística) como fonte de **benchmarking metodológico interno** para o trabalho no banco — extraindo dali:

1. A comparação formal entre técnicas de AR (VaR/percentil vs. CTE/Conditional Tail Expectation vs. Custo de Capital), usada para justificar por que a técnica de percentil (VaR) é adequada para o perfil de risco do Peculio;
2. A proposta de calcular o **CTE como validação cruzada** do percentil escolhido (ex.: média das perdas acima do percentil-alvo) — melhoria de rigor sem alterar a metodologia principal;
3. A prática de **fixar a semente do gerador aleatório** explicitamente no código;
4. Um **teste de convergência do número de cenários de Monte Carlo** (comparar o resultado do AR rodando com 1.000, 5.000, 10.000 e 50.000 cenários e verificar estabilização abaixo de um limiar, ex. variação < 1% entre 10k e 50k) — usado para justificar tecnicamente por que a quantidade de cenários escolhida é suficiente, e não arbitrária;
5. Um **template estruturado de documentação de premissas** (hipótese, justificativa, limitação, fonte) para formalizar cada decisão do pipeline do banco.

Este é um ponto narrativo importante: o ciclo se fecha — o portfólio pessoal informou o trabalho real no banco, e agora o trabalho real (metodologicamente, não numericamente) retroalimenta e amplia o portfólio pessoal.

---

## 3. Metodologia Final Consolidada

### 3.1 Visão geral do método

**Nome da técnica:** Ajuste ao Risco por Intervalo de Confiança (percentil), calibrado por simulação de Monte Carlo sobre a distribuição empírica ajustada à sinistralidade/experiência histórica, com estresse aplicado sobre a tábua biométrica (QX) e recálculo do BEL.

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Base de Expostos (carteira ativa)  →  denominador             │
│ 2. Base de Sinistros/Concedidos       →  numerador                │
│                                                                    │
│         ↓ conciliação (chave: produto × plano × cobertura × mês) │
│                                                                    │
│ 3. Série histórica de sinistralidade OU de A/E, por célula        │
│    célula = idade × sexo × produto × período                     │
│                                                                    │
│         ↓ credibility testing (Bühlmann se célula pequena)       │
│         ↓ teste de aderência (AIC/BIC/KS) → escolha da distrib.  │
│                                                                    │
│ 4. Simulação de Monte Carlo sobre a distribuição ajustada         │
│    → distribuição empírica de médias simuladas                   │
│                                                                    │
│         ↓ percentil-alvo (ex. P75/P80/P90)                       │
│                                                                    │
│ 5. Fator de stress = percentil_alvo / mediana_simulada           │
│                                                                    │
│         ↓ aplica sobre a tábua                                   │
│                                                                    │
│ 6. QX_stress = fator_de_stress × QX_base                          │
│    BEL_stress = VPL(fluxos, QX_stress)                            │
│    BEL_base   = VPL(fluxos, QX_base)                              │
│                                                                    │
│ 7. AR = BEL_stress − BEL_base                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Definição da célula de risco

`Célula = idade × sexo × produto/cobertura × período (mês)`

A granularidade mensal (não anual) é necessária para gerar pontos suficientes para ajuste e teste de aderência de uma distribuição estatística. A quebra por sexo é obrigatória porque as tábuas biométricas oficiais (BR-EMS, AT-2000) são diferenciadas por sexo — usar a tábua errada (ex. feminina em vez de masculina, ou vice-versa) invalida todo o A/E calculado a partir dela.

### 3.3 Credibility Testing (Bühlmann)

Antes de usar o A/E observado de uma célula para calibrar o stress, testar se o volume de expostos é suficiente para dar confiança estatística ao valor observado (regra de bolso comum no mercado: milhares de expostos e dezenas de eventos mínimos por célula). Se insuficiente:

```
fator_final = Z × A/E_interno + (1 − Z) × A/E_mercado (tábua/benchmark)
```

Onde `Z` (fator de credibilidade, entre 0 e 1) cresce com o volume de exposição/eventos da célula — quanto mais dados internos confiáveis, mais peso ao A/E observado; quanto menos, mais peso ao benchmark de mercado/tábua oficial.

### 3.4 Seleção de distribuição estatística

Candidatas testadas: **Gamma**, Lognormal, Normal (para a sinistralidade agregada mensal, contínua, positiva e tipicamente assimétrica à direita); **Binomial Negativa** vs. Poisson (para a contagem/frequência de eventos, quando há sobre-dispersão frente à Poisson); **Lognormal** (para a severidade individual de cada evento).

Critérios de seleção, em conjunto (nunca apenas um): **AIC/BIC** (penalizam complexidade), **teste de Kolmogorov-Smirnov** (aderência da forma), e razoabilidade teórica do suporte da distribuição (ex.: Gamma tem suporte em `[0, ∞)`, compatível com uma sinistralidade que nunca é negativa e tem cauda direita mais pesada que a Normal). É explicitamente insuficiente justificar a escolha apenas com "o critério estatístico apontou X" — é necessário also explicar teoricamente por que a forma da distribuição escolhida é compatível com o fenômeno modelado.

### 3.5 Simulação de Monte Carlo

- **Objetivo:** gerar a distribuição empírica da incerteza em torno da média histórica da sinistralidade/A/E, para dela extrair um percentil de confiança.
- **Inputs a documentar sempre, explicitamente, por escrito:** distribuição escolhida e seus parâmetros estimados (ex. shape/scale da Gamma), tratamento de zeros (ex. indicador Bernoulli com probabilidade `p₀` — e se `p₀` é estimado da base ou é uma premissa do analista, isso precisa estar rotulado), tamanho da amostra por cenário (igual ao tamanho da janela histórica disponível), número de cenários simulados, semente do gerador aleatório (fixada).
- **Mecânica:** por cenário, gerar uma série sintética do mesmo tamanho da janela histórica; cada ponto é zero (probabilidade `p₀`) ou amostrado da distribuição ajustada; calcular a média da série simulada; repetir e armazenar por todos os cenários; ordenar as médias simuladas e extrair os percentis de interesse.
- **Validação de convergência:** repetir a simulação com quantidades crescentes de cenários (ex. 1.000 / 5.000 / 10.000 / 50.000) e verificar que o resultado (AR ou fator de stress) estabiliza — variação abaixo de um limiar pequeno (ex. < 1%) entre a maior e a penúltima quantidade testada — antes de fixar o número de cenários definitivo.

### 3.6 Cálculo do AR e do BEL estressado

```
Fator de stress = Percentil_alvo(distribuição simulada) / Mediana(distribuição simulada)

QX_stress = Fator de stress × QX_base

BEL_base   = Σ [ QX_base(idade)   × Exposição(idade) × Benefício × Fator_desconto ]
BEL_stress = Σ [ QX_stress(idade) × Exposição(idade) × Benefício × Fator_desconto ]

AR (monetário) = BEL_stress − BEL_base
```

O stress é aplicado **uma única vez** sobre a tábua para o recálculo determinístico do BEL — não se recalcula o BEL 10.000 vezes; as 10.000 (ou N) simulações servem apenas para **calibrar o fator de stress**, que depois é aplicado de forma determinística.

### 3.7 Direção do stress por tipo de risco (assimetria importante)

| Risco | Direção do stress adverso | Por quê |
|---|---|---|
| Mortalidade (Peculio, Pensão por Morte, fase de diferimento) | `QX × (1 + fator)`, fator > 0 | Mais mortes → mais sinistros/benefícios pagos |
| Longevidade (fase de renda/concessão) | `QX × (1 − fator)`, fator > 0 | Menos mortes → participante vive mais → mais anuidades pagas |
| Invalidez | `QX_invalidez × (1 + fator)` | Mais eventos de invalidez → mais rendas concedidas |
| Conversão em renda | stress para cima | Mais saldo migrando para a fase vitalícia → mais exposição de longo prazo |
| Resgate/Lapse | **contraintuitivo:** stress adverso é resgate **menor**, não maior | Resgate maior tira gente da carteira antes da fase de renda vitalícia (reduz exposição futura); resgate menor mantém mais pessoas até a conversão, aumentando a exposição à longevidade — que é tipicamente o risco dominante em produtos de renda vitalícia |

**Implicação central:** o pior cenário para o AR de um produto de renda vitalícia normalmente não é estressar cada premissa isoladamente no seu extremo absoluto — é a **correlação adversa** entre elas (mais gente vivendo mais, **e** convertendo mais em renda, **e** resgatando menos antes de chegar lá). Modelar essa correlação (mesmo que de forma simplificada na primeira fase) é mais realista que a soma simples de componentes independentes.

### 3.8 Estrutura "caixinhas" (fase 1: soma simples; evolução futura: diversificação)

```
AR_total (fase 1) = AR_mortalidade + AR_longevidade + AR_invalidez + AR_resgate

AR_total (evolução proposta) = Σ AR_componente − Benefício_de_diversificação
```

O benefício de diversificação (tipicamente 10%–20% de redução sobre a soma simples, calibrado por correlação histórica entre os riscos) é uma prática recomendada por organismos atuariais internacionais (ver seção 7) mas não chegou a ser implementada na fase do projeto concluída por Yuri — fica registrada como evolução metodológica pendente.

### 3.9 Tratamento por produto

| Produto | Tipo de fluxo | Particularidade de cálculo |
|---|---|---|
| Peculio | Pagamento único (lump sum) | Valor do sinistro já está completo na base — cálculo direto de sinistralidade/A/E, sem VPL intermediário |
| Pensão por Morte | Renda mensal vitalícia ao beneficiário | Exige cálculo de valor presente de anuidade (VPL) para tornar comparável ao prêmio/exposição — mesma lógica do Peculio aplicada sobre o VPL em vez do valor nominal |
| Renda por Invalidez (PMBC) | Renda mensal (temporária ou vitalícia) ao segurado | Mesma lógica de VPL da Pensão; adicionalmente, a *probabilidade de entrada* em invalidez é ela própria uma tábua/premissa separada da tábua de mortalidade |
| Pensão ao Menor | Renda mensal até maioridade do dependente | VPL de anuidade temporária (prazo determinado pela idade de maioridade menos idade atual do dependente, não vitalícia) |
| Previdência — Longevidade | Renda vitalícia na fase de concessão | Tábua de renda (ex. família de tábuas PRN/SUSEP) tratada separadamente da tábua de mortalidade em risco; stress na direção de menor mortalidade (ver 3.7) |
| Previdência — Resgate/Lapse | Saída antecipada na fase de acumulação | Direção de stress contraintuitiva (ver 3.7); depende de uma base de histórico de resgates que nunca chegou a ser disponibilizada durante o projeto original |

---

## 4. Data Dictionary (estrutura de dados necessária — genérico, sem números da carteira real)

| Variável/Base | Papel no modelo | Granularidade | Período | Observação |
|---|---|---|---|---|
| Base de Expostos (carteira ativa) | Denominador do A/E e da sinistralidade | Idade × sexo × produto/cobertura × mês | Janela histórica de vários anos (ideal: 8 anos para capturar ciclos econômicos e eventos de cauda como pandemias; mínimo prático viável: ~5 anos) | Contém prêmio/contribuição e capital segurado por registro; uma linha por mês de exposição por segurado (base longitudinal) |
| Base de Sinistros/Concedidos | Numerador do A/E; benefícios pagos | Data de ocorrência, data de aviso, valor pago, idade, sexo, produto/cobertura | Mesma janela da base de expostos (idealmente estendida para trás, se disponível) | Contém o lag ocorrência→aviso, base para IBNR; para pensão/invalidez/pensão ao menor, contém o valor de renda mensal (exige VPL) |
| Base de Resgates/Lapse | Denominador e numerador do stress de resgate | Fundo/plano × ano/mês | Histórico disponível | **Gap crítico não resolvido no projeto original** — nunca chegou a ser disponibilizada |
| Tábua de mortalidade base | QX_base para BEL | Idade × sexo | Vigente | Tábua oficial do mercado (ex. BR-EMS) usada na fase de diferimento/risco |
| Tábua de mortalidade contratual | QX para cálculo do benefício de renda (fator atuarial) | Idade × sexo | Vigente | Tábua contratual (ex. tábuas históricas do tipo "T-XXXX"), usada apenas no cálculo do fator atuarial do benefício, nunca alterada pelo AR |
| Tábuas de longevidade (renda) | Calibração do stress de longevidade | Idade × sexo × versão/ano de publicação | Série histórica de versões (ex. desde 2010) | A evolução histórica das revisões dessas tábuas (queda do QX ao longo das versões = "melhoria de mortalidade") é a base para projetar o fator de stress de longevidade quando o volume de dados internos em fase de renda é pequeno |
| Taxa de conversão em renda | Stress de conversão | Por plano/produto × período | Histórico disponível | Percentual do saldo acumulado que efetivamente migra para renda vitalícia na data de elegibilidade |
| AR% vigente (Peculio) | Ponto de partida para auditoria/recalibração | Por produto | Atual | Único componente do estudo que já tinha uma calibração pré-existente a ser revisada, não criada do zero |

---

## 5. Arquitetura Técnica Planejada

```
AWS (Athena + S3, dados em Parquet)
        │
        ▼  (boto3 / SQL via Athena)
VS Code local (Python)
        │
        ▼
┌─────────────────────────────────────────────┐
│  Módulo 1 — data_loader                       │  → carrega Parquet, valida schema, tipos, nulos
│  Módulo 2 — mortality_table                    │  → carrega tábuas oficiais (QX por idade/sexo)
│  Módulo 3 — experience_engine (A/E, conciliação)│ → cruza expostos × sinistros, calcula A/E
│  Módulo 4 — stress_calibrator                  │  → teste de distribuição, Monte Carlo, percentil
│  Módulo 5 — bel_calculator                     │  → VPL base e VPL estressado
│  Módulo 6 — ar_engine                          │  → AR = BEL_stress − BEL_base, por componente
│  Módulo 7 — backtester                         │  → validação, convergência, testes de aderência
└─────────────────────────────────────────────┘
        │
        ▼
Resultado (S3) + Excel/relatório de auditoria (item a item, fórmulas visíveis)
```

Ferramentas em ordem de introdução: **Athena** (exploração SQL inicial) → **VS Code + boto3** (scripts repetíveis e versionáveis) → **SageMaker** (reservado para modelos que exigissem ML — não se confirmou necessário nesta fase, já que a metodologia é estatística clássica/atuarial, não aprendizado de máquina).

---

## 6. Gaps e Itens Nunca Resolvidos (no momento do desligamento)

1. **Base de Resgates/Lapse nunca foi disponibilizada** — o componente de resgate ficou completamente bloqueado; a metodologia para ele existe apenas em nível conceitual (seção 3.7), nunca chegou a ser calibrada com dados, nem sintéticos.
2. **Percentil-alvo final nunca foi formalmente aprovado pela liderança** — o projeto trabalhou consistentemente na faixa 75%–90%, com P80 como caso mais desenvolvido no componente Peculio, mas a decisão final de qual percentil reportar oficialmente ficou pendente de validação com a liderança (checkpoint que dependia do retorno de férias do orientador principal).
3. **BEL estressado monetário do Peculio não chegou a ser fechado** — o fator de stress foi calibrado e validado na simulação de Monte Carlo, mas o passo final de recalcular o BEL com a tábua estressada e apurar o AR monetário (`BEL_stress − BEL_base`) era a entrega pendente do checkpoint seguinte ao desligamento.
4. **Benefício de diversificação entre componentes de risco não foi implementado** — a soma das "caixinhas" permaneceu simples (sem desconto de correlação) durante todo o projeto; é uma melhoria explicitamente identificada mas não executada.
5. **Componentes de Longevidade, Invalidez e Pensão ao Menor não avançaram além da formulação conceitual** — o trabalho de dados avançou concretamente apenas no Peculio; os demais componentes têm a lógica definida (seção 3.9) mas não foram calibrados com nenhum dado, real ou sintético.
6. **Ausência de benchmark A/E vs. tábua alternativa** — foi levantada a hipótese própria de que uma tábua oficial pudesse estar super ou subestimando a mortalidade para o perfil específico do produto avaliado (baseado em um teste qui-quadrado significativo entre observado e esperado), mas o teste de uma tábua alternativa nunca chegou a ser executado.
7. **Modelo de correlação adversa (mortalidade↓ + conversão↑ + resgate↓ simultâneos) nunca foi simulado conjuntamente** — ficou descrito qualitativamente (seção 3.7) mas sem simulação conjunta multivariada.
8. **Credibility testing (Bühlmann) formulado mas não implementado em código** — permaneceu como próximo passo identificado desde a fase conceitual inicial, nunca chegou a ser codificado, pois o volume de dados do Peculio (o único componente com dados reais trabalhados) foi suficiente para dispensar essa camada nas células analisadas.

---

## 7. Referências e Fontes Externas Consultadas

| Fonte | O que contribui |
|---|---|
| **IFRS 17, §37** | Define o AR como compensação pela incerteza de valor/prazo dos fluxos de risco não financeiro; base normativa de toda a metodologia |
| **EIOPA Standard Formula — SCR Mortality/Longevity Module (Solvency II)** | Benchmark de choque padrão europeu (mortalidade: +15% no QX a 99,5% de confiança a 1 ano) — usado para posicionar direcionalmente qualquer fator de stress obtido via percentil menor que 99,5% |
| **EIOPA — First year IFRS 17 implementation study (2024)** | Evidência de mercado de que o AR do IFRS 17 é, em média, ~33%–44% menor que o Risk Margin do Solvency II para vida — confirma que o IFRS 17 não busca o conservadorismo extremo do Solvency II |
| **Moodys — Equivalent Confidence Level for the IFRS 17 Risk Adjustment** | Pesquisa de mercado sobre níveis de confiança divulgados por seguradoras reais sob IFRS 17 (ex.: Manulife 90–95%, QBE 90%, Sun Life 80–85%; faixa mais comum para vida de longa duração: 75%–90%) |
| **Canadian Institute of Actuaries (CIA) — Educational Note: IFRS 17 RA for Life and Health** | Recomenda separação do AR por tipo de risco (mortalidade, longevidade, resgate) com benefício de diversificação — valida a abordagem de "caixinhas" com evolução futura para diversificação |
| **IAA — Risk Adjustments for Insurance Contracts under IFRS 17** | Monografia de referência técnica completa sobre AR sob IFRS 17 |
| **Milliman — Deriving the Confidence Level for the Risk Adjustment** | Estudo de caso passo a passo para derivar o nível de confiança equivalente de um AR calibrado por outra técnica |
| **MDPI/Risks (2023) — A Model for Risk Adjustment (IFRS 17) for Surrender Risk in Life Insurance** | Modelo acadêmico específico para risco de resgate via ordenação convexa de variáveis estocásticas, com fórmulas fechadas para quantis de portfólio — diretamente aplicável ao componente de resgate/lapse deste projeto (nunca implementado por falta de dados) |
| **SUSEP / CNSP (regulação brasileira)** | Referências regulatórias locais sobre margem de risco em seguros de vida no Brasil, usadas como ponto de comparação complementar ao benchmark internacional |
| **SOA — IFRS-17 Experiences From Roll Out (2025)** | Relatos de mercado sobre a implementação prática do IFRS 17 em diferentes seguradoras |

---

## 8. Propostas de Melhoria Identificadas (para completar no projeto de portfólio)

Estas são melhorias já identificadas durante o projeto original, mas nunca implementadas — tornam-se o roteiro de evolução do projeto de portfólio:

1. **Implementar credibility testing de Bühlmann de fato em código**, com um parâmetro de credibilidade Z explícito e testável, não apenas formulado.
2. **Implementar o benefício de diversificação entre caixinhas de risco** via matriz de correlação (histórica ou assumida com justificativa), reduzindo a soma simples dos componentes.
3. **Simulação conjunta multivariada do cenário de correlação adversa** (mortalidade↓, conversão↑, resgate↓ simultaneamente) em vez de stress isolado por variável.
4. **Adicionar CTE (Conditional Tail Expectation) como validação cruzada** de todo percentil escolhido — não apenas reportar o VaR/percentil isolado.
5. **Teste de convergência formal do número de cenários de Monte Carlo**, documentado como parte do artefato de validação (não apenas mencionado).
6. **Modelo de resgate/lapse via ordenação convexa** (referência MDPI 2023), implementado com dados sintéticos calibrados a taxas de lapse plausíveis para o mercado brasileiro.
7. **Completar os componentes de Longevidade, Invalidez e Pensão ao Menor**, hoje apenas formulados conceitualmente, com implementação de ponta a ponta.
8. **Dashboard interativo** para explorar o impacto de diferentes percentis-alvo e cenários de stress no AR e no CSM resultante — transformando a metodologia estática em uma ferramenta de decisão.
9. **Pesquisa complementar de métodos alternativos** (bootstrap não paramétrico para amostras pequenas, cópulas para modelar dependência entre riscos, comparação com Cost of Capital) — foi sugerido internamente e nunca executado.

---

## 9. Como este documento se conecta ao projeto de portfólio

Este documento é a base metodológica para um novo projeto (`v3`) no repositório de portfólio `IFRS17_Risk`, que:

- Implementa esta metodologia de ponta a ponta em Python, com dados **sintéticos, calibrados a tábuas oficiais e públicas** (BR-EMS, AT-2000, PRSSVBR/SUSEP) — nenhum dado ou resultado numérico da carteira real da instituição é usado;
- Endereça as propostas de melhoria da seção 8 que não puderam ser concluídas no projeto original;
- Mantém rastreabilidade total de cálculo (uma lição de processo central deste projeto — seção 2, Fase 5) como requisito de design, não como item posterior de documentação;
- É a evolução natural da linha **v1 (`ifrs17-risk-adjustment`, genérico) → v2 (`credit-risk-ecl-engine`, pivô para crédito) → v3 (aplicação real de metodologia atuarial multi-produto de previdência)** já presente no repositório.
