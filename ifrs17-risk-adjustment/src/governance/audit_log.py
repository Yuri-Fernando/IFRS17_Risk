"""Audit log para rastreabilidade."""

import pandas as pd
from datetime import datetime


class AuditLog:
    def __init__(self):
        self.logs = []

    def record(self, operation, details=None, status='SUCCESS'):
        """Registra operação no log."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'details': details or {},
            'status': status
        }
        self.logs.append(log_entry)

    def record_model_execution(self, model_name, parameters):
        """Registra execução do modelo."""
        self.record(f'Model Execution: {model_name}', parameters)

    def record_validation(self, test_name, result):
        """Registra validação."""
        self.record(f'Validation: {test_name}', {'result': result})

    def record_parameter_change(self, parameter, old_value, new_value):
        """Registra mudança de parâmetro."""
        self.record('Parameter Change', {
            'parameter': parameter,
            'old_value': old_value,
            'new_value': new_value
        })

    def to_dataframe(self):
        """Converte logs para DataFrame."""
        return pd.DataFrame(self.logs)
