"""
Registro de premissas (audit trail) — formato hipótese / justificativa /
limitação / fonte, replicando o template exigido na prática real do projeto
(itau/METODOLOGIA_MESTRE.md, seção 2 Fase 5, item 3: "toda constante decidida,
e não calculada, deve ser rotulada explicitamente como premissa").
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class Assumption:
    name: str
    value: str
    justification: str
    limitation: str
    source: str


@dataclass
class AssumptionRegistry:
    assumptions: list[Assumption] = field(default_factory=list)

    def add(self, name: str, value: str, justification: str, limitation: str, source: str) -> None:
        self.assumptions.append(Assumption(name, value, justification, limitation, source))

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([a.__dict__ for a in self.assumptions])

    def to_markdown(self) -> str:
        df = self.to_dataframe()
        lines = ["| Premissa | Valor | Justificativa | Limitação | Fonte |", "|---|---|---|---|---|"]
        for _, r in df.iterrows():
            lines.append(f"| {r['name']} | {r['value']} | {r['justification']} | {r['limitation']} | {r['source']} |")
        return "\n".join(lines)


def default_registry(config: dict) -> AssumptionRegistry:
    """Popula o registro com as premissas centrais deste projeto — cada uma
    rastreável até uma decisão específica documentada em METODOLOGIA_MESTRE.md."""
    reg = AssumptionRegistry()
    reg.add(
        name="Tábuas de mortalidade",
        value="Aproximação paramétrica (Makeham), não a tábua oficial BR-EMS/AT-2000/PRSSVBR",
        justification="Tábuas oficiais têm distribuição restrita (IBA/SUSEP); a forma de Makeham reproduz o formato realista de uma curva de mortalidade humana",
        limitation="Valores de qx não correspondem exatamente aos publicados oficialmente — válido para demonstrar a METODOLOGIA, não para uso regulatório real",
        source="src/data/mortality_tables.py; Makeham (1860); Bowers et al., Actuarial Mathematics",
    )
    reg.add(
        name="Portfólio",
        value="100% sintético, gerado por simulação",
        justification="Nenhum dado real de nenhuma carteira/instituição é usado neste projeto de portfólio público",
        limitation="Distribuição etária, de produtos e de capital segurado é ilustrativa, não calibrada a um mercado real específico",
        source="src/data/synthetic_portfolio.py",
    )
    reg.add(
        name="Probabilidade de mês com sinistralidade zero (p0)",
        value="Estimada empiricamente da série sintética gerada (não fixada arbitrariamente)",
        justification="O projeto original fixou p0 por decisão do analista sem verificação estatística prévia — identificado como falha de rastreabilidade (METODOLOGIA_MESTRE.md, Fase 5, item 3). Este projeto corrige isso estimando p0 diretamente dos dados.",
        limitation="Ainda assume que a taxa histórica de meses com zero sinistros é representativa do futuro",
        source="src/simulation/monte_carlo.py::estimate_zero_probability",
    )
    reg.add(
        name="Percentil-alvo do AR",
        value=str(config["risk_adjustment"]["default_percentile"]),
        justification="Dentro da faixa de mercado internacional (75%-90%) para produtos de vida de longa duração",
        limitation="O projeto original nunca obteve aprovação formal da liderança sobre o percentil definitivo (gap #2 da metodologia)",
        source="Moodys — Equivalent Confidence Level for the IFRS 17 Risk Adjustment; METODOLOGIA_MESTRE.md seção 7",
    )
    reg.add(
        name="Benefício de diversificação entre componentes",
        value=f"{config['risk_adjustment']['diversification_benefit']:.0%} de redução sobre a soma simples das caixinhas",
        justification="Recomendação de organismos atuariais (CIA) para refletir correlação imperfeita entre riscos distintos (mortalidade, longevidade, invalidez)",
        limitation="Percentual ilustrativo — calibração real exigiria matriz de correlação histórica entre os componentes",
        source="CIA — Educational Note: IFRS 17 RA for Life and Health; METODOLOGIA_MESTRE.md seção 3.8",
    )
    reg.add(
        name="Semente do gerador aleatório (seed)",
        value=str(config["seed"]),
        justification="Fixada explicitamente em todas as simulações para garantir reprodutibilidade total do resultado",
        limitation="Nenhuma — requisito de governança, não uma limitação",
        source="METODOLOGIA_MESTRE.md, Fase 5, item 5 (lição de processo do projeto original)",
    )
    return reg
