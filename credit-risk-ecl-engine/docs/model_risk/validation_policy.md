# Política de validação

Referências conceituais: SR 11-7 (Fed/OCC), Resolução CMN 4.557 (gerenciamento de riscos) e CMN 4.966 (instrumentos financeiros).

1. **Independência:** o validador não é o desenvolvedor. Nesta PoC o pack é gerado automaticamente e marcado "requer revisão humana".
2. **Escopo mínimo por validação:** discriminação, calibração por rating (binomial/Jeffreys), estabilidade (PSI), backtesting por safra, benchmarking de métodos, sensibilidade de premissas, limitações.
3. **Semáforo de backtesting:** razão observado/previsto em [0,8; 1,25] verde; [0,6; 1,6] âmbar; fora, vermelho.
4. **Gatilhos de revalidação:** mudança de metodologia, 2 safras vermelhas consecutivas, PSI > 0,25, mudança material de cenários macro.
5. **Resultado:** aprovado / aprovado com ressalvas / reprovado — sempre com plano de ação datado.
6. **Evidência:** `reports/lifetime/validation_pack.md` + `summary.json` versionados junto do commit do código.
