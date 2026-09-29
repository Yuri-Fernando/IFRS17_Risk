# Limitações conhecidas

1. **Dados:** German Credit (1994) para PD 12m; painel lifetime 100% sintético — valida software e método, não carteira real.
2. **Série macro curta** (54 meses, uma recessão): o satélite tem poucos graus de liberdade (R² 0,74 in-sample; sem validação fora da amostra).
3. **Pré-pagamento como censura no KM:** estima PD "na ausência de saída"; a incidência cumulativa com risco competitivo (reportada) é menor. O ECL usa KM condicionado à sobrevivência do contrato no MOB atual — escolha conservadora.
4. **Cauda da hazard** além do MOB observado é extrapolada pela média dos últimos 12 meses.
5. **Markov homogêneo** (não depende de MOB nem de macro) — usado só para contratos já em atraso.
6. **LGD:** workouts abertos excluídos (viés de resolução); downturn definido por Z < −0,8.
7. **Rotativo:** vida comportamental fixada em 36 meses.
8. **SICR:** regra relativa 2× + absoluta 0,5 p.p. é ilustrativa; sem calibração por análise de migração real.
9. **Cenários e pesos** (50/20/30) ilustrativos; não há processo de governança de cenários.
10. **Sem calibração regulatória** e sem validação independente real.
