"""
Versionamento de modelo.

Gera um identificador determinístico (hash) a partir dos parâmetros de
execução e metadados do modelo campeão, permitindo rastrear exatamente
qual configuração gerou qual resultado — essencial em auditoria de
modelos de provisão.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ModelVersion:
    model_name: str
    parameters: dict
    gini: float
    ks: float

    @property
    def version_hash(self) -> str:
        payload = json.dumps(
            {"model_name": self.model_name, "parameters": self.parameters}, sort_keys=True
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()[:12]

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "version_hash": self.version_hash,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "parameters": self.parameters,
            "gini": self.gini,
            "ks": self.ks,
        }
