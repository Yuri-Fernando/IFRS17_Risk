"""
Trilha de auditoria da execução do pipeline.

Registra, em ordem cronológica, cada etapa executada com timestamp,
parâmetros relevantes e status — requisito de governança de modelos
(Resolução CMN 4.966, princípios de model risk management) para permitir
reconstituir integralmente como um número de provisão foi produzido.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class AuditLog:
    entries: list[dict] = field(default_factory=list)

    def log(self, step: str, status: str = "OK", **details) -> None:
        self.entries.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": step,
                "status": status,
                "details": details,
            }
        )

    def to_list(self) -> list[dict]:
        return self.entries

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)
