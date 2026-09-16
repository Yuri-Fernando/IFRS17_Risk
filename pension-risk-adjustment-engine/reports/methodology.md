# Metodologia — pension-risk-adjustment-engine

> Documento resumido. A metodologia completa, com a evolução histórica, decisões,
> lições de processo e referências, está em [`../../itau/METODOLOGIA_MESTRE.md`](../../itau/METODOLOGIA_MESTRE.md).

## Pipeline

```
Base de Expostos + Base de Sinistros (100% sintéticas)
        │
        ▼  conciliação por célula (idade x sexo x produto x mês)
Série histórica de sinistralidade / A/E ratio
        │
        ▼  credibility testing (Bühlmann) + seleção de distribuição (AIC/BIC/KS)
Simulação de Monte Carlo (N cenários, semente fixa)
        │
        ▼  percentil-alvo (P75/P80/P90) / mediana
Fator de stress
        │
        ▼  aplicado à tábua biométrica
QX_stress = fator x QX_base  →  BEL_stress = VPL(QX_stress)
        │
        ▼
AR = BEL_stress − BEL_base  (por componente/"caixinha")
        │
        ▼  soma com benefício de diversificação
AR total  →  impacto no CSM (CSM cai R$1 para cada R$1 de AR)
```

## Produtos cobertos

| Produto | Tipo de fluxo | Direção do stress |
|---|---|---|
| Peculio | Pagamento único (lump sum) na morte | Mortalidade ↑ (QX × fator) |
| Pensão por Morte | Capital equivalente de renda, pago na entrada (morte do titular) | Mortalidade ↑ |
| Renda por Invalidez | Capital equivalente de renda, pago na entrada (invalidez) | Incidência de invalidez ↑ |
| Pensão ao Menor | Capital equivalente de renda temporária, pago na entrada | Mortalidade ↑ |
| Previdência — Longevidade | Anuidade vitalícia contingente à sobrevivência do rentista | Longevidade ↑ (QX ÷ fator) |
| Previdência — Resgate | Não implementado (dados de lapse nunca disponibilizados no projeto original) | — |

## Por que "capital equivalente" para produtos de renda contingente à entrada

Pensão por Morte, Renda por Invalidez e Pensão ao Menor pagam uma renda **que só começa após
um evento de entrada** (morte/invalidez do titular). Modelar isso corretamente exigiria um
decremento encadeado (probabilidade de entrada × sobrevivência subsequente do beneficiário).
Este projeto simplifica deliberadamente esse segundo estágio, aproximando o valor pago na
entrada por um capital fixo equivalente (`renda mensal × fator de duração esperada`), documentado
em `src/actuarial/bel_calculator.py`. Isso preserva a direção e a mecânica corretas do stress
(mais eventos de entrada → mais BEL → mais AR), mas não deve ser lido como um cálculo atuarial
de precisão para uso institucional real.

## Dataset

100% sintético. Portfólio gerado por simulação (idade, sexo, produto, capital segurado);
sinistros sorteados a partir das próprias tábuas biométricas paramétricas do projeto — o que
torna o dataset **internamente auditável**: o A/E ratio agregado deve ficar próximo de 100%
quando calculado contra a mesma tábua usada para gerá-lo (verificado em
`tests/test_synthetic_portfolio.py::test_dataset_internally_consistent_ae_near_100pct` e na
seção 2 do notebook).

## Tábuas biométricas

Aproximação paramétrica via lei de Gompertz-Makeham (`src/data/mortality_tables.py`), calibrada
para reproduzir a *forma* de uma curva de mortalidade humana plausível para o mercado brasileiro
— não os valores exatos das tábuas oficiais (BR-EMS, AT-2000, PRSSVBR), que têm distribuição
restrita. Ver `reports/assumptions.md` para o detalhamento dessa limitação.

## Resultado de referência (execução real, seed=42, 60.000 segurados sintéticos)

Ver `reports/results/final_results.json` para o resultado completo gerado pela última
execução de `run_pipeline.py` / do notebook.
