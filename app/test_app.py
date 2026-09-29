from unittest.mock import MagicMock, patch

from redis.exceptions import RedisError

from app import app


def test_health_ok():
    client = MagicMock()
    client.ping.return_value = True
    with patch("app.get_redis", return_value=client):
        res = app.test_client().get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_health_redis_down():
    client = MagicMock()
    client.ping.side_effect = RedisError("down")
    with patch("app.get_redis", return_value=client):
        res = app.test_client().get("/health")
    assert res.status_code == 503
    assert res.get_json()["status"] == "down"


def test_status():
    res = app.test_client().get("/status")
    assert res.status_code == 200
    body = res.get_json()
    assert body["service"] == "devops-eval"
    assert "version" in body
    assert "git_sha" in body


def test_metrics_and_counter():
    c = app.test_client()
    c.get("/status")
    res = c.get("/metrics")
    assert res.status_code == 200
    text = res.data.decode("utf-8")
    assert "http_requests_total" in text
    assert 'endpoint="/status"' in text
    assert "http_request_duration_seconds_bucket" in text
    assert "app_info" in text


def test_health_uses_redis_service():
    # ping reel (service Redis en CI)
    import os

    import redis

    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "127.0.0.1"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
        socket_connect_timeout=2,
    )
    assert r.ping() is True

    with patch("app.get_redis", return_value=r):
        res = app.test_client().get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"
