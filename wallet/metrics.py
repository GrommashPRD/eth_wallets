from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP Request Duration', ['method', 'endpoint'])


def record_request(method, endpoint):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()


def record_duration(method, endpoint, duration):
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)