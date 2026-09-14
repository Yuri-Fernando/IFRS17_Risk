# Alinhamento Regulatório — IFRS 9 / Resolução CMN 4.966

## Mapeamento requisito → implementação

| Requisito normativo | Referência | Implementação no projeto |
|---|---|---|
| Classificação em 3 estágios (Stage 1/2/3) | IFRS 9 §5.5.1–5.5.5 | `src/modeling/staging.py::classify_stage` |
| Critério de SICR (aumento significativo de risco) | IFRS 9 §5.5.9–5.5.11 | Deterioração relativa (2× PD originação) e absoluta (PD ≥ 20%) |
| ECL 12 meses para Stage 1 | IFRS 9 §5.5.5 | `pd_12m × LGD × EAD` |
| ECL lifetime para Stage 2 e 3 | IFRS 9 §5.5.3 | `pd_lifetime × LGD × EAD` |
| Incorporação de informação prospectiva (forward-looking) | IFRS 9 §5.5.17(c) | Stress testing com cenários macroeconômicos (`src/validation/stress_test.py`) |
| Uso de múltiplos cenários ponderados por probabilidade | IFRS 9 §5.5.18 | Simulação de Monte Carlo gera distribuição completa de perdas, não apenas ponto único |
| Definição de default | IFRS 9 Apêndice A | Flag `default` do dataset, tratada como evidência objetiva de perda (Stage 3) |
| Mensuração de PD, LGD, EAD | IFRS 9 §B5.5.28–B5.5.55 | `src/modeling/pd_model.py`, `lgd_model.py`, `ead_model.py` |
| Governança e validação de modelos | Resolução CMN 4.966, Art. 32-A e correlatos; Resolução BCB 352/2023 | `src/governance/`, `src/validation/`, gates em `config/model_config.yaml` |
| Divulgação de premissas e julgamentos significativos | IFRS 9 §35F-35G (IFRS 7) | `reports/assumptions.md` |
| Sensibilidade da provisão a mudanças de premissas | Boas práticas de disclosure | `reports/model_comparison.md` (stress test) |

## Convergência Brasil × IASB

A Resolução CMN n. 4.966/2021 substitui a Resolução CMN 2.682/1999 e
alinha as instituições financeiras brasileiras ao modelo de perda
esperada da IFRS 9, com vigência a partir de 2025. A metodologia deste
projeto (PD/LGD/EAD → ECL por estágio) é diretamente aplicável a ambos os
frameworks, já que a resolução brasileira foi desenhada para
convergência com a norma internacional.

## O que este PoC NÃO cobre (fora de escopo declarado)

- Definição contábil completa de "compromissos de crédito não desembolsados"
  e cálculo de CCF regulatório detalhado.
- Tratamento de ativos financeiros adquiridos ou originados com problemas
  de recuperação de crédito (POCI).
- Purchased or Originated Credit-Impaired assets.
- Hedge accounting e suas interações com ECL.
- Divulgações completas de nota explicativa (IFRS 7) — o projeto foca no
  motor de cálculo, não no relatório financeiro final.
