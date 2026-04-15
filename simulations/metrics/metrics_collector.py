class MetricsCollector:
    """Recolector de KPIs para validación de escenarios."""
    def __init__(self):
        self.kpis = {
            "safe_stop_rate": 0.0,
            "decision_latency": [],
            "escalation_rate": 0.0,
            "anchoring_time": []
        }

    def log_event(self, metric_name, value):
        if metric_name in self.kpis and isinstance(self.kpis[metric_name], list):
            self.kpis[metric_name].append(value)
        else:
            self.kpis[metric_name] = value

    def get_summary(self):
        return self.kpis
