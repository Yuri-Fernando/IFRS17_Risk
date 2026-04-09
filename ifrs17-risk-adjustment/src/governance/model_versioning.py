"""Versionamento de modelos."""

from datetime import datetime


class ModelVersion:
    def __init__(self, version, description, parameters):
        self.version = version
        self.description = description
        self.parameters = parameters
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            'version': self.version,
            'description': self.description,
            'parameters': self.parameters,
            'timestamp': self.timestamp
        }


class ModelRegistry:
    def __init__(self):
        self.versions = {}

    def register_version(self, version, description, parameters):
        """Registra nova versão do modelo."""
        mv = ModelVersion(version, description, parameters)
        self.versions[version] = mv
        return mv

    def get_version(self, version):
        """Obtém versão específica."""
        return self.versions.get(version)

    def list_versions(self):
        """Lista todas as versões."""
        return list(self.versions.keys())
