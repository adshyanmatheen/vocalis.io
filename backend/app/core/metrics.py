from __future__ import annotations

import time

from litestar import MediaType, get
from litestar.response import Response
from litestar.types import ASGIApp, Message, Receive, Scope, Send
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from prometheus_client.registry import REGISTRY

request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

in_flight_requests = Gauge(
    "http_in_flight_requests",
    "Number of HTTP requests currently in flight",
)

websocket_connections = Gauge(
    "websocket_connections_active",
    "Number of active WebSocket connections",
)


class MetricsMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/unknown")

        in_flight_requests.inc()
        start = time.perf_counter()
        status_code: int | None = None

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.perf_counter() - start
            in_flight_requests.dec()
            if status_code is not None:
                request_count.labels(
                    method=method, path=path, status=str(status_code)
                ).inc()
                request_duration.labels(method=method, path=path).observe(duration)


def create_metrics_middleware(app: ASGIApp) -> MetricsMiddleware:
    return MetricsMiddleware(app)


@get(
    path="/metrics",
    operation_id="prometheusMetrics",
    summary="Prometheus Metrics",
    description="Exposes Prometheus-formatted metrics for monitoring and alerting.",
    tags=["Health"],
    media_type=MediaType.TEXT,
    sync_to_thread=False,
)
def metrics_endpoint() -> Response[str]:
    return Response(
        content=generate_latest(REGISTRY).decode("utf-8"),
        media_type=MediaType.TEXT,
        headers={"Content-Type": "text/plain; version=0.0.4"},
    )
