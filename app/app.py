import os
import time

import redis
from flask import Flask, Response, g, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from redis.exceptions import RedisError

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
GIT_SHA = os.getenv("GIT_SHA", "unknown")

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total requetes HTTP",
    ["endpoint", "code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "Latence HTTP",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

APP_INFO = Gauge(
    "app_info",
    "version / git_sha deployes",
    ["version", "git_sha"],
)
APP_INFO.labels(version=APP_VERSION, git_sha=GIT_SHA).set(1)


def get_redis():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


@app.before_request
def start_timer():
    g.t0 = time.perf_counter()


@app.after_request
def record_metrics(response):
    if request.path == "/metrics":
        return response

    endpoint = request.url_rule.rule if request.url_rule else request.path
    code = str(response.status_code)

    HTTP_REQUESTS_TOTAL.labels(endpoint=endpoint, code=code).inc()

    t0 = getattr(g, "t0", None)
    if t0 is not None:
        HTTP_REQUEST_DURATION_SECONDS.labels(endpoint=endpoint).observe(
            time.perf_counter() - t0
        )

    return response


@app.route("/health")
def health():
    try:
        if get_redis().ping():
            return jsonify(status="ok"), 200
    except RedisError:
        pass
    return jsonify(status="down", reason="redis"), 503


@app.route("/status")
def status():
    return jsonify(
        service="devops-eval",
        version=APP_VERSION,
        git_sha=GIT_SHA,
    ), 200


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/simulate-error")
def simulate_error():
    return jsonify(error="boom"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
