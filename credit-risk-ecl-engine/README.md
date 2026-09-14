# Credit Risk ECL Engine

Motor de cálculo de **Perda Esperada de Crédito (ECL)** conforme **IFRS 9**
e **Resolução CMN n. 4.966/2021**, com modelagem de **PD, LGD e EAD**,
**staging** por estágio de risco (Stage 1/2/3), **simulação de Monte
Carlo com correlação entre segmentos via cópula Gaussiana**, e um pacote
completo de **validação, backtesting e stress testing** de modelos de
crédito.

> Este projeto é a **v2** do [ifrs17-risk-adjustment](../ifrs17-risk-adjustment/),
> pivotado de risco atuarial de seguros (IFRS 17) para **risco de
> crédito bancário** (IFRS 9 / PD-LGD-EAD), mantendo a mesma disciplina
> de engenharia (modularidade, governança, validação estatística) e
> endereçando explicitamente a lacuna de correlação entre riscos que
> costuma faltar em PoCs desse tipo.

---

## 🚀 Como rodar (3 passos)

```bash
cd credit-risk-ecl-engine

# 1. Instala dependências e baixa o dataset (German Credit, UCI)
python setup_environment.py

# 2. Roda o pipeline completo
python run_pipeline.py --export-json

# 3. Veja o resultado
#    - Console: resumo executivo
#    - reports/result_final.json: resultado completo + trilha de auditoria
#    - data/processed/portfolio_ecl_scored.csv: carteira contrato a contrato
```

Sem internet? Use dados sintéticos:
```bash
python run_pipeline.py --data-source synthetic
```

---

## Por que este projeto

Vaga de referência (área de Gerenciamento de Riscos Financeiros — Risco
de Crédito, ver `../para add.md`): **PD, LGD, EAD, IFRS 9, Resolução CMN
4.966, ciclo de crédito, otimização de custo de crédito**. Este PoC
implementa cada um desses conceitos de ponta a ponta, com dados reais
baixados (não simulados do zero), código testado (11 testes unitários) e
resultados reproduzíveis — não um exercício teórico, mas uma
demonstração de execução completa do fluxo que uma área de Modelagem de
Risco de Crédito realmente roda.

**Correlação entre riscos** — um gap comum em modelos de crédito que
somam `PD × LGD × EAD` contrato a contrato assumindo independência — é
tratado explicitamente aqui via **cópula Gaussiana + mistura de Vasicek**
no motor de simulação (`src/simulation/copula_simulation.py`), gerando
VaR e CVaR de cauda além da ECL contábil pontual.

---

## O que a provisão é (resultado de referência)

Execução com o dataset real German Credit (1.000 contratos):

| Métrica | Valor |
|---|---|
| Exposição total (EAD) | R$ 2.289.880,60 |
| ECL total (provisão) | R$ 874.913,67 |
| Coverage ratio | 38,2% |
| VaR 99,9% (Monte Carlo c/ cópula) | R$ 1.026.556,20 |
| Gini / KS do modelo de PD | 0,617 / 0,531 |

Números completos, por stage e por segmento, em
[reports/model_comparison.md](reports/model_comparison.md). Coverage
ratio elevado é esperado neste dataset específico (30% de mau pagador
por desenho amostral) — ver [docs/dataset_card.md](docs/dataset_card.md).

---

## Estrutura do projeto

```
credit-risk-ecl-engine/
├── data/
│   ├── raw/german_credit.csv          # dataset real (UCI German Credit, baixado)
│   ├── processed/                      # carteira scorada (gerado pelo pipeline)
│   └── external/
├── src/
│   ├── data/            # load_data.py, preprocess.py (segmentação, encoding)
│   ├── modeling/        # pd_model.py, staging.py, lgd_model.py, ead_model.py, ecl_calculation.py
│   ├── simulation/      # copula_simulation.py (Monte Carlo + correlação)
│   ├── validation/      # model_validation.py, backtesting.py, stress_test.py
│   ├── governance/      # audit_log.py, model_versioning.py
│   └── cloud/           # pipeline.py (orquestração)
├── config/
│   ├── parameters.yaml  # parâmetros de execução
│   └── model_config.yaml # gates de qualidade, alinhamento regulatório
├── reports/              # metodologia, premissas, alinhamento IFRS9, validação, resultados
├── docs/                 # explicação de negócio, glossário, dataset card, diagrama
├── notebooks/            # quickstart (formato percent, compatível com Jupyter)
├── tests/                # 11 testes unitários (pytest)
├── run_pipeline.py       # CLI principal
└── setup_environment.py  # instala deps + baixa dataset
```

---

## Metodologia (resumo)

```
1. Carrega German Credit (1.000 contratos reais, UCI)
2. Segmenta a carteira (4 linhas de negócio) + codifica atributos
3. Treina PD: Regressão Logística (champion) vs. Gradient Boosting (challenger)
4. Classifica Stage 1/2/3 (SICR) e extrapola PD lifetime
5. Estima LGD (Beta por colateral) e EAD (saldo remanescente)
6. Calcula ECL = PD x LGD x EAD, por contrato, stage e segmento
7. Simula 10.000 cenários correlacionados (cópula Gaussiana + Vasicek) → VaR / CVaR
8. Valida: Gini, KS, PSI, calibração, backtesting de Kupiec
9. Aplica 4 cenários de stress (choques de PD e LGD downturn)
10. Registra trilha de auditoria completa e versiona o modelo
```

Detalhamento técnico completo em
[reports/methodology.md](reports/methodology.md).

## Documentação

| Documento | Conteúdo |
|---|---|
| [docs/business_explanation.md](docs/business_explanation.md) | O que o modelo faz, em linguagem de negócio |
| [docs/glossary.md](docs/glossary.md) | PD, LGD, EAD, ECL, Stage 1/2/3, SICR, cópula, VaR/CVaR... |
| [docs/dataset_card.md](docs/dataset_card.md) | Origem, estrutura e limitações do dataset German Credit |
| [docs/architecture_diagram.md](docs/architecture_diagram.md) | Diagrama de fluxo (Mermaid) |
| [reports/methodology.md](reports/methodology.md) | Como cada componente é calculado |
| [reports/assumptions.md](reports/assumptions.md) | Toda premissa não observada nos dados, justificada |
| [reports/ifrs9_alignment.md](reports/ifrs9_alignment.md) | Mapeamento requisito normativo → implementação |
| [reports/validation_report.md](reports/validation_report.md) | Como interpretar cada teste estatístico |
| [reports/model_comparison.md](reports/model_comparison.md) | Resultados numéricos da execução de referência |
| [reports/audit_trail.md](reports/audit_trail.md) | Como a trilha de auditoria funciona |

---

## Testes

```bash
pytest tests/ -v          # 11 testes cobrindo dados, PD, staging, LGD/EAD, ECL, simulação, validação
```

## Uso programático

```python
from src.cloud.pipeline import run_pipeline

result = run_pipeline(
    data_source="csv",
    data_path="data/raw/german_credit.csv",
    n_simulations=50000,
    inter_segment_correlation=0.30,
)

print(f"ECL: R$ {result['portfolio']['total_ecl']:,.2f}")
print(f"VaR 99.9%: R$ {result['monte_carlo']['var']['var_99.9']:,.2f}")
```

## Limitações conhecidas (declaradas, não ocultadas)

1. Dataset é um corte transversal único — sem múltiplas safras, o que
   limita a validação real de PD lifetime e o backtesting por stage a um
   exercício ilustrativo (ver achado documentado em `reports/assumptions.md`).
2. LGD não é observada (dataset sem dados de recuperação/cobrança) —
   modelada por proxy de colateral.
3. Correlação entre segmentos é parametrizada, não estimada de série
   histórica real de inadimplência.
4. Taxa de default do dataset (30%) não representa carteiras bancárias
   reais — leia resultados como demonstração de método, não benchmark.

## Roadmap (evoluções de produção)

- [ ] Estimar correlação de segmentos de dados históricos reais (substituindo a equicorrelação parametrizada)
- [ ] Curva de PD marginal por vintage (substituindo a extrapolação por hazard rate constante)
- [ ] Modelo de LGD com dados reais de recuperação/cobrança
- [ ] API REST para scoring em tempo real
- [ ] Dashboard executivo (Power BI/Tableau) consumindo `reports/result_final.json`
- [ ] Integração com banco de dados (PostgreSQL) para histórico de execuções

---

## Créditos e licença

- Dataset: UCI Statlog German Credit Data (Hofmann, 1994), domínio público acadêmico.
- Código: uso livre para fins de portfólio/estudo.
- v1 (risco atuarial de seguros, IFRS 17): [../ifrs17-risk-adjustment](../ifrs17-risk-adjustment/)
