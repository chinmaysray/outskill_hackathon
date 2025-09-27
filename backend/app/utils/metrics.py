import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
import structlog

logger = structlog.get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_ANALYSES = Gauge('active_analyses_total', 'Number of active analyses')
AGENT_EXECUTION_TIME = Histogram('agent_execution_seconds', 'Agent execution time', ['agent_type'])
ANALYSIS_SUCCESS_RATE = Counter('analysis_success_total', 'Successful analyses', ['agent_type'])

def setup_metrics(app: FastAPI):
    """Setup Prometheus metrics endpoint."""

    @app.get("/metrics")
    async def metrics():
        return PlainTextResponse(generate_latest())

    logger.info("Metrics endpoint configured at /metrics")

def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metrics."""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
    REQUEST_DURATION.observe(duration)

def record_analysis_start():
    """Record analysis start."""
    ACTIVE_ANALYSES.inc()

def record_analysis_complete(agent_type: str, duration: float, success: bool):
    """Record analysis completion."""
    ACTIVE_ANALYSES.dec()
    AGENT_EXECUTION_TIME.labels(agent_type=agent_type).observe(duration)
    if success:
        ANALYSIS_SUCCESS_RATE.labels(agent_type=agent_type).inc()
