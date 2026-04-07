from prometheus_client import Counter, Gauge, Histogram

ATTACKS_TOTAL = Counter("rtk1_attacks_total", "Total red team attacks")
ASR_GAUGE = Gauge("rtk1_attack_success_rate", "Attack Success Rate")
LATENCY_HISTOGRAM = Histogram("rtk1_latency_seconds", "Request latency")
