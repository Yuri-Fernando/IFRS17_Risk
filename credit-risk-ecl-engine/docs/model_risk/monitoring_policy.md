# Política de monitoramento

| Indicador | Frequência | Verde | Âmbar | Vermelho | Ação |
|---|---|---|---|---|---|
| PSI do mix de rating | mensal | < 0,10 | 0,10–0,25 | > 0,25 | investigar originação |
| Observado/previsto 12m por safra | trimestral | 0,8–1,25 | 0,6–1,6 | fora | revisar PIT/satélite |
| Roll rates (C→30, 30→60, 60→default) | mensal | ±20% da média | ±40% | além | revisar staging/Markov |
| Cobertura (ECL/EAD) por stage | mensal | dentro da faixa histórica | — | quebra de tendência sem explicação | waterfall de drivers |
| Taxa de cura D30/D60 | mensal | estável | — | queda persistente | revisar critério de SICR |
| Workouts abertos > 24 meses | trimestral | < 10% | 10–20% | > 20% | revisar LGD (viés de resolução) |

Implementação atual: indicadores calculados em `run_lifetime_pipeline.py` (roll rates, backtesting, PSI). Automação contínua fica no ROADMAP.
